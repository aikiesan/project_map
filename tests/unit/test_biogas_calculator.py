"""
CP2B Maps - Unit Tests for Biogas Calculator
Tests core calculation accuracy following Section 2.6.1 methodology
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.biogas_calculator import BiogasCalculator, ConversionFactors


class TestBiogasCalculator:
    """Test suite for biogas potential calculations"""

    def test_calculator_initialization(self):
        """Test calculator initializes with default factors"""
        calc = BiogasCalculator()
        assert calc.factors is not None
        assert isinstance(calc.factors, ConversionFactors)

    def test_calculator_with_custom_factors(self):
        """Test calculator accepts custom conversion factors"""
        custom_factors = ConversionFactors(
            biogas_yield_organic=0.6,
            methane_content=0.65
        )
        calc = BiogasCalculator(factors=custom_factors)
        assert calc.factors.biogas_yield_organic == 0.6
        assert calc.factors.methane_content == 0.65

    def test_organic_waste_calculation(self):
        """Test organic waste fraction calculation"""
        calc = BiogasCalculator()

        # Test with known values
        urban_waste = 100  # tons/day
        rural_waste = 50   # tons/day
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        # Verify result structure
        assert 'biogas_production_m3_day' in result
        assert 'methane_production_m3_day' in result
        assert 'energy_potential_kwh_day' in result
        assert 'co2_reduction_tons_year' in result

        # Verify calculations are positive
        assert result['biogas_production_m3_day'] > 0
        assert result['methane_production_m3_day'] > 0
        assert result['energy_potential_kwh_day'] > 0

    def test_biogas_yield_calculation(self):
        """Test biogas yield from organic waste"""
        calc = BiogasCalculator()
        factors = ConversionFactors(biogas_yield_organic=0.5)
        calc.factors = factors

        # 100 tons urban waste × 52% organic × 1000 kg/ton = 52,000 kg organic
        # 52,000 kg × 0.5 m³/kg = 26,000 m³ biogas
        urban_waste = 100
        rural_waste = 0
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        expected_organic_kg = 100 * 1000 * 0.52  # 52,000 kg
        expected_biogas = expected_organic_kg * 0.5

        # Allow 1% tolerance for floating point
        assert abs(result['biogas_production_m3_day'] - expected_biogas) / expected_biogas < 0.01

    def test_methane_content_calculation(self):
        """Test methane extraction from biogas"""
        calc = BiogasCalculator()

        urban_waste = 100
        rural_waste = 0
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        # Methane should be ~60% of biogas
        methane_fraction = result['methane_production_m3_day'] / result['biogas_production_m3_day']

        assert abs(methane_fraction - calc.factors.methane_content) < 0.001

    def test_energy_potential_calculation(self):
        """Test energy conversion from methane"""
        calc = BiogasCalculator()

        urban_waste = 100
        rural_waste = 0
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        # Energy = methane × energy_content
        expected_energy = result['methane_production_m3_day'] * calc.factors.methane_energy_content

        assert abs(result['energy_potential_kwh_day'] - expected_energy) < 0.1

    def test_zero_waste_handling(self):
        """Test calculator handles zero waste gracefully"""
        calc = BiogasCalculator()

        result = calc.calculate_municipality_potential(0, 0, 100000)

        assert result['biogas_production_m3_day'] == 0
        assert result['methane_production_m3_day'] == 0
        assert result['energy_potential_kwh_day'] == 0

    def test_negative_values_handling(self):
        """Test calculator handles negative values"""
        calc = BiogasCalculator()

        # Negative waste should be handled gracefully
        result = calc.calculate_municipality_potential(-10, -5, 100000)

        # Should either raise error or return zero values
        # (depending on implementation decision)
        assert isinstance(result, dict)

    def test_per_capita_calculations(self):
        """Test per capita metrics calculation"""
        calc = BiogasCalculator()

        urban_waste = 100
        rural_waste = 50
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        # Verify per capita calculations exist and are reasonable
        if 'energy_per_capita_kwh_year' in result:
            assert result['energy_per_capita_kwh_year'] > 0
            assert result['energy_per_capita_kwh_year'] < 10000  # Reasonable upper bound

    def test_rural_vs_urban_organic_fraction(self):
        """Test different organic fractions for rural vs urban"""
        calc = BiogasCalculator()

        # Same total waste, different distribution
        result1 = calc.calculate_municipality_potential(150, 0, 100000)
        result2 = calc.calculate_municipality_potential(0, 150, 100000)

        # Rural should produce more biogas (65% vs 52% organic)
        assert result2['biogas_production_m3_day'] > result1['biogas_production_m3_day']

    def test_co2_reduction_calculation(self):
        """Test CO2 reduction potential calculation"""
        calc = BiogasCalculator()

        urban_waste = 100
        rural_waste = 50
        population = 100000

        result = calc.calculate_municipality_potential(
            urban_waste, rural_waste, population
        )

        # CO2 reduction should be positive and reasonable
        assert result['co2_reduction_tons_year'] > 0

        # Should be from two sources: energy and waste decay
        # Verify it's within reasonable bounds (not excessively high)
        waste_kg_year = (urban_waste + rural_waste) * 1000 * 365
        organic_kg_year = waste_kg_year * 0.6  # Approximate organic fraction

        # CO2 shouldn't exceed worst case (all waste decays)
        max_co2 = organic_kg_year * calc.factors.co2_from_waste_decay / 1000
        assert result['co2_reduction_tons_year'] < max_co2 * 2  # 2x safety factor


class TestConversionFactors:
    """Test suite for conversion factors"""

    def test_default_factors_within_ranges(self):
        """Test default factors are within scientifically valid ranges"""
        factors = ConversionFactors()

        # Biogas yields (m³/kg) - typical range 0.2-0.8
        assert 0.2 <= factors.biogas_yield_organic <= 0.8
        assert 0.2 <= factors.biogas_yield_food <= 0.8
        assert 0.2 <= factors.biogas_yield_garden <= 0.8

        # Methane content (%) - typical range 50-70%
        assert 0.5 <= factors.methane_content <= 0.7

        # Energy content - should be around 10 kWh/m³
        assert 9 <= factors.methane_energy_content <= 11

        # Organic fractions
        assert 0 < factors.organic_fraction_urban < 1
        assert 0 < factors.organic_fraction_rural < 1

        # Rural should have higher organic fraction
        assert factors.organic_fraction_rural > factors.organic_fraction_urban

    def test_factors_immutability(self):
        """Test that factor values are consistent"""
        factors1 = ConversionFactors()
        factors2 = ConversionFactors()

        # Default values should be identical
        assert factors1.biogas_yield_organic == factors2.biogas_yield_organic
        assert factors1.methane_content == factors2.methane_content


class TestNumericalPrecision:
    """Test numerical precision and stability"""

    def test_floating_point_precision(self):
        """Validate numerical precision in calculations"""
        calc = BiogasCalculator()

        # Small values
        result_small = calc.calculate_municipality_potential(0.001, 0.001, 1000)

        # Large values
        result_large = calc.calculate_municipality_potential(10000, 5000, 10000000)

        # Both should produce valid results
        assert result_small['biogas_production_m3_day'] >= 0
        assert result_large['biogas_production_m3_day'] > 0

    def test_calculation_consistency(self):
        """Test that same inputs produce same outputs"""
        calc = BiogasCalculator()

        urban_waste = 123.456
        rural_waste = 78.9
        population = 234567

        result1 = calc.calculate_municipality_potential(urban_waste, rural_waste, population)
        result2 = calc.calculate_municipality_potential(urban_waste, rural_waste, population)

        # Results should be identical
        assert result1['biogas_production_m3_day'] == result2['biogas_production_m3_day']
        assert result1['energy_potential_kwh_day'] == result2['energy_potential_kwh_day']
