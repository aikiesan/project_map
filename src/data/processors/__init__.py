"""
CP2B Maps V2 - Data Processors Module
Focused, single-responsibility data processing components

Refactored from monolithic DataProcessor class into:
- DatabaseValidator: Database structure and data quality validation
- CoordinateUpdater: Municipality coordinate management
- BiogasRecalculator: Biogas potential calculations and updates
- DataMigrator: Database optimization, fixes, and migrations
"""

from .database_validator import DatabaseValidator, get_database_validator
from .coordinate_updater import CoordinateUpdater, get_coordinate_updater
from .biogas_recalculator import BiogasRecalculator, get_biogas_recalculator
from .data_migrator import DataMigrator, get_data_migrator

# Backward compatibility: Import old DataProcessor if needed
try:
    from .data_processor_legacy import DataProcessor, create_data_processor
    HAS_LEGACY_PROCESSOR = True
except ImportError:
    HAS_LEGACY_PROCESSOR = False

__all__ = [
    # New focused processors
    'DatabaseValidator',
    'CoordinateUpdater',
    'BiogasRecalculator',
    'DataMigrator',
    # Factory functions
    'get_database_validator',
    'get_coordinate_updater',
    'get_biogas_recalculator',
    'get_data_migrator',
]

# Add legacy processor to exports if available
if HAS_LEGACY_PROCESSOR:
    __all__.extend(['DataProcessor', 'create_data_processor'])
