"""
CP2B Maps - Municipality Details Component
Detailed municipality information with biogas breakdown and analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, Any, List
import numpy as np

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class MunicipalityDetails:
    """
    Detailed municipality component with biogas analysis and visualization
    Features: Biogas breakdown, waste composition, comparison charts, KPIs
    """

    def __init__(self):
        """Initialize Municipality Details component"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing MunicipalityDetails component")

    def render(self, municipality_name: Optional[str] = None,
               comparison_municipalities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Render municipality details with comprehensive analysis

        Args:
            municipality_name: Selected municipality for detailed view
            comparison_municipalities: List of municipalities for comparison

        Returns:
            Dictionary with municipality data and analysis results
        """
        try:
            if not municipality_name:
                self._render_selection_prompt()
                return {}

            st.markdown(f"### 🏛️ Municipality Analysis: {municipality_name}")

            # Load municipality data
            municipality_data = self._load_municipality_data(municipality_name)
            if not municipality_data:
                st.error(f"⚠️ No data found for {municipality_name}")
                return {}

            # Main analysis sections
            overview_data = self._render_overview_section(municipality_data)
            biogas_analysis = self._render_biogas_analysis(municipality_data)
            comparative_analysis = self._render_comparative_analysis(
                municipality_data, comparison_municipalities
            )
            environmental_impact = self._render_environmental_impact(municipality_data)

            # Combine results
            analysis_results = {
                'municipality_data': municipality_data,
                'overview': overview_data,
                'biogas_analysis': biogas_analysis,
                'comparative_analysis': comparative_analysis,
                'environmental_impact': environmental_impact
            }

            return analysis_results

        except Exception as e:
            self.logger.error(f"Error rendering municipality details: {e}", exc_info=True)
            st.error("⚠️ Failed to render municipality details. Check logs.")
            return {}

    def _render_selection_prompt(self) -> None:
        """Show municipality selection prompt"""
        st.markdown("### 🏛️ Municipality Details")
        st.info("👆 Select a municipality from the sidebar search or click on the map to see detailed analysis.")

        # Show top 10 municipalities as quick selection
        try:
            top_municipalities = database_loader.get_top_municipalities(limit=10)
            if top_municipalities is not None:
                st.markdown("#### 🏆 Quick Selection - Top Municipalities")

                # Create clickable municipality cards
                cols = st.columns(2)
                for i, (_, municipality) in enumerate(top_municipalities.iterrows()):
                    col = cols[i % 2]
                    with col:
                        name = municipality.get('nome_municipio', 'Unknown')
                        biogas = municipality.get('biogas_potential_m3_day', 0)

                        if st.button(
                            f"📍 {name}\n{biogas:,.0f} m³/day",
                            help=f"Click to analyze {name}",
                            key=f"quick_select_{name}"
                        ):
                            st.session_state.selected_municipality = name
                            st.rerun()

        except Exception as e:
            self.logger.error(f"Error showing quick selection: {e}")

    def _load_municipality_data(self, municipality_name: str) -> Optional[pd.Series]:
        """Load comprehensive data for a specific municipality"""
        try:
            municipalities_df = database_loader.load_municipalities_data()
            if municipalities_df is None:
                return None

            # Find municipality by name
            municipality_row = municipalities_df[
                municipalities_df['nome_municipio'] == municipality_name
            ]

            if len(municipality_row) == 0:
                self.logger.warning(f"Municipality not found: {municipality_name}")
                return None

            return municipality_row.iloc[0]

        except Exception as e:
            self.logger.error(f"Error loading municipality data: {e}")
            return None

    def _render_overview_section(self, municipality_data: pd.Series) -> Dict[str, Any]:
        """Render municipality overview with key metrics"""
        st.markdown("#### 📊 Key Performance Indicators")

        # Extract data with safe fallbacks
        name = municipality_data.get('nome_municipio', 'Unknown')
        biogas_daily = municipality_data.get('biogas_potential_m3_day', 0)
        energy_daily = municipality_data.get('energy_potential_kwh_day', 0)
        population = municipality_data.get('population', 0)

        # Calculate additional metrics
        biogas_annual = biogas_daily * 365
        energy_annual = energy_daily * 365
        biogas_per_capita = biogas_daily / population if population > 0 else 0

        # Display main metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Daily Biogas Potential", f"{biogas_daily:,.0f} m³",
                     help="Estimated daily biogas production potential")

        with col2:
            st.metric("Daily Energy Potential", f"{energy_daily:,.0f} kWh",
                     help="Estimated daily energy generation potential")

        with col3:
            st.metric("Population", f"{population:,}",
                     help="Municipality population")

        with col4:
            st.metric("Biogas per Capita", f"{biogas_per_capita:.2f} m³",
                     help="Daily biogas potential per resident")

        # Additional metrics
        col5, col6 = st.columns(2)

        with col5:
            st.metric("Annual Biogas", f"{biogas_annual:,.0f} m³",
                     help="Estimated annual biogas production")

        with col6:
            st.metric("Annual Energy", f"{energy_annual/1000:,.0f} MWh",
                     help="Estimated annual energy generation in MWh")

        return {
            'biogas_daily': biogas_daily,
            'energy_daily': energy_daily,
            'population': population,
            'biogas_per_capita': biogas_per_capita,
            'biogas_annual': biogas_annual,
            'energy_annual': energy_annual
        }

    def _render_biogas_analysis(self, municipality_data: pd.Series) -> Dict[str, Any]:
        """Render detailed biogas potential analysis"""
        st.markdown("#### ⚡ Biogas Potential Analysis")

        # Create biogas breakdown visualization
        biogas_breakdown = self._calculate_biogas_breakdown(municipality_data)

        # Create visualizations
        col1, col2 = st.columns([1, 1])

        with col1:
            # Pie chart for waste composition
            fig_pie = self._create_waste_composition_chart(biogas_breakdown)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart for biogas sources
            fig_bar = self._create_biogas_sources_chart(biogas_breakdown)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Detailed breakdown table
        st.markdown("##### 📋 Detailed Breakdown")
        breakdown_df = pd.DataFrame(biogas_breakdown['sources']).T
        breakdown_df.columns = ['Waste Type', 'Volume (m³/day)', 'Percentage (%)']
        st.dataframe(breakdown_df, use_container_width=True)

        return biogas_breakdown

    def _render_comparative_analysis(self,
                                   municipality_data: pd.Series,
                                   comparison_municipalities: Optional[List[str]]) -> Dict[str, Any]:
        """Render comparative analysis with state averages and similar municipalities"""
        st.markdown("#### 🔍 Comparative Analysis")

        try:
            # Get state averages
            municipalities_df = database_loader.load_municipalities_data()
            if municipalities_df is None:
                st.warning("⚠️ No comparison data available")
                return {}

            state_stats = self._calculate_state_statistics(municipalities_df)
            municipality_stats = self._extract_municipality_statistics(municipality_data)

            # Create comparison chart
            fig_comparison = self._create_comparison_chart(municipality_stats, state_stats)
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Similar municipalities analysis
            similar_municipalities = self._find_similar_municipalities(
                municipality_data, municipalities_df, limit=5
            )

            if len(similar_municipalities) > 0:
                st.markdown("##### 🏘️ Similar Municipalities")
                similar_df = similar_municipalities[['nome_municipio', 'biogas_potential_m3_day',
                                                   'energy_potential_kwh_day', 'population']].copy()
                similar_df.columns = ['Municipality', 'Biogas (m³/day)', 'Energy (kWh/day)', 'Population']
                st.dataframe(similar_df, use_container_width=True)

            return {
                'state_stats': state_stats,
                'municipality_stats': municipality_stats,
                'similar_municipalities': similar_municipalities
            }

        except Exception as e:
            self.logger.error(f"Error in comparative analysis: {e}")
            st.error("⚠️ Comparative analysis unavailable")
            return {}

    def _render_environmental_impact(self, municipality_data: pd.Series) -> Dict[str, Any]:
        """Render environmental impact analysis"""
        st.markdown("#### 🌱 Environmental Impact")

        # Calculate environmental benefits
        biogas_daily = municipality_data.get('biogas_potential_m3_day', 0)
        energy_daily = municipality_data.get('energy_potential_kwh_day', 0)

        # CO2 reduction calculations (using biogas_calculator factors)
        factors = biogas_calculator.get_conversion_factors_info()
        co2_reduction_daily = energy_daily * factors.get('co2_avoided_per_kwh', 0.45)  # kg CO2/day
        co2_reduction_annual = co2_reduction_daily * 365 / 1000  # tons CO2/year

        # Waste diversion calculations
        population = municipality_data.get('population', 0)
        waste_diverted_daily = biogas_daily * 2  # Approximate kg waste per m³ biogas
        waste_diverted_annual = waste_diverted_daily * 365 / 1000  # tons/year

        # Display environmental metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("CO₂ Reduction", f"{co2_reduction_annual:,.0f} tons/year",
                     help="Annual CO₂ emissions avoided through biogas use")

        with col2:
            st.metric("Waste Diverted", f"{waste_diverted_annual:,.0f} tons/year",
                     help="Annual organic waste diverted from landfills")

        with col3:
            equivalent_cars = co2_reduction_annual / 4.6  # Average car emissions per year
            st.metric("Equivalent Cars", f"{equivalent_cars:,.0f}",
                     help="Number of cars off the road for equivalent CO₂ reduction")

        # Environmental impact visualization
        impact_data = {
            'CO₂ Reduction (tons/year)': co2_reduction_annual,
            'Waste Diverted (tons/year)': waste_diverted_annual,
            'Energy Generated (MWh/year)': energy_daily * 365 / 1000
        }

        fig_impact = go.Figure(data=[
            go.Bar(x=list(impact_data.keys()), y=list(impact_data.values()),
                   marker_color=['green', 'blue', 'orange'])
        ])
        fig_impact.update_layout(
            title="Annual Environmental Benefits",
            yaxis_title="Impact Volume",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_impact, use_container_width=True)

        return {
            'co2_reduction_annual': co2_reduction_annual,
            'waste_diverted_annual': waste_diverted_annual,
            'equivalent_cars': equivalent_cars,
            'impact_data': impact_data
        }

    def _calculate_biogas_breakdown(self, municipality_data: pd.Series) -> Dict[str, Any]:
        """Calculate detailed biogas potential breakdown by source"""
        total_biogas = municipality_data.get('biogas_potential_m3_day', 0)

        # Estimated breakdown percentages (based on typical municipal waste composition)
        breakdown_percentages = {
            'Food Waste': 45,
            'Garden Waste': 25,
            'Paper Waste': 15,
            'Other Organic': 15
        }

        sources = {}
        for source, percentage in breakdown_percentages.items():
            volume = total_biogas * (percentage / 100)
            sources[source] = {
                'volume': volume,
                'percentage': percentage
            }

        return {
            'total_biogas': total_biogas,
            'sources': sources,
            'breakdown_percentages': breakdown_percentages
        }

    def _create_waste_composition_chart(self, biogas_breakdown: Dict[str, Any]) -> go.Figure:
        """Create pie chart for waste composition"""
        sources = biogas_breakdown['sources']
        labels = list(sources.keys())
        values = [sources[label]['percentage'] for label in labels]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=['#FF6B35', '#F7931E', '#FFD23F', '#06D6A0']
        )])

        fig.update_layout(
            title="Waste Source Composition",
            showlegend=True,
            height=400
        )

        return fig

    def _create_biogas_sources_chart(self, biogas_breakdown: Dict[str, Any]) -> go.Figure:
        """Create bar chart for biogas sources"""
        sources = biogas_breakdown['sources']
        labels = list(sources.keys())
        values = [sources[label]['volume'] for label in labels]

        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=['#FF6B35', '#F7931E', '#FFD23F', '#06D6A0']
        )])

        fig.update_layout(
            title="Biogas Potential by Source",
            xaxis_title="Waste Source",
            yaxis_title="Biogas Potential (m³/day)",
            height=400
        )

        return fig

    def _calculate_state_statistics(self, municipalities_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate state-wide statistics for comparison"""
        return {
            'avg_biogas': municipalities_df['biogas_potential_m3_day'].mean(),
            'avg_energy': municipalities_df['energy_potential_kwh_day'].mean(),
            'avg_population': municipalities_df['population'].mean() if 'population' in municipalities_df.columns else 0,
            'median_biogas': municipalities_df['biogas_potential_m3_day'].median(),
            'total_municipalities': len(municipalities_df)
        }

    def _extract_municipality_statistics(self, municipality_data: pd.Series) -> Dict[str, float]:
        """Extract municipality statistics for comparison"""
        return {
            'biogas': municipality_data.get('biogas_potential_m3_day', 0),
            'energy': municipality_data.get('energy_potential_kwh_day', 0),
            'population': municipality_data.get('population', 0)
        }

    def _create_comparison_chart(self, municipality_stats: Dict[str, float],
                               state_stats: Dict[str, float]) -> go.Figure:
        """Create comparison chart with state averages"""
        categories = ['Biogas Potential', 'Energy Potential', 'Population']
        municipality_values = [municipality_stats['biogas'],
                             municipality_stats['energy'],
                             municipality_stats['population']]
        state_values = [state_stats['avg_biogas'],
                       state_stats['avg_energy'],
                       state_stats['avg_population']]

        fig = go.Figure(data=[
            go.Bar(name='This Municipality', x=categories, y=municipality_values, marker_color='#FF6B35'),
            go.Bar(name='State Average', x=categories, y=state_values, marker_color='#06D6A0')
        ])

        fig.update_layout(
            title="Municipality vs State Average",
            barmode='group',
            yaxis_title="Values",
            height=400
        )

        return fig

    def _find_similar_municipalities(self,
                                   municipality_data: pd.Series,
                                   municipalities_df: pd.DataFrame,
                                   limit: int = 5) -> pd.DataFrame:
        """Find municipalities with similar characteristics"""
        target_population = municipality_data.get('population', 0)
        target_biogas = municipality_data.get('biogas_potential_m3_day', 0)

        if target_population == 0 and target_biogas == 0:
            return pd.DataFrame()

        # Calculate similarity scores based on population and biogas potential
        municipalities_df['similarity_score'] = (
            abs(municipalities_df['population'] - target_population) / max(target_population, 1) +
            abs(municipalities_df['biogas_potential_m3_day'] - target_biogas) / max(target_biogas, 1)
        )

        # Filter out the current municipality and get most similar ones
        similar = municipalities_df[
            municipalities_df['nome_municipio'] != municipality_data.get('nome_municipio')
        ].nsmallest(limit, 'similarity_score')

        return similar