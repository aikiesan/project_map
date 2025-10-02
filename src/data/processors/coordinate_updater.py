"""
CP2B Maps V2 - Coordinate Updater
Focused on municipality coordinate management and updates
Extracted from DataProcessor for Single Responsibility
"""

import sqlite3
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class CoordinateUpdater:
    """
    Municipality coordinate management and updates
    
    Responsibilities:
    - Update coordinates from shapefiles
    - Validate coordinate ranges
    - Batch coordinate updates
    - Calculate centroids from geometries
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize CoordinateUpdater
        
        Args:
            db_path: Path to SQLite database (uses settings default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = db_path or (settings.DATA_DIR / "database" / "cp2b_maps.db")
        
        if not self.db_path.exists():
            self.logger.warning(f"Database not found: {self.db_path}")

    def update_from_shapefile(self, shapefile_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Add or update municipality coordinates from shapefile centroids
        
        Args:
            shapefile_path: Path to municipality shapefile
        
        Returns:
            Dictionary with coordinate update results
        """
        try:
            self.logger.info("Starting coordinate update from shapefile")
            
            # Default shapefile path
            if not shapefile_path:
                shapefile_path = settings.SHAPEFILE_DIR / "SP_Municipios_2024.shp"
            
            shapefile_path = Path(shapefile_path)
            if not shapefile_path.exists():
                raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
            
            results = {
                'update_date': datetime.now(),
                'shapefile_path': str(shapefile_path),
                'municipalities_processed': 0,
                'coordinates_updated': 0,
                'coordinate_range': {}
            }
            
            # Load shapefile and calculate centroids
            gdf = gpd.read_file(shapefile_path)
            self.logger.info(f"Loaded {len(gdf)} municipalities from shapefile")
            
            # Convert to WGS84 if necessary
            if gdf.crs != 'EPSG:4326':
                self.logger.info(f"Converting from {gdf.crs} to EPSG:4326")
                gdf = gdf.to_crs('EPSG:4326')
            
            # Calculate centroids
            centroids = gdf.geometry.centroid
            gdf['lon'] = centroids.x
            gdf['lat'] = centroids.y
            
            # Prepare coordinate data
            # Try different possible column names for municipality code
            code_col = None
            for col in ['CD_MUN', 'cd_mun', 'codigo_municipio', 'CODIGO']:
                if col in gdf.columns:
                    code_col = col
                    break
            
            if not code_col:
                raise ValueError("Could not find municipality code column in shapefile")
            
            coords_df = gdf[[code_col, 'lat', 'lon']].copy()
            coords_df[code_col] = coords_df[code_col].astype(str)
            coords_df = coords_df.rename(columns={code_col: 'codigo_municipio'})
            
            results['municipalities_processed'] = len(coords_df)
            results['coordinate_range'] = {
                'lat_min': float(coords_df['lat'].min()),
                'lat_max': float(coords_df['lat'].max()),
                'lon_min': float(coords_df['lon'].min()),
                'lon_max': float(coords_df['lon'].max())
            }
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                # Ensure coordinate columns exist
                self._ensure_coordinate_columns(conn)
                
                # Update coordinates
                updated_count = self._update_coordinates(conn, coords_df)
                results['coordinates_updated'] = updated_count
            
            self.logger.info(f"Coordinate update completed: {updated_count} municipalities updated")
            return results
        
        except Exception as e:
            self.logger.error(f"Error updating coordinates: {e}", exc_info=True)
            return {'error': str(e), 'update_date': datetime.now()}

    def batch_update_coordinates(self, updates: Dict[str, Tuple[float, float]]) -> int:
        """
        Batch update coordinates for multiple municipalities
        
        Args:
            updates: Dictionary mapping municipality_code to (lat, lon) tuples
        
        Returns:
            Number of municipalities updated
        """
        try:
            self.logger.info(f"Starting batch coordinate update for {len(updates)} municipalities")
            
            with sqlite3.connect(self.db_path) as conn:
                # Ensure coordinate columns exist
                self._ensure_coordinate_columns(conn)
                
                updated_count = 0
                cursor = conn.cursor()
                
                for municipio_code, (lat, lon) in updates.items():
                    # Validate coordinates
                    if not self._validate_coordinate(lat, lon):
                        self.logger.warning(f"Invalid coordinates for {municipio_code}: ({lat}, {lon})")
                        continue
                    
                    cursor.execute("""
                        UPDATE municipalities
                        SET lat = ?, lon = ?
                        WHERE codigo_municipio = ?
                    """, (lat, lon, str(municipio_code)))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                
                conn.commit()
            
            self.logger.info(f"Batch update completed: {updated_count}/{len(updates)} municipalities updated")
            return updated_count
        
        except Exception as e:
            self.logger.error(f"Error in batch coordinate update: {e}")
            return 0

    def update_single_coordinate(self, municipality_code: str, lat: float, lon: float) -> bool:
        """
        Update coordinates for a single municipality
        
        Args:
            municipality_code: Municipality code
            lat: Latitude
            lon: Longitude
        
        Returns:
            True if update was successful
        """
        try:
            # Validate coordinates
            if not self._validate_coordinate(lat, lon):
                self.logger.error(f"Invalid coordinates: ({lat}, {lon})")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                # Ensure coordinate columns exist
                self._ensure_coordinate_columns(conn)
                
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE municipalities
                    SET lat = ?, lon = ?
                    WHERE codigo_municipio = ?
                """, (lat, lon, str(municipality_code)))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated coordinates for municipality {municipality_code}")
                    return True
                else:
                    self.logger.warning(f"Municipality not found: {municipality_code}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Error updating single coordinate: {e}")
            return False

    def get_missing_coordinates(self) -> List[str]:
        """
        Get list of municipalities with missing coordinates
        
        Returns:
            List of municipality codes with missing coordinates
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo_municipio 
                    FROM municipalities
                    WHERE lat IS NULL OR lon IS NULL
                    ORDER BY nome_municipio
                """)
                
                missing = [row[0] for row in cursor.fetchall()]
                
                if missing:
                    self.logger.info(f"Found {len(missing)} municipalities with missing coordinates")
                
                return missing
        
        except Exception as e:
            self.logger.error(f"Error getting missing coordinates: {e}")
            return []

    def validate_all_coordinates(self) -> Dict[str, Any]:
        """
        Validate all coordinates in the database
        
        Returns:
            Dictionary with validation results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all coordinates
                cursor.execute("""
                    SELECT codigo_municipio, nome_municipio, lat, lon
                    FROM municipalities
                    WHERE lat IS NOT NULL AND lon IS NOT NULL
                """)
                
                all_coords = cursor.fetchall()
                invalid_coords = []
                
                for code, name, lat, lon in all_coords:
                    if not self._validate_coordinate(lat, lon):
                        invalid_coords.append({
                            'codigo': code,
                            'nome': name,
                            'lat': lat,
                            'lon': lon
                        })
                
                return {
                    'total_with_coords': len(all_coords),
                    'invalid_count': len(invalid_coords),
                    'invalid_coords': invalid_coords,
                    'validation_passed': len(invalid_coords) == 0
                }
        
        except Exception as e:
            self.logger.error(f"Error validating coordinates: {e}")
            return {'error': str(e)}

    # Helper methods
    
    def _ensure_coordinate_columns(self, conn: sqlite3.Connection) -> None:
        """
        Ensure lat/lon columns exist in municipalities table
        
        Args:
            conn: SQLite database connection
        """
        try:
            conn.execute('ALTER TABLE municipalities ADD COLUMN lat REAL')
            self.logger.debug("Added 'lat' column to municipalities table")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute('ALTER TABLE municipalities ADD COLUMN lon REAL')
            self.logger.debug("Added 'lon' column to municipalities table")
        except sqlite3.OperationalError:
            pass  # Column already exists

    def _update_coordinates(self, conn: sqlite3.Connection, coords_df) -> int:
        """
        Update municipality coordinates from DataFrame
        
        Args:
            conn: SQLite database connection
            coords_df: DataFrame with codigo_municipio, lat, lon columns
        
        Returns:
            Number of municipalities updated
        """
        updated_count = 0
        cursor = conn.cursor()
        
        for _, row in coords_df.iterrows():
            cursor.execute("""
                UPDATE municipalities
                SET lat = ?, lon = ?
                WHERE codigo_municipio = ?
            """, (row['lat'], row['lon'], row['codigo_municipio']))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        return updated_count

    def _validate_coordinate(self, lat: float, lon: float) -> bool:
        """
        Validate if coordinates are within São Paulo state boundaries
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            True if coordinates are valid
        """
        # São Paulo state approximate boundaries
        # Latitude: -25.5 to -19.5
        # Longitude: -53.5 to -44.0
        
        if not (-25.5 <= lat <= -19.5):
            return False
        
        if not (-53.5 <= lon <= -44.0):
            return False
        
        return True


# Factory function
def get_coordinate_updater(db_path: Optional[Path] = None) -> CoordinateUpdater:
    """
    Factory function to create CoordinateUpdater instance
    
    Args:
        db_path: Optional path to database file
    
    Returns:
        CoordinateUpdater instance
    """
    return CoordinateUpdater(db_path)

