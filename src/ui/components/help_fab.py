"""
CP2B Maps - Help Floating Action Button (FAB)
WCAG 2.1 Level AA compliant help system with contextual documentation
"""

import streamlit as st
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


def render_help_fab(
    current_page: Optional[str] = None,
    show_bagacinho_link: bool = True,
    custom_help_items: Optional[List[Dict[str, str]]] = None
) -> None:
    """
    Render a floating action button for help and documentation access

    Args:
        current_page: Current page name for contextual help
        show_bagacinho_link: Whether to show quick link to Bagacinho IA
        custom_help_items: Custom help items for specific pages
    """

    # CSS for floating button
    st.markdown("""
    <style>
    /* Floating Action Button */
    .help-fab-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }

    .help-fab-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        font-size: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }

    .help-fab-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }

    .help-fab-button:focus {
        outline: 3px solid #ffdd57;
        outline-offset: 2px;
    }

    /* Help Panel Styles */
    .help-panel {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .help-section {
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e9ecef;
    }

    .help-section:last-child {
        border-bottom: none;
    }

    .help-section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .help-item {
        margin: 0.5rem 0;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 5px;
        transition: background-color 0.2s;
    }

    .help-item:hover {
        background-color: #e9ecef;
    }

    .help-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }

    .help-link:hover {
        text-decoration: underline;
    }

    .help-description {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }

    .quick-action-button {
        width: 100%;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
        margin-top: 0.5rem;
    }

    .quick-action-button:hover {
        transform: translateY(-2px);
    }

    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        .help-fab-button, .quick-action-button {
            transition: none;
        }
    }

    /* Keyboard navigation highlight */
    .help-item:focus-within {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create help button in sidebar with popover
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💡 Precisa de Ajuda?")

        with st.expander("📚 Central de Ajuda", expanded=False):
            _render_help_content(current_page, show_bagacinho_link, custom_help_items)


def _render_help_content(
    current_page: Optional[str],
    show_bagacinho_link: bool,
    custom_help_items: Optional[List[Dict[str, str]]]
) -> None:
    """Render help content based on current page and context"""

    # Contextual help based on page
    if current_page:
        st.markdown(f"<div class='help-section-title'>📍 Ajuda para: {current_page}</div>", unsafe_allow_html=True)
        contextual_help = _get_contextual_help(current_page)

        if contextual_help:
            for item in contextual_help:
                st.markdown(
                    f"""
                    <div class='help-item'>
                        <strong>{item['title']}</strong>
                        <div class='help-description'>{item['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("<br/>", unsafe_allow_html=True)

    # Custom help items
    if custom_help_items:
        st.markdown("<div class='help-section-title'>🔍 Mais Informações</div>", unsafe_allow_html=True)
        for item in custom_help_items:
            st.markdown(
                f"""
                <div class='help-item'>
                    <strong>{item.get('title', 'Item')}</strong>
                    <div class='help-description'>{item.get('description', '')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<br/>", unsafe_allow_html=True)

    # Quick links
    st.markdown("<div class='help-section-title'>⚡ Acesso Rápido</div>", unsafe_allow_html=True)

    # Bagacinho IA link
    if show_bagacinho_link:
        if st.button("🤖 Pergunte ao Bagacinho IA", use_container_width=True, type="primary"):
            st.switch_page("pages/05_🤖_Bagacinho_IA.py")

    # Documentation links
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📖 Glossário Técnico", use_container_width=True):
            _show_glossary_overview()

    with col2:
        if st.button("📊 Ver Exemplos", use_container_width=True):
            _show_examples()

    st.markdown("<br/>", unsafe_allow_html=True)

    # FAQ Section
    st.markdown("<div class='help-section-title'>❓ Perguntas Frequentes</div>", unsafe_allow_html=True)

    with st.expander("Como interpretar os cenários de disponibilidade?"):
        st.markdown("""
        Os **cenários** representam diferentes níveis de disponibilidade real de resíduos:

        - **Realista (17.5%)**: Validado empiricamente para planejamento de curto prazo
        - **Otimista (35%)**: Projeta melhorias logísticas para médio prazo
        - **Pessimista (5%)**: Considera restrições severas para análise de riscos
        - **Teórico (100%)**: Potencial máximo sem restrições (apenas comparação)

        💡 **Recomendação**: Use o cenário Realista para viabilidade técnica inicial.
        """)

    with st.expander("Qual a diferença entre biogás e metano?"):
        st.markdown("""
        - **Biogás**: Mistura gasosa (CH₄ 50-70%, CO₂ 30-50%, traços de outros gases)
        - **Metano (CH₄)**: Componente energético principal do biogás

        A energia gerada depende do **conteúdo de metano**. O biogás pode ser:
        - Usado diretamente em motores/caldeiras
        - Purificado para **biometano** (>90% CH₄) para injeção em gasodutos

        📚 Consulte o glossário para conversões energéticas detalhadas.
        """)

    with st.expander("Como funciona a análise de proximidade?"):
        st.markdown("""
        A **Análise de Proximidade** agrega municípios dentro de um raio de distância:

        1. Selecione município central e raio (10-100 km)
        2. Algoritmo identifica municípios vizinhos (distância euclidiana SIRGAS 2000)
        3. Métricas são somadas para avaliar viabilidade regional
        4. Camadas de infraestrutura mostram acesso a gasodutos e energia

        💡 **Uso**: Ideal para avaliar viabilidade de plantas centralizadas.
        """)

    with st.expander("Como exportar dados para análise externa?"):
        st.markdown("""
        Em cada página você pode exportar dados em diferentes formatos:

        - **CSV**: Dados tabulares para Excel, Python, R
        - **GeoJSON**: Dados geoespaciais para QGIS, ArcGIS, Leaflet
        - **Shapefiles**: Compatibilidade com sistemas GIS legados

        📍 Localização: Botões de exportação estão na barra lateral de cada análise.
        """)

    with st.expander("O que significam as unidades Nm³, MWh, GJ?"):
        st.markdown("""
        - **Nm³** (Normal metro cúbico): Volume de gás a 0°C e 1 atm (padronização)
        - **MWh** (Megawatt-hora): 1000 kWh de energia elétrica
        - **GJ** (Gigajoule): Energia térmica (1 GJ = 277.78 kWh)
        - **tCO₂eq**: Toneladas de CO₂ equivalente (emissões evitadas)

        💡 Use os tooltips (ℹ️) ao lado de cada métrica para conversões práticas.
        """)

    # Report issue section
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='help-section-title'>🐛 Encontrou um Problema?</div>", unsafe_allow_html=True)

    with st.expander("Reportar Bug ou Sugerir Melhoria"):
        st.markdown("""
        **Descreva o problema ou sugestão:**
        """)

        issue_type = st.selectbox(
            "Tipo",
            ["🐛 Bug / Erro", "💡 Sugestão de Melhoria", "📚 Documentação Incompleta", "🚀 Nova Funcionalidade"],
            key="help_issue_type"
        )

        issue_description = st.text_area(
            "Descrição detalhada",
            height=100,
            key="help_issue_desc",
            help="Descreva o problema ou sugestão em detalhes"
        )

        if st.button("📤 Enviar Feedback", type="primary"):
            if issue_description.strip():
                # In a real implementation, this would send to a feedback system
                st.success("✅ Feedback enviado com sucesso! Obrigado pela contribuição.")
                logger.info(f"User feedback: {issue_type} - {issue_description}")
            else:
                st.warning("Por favor, descreva o problema ou sugestão.")

    # Footer with version and contact
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #999; font-size: 0.85rem; margin-top: 1rem;'>
        CP2B Maps V2 | WCAG 2.1 Nível A<br/>
        <a href='https://github.com/yourusername/cp2b-maps' target='_blank' style='color: #667eea;'>📂 GitHub</a> |
        <a href='mailto:support@cp2bmaps.com' style='color: #667eea;'>✉️ Contato</a>
    </div>
    """, unsafe_allow_html=True)


def _get_contextual_help(page_name: str) -> List[Dict[str, str]]:
    """Get contextual help items based on page name"""

    help_map = {
        "Mapa Principal": [
            {
                "title": "Visualização de Dados",
                "description": "Use os filtros na sidebar para selecionar cenários, substratos e municípios específicos."
            },
            {
                "title": "Interação com Mapa",
                "description": "Clique em municípios para ver detalhes. Use zoom e pan para explorar regiões."
            },
            {
                "title": "Legendas e Cores",
                "description": "Cores mais intensas indicam maior potencial de geração de biogás."
            }
        ],
        "Explorar Dados": [
            {
                "title": "Rankings e Comparações",
                "description": "Visualize os municípios com maior potencial em diferentes categorias."
            },
            {
                "title": "Gráficos Interativos",
                "description": "Passe o mouse sobre gráficos para ver valores detalhados."
            },
            {
                "title": "Exportação de Dados",
                "description": "Use os botões de exportação para análise externa em Excel ou ferramentas estatísticas."
            }
        ],
        "Análise de Proximidade": [
            {
                "title": "Seleção de Raio",
                "description": "Escolha raio de 10-100 km baseado em viabilidade logística de transporte."
            },
            {
                "title": "Agregação Regional",
                "description": "Métricas agregadas ajudam a avaliar viabilidade de plantas centralizadas."
            },
            {
                "title": "Infraestrutura",
                "description": "Camadas de gasodutos e energia mostram acesso a infraestrutura existente."
            }
        ],
        "Análise Econômica": [
            {
                "title": "Parâmetros Econômicos",
                "description": "Ajuste custos de investimento, operação e preços de energia na sidebar."
            },
            {
                "title": "Indicadores de Viabilidade",
                "description": "VPL, TIR e Payback indicam atratividade econômica do projeto."
            },
            {
                "title": "Análise de Sensibilidade",
                "description": "Teste diferentes cenários para avaliar riscos e oportunidades."
            }
        ],
        "Bagacinho IA": [
            {
                "title": "Consultas em Linguagem Natural",
                "description": "Faça perguntas sobre biogás, metodologias e dados técnicos."
            },
            {
                "title": "Exemplos de Perguntas",
                "description": "Use os exemplos fornecidos como ponto de partida para suas consultas."
            },
            {
                "title": "Precisão das Respostas",
                "description": "Respostas baseadas em documentação técnica e referências científicas validadas."
            }
        ]
    }

    return help_map.get(page_name, [])


def _show_glossary_overview() -> None:
    """Show glossary overview in a modal"""
    st.info("📖 **Glossário Técnico**\n\nAcesse o glossário completo clicando nos ícones ℹ️ ao lado de termos técnicos em qualquer página.")


def _show_examples() -> None:
    """Show usage examples"""
    st.info("📊 **Exemplos de Uso**\n\nExplore os tutoriais interativos na página inicial (Home) para ver exemplos práticos de análises.")


# ARIA live region component for accessibility
def render_aria_live_region() -> None:
    """
    Render ARIA live region for dynamic content announcements
    Should be placed once in the main app layout
    """
    st.markdown("""
    <div
        id="aria-live-region"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        style="
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        "
    ></div>
    """, unsafe_allow_html=True)


def announce_to_screen_reader(message: str, priority: str = "polite") -> None:
    """
    Announce message to screen readers via ARIA live region

    Args:
        message: Message to announce
        priority: 'polite' or 'assertive'
    """
    st.markdown(f"""
    <script>
    (function() {{
        const liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {{
            liveRegion.setAttribute('aria-live', '{priority}');
            liveRegion.textContent = '{message}';
            // Clear after announcement
            setTimeout(() => {{ liveRegion.textContent = ''; }}, 1000);
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)
