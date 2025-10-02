"""
CP2B Maps V2 - V1-Style References Page
Pixel-perfect match with V1 reference structure
"""

import streamlit as st
from src.data.references.scientific_references import render_reference_button
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_references_v1_page():
    """Render V1-style references page with category tabs"""

    st.title("📚 Referências Científicas")

    # Header
    st.markdown("""
    ### 🎯 Base Científica do CP2B Maps

    Esta página compila todas as **referências acadêmicas** utilizadas no sistema CP2B Maps.
    Cada valor, fator de conversão e metodologia apresentada possui respaldo científico de
    **pesquisas revisadas por pares**.

    **📖 Categorias de Referências:**
    """)

    # Category tabs
    ref_tabs = st.tabs([
        "🌾 Substratos Agrícolas",
        "🐄 Resíduos Pecuários",
        "⚗️ Co-digestão",
        "🗺️ Fontes de Dados",
        "🔬 Metodologias",
        "📋 Todas as Referências"
    ])

    with ref_tabs[0]:  # Agricultural
        st.markdown("### 🌾 Substratos Agrícolas")
        st.markdown("Pesquisas sobre potencial de biogás de resíduos de culturas:")
        _render_category_refs("agricultural")

    with ref_tabs[1]:  # Livestock
        st.markdown("### 🐄 Resíduos Pecuários")
        st.markdown("Estudos sobre dejetos animais e produção de metano:")
        _render_category_refs("livestock")

    with ref_tabs[2]:  # Co-digestion
        st.markdown("### ⚗️ Co-digestão")
        st.markdown("Pesquisas sobre misturas de substratos:")
        _render_category_refs("codigestion")

    with ref_tabs[3]:  # Data Sources
        st.markdown("### 🗺️ Fontes de Dados")
        st.markdown("Bases de dados utilizadas:")
        _render_data_sources()

    with ref_tabs[4]:  # Methodologies
        st.markdown("### 🔬 Metodologias")
        st.markdown("Métodos de cálculo e estimativa:")
        _render_methodologies()

    with ref_tabs[5]:  # All
        st.markdown("### 📋 Todas as Referências")
        st.markdown("Lista completa ordenada alfabeticamente:")
        _render_all_refs()

    # Search
    st.markdown("---")
    st.markdown("### 🔍 Buscar Referências")
    search_query = st.text_input(
        "Digite palavras-chave:",
        placeholder="Ex: cana, metano, digestão anaeróbia..."
    )
    if search_query:
        _render_search_results(search_query)


def _render_category_refs(category: str):
    """Render references by category"""
    # Simplified - show key references
    refs = {
        "agricultural": [
            ("Bagaço de Cana-de-açúcar", "sugarcane_bagasse"),
            ("Palha de Soja", "soybean_straw"),
            ("Resíduos de Milho", "corn_straw"),
            ("Casca de Café", "coffee_husk"),
            ("Bagaço de Citros", "citrus_bagasse"),
        ],
        "livestock": [
            ("Dejetos Bovinos", "biogas_calculation"),
            ("Dejetos Suínos", "biogas_calculation"),
            ("Cama de Frango", "biogas_calculation"),
        ],
        "codigestion": [
            ("Co-digestão Geral", "biogas_calculation"),
        ]
    }

    for title, ref_id in refs.get(category, []):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{title}**")
        with col2:
            render_reference_button(ref_id, compact=True)
        st.markdown("---")


def _render_data_sources():
    """Render data sources"""
    st.markdown("""
    - **IBGE**: Instituto Brasileiro de Geografia e Estatística
    - **MapBiomas**: Projeto MapBiomas Coleção 9
    - **CETESB**: Companhia Ambiental do Estado de São Paulo
    - **EPE**: Empresa de Pesquisa Energética
    """)


def _render_methodologies():
    """Render methodologies"""
    st.markdown("""
    #### Cálculo de Potencial de Biogás

    A metodologia segue padrões internacionais:

    1. **Produção de resíduos**: Dados do IBGE (agricultura, pecuária)
    2. **Fatores de conversão**: Literatura científica revisada
    3. **Potencial de metano**: m³ CH₄/ton resíduo
    4. **Biogás total**: Conversão de CH₄ para biogás (60-70% CH₄)

    **Referências Metodológicas:**
    - Digestão Anaeróbia: VDI 4630 (Alemanha)
    - Potencial BMP: ISO/DIS 11734
    """)


def _render_all_refs():
    """Render all references"""
    st.info("📚 Consulte as abas por categoria para acessar todas as referências organizadas por tema.")


def _render_search_results(query: str):
    """Render search results"""
    st.info(f"Buscando por: **{query}**")
    st.markdown("Funcionalidade de busca em desenvolvimento.")
