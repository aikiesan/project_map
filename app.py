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

        # V1-Style Tab Navigation (7 tabs - EXACT V1 match)
        tabs = st.tabs([
            "🏠 Mapa Principal",
            "🔍 Explorar Dados",
            "📊 Análises Avançadas",
            "🎯 Análise de Proximidade",
            "🍊 Bagacinho IA",
            "📚 Referências Científicas",
            "ℹ️ Sobre o CP2B Maps"
        ])

        # Add custom CSS for V1-style tabs + Accessibility fixes
        st.markdown("""
            <style>
            /* Import Montserrat font */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

            /* Hide accessibility skip links visually (but keep for screen readers) */
            a[href="#main-content"],
            a[href="#sidebar"],
            a[href^="Pular"] {
                position: absolute !important;
                left: -10000px !important;
                top: auto !important;
                width: 1px !important;
                height: 1px !important;
                overflow: hidden !important;
            }
            /* Show on keyboard focus for accessibility */
            a[href="#main-content"]:focus,
            a[href="#sidebar"]:focus {
                position: static !important;
                width: auto !important;
                height: auto !important;
                background: #2E8B57;
                color: white;
                padding: 0.5rem 1rem;
                z-index: 9999;
            }

            /* Remove purple lines from sidebar headers */
            .stMarkdown h3 {
                border-bottom: none !important;
            }
            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                border-bottom: none !important;
            }

            /* Compact navigation tabs - 60% of V1 size */
            .stTabs [data-baseweb="tab-list"] {
                gap: 7px;
                background-color: #f8f9fa;
                padding: 5px 7px;
                border-radius: 6px;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .stTabs [data-baseweb="tab"] {
                margin-right: 4px;
                padding: 6px 11px;
                border-radius: 5px;
                font-weight: 500;
                transition: all 0.3s ease;
                border: 1px solid transparent;
                font-family: 'Montserrat', system-ui, sans-serif;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e3f2fd;
                transform: translateY(-1px);
                box-shadow: 0 1px 5px rgba(0,0,0,0.15);
            }
            .stTabs [aria-selected="true"] {
                background-color: #2E8B57 !important;
                color: white !important;
                border-color: #2E8B57;
                box-shadow: 0 2px 6px rgba(46,139,87,0.3);
            }
            .stTabs [aria-selected="true"]:hover {
                background-color: #257a4a !important;
            }
            .stTabs [data-baseweb="tab"] p {
                font-size: 11px;
                margin: 0;
                font-weight: 600;
                font-family: 'Montserrat', system-ui, sans-serif;
            }
            </style>
            """, unsafe_allow_html=True)

        # Main content area with landmark (WCAG 1.3.1)
        st.markdown('<main role="main" id="main-content" aria-label="Conteúdo principal">', unsafe_allow_html=True)

        # Render content in tabs
        with tabs[0]:  # Home
            announce_page_change("Home")
            # Hidden heading for accessibility only
            st.markdown('<h2 style="position: absolute; left: -10000px;" id="home-section">Página Inicial</h2>', unsafe_allow_html=True)
            from src.ui.pages.home import HomePage
            home_page = HomePage()
            home_page.render()

        with tabs[1]:  # Explorar Dados (Enhanced Data Explorer with V1 charts)
            announce_page_change("Explorar Dados")
            # Note: Data Explorer has its own styled banner header

            # Enhanced Data Explorer with V1's comprehensive chart library
            from src.ui.pages.data_explorer import create_data_explorer_page
            data_explorer = create_data_explorer_page()
            data_explorer.render()

        with tabs[2]:  # Análises Avançadas (Residue Analysis only)
            announce_page_change("Análises Avançadas")
            # Note: Residue Analysis page has its own styled banner header

            # Direct render - no sub-tabs
            from src.ui.pages.residue_analysis import create_residue_analysis_page
            create_residue_analysis_page()

        with tabs[3]:  # Proximity Analysis (V1 UX with V2 Architecture)
            announce_page_change("Análise de Proximidade")
            # Note: Proximity Analysis page has its own styled banner header

            from src.ui.pages.proximity_analysis import create_proximity_analysis_page
            proximity_page = create_proximity_analysis_page()
            proximity_page.render()

        with tabs[4]:  # Bagacinho AI Assistant
            announce_page_change("Bagacinho IA")
            # Note: Bagacinho page has its own beautiful header, no need for duplicate heading here

            # Import and render Bagacinho assistant
            from src.ui.pages.bagacinho_assistant import render_bagacinho_page
            render_bagacinho_page()

        with tabs[5]:  # References (V1 style)
            announce_page_change("Academic References")
            # Note: References page has its own styled banner header

            from src.ui.pages.references_v1 import render_references_v1_page
            render_references_v1_page()

        with tabs[6]:  # Sobre (About) - V1 Style
            announce_page_change("Sobre o CP2B Maps")
            # Note: About page has its own styled banner header

            from src.ui.pages.about_v1 import render_about_v1_page
            render_about_v1_page()

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