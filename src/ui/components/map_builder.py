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
from src.data.loaders.raster_loader import RasterLoader
from src.data.loaders.mapbiomas_loader import MapBiomasLoader

logger = get_logger(__name__)


class MapBuilder:
    """
    Builds Folium maps with municipality data and layers
    Handles all map visualization logic
    """

    def __init__(self):
        """Initialize map builder"""
        self.logger = get_logger(self.__class__.__name__)
        self.raster_loader = RasterLoader()
        self.mapbiomas_loader = MapBiomasLoader()

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

            # Add gas pipelines if enabled
            if config.show_gasodutos_dist or config.show_gasodutos_transp:
                self._add_pipelines(m, config)

            # Add MapBiomas raster if enabled
            if config.show_mapbiomas:
                self._add_mapbiomas_layer(m)

            # Add infrastructure layers if enabled
            if config.show_etes:
                self._add_etes(m)

            if config.show_power_substations:
                self._add_power_substations(m)

            if config.show_transmission_lines:
                self._add_transmission_lines(m)

            if config.show_apps_hidrography:
                self._add_apps_hidrography(m)

            if config.show_highways:
                self._add_highways(m)

            if config.show_urban_areas:
                self._add_urban_areas(m)

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
        elif config.viz_type == "Mapa de Preenchimento (Coroplético)":
            self._add_choropleth(m, df_filtered, config)

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

    def _add_pipelines(self, m: folium.Map, config: MapConfig) -> None:
        """Add gas pipeline networks"""
        try:
            pipelines_gdf = shapefile_loader.load_gas_pipelines("both")

            if pipelines_gdf is not None:
                folium.GeoJson(
                    pipelines_gdf,
                    style_function=lambda feature: {
                        'color': '#FF6B35',
                        'weight': 2,
                        'opacity': 0.8,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['TIPO'],
                        aliases=['Tipo:'],
                        localize=True
                    )
                ).add_to(m)
                self.logger.debug("Added gas pipelines to map")
        except Exception as e:
            self.logger.warning(f"Could not add pipelines: {e}")

    def _add_mapbiomas_layer(self, m: folium.Map) -> None:
        """Add MapBiomas agricultural raster layer"""
        try:
            from pathlib import Path

            # Path to MapBiomas raster
            raster_path = Path("data/rasters/mapbiomas_agropecuaria_sp_2024.tif")

            if not raster_path.exists():
                self.logger.warning(f"MapBiomas raster not found: {raster_path}")
                return

            # Load raster data
            data, metadata = self.raster_loader.load_raster(
                str(raster_path),
                max_size=settings.MAX_RASTER_SIZE
            )

            if data is None or metadata is None:
                self.logger.warning("Failed to load MapBiomas raster data")
                return

            # All agricultural classes auto-selected
            all_agri_classes = [15, 18, 19, 39, 20, 40, 62, 41, 36, 46, 47, 48, 9, 21]

            # Create overlay
            overlay = self.mapbiomas_loader.create_folium_overlay(
                data, metadata,
                selected_classes=all_agri_classes,
                opacity=0.6
            )

            if overlay:
                # Create feature group
                raster_group = folium.FeatureGroup(
                    name="MapBiomas - Agropecuária",
                    show=True
                )
                overlay.add_to(raster_group)
                raster_group.add_to(m)

                # Add legend
                legend_html = self.mapbiomas_loader.create_legend_html(
                    selected_classes=all_agri_classes,
                    language='pt'
                )
                m.get_root().html.add_child(folium.Element(legend_html))

                self.logger.debug("Added MapBiomas layer to map")
        except Exception as e:
            self.logger.warning(f"Could not add MapBiomas layer: {e}")

    def _add_etes(self, m: folium.Map) -> None:
        """Add wastewater treatment plants (ETEs) to map"""
        try:
            etes = shapefile_loader.load_etes()
            if etes is not None:
                for _, ete in etes.iterrows():
                    folium.CircleMarker(
                        location=[ete.geometry.y, ete.geometry.x],
                        radius=5,
                        popup="ETE - Estação de Tratamento de Esgoto",
                        tooltip="Estação de Tratamento",
                        color='#1E90FF',
                        fillColor='#4169E1',
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)
                self.logger.debug("Added ETEs to map")
        except Exception as e:
            self.logger.warning(f"Could not add ETEs: {e}")

    def _add_power_substations(self, m: folium.Map) -> None:
        """Add power substations to map"""
        try:
            substations = shapefile_loader.load_power_substations()
            if substations is not None:
                for _, sub in substations.iterrows():
                    folium.CircleMarker(
                        location=[sub.geometry.y, sub.geometry.x],
                        radius=4,
                        popup="Subestação de Energia",
                        tooltip="Subestação",
                        color='#FFD700',
                        fillColor='#FFA500',
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)
                self.logger.debug("Added power substations to map")
        except Exception as e:
            self.logger.warning(f"Could not add power substations: {e}")

    def _add_transmission_lines(self, m: folium.Map) -> None:
        """Add electricity transmission lines to map"""
        try:
            lines = shapefile_loader.load_transmission_lines()
            if lines is not None:
                folium.GeoJson(
                    lines,
                    style_function=lambda feature: {
                        'color': '#DC143C',
                        'weight': 2,
                        'opacity': 0.7,
                    },
                    tooltip="Linha de Transmissão"
                ).add_to(m)
                self.logger.debug("Added transmission lines to map")
        except Exception as e:
            self.logger.warning(f"Could not add transmission lines: {e}")

    def _add_apps_hidrography(self, m: folium.Map) -> None:
        """Add APPs and hydrography to map"""
        try:
            apps = shapefile_loader.load_apps_hidrography()
            if apps is not None:
                folium.GeoJson(
                    apps,
                    style_function=lambda feature: {
                        'color': '#00CED1',
                        'weight': 1,
                        'opacity': 0.6,
                        'fillColor': '#87CEEB',
                        'fillOpacity': 0.3,
                    },
                    tooltip="APPs e Hidrografia"
                ).add_to(m)
                self.logger.debug("Added APPs and hydrography to map")
        except Exception as e:
            self.logger.warning(f"Could not add APPs/hydrography: {e}")

    def _add_highways(self, m: folium.Map) -> None:
        """Add state highways to map"""
        try:
            highways = shapefile_loader.load_highways()
            if highways is not None:
                folium.GeoJson(
                    highways,
                    style_function=lambda feature: {
                        'color': '#696969',
                        'weight': 2,
                        'opacity': 0.7,
                    },
                    tooltip="Rodovia Estadual"
                ).add_to(m)
                self.logger.debug("Added highways to map")
        except Exception as e:
            self.logger.warning(f"Could not add highways: {e}")

    def _add_urban_areas(self, m: folium.Map) -> None:
        """Add urban areas to map"""
        try:
            urban = shapefile_loader.load_urban_areas()
            if urban is not None:
                folium.GeoJson(
                    urban,
                    style_function=lambda feature: {
                        'color': '#A9A9A9',
                        'weight': 1,
                        'opacity': 0.5,
                        'fillColor': '#D3D3D3',
                        'fillOpacity': 0.3,
                    },
                    tooltip="Área Urbana"
                ).add_to(m)
                self.logger.debug("Added urban areas to map")
        except Exception as e:
            self.logger.warning(f"Could not add urban areas: {e}")

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

    def _add_choropleth_legend(self,
                               m: folium.Map,
                               df: pd.DataFrame,
                               config: MapConfig) -> None:
        """Add compact legend for choropleth map"""
        try:
            df_filtered = df[df[config.data_column] > 0]
            if len(df_filtered) == 0:
                return

            min_val = df_filtered[config.data_column].min()
            max_val = df_filtered[config.data_column].max()
            quartile_1 = df_filtered[config.data_column].quantile(0.25)
            quartile_2 = df_filtered[config.data_column].quantile(0.50)
            quartile_3 = df_filtered[config.data_column].quantile(0.75)

            legend_html = f'''
            <div style="position: fixed;
                        bottom: 50px; right: 50px; width: 220px; height: auto;
                        background-color: white; z-index:9999; font-size:12px;
                        border-radius: 8px; padding: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        border: 2px solid #2E8B57;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #2E8B57; font-size: 13px;">
                    🗺️ {config.get_data_column_display_name()}
                </p>
                <div style="margin: 5px 0;">
                    <span style="background: #ffffcc; width: 24px; height: 16px; display: inline-block; border: 1px solid #888; border-radius: 2px;"></span>
                    <span style="margin-left: 5px; font-size: 11px;">{min_val:,.0f} - {quartile_1:,.0f}</span>
                </div>
                <div style="margin: 5px 0;">
                    <span style="background: #c7e9c0; width: 24px; height: 16px; display: inline-block; border: 1px solid #888; border-radius: 2px;"></span>
                    <span style="margin-left: 5px; font-size: 11px;">{quartile_1:,.0f} - {quartile_2:,.0f}</span>
                </div>
                <div style="margin: 5px 0;">
                    <span style="background: #74c476; width: 24px; height: 16px; display: inline-block; border: 1px solid #888; border-radius: 2px;"></span>
                    <span style="margin-left: 5px; font-size: 11px;">{quartile_2:,.0f} - {quartile_3:,.0f}</span>
                </div>
                <div style="margin: 5px 0;">
                    <span style="background: #238b45; width: 24px; height: 16px; display: inline-block; border: 1px solid #888; border-radius: 2px;"></span>
                    <span style="margin-left: 5px; font-size: 11px;">{quartile_3:,.0f} - {max_val:,.0f}</span>
                </div>
                <div style="margin: 5px 0;">
                    <span style="background: #00441b; width: 24px; height: 16px; display: inline-block; border: 1px solid #888; border-radius: 2px;"></span>
                    <span style="margin-left: 5px; font-size: 11px;">{max_val:,.0f}+</span>
                </div>
                <p style="margin: 10px 0 0 0; font-size: 10px; color: #666; font-style: italic;">
                    m³/ano por município
                </p>
            </div>
            '''

            m.get_root().html.add_child(folium.Element(legend_html))
        except Exception as e:
            self.logger.warning(f"Could not add choropleth legend: {e}")

    def _add_choropleth(self,
                       m: folium.Map,
                       df: pd.DataFrame,
                       config: MapConfig) -> None:
        """Add choropleth (filled polygons) visualization"""
        try:
            # Load municipality polygons
            municipalities_gdf = shapefile_loader.load_municipalities()

            if municipalities_gdf is None:
                self.logger.warning("Municipality polygons not available for choropleth")
                # Fallback to circle markers
                self._add_circle_markers(m, df, config)
                return

            # Create GeoJSON for choropleth
            import json
            geojson_data = json.loads(municipalities_gdf.to_json())

            # Create choropleth (without automatic legend to avoid crowding)
            choropleth = folium.Choropleth(
                geo_data=geojson_data,
                name='Potencial de Biogás',
                data=df,
                columns=['municipality', config.data_column],
                key_on='feature.properties.NM_MUN',  # Adjust based on actual property name in shapefile
                fill_color='YlGn',  # Yellow to Green color scheme
                fill_opacity=0.7,
                line_opacity=0.3,
                legend_name=None,  # Disable automatic legend (we'll add custom one)
                nan_fill_color='lightgray',
                nan_fill_opacity=0.2
            ).add_to(m)

            # Remove the automatic color legend created by Choropleth
            for child in m._children.values():
                if hasattr(child, '_name') and 'color_map' in child._name:
                    m._children.pop(list(m._children.keys())[list(m._children.values()).index(child)])
                    break

            # Add tooltips with municipality info
            folium.GeoJson(
                geojson_data,
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'transparent',
                    'weight': 0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['NM_MUN'],  # Adjust based on actual property name
                    aliases=['Município:'],
                    localize=True
                )
            ).add_to(m)

            # Add custom compact legend for choropleth
            self._add_choropleth_legend(m, df, config)

            self.logger.info("Choropleth map created successfully")

        except Exception as e:
            self.logger.error(f"Error creating choropleth: {e}", exc_info=True)
            # Fallback to circle markers
            self._add_circle_markers(m, df, config)

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
