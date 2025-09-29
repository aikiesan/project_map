"""
CP2B Maps V2 - Proximity Analysis Controls Component
Interactive UI controls for proximity analysis and biogas plant location optimization
"""

from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import pandas as pd

from config.settings import settings
from src.utils.logging_config import get_logger
from src.core.proximity_analyzer import get_proximity_analyzer

logger = get_logger(__name__)


class ProximityControls:
    """
    Professional proximity analysis controls with interactive features
    Features: Radius selection, coordinate input, analysis triggers, result caching
    """

    def __init__(self):
        """Initialize ProximityControls"""
        self.logger = get_logger(self.__class__.__name__)
        self.proximity_analyzer = get_proximity_analyzer()

    def render(self, municipality_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Render the complete proximity controls interface

        Args:
            municipality_data: Municipality data for validation

        Returns:
            Dictionary with control settings and user interactions
        """
        try:
            st.markdown("### 🎯 Proximity Analysis Controls")

            # Create main control sections
            controls = {}

            # Analysis enablement
            controls['enabled'] = self._render_analysis_toggle()

            if controls['enabled']:
                # Analysis parameters
                controls['parameters'] = self._render_analysis_parameters()

                # Coordinate input options
                controls['coordinate_input'] = self._render_coordinate_input()

                # Advanced options
                controls['advanced'] = self._render_advanced_options()

                # Analysis triggers
                controls['triggers'] = self._render_analysis_triggers(municipality_data)

                # Quick analysis options
                controls['quick_analysis'] = self._render_quick_analysis_options()

            else:
                # Clear any existing analysis when disabled
                self._clear_proximity_session_state()

            return controls

        except Exception as e:
            self.logger.error(f"Error rendering proximity controls: {e}")
            st.error("⚠️ Error rendering proximity controls")
            return {'enabled': False}

    def _render_analysis_toggle(self) -> bool:
        """Render the main analysis enable/disable toggle"""
        return st.checkbox(
            "🎯 Enable Proximity Analysis",
            value=st.session_state.get('proximity_enabled', False),
            key='proximity_enabled',
            help="Enable radius-based catchment area analysis for biogas plant location optimization"
        )

    def _render_analysis_parameters(self) -> Dict[str, Any]:
        """Render analysis parameter controls"""
        st.markdown("#### 📏 Analysis Parameters")

        col1, col2 = st.columns(2)

        with col1:
            radius_km = st.slider(
                "Analysis Radius (km):",
                min_value=1.0,
                max_value=100.0,
                value=st.session_state.get('proximity_radius', settings.DEFAULT_ANALYSIS_RADIUS_KM),
                step=1.0,
                key='proximity_radius',
                help="Radius for catchment area analysis"
            )

        with col2:
            analysis_depth = st.selectbox(
                "Analysis Depth:",
                options=['Basic', 'Standard', 'Comprehensive'],
                index=['Basic', 'Standard', 'Comprehensive'].index(
                    st.session_state.get('proximity_depth', 'Standard')
                ),
                key='proximity_depth',
                help="Level of detail for analysis results"
            )

        return {
            'radius_km': radius_km,
            'analysis_depth': analysis_depth
        }

    def _render_coordinate_input(self) -> Dict[str, Any]:
        """Render coordinate input options"""
        st.markdown("#### 📍 Analysis Center")

        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            options=['Map Click', 'Manual Input', 'Municipality Center'],
            index=0,
            key='proximity_input_method',
            help="How to specify the analysis center point"
        )

        coordinates = {'method': input_method}

        if input_method == 'Manual Input':
            coordinates.update(self._render_manual_coordinates())
        elif input_method == 'Municipality Center':
            coordinates.update(self._render_municipality_selection())
        else:  # Map Click
            coordinates.update(self._render_map_click_info())

        return coordinates

    def _render_manual_coordinates(self) -> Dict[str, Any]:
        """Render manual coordinate input"""
        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input(
                "Latitude:",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.get('proximity_manual_lat', settings.DEFAULT_CENTER[0]),
                step=0.0001,
                format="%.4f",
                key='proximity_manual_lat',
                help="Latitude in decimal degrees"
            )

        with col2:
            longitude = st.number_input(
                "Longitude:",
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.get('proximity_manual_lon', settings.DEFAULT_CENTER[1]),
                step=0.0001,
                format="%.4f",
                key='proximity_manual_lon',
                help="Longitude in decimal degrees"
            )

        # Validation
        is_valid, msg = self.proximity_analyzer.validate_coordinates(
            latitude, longitude, st.session_state.get('proximity_radius', 50.0)
        )

        if is_valid:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

        return {
            'latitude': latitude,
            'longitude': longitude,
            'valid': is_valid,
            'message': msg
        }

    def _render_municipality_selection(self) -> Dict[str, Any]:
        """Render municipality center selection"""
        # This would require municipality data with coordinates
        st.info("💡 Select a municipality to use its center as analysis point")

        # Placeholder for municipality selection
        # In a real implementation, this would load municipality data
        selected_municipality = st.selectbox(
            "Select Municipality:",
            options=['São Paulo', 'Campinas', 'Santos', 'Ribeirão Preto'],
            key='proximity_selected_municipality',
            help="Choose municipality center for analysis"
        )

        # Dummy coordinates (in real implementation, lookup from data)
        municipality_coords = {
            'São Paulo': (-23.5505, -46.6333),
            'Campinas': (-22.9099, -47.0626),
            'Santos': (-23.9618, -46.3322),
            'Ribeirão Preto': (-21.1775, -47.8108)
        }

        coords = municipality_coords.get(selected_municipality, settings.DEFAULT_CENTER)

        return {
            'municipality': selected_municipality,
            'latitude': coords[0],
            'longitude': coords[1],
            'valid': True,
            'message': f"Using {selected_municipality} center coordinates"
        }

    def _render_map_click_info(self) -> Dict[str, Any]:
        """Render map click information and instructions"""
        st.info("🗺️ Click on the map to set analysis center point")

        # Check for map click data in session state
        if 'map_click_lat' in st.session_state and 'map_click_lon' in st.session_state:
            lat = st.session_state['map_click_lat']
            lon = st.session_state['map_click_lon']

            st.success(f"📍 Map clicked at: {lat:.4f}, {lon:.4f}")

            # Validation
            is_valid, msg = self.proximity_analyzer.validate_coordinates(
                lat, lon, st.session_state.get('proximity_radius', 50.0)
            )

            if not is_valid:
                st.warning(f"⚠️ {msg}")

            return {
                'latitude': lat,
                'longitude': lon,
                'valid': is_valid,
                'message': msg if is_valid else f"Map click validation: {msg}"
            }
        else:
            st.info("👆 No map click detected yet")
            return {
                'latitude': None,
                'longitude': None,
                'valid': False,
                'message': "Waiting for map click"
            }

    def _render_advanced_options(self) -> Dict[str, Any]:
        """Render advanced analysis options"""
        with st.expander("🔧 Advanced Options"):
            st.markdown("#### Analysis Configuration")

            col1, col2 = st.columns(2)

            with col1:
                include_raster = st.checkbox(
                    "Include Raster Analysis",
                    value=st.session_state.get('proximity_include_raster', True),
                    key='proximity_include_raster',
                    help="Include land use analysis from satellite data"
                )

                show_optimization = st.checkbox(
                    "Show Optimization Metrics",
                    value=st.session_state.get('proximity_show_optimization', True),
                    key='proximity_show_optimization',
                    help="Display plant location optimization calculations"
                )

            with col2:
                cache_results = st.checkbox(
                    "Cache Analysis Results",
                    value=st.session_state.get('proximity_cache_results', True),
                    key='proximity_cache_results',
                    help="Cache results to avoid repeated calculations"
                )

                export_format = st.selectbox(
                    "Export Format:",
                    options=['CSV', 'Excel', 'GeoJSON'],
                    index=0,
                    key='proximity_export_format',
                    help="Format for exporting analysis results"
                )

            # Analysis columns selection
            st.markdown("#### Data Columns to Analyze")
            analysis_columns = st.multiselect(
                "Select columns:",
                options=[
                    'potencial_biogas_total',
                    'potencial_biogas_animais',
                    'potencial_biogas_agricola',
                    'populacao_total',
                    'area_km2'
                ],
                default=['potencial_biogas_total', 'potencial_biogas_animais'],
                key='proximity_analysis_columns',
                help="Choose which data columns to include in analysis"
            )

        return {
            'include_raster': include_raster,
            'show_optimization': show_optimization,
            'cache_results': cache_results,
            'export_format': export_format,
            'analysis_columns': analysis_columns
        }

    def _render_analysis_triggers(self, municipality_data: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Render analysis trigger buttons and controls"""
        st.markdown("#### 🚀 Analysis Actions")

        col1, col2, col3 = st.columns(3)

        triggers = {}

        with col1:
            triggers['run_analysis'] = st.button(
                "🎯 Run Analysis",
                key='proximity_run_analysis',
                help="Perform proximity analysis with current settings",
                type="primary"
            )

        with col2:
            triggers['clear_results'] = st.button(
                "🗑️ Clear Results",
                key='proximity_clear_results',
                help="Clear all analysis results and cached data"
            )

        with col3:
            triggers['find_optimal'] = st.button(
                "📍 Find Optimal Location",
                key='proximity_find_optimal',
                help="Search for optimal biogas plant locations",
                disabled=(municipality_data is None)
            )

        # Handle clear results
        if triggers['clear_results']:
            self._clear_proximity_session_state()
            st.success("✅ Analysis results cleared")
            st.rerun()

        return triggers

    def _render_quick_analysis_options(self) -> Dict[str, Any]:
        """Render quick analysis preset options"""
        with st.expander("⚡ Quick Analysis Presets"):
            st.markdown("#### Predefined Analysis Scenarios")

            col1, col2 = st.columns(2)

            presets = {}

            with col1:
                presets['small_plant'] = st.button(
                    "🏭 Small Plant (15km)",
                    key='proximity_preset_small',
                    help="Quick analysis for small biogas plant (15km radius)"
                )

                presets['regional_plant'] = st.button(
                    "🏗️ Regional Plant (50km)",
                    key='proximity_preset_regional',
                    help="Analysis for regional biogas plant (50km radius)"
                )

            with col2:
                presets['transport_study'] = st.button(
                    "🚛 Transport Study (25km)",
                    key='proximity_preset_transport',
                    help="Focus on transport optimization (25km radius)"
                )

                presets['feasibility_study'] = st.button(
                    "📊 Feasibility Study (30km)",
                    key='proximity_preset_feasibility',
                    help="Comprehensive feasibility analysis (30km radius)"
                )

            # Handle preset selection
            for preset, clicked in presets.items():
                if clicked:
                    self._apply_preset(preset)

        return presets

    def _apply_preset(self, preset_name: str) -> None:
        """Apply predefined analysis preset"""
        try:
            presets = {
                'small_plant': {
                    'proximity_radius': 15.0,
                    'proximity_depth': 'Basic',
                    'proximity_include_raster': False,
                    'proximity_analysis_columns': ['potencial_biogas_total']
                },
                'regional_plant': {
                    'proximity_radius': 50.0,
                    'proximity_depth': 'Comprehensive',
                    'proximity_include_raster': True,
                    'proximity_analysis_columns': ['potencial_biogas_total', 'potencial_biogas_animais', 'potencial_biogas_agricola']
                },
                'transport_study': {
                    'proximity_radius': 25.0,
                    'proximity_depth': 'Standard',
                    'proximity_show_optimization': True,
                    'proximity_analysis_columns': ['potencial_biogas_total']
                },
                'feasibility_study': {
                    'proximity_radius': 30.0,
                    'proximity_depth': 'Comprehensive',
                    'proximity_include_raster': True,
                    'proximity_show_optimization': True,
                    'proximity_analysis_columns': ['potencial_biogas_total', 'potencial_biogas_animais', 'populacao_total']
                }
            }

            preset_config = presets.get(preset_name, {})

            # Apply preset settings to session state
            for key, value in preset_config.items():
                st.session_state[key] = value

            st.success(f"✅ Applied {preset_name.replace('_', ' ').title()} preset")
            st.rerun()

        except Exception as e:
            self.logger.error(f"Error applying preset {preset_name}: {e}")
            st.error("⚠️ Error applying preset")

    def _clear_proximity_session_state(self) -> None:
        """Clear proximity analysis session state"""
        try:
            # Keys to clear
            keys_to_clear = [
                'proximity_results',
                'proximity_analysis_cache',
                'proximity_raster_results',
                'proximity_map_data',
                'map_click_lat',
                'map_click_lon'
            ]

            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

            self.logger.info("Proximity analysis session state cleared")

        except Exception as e:
            self.logger.error(f"Error clearing session state: {e}")

    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Get current analysis configuration from session state

        Returns:
            Dictionary with current analysis configuration
        """
        try:
            config = {
                'enabled': st.session_state.get('proximity_enabled', False),
                'radius_km': st.session_state.get('proximity_radius', settings.DEFAULT_ANALYSIS_RADIUS_KM),
                'analysis_depth': st.session_state.get('proximity_depth', 'Standard'),
                'input_method': st.session_state.get('proximity_input_method', 'Map Click'),
                'include_raster': st.session_state.get('proximity_include_raster', True),
                'show_optimization': st.session_state.get('proximity_show_optimization', True),
                'cache_results': st.session_state.get('proximity_cache_results', True),
                'export_format': st.session_state.get('proximity_export_format', 'CSV'),
                'analysis_columns': st.session_state.get('proximity_analysis_columns', ['potencial_biogas_total'])
            }

            # Add coordinates based on input method
            if config['input_method'] == 'Manual Input':
                config['latitude'] = st.session_state.get('proximity_manual_lat')
                config['longitude'] = st.session_state.get('proximity_manual_lon')
            elif config['input_method'] == 'Map Click':
                config['latitude'] = st.session_state.get('map_click_lat')
                config['longitude'] = st.session_state.get('map_click_lon')
            elif config['input_method'] == 'Municipality Center':
                # Would load from municipality data in real implementation
                config['latitude'] = settings.DEFAULT_CENTER[0]
                config['longitude'] = settings.DEFAULT_CENTER[1]

            return config

        except Exception as e:
            self.logger.error(f"Error getting analysis config: {e}")
            return {'enabled': False}

    def is_ready_for_analysis(self) -> Tuple[bool, str]:
        """
        Check if all requirements for analysis are met

        Returns:
            Tuple of (is_ready, message)
        """
        try:
            config = self.get_analysis_config()

            if not config['enabled']:
                return False, "Proximity analysis is not enabled"

            if config['latitude'] is None or config['longitude'] is None:
                return False, "Analysis center coordinates not specified"

            # Validate coordinates
            is_valid, msg = self.proximity_analyzer.validate_coordinates(
                config['latitude'], config['longitude'], config['radius_km']
            )

            if not is_valid:
                return False, f"Invalid coordinates: {msg}"

            return True, "Ready for analysis"

        except Exception as e:
            self.logger.error(f"Error checking analysis readiness: {e}")
            return False, f"Error checking readiness: {str(e)}"


# Factory function
def create_proximity_controls() -> ProximityControls:
    """
    Create ProximityControls instance

    Returns:
        ProximityControls instance
    """
    return ProximityControls()