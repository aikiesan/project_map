"""
CP2B Maps V2 - Regional Classification Enhancement Script
Adds IBGE regional classification columns to the municipalities table
"""

import sqlite3
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_regional_columns():
    """Add regional classification columns to municipalities table"""

    # Database path
    db_path = Path("A:/CP2B_Maps_V2/data/database/cp2b_maps.db")

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Add regional classification columns
            logger.info("Adding regional classification columns...")

            columns_to_add = [
                "cd_rgi TEXT",  # Immediate region code
                "nm_rgi TEXT",  # Immediate region name
                "cd_rgint TEXT",  # Intermediate region code
                "nm_rgint TEXT"   # Intermediate region name
            ]

            for column in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE municipalities ADD COLUMN {column}")
                    logger.info(f"Added column: {column}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        logger.info(f"Column {column} already exists")
                    else:
                        raise e

            conn.commit()
            logger.info("Regional columns added successfully!")
            return True

    except Exception as e:
        logger.error(f"Failed to add regional columns: {e}")
        return False

def populate_regional_data():
    """Populate regional data using municipality shapefiles"""

    # Paths
    municipalities_shp = Path("A:/CP2B_Maps_V2/data/shapefile/SP_Municipios_2024.shp")
    db_path = Path("A:/CP2B_Maps_V2/data/database/cp2b_maps.db")

    if not municipalities_shp.exists():
        logger.error(f"Municipality shapefile not found: {municipalities_shp}")
        return False

    try:
        # Load municipality shapefile with regional data
        logger.info("Loading municipality shapefile...")
        gdf = gpd.read_file(municipalities_shp)

        # Check required columns
        required_cols = ['CD_MUN', 'CD_RGI', 'NM_RGI', 'CD_RGINT', 'NM_RGINT']
        missing_cols = [col for col in required_cols if col not in gdf.columns]

        if missing_cols:
            logger.error(f"Missing required columns in shapefile: {missing_cols}")
            logger.info(f"Available columns: {list(gdf.columns)}")
            return False

        # Prepare regional data
        regional_data = gdf[required_cols].copy()
        regional_data.columns = ['cd_mun', 'cd_rgi', 'nm_rgi', 'cd_rgint', 'nm_rgint']

        logger.info(f"Loaded regional data for {len(regional_data)} municipalities")

        # Update database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Update each municipality with regional data
            updated_count = 0
            for _, row in regional_data.iterrows():
                cursor.execute("""
                    UPDATE municipalities
                    SET cd_rgi = ?, nm_rgi = ?, cd_rgint = ?, nm_rgint = ?
                    WHERE cd_mun = ?
                """, (row['cd_rgi'], row['nm_rgi'], row['cd_rgint'], row['nm_rgint'], row['cd_mun']))

                if cursor.rowcount > 0:
                    updated_count += 1

            conn.commit()
            logger.info(f"Updated regional data for {updated_count} municipalities")

            # Verify updates
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(cd_rgi) as with_regions
                FROM municipalities
            """)

            result = cursor.fetchone()
            logger.info(f"Total municipalities: {result[0]}, With regional data: {result[1]}")

            return True

    except Exception as e:
        logger.error(f"Failed to populate regional data: {e}")
        return False

def create_regional_summary():
    """Create summary of regional classification"""

    db_path = Path("A:/CP2B_Maps_V2/data/database/cp2b_maps.db")

    try:
        with sqlite3.connect(db_path) as conn:
            # Regional summary
            logger.info("\n=== REGIONAL CLASSIFICATION SUMMARY ===")

            # Intermediate regions summary
            df_intermediate = pd.read_sql_query("""
                SELECT cd_rgint, nm_rgint, COUNT(*) as municipalities,
                       ROUND(SUM(total_final_m_ano)/1e6, 1) as total_biogas_millions_m3
                FROM municipalities
                WHERE cd_rgint IS NOT NULL
                GROUP BY cd_rgint, nm_rgint
                ORDER BY total_biogas_millions_m3 DESC
            """, conn)

            print("\n📊 INTERMEDIATE REGIONS SUMMARY:")
            print(df_intermediate.to_string(index=False))

            # Immediate regions summary (top 10)
            df_immediate = pd.read_sql_query("""
                SELECT cd_rgi, nm_rgi, nm_rgint, COUNT(*) as municipalities,
                       ROUND(SUM(total_final_m_ano)/1e6, 1) as total_biogas_millions_m3
                FROM municipalities
                WHERE cd_rgi IS NOT NULL
                GROUP BY cd_rgi, nm_rgi, nm_rgint
                ORDER BY total_biogas_millions_m3 DESC
                LIMIT 10
            """, conn)

            print("\n📍 TOP 10 IMMEDIATE REGIONS BY BIOGAS POTENTIAL:")
            print(df_immediate.to_string(index=False))

            return True

    except Exception as e:
        logger.error(f"Failed to create regional summary: {e}")
        return False

def main():
    """Main function to run regional classification enhancement"""

    logger.info("🚀 Starting Regional Classification Enhancement...")

    # Step 1: Add columns
    if not add_regional_columns():
        logger.error("❌ Failed to add regional columns")
        return

    # Step 2: Populate data
    if not populate_regional_data():
        logger.error("❌ Failed to populate regional data")
        return

    # Step 3: Create summary
    if not create_regional_summary():
        logger.error("❌ Failed to create regional summary")
        return

    logger.info("✅ Regional classification enhancement completed successfully!")
    print("\n🎯 Next Steps:")
    print("1. Regional boundaries are now available in the map")
    print("2. Regional analysis can be performed in the data explorer")
    print("3. Database contains complete IBGE regional classification")

if __name__ == "__main__":
    main()