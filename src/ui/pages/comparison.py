"""
CP2B Maps V2 - Comparison Page
Professional multi-municipality comparison and benchmarking analysis
Enhanced with V1 design system
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple
import itertools

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import get_database_loader
from src.data.loaders.database_loader import DatabaseLoader
from src.core import get_biogas_calculator
from src.core.biogas_calculator import BiogasCalculator
from src.ui.components.charts import Charts

# Import V1 design system
from src.ui.components.design_system import (
    render_page_header,
    render_section_header,
    render_info_banner
)

logger = get_logger(__name__)


class ComparisonPage:
    """
    Professional comparison page for multi-municipality analysis
    Features: Side-by-side comparison, benchmarking, ranking analysis, export reports
    """

    def __init__(self,
                 db_loader: DatabaseLoader = None,
                 calculator: BiogasCalculator = None):
        """
        Initialize Comparison Page with dependency injection

        Args:
            db_loader: DatabaseLoader instance (uses default if None)
            calculator: BiogasCalculator instance (uses default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing ComparisonPage component")

        # Inject dependencies
        self.database_loader = db_loader if db_loader is not None else get_database_loader()
        self.biogas_calculator = calculator if calculator is not None else get_biogas_calculator()

        # Initialize charts component for visualization
        self.charts = Charts()

    def render(self) -> Dict[str, Any]:
        """
        Render comprehensive comparison analysis page

        Returns:
            Dictionary with comparison results and analysis data
        """
        try:
            # V1-style header
            render_page_header(
                title="Comparação de Municípios",
                subtitle="Análise Comparativa e Benchmarking",
                description="Compare múltiplos municípios lado a lado com análise detalhada de benchmarking e rankings",
                icon="🔍",
                show_stats=True
            )

            # Load municipality data
            municipalities_df = self._load_comparison_data()
            if municipalities_df is None or len(municipalities_df) == 0:
                st.error("⚠️ No municipality data available for comparison")
                return {}

            # Municipality selection interface
            selected_municipalities = self._render_municipality_selector(municipalities_df)

            if len(selected_municipalities) < 2:
                self._render_selection_guidance()
                return {'municipalities_df': municipalities_df}

            # Main comparison analysis
            comparison_results = self._render_comparison_analysis(
                municipalities_df, selected_municipalities
            )

            # Benchmarking analysis
            benchmarking_results = self._render_benchmarking_analysis(
                municipalities_df, selected_municipalities
            )

            # Ranking analysis
            ranking_results = self._render_ranking_analysis(
                municipalities_df, selected_municipalities
            )

            # Export options
            export_data = self._render_export_options(
                municipalities_df, selected_municipalities, comparison_results
            )

            return {
                'municipalities_df': municipalities_df,
                'selected_municipalities': selected_municipalities,
                'comparison_results': comparison_results,
                'benchmarking_results': benchmarking_results,
                'ranking_results': ranking_results,
                'export_data': export_data
            }

        except Exception as e:
            self.logger.error(f"Error rendering comparison page: {e}", exc_info=True)
            st.error("⚠️ Failed to render comparison page. Check logs for details.")
            return {}

    def _load_comparison_data(self) -> Optional[pd.DataFrame]:
        """Load and prepare municipality data for comparison"""
        try:
            data = self.database_loader.load_municipalities_data()
            if data is None:
                return None

            # Add calculated fields for comparison
            data['biogas_per_capita'] = np.where(
                data['population'] > 0,
                data['biogas_potential_m3_day'] / data['population'],
                0
            )

            data['energy_per_capita'] = np.where(
                data['population'] > 0,
                data['energy_potential_kwh_day'] / data['population'],
                0
            )

            # Add efficiency metrics
            data['biogas_efficiency'] = np.where(
                data['population'] > 0,
                data['biogas_potential_m3_day'] / (data['population'] / 1000),  # m³/day per 1k residents
                0
            )

            # Add ranking columns
            data['biogas_rank'] = data['biogas_potential_m3_day'].rank(ascending=False, method='dense')
            data['energy_rank'] = data['energy_potential_kwh_day'].rank(ascending=False, method='dense')
            data['efficiency_rank'] = data['biogas_per_capita'].rank(ascending=False, method='dense')

            self.logger.info(f"Loaded {len(data)} municipalities for comparison")
            return data

        except Exception as e:
            self.logger.error(f"Error loading comparison data: {e}")
            return None

    def _render_municipality_selector(self, data: pd.DataFrame) -> List[str]:
        """Render municipality selection interface"""
        st.markdown("#### 📍 Select Municipalities for Comparison")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Multi-select with search functionality
            available_municipalities = sorted(data['nome_municipio'].tolist())
            selected = st.multiselect(
                "Choose municipalities to compare:",
                options=available_municipalities,
                help="Select 2 or more municipalities for side-by-side analysis",
                key="comparison_municipalities"
            )

        with col2:
            # Quick selection options
            st.markdown("**Quick Selection:**")

            if st.button("🏆 Top 5 by Biogas", help="Select top 5 municipalities by biogas potential"):
                top_5 = data.nlargest(5, 'biogas_potential_m3_day')['nome_municipio'].tolist()
                st.session_state.comparison_municipalities = top_5
                st.rerun()

            if st.button("👥 Most Efficient", help="Select 5 most efficient municipalities (per capita)"):
                top_efficient = data.nlargest(5, 'biogas_per_capita')['nome_municipio'].tolist()
                st.session_state.comparison_municipalities = top_efficient
                st.rerun()

            if st.button("🌆 Largest Cities", help="Select 5 largest municipalities by population"):
                largest = data.nlargest(5, 'population')['nome_municipio'].tolist()
                st.session_state.comparison_municipalities = largest
                st.rerun()

        return selected

    def _render_selection_guidance(self) -> None:
        """Show guidance for municipality selection"""
        st.info("👆 Please select at least 2 municipalities to start comparison analysis.")

        # Show some statistics to help with selection
        try:
            # Quick stats
            data = self.database_loader.load_municipalities_data()
            if data is not None:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Municipalities", f"{len(data):,}")

                with col2:
                    avg_biogas = data['biogas_potential_m3_day'].mean()
                    st.metric("Average Biogas", f"{avg_biogas:,.0f} m³/day")

                with col3:
                    total_potential = data['biogas_potential_m3_day'].sum()
                    st.metric("Total State Potential", f"{total_potential:,.0f} m³/day")

        except Exception as e:
            self.logger.error(f"Error showing selection guidance: {e}")

    def _render_comparison_analysis(self,
                                  data: pd.DataFrame,
                                  selected_municipalities: List[str]) -> Dict[str, Any]:
        """Render side-by-side comparison analysis"""
        st.markdown("#### 📊 Side-by-Side Comparison")

        # Filter data for selected municipalities
        comparison_data = data[data['nome_municipio'].isin(selected_municipalities)].copy()

        # Comparison table
        self._render_comparison_table(comparison_data)

        # Comparison charts
        comparison_charts = self._render_comparison_charts(comparison_data)

        # Performance radar chart
        radar_chart = self._create_comparison_radar_chart(comparison_data)
        st.plotly_chart(radar_chart, use_container_width=True)

        return {
            'comparison_data': comparison_data,
            'comparison_charts': comparison_charts,
            'radar_chart': radar_chart
        }

    def _render_comparison_table(self, data: pd.DataFrame) -> None:
        """Render detailed comparison table"""
        st.markdown("##### 📋 Detailed Metrics Table")

        # Select key columns for comparison
        display_columns = [
            'nome_municipio', 'population', 'biogas_potential_m3_day',
            'energy_potential_kwh_day', 'biogas_per_capita', 'energy_per_capita',
            'biogas_rank', 'energy_rank', 'efficiency_rank'
        ]

        display_data = data[display_columns].copy()

        # Rename columns for better display
        display_data.columns = [
            'Municipality', 'Population', 'Biogas (m³/day)', 'Energy (kWh/day)',
            'Biogas per Capita', 'Energy per Capita', 'Biogas Rank', 'Energy Rank', 'Efficiency Rank'
        ]

        # Format numeric columns
        numeric_columns = ['Population', 'Biogas (m³/day)', 'Energy (kWh/day)',
                         'Biogas per Capita', 'Energy per Capita']
        for col in numeric_columns:
            if col in display_data.columns:
                display_data[col] = display_data[col].round(2)

        # Display with styling
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

        # Highlight leader in each category
        self._render_category_leaders(display_data)

    def _render_category_leaders(self, data: pd.DataFrame) -> None:
        """Highlight leaders in each category"""
        st.markdown("##### 🏆 Category Leaders")

        col1, col2, col3, col4 = st.columns(4)

        try:
            with col1:
                biogas_leader = data.loc[data['Biogas (m³/day)'].idxmax(), 'Municipality']
                biogas_value = data['Biogas (m³/day)'].max()
                st.metric("🥇 Highest Biogas", biogas_leader, f"{biogas_value:,.0f} m³/day")

            with col2:
                energy_leader = data.loc[data['Energy (kWh/day)'].idxmax(), 'Municipality']
                energy_value = data['Energy (kWh/day)'].max()
                st.metric("⚡ Highest Energy", energy_leader, f"{energy_value:,.0f} kWh/day")

            with col3:
                efficiency_leader = data.loc[data['Biogas per Capita'].idxmax(), 'Municipality']
                efficiency_value = data['Biogas per Capita'].max()
                st.metric("📈 Most Efficient", efficiency_leader, f"{efficiency_value:.3f} m³/person/day")

            with col4:
                population_leader = data.loc[data['Population'].idxmax(), 'Municipality']
                population_value = data['Population'].max()
                st.metric("👥 Largest Population", population_leader, f"{population_value:,.0f}")

        except Exception as e:
            self.logger.error(f"Error showing category leaders: {e}")

    def _render_comparison_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render comparison visualization charts"""
        st.markdown("##### 📊 Comparison Charts")

        col1, col2 = st.columns(2)

        with col1:
            # Biogas potential comparison
            fig_biogas = px.bar(
                data,
                x='nome_municipio',
                y='biogas_potential_m3_day',
                title='Biogas Potential Comparison',
                color='biogas_potential_m3_day',
                color_continuous_scale='Viridis'
            )
            fig_biogas.update_layout(
                xaxis_title='Municipality',
                yaxis_title='Biogas Potential (m³/day)',
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig_biogas, use_container_width=True)

        with col2:
            # Per capita comparison
            fig_per_capita = px.bar(
                data,
                x='nome_municipio',
                y='biogas_per_capita',
                title='Biogas per Capita Comparison',
                color='biogas_per_capita',
                color_continuous_scale='Plasma'
            )
            fig_per_capita.update_layout(
                xaxis_title='Municipality',
                yaxis_title='Biogas per Capita (m³/day)',
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig_per_capita, use_container_width=True)

        # Multi-metric comparison
        fig_multi = self._create_multi_metric_comparison(data)
        st.plotly_chart(fig_multi, use_container_width=True)

        return {
            'biogas_comparison': fig_biogas,
            'per_capita_comparison': fig_per_capita,
            'multi_metric_comparison': fig_multi
        }

    def _render_benchmarking_analysis(self,
                                    all_data: pd.DataFrame,
                                    selected_municipalities: List[str]) -> Dict[str, Any]:
        """Render benchmarking analysis against state averages"""
        st.markdown("#### 🎯 Benchmarking Analysis")

        # Calculate state benchmarks
        state_benchmarks = {
            'avg_biogas': all_data['biogas_potential_m3_day'].mean(),
            'avg_energy': all_data['energy_potential_kwh_day'].mean(),
            'avg_per_capita': all_data['biogas_per_capita'].mean(),
            'median_biogas': all_data['biogas_potential_m3_day'].median(),
            'top_10_percentile': all_data['biogas_potential_m3_day'].quantile(0.9),
            'top_25_percentile': all_data['biogas_potential_m3_day'].quantile(0.75)
        }

        # Selected municipalities data
        selected_data = all_data[all_data['nome_municipio'].isin(selected_municipalities)]

        # Benchmark comparison chart
        benchmark_chart = self._create_benchmark_comparison_chart(selected_data, state_benchmarks)
        st.plotly_chart(benchmark_chart, use_container_width=True)

        # Performance categories
        self._render_performance_categories(selected_data, state_benchmarks)

        return {
            'state_benchmarks': state_benchmarks,
            'selected_data': selected_data,
            'benchmark_chart': benchmark_chart
        }

    def _render_performance_categories(self,
                                     data: pd.DataFrame,
                                     benchmarks: Dict[str, float]) -> None:
        """Categorize municipalities by performance levels"""
        st.markdown("##### 🏅 Performance Categories")

        for _, municipality in data.iterrows():
            name = municipality['nome_municipio']
            biogas = municipality['biogas_potential_m3_day']

            if biogas >= benchmarks['top_10_percentile']:
                category = "🥇 Top Performer (Top 10%)"
                color = "success"
            elif biogas >= benchmarks['top_25_percentile']:
                category = "🥈 High Performer (Top 25%)"
                color = "info"
            elif biogas >= benchmarks['avg_biogas']:
                category = "🥉 Above Average"
                color = "warning"
            else:
                category = "📊 Below Average"
                color = "normal"

            if color == "success":
                st.success(f"**{name}**: {category}")
            elif color == "info":
                st.info(f"**{name}**: {category}")
            elif color == "warning":
                st.warning(f"**{name}**: {category}")
            else:
                st.write(f"**{name}**: {category}")

    def _render_ranking_analysis(self,
                               all_data: pd.DataFrame,
                               selected_municipalities: List[str]) -> Dict[str, Any]:
        """Render ranking analysis for selected municipalities"""
        st.markdown("#### 🏆 Ranking Analysis")

        selected_data = all_data[all_data['nome_municipio'].isin(selected_municipalities)].copy()

        # Ranking table
        ranking_columns = ['nome_municipio', 'biogas_rank', 'energy_rank', 'efficiency_rank']
        ranking_data = selected_data[ranking_columns].copy()
        ranking_data.columns = ['Municipality', 'Biogas Rank', 'Energy Rank', 'Efficiency Rank']

        st.dataframe(ranking_data, use_container_width=True, hide_index=True)

        # Ranking visualization
        ranking_chart = self._create_ranking_visualization(selected_data)
        st.plotly_chart(ranking_chart, use_container_width=True)

        return {
            'ranking_data': ranking_data,
            'ranking_chart': ranking_chart
        }

    def _render_export_options(self,
                             all_data: pd.DataFrame,
                             selected_municipalities: List[str],
                             comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Render export options for comparison data"""
        st.markdown("#### 📥 Export Comparison Report")

        col1, col2, col3 = st.columns(3)

        export_data = {}

        with col1:
            if st.button("📊 Export to Excel", help="Export comparison data to Excel file"):
                export_data['excel'] = self._prepare_excel_export(
                    all_data, selected_municipalities, comparison_results
                )
                st.success("✅ Excel export prepared!")

        with col2:
            if st.button("📄 Generate PDF Report", help="Generate comprehensive PDF report"):
                export_data['pdf'] = self._prepare_pdf_export(
                    all_data, selected_municipalities, comparison_results
                )
                st.success("✅ PDF report prepared!")

        with col3:
            if st.button("📋 Copy Summary", help="Copy summary to clipboard"):
                export_data['summary'] = self._generate_text_summary(
                    selected_municipalities, comparison_results
                )
                st.success("✅ Summary generated!")

        return export_data

    def _create_comparison_radar_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create radar chart for municipality comparison"""
        fig = go.Figure()

        # Normalize values for radar chart
        max_biogas = data['biogas_potential_m3_day'].max()
        max_energy = data['energy_potential_kwh_day'].max()
        max_population = data['population'].max()
        max_per_capita = data['biogas_per_capita'].max()

        categories = ['Biogas Potential', 'Energy Potential', 'Population', 'Biogas per Capita']

        for _, municipality in data.iterrows():
            # Normalize to 0-100 scale
            values = [
                (municipality['biogas_potential_m3_day'] / max_biogas) * 100 if max_biogas > 0 else 0,
                (municipality['energy_potential_kwh_day'] / max_energy) * 100 if max_energy > 0 else 0,
                (municipality['population'] / max_population) * 100 if max_population > 0 else 0,
                (municipality['biogas_per_capita'] / max_per_capita) * 100 if max_per_capita > 0 else 0
            ]

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=municipality['nome_municipio'][:15]  # Truncate long names
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title='Multi-Dimensional Performance Comparison',
            height=500
        )

        return fig

    def _create_multi_metric_comparison(self, data: pd.DataFrame) -> go.Figure:
        """Create multi-metric comparison chart"""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Biogas Potential', 'Energy Potential', 'Population', 'Biogas per Capita'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        municipalities = data['nome_municipio'].tolist()

        # Biogas potential
        fig.add_trace(
            go.Bar(x=municipalities, y=data['biogas_potential_m3_day'], name='Biogas'),
            row=1, col=1
        )

        # Energy potential
        fig.add_trace(
            go.Bar(x=municipalities, y=data['energy_potential_kwh_day'], name='Energy'),
            row=1, col=2
        )

        # Population
        fig.add_trace(
            go.Bar(x=municipalities, y=data['population'], name='Population'),
            row=2, col=1
        )

        # Biogas per capita
        fig.add_trace(
            go.Bar(x=municipalities, y=data['biogas_per_capita'], name='Per Capita'),
            row=2, col=2
        )

        fig.update_layout(
            title='Comprehensive Metrics Comparison',
            height=600,
            showlegend=False
        )

        return fig

    def _create_benchmark_comparison_chart(self,
                                         data: pd.DataFrame,
                                         benchmarks: Dict[str, float]) -> go.Figure:
        """Create benchmark comparison chart"""
        municipalities = data['nome_municipio'].tolist()
        biogas_values = data['biogas_potential_m3_day'].tolist()

        fig = go.Figure()

        # Municipality bars
        fig.add_trace(go.Bar(
            x=municipalities,
            y=biogas_values,
            name='Municipality',
            marker_color='lightblue'
        ))

        # Benchmark lines
        fig.add_hline(
            y=benchmarks['avg_biogas'],
            line_dash="dash",
            line_color="red",
            annotation_text="State Average"
        )

        fig.add_hline(
            y=benchmarks['top_25_percentile'],
            line_dash="dot",
            line_color="green",
            annotation_text="Top 25%"
        )

        fig.add_hline(
            y=benchmarks['top_10_percentile'],
            line_dash="solid",
            line_color="gold",
            annotation_text="Top 10%"
        )

        fig.update_layout(
            title='Performance vs State Benchmarks',
            xaxis_title='Municipality',
            yaxis_title='Biogas Potential (m³/day)',
            height=400
        )

        return fig

    def _create_ranking_visualization(self, data: pd.DataFrame) -> go.Figure:
        """Create ranking visualization"""
        municipalities = data['nome_municipio'].tolist()

        fig = go.Figure()

        # Biogas ranking (inverted for better visualization)
        fig.add_trace(go.Scatter(
            x=municipalities,
            y=data['biogas_rank'],
            mode='lines+markers',
            name='Biogas Rank',
            line=dict(color='blue')
        ))

        # Energy ranking
        fig.add_trace(go.Scatter(
            x=municipalities,
            y=data['energy_rank'],
            mode='lines+markers',
            name='Energy Rank',
            line=dict(color='green')
        ))

        # Efficiency ranking
        fig.add_trace(go.Scatter(
            x=municipalities,
            y=data['efficiency_rank'],
            mode='lines+markers',
            name='Efficiency Rank',
            line=dict(color='orange')
        ))

        fig.update_layout(
            title='Ranking Comparison Across Metrics',
            xaxis_title='Municipality',
            yaxis_title='Ranking (Lower is Better)',
            yaxis=dict(autorange='reversed'),  # Reverse y-axis so rank 1 is at top
            height=400
        )

        return fig

    def _prepare_excel_export(self,
                            all_data: pd.DataFrame,
                            selected_municipalities: List[str],
                            comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Excel export"""
        selected_data = all_data[all_data['nome_municipio'].isin(selected_municipalities)]

        return {
            'selected_data': selected_data,
            'state_summary': {
                'total_municipalities': len(all_data),
                'avg_biogas': all_data['biogas_potential_m3_day'].mean(),
                'total_biogas': all_data['biogas_potential_m3_day'].sum()
            },
            'comparison_summary': comparison_results
        }

    def _prepare_pdf_export(self,
                          all_data: pd.DataFrame,
                          selected_municipalities: List[str],
                          comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for PDF report"""
        return {
            'municipalities': selected_municipalities,
            'comparison_data': comparison_results['comparison_data'],
            'charts': comparison_results['comparison_charts'],
            'report_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _generate_text_summary(self,
                             selected_municipalities: List[str],
                             comparison_results: Dict[str, Any]) -> str:
        """Generate text summary of comparison"""
        summary = f"""
CP2B Maps V2 - Municipality Comparison Summary
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

Selected Municipalities: {', '.join(selected_municipalities)}
Number of Municipalities Compared: {len(selected_municipalities)}

Key Findings:
- Highest biogas potential municipality
- Most efficient municipality (per capita)
- Largest population municipality
- Performance against state averages

For detailed analysis, please refer to the full comparison report.
"""
        return summary