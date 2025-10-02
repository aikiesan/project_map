"""
CP2B Maps V2 - Data Migrator
Focused on database optimization, fixes, and data migration
Extracted from DataProcessor for Single Responsibility
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DataMigrator:
    """
    Database optimization, fixes, and data migration manager
    
    Responsibilities:
    - Fix data type inconsistencies
    - Remove duplicate records
    - Fix null values
    - Optimize database performance
    - Create performance indexes
    - Manage database backups
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize DataMigrator
        
        Args:
            db_path: Path to SQLite database (uses settings default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = db_path or (settings.DATA_DIR / "database" / "cp2b_maps.db")
        
        if not self.db_path.exists():
            self.logger.warning(f"Database not found: {self.db_path}")

    def perform_database_fixes(self) -> Dict[str, Any]:
        """
        Perform comprehensive database fixes and optimizations
        
        Returns:
            Dictionary with fix and optimization results
        """
        try:
            self.logger.info("Starting database fixes and optimization")
            
            results = {
                'fix_date': datetime.now(),
                'fixes_applied': [],
                'optimizations': []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                # Fix data type inconsistencies
                type_fixes = self.fix_data_types(conn)
                results['fixes_applied'].extend(type_fixes)
                
                # Remove duplicate records
                duplicate_fixes = self.remove_duplicates(conn)
                results['fixes_applied'].extend(duplicate_fixes)
                
                # Update null values
                null_fixes = self.fix_null_values(conn)
                results['fixes_applied'].extend(null_fixes)
                
                # Optimize database
                optimizations = self.optimize_database(conn)
                results['optimizations'].extend(optimizations)
                
                # Create indexes for performance
                index_creation = self.create_performance_indexes(conn)
                results['optimizations'].extend(index_creation)
            
            self.logger.info("Database fixes completed")
            return results
        
        except Exception as e:
            self.logger.error(f"Error during database fix: {e}", exc_info=True)
            return {'error': str(e), 'fix_date': datetime.now()}

    def fix_data_types(self, conn: sqlite3.Connection) -> List[str]:
        """
        Fix data type inconsistencies in database
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of fixes applied
        """
        fixes = []
        
        try:
            # Ensure numeric columns are properly typed
            numeric_columns = ['populacao_2022', 'area_km2', 'densidade_demografica', 'lat', 'lon']
            
            table_columns = self._get_table_columns(conn, 'municipalities')
            
            for col in numeric_columns:
                if col in table_columns:
                    conn.execute(f"""
                        UPDATE municipalities
                        SET {col} = CAST({col} AS REAL)
                        WHERE {col} IS NOT NULL
                    """)
                    fixes.append(f"Fixed data type for {col}")
                    self.logger.debug(f"Fixed data type for column: {col}")
            
            conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error fixing data types: {e}")
        
        return fixes

    def remove_duplicates(self, conn: sqlite3.Connection) -> List[str]:
        """
        Remove duplicate records from database
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of fixes applied
        """
        fixes = []
        
        try:
            # Remove duplicates based on codigo_municipio
            cursor = conn.cursor()
            
            # First, identify duplicates
            cursor.execute("""
                SELECT codigo_municipio, COUNT(*) as count
                FROM municipalities
                GROUP BY codigo_municipio
                HAVING COUNT(*) > 1
            """)
            
            duplicates = cursor.fetchall()
            
            if duplicates:
                self.logger.info(f"Found {len(duplicates)} duplicate municipality codes")
                
                # Remove duplicates, keeping the first occurrence
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
                    self.logger.info(f"Removed {removed_count} duplicate records")
            
            conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {e}")
        
        return fixes

    def fix_null_values(self, conn: sqlite3.Connection) -> List[str]:
        """
        Fix null values with appropriate defaults
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of fixes applied
        """
        fixes = []
        
        try:
            cursor = conn.cursor()
            table_columns = self._get_table_columns(conn, 'municipalities')
            
            # Fix null biogas values (set to 0)
            biogas_columns = [col for col in table_columns
                            if ('biogas' in col.lower() or 'potencial' in col.lower())
                            and ('m_ano' in col or 'm3_ano' in col)]
            
            for col in biogas_columns:
                cursor.execute(f"""
                    UPDATE municipalities
                    SET {col} = 0
                    WHERE {col} IS NULL
                """)
                
                if cursor.rowcount > 0:
                    fixes.append(f"Fixed {cursor.rowcount} null values in {col}")
                    self.logger.debug(f"Fixed {cursor.rowcount} null values in {col}")
            
            # Fix null numeric values with appropriate defaults
            numeric_defaults = {
                'populacao_2022': 0,
                'area_km2': 0.0,
                'densidade_demografica': 0.0
            }
            
            for col, default_value in numeric_defaults.items():
                if col in table_columns:
                    cursor.execute(f"""
                        UPDATE municipalities
                        SET {col} = ?
                        WHERE {col} IS NULL
                    """, (default_value,))
                    
                    if cursor.rowcount > 0:
                        fixes.append(f"Fixed {cursor.rowcount} null values in {col}")
            
            conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error fixing null values: {e}")
        
        return fixes

    def optimize_database(self, conn: sqlite3.Connection) -> List[str]:
        """
        Optimize database performance
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of optimizations performed
        """
        optimizations = []
        
        try:
            # Vacuum database to reclaim space and defragment
            conn.execute("VACUUM")
            optimizations.append("Database vacuum completed (reclaimed space and defragmented)")
            self.logger.info("Database vacuum completed")
            
            # Analyze database statistics for query optimization
            conn.execute("ANALYZE")
            optimizations.append("Database analysis completed (updated query statistics)")
            self.logger.info("Database analysis completed")
            
            # Set optimal SQLite settings
            conn.execute("PRAGMA optimize")
            optimizations.append("Database optimization completed")
            
        except Exception as e:
            self.logger.error(f"Error optimizing database: {e}")
        
        return optimizations

    def create_performance_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """
        Create indexes for better query performance
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of indexes created
        """
        indexes = []
        
        try:
            # Index on codigo_municipio (primary key for lookups)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_codigo_municipio
                ON municipalities(codigo_municipio)
            """)
            indexes.append("Created index on codigo_municipio")
            
            # Index on municipio name (for search functionality)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_nome_municipio
                ON municipalities(nome_municipio)
            """)
            indexes.append("Created index on nome_municipio")
            
            # Index on coordinates for spatial queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_coordinates
                ON municipalities(lat, lon)
            """)
            indexes.append("Created index on coordinates (lat, lon)")
            
            # Index on population for filtering/sorting
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_populacao
                ON municipalities(populacao_2022)
            """)
            indexes.append("Created index on populacao_2022")
            
            conn.commit()
            self.logger.info(f"Created {len(indexes)} performance indexes")
        
        except Exception as e:
            self.logger.error(f"Error creating indexes: {e}")
        
        return indexes

    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a full backup of the database
        
        Args:
            backup_name: Optional custom backup name
        
        Returns:
            Dictionary with backup details
        """
        try:
            if not backup_name:
                backup_name = f"cp2b_maps_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            backup_path = self.db_path.parent / backup_name
            
            # Create backup using SQLite backup API
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            result = {
                'backup_created': True,
                'backup_path': str(backup_path),
                'backup_size_mb': round(backup_size_mb, 2),
                'backup_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Backup created successfully: {backup_path} ({backup_size_mb:.2f} MB)")
            return result
        
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return {
                'backup_created': False,
                'error': str(e),
                'backup_date': datetime.now().isoformat()
            }

    def restore_from_backup(self, backup_path: Path) -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            Dictionary with restore results
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create a safety backup of current database
            safety_backup = self.create_backup("pre_restore_safety_backup.db")
            
            # Restore from backup
            backup_conn = sqlite3.connect(backup_path)
            restore_conn = sqlite3.connect(self.db_path)
            
            backup_conn.backup(restore_conn)
            
            backup_conn.close()
            restore_conn.close()
            
            result = {
                'restore_successful': True,
                'restored_from': str(backup_path),
                'safety_backup': safety_backup.get('backup_path'),
                'restore_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Database restored from: {backup_path}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return {
                'restore_successful': False,
                'error': str(e),
                'restore_date': datetime.now().isoformat()
            }

    def compact_database(self) -> Dict[str, Any]:
        """
        Compact database by removing unused space
        
        Returns:
            Dictionary with compaction results
        """
        try:
            # Get initial size
            initial_size_mb = self.db_path.stat().st_size / (1024 * 1024)
            
            with sqlite3.connect(self.db_path) as conn:
                # Vacuum to compact
                conn.execute("VACUUM")
            
            # Get final size
            final_size_mb = self.db_path.stat().st_size / (1024 * 1024)
            space_saved_mb = initial_size_mb - final_size_mb
            
            result = {
                'compaction_successful': True,
                'initial_size_mb': round(initial_size_mb, 2),
                'final_size_mb': round(final_size_mb, 2),
                'space_saved_mb': round(space_saved_mb, 2),
                'compaction_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Database compacted: saved {space_saved_mb:.2f} MB")
            return result
        
        except Exception as e:
            self.logger.error(f"Error compacting database: {e}")
            return {
                'compaction_successful': False,
                'error': str(e),
                'compaction_date': datetime.now().isoformat()
            }

    def verify_database_integrity(self) -> Dict[str, Any]:
        """
        Verify database integrity using SQLite's integrity check
        
        Returns:
            Dictionary with integrity check results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                results = cursor.fetchall()
                
                # SQLite returns 'ok' if database is intact
                is_intact = len(results) == 1 and results[0][0] == 'ok'
                
                return {
                    'integrity_check_passed': is_intact,
                    'check_results': [r[0] for r in results],
                    'check_date': datetime.now().isoformat()
                }
        
        except Exception as e:
            self.logger.error(f"Error verifying database integrity: {e}")
            return {
                'integrity_check_passed': False,
                'error': str(e),
                'check_date': datetime.now().isoformat()
            }

    # Helper methods
    
    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """
        Get list of columns for a table
        
        Args:
            conn: SQLite database connection
            table_name: Name of the table
        
        Returns:
            List of column names
        """
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]


# Factory function
def get_data_migrator(db_path: Optional[Path] = None) -> DataMigrator:
    """
    Factory function to create DataMigrator instance
    
    Args:
        db_path: Optional path to database file
    
    Returns:
        DataMigrator instance
    """
    return DataMigrator(db_path)

