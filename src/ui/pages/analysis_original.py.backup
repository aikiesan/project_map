"""
CP2B Maps V2 - Analysis Page
Advanced biogas potential analysis with scenario planning and economic feasibility
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple
import datetime

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class AnalysisPage:
    """
    Advanced analysis page for biogas potential with scenario planning
    Features: Economic analysis, environmental impact, feasibility studies, projections
    """

    def __init__(self):
        """Initialize Analysis Page"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing AnalysisPage component")

        # Economic and technical parameters
        self.economic_factors = {
            'biogas_price_brl_m3': 0.85,  # BRL per m³ biogas
            'electricity_price_brl_kwh': 0.55,  # BRL per kWh
            'investment_cost_brl_m3_capacity': 1200,  # BRL per m³ daily capacity
            'operational_cost_percentage': 0.05,  # 5% of investment per year
            'carbon_credit_brl_ton': 45,  # BRL per ton CO2
            'plant_lifetime_years': 20,
            'discount_rate': 0.08  # 8% annual discount rate
        }

    def render(self) -> Dict[str, Any]:
        """
        Render comprehensive analysis page with scenario planning

        Returns:
            Dictionary with analysis results and scenario data
        """
        try:
            st.markdown("# 📈 Advanced Biogas Analysis & Planning")
            st.markdown("### Scenario planning, economic feasibility, and environmental impact analysis")

            # Load data
            analysis_data = self._load_analysis_data()
            if analysis_data is None or len(analysis_data) == 0:
                st.error("⚠️ No data available for analysis")
                return {}

            # Scenario configuration
            scenario_config = self._render_scenario_configuration()

            # Economic feasibility analysis
            economic_results = self._render_economic_analysis(analysis_data, scenario_config)

            # Environmental impact analysis
            environmental_results = self._render_environmental_analysis(analysis_data, scenario_config)

            # Technical feasibility analysis
            technical_results = self._render_technical_analysis(analysis_data, scenario_config)

            # Regional development potential
            regional_results = self._render_regional_development_analysis(analysis_data, scenario_config)

            # Investment prioritization
            prioritization_results = self._render_investment_prioritization(analysis_data, scenario_config)

            return {
                'analysis_data': analysis_data,
                'scenario_config': scenario_config,
                'economic_results': economic_results,
                'environmental_results': environmental_results,
                'technical_results': technical_results,
                'regional_results': regional_results,
                'prioritization_results': prioritization_results
            }

        except Exception as e:
            self.logger.error(f"Error rendering analysis page: {e}", exc_info=True)
            st.error("⚠️ Failed to render analysis page. Check logs for details.")
            return {}

    def _load_analysis_data(self) -> Optional[pd.DataFrame]:
        """Load and prepare data for advanced analysis"""
        try:
            data = database_loader.load_municipalities_data()
            if data is None:
                return None

            # Add calculated fields for analysis
            data['biogas_annual_m3'] = data['biogas_potential_m3_day'] * 365
            data['energy_annual_kwh'] = data['energy_potential_kwh_day'] * 365

            # Economic calculations
            data['annual_revenue_biogas'] = data['biogas_annual_m3'] * self.economic_factors['biogas_price_brl_m3']
            data['annual_revenue_electricity'] = data['energy_annual_kwh'] * self.economic_factors['electricity_price_brl_kwh']
            data['investment_required'] = data['biogas_potential_m3_day'] * self.economic_factors['investment_cost_brl_m3_capacity']

            # Environmental calculations
            factors = biogas_calculator.get_conversion_factors_info()
            data['co2_reduction_annual_tons'] = data['energy_annual_kwh'] * factors.get('co2_avoided_per_kwh', 0.45) / 1000
            data['carbon_credit_revenue'] = data['co2_reduction_annual_tons'] * self.economic_factors['carbon_credit_brl_ton']

            # Total revenue potential
            data['total_annual_revenue'] = (data['annual_revenue_biogas'] +
                                         data['annual_revenue_electricity'] +
                                         data['carbon_credit_revenue'])

            # Payback calculations
            data['operational_cost_annual'] = data['investment_required'] * self.economic_factors['operational_cost_percentage']
            data['net_annual_profit'] = data['total_annual_revenue'] - data['operational_cost_annual']
            data['simple_payback_years'] = np.where(
                data['net_annual_profit'] > 0,
                data['investment_required'] / data['net_annual_profit'],
                np.inf
            )

            # Feasibility categories
            data['feasibility_category'] = pd.cut(
                data['simple_payback_years'],
                bins=[0, 5, 10, 15, np.inf],
                labels=['Highly Feasible (<5y)', 'Feasible (5-10y)', 'Marginal (10-15y)', 'Not Feasible (>15y)']
            )

            self.logger.info(f"Prepared analysis data for {len(data)} municipalities")
            return data

        except Exception as e:
            self.logger.error(f"Error loading analysis data: {e}")
            return None

    def _render_scenario_configuration(self) -> Dict[str, Any]:
        """Render scenario configuration interface"""
        st.markdown("#### ⚙️ Scenario Configuration")

        with st.expander("🔧 Economic Parameters", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                biogas_price = st.number_input(
                    "Biogas Price (BRL/m³)",
                    value=self.economic_factors['biogas_price_brl_m3'],
                    min_value=0.1, max_value=2.0, step=0.05,
                    help="Market price for biogas"
                )

                electricity_price = st.number_input(
                    "Electricity Price (BRL/kWh)",
                    value=self.economic_factors['electricity_price_brl_kwh'],
                    min_value=0.1, max_value=1.0, step=0.05,
                    help="Electricity tariff price"
                )

            with col2:
                investment_cost = st.number_input(
                    "Investment Cost (BRL/m³ capacity)",
                    value=self.economic_factors['investment_cost_brl_m3_capacity'],
                    min_value=500, max_value=3000, step=50,
                    help="Capital cost per m³ daily capacity"
                )

                operational_cost = st.slider(
                    "Operational Cost (%)",
                    min_value=2, max_value=10, value=5,
                    help="Annual operational cost as % of investment"
                ) / 100

            with col3:
                carbon_credit = st.number_input(
                    "Carbon Credit (BRL/ton CO₂)",
                    value=self.economic_factors['carbon_credit_brl_ton'],
                    min_value=10, max_value=100, step=5,
                    help="Carbon credit price per ton CO₂"
                )

                discount_rate = st.slider(
                    "Discount Rate (%)",
                    min_value=5, max_value=15, value=8,
                    help="Annual discount rate for NPV calculations"
                ) / 100

        # Scenario selection
        st.markdown("##### 📊 Analysis Scenarios")
        scenario_type = st.selectbox(
            "Select analysis scenario:",
            options=['current_market', 'optimistic', 'conservative', 'carbon_focused', 'custom'],
            format_func=lambda x: {
                'current_market': '📈 Current Market Conditions',
                'optimistic': '🚀 Optimistic Growth Scenario',
                'conservative': '🛡️ Conservative Scenario',
                'carbon_focused': '🌱 Carbon Credit Focused',
                'custom': '⚙️ Custom Parameters'
            }[x],
            help="Choose analysis scenario type"
        )

        # Apply scenario adjustments
        scenario_factors = self._get_scenario_factors(scenario_type)

        return {
            'biogas_price': biogas_price * scenario_factors.get('biogas_multiplier', 1.0),
            'electricity_price': electricity_price * scenario_factors.get('electricity_multiplier', 1.0),
            'investment_cost': investment_cost * scenario_factors.get('investment_multiplier', 1.0),
            'operational_cost_percentage': operational_cost * scenario_factors.get('operational_multiplier', 1.0),
            'carbon_credit': carbon_credit * scenario_factors.get('carbon_multiplier', 1.0),
            'discount_rate': discount_rate,
            'scenario_type': scenario_type,
            'scenario_factors': scenario_factors
        }

    def _render_economic_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render comprehensive economic analysis"""
        st.markdown("#### 💰 Economic Feasibility Analysis")

        # Recalculate with scenario parameters
        scenario_data = self._apply_scenario_parameters(data, scenario_config)

        # Economic overview metrics
        self._render_economic_overview(scenario_data, scenario_config)

        # Investment feasibility charts
        feasibility_charts = self._render_feasibility_charts(scenario_data)

        # ROI and payback analysis
        roi_analysis = self._render_roi_analysis(scenario_data, scenario_config)

        # Risk analysis
        risk_analysis = self._render_risk_analysis(scenario_data, scenario_config)

        return {
            'scenario_data': scenario_data,
            'feasibility_charts': feasibility_charts,
            'roi_analysis': roi_analysis,
            'risk_analysis': risk_analysis
        }

    def _render_environmental_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render environmental impact analysis"""
        st.markdown("#### 🌱 Environmental Impact Analysis")

        # Apply scenario parameters
        scenario_data = self._apply_scenario_parameters(data, scenario_config)

        # Environmental metrics
        col1, col2, col3, col4 = st.columns(4)

        total_co2_reduction = scenario_data['co2_reduction_annual_tons'].sum()
        total_waste_diverted = scenario_data['biogas_annual_m3'].sum() * 2 / 1000  # Estimate tons waste
        total_energy_clean = scenario_data['energy_annual_kwh'].sum() / 1000000  # Convert to GWh

        with col1:
            st.metric("Total CO₂ Reduction", f"{total_co2_reduction:,.0f} tons/year")

        with col2:
            st.metric("Waste Diverted", f"{total_waste_diverted:,.0f} tons/year")

        with col3:
            st.metric("Clean Energy", f"{total_energy_clean:.1f} GWh/year")

        with col4:
            equivalent_cars = total_co2_reduction / 4.6
            st.metric("Equivalent Cars", f"{equivalent_cars:,.0f}")

        # Environmental impact charts
        impact_charts = self._create_environmental_impact_charts(scenario_data)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(impact_charts['co2_distribution'], use_container_width=True)
        with col2:
            st.plotly_chart(impact_charts['impact_projection'], use_container_width=True)

        return {
            'total_co2_reduction': total_co2_reduction,
            'total_waste_diverted': total_waste_diverted,
            'total_energy_clean': total_energy_clean,
            'equivalent_cars': equivalent_cars,
            'impact_charts': impact_charts
        }

    def _render_technical_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render technical feasibility analysis"""
        st.markdown("#### 🔧 Technical Feasibility Analysis")

        scenario_data = self._apply_scenario_parameters(data, scenario_config)

        # Technical categories
        tech_categories = {
            'Small Scale (<500 m³/day)': len(scenario_data[scenario_data['biogas_potential_m3_day'] < 500]),
            'Medium Scale (500-2000 m³/day)': len(scenario_data[
                (scenario_data['biogas_potential_m3_day'] >= 500) &
                (scenario_data['biogas_potential_m3_day'] < 2000)
            ]),
            'Large Scale (2000-5000 m³/day)': len(scenario_data[
                (scenario_data['biogas_potential_m3_day'] >= 2000) &
                (scenario_data['biogas_potential_m3_day'] < 5000)
            ]),
            'Industrial Scale (>5000 m³/day)': len(scenario_data[scenario_data['biogas_potential_m3_day'] >= 5000])
        }

        # Technical distribution chart
        fig_tech = px.pie(
            values=list(tech_categories.values()),
            names=list(tech_categories.keys()),
            title='Technical Scale Distribution'
        )
        st.plotly_chart(fig_tech, use_container_width=True)

        # Implementation timeline
        timeline_chart = self._create_implementation_timeline(scenario_data)
        st.plotly_chart(timeline_chart, use_container_width=True)

        return {
            'tech_categories': tech_categories,
            'timeline_chart': timeline_chart
        }

    def _render_regional_development_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render regional development potential analysis"""
        st.markdown("#### 🗺️ Regional Development Potential")

        scenario_data = self._apply_scenario_parameters(data, scenario_config)

        # Simulated regional analysis (since we don't have actual regions)
        regional_analysis = self._simulate_regional_development(scenario_data)

        # Regional potential chart
        regional_chart = self._create_regional_development_chart(regional_analysis)
        st.plotly_chart(regional_chart, use_container_width=True)

        # Development recommendations
        self._render_development_recommendations(regional_analysis)

        return {
            'regional_analysis': regional_analysis,
            'regional_chart': regional_chart
        }

    def _render_investment_prioritization(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render investment prioritization analysis"""
        st.markdown("#### 🎯 Investment Prioritization")

        scenario_data = self._apply_scenario_parameters(data, scenario_config)

        # Priority ranking based on multiple criteria
        priority_weights = st.slider(
            "Adjust priority weights (Economic vs Environmental):",
            min_value=0.0, max_value=1.0, value=0.6, step=0.1,
            help="0 = Pure environmental focus, 1 = Pure economic focus"
        )

        # Calculate priority scores
        scenario_data = self._calculate_priority_scores(scenario_data, priority_weights)

        # Top investment opportunities
        top_opportunities = scenario_data.nlargest(20, 'priority_score')

        # Priority visualization
        priority_chart = self._create_priority_chart(top_opportunities)
        st.plotly_chart(priority_chart, use_container_width=True)

        # Investment recommendations table
        self._render_investment_recommendations_table(top_opportunities)

        return {
            'priority_weights': priority_weights,
            'top_opportunities': top_opportunities,
            'priority_chart': priority_chart
        }

    def _get_scenario_factors(self, scenario_type: str) -> Dict[str, float]:
        """Get multiplier factors for different scenarios"""
        factors = {
            'current_market': {
                'biogas_multiplier': 1.0,
                'electricity_multiplier': 1.0,
                'investment_multiplier': 1.0,
                'operational_multiplier': 1.0,
                'carbon_multiplier': 1.0
            },
            'optimistic': {
                'biogas_multiplier': 1.3,
                'electricity_multiplier': 1.2,
                'investment_multiplier': 0.8,
                'operational_multiplier': 0.9,
                'carbon_multiplier': 1.5
            },
            'conservative': {
                'biogas_multiplier': 0.8,
                'electricity_multiplier': 0.9,
                'investment_multiplier': 1.2,
                'operational_multiplier': 1.1,
                'carbon_multiplier': 0.7
            },
            'carbon_focused': {
                'biogas_multiplier': 1.0,
                'electricity_multiplier': 1.0,
                'investment_multiplier': 1.0,
                'operational_multiplier': 1.0,
                'carbon_multiplier': 2.0
            },
            'custom': {
                'biogas_multiplier': 1.0,
                'electricity_multiplier': 1.0,
                'investment_multiplier': 1.0,
                'operational_multiplier': 1.0,
                'carbon_multiplier': 1.0
            }
        }

        return factors.get(scenario_type, factors['current_market'])

    def _apply_scenario_parameters(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
        """Apply scenario parameters to data"""
        scenario_data = data.copy()

        # Recalculate with scenario parameters
        scenario_data['annual_revenue_biogas'] = scenario_data['biogas_annual_m3'] * scenario_config['biogas_price']
        scenario_data['annual_revenue_electricity'] = scenario_data['energy_annual_kwh'] * scenario_config['electricity_price']
        scenario_data['investment_required'] = scenario_data['biogas_potential_m3_day'] * scenario_config['investment_cost']
        scenario_data['carbon_credit_revenue'] = scenario_data['co2_reduction_annual_tons'] * scenario_config['carbon_credit']

        scenario_data['total_annual_revenue'] = (scenario_data['annual_revenue_biogas'] +
                                               scenario_data['annual_revenue_electricity'] +
                                               scenario_data['carbon_credit_revenue'])

        scenario_data['operational_cost_annual'] = scenario_data['investment_required'] * scenario_config['operational_cost_percentage']
        scenario_data['net_annual_profit'] = scenario_data['total_annual_revenue'] - scenario_data['operational_cost_annual']

        scenario_data['simple_payback_years'] = np.where(
            scenario_data['net_annual_profit'] > 0,
            scenario_data['investment_required'] / scenario_data['net_annual_profit'],
            np.inf
        )

        # NPV calculation
        scenario_data['npv'] = self._calculate_npv(
            scenario_data['net_annual_profit'],
            scenario_data['investment_required'],
            scenario_config['discount_rate'],
            self.economic_factors['plant_lifetime_years']
        )

        return scenario_data

    def _render_economic_overview(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> None:
        """Render economic overview metrics"""
        st.markdown("##### 💵 Economic Overview")

        col1, col2, col3, col4 = st.columns(4)

        total_investment = data['investment_required'].sum() / 1000000  # Convert to millions
        total_revenue = data['total_annual_revenue'].sum() / 1000000
        avg_payback = data[data['simple_payback_years'] != np.inf]['simple_payback_years'].mean()
        feasible_projects = len(data[data['simple_payback_years'] <= 10])

        with col1:
            st.metric("Total Investment Required", f"R$ {total_investment:.1f}M")

        with col2:
            st.metric("Total Annual Revenue", f"R$ {total_revenue:.1f}M")

        with col3:
            st.metric("Average Payback", f"{avg_payback:.1f} years")

        with col4:
            st.metric("Feasible Projects (<10y)", f"{feasible_projects:,}")

    def _render_feasibility_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create feasibility analysis charts"""
        col1, col2 = st.columns(2)

        with col1:
            # Feasibility distribution
            feasibility_counts = data['feasibility_category'].value_counts()
            fig_feasibility = px.pie(
                values=feasibility_counts.values,
                names=feasibility_counts.index,
                title='Project Feasibility Distribution'
            )
            st.plotly_chart(fig_feasibility, use_container_width=True)

        with col2:
            # Payback vs Investment scatter
            fig_scatter = px.scatter(
                data[data['simple_payback_years'] < 20],  # Filter extreme outliers
                x='investment_required',
                y='simple_payback_years',
                size='biogas_potential_m3_day',
                color='feasibility_category',
                title='Investment vs Payback Period',
                hover_data=['nome_municipio']
            )
            fig_scatter.update_layout(
                xaxis_title='Investment Required (BRL)',
                yaxis_title='Payback Period (years)'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        return {
            'feasibility_distribution': fig_feasibility,
            'payback_scatter': fig_scatter
        }

    def _render_roi_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render ROI and profitability analysis"""
        st.markdown("##### 📊 Return on Investment Analysis")

        # ROI calculations
        data['roi_percentage'] = np.where(
            data['investment_required'] > 0,
            (data['net_annual_profit'] / data['investment_required']) * 100,
            0
        )

        # ROI distribution
        fig_roi = px.histogram(
            data[data['roi_percentage'] > -50],  # Filter extreme negatives
            x='roi_percentage',
            nbins=50,
            title='ROI Distribution (%)',
            marginal='box'
        )
        fig_roi.update_layout(
            xaxis_title='ROI (%)',
            yaxis_title='Number of Projects'
        )
        st.plotly_chart(fig_roi, use_container_width=True)

        return {'roi_distribution': fig_roi}

    def _render_risk_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render risk analysis"""
        st.markdown("##### ⚠️ Risk Analysis")

        # Risk categories based on payback and investment size
        data['risk_category'] = pd.cut(
            data['simple_payback_years'],
            bins=[0, 3, 7, 12, np.inf],
            labels=['Low Risk', 'Medium Risk', 'High Risk', 'Very High Risk']
        )

        # Risk distribution
        risk_counts = data['risk_category'].value_counts()
        fig_risk = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            title='Investment Risk Distribution',
            color=risk_counts.values,
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        return {'risk_distribution': fig_risk}

    def _create_environmental_impact_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create environmental impact charts"""
        # CO2 reduction by municipality size
        fig_co2 = px.scatter(
            data,
            x='population',
            y='co2_reduction_annual_tons',
            size='biogas_potential_m3_day',
            title='CO₂ Reduction vs Municipality Size',
            hover_data=['nome_municipio']
        )
        fig_co2.update_layout(
            xaxis_title='Population',
            yaxis_title='CO₂ Reduction (tons/year)'
        )

        # Environmental impact projection over time
        years = list(range(2024, 2035))
        annual_co2 = data['co2_reduction_annual_tons'].sum()
        cumulative_co2 = [annual_co2 * (i - 2023) for i in years]

        fig_projection = go.Figure()
        fig_projection.add_trace(go.Scatter(
            x=years,
            y=cumulative_co2,
            mode='lines+markers',
            name='Cumulative CO₂ Reduction',
            line=dict(color='green')
        ))
        fig_projection.update_layout(
            title='Projected Cumulative Environmental Impact',
            xaxis_title='Year',
            yaxis_title='Cumulative CO₂ Reduction (tons)'
        )

        return {
            'co2_distribution': fig_co2,
            'impact_projection': fig_projection
        }

    def _create_implementation_timeline(self, data: pd.DataFrame) -> go.Figure:
        """Create implementation timeline chart"""
        # Simulate implementation phases based on feasibility
        phases = {
            'Phase 1 (Years 1-2)': len(data[data['simple_payback_years'] <= 5]),
            'Phase 2 (Years 3-5)': len(data[(data['simple_payback_years'] > 5) & (data['simple_payback_years'] <= 10)]),
            'Phase 3 (Years 6-10)': len(data[(data['simple_payback_years'] > 10) & (data['simple_payback_years'] <= 15)]),
            'Future Consideration': len(data[data['simple_payback_years'] > 15])
        }

        fig = px.bar(
            x=list(phases.keys()),
            y=list(phases.values()),
            title='Recommended Implementation Timeline',
            color=list(phases.values()),
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title='Implementation Phase',
            yaxis_title='Number of Projects'
        )

        return fig

    def _simulate_regional_development(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simulate regional development analysis"""
        # Create simulated regions
        np.random.seed(42)
        regions = ['North', 'South', 'East', 'West', 'Central']

        regional_data = []
        for region in regions:
            region_size = len(data) // len(regions)
            region_sample = data.sample(n=min(region_size, len(data)))

            regional_data.append({
                'region': region,
                'total_investment': region_sample['investment_required'].sum(),
                'total_revenue': region_sample['total_annual_revenue'].sum(),
                'avg_payback': region_sample[region_sample['simple_payback_years'] != np.inf]['simple_payback_years'].mean(),
                'feasible_projects': len(region_sample[region_sample['simple_payback_years'] <= 10]),
                'total_co2_reduction': region_sample['co2_reduction_annual_tons'].sum(),
                'development_priority': np.random.uniform(0.3, 1.0)
            })

        return pd.DataFrame(regional_data)

    def _create_regional_development_chart(self, regional_data: pd.DataFrame) -> go.Figure:
        """Create regional development potential chart"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Investment Required', 'Expected Revenue', 'Feasible Projects', 'CO₂ Impact'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        regions = regional_data['region'].tolist()

        # Investment
        fig.add_trace(
            go.Bar(x=regions, y=regional_data['total_investment'], name='Investment'),
            row=1, col=1
        )

        # Revenue
        fig.add_trace(
            go.Bar(x=regions, y=regional_data['total_revenue'], name='Revenue'),
            row=1, col=2
        )

        # Projects
        fig.add_trace(
            go.Bar(x=regions, y=regional_data['feasible_projects'], name='Projects'),
            row=2, col=1
        )

        # CO2
        fig.add_trace(
            go.Bar(x=regions, y=regional_data['total_co2_reduction'], name='CO₂'),
            row=2, col=2
        )

        fig.update_layout(
            title='Regional Development Potential Analysis',
            height=600,
            showlegend=False
        )

        return fig

    def _render_development_recommendations(self, regional_data: pd.DataFrame) -> None:
        """Render development recommendations"""
        st.markdown("##### 🎯 Regional Development Recommendations")

        # Sort regions by development priority
        top_regions = regional_data.nlargest(3, 'development_priority')

        for _, region in top_regions.iterrows():
            with st.expander(f"🏆 {region['region']} Region - High Priority"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Investment Required", f"R$ {region['total_investment']/1000000:.1f}M")
                    st.metric("Feasible Projects", f"{region['feasible_projects']:,.0f}")

                with col2:
                    st.metric("Expected Revenue", f"R$ {region['total_revenue']/1000000:.1f}M/year")
                    st.metric("CO₂ Reduction", f"{region['total_co2_reduction']:,.0f} tons/year")

    def _calculate_priority_scores(self, data: pd.DataFrame, economic_weight: float) -> pd.DataFrame:
        """Calculate investment priority scores"""
        env_weight = 1.0 - economic_weight

        # Normalize metrics to 0-100 scale
        data['economic_score'] = ((1 / (data['simple_payback_years'] + 1)) * 100).fillna(0)
        data['environmental_score'] = ((data['co2_reduction_annual_tons'] / data['co2_reduction_annual_tons'].max()) * 100).fillna(0)

        # Combined priority score
        data['priority_score'] = (economic_weight * data['economic_score'] +
                                env_weight * data['environmental_score'])

        return data

    def _create_priority_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create investment priority chart"""
        fig = px.scatter(
            data,
            x='economic_score',
            y='environmental_score',
            size='priority_score',
            color='priority_score',
            hover_data=['nome_municipio', 'simple_payback_years', 'co2_reduction_annual_tons'],
            title='Investment Priority Matrix',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title='Economic Score',
            yaxis_title='Environmental Score',
            height=500
        )

        return fig

    def _render_investment_recommendations_table(self, data: pd.DataFrame) -> None:
        """Render investment recommendations table"""
        st.markdown("##### 🏆 Top Investment Recommendations")

        display_data = data[['nome_municipio', 'priority_score', 'simple_payback_years',
                           'investment_required', 'total_annual_revenue', 'co2_reduction_annual_tons']].copy()

        display_data.columns = ['Municipality', 'Priority Score', 'Payback (years)',
                              'Investment (BRL)', 'Revenue (BRL/year)', 'CO₂ Reduction (tons/year)']

        # Format numbers
        display_data['Investment (BRL)'] = display_data['Investment (BRL)'].apply(lambda x: f"R$ {x:,.0f}")
        display_data['Revenue (BRL/year)'] = display_data['Revenue (BRL/year)'].apply(lambda x: f"R$ {x:,.0f}")
        display_data['Priority Score'] = display_data['Priority Score'].round(1)
        display_data['Payback (years)'] = display_data['Payback (years)'].round(1)
        display_data['CO₂ Reduction (tons/year)'] = display_data['CO₂ Reduction (tons/year)'].round(0)

        st.dataframe(display_data.head(15), use_container_width=True, hide_index=True)

    def _calculate_npv(self, annual_profit: pd.Series, investment: pd.Series,
                      discount_rate: float, years: int) -> pd.Series:
        """Calculate Net Present Value"""
        npv = -investment  # Initial investment (negative cash flow)

        for year in range(1, years + 1):
            npv += annual_profit / ((1 + discount_rate) ** year)

        return npv