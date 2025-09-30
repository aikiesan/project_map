"""
CP2B Maps V2 - Environmental Analysis Module
Environmental impact assessment, CO2 reduction calculations, and sustainability metrics
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

# Import V1 design system
from src.ui.components.design_system import (
    render_section_header,
    render_info_banner
)

logger = get_logger(__name__)


class EnvironmentalAnalyzer:
    """
    Environmental impact analysis engine for biogas projects
    Features: CO2 reduction, lifecycle assessment, sustainability metrics
    """

    def __init__(self):
        """Initialize Environmental Analyzer"""
        self.logger = get_logger(self.__class__.__name__)

        # Environmental factors (based on scientific literature)
        self.environmental_factors = {
            'co2_reduction_kg_per_m3_biogas': 2.3,  # kg CO2 avoided per m³ biogas
            'methane_gwp': 25,  # Global Warming Potential of methane (25x CO2)
            'fossil_fuel_substitution_rate': 0.85,  # 85% fossil fuel substitution
            'fertilizer_replacement_kg_per_m3': 0.5,  # kg fertilizer replaced per m³ biogas
            'water_saving_liters_per_m3': 2.5,  # liters water saved per m³ biogas
            'soil_improvement_factor': 1.2,  # Soil quality improvement factor
            'air_quality_improvement_factor': 0.15  # Local air quality improvement
        }

    def render_environmental_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render comprehensive environmental impact analysis

        Args:
            data: Municipality data with biogas calculations
            scenario_config: Scenario parameters

        Returns:
            Dictionary with environmental analysis results
        """
        try:
            render_section_header(
                "🌍 Análise de Impacto Ambiental",
                description="Redução de CO2, métricas de sustentabilidade e benefícios ecológicos"
            )

            # Calculate environmental metrics
            environmental_data = self._calculate_environmental_metrics(data, scenario_config)

            # Environmental overview
            self._render_environmental_overview(environmental_data)

            # CO2 impact analysis
            co2_results = self._render_co2_impact_analysis(environmental_data)

            # Sustainability metrics
            sustainability_results = self._render_sustainability_metrics(environmental_data)

            # Environmental benefits charts
            benefits_results = self._create_environmental_impact_charts(environmental_data)

            # Regional environmental impact
            regional_impact = self._render_regional_environmental_impact(environmental_data)

            return {
                'environmental_data': environmental_data,
                'co2_results': co2_results,
                'sustainability_results': sustainability_results,
                'benefits_results': benefits_results,
                'regional_impact': regional_impact
            }

        except Exception as e:
            self.logger.error(f"Error in environmental analysis: {e}")
            st.error("❌ Error performing environmental analysis")
            return {}

    def _calculate_environmental_metrics(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate environmental impact metrics for each municipality"""
        try:
            env_data = data.copy()

            # Calculate total biogas potential
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]
            env_data['total_biogas_potential'] = env_data[biogas_columns].sum(axis=1)

            # CO2 reduction calculations
            env_data['co2_reduction_tons_year'] = (
                env_data['total_biogas_potential'] *
                self.environmental_factors['co2_reduction_kg_per_m3_biogas'] / 1000
            )

            # Methane emission reduction (from waste decomposition)
            env_data['methane_reduction_tons_year'] = (
                env_data['total_biogas_potential'] * 0.6 / 1000  # 60% methane in biogas
            )

            # CO2 equivalent reduction (including methane GWP)
            env_data['co2_equivalent_reduction_tons_year'] = (
                env_data['co2_reduction_tons_year'] +
                (env_data['methane_reduction_tons_year'] * self.environmental_factors['methane_gwp'])
            )

            # Fossil fuel substitution
            env_data['fossil_fuel_avoided_tons_year'] = (
                env_data['total_biogas_potential'] *
                self.environmental_factors['fossil_fuel_substitution_rate'] * 0.7 / 1000  # 0.7 kg per m³
            )

            # Fertilizer replacement potential
            env_data['fertilizer_replacement_tons_year'] = (
                env_data['total_biogas_potential'] *
                self.environmental_factors['fertilizer_replacement_kg_per_m3'] / 1000
            )

            # Water conservation
            env_data['water_saving_million_liters_year'] = (
                env_data['total_biogas_potential'] *
                self.environmental_factors['water_saving_liters_per_m3'] / 1e6
            )

            # Air quality improvement score (arbitrary units)
            env_data['air_quality_score'] = (
                env_data['co2_equivalent_reduction_tons_year'] *
                self.environmental_factors['air_quality_improvement_factor']
            )

            # Soil improvement potential (ha benefited)
            env_data['soil_improvement_hectares'] = (
                env_data['fertilizer_replacement_tons_year'] *
                self.environmental_factors['soil_improvement_factor']
            )

            # Calculate cumulative 20-year impact
            env_data['co2_reduction_20years'] = env_data['co2_equivalent_reduction_tons_year'] * 20
            env_data['total_environmental_value'] = (
                env_data['co2_reduction_20years'] * 45 +  # Carbon credit value
                env_data['water_saving_million_liters_year'] * 20 * 2.5 +  # Water value
                env_data['fertilizer_replacement_tons_year'] * 20 * 2800  # Fertilizer value
            )

            return env_data

        except Exception as e:
            self.logger.error(f"Error calculating environmental metrics: {e}")
            return data

    def _render_environmental_overview(self, data: pd.DataFrame) -> None:
        """Render environmental impact overview"""
        try:
            st.markdown("#### 🌱 Environmental Impact Overview")

            # Calculate summary metrics
            total_co2_reduction = data['co2_equivalent_reduction_tons_year'].sum()
            total_water_saving = data['water_saving_million_liters_year'].sum()
            total_fertilizer_replacement = data['fertilizer_replacement_tons_year'].sum()
            total_soil_improvement = data['soil_improvement_hectares'].sum()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "CO2 Equivalent Reduction",
                    f"{total_co2_reduction / 1e6:.2f}M tons/year",
                    help="Total CO2 equivalent reduction including methane GWP"
                )

            with col2:
                st.metric(
                    "Water Conservation",
                    f"{total_water_saving:.1f}M liters/year",
                    help="Water saved through improved waste management"
                )

            with col3:
                st.metric(
                    "Fertilizer Replacement",
                    f"{total_fertilizer_replacement / 1000:.1f}K tons/year",
                    help="Chemical fertilizer that can be replaced with digestate"
                )

            with col4:
                st.metric(
                    "Soil Improvement",
                    f"{total_soil_improvement / 1000:.1f}K hectares",
                    help="Agricultural land that can benefit from digestate application"
                )

            # Environmental value estimation
            total_environmental_value = data['total_environmental_value'].sum()
            st.info(
                f"💰 **Total Environmental Value (20 years):** R$ {total_environmental_value / 1e9:.2f} billion\n\n"
                f"This includes carbon credits, water conservation value, and fertilizer replacement savings."
            )

        except Exception as e:
            self.logger.error(f"Error rendering environmental overview: {e}")

    def _render_co2_impact_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render CO2 impact analysis"""
        try:
            st.markdown("#### 🌡️ Carbon Footprint Reduction Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # CO2 reduction by source type
                source_data = []
                biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]

                for col in biogas_columns:
                    if col in data.columns:
                        source_name = col.replace('biogas_', '').replace('_nm_ano', '').title()
                        source_co2 = (data[col] * self.environmental_factors['co2_reduction_kg_per_m3_biogas'] / 1000).sum()
                        if source_co2 > 0:
                            source_data.append({'Source': source_name, 'CO2_Reduction': source_co2})

                if source_data:
                    source_df = pd.DataFrame(source_data)
                    fig_sources = px.pie(
                        source_df,
                        values='CO2_Reduction',
                        names='Source',
                        title='CO2 Reduction by Biogas Source',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_sources.update_layout(height=400)
                    st.plotly_chart(fig_sources, use_container_width=True)

            with col2:
                # Cumulative CO2 reduction over time
                years = list(range(1, 21))  # 20 years
                cumulative_co2 = [data['co2_equivalent_reduction_tons_year'].sum() * year for year in years]

                fig_cumulative = go.Figure()
                fig_cumulative.add_trace(go.Scatter(
                    x=years,
                    y=cumulative_co2,
                    mode='lines+markers',
                    name='Cumulative CO2 Reduction',
                    line=dict(color='green', width=3)
                ))
                fig_cumulative.update_layout(
                    title='Cumulative CO2 Reduction Over Time',
                    xaxis_title='Years',
                    yaxis_title='CO2 Equivalent Reduction (tons)',
                    height=400
                )
                st.plotly_chart(fig_cumulative, use_container_width=True)

            # Top municipalities by environmental impact
            if 'municipio' in data.columns:
                top_env_municipalities = data.nlargest(10, 'co2_equivalent_reduction_tons_year')[
                    ['municipio', 'co2_equivalent_reduction_tons_year', 'water_saving_million_liters_year', 'fertilizer_replacement_tons_year']
                ]

                st.markdown("##### 🏆 Top 10 Municipalities by Environmental Impact")
                display_data = top_env_municipalities.copy()
                display_data.columns = ['Municipality', 'CO2 Reduction (tons/year)', 'Water Saving (M liters/year)', 'Fertilizer Replacement (tons/year)']
                display_data = display_data.round(2)
                st.dataframe(display_data, use_container_width=True)

            return {
                'source_distribution': fig_sources if source_data else None,
                'cumulative_co2': fig_cumulative,
                'top_municipalities': top_env_municipalities if 'municipio' in data.columns else pd.DataFrame()
            }

        except Exception as e:
            self.logger.error(f"Error rendering CO2 impact analysis: {e}")
            return {}

    def _render_sustainability_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render sustainability metrics and indicators"""
        try:
            st.markdown("#### ♻️ Sustainability Metrics")

            # Calculate sustainability indicators
            total_biogas = data['total_biogas_potential'].sum()

            # SDG impact metrics
            sdg_metrics = {
                'Clean Energy (SDG 7)': {
                    'value': total_biogas * 6.0 / 1e6,  # MWh equivalent
                    'unit': 'MWh/year',
                    'description': 'Renewable energy generation potential'
                },
                'Climate Action (SDG 13)': {
                    'value': data['co2_equivalent_reduction_tons_year'].sum() / 1e6,
                    'unit': 'Million tons CO2eq/year',
                    'description': 'Carbon footprint reduction'
                },
                'Sustainable Agriculture (SDG 2)': {
                    'value': data['fertilizer_replacement_tons_year'].sum() / 1000,
                    'unit': 'Thousand tons fertilizer/year',
                    'description': 'Organic fertilizer production'
                },
                'Clean Water (SDG 6)': {
                    'value': data['water_saving_million_liters_year'].sum(),
                    'unit': 'Million liters/year',
                    'description': 'Water resource conservation'
                },
                'Life on Land (SDG 15)': {
                    'value': data['soil_improvement_hectares'].sum() / 1000,
                    'unit': 'Thousand hectares',
                    'description': 'Soil health improvement'
                }
            }

            # Display SDG metrics
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 🎯 UN Sustainable Development Goals Impact")
                for sdg, metrics in sdg_metrics.items():
                    st.metric(
                        sdg,
                        f"{metrics['value']:.2f} {metrics['unit']}",
                        help=metrics['description']
                    )

            with col2:
                # Sustainability score radar chart
                sustainability_scores = {
                    'Carbon Reduction': min(100, data['co2_equivalent_reduction_tons_year'].sum() / 10000),
                    'Resource Efficiency': min(100, total_biogas / 100000),
                    'Waste Management': min(100, data['fertilizer_replacement_tons_year'].sum() / 1000),
                    'Water Conservation': min(100, data['water_saving_million_liters_year'].sum() * 10),
                    'Soil Health': min(100, data['soil_improvement_hectares'].sum() / 10000)
                }

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=list(sustainability_scores.values()),
                    theta=list(sustainability_scores.keys()),
                    fill='toself',
                    name='Sustainability Score',
                    line=dict(color='green')
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    title="Sustainability Performance Score",
                    height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            return {
                'sdg_metrics': sdg_metrics,
                'sustainability_scores': sustainability_scores,
                'radar_chart': fig_radar
            }

        except Exception as e:
            self.logger.error(f"Error rendering sustainability metrics: {e}")
            return {}

    def _create_environmental_impact_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive environmental impact visualizations"""
        try:
            st.markdown("#### 📊 Environmental Impact Visualizations")

            # Multi-metric comparison chart
            if 'municipio' in data.columns:
                # Select top 15 municipalities by total environmental impact
                top_municipalities = data.nlargest(15, 'total_environmental_value')

                fig_multi = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('CO2 Reduction', 'Water Saving', 'Fertilizer Replacement', 'Soil Improvement'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )

                # CO2 reduction
                fig_multi.add_trace(
                    go.Bar(
                        x=top_municipalities['municipio'],
                        y=top_municipalities['co2_equivalent_reduction_tons_year'],
                        name='CO2 Reduction',
                        marker_color='green'
                    ),
                    row=1, col=1
                )

                # Water saving
                fig_multi.add_trace(
                    go.Bar(
                        x=top_municipalities['municipio'],
                        y=top_municipalities['water_saving_million_liters_year'],
                        name='Water Saving',
                        marker_color='blue'
                    ),
                    row=1, col=2
                )

                # Fertilizer replacement
                fig_multi.add_trace(
                    go.Bar(
                        x=top_municipalities['municipio'],
                        y=top_municipalities['fertilizer_replacement_tons_year'],
                        name='Fertilizer Replacement',
                        marker_color='brown'
                    ),
                    row=2, col=1
                )

                # Soil improvement
                fig_multi.add_trace(
                    go.Bar(
                        x=top_municipalities['municipio'],
                        y=top_municipalities['soil_improvement_hectares'],
                        name='Soil Improvement',
                        marker_color='orange'
                    ),
                    row=2, col=2
                )

                fig_multi.update_layout(
                    height=800,
                    title_text="Environmental Impact by Municipality (Top 15)",
                    showlegend=False
                )

                # Rotate x-axis labels for better readability
                fig_multi.update_xaxes(tickangle=45)

                st.plotly_chart(fig_multi, use_container_width=True)

            # Environmental value vs biogas potential scatter
            fig_scatter = px.scatter(
                data.dropna(subset=['total_biogas_potential', 'total_environmental_value']),
                x='total_biogas_potential',
                y='total_environmental_value',
                hover_data=['municipio'] if 'municipio' in data.columns else None,
                title='Environmental Value vs Biogas Potential',
                labels={
                    'total_biogas_potential': 'Total Biogas Potential (m³/year)',
                    'total_environmental_value': 'Total Environmental Value (BRL, 20 years)'
                },
                color='co2_equivalent_reduction_tons_year',
                color_continuous_scale='Viridis',
                size='water_saving_million_liters_year',
                size_max=20
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)

            return {
                'multi_metric_chart': fig_multi if 'municipio' in data.columns else None,
                'environmental_value_scatter': fig_scatter
            }

        except Exception as e:
            self.logger.error(f"Error creating environmental impact charts: {e}")
            return {}

    def _render_regional_environmental_impact(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render regional environmental impact analysis"""
        try:
            st.markdown("#### 🗺️ Regional Environmental Impact")

            # Environmental impact by region (if region data is available)
            region_column = None
            for col in data.columns:
                if 'regiao' in col.lower() or 'region' in col.lower():
                    region_column = col
                    break

            if region_column:
                regional_impact = data.groupby(region_column).agg({
                    'co2_equivalent_reduction_tons_year': 'sum',
                    'water_saving_million_liters_year': 'sum',
                    'fertilizer_replacement_tons_year': 'sum',
                    'total_environmental_value': 'sum',
                    'municipio': 'count' if 'municipio' in data.columns else 'size'
                }).round(2)

                regional_impact.columns = ['CO2 Reduction (tons/year)', 'Water Saving (M liters/year)',
                                         'Fertilizer Replacement (tons/year)', 'Environmental Value (BRL)',
                                         'Municipalities']

                st.markdown("##### 📍 Environmental Impact by Region")
                st.dataframe(regional_impact, use_container_width=True)

                # Regional comparison chart
                fig_regional = px.bar(
                    regional_impact.reset_index(),
                    x=region_column,
                    y='CO2 Reduction (tons/year)',
                    title='CO2 Reduction by Region',
                    color='Environmental Value (BRL)',
                    color_continuous_scale='Viridis'
                )
                fig_regional.update_layout(height=400)
                st.plotly_chart(fig_regional, use_container_width=True)

                return {
                    'regional_impact': regional_impact,
                    'regional_chart': fig_regional
                }
            else:
                st.info("ℹ️ Regional data not available for detailed regional analysis")
                return {}

        except Exception as e:
            self.logger.error(f"Error rendering regional environmental impact: {e}")
            return {}


# Factory function
def create_environmental_analyzer() -> EnvironmentalAnalyzer:
    """Create EnvironmentalAnalyzer instance"""
    return EnvironmentalAnalyzer()