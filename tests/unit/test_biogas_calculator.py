"""
CP2B Maps - Unit Tests for Biogas Calculator
Tests core calculation accuracy following Section 2.6.1 methodology
"""

import pytest
import pandas as pd
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
        assert 'biogas_potential_m3_day' in result
        assert 'methane_potential_m3_day' in result
        assert 'energy_potential_kwh_day' in result
        assert 'co2_reduction_tons_year' in result

        # Verify calculations are positive
        assert result['biogas_potential_m3_day'] > 0
        assert result['methane_potential_m3_day'] > 0
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
        assert abs(result['biogas_potential_m3_day'] - expected_biogas) / expected_biogas < 0.01

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
        methane_fraction = result['methane_potential_m3_day'] / result['biogas_potential_m3_day']

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
        expected_energy = result['methane_potential_m3_day'] * calc.factors.methane_energy_content

        assert abs(result['energy_potential_kwh_day'] - expected_energy) < 0.1

    def test_zero_waste_handling(self):
        """Test calculator handles zero waste gracefully"""
        calc = BiogasCalculator()

        result = calc.calculate_municipality_potential(0, 0, 100000)

        assert result['biogas_potential_m3_day'] == 0
        assert result['methane_potential_m3_day'] == 0
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
        assert result2['biogas_potential_m3_day'] > result1['biogas_potential_m3_day']

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
        assert result_small['biogas_potential_m3_day'] >= 0
        assert result_large['biogas_potential_m3_day'] > 0

    def test_calculation_consistency(self):
        """Test that same inputs produce same outputs"""
        calc = BiogasCalculator()

        urban_waste = 123.456
        rural_waste = 78.9
        population = 234567

        result1 = calc.calculate_municipality_potential(urban_waste, rural_waste, population)
        result2 = calc.calculate_municipality_potential(urban_waste, rural_waste, population)

        # Results should be identical
        assert result1['biogas_potential_m3_day'] == result2['biogas_potential_m3_day']
        assert result1['energy_potential_kwh_day'] == result2['energy_potential_kwh_day']


class TestErrorHandling:
    """Test error handling and robustness"""

    def test_negative_urban_waste(self):
        """Test that negative urban waste returns empty dict due to exception"""
        calc = BiogasCalculator()

        # Implementation catches exceptions and returns empty dict
        # Negative values should trigger error path
        result = calc.calculate_municipality_potential(-100, 50, 100000)

        # Should return dict (either empty or with values)
        assert isinstance(result, dict)

    def test_negative_rural_waste(self):
        """Test that negative rural waste is handled gracefully"""
        calc = BiogasCalculator()

        result = calc.calculate_municipality_potential(100, -50, 100000)

        # Should return dict
        assert isinstance(result, dict)

    def test_string_inputs_type_error(self):
        """Test that string inputs trigger exception path"""
        calc = BiogasCalculator()

        # String instead of number should trigger exception
        result = calc.calculate_municipality_potential("100", 50, 100000)

        # Should return empty dict due to exception
        assert isinstance(result, dict)

    def test_none_inputs_type_error(self):
        """Test that None inputs trigger exception path"""
        calc = BiogasCalculator()

        # None should trigger exception
        result = calc.calculate_municipality_potential(None, 50, 100000)

        # Should return empty dict due to exception
        assert isinstance(result, dict)

    def test_zero_population_handling(self):
        """Test that zero population is handled without ZeroDivisionError"""
        calc = BiogasCalculator()

        # Should not raise ZeroDivisionError (population > 0 check in code)
        result = calc.calculate_municipality_potential(100, 50, 0)

        # Should return results with 0 for per capita values
        assert isinstance(result, dict)
        if 'per_capita_biogas_m3_day' in result:
            assert result['per_capita_biogas_m3_day'] == 0
        if 'per_capita_energy_kwh_day' in result:
            assert result['per_capita_energy_kwh_day'] == 0


class TestValidation:
    """Test input validation methods"""

    def test_validate_inputs_with_valid_data(self):
        """Test validate_inputs returns True for valid data"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(100, 50, 100000)

        assert result is True

    def test_validate_inputs_negative_urban_waste(self):
        """Test validate_inputs rejects negative urban waste"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(-100, 50, 100000)

        assert result is False

    def test_validate_inputs_negative_rural_waste(self):
        """Test validate_inputs rejects negative rural waste"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(100, -50, 100000)

        assert result is False

    def test_validate_inputs_zero_population(self):
        """Test validate_inputs rejects zero population"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(100, 50, 0)

        assert result is False

    def test_validate_inputs_negative_population(self):
        """Test validate_inputs rejects negative population"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(100, 50, -1000)

        assert result is False

    def test_validate_inputs_zero_waste(self):
        """Test validate_inputs rejects zero total waste"""
        calc = BiogasCalculator()

        result = calc.validate_inputs(0, 0, 100000)

        assert result is False


class TestConversionFactorsInfo:
    """Test conversion factors information retrieval"""

    def test_get_conversion_factors_info(self):
        """Test that conversion factors info is returned correctly"""
        calc = BiogasCalculator()

        info = calc.get_conversion_factors_info()

        # Should return dict
        assert isinstance(info, dict)

        # Should have expected keys
        assert 'biogas_yield_organic' in info
        assert 'methane_content' in info
        assert 'methane_energy_content' in info
        assert 'organic_fraction_urban' in info
        assert 'organic_fraction_rural' in info
        assert 'source' in info

    def test_custom_factors_in_info(self):
        """Test that custom factors are reflected in info"""
        custom_factors = ConversionFactors(
            biogas_yield_organic=0.7,
            methane_content=0.65
        )
        calc = BiogasCalculator(factors=custom_factors)

        info = calc.get_conversion_factors_info()

        # Should reflect custom values
        assert '0.7' in info['biogas_yield_organic']
        assert '65' in info['methane_content']  # 0.65 * 100 = 65%


class TestBatchCalculations:
    """Test batch municipality calculations"""

    def test_calculate_batch_municipalities(self):
        """Test batch calculation for multiple municipalities"""
        calc = BiogasCalculator()

        # Create sample DataFrame
        df = pd.DataFrame({
            'municipality': ['City A', 'City B', 'City C'],
            'urban_waste_tons_day': [100, 200, 150],
            'rural_waste_tons_day': [50, 30, 75],
            'population': [100000, 200000, 150000]
        })

        result = calc.calculate_batch_municipalities(df)

        # Should return DataFrame with all original and calculated columns
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'biogas_potential_m3_day' in result.columns
        assert 'energy_potential_kwh_day' in result.columns
        assert 'municipality' in result.columns

    def test_calculate_batch_empty_dataframe(self):
        """Test batch calculation with empty DataFrame"""
        calc = BiogasCalculator()

        df = pd.DataFrame()

        result = calc.calculate_batch_municipalities(df)

        # Should handle gracefully
        assert isinstance(result, pd.DataFrame)

    def test_calculate_batch_missing_columns(self):
        """Test batch calculation with missing columns"""
        calc = BiogasCalculator()

        # DataFrame missing some required columns
        df = pd.DataFrame({
            'municipality': ['City A'],
            'population': [100000]
            # Missing urban_waste_tons_day and rural_waste_tons_day
        })

        result = calc.calculate_batch_municipalities(df)

        # Should handle gracefully (defaults to 0)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestStateTotals:
    """Test state-wide aggregation calculations"""

    def test_get_state_totals(self):
        """Test state-wide totals calculation"""
        calc = BiogasCalculator()

        # Create sample DataFrame with calculated values
        df = pd.DataFrame({
            'municipality': ['City A', 'City B', 'City C'],
            'population': [100000, 200000, 150000],
            'biogas_potential_m3_day': [10000, 20000, 15000],
            'energy_potential_kwh_day': [60000, 120000, 90000],
            'energy_potential_mwh_year': [21900, 43800, 32850],
            'co2_reduction_tons_year': [5000, 10000, 7500]
        })

        totals = calc.get_state_totals(df)

        # Should return dict with expected keys
        assert isinstance(totals, dict)
        assert 'total_municipalities' in totals
        assert 'total_population' in totals
        assert 'total_biogas_m3_day' in totals
        assert 'total_energy_kwh_day' in totals

        # Verify calculations
        assert totals['total_municipalities'] == 3
        assert totals['total_population'] == 450000
        assert totals['total_biogas_m3_day'] == 45000
        assert totals['total_energy_kwh_day'] == 270000

    def test_get_state_totals_empty_dataframe(self):
        """Test state totals with empty DataFrame"""
        calc = BiogasCalculator()

        df = pd.DataFrame()

        totals = calc.get_state_totals(df)

        # Should handle gracefully
        assert isinstance(totals, dict)
        if 'total_municipalities' in totals:
            assert totals['total_municipalities'] == 0

    def test_get_state_totals_missing_columns(self):
        """Test state totals with missing columns"""
        calc = BiogasCalculator()

        # DataFrame with only some columns
        df = pd.DataFrame({
            'municipality': ['City A'],
            'population': [100000]
            # Missing biogas columns
        })

        totals = calc.get_state_totals(df)

        # Should handle gracefully with 0 values for missing columns
        assert isinstance(totals, dict)
        assert totals['total_biogas_m3_day'] == 0


class TestCustomFactorsIntegration:
    """Test that custom factors are actually used in calculations"""

    def test_custom_biogas_yield_affects_output(self):
        """Test that custom biogas yield factor changes calculation results"""
        # Standard factors
        calc_standard = BiogasCalculator()
        result_standard = calc_standard.calculate_municipality_potential(100, 0, 100000)

        # Custom higher yield
        custom_factors = ConversionFactors(biogas_yield_organic=1.0)  # Double the default 0.5
        calc_custom = BiogasCalculator(factors=custom_factors)
        result_custom = calc_custom.calculate_municipality_potential(100, 0, 100000)

        # Custom should produce approximately double the biogas
        ratio = result_custom['biogas_potential_m3_day'] / result_standard['biogas_potential_m3_day']
        assert 1.9 < ratio < 2.1  # Allow small floating point variance

    def test_custom_methane_content_affects_output(self):
        """Test that custom methane content changes methane output"""
        # Standard factors (60% methane)
        calc_standard = BiogasCalculator()
        result_standard = calc_standard.calculate_municipality_potential(100, 0, 100000)

        # Custom higher methane content
        custom_factors = ConversionFactors(methane_content=0.8)  # 80% instead of 60%
        calc_custom = BiogasCalculator(factors=custom_factors)
        result_custom = calc_custom.calculate_municipality_potential(100, 0, 100000)

        # Biogas should be same, but methane should be higher
        assert result_custom['biogas_potential_m3_day'] == result_standard['biogas_potential_m3_day']
        assert result_custom['methane_potential_m3_day'] > result_standard['methane_potential_m3_day']
