"""
Core business logic for biogas calculations and geospatial operations
"""

from .biogas_calculator import BiogasCalculator, get_biogas_calculator

# Backward compatibility: provide default instance via factory
biogas_calculator = get_biogas_calculator()

__all__ = ["BiogasCalculator", "get_biogas_calculator", "biogas_calculator"]