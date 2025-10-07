"""
CP2B Maps - Validated Research Data Page
FAPESP 2025/08745-2 - Objective and intuitive presentation of validated residue availability
Professional design with modern gradient header
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

from src.utils.logging_config import get_logger
from src.data.research_data import (
    get_available_categories,
    get_cultures_by_category,
    get_culture_data,
    get_category_icon,
    get_culture_icon
)
from src.ui.components.academic_footer import render_compact_academic_footer

logger = get_logger(__name__)


class ValidatedResearchPage:
    """
    Main page for displaying validated research data
    Professional, objective, and intuitive presentation
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def _render_modern_header(self) -> None:
        """Render modern gradient header (blue/green professional)"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2563eb 0%, #059669 50%, #0d9488 100%);
                    color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                    text-align: center; border-radius: 0 0 25px 25px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
            <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
                📚 Dados Validados de Pesquisa
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
                Fatores de Disponibilidade real de resíduos
            </p>
            <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.8;'>
                🔬 Metodologia Conservadora • 📊 Dados Validados • 🌾 Agricultura • 🐄 Pecuária • 🏙️ RSU
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_culture_selector(self) -> str:
        """Render simplified culture/residue selector"""
        st.markdown("### 🎯 Selecione a Fonte de Resíduo")

        # Get all available cultures across all categories
        all_cultures = []
        categories = get_available_categories()
        
        for category in categories:
            cultures = get_cultures_by_category(category)
            for culture in cultures:
                if get_culture_data(culture) is not None:
                    all_cultures.append(culture)
        
        if not all_cultures:
            st.warning("⏳ Nenhum dado disponível no momento")
            return None

        selected_culture = st.selectbox(
            "**🌾 Cultura/Resíduo:**",
            all_cultures,
            format_func=lambda x: f"{get_culture_icon(x)} {x}",
            key='research_culture_selector'
        )

        return selected_culture

    def _render_overview_cards(self, overview: dict) -> None:
        """Render key research metrics as cards"""
        st.markdown("### 📊 Principais Resultados")

        results = overview['main_results']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💨 Potencial de Biogás",
                results.get('biogas_potential', 'N/A'),
                help="Cenário realista validado"
            )

        with col2:
            electricity = results.get('electricity', 'N/A')
            # Safely extract electricity value
            if '(' in electricity:
                electricity_value = electricity.split('(')[0].strip()
            else:
                electricity_value = electricity
            
            st.metric(
                "⚡ Energia Equivalente",
                electricity_value,
                help=electricity
            )

        with col3:
            territorial = results.get('territorial_coverage', 'N/A')
            # Safely extract first part if comma exists
            if ',' in territorial:
                territorial_value = territorial.split(',')[0]
            else:
                territorial_value = territorial
            
            st.metric(
                "📍 Cobertura Territorial",
                territorial_value,
                help=territorial
            )

        with col4:
            # Different metrics for different cultures
            if 'cane_processed' in results:
                st.metric(
                    "🌾 Base de Cálculo",
                    results['cane_processed'],
                    help="Total processado no Estado de São Paulo (2023)"
                )
            elif 'residue_available' in results:
                st.metric(
                    "♻️ Resíduo Disponível",
                    results['residue_available'],
                    help="Resíduo disponível após fatores de correção"
                )
            else:
                st.metric(
                    "📊 Disponibilidade",
                    results.get('effective_availability', 'N/A'),
                    help="Disponibilidade efetiva do resíduo"
                )

        # Key findings banner
        st.info(f"""
        **📌 Achados Principais:**

        {chr(10).join(overview['key_findings'])}
        """)

    def _render_residue_cards(self, residues: dict) -> None:
        """Render residue availability cards"""
        st.markdown("### 🔬 Disponibilidade por Resíduo")

        # Create cards for each residue
        for residue_key, residue_data in residues.items():
            with st.expander(
                f"**{get_culture_icon('Cana-de-açúcar')} {residue_data.name}** - Disponibilidade: {residue_data.factors.final_availability}%",
                expanded=(residue_key == 'palha')  # Expand palha by default (most important)
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Generation and destination
                    st.markdown(f"""
                    **📈 Geração:** {residue_data.generation}

                    **🎯 Destino Atual:** {residue_data.destination}

                    **💧 Potencial Metanogênico:** {residue_data.methane_potential}

                    **💦 Umidade:** {residue_data.moisture}
                    """)

                with col2:
                    # Availability factors
                    st.markdown("**🔢 Fatores de Correção:**")
                    factors = residue_data.factors.to_dict()

                    for factor_name, factor_value in factors.items():
                        if factor_name == 'Disponibilidade Final':
                            st.metric(factor_name, f"{factor_value}%")
                        else:
                            st.caption(f"{factor_name}: {factor_value}")

                # Technical justification (expandable)
                with st.expander("📝 Justificativa Técnica", expanded=False):
                    st.markdown(residue_data.justification)

    def _render_availability_factors_table(self, residues: dict) -> None:
        """Render comprehensive availability factors table"""
        st.markdown("### 📋 Tabela de Fatores de Disponibilidade")

        # Prepare data for table
        table_data = []
        for residue_data in residues.values():
            table_data.append({
                'Resíduo': residue_data.name,
                'Geração': residue_data.generation,
                'FC': residue_data.factors.fc,
                'FCp': residue_data.factors.fcp,
                'FS': residue_data.factors.fs,
                'FL': residue_data.factors.fl,
                'Disponibilidade Final (%)': residue_data.factors.final_availability,
                'PM (m³ CH₄/ton MS)': residue_data.methane_potential
            })

        df = pd.DataFrame(table_data)

        # Style the dataframe
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            column_config={
                'Resíduo': st.column_config.TextColumn('Resíduo', width='medium'),
                'Disponibilidade Final (%)': st.column_config.ProgressColumn(
                    'Disponibilidade Final (%)',
                    min_value=0,
                    max_value=100,
                    format='%.1f%%'
                )
            }
        )

        # Factor legend
        with st.expander("ℹ️ Legenda dos Fatores", expanded=False):
            st.markdown("""
            **Fatores de Correção Aplicados:**

            - **FC (Fator de Coleta)**: Eficiência técnica de recolhimento do resíduo
            - **FCp (Fator de Competição)**: Percentual competido por usos prioritários estabelecidos
            - **FS (Fator Sazonal)**: Variação sazonal da disponibilidade ao longo do ano
            - **FL (Fator Logístico)**: Restrição por distância econômica de transporte (tipicamente 20-30 km)
            - **PM (Potencial Metanogênico)**: Volume de metano produzido por tonelada de matéria seca

            **Metodologia:**
            Disponibilidade Final = FC × (1 - FCp) × FS × FL × 100%

            Valores conservadores baseados em dados de usinas reais, literatura científica e normas ambientais.
            """)

    def _render_contribution_chart(self, contribution: dict) -> None:
        """Render residue contribution breakdown chart"""
        st.markdown("### 📊 Contribuição por Tipo de Resíduo")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart for percentage contribution
            residues = [k for k in contribution.keys() if k != 'Total']
            percentages = [contribution[k]['pct'] for k in residues]

            fig_pie = px.pie(
                values=percentages,
                names=residues,
                title='Contribuição Percentual ao Potencial Total',
                color_discrete_sequence=['#f59e0b', '#dc2626', '#7c3aed']
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>%{value:.1f}%<br>%{customdata} Mi m³/ano<extra></extra>',
                customdata=[contribution[k]['ch4'] for k in residues]
            )
            st.plotly_chart(fig_pie, width='stretch')

        with col2:
            # Bar chart for absolute values
            ch4_values = [contribution[k]['ch4'] for k in residues]

            fig_bar = px.bar(
                x=residues,
                y=ch4_values,
                title='Potencial de Metano (Mi m³ CH₄/ano)',
                labels={'x': 'Resíduo', 'y': 'CH₄ (Mi m³/ano)'},
                color=ch4_values,
                color_continuous_scale='Oranges'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, width='stretch')

        # Total summary
        total = contribution['Total']
        st.success(f"""
        **✅ Total Consolidado:**
        - 💨 Biogás: **{total['ch4']} milhões m³ CH₄/ano**
        - ⚡ Eletricidade: **{total['electricity']} GWh/ano**
        - 🏠 Residências: **~{total['electricity']/166/12:.1f} milhões de domicílios** (consumo 166 kWh/mês)
        """)

    def _render_top_municipalities(self, top_munis: list, culture: str = 'Cana-de-açúcar') -> None:
        """Render top municipalities by potential"""
        st.markdown("### 🏆 Top 10 Municípios Produtores")

        # Prepare data
        df = pd.DataFrame(top_munis)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Horizontal bar chart
            fig = px.bar(
                df,
                y='name',
                x='ch4',
                orientation='h',
                title='Potencial de Biogás por Município (Mi m³ CH₄/ano)',
                labels={'ch4': 'CH₄ (Mi m³/ano)', 'name': 'Município'},
                color='ch4',
                color_continuous_scale='Greens',
                text='ch4'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig, width='stretch')

        with col2:
            st.markdown("**📋 Ranking Detalhado:**")

            # Format dataframe for display - handle different data types
            display_df = df.copy()
            display_df['Potencial (Mi m³/ano)'] = display_df['ch4']
            display_df['Eletricidade (GWh/ano)'] = display_df['electricity']
            
            # Check if 'area' or 'birds' column exists
            if 'area' in display_df.columns:
                display_df['Área Cana (ha)'] = display_df['area'].apply(lambda x: f"{x:,}")
                columns_to_show = ['#', 'Município', 'Potencial (Mi m³/ano)', 'Eletricidade (GWh/ano)']
            elif 'birds' in display_df.columns:
                display_df['Plantel (Mi aves)'] = (display_df['birds'] / 1000000).apply(lambda x: f"{x:.1f}")
                columns_to_show = ['#', 'Município', 'Potencial (Mi m³/ano)', 'Plantel (Mi aves)']
            else:
                columns_to_show = ['#', 'Município', 'Potencial (Mi m³/ano)', 'Eletricidade (GWh/ano)']
            
            display_df = display_df.rename(columns={'rank': '#', 'name': 'Município'})

            st.dataframe(
                display_df[columns_to_show],
                width='stretch',
                hide_index=True,
                height=500
            )

        # Culture-specific caption
        if culture == 'Avicultura':
            st.caption("💡 Top 10 municípios concentram 68,4% do potencial avícola estadual (Bastos: 24,8%)")
        else:
            st.caption("💡 Top 10 municípios representam 10,4% do potencial estadual em 10,3% da área cultivada")

    def _render_scenario_comparison(self, scenarios: dict) -> None:
        """Render scenario comparison"""
        st.markdown("### 🎭 Comparação entre Cenários")

        st.info("""
        **Metodologia de Cenários:**

        - **Pessimista**: Fatores conservadores máximos (maior competição por usos alternativos)
        - **Realista**: Fatores calibrados com dados reais de usinas e literatura validada (base para planejamento)
        - **Otimista**: Fatores otimistas (menor competição, maior eficiência de coleta)
        - **Teórico (100%)**: Disponibilidade total sem considerar competições (não operacional)
        """)

        # Prepare data
        scenario_names = list(scenarios.keys())
        ch4_values = [scenarios[s]['ch4'] for s in scenario_names]
        elec_values = [scenarios[s]['electricity'] for s in scenario_names]
        delta_values = [scenarios[s]['delta'] for s in scenario_names]

        col1, col2 = st.columns(2)

        with col1:
            # CH4 potential comparison
            fig_ch4 = go.Figure(data=[
                go.Bar(
                    x=scenario_names,
                    y=ch4_values,
                    text=[f"{v:,}" for v in ch4_values],
                    textposition='auto',
                    marker_color=['#dc2626', '#059669', '#f59e0b', '#6b7280']
                )
            ])
            fig_ch4.update_layout(
                title='Potencial de Biogás (Mi m³ CH₄/ano)',
                yaxis_title='CH₄ (Mi m³/ano)',
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_ch4, use_container_width=True)

        with col2:
            # Delta comparison from realistic
            fig_delta = go.Figure(data=[
                go.Bar(
                    x=scenario_names,
                    y=delta_values,
                    text=[f"{v:+.1f}%" for v in delta_values],
                    textposition='auto',
                    marker_color=['#dc2626', '#6b7280', '#f59e0b', '#2563eb']
                )
            ])
            fig_delta.update_layout(
                title='Variação vs Cenário Realista (%)',
                yaxis_title='Delta (%)',
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_delta, use_container_width=True)

        # Highlight realistic scenario
        st.success(f"""
        **✅ Cenário Realista Selecionado:**
        - 💨 **{scenarios['Realista']['ch4']:,} milhões m³ CH₄/ano**
        - ⚡ **{scenarios['Realista']['electricity']:,} GWh/ano**
        - 📉 **72% menor que teórico** (devido a fatores de competição operacionais)
        """)

    def _render_validation_section(self, validation: dict, culture: str = 'Cana-de-açúcar') -> None:
        """Render validation and quality assurance section"""
        st.markdown("### ✅ Validação dos Dados")

        col1, col2, col3 = st.columns(3)

        # Different validation metrics based on culture type
        if 'sidra_area' in validation:  # Cana-de-açúcar (agriculture)
            with col1:
                st.metric(
                    "🗺️ SIDRA - Área Colhida",
                    f"{validation['sidra_area']:.2f} Mi ha",
                    help="Base oficial IBGE para cálculo"
                )
                st.metric(
                    "🛰️ MapBiomas - Área Plantada",
                    f"{validation['mapbiomas_area']:.2f} Mi ha",
                    delta=f"+{validation['divergence']}% (esperado)",
                    help="Validação via sensoriamento remoto"
                )

            with col2:
                st.metric(
                    "📍 Municípios Produtores",
                    f"{validation['municipalities']}",
                    help="Municípios com produção de cana registrada"
                )
                st.metric(
                    "🏭 Usinas Mapeadas",
                    f"{validation['plants']}",
                    help="Infraestrutura existente georreferenciada"
                )

            with col3:
                st.metric(
                    "💨 Usinas de Biogás",
                    f"{validation['plants_biogas']}",
                    help="Usinas com biodigestores operacionais"
                )
                st.metric(
                    "📡 Cobertura Territorial",
                    f"{validation['coverage']}%",
                    help="% da cana dentro de 20km de uma usina"
                )

            # Validation explanation (Cana)
            with st.expander("📊 Metodologia de Validação", expanded=False):
                st.markdown(f"""
                **Validação Cruzada SIDRA × MapBiomas:**

                A divergência de **+{validation['divergence']}%** (MapBiomas > SIDRA) é metodologicamente esperada:

                - **SIDRA**: Registra área **colhida** (retrospectiva, safra completada)
                - **MapBiomas**: Classifica área **plantada** (presente/futuro, sensoriamento remoto)
                - **Ciclo cana**: 12-18 meses semi-perene (plantio 2023 → colheita 2024)

                **Para biogás, o dado correto é área colhida** (geração de resíduos ocorre na colheita).

                ---

                **Cobertura Espacial ({validation['coverage']}%):**

                Análise GEE revelou que {validation['coverage']}% da cana SP está a <20km de uma usina existente:

                ✅ Infraestrutura bem distribuída
                ✅ Potencial de retrofit em usinas existentes
                ✅ Redução de custos de transporte
                ⚠️ Necessidade de novas plantas em {100-validation['coverage']}% da área (greenfield)
                """)
        
        elif 'total_birds' in validation:  # Avicultura (poultry)
            with col1:
                st.metric(
                    "🐔 Plantel Total",
                    f"{validation['total_birds']:.1f} Mi aves",
                    help="Total de aves em granjas comerciais"
                )
                st.metric(
                    "🏭 Granjas Licenciadas",
                    f"{validation['farms']:,}",
                    help="Granjas comerciais mapeadas"
                )

            with col2:
                st.metric(
                    "📍 Municípios Produtores",
                    f"{validation['municipalities']}",
                    help="Municípios com produção avícola"
                )
                st.metric(
                    "📡 Cobertura em Clusters",
                    f"{validation['coverage']}%",
                    help="% da produção dentro de 30km de clusters"
                )

            with col3:
                st.metric(
                    "🎯 Polo Principal",
                    f"{validation['main_cluster']}",
                    delta=f"{validation['cluster_contribution']:.1f}% do total",
                    help="Epicentro da produção avícola"
                )
                st.metric(
                    "📉 Redução do Teórico",
                    f"{validation['theoretical_reduction']:.1f}%",
                    help="Diferença entre potencial teórico e real"
                )

            # Validation explanation (Avicultura)
            with st.expander("📊 Metodologia de Validação", expanded=False):
                st.markdown(f"""
                **Validação de Dados Avícolas:**

                A redução de **{validation['theoretical_reduction']:.1f}%** do potencial teórico para o real é resultado de:

                - **Fonte de dados**: IBGE - Censo Agropecuário e Produção da Pecuária Municipal (PPM)
                - **Plantel mapeado**: {validation['total_birds']:.1f} milhões de aves em {validation['farms']:,} granjas comerciais
                - **Municípios**: {validation['municipalities']} municípios produtores
                - **Validação cruzada**: 15 artigos científicos brasileiros e paulistas

                ---

                **Distribuição Espacial:**

                A produção avícola está concentrada em **clusters produtivos**:

                ✅ **Bastos** é o epicentro: {validation['cluster_contribution']:.1f}% do potencial estadual
                ✅ {validation['coverage']}% da produção dentro de raios logísticos viáveis (30 km)
                ✅ Outros polos: Salto, Tatuí, Ourinhos, Rancharia
                
                ---

                **Coproduto Valorizado:**

                💡 **Biofertilizante**: {validation['biofertilizer_coproduct']:.2f} milhões ton/ano
                - Substituto de fertilizantes químicos importados
                - Menor carga patogênica que dejeto bruto
                - Economia circular no agronegócio
                """)

    def _render_references(self, references: list) -> None:
        """Render scientific references"""
        st.markdown("### 📚 Referências Científicas")

        # Group references by type
        primary_refs = [r for r in references if r['type'] == 'Dados Primários']
        scientific_refs = [r for r in references if r['type'] == 'Literatura Científica']
        remote_sensing_refs = [r for r in references if r['type'] == 'Sensoriamento Remoto']
        norms_refs = [r for r in references if r['type'] == 'Normas Ambientais']

        col1, col2 = st.columns(2)

        with col1:
            if primary_refs:
                st.markdown("**📊 Dados Primários:**")
                for ref in primary_refs:
                    if ref['url']:
                        st.markdown(f"- [{ref['title']}]({ref['url']})")
                    else:
                        st.markdown(f"- {ref['title']}")

            if remote_sensing_refs:
                st.markdown("**🛰️ Sensoriamento Remoto:**")
                for ref in remote_sensing_refs:
                    if ref['url']:
                        st.markdown(f"- [{ref['title']}]({ref['url']})")
                    else:
                        st.markdown(f"- {ref['title']}")

        with col2:
            if scientific_refs:
                st.markdown("**📖 Literatura Científica:**")
                for ref in scientific_refs:
                    if ref['url']:
                        st.markdown(f"- [{ref['title']}]({ref['url']})")
                    else:
                        st.markdown(f"- {ref['title']}")

            if norms_refs:
                st.markdown("**⚖️ Normas Ambientais:**")
                for ref in norms_refs:
                    if ref['url']:
                        st.markdown(f"- [{ref['title']}]({ref['url']})")
                    else:
                        st.markdown(f"- {ref['title']}")

    def render(self) -> None:
        """Main render method"""
        try:
            # Modern header
            self._render_modern_header()

            # Simplified culture selector (no category needed)
            selected_culture = self._render_culture_selector()

            if not selected_culture:
                st.warning("⏳ Dados em desenvolvimento. Atualmente disponível: **Cana-de-açúcar** e **Avicultura**")
                st.info("""
                **🚧 Em breve:**
                - ☕ Café
                - 🍊 Citros
                - 🌽 Milho
                - 🫘 Soja
                - 🐄 Bovinocultura
                - 🐷 Suinocultura
                - 🏙️ RSU
                """)
                return

            st.markdown("---")

            # Load culture data
            culture_data = get_culture_data(selected_culture)

            if not culture_data:
                st.error("⚠️ Dados não encontrados")
                return

            # Render sections
            self._render_overview_cards(culture_data['overview'])

            st.markdown("---")

            self._render_residue_cards(culture_data['residues'])

            st.markdown("---")

            self._render_availability_factors_table(culture_data['residues'])

            st.markdown("---")

            self._render_contribution_chart(culture_data['contribution'])

            st.markdown("---")

            self._render_top_municipalities(culture_data['top_municipalities'], selected_culture)

            st.markdown("---")

            self._render_scenario_comparison(culture_data['scenarios'])

            st.markdown("---")

            self._render_validation_section(culture_data['validation'], selected_culture)

            st.markdown("---")

            self._render_references(culture_data['references'])

            # Academic footer
            render_compact_academic_footer(key_suffix="validated_research")

        except Exception as e:
            self.logger.error(f"Error rendering validated research page: {e}", exc_info=True)
            st.error(f"⚠️ Erro ao carregar dados de pesquisa: {str(e)}")


def create_validated_research_page():
    """Factory function to create validated research page"""
    page = ValidatedResearchPage()
    page.render()
