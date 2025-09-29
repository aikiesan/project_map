"""
CP2B Maps V2 - Accessible Components Package
WCAG 2.1 Level A compliant UI components
"""

from .accessible_components import (
    accessible_button,
    accessible_selectbox,
    accessible_text_input,
    accessible_text_area,
    create_skip_links,
    create_aria_landmark,
    accessible_metric,
    accessible_expander
)

__all__ = [
    'accessible_button',
    'accessible_selectbox',
    'accessible_text_input',
    'accessible_text_area',
    'create_skip_links',
    'create_aria_landmark',
    'accessible_metric',
    'accessible_expander'
]