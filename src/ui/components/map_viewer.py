"""
CP2B Maps V2 - Advanced MapViewer Component
Professional multi-layer map with interactive municipality visualization
"""

import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from branca.colormap import LinearColormap

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader, shapefile_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class MapViewer:
    """
    Advanced map viewer with multi-layer controls and interactive visualization
    Features: Layer management, choropleth mapping, municipality polygons, performance optimization
    """

    def __init__(self):
        """Initialize MapViewer with layer configurations"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing MapViewer component")

        # Layer configurations
        self.layer_configs = {
            'municipalities': {
                'name': 'Municipality Boundaries',
                'description': 'São Paulo municipality polygons with biogas potential',
                'default_visible': True,
                'performance_limit': 100
            },
            'biogas_plants': {
                'name': 'Biogas Plants',
                'description': '425 existing and potential biogas facilities',
                'default_visible': True,
                'performance_limit': 50
            },
            'state_boundary': {
                'name': 'State Boundary',
                'description': 'São Paulo state administrative boundary',
                'default_visible': True,
                'performance_limit': 1
            },
            'pipelines': {
                'name': 'Gas Pipelines',
                'description': 'Natural gas pipeline infrastructure',
                'default_visible': False,
                'performance_limit': 200
            }
        }

    def render(self, selected_municipalities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Render advanced map viewer with layer controls

        Args:
            selected_municipalities: List of municipality names to highlight

        Returns:
            Dictionary with map interaction data and selected features
        """
        try:
            st.markdown("### 🗺️ Advanced Interactive Map")

            # Layer controls
            layer_controls = self._render_layer_controls()

            # Map view controls
            map_config = self._render_map_controls()

            # Create and configure map
            map_obj = self._create_base_map(map_config)

            # Add layers based on user selection
            layer_data = self._add_selected_layers(map_obj, layer_controls, selected_municipalities)

            # Render map with interactions
            map_data = self._render_interactive_map(map_obj)

            # Process and return interaction results
            interaction_results = self._process_map_interactions(map_data, layer_data)

            return interaction_results

        except Exception as e:
            self.logger.error(f"Error rendering map viewer: {e}", exc_info=True)
            st.error("⚠️ Failed to render map viewer. Check logs for details.")
            return {}

    def _render_layer_controls(self) -> Dict[str, bool]:
        """Render layer control checkboxes"""
        st.markdown("#### 🎛️ Map Layers")

        layer_controls = {}
        cols = st.columns(2)

        for i, (layer_id, config) in enumerate(self.layer_configs.items()):
            col = cols[i % 2]
            with col:
                layer_controls[layer_id] = st.checkbox(
                    f"{config['name']}",
                    value=config['default_visible'],
                    help=config['description'],
                    key=f"layer_{layer_id}"
                )

        return layer_controls

    def _render_map_controls(self) -> Dict[str, Any]:
        """Render map configuration controls"""
        with st.expander("🔧 Map Configuration", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                map_style = st.selectbox(
                    "Map Style",
                    options=['CartoDB positron', 'CartoDB dark_matter', 'OpenStreetMap'],
                    index=0,
                    help="Choose base map style"
                )

                zoom_level = st.slider(
                    "Initial Zoom",
                    min_value=6, max_value=12, value=7,
                    help="Set initial map zoom level"
                )

            with col2:
                center_lat = st.number_input(
                    "Center Latitude",
                    value=settings.DEFAULT_CENTER[0],
                    format="%.6f",
                    help="Map center latitude"
                )

                center_lon = st.number_input(
                    "Center Longitude",
                    value=settings.DEFAULT_CENTER[1],
                    format="%.6f",
                    help="Map center longitude"
                )

        return {
            'style': map_style,
            'zoom': zoom_level,
            'center': [center_lat, center_lon]
        }

    def _create_base_map(self, config: Dict[str, Any]) -> folium.Map:
        """Create base folium map with configuration"""
        map_obj = folium.Map(
            location=config['center'],
            zoom_start=config['zoom'],
            tiles=config['style']
        )

        # Add fullscreen plugin
        folium.plugins.Fullscreen().add_to(map_obj)

        # Add measure control
        folium.plugins.MeasureControl().add_to(map_obj)

        return map_obj

    def _add_selected_layers(self,
                           map_obj: folium.Map,
                           layer_controls: Dict[str, bool],
                           selected_municipalities: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add selected layers to map"""
        layer_data = {}

        # Add state boundary layer
        if layer_controls.get('state_boundary', False):
            boundary_data = self._add_state_boundary_layer(map_obj)
            layer_data['state_boundary'] = boundary_data

        # Add municipalities layer with biogas visualization
        if layer_controls.get('municipalities', False):
            municipalities_data = self._add_municipalities_layer(
                map_obj, selected_municipalities
            )
            layer_data['municipalities'] = municipalities_data

        # Add biogas plants layer
        if layer_controls.get('biogas_plants', False):
            plants_data = self._add_biogas_plants_layer(map_obj)
            layer_data['biogas_plants'] = plants_data

        # Add pipelines layer
        if layer_controls.get('pipelines', False):
            pipelines_data = self._add_pipelines_layer(map_obj)
            layer_data['pipelines'] = pipelines_data

        return layer_data

    def _add_state_boundary_layer(self, map_obj: folium.Map) -> Optional[gpd.GeoDataFrame]:
        """Add São Paulo state boundary"""
        try:
            boundary = shapefile_loader.load_state_boundary()
            if boundary is not None:
                folium.GeoJson(
                    boundary,
                    style_function=lambda feature: {
                        'color': '#2E8B57',
                        'weight': 3,
                        'opacity': 0.8,
                        'fillOpacity': 0.1,
                        'dashArray': '5, 5'
                    },
                    popup="São Paulo State",
                    tooltip="São Paulo State - 645 Municipalities"
                ).add_to(map_obj)

                self.logger.info("Added state boundary layer")
                return boundary

        except Exception as e:
            self.logger.error(f"Error adding state boundary: {e}")

        return None

    def _add_municipalities_layer(self,
                                map_obj: folium.Map,
                                selected_municipalities: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Add municipalities with biogas potential choropleth"""
        try:
            # Load municipality data
            municipalities_df = database_loader.load_municipalities_data()
            if municipalities_df is None or len(municipalities_df) == 0:
                self.logger.warning("No municipality data available for mapping")
                return None

            # Create choropleth colormap for biogas potential
            biogas_values = municipalities_df['biogas_potential_m3_day'].fillna(0)
            colormap = LinearColormap(
                colors=['yellow', 'orange', 'red', 'darkred'],
                vmin=biogas_values.min(),
                vmax=biogas_values.max(),
                caption='Biogas Potential (m³/day)'
            )

            # Add colormap to map
            colormap.add_to(map_obj)

            # Add top municipalities as circles (performance optimization)
            top_municipalities = municipalities_df.nlargest(
                self.layer_configs['municipalities']['performance_limit'],
                'biogas_potential_m3_day'
            )

            for _, municipality in top_municipalities.iterrows():
                # Calculate circle size based on biogas potential
                biogas_potential = municipality.get('biogas_potential_m3_day', 0)
                radius = min(max(biogas_potential / 1000, 3), 20)  # Scale radius 3-20

                # Determine color and opacity
                color = colormap(biogas_potential)
                is_selected = (selected_municipalities and
                             municipality.get('nome_municipio') in selected_municipalities)

                folium.CircleMarker(
                    location=[
                        municipality.get('latitude', settings.DEFAULT_CENTER[0]),
                        municipality.get('longitude', settings.DEFAULT_CENTER[1])
                    ],
                    radius=radius,
                    popup=self._create_municipality_popup(municipality),
                    tooltip=f"{municipality.get('nome_municipio', 'Unknown')}: {biogas_potential:,.0f} m³/day",
                    color='black' if is_selected else color,
                    weight=3 if is_selected else 1,
                    fillColor=color,
                    fillOpacity=0.8 if is_selected else 0.6
                ).add_to(map_obj)

            self.logger.info(f"Added {len(top_municipalities)} municipality markers")

            return {
                'data': top_municipalities,
                'colormap': colormap,
                'total_municipalities': len(municipalities_df)
            }

        except Exception as e:
            self.logger.error(f"Error adding municipalities layer: {e}")

        return None

    def _add_biogas_plants_layer(self, map_obj: folium.Map) -> Optional[gpd.GeoDataFrame]:
        """Add biogas plants markers"""
        try:
            plants = shapefile_loader.load_biogas_plants()
            if plants is not None and len(plants) > 0:
                # Limit plants for performance
                display_plants = plants.head(self.layer_configs['biogas_plants']['performance_limit'])

                for _, plant in display_plants.iterrows():
                    folium.CircleMarker(
                        location=[plant.geometry.y, plant.geometry.x],
                        radius=6,
                        popup=self._create_plant_popup(plant),
                        tooltip=f"Biogas Plant: {plant.get('TIPO_PLANT', 'Unknown')}",
                        color='#FF6B35',
                        fillColor='#FF6B35',
                        fillOpacity=0.8,
                        weight=2
                    ).add_to(map_obj)

                self.logger.info(f"Added {len(display_plants)} biogas plant markers")
                return display_plants

        except Exception as e:
            self.logger.error(f"Error adding biogas plants: {e}")

        return None

    def _add_pipelines_layer(self, map_obj: folium.Map) -> Optional[gpd.GeoDataFrame]:
        """Add gas pipelines if available"""
        try:
            # This is a placeholder for future pipeline data
            # Would load from shapefile_loader.load_pipelines() when available
            self.logger.info("Pipeline layer not yet implemented")
            return None

        except Exception as e:
            self.logger.error(f"Error adding pipelines: {e}")

        return None

    def _create_municipality_popup(self, municipality: pd.Series) -> str:
        """Create detailed popup for municipality"""
        name = municipality.get('nome_municipio', 'Unknown')
        biogas = municipality.get('biogas_potential_m3_day', 0)
        energy = municipality.get('energy_potential_kwh_day', 0)
        population = municipality.get('population', 0)

        return f"""
        <div style='width: 200px'>
            <h4>{name}</h4>
            <b>Biogas Potential:</b> {biogas:,.0f} m³/day<br>
            <b>Energy Potential:</b> {energy:,.0f} kWh/day<br>
            <b>Population:</b> {population:,}<br>
            <hr>
            <small>Click for detailed analysis</small>
        </div>
        """

    def _create_plant_popup(self, plant: pd.Series) -> str:
        """Create popup for biogas plant"""
        plant_type = plant.get('TIPO_PLANT', 'Unknown')
        return f"""
        <div style='width: 150px'>
            <h4>Biogas Plant</h4>
            <b>Type:</b> {plant_type}<br>
            <hr>
            <small>Existing or potential facility</small>
        </div>
        """

    def _render_interactive_map(self, map_obj: folium.Map) -> Dict[str, Any]:
        """Render map with interaction handling"""
        map_data = st_folium(
            map_obj,
            width=700,
            height=600,
            returned_objects=["last_object_clicked", "last_clicked", "bounds"],
            key="advanced_map_viewer"
        )

        return map_data

    def _process_map_interactions(self,
                                map_data: Dict[str, Any],
                                layer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process map interaction results"""
        results = {
            'clicked_object': map_data.get('last_object_clicked'),
            'clicked_location': map_data.get('last_clicked'),
            'map_bounds': map_data.get('bounds'),
            'layer_data': layer_data
        }

        # Show interaction feedback
        if results['clicked_object']:
            st.success("✅ Map object clicked! See details in the sidebar.")
        elif results['clicked_location']:
            lat, lon = results['clicked_location']['lat'], results['clicked_location']['lng']
            st.info(f"📍 Location clicked: {lat:.4f}, {lon:.4f}")

        return results