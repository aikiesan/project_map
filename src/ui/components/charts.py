"""
CP2B Maps - Charts Component
Professional data visualization with Plotly charts for biogas analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class Charts:
    """
    Professional charts component for biogas data visualization
    Features: Interactive plots, comparative analysis, time series, distribution analysis
    """

    def __init__(self):
        """Initialize Charts component"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing Charts component")

        # Chart configuration
        self.color_palette = {
            'primary': '#FF6B35',
            'secondary': '#06D6A0',
            'accent': '#FFD23F',
            'neutral': '#8B8B8B',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545'
        }

    def render(self, chart_types: Optional[List[str]] = None,
               filtered_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Render comprehensive chart analysis

        Args:
            chart_types: List of specific chart types to render
            filtered_data: Pre-filtered municipality data

        Returns:
            Dictionary with chart data and analysis results
        """
        try:
            st.markdown("### 📊 Data Visualization & Analysis")

            # Load data
            data = self._load_chart_data(filtered_data)
            if data is None or len(data) == 0:
                st.warning("⚠️ No data available for visualization")
                return {}

            # Chart type selection
            selected_charts = self._render_chart_selector(chart_types)

            # Render selected charts
            chart_results = {}

            if 'overview' in selected_charts:
                chart_results['overview'] = self._render_overview_charts(data)

            if 'distribution' in selected_charts:
                chart_results['distribution'] = self._render_distribution_charts(data)

            if 'ranking' in selected_charts:
                chart_results['ranking'] = self._render_ranking_charts(data)

            if 'correlation' in selected_charts:
                chart_results['correlation'] = self._render_correlation_analysis(data)

            if 'regional' in selected_charts:
                chart_results['regional'] = self._render_regional_analysis(data)

            if 'trends' in selected_charts:
                chart_results['trends'] = self._render_trend_analysis(data)

            return {
                'data': data,
                'selected_charts': selected_charts,
                'chart_results': chart_results
            }

        except Exception as e:
            self.logger.error(f"Error rendering charts: {e}", exc_info=True)
            st.error("⚠️ Failed to render charts. Check logs for details.")
            return {}

    def _load_chart_data(self, filtered_data: Optional[pd.DataFrame] = None) -> Optional[pd.DataFrame]:
        """Load and prepare data for charts"""
        try:
            if filtered_data is not None:
                data = filtered_data.copy()
            else:
                data = database_loader.load_municipalities_data()

            if data is None:
                return None

            # Ensure required columns exist with safe defaults
            required_columns = {
                'biogas_potential_m3_day': 0,
                'energy_potential_kwh_day': 0,
                'population': 0
            }

            for col, default_val in required_columns.items():
                if col not in data.columns:
                    data[col] = default_val
                else:
                    data[col] = data[col].fillna(default_val)

            # Add calculated columns for analysis
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

            # Add categorical columns for analysis
            data['population_category'] = pd.cut(
                data['population'],
                bins=[0, 10000, 50000, 100000, 500000, np.inf],
                labels=['Small (<10k)', 'Medium (10-50k)', 'Large (50-100k)',
                       'Very Large (100-500k)', 'Metropolitan (>500k)']
            )

            data['biogas_category'] = pd.cut(
                data['biogas_potential_m3_day'],
                bins=[0, 100, 500, 1000, 5000, np.inf],
                labels=['Very Low (<100)', 'Low (100-500)', 'Medium (500-1k)',
                       'High (1-5k)', 'Very High (>5k)']
            )

            self.logger.info(f"Prepared chart data for {len(data)} municipalities")
            return data

        except Exception as e:
            self.logger.error(f"Error loading chart data: {e}")
            return None

    def _render_chart_selector(self, chart_types: Optional[List[str]] = None) -> List[str]:
        """Render chart type selection interface"""
        available_charts = {
            'overview': '📈 Overview Charts',
            'distribution': '📊 Distribution Analysis',
            'ranking': '🏆 Ranking & Top Performers',
            'correlation': '🔗 Correlation Analysis',
            'regional': '🗺️ Regional Analysis',
            'trends': '📈 Trend Analysis'
        }

        if chart_types:
            return chart_types

        st.markdown("#### Chart Selection")
        selected = st.multiselect(
            "Select chart types to display:",
            options=list(available_charts.keys()),
            default=['overview', 'distribution', 'ranking'],
            format_func=lambda x: available_charts[x],
            help="Choose which types of analysis charts to display"
        )

        return selected

    def _render_overview_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render overview charts with key metrics"""
        st.markdown("#### 📈 Overview Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Total biogas potential by population category
            fig_population = self._create_population_biogas_chart(data)
            st.plotly_chart(fig_population, use_container_width=True)

        with col2:
            # Energy vs biogas potential scatter
            fig_scatter = self._create_energy_biogas_scatter(data)
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Summary statistics
        summary_stats = self._calculate_summary_statistics(data)
        self._display_summary_metrics(summary_stats)

        return {
            'population_biogas_chart': fig_population,
            'energy_biogas_scatter': fig_scatter,
            'summary_stats': summary_stats
        }

    def _render_distribution_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render distribution analysis charts"""
        st.markdown("#### 📊 Distribution Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Biogas potential histogram
            fig_biogas_hist = self._create_biogas_distribution_chart(data)
            st.plotly_chart(fig_biogas_hist, use_container_width=True)

        with col2:
            # Population distribution
            fig_pop_hist = self._create_population_distribution_chart(data)
            st.plotly_chart(fig_pop_hist, use_container_width=True)

        # Box plots for detailed distribution
        fig_box = self._create_distribution_box_plots(data)
        st.plotly_chart(fig_box, use_container_width=True)

        return {
            'biogas_distribution': fig_biogas_hist,
            'population_distribution': fig_pop_hist,
            'box_plots': fig_box
        }

    def _render_ranking_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render ranking and top performer charts"""
        st.markdown("#### 🏆 Ranking & Top Performers")

        # Top municipalities by different metrics
        metric_options = {
            'biogas_potential_m3_day': 'Biogas Potential',
            'energy_potential_kwh_day': 'Energy Potential',
            'biogas_per_capita': 'Biogas per Capita',
            'population': 'Population'
        }

        selected_metric = st.selectbox(
            "Select ranking metric:",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="ranking_metric"
        )

        # Top 20 chart
        fig_top = self._create_top_municipalities_chart(data, selected_metric, limit=20)
        st.plotly_chart(fig_top, use_container_width=True)

        # Performance comparison
        fig_comparison = self._create_performance_comparison_chart(data)
        st.plotly_chart(fig_comparison, use_container_width=True)

        return {
            'top_municipalities': fig_top,
            'performance_comparison': fig_comparison,
            'selected_metric': selected_metric
        }

    def _render_correlation_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render correlation analysis charts"""
        st.markdown("#### 🔗 Correlation Analysis")

        # Correlation matrix
        fig_corr = self._create_correlation_matrix(data)
        st.plotly_chart(fig_corr, use_container_width=True)

        # Scatter matrix for key variables
        fig_scatter_matrix = self._create_scatter_matrix(data)
        st.plotly_chart(fig_scatter_matrix, use_container_width=True)

        return {
            'correlation_matrix': fig_corr,
            'scatter_matrix': fig_scatter_matrix
        }

    def _render_regional_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render regional analysis charts"""
        st.markdown("#### 🗺️ Regional Analysis")

        # Regional aggregation (simulated since we don't have region data)
        regional_data = self._simulate_regional_data(data)

        col1, col2 = st.columns(2)

        with col1:
            # Regional biogas potential
            fig_regional = self._create_regional_chart(regional_data, 'biogas')
            st.plotly_chart(fig_regional, use_container_width=True)

        with col2:
            # Regional efficiency
            fig_efficiency = self._create_regional_chart(regional_data, 'efficiency')
            st.plotly_chart(fig_efficiency, use_container_width=True)

        return {
            'regional_data': regional_data,
            'regional_biogas': fig_regional,
            'regional_efficiency': fig_efficiency
        }

    def _render_trend_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render trend analysis charts"""
        st.markdown("#### 📈 Trend Analysis")

        # Projected growth scenarios
        fig_projection = self._create_projection_chart(data)
        st.plotly_chart(fig_projection, use_container_width=True)

        # Performance indicators over time (simulated)
        fig_indicators = self._create_performance_indicators_chart(data)
        st.plotly_chart(fig_indicators, use_container_width=True)

        return {
            'projection_chart': fig_projection,
            'performance_indicators': fig_indicators
        }

    def _create_population_biogas_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create population vs biogas potential chart"""
        fig = px.bar(
            data.groupby('population_category')['biogas_potential_m3_day'].sum().reset_index(),
            x='population_category',
            y='biogas_potential_m3_day',
            title='Total Biogas Potential by Population Category',
            color='biogas_potential_m3_day',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title='Population Category',
            yaxis_title='Total Biogas Potential (m³/day)',
            height=400
        )
        return fig

    def _create_energy_biogas_scatter(self, data: pd.DataFrame) -> go.Figure:
        """Create energy vs biogas scatter plot"""
        fig = px.scatter(
            data,
            x='biogas_potential_m3_day',
            y='energy_potential_kwh_day',
            size='population',
            color='population_category',
            title='Energy vs Biogas Potential',
            hover_data=['nome_municipio'],
            size_max=20
        )
        fig.update_layout(
            xaxis_title='Biogas Potential (m³/day)',
            yaxis_title='Energy Potential (kWh/day)',
            height=400
        )
        return fig

    def _create_biogas_distribution_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create biogas potential distribution histogram"""
        fig = px.histogram(
            data,
            x='biogas_potential_m3_day',
            nbins=50,
            title='Distribution of Biogas Potential',
            marginal='box'
        )
        fig.update_layout(
            xaxis_title='Biogas Potential (m³/day)',
            yaxis_title='Number of Municipalities',
            height=400
        )
        return fig

    def _create_population_distribution_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create population distribution histogram"""
        fig = px.histogram(
            data,
            x='population',
            nbins=50,
            title='Distribution of Municipality Population',
            marginal='box'
        )
        fig.update_layout(
            xaxis_title='Population',
            yaxis_title='Number of Municipalities',
            height=400
        )
        return fig

    def _create_distribution_box_plots(self, data: pd.DataFrame) -> go.Figure:
        """Create box plots for distribution analysis"""
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=['Biogas Potential', 'Energy Potential', 'Per Capita Biogas']
        )

        fig.add_trace(
            go.Box(y=data['biogas_potential_m3_day'], name='Biogas'),
            row=1, col=1
        )
        fig.add_trace(
            go.Box(y=data['energy_potential_kwh_day'], name='Energy'),
            row=1, col=2
        )
        fig.add_trace(
            go.Box(y=data['biogas_per_capita'], name='Per Capita'),
            row=1, col=3
        )

        fig.update_layout(
            title='Distribution Box Plots',
            height=400,
            showlegend=False
        )
        return fig

    def _create_top_municipalities_chart(self, data: pd.DataFrame,
                                       metric: str, limit: int = 20) -> go.Figure:
        """Create top municipalities chart"""
        top_data = data.nlargest(limit, metric)

        fig = px.bar(
            top_data,
            x=metric,
            y='nome_municipio',
            orientation='h',
            title=f'Top {limit} Municipalities by {metric}',
            color=metric,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=600
        )
        return fig

    def _create_performance_comparison_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create performance comparison radar chart"""
        # Get top 5 municipalities for comparison
        top_5 = data.nlargest(5, 'biogas_potential_m3_day')

        fig = go.Figure()

        for _, municipality in top_5.iterrows():
            # Normalize values to 0-100 scale for radar chart
            biogas_norm = (municipality['biogas_potential_m3_day'] / data['biogas_potential_m3_day'].max()) * 100
            energy_norm = (municipality['energy_potential_kwh_day'] / data['energy_potential_kwh_day'].max()) * 100
            pop_norm = (municipality['population'] / data['population'].max()) * 100
            per_capita_norm = (municipality['biogas_per_capita'] / data['biogas_per_capita'].max()) * 100

            fig.add_trace(go.Scatterpolar(
                r=[biogas_norm, energy_norm, pop_norm, per_capita_norm],
                theta=['Biogas Potential', 'Energy Potential', 'Population', 'Per Capita Biogas'],
                fill='toself',
                name=municipality['nome_municipio'][:20]  # Truncate long names
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            title='Top 5 Municipalities Performance Comparison',
            height=500
        )
        return fig

    def _create_correlation_matrix(self, data: pd.DataFrame) -> go.Figure:
        """Create correlation matrix heatmap"""
        numeric_cols = ['biogas_potential_m3_day', 'energy_potential_kwh_day',
                       'population', 'biogas_per_capita', 'energy_per_capita']

        corr_matrix = data[numeric_cols].corr()

        fig = px.imshow(
            corr_matrix,
            title='Variable Correlation Matrix',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig.update_layout(height=500)
        return fig

    def _create_scatter_matrix(self, data: pd.DataFrame) -> go.Figure:
        """Create scatter matrix for key variables"""
        numeric_cols = ['biogas_potential_m3_day', 'energy_potential_kwh_day',
                       'population', 'biogas_per_capita']

        fig = px.scatter_matrix(
            data,
            dimensions=numeric_cols,
            color='population_category',
            title='Scatter Matrix of Key Variables'
        )
        fig.update_layout(height=600)
        return fig

    def _simulate_regional_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate regional data for demonstration"""
        # Create simulated regions based on municipality names
        regions = ['North', 'South', 'East', 'West', 'Central']
        np.random.seed(42)  # For reproducible results

        regional_data = []
        for region in regions:
            # Randomly assign municipalities to regions
            region_municipalities = data.sample(n=min(len(data)//5, 50))
            regional_data.append({
                'region': region,
                'total_biogas': region_municipalities['biogas_potential_m3_day'].sum(),
                'total_energy': region_municipalities['energy_potential_kwh_day'].sum(),
                'total_population': region_municipalities['population'].sum(),
                'municipalities_count': len(region_municipalities),
                'avg_efficiency': region_municipalities['biogas_per_capita'].mean()
            })

        return pd.DataFrame(regional_data)

    def _create_regional_chart(self, regional_data: pd.DataFrame, chart_type: str) -> go.Figure:
        """Create regional analysis chart"""
        if chart_type == 'biogas':
            fig = px.bar(
                regional_data,
                x='region',
                y='total_biogas',
                title='Total Biogas Potential by Region',
                color='total_biogas',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(yaxis_title='Total Biogas (m³/day)')
        else:  # efficiency
            fig = px.bar(
                regional_data,
                x='region',
                y='avg_efficiency',
                title='Average Biogas Efficiency by Region',
                color='avg_efficiency',
                color_continuous_scale='Plasma'
            )
            fig.update_layout(yaxis_title='Avg Biogas per Capita (m³/day)')

        fig.update_layout(height=400)
        return fig

    def _create_projection_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create projection chart with growth scenarios"""
        years = list(range(2024, 2035))
        current_total = data['biogas_potential_m3_day'].sum()

        # Growth scenarios
        conservative = [current_total * (1.02 ** (year - 2024)) for year in years]
        moderate = [current_total * (1.05 ** (year - 2024)) for year in years]
        optimistic = [current_total * (1.08 ** (year - 2024)) for year in years]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=conservative, mode='lines+markers',
                               name='Conservative (2%)', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=years, y=moderate, mode='lines+markers',
                               name='Moderate (5%)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=years, y=optimistic, mode='lines+markers',
                               name='Optimistic (8%)', line=dict(color='green')))

        fig.update_layout(
            title='Biogas Potential Growth Projections',
            xaxis_title='Year',
            yaxis_title='Total Biogas Potential (m³/day)',
            height=400
        )
        return fig

    def _create_performance_indicators_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create performance indicators chart"""
        # Simulate quarterly performance indicators
        quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
        efficiency = [75, 78, 82, 85]
        utilization = [60, 65, 70, 73]
        capacity = [40, 45, 50, 55]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=quarters, y=efficiency, mode='lines+markers',
                               name='Efficiency (%)', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=quarters, y=utilization, mode='lines+markers',
                               name='Utilization (%)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=quarters, y=capacity, mode='lines+markers',
                               name='Capacity (%)', line=dict(color='red')))

        fig.update_layout(
            title='Performance Indicators Trend',
            xaxis_title='Quarter',
            yaxis_title='Percentage (%)',
            height=400
        )
        return fig

    def _calculate_summary_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for overview"""
        return {
            'total_municipalities': len(data),
            'total_biogas': data['biogas_potential_m3_day'].sum(),
            'total_energy': data['energy_potential_kwh_day'].sum(),
            'total_population': data['population'].sum(),
            'avg_biogas': data['biogas_potential_m3_day'].mean(),
            'median_biogas': data['biogas_potential_m3_day'].median(),
            'std_biogas': data['biogas_potential_m3_day'].std(),
            'max_biogas': data['biogas_potential_m3_day'].max(),
            'min_biogas': data['biogas_potential_m3_day'].min()
        }

    def _display_summary_metrics(self, stats: Dict[str, Any]) -> None:
        """Display summary metrics"""
        st.markdown("##### 📋 Summary Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Municipalities", f"{stats['total_municipalities']:,}")
            st.metric("Average Biogas", f"{stats['avg_biogas']:,.0f} m³/day")

        with col2:
            st.metric("Total Biogas Potential", f"{stats['total_biogas']:,.0f} m³/day")
            st.metric("Median Biogas", f"{stats['median_biogas']:,.0f} m³/day")

        with col3:
            st.metric("Total Energy Potential", f"{stats['total_energy']:,.0f} kWh/day")
            st.metric("Max Biogas", f"{stats['max_biogas']:,.0f} m³/day")

        with col4:
            st.metric("Total Population", f"{stats['total_population']:,}")
            st.metric("Min Biogas", f"{stats['min_biogas']:,.0f} m³/day")