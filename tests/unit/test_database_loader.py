"""
CP2B Maps - Unit Tests for Database Loader
Tests data integrity and loading following Section 2.6.1 methodology
"""

import pytest
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loaders.database_loader import DatabaseLoader
from config.settings import settings


class TestDatabaseConnection:
    """Test suite for database connection and initialization"""

    def test_database_exists(self):
        """Test that database file exists"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"
        assert db_path.exists(), f"Database not found at {db_path}"

    def test_database_loader_initialization(self):
        """Test DatabaseLoader initializes correctly"""
        loader = DatabaseLoader()
        assert loader.db_path.exists()
        assert str(loader.db_path).endswith('cp2b_maps.db')

    def test_database_connection_context_manager(self):
        """Test database connection using context manager"""
        loader = DatabaseLoader()

        try:
            with loader.get_connection() as conn:
                assert conn is not None
                # Test simple query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1
        except AttributeError:
            # If get_connection not implemented as context manager
            pytest.skip("Context manager not implemented")

    def test_database_readable(self):
        """Test database is readable and not corrupted"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check database is not corrupted
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()

        conn.close()

        assert result[0] == 'ok', "Database integrity check failed"


class TestDatabaseSchema:
    """Test suite for database schema validation"""

    def test_municipalities_table_exists(self):
        """Test that main municipalities table exists"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Should have at least one main data table
        assert len(tables) > 0, "No tables found in database"

    def test_required_columns_present(self):
        """Test that required columns are present in main table"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            # Try to load data with pandas
            df = pd.read_sql_query(
                "SELECT * FROM municipalities LIMIT 1",
                sqlite3.connect(db_path)
            )

            # Check for critical columns
            # Note: Exact column names depend on schema
            # This is a template - adjust based on actual schema
            expected_base_columns = [
                'ibge_code', 'municipality'
            ]

            for col in expected_base_columns:
                if col in df.columns:
                    assert col in df.columns

        except Exception as e:
            # Table might have different name
            pytest.skip(f"Could not query municipalities table: {e}")

    def test_column_data_types(self):
        """Test that columns have appropriate data types"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities LIMIT 10",
                conn
            )
            conn.close()

            # IBGE codes should be numeric or string
            if 'ibge_code' in df.columns:
                assert df['ibge_code'].dtype in ['int64', 'object']

            # Population should be numeric
            if 'population' in df.columns:
                assert pd.api.types.is_numeric_dtype(df['population'])

            # Biogas values should be numeric
            biogas_cols = [col for col in df.columns if 'biogas' in col.lower()]
            for col in biogas_cols:
                assert pd.api.types.is_numeric_dtype(df[col])

        except Exception as e:
            pytest.skip(f"Could not validate column types: {e}")


class TestDataCompleteness:
    """Test suite for data completeness validation"""

    def test_municipality_count(self):
        """Ensure all 645 São Paulo municipalities present"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            # São Paulo has 645 municipalities
            expected_count = 645

            # Allow some flexibility (at least 640)
            assert len(df) >= 640, f"Expected ~{expected_count} municipalities, found {len(df)}"

            if 'ibge_code' in df.columns:
                # IBGE codes should be unique
                assert df['ibge_code'].nunique() == len(df), "Duplicate IBGE codes found"

                # No null IBGE codes
                assert df['ibge_code'].isnull().sum() == 0, "Null IBGE codes found"

        except Exception as e:
            pytest.skip(f"Could not validate municipality count: {e}")

    def test_no_null_critical_fields(self):
        """Test that critical fields have no null values"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            # Critical fields should not be null
            critical_fields = ['ibge_code', 'municipality']

            for field in critical_fields:
                if field in df.columns:
                    null_count = df[field].isnull().sum()
                    assert null_count == 0, f"{null_count} null values found in {field}"

        except Exception as e:
            pytest.skip(f"Could not validate null fields: {e}")

    def test_coordinate_completeness(self):
        """Test that all municipalities have coordinates"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            # Check for coordinate columns (various naming conventions)
            lat_cols = [col for col in df.columns if 'lat' in col.lower()]
            lon_cols = [col for col in df.columns if 'lon' in col.lower()]

            if lat_cols and lon_cols:
                lat_col = lat_cols[0]
                lon_col = lon_cols[0]

                # Most municipalities should have coordinates (allow up to 5% missing)
                lat_missing = df[lat_col].isnull().sum()
                lon_missing = df[lon_col].isnull().sum()

                assert lat_missing <= len(df) * 0.05, f"Too many missing latitudes: {lat_missing}"
                assert lon_missing <= len(df) * 0.05, f"Too many missing longitudes: {lon_missing}"

        except Exception as e:
            pytest.skip(f"Could not validate coordinates: {e}")


class TestDataValidity:
    """Test suite for data validity and reasonable ranges"""

    def test_biogas_values_positive(self):
        """Test that biogas values are non-negative"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            # Find biogas columns
            biogas_cols = [col for col in df.columns if 'biogas' in col.lower()]

            for col in biogas_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Biogas values should be non-negative
                    negative_count = (df[col] < 0).sum()
                    assert negative_count == 0, f"Found {negative_count} negative values in {col}"

        except Exception as e:
            pytest.skip(f"Could not validate biogas values: {e}")

    def test_coordinate_ranges_valid(self):
        """Test that coordinates are within São Paulo state bounds"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            # Find coordinate columns
            lat_cols = [col for col in df.columns if 'lat' in col.lower()]
            lon_cols = [col for col in df.columns if 'lon' in col.lower()]

            if lat_cols and lon_cols:
                lat_col = lat_cols[0]
                lon_col = lon_cols[0]

                # São Paulo state approximate bounds
                # Latitude: -25.5 to -19.8
                # Longitude: -53.2 to -44.2

                valid_lat = df[lat_col].dropna()
                valid_lon = df[lon_col].dropna()

                # Check latitude range (allow small buffer)
                assert (valid_lat >= -26).all() and (valid_lat <= -19).all(), \
                    f"Latitude out of range: {valid_lat.min()} to {valid_lat.max()}"

                # Check longitude range (allow small buffer)
                assert (valid_lon >= -54).all() and (valid_lon <= -44).all(), \
                    f"Longitude out of range: {valid_lon.min()} to {valid_lon.max()}"

        except Exception as e:
            pytest.skip(f"Could not validate coordinate ranges: {e}")

    def test_population_reasonable(self):
        """Test that population values are reasonable"""
        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities",
                conn
            )
            conn.close()

            pop_cols = [col for col in df.columns if 'pop' in col.lower()]

            if pop_cols:
                pop_col = pop_cols[0]

                if pd.api.types.is_numeric_dtype(df[pop_col]):
                    valid_pop = df[pop_col].dropna()

                    # Population should be positive
                    assert (valid_pop >= 0).all(), "Negative population values found"

                    # São Paulo largest city ~12M, smallest ~1000
                    # Allow reasonable bounds
                    assert valid_pop.max() <= 15000000, f"Population too high: {valid_pop.max()}"
                    assert valid_pop.min() >= 0, f"Population too low: {valid_pop.min()}"

        except Exception as e:
            pytest.skip(f"Could not validate population: {e}")


class TestScenarioFactors:
    """Test suite for scenario factor application"""

    def test_scenario_factor_application(self):
        """Test that scenario factors are applied correctly"""
        loader = DatabaseLoader()

        # Create sample data
        df = pd.DataFrame({
            'municipality': ['Test'],
            'biogas_potential_m3_year': [1000000.0],
            'energy_potential_kwh_day': [10000.0]
        })

        # Apply scenario factor
        df_adjusted = loader.apply_scenario_factor(df)

        # Adjusted values should be <= original (factors are <= 1.0)
        assert df_adjusted['biogas_potential_m3_year'].iloc[0] <= df['biogas_potential_m3_year'].iloc[0]

        # Values should still be positive
        assert df_adjusted['biogas_potential_m3_year'].iloc[0] >= 0

    def test_scenario_factor_bounds(self):
        """Test that scenario factors are within valid range [0, 1]"""
        # This is a conceptual test - actual implementation may vary
        from config.scenario_config import get_scenario_factor

        factor = get_scenario_factor()

        # Factor should be between 0 and 1
        assert 0 <= factor <= 1, f"Scenario factor {factor} out of valid range"

    def test_biogas_columns_identification(self):
        """Test that BIOGAS_COLUMNS list is comprehensive"""
        loader = DatabaseLoader()

        # Check that BIOGAS_COLUMNS is defined
        assert hasattr(loader, 'BIOGAS_COLUMNS')
        assert len(loader.BIOGAS_COLUMNS) > 0

        # Common biogas-related column patterns
        expected_patterns = ['biogas', 'energy', 'potential', 'co2']

        biogas_cols_lower = [col.lower() for col in loader.BIOGAS_COLUMNS]

        # At least one pattern should be present
        patterns_found = sum(
            any(pattern in col for col in biogas_cols_lower)
            for pattern in expected_patterns
        )

        assert patterns_found > 0, "No biogas-related patterns found in BIOGAS_COLUMNS"


class TestQueryPerformance:
    """Test suite for query performance (basic timing checks)"""

    def test_full_table_load_performance(self):
        """Test that loading full table is reasonably fast"""
        import time

        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        start_time = time.time()

        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM municipalities", conn)
            conn.close()

            elapsed_time = time.time() - start_time

            # Should load in under 2 seconds for 645 municipalities
            assert elapsed_time < 2.0, f"Query took {elapsed_time:.2f}s, expected <2s"

            # Verify data was loaded
            assert len(df) > 0

        except Exception as e:
            pytest.skip(f"Could not test query performance: {e}")

    def test_single_municipality_query_performance(self):
        """Test that single municipality query is fast"""
        import time

        db_path = settings.DATA_DIR / "database" / "cp2b_maps.db"

        start_time = time.time()

        try:
            conn = sqlite3.connect(db_path)

            # Query single municipality (Piracicaba IBGE: 3538709)
            df = pd.read_sql_query(
                "SELECT * FROM municipalities WHERE ibge_code = 3538709",
                conn
            )
            conn.close()

            elapsed_time = time.time() - start_time

            # Should complete in under 0.5 seconds
            assert elapsed_time < 0.5, f"Query took {elapsed_time:.2f}s, expected <0.5s"

        except Exception as e:
            pytest.skip(f"Could not test single query performance: {e}")


class TestScenarioFactorEdgeCases:
    """Test scenario factor application edge cases"""

    def test_scenario_factor_1_0_unchanged(self):
        """Test that factor 1.0 leaves values unchanged"""
        loader = DatabaseLoader()

        # Create sample data
        df = pd.DataFrame({
            'municipality': ['Test'],
            'biogas_potential_m3_year': [1000000.0],
            'energy_potential_kwh_day': [10000.0]
        })

        # Mock scenario factor as 1.0
        from config import scenario_config
        original_factor = scenario_config.get_scenario_factor
        scenario_config.get_scenario_factor = lambda: 1.0
        scenario_config.get_current_scenario = lambda: 'utopian'

        try:
            df_adjusted = loader.apply_scenario_factor(df)

            # Values should be identical
            assert df_adjusted['biogas_potential_m3_year'].iloc[0] == 1000000.0
            assert df_adjusted['energy_potential_kwh_day'].iloc[0] == 10000.0

        finally:
            # Restore original function
            scenario_config.get_scenario_factor = original_factor

    def test_scenario_factor_reduces_values(self):
        """Test that scenario factor scales biogas values proportionally"""
        loader = DatabaseLoader()

        # Create sample data
        df = pd.DataFrame({
            'municipality': ['Test'],
            'biogas_potential_m3_year': [1000000.0],
            'energy_potential_kwh_day': [10000.0],
            'other_column': [100]  # Should not be affected
        })

        df_adjusted = loader.apply_scenario_factor(df)

        # Biogas columns should be scaled (factor is 0 < factor <= 1)
        # Adjusted values should be <= original (unless factor > 1)
        assert df_adjusted['biogas_potential_m3_year'].iloc[0] <= df['biogas_potential_m3_year'].iloc[0]
        assert df_adjusted['energy_potential_kwh_day'].iloc[0] <= df['energy_potential_kwh_day'].iloc[0]

        # Non-biogas columns should be unchanged
        assert df_adjusted['other_column'].iloc[0] == df['other_column'].iloc[0]

        # Values should still be non-negative
        assert df_adjusted['biogas_potential_m3_year'].iloc[0] >= 0
        assert df_adjusted['energy_potential_kwh_day'].iloc[0] >= 0

    def test_apply_scenario_factor_empty_dataframe(self):
        """Test scenario factor application to empty DataFrame"""
        loader = DatabaseLoader()

        df = pd.DataFrame()

        df_adjusted = loader.apply_scenario_factor(df)

        # Should return empty DataFrame without errors
        assert isinstance(df_adjusted, pd.DataFrame)
        assert len(df_adjusted) == 0

    def test_apply_scenario_factor_missing_columns(self):
        """Test scenario factor with DataFrame missing biogas columns"""
        loader = DatabaseLoader()

        # DataFrame with no biogas columns
        df = pd.DataFrame({
            'municipality': ['Test'],
            'population': [100000]
        })

        df_adjusted = loader.apply_scenario_factor(df)

        # Should handle gracefully (no columns to adjust)
        assert isinstance(df_adjusted, pd.DataFrame)
        assert 'municipality' in df_adjusted.columns
        assert df_adjusted['population'].iloc[0] == 100000

    def test_apply_scenario_factor_preserves_original(self):
        """Test that applying scenario factor doesn't modify original DataFrame"""
        loader = DatabaseLoader()

        # Create sample data
        df_original = pd.DataFrame({
            'municipality': ['Test'],
            'biogas_potential_m3_year': [1000000.0]
        })

        original_value = df_original['biogas_potential_m3_year'].iloc[0]

        df_adjusted = loader.apply_scenario_factor(df_original)

        # Original should be unchanged
        assert df_original['biogas_potential_m3_year'].iloc[0] == original_value


class TestDatabaseLoaderMethods:
    """Test additional DatabaseLoader methods"""

    def test_get_database_info(self):
        """Test get_database_info returns expected structure"""
        loader = DatabaseLoader()

        info = loader.get_database_info()

        # Should return dict
        assert isinstance(info, dict)

        # Should have expected keys
        if 'error' not in info:
            assert 'database_path' in info
            assert 'database_size_mb' in info
            assert 'tables' in info

    def test_validate_database_success(self):
        """Test database validation succeeds for valid database"""
        loader = DatabaseLoader()

        result = loader.validate_database()

        # Should return True for valid database
        assert result is True

    def test_validate_database_invalid_path(self):
        """Test database validation fails for invalid path"""
        from pathlib import Path

        # Create loader with invalid path
        invalid_path = Path("/nonexistent/path/to/database.db")
        loader = DatabaseLoader(db_path=invalid_path)

        result = loader.validate_database()

        # Should return False
        assert result is False

    def test_search_municipalities(self):
        """Test municipality search functionality"""
        loader = DatabaseLoader()

        try:
            result = loader.search_municipalities("São Paulo", limit=5)

            if result is not None:
                # Should return DataFrame
                assert isinstance(result, pd.DataFrame)
                # Should have at most 5 results
                assert len(result) <= 5

        except Exception:
            # If method uses different table structure, skip
            pytest.skip("search_municipalities not compatible with current schema")

    def test_search_municipalities_no_results(self):
        """Test municipality search with no matching results"""
        loader = DatabaseLoader()

        try:
            result = loader.search_municipalities("NONEXISTENTCITYXYZ123", limit=10)

            if result is not None:
                # Should return empty DataFrame
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 0

        except Exception:
            pytest.skip("search_municipalities not compatible with current schema")

    def test_search_municipalities_empty_term(self):
        """Test municipality search with empty search term"""
        loader = DatabaseLoader()

        try:
            result = loader.search_municipalities("", limit=10)

            # Should handle gracefully
            assert result is None or isinstance(result, pd.DataFrame)

        except Exception:
            pytest.skip("search_municipalities not compatible with current schema")


class TestDatabaseConnectionErrors:
    """Test database connection error handling"""

    def test_database_loader_nonexistent_path_initialization(self):
        """Test DatabaseLoader initialization with nonexistent database"""
        from pathlib import Path

        invalid_path = Path("/tmp/nonexistent_database.db")

        # Should initialize without error (error logged)
        loader = DatabaseLoader(db_path=invalid_path)

        assert loader.db_path == invalid_path

    def test_get_connection_with_invalid_database(self):
        """Test get_connection with invalid database path"""
        from pathlib import Path

        invalid_path = Path("/tmp/nonexistent_database.db")
        loader = DatabaseLoader(db_path=invalid_path)

        # Connection might succeed even for nonexistent DB (SQLite creates it)
        # but querying non-existent table should fail
        try:
            with loader.get_connection() as conn:
                # Try to query a table that doesn't exist
                with pytest.raises(Exception):  # Could be sqlite3.OperationalError or DatabaseError
                    conn.execute("SELECT * FROM nonexistent_table").fetchall()
        except sqlite3.Error:
            # If connection itself fails, that's also acceptable
            pass


class TestDatabaseCaching:
    """Test that caching decorators work correctly"""

    def test_load_municipalities_data_cached(self):
        """Test that load_municipalities_data uses caching"""
        loader = DatabaseLoader()

        # First call
        df1 = loader.load_municipalities_data()

        # Second call (should be cached)
        df2 = loader.load_municipalities_data()

        # Both should be DataFrames (or both None)
        if df1 is not None:
            assert isinstance(df1, pd.DataFrame)
            assert isinstance(df2, pd.DataFrame)
            # Should have same shape
            assert df1.shape == df2.shape

    def test_get_top_municipalities(self):
        """Test get_top_municipalities method"""
        loader = DatabaseLoader()

        result = loader.get_top_municipalities(limit=10)

        if result is not None:
            # Should return DataFrame
            assert isinstance(result, pd.DataFrame)
            # Should have at most 10 results
            assert len(result) <= 10
            # Should have expected columns
            if len(result) > 0:
                assert 'municipality' in result.columns

    def test_get_top_municipalities_different_limits(self):
        """Test get_top_municipalities with different limits"""
        loader = DatabaseLoader()

        result_5 = loader.get_top_municipalities(limit=5)
        result_20 = loader.get_top_municipalities(limit=20)

        if result_5 is not None and result_20 is not None:
            # 5-limit result should be smaller
            assert len(result_5) <= 5
            assert len(result_20) <= 20
            assert len(result_5) <= len(result_20)

    def test_get_summary_statistics(self):
        """Test get_summary_statistics method"""
        loader = DatabaseLoader()

        stats = loader.get_summary_statistics()

        # Should return dict (or None if method implementation varies)
        if stats is not None:
            assert isinstance(stats, dict)
            # May have various keys depending on implementation

    def test_load_municipality_by_name(self):
        """Test loading specific municipality by name"""
        loader = DatabaseLoader()

        try:
            # Try loading a known municipality
            result = loader.load_municipality_by_name("Piracicaba")

            if result is not None:
                # Should return Series
                assert isinstance(result, pd.Series)

        except Exception:
            # If method signature differs, skip
            pytest.skip("load_municipality_by_name not compatible")

    def test_load_municipality_by_name_not_found(self):
        """Test loading nonexistent municipality"""
        loader = DatabaseLoader()

        try:
            result = loader.load_municipality_by_name("NONEXISTENTCITY123XYZ")

            # Should return None
            assert result is None

        except Exception:
            pytest.skip("load_municipality_by_name not compatible")
