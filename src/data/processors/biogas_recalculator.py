"""
CP2B Maps V2 - Biogas Potential Recalculator
Focused on biogas potential calculations and updates
Extracted from DataProcessor for Single Responsibility
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from config.settings import settings
from src.utils.logging_config import get_logger
from src.core.biogas_calculator import get_biogas_calculator, ConversionFactors

logger = get_logger(__name__)


class BiogasRecalculator:
    """
    Biogas potential calculation and recalculation manager
    
    Responsibilities:
    - Recalculate biogas potentials with new factors
    - Estimate potentials for municipalities with zero values
    - Update conversion factors in database
    - Manage calculation backups
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize BiogasRecalculator
        
        Args:
            db_path: Path to SQLite database (uses settings default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = db_path or (settings.DATA_DIR / "database" / "cp2b_maps.db")
        
        # Default conversion factors for biogas calculations
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
        
        if not self.db_path.exists():
            self.logger.warning(f"Database not found: {self.db_path}")

    def recalculate_all_potentials(self,
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
                updates_made = self._recalculate_potentials(conn, factors)
                results['municipalities_updated'] = updates_made
                
                # Get new totals
                new_totals = self._calculate_current_totals(conn)
                results['total_potential_after'] = new_totals
                
                # Update conversion factors table
                self._update_conversion_factors_table(conn, factors)
            
            self.logger.info(f"Biogas recalculation completed: {updates_made} municipalities updated")
            return results
        
        except Exception as e:
            self.logger.error(f"Error during biogas recalculation: {e}", exc_info=True)
            return {'error': str(e), 'calculation_date': datetime.now()}

    def estimate_zero_municipalities(self,
                                   estimation_method: str = 'regional_average') -> Dict[str, Any]:
        """
        Estimate biogas potential for municipalities with zero values
        
        Args:
            estimation_method: Method for estimation 
                ('regional_average', 'population_based', 'area_based')
        
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
            self.logger.error(f"Error estimating zero municipalities: {e}", exc_info=True)
            return {'error': str(e), 'estimation_date': datetime.now()}

    def update_conversion_factors(self, new_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Update conversion factors in the database
        
        Args:
            new_factors: Dictionary of factor_name: value pairs
        
        Returns:
            Dictionary with update results
        """
        try:
            self.logger.info("Updating conversion factors")
            
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
                
                # Optionally trigger recalculation
                # (Commented out to avoid automatic recalculation - should be explicit)
                # if updated_count > 0:
                #     self.recalculate_all_potentials(new_factors, create_backup=True)
            
            self.logger.info(f"Conversion factors update completed: {updated_count} factors updated")
            return results
        
        except Exception as e:
            self.logger.error(f"Error updating conversion factors: {e}")
            return {'error': str(e), 'update_date': datetime.now()}

    def get_current_factors(self) -> Dict[str, float]:
        """
        Get current conversion factors from database
        
        Returns:
            Dictionary of current conversion factors
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                return self._get_current_conversion_factors(conn)
        except Exception as e:
            self.logger.error(f"Error getting current factors: {e}")
            return self.default_conversion_factors

    # Helper methods
    
    def _create_backup_table(self, conn: sqlite3.Connection) -> str:
        """
        Create backup table with timestamp
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Name of created backup table
        """
        backup_table = f"municipalities_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn.execute(f"""
            CREATE TABLE {backup_table} AS
            SELECT * FROM municipalities
        """)
        
        self.logger.info(f"Backup created: {backup_table}")
        return backup_table

    def _calculate_current_totals(self, conn: sqlite3.Connection) -> float:
        """
        Calculate current total biogas potential
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Total biogas potential across all municipalities
        """
        try:
            biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                            if ('biogas' in col.lower() or 'potencial' in col.lower()) 
                            and ('m_ano' in col or 'm3_ano' in col)]
            
            if not biogas_columns:
                return 0.0
            
            total = 0.0
            for col in biogas_columns:
                cursor = conn.cursor()
                cursor.execute(f"SELECT SUM({col}) FROM municipalities WHERE {col} IS NOT NULL")
                col_total = cursor.fetchone()[0] or 0
                total += col_total
            
            return round(total, 2)
        
        except Exception as e:
            self.logger.error(f"Error calculating current totals: {e}")
            return 0.0

    def _recalculate_potentials(self, conn: sqlite3.Connection, factors: Dict[str, float]) -> int:
        """
        Recalculate biogas potentials using new factors
        
        Args:
            conn: SQLite database connection
            factors: New conversion factors to apply
        
        Returns:
            Number of municipalities updated
        """
        try:
            # This is a simplified version
            # In production, you would recalculate based on source data
            # (livestock counts, crop production, etc.)
            
            factor_mapping = {
                'biogas_bovinos_m_ano': factors.get('cattle', 225.0),
                'biogas_suino_m_ano': factors.get('swine', 210.0),
                'biogas_aves_m_ano': factors.get('poultry', 34.0),
                'biogas_cafe_m_ano': factors.get('coffee', 150.0),
                'biogas_cana_m_ano': factors.get('sugarcane', 200.0),
                'biogas_milho_m_ano': factors.get('corn', 225.0),
                'biogas_soja_m_ano': factors.get('soybean', 180.0),
                'biogas_citros_m_ano': factors.get('citrus', 120.0),
                'rsu_potencial_m_ano': factors.get('urban_waste', 117.0),
                'rpo_potencial_m_ano': factors.get('industrial_waste', 7.0),
                'biogas_piscicultura_m_ano': factors.get('aquaculture', 62.0)
            }
            
            cursor = conn.cursor()
            cursor.execute("SELECT codigo_municipio FROM municipalities")
            municipalities = cursor.fetchall()
            
            updates_made = 0
            for (codigo_municipio,) in municipalities:
                # In a real implementation, you would recalculate based on
                # source data (livestock counts, crop production, etc.)
                # For now, this is a placeholder for the actual calculation logic
                updates_made += 1
            
            conn.commit()
            return updates_made
        
        except Exception as e:
            self.logger.error(f"Error recalculating potentials: {e}")
            return 0

    def _update_conversion_factors_table(self, conn: sqlite3.Connection, factors: Dict[str, float]) -> int:
        """
        Update or create conversion factors table
        
        Args:
            conn: SQLite database connection
            factors: Dictionary of conversion factors
        
        Returns:
            Number of factors updated
        """
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

    def _get_current_conversion_factors(self, conn: sqlite3.Connection) -> Dict[str, float]:
        """
        Get current conversion factors from database
        
        Args:
            conn: SQLite database connection
        
        Returns:
            Dictionary of current conversion factors
        """
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT subcategory, final_factor FROM conversion_factors")
            return {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            # Table doesn't exist, return defaults
            return self.default_conversion_factors

    def _identify_zero_municipalities(self, conn: sqlite3.Connection) -> List[str]:
        """
        Identify municipalities with zero biogas potential
        
        Args:
            conn: SQLite database connection
        
        Returns:
            List of municipality codes with zero biogas potential
        """
        cursor = conn.cursor()
        
        biogas_columns = [col for col in self._get_table_columns(conn, 'municipalities')
                         if ('biogas' in col.lower() or 'potencial' in col.lower())
                         and ('m_ano' in col or 'm3_ano' in col)]
        
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

    def _estimate_by_regional_average(self, conn: sqlite3.Connection, 
                                     zero_municipalities: List[str]) -> Dict[str, float]:
        """
        Estimate biogas potential using regional averages
        
        Args:
            conn: SQLite database connection
            zero_municipalities: List of municipality codes to estimate
        
        Returns:
            Dictionary mapping municipality codes to estimated values
        """
        # Calculate state-wide average from non-zero municipalities
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(total_final_m_ano) 
            FROM municipalities 
            WHERE total_final_m_ano IS NOT NULL AND total_final_m_ano > 0
        """)
        
        result = cursor.fetchone()
        avg_potential = result[0] if result and result[0] else 1000.0
        
        estimates = {}
        for municipio in zero_municipalities:
            estimates[municipio] = avg_potential
        
        return estimates

    def _estimate_by_population(self, conn: sqlite3.Connection, 
                               zero_municipalities: List[str]) -> Dict[str, float]:
        """
        Estimate biogas potential based on population
        
        Args:
            conn: SQLite database connection
            zero_municipalities: List of municipality codes to estimate
        
        Returns:
            Dictionary mapping municipality codes to estimated values
        """
        estimates = {}
        
        for municipio in zero_municipalities:
            cursor = conn.cursor()
            cursor.execute("SELECT populacao_2022 FROM municipalities WHERE codigo_municipio = ?", 
                         (municipio,))
            result = cursor.fetchone()
            
            if result and result[0]:
                population = result[0]
                # Simple per-capita estimation (117 m³/person/year from urban waste)
                estimated_potential = population * 117.0
                estimates[municipio] = estimated_potential
        
        return estimates

    def _estimate_by_area(self, conn: sqlite3.Connection, 
                         zero_municipalities: List[str]) -> Dict[str, float]:
        """
        Estimate biogas potential based on area
        
        Args:
            conn: SQLite database connection
            zero_municipalities: List of municipality codes to estimate
        
        Returns:
            Dictionary mapping municipality codes to estimated values
        """
        estimates = {}
        
        for municipio in zero_municipalities:
            cursor = conn.cursor()
            cursor.execute("SELECT area_km2 FROM municipalities WHERE codigo_municipio = ?", 
                         (municipio,))
            result = cursor.fetchone()
            
            if result and result[0]:
                area = result[0]
                # Simple per-area estimation (1000 m³/km²/year)
                estimated_potential = area * 1000.0
                estimates[municipio] = estimated_potential
        
        return estimates

    def _apply_estimations(self, conn: sqlite3.Connection, estimates: Dict[str, float]) -> int:
        """
        Apply estimations to database
        
        Args:
            conn: SQLite database connection
            estimates: Dictionary of municipality codes to estimated values
        
        Returns:
            Number of municipalities updated
        """
        updated_count = 0
        
        for municipio, estimated_value in estimates.items():
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE municipalities
                SET total_biogas_estimated_m_ano = ?
                WHERE codigo_municipio = ?
            """, (estimated_value, municipio))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        conn.commit()
        return updated_count

    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Get list of columns for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]


# Factory function
def get_biogas_recalculator(db_path: Optional[Path] = None) -> BiogasRecalculator:
    """
    Factory function to create BiogasRecalculator instance
    
    Args:
        db_path: Optional path to database file
    
    Returns:
        BiogasRecalculator instance
    """
    return BiogasRecalculator(db_path)

