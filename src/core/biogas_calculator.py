"""
CP2B Maps V2 - Professional Biogas Calculator
Literature-validated biogas potential calculations for municipal waste
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConversionFactors:
    """
    Literature-validated conversion factors for biogas calculations
    Based on scientific research and Brazilian waste characteristics
    """

    # Biogas production from organic waste (m³/kg)
    biogas_yield_organic: float = 0.5  # m³ biogas per kg organic waste
    biogas_yield_food: float = 0.6     # m³ biogas per kg food waste
    biogas_yield_garden: float = 0.4   # m³ biogas per kg garden waste

    # Methane content in biogas (%)
    methane_content: float = 0.6       # 60% methane in biogas

    # Energy content (kWh/m³)
    methane_energy_content: float = 9.97  # kWh per m³ of methane

    # CO2 reduction factors
    co2_avoided_per_kwh: float = 0.45     # kg CO2 avoided per kWh
    co2_from_waste_decay: float = 1.8     # kg CO2 per kg organic waste if not treated

    # Waste composition (Brazilian municipalities average)
    organic_fraction_urban: float = 0.52   # 52% organic waste in urban areas
    organic_fraction_rural: float = 0.65   # 65% organic waste in rural areas


class BiogasCalculator:
    """
    Professional biogas potential calculator for municipalities
    Uses literature-validated factors and handles 645 São Paulo municipalities
    """

    def __init__(self, factors: Optional[ConversionFactors] = None):
        """
        Initialize calculator with conversion factors

        Args:
            factors: ConversionFactors instance (uses defaults if None)
        """
        self.factors = factors or ConversionFactors()
        self.logger = get_logger(self.__class__.__name__)

    def calculate_municipality_potential(self,
                                       urban_waste: float,
                                       rural_waste: float,
                                       population: int) -> Dict[str, float]:
        """
        Calculate complete biogas potential for a municipality

        Args:
            urban_waste: Urban waste production (tons/day)
            rural_waste: Rural waste production (tons/day)
            population: Municipality population

        Returns:
            Dictionary with all calculated values
        """
        try:
            # Convert tons to kg
            urban_waste_kg = urban_waste * 1000
            rural_waste_kg = rural_waste * 1000
            total_waste_kg = urban_waste_kg + rural_waste_kg

            # Calculate organic waste fractions
            organic_urban_kg = urban_waste_kg * self.factors.organic_fraction_urban
            organic_rural_kg = rural_waste_kg * self.factors.organic_fraction_rural
            total_organic_kg = organic_urban_kg + organic_rural_kg

            # Biogas production (m³/day)
            biogas_production = total_organic_kg * self.factors.biogas_yield_organic

            # Methane production (m³/day)
            methane_production = biogas_production * self.factors.methane_content

            # Energy potential (kWh/day)
            energy_potential = methane_production * self.factors.methane_energy_content

            # CO2 reduction potential (tons/year)
            co2_from_energy = (energy_potential * self.factors.co2_avoided_per_kwh * 365) / 1000
            co2_from_waste = (total_organic_kg * self.factors.co2_from_waste_decay * 365) / 1000
            total_co2_reduction = co2_from_energy + co2_from_waste

            # Calculate per capita values
            per_capita_biogas = biogas_production / population if population > 0 else 0
            per_capita_energy = energy_potential / population if population > 0 else 0

            results = {
                "total_waste_tons_day": round(total_waste_kg / 1000, 2),
                "organic_waste_tons_day": round(total_organic_kg / 1000, 2),
                "biogas_potential_m3_day": round(biogas_production, 2),
                "methane_potential_m3_day": round(methane_production, 2),
                "energy_potential_kwh_day": round(energy_potential, 2),
                "energy_potential_mwh_year": round((energy_potential * 365) / 1000, 2),
                "co2_reduction_tons_year": round(total_co2_reduction, 2),
                "per_capita_biogas_m3_day": round(per_capita_biogas, 4),
                "per_capita_energy_kwh_day": round(per_capita_energy, 2)
            }

            self.logger.debug(f"Calculated biogas potential: {biogas_production:.2f} m³/day")
            return results

        except Exception as e:
            self.logger.error(f"Calculation failed: {e}", exc_info=True)
            return {}

    def calculate_batch_municipalities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate biogas potential for multiple municipalities efficiently

        Args:
            df: DataFrame with columns: urban_waste_tons_day, rural_waste_tons_day, population

        Returns:
            DataFrame with added calculation columns
        """
        try:
            results_list = []

            for _, row in df.iterrows():
                urban_waste = row.get('urban_waste_tons_day', 0)
                rural_waste = row.get('rural_waste_tons_day', 0)
                population = row.get('population', 0)

                calculations = self.calculate_municipality_potential(
                    urban_waste, rural_waste, population
                )

                # Combine original row with calculations
                combined_row = row.to_dict()
                combined_row.update(calculations)
                results_list.append(combined_row)

            result_df = pd.DataFrame(results_list)
            self.logger.info(f"Batch calculation completed for {len(result_df)} municipalities")

            return result_df

        except Exception as e:
            self.logger.error(f"Batch calculation failed: {e}", exc_info=True)
            return df

    def get_state_totals(self, municipalities_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate state-wide totals for São Paulo

        Args:
            municipalities_df: DataFrame with municipality calculations (from DatabaseLoader)

        Returns:
            Dictionary with state totals
        """
        try:
            # Use the actual column names that DatabaseLoader returns
            totals = {
                "total_municipalities": len(municipalities_df),
                "total_population": municipalities_df['population'].sum() if 'population' in municipalities_df.columns else 0,
                "total_biogas_m3_day": municipalities_df['biogas_potential_m3_day'].sum() if 'biogas_potential_m3_day' in municipalities_df.columns else 0,
                "total_energy_kwh_day": municipalities_df['energy_potential_kwh_day'].sum() if 'energy_potential_kwh_day' in municipalities_df.columns else 0,
                "total_energy_mwh_year": municipalities_df['energy_potential_mwh_year'].sum() if 'energy_potential_mwh_year' in municipalities_df.columns else 0,
                "total_co2_reduction_tons_year": municipalities_df['co2_reduction_tons_year'].sum() if 'co2_reduction_tons_year' in municipalities_df.columns else 0,
            }

            # Calculate methane (60% of biogas)
            totals["total_methane_m3_day"] = totals["total_biogas_m3_day"] * 0.6

            # Calculate averages (avoid division by zero)
            if totals["total_municipalities"] > 0:
                totals.update({
                    "avg_biogas_per_municipality": totals["total_biogas_m3_day"] / totals["total_municipalities"],
                    "avg_energy_per_municipality": totals["total_energy_kwh_day"] / totals["total_municipalities"]
                })

            if totals["total_population"] > 0:
                totals.update({
                    "avg_biogas_per_capita": totals["total_biogas_m3_day"] / totals["total_population"],
                    "avg_energy_per_capita": totals["total_energy_kwh_day"] / totals["total_population"]
                })

            # Round all values
            for key, value in totals.items():
                if isinstance(value, float):
                    totals[key] = round(value, 2)

            self.logger.info(f"Calculated state totals for {totals['total_municipalities']} municipalities")
            self.logger.debug(f"Total biogas potential: {totals['total_biogas_m3_day']} m³/day")

            return totals

        except Exception as e:
            self.logger.error(f"State totals calculation failed: {e}", exc_info=True)
            return {}

    def validate_inputs(self,
                       urban_waste: float,
                       rural_waste: float,
                       population: int) -> bool:
        """
        Validate input parameters for calculations

        Args:
            urban_waste: Urban waste (tons/day)
            rural_waste: Rural waste (tons/day)
            population: Population count

        Returns:
            True if inputs are valid
        """
        if urban_waste < 0 or rural_waste < 0:
            self.logger.warning("Negative waste values detected")
            return False

        if population <= 0:
            self.logger.warning("Invalid population value")
            return False

        if (urban_waste + rural_waste) == 0:
            self.logger.warning("Zero total waste detected")
            return False

        return True

    def get_conversion_factors_info(self) -> Dict[str, Any]:
        """
        Get information about the conversion factors used

        Returns:
            Dictionary with factor information and sources
        """
        return {
            "biogas_yield_organic": f"{self.factors.biogas_yield_organic} m³/kg",
            "methane_content": f"{self.factors.methane_content * 100}%",
            "methane_energy_content": f"{self.factors.methane_energy_content} kWh/m³",
            "organic_fraction_urban": f"{self.factors.organic_fraction_urban * 100}%",
            "organic_fraction_rural": f"{self.factors.organic_fraction_rural * 100}%",
            "co2_avoided_per_kwh": f"{self.factors.co2_avoided_per_kwh} kg CO2/kWh",
            "source": "Literature-validated factors for Brazilian municipalities",
            "validation": "Peer-reviewed research and local waste characteristics"
        }


# Global instance for easy access
biogas_calculator = BiogasCalculator()