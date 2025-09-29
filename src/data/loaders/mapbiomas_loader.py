"""
CP2B Maps V2 - MapBiomas Integration Module
Professional satellite data processing for agricultural land use analysis
"""

import base64
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from io import BytesIO
import streamlit as st

# Geospatial imports with error handling
try:
    import folium
    from rasterio.mask import mask
    from shapely.geometry import Point
    import geopandas as gpd
    from pyproj import Transformer
    HAS_GEOSPATIAL = True
except ImportError:
    HAS_GEOSPATIAL = False
    folium = None

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None

# Optional matplotlib for colors
try:
    import matplotlib.colors as mcolors
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    mcolors = None

from config.settings import settings
from src.utils.logging_config import get_logger
from .raster_loader import RasterLoader

logger = get_logger(__name__)


# MapBiomas Agricultural Classes Color Palette
MAPBIOMAS_COLORS = {
    # Pastagem (Pasture)
    15: '#FFD966',  # Light yellow

    # Silvicultura (Forestry)
    9: '#6D4C41',   # Brown

    # Lavouras Temporárias (Temporary Crops)
    39: '#E1BEE7',  # Soy - Light purple
    20: '#C5E1A5',  # Sugarcane - Light green
    40: '#FFCDD2',  # Rice - Light pink
    62: '#F8BBD9',  # Cotton - Pink
    41: '#DCEDC8',  # Other temporary - Very light green

    # Lavouras Perenes (Perennial Crops)
    46: '#8D6E63',  # Coffee - Light brown
    47: '#FFA726',  # Citrus - Orange
    35: '#66BB6A',  # Palm oil - Green
    48: '#A1887F'   # Other perennial - Grayish brown
}

# Class names in Portuguese and English
MAPBIOMAS_CLASS_NAMES = {
    15: {'pt': 'Pastagem', 'en': 'Pasture'},
    9: {'pt': 'Silvicultura', 'en': 'Forestry'},
    39: {'pt': 'Soja', 'en': 'Soy'},
    20: {'pt': 'Cana-de-açúcar', 'en': 'Sugarcane'},
    40: {'pt': 'Arroz', 'en': 'Rice'},
    62: {'pt': 'Algodão', 'en': 'Cotton'},
    41: {'pt': 'Outras Temporárias', 'en': 'Other Temporary Crops'},
    46: {'pt': 'Café', 'en': 'Coffee'},
    47: {'pt': 'Citros', 'en': 'Citrus'},
    35: {'pt': 'Dendê', 'en': 'Palm Oil'},
    48: {'pt': 'Outras Perenes', 'en': 'Other Perennial Crops'}
}


class MapBiomasLoader:
    """
    Professional MapBiomas satellite data integration
    Features: Color management, class filtering, legend generation, analysis
    """

    def __init__(self, raster_loader: Optional[RasterLoader] = None):
        """
        Initialize MapBiomas loader

        Args:
            raster_loader: RasterLoader instance (optional)
        """
        self.raster_loader = raster_loader or RasterLoader()
        self.logger = get_logger(self.__class__.__name__)

        if not HAS_GEOSPATIAL:
            self.logger.warning("Geospatial libraries not available - limited functionality")

    def get_class_color(self, class_id: int) -> str:
        """
        Get color for MapBiomas class

        Args:
            class_id: MapBiomas class identifier

        Returns:
            Hex color string
        """
        return MAPBIOMAS_COLORS.get(class_id, '#CCCCCC')

    def get_class_name(self, class_id: int, language: str = 'pt') -> str:
        """
        Get class name in specified language

        Args:
            class_id: MapBiomas class identifier
            language: Language code ('pt' or 'en')

        Returns:
            Class name string
        """
        names = MAPBIOMAS_CLASS_NAMES.get(class_id, {'pt': 'Desconhecido', 'en': 'Unknown'})
        return names.get(language, names['pt'])

    def create_colored_image(self, data: np.ndarray, selected_classes: List[int] = None) -> Optional[np.ndarray]:
        """
        Create colored image from MapBiomas raster data

        Args:
            data: Raster data array
            selected_classes: List of class IDs to display

        Returns:
            RGBA image array or None
        """
        try:
            # Filter classes if specified
            if selected_classes is not None:
                mask = np.zeros_like(data, dtype=bool)
                for class_id in selected_classes:
                    mask |= (data == class_id)
                data_filtered = np.where(mask, data, np.nan)
            else:
                data_filtered = data.copy()

            # Get unique values
            unique_values = np.unique(data_filtered[~np.isnan(data_filtered)])

            # Create RGBA image
            height, width = data_filtered.shape
            colored_image = np.zeros((height, width, 4), dtype=np.uint8)

            for value in unique_values:
                if np.isnan(value):
                    continue

                mask = data_filtered == int(value)
                color_hex = self.get_class_color(int(value))

                # Convert hex to RGB
                if HAS_MATPLOTLIB:
                    rgb = mcolors.hex2color(color_hex)
                    rgb_255 = [int(c * 255) for c in rgb]
                else:
                    # Manual hex to RGB conversion
                    hex_color = color_hex.lstrip('#')
                    rgb_255 = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

                # Set RGBA values (200 = ~78% opacity)
                colored_image[mask] = [rgb_255[0], rgb_255[1], rgb_255[2], 200]

            return colored_image

        except Exception as e:
            self.logger.error(f"Error creating colored image: {e}")
            return None

    def create_folium_overlay(self,
                            data: np.ndarray,
                            metadata: Dict[str, Any],
                            selected_classes: List[int] = None,
                            opacity: float = 0.7) -> Optional[object]:
        """
        Create Folium overlay from MapBiomas data

        Args:
            data: Raster data array
            metadata: Raster metadata
            selected_classes: List of class IDs to display
            opacity: Overlay opacity (0-1)

        Returns:
            Folium ImageOverlay object or None
        """
        if not HAS_GEOSPATIAL:
            self.logger.error("Folium not available for overlay creation")
            return None

        try:
            # Remove nodata values
            if metadata.get('nodata') is not None:
                data_masked = np.where(data == metadata['nodata'], np.nan, data)
            else:
                data_masked = data.copy()

            # Create colored image
            colored_image = self.create_colored_image(data_masked, selected_classes)
            if colored_image is None:
                return None

            # Convert to base64
            img_base64 = self._array_to_base64(colored_image)
            if img_base64 is None:
                return None

            # Define geographic bounds
            bounds = metadata['bounds']
            folium_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

            # Create Folium overlay
            overlay = folium.raster_layers.ImageOverlay(
                image=img_base64,
                bounds=folium_bounds,
                opacity=opacity,
                interactive=True,
                cross_origin=False,
                zindex=1
            )

            self.logger.info("Successfully created Folium overlay")
            return overlay

        except Exception as e:
            self.logger.error(f"Error creating Folium overlay: {e}")
            return None

    def _array_to_base64(self, array: np.ndarray) -> Optional[str]:
        """
        Convert numpy array to base64 string for Folium

        Args:
            array: RGBA image array

        Returns:
            Base64 encoded image string or None
        """
        if not HAS_PIL:
            self.logger.error("PIL required for image conversion")
            return None

        try:
            # Convert to PIL Image
            img = Image.fromarray(array, mode='RGBA')

            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Convert to base64
            img_str = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            self.logger.error(f"Error converting array to base64: {e}")
            return None

    def create_legend_html(self, selected_classes: List[int] = None, language: str = 'pt') -> str:
        """
        Create HTML legend for MapBiomas classes

        Args:
            selected_classes: List of class IDs to include in legend
            language: Language for class names

        Returns:
            HTML string for legend
        """
        legend_html = f"""
        <div style="
            position: fixed;
            bottom: 50px; right: 50px; width: 200px; height: auto;
            background-color: white; border: 2px solid grey; z-index: 9999;
            font-size: 12px; padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        ">
        <h4 style="margin-top: 0; text-align: center;">
            {'MapBiomas - Agropecuária' if language == 'pt' else 'MapBiomas - Agriculture'}
        </h4>
        """

        # Filter classes if specified
        if selected_classes is not None:
            classes_to_show = {code: MAPBIOMAS_CLASS_NAMES[code]
                             for code in selected_classes
                             if code in MAPBIOMAS_CLASS_NAMES}
        else:
            classes_to_show = MAPBIOMAS_CLASS_NAMES

        # Add legend items
        for code, names in classes_to_show.items():
            color = self.get_class_color(code)
            name = names.get(language, names['pt'])

            legend_html += f"""
            <div style="margin: 3px 0;">
                <span style="
                    display: inline-block;
                    width: 20px; height: 15px;
                    background-color: {color};
                    margin-right: 8px;
                    border: 1px solid #333;
                    vertical-align: middle;
                "></span>
                <span style="font-size: 10px;">{name}</span>
            </div>
            """

        legend_html += "</div>"
        return legend_html

    def analyze_radius_area(self,
                          raster_path: str,
                          center_lat: float,
                          center_lon: float,
                          radius_km: float) -> Dict[str, Any]:
        """
        Analyze MapBiomas data within radius from center point

        Args:
            raster_path: Path to MapBiomas raster file
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Analysis radius in kilometers

        Returns:
            Dictionary with area analysis results
        """
        if not HAS_GEOSPATIAL:
            self.logger.error("Geospatial libraries required for radius analysis")
            return {}

        try:
            import rasterio

            # Create circular geometry
            center_point = Point(center_lon, center_lat)
            buffer_degrees = radius_km / 111.0  # Approximate conversion
            circle_geometry = center_point.buffer(buffer_degrees)

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame([1], geometry=[circle_geometry], crs="EPSG:4326")

            # Open raster and perform analysis
            with rasterio.open(raster_path) as src:
                # Transform geometry to raster CRS
                if src.crs != gdf.crs:
                    gdf_transformed = gdf.to_crs(src.crs)
                else:
                    gdf_transformed = gdf

                # Mask raster data
                out_image, out_transform = mask(src, gdf_transformed.geometry, crop=True, filled=True)
                data = out_image[0]  # First band

                # Remove nodata values
                valid_data = data[data != src.nodata]

                if valid_data.size == 0:
                    self.logger.warning("No valid pixels found in analysis area")
                    return {}

                # Count pixels by class
                unique_values, counts = np.unique(valid_data, return_counts=True)

                # Calculate pixel area in hectares
                pixel_width_deg = abs(out_transform[0])
                pixel_height_deg = abs(out_transform[4])

                # Convert degrees to meters (considering latitude)
                m_per_deg_lat = 111320
                m_per_deg_lon = m_per_deg_lat * np.cos(np.radians(center_lat))

                pixel_area_m2 = (pixel_height_deg * m_per_deg_lat) * (pixel_width_deg * m_per_deg_lon)
                pixel_area_ha = pixel_area_m2 / 10000  # Convert to hectares

                # Process results
                results = {}
                total_area = 0

                for value, count in zip(unique_values, counts):
                    class_code = int(value)
                    area_ha = count * pixel_area_ha

                    if class_code in MAPBIOMAS_CLASS_NAMES and area_ha > 0.01:  # Minimum 100m²
                        class_name = self.get_class_name(class_code)
                        results[class_name] = {
                            'area_ha': round(area_ha, 1),
                            'class_id': class_code,
                            'pixel_count': count
                        }
                        total_area += area_ha

                # Add summary metadata
                results['_metadata'] = {
                    'center_lat': center_lat,
                    'center_lon': center_lon,
                    'radius_km': radius_km,
                    'total_analyzed_area_ha': round(total_area, 1),
                    'unique_classes': len(results) - 1,  # Exclude metadata
                    'total_pixels': len(valid_data)
                }

                self.logger.info(f"Analyzed {len(results)-1} classes in {radius_km}km radius")
                return results

        except Exception as e:
            self.logger.error(f"Error in radius analysis: {e}")
            return {}

    def get_available_mapbiomas_files(self) -> List[Dict[str, Any]]:
        """
        Get list of available MapBiomas raster files

        Returns:
            List of MapBiomas file information
        """
        all_rasters = self.raster_loader.list_available_rasters()

        # Filter for MapBiomas files
        mapbiomas_files = []
        for raster_info in all_rasters:
            filename_lower = raster_info['filename'].lower()
            if any(keyword in filename_lower for keyword in ['mapbiomas', 'agropecuaria', 'agriculture']):
                mapbiomas_files.append(raster_info)

        return mapbiomas_files


# Factory function
@st.cache_resource
def get_mapbiomas_loader() -> MapBiomasLoader:
    """
    Get cached MapBiomasLoader instance

    Returns:
        MapBiomasLoader instance
    """
    return MapBiomasLoader()


# Convenience functions
def create_mapbiomas_legend(selected_classes: List[int] = None, language: str = 'pt') -> str:
    """
    Convenience function to create MapBiomas legend

    Args:
        selected_classes: List of class IDs to include
        language: Language for class names

    Returns:
        HTML legend string
    """
    loader = get_mapbiomas_loader()
    return loader.create_legend_html(selected_classes, language)


def analyze_mapbiomas_radius(raster_path: str,
                           center_lat: float,
                           center_lon: float,
                           radius_km: float) -> Dict[str, Any]:
    """
    Convenience function for MapBiomas radius analysis

    Args:
        raster_path: Path to MapBiomas raster
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Analysis radius in kilometers

    Returns:
        Analysis results dictionary
    """
    loader = get_mapbiomas_loader()
    return loader.analyze_radius_area(raster_path, center_lat, center_lon, radius_km)