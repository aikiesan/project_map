"""
CP2B Maps V2 - V1-Style About Page
Pixel-perfect match with V1 structure
"""

import streamlit as st
from src.data.references.scientific_references import render_reference_button
from src.ui.components.substrate_info import render_substrate_information
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_about_v1_page():
    """Render V1-style About page with all sections"""

    st.title("ℹ️ Sobre o CP2B Maps")

    # 1. Contexto Institucional
    with st.expander("🏛️ Contexto Institucional do CP2B", expanded=True):
        st.subheader("Missão, Visão e Valores")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Missão**

            Desenvolver pesquisas, tecnologias e soluções inovadoras de biogás com motivação industrial, ambiental e social, que promovam o aproveitamento inteligente de resíduos para o desenvolvimento sustentável.
            """)

            st.markdown("""
            **🔮 Visão**

            Ser referência nacional e internacional na gestão eficiente e sustentável de resíduos urbanos e agropecuários, transformando o estado de São Paulo em vitrine de soluções inteligentes em biogás.
            """)

        with col2:
            st.markdown("""
            **⚖️ Valores**

            • Abordagem transdisciplinar como premissa para soluções inovadoras
            • Bioeconomia circular e valorização de resíduos
            • Compromisso com a agenda de descarbonização até 2050
            • Educação como instrumento de transformação social
            • Desenvolvimento de projetos com abordagem local e potencial de replicação
            """)

        st.subheader("📋 Plano de Trabalho (FAPESP 2024/01112-1)")
        st.markdown("""
        **Objetivo Geral**: Contribuir para a gestão de resíduos orgânicos e lignocelulósicos no Estado de São Paulo nos segmentos urbano e agroindustrial, com prioridade para as ações voltadas à gestão pública de resíduos e setores estratégicos para a economia do estado.

        **Entregáveis**: Publicações científicas, patentes, softwares (como este mapa), workshops, cursos de extensão universitária e capacitação de recursos humanos em todos os níveis.
        """)

    # 2. Fatores de Conversão
    with st.expander("⚙️ Fatores de Conversão e Metodologia"):
        st.subheader("Dados Técnicos")
        st.markdown("""
        Os fatores de conversão são calibrados com base em literatura científica e dados empíricos, considerando as condições específicas do Estado de São Paulo.
        """)

        st.markdown("#### 📊 Principais Fatores de Conversão")

        # Pecuária
        st.markdown("**🐄 Pecuária**")
        pecuaria_data = [
            ("Dejetos Bovinos", "225 m³/ano", "cabeça", "biogas_calculation"),
            ("Dejetos Suínos", "450-650 m³/ton", "ton MS", "biogas_calculation"),
            ("Cama de Frango", "180-280 m³/ton", "ton MS", "biogas_calculation")
        ]

        for substrate, potential, unit, ref_id in pecuaria_data:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"• {substrate}")
            with col2:
                st.write(potential)
            with col3:
                st.write(unit)
            with col4:
                render_reference_button(ref_id, compact=True)

        # Agricultura
        st.markdown("**🌾 Agricultura**")
        agricultura_data = [
            ("Bagaço de Cana", "175 m³/ton", "ton MS", "sugarcane_bagasse"),
            ("Palha de Cana", "200 m³/ton", "ton MS", "sugarcane_straw"),
            ("Palha de Soja", "160-220 m³/ton", "ton MS", "soybean_straw"),
            ("Palha de Milho", "200-260 m³/ton", "ton MS", "corn_straw"),
            ("Casca de Café", "150-200 m³/ton", "ton MS", "coffee_husk"),
            ("Bagaço de Citros", "80-150 m³/ton", "ton MS", "citrus_bagasse")
        ]

        for substrate, potential, unit, ref_id in agricultura_data:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"• {substrate}")
            with col2:
                st.write(potential)
            with col3:
                st.write(unit)
            with col4:
                render_reference_button(ref_id, compact=True)

        st.subheader("🧮 Exemplo de Cálculo: Dejetos Bovinos")
        st.code("""
Parâmetros:
- Produção: 10 kg/cabeça/dia
- Potencial: 150-300 m³ CH₄/ton MS (média: 225 m³)
- Disponibilidade: 6% (sistemas extensivos)

Cálculo:
1. Produção aproveitável: 10 kg/dia × 365 × 0,06 = 219 kg/ano = 0,219 ton/ano
2. Metano: 0,219 ton × 225 m³/ton = 49,3 m³ CH₄/ano
3. Biogás (55% CH₄): 49,3 ÷ 0,55 = 89,6 m³/ano
4. Fator final: 225 m³ biogás/cabeça/ano
        """)

    # 3. Referências
    with st.expander("📚 Referências Bibliográficas"):
        st.markdown("""
        ### Principais Referências Técnicas

        1. **Biogas production from agricultural biomass** - Smith et al. (2023)
        2. **Methane potential of organic waste in São Paulo** - Silva et al. (2022)
        3. **Anaerobic digestion of livestock waste** - Santos et al. (2023)
        4. **Bioenergy potential assessment methodology** - Oliveira et al. (2021)
        5. **Circular economy in waste management** - Costa et al. (2023)

        ### Normas e Padrões

        - **ABNT NBR 15849**: Resíduos sólidos urbanos - Aterros sanitários
        - **CONAMA 481/2017**: Critérios e procedimentos ambientais
        - **Lei 12.305/2010**: Política Nacional de Resíduos Sólidos
        """)

    # 4. Alinhamento Estratégico
    with st.expander("🎯 Contribuição para os Eixos do CP2B"):
        st.markdown("""
        ### Alinhamento com o Plano de Trabalho

        **Eixo 1 - Tecnologias**: Entregável de software, contribuindo para:
        - Desenvolvimento de ferramentas de apoio à decisão
        - Transferência de tecnologia para gestores públicos
        - Capacitação em análise de dados geoespaciais

        **Eixo 2 - Gestão**: Tomada de decisão para políticas públicas:
        - Mapeamento do potencial de biogás municipal
        - Priorização de investimentos em infraestrutura
        - Identificação de oportunidades PPP

        **Indicadores**:
        - Publicações científicas
        - Workshops e cursos
        - Parcerias público-privadas
        - Consultoria para projetos
        """)

    # 5. Sobre o Aplicativo
    with st.expander("🛠️ Sobre o Aplicativo"):
        st.subheader("Funcionalidades Principais")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **📊 Dados Analisados**:
            - **Agrícolas**: Cana, soja, milho, café, citros
            - **Pecuários**: Bovinos, suínos, aves, piscicultura
            - **Urbanos**: RSU e resíduos de poda
            - **Silvicultura**: Eucalipto e resíduos florestais
            """)

            st.markdown("""
            **🗺️ Mapas Interativos**:
            - Visualização geoespacial
            - Filtros por resíduo
            - Rankings municipais
            - Análises regionais
            """)

        with col2:
            st.markdown("""
            **📈 Análises Estatísticas**:
            - Correlações
            - Comparações
            - Portfólio
            - Scatter plots
            """)

            st.markdown("""
            **💾 Exportação**:
            - CSV
            - Relatórios
            - Dados filtrados
            """)

        st.markdown("### 📖 Guia Rápido")
        st.markdown("""
        1. **🏠 Mapa Principal**: Visualize o potencial de biogás por município
        2. **🔍 Explorar Dados**: Análise com gráficos e tabelas
        3. **📊 Análises Avançadas**: Análises detalhadas
        4. **ℹ️ Sobre**: Informações técnicas e institucionais
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; padding: 1rem;'>"
        "<small>Desenvolvido pelo Centro Paulista de Estudos em Biogás e Bioprodutos (CP2B)<br>"
        "Financiamento: FAPESP - Processo 2024/01112-1</small>"
        "</div>",
        unsafe_allow_html=True
    )

    # Logo
    try:
        st.image("logotipo-full-black.png", width=400)
    except:
        logger.warning("Logo not found")
