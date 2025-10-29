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
    """Render the onboarding modal content"""

    # Custom CSS for modal
    st.markdown("""
    <style>
    .onboarding-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .onboarding-modal {
        background: white;
        border-radius: 15px;
        padding: 2.5rem;
        max-width: 600px;
        width: 90%;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.4s ease-out;
        position: relative;
    }

    @keyframes slideUp {
        from {
            transform: translateY(50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .onboarding-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .onboarding-logo {
        font-size: 4rem;
        margin-bottom: 1rem;
    }

    .onboarding-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .onboarding-subtitle {
        font-size: 1rem;
        color: #666;
    }

    .onboarding-content {
        margin: 2rem 0;
    }

    .onboarding-feature {
        display: flex;
        align-items: flex-start;
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        transition: transform 0.2s;
    }

    .onboarding-feature:hover {
        transform: translateX(5px);
        background: #e9ecef;
    }

    .onboarding-feature-icon {
        font-size: 2rem;
        margin-right: 1rem;
        flex-shrink: 0;
    }

    .onboarding-feature-text {
        flex-grow: 1;
    }

    .onboarding-feature-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.25rem;
    }

    .onboarding-feature-description {
        font-size: 0.9rem;
        color: #666;
    }

    .onboarding-footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e9ecef;
    }

    .onboarding-checkbox-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #666;
    }

    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        .onboarding-overlay, .onboarding-modal, .onboarding-feature {
            animation: none;
            transition: none;
        }
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .onboarding-modal {
            padding: 1.5rem;
            width: 95%;
        }

        .onboarding-title {
            font-size: 1.4rem;
        }

        .onboarding-feature-icon {
            font-size: 1.5rem;
        }
    }

    /* Focus styles for keyboard navigation */
    .onboarding-modal:focus-within {
        outline: 3px solid #667eea;
        outline-offset: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Use Streamlit dialog (available in newer versions) or container
    @st.dialog("🗺️ Bem-vindo ao CP2B Maps V2", width="large")
    def onboarding_dialog():
        # Header
        st.markdown("### Plataforma de Análise de Potencial de Biogás")
        st.markdown("---")

        # Features using native Streamlit components
        st.markdown("#### Principais Funcionalidades:")

        # Feature 1: Bagacinho IA
        with st.container():
            col_icon1, col_text1 = st.columns([0.1, 0.9])
            with col_icon1:
                st.markdown("### 🤖")
            with col_text1:
                st.markdown("**Bagacinho IA**")
                st.caption("Assistente inteligente para consultas técnicas e análise de dados em linguagem natural")

        st.markdown("")  # Spacer

        # Feature 2: Glossário Técnico
        with st.container():
            col_icon2, col_text2 = st.columns([0.1, 0.9])
            with col_icon2:
                st.markdown("### 📚")
            with col_text2:
                st.markdown("**Glossário Técnico**")
                st.caption("Clique nos ícones ℹ️ para acessar definições científicas rigorosas e referências")

        st.markdown("")  # Spacer

        # Feature 3: Central de Ajuda
        with st.container():
            col_icon3, col_text3 = st.columns([0.1, 0.9])
            with col_icon3:
                st.markdown("### 💡")
            with col_text3:
                st.markdown("**Central de Ajuda**")
                st.caption("Acesse a ajuda contextual na sidebar para FAQ, exemplos e documentação técnica")

        st.markdown("---")

        # Checkbox to not show again
        dont_show_again = st.checkbox(
            "Não mostrar novamente",
            value=False,
            key="onboarding_dont_show_checkbox",
            help="Você pode sempre reativar esta introdução nas configurações"
        )

        # Buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("⏭️ Pular", use_container_width=True):
                _dismiss_onboarding(dont_show_again)
                st.rerun()

        with col2:
            if st.button("📚 Ver Tutorial", use_container_width=True, type="secondary"):
                _dismiss_onboarding(dont_show_again)
                st.switch_page("pages/01_🏠_Home.py")

        with col3:
            if st.button("🚀 Começar", use_container_width=True, type="primary"):
                _dismiss_onboarding(dont_show_again)
                st.rerun()

    # Show dialog
    onboarding_dialog()


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
