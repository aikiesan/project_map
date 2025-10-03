"""
CP2B Maps V2 - Map Builder Component
Handles map creation with municipality data visualization
Single Responsibility: Build Folium maps with configured layers
"""

import folium
import folium.plugins
import pandas as pd
import streamlit as st
from typing import Optional

from config.settings import settings
from src.utils.logging_config import get_logger
from src.ui.models.map_config import MapConfig
from src.data.loaders.shapefile_loader import shapefile_loader

logger = get_logger(__name__)


class MapBuilder:
    """
    Builds Folium maps with municipality data and layers
    Handles all map visualization logic
    """

    def __init__(self):
        """Initialize map builder"""
        self.logger = get_logger(self.__class__.__name__)

    def build_map(self,
                  municipalities_df: pd.DataFrame,
                  config: MapConfig) -> folium.Map:
        """
        Build Folium map with configuration

        Args:
            municipalities_df: Municipality data
            config: Map configuration

        Returns:
            Configured Folium map
        """
        try:
            # Create base map
            m = folium.Map(
                location=[config.center_lat, config.center_lon],
                zoom_start=config.zoom_start,
                tiles='CartoDB positron',
                prefer_canvas=True
            )

            # Add fullscreen control
            folium.plugins.Fullscreen().add_to(m)

            # Add state boundary
            if config.show_boundary:
                self._add_state_boundary(m)

            # Add regional boundaries if enabled
            if config.show_regioes_intermediarias:
                self._add_intermediate_regions(m)

            if config.show_regioes_imediatas:
                self._add_immediate_regions(m)

            # Add municipality circles if biogas layer enabled
            if config.show_biogas and municipalities_df is not None:
                self._add_municipality_layer(m, municipalities_df, config)

            # Add biogas plants if enabled
            if config.show_plantas:
                self._add_biogas_plants(m)

            # Add floating legend
            if config.show_legend and config.show_biogas:
                self._add_floating_legend(m, municipalities_df, config)

            return m

        except Exception as e:
            self.logger.error(f"Error building map: {e}", exc_info=True)
            # Return empty map on error
            return folium.Map(location=[config.center_lat, config.center_lon], zoom_start=config.zoom_start)

    def _add_state_boundary(self, m: folium.Map) -> None:
        """Add São Paulo state boundary"""
        try:
            state_boundary = shapefile_loader.load_state_boundary()
            if state_boundary is not None:
                folium.GeoJson(
                    state_boundary,
                    style_function=lambda feature: {
                        'color': '#2E8B57',
                        'weight': 2,
                        'opacity': 0.8,
                        'fillOpacity': 0.05,
                        'dashArray': '5, 5'
                    },
                    tooltip="São Paulo State"
                ).add_to(m)
        except Exception as e:
            self.logger.warning(f"Could not add state boundary: {e}")

    def _add_intermediate_regions(self, m: folium.Map) -> None:
        """Add IBGE intermediate regions boundaries"""
        try:
            intermediate_regions = shapefile_loader.load_intermediate_regions()
            if intermediate_regions is not None:
                folium.GeoJson(
                    intermediate_regions,
                    style_function=lambda feature: {
                        'color': '#1565C0',
                        'weight': 3,
                        'opacity': 0.8,
                        'fillOpacity': 0.1,
                        'fillColor': '#1976D2',
                        'dashArray': '8, 4'
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['NM_RGINT', 'AREA_KM2'],
                        aliases=['Região Intermediária:', 'Área (km²):'],
                        localize=True,
                        sticky=False,
                        labels=True,
                        style="""
                            background-color: white;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """
                    )
                ).add_to(m)
                self.logger.debug("Added intermediate regions to map")
        except Exception as e:
            self.logger.warning(f"Could not add intermediate regions: {e}")

    def _add_immediate_regions(self, m: folium.Map) -> None:
        """Add IBGE immediate regions boundaries"""
        try:
            immediate_regions = shapefile_loader.load_immediate_regions()
            if immediate_regions is not None:
                folium.GeoJson(
                    immediate_regions,
                    style_function=lambda feature: {
                        'color': '#E65100',
                        'weight': 2,
                        'opacity': 0.7,
                        'fillOpacity': 0.05,
                        'fillColor': '#FF9800',
                        'dashArray': '4, 2'
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['NM_RGI', 'NM_RGINT', 'AREA_KM2'],
                        aliases=['Região Imediata:', 'Região Intermediária:', 'Área (km²):'],
                        localize=True,
                        sticky=False,
                        labels=True,
                        style="""
                            background-color: white;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """
                    )
                ).add_to(m)
                self.logger.debug("Added immediate regions to map")
        except Exception as e:
            self.logger.warning(f"Could not add immediate regions: {e}")

    def _add_municipality_layer(self,
                                m: folium.Map,
                                df: pd.DataFrame,
                                config: MapConfig) -> None:
        """Add municipality data layer based on visualization type"""
        if df is None or len(df) == 0:
            return

        # Filter and prepare data
        df_filtered = df[df[config.data_column] > 0].copy()

        # Apply search filter
        if config.search_term and len(config.search_term) >= 2:
            df_filtered = df_filtered[
                df_filtered['municipality'].str.contains(config.search_term, case=False, na=False)
            ]

        if len(df_filtered) == 0:
            return

        # Render based on visualization type
        if config.viz_type == "Círculos Proporcionais":
            self._add_circle_markers(m, df_filtered, config)
        elif config.viz_type == "Mapa de Calor (Heatmap)":
            self._add_heatmap(m, df_filtered, config)
        elif config.viz_type == "Agrupamentos (Clusters)":
            self._add_clusters(m, df_filtered, config)
        # Choropleth would go here but requires more complex setup

    def _add_circle_markers(self,
                           m: folium.Map,
                           df: pd.DataFrame,
                           config: MapConfig) -> None:
        """Add proportional circle markers"""
        max_val = df[config.data_column].max()
        min_val = df[config.data_column].min()

        for _, row in df.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                value = row[config.data_column]

                # Calculate radius (5-25 pixels)
                if max_val > min_val:
                    normalized = (value - min_val) / (max_val - min_val)
                    radius = 5 + (normalized * 20)
                else:
                    radius = 10

                # Color based on value
                color = self._get_color_for_value(value, min_val, max_val)

                # Create popup
                popup_html = f"""
                <div style='font-family: Arial; font-size: 12px;'>
                    <h4 style='margin: 0 0 8px 0; color: #2E8B57;'>{row['municipality']}</h4>
                    <b>Potencial:</b> {value:,.0f} m³/ano<br>
                    <b>População:</b> {row.get('population', 0):,.0f}<br>
                    <small>Clique para mais detalhes</small>
                </div>
                """

                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['municipality']}: {value:,.0f} m³/ano",
                    color=color,
                    fillColor=color,
                    fillOpacity=0.6,
                    weight=2,
                    opacity=0.8
                ).add_to(m)

    def _add_heatmap(self,
                    m: folium.Map,
                    df: pd.DataFrame,
                    config: MapConfig) -> None:
        """Add heatmap visualization"""
        heat_data = [
            [row['latitude'], row['longitude'], row[config.data_column]]
            for _, row in df.iterrows()
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude'))
        ]

        if heat_data:
            folium.plugins.HeatMap(
                heat_data,
                radius=25,
                blur=30,
                max_zoom=13,
                gradient={
                    0.0: '#00ff00',
                    0.5: '#ffff00',
                    1.0: '#ff0000'
                }
            ).add_to(m)

    def _add_clusters(self,
                     m: folium.Map,
                     df: pd.DataFrame,
                     config: MapConfig) -> None:
        """Add marker clusters"""
        marker_cluster = folium.plugins.MarkerCluster(name="Municípios").add_to(m)

        for _, row in df.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                value = row[config.data_column]

                popup_html = f"""
                <div style='font-family: Arial; font-size: 12px;'>
                    <h4 style='margin: 0 0 8px 0; color: #2E8B57;'>{row['municipality']}</h4>
                    <b>Potencial:</b> {value:,.0f} m³/ano<br>
                    <b>População:</b> {row.get('population', 0):,.0f}
                </div>
                """

                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=row['municipality'],
                    color='#2E8B57',
                    fillColor='#32CD32',
                    fillOpacity=0.7,
                    weight=2
                ).add_to(marker_cluster)

    def _add_biogas_plants(self, m: folium.Map) -> None:
        """Add biogas plant markers"""
        try:
            biogas_plants = shapefile_loader.load_biogas_plants()
            if biogas_plants is not None and len(biogas_plants) > 0:
                display_plants = biogas_plants.head(100)
                for _, plant in display_plants.iterrows():
                    folium.CircleMarker(
                        location=[plant.geometry.y, plant.geometry.x],
                        radius=4,
                        popup=f"🏭 {plant.get('TIPO_PLANT', 'Planta de Biogás')}",
                        color='#FF6B35',
                        fillColor='#FF6B35',
                        fillOpacity=0.7,
                        weight=1
                    ).add_to(m)
        except Exception as e:
            self.logger.warning(f"Could not add biogas plants: {e}")

    def _add_floating_legend(self,
                            m: folium.Map,
                            df: pd.DataFrame,
                            config: MapConfig) -> None:
        """Add floating legend to map"""
        try:
            df_filtered = df[df[config.data_column] > 0]
            if len(df_filtered) == 0:
                return

            max_val = df_filtered[config.data_column].max()

            legend_html = f'''
            <div style="position: fixed;
                        bottom: 50px; right: 50px; width: 200px; height: auto;
                        background-color: white; z-index:9999; font-size:12px;
                        border-radius: 8px; padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        border: 2px solid #2E8B57;">
                <p style="margin: 0 0 8px 0; font-weight: bold; color: #2E8B57; font-size: 13px;">
                    📊 Potencial de Biogás
                </p>
                <div style="margin: 4px 0;">
                    <span style="background: #C8E6C9; width: 20px; height: 12px; display: inline-block; border: 1px solid #888;"></span>
                    <span style="margin-left: 5px;">0 - {max_val*0.25:,.0f}</span>
                </div>
                <div style="margin: 4px 0;">
                    <span style="background: #81C784; width: 20px; height: 12px; display: inline-block; border: 1px solid #888;"></span>
                    <span style="margin-left: 5px;">{max_val*0.25:,.0f} - {max_val*0.5:,.0f}</span>
                </div>
                <div style="margin: 4px 0;">
                    <span style="background: #4CAF50; width: 20px; height: 12px; display: inline-block; border: 1px solid #888;"></span>
                    <span style="margin-left: 5px;">{max_val*0.5:,.0f} - {max_val*0.75:,.0f}</span>
                </div>
                <div style="margin: 4px 0;">
                    <span style="background: #2E7D32; width: 20px; height: 12px; display: inline-block; border: 1px solid #888;"></span>
                    <span style="margin-left: 5px;">{max_val*0.75:,.0f}+</span>
                </div>
                <p style="margin: 8px 0 0 0; font-size: 10px; color: #666; font-style: italic;">
                    m³/ano por município
                </p>
            </div>
            '''

            m.get_root().html.add_child(folium.Element(legend_html))
        except Exception as e:
            self.logger.warning(f"Could not add legend: {e}")

    def _get_color_for_value(self, value: float, min_val: float, max_val: float) -> str:
        """Get green gradient color based on value"""
        if max_val > min_val:
            normalized = (value - min_val) / (max_val - min_val)
        else:
            normalized = 0.5

        # Green gradient
        if normalized < 0.25:
            return '#C8E6C9'  # Very light green
        elif normalized < 0.5:
            return '#81C784'  # Light green
        elif normalized < 0.75:
            return '#4CAF50'  # Medium green
        else:
            return '#2E7D32'  # Dark green
