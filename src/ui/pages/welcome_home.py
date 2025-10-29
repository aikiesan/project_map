"""
CP2B Maps - Welcome Home Page
Professional welcome page that introduces users to the platform
Follows SOLID principles - Single Responsibility: Welcome and guide new users
"""

import streamlit as st
from typing import Optional
from src.utils.logging_config import get_logger
from src.ui.components.feature_card import render_feature_grid
from src.ui.components.workflow_guide import (
    render_workflow_section,
    render_faq_section,
    render_research_scenarios,
    render_getting_started_cta
)

logger = get_logger(__name__)


class WelcomeHomePage:
    """
    Welcome home page component

    Responsibilities:
    - Welcome new users
    - Introduce platform features
    - Provide navigation guidance
    - Display practical examples and FAQs

    Follows SOLID principles:
    - Single Responsibility: Only handles welcome/introduction
    - Open/Closed: Extensible through component addition
    - Dependency Inversion: Uses abstract component interfaces
    """

    def __init__(self):
        """Initialize welcome home page"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing WelcomeHomePage")

    def render(self) -> None:
        """
        Render complete welcome home page

        Structure:
        1. Platform Introduction
        2. Feature cards grid (7 tools)
        3. Workflow examples
        4. FAQ section
        5. Research scenarios
        6. Call-to-action

        Note: Main green header is rendered by app.py, no hero banner needed here
        """
        try:
            # Platform Introduction (starts the page)
            self._render_introduction()

            # Feature Cards
            self._render_feature_cards()

            # Practical Guides
            self._render_practical_guides()

            # Call to Action
            render_getting_started_cta()

        except Exception as e:
            self.logger.error(f"Error rendering welcome page: {e}", exc_info=True)
            st.error("⚠️ Erro ao carregar a página de boas-vindas. Por favor, recarregue a página.")

    def _render_introduction(self) -> None:
        """Render platform introduction"""

        # Simple welcome heading
        st.markdown("# 👋 Bem-vindo ao CP2B Maps!")
        st.markdown("### Sua plataforma completa para análise de potencial de biogás em São Paulo")
        st.markdown("")  # Spacing

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("""
            ## 🌟 O que é o CP2B Maps?

            O **CP2B Maps** é uma plataforma profissional de análise geoespacial desenvolvida pelo
            **Centro Paulista de Estudos em Biogás e Bioprodutos**. Nosso objetivo é fornecer
            ferramentas avançadas e acessíveis para:

            - 🔬 **Pesquisadores** que estudam energia renovável e sustentabilidade
            - 🏢 **Empresas** que planejam investimentos em biogás e bioenergia
            - 🏛️ **Gestores públicos** que desenvolvem políticas energéticas e de sustentabilidade
            - 🎓 **Estudantes** que exploram temas de energia limpa e meio ambiente

            ### 🎯 Por que usar o CP2B Maps?

            ✅ **Dados Científicos Validados** - Baseado em pesquisa FAPESP 2024/01112-1
            ✅ **Múltiplas Ferramentas Integradas** - 7 módulos especializados
            ✅ **Visualizações Interativas** - Mapas, gráficos e dashboards
            ✅ **Assistente IA** - Bagacinho para consultas em linguagem natural
            ✅ **Acessibilidade Completa** - WCAG 2.1 Nível A (leitores de tela, teclado)
            """)

        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
                        color: white; padding: 1.5rem; border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(79,70,229,0.2); margin-top: 2rem;'>
                <div style='font-size: 2rem; text-align: center; margin-bottom: 1rem;'>🚀</div>
                <h4 style='margin: 0 0 1rem 0; text-align: center; font-weight: 600;'>
                    Início Rápido
                </h4>
                <div style='font-size: 0.9rem; line-height: 1.6;'>
                    <strong>1.</strong> Explore os <strong>645 municípios</strong> no mapa<br>
                    <strong>2.</strong> Compare <strong>potenciais de biogás</strong><br>
                    <strong>3.</strong> Analise <strong>uso do solo</strong> (MapBiomas)<br>
                    <strong>4.</strong> Pergunte ao <strong>Bagacinho IA</strong><br>
                    <strong>5.</strong> Exporte <strong>dados e relatórios</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")
            st.info("💡 **Primeira vez?** Role para baixo para ver os exemplos práticos e perguntas frequentes!")

    def _render_feature_cards(self) -> None:
        """Render feature cards for all 6 tools"""

        st.markdown("""
        <h2 style='color: #2c3e50; font-weight: 600; margin-top: 3rem; margin-bottom: 1rem;
                   border-bottom: 3px solid #2E8B57; padding-bottom: 0.75rem;'>
            🛠️ Ferramentas Disponíveis
        </h2>
        <p style='color: #6c757d; font-size: 1.1rem; line-height: 1.8; margin-bottom: 2.5rem; max-width: 900px;'>
            Descubra as 6 ferramentas especializadas que compõem o CP2B Maps.
            Cada uma foi desenvolvida para atender necessidades específicas de análise geoespacial e planejamento energético.
        </p>
        """, unsafe_allow_html=True)

        features = [
            {
                "icon": "🗺️",
                "title": "Mapa Principal",
                "description": "Visualize o potencial de biogás em mapas interativos com múltiplas camadas GIS e dados de 645 municípios.",
                "tool_key": "mapa_principal"
            },
            {
                "icon": "🔍",
                "title": "Explorar Dados",
                "description": "Analise estatísticas, rankings e compare municípios com gráficos interativos avançados.",
                "tool_key": "explorar_dados"
            },
            {
                "icon": "📊",
                "title": "Análises Avançadas",
                "description": "Examine a composição detalhada de resíduos por tipo (9 substratos) e distribuição regional.",
                "tool_key": "analises_avancadas"
            },
            {
                "icon": "🎯",
                "title": "Análise de Proximidade",
                "description": "Agrupe municípios por raio customizável e analise uso do solo com integração MapBiomas.",
                "tool_key": "proximidade"
            },
            {
                "icon": "🍊",
                "title": "Bagacinho IA",
                "description": "Converse com nosso assistente inteligente sobre dados usando linguagem natural (Google Gemini + RAG).",
                "tool_key": "bagacinho_ia"
            },
            {
                "icon": "📚",
                "title": "Referências Científicas",
                "description": "Explore as 20+ fontes científicas que embasam os cálculos com citações em formato ABNT.",
                "tool_key": "referencias"
            }
        ]

        render_feature_grid(features, columns=3)

    def _render_practical_guides(self) -> None:
        """Render practical guides: workflows, FAQ, and research scenarios"""

        # Workflow Examples
        render_workflow_section()

        # FAQ Section
        render_faq_section()

        # Research Scenarios
        render_research_scenarios()


# Factory function for creating WelcomeHomePage instances
def create_welcome_home_page() -> WelcomeHomePage:
    """
    Factory function to create WelcomeHomePage instance

    Returns:
        WelcomeHomePage instance
    """
    return WelcomeHomePage()
