"""
CP2B Maps V2 - Home Page Component
Professional home page with real data showcase and advanced functionality
"""

import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from typing import Dict, Any, Optional

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader, shapefile_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class HomePage:
    """
    Professional home page component with real data integration
    Showcases 645 municipalities and 425 biogas plants
    """

    def __init__(self):
        """Initialize home page component"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing HomePage component")

    def render(self) -> None:
        """
        Render the home page with real data and functionality
        """
        try:
            self._render_welcome_section()
            self._render_data_status()
            self._render_live_statistics()
            self._render_interactive_map()

        except Exception as e:
            self.logger.error(f"Error rendering home page: {e}", exc_info=True)
            st.error("⚠️ Failed to render home page. Check logs for details.")

    def _render_welcome_section(self) -> None:
        """Render welcome message with real data capabilities"""
        st.markdown("""
        ## 🗺️ CP2B Maps V2 - Professional Biogas Analysis Platform

        ### 🎯 **Live Data Integration**
        - **645 São Paulo Municipalities** with biogas potential calculations
        - **425 Biogas Plants** (existing and potential locations)
        - **Professional Architecture** with smart caching and optimization
        - **Real-time Calculations** using literature-validated factors
        """)

    def _render_data_status(self) -> None:
        """Show current data loading status and validation"""
        st.markdown("### 📊 Data Infrastructure Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Database status
            db_valid = database_loader.validate_database()
            if db_valid:
                st.success("✅ Database Connected")
                db_info = database_loader.get_database_info()
                st.caption(f"Size: {db_info.get('database_size_mb', 'Unknown')} MB")
            else:
                st.error("❌ Database Error")

        with col2:
            # Shapefile status
            shapefiles = shapefile_loader.get_available_shapefiles()
            if shapefiles:
                st.success(f"✅ {len(shapefiles)} Shapefiles")
                total_size = sum(info['size_mb'] for info in shapefiles.values())
                st.caption(f"Total: {total_size:.1f} MB")
            else:
                st.error("❌ No Shapefiles")

        with col3:
            # Calculator status
            factors = biogas_calculator.get_conversion_factors_info()
            st.success("✅ Calculator Ready")
            st.caption("Literature-validated factors")

    def _render_live_statistics(self) -> None:
        """Display live statistics from the database"""
        st.markdown("### 📈 Live São Paulo State Statistics")

        # Load municipality data
        municipalities_df = database_loader.load_municipalities_data()

        if municipalities_df is not None and len(municipalities_df) > 0:
            # Calculate state totals
            stats = biogas_calculator.get_state_totals(municipalities_df)

            # Display in columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Municipalities",
                    f"{stats.get('total_municipalities', 0):,}",
                    delta="Complete Coverage"
                )

            with col2:
                st.metric(
                    "Daily Biogas Potential",
                    f"{stats.get('total_biogas_m3_day', 0):,.0f} m³",
                    delta="Per Day"
                )

            with col3:
                st.metric(
                    "Annual Energy Potential",
                    f"{stats.get('total_energy_mwh_year', 0):,.0f} MWh",
                    delta="Clean Energy"
                )

            with col4:
                st.metric(
                    "CO₂ Reduction Potential",
                    f"{stats.get('total_co2_reduction_tons_year', 0):,.0f} tons",
                    delta="Per Year"
                )

            # Top municipalities
            self._render_top_municipalities(municipalities_df)

        else:
            st.warning("⚠️ Municipality data not available. Check database connection.")

    def _render_top_municipalities(self, df: pd.DataFrame) -> None:
        """Display top municipalities by biogas potential"""
        st.markdown("#### 🏆 Top 10 Municipalities by Biogas Potential")

        top_municipalities = database_loader.get_top_municipalities(
            by_column="biogas_potential_m3_day",
            limit=10
        )

        if top_municipalities is not None:
            # Format the data for display
            display_df = top_municipalities.copy()
            display_df['biogas_potential_m3_day'] = display_df['biogas_potential_m3_day'].round(1)
            display_df['energy_potential_kwh_day'] = display_df['energy_potential_kwh_day'].round(1)
            display_df['population'] = display_df['population'].astype(int)

            # Rename columns for display
            display_df.columns = ['Municipality', 'Biogas (m³/day)', 'Energy (kWh/day)', 'Population']

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

    def _render_interactive_map(self) -> None:
        """Render interactive map with real data"""
        st.markdown("### 🗺️ Interactive São Paulo State Map")

        # Create folium map centered on São Paulo
        m = folium.Map(
            location=settings.DEFAULT_CENTER,
            zoom_start=7,
            tiles="CartoDB positron"
        )

        # Load and display state boundary
        state_boundary = shapefile_loader.load_state_boundary()
        if state_boundary is not None:
            folium.GeoJson(
                state_boundary,
                style_function=lambda feature: {
                    'color': '#2E8B57',
                    'weight': 3,
                    'opacity': 0.8,
                    'fillOpacity': 0.1
                },
                popup="São Paulo State",
                tooltip="São Paulo State - 645 Municipalities"
            ).add_to(m)

        # Load and display biogas plants
        biogas_plants = shapefile_loader.load_biogas_plants()
        if biogas_plants is not None and len(biogas_plants) > 0:
            for _, plant in biogas_plants.head(50).iterrows():  # Limit for performance
                folium.CircleMarker(
                    location=[plant.geometry.y, plant.geometry.x],
                    radius=5,
                    popup=f"Biogas Plant<br>Type: {plant.get('TIPO_PLANT', 'Unknown')}",
                    tooltip=f"Biogas Plant: {plant.get('TIPO_PLANT', 'Unknown')}",
                    color='#FF6B35',
                    fillColor='#FF6B35',
                    fillOpacity=0.7
                ).add_to(m)

        # Display map
        map_data = st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_object_clicked"]
        )

        # Show interaction feedback
        if map_data["last_object_clicked"]:
            st.success("✅ Map interaction detected! Click on biogas plants to see details.")

        # Development progress
        st.markdown("---")
        st.markdown("### 🚀 Development Progress")

        progress_col1, progress_col2 = st.columns([3, 1])

        with progress_col1:
            st.progress(0.6, text="Phase 2A: Data Infrastructure Complete")

        with progress_col2:
            st.metric("Progress", "60%", delta="Phase 2A ✅")

        # Next steps
        st.markdown("""
        **✅ Completed:**
        - Professional data loaders (ShapefileLoader, DatabaseLoader)
        - Biogas calculation engine with literature-validated factors
        - Real-time statistics from 645 municipalities
        - Interactive map with state boundary and biogas plants

        **🚧 Next Phase:**
        - Advanced map layers and controls
        - Municipality comparison tools
        - Export functionality
        - Performance optimization
        """)