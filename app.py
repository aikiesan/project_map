"""
CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas
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
    page_title="CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas | WCAG 2.1 Nível A",
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state=settings.SIDEBAR_STATE
)

# Preload Montserrat font to prevent FOUT (Flash of Unstyled Text)
# This ensures font is ready before first render, eliminating layout shifts
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

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

# Import scenario system
from config.scenario_config import init_scenario_state

# Initialize logger
logger = get_logger(__name__)


# ============================================================================
# CACHED INITIALIZATION - Prevents double loading
# ============================================================================

@st.cache_resource
def initialize_accessibility():
    """Initialize accessibility manager once and cache it"""
    logger.info("Initializing accessibility manager (cached)")
    return AccessibilityManager()


@st.cache_resource
def initialize_global_resources():
    """Initialize global resources once"""
    logger.info("Loading global CSS (cached)")
    load_global_css()
    return True


@st.cache_resource
def load_tab_navigation_css():
    """Load tab navigation CSS once (cached)"""
    st.markdown("""
        <style>
        /* Montserrat font already preloaded via <link> in <head> */

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


# ============================================================================
# SESSION STATE INITIALIZATION - Runs only once per session
# ============================================================================

def init_session_state():
    """Initialize session state variables only once"""
    if 'app_initialized' not in st.session_state:
        logger.info("First session initialization")
        st.session_state.app_initialized = True
        st.session_state.accessibility_manager = initialize_accessibility()
        st.session_state.global_resources_loaded = initialize_global_resources()
        # Initialize scenario system
        init_scenario_state()
        # Load tab navigation CSS once
        load_tab_navigation_css()


def main():
    """
    Main application entry point with WCAG 2.1 Level A compliance
    Professional structure with accessibility and error handling
    """
    try:
        # Initialize session state once
        init_session_state()

        # Get cached accessibility manager
        accessibility_manager = st.session_state.accessibility_manager

        # Initialize accessibility features (WCAG Level A requirements)
        accessibility_manager.initialize()

        # Log application start
        logger.info("Starting CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas with accessibility features")

        # V1-style beautiful green gradient header
        render_green_header()

        # Language identification (WCAG 3.1.1)
        st.markdown('<div lang="pt-BR">', unsafe_allow_html=True)

        # V1-Style Tab Navigation (8 tabs - Added Validated Research Data)
        tabs = st.tabs([
            "🏠 Mapa Principal",
            "🔍 Explorar Dados",
            "📊 Análises Avançadas",
            "🎯 Análise de Proximidade",
            "🍊 Bagacinho IA",
            "📚 Referências Científicas",
            "🔬 Dados Validados",
            "ℹ️ Sobre o CP2B Maps"
        ])

        # CSS already loaded via cached function (load_tab_navigation_css)

        # Main content area with landmark (WCAG 1.3.1)
        st.markdown('<main role="main" id="main-content" aria-label="Conteúdo principal">', unsafe_allow_html=True)

        # Render content in tabs (with loading indicator for Home tab)
        with tabs[0]:  # Home
            # Hidden heading for accessibility only
            st.markdown('<h2 style="position: absolute; left: -10000px;" id="home-section">Página Inicial</h2>', unsafe_allow_html=True)

            # Show loading spinner for initial map load
            with st.spinner('🗺️ Carregando mapa e dados...'):
                from src.ui.pages.home import HomePage
                home_page = HomePage()
                home_page.render()

        with tabs[1]:  # Explorar Dados (Enhanced Data Explorer with V1 charts)
            # Note: Data Explorer has its own styled banner header
            with st.spinner('📊 Carregando explorador de dados...'):
                from src.ui.pages.data_explorer import create_data_explorer_page
                data_explorer = create_data_explorer_page()
                data_explorer.render()

        with tabs[2]:  # Análises Avançadas (Residue Analysis only)
            # Note: Residue Analysis page has its own styled banner header
            with st.spinner('📈 Carregando análises avançadas...'):
                from src.ui.pages.residue_analysis import create_residue_analysis_page
                create_residue_analysis_page()

        with tabs[3]:  # Proximity Analysis (V1 UX with V2 Architecture)
            # Note: Proximity Analysis page has its own styled banner header
            with st.spinner('🎯 Carregando análise de proximidade...'):
                from src.ui.pages.proximity_analysis import create_proximity_analysis_page
                proximity_page = create_proximity_analysis_page()
                proximity_page.render()

        with tabs[4]:  # Bagacinho AI Assistant
            # Note: Bagacinho page has its own beautiful header, no need for duplicate heading here
            with st.spinner('🍊 Carregando Bagacinho IA...'):
                from src.ui.pages.bagacinho_assistant import render_bagacinho_page
                render_bagacinho_page()

        with tabs[5]:  # References (V1 style)
            # Note: References page has its own styled banner header
            from src.ui.pages.references_v1 import render_references_v1_page
            render_references_v1_page()

        with tabs[6]:  # Validated Research Data (NEW)
            # Note: Validated Research page has its own styled banner header
            from src.ui.pages.validated_research import create_validated_research_page
            create_validated_research_page()

        with tabs[7]:  # Sobre (About) - V1 Style
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