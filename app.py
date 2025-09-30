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

        # Navigation and page selection
        with st.sidebar:
            # Sidebar landmark setup
            st.markdown('<div role="navigation" aria-label="Navegação principal">', unsafe_allow_html=True)

            st.markdown(f"**Versão:** {settings.APP_VERSION}")
            st.markdown("---")

            # Accessibility settings panel
            with st.expander("♿ Acessibilidade", expanded=False):
                accessibility_settings.render_basic_settings()

            st.markdown("---")

            # Accessible page navigation (WCAG 2.4.4, 3.3.2)
            page = accessible_selectbox(
                "Navegar por:",
                options=["Home", "Advanced Maps", "Raster Analysis", "Advanced Satellite Analysis", "Proximity Analysis", "Data Analysis", "Municipality Comparison", "Academic References", "Export & Reports"],
                help_text="Selecione uma página para explorar diferentes recursos",
                aria_label="Navegação principal do aplicativo"
            )

            st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)  # Close navigation landmark

        # Main content area with landmark (WCAG 1.3.1)
        st.markdown('<main role="main" id="main-content" aria-label="Conteúdo principal">', unsafe_allow_html=True)

        # Announce page changes to screen readers (WCAG dynamic content)
        announce_page_change(page)

        # Render selected page with accessibility features
        if page == "Home":
            accessibility_manager.create_accessible_heading("Página Inicial", level=2, id_attr="home-section")
            from src.ui.pages.home import HomePage
            home_page = HomePage()
            home_page.render()

        elif page == "Advanced Maps":
            accessibility_manager.create_accessible_heading("Mapas Interativos Avançados", level=2, id_attr="maps-section")
            st.markdown("Mapeamento profissional multi-camadas com visualização de infraestrutura de biogás")

            from src.ui.components.map_viewer import MapViewer
            map_viewer = MapViewer()
            map_viewer.render()

        elif page == "Raster Analysis":
            accessibility_manager.create_accessible_heading("Análise de Dados Raster e Satélite", level=2, id_attr="raster-section")
            st.markdown("Análise geoespacial avançada usando MapBiomas e imagens de satélite")

            from src.ui.components.raster_map_viewer import create_raster_map_viewer
            from src.data.loaders.database_loader import DatabaseLoader

            # Load municipality data for overlay
            try:
                db_loader = DatabaseLoader()
                municipality_data = db_loader.load_municipalities_data()
                accessibility_manager.announce_to_screen_reader("Dados municipais carregados com sucesso", "polite")
            except Exception as e:
                logger.warning(f"Could not load municipality data: {e}")
                municipality_data = None
                create_accessible_alert("Aviso: Alguns dados municipais podem não estar disponíveis", "warning")

            # Create and render raster map viewer
            raster_viewer = create_raster_map_viewer()
            raster_viewer.render(municipality_data)

        elif page == "Advanced Satellite Analysis":
            accessibility_manager.create_accessible_heading("Análise Avançada de Dados de Satélite", level=2, id_attr="advanced-satellite-section")
            st.markdown("Análise profissional de dados MapBiomas com ferramentas avançadas de visualização e estatísticas")

            from src.ui.pages.advanced_raster_analysis import render_advanced_raster_analysis_page
            render_advanced_raster_analysis_page()

        elif page == "Proximity Analysis":
            accessibility_manager.create_accessible_heading("Análise de Proximidade", level=2, id_attr="proximity-section")

            from src.ui.pages.proximity_analysis import create_proximity_analysis_page
            proximity_page = create_proximity_analysis_page()
            proximity_page.render()

        elif page == "Data Analysis":
            accessibility_manager.create_accessible_heading("Análise de Dados", level=2, id_attr="analysis-section")

            from src.ui.pages.analysis import AnalysisPage
            analysis_page = AnalysisPage()
            analysis_page.render()

        elif page == "Municipality Comparison":
            accessibility_manager.create_accessible_heading("Comparação de Municípios", level=2, id_attr="comparison-section")

            from src.ui.pages.comparison import ComparisonPage
            comparison_page = ComparisonPage()
            comparison_page.render()

        elif page == "Academic References":
            accessibility_manager.create_accessible_heading("Referências Acadêmicas", level=2, id_attr="references-section")

            from src.ui.components.reference_browser import create_reference_browser
            reference_browser = create_reference_browser()
            reference_browser.render()

        elif page == "Export & Reports":
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