"""
CP2B Maps - Database Validator
Focused on database structure validation and data quality checks
Extracted from DataProcessor for Single Responsibility
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseValidator:
    """
    Database validation and data quality checker
    
    Responsibilities:
    - Validate database structure
    - Check data quality
    - Update with census data
    - Generate database statistics
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize DatabaseValidator
        
        Args:
            db_path: Path to SQLite database (uses settings default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = db_path or (settings.DATA_DIR / "database" / "cp2b_maps.db")
        
        if not self.db_path.exists():
            self.logger.warning(f"Database not found: {self.db_path}")

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
                structure_check = self.validate_structure(conn)
                results['structure_check'] = structure_check
                
                # Update with census data if provided
                if census_csv_path and Path(census_csv_path).exists():
                    census_update = self.update_with_census_data(conn, census_csv_path)
                    results['census_update'] = census_update
                    results['updates_made'].extend(census_update.get('updates', []))
                
                # Validate data quality
                quality_check = self.validate_data_quality(conn)
                results['quality_check'] = quality_check
                
                # Generate statistics
                results['statistics'] = self.generate_statistics(conn)
            
            self.logger.info("Database validation completed successfully")
            return results
        
        except Exception as e:
            self.logger.error(f"Error during database validation: {e}", exc_info=True)
            return {'error': str(e), 'validation_date': datetime.now()}

    def validate_structure(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Validate database table structure
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Dictionary with structure validation results
        """
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
            
            required_columns = ['nome_municipio', 'populacao_2022', 'codigo_municipio']
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

    def validate_data_quality(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Validate data quality and identify issues
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Dictionary with data quality metrics
        """
        try:
            cursor = conn.cursor()
            
            # Check for null values in critical columns
            cursor.execute("""
                SELECT COUNT(*) FROM municipalities WHERE nome_municipio IS NULL
            """)
            null_municipio = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM municipalities WHERE populacao_2022 IS NULL
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
            
            # Check for invalid coordinates (São Paulo state boundaries)
            cursor.execute("""
                SELECT COUNT(*) FROM municipalities
                WHERE lat IS NOT NULL AND lon IS NOT NULL
                AND (lat < -25.5 OR lat > -19.5 OR lon < -53.5 OR lon > -44.0)
            """)
            invalid_coords = cursor.fetchone()[0]
            
            quality_score = self._calculate_quality_score(
                null_municipio, null_populacao, len(duplicates), invalid_coords
            )
            
            return {
                'null_municipio': null_municipio,
                'null_populacao': null_populacao,
                'duplicate_count': len(duplicates),
                'duplicates': duplicates,
                'invalid_coordinates': invalid_coords,
                'quality_score': quality_score
            }
        
        except Exception as e:
            self.logger.error(f"Error validating data quality: {e}")
            return {'error': str(e)}

    def update_with_census_data(self, conn: sqlite3.Connection, csv_path: str) -> Dict[str, Any]:
        """
        Update database with census data from CSV
        
        Args:
            conn: SQLite database connection
            csv_path: Path to census CSV file
        
        Returns:
            Dictionary with update results
        """
        try:
            # Load census data
            census_df = pd.read_csv(csv_path)
            
            # Clean and prepare data
            census_df.columns = census_df.columns.str.strip()
            
            # Handle Brazilian number format (comma as decimal separator)
            for col in census_df.columns:
                if 'Area' in col or 'Densidade' in col:
                    census_df[col] = (census_df[col].astype(str)
                                    .str.replace(',', '.')
                                    .astype(float))
            
            # Rename columns to match database schema
            column_mapping = {
                'CD_MUN': 'codigo_municipio',
                'NM_MUN': 'nome_municipio',
                'Populacao_Residente_2022': 'populacao_2022',
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
                    SET populacao_2022 = ?, area_km2 = ?, densidade_demografica = ?
                    WHERE codigo_municipio = ?
                """, (row.get('populacao_2022'), row.get('area_km2'),
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

    def generate_statistics(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """
        Generate comprehensive database statistics
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Dictionary with database statistics
        """
        try:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM municipalities")
            total_municipalities = cursor.fetchone()[0]
            
            # Get biogas columns
            biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                            if 'biogas' in col.lower() or 'potencial' in col.lower()]
            
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
                    try:
                        cursor.execute(f"SELECT SUM({col}) FROM municipalities WHERE {col} IS NOT NULL")
                        total = cursor.fetchone()[0] or 0
                        biogas_totals[col] = float(total)
                    except sqlite3.OperationalError:
                        continue
                
                stats['biogas_totals'] = biogas_totals
                stats['total_biogas_potential'] = sum(biogas_totals.values())
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error generating database statistics: {e}")
            return {'error': str(e)}

    def check_data_integrity(self) -> bool:
        """
        Quick check if database has basic data integrity
        
        Returns:
            True if database passes basic integrity checks
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if municipalities table exists and has data
                cursor.execute("SELECT COUNT(*) FROM municipalities")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    self.logger.warning("Municipalities table is empty")
                    return False
                
                # Check if key columns have data
                cursor.execute("""
                    SELECT COUNT(*) FROM municipalities 
                    WHERE nome_municipio IS NOT NULL AND populacao_2022 IS NOT NULL
                """)
                valid_count = cursor.fetchone()[0]
                
                integrity_ratio = valid_count / count if count > 0 else 0
                
                return integrity_ratio > 0.95  # At least 95% of records should be valid
        
        except Exception as e:
            self.logger.error(f"Error checking data integrity: {e}")
            return False

    # Helper methods
    
    def _calculate_quality_score(self, null_municipio: int, null_populacao: int,
                                duplicates: int, invalid_coords: int) -> float:
        """
        Calculate overall data quality score (0-100)
        
        Args:
            null_municipio: Count of null municipality names
            null_populacao: Count of null population values
            duplicates: Count of duplicate records
            invalid_coords: Count of invalid coordinates
        
        Returns:
            Quality score from 0 to 100
        """
        total_issues = null_municipio + null_populacao + duplicates + invalid_coords
        if total_issues == 0:
            return 100.0
        
        # Deduct 5 points per issue
        score = max(0, 100 - (total_issues * 5))
        return round(score, 2)

    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Get list of columns for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    def _get_table_size(self, conn: sqlite3.Connection, table_name: str) -> float:
        """
        Get approximate table size in MB
        
        Args:
            conn: SQLite database connection
            table_name: Name of the table
        
        Returns:
            Approximate size in MB
        """
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Rough estimate: 1KB per row
            size_mb = (row_count * 1024) / (1024 * 1024)
            return round(size_mb, 2)
        
        except Exception:
            return 0.0


# Factory function
def get_database_validator(db_path: Optional[Path] = None) -> DatabaseValidator:
    """
    Factory function to create DatabaseValidator instance
    
    Args:
        db_path: Optional path to database file
    
    Returns:
        DatabaseValidator instance
    """
    return DatabaseValidator(db_path)

