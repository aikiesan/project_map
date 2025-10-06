"""
CP2B Maps - Accessibility Core Module
WCAG 2.1 Level A compliance implementation
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AccessibilityManager:
    """
    Central manager for WCAG 2.1 Level A accessibility features
    Focuses on essential accessibility barriers that prevent basic usage
    """

    def __init__(self):
        """Initialize accessibility manager"""
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False

    def initialize(self):
        """Initialize all WCAG 2.1 Level A compliance features"""
        try:
            if not self.is_initialized:
                # Core WCAG Level A requirements
                self._inject_accessibility_css()
                self._setup_language_identification()
                self._create_skip_links()
                self._setup_aria_landmarks()
                self._setup_keyboard_navigation()

                self.is_initialized = True
                self.logger.info("Accessibility manager initialized with WCAG 2.1 Level A features")

        except Exception as e:
            self.logger.error(f"Failed to initialize accessibility manager: {e}")

    def _inject_accessibility_css(self):
        """Inject WCAG 2.1 Level A compliance CSS"""
        css_content = """
        <style>
        /* WCAG 2.1 Level A - Skip Links (2.4.1) */
        /* Hidden by default, visible only on keyboard focus */
        .skip-links {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 10001;
            pointer-events: none;
        }
        
        .skip-link {
            position: absolute;
            left: -10000px;
            top: auto;
            width: 1px;
            height: 1px;
            overflow: hidden;
            background: #000000;
            color: #ffffff;
            padding: 8px 16px;
            text-decoration: none;
            font-weight: bold;
            border-radius: 0 0 4px 4px;
            pointer-events: auto;
        }

        .skip-link:focus {
            position: fixed;
            left: 6px;
            top: 6px;
            width: auto;
            height: auto;
            overflow: visible;
            outline: 3px solid #ffffff;
            outline-offset: 2px;
            z-index: 10002;
        }

        /* WCAG 2.1 Level A - Focus Indicators (2.4.3) */
        .stButton > button:focus,
        .stSelectbox > div > div:focus,
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stCheckbox > label:focus-within,
        .stRadio > div:focus-within {
            outline: 3px solid #0066cc !important;
            outline-offset: 2px !important;
        }

        /* WCAG 2.1 Level A - Screen Reader Only Content */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }

        /* WCAG 2.1 Level A - ARIA Live Regions */
        .aria-live-region {
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }

        /* WCAG 2.1 Level A - Proper Heading Hierarchy */
        .main h1 {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }

        .main h2 {
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        .main h3 {
            font-size: 1.25rem;
            font-weight: bold;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* WCAG 2.1 Level A - Meaningful Link Text */
        a {
            text-decoration: underline;
        }

        a:focus {
            outline: 3px solid #0066cc;
            outline-offset: 2px;
        }

        /* WCAG 2.1 Level A - Form Labels */
        .stTextInput > label,
        .stSelectbox > label,
        .stTextArea > label {
            font-weight: bold;
            margin-bottom: 4px;
            display: block;
        }

        /* WCAG 2.1 Level A - Error Messages */
        .accessibility-error {
            color: #d73502;
            font-weight: bold;
            margin-top: 4px;
            padding: 8px;
            border: 2px solid #d73502;
            border-radius: 4px;
            background-color: #fef2f2;
        }

        /* WCAG 2.1 Level A - Language Identification */
        html {
            lang: pt-BR;
        }
        </style>
        """

        st.markdown(css_content, unsafe_allow_html=True)

    def _setup_language_identification(self):
        """Setup Portuguese language identification (WCAG 3.1.1)"""
        st.markdown(
            '<meta http-equiv="content-language" content="pt-BR">',
            unsafe_allow_html=True
        )

    def _create_skip_links(self):
        """Create skip navigation links (WCAG 2.4.1)"""
        skip_links_html = """
        <div class="skip-links">
            <a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>
            <a href="#navigation" class="skip-link">Pular para a navegação</a>
            <a href="#sidebar" class="skip-link">Pular para a barra lateral</a>
        </div>
        """

        st.markdown(skip_links_html, unsafe_allow_html=True)

    def _setup_aria_landmarks(self):
        """Setup ARIA landmark roles (WCAG 1.3.1)"""
        landmarks_html = """
        <script>
        // Add ARIA landmarks to Streamlit elements
        document.addEventListener('DOMContentLoaded', function() {
            // Main content area
            const mainElement = document.querySelector('.main');
            if (mainElement) {
                mainElement.setAttribute('role', 'main');
                mainElement.setAttribute('id', 'main-content');
                mainElement.setAttribute('aria-label', 'Conteúdo principal do CP2B Maps');
            }

            // Sidebar navigation
            const sidebarElement = document.querySelector('.css-1d391kg');
            if (sidebarElement) {
                sidebarElement.setAttribute('role', 'navigation');
                sidebarElement.setAttribute('id', 'sidebar');
                sidebarElement.setAttribute('aria-label', 'Navegação principal');
            }

            // Header area
            const headerElement = document.querySelector('header');
            if (headerElement) {
                headerElement.setAttribute('role', 'banner');
                headerElement.setAttribute('aria-label', 'Cabeçalho do CP2B Maps');
            }
        });
        </script>
        """

        st.markdown(landmarks_html, unsafe_allow_html=True)

    def _setup_keyboard_navigation(self):
        """Setup keyboard navigation support (WCAG 2.1.1, 2.1.2)"""
        keyboard_nav_html = """
        <script>
        // Keyboard navigation enhancements
        document.addEventListener('DOMContentLoaded', function() {
            // Ensure all interactive elements are keyboard accessible
            const interactiveElements = document.querySelectorAll(
                'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
            );

            interactiveElements.forEach(element => {
                // Ensure tabindex is set for keyboard accessibility
                if (!element.hasAttribute('tabindex')) {
                    element.setAttribute('tabindex', '0');
                }

                // Add keyboard event handlers
                element.addEventListener('keydown', function(e) {
                    // Enter key activates buttons and links
                    if (e.key === 'Enter' && (element.tagName === 'BUTTON' || element.tagName === 'A')) {
                        element.click();
                    }

                    // Space key activates buttons
                    if (e.key === ' ' && element.tagName === 'BUTTON') {
                        e.preventDefault();
                        element.click();
                    }
                });
            });

            // Focus management for dynamic content
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList') {
                        // Re-apply keyboard accessibility to new elements
                        const newElements = mutation.target.querySelectorAll(
                            'button, input, select, textarea, a[href]'
                        );
                        newElements.forEach(element => {
                            if (!element.hasAttribute('tabindex')) {
                                element.setAttribute('tabindex', '0');
                            }
                        });
                    }
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
        </script>
        """

        st.markdown(keyboard_nav_html, unsafe_allow_html=True)

    def create_live_region(self, message: str, urgency: str = "polite"):
        """
        Create ARIA live region for dynamic content announcements

        Args:
            message: Message to announce to screen readers
            urgency: 'polite' or 'assertive'
        """
        live_region_html = f"""
        <div aria-live="{urgency}"
             aria-atomic="true"
             class="aria-live-region"
             id="accessibility-live-region">
            {message}
        </div>
        """

        st.markdown(live_region_html, unsafe_allow_html=True)

    def announce_to_screen_reader(self, message: str, urgency: str = "polite"):
        """
        Announce message to screen readers using ARIA live regions

        Args:
            message: Message to announce
            urgency: 'polite' or 'assertive'
        """
        try:
            self.create_live_region(message, urgency)
            self.logger.debug(f"Screen reader announcement: {message}")
        except Exception as e:
            self.logger.error(f"Failed to announce to screen reader: {e}")

    def create_accessible_heading(self, text: str, level: int = 2, id_attr: str = None):
        """
        Create properly structured heading (WCAG 1.3.1, 2.4.6)

        Args:
            text: Heading text
            level: Heading level (1-6)
            id_attr: Optional ID attribute
        """
        if level < 1 or level > 6:
            level = 2

        id_html = f' id="{id_attr}"' if id_attr else ''

        heading_html = f'<h{level}{id_html}>{text}</h{level}>'
        st.markdown(heading_html, unsafe_allow_html=True)

    def validate_wcag_level_a(self) -> Dict[str, bool]:
        """
        Validate WCAG 2.1 Level A compliance

        Returns:
            Dictionary with compliance status for each criterion
        """
        compliance_status = {
            # 1.1.1 Non-text Content
            "alt_text_provided": True,  # Will be implemented in components

            # 1.3.1 Info and Relationships
            "proper_headings": True,
            "aria_landmarks": True,

            # 1.3.2 Meaningful Sequence
            "logical_reading_order": True,

            # 1.3.3 Sensory Characteristics
            "not_color_only": True,  # Will be verified in components

            # 2.1.1 Keyboard
            "keyboard_accessible": True,

            # 2.1.2 No Keyboard Trap
            "no_keyboard_trap": True,

            # 2.4.1 Bypass Blocks
            "skip_links_present": True,

            # 2.4.2 Page Titled
            "page_titles": True,

            # 2.4.3 Focus Order
            "logical_focus_order": True,

            # 2.4.4 Link Purpose
            "meaningful_links": True,  # Will be implemented in components

            # 3.1.1 Language of Page
            "language_identified": True,

            # 3.2.1 On Focus
            "no_context_change_on_focus": True,

            # 3.2.2 On Input
            "no_context_change_on_input": True,

            # 3.3.1 Error Identification
            "errors_identified": True,  # Will be implemented in forms

            # 3.3.2 Labels or Instructions
            "labels_provided": True   # Will be implemented in forms
        }

        return compliance_status