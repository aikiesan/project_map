"""
CP2B Maps V2 - Modern Residue-Based Data Explorer
Advanced biogas potential analysis by residue type with SOLID architecture
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import get_database_loader
from src.data.loaders.database_loader import DatabaseLoader

# Import design system
from src.ui.components.design_system import (
    render_section_header,
    render_info_banner,
    render_styled_metrics
)

# Import chart components
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

# Import reference system
from src.data.references.scientific_references import (
    render_reference_button,
    get_substrate_reference_map
)

# Import academic footer
from src.ui.components.academic_footer import render_compact_academic_footer

logger = get_logger(__name__)


# SOLID Architecture Implementation

class DataVisualization(ABC):
    """Interface for data visualization components"""

    @abstractmethod
    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        pass


class ResidueSelector:
    """Single Responsibility: Handle residue selection and filtering"""

    RESIDUE_CATEGORIES = {
        "Agrícola": {
            "biogas_cana_m_ano": "🌾 Cana-de-açúcar",
            "biogas_soja_m_ano": "🫘 Soja",
            "biogas_milho_m_ano": "🌽 Milho",
            "biogas_cafe_m_ano": "☕ Café",
            "biogas_citros_m_ano": "🍊 Citros"
        },
        "Pecuário": {
            "biogas_bovinos_m_ano": "🐄 Bovinos",
            "biogas_suino_m_ano": "🐷 Suínos",
            "biogas_aves_m_ano": "🐔 Aves",
            "biogas_piscicultura_m_ano": "🐟 Piscicultura"
        },
        "Urbano": {
            "urban_biogas_m3_year": "🏘️ Resíduos Urbanos",
            "urban_waste_potential_m3_year": "🗑️ RSU"
        }
    }

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def render_selection_controls(self) -> Tuple[List[str], str, str]:
        """Render modern selection controls with improved design"""
        # Modern control section with enhanced styling
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 1.5rem; border-radius: 15px; margin: 1rem 0;
                    border: 1px solid #dee2e6; box-shadow: 0 4px 6px rgba(0,0,0,0.07);'>
        </div>
        """, unsafe_allow_html=True)

        # Three-column layout inspired by Análise de Proximidade
        col1, col2, col3 = st.columns([1.5, 2.5, 2])

        # Column 1: Category and Residue Selection
        with col1:
            st.markdown("##### 📂 Seleção de Resíduos")
            category = st.selectbox(
                "🏷️ Categoria:",
                options=["Todos"] + list(self.RESIDUE_CATEGORIES.keys()),
                key="residue_category",
                help="Escolha a categoria de resíduos para análise"
            )

            # Get available residues based on category
            if category == "Todos":
                available_residues = {}
                for cat_residues in self.RESIDUE_CATEGORIES.values():
                    available_residues.update(cat_residues)
            else:
                available_residues = self.RESIDUE_CATEGORIES[category]

            selected_residues = st.multiselect(
                "🌾 Resíduos:",
                options=list(available_residues.keys()),
                default=list(available_residues.keys())[:3],  # Select first 3 by default
                format_func=lambda x: available_residues[x],
                key="selected_residues",
                help="Selecione um ou mais tipos de resíduos"
            )

            # Status indicator
            if selected_residues:
                st.success(f"✅ {len(selected_residues)} resíduo(s) selecionado(s)")
            else:
                st.warning("⚠️ Selecione pelo menos um resíduo")

        # Column 2: Metrics and Visualization
        with col2:
            st.markdown("##### 📊 Configuração de Análise")

            metric_type = st.selectbox(
                "📈 Métrica de análise:",
                options=["Potencial (m³/ano)", "Energia (MWh/ano)", "Redução CO₂ (ton/ano)"],
                key="metric_type",
                help="Escolha a métrica para visualização dos dados"
            )

            display_type = st.selectbox(
                "🎯 Tipo de visualização:",
                options=["Individual", "Agregado", "Comparativo"],
                key="display_type",
                help="Defina como os dados serão apresentados"
            )

            # Metric explanation
            if metric_type == "Potencial (m³/ano)":
                st.caption("📏 Volume de biogás em metros cúbicos por ano")
            elif metric_type == "Energia (MWh/ano)":
                st.caption("⚡ Potencial energético em megawatts-hora por ano")
            else:
                st.caption("🌱 Redução de emissões de CO₂ em toneladas por ano")

        # Column 3: Analysis Summary and Actions
        with col3:
            st.markdown("##### 🎯 Resumo da Análise")

            if selected_residues:
                st.info(f"""
                **📋 Configuração Atual:**
                - **Resíduos:** {len(selected_residues)}
                - **Métrica:** {metric_type.split('(')[0].strip()}
                - **Visualização:** {display_type}
                """)

                # Quick analysis button
                if st.button("🚀 Executar Análise Rápida", help="Gera análise automática dos dados selecionados"):
                    st.success("✨ Análise executada! Verifique os resultados abaixo.")
            else:
                st.warning("📌 Configure os parâmetros ao lado para iniciar a análise")

        # Elegant separator
        st.markdown("""
        <div style='height: 2px; background: linear-gradient(90deg, transparent, #4a90e2, transparent);
                    margin: 2rem 0 1rem 0; border-radius: 1px;'></div>
        """, unsafe_allow_html=True)

        return selected_residues, metric_type, display_type


class MetricConverter:
    """Helper class for converting biogas values to different metrics"""

    @staticmethod
    def convert_biogas_to_metric(data: pd.DataFrame, biogas_columns: List[str], metric_type: str) -> pd.DataFrame:
        """
        Convert biogas values to specified metric type

        Args:
            data: DataFrame with biogas data
            biogas_columns: List of biogas column names
            metric_type: Target metric type

        Returns:
            DataFrame with converted values
        """
        converted_data = data.copy()

        if metric_type == "Energia (MWh/ano)":
            # Convert m³/ano to MWh/ano: m³ × 0.6 (methane) × 9.97 kWh/m³ ÷ 1000
            for col in biogas_columns:
                if col in converted_data.columns:
                    converted_data[col] = converted_data[col] * 0.6 * 9.97 / 1000

        elif metric_type == "Redução CO₂ (ton/ano)":
            # Convert m³/ano to ton CO₂/ano: m³ × 0.6 × 9.97 kWh × 0.45 kg CO₂/kWh ÷ 1000
            for col in biogas_columns:
                if col in converted_data.columns:
                    converted_data[col] = converted_data[col] * 0.6 * 9.97 * 0.45 / 1000

        return converted_data

    @staticmethod
    def get_metric_unit(metric_type: str) -> str:
        """Get the appropriate unit for the metric type"""
        if metric_type == "Energia (MWh/ano)":
            return "MWh/ano"
        elif metric_type == "Redução CO₂ (ton/ano)":
            return "ton CO₂/ano"
        else:
            return "m³/ano"


class OverviewAnalyzer(DataVisualization):
    """Single Responsibility: Overview dashboard with KPIs and basic charts"""

    def __init__(self, db_loader: DatabaseLoader):
        self.db_loader = db_loader
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render overview dashboard"""
        selected_residues = config["selected_residues"]
        metric_type = config["metric_type"]
        display_type = config["display_type"]

        if not selected_residues:
            st.warning("⚠️ Selecione pelo menos um resíduo para análise")
            return

        # Debug logging
        self.logger.info(f"Selected residues: {selected_residues}")
        self.logger.info(f"Available columns: {list(data.columns)}")

        # Validate that selected residues exist in data
        valid_residues = [r for r in selected_residues if r in data.columns]
        self.logger.info(f"Valid residues found: {valid_residues}")

        if not valid_residues:
            st.error("⚠️ Nenhum dos resíduos selecionados foi encontrado nos dados")
            st.info(f"🔍 Debug: Resíduos selecionados: {selected_residues}")
            st.info(f"🔍 Debug: Colunas disponíveis: {[col for col in data.columns if 'biogas' in col.lower()]}")
            return

        # Convert data based on metric type
        converted_data = MetricConverter.convert_biogas_to_metric(data, valid_residues, metric_type)
        metric_unit = MetricConverter.get_metric_unit(metric_type)

        st.markdown("### 📊 Visão Geral")

        # Calculate aggregate metrics with proper units
        self._render_kpi_cards(converted_data, valid_residues, metric_type, metric_unit)

        st.markdown("---")

        # Top municipalities chart based on display type
        if display_type == "Individual":
            self._render_individual_charts(converted_data, valid_residues, metric_unit)
        elif display_type == "Agregado":
            self._render_aggregated_charts(converted_data, valid_residues, metric_unit)
        else:  # Comparativo
            self._render_comparative_charts(converted_data, valid_residues, metric_unit)

    def _render_kpi_cards(self, data: pd.DataFrame, residues: List[str], metric_type: str, metric_unit: str) -> None:
        """Render KPI cards for selected residues with proper units"""
        cols = st.columns(len(residues))

        for i, residue in enumerate(residues):
            if residue not in data.columns:
                continue

            with cols[i]:
                total = data[residue].sum()
                avg = data[residue].mean()

                # Get residue display name
                display_name = self._get_residue_display_name(residue)

                # Format values based on metric type
                if metric_type == "Energia (MWh/ano)":
                    value_str = f"{total:,.1f} {metric_unit}"
                    delta_str = f"Média: {avg:,.1f}"
                elif metric_type == "Redução CO₂ (ton/ano)":
                    value_str = f"{total:,.1f} {metric_unit}"
                    delta_str = f"Média: {avg:,.1f}"
                else:
                    value_str = f"{total:,.0f} {metric_unit}"
                    delta_str = f"Média: {avg:,.0f}"

                st.metric(
                    label=display_name,
                    value=value_str,
                    delta=delta_str
                )

    def _render_top_municipalities(self, data: pd.DataFrame, residues: List[str]) -> None:
        """Render top municipalities chart"""
        if len(residues) == 1:
            residue = residues[0]
            if residue in data.columns:
                fig = create_top_municipalities_chart(
                    data, residue, f"Top Municípios - {self._get_residue_display_name(residue)}", 10
                )
                if fig:
                    st.plotly_chart(fig, width="stretch")
        else:
            # Multi-residue aggregation
            valid_residues = [r for r in residues if r in data.columns]
            if valid_residues:
                data["total_selected"] = data[valid_residues].sum(axis=1)
                fig = create_top_municipalities_chart(
                    data, "total_selected", "Top Municípios - Resíduos Selecionados", 10
                )
                if fig:
                    st.plotly_chart(fig, width="stretch")

    def _render_individual_charts(self, data: pd.DataFrame, residues: List[str], metric_unit: str) -> None:
        """Render individual charts for each residue"""
        st.markdown("#### 📊 Análise Individual por Resíduo")

        # Create tabs for each residue
        if len(residues) <= 4:
            tabs = st.tabs([self._get_residue_display_name(r) for r in residues])

            for i, residue in enumerate(residues):
                with tabs[i]:
                    col1, col2 = st.columns(2)

                    with col1:
                        fig = create_top_municipalities_chart(
                            data, residue, f"Top Municípios - {self._get_residue_display_name(residue)}", 10
                        )
                        if fig:
                            st.plotly_chart(fig, width="stretch")

                    with col2:
                        # Regional analysis for individual residue
                        if 'nm_rgint' in data.columns:
                            self._render_regional_analysis_individual(data, residue, metric_unit)
                        else:
                            st.info("Dados regionais não disponíveis")
        else:
            # Too many residues, show select box
            selected_residue = st.selectbox(
                "Escolha um resíduo para visualizar:",
                residues,
                format_func=self._get_residue_display_name
            )

            col1, col2 = st.columns(2)
            with col1:
                fig = create_top_municipalities_chart(
                    data, selected_residue, f"Top Municípios - {self._get_residue_display_name(selected_residue)}", 10
                )
                if fig:
                    st.plotly_chart(fig, width="stretch")

            with col2:
                if 'nm_rgint' in data.columns:
                    self._render_regional_analysis_individual(data, selected_residue, metric_unit)
                else:
                    st.info("Dados regionais não disponíveis")

    def _render_aggregated_charts(self, data: pd.DataFrame, residues: List[str], metric_unit: str) -> None:
        """Render aggregated view of all selected residues"""
        st.markdown("#### 📈 Análise Agregada - Todos os Resíduos")

        # Create aggregated column
        data["total_selected"] = data[residues].sum(axis=1)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🏆 Top 15 Municípios (Agregado)")
            fig = create_top_municipalities_chart(
                data, "total_selected", f"Top Municípios - Total Agregado ({metric_unit})", 15
            )
            if fig:
                st.plotly_chart(fig, width="stretch")

        with col2:
            st.markdown("##### 🗺️ Distribuição Regional Agregada")
            if 'nm_rgint' in data.columns:
                self._render_regional_analysis_aggregated(data, "total_selected", metric_unit)
            else:
                st.info("Dados regionais não disponíveis")

    def _render_comparative_charts(self, data: pd.DataFrame, residues: List[str], metric_unit: str) -> None:
        """Render comparative analysis between residues"""
        st.markdown("#### ⚖️ Análise Comparativa entre Resíduos")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📊 Comparação de Totais")
            # Create comparison bar chart
            totals = []
            names = []
            for residue in residues:
                if residue in data.columns:
                    totals.append(data[residue].sum())
                    names.append(self._get_residue_display_name(residue))

            if totals:
                comparison_data = pd.DataFrame({
                    'Resíduo': names,
                    'Total': totals
                }).sort_values('Total', ascending=True)

                import plotly.express as px
                fig = px.bar(
                    comparison_data,
                    x='Total',
                    y='Resíduo',
                    orientation='h',
                    title=f"Comparação de Potencial Total ({metric_unit})",
                    labels={'Total': f'Total ({metric_unit})', 'Resíduo': 'Tipo de Resíduo'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width="stretch")

        with col2:
            st.markdown("##### 📈 Distribuição por Municípios")
            # Box plot comparison
            fig = create_comparative_municipalities_chart(data, residues)
            if fig:
                st.plotly_chart(fig, width="stretch")

    def _render_regional_analysis_individual(self, data: pd.DataFrame, residue: str, metric_unit: str) -> None:
        """Render regional analysis for individual residue"""
        st.markdown("##### 🗺️ Análise Regional")

        if 'nm_rgint' in data.columns:
            # Group by immediate regions
            regional_data = data.groupby('nm_rgint')[residue].sum().sort_values(ascending=False).head(10)

            if not regional_data.empty:
                st.markdown("**Top 10 Regiões Imediatas:**")
                for i, (region, value) in enumerate(regional_data.items(), 1):
                    if metric_unit == "MWh/ano":
                        st.write(f"{i}. {region}: {value:,.1f} {metric_unit}")
                    elif metric_unit == "ton CO₂/ano":
                        st.write(f"{i}. {region}: {value:,.1f} {metric_unit}")
                    else:
                        st.write(f"{i}. {region}: {value:,.0f} {metric_unit}")
            else:
                st.info("Nenhum dado regional disponível para este resíduo")

    def _render_regional_analysis_aggregated(self, data: pd.DataFrame, column: str, metric_unit: str) -> None:
        """Render regional analysis for aggregated data"""
        if 'nm_rgint' in data.columns:
            # Group by immediate regions
            regional_data = data.groupby('nm_rgint')[column].sum().sort_values(ascending=False).head(10)

            if not regional_data.empty:
                st.markdown("**Top 10 Regiões Imediatas:**")
                for i, (region, value) in enumerate(regional_data.items(), 1):
                    if metric_unit == "MWh/ano":
                        st.write(f"{i}. {region}: {value:,.1f} {metric_unit}")
                    elif metric_unit == "ton CO₂/ano":
                        st.write(f"{i}. {region}: {value:,.1f} {metric_unit}")
                    else:
                        st.write(f"{i}. {region}: {value:,.0f} {metric_unit}")

    def _get_residue_display_name(self, residue: str) -> str:
        """Get display name for residue"""
        for category in ResidueSelector.RESIDUE_CATEGORIES.values():
            if residue in category:
                return category[residue]
        return residue.replace("_", " ").title()


class DetailedAnalyzer(DataVisualization):
    """Single Responsibility: Detailed statistical analysis and advanced charts"""

    def __init__(self, db_loader: DatabaseLoader):
        self.db_loader = db_loader
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render detailed analysis dashboard"""
        selected_residues = config["selected_residues"]
        metric_type = config["metric_type"]

        if not selected_residues:
            st.warning("⚠️ Selecione pelo menos um resíduo para análise")
            return

        # Validate that selected residues exist in data
        valid_residues = [r for r in selected_residues if r in data.columns]
        if not valid_residues:
            st.error("⚠️ Nenhum dos resíduos selecionados foi encontrado nos dados")
            return

        # Convert data based on metric type
        converted_data = MetricConverter.convert_biogas_to_metric(data, valid_residues, metric_type)
        metric_unit = MetricConverter.get_metric_unit(metric_type)

        st.markdown("### 🔬 Análise Detalhada")

        # Statistical analysis for each residue
        for residue in valid_residues:
            if residue not in converted_data.columns:
                continue

            with st.expander(f"📈 Análise: {self._get_residue_display_name(residue)}", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("##### Distribuição de Valores")
                    fig = create_distribution_histogram(converted_data, residue)
                    if fig:
                        # Update chart title to include metric unit
                        fig.update_layout(title=f"Distribuição - {self._get_residue_display_name(residue)} ({metric_unit})")
                        st.plotly_chart(fig, width="stretch")

                with col2:
                    st.markdown("##### Correlação com População")
                    if "population" in converted_data.columns:
                        fig = create_scatter_correlation(
                            converted_data, "population", residue,
                            title=f"População vs {self._get_residue_display_name(residue)} ({metric_unit})"
                        )
                        if fig:
                            st.plotly_chart(fig, width="stretch")

                # Statistical summary with proper units
                st.markdown("##### 📊 Estatísticas Descritivas")
                stats_df = create_summary_statistics_table(converted_data, residue)
                if stats_df is not None:
                    # Add metric unit to the title
                    st.markdown(f"**Unidade: {metric_unit}**")
                    st.dataframe(stats_df, width="stretch")

    def _get_residue_display_name(self, residue: str) -> str:
        """Get display name for residue"""
        for category in ResidueSelector.RESIDUE_CATEGORIES.values():
            if residue in category:
                return category[residue]
        return residue.replace("_", " ").title()


class ComparisonAnalyzer(DataVisualization):
    """Single Responsibility: Multi-residue comparison analysis"""

    def __init__(self, db_loader: DatabaseLoader):
        self.db_loader = db_loader
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render comparison analysis dashboard"""
        selected_residues = config["selected_residues"]
        metric_type = config["metric_type"]

        # Validate that selected residues exist in data
        valid_residues = [r for r in selected_residues if r in data.columns]

        if len(valid_residues) < 2:
            st.warning("⚠️ Selecione pelo menos dois resíduos válidos para comparação")
            return

        # Convert data based on metric type
        converted_data = MetricConverter.convert_biogas_to_metric(data, valid_residues, metric_type)
        metric_unit = MetricConverter.get_metric_unit(metric_type)

        st.markdown("### ⚖️ Comparação Multi-Resíduos")

        # Statistical comparison
        st.markdown("#### 📈 Análise Estatística Comparativa")
        self._render_statistical_comparison(converted_data, valid_residues, metric_unit)

    def _render_statistical_comparison(self, data: pd.DataFrame, residues: List[str], metric_unit: str) -> None:
        """Render statistical comparison between residues"""
        valid_residues = [r for r in residues if r in data.columns]

        stats_data = []
        for residue in valid_residues:
            residue_data = data[residue].dropna()

            # Format values based on metric unit
            if metric_unit in ["MWh/ano", "ton CO₂/ano"]:
                stats_data.append({
                    "Resíduo": self._get_residue_display_name(residue),
                    f"Total ({metric_unit})": f"{residue_data.sum():,.1f}",
                    "Média": f"{residue_data.mean():,.1f}",
                    "Mediana": f"{residue_data.median():,.1f}",
                    "Máximo": f"{residue_data.max():,.1f}",
                    "Desvio Padrão": f"{residue_data.std():,.1f}"
                })
            else:
                stats_data.append({
                    "Resíduo": self._get_residue_display_name(residue),
                    f"Total ({metric_unit})": f"{residue_data.sum():,.0f}",
                    "Média": f"{residue_data.mean():,.0f}",
                    "Mediana": f"{residue_data.median():,.0f}",
                    "Máximo": f"{residue_data.max():,.0f}",
                    "Desvio Padrão": f"{residue_data.std():,.0f}"
                })

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, width="stretch")

    def _get_residue_display_name(self, residue: str) -> str:
        """Get display name for residue"""
        for category in ResidueSelector.RESIDUE_CATEGORIES.values():
            if residue in category:
                return category[residue]
        return residue.replace("_", " ").title()


class MathematicalInsights(DataVisualization):
    """Single Responsibility: Advanced mathematical analysis and insights"""

    def __init__(self, db_loader: DatabaseLoader):
        self.db_loader = db_loader
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render mathematical insights dashboard"""
        selected_residues = config["selected_residues"]
        metric_type = config["metric_type"]

        if not selected_residues:
            st.warning("⚠️ Selecione pelo menos um resíduo para análise")
            return

        # Validate that selected residues exist in data
        valid_residues = [r for r in selected_residues if r in data.columns]
        if not valid_residues:
            st.error("⚠️ Nenhum dos resíduos selecionados foi encontrado nos dados")
            return

        # Convert data based on metric type
        converted_data = MetricConverter.convert_biogas_to_metric(data, valid_residues, metric_type)
        metric_unit = MetricConverter.get_metric_unit(metric_type)

        st.markdown("### 🧮 Insights Matemáticos")

        # Advanced statistical analysis
        for residue in valid_residues:
            if residue not in converted_data.columns:
                continue

            with st.expander(f"🔢 Análise Matemática: {self._get_residue_display_name(residue)}", expanded=False):
                residue_data = converted_data[residue].dropna()
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("##### 📊 Estatísticas Avançadas")

                    # Format percentile values based on metric type
                    if metric_unit in ["MWh/ano", "ton CO₂/ano"]:
                        percentile_format = ",.1f"
                        iqr_format = ",.1f"
                    else:
                        percentile_format = ",.0f"
                        iqr_format = ",.0f"

                    metrics = {
                        "Coeficiente de Variação": f"{(residue_data.std() / residue_data.mean() * 100):.2f}%",
                        "Assimetria (Skewness)": f"{residue_data.skew():.3f}",
                        "Curtose": f"{residue_data.kurtosis():.3f}",
                        "Percentil 90": f"{residue_data.quantile(0.9):{percentile_format}} {metric_unit}",
                        "Percentil 95": f"{residue_data.quantile(0.95):{percentile_format}} {metric_unit}",
                        "IQR": f"{residue_data.quantile(0.75) - residue_data.quantile(0.25):{iqr_format}} {metric_unit}"
                    }
                    for metric, value in metrics.items():
                        st.metric(metric, value)

                with col2:
                    st.markdown("##### 🎯 Potencial de Concentração")
                    total_potential = residue_data.sum()
                    top_10_potential = residue_data.nlargest(10).sum()
                    top_50_potential = residue_data.nlargest(50).sum()

                    concentration_metrics = {
                        "Top 10 Municípios": f"{(top_10_potential/total_potential*100):.1f}% do total",
                        "Top 50 Municípios": f"{(top_50_potential/total_potential*100):.1f}% do total",
                        "Índice de Concentração": f"{(top_10_potential/total_potential):.3f}",
                        "Potencial Distribuído": f"{len(residue_data[residue_data > 0])} municípios"
                    }
                    for metric, value in concentration_metrics.items():
                        st.metric(metric, value)

                # Projections and forecasts with proper units
                st.markdown("##### 📈 Projeções e Cenários")
                scenario_cols = st.columns(3)

                scenario_format = ",.1f" if metric_unit in ["MWh/ano", "ton CO₂/ano"] else ",.0f"

                with scenario_cols[0]:
                    st.metric("Cenário Conservador (70%)", f"{total_potential * 0.7:{scenario_format}} {metric_unit}")
                with scenario_cols[1]:
                    st.metric("Cenário Realista (85%)", f"{total_potential * 0.85:{scenario_format}} {metric_unit}")
                with scenario_cols[2]:
                    st.metric("Cenário Otimista (95%)", f"{total_potential * 0.95:{scenario_format}} {metric_unit}")

    def _get_residue_display_name(self, residue: str) -> str:
        """Get display name for residue"""
        for category in ResidueSelector.RESIDUE_CATEGORIES.values():
            if residue in category:
                return category[residue]
        return residue.replace("_", " ").title()


class ModernDataExplorer:
    """
    Main controller class implementing Dependency Inversion Principle
    Orchestrates all components with clean interfaces
    """

    def __init__(self, db_loader: DatabaseLoader = None):
        """Initialize with dependency injection"""
        self.logger = get_logger(self.__class__.__name__)
        self.db_loader = db_loader if db_loader is not None else get_database_loader()

        # Initialize components
        self.residue_selector = ResidueSelector()
        self.overview_analyzer = OverviewAnalyzer(self.db_loader)
        self.detailed_analyzer = DetailedAnalyzer(self.db_loader)
        self.comparison_analyzer = ComparisonAnalyzer(self.db_loader)
        self.mathematical_insights = MathematicalInsights(self.db_loader)

    def _render_gradient_header(self) -> None:
        """Render modern gradient header inspired by Análise de Proximidade"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #4a90e2 100%);
                    color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                    text-align: center; border-radius: 0 0 25px 25px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
            <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
                🌾 Explorador de Dados
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
                Análise avançada de potencial de biogás por tipo de resíduo
            </p>
            <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.8;'>
                📊 Análise Municipal • 🗺️ Dados Regionais • 📈 Múltiplas Métricas
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render(self) -> None:
        """Render the complete modern data explorer"""
        try:
            # Modern gradient header (inspired by Análise de Proximidade)
            self._render_gradient_header()

            # Load data with cache invalidation
            data = self.db_loader.load_municipalities_data()
            if data is None or len(data) == 0:
                st.error("⚠️ Não foi possível carregar os dados dos municípios")
                return

            # Log available columns for debugging
            self.logger.info(f"Available columns: {list(data.columns)}")

            # Check if we're missing expected biogas columns (cache issue detection)
            expected_biogas_cols = ['biogas_cana_m_ano', 'biogas_soja_m_ano', 'biogas_milho_m_ano',
                                  'biogas_cafe_m_ano', 'biogas_citros_m_ano', 'biogas_bovinos_m_ano',
                                  'biogas_suino_m_ano', 'biogas_aves_m_ano', 'biogas_piscicultura_m_ano']
            missing_cols = [col for col in expected_biogas_cols if col not in data.columns]

            if missing_cols:
                self.logger.warning(f"Missing biogas columns (possible cache issue): {missing_cols}")
                st.warning(f"🔄 Cache issue detected. Missing columns: {missing_cols}")
                st.info("💡 Please refresh the page to clear cache and reload data.")

                # Add cache clear button
                if st.button("🔄 Clear Cache and Reload Data", key="clear_cache_button"):
                    st.cache_data.clear()
                    st.rerun()
                return

            # Check if we have at least some biogas columns
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower()]
            if not biogas_columns:
                st.error("⚠️ Nenhuma coluna de biogás encontrada nos dados")
                return

            # Residue selection controls in main page
            selected_residues, metric_type, display_type = self.residue_selector.render_selection_controls()

            # Configuration for all analyzers
            config = {
                "selected_residues": selected_residues,
                "metric_type": metric_type,
                "display_type": display_type
            }

            # Main dashboard with modern tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Visão Geral",
                "🔬 Análise Detalhada",
                "⚖️ Comparação Multi-Resíduos",
                "🧮 Insights Matemáticos"
            ])

            with tab1:
                self.overview_analyzer.render(data, config)

            with tab2:
                self.detailed_analyzer.render(data, config)

            with tab3:
                self.comparison_analyzer.render(data, config)

            with tab4:
                self.mathematical_insights.render(data, config)

            # Academic footer
            render_compact_academic_footer(key_suffix="data_explorer")

        except Exception as e:
            self.logger.error(f"Error rendering modern data explorer: {e}", exc_info=True)
            st.error("⚠️ Erro ao renderizar explorador de dados. Verifique os logs.")


# Factory function for easy integration
def create_data_explorer_page() -> ModernDataExplorer:
    """Factory function to create and return the modern data explorer page"""
    return ModernDataExplorer()