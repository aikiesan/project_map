"""
CP2B Maps V2 - Proximity Analysis Page
Comprehensive proximity analysis with integrated raster analysis and biogas plant optimization
"""

from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import pandas as pd

# Geospatial imports with error handling
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    folium = None
    st_folium = None

from config.settings import settings
from src.utils.logging_config import get_logger
from src.core.proximity_analyzer import get_proximity_analyzer
from src.ui.components.proximity_controls import create_proximity_controls
from src.ui.components.proximity_results import create_proximity_results
from src.data.loaders.mapbiomas_loader import get_mapbiomas_loader
from src.data.loaders.database_loader import DatabaseLoader

# Import V1 design system
from src.ui.components.design_system import (
    render_page_header,
    render_section_header,
    render_info_banner
)

logger = get_logger(__name__)


class ProximityAnalysisPage:
    """
    Professional proximity analysis page with integrated features
    Features: Interactive map, proximity controls, raster integration, results display
    """

    def __init__(self):
        """Initialize ProximityAnalysisPage"""
        self.logger = get_logger(self.__class__.__name__)
        self.proximity_analyzer = get_proximity_analyzer()
        self.proximity_controls = create_proximity_controls()
        self.proximity_results = create_proximity_results()
        self.mapbiomas_loader = get_mapbiomas_loader()

        if not HAS_FOLIUM:
            self.logger.error("Folium not available - map functionality disabled")

    def render(self) -> None:
        """Render the complete proximity analysis page"""
        try:
            # V1-style beautiful header
            render_page_header(
                title="Análise de Proximidade",
                subtitle="Otimização de Localização de Plantas de Biogás",
                description="Análise avançada de área de captação com integração de dados raster e cálculos espaciais",
                icon="🎯",
                show_stats=True
            )

            # Load municipality data
            municipality_data = self._load_municipality_data()

            if municipality_data is None:
                st.error("⚠️ Could not load municipality data")
                return

            # Create layout
            self._render_page_layout(municipality_data)

        except Exception as e:
            self.logger.error(f"Error rendering proximity analysis page: {e}")
            st.error("⚠️ Error loading proximity analysis page")

    def _load_municipality_data(self) -> Optional[pd.DataFrame]:
        """Load municipality data for analysis"""
        try:
            db_loader = DatabaseLoader()
            data = db_loader.load_municipalities_data()

            if data is not None and not data.empty:
                self.logger.info(f"Loaded {len(data)} municipalities for proximity analysis")
                return data
            else:
                self.logger.warning("No municipality data available")
                return None

        except Exception as e:
            self.logger.error(f"Error loading municipality data: {e}")
            return None

    def _render_page_layout(self, municipality_data: pd.DataFrame) -> None:
        """Render the main page layout"""
        try:
            # Create sidebar for controls
            with st.sidebar:
                # Render proximity controls
                controls = self.proximity_controls.render(municipality_data)

            # Main content area
            if controls.get('enabled'):
                # Create two-column layout
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Interactive map
                    map_data = self._render_interactive_map(municipality_data, controls)

                with col2:
                    # Analysis status and quick info
                    self._render_analysis_status(controls)

                # Check if analysis should be triggered
                analysis_results = self._check_and_run_analysis(municipality_data, controls, map_data)

                # Display results if available
                if analysis_results:
                    st.markdown("---")
                    self.proximity_results.render(analysis_results)

            else:
                # Analysis disabled - show information
                self._render_disabled_state()

        except Exception as e:
            self.logger.error(f"Error rendering page layout: {e}")
            st.error("⚠️ Error rendering page layout")

    def _render_interactive_map(self, municipality_data: pd.DataFrame, controls: Dict[str, Any]) -> Dict[str, Any]:
        """Render interactive map with proximity analysis features"""
        if not HAS_FOLIUM:
            st.error("⚠️ Map functionality requires folium library")
            return {}

        try:
            st.markdown("### 🗺️ Interactive Analysis Map")

            # Get current analysis configuration
            config = self.proximity_controls.get_analysis_config()

            # Create base map
            center_lat, center_lon = settings.DEFAULT_CENTER

            # Use analysis center if available
            if config.get('latitude') and config.get('longitude'):
                center_lat = config['latitude']
                center_lon = config['longitude']

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=settings.DEFAULT_ZOOM,
                tiles='OpenStreetMap'
            )

            # Add municipality markers
            self._add_municipality_markers(m, municipality_data)

            # Add analysis center and radius if coordinates are set
            if config.get('latitude') and config.get('longitude'):
                self._add_analysis_circle(m, config)

            # Add any existing analysis results
            if 'proximity_results' in st.session_state:
                self._add_results_to_map(m, st.session_state['proximity_results'])

            # Render map with click detection
            map_data = st_folium(
                m,
                key="proximity_map",
                width=None,
                height=500,
                returned_objects=["last_clicked", "last_object_clicked"]
            )

            # Handle map clicks
            self._handle_map_click(map_data)

            return map_data

        except Exception as e:
            self.logger.error(f"Error rendering interactive map: {e}")
            st.error("⚠️ Error rendering map")
            return {}

    def _add_municipality_markers(self, map_obj, municipality_data: pd.DataFrame) -> None:
        """Add municipality markers to map"""
        try:
            if 'lat' not in municipality_data.columns or 'lon' not in municipality_data.columns:
                return

            # Create municipality group
            municipality_group = folium.FeatureGroup(name="Municipalities", show=True)

            # Sample municipalities for performance (show up to 100)
            sample_data = municipality_data.sample(n=min(100, len(municipality_data)))

            for idx, row in sample_data.iterrows():
                if pd.notna(row['lat']) and pd.notna(row['lon']):
                    # Create popup content
                    popup_text = f"<b>{row.get('nome_municipio', 'Unknown')}</b>"

                    if 'potencial_biogas_total' in row and pd.notna(row['potencial_biogas_total']):
                        popup_text += f"<br>Biogas Potential: {row['potencial_biogas_total']:,.0f} m³/ano"

                    if 'populacao_total' in row and pd.notna(row['populacao_total']):
                        popup_text += f"<br>Population: {row['populacao_total']:,.0f}"

                    # Determine marker size based on biogas potential
                    potential = row.get('potencial_biogas_total', 0)
                    if potential > 1000000:  # > 1M m³/year
                        radius = 8
                        color = 'red'
                    elif potential > 500000:  # > 500k m³/year
                        radius = 6
                        color = 'orange'
                    elif potential > 100000:  # > 100k m³/year
                        radius = 4
                        color = 'yellow'
                    else:
                        radius = 3
                        color = 'blue'

                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=radius,
                        popup=popup_text,
                        color=color,
                        fillColor=color,
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(municipality_group)

            municipality_group.add_to(map_obj)

            # Add layer control
            folium.LayerControl().add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding municipality markers: {e}")

    def _add_analysis_circle(self, map_obj, config: Dict[str, Any]) -> None:
        """Add analysis center point and radius circle to map"""
        try:
            lat = config['latitude']
            lon = config['longitude']
            radius_km = config['radius_km']

            # Add center marker
            folium.Marker(
                location=[lat, lon],
                popup=f"Analysis Center<br>{lat:.4f}, {lon:.4f}",
                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa'),
                tooltip="Analysis Center"
            ).add_to(map_obj)

            # Add radius circle
            folium.Circle(
                location=[lat, lon],
                radius=radius_km * 1000,  # Convert km to meters
                color='red',
                fillColor='red',
                fillOpacity=0.1,
                weight=2,
                popup=f"Analysis Radius: {radius_km} km"
            ).add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding analysis circle: {e}")

    def _add_results_to_map(self, map_obj, results: Dict[str, Any]) -> None:
        """Add analysis results visualization to map"""
        try:
            if not results or 'municipality_details' not in results:
                return

            municipality_details = results['municipality_details']

            # Create results group
            results_group = folium.FeatureGroup(name="Analysis Results", show=True)

            for municipality in municipality_details:
                if 'lat' in municipality and 'lon' in municipality:
                    lat = municipality.get('lat')
                    lon = municipality.get('lon')

                    if lat and lon:
                        # Create detailed popup
                        popup_text = f"<b>{municipality.get('nome_municipio', 'Unknown')}</b><br>"
                        popup_text += f"Distance: {municipality.get('distance_km', 0):.2f} km<br>"

                        for key, value in municipality.items():
                            if 'biogas' in key.lower() and isinstance(value, (int, float)):
                                popup_text += f"{key.replace('_', ' ').title()}: {value:,.0f}<br>"

                        # Color based on distance
                        distance = municipality.get('distance_km', 0)
                        if distance <= 10:
                            color = 'green'
                        elif distance <= 25:
                            color = 'orange'
                        else:
                            color = 'red'

                        folium.CircleMarker(
                            location=[lat, lon],
                            radius=6,
                            popup=popup_text,
                            color=color,
                            fillColor=color,
                            fillOpacity=0.8,
                            weight=2
                        ).add_to(results_group)

            results_group.add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding results to map: {e}")

    def _handle_map_click(self, map_data: Dict[str, Any]) -> None:
        """Handle map click events for analysis center selection"""
        try:
            if map_data and map_data.get('last_clicked'):
                clicked_point = map_data['last_clicked']
                lat = clicked_point['lat']
                lon = clicked_point['lng']

                # Store clicked coordinates in session state
                st.session_state['map_click_lat'] = lat
                st.session_state['map_click_lon'] = lon

                # Clear any existing results when new point is clicked
                if 'proximity_results' in st.session_state:
                    del st.session_state['proximity_results']

                self.logger.info(f"Map clicked at: {lat:.4f}, {lon:.4f}")

        except Exception as e:
            self.logger.error(f"Error handling map click: {e}")

    def _render_analysis_status(self, controls: Dict[str, Any]) -> None:
        """Render analysis status and quick information"""
        try:
            st.markdown("### 📊 Analysis Status")

            # Check if ready for analysis
            is_ready, message = self.proximity_controls.is_ready_for_analysis()

            if is_ready:
                st.success(f"✅ {message}")

                # Show current configuration
                config = self.proximity_controls.get_analysis_config()

                with st.expander("📋 Current Configuration"):
                    st.write(f"**Method:** {config.get('input_method', 'N/A')}")
                    st.write(f"**Radius:** {config.get('radius_km', 'N/A')} km")
                    st.write(f"**Analysis Depth:** {config.get('analysis_depth', 'N/A')}")

                    if config.get('latitude') and config.get('longitude'):
                        st.write(f"**Center:** {config['latitude']:.4f}, {config['longitude']:.4f}")

            else:
                st.warning(f"⚠️ {message}")

                # Provide guidance
                st.markdown("#### 💡 Next Steps:")
                if "coordinates" in message.lower():
                    st.markdown("- Click on the map to set analysis center")
                    st.markdown("- Or use manual coordinate input")
                elif "not enabled" in message.lower():
                    st.markdown("- Enable proximity analysis in the sidebar")

            # Show recent results summary
            if 'proximity_results' in st.session_state:
                results = st.session_state['proximity_results']
                st.markdown("#### 📈 Latest Results")
                st.info(f"Found {results.get('municipalities_found', 0)} municipalities")

        except Exception as e:
            self.logger.error(f"Error rendering analysis status: {e}")

    def _check_and_run_analysis(self,
                               municipality_data: pd.DataFrame,
                               controls: Dict[str, Any],
                               map_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if analysis should be triggered and run it"""
        try:
            # Check for analysis trigger
            triggers = controls.get('triggers', {})

            if not triggers.get('run_analysis'):
                # Return existing results if available
                return st.session_state.get('proximity_results')

            # Check if ready for analysis
            is_ready, message = self.proximity_controls.is_ready_for_analysis()

            if not is_ready:
                st.error(f"❌ Cannot run analysis: {message}")
                return None

            # Get analysis configuration
            config = self.proximity_controls.get_analysis_config()

            # Run analysis with progress indicator
            with st.spinner("🔄 Running proximity analysis..."):
                results = self._perform_comprehensive_analysis(
                    municipality_data, config
                )

            if results and 'error' not in results:
                # Store results in session state
                st.session_state['proximity_results'] = results
                st.success("✅ Analysis completed successfully!")

                # Add raster analysis if enabled
                if config.get('include_raster', False):
                    self._add_raster_analysis(results, config)

                return results
            else:
                error_msg = results.get('error', 'Unknown error') if results else 'Analysis failed'
                st.error(f"❌ Analysis failed: {error_msg}")
                return None

        except Exception as e:
            self.logger.error(f"Error in analysis execution: {e}")
            st.error(f"⚠️ Analysis error: {str(e)}")
            return None

    def _perform_comprehensive_analysis(self,
                                      municipality_data: pd.DataFrame,
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive proximity analysis"""
        try:
            # Extract analysis parameters
            lat = config['latitude']
            lon = config['longitude']
            radius_km = config['radius_km']
            analysis_columns = config.get('analysis_columns', ['potencial_biogas_total'])

            # Run core proximity analysis
            results = self.proximity_analyzer.analyze_catchment_area(
                lat, lon, radius_km, municipality_data, analysis_columns
            )

            return results

        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return {'error': f'Analysis failed: {str(e)}'}

    def _add_raster_analysis(self, results: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add raster analysis to proximity results"""
        try:
            # Check if raster files are available
            available_rasters = self.mapbiomas_loader.get_available_mapbiomas_files()

            if not available_rasters:
                self.logger.warning("No raster files available for analysis")
                return

            # Perform raster analysis
            lat = config['latitude']
            lon = config['longitude']
            radius_km = config['radius_km']

            # Use first available raster file
            raster_file = available_rasters[0]
            raster_path = raster_file['path']

            with st.spinner("🛰️ Adding satellite data analysis..."):
                raster_results = self.mapbiomas_loader.analyze_radius_area(
                    raster_path, lat, lon, radius_km
                )

            if raster_results:
                # Add raster results to main results
                results['raster_analysis'] = raster_results
                st.success("✅ Satellite data analysis added")
            else:
                st.warning("⚠️ Could not complete satellite data analysis")

        except Exception as e:
            self.logger.error(f"Error adding raster analysis: {e}")
            st.warning("⚠️ Error adding satellite data analysis")

    def _render_disabled_state(self) -> None:
        """Render content when proximity analysis is disabled"""
        st.markdown("## 🎯 Proximity Analysis")

        st.info("**Enable proximity analysis in the sidebar to get started**")

        st.markdown("""
        ### 🔍 What is Proximity Analysis?

        Proximity analysis helps you find the optimal location for biogas plants by analyzing:

        - **Catchment Areas**: Municipality distribution within specified radius
        - **Biogas Potential**: Total and per-source biogas generation capacity
        - **Transport Optimization**: Distance-weighted resource accessibility
        - **Feasibility Assessment**: Economic viability based on potential and concentration

        ### 📊 Features Available:

        - **Interactive Map Selection**: Click to choose analysis center
        - **Flexible Radius**: Analyze areas from 1km to 100km radius
        - **Multi-Source Analysis**: Animal waste, agricultural residues, total potential
        - **Satellite Integration**: Land use analysis from MapBiomas data
        - **Professional Reports**: Export results for academic or commercial use

        ### 🚀 Getting Started:

        1. **Enable Analysis**: Check "Enable Proximity Analysis" in the sidebar
        2. **Set Parameters**: Choose analysis radius and options
        3. **Select Center**: Click on map or use coordinates
        4. **Run Analysis**: Click "Run Analysis" to generate results
        """)

        # Show sample visualization
        st.markdown("### 📈 Sample Analysis Output:")
        st.image("https://via.placeholder.com/600x300/1f77b4/ffffff?text=Sample+Proximity+Analysis+Chart",
                caption="Example: Biogas potential distribution within 50km radius")


# Factory function for page creation
def create_proximity_analysis_page() -> ProximityAnalysisPage:
    """
    Create ProximityAnalysisPage instance

    Returns:
        ProximityAnalysisPage instance
    """
    return ProximityAnalysisPage()