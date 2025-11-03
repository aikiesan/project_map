"""
CP2B Maps - Integration Tests for Complete Workflow
Tests full analysis pipeline combining multiple modules
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loaders.database_loader import DatabaseLoader
from src.core.geospatial_analysis import GeospatialAnalyzer
from src.core.biogas_calculator import BiogasCalculator


class TestFullAnalysisPipeline:
    """Test complete workflow integrating all modules"""

    def test_full_analysis_pipeline_for_single_municipality(self):
        """
        Test complete analysis workflow: Load → Analyze Radius → Calculate Biogas
        This integration test verifies all modules work together correctly
        """
        # Step 1: Initialize DatabaseLoader and load data
        db_loader = DatabaseLoader()
        df_all = db_loader.load_municipalities_data()

        assert df_all is not None, "Failed to load municipality data"
        assert len(df_all) > 0, "No municipalities loaded"
        assert 'municipality' in df_all.columns

        # Step 2: Find a known municipality (Piracicaba)
        piracicaba = df_all[df_all['municipality'] == 'Piracicaba']

        if len(piracicaba) == 0:
            # Try alternative name
            piracicaba = df_all[df_all['municipality'].str.contains('Piracicaba', case=False, na=False)]

        assert len(piracicaba) > 0, "Piracicaba not found in database"

        # Get Piracicaba coordinates
        pira_lat = piracicaba['latitude'].iloc[0]
        pira_lon = piracicaba['longitude'].iloc[0]

        assert pira_lat is not None, "Piracicaba latitude is missing"
        assert pira_lon is not None, "Piracicaba longitude is missing"

        # Step 3: Initialize GeospatialAnalyzer and find municipalities within 50km radius
        geo_analyzer = GeospatialAnalyzer()

        # Prepare DataFrame with lat/lon columns
        df_geo = df_all.copy()
        df_geo['lat'] = df_geo['latitude']
        df_geo['lon'] = df_geo['longitude']

        nearby_municipalities = geo_analyzer.find_municipalities_in_radius(
            df_geo, pira_lat, pira_lon, radius_km=50
        )

        assert len(nearby_municipalities) > 0, "No municipalities found in radius"

        # Verify Piracicaba itself is in results with distance 0
        pira_in_results = nearby_municipalities[
            nearby_municipalities['municipality'].str.contains('Piracicaba', case=False, na=False)
        ]

        if len(pira_in_results) > 0:
            assert pira_in_results['distance_km'].iloc[0] < 1, "Piracicaba should have distance ~0"

        # Step 4: Initialize BiogasCalculator
        biogas_calc = BiogasCalculator()

        # Step 5: Calculate biogas potential for each nearby municipality
        # (if they have the required waste data)
        biogas_results = []

        for idx, row in nearby_municipalities.head(5).iterrows():
            # Check if municipality has biogas data already
            if 'biogas_potential_m3_day' in row and pd.notna(row['biogas_potential_m3_day']):
                biogas_value = row['biogas_potential_m3_day']

                # Biogas potential should be non-negative
                assert biogas_value >= 0, f"Negative biogas value for {row['municipality']}"

                biogas_results.append({
                    'municipality': row['municipality'],
                    'distance_km': row['distance_km'],
                    'biogas_potential_m3_day': biogas_value
                })

        # Should have calculated biogas for at least one municipality
        assert len(biogas_results) > 0, "No biogas calculations performed"

    def test_workflow_database_to_geospatial(self):
        """Test workflow from database loading to geospatial analysis"""
        # Load data
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        assert df is not None
        assert len(df) > 0

        # Get top municipality by biogas potential
        if 'biogas_potential_m3_day' in df.columns:
            top_municipality = df.nlargest(1, 'biogas_potential_m3_day')

            # Should have coordinates
            assert 'latitude' in top_municipality.columns
            assert 'longitude' in top_municipality.columns

            lat = top_municipality['latitude'].iloc[0]
            lon = top_municipality['longitude'].iloc[0]

            if pd.notna(lat) and pd.notna(lon):
                # Use geospatial analyzer
                geo_analyzer = GeospatialAnalyzer()

                df_geo = df.copy()
                df_geo['lat'] = df_geo['latitude']
                df_geo['lon'] = df_geo['longitude']

                # Find municipalities within 100km
                nearby = geo_analyzer.find_municipalities_in_radius(
                    df_geo, lat, lon, 100
                )

                # Should find at least the top municipality itself
                assert len(nearby) >= 1

    def test_workflow_catchment_analysis(self):
        """Test complete catchment analysis workflow"""
        # Load data
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is None or len(df) == 0:
            pytest.skip("No municipality data available")

        # Pick a central location (São Paulo city)
        sp_lat, sp_lon = -23.5505, -46.6333

        # Prepare geospatial data
        df_geo = df.copy()
        df_geo['lat'] = df_geo['latitude']
        df_geo['lon'] = df_geo['longitude']

        # Initialize analyzer
        geo_analyzer = GeospatialAnalyzer()

        # Calculate catchment statistics if biogas_potential column exists
        if 'biogas_potential_m3_day' in df_geo.columns:
            stats = geo_analyzer.calculate_catchment_statistics(
                df_geo, sp_lat, sp_lon, radius_km=50,
                value_column='biogas_potential_m3_day'
            )

            # If any municipalities in radius, should have stats
            if stats:
                assert 'total_value' in stats
                assert 'mean_value' in stats
                assert 'count_municipalities' in stats
                assert stats['count_municipalities'] > 0

    def test_workflow_batch_calculation(self):
        """Test batch biogas calculation workflow"""
        # Load database
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is None or len(df) == 0:
            pytest.skip("No municipality data available")

        # Create sample batch data with waste inputs
        sample_batch = pd.DataFrame({
            'municipality': ['Test City A', 'Test City B', 'Test City C'],
            'urban_waste_tons_day': [100, 200, 150],
            'rural_waste_tons_day': [50, 30, 75],
            'population': [100000, 200000, 150000]
        })

        # Initialize calculator
        biogas_calc = BiogasCalculator()

        # Run batch calculation
        result = biogas_calc.calculate_batch_municipalities(sample_batch)

        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'biogas_potential_m3_day' in result.columns
        assert 'energy_potential_kwh_day' in result.columns

        # All biogas values should be positive
        assert (result['biogas_potential_m3_day'] > 0).all()

    def test_workflow_state_totals(self):
        """Test state-wide totals calculation workflow"""
        # Load database
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is None or len(df) == 0:
            pytest.skip("No municipality data available")

        # Initialize calculator
        biogas_calc = BiogasCalculator()

        # Calculate state totals
        totals = biogas_calc.get_state_totals(df)

        # Verify totals structure
        assert isinstance(totals, dict)

        if 'total_municipalities' in totals:
            # Should match loaded data
            assert totals['total_municipalities'] == len(df)

        if 'total_biogas_m3_day' in totals:
            # Should be positive if data exists
            assert totals['total_biogas_m3_day'] >= 0

    def test_workflow_validation_chain(self):
        """Test validation workflow: validate database → validate inputs → calculate"""
        # Step 1: Validate database
        db_loader = DatabaseLoader()
        db_valid = db_loader.validate_database()

        assert db_valid is True, "Database validation failed"

        # Step 2: Load data
        df = db_loader.load_municipalities_data()
        assert df is not None, "Data loading failed"

        # Step 3: Validate biogas calculator inputs
        biogas_calc = BiogasCalculator()

        # Test with valid inputs
        valid = biogas_calc.validate_inputs(100, 50, 100000)
        assert valid is True

        # Test with invalid inputs
        invalid = biogas_calc.validate_inputs(-100, 50, 100000)
        assert invalid is False

        # Step 4: Calculate only if validation passes
        if valid:
            result = biogas_calc.calculate_municipality_potential(100, 50, 100000)
            assert 'biogas_potential_m3_day' in result
            assert result['biogas_potential_m3_day'] > 0


class TestModuleInteraction:
    """Test interactions between different modules"""

    def test_database_provides_geospatial_data(self):
        """Test that database provides necessary data for geospatial analysis"""
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is not None and len(df) > 0:
            # Should have coordinates for geospatial analysis
            assert 'latitude' in df.columns or 'lat' in df.columns
            assert 'longitude' in df.columns or 'lon' in df.columns

    def test_database_provides_calculator_data(self):
        """Test that database provides necessary data for biogas calculations"""
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is not None and len(df) > 0:
            # Should have biogas-related columns
            biogas_columns = [col for col in df.columns if 'biogas' in col.lower()]
            assert len(biogas_columns) > 0, "No biogas columns found in database"

    def test_geospatial_filters_for_calculator(self):
        """Test that geospatial filtering provides valid input for calculations"""
        # Load data
        db_loader = DatabaseLoader()
        df = db_loader.load_municipalities_data()

        if df is None or len(df) == 0:
            pytest.skip("No municipality data available")

        # Add lat/lon columns
        df['lat'] = df['latitude']
        df['lon'] = df['longitude']

        # Filter with geospatial
        geo_analyzer = GeospatialAnalyzer()
        filtered = geo_analyzer.find_municipalities_in_radius(
            df, -22.7253, -47.6489, radius_km=50
        )

        if len(filtered) > 0:
            # Filtered data should still have necessary columns for calculations
            assert 'municipality' in filtered.columns

    def test_conversion_factors_consistency(self):
        """Test that conversion factors are consistently used across modules"""
        from src.core.biogas_calculator import ConversionFactors

        # Create calculator with custom factors
        custom_factors = ConversionFactors(
            biogas_yield_organic=0.7,
            methane_content=0.65
        )

        biogas_calc = BiogasCalculator(factors=custom_factors)

        # Verify factors are applied
        info = biogas_calc.get_conversion_factors_info()

        assert '0.7' in info['biogas_yield_organic']
        assert '65' in info['methane_content']

        # Calculate with custom factors
        result = biogas_calc.calculate_municipality_potential(100, 0, 100000)

        # Should produce results
        assert result['biogas_potential_m3_day'] > 0


class TestErrorPropagation:
    """Test how errors propagate through the workflow"""

    def test_invalid_database_path_workflow(self):
        """Test workflow with invalid database path"""
        from pathlib import Path

        invalid_loader = DatabaseLoader(db_path=Path("/invalid/path/db.db"))

        # Should initialize without crashing
        assert invalid_loader.db_path.name == "db.db"

        # Validation should fail
        valid = invalid_loader.validate_database()
        assert valid is False

        # Load should return None
        df = invalid_loader.load_municipalities_data()
        # May return None or raise exception depending on implementation

    def test_empty_dataframe_workflow(self):
        """Test workflow with empty DataFrame"""
        # Create empty DataFrame
        df_empty = pd.DataFrame()

        # Geospatial analysis
        geo_analyzer = GeospatialAnalyzer()
        result = geo_analyzer.find_municipalities_in_radius(
            df_empty, -22.7253, -47.6489, 50
        )

        # Should return empty DataFrame without crashing
        assert len(result) == 0

        # Biogas calculator
        biogas_calc = BiogasCalculator()
        totals = biogas_calc.get_state_totals(df_empty)

        # Should return dict (possibly empty or with zeros)
        assert isinstance(totals, dict)

    def test_missing_coordinates_workflow(self):
        """Test workflow when coordinates are missing"""
        # DataFrame without coordinates
        df_no_coords = pd.DataFrame({
            'municipality': ['Test City'],
            'biogas_potential_m3_day': [10000]
        })

        geo_analyzer = GeospatialAnalyzer()

        # Should handle gracefully
        result = geo_analyzer.find_municipalities_in_radius(
            df_no_coords, -22.7253, -47.6489, 50
        )

        # Should return empty or error gracefully
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
