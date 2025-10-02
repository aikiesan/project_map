"""
Data access layer for shapefiles, rasters, and database operations
"""

from .loaders.shapefile_loader import ShapefileLoader, shapefile_loader
from .loaders.database_loader import DatabaseLoader, get_database_loader

# Backward compatibility: provide default instance via factory
database_loader = get_database_loader()

__all__ = ["ShapefileLoader", "shapefile_loader", "DatabaseLoader", "get_database_loader", "database_loader"]