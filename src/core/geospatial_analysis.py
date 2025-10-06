"""
CP2B Maps - Geospatial Analysis Core Module
Professional geospatial processing and analysis functions
"""

import math
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import streamlit as st

# Geospatial imports with error handling
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    from pyproj import Transformer, CRS
    import rasterio
    from rasterio.mask import mask
    HAS_GEOSPATIAL = True
except ImportError:
    HAS_GEOSPATIAL = False

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GeospatialAnalyzer:
    """
    Professional geospatial analysis with coordinate systems and transformations
    Features: Distance calculations, radius analysis, CRS transformations, area calculations
    """

    def __init__(self):
        """Initialize GeospatialAnalyzer"""
        self.logger = get_logger(self.__class__.__name__)

        if not HAS_GEOSPATIAL:
            self.logger.warning("Geospatial libraries not available - limited functionality")

    def calculate_distance_haversine(self,
                                   lat1: float, lon1: float,
                                   lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        try:
            # Convert to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)

            # Haversine formula
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad

            a = (math.sin(dlat/2)**2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)

            c = 2 * math.asin(math.sqrt(a))
            radius_earth_km = 6371  # Earth radius in km

            return radius_earth_km * c

        except Exception as e:
            self.logger.error(f"Error calculating distance: {e}")
            return 0.0

    def find_municipalities_in_radius(self,
                                    df: pd.DataFrame,
                                    center_lat: float,
                                    center_lon: float,
                                    radius_km: float,
                                    lat_col: str = 'lat',
                                    lon_col: str = 'lon') -> pd.DataFrame:
        """
        Find municipalities within radius from center point

        Args:
            df: DataFrame with municipality data
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Search radius in kilometers
            lat_col: Name of latitude column
            lon_col: Name of longitude column

        Returns:
            Filtered DataFrame with municipalities in radius
        """
        try:
            if lat_col not in df.columns or lon_col not in df.columns:
                self.logger.error(f"Required columns {lat_col}, {lon_col} not found")
                return pd.DataFrame()

            # Calculate distances
            distances = []
            for idx, row in df.iterrows():
                if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
                    dist = self.calculate_distance_haversine(
                        center_lat, center_lon,
                        row[lat_col], row[lon_col]
                    )
                    distances.append(dist)
                else:
                    distances.append(float('inf'))

            # Filter by radius
            df_copy = df.copy()
            df_copy['distance_km'] = distances
            result = df_copy[df_copy['distance_km'] <= radius_km].copy()

            # Sort by distance
            result = result.sort_values('distance_km')

            self.logger.info(f"Found {len(result)} municipalities within {radius_km}km")
            return result

        except Exception as e:
            self.logger.error(f"Error finding municipalities in radius: {e}")
            return pd.DataFrame()

    def create_circular_geometry(self,
                               center_lat: float,
                               center_lon: float,
                               radius_km: float,
                               crs: str = "EPSG:4326") -> Optional[object]:
        """
        Create circular geometry for spatial analysis

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers
            crs: Coordinate reference system

        Returns:
            GeoDataFrame with circular geometry or None
        """
        if not HAS_GEOSPATIAL:
            self.logger.error("Geospatial libraries required for geometry creation")
            return None

        try:
            # Create center point
            center_point = Point(center_lon, center_lat)

            # Convert radius to degrees (approximate)
            # 1 degree ≈ 111 km at equator
            buffer_degrees = radius_km / 111.0

            # Adjust for latitude (longitude lines converge at poles)
            buffer_degrees_lon = buffer_degrees / math.cos(math.radians(center_lat))

            # Create elliptical buffer to approximate circular area
            # This is a simple approximation; for precise work, use projected CRS
            if abs(center_lat) < 60:  # Reasonable approximation range
                circle_geometry = center_point.buffer(buffer_degrees)
            else:
                # Use more conservative circular approximation for high latitudes
                circle_geometry = center_point.buffer(buffer_degrees)

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame([1], geometry=[circle_geometry], crs=crs)

            return gdf

        except Exception as e:
            self.logger.error(f"Error creating circular geometry: {e}")
            return None

    def analyze_raster_in_circle(self,
                               raster_path: Union[str, Path],
                               center_lat: float,
                               center_lon: float,
                               radius_km: float,
                               class_map: Optional[Dict[int, str]] = None) -> Dict[str, Any]:
        """
        Analyze raster data within circular area

        Args:
            raster_path: Path to raster file
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Analysis radius in kilometers
            class_map: Dictionary mapping class codes to names

        Returns:
            Dictionary with analysis results
        """
        if not HAS_GEOSPATIAL:
            self.logger.error("Geospatial libraries required for raster analysis")
            return {}

        try:
            # Create circular geometry
            circle_gdf = self.create_circular_geometry(center_lat, center_lon, radius_km)
            if circle_gdf is None:
                return {}

            # Open raster file
            with rasterio.open(raster_path) as src:
                # Transform geometry to raster CRS if needed
                if src.crs != circle_gdf.crs:
                    circle_transformed = circle_gdf.to_crs(src.crs)
                else:
                    circle_transformed = circle_gdf

                # Mask raster data
                out_image, out_transform = mask(
                    src, circle_transformed.geometry,
                    crop=True, filled=True
                )

                # Extract first band
                data = out_image[0]

                # Remove nodata pixels
                if src.nodata is not None:
                    valid_data = data[data != src.nodata]
                else:
                    valid_data = data.flatten()

                if valid_data.size == 0:
                    self.logger.warning("No valid pixels found in analysis area")
                    return {}

                # Count unique values
                unique_values, counts = np.unique(valid_data, return_counts=True)

                # Calculate pixel area in hectares
                pixel_area_ha = self._calculate_pixel_area_ha(
                    out_transform, center_lat
                )

                # Process results
                results = {}
                total_area_ha = 0

                for value, count in zip(unique_values, counts):
                    class_code = int(value)
                    area_ha = count * pixel_area_ha

                    # Use class name if provided, otherwise use code
                    if class_map and class_code in class_map:
                        class_name = class_map[class_code]
                    else:
                        class_name = f"Class_{class_code}"

                    if area_ha > 0.01:  # Minimum area threshold (100 m²)
                        results[class_name] = {
                            'area_ha': round(area_ha, 2),
                            'percentage': 0,  # Will be calculated after total
                            'pixel_count': int(count),
                            'class_code': class_code
                        }
                        total_area_ha += area_ha

                # Calculate percentages
                for class_name in results:
                    if total_area_ha > 0:
                        results[class_name]['percentage'] = round(
                            (results[class_name]['area_ha'] / total_area_ha) * 100, 1
                        )

                # Add metadata
                results['_metadata'] = {
                    'center_coordinates': (center_lat, center_lon),
                    'radius_km': radius_km,
                    'total_area_ha': round(total_area_ha, 2),
                    'analysis_area_km2': round(total_area_ha / 100, 2),  # Convert ha to km²
                    'unique_classes': len([k for k in results.keys() if not k.startswith('_')]),
                    'total_pixels_analyzed': len(valid_data),
                    'raster_file': str(raster_path)
                }

                self.logger.info(f"Analyzed {len(results)-1} classes covering {total_area_ha:.1f} hectares")
                return results

        except Exception as e:
            self.logger.error(f"Error in raster circle analysis: {e}")
            return {}

    def _calculate_pixel_area_ha(self, transform, center_lat: float) -> float:
        """
        Calculate pixel area in hectares considering latitude

        Args:
            transform: Raster transform matrix
            center_lat: Center latitude for adjustment

        Returns:
            Pixel area in hectares
        """
        try:
            # Get pixel dimensions in degrees
            pixel_width_deg = abs(transform[0])
            pixel_height_deg = abs(transform[4])

            # Convert to meters considering latitude
            m_per_deg_lat = 111320  # meters per degree latitude
            m_per_deg_lon = m_per_deg_lat * math.cos(math.radians(center_lat))

            # Calculate area
            pixel_area_m2 = (pixel_height_deg * m_per_deg_lat) * (pixel_width_deg * m_per_deg_lon)
            pixel_area_ha = pixel_area_m2 / 10000  # Convert m² to hectares

            return pixel_area_ha

        except Exception as e:
            self.logger.error(f"Error calculating pixel area: {e}")
            return 0.0

    def calculate_catchment_statistics(self,
                                     df: pd.DataFrame,
                                     center_lat: float,
                                     center_lon: float,
                                     radius_km: float,
                                     value_column: str) -> Dict[str, Any]:
        """
        Calculate statistics for catchment area

        Args:
            df: Municipality data DataFrame
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Catchment radius in kilometers
            value_column: Column to analyze

        Returns:
            Dictionary with catchment statistics
        """
        try:
            # Find municipalities in radius
            municipalities_in_radius = self.find_municipalities_in_radius(
                df, center_lat, center_lon, radius_km
            )

            if municipalities_in_radius.empty or value_column not in municipalities_in_radius.columns:
                return {}

            # Extract values and filter valid data
            values = municipalities_in_radius[value_column].dropna()

            if values.empty:
                return {}

            # Calculate statistics
            stats = {
                'total_value': float(values.sum()),
                'mean_value': float(values.mean()),
                'median_value': float(values.median()),
                'std_value': float(values.std()) if len(values) > 1 else 0.0,
                'min_value': float(values.min()),
                'max_value': float(values.max()),
                'count_municipalities': len(values),
                'total_municipalities_in_radius': len(municipalities_in_radius)
            }

            # Add percentiles
            stats.update({
                'percentile_25': float(values.quantile(0.25)),
                'percentile_75': float(values.quantile(0.75)),
                'percentile_90': float(values.quantile(0.90))
            })

            # Add metadata
            stats['_metadata'] = {
                'center_coordinates': (center_lat, center_lon),
                'radius_km': radius_km,
                'analyzed_column': value_column,
                'catchment_area_km2': round(math.pi * radius_km ** 2, 2)
            }

            return stats

        except Exception as e:
            self.logger.error(f"Error calculating catchment statistics: {e}")
            return {}

    def create_analysis_summary(self,
                              raster_results: Dict[str, Any],
                              municipality_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create combined analysis summary

        Args:
            raster_results: Results from raster analysis
            municipality_stats: Results from municipality analysis

        Returns:
            Combined analysis summary
        """
        try:
            summary = {
                'analysis_type': 'Combined Geospatial Analysis',
                'timestamp': pd.Timestamp.now().isoformat(),
            }

            # Add raster summary
            if raster_results and '_metadata' in raster_results:
                raster_meta = raster_results['_metadata']
                summary['raster_analysis'] = {
                    'total_area_analyzed_ha': raster_meta.get('total_area_ha', 0),
                    'unique_land_classes': raster_meta.get('unique_classes', 0),
                    'dominant_class': self._find_dominant_class(raster_results)
                }

            # Add municipality summary
            if municipality_stats:
                summary['municipality_analysis'] = {
                    'municipalities_analyzed': municipality_stats.get('count_municipalities', 0),
                    'total_biogas_potential': municipality_stats.get('total_value', 0),
                    'average_potential': municipality_stats.get('mean_value', 0)
                }

            # Add geographic info
            if municipality_stats and '_metadata' in municipality_stats:
                meta = municipality_stats['_metadata']
                summary['geographic_info'] = {
                    'center_coordinates': meta.get('center_coordinates'),
                    'analysis_radius_km': meta.get('radius_km'),
                    'total_area_km2': meta.get('catchment_area_km2')
                }

            return summary

        except Exception as e:
            self.logger.error(f"Error creating analysis summary: {e}")
            return {}

    def _find_dominant_class(self, raster_results: Dict[str, Any]) -> Optional[str]:
        """Find the dominant land use class from raster results"""
        try:
            max_area = 0
            dominant_class = None

            for key, value in raster_results.items():
                if not key.startswith('_') and isinstance(value, dict):
                    area = value.get('area_ha', 0)
                    if area > max_area:
                        max_area = area
                        dominant_class = key

            return dominant_class

        except Exception:
            return None


# Factory function
@st.cache_resource
def get_geospatial_analyzer() -> GeospatialAnalyzer:
    """
    Get cached GeospatialAnalyzer instance

    Returns:
        GeospatialAnalyzer instance
    """
    return GeospatialAnalyzer()


# Convenience functions
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Convenience function to calculate distance between two points

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    analyzer = get_geospatial_analyzer()
    return analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)


def analyze_municipalities_in_radius(df: pd.DataFrame,
                                   center_lat: float,
                                   center_lon: float,
                                   radius_km: float) -> pd.DataFrame:
    """
    Convenience function to find municipalities in radius

    Args:
        df: Municipality DataFrame
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Search radius in kilometers

    Returns:
        Filtered DataFrame with municipalities in radius
    """
    analyzer = get_geospatial_analyzer()
    return analyzer.find_municipalities_in_radius(df, center_lat, center_lon, radius_km)