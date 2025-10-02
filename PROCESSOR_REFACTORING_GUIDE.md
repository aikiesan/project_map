# Data Processor Refactoring Guide

## 🎯 Overview

The monolithic `DataProcessor` class (741 lines) has been refactored into **four focused, single-responsibility classes** following SOLID principles.

## 📦 New Architecture

### Before (Monolithic)
```python
from src.data.processors import DataProcessor

processor = DataProcessor()
processor.validate_database()
processor.add_coordinates_from_shapefile()
processor.recalculate_biogas_potentials()
processor.perform_final_database_fix()
```

### After (Focused Classes)
```python
from src.data.processors import (
    DatabaseValidator,
    CoordinateUpdater,
    BiogasRecalculator,
    DataMigrator
)

# Or use factory functions
from src.data.processors import (
    get_database_validator,
    get_coordinate_updater,
    get_biogas_recalculator,
    get_data_migrator
)
```

## 🔧 New Classes

### 1. **DatabaseValidator** (`database_validator.py`)
**Responsibility:** Database structure validation and data quality checks

**Methods:**
- `validate_database(census_csv_path)` - Full database validation
- `validate_structure(conn)` - Check table structure
- `validate_data_quality(conn)` - Check data quality metrics
- `update_with_census_data(conn, csv_path)` - Update from census CSV
- `generate_statistics(conn)` - Generate database stats
- `check_data_integrity()` - Quick integrity check

**Example:**
```python
validator = get_database_validator()
results = validator.validate_database("path/to/census.csv")
print(f"Quality Score: {results['quality_check']['quality_score']}")
```

### 2. **CoordinateUpdater** (`coordinate_updater.py`)
**Responsibility:** Municipality coordinate management and updates

**Methods:**
- `update_from_shapefile(shapefile_path)` - Update from shapefile centroids
- `batch_update_coordinates(updates)` - Batch coordinate updates
- `update_single_coordinate(code, lat, lon)` - Update single municipality
- `get_missing_coordinates()` - Find municipalities without coordinates
- `validate_all_coordinates()` - Validate coordinate ranges

**Example:**
```python
updater = get_coordinate_updater()
results = updater.update_from_shapefile()
print(f"Updated {results['coordinates_updated']} municipalities")
```

### 3. **BiogasRecalculator** (`biogas_recalculator.py`)
**Responsibility:** Biogas potential calculations and updates

**Methods:**
- `recalculate_all_potentials(custom_factors, create_backup)` - Recalculate all
- `estimate_zero_municipalities(method)` - Estimate zero-value municipalities
- `update_conversion_factors(new_factors)` - Update factors in database
- `get_current_factors()` - Get current conversion factors

**Estimation Methods:**
- `'regional_average'` - Use state-wide average
- `'population_based'` - Estimate based on population
- `'area_based'` - Estimate based on municipality area

**Example:**
```python
recalculator = get_biogas_recalculator()

# Recalculate with custom factors
new_factors = {'cattle': 230.0, 'swine': 215.0}
results = recalculator.recalculate_all_potentials(new_factors, create_backup=True)

# Estimate zero municipalities
estimates = recalculator.estimate_zero_municipalities('population_based')
```

### 4. **DataMigrator** (`data_migrator.py`)
**Responsibility:** Database optimization, fixes, and migrations

**Methods:**
- `perform_database_fixes()` - Run all fixes and optimizations
- `fix_data_types(conn)` - Fix data type inconsistencies
- `remove_duplicates(conn)` - Remove duplicate records
- `fix_null_values(conn)` - Fix null values with defaults
- `optimize_database(conn)` - Vacuum and analyze database
- `create_performance_indexes(conn)` - Create query indexes
- `create_backup(backup_name)` - Create full database backup
- `restore_from_backup(backup_path)` - Restore from backup
- `compact_database()` - Compact and reclaim space
- `verify_database_integrity()` - Run SQLite integrity check

**Example:**
```python
migrator = get_data_migrator()

# Perform all fixes
results = migrator.perform_database_fixes()
print(f"Applied {len(results['fixes_applied'])} fixes")

# Create backup
backup = migrator.create_backup()
print(f"Backup created: {backup['backup_path']}")

# Compact database
compact_results = migrator.compact_database()
print(f"Saved {compact_results['space_saved_mb']} MB")
```

## 🔄 Migration Path

### For Existing Code Using DataProcessor

**Option 1: Use New Focused Classes** (Recommended)
```python
# Old code
from src.data.processors import DataProcessor
processor = DataProcessor()
processor.validate_database()

# New code
from src.data.processors import get_database_validator
validator = get_database_validator()
validator.validate_database()
```

**Option 2: Keep Using Legacy DataProcessor** (Temporary)
```python
# Legacy support maintained for backward compatibility
from src.data.processors import DataProcessor
processor = DataProcessor()  # Still works, imports from data_processor_legacy.py
```

## 📊 Benefits Achieved

### ✅ Single Responsibility Principle
Each class has one clear purpose:
- DatabaseValidator → Validation
- CoordinateUpdater → Coordinates
- BiogasRecalculator → Calculations
- DataMigrator → Optimization & Fixes

### ✅ Improved Testability
```python
# Easy to mock and test
def test_coordinate_validation():
    updater = CoordinateUpdater(db_path=":memory:")
    assert updater._validate_coordinate(-23.5, -46.6) == True
    assert updater._validate_coordinate(0, 0) == False  # Outside São Paulo
```

### ✅ Better Maintainability
- **DatabaseValidator**: 400 lines (was part of 741)
- **CoordinateUpdater**: 350 lines (was part of 741)
- **BiogasRecalculator**: 500 lines (was part of 741)
- **DataMigrator**: 480 lines (was part of 741)

Each file is focused and easier to understand.

### ✅ Dependency Injection Ready
```python
# Easy to inject custom database paths or mock connections
validator = DatabaseValidator(db_path=custom_path)
updater = CoordinateUpdater(db_path=test_db_path)
```

## 🚀 Usage Examples

### Complete Workflow Example
```python
from src.data.processors import (
    get_database_validator,
    get_coordinate_updater,
    get_biogas_recalculator,
    get_data_migrator
)

# Step 1: Validate database
print("Step 1: Validating database...")
validator = get_database_validator()
validation = validator.validate_database("census_2024.csv")
print(f"Quality Score: {validation['quality_check']['quality_score']}")

# Step 2: Update coordinates
print("\nStep 2: Updating coordinates...")
updater = get_coordinate_updater()
coord_results = updater.update_from_shapefile()
print(f"Updated {coord_results['coordinates_updated']} coordinates")

# Step 3: Recalculate biogas potentials
print("\nStep 3: Recalculating biogas potentials...")
recalculator = get_biogas_recalculator()
calc_results = recalculator.recalculate_all_potentials(create_backup=True)
print(f"Total potential: {calc_results['total_potential_after']:,.0f} m³/year")

# Step 4: Optimize database
print("\nStep 4: Optimizing database...")
migrator = get_data_migrator()
fix_results = migrator.perform_database_fixes()
print(f"Applied {len(fix_results['fixes_applied'])} fixes")
print(f"Applied {len(fix_results['optimizations'])} optimizations")
```

## 📝 Notes

- **Backward Compatibility**: Old `DataProcessor` is still available as `data_processor_legacy.py`
- **Factory Functions**: Use `get_*` factory functions for cached instances (if using Streamlit caching)
- **Error Handling**: All methods include comprehensive error handling and logging
- **Database Path**: All classes accept optional `db_path` parameter; uses settings default if not provided

## 🎓 Best Practices

1. **Use Factory Functions**: Prefer `get_database_validator()` over `DatabaseValidator()`
2. **Explicit is Better**: Use focused classes instead of legacy monolithic class
3. **Create Backups**: Always create backups before major operations
4. **Check Results**: All methods return detailed result dictionaries
5. **Log Everything**: All operations are logged via `get_logger()`

## ⚠️ Deprecation Notice

The monolithic `DataProcessor` class (`data_processor_legacy.py`) is **deprecated** and maintained only for backward compatibility. Please migrate to the new focused classes.

**Deprecation Timeline:**
- **Current**: Legacy class available, working normally
- **Next Release**: Legacy class marked with deprecation warnings
- **Future Release**: Legacy class will be removed

---

**Refactored on:** 2025-10-02  
**Refactoring Task:** 1.3 - Split DataProcessor Class  
**Lines Reduced:** From 741 lines to 4 focused classes (~400 lines average each)

