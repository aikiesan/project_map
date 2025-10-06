"""
CP2B Maps - Professional Raster Loader
High-performance geospatial raster processing with smart caching and optimization
"""

import os
import base64
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, Union
from io import BytesIO
from functools import lru_cache
import streamlit as st

# Geospatial imports with error handling
try:
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    from rasterio.enums import ColorInterp
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    rasterio = None

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class RasterLoader:
    """
    Professional raster data loader with V2 architecture integration
    Features: Smart caching, memory optimization, error handling, CRS conversion
    """

    def __init__(self, raster_dir: Optional[Path] = None):
        """
        Initialize RasterLoader with raster directory

        Args:
            raster_dir: Path to raster directory (defaults to settings.DATA_DIR/rasters)
        """
        self.raster_dir = raster_dir or settings.DATA_DIR / "rasters"
        self.logger = get_logger(self.__class__.__name__)

        # Validate dependencies
        if not HAS_RASTERIO:
            self.logger.error("rasterio not available - raster functionality disabled")
            raise ImportError("rasterio required for raster processing")

        if not HAS_PIL:
            self.logger.warning("PIL not available - image processing may be limited")

        # Create raster directory if it doesn't exist
        if not self.raster_dir.exists():
            self.logger.info(f"Creating raster directory: {self.raster_dir}")
            self.raster_dir.mkdir(parents=True, exist_ok=True)

    def get_raster_path(self, filename: str) -> Path:
        """
        Get full path for raster file

        Args:
            filename: Raster filename

        Returns:
            Path object for the raster file
        """
        return self.raster_dir / filename

    @st.cache_data(ttl=settings.CACHE_TTL)
    def load_raster(_self,
                   raster_path: Union[str, Path],
                   max_size: int = 1536,
                   target_crs: str = "EPSG:4326") -> Tuple[Optional[np.ndarray], Optional[Dict[str, Any]]]:
        """
        Load raster file with caching and optimization

        Args:
            raster_path: Path to raster file
            max_size: Maximum size for performance optimization
            target_crs: Target coordinate reference system

        Returns:
            Tuple of (raster_data, metadata) or (None, None) on error
        """
        try:
            raster_path = Path(raster_path)

            if not raster_path.exists():
                _self.logger.warning(f"Raster file not found: {raster_path}")
                return None, None

            _self.logger.info(f"Loading raster: {raster_path}")

            with rasterio.open(raster_path) as src:
                # Get basic info
                profile = src.profile.copy()
                height, width = src.height, src.width

                # Calculate scaling for performance
                scale_factor = 1.0
                if max(height, width) > max_size:
                    scale_factor = max_size / max(height, width)
                    new_height = int(height * scale_factor)
                    new_width = int(width * scale_factor)

                    # Read with resampling
                    data = src.read(
                        out_shape=(src.count, new_height, new_width),
                        resampling=Resampling.nearest
                    )[0]  # First band

                    _self.logger.info(f"Raster resampled from {width}x{height} to {new_width}x{new_height}")
                else:
                    # Read at original resolution
                    data = src.read(1)

                # Prepare metadata
                metadata = {
                    'filename': raster_path.name,
                    'width': data.shape[1] if len(data.shape) > 1 else data.shape[0],
                    'height': data.shape[0] if len(data.shape) > 1 else 1,
                    'crs': str(profile.get('crs', target_crs)),
                    'transform': profile.get('transform'),
                    'bounds': src.bounds,
                    'dtype': str(data.dtype),
                    'scale_factor': scale_factor,
                    'original_size': (width, height),
                    'nodata': profile.get('nodata'),
                    'size_mb': round(raster_path.stat().st_size / (1024*1024), 2)
                }

                _self.logger.info(f"Successfully loaded raster: {raster_path.name}")
                return data, metadata

        except Exception as e:
            _self.logger.error(f"Error loading raster {raster_path}: {e}")
            return None, None

    def get_raster_info(self, raster_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Get raster information without loading data

        Args:
            raster_path: Path to raster file

        Returns:
            Dictionary with raster information or None
        """
        try:
            raster_path = Path(raster_path)

            if not raster_path.exists():
                return None

            with rasterio.open(raster_path) as src:
                return {
                    'filename': raster_path.name,
                    'width': src.width,
                    'height': src.height,
                    'count': src.count,
                    'dtype': str(src.dtypes[0]),
                    'crs': str(src.crs),
                    'bounds': src.bounds,
                    'transform': src.transform,
                    'size_mb': round(raster_path.stat().st_size / (1024*1024), 2),
                    'nodata': src.nodata
                }

        except Exception as e:
            self.logger.error(f"Error getting raster info for {raster_path}: {e}")
            return None

    def list_available_rasters(self, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """
        List all available raster files with metadata

        Args:
            extensions: List of file extensions to search for

        Returns:
            List of dictionaries with raster information
        """
        if extensions is None:
            extensions = ['.tif', '.tiff', '.geotiff']

        rasters = []

        try:
            for ext in extensions:
                # Search case-insensitive
                for pattern in [f"*{ext}", f"*{ext.upper()}"]:
                    for raster_path in self.raster_dir.glob(pattern):
                        info = self.get_raster_info(raster_path)
                        if info:
                            info['path'] = str(raster_path)
                            rasters.append(info)

            if len(rasters) == 0:
                self.logger.warning(f"Found {len(rasters)} raster files in {self.raster_dir}")
                self.logger.info("To use raster analysis features, add .tif/.tiff files to the rasters directory")
                self.logger.info(f"Raster directory: {self.raster_dir}")
            else:
                self.logger.info(f"Found {len(rasters)} raster files")

            return sorted(rasters, key=lambda x: x['filename'])

        except Exception as e:
            self.logger.error(f"Error listing rasters: {e}")
            return []

    def create_base64_image(self, data: np.ndarray, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Convert raster data to base64 image for web display

        Args:
            data: Raster data array
            metadata: Raster metadata

        Returns:
            Base64 encoded image string or None
        """
        if not HAS_PIL:
            self.logger.error("PIL required for image conversion")
            return None

        try:
            # Normalize data to 0-255 range
            if data.dtype != np.uint8:
                # Handle nodata values
                if metadata.get('nodata') is not None:
                    data_clean = np.where(data == metadata['nodata'], np.nan, data)
                else:
                    data_clean = data.copy()

                # Normalize to 0-255
                valid_data = data_clean[~np.isnan(data_clean)]
                if len(valid_data) > 0:
                    min_val, max_val = np.min(valid_data), np.max(valid_data)
                    if max_val > min_val:
                        normalized = ((data_clean - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                    else:
                        normalized = np.full_like(data_clean, 127, dtype=np.uint8)
                else:
                    normalized = np.zeros_like(data_clean, dtype=np.uint8)

                # Handle NaN values
                normalized = np.nan_to_num(normalized, nan=0)
            else:
                normalized = data

            # Convert to PIL Image
            if len(normalized.shape) == 2:
                # Grayscale
                img = Image.fromarray(normalized, mode='L')
            else:
                self.logger.warning("Multi-band raster conversion not fully implemented")
                img = Image.fromarray(normalized, mode='L')

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            img_str = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            self.logger.error(f"Error creating base64 image: {e}")
            return None


# Factory function for easy access
@st.cache_resource
def get_raster_loader() -> RasterLoader:
    """
    Get cached RasterLoader instance

    Returns:
        RasterLoader instance
    """
    return RasterLoader()


# Convenience functions
def load_raster_data(filename: str, **kwargs) -> Tuple[Optional[np.ndarray], Optional[Dict[str, Any]]]:
    """
    Convenience function to load raster data

    Args:
        filename: Raster filename
        **kwargs: Additional arguments for load_raster

    Returns:
        Tuple of (raster_data, metadata)
    """
    loader = get_raster_loader()
    raster_path = loader.get_raster_path(filename)
    return loader.load_raster(raster_path, **kwargs)


def list_raster_files() -> List[Dict[str, Any]]:
    """
    Convenience function to list available rasters

    Returns:
        List of raster information dictionaries
    """
    loader = get_raster_loader()
    return loader.list_available_rasters()