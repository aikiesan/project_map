"""
CP2B Maps V2 - Application Settings
Professional configuration management system
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AppSettings:
    """
    Central configuration class for CP2B Maps V2
    Manages all application settings in one place
    """

    # Application Info
    APP_NAME: str = "CP2B Maps V2"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Professional biogas potential analysis platform"

    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    CACHE_DIR: Path = BASE_DIR / ".cache"

    # Streamlit Configuration
    PAGE_TITLE: str = "CP2B Maps V2 🗺️"
    PAGE_ICON: str = "🗺️"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"

    # Performance Settings
    CACHE_TTL: int = 3600  # 1 hour
    MAX_MUNICIPALITIES: int = 50
    SIMPLIFY_TOLERANCE: float = 0.001

    # Logging
    LOG_LEVEL: str = os.getenv("CP2B_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Map Settings
    DEFAULT_CENTER: tuple = (-23.5505, -46.6333)  # São Paulo
    DEFAULT_ZOOM: int = 7

    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        for dir_path in [cls.DATA_DIR, cls.ASSETS_DIR, cls.CACHE_DIR]:
            dir_path.mkdir(exist_ok=True, parents=True)

    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """Get full path for data file"""
        return cls.DATA_DIR / filename

    @classmethod
    def get_asset_path(cls, filename: str) -> Path:
        """Get full path for asset file"""
        return cls.ASSETS_DIR / filename


# Global settings instance
settings = AppSettings()

# Create directories on import
settings.create_directories()