"""
CP2B Maps - Professional Shapefile Loader
High-performance geospatial data loading with smart caching and optimization
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, Union
import geopandas as gpd
import pandas as pd
from functools import lru_cache
import streamlit as st

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ShapefileLoader:
    """
    Professional shapefile loading with performance optimizations
    Features: Smart caching, CRS conversion, geometry simplification, error handling
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize ShapefileLoader with data directory

        Args:
            data_dir: Path to shapefile directory (defaults to settings.DATA_DIR/shapefile)
        """
        self.data_dir = data_dir or settings.DATA_DIR / "shapefile"
        self.logger = get_logger(self.__class__.__name__)

        if not self.data_dir.exists():
            self.logger.warning(f"Shapefile directory not found: {self.data_dir}")
            self.data_dir.mkdir(parents=True, exist_ok=True)

    @st.cache_data(ttl=settings.CACHE_TTL)
    def load_shapefile(_self,
                      filename: str,
                      simplify_tolerance: float = 0.001,
                      target_crs: str = "EPSG:4326") -> Optional[gpd.GeoDataFrame]:
        """
        Load shapefile with caching and optimization

        Args:
            filename: Shapefile name (without extension)
            simplify_tolerance: Geometry simplification tolerance (0 = no simplification)
            target_crs: Target coordinate reference system

        Returns:
            GeoDataFrame or None if loading fails
        """
        try:
            shapefile_path = _self.data_dir / f"{filename}.shp"

            if not shapefile_path.exists():
                _self.logger.error(f"Shapefile not found: {shapefile_path}")
                return None

            _self.logger.info(f"Loading shapefile: {filename}")

            # Load shapefile
            gdf = gpd.read_file(shapefile_path)

            # CRS conversion
            if gdf.crs and str(gdf.crs) != target_crs:
                gdf = gdf.to_crs(target_crs)
                _self.logger.debug(f"Converted CRS to {target_crs}")

            # Data type optimization to prevent serialization errors
            _self._optimize_datatypes(gdf)

            # Geometry simplification for performance
            if simplify_tolerance > 0:
                gdf['geometry'] = gdf['geometry'].simplify(
                    simplify_tolerance, preserve_topology=True
                )
                _self.logger.debug(f"Simplified geometry with tolerance {simplify_tolerance}")

            _self.logger.info(f"Successfully loaded {len(gdf)} features from {filename}")
            return gdf

        except Exception as e:
            _self.logger.error(f"Failed to load {filename}: {e}", exc_info=True)
            return None

    def _optimize_datatypes(self, gdf: gpd.GeoDataFrame) -> None:
        """
        Optimize data types for Streamlit caching and performance

        Args:
            gdf: GeoDataFrame to optimize (modified in place)
        """
        for col in gdf.columns:
            if col != 'geometry':
                if gdf[col].dtype == 'datetime64[ns]' or str(gdf[col].dtype).startswith('datetime'):
                    gdf[col] = gdf[col].astype(str)
                elif gdf[col].dtype == 'object':
                    # Convert object columns to string for consistency
                    gdf[col] = gdf[col].astype(str)

    def load_municipalities(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load São Paulo municipalities shapefile (645 municipalities)

        Returns:
            GeoDataFrame with municipality boundaries
        """
        return self.load_shapefile("SP_Municipios_2024", simplify_tolerance=0.001)

    def load_biogas_plants(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load biogas plants data (425 plants)

        Returns:
            GeoDataFrame with biogas plant locations
        """
        return self.load_shapefile("Shapefile_425_Biogas_Mapbiomas_SP", simplify_tolerance=0)

    def load_state_boundary(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load São Paulo state boundary

        Returns:
            GeoDataFrame with state boundary
        """
        return self.load_shapefile("Limite_SP", simplify_tolerance=0.001)

    def load_gas_pipelines(self, pipeline_type: str = "both") -> Optional[gpd.GeoDataFrame]:
        """
        Load gas pipeline networks

        Args:
            pipeline_type: "distribution", "transport", or "both"

        Returns:
            GeoDataFrame with pipeline networks
        """
        if pipeline_type == "distribution":
            return self.load_shapefile("Gasodutos_Distribuicao_SP", simplify_tolerance=0.0001)
        elif pipeline_type == "transport":
            return self.load_shapefile("Gasodutos_Transporte_SP", simplify_tolerance=0.0001)
        elif pipeline_type == "both":
            dist = self.load_shapefile("Gasodutos_Distribuicao_SP", simplify_tolerance=0.0001)
            trans = self.load_shapefile("Gasodutos_Transporte_SP", simplify_tolerance=0.0001)

            if dist is not None and trans is not None:
                # Add type identifier to each shapefile
                dist = dist.copy()
                trans = trans.copy()
                dist['TIPO'] = 'Distribuição'
                trans['TIPO'] = 'Transporte'

                # Combine both pipeline types
                combined = pd.concat([dist, trans], ignore_index=True)
                return gpd.GeoDataFrame(combined, crs=dist.crs)
            elif dist is not None:
                dist = dist.copy()
                dist['TIPO'] = 'Distribuição'
                return dist
            elif trans is not None:
                trans = trans.copy()
                trans['TIPO'] = 'Transporte'
                return trans

        return None

    def load_immediate_regions(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load IBGE immediate regions shapefile (53 regions)

        Returns:
            GeoDataFrame with immediate region boundaries
        """
        return self.load_shapefile("SP_RG_Imediatas_2024", simplify_tolerance=0.001)

    def load_intermediate_regions(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load IBGE intermediate regions shapefile (11 regions)

        Returns:
            GeoDataFrame with intermediate region boundaries
        """
        return self.load_shapefile("SP_RG_Intermediarias_2024", simplify_tolerance=0.001)

    def load_etes(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load wastewater treatment plants (ETEs) shapefile

        Returns:
            GeoDataFrame with ETE locations
        """
        return self.load_shapefile("ETEs_2019_SP", simplify_tolerance=0)

    def load_power_substations(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load power substations shapefile

        Returns:
            GeoDataFrame with power substation locations
        """
        return self.load_shapefile("Subestacoes_Energia", simplify_tolerance=0)

    def load_transmission_lines(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load electricity transmission lines shapefile

        Returns:
            GeoDataFrame with transmission line geometries
        """
        return self.load_shapefile("Linhas_De_Transmissao_Energia", simplify_tolerance=0.0001)

    def load_apps_hidrography(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load permanent preservation areas and hydrography shapefile

        Returns:
            GeoDataFrame with APPs and hydrographic features
        """
        return self.load_shapefile("APPs_Hidrografia", simplify_tolerance=0.001)

    def load_highways(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load state highways shapefile

        Returns:
            GeoDataFrame with highway geometries
        """
        return self.load_shapefile("Rodovias_Estaduais_SP", simplify_tolerance=0.0001)

    def load_urban_areas(self) -> Optional[gpd.GeoDataFrame]:
        """
        Load urban areas shapefile

        Returns:
            GeoDataFrame with urban area boundaries
        """
        return self.load_shapefile("Areas_Urbanas_SP", simplify_tolerance=0.001)

    def load_regional_boundaries(self, region_type: str = "both") -> Optional[gpd.GeoDataFrame]:
        """
        Load regional boundaries (immediate, intermediate, or both)

        Args:
            region_type: "immediate", "intermediate", or "both"

        Returns:
            GeoDataFrame with regional boundaries
        """
        if region_type == "immediate":
            return self.load_immediate_regions()
        elif region_type == "intermediate":
            return self.load_intermediate_regions()
        elif region_type == "both":
            immediate = self.load_immediate_regions()
            intermediate = self.load_intermediate_regions()

            if immediate is not None and intermediate is not None:
                # Add region type identifier
                immediate = immediate.copy()
                intermediate = intermediate.copy()
                immediate['region_type'] = 'immediate'
                intermediate['region_type'] = 'intermediate'

                # Combine both region types
                combined = pd.concat([intermediate, immediate], ignore_index=True)
                return gpd.GeoDataFrame(combined, crs=immediate.crs)
            elif immediate is not None:
                return immediate
            elif intermediate is not None:
                return intermediate

        return None

    def get_available_shapefiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available shapefiles

        Returns:
            Dictionary with shapefile information
        """
        shapefiles = {}

        for shp_file in self.data_dir.glob("*.shp"):
            name = shp_file.stem
            size_mb = shp_file.stat().st_size / (1024 * 1024)

            shapefiles[name] = {
                "path": shp_file,
                "size_mb": round(size_mb, 2),
                "exists": True
            }

        return shapefiles

    def validate_shapefile(self, filename: str) -> bool:
        """
        Validate if shapefile exists and is readable

        Args:
            filename: Shapefile name (without extension)

        Returns:
            True if shapefile is valid
        """
        try:
            shapefile_path = self.data_dir / f"{filename}.shp"
            if not shapefile_path.exists():
                return False

            # Try to read basic info without loading full data
            gdf = gpd.read_file(shapefile_path, rows=1)
            return len(gdf) >= 0

        except Exception as e:
            self.logger.error(f"Shapefile validation failed for {filename}: {e}")
            return False


# Global instance for easy access
shapefile_loader = ShapefileLoader()