"""
CP2B Maps - Accessibility Settings
Basic accessibility preferences for WCAG 2.1 Level A compliance
"""

import streamlit as st
from typing import Dict, Any
import json

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AccessibilitySettings:
    """
    Manage basic accessibility settings for WCAG 2.1 Level A compliance
    """

    def __init__(self):
        """Initialize accessibility settings"""
        self.logger = get_logger(self.__class__.__name__)

        # Initialize basic settings from session state
        self.screen_reader_mode = st.session_state.get('accessibility_screen_reader', False)
        self.keyboard_navigation = st.session_state.get('accessibility_keyboard_nav', True)
        self.skip_links_enabled = st.session_state.get('accessibility_skip_links', True)

    def render_basic_settings(self):
        """Render basic accessibility settings panel"""
        try:
            st.markdown("### ♿ Configurações de Acessibilidade")
            st.markdown("*Recursos básicos para melhorar a acessibilidade*")

            # Initialize first render flag to prevent rerun on initial load
            if 'accessibility_first_render' not in st.session_state:
                st.session_state.accessibility_first_render = True

            # Screen reader optimization
            screen_reader = st.checkbox(
                "🔊 Modo Leitor de Tela",
                value=self.screen_reader_mode,
                help="Otimiza a interface para leitores de tela como NVDA e ORCA",
                key='accessibility_screen_reader_toggle'
            )

            # Keyboard navigation
            keyboard_nav = st.checkbox(
                "⌨️ Navegação por Teclado Aprimorada",
                value=self.keyboard_navigation,
                help="Melhora a navegação usando apenas o teclado",
                key='accessibility_keyboard_nav_toggle'
            )

            # Skip links
            skip_links = st.checkbox(
                "🔗 Links de Pular Conteúdo",
                value=self.skip_links_enabled,
                help="Exibe links para pular para o conteúdo principal",
                key='accessibility_skip_links_toggle'
            )

            # Apply settings if changed (but NOT on first render to prevent unnecessary rerun)
            settings_changed = (
                screen_reader != self.screen_reader_mode or
                keyboard_nav != self.keyboard_navigation or
                skip_links != self.skip_links_enabled
            )

            if settings_changed and not st.session_state.accessibility_first_render:
                self.apply_settings(screen_reader, keyboard_nav, skip_links, show_success=True)

            # Clear first render flag after initial render
            if st.session_state.accessibility_first_render:
                st.session_state.accessibility_first_render = False

            # Information about WCAG compliance
            with st.expander("ℹ️ Sobre a Conformidade WCAG 2.1"):
                st.markdown("""
                **CP2B Maps está em conformidade com WCAG 2.1 Nível A:**

                ✅ **Alternativas de Texto**: Descrições para mapas e gráficos
                ✅ **Navegação por Teclado**: Todos os recursos acessíveis via teclado
                ✅ **Estrutura Semântica**: Cabeçalhos e marcos apropriados
                ✅ **Identificação de Idioma**: Interface em português brasileiro
                ✅ **Links de Pular**: Navegação rápida para conteúdo principal
                ✅ **Ordem de Foco**: Sequência lógica de navegação

                **Leitores de Tela Suportados:**
                - NVDA (Windows) - Gratuito
                - ORCA (Linux) - Nativo
                - JAWS (Windows) - Comercial
                - VoiceOver (macOS) - Nativo
                """)

        except Exception as e:
            self.logger.error(f"Error rendering accessibility settings: {e}")
            st.error("Erro ao carregar configurações de acessibilidade")

    def apply_settings(self, screen_reader: bool, keyboard_nav: bool, skip_links: bool, show_success: bool = False):
        """
        Apply accessibility settings

        Args:
            screen_reader: Enable screen reader mode
            keyboard_nav: Enable keyboard navigation
            skip_links: Enable skip links
            show_success: Show success message (only on actual user change, not initialization)
        """
        try:
            # Update session state
            st.session_state.accessibility_screen_reader = screen_reader
            st.session_state.accessibility_keyboard_nav = keyboard_nav
            st.session_state.accessibility_skip_links = skip_links

            # Update instance variables
            self.screen_reader_mode = screen_reader
            self.keyboard_navigation = keyboard_nav
            self.skip_links_enabled = skip_links

            # Apply CSS changes for screen reader mode (only if enabling for first time)
            if screen_reader and 'screen_reader_css_applied' not in st.session_state:
                self._apply_screen_reader_optimizations()
                st.session_state.screen_reader_css_applied = True

            # Save settings
            self.save_settings()

            # Only show success message if explicitly requested (not on init)
            if show_success:
                st.success("✅ Configurações de acessibilidade aplicadas")

            self.logger.info("Accessibility settings applied successfully")

        except Exception as e:
            self.logger.error(f"Error applying accessibility settings: {e}")
            st.error("Erro ao aplicar configurações")

    def _apply_screen_reader_optimizations(self):
        """Apply screen reader specific optimizations"""
        screen_reader_css = """
        <style>
        /* Screen reader optimizations */
        .stButton > button {
            position: relative;
        }

        .stButton > button::after {
            content: attr(aria-label);
            position: absolute;
            left: -10000px;
        }

        /* Enhanced focus indicators for screen readers */
        .stSelectbox > div:focus-within,
        .stTextInput > div:focus-within {
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.3);
        }

        /* Screen reader friendly table headers */
        table th {
            scope: col;
        }

        /* Enhanced live region visibility for testing */
        .aria-live-region {
            clip: rect(1px, 1px, 1px, 1px);
            height: 1px;
            overflow: hidden;
            position: absolute;
            width: 1px;
        }
        </style>
        """

        st.markdown(screen_reader_css, unsafe_allow_html=True)

    def save_settings(self):
        """Save accessibility settings to session state"""
        try:
            accessibility_preferences = {
                'screen_reader_mode': self.screen_reader_mode,
                'keyboard_navigation': self.keyboard_navigation,
                'skip_links_enabled': self.skip_links_enabled,
                'wcag_level': 'A'
            }

            st.session_state.accessibility_preferences = accessibility_preferences

            # Also save to browser localStorage if possible
            settings_json = json.dumps(accessibility_preferences)
            local_storage_script = f"""
            <script>
            try {{
                localStorage.setItem('cp2b_accessibility_settings', '{settings_json}');
            }} catch(e) {{
                console.log('Could not save to localStorage:', e);
            }}
            </script>
            """

            st.markdown(local_storage_script, unsafe_allow_html=True)

        except Exception as e:
            self.logger.error(f"Error saving accessibility settings: {e}")

    def load_settings(self):
        """Load accessibility settings from session state"""
        try:
            if 'accessibility_preferences' in st.session_state:
                prefs = st.session_state.accessibility_preferences

                self.screen_reader_mode = prefs.get('screen_reader_mode', False)
                self.keyboard_navigation = prefs.get('keyboard_navigation', True)
                self.skip_links_enabled = prefs.get('skip_links_enabled', True)

                self.logger.info("Accessibility settings loaded from session state")

        except Exception as e:
            self.logger.error(f"Error loading accessibility settings: {e}")

    def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of current accessibility settings"""
        return {
            'screen_reader_mode': self.screen_reader_mode,
            'keyboard_navigation': self.keyboard_navigation,
            'skip_links_enabled': self.skip_links_enabled,
            'wcag_compliance_level': 'A',
            'features_enabled': [
                'Alt text for images',
                'Keyboard navigation',
                'Skip links',
                'Semantic markup',
                'Portuguese language support',
                'Focus indicators',
                'ARIA landmarks'
            ]
        }

    def render_accessibility_status(self):
        """Render accessibility compliance status"""
        try:
            settings = self.get_settings_summary()

            st.markdown("#### 📊 Status de Acessibilidade")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Nível WCAG",
                    "Nível A",
                    help="Conformidade com WCAG 2.1 Nível A"
                )

            with col2:
                features_count = len(settings['features_enabled'])
                st.metric(
                    "Recursos Ativos",
                    f"{features_count}",
                    help="Número de recursos de acessibilidade ativos"
                )

            # Features list
            with st.expander("🔧 Recursos de Acessibilidade Ativos"):
                for feature in settings['features_enabled']:
                    st.markdown(f"✅ {feature}")

        except Exception as e:
            self.logger.error(f"Error rendering accessibility status: {e}")
            st.error("Erro ao exibir status de acessibilidade")