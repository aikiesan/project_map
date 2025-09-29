"""
CP2B Maps V2 - Accessibility Package
WCAG 2.1 Level A compliance implementation for Brazilian users
"""

from .core import AccessibilityManager
from .settings import AccessibilitySettings
from .components.accessible_components import (
    accessible_button,
    accessible_selectbox,
    accessible_text_input,
    create_skip_links,
    create_aria_landmark
)

__all__ = [
    'AccessibilityManager',
    'AccessibilitySettings',
    'accessible_button',
    'accessible_selectbox',
    'accessible_text_input',
    'create_skip_links',
    'create_aria_landmark'
]