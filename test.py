import sys

# Ensure the source directory is in the Python path
SRC_PATH = r'A:\CP2B_Maps_V2\src'
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

try:
    from data.loaders.database_loader import DatabaseLoader
except ImportError as e:
    print(f"❌ Failed to import DatabaseLoader: {e}")
    sys.exit(1)

def main():
    # Create database loader
    try:
        db_loader = DatabaseLoader()
    except Exception as e:
        print(f"❌ Error initializing DatabaseLoader: {e}")
        sys.exit(1)

    # Load data and check columns
    try:
        data = db_loader.load_municipalities_data()
    except Exception as e:
        print(f"❌ Error loading municipalities data: {e}")
        sys.exit(1)

    if data is not None:
        print("LOADED COLUMNS:")
        print(data.columns.tolist())
        print(f"\nTotal rows: {len(data)}")

        # Check for specific problematic columns
        expected = ["urban_biogas_m3_year", "urban_waste_potential_m3_year"]
        for col in expected:
            if col in data.columns:
                print(f"✅ {col} - EXISTS")
            else:
                print(f"❌ {col} - MISSING")
    else:
        print("❌ Failed to load data!")

if __name__ == "__main__":
    main()