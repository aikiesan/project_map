"""
Biogas Potential Database Queries
Answers immediate data needs for São Paulo State
"""

import sqlite3
import pandas as pd
from pathlib import Path

# Database path
db_path = Path("/home/user/project_map/data/database/cp2b_maps.db")

def get_connection():
    """Get database connection"""
    return sqlite3.connect(db_path)

def query_1_state_totals():
    """Query 1: Total State Biogas Potential"""
    print("\n" + "="*80)
    print("QUERY 1: TOTAL STATE BIOGAS POTENTIAL - SÃO PAULO")
    print("="*80)

    with get_connection() as conn:
        # First, check what columns exist
        schema_query = "PRAGMA table_info(municipalities)"
        schema = pd.read_sql_query(schema_query, conn)
        print("\n📊 Available columns:")
        print(schema[['name', 'type']].to_string(index=False))

        # Get theoretical potential (this would be at 100% scenario factor)
        query = """
        SELECT
            COUNT(*) as total_municipalities,
            SUM(total_final_m_ano) as theoretical_biogas_m3_year,
            SUM(total_final_m_ano) / 365.0 as theoretical_biogas_m3_day,
            SUM(total_urbano_m_ano) as urban_theoretical_m3_year,
            SUM(total_agricola_m_ano) as agricultural_theoretical_m3_year,
            SUM(total_pecuaria_m_ano) as livestock_theoretical_m3_year
        FROM municipalities
        WHERE total_final_m_ano IS NOT NULL
        """

        df = pd.read_sql_query(query, conn)

        print("\n📈 STATE TOTALS:")
        print(f"Total Municipalities: {df['total_municipalities'].iloc[0]}")
        print(f"\n🔬 THEORETICAL BIOGAS POTENTIAL (100% scenario):")
        print(f"  - Total: {df['theoretical_biogas_m3_year'].iloc[0]:,.2f} m³/year")
        print(f"  - Total: {df['theoretical_biogas_m3_day'].iloc[0]:,.2f} m³/day")
        print(f"\n📊 By Sector (Theoretical):")
        print(f"  - Urban: {df['urban_theoretical_m3_year'].iloc[0]:,.2f} m³/year")
        print(f"  - Agricultural: {df['agricultural_theoretical_m3_year'].iloc[0]:,.2f} m³/year")
        print(f"  - Livestock: {df['livestock_theoretical_m3_year'].iloc[0]:,.2f} m³/year")

        # Common scenario factors in biogas projects
        scenarios = {
            'Conservative (30%)': 0.30,
            'Moderate (50%)': 0.50,
            'Realistic (70%)': 0.70,
            'Optimistic (90%)': 0.90
        }

        print(f"\n💡 AVAILABLE BIOGAS POTENTIAL (After Correction Factors):")
        theoretical_daily = df['theoretical_biogas_m3_day'].iloc[0]

        for scenario_name, factor in scenarios.items():
            available = theoretical_daily * factor
            reduction = (1 - factor) * 100
            print(f"\n  {scenario_name}:")
            print(f"    - Available: {available:,.2f} m³/day")
            print(f"    - Reduction from theoretical: {reduction:.1f}%")

def query_2_top_municipalities():
    """Query 2: Top 10 Municipalities Ranking"""
    print("\n\n" + "="*80)
    print("QUERY 2: TOP 10 MUNICIPALITIES BY AVAILABLE BIOGAS POTENTIAL")
    print("="*80)

    with get_connection() as conn:
        query = """
        SELECT
            nome_municipio as municipality,
            (total_final_m_ano / 365.0) as biogas_m3_day,
            total_urbano_m_ano / 365.0 as urban_m3_day,
            total_agricola_m_ano / 365.0 as agricultural_m3_day,
            total_pecuaria_m_ano / 365.0 as livestock_m3_day,
            populacao_2022 as population,
            CASE
                WHEN total_final_m_ano > 0 THEN (total_urbano_m_ano / total_final_m_ano * 100)
                ELSE 0
            END as urban_pct,
            CASE
                WHEN total_final_m_ano > 0 THEN (total_agricola_m_ano / total_final_m_ano * 100)
                ELSE 0
            END as agricultural_pct,
            CASE
                WHEN total_final_m_ano > 0 THEN (total_pecuaria_m_ano / total_final_m_ano * 100)
                ELSE 0
            END as livestock_pct
        FROM municipalities
        WHERE total_final_m_ano IS NOT NULL
        ORDER BY total_final_m_ano DESC
        LIMIT 10
        """

        df = pd.read_sql_query(query, conn)

        print("\n🏆 TOP 10 MUNICIPALITIES (Theoretical Potential):")
        print("\nNote: Apply scenario factors (30-90%) to get available potential")
        print("-" * 80)

        for idx, row in df.iterrows():
            print(f"\n{idx + 1}. {row['municipality']}")
            print(f"   Total Biogas: {row['biogas_m3_day']:,.2f} m³/day")
            print(f"   Population: {row['population']:,.0f}")
            print(f"   Primary Substrate Contributions:")
            print(f"     - Urban: {row['urban_pct']:.1f}%")
            print(f"     - Agricultural: {row['agricultural_pct']:.1f}%")
            print(f"     - Livestock: {row['livestock_pct']:.1f}%")

def query_3_substrate_breakdown():
    """Query 3: Substrate Contribution Breakdown"""
    print("\n\n" + "="*80)
    print("QUERY 3: SUBSTRATE CONTRIBUTION BREAKDOWN - SÃO PAULO STATE")
    print("="*80)

    with get_connection() as conn:
        query = """
        SELECT
            -- Main categories
            SUM(total_urbano_m_ano) / 365.0 as urban_m3_day,
            SUM(total_agricola_m_ano) / 365.0 as agricultural_m3_day,
            SUM(total_pecuaria_m_ano) / 365.0 as livestock_m3_day,
            SUM(total_final_m_ano) / 365.0 as total_m3_day,

            -- Agricultural breakdown
            SUM(biogas_cana_m_ano) / 365.0 as sugarcane_m3_day,
            SUM(biogas_soja_m_ano) / 365.0 as soybean_m3_day,
            SUM(biogas_milho_m_ano) / 365.0 as corn_m3_day,
            SUM(biogas_cafe_m_ano) / 365.0 as coffee_m3_day,
            SUM(biogas_citros_m_ano) / 365.0 as citrus_m3_day,

            -- Livestock breakdown
            SUM(biogas_bovinos_m_ano) / 365.0 as cattle_m3_day,
            SUM(biogas_suino_m_ano) / 365.0 as swine_m3_day,
            SUM(biogas_aves_m_ano) / 365.0 as poultry_m3_day,
            SUM(biogas_piscicultura_m_ano) / 365.0 as fish_m3_day,

            -- Urban waste breakdown
            SUM(rsu_potencial_m_ano) / 365.0 as municipal_solid_waste_m3_day,
            SUM(rpo_potencial_m_ano) / 365.0 as rural_organic_waste_m3_day
        FROM municipalities
        WHERE total_final_m_ano IS NOT NULL
        """

        df = pd.read_sql_query(query, conn)
        row = df.iloc[0]

        total = row['total_m3_day']

        print(f"\n🌍 STATE-WIDE SUBSTRATE BREAKDOWN (Theoretical Daily Production):")
        print(f"\nTotal Biogas Potential: {total:,.2f} m³/day")
        print("\n" + "-" * 80)

        # Main categories
        print("\n📊 PRIMARY CATEGORIES:")
        categories = [
            ('Urban/Municipal', row['urban_m3_day']),
            ('Agricultural Residues', row['agricultural_m3_day']),
            ('Livestock Manure', row['livestock_m3_day'])
        ]

        for name, value in categories:
            pct = (value / total * 100) if total > 0 else 0
            print(f"\n  {name}:")
            print(f"    - Volume: {value:,.2f} m³/day ({pct:.1f}%)")

        # Agricultural breakdown
        print("\n\n🌾 AGRICULTURAL RESIDUES BREAKDOWN:")
        agri_total = row['agricultural_m3_day']
        agri_sources = [
            ('Sugarcane', row['sugarcane_m3_day']),
            ('Soybean', row['soybean_m3_day']),
            ('Corn', row['corn_m3_day']),
            ('Coffee', row['coffee_m3_day']),
            ('Citrus', row['citrus_m3_day'])
        ]

        for name, value in agri_sources:
            pct_total = (value / total * 100) if total > 0 else 0
            pct_agri = (value / agri_total * 100) if agri_total > 0 else 0
            print(f"  - {name}: {value:,.2f} m³/day ({pct_agri:.1f}% of agricultural, {pct_total:.1f}% of total)")

        # Livestock breakdown
        print("\n\n🐄 LIVESTOCK MANURE BREAKDOWN:")
        livestock_total = row['livestock_m3_day']
        livestock_sources = [
            ('Cattle', row['cattle_m3_day']),
            ('Swine', row['swine_m3_day']),
            ('Poultry', row['poultry_m3_day']),
            ('Fish Farming', row['fish_m3_day'])
        ]

        for name, value in livestock_sources:
            pct_total = (value / total * 100) if total > 0 else 0
            pct_livestock = (value / livestock_total * 100) if livestock_total > 0 else 0
            print(f"  - {name}: {value:,.2f} m³/day ({pct_livestock:.1f}% of livestock, {pct_total:.1f}% of total)")

        # Urban breakdown
        print("\n\n🏙️ URBAN WASTE BREAKDOWN:")
        print(f"  - Municipal Solid Waste: {row['municipal_solid_waste_m3_day']:,.2f} m³/day")
        print(f"  - Rural Organic Waste: {row['rural_organic_waste_m3_day']:,.2f} m³/day")

def main():
    """Run all queries"""
    print("\n🔬 BIOGAS POTENTIAL DATABASE QUERIES")
    print("📍 São Paulo State, Brazil")
    print("⚡ Immediate Data Needs Analysis")

    try:
        query_1_state_totals()
        query_2_top_municipalities()
        query_3_substrate_breakdown()

        print("\n\n" + "="*80)
        print("✅ ALL QUERIES COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n📝 Note: Theoretical values represent 100% utilization scenario.")
        print("Apply correction factors (30-90%) based on project feasibility for available potential.")

    except Exception as e:
        print(f"\n❌ Error executing queries: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
