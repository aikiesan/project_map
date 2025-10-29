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

# Import new usability components (Phase 1)
from src.ui.components.help_fab import render_help_fab, render_aria_live_region, announce_to_screen_reader
from src.ui.components.onboarding_modal import show_onboarding_modal

# CRITICAL: Import all page modules at startup to prevent re-imports on tab rendering
# This eliminates multiple reruns caused by lazy imports inside tab blocks
from src.ui.pages.welcome_home import WelcomeHomePage
from src.ui.pages.home import HomePage
from src.ui.pages.data_explorer import create_data_explorer_page
from src.ui.pages.residue_analysis import create_residue_analysis_page
from src.ui.pages.proximity_analysis import create_proximity_analysis_page
from src.ui.pages.bagacinho_assistant import render_bagacinho_page
from src.ui.pages.references_v1 import render_references_v1_page
# TEMPORARILY DISABLED: Dados Validados page needs further development
# from src.ui.pages.validated_research import create_validated_research_page
from src.ui.pages.about_v1 import render_about_v1_page

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


# ============================================================================
# SESSION STATE INITIALIZATION - Runs only once per session
# ============================================================================

def _get_current_page_name() -> str:
    """Get current page name based on active tab (helper for contextual help)"""
    # Initialize if not exists
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Início"

    return st.session_state.get('current_tab', "Início")


def init_session_state():
    """Initialize session state variables only once"""
    if 'app_initialized' not in st.session_state:
        logger.info("🚀 First session initialization - Starting app...")

        # CRITICAL: Load CSS ONCE at session initialization
        # This prevents multiple reruns caused by module-level CSS loading
        logger.info("Loading global CSS...")
        load_global_css()

        st.session_state.app_initialized = True
        st.session_state.accessibility_manager = initialize_accessibility()

        # Initialize scenario system
        logger.info("Initializing scenario system...")
        init_scenario_state()

        # CRITICAL: Initialize OBJECT-BASED page instances ONCE and cache in session state
        # Prevents creating new page objects on every rerun
        # Note: Functional pages (that render on creation) are not cached here
        logger.info("Initializing cached page instances...")
        st.session_state.welcome_page = WelcomeHomePage()
        st.session_state.map_page = HomePage()
        st.session_state.data_explorer_page = create_data_explorer_page()
        st.session_state.proximity_analysis_page = create_proximity_analysis_page()
        logger.info("✅ Page instances cached successfully - App initialization complete")
    else:
        logger.debug("App already initialized - skipping initialization")
    
    # Defensive initialization: ensure page instances exist even if session state was partially cleared
    if 'welcome_page' not in st.session_state:
        logger.warning("welcome_page missing from session state - reinitializing")
        st.session_state.welcome_page = WelcomeHomePage()

    if 'map_page' not in st.session_state:
        logger.warning("map_page missing from session state - reinitializing")
        st.session_state.map_page = HomePage()

    if 'data_explorer_page' not in st.session_state:
        logger.warning("data_explorer_page missing from session state - reinitializing")
        st.session_state.data_explorer_page = create_data_explorer_page()

    if 'proximity_analysis_page' not in st.session_state:
        logger.warning("proximity_analysis_page missing from session state - reinitializing")
        st.session_state.proximity_analysis_page = create_proximity_analysis_page()


def main():
    """
    Main application entry point with WCAG 2.1 Level A compliance
    Professional structure with accessibility and error handling
    """
    try:
        # Track script executions for debugging reloads
        if 'script_run_count' not in st.session_state:
            st.session_state.script_run_count = 0
        st.session_state.script_run_count += 1
        logger.info(f"📊 Script execution #{st.session_state.script_run_count}")

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

        # ARIA live region for accessibility announcements (WCAG 4.1.3)
        render_aria_live_region()

        # Show onboarding modal for first-time users
        show_onboarding_modal()

        # Render Help FAB in sidebar
        current_page = _get_current_page_name()
        render_help_fab(current_page=current_page, show_bagacinho_link=True)

        # Language identification (WCAG 3.1.1)
        st.markdown('<div lang="pt-BR">', unsafe_allow_html=True)

        # V1-Style Tab Navigation (8 tabs - Dados Validados temporarily disabled)
        # CSS loaded at startup via st.components.v1.html, so tabs render with correct styles immediately
        tabs = st.tabs([
            "🏠 Início",
            "🗺️ Mapa Principal",
            "🔍 Explorar Dados",
            "📊 Análises Avançadas",
            "🎯 Análise de Proximidade",
            "🍊 Bagacinho IA",
            "📚 Referências Científicas",
            "ℹ️ Sobre o CP2B Maps"
        ])

        # Main content area with landmark (WCAG 1.3.1)
        st.markdown('<main role="main" id="main-content" aria-label="Conteúdo principal">', unsafe_allow_html=True)

        # Render content in tabs (using cached page instances from session state)
        with tabs[0]:  # Welcome Home
            st.session_state.current_tab = "Início"
            # Hidden heading for accessibility only
            st.markdown('<h2 style="position: absolute; left: -10000px;" id="welcome-section">Página Inicial</h2>', unsafe_allow_html=True)
            # Announce page change to screen readers
            announce_to_screen_reader("Navegando para Página Inicial", priority="polite")

            # Use cached welcome page instance
            st.session_state.welcome_page.render()

        with tabs[1]:  # Map Page
            st.session_state.current_tab = "Mapa Principal"
            # Hidden heading for accessibility only
            st.markdown('<h2 style="position: absolute; left: -10000px;" id="map-section">Mapa Principal</h2>', unsafe_allow_html=True)
            announce_to_screen_reader("Navegando para Mapa Principal", priority="polite")

            # Use cached map page instance
            st.session_state.map_page.render()

        with tabs[2]:  # Explorar Dados (Enhanced Data Explorer with V1 charts)
            st.session_state.current_tab = "Explorar Dados"
            announce_to_screen_reader("Navegando para Explorar Dados", priority="polite")
            # Note: Data Explorer has its own styled banner header
            st.session_state.data_explorer_page.render()

        with tabs[3]:  # Análises Avançadas (Residue Analysis only)
            st.session_state.current_tab = "Análises Avançadas"
            announce_to_screen_reader("Navegando para Análises Avançadas", priority="polite")
            # Note: Residue Analysis page has its own styled banner header
            # Functional page - renders on creation
            create_residue_analysis_page()

        with tabs[4]:  # Proximity Analysis (V1 UX with V2 Architecture)
            st.session_state.current_tab = "Análise de Proximidade"
            announce_to_screen_reader("Navegando para Análise de Proximidade", priority="polite")
            # Note: Proximity Analysis page has its own styled banner header
            st.session_state.proximity_analysis_page.render()

        with tabs[5]:  # Bagacinho AI Assistant
            st.session_state.current_tab = "Bagacinho IA"
            announce_to_screen_reader("Navegando para Bagacinho IA", priority="polite")
            # Note: Bagacinho page has its own beautiful header
            render_bagacinho_page()

        with tabs[6]:  # References (V1 style)
            st.session_state.current_tab = "Referências Científicas"
            announce_to_screen_reader("Navegando para Referências Científicas", priority="polite")
            # Note: References page has its own styled banner header
            render_references_v1_page()

        # TEMPORARILY DISABLED: Dados Validados page needs further development
        # with tabs[7]:  # Validated Research Data (NEW)
        #     # Note: Validated Research page has its own styled banner header
        #     create_validated_research_page()

        with tabs[7]:  # Sobre (About) - V1 Style
            st.session_state.current_tab = "Sobre"
            announce_to_screen_reader("Navegando para Sobre o CP2B Maps", priority="polite")
            # Note: About page has its own styled banner header
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