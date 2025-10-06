"""
CP2B Maps - Data Processing Module
Comprehensive data processing utilities for database maintenance and updates
Consolidated from V1 processing scripts with enhanced functionality
"""

import sqlite3
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import json

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DataProcessor:
    """
    Comprehensive data processing engine for CP2B Maps database maintenance
    Features: Database validation, coordinate updates, biogas recalculation, data migration
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize Data Processor"""
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = db_path or settings.database.path

        # Conversion factors for biogas calculations
        self.default_conversion_factors = {
            'cattle': 225.0,  # m³/head/year
            'swine': 210.0,   # m³/head/year
            'poultry': 34.0,  # m³/head/year
            'coffee': 150.0,  # m³/ton/year
            'sugarcane': 200.0,  # m³/ton/year
            'corn': 225.0,    # m³/ton/year
            'soybean': 180.0, # m³/ton/year
            'citrus': 120.0,  # m³/ton/year
            'urban_waste': 117.0,  # m³/inhabitant/year
            'industrial_waste': 7.0,  # m³/inhabitant/year
            'aquaculture': 62.0  # m³/ton fish/year
        }

    def validate_database(self, census_csv_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate and update database with latest census data

        Args:
            census_csv_path: Path to census CSV file

        Returns:
            Dictionary with validation results
        """
        try:
            self.logger.info("Starting database validation process")

            results = {
                'validation_date': datetime.now(),
                'updates_made': [],
                'errors': [],
                'statistics': {}
            }

            with sqlite3.connect(self.db_path) as conn:
                # Check database structure
                structure_check = self._validate_database_structure(conn)
                results['structure_check'] = structure_check

                # Update with census data if provided
                if census_csv_path and Path(census_csv_path).exists():
                    census_update = self._update_with_census_data(conn, census_csv_path)
                    results['census_update'] = census_update
                    results['updates_made'].extend(census_update.get('updates', []))

                # Validate data quality
                quality_check = self._validate_data_quality(conn)
                results['quality_check'] = quality_check

                # Generate statistics
                results['statistics'] = self._generate_database_statistics(conn)

            self.logger.info("Database validation completed successfully")
            return results

        except Exception as e:
            self.logger.error(f"Error during database validation: {e}")
            return {'error': str(e), 'validation_date': datetime.now()}

    def recalculate_biogas_potentials(self,
                                    custom_factors: Optional[Dict[str, float]] = None,
                                    create_backup: bool = True) -> Dict[str, Any]:
        """
        Recalculate biogas potentials using updated conversion factors

        Args:
            custom_factors: Custom conversion factors to use
            create_backup: Whether to create backup before changes

        Returns:
            Dictionary with recalculation results
        """
        try:
            self.logger.info("Starting biogas potential recalculation")

            # Use custom factors or defaults
            factors = custom_factors if custom_factors else self.default_conversion_factors

            results = {
                'calculation_date': datetime.now(),
                'factors_used': factors,
                'backup_table': None,
                'municipalities_updated': 0,
                'total_potential_before': 0,
                'total_potential_after': 0
            }

            with sqlite3.connect(self.db_path) as conn:
                # Create backup if requested
                if create_backup:
                    backup_table = self._create_backup_table(conn)
                    results['backup_table'] = backup_table

                # Get current totals
                current_totals = self._calculate_current_totals(conn)
                results['total_potential_before'] = current_totals

                # Recalculate biogas potentials
                updates_made = self._recalculate_all_potentials(conn, factors)
                results['municipalities_updated'] = updates_made

                # Get new totals
                new_totals = self._calculate_current_totals(conn)
                results['total_potential_after'] = new_totals

                # Update conversion factors table
                self._update_conversion_factors_table(conn, factors)

            self.logger.info(f"Biogas recalculation completed: {updates_made} municipalities updated")
            return results

        except Exception as e:
            self.logger.error(f"Error during biogas recalculation: {e}")
            return {'error': str(e), 'calculation_date': datetime.now()}

    def add_coordinates_from_shapefile(self, shapefile_path: Optional[str] = None) -> Dict[str, Any]:
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
                shapefile_path = Path(settings.data_dir) / "shapefile" / "SP_Municipios_2024.shp"

            if not Path(shapefile_path).exists():
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
            coords_df = gdf[['CD_MUN', 'NM_MUN', 'lat', 'lon']].copy()
            coords_df['CD_MUN'] = coords_df['CD_MUN'].astype(str)

            results['municipalities_processed'] = len(coords_df)
            results['coordinate_range'] = {
                'lat_min': float(coords_df['lat'].min()),
                'lat_max': float(coords_df['lat'].max()),
                'lon_min': float(coords_df['lon'].min()),
                'lon_max': float(coords_df['lon'].max())
            }

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                # Add coordinate columns if they don't exist
                self._ensure_coordinate_columns(conn)

                # Update coordinates
                updated_count = self._update_municipality_coordinates(conn, coords_df)
                results['coordinates_updated'] = updated_count

            self.logger.info(f"Coordinate update completed: {updated_count} municipalities updated")
            return results

        except Exception as e:
            self.logger.error(f"Error updating coordinates: {e}")
            return {'error': str(e), 'update_date': datetime.now()}

    def estimate_zero_municipalities(self,
                                   estimation_method: str = 'regional_average') -> Dict[str, Any]:
        """
        Estimate biogas potential for municipalities with zero values

        Args:
            estimation_method: Method for estimation ('regional_average', 'population_based', 'area_based')

        Returns:
            Dictionary with estimation results
        """
        try:
            self.logger.info(f"Starting zero municipality estimation using {estimation_method}")

            results = {
                'estimation_date': datetime.now(),
                'method_used': estimation_method,
                'municipalities_estimated': 0,
                'estimated_values': {}
            }

            with sqlite3.connect(self.db_path) as conn:
                # Identify municipalities with zero biogas potential
                zero_municipalities = self._identify_zero_municipalities(conn)

                if len(zero_municipalities) == 0:
                    self.logger.info("No municipalities with zero biogas potential found")
                    return results

                self.logger.info(f"Found {len(zero_municipalities)} municipalities with zero biogas potential")

                # Apply estimation method
                if estimation_method == 'regional_average':
                    estimates = self._estimate_by_regional_average(conn, zero_municipalities)
                elif estimation_method == 'population_based':
                    estimates = self._estimate_by_population(conn, zero_municipalities)
                elif estimation_method == 'area_based':
                    estimates = self._estimate_by_area(conn, zero_municipalities)
                else:
                    raise ValueError(f"Unknown estimation method: {estimation_method}")

                # Update database with estimates
                updated_count = self._apply_estimations(conn, estimates)

                results['municipalities_estimated'] = updated_count
                results['estimated_values'] = {k: float(v) for k, v in estimates.items()}

            self.logger.info(f"Zero municipality estimation completed: {updated_count} municipalities estimated")
            return results

        except Exception as e:
            self.logger.error(f"Error estimating zero municipalities: {e}")
            return {'error': str(e), 'estimation_date': datetime.now()}

    def update_key_factors(self, new_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Update key conversion factors in the database

        Args:
            new_factors: Dictionary of factor_name: value pairs

        Returns:
            Dictionary with update results
        """
        try:
            self.logger.info("Updating key conversion factors")

            results = {
                'update_date': datetime.now(),
                'factors_updated': 0,
                'previous_factors': {},
                'new_factors': new_factors
            }

            with sqlite3.connect(self.db_path) as conn:
                # Get current factors
                current_factors = self._get_current_conversion_factors(conn)
                results['previous_factors'] = current_factors

                # Update factors
                updated_count = self._update_conversion_factors_table(conn, new_factors)
                results['factors_updated'] = updated_count

                # Update municipalities table with new calculations
                if updated_count > 0:
                    self.recalculate_biogas_potentials(new_factors, create_backup=True)

            self.logger.info(f"Key factors update completed: {updated_count} factors updated")
            return results

        except Exception as e:
            self.logger.error(f"Error updating key factors: {e}")
            return {'error': str(e), 'update_date': datetime.now()}

    def perform_final_database_fix(self) -> Dict[str, Any]:
        """
        Perform final database fixes and optimizations

        Returns:
            Dictionary with fix results
        """
        try:
            self.logger.info("Starting final database fix and optimization")

            results = {
                'fix_date': datetime.now(),
                'fixes_applied': [],
                'optimizations': []
            }

            with sqlite3.connect(self.db_path) as conn:
                # Fix data type inconsistencies
                type_fixes = self._fix_data_types(conn)
                results['fixes_applied'].extend(type_fixes)

                # Remove duplicate records
                duplicate_fixes = self._remove_duplicates(conn)
                results['fixes_applied'].extend(duplicate_fixes)

                # Update null values
                null_fixes = self._fix_null_values(conn)
                results['fixes_applied'].extend(null_fixes)

                # Optimize database
                optimizations = self._optimize_database(conn)
                results['optimizations'].extend(optimizations)

                # Create indexes for performance
                index_creation = self._create_performance_indexes(conn)
                results['optimizations'].extend(index_creation)

            self.logger.info("Final database fix completed")
            return results

        except Exception as e:
            self.logger.error(f"Error during final database fix: {e}")
            return {'error': str(e), 'fix_date': datetime.now()}

    # Helper methods for internal operations

    def _validate_database_structure(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Validate database table structure"""
        try:
            cursor = conn.cursor()

            # Check if main tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('municipalities', 'conversion_factors')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]

            # Check municipalities table structure
            cursor.execute("PRAGMA table_info(municipalities)")
            municipalities_columns = [row[1] for row in cursor.fetchall()]

            required_columns = ['municipio', 'populacao', 'codigo_municipio']
            missing_columns = [col for col in required_columns if col not in municipalities_columns]

            return {
                'existing_tables': existing_tables,
                'municipalities_columns': municipalities_columns,
                'missing_columns': missing_columns,
                'structure_valid': len(missing_columns) == 0
            }

        except Exception as e:
            self.logger.error(f"Error validating database structure: {e}")
            return {'error': str(e)}

    def _update_with_census_data(self, conn: sqlite3.Connection, csv_path: str) -> Dict[str, Any]:
        """Update database with census data"""
        try:
            # Load census data
            census_df = pd.read_csv(csv_path)

            # Clean and prepare data
            census_df.columns = census_df.columns.str.strip()

            # Handle Brazilian number format
            for col in census_df.columns:
                if 'Area' in col or 'Densidade' in col:
                    census_df[col] = (census_df[col].astype(str)
                                    .str.replace(',', '.')
                                    .astype(float))

            # Rename columns to match database schema
            column_mapping = {
                'CD_MUN': 'codigo_municipio',
                'NM_MUN': 'nome_municipio',
                'Populacao_Residente_2022': 'populacao',
                'Area_Da_Unidade_territorial_km²': 'area_km2',
                'Densidade_Demografica_2022': 'densidade_demografica'
            }

            census_df = census_df.rename(columns=column_mapping)
            census_df['codigo_municipio'] = census_df['codigo_municipio'].astype(str)

            # Update database
            updates_made = []
            for _, row in census_df.iterrows():
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE municipalities
                    SET populacao = ?, area_km2 = ?, densidade_demografica = ?
                    WHERE codigo_municipio = ?
                """, (row['populacao'], row.get('area_km2'),
                     row.get('densidade_demografica'), row['codigo_municipio']))

                if cursor.rowcount > 0:
                    updates_made.append(row['codigo_municipio'])

            conn.commit()

            return {
                'updates': updates_made,
                'total_updated': len(updates_made),
                'census_records': len(census_df)
            }

        except Exception as e:
            self.logger.error(f"Error updating with census data: {e}")
            return {'error': str(e)}

    def _validate_data_quality(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Validate data quality and identify issues"""
        try:
            cursor = conn.cursor()

            # Check for null values in critical columns
            cursor.execute("""
                SELECT COUNT(*) as null_municipio FROM municipalities WHERE municipio IS NULL
            """)
            null_municipio = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) as null_populacao FROM municipalities WHERE populacao IS NULL
            """)
            null_populacao = cursor.fetchone()[0]

            # Check for duplicate municipalities
            cursor.execute("""
                SELECT codigo_municipio, COUNT(*) as count
                FROM municipalities
                GROUP BY codigo_municipio
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()

            # Check for invalid coordinates
            cursor.execute("""
                SELECT COUNT(*) as invalid_coords
                FROM municipalities
                WHERE lat IS NOT NULL AND lon IS NOT NULL
                AND (lat < -35 OR lat > 5 OR lon < -75 OR lon > -30)
            """)
            invalid_coords = cursor.fetchone()[0]

            return {
                'null_municipio': null_municipio,
                'null_populacao': null_populacao,
                'duplicate_count': len(duplicates),
                'duplicates': duplicates,
                'invalid_coordinates': invalid_coords,
                'quality_score': self._calculate_quality_score(null_municipio, null_populacao, len(duplicates), invalid_coords)
            }

        except Exception as e:
            self.logger.error(f"Error validating data quality: {e}")
            return {'error': str(e)}

    def _calculate_quality_score(self, null_municipio: int, null_populacao: int,
                                duplicates: int, invalid_coords: int) -> float:
        """Calculate overall data quality score (0-100)"""
        total_issues = null_municipio + null_populacao + duplicates + invalid_coords
        if total_issues == 0:
            return 100.0

        # Simple scoring: reduce score based on issues
        score = max(0, 100 - (total_issues * 5))  # 5 points per issue
        return score

    def _generate_database_statistics(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Generate comprehensive database statistics"""
        try:
            cursor = conn.cursor()

            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM municipalities")
            total_municipalities = cursor.fetchone()[0]

            # Biogas potential statistics
            biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                            if 'biogas' in col.lower() and 'nm_ano' in col]

            stats = {
                'total_municipalities': total_municipalities,
                'biogas_columns': len(biogas_columns),
                'table_size_mb': self._get_table_size(conn, 'municipalities'),
                'last_updated': datetime.now().isoformat()
            }

            # Calculate biogas totals
            if biogas_columns:
                biogas_totals = {}
                for col in biogas_columns:
                    cursor.execute(f"SELECT SUM({col}) FROM municipalities WHERE {col} IS NOT NULL")
                    total = cursor.fetchone()[0] or 0
                    biogas_totals[col] = total

                stats['biogas_totals'] = biogas_totals
                stats['total_biogas_potential'] = sum(biogas_totals.values())

            return stats

        except Exception as e:
            self.logger.error(f"Error generating database statistics: {e}")
            return {'error': str(e)}

    def _create_backup_table(self, conn: sqlite3.Connection) -> str:
        """Create backup table with timestamp"""
        backup_table = f"municipalities_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        conn.execute(f"""
            CREATE TABLE {backup_table} AS
            SELECT * FROM municipalities
        """)

        self.logger.info(f"Backup created: {backup_table}")
        return backup_table

    def _calculate_current_totals(self, conn: sqlite3.Connection) -> float:
        """Calculate current total biogas potential"""
        try:
            biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                            if 'biogas' in col.lower() and 'nm_ano' in col]

            if not biogas_columns:
                return 0.0

            total = 0.0
            for col in biogas_columns:
                cursor = conn.cursor()
                cursor.execute(f"SELECT SUM({col}) FROM municipalities WHERE {col} IS NOT NULL")
                col_total = cursor.fetchone()[0] or 0
                total += col_total

            return total

        except Exception as e:
            self.logger.error(f"Error calculating current totals: {e}")
            return 0.0

    def _recalculate_all_potentials(self, conn: sqlite3.Connection, factors: Dict[str, float]) -> int:
        """Recalculate biogas potentials using new factors"""
        try:
            updates_made = 0

            # This is a simplified version - in practice, you'd need to map
            # specific columns to specific factors based on your data structure
            factor_mapping = {
                'biogas_bovinos_nm_ano': factors.get('cattle', 225.0),
                'biogas_suino_nm_ano': factors.get('swine', 210.0),
                'biogas_aves_nm_ano': factors.get('poultry', 34.0),
                'biogas_cafe_nm_ano': factors.get('coffee', 150.0),
                'biogas_cana_nm_ano': factors.get('sugarcane', 200.0),
                'biogas_milho_nm_ano': factors.get('corn', 225.0),
                'biogas_soja_nm_ano': factors.get('soybean', 180.0),
                'biogas_citros_nm_ano': factors.get('citrus', 120.0),
                'rsu_potencial_nm_ano': factors.get('urban_waste', 117.0),
                'rpo_potencial_nm_ano': factors.get('industrial_waste', 7.0),
                'biogas_piscicultura_nm_ano': factors.get('aquaculture', 62.0)
            }

            cursor = conn.cursor()
            cursor.execute("SELECT codigo_municipio FROM municipalities")
            municipalities = cursor.fetchall()

            for (codigo_municipio,) in municipalities:
                # In a real implementation, you would recalculate based on
                # source data (livestock counts, crop production, etc.)
                # For now, we'll just apply a factor adjustment

                for column, factor in factor_mapping.items():
                    # Check if column exists
                    if column in self._get_table_columns(conn, 'municipalities'):
                        # Simple factor-based adjustment (this would be more complex in reality)
                        cursor.execute(f"""
                            UPDATE municipalities
                            SET {column} = COALESCE({column}, 0) * ?
                            WHERE codigo_municipio = ?
                        """, (factor / 200.0, codigo_municipio))  # Normalize against base factor

                updates_made += 1

            conn.commit()
            return updates_made

        except Exception as e:
            self.logger.error(f"Error recalculating potentials: {e}")
            return 0

    def _update_conversion_factors_table(self, conn: sqlite3.Connection, factors: Dict[str, float]) -> int:
        """Update or create conversion factors table"""
        try:
            # Create table if it doesn't exist
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversion_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    final_factor REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, subcategory)
                )
            """)

            updates_made = 0
            for factor_name, value in factors.items():
                conn.execute("""
                    INSERT OR REPLACE INTO conversion_factors
                    (category, subcategory, final_factor, last_updated)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, ('biogas', factor_name, value))
                updates_made += 1

            conn.commit()
            return updates_made

        except Exception as e:
            self.logger.error(f"Error updating conversion factors table: {e}")
            return 0

    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Get list of columns for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    def _get_table_size(self, conn: sqlite3.Connection, table_name: str) -> float:
        """Get approximate table size in MB"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Rough estimate: 1KB per row
            size_mb = (row_count * 1024) / (1024 * 1024)
            return round(size_mb, 2)

        except Exception:
            return 0.0

    def _ensure_coordinate_columns(self, conn: sqlite3.Connection):
        """Ensure lat/lon columns exist in municipalities table"""
        try:
            conn.execute('ALTER TABLE municipalities ADD COLUMN lat REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            conn.execute('ALTER TABLE municipalities ADD COLUMN lon REAL')
        except sqlite3.OperationalError:
            pass  # Column already exists

    def _update_municipality_coordinates(self, conn: sqlite3.Connection, coords_df: pd.DataFrame) -> int:
        """Update municipality coordinates from dataframe"""
        updated_count = 0

        for _, row in coords_df.iterrows():
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE municipalities
                SET lat = ?, lon = ?
                WHERE codigo_municipio = ?
            """, (row['lat'], row['lon'], row['CD_MUN']))

            if cursor.rowcount > 0:
                updated_count += 1

        conn.commit()
        return updated_count

    def _identify_zero_municipalities(self, conn: sqlite3.Connection) -> List[str]:
        """Identify municipalities with zero biogas potential"""
        cursor = conn.cursor()

        biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                         if 'biogas' in col.lower() and 'nm_ano' in col]

        if not biogas_columns:
            return []

        # Build query to find municipalities where all biogas columns are zero or null
        conditions = []
        for col in biogas_columns:
            conditions.append(f"COALESCE({col}, 0) = 0")

        where_clause = " AND ".join(conditions)

        cursor.execute(f"""
            SELECT codigo_municipio
            FROM municipalities
            WHERE {where_clause}
        """)

        return [row[0] for row in cursor.fetchall()]

    def _estimate_by_regional_average(self, conn: sqlite3.Connection, zero_municipalities: List[str]) -> Dict[str, float]:
        """Estimate biogas potential using regional averages"""
        # This is a simplified implementation
        # In practice, you'd calculate regional averages and apply them
        estimates = {}

        for municipio in zero_municipalities:
            # Simple estimation: use state average
            estimates[municipio] = 1000.0  # Placeholder value

        return estimates

    def _estimate_by_population(self, conn: sqlite3.Connection, zero_municipalities: List[str]) -> Dict[str, float]:
        """Estimate biogas potential based on population"""
        estimates = {}

        for municipio in zero_municipalities:
            cursor = conn.cursor()
            cursor.execute("SELECT populacao FROM municipalities WHERE codigo_municipio = ?", (municipio,))
            result = cursor.fetchone()

            if result and result[0]:
                population = result[0]
                # Simple per-capita estimation
                estimated_potential = population * 0.5  # 0.5 m³/person/year
                estimates[municipio] = estimated_potential

        return estimates

    def _estimate_by_area(self, conn: sqlite3.Connection, zero_municipalities: List[str]) -> Dict[str, float]:
        """Estimate biogas potential based on area"""
        estimates = {}

        for municipio in zero_municipalities:
            cursor = conn.cursor()
            cursor.execute("SELECT area_km2 FROM municipalities WHERE codigo_municipio = ?", (municipio,))
            result = cursor.fetchone()

            if result and result[0]:
                area = result[0]
                # Simple per-area estimation
                estimated_potential = area * 10.0  # 10 m³/km²/year
                estimates[municipio] = estimated_potential

        return estimates

    def _apply_estimations(self, conn: sqlite3.Connection, estimates: Dict[str, float]) -> int:
        """Apply estimations to database"""
        updated_count = 0

        for municipio, estimated_value in estimates.items():
            cursor = conn.cursor()
            # Apply estimation to total biogas potential or specific column
            cursor.execute("""
                UPDATE municipalities
                SET total_biogas_estimated = ?
                WHERE codigo_municipio = ?
            """, (estimated_value, municipio))

            if cursor.rowcount > 0:
                updated_count += 1

        conn.commit()
        return updated_count

    def _get_current_conversion_factors(self, conn: sqlite3.Connection) -> Dict[str, float]:
        """Get current conversion factors from database"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT subcategory, final_factor FROM conversion_factors")
            return {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            # Table doesn't exist, return defaults
            return self.default_conversion_factors

    def _fix_data_types(self, conn: sqlite3.Connection) -> List[str]:
        """Fix data type inconsistencies"""
        fixes = []

        try:
            # Ensure numeric columns are properly typed
            numeric_columns = ['populacao', 'area_km2', 'densidade_demografica', 'lat', 'lon']

            for col in numeric_columns:
                if col in self._get_table_columns(conn, 'municipalities'):
                    conn.execute(f"""
                        UPDATE municipalities
                        SET {col} = CAST({col} AS REAL)
                        WHERE {col} IS NOT NULL
                    """)
                    fixes.append(f"Fixed data type for {col}")

            conn.commit()

        except Exception as e:
            self.logger.error(f"Error fixing data types: {e}")

        return fixes

    def _remove_duplicates(self, conn: sqlite3.Connection) -> List[str]:
        """Remove duplicate records"""
        fixes = []

        try:
            # Remove duplicates based on codigo_municipio
            conn.execute("""
                DELETE FROM municipalities
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM municipalities
                    GROUP BY codigo_municipio
                )
            """)

            removed_count = conn.total_changes
            if removed_count > 0:
                fixes.append(f"Removed {removed_count} duplicate records")

            conn.commit()

        except Exception as e:
            self.logger.error(f"Error removing duplicates: {e}")

        return fixes

    def _fix_null_values(self, conn: sqlite3.Connection) -> List[str]:
        """Fix null values with appropriate defaults"""
        fixes = []

        try:
            # Set default values for null numeric columns
            cursor = conn.cursor()

            # Fix null biogas values
            biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                            if 'biogas' in col.lower() and 'nm_ano' in col]

            for col in biogas_columns:
                cursor.execute(f"""
                    UPDATE municipalities
                    SET {col} = 0
                    WHERE {col} IS NULL
                """)

                if cursor.rowcount > 0:
                    fixes.append(f"Fixed {cursor.rowcount} null values in {col}")

            conn.commit()

        except Exception as e:
            self.logger.error(f"Error fixing null values: {e}")

        return fixes

    def _optimize_database(self, conn: sqlite3.Connection) -> List[str]:
        """Optimize database performance"""
        optimizations = []

        try:
            # Vacuum database
            conn.execute("VACUUM")
            optimizations.append("Database vacuum completed")

            # Analyze database statistics
            conn.execute("ANALYZE")
            optimizations.append("Database analysis completed")

        except Exception as e:
            self.logger.error(f"Error optimizing database: {e}")

        return optimizations

    def _create_performance_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """Create indexes for better performance"""
        indexes = []

        try:
            # Index on codigo_municipio
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_codigo_municipio
                ON municipalities(codigo_municipio)
            """)
            indexes.append("Created index on codigo_municipio")

            # Index on municipio name
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_municipio
                ON municipalities(municipio)
            """)
            indexes.append("Created index on municipio")

            # Index on coordinates for spatial queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_coordinates
                ON municipalities(lat, lon)
            """)
            indexes.append("Created index on coordinates")

            conn.commit()

        except Exception as e:
            self.logger.error(f"Error creating indexes: {e}")

        return indexes


# Factory function
def create_data_processor(db_path: Optional[str] = None) -> DataProcessor:
    """Create DataProcessor instance"""
    return DataProcessor(db_path)