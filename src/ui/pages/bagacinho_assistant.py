"""
CP2B Maps V2 - Bagacinho AI Assistant Page
Full-page AI chatbot interface with RAG and Gemini integration
WCAG 2.1 Level A compliant
"""

import html
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

from src.utils.logging_config import get_logger
from src.accessibility.components.accessible_components import (
    accessible_button,
    create_accessible_alert
)

logger = get_logger(__name__)

# Try importing AI modules
try:
    from src.ai.gemini_integration import query_gemini, check_gemini_connection
    HAS_GEMINI = True
    logger.info("Gemini integration loaded successfully")
except ImportError as e:
    HAS_GEMINI = False
    logger.warning(f"Gemini integration not available: {e}")

try:
    from src.ai.bagacinho_rag import BagacinhoRAG
    HAS_RAG = True
    logger.info("BagacinhoRAG loaded successfully")
except ImportError as e:
    HAS_RAG = False
    logger.warning(f"BagacinhoRAG not available: {e}")


# ============================================================================
# DATABASE CONTEXT PREPARATION WITH CACHING
# ============================================================================

@st.cache_resource
def get_rag_instance() -> Optional['BagacinhoRAG']:
    """
    Get or create cached RAG instance

    Returns:
        BagacinhoRAG instance or None if not available
    """
    if not HAS_RAG:
        logger.warning("RAG not available")
        return None

    try:
        # FIXED: Correct database path
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "database" / "cp2b_maps.db"
        rag = BagacinhoRAG(db_path=db_path)
        logger.info("✓ RAG instance initialized (cached)")
        return rag
    except Exception as e:
        logger.error(f"Failed to initialize BagacinhoRAG: {e}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def prepare_database_context() -> str:
    """
    Prepare comprehensive context about the CP2B biogas database (cached to avoid repeated DB calls)

    Returns:
        Context string from database
    """
    context_parts = []

    # 1. System Overview
    context_parts.append("""
# CP2B Maps - Sistema de Análise de Potencial de Biogás

## Visão Geral
O CP2B Maps é uma plataforma WebGIS desenvolvida pelo Centro Paulista de Estudos em Biogás e Bioprodutos (UNICAMP).
O sistema analisa o potencial de produção de biogás a partir de resíduos orgânicos em 645 municípios do estado de São Paulo.

## Fontes de Resíduos
O sistema calcula o potencial de biogás de três categorias principais:

### 1. Resíduos Agrícolas
- **Cana-de-açúcar**: Bagaço e vinhaça da produção de etanol e açúcar
- **Soja**: Resíduos de colheita e processamento
- **Milho**: Restos de colheita e sabugo
- **Café**: Casca e polpa do beneficiamento
- **Citros**: Bagaço de laranja e cascas da indústria de suco

### 2. Resíduos Pecuários
- **Bovinos**: Esterco de gado de corte e leite
- **Suínos**: Dejetos de criações confinadas
- **Aves**: Cama de frango de corte e poedeiras
- **Piscicultura**: Resíduos de aquicultura

### 3. Resíduos Urbanos
- **RSU**: Resíduos Sólidos Urbanos orgânicos
- **RPO**: Resíduos de Poda e capina

## Unidades
- Potencial de biogás: Nm³/ano (Normal metros cúbicos por ano)
- População: Habitantes (Censo 2022)
- Área: km²
""")

    # 2. Get database statistics
    try:
        # FIXED: Use correct database path
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "database" / "cp2b_maps.db"
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get basic statistics
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_municipios,
                        SUM(total_final_m_ano) as potencial_total,
                        SUM(total_agricola_m_ano) as potencial_agricola,
                        SUM(total_pecuaria_m_ano) as potencial_pecuaria,
                        AVG(total_final_m_ano) as media_municipal,
                        MAX(total_final_m_ano) as maior_potencial,
                        SUM(populacao_2022) as populacao_total
                    FROM municipalities
                """)

                stats = cursor.fetchone()
                if stats:
                    context_parts.append(f"""
## Estatísticas do Banco de Dados

### Dados Gerais
- **Total de Municípios**: {stats[0]:,}
- **População Total**: {stats[6]:,} habitantes
- **Potencial Total de Biogás**: {stats[1]:,.0f} Nm³/ano
- **Potencial Agrícola**: {stats[2]:,.0f} Nm³/ano ({stats[2]/stats[1]*100:.1f}%)
- **Potencial Pecuário**: {stats[3]:,.0f} Nm³/ano ({stats[3]/stats[1]*100:.1f}%)
- **Média por Município**: {stats[4]:,.0f} Nm³/ano
- **Maior Potencial Municipal**: {stats[5]:,.0f} Nm³/ano
""")

                # Get top municipalities
                cursor.execute("""
                    SELECT nome_municipio, total_final_m_ano, populacao_2022
                    FROM municipalities
                    ORDER BY total_final_m_ano DESC
                    LIMIT 10
                """)

                top_cities = cursor.fetchall()
                if top_cities:
                    context_parts.append("\n### Top 10 Municípios por Potencial de Biogás\n")
                    for i, (nome, potencial, pop) in enumerate(top_cities, 1):
                        context_parts.append(
                            f"{i}. **{nome}**: {potencial:,.0f} Nm³/ano (Pop: {pop:,})\n"
                        )

    except Exception as e:
        logger.error(f"Erro ao preparar contexto do banco: {e}")
        context_parts.append("\n⚠️ Erro ao acessar estatísticas do banco de dados.\n")

    # 3. Technical Information
    context_parts.append("""
## Informações Técnicas

### Fatores de Conversão
O sistema utiliza fatores de conversão validados pela literatura científica para calcular
o potencial de biogás a partir das quantidades de resíduos produzidos.

### Metodologia
A metodologia segue padrões internacionais de cálculo de potencial de biogás, considerando:
- Produção anual de resíduos por fonte
- Fatores de conversão (m³ CH₄/ton de resíduo)
- Potencial de metano como proxy para biogás (60-70% CH₄)

### Referências Científicas
O projeto é financiado pela FAPESP (processo 2024/01112-1) e utiliza dados de:
- IBGE (população, agricultura, pecuária)
- CETESB (resíduos urbanos)
- MapBiomas (uso do solo)
- Literatura científica peer-reviewed
""")

    return "\n".join(context_parts)


# ============================================================================
# AI QUERY LOGIC
# ============================================================================

def check_ai_connection(provider: str = "auto") -> Tuple[bool, str, str]:
    """
    Check if AI provider is available

    Args:
        provider: "gemini" or "auto" (auto-detect)

    Returns:
        Tuple of (is_connected, message, selected_provider)
    """
    # Only Gemini supported in V2 for now
    if HAS_GEMINI:
        is_connected, msg = check_gemini_connection()
        if is_connected:
            return True, msg, "gemini"

    return False, "❌ Nenhum provedor de IA disponível. Configure Gemini API.", "none"


def query_ai(
    question: str,
    context: str = "",
    conversation_history: Optional[List[Dict]] = None,
    use_rag: bool = True,
    provider: str = "gemini"
) -> Tuple[str, bool]:
    """
    Query AI provider (Gemini) with a question and context.

    Args:
        question: User's question
        context: Database context to provide (used as fallback if RAG fails)
        conversation_history: Previous messages for context
        use_rag: Whether to use RAG for dynamic context retrieval (default: True)
        provider: AI provider to use - only "gemini" supported in V2

    Returns:
        Tuple of (answer, success)
    """
    if provider != "gemini" or not HAS_GEMINI:
        return "Erro: Integração Gemini não disponível.", False

    # Get RAG context if enabled
    final_context = context
    if use_rag and HAS_RAG:
        try:
            rag = get_rag_instance()
            if rag:
                rag_context = rag.construir_contexto(question)
                if rag_context:
                    final_context = rag_context
                logger.info(f"RAG context generated for Gemini query")
        except Exception as e:
            logger.warning(f"RAG failed for Gemini, using static context: {e}")

    # Query Gemini
    return query_gemini(
        question=question,
        db_context=final_context,
        conversation_history=conversation_history
    )


# ============================================================================
# FULL-PAGE CHATBOT UI
# ============================================================================

@st.fragment
def chat_interface():
    """Chat interface as a fragment to avoid full page reload"""
    # AI Provider check
    if 'ai_provider_fullpage' not in st.session_state:
        st.session_state.ai_provider_fullpage = "gemini"

    # Check connection
    is_connected, status_msg, active_provider = check_ai_connection(st.session_state.ai_provider_fullpage)

    if not is_connected:
        create_accessible_alert(
            "❌ Assistente indisponível. Configure Gemini API para utilizar o Bagacinho IA.",
            "error"
        )

        # Instructions
        st.markdown("""
        ### Como Configurar o Gemini API

        1. Obtenha sua chave API gratuita em: https://makersuite.google.com/app/apikey
        2. Adicione no arquivo `.streamlit/secrets.toml`:
           ```toml
           GEMINI_API_KEY = "sua-chave-aqui"
           ```
        3. Ou defina a variável de ambiente `GEMINI_API_KEY`
        4. Reinicie a aplicação
        """)
        return

    st.divider()

    # Initialize session state with greeting
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Olá! Vamos falar sobre a Cana? 🍊"
        })

    if 'db_context' not in st.session_state:
        with st.spinner("Preparando contexto..."):
            st.session_state.db_context = prepare_database_context()

    # Hide form buttons
    st.markdown("""
    <style>
    /* Hide form buttons */
    div[data-testid="stForm"] button[kind="formSubmit"] {
        display: none !important;
    }
    /* Make chat container scrollable */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Chat messages area with bubbles
    chat_container = st.container()

    with chat_container:
        # Display chat history with beautiful bubbles
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                # User message bubble (right-aligned, light green)
                safe_content = html.escape(msg['content']).replace('\n', '<br>')
                st.markdown(f"""
                <div style='margin: 1rem 0; display: flex; justify-content: flex-end;'>
                    <div style='background: #DCF8C6; color: #000; padding: 1rem 1.2rem;
                                border-radius: 18px 18px 4px 18px; max-width: 70%;
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-size: 1rem;
                                word-wrap: break-word; line-height: 1.5;'>
                        {safe_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Bagacinho message bubble (left-aligned, white)
                safe_content = html.escape(msg['content']).replace('\n', '<br>')
                st.markdown(f"""
                <div style='margin: 1rem 0; display: flex; justify-content: flex-start;'>
                    <div style='background: #FFFFFF; color: #000; padding: 1rem 1.2rem;
                                border-radius: 18px 18px 18px 4px; max-width: 70%;
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-size: 1rem;
                                border: 1px solid #E5E5EA; word-wrap: break-word; line-height: 1.5;'>
                        <strong style='color: #FF8C00; font-size: 1.1rem;'>🍊 Bagacinho IA:</strong><br><br>
                        {safe_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Spacer before input
    st.markdown("<br>" * 2, unsafe_allow_html=True)

    # Input area at bottom
    st.markdown("""
    <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 12px;
                border: 2px solid #e0e0e0; margin-top: 2rem;'>
    </div>
    """, unsafe_allow_html=True)

    # Input form
    with st.form(key="chat_form_fullpage", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])

        with col1:
            user_input = st.text_area(
                "Mensagem",
                key="chat_input_full",
                placeholder="Digite sua pergunta e pressione Ctrl+Enter para enviar...",
                height=100,
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <p style='font-size: 0.85rem; color: #666; margin: 0;'>
                    Pressione<br>
                    <strong style='color: #25D366;'>Ctrl + Enter</strong><br>
                    para enviar
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Hidden submit button
        submitted = st.form_submit_button("send")

    # Handle submission
    if submitted and user_input.strip():
        with st.spinner("🍊 Bagacinho IA está pensando..."):
            answer, success = query_ai(
                question=user_input,
                context=st.session_state.db_context,
                conversation_history=st.session_state.chat_history,
                provider=active_provider
            )

            if success:
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
                # Force a rerun to show the new messages (fragment will handle this)
                st.rerun()
            else:
                create_accessible_alert(f"Erro: {answer}", "error")


def render_bagacinho_page() -> None:
    """
    Main page render function with header and chat interface
    """
    # Modern header with green gradient
    st.markdown("""
    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
                color: white; padding: 2.5rem; margin: -1rem -1rem 0 -1rem;
                text-align: center; border-radius: 0 0 25px 25px;
                box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);'>
        <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; font-family: "Montserrat", sans-serif;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
            🍊 Bagacinho IA
        </h1>
        <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
            Assistente IA Especialista em Biogás do CP2B Maps
        </p>
        <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.85;'>
            🤖 Gemini AI • 📊 RAG • 🔬 Análise Científica
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add spacing after header
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Render chat interface as fragment
    chat_interface()
