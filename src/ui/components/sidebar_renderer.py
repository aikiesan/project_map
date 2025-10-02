"""
CP2B Maps V2 - Sidebar Renderer Component
Handles sidebar rendering with logo and collapsible panels
Single Responsibility: Render sidebar UI and collect user selections
"""

import streamlit as st
from typing import Optional
from pathlib import Path

from src.utils.logging_config import get_logger
from src.ui.models.map_config import MapConfig

logger = get_logger(__name__)


class SidebarRenderer:
    """
    Renders V1-style sidebar with logo and collapsible panels
    Returns MapConfig with user selections
    """

    def __init__(self, logo_path: Optional[Path] = None):
        """
        Initialize sidebar renderer

        Args:
            logo_path: Path to CP2B logo image
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logo_path = logo_path or Path("logotipo-full-black.png")

    def render(self) -> MapConfig:
        """
        Render sidebar and return configuration

        Returns:
            MapConfig with user selections
        """
        with st.sidebar:
            # Render logo
            self._render_logo()

            # Render header
            self._render_header()

            # Render panels and collect configuration
            config = self._render_panels()

            return config

    def _render_logo(self) -> None:
        """Render CP2B logo at top of sidebar"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image(str(self.logo_path), width=200)
            except Exception as e:
                self.logger.warning(f"Logo not found: {e}")
                st.markdown("**CP2B MAPS**")  # Fallback

    def _render_header(self) -> None:
        """Render green header with control panel title"""
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
        /* Sidebar white background - match site background */
        section[data-testid="stSidebar"] {
            background-color: white !important;
        }
        section[data-testid="stSidebar"] > div {
            background-color: white !important;
        }
        </style>
        <div style='background: #2E8B57; color: white; padding: 0.8rem; margin: 0.5rem -1rem 1rem -1rem;
                    text-align: center; border-radius: 8px;'>
            <h3 style='margin: 0; font-size: 1.1rem;'>🎛️ PAINEL DE CONTROLE DO MAPA</h3>
            <p style='font-size: 0.8rem; opacity: 0.9; margin: 0.2rem 0 0 0;'>Página Mapa Principal</p>
        </div>
        """, unsafe_allow_html=True)

    def _render_panels(self) -> MapConfig:
        """
        Render collapsible panels and collect user selections

        Returns:
            MapConfig with user selections
        """
        config = MapConfig()

        # Panel 1: Camadas Visíveis
        with st.expander("🗺️ Camadas Visíveis", expanded=False):
            st.markdown("**Dados Principais:**")
            config.show_biogas = st.checkbox("📊 Potencial de Biogás", value=True, key="show_biogas")
            show_polygons = st.checkbox("🗺️ Polígonos dos Municípios", value=False, disabled=True,
                                       key="show_polygons", help="Funcionalidade desabilitada na versão demo")
            config.show_polygons = False  # Force disable

            st.markdown("**Infraestrutura:**")
            config.show_plantas = st.checkbox("🏭 Plantas de Biogás", value=False, key="show_plantas")
            config.show_gasodutos_dist = st.checkbox("⛽ Distribuição", value=False, key="show_gas_dist")
            config.show_gasodutos_transp = st.checkbox("⛽ Transporte", value=False, key="show_gas_transp")

            st.markdown("**Referência:**")
            config.show_rodovias = st.checkbox("🛣️ Rodovias", value=False, key="show_roads")
            config.show_regioes_admin = st.checkbox("🏛️ Regiões Admin.", value=False, key="show_regions")

            st.markdown("**Imagem de Satélite:**")
            config.show_mapbiomas = st.checkbox("🌾 MapBiomas - Uso do Solo", value=False, key="show_mapbiomas")

        # Panel 2: Filtros de Dados
        if config.show_biogas:
            with st.expander("📊 Filtros de Dados", expanded=False):
                st.info("💡 **Filtros para visualização do Potencial de Biogás**")

                config.filter_mode = st.radio(
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

                if config.filter_mode == "Individual":
                    selected = st.selectbox("Resíduo:", list(data_options.keys()), key="data_select")
                    config.data_column = data_options[selected]
                else:
                    selected_list = st.multiselect(
                        "Resíduos:",
                        list(data_options.keys()),
                        default=["Potencial Total"],
                        key="data_multi"
                    )
                    if selected_list:
                        config.data_column = data_options[selected_list[0]]
                        config.selected_data = selected_list

                # Municipality search
                config.search_term = st.text_input(
                    "Buscar:",
                    placeholder="Nome do município...",
                    key="mun_search"
                )
        else:
            # Disabled state
            with st.expander("📊 Filtros de Dados", expanded=False):
                st.warning("⚠️ **Ative a camada 'Potencial de Biogás' para usar os filtros**")

        # Panel 3: Estilos de Visualização
        with st.expander("🎨 Estilos de Visualização", expanded=False):
            st.markdown("**🎯 Escolha o estilo de visualização:**")

            config.viz_type = st.radio(
                "Tipo de mapa:",
                ["Círculos Proporcionais", "Mapa de Preenchimento (Coroplético)",
                 "Mapa de Calor (Heatmap)", "Agrupamentos (Clusters)"],
                key="viz_type",
                index=0
            )

            # Info based on selection
            if config.viz_type == "Círculos Proporcionais":
                st.info("🔵 **Círculos Proporcionais**: O tamanho dos círculos representa o valor dos dados. Maior potencial = círculo maior.")
            elif config.viz_type == "Mapa de Preenchimento (Coroplético)":
                st.info("🗺️ **Mapa Coroplético**: Municípios preenchidos com cores baseadas no valor. Verde claro = baixo, verde escuro = alto.")
            elif config.viz_type == "Mapa de Calor (Heatmap)":
                st.info("🔥 **Mapa de Calor**: Cores quentes (vermelho) indicam valores altos, cores frias (azul) indicam valores baixos.")
            elif config.viz_type == "Agrupamentos (Clusters)":
                st.info("📍 **Agrupamentos**: Municípios próximos são agrupados em clusters. Números indicam quantos pontos estão agrupados.")

            st.markdown("---")
            st.markdown("💡 **Dica**: Experimente diferentes estilos para descobrir qual visualização funciona melhor para seus dados!")

        # Panel 4: Acessibilidade
        with st.expander("♿ Acessibilidade", expanded=False):
            from src.accessibility.settings import AccessibilitySettings
            accessibility_settings = AccessibilitySettings()
            accessibility_settings.render_basic_settings()

        # Panel 5: Informações sobre Substratos
        with st.expander("🧪 Informações sobre Substratos", expanded=False):
            st.info("📚 Dados técnicos sobre substratos para produção de biogás")
            if st.button("📖 Ver Guia Completo de Substratos", use_container_width=True):
                st.session_state['show_substrate_modal'] = True

        return config
