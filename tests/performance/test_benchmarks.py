"""
CP2B Maps - Performance Benchmark Tests
Section 2.6.3 - Performance Testing
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.biogas_calculator import BiogasCalculator
from src.core.geospatial_analysis import GeospatialAnalyzer
from src.data.loaders.database_loader import DatabaseLoader


class TestPerformanceBenchmarks:
    """Performance benchmarks for critical operations"""

    def test_biogas_calculation_performance(self, benchmark):
        """Benchmark: Single municipality biogas calculation
        Target: <100ms per calculation
        """
        calc = BiogasCalculator()

        result = benchmark(
            calc.calculate_municipality_potential,
            urban_waste=100,
            rural_waste=50,
            population=100000
        )

        assert result['biogas_potential_m3_day'] > 0

    def test_haversine_distance_performance(self, benchmark):
        """Benchmark: Haversine distance calculation
        Target: <1ms per calculation
        """
        analyzer = GeospatialAnalyzer()

        result = benchmark(
            analyzer.calculate_distance_haversine,
            lat1=-22.7253, lon1=-47.6489,
            lat2=-23.5505, lon2=-46.6333
        )

        assert result > 0

    def test_database_connection_performance(self, benchmark):
        """Benchmark: Database connection
        Target: <50ms
        """
        def get_connection():
            loader = DatabaseLoader()
            return loader

        result = benchmark(get_connection)
        assert result is not None

    def test_batch_calculation_performance(self, benchmark):
        """Benchmark: Batch calculations (10 municipalities)
        Target: <1s for 10 municipalities
        """
        calc = BiogasCalculator()

        def batch_calc():
            results = []
            for i in range(10):
                result = calc.calculate_municipality_potential(
                    urban_waste=100 + i*10,
                    rural_waste=50 + i*5,
                    population=100000 + i*10000
                )
                results.append(result)
            return results

        results = benchmark(batch_calc)
        assert len(results) == 10
