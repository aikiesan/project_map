"""
CP2B Maps - Pytest Configuration and Fixtures
Shared test fixtures for unit, integration, and performance testing
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_municipality_data():
    """Sample municipality data for testing"""
    return pd.DataFrame({
        'ibge_code': [3538709, 3550308, 3509502],
        'municipality': ['Piracicaba', 'São Paulo', 'Campinas'],
        'lat': [-22.7253, -23.5505, -22.9099],
        'lon': [-47.6489, -46.6333, -47.0626],
        'population': [404142, 12325232, 1213792],
        'biogas_potential_m3_year': [50000000, 500000000, 100000000]
    })


@pytest.fixture
def sample_correction_factors():
    """Sample correction factors for testing"""
    return {
        'FC': 0.98,   # Collection factor
        'FCo': 0.02,  # Competition factor
        'FS': 0.70,   # Sustainability factor
        'FL': 0.85    # Logistics factor
    }


@pytest.fixture
def sample_production_data():
    """Sample agricultural production data"""
    return {
        'sugarcane_production': 1000000,  # tons
        'cattle_herd': 50000,
        'swine_herd': 10000,
        'poultry_herd': 500000
    }


@pytest.fixture
def known_values():
    """Known validation values from literature"""
    return {
        'sp_bagasse_theoretical_range': (100e6, 140e6),  # tons/year
        'bagasse_rpr': 0.21,  # Residue-to-product ratio
        'bagasse_moisture': 0.50,
        'cattle_manure_daily': 34.8,  # L/day per animal
        'earth_radius_km': 6371
    }
