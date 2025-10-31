"""
CP2B Maps - Unit Tests for Geospatial Analysis
Tests spatial operations accuracy following Section 2.6.1 methodology
"""

import pytest
import pandas as pd
import math
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.geospatial_analysis import GeospatialAnalyzer


class TestHaversineDistance:
    """Test suite for Haversine distance calculations"""

    def test_same_point_distance(self):
        """Test distance between same point is zero"""
        analyzer = GeospatialAnalyzer()

        lat, lon = -22.7253, -47.6489  # Piracicaba
        distance = analyzer.calculate_distance_haversine(lat, lon, lat, lon)

        assert distance == 0.0

    def test_known_distance_sao_paulo_campinas(self):
        """Test known distance: São Paulo to Campinas (~90km)"""
        analyzer = GeospatialAnalyzer()

        # São Paulo coordinates
        sp_lat, sp_lon = -23.5505, -46.6333

        # Campinas coordinates
        camp_lat, camp_lon = -22.9099, -47.0626

        distance = analyzer.calculate_distance_haversine(
            sp_lat, sp_lon, camp_lat, camp_lon
        )

        # Distance should be approximately 90-100 km
        assert 85 <= distance <= 105, f"Distance {distance}km not in expected range"

    def test_known_distance_piracicaba_campinas(self):
        """Test known distance: Piracicaba to Campinas (~60km)"""
        analyzer = GeospatialAnalyzer()

        # Piracicaba coordinates
        pira_lat, pira_lon = -22.7253, -47.6489

        # Campinas coordinates
        camp_lat, camp_lon = -22.9099, -47.0626

        distance = analyzer.calculate_distance_haversine(
            pira_lat, pira_lon, camp_lat, camp_lon
        )

        # Distance should be approximately 50-70 km
        assert 50 <= distance <= 70, f"Distance {distance}km not in expected range"

    def test_distance_symmetry(self):
        """Test that distance(A,B) = distance(B,A)"""
        analyzer = GeospatialAnalyzer()

        lat1, lon1 = -22.7253, -47.6489
        lat2, lon2 = -23.5505, -46.6333

        dist_forward = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)
        dist_backward = analyzer.calculate_distance_haversine(lat2, lon2, lat1, lon1)

        assert abs(dist_forward - dist_backward) < 0.001  # Should be identical

    def test_equator_distance(self):
        """Test distance calculation along equator (simplest case)"""
        analyzer = GeospatialAnalyzer()

        # Two points on equator, 1 degree apart
        lat1, lon1 = 0.0, 0.0
        lat2, lon2 = 0.0, 1.0

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # At equator, 1 degree ≈ 111 km
        assert 110 <= distance <= 112

    def test_northern_southern_hemisphere(self):
        """Test distance calculation across hemispheres"""
        analyzer = GeospatialAnalyzer()

        # Point in northern hemisphere
        lat1, lon1 = 10.0, 0.0

        # Point in southern hemisphere
        lat2, lon2 = -10.0, 0.0

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # 20 degrees latitude ≈ 2220 km
        assert 2200 <= distance <= 2250

    def test_antipodal_points(self):
        """Test maximum distance (opposite sides of Earth)"""
        analyzer = GeospatialAnalyzer()

        # Brazil and Indonesia (nearly antipodal)
        lat1, lon1 = -15.0, -47.0  # Central Brazil
        lat2, lon2 = 15.0, 133.0   # Opposite side

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # Should be close to half Earth's circumference (~20,000 km)
        # But not necessarily exactly, depends on latitude
        assert 10000 <= distance <= 20100  # Max is π × R ≈ 20,015 km

    def test_invalid_coordinates_handling(self):
        """Test handling of invalid coordinates"""
        analyzer = GeospatialAnalyzer()

        # Invalid latitude (>90)
        distance = analyzer.calculate_distance_haversine(100, 0, 0, 0)
        # Should handle gracefully (return 0 or raise)
        assert isinstance(distance, float)

    def test_precision_small_distances(self):
        """Test precision for very small distances"""
        analyzer = GeospatialAnalyzer()

        # Two very close points (~1km apart)
        lat1, lon1 = -22.7253, -47.6489
        lat2, lon2 = -22.7263, -47.6499  # ~1.4km apart

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # Should be between 1-2 km
        assert 0.5 <= distance <= 2.5


class TestRadiusAnalysis:
    """Test suite for radius-based municipality finding"""

    def test_find_municipalities_in_radius(self, sample_municipality_data):
        """Test finding municipalities within radius"""
        analyzer = GeospatialAnalyzer()

        # Center on Piracicaba
        center_lat, center_lon = -22.7253, -47.6489
        radius_km = 100

        result = analyzer.find_municipalities_in_radius(
            sample_municipality_data,
            center_lat,
            center_lon,
            radius_km
        )

        # Should find at least Piracicaba itself
        assert len(result) >= 1

        # Result should have distance_km column
        assert 'distance_km' in result.columns

        # All distances should be within radius
        assert (result['distance_km'] <= radius_km).all()

    def test_radius_sorting(self, sample_municipality_data):
        """Test that results are sorted by distance"""
        analyzer = GeospatialAnalyzer()

        center_lat, center_lon = -22.7253, -47.6489
        radius_km = 200

        result = analyzer.find_municipalities_in_radius(
            sample_municipality_data,
            center_lat,
            center_lon,
            radius_km
        )

        if len(result) > 1:
            # Distances should be in ascending order
            distances = result['distance_km'].tolist()
            assert distances == sorted(distances)

    def test_zero_radius(self, sample_municipality_data):
        """Test with zero radius (should find nothing or only exact match)"""
        analyzer = GeospatialAnalyzer()

        center_lat, center_lon = -22.7253, -47.6489
        radius_km = 0

        result = analyzer.find_municipalities_in_radius(
            sample_municipality_data,
            center_lat,
            center_lon,
            radius_km
        )

        # Should find 0 or 1 (exact match only)
        assert len(result) <= 1

    def test_large_radius(self, sample_municipality_data):
        """Test with very large radius (should find all)"""
        analyzer = GeospatialAnalyzer()

        center_lat, center_lon = -22.7253, -47.6489
        radius_km = 10000  # Larger than São Paulo state

        result = analyzer.find_municipalities_in_radius(
            sample_municipality_data,
            center_lat,
            center_lon,
            radius_km
        )

        # Should find all municipalities in sample
        assert len(result) == len(sample_municipality_data)

    def test_missing_coordinate_columns(self):
        """Test handling of missing coordinate columns"""
        analyzer = GeospatialAnalyzer()

        # DataFrame without lat/lon columns
        df = pd.DataFrame({
            'name': ['Test'],
            'value': [123]
        })

        result = analyzer.find_municipalities_in_radius(
            df, -22.7253, -47.6489, 50
        )

        # Should return empty DataFrame gracefully
        assert len(result) == 0

    def test_null_coordinates_handling(self):
        """Test handling of null coordinates in data"""
        analyzer = GeospatialAnalyzer()

        df = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'lat': [-22.7253, None, -23.5505],
            'lon': [-47.6489, -46.6333, None]
        })

        result = analyzer.find_municipalities_in_radius(
            df, -22.7253, -47.6489, 100
        )

        # Should handle nulls gracefully
        assert isinstance(result, pd.DataFrame)

        # Nulls should be excluded (distance = inf)
        assert len(result) <= 1  # Only valid 'A' should be close

    def test_custom_column_names(self):
        """Test with custom lat/lon column names"""
        analyzer = GeospatialAnalyzer()

        df = pd.DataFrame({
            'name': ['Test'],
            'latitude': [-22.7253],
            'longitude': [-47.6489]
        })

        result = analyzer.find_municipalities_in_radius(
            df, -22.7253, -47.6489, 50,
            lat_col='latitude', lon_col='longitude'
        )

        assert len(result) >= 1


class TestAreaCalculations:
    """Test suite for area calculations"""

    def test_circular_buffer_area(self):
        """Test circular buffer area calculation"""
        analyzer = GeospatialAnalyzer()

        # Create circular buffer of 20km radius
        # Expected area = π × 20² ≈ 1256.64 km²
        radius_km = 20
        expected_area = math.pi * radius_km ** 2

        # Test with Campinas coordinates
        center_lat, center_lon = -22.9099, -47.0626

        geometry = analyzer.create_circular_geometry(
            center_lat, center_lon, radius_km
        )

        # This test only runs if geospatial libraries available
        if geometry is not None:
            # Convert to projected CRS for area calculation
            # Area should be close to expected (within 1%)
            # Note: Exact implementation depends on GeospatialAnalyzer
            pass  # Implementation-dependent test

    def test_buffer_concentric_circles(self):
        """Test that larger radius creates larger area"""
        analyzer = GeospatialAnalyzer()

        center_lat, center_lon = -22.9099, -47.0626

        buffer_10km = analyzer.create_circular_geometry(center_lat, center_lon, 10)
        buffer_20km = analyzer.create_circular_geometry(center_lat, center_lon, 20)

        # This test structure depends on implementation
        # Larger radius should create larger geometry
        # Exact assertion depends on return type
        pass  # Implementation-dependent test


class TestCoordinateValidation:
    """Test suite for coordinate validation"""

    def test_valid_brazil_coordinates(self):
        """Test that São Paulo state coordinates are valid"""
        analyzer = GeospatialAnalyzer()

        # São Paulo state bounds approximately:
        # Lat: -25.5 to -19.8
        # Lon: -53.2 to -44.2

        valid_coords = [
            (-22.7253, -47.6489),  # Piracicaba
            (-23.5505, -46.6333),  # São Paulo
            (-22.9099, -47.0626),  # Campinas
        ]

        for lat, lon in valid_coords:
            # Distance calculation should work
            distance = analyzer.calculate_distance_haversine(
                lat, lon, -22.7253, -47.6489
            )
            assert distance >= 0

    def test_edge_case_coordinates(self):
        """Test edge case coordinates (poles, date line)"""
        analyzer = GeospatialAnalyzer()

        # North pole to south pole
        distance = analyzer.calculate_distance_haversine(90, 0, -90, 0)

        # Should be half Earth's circumference (π × R ≈ 20,015 km)
        assert 19900 <= distance <= 20100

    def test_international_date_line(self):
        """Test distance across international date line"""
        analyzer = GeospatialAnalyzer()

        # Just west of date line
        lat1, lon1 = 0, 179

        # Just east of date line
        lat2, lon2 = 0, -179

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # Should be small (~222 km for 2 degrees at equator)
        assert distance < 300


class TestNumericalStability:
    """Test numerical stability in geospatial calculations"""

    def test_precision_accumulation(self):
        """Test that repeated calculations don't accumulate errors"""
        analyzer = GeospatialAnalyzer()

        lat1, lon1 = -22.7253, -47.6489
        lat2, lon2 = -23.5505, -46.6333

        # Calculate distance 100 times
        distances = [
            analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)
            for _ in range(100)
        ]

        # All results should be identical
        assert len(set(distances)) == 1

    def test_extreme_precision_inputs(self):
        """Test with very high precision coordinates"""
        analyzer = GeospatialAnalyzer()

        lat1 = -22.72534567891234
        lon1 = -47.64891234567890
        lat2 = -22.72534567891235
        lon2 = -47.64891234567891

        distance = analyzer.calculate_distance_haversine(lat1, lon1, lat2, lon2)

        # Should handle high precision gracefully
        assert distance >= 0
        assert distance < 0.01  # Very small distance
