"""
CP2B Maps V2 - Professional Biogas Analysis Platform
Entry point for Streamlit application with modular architecture
WCAG 2.1 Level A compliant accessibility implementation
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure Streamlit page (must be first Streamlit command)
import streamlit as st
from config.settings import settings

st.set_page_config(
    page_title="CP2B Maps V2 - Análise de Potencial de Biogás | WCAG 2.1 Nível A",
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state=settings.SIDEBAR_STATE
)

# Import after page config
from src.utils.logging_config import get_logger
from src.ui.pages.home import HomePage

# Import design system for V1 styling
from src.ui.components.design_system import render_green_header, load_global_css

# Import accessibility components
from src.accessibility.core import AccessibilityManager
from src.accessibility.settings import AccessibilitySettings
from src.accessibility.components.accessible_components import (
    accessible_button,
    accessible_selectbox,
    announce_page_change,
    create_accessible_alert
)

# Initialize logger and accessibility
logger = get_logger(__name__)
accessibility_manager = AccessibilityManager()
accessibility_settings = AccessibilitySettings()


def main():
    """
    Main application entry point with WCAG 2.1 Level A compliance
    Professional structure with accessibility and error handling
    """
    try:
        # Initialize accessibility features (WCAG Level A requirements)
        accessibility_manager.initialize()

        # Load global CSS for V1 visual parity
        load_global_css()

        # Log application start
        logger.info("Starting CP2B Maps V2 application with accessibility features")

        # V1-style beautiful green gradient header
        render_green_header()

        # Language identification (WCAG 3.1.1)
        st.markdown('<div lang="pt-BR">', unsafe_allow_html=True)

        # V1-Style Tab Navigation
        tabs = st.tabs([
            "🏠 Mapa Principal",
            "🗺️ Mapas Avançados",
            "🛰️ Análise de Satélite",
            "🎯 Análise de Proximidade",
            "📊 Análise de Dados",
            "🔄 Comparação",
            "📚 Referências",
            "📥 Exportar"
        ])

        # Add custom CSS for V1-style tabs
        st.markdown("""
            <style>
            /* Improve main navigation tabs - V1 Style */
            .stTabs [data-baseweb="tab-list"] {
                gap: 12px;
                background-color: #f8f9fa;
                padding: 8px 12px;
                border-radius: 10px;
                margin-bottom: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stTabs [data-baseweb="tab"] {
                margin-right: 6px;
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e3f2fd;
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }
            .stTabs [aria-selected="true"] {
                background-color: #2E8B57 !important;
                color: white !important;
                border-color: #2E8B57;
                box-shadow: 0 3px 10px rgba(46,139,87,0.3);
            }
            .stTabs [aria-selected="true"]:hover {
                background-color: #257a4a !important;
            }
            .stTabs [data-baseweb="tab"] p {
                font-size: 14px;
                margin: 0;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)

        # Main content area with landmark (WCAG 1.3.1)
        st.markdown('<main role="main" id="main-content" aria-label="Conteúdo principal">', unsafe_allow_html=True)

        # Render content in tabs
        with tabs[0]:  # Home
            announce_page_change("Home")
            accessibility_manager.create_accessible_heading("Página Inicial", level=2, id_attr="home-section")
            from src.ui.pages.home import HomePage
            home_page = HomePage()
            home_page.render()

        with tabs[1]:  # Advanced Maps
            announce_page_change("Advanced Maps")
            accessibility_manager.create_accessible_heading("Mapas Interativos Avançados", level=2, id_attr="maps-section")
            st.markdown("Mapeamento profissional multi-camadas com visualização de infraestrutura de biogás")

            from src.ui.components.map_viewer import MapViewer
            map_viewer = MapViewer()
            map_viewer.render()

        with tabs[2]:  # Satellite Analysis
            announce_page_change("Advanced Satellite Analysis")
            accessibility_manager.create_accessible_heading("Análise Avançada de Dados de Satélite", level=2, id_attr="advanced-satellite-section")
            st.markdown("Análise profissional de dados MapBiomas com ferramentas avançadas de visualização e estatísticas")

            from src.ui.pages.advanced_raster_analysis import render_advanced_raster_analysis_page
            render_advanced_raster_analysis_page()

        with tabs[3]:  # Proximity Analysis
            announce_page_change("Proximity Analysis")
            accessibility_manager.create_accessible_heading("Análise de Proximidade", level=2, id_attr="proximity-section")

            from src.ui.pages.proximity_analysis import create_proximity_analysis_page
            proximity_page = create_proximity_analysis_page()
            proximity_page.render()

        with tabs[4]:  # Data Analysis
            announce_page_change("Data Analysis")
            accessibility_manager.create_accessible_heading("Análise de Dados", level=2, id_attr="analysis-section")

            from src.ui.pages.analysis import AnalysisPage
            analysis_page = AnalysisPage()
            analysis_page.render()

        with tabs[5]:  # Comparison
            announce_page_change("Municipality Comparison")
            accessibility_manager.create_accessible_heading("Comparação de Municípios", level=2, id_attr="comparison-section")

            from src.ui.pages.comparison import ComparisonPage
            comparison_page = ComparisonPage()
            comparison_page.render()

        with tabs[6]:  # References
            announce_page_change("Academic References")
            accessibility_manager.create_accessible_heading("Referências Acadêmicas", level=2, id_attr="references-section")

            from src.ui.components.reference_browser import create_reference_browser
            reference_browser = create_reference_browser()
            reference_browser.render()

        with tabs[7]:  # Export
            announce_page_change("Export & Reports")
            accessibility_manager.create_accessible_heading("Exportação e Relatórios", level=2, id_attr="export-section")

            from src.ui.components.export import Export
            from src.ui.components.charts import Charts

            # Load data for export
            try:
                from src.data import database_loader
                data = database_loader.load_municipalities_data()
                accessibility_manager.announce_to_screen_reader("Dados carregados para exportação", "polite")
            except Exception as e:
                logger.error(f"Error loading data for export: {e}")
                create_accessible_alert("Erro: Não foi possível carregar dados para exportação", "error")
                data = None

            if data is not None:
                # Export functionality
                export_component = Export()
                export_component.render(data)

                # Add some charts for the export page
                st.markdown("---")
                charts_component = Charts()
                charts_component.render()

        # Close main content landmark
        st.markdown('</main>', unsafe_allow_html=True)

        # Close language identification
        st.markdown('</div>', unsafe_allow_html=True)

        # Log successful render
        logger.debug("Application rendered successfully with accessibility features")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)

        # Accessible error handling (WCAG 3.3.1)
        create_accessible_alert(
            "Ocorreu um erro na aplicação. Por favor, tente recarregar a página ou entre em contato com o suporte.",
            alert_type="error"
        )

        # Announce error to screen readers
        try:
            accessibility_manager.announce_to_screen_reader(
                "Erro na aplicação: Por favor, recarregue a página",
                urgency="assertive"
            )
        except:
            pass  # Fallback if accessibility manager fails

        # Technical details in expander for debugging
        with st.expander("🔧 Detalhes Técnicos (para desenvolvedores)"):
            st.exception(e)


if __name__ == "__main__":
    main()