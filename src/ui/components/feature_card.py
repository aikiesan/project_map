"""
CP2B Maps - Feature Card Component
Renders interactive feature cards with modal details
"""

import streamlit as st
from typing import List, Dict
from src.utils.logging_config import get_logger
from src.ui.components.feature_modal import show_feature_modal

logger = get_logger(__name__)


def render_feature_grid(features: List[Dict], columns: int = 3) -> None:
    """
    Render a grid of feature cards

    Args:
        features: List of feature dictionaries with icon, title, description, tool_key
        columns: Number of columns in the grid (default: 3)
    """
    try:
        # Create columns
        cols = st.columns(columns)

        for idx, feature in enumerate(features):
            col_idx = idx % columns

            with cols[col_idx]:
                render_feature_card(
                    icon=feature["icon"],
                    title=feature["title"],
                    description=feature["description"],
                    tool_key=feature["tool_key"]
                )

    except Exception as e:
        logger.error(f"Error rendering feature grid: {e}", exc_info=True)
        st.error("Erro ao carregar os cards de ferramentas.")


def render_feature_card(icon: str, title: str, description: str, tool_key: str) -> None:
    """
    Render a single feature card with modal trigger

    Args:
        icon: Emoji icon for the feature
        title: Feature title
        description: Short description
        tool_key: Unique key for feature modal
    """
    try:
        # Card container
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 1.5rem;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    border: 1px solid #e9ecef; margin-bottom: 1.5rem;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    height: 100%;'>
            <div style='font-size: 3rem; text-align: center; margin-bottom: 1rem;'>
                {icon}
            </div>
            <h3 style='color: #2c3e50; font-weight: 600; margin: 0 0 0.75rem 0;
                       font-size: 1.3rem; text-align: center;'>
                {title}
            </h3>
            <p style='color: #6c757d; font-size: 0.95rem; line-height: 1.6;
                      text-align: center; margin-bottom: 1.25rem;'>
                {description}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Modal trigger button
        if st.button(
            "Ver detalhes",
            key=f"btn_{tool_key}",
            use_container_width=True
        ):
            show_feature_modal(tool_key)

    except Exception as e:
        logger.error(f"Error rendering feature card '{title}': {e}", exc_info=True)
        st.error(f"Erro ao carregar card: {title}")
