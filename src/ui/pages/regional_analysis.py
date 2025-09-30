"""
CP2B Maps V2 - Regional Analysis Module
Regional development analysis, investment prioritization, and policy recommendations
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

# Import V1 design system
from src.ui.components.design_system import (
    render_section_header,
    render_info_banner
)

logger = get_logger(__name__)


class RegionalAnalyzer:
    """
    Regional development analysis engine for biogas projects
    Features: Regional planning, investment prioritization, policy recommendations
    """

    def __init__(self):
        """Initialize Regional Analyzer"""
        self.logger = get_logger(self.__class__.__name__)

        # Regional development factors
        self.regional_factors = {
            'economic_multiplier': 1.5,  # Economic impact multiplier
            'job_creation_per_mw': 12,  # Jobs created per MW installed
            'local_content_percentage': 0.65,  # Local content in projects
            'supply_chain_development': 0.25,  # Supply chain development factor
            'technology_transfer_factor': 0.15,  # Technology transfer benefits
            'rural_development_impact': 1.8  # Rural development multiplier
        }

        # Investment criteria weights
        self.investment_weights = {
            'economic_potential': 0.35,
            'technical_feasibility': 0.25,
            'environmental_impact': 0.20,
            'social_development': 0.15,
            'policy_alignment': 0.05
        }

    def render_regional_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render comprehensive regional development analysis

        Args:
            data: Municipality data with biogas calculations
            scenario_config: Scenario parameters

        Returns:
            Dictionary with regional analysis results
        """
        try:
            render_section_header(
                "🗺️ Análise de Desenvolvimento Regional",
                description="Priorização de investimentos, recomendações de políticas e planejamento regional"
            )

            # Calculate regional metrics
            regional_data = self._calculate_regional_metrics(data, scenario_config)

            # Regional overview
            self._render_regional_overview(regional_data)

            # Investment prioritization
            prioritization_results = self._render_investment_prioritization(regional_data)

            # Regional development simulation
            development_results = self._simulate_regional_development(regional_data)

            # Policy recommendations
            policy_results = self._render_policy_recommendations(regional_data)

            # Regional clustering analysis
            clustering_results = self._render_regional_clustering(regional_data)

            return {
                'regional_data': regional_data,
                'prioritization_results': prioritization_results,
                'development_results': development_results,
                'policy_results': policy_results,
                'clustering_results': clustering_results
            }

        except Exception as e:
            self.logger.error(f"Error in regional analysis: {e}")
            st.error("❌ Error performing regional analysis")
            return {}

    def _calculate_regional_metrics(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate regional development metrics"""
        try:
            regional_data = data.copy()

            # Calculate total biogas potential
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]
            regional_data['total_biogas_potential'] = regional_data[biogas_columns].sum(axis=1)

            # Economic development metrics
            regional_data = self._calculate_economic_development_metrics(regional_data)

            # Social development metrics
            regional_data = self._calculate_social_development_metrics(regional_data)

            # Environmental development metrics
            regional_data = self._calculate_environmental_development_metrics(regional_data)

            # Infrastructure development metrics
            regional_data = self._calculate_infrastructure_development_metrics(regional_data)

            # Investment priority score
            regional_data = self._calculate_priority_scores(regional_data)

            return regional_data

        except Exception as e:
            self.logger.error(f"Error calculating regional metrics: {e}")
            return data

    def _calculate_economic_development_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate economic development metrics"""
        try:
            # Electrical capacity (MW)
            data['electrical_capacity_mw'] = (
                data['total_biogas_potential'] * 6.0 * 0.38 / 8760  # kWh to MW conversion
            )

            # Job creation potential
            data['direct_jobs_created'] = (
                data['electrical_capacity_mw'] * self.regional_factors['job_creation_per_mw']
            )

            # Indirect job creation (supply chain, services)
            data['indirect_jobs_created'] = data['direct_jobs_created'] * 2.5

            # Total economic impact (BRL)
            data['total_economic_impact'] = (
                data['total_biogas_potential'] * 0.85 * 365 *  # Annual biogas revenue
                self.regional_factors['economic_multiplier']
            )

            # Local content value
            data['local_content_value'] = (
                data['total_economic_impact'] * self.regional_factors['local_content_percentage']
            )

            # GDP contribution estimate
            data['gdp_contribution'] = data['total_economic_impact'] * 0.3  # 30% of economic impact

            return data

        except Exception as e:
            self.logger.error(f"Error calculating economic development metrics: {e}")
            return data

    def _calculate_social_development_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate social development metrics"""
        try:
            # Rural development impact (based on agricultural biogas sources)
            agricultural_columns = [col for col in data.columns if any(crop in col.lower() for crop in ['cafe', 'cana', 'milho', 'soja', 'citros'])]
            data['agricultural_biogas'] = data[agricultural_columns].sum(axis=1) if agricultural_columns else 0

            data['rural_development_score'] = (
                data['agricultural_biogas'] / data['total_biogas_potential'].replace(0, 1) *
                self.regional_factors['rural_development_impact']
            )

            # Energy security improvement
            data['energy_security_score'] = np.minimum(
                data['electrical_capacity_mw'] / 10,  # Normalize to reasonable scale
                1.0
            )

            # Skill development potential
            data['skill_development_score'] = (
                data['direct_jobs_created'] / 100 *  # Normalize
                self.regional_factors['technology_transfer_factor']
            )

            # Community benefit index
            data['community_benefit_index'] = (
                data['rural_development_score'] * 0.4 +
                data['energy_security_score'] * 0.3 +
                data['skill_development_score'] * 0.3
            )

            return data

        except Exception as e:
            self.logger.error(f"Error calculating social development metrics: {e}")
            return data

    def _calculate_environmental_development_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate environmental development metrics"""
        try:
            # CO2 reduction impact
            data['co2_reduction_tons_year'] = data['total_biogas_potential'] * 2.3 / 1000

            # Waste management improvement
            data['waste_management_score'] = np.minimum(
                data['total_biogas_potential'] / 10000,  # Normalize
                1.0
            )

            # Circular economy contribution
            data['circular_economy_score'] = (
                data['waste_management_score'] * 0.6 +
                (data['co2_reduction_tons_year'] / 1000) * 0.4
            )

            # Environmental resilience index
            data['environmental_resilience'] = np.minimum(
                data['circular_economy_score'] + data['waste_management_score'],
                1.0
            )

            return data

        except Exception as e:
            self.logger.error(f"Error calculating environmental development metrics: {e}")
            return data

    def _calculate_infrastructure_development_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate infrastructure development metrics"""
        try:
            # Infrastructure investment requirement (BRL)
            data['infrastructure_investment'] = data['electrical_capacity_mw'] * 2e6  # 2M BRL per MW

            # Grid modernization benefit
            data['grid_modernization_score'] = np.minimum(
                data['electrical_capacity_mw'] / 5,  # Normalize
                1.0
            )

            # Technology hub potential
            data['technology_hub_potential'] = (
                data['direct_jobs_created'] / 50 *  # Normalize
                self.regional_factors['technology_transfer_factor']
            )

            # Infrastructure development index
            data['infrastructure_development_index'] = (
                data['grid_modernization_score'] * 0.5 +
                data['technology_hub_potential'] * 0.5
            )

            return data

        except Exception as e:
            self.logger.error(f"Error calculating infrastructure development metrics: {e}")
            return data

    def _calculate_priority_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate investment priority scores using multi-criteria analysis"""
        try:
            # Normalize metrics to 0-1 scale for comparison
            metrics_to_normalize = [
                'total_economic_impact', 'electrical_capacity_mw', 'co2_reduction_tons_year',
                'community_benefit_index', 'infrastructure_development_index'
            ]

            normalized_data = data.copy()

            for metric in metrics_to_normalize:
                if metric in data.columns:
                    max_val = data[metric].max()
                    if max_val > 0:
                        normalized_data[f'{metric}_normalized'] = data[metric] / max_val
                    else:
                        normalized_data[f'{metric}_normalized'] = 0

            # Calculate weighted priority score
            weights = self.investment_weights

            normalized_data['priority_score'] = (
                normalized_data.get('total_economic_impact_normalized', 0) * weights['economic_potential'] +
                normalized_data.get('electrical_capacity_mw_normalized', 0) * weights['technical_feasibility'] +
                normalized_data.get('co2_reduction_tons_year_normalized', 0) * weights['environmental_impact'] +
                normalized_data.get('community_benefit_index', 0) * weights['social_development'] +
                0.5 * weights['policy_alignment']  # Fixed policy alignment score
            )

            # Priority categories
            normalized_data['priority_category'] = pd.cut(
                normalized_data['priority_score'],
                bins=[0, 0.3, 0.6, 1.0],
                labels=['Low Priority', 'Medium Priority', 'High Priority']
            )

            # Investment readiness assessment
            normalized_data['investment_readiness'] = (
                normalized_data['priority_score'] * 0.7 +
                normalized_data.get('infrastructure_development_index', 0) * 0.3
            )

            return normalized_data

        except Exception as e:
            self.logger.error(f"Error calculating priority scores: {e}")
            return data

    def _render_regional_overview(self, data: pd.DataFrame) -> None:
        """Render regional development overview"""
        try:
            st.markdown("#### 🌟 Regional Development Overview")

            # Calculate summary metrics
            total_jobs = data['direct_jobs_created'].sum() + data['indirect_jobs_created'].sum()
            total_gdp_impact = data['gdp_contribution'].sum()
            total_investment = data['infrastructure_investment'].sum()
            high_priority_count = len(data[data['priority_category'] == 'High Priority'])

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Job Creation",
                    f"{total_jobs:.0f}",
                    help="Direct and indirect jobs created across all projects"
                )

            with col2:
                st.metric(
                    "GDP Contribution",
                    f"R$ {total_gdp_impact / 1e9:.2f}B",
                    help="Estimated annual contribution to regional GDP"
                )

            with col3:
                st.metric(
                    "Infrastructure Investment",
                    f"R$ {total_investment / 1e9:.2f}B",
                    help="Total infrastructure investment required"
                )

            with col4:
                st.metric(
                    "High Priority Projects",
                    f"{high_priority_count}",
                    f"{high_priority_count / len(data) * 100:.1f}% of total",
                    help="Projects with high investment priority"
                )

            # Regional development metrics visualization
            col1, col2 = st.columns(2)

            with col1:
                # Development impact by category
                if 'priority_category' in data.columns:
                    category_impact = data.groupby('priority_category').agg({
                        'total_economic_impact': 'sum',
                        'direct_jobs_created': 'sum',
                        'co2_reduction_tons_year': 'sum'
                    }).round(2)

                    fig_category = px.bar(
                        category_impact.reset_index(),
                        x='priority_category',
                        y='total_economic_impact',
                        title='Economic Impact by Priority Category',
                        labels={
                            'priority_category': 'Priority Category',
                            'total_economic_impact': 'Economic Impact (BRL)'
                        },
                        color='priority_category',
                        color_discrete_map={
                            'High Priority': '#2E8B57',
                            'Medium Priority': '#FFD700',
                            'Low Priority': '#DC143C'
                        }
                    )
                    st.plotly_chart(fig_category, use_container_width=True)

            with col2:
                # Regional development dimensions radar
                avg_scores = {
                    'Economic Impact': data.get('total_economic_impact_normalized', pd.Series(0)).mean() * 100,
                    'Social Development': data.get('community_benefit_index', pd.Series(0)).mean() * 100,
                    'Environmental Impact': data.get('co2_reduction_tons_year_normalized', pd.Series(0)).mean() * 100,
                    'Infrastructure Development': data.get('infrastructure_development_index', pd.Series(0)).mean() * 100,
                    'Investment Readiness': data.get('investment_readiness', pd.Series(0)).mean() * 100
                }

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=list(avg_scores.values()),
                    theta=list(avg_scores.keys()),
                    fill='toself',
                    name='Regional Development',
                    line=dict(color='blue')
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    title="Regional Development Dimensions",
                    height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error rendering regional overview: {e}")

    def _render_investment_prioritization(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render investment prioritization analysis"""
        try:
            st.markdown("#### 🎯 Investment Prioritization Analysis")

            # Priority scoring methodology
            with st.expander("📊 Priority Scoring Methodology"):
                st.markdown("**Investment Priority Weights:**")
                for criterion, weight in self.investment_weights.items():
                    st.markdown(f"• {criterion.replace('_', ' ').title()}: {weight*100:.0f}%")

            # Top priority projects
            if 'municipio' in data.columns:
                top_priority = data.nlargest(15, 'priority_score')[
                    ['municipio', 'priority_score', 'total_economic_impact', 'direct_jobs_created',
                     'co2_reduction_tons_year', 'investment_readiness']
                ]

                st.markdown("##### 🏆 Top 15 Investment Priority Projects")

                # Format display data
                display_data = top_priority.copy()
                display_data['total_economic_impact'] = display_data['total_economic_impact'].apply(
                    lambda x: f"R$ {x/1e6:.1f}M" if not pd.isna(x) else "N/A"
                )
                display_data['direct_jobs_created'] = display_data['direct_jobs_created'].round(0)
                display_data['co2_reduction_tons_year'] = display_data['co2_reduction_tons_year'].round(0)
                display_data['priority_score'] = display_data['priority_score'].round(3)
                display_data['investment_readiness'] = display_data['investment_readiness'].round(3)

                display_data.columns = ['Municipality', 'Priority Score', 'Economic Impact',
                                      'Jobs Created', 'CO2 Reduction (tons/year)', 'Investment Readiness']

                st.dataframe(display_data, use_container_width=True)

            # Investment portfolio optimization
            col1, col2 = st.columns(2)

            with col1:
                # Risk-return analysis
                if 'investment_readiness' in data.columns and 'priority_score' in data.columns:
                    fig_portfolio = px.scatter(
                        data,
                        x='investment_readiness',
                        y='priority_score',
                        title='Investment Portfolio: Risk vs Return',
                        labels={
                            'investment_readiness': 'Investment Readiness (Risk)',
                            'priority_score': 'Priority Score (Return)'
                        },
                        hover_data=['municipio'] if 'municipio' in data.columns else None,
                        color='priority_category',
                        size='total_economic_impact'
                    )
                    fig_portfolio.update_layout(height=400)
                    st.plotly_chart(fig_portfolio, use_container_width=True)

            with col2:
                # Cumulative impact analysis
                if 'priority_score' in data.columns:
                    sorted_data = data.sort_values('priority_score', ascending=False).reset_index(drop=True)
                    sorted_data['cumulative_economic_impact'] = sorted_data['total_economic_impact'].cumsum()
                    sorted_data['project_rank'] = range(1, len(sorted_data) + 1)

                    fig_cumulative = px.line(
                        sorted_data.head(50),  # Top 50 projects
                        x='project_rank',
                        y='cumulative_economic_impact',
                        title='Cumulative Economic Impact (Top 50)',
                        labels={
                            'project_rank': 'Project Rank',
                            'cumulative_economic_impact': 'Cumulative Economic Impact (BRL)'
                        }
                    )
                    fig_cumulative.update_layout(height=400)
                    st.plotly_chart(fig_cumulative, use_container_width=True)

            return {
                'top_priority': top_priority if 'municipio' in data.columns else pd.DataFrame(),
                'portfolio_chart': fig_portfolio if 'investment_readiness' in data.columns else None,
                'cumulative_impact_chart': fig_cumulative if 'priority_score' in data.columns else None
            }

        except Exception as e:
            self.logger.error(f"Error rendering investment prioritization: {e}")
            return {}

    def _simulate_regional_development(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Simulate regional development scenarios"""
        try:
            st.markdown("#### 📈 Regional Development Simulation")

            # Development scenarios
            scenarios = {
                'Conservative': {'implementation_rate': 0.3, 'timeline_years': 10},
                'Moderate': {'implementation_rate': 0.6, 'timeline_years': 8},
                'Aggressive': {'implementation_rate': 0.8, 'timeline_years': 5}
            }

            selected_scenario = st.selectbox("Select Development Scenario:", list(scenarios.keys()))

            if selected_scenario:
                scenario_params = scenarios[selected_scenario]

                # Simulate development over time
                timeline_years = scenario_params['timeline_years']
                implementation_rate = scenario_params['implementation_rate']

                # Select projects based on priority and implementation rate
                high_priority = data[data['priority_category'] == 'High Priority']
                medium_priority = data[data['priority_category'] == 'Medium Priority']

                # Projects to implement
                high_to_implement = int(len(high_priority) * implementation_rate)
                medium_to_implement = int(len(medium_priority) * implementation_rate * 0.7)

                # Create timeline simulation
                timeline_data = []
                cumulative_jobs = 0
                cumulative_gdp = 0
                cumulative_co2 = 0

                for year in range(1, timeline_years + 1):
                    # Linear implementation over timeline
                    year_fraction = year / timeline_years

                    jobs_this_year = (high_priority.head(high_to_implement)['direct_jobs_created'].sum() +
                                    medium_priority.head(medium_to_implement)['direct_jobs_created'].sum()) * year_fraction

                    gdp_this_year = (high_priority.head(high_to_implement)['gdp_contribution'].sum() +
                                   medium_priority.head(medium_to_implement)['gdp_contribution'].sum()) * year_fraction

                    co2_this_year = (high_priority.head(high_to_implement)['co2_reduction_tons_year'].sum() +
                                   medium_priority.head(medium_to_implement)['co2_reduction_tons_year'].sum()) * year_fraction

                    timeline_data.append({
                        'Year': year,
                        'Cumulative Jobs': jobs_this_year,
                        'Cumulative GDP (BRL)': gdp_this_year,
                        'Cumulative CO2 Reduction (tons)': co2_this_year
                    })

                timeline_df = pd.DataFrame(timeline_data)

                # Visualization
                col1, col2 = st.columns(2)

                with col1:
                    # Jobs creation timeline
                    fig_jobs = px.line(
                        timeline_df,
                        x='Year',
                        y='Cumulative Jobs',
                        title=f'Job Creation Timeline - {selected_scenario} Scenario',
                        markers=True
                    )
                    st.plotly_chart(fig_jobs, use_container_width=True)

                with col2:
                    # Multi-metric timeline
                    fig_multi = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=['GDP Contribution', 'CO2 Reduction'],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
                    )

                    fig_multi.add_trace(
                        go.Scatter(
                            x=timeline_df['Year'],
                            y=timeline_df['Cumulative GDP (BRL)'],
                            name='GDP Impact',
                            line=dict(color='green')
                        ),
                        row=1, col=1
                    )

                    fig_multi.add_trace(
                        go.Scatter(
                            x=timeline_df['Year'],
                            y=timeline_df['Cumulative CO2 Reduction (tons)'],
                            name='CO2 Reduction',
                            line=dict(color='blue')
                        ),
                        row=2, col=1
                    )

                    fig_multi.update_layout(height=500, title_text=f"Development Timeline - {selected_scenario}")
                    st.plotly_chart(fig_multi, use_container_width=True)

                # Scenario summary
                final_year = timeline_df.iloc[-1]
                st.markdown(f"##### 📋 {selected_scenario} Scenario Summary ({timeline_years} years)")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Jobs Created", f"{final_year['Cumulative Jobs']:.0f}")
                with col2:
                    st.metric("GDP Contribution", f"R$ {final_year['Cumulative GDP (BRL)']/1e9:.2f}B")
                with col3:
                    st.metric("CO2 Reduction", f"{final_year['Cumulative CO2 Reduction (tons)']/1000:.0f}K tons")

            return {
                'timeline_data': timeline_df if selected_scenario else pd.DataFrame(),
                'scenario_params': scenario_params if selected_scenario else {},
                'jobs_timeline': fig_jobs if selected_scenario else None,
                'multi_timeline': fig_multi if selected_scenario else None
            }

        except Exception as e:
            self.logger.error(f"Error simulating regional development: {e}")
            return {}

    def _render_policy_recommendations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render policy recommendations based on analysis"""
        try:
            st.markdown("#### 📋 Policy Recommendations")

            # Policy framework recommendations
            policy_recommendations = {
                'Financial Incentives': [
                    'Tax incentives for biogas plant construction (IPI/ICMS reduction)',
                    'Subsidized credit lines through BNDES for biogas projects',
                    'Feed-in tariffs for biogas electricity generation',
                    'Carbon credit programs for methane emission reduction',
                    'Rural development grants for agricultural biogas projects'
                ],
                'Regulatory Framework': [
                    'Streamlined licensing procedures for small-scale plants',
                    'Technical standards for biogas plant safety and operation',
                    'Grid connection regulations for distributed generation',
                    'Digestate use regulations for agricultural applications',
                    'Professional certification programs for biogas technicians'
                ],
                'Infrastructure Development': [
                    'Priority grid connection for renewable energy projects',
                    'Rural road improvement for feedstock transportation',
                    'Research and development centers for biogas technology',
                    'Training centers for biogas plant operators',
                    'Demonstration plants for technology showcase'
                ],
                'Market Development': [
                    'Biomethane injection standards for natural gas grid',
                    'Green certificates for renewable gas consumption',
                    'Public procurement programs for biogas equipment',
                    'Technology transfer partnerships with international providers',
                    'Supply chain development programs for local manufacturing'
                ]
            }

            # Display recommendations
            for category, recommendations in policy_recommendations.items():
                with st.expander(f"🎯 {category}"):
                    for i, recommendation in enumerate(recommendations, 1):
                        st.markdown(f"{i}. {recommendation}")

            # Priority regions for policy implementation
            if 'priority_score' in data.columns and 'municipio' in data.columns:
                st.markdown("##### 🗺️ Priority Regions for Policy Implementation")

                # Regional policy priorities
                top_regions = data.nlargest(10, 'priority_score')[
                    ['municipio', 'priority_score', 'total_economic_impact', 'community_benefit_index']
                ]

                # Policy implementation urgency
                policy_urgency = []
                for _, row in top_regions.iterrows():
                    if row['priority_score'] > 0.7:
                        urgency = 'Immediate (0-6 months)'
                    elif row['priority_score'] > 0.5:
                        urgency = 'Short-term (6-18 months)'
                    else:
                        urgency = 'Medium-term (1-3 years)'

                    policy_urgency.append({
                        'Municipality': row['municipio'],
                        'Priority Score': f"{row['priority_score']:.3f}",
                        'Policy Implementation Urgency': urgency,
                        'Economic Impact': f"R$ {row['total_economic_impact']/1e6:.1f}M",
                        'Community Benefit': f"{row['community_benefit_index']:.2f}"
                    })

                policy_df = pd.DataFrame(policy_urgency)
                st.dataframe(policy_df, use_container_width=True)

            return {
                'policy_recommendations': policy_recommendations,
                'priority_regions': policy_df if 'priority_score' in data.columns else pd.DataFrame()
            }

        except Exception as e:
            self.logger.error(f"Error rendering policy recommendations: {e}")
            return {}

    def _render_regional_clustering(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render regional clustering analysis for strategic planning"""
        try:
            st.markdown("#### 🎲 Regional Clustering Analysis")

            # Cluster municipalities based on development characteristics
            clustering_features = [
                'total_economic_impact', 'community_benefit_index', 'co2_reduction_tons_year',
                'investment_readiness', 'infrastructure_development_index'
            ]

            # Check if required features exist
            available_features = [f for f in clustering_features if f in data.columns]

            if len(available_features) >= 3:
                # Prepare data for clustering
                cluster_data = data[available_features].fillna(0)

                # Normalize data
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                normalized_data = scaler.fit_transform(cluster_data)

                # Simple k-means clustering (k=4 for strategic planning)
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=4, random_state=42)
                data['cluster'] = kmeans.fit_predict(normalized_data)

                # Define cluster characteristics
                cluster_labels = {
                    0: 'High Economic Potential',
                    1: 'Balanced Development',
                    2: 'Environmental Focus',
                    3: 'Infrastructure Priority'
                }

                data['cluster_label'] = data['cluster'].map(cluster_labels)

                # Cluster analysis visualization
                col1, col2 = st.columns(2)

                with col1:
                    # Cluster distribution
                    cluster_counts = data['cluster_label'].value_counts()
                    fig_cluster_dist = px.pie(
                        values=cluster_counts.values,
                        names=cluster_counts.index,
                        title='Regional Cluster Distribution'
                    )
                    st.plotly_chart(fig_cluster_dist, use_container_width=True)

                with col2:
                    # Cluster characteristics
                    if len(available_features) >= 2:
                        fig_cluster_scatter = px.scatter(
                            data,
                            x=available_features[0],
                            y=available_features[1],
                            color='cluster_label',
                            title='Cluster Characteristics',
                            hover_data=['municipio'] if 'municipio' in data.columns else None
                        )
                        st.plotly_chart(fig_cluster_scatter, use_container_width=True)

                # Cluster summary statistics
                cluster_summary = data.groupby('cluster_label')[available_features].mean().round(2)

                st.markdown("##### 📊 Cluster Characteristics Summary")
                st.dataframe(cluster_summary, use_container_width=True)

                # Strategic recommendations by cluster
                cluster_strategies = {
                    'High Economic Potential': 'Focus on accelerated implementation and large-scale projects',
                    'Balanced Development': 'Comprehensive development approach with moderate timeline',
                    'Environmental Focus': 'Emphasize environmental benefits and sustainability messaging',
                    'Infrastructure Priority': 'Invest in infrastructure development before project implementation'
                }

                st.markdown("##### 🎯 Strategic Recommendations by Cluster")
                for cluster, strategy in cluster_strategies.items():
                    if cluster in data['cluster_label'].values:
                        count = len(data[data['cluster_label'] == cluster])
                        st.markdown(f"**{cluster}** ({count} municipalities): {strategy}")

                return {
                    'cluster_data': data[['municipio', 'cluster_label'] + available_features] if 'municipio' in data.columns else data[['cluster_label'] + available_features],
                    'cluster_distribution': fig_cluster_dist,
                    'cluster_scatter': fig_cluster_scatter if len(available_features) >= 2 else None,
                    'cluster_summary': cluster_summary,
                    'cluster_strategies': cluster_strategies
                }

            else:
                st.warning("⚠️ Insufficient data for clustering analysis")
                return {}

        except Exception as e:
            self.logger.error(f"Error rendering regional clustering: {e}")
            st.warning("⚠️ Clustering analysis requires scikit-learn library")
            return {}


# Factory function
def create_regional_analyzer() -> RegionalAnalyzer:
    """Create RegionalAnalyzer instance"""
    return RegionalAnalyzer()