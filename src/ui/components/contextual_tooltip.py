"""
CP2B Maps - Contextual Tooltip Component
WCAG 2.1 Level AA compliant tooltips with technical definitions
"""

import streamlit as st
import json
from pathlib import Path
from typing import Optional, Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)


class TechnicalGlossary:
    """Singleton class to manage technical glossary data"""

    _instance = None
    _glossary = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_glossary()
        return cls._instance

    @classmethod
    def _load_glossary(cls):
        """Load technical glossary from JSON file"""
        try:
            glossary_path = Path(__file__).parent.parent.parent / "data" / "technical_glossary.json"
            with open(glossary_path, 'r', encoding='utf-8') as f:
                cls._glossary = json.load(f)
            logger.info("Technical glossary loaded successfully")
        except Exception as e:
            logger.error(f"Error loading technical glossary: {e}")
            cls._glossary = {}

    @classmethod
    def get_term(cls, category: str, term_key: str) -> Optional[Dict[str, Any]]:
        """
        Get term definition from glossary

        Args:
            category: Category of the term (scenarios, substrates, metrics, etc.)
            term_key: Key of the term within the category

        Returns:
            Dictionary with term information or None if not found
        """
        if cls._glossary is None:
            cls._load_glossary()

        try:
            return cls._glossary.get(category, {}).get(term_key)
        except Exception as e:
            logger.error(f"Error getting term {category}.{term_key}: {e}")
            return None

    @classmethod
    def search_term(cls, search_key: str) -> Optional[tuple[str, str, Dict[str, Any]]]:
        """
        Search for a term across all categories

        Args:
            search_key: Key to search for

        Returns:
            Tuple of (category, key, term_data) or None if not found
        """
        if cls._glossary is None:
            cls._load_glossary()

        for category, terms in cls._glossary.items():
            if search_key in terms:
                return (category, search_key, terms[search_key])

        return None


def contextual_tooltip(
    label: str,
    category: str,
    term_key: str,
    inline: bool = True,
    icon: str = "ℹ️",
    style: Literal["default", "compact", "detailed"] = "default"
) -> None:
    """
    Render a contextual tooltip with technical information

    Args:
        label: Display label for the term
        category: Category in glossary (scenarios, substrates, metrics, technical_terms, infrastructure, units)
        term_key: Key of the term in the glossary
        inline: If True, render inline with icon. If False, render as expander
        icon: Icon to display next to label (default: ℹ️)
        style: Display style - default (title + definition), compact (definition only), detailed (all fields)
    """
    glossary = TechnicalGlossary()
    term_data = glossary.get_term(category, term_key)

    if not term_data:
        logger.warning(f"Term not found: {category}.{term_key}")
        st.markdown(f"**{label}**")
        return

    # Inline tooltip with popover
    if inline:
        _render_inline_tooltip(label, term_data, icon, style)
    else:
        _render_expander_tooltip(label, term_data, style)


def _render_inline_tooltip(
    label: str,
    term_data: Dict[str, Any],
    icon: str,
    style: str
) -> None:
    """Render inline tooltip with popover"""

    # Create unique key for popover
    import hashlib
    key_hash = hashlib.md5(f"{label}{term_data.get('title', '')}".encode()).hexdigest()[:8]

    # Render label with icon using popover
    col1, col2 = st.columns([0.95, 0.05])

    with col1:
        st.markdown(f"**{label}**", help=term_data.get('definition', 'No definition available'))

    with col2:
        with st.popover(icon, use_container_width=False):
            _render_tooltip_content(term_data, style)


def _render_expander_tooltip(
    label: str,
    term_data: Dict[str, Any],
    style: str
) -> None:
    """Render tooltip as expander"""

    title = term_data.get('title', label)

    with st.expander(f"📖 {title}", expanded=False):
        _render_tooltip_content(term_data, style)


def _render_tooltip_content(term_data: Dict[str, Any], style: str) -> None:
    """Render tooltip content based on style"""

    # CSS for tooltip styling
    st.markdown("""
    <style>
    .tooltip-content {
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .tooltip-title {
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .tooltip-section {
        margin-top: 0.75rem;
    }
    .tooltip-label {
        font-weight: 600;
        color: #555;
        font-size: 0.85rem;
        text-transform: uppercase;
    }
    .tooltip-reference {
        font-style: italic;
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-left: 3px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    if style == "compact":
        # Compact: definition only
        st.markdown(f"<div class='tooltip-content'>{term_data.get('definition', 'No definition available')}</div>",
                   unsafe_allow_html=True)

    elif style == "detailed":
        # Detailed: show all available fields
        if 'title' in term_data:
            st.markdown(f"<div class='tooltip-title'>{term_data['title']}</div>", unsafe_allow_html=True)

        if 'definition' in term_data:
            st.markdown(f"<div class='tooltip-content'>{term_data['definition']}</div>", unsafe_allow_html=True)

        # Display all other fields except title and definition
        excluded_fields = {'title', 'definition'}
        for key, value in term_data.items():
            if key not in excluded_fields and value:
                formatted_key = key.replace('_', ' ').title()
                st.markdown(f"<div class='tooltip-section'><span class='tooltip-label'>{formatted_key}:</span><br/>{value}</div>",
                           unsafe_allow_html=True)

    else:  # default style
        # Default: title + definition + reference if available
        if 'title' in term_data:
            st.markdown(f"<div class='tooltip-title'>{term_data['title']}</div>", unsafe_allow_html=True)

        if 'definition' in term_data:
            st.markdown(f"<div class='tooltip-content'>{term_data['definition']}</div>", unsafe_allow_html=True)

        # Show key fields based on category
        if 'conversion' in term_data:
            st.markdown(f"<div class='tooltip-section'><span class='tooltip-label'>Conversão:</span><br/>{term_data['conversion']}</div>",
                       unsafe_allow_html=True)

        if 'use_case' in term_data:
            st.markdown(f"<div class='tooltip-section'><span class='tooltip-label'>Aplicação:</span><br/>{term_data['use_case']}</div>",
                       unsafe_allow_html=True)

        if 'methodology' in term_data:
            st.markdown(f"<div class='tooltip-section'><span class='tooltip-label'>Metodologia:</span><br/>{term_data['methodology']}</div>",
                       unsafe_allow_html=True)

        if 'reference' in term_data:
            st.markdown(f"<div class='tooltip-reference'>📚 Referência: {term_data['reference']}</div>",
                       unsafe_allow_html=True)


def quick_tooltip(
    text: str,
    tooltip_text: str,
    icon: str = "ℹ️"
) -> None:
    """
    Quick inline tooltip without glossary lookup

    Args:
        text: Display text
        tooltip_text: Tooltip content
        icon: Icon to display
    """
    col1, col2 = st.columns([0.95, 0.05])

    with col1:
        st.markdown(f"**{text}**", help=tooltip_text)

    with col2:
        with st.popover(icon, use_container_width=False):
            st.markdown(f"<div class='tooltip-content'>{tooltip_text}</div>", unsafe_allow_html=True)


def metric_with_tooltip(
    label: str,
    value: str,
    category: str = "metrics",
    term_key: Optional[str] = None,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> None:
    """
    Render a Streamlit metric with integrated tooltip

    Args:
        label: Metric label
        value: Metric value
        category: Glossary category (default: metrics)
        term_key: Term key in glossary (if None, derived from label)
        delta: Delta value for metric
        delta_color: Color for delta (normal, inverse, off)
    """
    # Derive term_key from label if not provided
    if term_key is None:
        term_key = label.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')

    glossary = TechnicalGlossary()
    term_data = glossary.get_term(category, term_key)

    # Create columns for metric and info icon
    col1, col2 = st.columns([0.9, 0.1])

    with col1:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

    with col2:
        if term_data:
            st.markdown("<br/>", unsafe_allow_html=True)  # Align with metric
            with st.popover("ℹ️", use_container_width=False):
                _render_tooltip_content(term_data, style="default")


def scenario_badge_with_tooltip(
    scenario_key: str,
    percentage: Optional[float] = None
) -> None:
    """
    Render a scenario badge with tooltip

    Args:
        scenario_key: Scenario key (realista, otimista, pessimista, 100_percent)
        percentage: Scenario percentage (optional)
    """
    glossary = TechnicalGlossary()
    term_data = glossary.get_term("scenarios", scenario_key)

    if not term_data:
        st.info(f"Scenario: {scenario_key}")
        return

    # Color mapping for scenarios
    color_map = {
        "realista": "#28a745",
        "otimista": "#17a2b8",
        "pessimista": "#ffc107",
        "100_percent": "#6c757d"
    }

    color = color_map.get(scenario_key, "#6c757d")
    title = term_data.get('title', scenario_key)

    if percentage is not None:
        display_text = f"{title} ({percentage}%)"
    else:
        display_text = title

    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: {color};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                font-weight: 600;
                text-align: center;
                margin: 0.5rem 0;
            ">
                {display_text}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown("<br/>", unsafe_allow_html=True)
        with st.popover("ℹ️", use_container_width=False):
            _render_tooltip_content(term_data, style="detailed")


# Convenience functions for common tooltip types

def scenario_tooltip(scenario_key: str, inline: bool = True) -> None:
    """Tooltip for scenario descriptions"""
    glossary = TechnicalGlossary()
    term_data = glossary.get_term("scenarios", scenario_key)
    if term_data:
        label = term_data.get('title', scenario_key)
        contextual_tooltip(label, "scenarios", scenario_key, inline=inline)


def substrate_tooltip(substrate_key: str, inline: bool = True) -> None:
    """Tooltip for substrate descriptions"""
    glossary = TechnicalGlossary()
    term_data = glossary.get_term("substrates", substrate_key)
    if term_data:
        label = term_data.get('title', substrate_key)
        contextual_tooltip(label, "substrates", substrate_key, inline=inline)


def metric_tooltip(metric_key: str, inline: bool = True) -> None:
    """Tooltip for metric descriptions"""
    glossary = TechnicalGlossary()
    term_data = glossary.get_term("metrics", metric_key)
    if term_data:
        label = term_data.get('title', metric_key)
        contextual_tooltip(label, "metrics", metric_key, inline=inline)
