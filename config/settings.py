"""
CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas
Professional configuration management system
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AppSettings:
    """
    Central configuration class for CP2B Maps
    Manages all application settings in one place
    """

    # Application Info
    APP_NAME: str = "CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Plataforma profissional de análise de potencial de geração de biogás para municípios do Estado de São Paulo"

    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    CACHE_DIR: Path = BASE_DIR / ".cache"
    RASTER_DIR: Path = DATA_DIR / "rasters"
    SHAPEFILE_DIR: Path = DATA_DIR / "shapefile"

    # Streamlit Configuration
    PAGE_TITLE: str = "CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás 🗺️"
    PAGE_ICON: str = "🗺️"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"

    # Performance Settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_MUNICIPALITIES: int = 50
    SIMPLIFY_TOLERANCE: float = 0.001

    # Raster Processing Settings
    MAX_RASTER_SIZE: int = 1536  # Maximum raster dimension for performance
    RASTER_OPACITY_DEFAULT: float = 0.7
    MIN_ANALYSIS_AREA_HA: float = 0.01  # Minimum area threshold in hectares
    DEFAULT_ANALYSIS_RADIUS_KM: float = 50.0

    # MapBiomas Settings
    MAPBIOMAS_DEFAULT_CLASSES: list = None  # None = all classes, or list of class IDs
    MAPBIOMAS_LEGEND_LANGUAGE: str = 'pt'  # 'pt' or 'en'

    # Logging
    LOG_LEVEL: str = os.getenv("CP2B_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Map Settings
    DEFAULT_CENTER: tuple = (-22.5, -48.5)  # São Paulo State center (matches V1)
    DEFAULT_ZOOM: int = 7

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        for dir_path in [cls.DATA_DIR, cls.ASSETS_DIR, cls.CACHE_DIR, cls.RASTER_DIR, cls.SHAPEFILE_DIR]:
            dir_path.mkdir(exist_ok=True, parents=True)

    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """Get full path for data file"""
        return cls.DATA_DIR / filename

    @classmethod
    def get_asset_path(cls, filename: str) -> Path:
        """Get full path for asset file"""
        return cls.ASSETS_DIR / filename

    @classmethod
    def get_raster_path(cls, filename: str) -> Path:
        """Get full path for raster file"""
        return cls.RASTER_DIR / filename

    @classmethod
    def get_shapefile_path(cls, filename: str) -> Path:
        """Get full path for shapefile"""
        return cls.SHAPEFILE_DIR / filename


# Global settings instance
settings = AppSettings()

# Create directories on import
settings.create_directories()