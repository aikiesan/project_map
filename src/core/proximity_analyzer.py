"""
CP2B Maps - Proximity Analyzer (Core Business Logic)
SOLID Principles: Single Responsibility, Dependency Injection
Clean separation of business logic from UI
"""

from typing import Dict, Optional, Tuple, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProximityAnalyzer:
    """
    Core business logic for proximity analysis

    Responsibilities:
    - Coordinate validation
    - Raster analysis orchestration
    - Result processing

    Follows Single Responsibility and Dependency Inversion principles
    """

    def __init__(self, raster_loader=None):
        """
        Initialize analyzer with optional dependency injection

        Args:
            raster_loader: Optional MapBiomasLoader instance for dependency injection
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mapbiomas_loader = raster_loader  # Actually expects MapBiomasLoader

        # MapBiomas class mapping (comprehensive)
        self.class_map = {
            # === AGRICULTURAL CLASSES (Priority) ===
            15: '🌾 Pastagem',
            20: '🌾 Cana-de-açúcar',
            39: '🌱 Soja',
            40: '🌾 Arroz',
            41: '🌾 Outras Culturas Temporárias',
            46: '☕ Café',
            47: '🍊 Citrus',
            62: '🌾 Algodão',
            35: '🌴 Dendê',
            48: '🌾 Outras Culturas Perenes',
            9: '🌲 Silvicultura',

            # === OTHER LAND USE CLASSES ===
            3: '🌳 Formação Florestal',
            4: '🌿 Formação Savânica',
            5: '🌾 Mangue',
            11: '🌾 Campo Alagado',
            12: '🌿 Formação Campestre',
            13: '🌿 Outras Formações',
            23: '🏖️ Praia e Duna',
            24: '🏘️ Área Urbanizada',
            25: '🌿 Outras Áreas não Vegetadas',
            26: '💧 Corpo d\'Água',
            27: '❄️ Não Observado',
            29: '🏞️ Afloramento Rochoso',
            30: '⛏️ Mineração',
            32: '💧 Apicum',
            33: '💧 Rio, Lago e Oceano'
        }

    def validate_coordinates(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> Tuple[bool, str]:
        """
        Validate proximity analysis coordinates

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius_km: Radius in kilometers

        Returns:
            Tuple of (is_valid, message)
        """
        if not (-90 <= lat <= 90):
            return False, f"Invalid latitude: {lat}"
        if not (-180 <= lon <= 180):
            return False, f"Invalid longitude: {lon}"
        if not (0 < radius_km <= 200):
            return False, f"Invalid radius: {radius_km}"
        return True, "Valid coordinates"

    def find_raster_files(self) -> List[str]:
        """
        Find available raster files for analysis

        Returns:
            List of raster file paths
        """
        project_root = Path(__file__).parent.parent.parent
        raster_dir = project_root / "data" / "rasters"  # Fixed: was missing 'data'

        if not raster_dir.exists():
            self.logger.warning(f"Raster directory does not exist: {raster_dir}")
            return []

        # Look for common raster file extensions
        extensions = ['.tif', '.tiff', '.geotiff']
        raster_files = []

        for ext in extensions:
            raster_files.extend(raster_dir.glob(f"*{ext}"))
            raster_files.extend(raster_dir.glob(f"*{ext.upper()}"))

        return [str(f) for f in raster_files]

    def analyze_proximity(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> Optional[Dict[str, float]]:
        """
        Perform raster-based proximity analysis

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Analysis radius in km

        Returns:
            Dictionary mapping land use types to area in hectares
            None if analysis fails
        """
        # Validation
        is_valid, msg = self.validate_coordinates(center_lat, center_lon, radius_km)
        if not is_valid:
            self.logger.error(f"Coordinate validation failed: {msg}")
            return None

        # Check for mapbiomas loader
        if self.mapbiomas_loader is None:
            self.logger.error("No MapBiomas loader available")
            return None

        # Find raster files
        raster_files = self.find_raster_files()
        if not raster_files:
            self.logger.error("No raster files found")
            return None

        # Perform analysis
        try:
            raster_path = str(raster_files[0])

            self.logger.info(
                f"Starting proximity analysis: center=({center_lat}, {center_lon}), "
                f"radius={radius_km}km, raster={raster_path}"
            )

            # Use MapBiomas loader's analyze_radius_area method (NOT analyze_raster_in_radius!)
            raw_results = self.mapbiomas_loader.analyze_radius_area(
                raster_path=raster_path,
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km
            )

            if not raw_results:
                self.logger.warning("Analysis returned empty results")
                return None

            # Convert MapBiomas format to simple dict {class_name: area_ha}
            results = {}
            for class_name, data in raw_results.items():
                if class_name != '_metadata' and isinstance(data, dict):
                    # Extract area_ha from nested dict
                    results[class_name] = data.get('area_ha', 0)

            if results:
                self.logger.info(f"Analysis successful: found {len(results)} land use types")
            else:
                self.logger.warning("Analysis returned no valid land use types")

            return results

        except Exception as e:
            self.logger.error(f"Proximity analysis failed: {e}", exc_info=True)
            return None

    def get_agricultural_uses(self, results: Dict[str, float]) -> Dict[str, float]:
        """
        Filter results to only agricultural uses

        Args:
            results: Full land use results

        Returns:
            Dictionary of agricultural uses only
        """
        agricultural_keywords = ['🌾', '🌱', '☕', '🍊', '🌴', '🌲']
        return {
            uso: area
            for uso, area in results.items()
            if any(keyword in uso for keyword in agricultural_keywords)
        }

    def get_summary_statistics(
        self,
        results: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate summary statistics for proximity analysis

        Args:
            results: Land use results

        Returns:
            Dictionary with total_area, agri_area, agri_percentage
        """
        if not results:
            return {
                'total_area': 0.0,
                'agri_area': 0.0,
                'agri_percentage': 0.0
            }

        total_area = sum(results.values())
        agri_results = self.get_agricultural_uses(results)
        agri_area = sum(agri_results.values())
        agri_percentage = (agri_area / total_area * 100) if total_area > 0 else 0.0

        return {
            'total_area': total_area,
            'agri_area': agri_area,
            'agri_percentage': agri_percentage,
            'num_types': len(results),
            'num_agri_types': len(agri_results)
        }


# Singleton instance accessor
_proximity_analyzer_instance = None

def get_proximity_analyzer(raster_loader=None) -> ProximityAnalyzer:
    """
    Get or create singleton proximity analyzer instance

    Args:
        raster_loader: Optional raster loader for dependency injection

    Returns:
        ProximityAnalyzer instance
    """
    global _proximity_analyzer_instance

    if _proximity_analyzer_instance is None:
        _proximity_analyzer_instance = ProximityAnalyzer(raster_loader=raster_loader)
    elif raster_loader is not None:
        # Update raster loader if provided
        _proximity_analyzer_instance.raster_loader = raster_loader

    return _proximity_analyzer_instance
