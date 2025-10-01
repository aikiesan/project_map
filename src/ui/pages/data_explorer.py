"""
CP2B Maps V2 - Data Explorer Page
Enhanced data exploration with V1's comprehensive chart library
Professional data analysis and visualization interface
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader

# Import V1 design system
from src.ui.components.design_system import (
    render_section_header,
    render_info_banner,
    render_styled_metrics
)

# Import enhanced chart library (ported from V1)
from src.ui.components.analysis_charts import (
    create_top_municipalities_chart,
    create_distribution_histogram,
    create_box_plot_analysis,
    create_scatter_correlation,
    create_municipality_ranking_table,
    create_summary_statistics_table,
    create_regional_comparison_pie,
    create_multi_source_comparison_bar,
    create_comparative_municipalities_chart
)

# Import reference system for inline citations
from src.data.references.scientific_references import (
    render_reference_button,
    get_substrate_reference_map
)

logger = get_logger(__name__)


class DataExplorerPage:
    """
    Enhanced Data Explorer with V1's comprehensive visualization tools
    Features: 4 chart types, rankings, statistics, municipality comparison
    """

    def __init__(self):
        """Initialize Data Explorer page"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing DataExplorerPage with V1 chart library")

    def render(self) -> None:
        """
        Render enhanced data explorer page
        """
        try:
            # V1-style section header
            render_section_header(
                "📊 Explorador de Dados",
                icon="🔍",
                description="Análise detalhada e comparativa com ferramentas interativas avançadas"
            )

            # Load municipality data
            df = database_loader.load_municipalities_data()
            if df is None or len(df) == 0:
                st.error("⚠️ Não foi possível carregar os dados dos municípios")
                return

            # Data selection sidebar
            selected_column, selected_municipalities = self._render_data_selection_sidebar(df)

            # Quick statistics banner
            self._render_quick_statistics(df, selected_column)

            st.markdown("---")

            # Main analysis tabs (V1 structure: Charts + Rankings + Comparison)
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Gráficos de Análise",
                "🏆 Rankings",
                "📊 Estatísticas",
                "🔄 Comparação de Municípios"
            ])

            with tab1:
                self._render_analysis_charts(df, selected_column)

            with tab2:
                self._render_rankings_section(df, selected_column)

            with tab3:
                self._render_statistics_section(df, selected_column)

            with tab4:
                self._render_comparison_section(df, selected_municipalities, selected_column)

        except Exception as e:
            self.logger.error(f"Error rendering data explorer: {e}", exc_info=True)
            st.error("⚠️ Erro ao renderizar explorador de dados. Verifique os logs.")

    def _render_data_selection_sidebar(self, df: pd.DataFrame) -> tuple[str, List[str]]:
        """Render data selection controls in sidebar"""
        with st.sidebar:
            st.markdown("### 🎯 Seleção de Dados")

            # Data column selection
            data_options = {
                "biogas_potential_m3_year": "🏭 Potencial Total de Biogás",
                "agricultural_biogas_m3_year": "🌾 Potencial Agrícola",
                "livestock_biogas_m3_year": "🐄 Potencial Pecuário",
                "urban_biogas_m3_year": "🏘️ Potencial Urbano",
                "energy_potential_mwh_year": "⚡ Potencial Energético (MWh)",
                "co2_reduction_tons_year": "🌱 Redução CO₂ (ton)"
            }

            # Filter to only show columns that exist in the dataframe
            available_options = {k: v for k, v in data_options.items() if k in df.columns}

            if not available_options:
                st.error("Nenhuma coluna de dados disponível")
                return "", []

            selected_column = st.selectbox(
                "Selecione o dado para análise:",
                options=list(available_options.keys()),
                format_func=lambda x: available_options[x],
                key="data_explorer_column"
            )

            st.markdown("---")

            # Municipality multi-selection for comparison
            st.markdown("### 🔍 Comparação de Municípios")

            # Get municipality name column (flexible)
            name_col = 'municipality' if 'municipality' in df.columns else 'municipio'

            if name_col not in df.columns:
                st.warning("Coluna de município não encontrada")
                selected_municipalities = []
            else:
                # Search functionality
                search_term = st.text_input(
                    "Buscar município:",
                    placeholder="Digite para filtrar...",
                    key="mun_search_explorer"
                )

                # Filter municipalities by search
                if search_term:
                    filtered_muns = df[df[name_col].str.contains(search_term, case=False, na=False)][name_col].unique()
                else:
                    filtered_muns = df[name_col].unique()

                # Multi-select for comparison
                selected_municipalities = st.multiselect(
                    "Selecione municípios para comparar:",
                    options=sorted(filtered_muns)[:100],  # Limit for performance
                    default=[],
                    key="selected_muns_explorer"
                )

                if len(selected_municipalities) > 0:
                    st.success(f"✅ {len(selected_municipalities)} municípios selecionados")

            return selected_column, selected_municipalities

    def _render_quick_statistics(self, df: pd.DataFrame, column: str) -> None:
        """Render quick statistics banner with inline references"""
        try:
            if column not in df.columns:
                return

            data = df[column].dropna()

            if len(data) == 0:
                return

            # Get reference for this data column (if available)
            ref_map = get_substrate_reference_map()
            ref_id = ref_map.get(column, "biogas_calculation")

            # Calculate key metrics with reference button
            col1, col2, col3, col4, col_ref = st.columns([2, 2, 2, 2, 0.5])

            with col1:
                st.metric("📊 Total de Municípios", f"{len(data):,}")

            with col2:
                st.metric("📈 Potencial Total", f"{data.sum():,.0f}", "m³/ano")

            with col3:
                st.metric("🎯 Média", f"{data.mean():,.0f}", "m³/ano")

            with col4:
                st.metric("⬆️ Máximo", f"{data.max():,.0f}", "m³/ano")

            with col_ref:
                st.markdown("<br>", unsafe_allow_html=True)  # Vertical spacing
                render_reference_button(ref_id, compact=True, label="📚")

        except Exception as e:
            self.logger.error(f"Error rendering quick statistics: {e}")

    def _render_analysis_charts(self, df: pd.DataFrame, column: str) -> None:
        """Render analysis charts section (V1's 4 chart types)"""
        try:
            # Header with reference
            col_title, col_ref = st.columns([10, 1])
            with col_title:
                render_section_header("📈 Análise Visual", description="Visualizações interativas para exploração de dados")
            with col_ref:
                ref_map = get_substrate_reference_map()
                ref_id = ref_map.get(column, "biogas_calculation")
                render_reference_button(ref_id, compact=True)

            # Chart type selector
            chart_types = {
                "top": "🏆 Top Municípios (Ranking)",
                "distribution": "📊 Distribuição (Histograma)",
                "box": "📦 Box Plot (Outliers)",
                "scatter": "🔍 Correlação (Scatter Plot)"
            }

            selected_chart = st.radio(
                "Selecione o tipo de gráfico:",
                options=list(chart_types.keys()),
                format_func=lambda x: chart_types[x],
                horizontal=True,
                key="chart_type_selector"
            )

            st.markdown("---")

            # Render selected chart
            if selected_chart == "top":
                limit = st.slider("Número de municípios:", 5, 50, 15, key="top_limit")
                fig = create_top_municipalities_chart(df, column, limit=limit)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foi possível gerar o gráfico")

            elif selected_chart == "distribution":
                fig = create_distribution_histogram(df, column)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Dica**: As linhas tracejadas indicam média (vermelho) e mediana (azul)")
                else:
                    st.warning("Não foi possível gerar o gráfico")

            elif selected_chart == "box":
                # Optional grouping
                group_col = st.selectbox(
                    "Agrupar por (opcional):",
                    options=["Nenhum"] + [col for col in df.columns if col in ['region', 'regiao', 'state']],
                    key="box_group"
                )
                group_by = None if group_col == "Nenhum" else group_col

                fig = create_box_plot_analysis(df, column, group_col=group_by)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Dica**: Pontos fora das caixas são outliers (valores extremos)")
                else:
                    st.warning("Não foi possível gerar o gráfico")

            elif selected_chart == "scatter":
                # X-axis selector
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                x_col = st.selectbox(
                    "Eixo X:",
                    options=numeric_cols,
                    index=numeric_cols.index('population') if 'population' in numeric_cols else 0,
                    key="scatter_x"
                )

                fig = create_scatter_correlation(df, x_col, column, size_col=column)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Dica**: A linha de tendência mostra a correlação entre as variáveis")
                else:
                    st.warning("Não foi possível gerar o gráfico")

        except Exception as e:
            self.logger.error(f"Error rendering analysis charts: {e}")
            st.error("Erro ao renderizar gráficos de análise")

    def _render_rankings_section(self, df: pd.DataFrame, column: str) -> None:
        """Render rankings section (V1 feature)"""
        try:
            # Header with reference
            col_title, col_ref = st.columns([10, 1])
            with col_title:
                render_section_header("🏆 Rankings", description="Classificação dos municípios por potencial")
            with col_ref:
                ref_map = get_substrate_reference_map()
                ref_id = ref_map.get(column, "biogas_calculation")
                render_reference_button(ref_id, compact=True)

            col1, col2 = st.columns([2, 1])

            with col1:
                ranking_type = st.radio(
                    "Tipo de ranking:",
                    ["Top municípios", "Bottom municípios"],
                    horizontal=True,
                    key="ranking_type"
                )

            with col2:
                limit = st.number_input(
                    "Quantidade:",
                    min_value=5,
                    max_value=100,
                    value=20,
                    step=5,
                    key="ranking_limit"
                )

            st.markdown("---")

            # Generate ranking
            if ranking_type == "Top municípios":
                ranking_df = create_municipality_ranking_table(df, column, limit=int(limit))
            else:
                # Bottom ranking (reverse)
                ranking_df = create_municipality_ranking_table(
                    df.sort_values(column, ascending=True),
                    column,
                    limit=int(limit)
                )

            if ranking_df is not None and not ranking_df.empty:
                # Display with styled dataframe
                st.dataframe(
                    ranking_df,
                    use_container_width=True,
                    height=600,
                    hide_index=True
                )

                # Export button
                csv = ranking_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Ranking (CSV)",
                    data=csv,
                    file_name=f"ranking_{column}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Não foi possível gerar o ranking")

        except Exception as e:
            self.logger.error(f"Error rendering rankings: {e}")
            st.error("Erro ao renderizar rankings")

    def _render_statistics_section(self, df: pd.DataFrame, column: str) -> None:
        """Render statistics section (V1 feature)"""
        try:
            # Header with reference
            col_title, col_ref = st.columns([10, 1])
            with col_title:
                render_section_header("📊 Estatísticas Descritivas", description="Análise estatística detalhada")
            with col_ref:
                ref_map = get_substrate_reference_map()
                ref_id = ref_map.get(column, "biogas_calculation")
                render_reference_button(ref_id, compact=True)

            # Two-column layout
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📈 Estatísticas Resumidas")
                stats_df = create_summary_statistics_table(df, column)
                if stats_df is not None:
                    st.dataframe(stats_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Sem dados estatísticos disponíveis")

            with col2:
                st.markdown("#### 🗺️ Distribuição Regional")
                # Try to create regional pie chart if region column exists
                region_col = None
                for col in ['region', 'regiao', 'administrative_region']:
                    if col in df.columns:
                        region_col = col
                        break

                if region_col:
                    fig = create_regional_comparison_pie(df, column, region_col=region_col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Dados regionais não disponíveis")
                else:
                    st.info("💡 Coluna de região não encontrada. Adicione dados regionais para visualização.")

            st.markdown("---")

            # Multi-source comparison (if applicable)
            st.markdown("#### 🌾 Composição por Fonte de Biogás")

            # Define biogas source columns (adapt to your schema)
            source_columns = {}
            potential_sources = {
                'agricultural_biogas_m3_year': 'Agrícola',
                'livestock_biogas_m3_year': 'Pecuário',
                'urban_biogas_m3_year': 'Urbano',
                'urban_waste_potential_m3_year': 'Resíduos Urbanos',
                'rural_waste_potential_m3_year': 'Resíduos Rurais'
            }

            for col, label in potential_sources.items():
                if col in df.columns:
                    source_columns[col] = label

            if source_columns:
                fig = create_multi_source_comparison_bar(df, source_columns)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dados de composição não disponíveis")
            else:
                st.info("💡 Colunas de fonte de biogás não encontradas")

        except Exception as e:
            self.logger.error(f"Error rendering statistics: {e}")
            st.error("Erro ao renderizar estatísticas")

    def _render_comparison_section(self, df: pd.DataFrame, selected_municipalities: List[str], column: str) -> None:
        """Render municipality comparison section (V1 feature)"""
        try:
            render_section_header("🔄 Comparação de Municípios", description="Compare municípios selecionados lado a lado")

            if not selected_municipalities or len(selected_municipalities) == 0:
                render_info_banner(
                    "💡 Selecione municípios na barra lateral para ativar a comparação",
                    banner_type="info",
                    icon="ℹ️"
                )
                return

            if len(selected_municipalities) > 10:
                st.warning("⚠️ Muitos municípios selecionados. Mostrando apenas os 10 primeiros.")
                selected_municipalities = selected_municipalities[:10]

            # Get municipality name column
            name_col = 'municipality' if 'municipality' in df.columns else 'municipio'

            if name_col not in df.columns:
                st.error("Coluna de município não encontrada")
                return

            # Filter data
            comparison_df = df[df[name_col].isin(selected_municipalities)].copy()

            if comparison_df.empty:
                st.warning("Nenhum dado encontrado para os municípios selecionados")
                return

            # Metric selector for comparison
            available_metrics = [col for col in df.select_dtypes(include=['number']).columns
                               if 'biogas' in col or 'energy' in col or 'co2' in col or 'potential' in col]

            selected_metrics = st.multiselect(
                "Selecione métricas para comparar:",
                options=available_metrics,
                default=[column] if column in available_metrics else available_metrics[:3],
                key="comparison_metrics"
            )

            if not selected_metrics:
                st.warning("Selecione pelo menos uma métrica")
                return

            st.markdown("---")

            # Comparative bar chart
            st.markdown("#### 📊 Gráfico Comparativo")
            fig = create_comparative_municipalities_chart(df, selected_municipalities, selected_metrics)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Comparison table
            st.markdown("#### 📋 Tabela Comparativa")

            # Select relevant columns for display
            display_cols = [name_col] + selected_metrics
            if 'population' in df.columns:
                display_cols.insert(1, 'population')

            display_df = comparison_df[display_cols].copy()

            # Format column names
            display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Export comparison
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Comparação (CSV)",
                data=csv,
                file_name=f"comparacao_municipios.csv",
                mime="text/csv"
            )

        except Exception as e:
            self.logger.error(f"Error rendering comparison: {e}")
            st.error("Erro ao renderizar comparação")


# Factory function for easy integration
def create_data_explorer_page() -> DataExplorerPage:
    """Create Data Explorer page instance"""
    return DataExplorerPage()
