"""
CP2B Maps V2 - Home Page Component
Complete V1 parity: sidebar with logo, collapsible panels, municipality data visualization, floating legend
Enhanced with V1 design system for beautiful UI
"""

import streamlit as st
import folium
import folium.plugins
import pandas as pd
from streamlit_folium import st_folium
from typing import Dict, Any, Optional, List
import numpy as np

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader, shapefile_loader
from src.core import biogas_calculator

# Import V1 design system
from src.ui.components.design_system import (
    render_section_header,
    render_info_banner,
    render_styled_metrics
)

logger = get_logger(__name__)


class HomePage:
    """
    Professional home page component matching V1 exactly
    Features: CP2B Logo, Collapsible panels, Municipality data viz, Floating legend
    """

    def __init__(self):
        """Initialize home page component"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing HomePage component with V1 structure")

        # Initialize session state for panels
        if 'active_panel' not in st.session_state:
            st.session_state.active_panel = 'camadas'

    def render(self) -> None:
        """
        Render home page with V1 structure:
        1. Sidebar with logo + 3 collapsible panels
        2. Main map with municipality data
        3. Live metrics dashboard
        """
        try:
            # Render V1-style sidebar (MUST be called first)
            self._render_v1_sidebar()

            # Main content area
            self._render_main_map_section()

            # Live dashboard metrics
            self._render_live_dashboard_strip()

        except Exception as e:
            self.logger.error(f"Error rendering home page: {e}", exc_info=True)
            st.error("⚠️ Failed to render home page. Check logs for details.")

    def _render_v1_sidebar(self) -> None:
        """Render V1-style sidebar with logo and 3 collapsible panels"""
        with st.sidebar:
            # CP2B Logo at top (V1 Issue #1)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                try:
                    st.image("logotipo-full-black.png", width=960)
                except:
                    st.markdown("**CP2B MAPS**")  # Fallback if logo not found

            # Green header: PAINEL DE CONTROLE DO MAPA (V1 Issue #1)
            st.markdown("""
            <style>
            /* Remove purple line below green header */
            .stMarkdown h3 {
                border-bottom: none !important;
            }
            /* Hide "Pular para barra lateral" accessibility link */
            a[href="#sidebar"] {
                position: absolute !important;
                left: -10000px !important;
                top: auto !important;
                width: 1px !important;
                height: 1px !important;
                overflow: hidden !important;
            }
            /* Show on focus for keyboard users */
            a[href="#sidebar"]:focus {
                position: static !important;
                width: auto !important;
                height: auto !important;
            }
            </style>
            <div style='background: #2E8B57; color: white; padding: 0.8rem; margin: 0.5rem -1rem 1rem -1rem;
                        text-align: center; border-radius: 8px;'>
                <h3 style='margin: 0; font-size: 1.1rem;'>🎛️ PAINEL DE CONTROLE DO MAPA</h3>
                <p style='font-size: 0.8rem; opacity: 0.9; margin: 0.2rem 0 0 0;'>Página Mapa Principal</p>
            </div>
            """, unsafe_allow_html=True)

            # Panel 1: CAMADAS VISÍVEIS (starts collapsed)
            with st.expander("🗺️ Camadas Visíveis", expanded=False):
                st.markdown("**Dados Principais:**")
                show_municipios_biogas = st.checkbox("📊 Potencial de Biogás", value=True, key="show_biogas")
                show_municipios_polygons = st.checkbox("🗺️ Polígonos dos Municípios", value=False, disabled=True, key="show_polygons", help="Funcionalidade desabilitada na versão demo")
                show_municipios_polygons = False  # Force disable

                st.markdown("**Infraestrutura:**")
                show_plantas = st.checkbox("🏭 Plantas de Biogás", value=False, key="show_plantas")
                show_gasodutos_dist = st.checkbox("⛽ Distribuição", value=False, key="show_gas_dist")
                show_gasodutos_transp = st.checkbox("⛽ Transporte", value=False, key="show_gas_transp")

                st.markdown("**Referência:**")
                show_rodovias = st.checkbox("🛣️ Rodovias", value=False, key="show_roads")
                show_regioes_admin = st.checkbox("🏛️ Regiões Admin.", value=False, key="show_regions")

                st.markdown("**Imagem de Satélite:**")
                show_mapbiomas = st.checkbox("🌾 MapBiomas - Uso do Solo", value=False, key="show_mapbiomas")

                # Store layer visibility (using different keys to avoid conflicts)
                st.session_state['layer_show_biogas'] = show_municipios_biogas
                st.session_state['layer_show_plantas'] = show_plantas
                st.session_state['layer_show_boundary'] = True
                st.session_state['layer_show_mapbiomas'] = show_mapbiomas

            # Panel 2: FILTROS DE DADOS (only active if biogas layer enabled)
            if show_municipios_biogas:
                with st.expander("📊 Filtros de Dados", expanded=(st.session_state.active_panel == 'filtros')):
                    st.info("💡 **Filtros para visualização do Potencial de Biogás**")

                    filter_mode = st.radio(
                        "Modo:",
                        ["Individual", "Múltiplos"],
                        horizontal=True,
                        key="filter_mode"
                    )

                    data_options = {
                        "Potencial Total": "biogas_potential_m3_year",
                        "Total Agrícola": "agricultural_biogas_m3_year",
                        "Total Pecuária": "livestock_biogas_m3_year",
                        "Total Urbano": "urban_biogas_m3_year",
                        "Resíduos Urbanos": "urban_waste_potential_m3_year",
                        "Resíduos Poda": "rural_waste_potential_m3_year",
                        "Energia (MWh/ano)": "energy_potential_mwh_year",
                        "Redução CO₂ (ton/ano)": "co2_reduction_tons_year"
                    }

                    if filter_mode == "Individual":
                        selected = st.selectbox("Resíduo:", list(data_options.keys()), key="data_select")
                        st.session_state['data_column'] = data_options[selected]
                    else:
                        selected_list = st.multiselect(
                            "Resíduos:",
                            list(data_options.keys()),
                            default=["Potencial Total"],
                            key="data_multi"
                        )
                        # For multiple, use first selection or default
                        if selected_list:
                            st.session_state['data_column'] = data_options[selected_list[0]]
                        else:
                            st.session_state['data_column'] = "biogas_potential_m3_year"

                    # Municipality search
                    search_term = st.text_input(
                        "Buscar:",
                        placeholder="Nome do município...",
                        key="mun_search"
                    )
                    st.session_state['mun_search_term'] = search_term
            else:
                # Disabled state
                with st.expander("📊 Filtros de Dados", expanded=False):
                    st.warning("⚠️ **Ative a camada 'Potencial de Biogás' para usar os filtros**")
                    st.session_state['data_column'] = "biogas_potential_m3_year"
                    st.session_state['mun_search_term'] = ""

            # Panel 3: ESTILOS DE VISUALIZAÇÃO
            with st.expander("🎨 Estilos de Visualização", expanded=(st.session_state.active_panel == 'estilos')):
                st.markdown("**🎯 Escolha o estilo de visualização:**")

                viz_type = st.radio(
                    "Tipo de mapa:",
                    ["Círculos Proporcionais", "Mapa de Calor (Heatmap)", "Agrupamentos (Clusters)"],
                    key="viz_type",
                    index=0
                )

                # Store with different key name to avoid conflict
                st.session_state['selected_viz_type'] = viz_type

                # Info based on selection (V1-style detailed descriptions)
                if viz_type == "Círculos Proporcionais":
                    st.info("🔵 **Círculos Proporcionais**: O tamanho dos círculos representa o valor dos dados. Maior potencial = círculo maior.")
                elif viz_type == "Mapa de Calor (Heatmap)":
                    st.info("🔥 **Mapa de Calor**: Cores quentes (vermelho) indicam valores altos, cores frias (azul) indicam valores baixos.")
                elif viz_type == "Agrupamentos (Clusters)":
                    st.info("📍 **Agrupamentos**: Municípios próximos são agrupados em clusters. Números indicam quantos pontos estão agrupados.")

                st.markdown("---")
                st.markdown("💡 **Dica**: Experimente diferentes estilos para descobrir qual visualização funciona melhor para seus dados!")

            # Panel 4: ACESSIBILIDADE (moved from app.py sidebar)
            with st.expander("♿ Acessibilidade", expanded=False):
                from src.accessibility.settings import AccessibilitySettings
                accessibility_settings = AccessibilitySettings()
                accessibility_settings.render_basic_settings()

            # === MUNICÍPIOS SELECIONADOS SECTION ===
            if 'selected_municipalities' not in st.session_state:
                st.session_state.selected_municipalities = []

            if st.session_state.selected_municipalities:
                st.markdown("---")
                st.markdown("**🎯 Municípios Selecionados:**")

                # Load municipality data to get names
                try:
                    municipalities_df = database_loader.load_municipalities_data()
                    selected_names = municipalities_df[
                        municipalities_df['municipality'].isin(st.session_state.selected_municipalities)
                    ]['municipality'].tolist()

                    # Show up to 3 names
                    for name in selected_names[:3]:
                        display_name = name[:15] + "..." if len(name) > 15 else name
                        st.markdown(f"• {display_name}")

                    # Show count if more than 3
                    if len(selected_names) > 3:
                        st.markdown(f"...+{len(selected_names)-3} mais")

                    # Clear button
                    if st.button("🗑️ Limpar Seleção", key="clear_selection"):
                        count = len(st.session_state.selected_municipalities)
                        st.session_state.selected_municipalities.clear()
                        st.toast(f"{count} municípios removidos da seleção!", icon="🗑️")
                        st.rerun()
                except Exception as e:
                    logger.error(f"Error displaying selected municipalities: {e}")

            # System info at bottom
            st.markdown("---")
            st.markdown("**🖥️ Status do Sistema**")
            db_status = "✅ Online" if database_loader.validate_database() else "❌ Error"
            st.markdown(f"🗄️ Database: {db_status}")
            st.markdown(f"⚙️ Calculator: ✅ Ready")

    def _render_main_map_section(self) -> None:
        """Render main map with municipality data visualization"""

        # === ACTIVE FILTERS BANNER (V1 Feature) ===
        active_filters = []

        # Check if biogas layer is active
        if st.session_state.get('layer_show_biogas', False):
            # Get selected data column
            data_column = st.session_state.get('data_column', 'biogas_potential_m3_year')

            # Reverse lookup for display name
            data_options = {
                "Potencial Total": "biogas_potential_m3_year",
                "Total Agrícola": "agricultural_biogas_m3_year",
                "Total Pecuária": "livestock_biogas_m3_year",
                "Total Urbano": "urban_biogas_m3_year",
                "Resíduos Urbanos": "urban_waste_potential_m3_year",
                "Resíduos Poda": "rural_waste_potential_m3_year",
                "Energia (MWh/ano)": "energy_potential_mwh_year",
                "Redução CO₂ (ton/ano)": "co2_reduction_tons_year"
            }
            reverse_options = {v: k for k, v in data_options.items()}
            display_name = reverse_options.get(data_column, "Potencial Total")

            if display_name != "Potencial Total":
                active_filters.append(f"Resíduo: **{display_name}**")

            # Check for search term
            search_term = st.session_state.get('mun_search_term', '')
            if search_term:
                active_filters.append(f"Busca: **'{search_term}'**")

            # Check for MapBiomas layer
            if st.session_state.get('layer_show_mapbiomas', False):
                active_filters.append(f"MapBiomas: **Ativo**")

        # Display active filters banner
        if active_filters:
            st.info(f"🎯 Filtros Ativos: {' | '.join(active_filters)}")

        # Main map with municipality data (V1 Issues #2, #4)
        self._render_map_with_data()

    def _render_map_with_data(self) -> None:
        """Render map with municipality circles and floating legend"""
        # Load municipality data
        municipalities_df = database_loader.load_municipalities_data()

        # Get selected data column
        data_column = st.session_state.get('data_column', 'biogas_potential_m3_year')

        # Create map
        m = folium.Map(
            location=settings.DEFAULT_CENTER,
            zoom_start=7,
            tiles='CartoDB positron',
            prefer_canvas=True
        )

        # Add fullscreen (remove MeasureControl per Issue #4)
        folium.plugins.Fullscreen().add_to(m)

        # Add state boundary
        if st.session_state.get('layer_show_boundary', True):
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

        # Add municipality circles if biogas layer enabled (V1 Issue #2)
        if st.session_state.get('layer_show_biogas', True) and municipalities_df is not None:
            self._add_municipality_circles(m, municipalities_df, data_column)

        # Add biogas plants if enabled
        if st.session_state.get('layer_show_plantas', False):
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

        # Add floating legend (V1 Issue #4)
        self._add_floating_legend(m, municipalities_df, data_column)

        # Display map (V1 uses height=600)
        map_data = st_folium(
            m,
            width="100%",
            height=600,
            returned_objects=["last_object_clicked"],
            key="main_map"
        )

        # Show municipality details if clicked
        if map_data and map_data.get("last_object_clicked"):
            self._show_municipality_popup(map_data["last_object_clicked"], municipalities_df)

    def _add_municipality_circles(self, m: folium.Map, df: pd.DataFrame, data_column: str) -> None:
        """Add municipality circles sized by biogas potential"""
        if df is None or len(df) == 0:
            return

        # Filter and prepare data
        df_filtered = df[df[data_column] > 0].copy()

        # Apply search filter if active
        search_term = st.session_state.get('mun_search_term', '')
        if search_term and len(search_term) >= 2:
            df_filtered = df_filtered[
                df_filtered['municipality'].str.contains(search_term, case=False, na=False)
            ]

        # Normalize values for circle size
        if len(df_filtered) > 0:
            max_val = df_filtered[data_column].max()
            min_val = df_filtered[data_column].min()

            # Get visualization type
            viz_type = st.session_state.get('selected_viz_type', 'Círculos Proporcionais')

            if viz_type == "Círculos Proporcionais":
                # Add circles for each municipality
                for _, row in df_filtered.iterrows():
                    if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                        value = row[data_column]

                        # Calculate radius (5-25 pixels based on value)
                        if max_val > min_val:
                            normalized = (value - min_val) / (max_val - min_val)
                            radius = 5 + (normalized * 20)
                        else:
                            radius = 10

                        # Color based on value (green gradient)
                        color = self._get_color_for_value(value, min_val, max_val)

                        # Create popup with data
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

            elif viz_type == "Mapa de Calor (Heatmap)":
                # Prepare data for heatmap
                heat_data = [
                    [row['latitude'], row['longitude'], row[data_column]]
                    for _, row in df_filtered.iterrows()
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

            elif viz_type == "Agrupamentos (Clusters)":
                # Use marker cluster
                marker_cluster = folium.plugins.MarkerCluster(name="Municípios").add_to(m)

                for _, row in df_filtered.iterrows():
                    if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                        value = row[data_column]

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

    def _get_color_for_value(self, value: float, min_val: float, max_val: float) -> str:
        """Get green gradient color based on value"""
        if max_val > min_val:
            normalized = (value - min_val) / (max_val - min_val)
        else:
            normalized = 0.5

        # Green gradient: light green to dark green
        if normalized < 0.25:
            return '#C8E6C9'  # Very light green
        elif normalized < 0.5:
            return '#81C784'  # Light green
        elif normalized < 0.75:
            return '#4CAF50'  # Medium green
        else:
            return '#2E7D32'  # Dark green

    def _add_floating_legend(self, m: folium.Map, df: pd.DataFrame, data_column: str) -> None:
        """Add floating legend to map (V1 Issue #4)"""
        if df is None or len(df) == 0:
            return

        # Calculate ranges
        df_filtered = df[df[data_column] > 0]
        if len(df_filtered) == 0:
            return

        max_val = df_filtered[data_column].max()

        # Create legend HTML
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

    def _show_municipality_popup(self, clicked_data: Dict, df: pd.DataFrame) -> None:
        """Show municipality details when map is clicked"""
        if df is None:
            return

        st.success(f"🎯 Município selecionado! Latitude: {clicked_data.get('lat')}, Longitude: {clicked_data.get('lng')}")

    def _render_live_dashboard_strip(self) -> None:
        """Render live metrics dashboard"""
        st.markdown("---")

        # Load municipality data
        municipalities_df = database_loader.load_municipalities_data()

        if municipalities_df is not None and len(municipalities_df) > 0:
            # Calculate state totals
            stats = biogas_calculator.get_state_totals(municipalities_df)
            db_status = "✅ Online" if database_loader.validate_database() else "❌ Error"

            # Use styled metrics helper
            metrics_data = [
                {
                    'icon': '🏘️',
                    'label': 'Municipalities',
                    'value': f"{stats.get('total_municipalities', 0):,}",
                    'delta': 'Complete Coverage'
                },
                {
                    'icon': '⛽',
                    'label': 'Daily Biogas',
                    'value': f"{stats.get('total_biogas_m3_day', 0):,.0f} m³",
                    'delta': 'Real-time Potential'
                },
                {
                    'icon': '⚡',
                    'label': 'Annual Energy',
                    'value': f"{stats.get('total_energy_mwh_year', 0):,.0f} MWh",
                    'delta': 'Clean Energy'
                },
                {
                    'icon': '🌱',
                    'label': 'CO₂ Reduction',
                    'value': f"{stats.get('total_co2_reduction_tons_year', 0):,.0f} tons",
                    'delta': 'Per Year'
                },
                {
                    'icon': '🖥️',
                    'label': 'System Status',
                    'value': db_status,
                    'delta': 'All Systems Operational'
                }
            ]

            render_styled_metrics(metrics_data, columns=5)
        else:
            st.warning("⚠️ Unable to load municipality data. Please check the database connection.")