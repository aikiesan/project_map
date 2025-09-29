"""
CP2B Maps V2 - Home Page Component
Professional home page with real data showcase and advanced functionality
"""

import streamlit as st
import folium
import folium.plugins
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
        Render Map-First home page with native Streamlit components
        """
        try:
            # Map-First approach: Hero map section at the top
            self._render_hero_map_section()

            # Live dashboard strip below map
            self._render_live_dashboard_strip()

            # Collapsible sections for additional info
            self._render_expandable_sections()

        except Exception as e:
            self.logger.error(f"Error rendering home page: {e}", exc_info=True)
            st.error("⚠️ Failed to render home page. Check logs for details.")

    def _render_hero_map_section(self) -> None:
        """Render Map-First hero section with sidebar controls"""
        # Simple header using native Streamlit
        st.title("🗺️ CP2B Maps V2 - Professional Biogas GIS Platform")

        # Load municipality data for statistics
        municipalities_df = database_loader.load_municipalities_data()

        # Organized sidebar sections
        with st.sidebar:
            st.markdown("### 🎛️ Map Controls")
            show_boundary = st.checkbox("🗺️ State Boundary", value=True)
            show_plants = st.checkbox("🏭 Biogas Plants", value=True)
            show_municipalities = st.checkbox("🏘️ Municipality Labels", value=False)
            map_style = st.selectbox("Map Style:", options=['CartoDB positron', 'CartoDB dark_matter', 'OpenStreetMap'])

            st.markdown("---")
            st.markdown("### 📊 Live Metrics")
            if municipalities_df is not None:
                stats = biogas_calculator.get_state_totals(municipalities_df)
                st.metric("Municipalities", f"{stats.get('total_municipalities', 0):,}")
                st.metric("Daily Biogas", f"{stats.get('total_biogas_m3_day', 0):,.0f} m³")
                st.metric("Annual Energy", f"{stats.get('total_energy_mwh_year', 0):,.0f} MWh")
                st.metric("CO₂ Reduction", f"{stats.get('total_co2_reduction_tons_year', 0):,.0f} tons/year")

            st.markdown("---")
            st.markdown("### 🖥️ System Status")
            db_status = "✅ Online" if database_loader.validate_database() else "❌ Error"
            shapefiles = shapefile_loader.get_available_shapefiles()
            gis_status = f"✅ {len(shapefiles)} Layers" if shapefiles else "❌ Error"
            st.success(f"🗄️ Database: {db_status}")
            st.success(f"🗺️ GIS: {gis_status}")
            st.success("⚙️ Calculator: ✅ Ready")

        # Horizontal navigation overlay (minimalistic buttons over map)
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        with nav_col1:
            if st.button("🗺️ Advanced Maps", key="nav_maps", use_container_width=True):
                st.info("👆 Use sidebar navigation to access Advanced Maps")
        with nav_col2:
            if st.button("📊 Data Analysis", key="nav_analysis", use_container_width=True):
                st.info("👆 Use sidebar navigation to access Data Analysis")
        with nav_col3:
            if st.button("🔄 Municipality Compare", key="nav_compare", use_container_width=True):
                st.info("👆 Use sidebar navigation to access Comparison tools")
        with nav_col4:
            if st.button("📥 Export & Reports", key="nav_export", use_container_width=True):
                st.info("👆 Use sidebar navigation to access Export tools")

        # Full-width hero map
        self._render_hero_map(show_boundary, show_plants, map_style)

    def _render_hero_map(self, show_boundary: bool, show_plants: bool, map_style: str) -> None:
        """Render the main hero map with professional styling"""
        # Create large, prominent map
        m = folium.Map(
            location=settings.DEFAULT_CENTER,
            zoom_start=7,
            tiles=map_style
        )

        # Add fullscreen and measure tools
        folium.plugins.Fullscreen().add_to(m)
        folium.plugins.MeasureControl().add_to(m)

        # Add state boundary if enabled
        if show_boundary:
            state_boundary = shapefile_loader.load_state_boundary()
            if state_boundary is not None:
                folium.GeoJson(
                    state_boundary,
                    style_function=lambda feature: {
                        'color': '#2E8B57',
                        'weight': 3,
                        'opacity': 0.8,
                        'fillOpacity': 0.1,
                        'dashArray': '5, 5'
                    },
                    popup="São Paulo State - 645 Municipalities",
                    tooltip="Click for state information"
                ).add_to(m)

        # Add biogas plants if enabled
        if show_plants:
            biogas_plants = shapefile_loader.load_biogas_plants()
            if biogas_plants is not None and len(biogas_plants) > 0:
                # Display first 100 plants for performance
                display_plants = biogas_plants.head(100)

                for _, plant in display_plants.iterrows():
                    plant_type = plant.get('TIPO_PLANT', 'Unknown')
                    folium.CircleMarker(
                        location=[plant.geometry.y, plant.geometry.x],
                        radius=6,
                        popup=f"🏭 Biogas Plant<br><b>Type:</b> {plant_type}<br><b>Status:</b> Active",
                        tooltip=f"🏭 {plant_type}",
                        color='#FF6B35',
                        fillColor='#FF6B35',
                        fillOpacity=0.8,
                        weight=2
                    ).add_to(m)

        # Display the hero map with increased height
        map_data = st_folium(
            m,
            width="100%",
            height=800,  # Large hero map
            returned_objects=["last_object_clicked", "bounds"],
            key="hero_map"
        )

        # Show interaction feedback
        if map_data.get("last_object_clicked"):
            st.success("🎯 Feature selected! Check the details in the sidebar.")

    def _render_live_dashboard_strip(self) -> None:
        """Render horizontal dashboard strip with key metrics"""
        st.markdown("---")
        st.markdown("### 📊 Real-Time Analytics Dashboard")

        # Load municipality data
        municipalities_df = database_loader.load_municipalities_data()

        if municipalities_df is not None and len(municipalities_df) > 0:
            # Calculate state totals
            stats = biogas_calculator.get_state_totals(municipalities_df)

            # Display metrics in horizontal layout
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    label="🏘️ Municipalities",
                    value=f"{stats.get('total_municipalities', 0):,}",
                    delta="Complete Coverage"
                )

            with col2:
                st.metric(
                    label="⛽ Daily Biogas",
                    value=f"{stats.get('total_biogas_m3_day', 0):,.0f} m³",
                    delta="Real-time Potential"
                )

            with col3:
                st.metric(
                    label="⚡ Annual Energy",
                    value=f"{stats.get('total_energy_mwh_year', 0):,.0f} MWh",
                    delta="Clean Energy"
                )

            with col4:
                st.metric(
                    label="🌱 CO₂ Reduction",
                    value=f"{stats.get('total_co2_reduction_tons_year', 0):,.0f} tons",
                    delta="Per Year"
                )

            with col5:
                # System health indicator
                db_status = "✅ Online" if database_loader.validate_database() else "❌ Error"
                st.metric(
                    label="🖥️ System Status",
                    value=db_status,
                    delta="All Systems Operational"
                )

        else:
            st.warning("⚠️ Unable to load municipality data. Please check the database connection.")

    def _render_expandable_sections(self) -> None:
        """Render collapsible section for top municipalities"""
        with st.expander("🏆 Top Performing Municipalities", expanded=False):
            self._render_top_municipalities_clean()

    def _render_top_municipalities_clean(self) -> None:
        """Clean version of top municipalities without complex styling"""
        top_municipalities = database_loader.get_top_municipalities(
            by_column="total_final_m_ano",
            limit=10
        )

        if top_municipalities is not None:
            st.markdown("**Top 10 Municipalities by Biogas Potential:**")

            for idx, (_, municipality) in enumerate(top_municipalities.iterrows(), 1):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

                with col1:
                    if idx <= 3:
                        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                        st.markdown(medals.get(idx, f"#{idx}"))
                    else:
                        st.markdown(f"#{idx}")

                with col2:
                    st.markdown(f"**{municipality['municipality']}**")

                with col3:
                    st.markdown(f"{municipality['biogas_potential_m3_day']:,.0f} m³/day")

                with col4:
                    st.markdown(f"{municipality['population']:,.0f} people")







