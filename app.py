"""
CP2B Maps V2 - Professional Biogas Analysis Platform
Entry point for Streamlit application with modular architecture
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
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state=settings.SIDEBAR_STATE
)

# Import after page config
from src.utils.logging_config import get_logger
from src.ui.pages.home import HomePage

# Initialize logger
logger = get_logger(__name__)


def main():
    """
    Main application entry point
    Professional structure with error handling
    """
    try:
        # Log application start
        logger.info("Starting CP2B Maps V2 application")

        # Display header
        st.title("🗺️ CP2B Maps V2")
        st.markdown("### Professional Biogas Potential Analysis Platform")

        # Show version info in sidebar
        with st.sidebar:
            st.markdown(f"**Version:** {settings.APP_VERSION}")
            st.markdown("---")

        # Initialize and render home page
        home_page = HomePage()
        home_page.render()

        # Log successful render
        logger.debug("Application rendered successfully")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error("⚠️ An error occurred. Please check the logs for details.")
        st.exception(e)


if __name__ == "__main__":
    main()