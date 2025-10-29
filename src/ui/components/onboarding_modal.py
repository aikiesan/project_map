"""
CP2B Maps - Simple Onboarding Modal
Minimal, skippable introduction for first-time users
WCAG 2.1 Level AA compliant
"""

import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def show_onboarding_modal(force_show: bool = False) -> None:
    """
    Show simple onboarding modal for first-time users

    Args:
        force_show: If True, show modal regardless of user preference
    """

    # Check if user has seen the onboarding
    if "onboarding_seen" not in st.session_state:
        st.session_state.onboarding_seen = False

    if "onboarding_dismissed" not in st.session_state:
        st.session_state.onboarding_dismissed = False

    # Show modal if not seen or force_show is True
    if force_show or (not st.session_state.onboarding_seen and not st.session_state.onboarding_dismissed):
        _render_onboarding_modal()


def _render_onboarding_modal() -> None:
    """Render compact and elegant welcome modal"""

    # Simple, elegant modal using Streamlit dialog
    @st.dialog("Bem-vindo ao CP2B Maps V2!", width="small")
    def welcome_dialog():
        # Centered emoji
        st.markdown(
            "<div style='text-align: center; font-size: 3.5rem; margin: 0.5rem 0 1rem 0;'>🗺️</div>",
            unsafe_allow_html=True
        )

        # Subtitle
        st.markdown(
            "<p style='text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 1.5rem;'>Plataforma de Análise de Potencial de Biogás</p>",
            unsafe_allow_html=True
        )

        # Single tip with icon
        st.info("💡 **Dica:** Clique nos ícones ℹ️ para ver definições técnicas e referências científicas", icon="💡")

        st.markdown("<br/>", unsafe_allow_html=True)

        # Checkbox centered
        col_spacer1, col_checkbox, col_spacer2 = st.columns([0.1, 0.8, 0.1])
        with col_checkbox:
            dont_show_again = st.checkbox(
                "Não mostrar novamente",
                value=False,
                key="onboarding_dont_show_checkbox",
                help="Marque para ocultar esta mensagem em futuras visitas"
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Single centered button
        col_btn1, col_btn2, col_btn3 = st.columns([0.2, 0.6, 0.2])
        with col_btn2:
            if st.button("🚀 Começar a Explorar", use_container_width=True, type="primary"):
                _dismiss_onboarding(dont_show_again)

    # Show dialog
    welcome_dialog()


def _dismiss_onboarding(dont_show_again: bool) -> None:
    """Dismiss onboarding modal"""
    st.session_state.onboarding_seen = True

    if dont_show_again:
        st.session_state.onboarding_dismissed = True
        # In production, this would be persisted to user preferences
        logger.info("User dismissed onboarding permanently")
    else:
        logger.info("User dismissed onboarding for this session")


def reset_onboarding() -> None:
    """Reset onboarding state (for testing or user preference)"""
    st.session_state.onboarding_seen = False
    st.session_state.onboarding_dismissed = False
    logger.info("Onboarding state reset")


def render_compact_welcome_banner() -> None:
    """
    Render a compact welcome banner as alternative to modal
    Useful for pages where modal might be disruptive
    """

    if "welcome_banner_dismissed" not in st.session_state:
        st.session_state.welcome_banner_dismissed = False

    if not st.session_state.welcome_banner_dismissed:
        with st.container():
            col1, col2 = st.columns([0.95, 0.05])

            with col1:
                st.info("""
                👋 **Bem-vindo ao CP2B Maps V2!**

                💡 **Dica**: Clique nos ícones ℹ️ para ver definições técnicas detalhadas.
                Use o **Bagacinho IA** para consultas em linguagem natural.
                Acesse a **Central de Ajuda** na sidebar para FAQ e documentação.
                """)

            with col2:
                if st.button("✖️", key="dismiss_welcome_banner", help="Dispensar banner"):
                    st.session_state.welcome_banner_dismissed = True
                    st.rerun()


def render_feature_highlight(
    feature_name: str,
    description: str,
    icon: str = "✨",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
) -> None:
    """
    Render a feature highlight card

    Args:
        feature_name: Name of the feature
        description: Feature description
        icon: Icon for the feature
        action_label: Label for action button (optional)
        action_callback: Callback function when button is clicked (optional)
    """

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">
            {feature_name}
        </div>
        <div style="font-size: 0.95rem; line-height: 1.5;">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if action_label and action_callback:
        if st.button(action_label, type="primary", use_container_width=True):
            action_callback()


def render_quick_start_tips(page_context: str) -> None:
    """
    Render contextual quick start tips based on current page

    Args:
        page_context: Current page identifier
    """

    tips_map = {
        "map": {
            "icon": "🗺️",
            "title": "Dicas - Mapa Principal",
            "tips": [
                "Use os filtros na sidebar para selecionar cenários e substratos",
                "Clique em municípios no mapa para ver detalhes completos",
                "Exporte dados em CSV ou GeoJSON para análise externa"
            ]
        },
        "explorer": {
            "icon": "📊",
            "title": "Dicas - Explorar Dados",
            "tips": [
                "Ordene tabelas clicando nos cabeçalhos das colunas",
                "Use filtros para comparar municípios específicos",
                "Visualize rankings para identificar regiões prioritárias"
            ]
        },
        "proximity": {
            "icon": "🎯",
            "title": "Dicas - Análise de Proximidade",
            "tips": [
                "Selecione raio de 30-50 km para viabilidade logística típica",
                "Ative camadas de infraestrutura para ver gasodutos e energia",
                "Agregação regional ajuda a avaliar plantas centralizadas"
            ]
        },
        "bagacinho": {
            "icon": "🤖",
            "title": "Dicas - Bagacinho IA",
            "tips": [
                "Faça perguntas em linguagem natural sobre biogás",
                "Use exemplos fornecidos como modelo para suas consultas",
                "Respostas incluem referências científicas validadas"
            ]
        }
    }

    tips_data = tips_map.get(page_context)

    if tips_data:
        with st.expander(f"{tips_data['icon']} {tips_data['title']}", expanded=False):
            for tip in tips_data['tips']:
                st.markdown(f"• {tip}")
