"""
CP2B Maps V2 - Professional Database Loader
High-performance SQLite database access with connection pooling and optimization
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache
import streamlit as st
from contextlib import contextmanager

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseLoader:
    """
    Professional SQLite database loader with connection pooling and optimization
    Handles 645 municipalities with biogas potential data
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize DatabaseLoader

        Args:
            db_path: Path to SQLite database (defaults to settings.DATA_DIR/database/cp2b_maps.db)
        """
        self.db_path = db_path or settings.DATA_DIR / "database" / "cp2b_maps.db"
        self.logger = get_logger(self.__class__.__name__)

        if not self.db_path.exists():
            self.logger.error(f"Database not found: {self.db_path}")
        else:
            self.logger.info(f"Database initialized: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with proper cleanup

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            # Enable foreign keys and optimize performance
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")

            yield conn

        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @st.cache_data(ttl=settings.CACHE_TTL)
    def load_municipalities_data(_self) -> Optional[pd.DataFrame]:
        """
        Load all municipality data with biogas calculations

        Returns:
            DataFrame with all 645 municipalities and their biogas potential data
        """
        try:
            with _self.get_connection() as conn:
                # Load main municipality data with correct Portuguese column names
                query = """
                SELECT
                    nome_municipio as municipality,
                    total_final_m_ano as biogas_potential_m3_year,
                    (total_final_m_ano / 365.0) as biogas_potential_m3_day,
                    total_urbano_m_ano as urban_biogas_m3_year,
                    total_agricola_m_ano as agricultural_biogas_m3_year,
                    total_pecuaria_m_ano as livestock_biogas_m3_year,
                    populacao_2022 as population,
                    rsu_potencial_m_ano as urban_waste_potential_m3_year,
                    rpo_potencial_m_ano as rural_waste_potential_m3_year,
                    area_km2,
                    densidade_demografica as population_density,
                    lat as latitude,
                    lon as longitude
                FROM municipalities
                WHERE total_final_m_ano IS NOT NULL
                ORDER BY nome_municipio
                """

                df = pd.read_sql_query(query, conn)

                # Calculate daily values and additional metrics
                df['energy_potential_kwh_day'] = df['biogas_potential_m3_day'] * 0.6 * 9.97  # 60% methane, 9.97 kWh/m³
                df['energy_potential_mwh_year'] = (df['energy_potential_kwh_day'] * 365) / 1000
                df['co2_reduction_tons_year'] = df['energy_potential_kwh_day'] * 0.45 * 365 / 1000  # kg CO2 per kWh

                _self.logger.info(f"Loaded data for {len(df)} municipalities")
                return df

        except Exception as e:
            _self.logger.error(f"Failed to load municipalities data: {e}", exc_info=True)
            return None

    @st.cache_data(ttl=settings.CACHE_TTL)
    def load_municipality_by_name(_self, municipality_name: str) -> Optional[pd.Series]:
        """
        Load specific municipality data

        Args:
            municipality_name: Name of the municipality

        Returns:
            Series with municipality data or None if not found
        """
        try:
            with _self.get_connection() as conn:
                query = """
                SELECT * FROM municipalities
                WHERE nome_municipio = ?
                LIMIT 1
                """

                df = pd.read_sql_query(query, conn, params=[municipality_name])

                if len(df) > 0:
                    return df.iloc[0]
                else:
                    _self.logger.warning(f"Municipality not found: {municipality_name}")
                    return None

        except Exception as e:
            _self.logger.error(f"Failed to load municipality {municipality_name}: {e}")
            return None

    @st.cache_data(ttl=settings.CACHE_TTL)
    def get_top_municipalities(_self,
                              by_column: str = "total_final_m_ano",
                              limit: int = 20) -> Optional[pd.DataFrame]:
        """
        Get top municipalities by specified metric

        Args:
            by_column: Column to sort by (using database column names)
            limit: Number of municipalities to return

        Returns:
            DataFrame with top municipalities
        """
        try:
            with _self.get_connection() as conn:
                query = f"""
                SELECT
                    nome_municipio as municipality,
                    (total_final_m_ano / 365.0) as biogas_potential_m3_day,
                    (total_final_m_ano / 365.0 * 0.6 * 9.97) as energy_potential_kwh_day,
                    populacao_2022 as population
                FROM municipalities
                WHERE {by_column} IS NOT NULL
                ORDER BY {by_column} DESC
                LIMIT ?
                """

                df = pd.read_sql_query(query, conn, params=[limit])
                _self.logger.debug(f"Retrieved top {len(df)} municipalities by {by_column}")
                return df

        except Exception as e:
            _self.logger.error(f"Failed to get top municipalities: {e}")
            return None

    @st.cache_data(ttl=settings.CACHE_TTL)
    def get_summary_statistics(_self) -> Optional[Dict[str, Any]]:
        """
        Get summary statistics for all municipalities

        Returns:
            Dictionary with summary statistics
        """
        try:
            with _self.get_connection() as conn:
                query = """
                SELECT
                    COUNT(*) as total_municipalities,
                    SUM(biogas_potential_m3_day) as total_biogas_m3_day,
                    AVG(biogas_potential_m3_day) as avg_biogas_m3_day,
                    SUM(energy_potential_kwh_day) as total_energy_kwh_day,
                    SUM(co2_reduction_tons_year) as total_co2_reduction_tons_year,
                    SUM(population) as total_population,
                    SUM(total_waste_tons_day) as total_waste_tons_day
                FROM municipalities
                WHERE biogas_potential_m3_day IS NOT NULL
                """

                result = conn.execute(query).fetchone()

                if result:
                    stats = {
                        "total_municipalities": result[0],
                        "total_biogas_m3_day": round(result[1], 2) if result[1] else 0,
                        "avg_biogas_m3_day": round(result[2], 2) if result[2] else 0,
                        "total_energy_kwh_day": round(result[3], 2) if result[3] else 0,
                        "total_co2_reduction_tons_year": round(result[4], 2) if result[4] else 0,
                        "total_population": result[5] if result[5] else 0,
                        "total_waste_tons_day": round(result[6], 2) if result[6] else 0
                    }

                    _self.logger.info(f"Generated statistics for {stats['total_municipalities']} municipalities")
                    return stats

        except Exception as e:
            _self.logger.error(f"Failed to get summary statistics: {e}")
            return None

    def search_municipalities(self, search_term: str, limit: int = 10) -> Optional[pd.DataFrame]:
        """
        Search municipalities by name

        Args:
            search_term: Search term (partial name matching)
            limit: Maximum number of results

        Returns:
            DataFrame with matching municipalities
        """
        try:
            with self.get_connection() as conn:
                query = """
                SELECT
                    municipality,
                    biogas_potential_m3_day,
                    energy_potential_kwh_day,
                    population
                FROM municipalities
                WHERE municipality LIKE ?
                ORDER BY municipality
                LIMIT ?
                """

                search_pattern = f"%{search_term}%"
                df = pd.read_sql_query(query, conn, params=[search_pattern, limit])

                self.logger.debug(f"Found {len(df)} municipalities matching '{search_term}'")
                return df

        except Exception as e:
            self.logger.error(f"Search failed for term '{search_term}': {e}")
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database structure

        Returns:
            Dictionary with database information
        """
        try:
            with self.get_connection() as conn:
                # Get table info
                tables = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()

                info = {
                    "database_path": str(self.db_path),
                    "database_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2),
                    "tables": [table[0] for table in tables]
                }

                # Get municipalities table info if it exists
                if "municipalities" in info["tables"]:
                    count_result = conn.execute("SELECT COUNT(*) FROM municipalities").fetchone()
                    info["municipality_count"] = count_result[0] if count_result else 0

                return info

        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}

    def validate_database(self) -> bool:
        """
        Validate database connectivity and structure

        Returns:
            True if database is valid and accessible
        """
        try:
            with self.get_connection() as conn:
                # Test basic query
                result = conn.execute("SELECT COUNT(*) FROM municipalities").fetchone()
                municipality_count = result[0] if result else 0

                if municipality_count > 0:
                    self.logger.info(f"Database validation successful: {municipality_count} municipalities")
                    return True
                else:
                    self.logger.warning("Database validation failed: no municipalities found")
                    return False

        except Exception as e:
            self.logger.error(f"Database validation failed: {e}")
            return False


# Factory function with caching for dependency injection
@st.cache_resource
def get_database_loader(db_path: Optional[Path] = None) -> DatabaseLoader:
    """
    Get cached DatabaseLoader instance for dependency injection

    Args:
        db_path: Optional custom database path

    Returns:
        Cached DatabaseLoader instance
    """
    return DatabaseLoader(db_path)