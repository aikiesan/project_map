"""
CP2B Maps - Workflow Guide Component
Provides practical examples, FAQs, and research scenarios
"""

import streamlit as st
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_workflow_section() -> None:
    """Render workflow examples section"""
    try:
        st.markdown("""
        <h2 style='color: #2c3e50; font-weight: 600; margin-top: 4rem; margin-bottom: 1rem;
                   border-bottom: 3px solid #2E8B57; padding-bottom: 0.75rem;'>
            💡 Exemplos Práticos de Uso
        </h2>
        <p style='color: #6c757d; font-size: 1.1rem; line-height: 1.8; margin-bottom: 2rem;'>
            Aprenda como usar o CP2B Maps com exemplos práticos para diferentes objetivos
        </p>
        """, unsafe_allow_html=True)

        # Workflow examples
        workflows = [
            {
                "title": "🎯 Identificar Região com Maior Potencial",
                "objective": "Encontrar municípios com alto potencial de biogás para investimento",
                "steps": [
                    "Acesse **Mapa Principal** e selecione visualização coroplética",
                    "Filtre por **'Potencial Total de Biogás'**",
                    "Identifique regiões com cores mais intensas (maior potencial)",
                    "Clique nos municípios para ver detalhes em popup",
                    "Vá para **Explorar Dados** e gere ranking dos top 20 municípios"
                ],
                "tip": "💡 **Dica:** Use o cenário 'Realista' para estimativas conservadoras baseadas em pesquisa FAPESP"
            },
            {
                "title": "📊 Análise de Viabilidade por Proximidade",
                "objective": "Avaliar potencial agregado em um raio econômico de coleta",
                "steps": [
                    "Acesse **Análise de Proximidade**",
                    "Selecione um município de referência (ex: onde planeja construir planta)",
                    "Defina raio de 30-50 km (viabilidade logística)",
                    "Visualize municípios próximos e potencial agregado",
                    "Ative análise MapBiomas para ver uso do solo",
                    "Exporte dados para análise detalhada"
                ],
                "tip": "💡 **Dica:** Raios de 20-30 km são ideais para coleta diária economicamente viável"
            },
            {
                "title": "🤖 Consulta Rápida com IA",
                "objective": "Obter informações específicas rapidamente usando linguagem natural",
                "steps": [
                    "Acesse **Bagacinho IA**",
                    "Digite pergunta em português (ex: 'Qual município tem mais biogás de cana?')",
                    "Aguarde resposta com dados e contexto",
                    "Faça perguntas de acompanhamento para aprofundar",
                    "Use respostas para guiar análises nas outras ferramentas"
                ],
                "tip": "💡 **Dica:** Seja específico nas perguntas para respostas mais precisas"
            }
        ]

        for workflow in workflows:
            with st.expander(workflow["title"], expanded=False):
                st.markdown(f"**Objetivo:** {workflow['objective']}")
                st.markdown("")
                st.markdown("**Passo a passo:**")
                for step in workflow['steps']:
                    st.markdown(f"- {step}")
                st.markdown("")
                st.info(workflow['tip'])

    except Exception as e:
        logger.error(f"Error rendering workflow section: {e}", exc_info=True)
        st.error("Erro ao carregar exemplos práticos.")


def render_faq_section() -> None:
    """Render FAQ section"""
    try:
        st.markdown("""
        <h2 style='color: #2c3e50; font-weight: 600; margin-top: 4rem; margin-bottom: 1rem;
                   border-bottom: 3px solid #2E8B57; padding-bottom: 0.75rem;'>
            ❓ Perguntas Frequentes
        </h2>
        """, unsafe_allow_html=True)

        faqs = [
            {
                "question": "O que são os 'Cenários de Disponibilidade'?",
                "answer": """
                Os cenários (Pessimista, Realista, Otimista, Utópico) aplicam fatores de disponibilidade
                aos resíduos para estimar quanto realmente pode ser coletado e usado para biogás.

                - **Pessimista (10%)**: Estimativa muito conservadora
                - **Realista (17.5%)**: Baseado em pesquisa FAPESP validada (recomendado)
                - **Otimista (27.5%)**: Cenário favorável com boa infraestrutura
                - **Utópico (100%)**: Potencial teórico máximo (improvável na prática)
                """
            },
            {
                "question": "Qual ferramenta devo usar primeiro?",
                "answer": """
                Recomendamos começar pelo **Mapa Principal** para ter uma visão geral do estado.
                Depois, use **Explorar Dados** para rankings e comparações. O **Bagacinho IA** é
                excelente para consultas rápidas em qualquer momento!
                """
            },
            {
                "question": "Os dados podem ser exportados?",
                "answer": """
                Sim! A maioria das ferramentas permite exportar:

                - **Mapas**: Formato HTML interativo
                - **Dados tabulares**: CSV e Excel
                - **Gráficos**: Imagens PNG (use botão de câmera do Plotly)
                - **Análises**: Tabelas completas com todos os municípios
                """
            },
            {
                "question": "Como citar o CP2B Maps em trabalhos acadêmicos?",
                "answer": """
                Sugestão de citação:

                **CP2B Maps V2** - Plataforma de Análise de Potencial de Geração de Biogás para
                Municípios Paulistas. (2025). CP2B Research Team. Financiamento FAPESP 2024/01112-1.

                Sempre mencione o **cenário utilizado** (Pessimista/Realista/Otimista/Utópico) ao
                citar valores numéricos.
                """
            },
            {
                "question": "A plataforma é acessível?",
                "answer": """
                Sim! O CP2B Maps segue padrões **WCAG 2.1 Nível A**:

                - ✅ Navegação completa por teclado (Tab, Enter, Setas)
                - ✅ Compatível com leitores de tela (NVDA, JAWS, ORCA, VoiceOver)
                - ✅ Contraste adequado e texto alternativo em gráficos
                - ✅ Estrutura semântica com marcos ARIA

                Ative o "Modo Leitor de Tela" na barra lateral para melhor experiência.
                """
            }
        ]

        for faq in faqs:
            with st.expander(faq["question"], expanded=False):
                st.markdown(faq["answer"])

    except Exception as e:
        logger.error(f"Error rendering FAQ section: {e}", exc_info=True)
        st.error("Erro ao carregar perguntas frequentes.")


def render_research_scenarios() -> None:
    """Render research scenarios section"""
    try:
        st.markdown("""
        <h2 style='color: #2c3e50; font-weight: 600; margin-top: 4rem; margin-bottom: 1rem;
                   border-bottom: 3px solid #2E8B57; padding-bottom: 0.75rem;'>
            🔬 Cenários de Pesquisa
        </h2>
        <p style='color: #6c757d; font-size: 1.1rem; line-height: 1.8; margin-bottom: 2rem;'>
            Exemplos de como pesquisadores podem usar o CP2B Maps
        </p>
        """, unsafe_allow_html=True)

        scenarios = [
            {
                "title": "📝 TCC/Dissertação sobre Biogás",
                "description": "Use **Explorar Dados** para estatísticas descritivas, **Análises Avançadas** para composição por substrato, e **Referências Científicas** para embasamento teórico. Exporte gráficos e tabelas para seu trabalho.",
                "tools": ["🔍 Explorar Dados", "📊 Análises Avançadas", "📚 Referências"]
            },
            {
                "title": "🏭 Estudo de Viabilidade Técnica",
                "description": "Use **Análise de Proximidade** para avaliar potencial agregado em raio de coleta, **Mapa Principal** com camadas de infraestrutura (gasodutos, linhas elétricas), e **MapBiomas** para uso do solo.",
                "tools": ["🎯 Proximidade", "🗺️ Mapa", "🔍 Explorar Dados"]
            },
            {
                "title": "🌍 Análise de Impacto Ambiental",
                "description": "Foque em **redução de CO₂** usando filtros de potencial de mitigação. Compare cenários diferentes e analise distribuição regional de impacto ambiental.",
                "tools": ["🔍 Explorar Dados", "📊 Análises Avançadas", "🍊 Bagacinho IA"]
            }
        ]

        for scenario in scenarios:
            st.markdown(f"""
            <div style='background: #f8f9fa; border-left: 4px solid #2E8B57; padding: 1.5rem;
                        margin-bottom: 1.5rem; border-radius: 8px;'>
                <h3 style='color: #2c3e50; margin: 0 0 0.75rem 0; font-size: 1.2rem;'>
                    {scenario['title']}
                </h3>
                <p style='color: #6c757d; margin: 0 0 1rem 0; line-height: 1.7;'>
                    {scenario['description']}
                </p>
                <div style='font-size: 0.9rem; color: #6c757d;'>
                    <strong>Ferramentas sugeridas:</strong> {' | '.join(scenario['tools'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering research scenarios: {e}", exc_info=True)
        st.error("Erro ao carregar cenários de pesquisa.")


def render_getting_started_cta() -> None:
    """Render call-to-action section"""
    try:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2E8B57 0%, #228B22 100%);
                    color: white; padding: 2.5rem; border-radius: 12px; text-align: center;
                    margin: 4rem 0 2rem 0; box-shadow: 0 4px 12px rgba(46,139,87,0.3);'>
            <h2 style='margin: 0 0 1rem 0; font-weight: 600; font-size: 1.8rem;'>
                🚀 Pronto para Começar?
            </h2>
            <p style='margin: 0 0 1.5rem 0; font-size: 1.1rem; opacity: 0.95; line-height: 1.7;'>
                Explore as ferramentas acima para análises profissionais de potencial de biogás.<br>
                Todas as funcionalidades estão acessíveis nas abas superiores.
            </p>
            <div style='font-size: 0.95rem; opacity: 0.9;'>
                💡 Dica: Use <strong>Ctrl+F</strong> para buscar municípios específicos nos gráficos e tabelas
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error rendering CTA: {e}", exc_info=True)
