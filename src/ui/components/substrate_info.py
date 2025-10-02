"""
Substrate Information Component for CP2B Maps V2
Educational component showing biogas potential from different substrates
SOLID: Single Responsibility - Display substrate technical information
"""

import streamlit as st
from typing import Dict, Any
from src.data.references import render_reference_button
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_substrate_panel(substrate_data: Dict[str, Any]) -> None:
    """
    Render individual substrate information panel

    Args:
        substrate_data: Dictionary with substrate parameters
    """
    with st.expander(f"{substrate_data['icon']} {substrate_data['name']}", expanded=False):
        # Key metrics in 3 columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Potencial CH₄",
                substrate_data['methane'],
                help="m³ de metano por tonelada de matéria seca"
            )

        with col2:
            st.metric(
                "Relação C/N",
                substrate_data['cn_ratio'],
                help="Razão Carbono/Nitrogênio ideal para digestão anaeróbica"
            )

        with col3:
            st.metric(
                "Umidade",
                substrate_data['moisture'],
                help="Percentual de umidade típico do substrato"
            )

        # Description
        st.info(substrate_data['description'])

        # Technical parameters
        with st.expander("⚙️ Parâmetros Técnicos"):
            st.markdown(f"**Tempo de Retenção Hidráulica:** {substrate_data['retention_time']}")
            st.markdown(f"**Temperatura Ideal:** {substrate_data.get('temperature', '35-55°C')}")
            st.markdown(f"**pH Ótimo:** {substrate_data.get('ph', '6.8-7.4')}")

        # Scientific reference
        if 'reference_id' in substrate_data:
            st.markdown("**📚 Referência Científica:**")
            render_reference_button(
                substrate_data['reference_id'],
                compact=False,
                label="Ver Artigo Completo"
            )


def render_agricultural_substrates() -> None:
    """Render agricultural substrates section"""
    st.markdown("### 🌾 Substratos Agrícolas")

    substrates = [
        {
            'icon': '🥤',
            'name': 'Bagaço de Cana-de-Açúcar',
            'methane': '175 m³/ton',
            'cn_ratio': '50-80',
            'moisture': '48-52%',
            'retention_time': '20-30 dias',
            'reference_id': 'sugarcane_bagasse',
            'description': 'Alto potencial energético. Requer pré-tratamento devido ao conteúdo de lignina.'
        },
        {
            'icon': '🌽',
            'name': 'Palha de Milho',
            'methane': '225 m³/ton',
            'cn_ratio': '60-80',
            'moisture': '10-15%',
            'retention_time': '25-35 dias',
            'reference_id': 'corn_straw',
            'description': 'Excelente substrato com alta disponibilidade sazonal. Ideal para co-digestão.'
        },
        {
            'icon': '☕',
            'name': 'Casca de Café',
            'methane': '150-200 m³/ton',
            'cn_ratio': '25-35',
            'moisture': '70-80%',
            'retention_time': '20-30 dias',
            'reference_id': 'coffee_husk',
            'description': 'Resíduo abundante em SP. Boa relação C/N para digestão anaeróbica.'
        },
        {
            'icon': '🍊',
            'name': 'Resíduos de Citros',
            'methane': '80-150 m³/ton',
            'cn_ratio': '15-25',
            'moisture': '85-90%',
            'retention_time': '15-25 dias',
            'reference_id': 'citrus_waste',
            'description': 'Requer neutralização de ácidos cítricos. Alto conteúdo de d-limoneno.'
        },
        {
            'icon': '🌱',
            'name': 'Resíduos de Soja',
            'methane': '200-250 m³/ton',
            'cn_ratio': '20-30',
            'moisture': '12-15%',
            'retention_time': '20-28 dias',
            'reference_id': 'soybean_residue',
            'description': 'Excelente relação C/N. Alta produção de metano por unidade de massa.'
        }
    ]

    for substrate in substrates:
        render_substrate_panel(substrate)


def render_livestock_substrates() -> None:
    """Render livestock substrates section"""
    st.markdown("### 🐄 Substratos Pecuários")

    substrates = [
        {
            'icon': '🐮',
            'name': 'Esterco Bovino',
            'methane': '225 m³/cabeça/ano',
            'cn_ratio': '18-25',
            'moisture': '85-90%',
            'retention_time': '20-30 dias',
            'reference_id': 'biogas_calculation',
            'description': 'Substrato mais utilizado no Brasil. Base ideal para co-digestão com resíduos agrícolas.'
        },
        {
            'icon': '🐷',
            'name': 'Esterco Suíno',
            'methane': '210 m³/cabeça/ano',
            'cn_ratio': '12-18',
            'moisture': '90-95%',
            'retention_time': '15-25 dias',
            'reference_id': 'biogas_calculation',
            'description': 'Alta carga orgânica. Excelente para biodigestores de pequeno e médio porte.'
        },
        {
            'icon': '🐔',
            'name': 'Cama de Aviário',
            'methane': '34 m³/cabeça/ano',
            'cn_ratio': '15-20',
            'moisture': '25-35%',
            'retention_time': '18-25 dias',
            'reference_id': 'biogas_calculation',
            'description': 'Alto teor de nitrogênio. Requer mistura com substratos carbonosos para balancear C/N.'
        }
    ]

    for substrate in substrates:
        render_substrate_panel(substrate)


def render_codigestion_info() -> None:
    """Render co-digestion information section"""
    st.markdown("### ⚗️ Co-digestão de Substratos")

    st.info("""
    **Co-digestão** é a digestão anaeróbica simultânea de dois ou mais substratos,
    visando balancear a relação C/N e aumentar a produção de metano.
    """)

    codigestion_examples = [
        {
            'icon': '🌽🐄',
            'name': 'Milho + Esterco Bovino',
            'methane': '+22.4% CH₄',
            'cn_ratio': '20-30 (ótimo)',
            'moisture': '70-80%',
            'retention_time': '25-30 dias',
            'reference_id': 'corn_cattle_codigestion',
            'description': 'Combinação ideal: alta carga carbonosa do milho equilibra nitrogênio do esterco.'
        },
        {
            'icon': '🥤🐄',
            'name': 'Vinhaça + Esterco Bovino',
            'methane': '54-83% redução DQO',
            'cn_ratio': '25-35',
            'moisture': '92-96%',
            'retention_time': '20-28 dias',
            'reference_id': 'vinasse_cattle_codigestion',
            'description': 'Vinhaça da produção de etanol + esterco. Alta eficiência na redução de DQO.'
        },
        {
            'icon': '☕🐄',
            'name': 'Café + Esterco Bovino',
            'methane': '+15-20% CH₄',
            'cn_ratio': '22-28',
            'moisture': '75-82%',
            'retention_time': '22-28 dias',
            'reference_id': 'coffee_cattle_codigestion',
            'description': 'Resíduos de café balanceiam relação C/N do esterco bovino. Reduz acidez do café.'
        }
    ]

    for example in codigestion_examples:
        render_substrate_panel(example)

    # C/N ratio calculator info
    st.markdown("---")
    st.markdown("#### 📊 Relação C/N Ótima")

    col1, col2 = st.columns(2)
    with col1:
        st.success("**Faixa Ideal:** 20-30:1")
        st.caption("Melhor equilíbrio para digestão anaeróbica")

    with col2:
        st.warning("**Problemas:**")
        st.caption("C/N < 20: Acúmulo de amônia (inibição)")
        st.caption("C/N > 30: Crescimento bacteriano lento")


def render_substrate_information() -> None:
    """
    Main function to render complete substrate information interface
    Single responsibility: Organize and display substrate educational content
    """
    try:
        st.markdown("## 🧪 Informações sobre Substratos para Biogás")

        # Tabs for organization
        tab1, tab2, tab3 = st.tabs([
            "🌾 Agrícola",
            "🐄 Pecuário",
            "⚗️ Co-digestão"
        ])

        with tab1:
            render_agricultural_substrates()

        with tab2:
            render_livestock_substrates()

        with tab3:
            render_codigestion_info()

        logger.debug("Substrate information rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering substrate information: {e}", exc_info=True)
        st.error("⚠️ Erro ao carregar informações de substratos")
