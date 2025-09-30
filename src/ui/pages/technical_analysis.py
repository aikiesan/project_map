"""
CP2B Maps V2 - Technical Analysis Module
Technical feasibility assessment, infrastructure requirements, and implementation planning
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


class TechnicalAnalyzer:
    """
    Technical feasibility analysis engine for biogas projects
    Features: Infrastructure assessment, technology selection, implementation planning
    """

    def __init__(self):
        """Initialize Technical Analyzer"""
        self.logger = get_logger(self.__class__.__name__)

        # Technical parameters and standards
        self.technical_factors = {
            'minimum_viable_biogas_m3_day': 50,  # Minimum daily production for viability
            'optimal_plant_size_m3_day': 500,  # Optimal plant size for efficiency
            'digester_retention_days': 30,  # Hydraulic retention time
            'biogas_to_biomethane_efficiency': 0.95,  # Upgrading efficiency
            'electricity_generation_efficiency': 0.38,  # Engine efficiency
            'heat_recovery_efficiency': 0.45,  # Heat recovery from engine
            'plant_capacity_factor': 0.85,  # Operational availability
            'substrate_preparation_factor': 1.2,  # Additional capacity for preprocessing
            'safety_margin_factor': 1.15  # Safety margin for design
        }

        # Infrastructure requirements
        self.infrastructure_requirements = {
            'electrical_grid_connection': 'Medium Voltage Connection Required',
            'road_access': 'All-weather road access for trucks',
            'water_supply': 'Reliable water source (10-15 L/m³ biogas)',
            'waste_management': 'Digestate storage and distribution system',
            'monitoring_systems': 'SCADA and remote monitoring capability',
            'safety_systems': 'Gas detection, flare systems, emergency protocols'
        }

    def render_technical_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render comprehensive technical feasibility analysis

        Args:
            data: Municipality data with biogas calculations
            scenario_config: Scenario parameters

        Returns:
            Dictionary with technical analysis results
        """
        try:
            render_section_header(
                "🔧 Análise de Viabilidade Técnica",
                description="Requisitos de infraestrutura, avaliação de tecnologia e planejamento de implementação"
            )

            # Calculate technical metrics
            technical_data = self._calculate_technical_metrics(data, scenario_config)

            # Technical overview
            self._render_technical_overview(technical_data)

            # Plant sizing and design
            sizing_results = self._render_plant_sizing_analysis(technical_data)

            # Technology selection
            technology_results = self._render_technology_selection(technical_data)

            # Infrastructure assessment
            infrastructure_results = self._render_infrastructure_assessment(technical_data)

            # Implementation timeline
            timeline_results = self._render_implementation_timeline(technical_data)

            return {
                'technical_data': technical_data,
                'sizing_results': sizing_results,
                'technology_results': technology_results,
                'infrastructure_results': infrastructure_results,
                'timeline_results': timeline_results
            }

        except Exception as e:
            self.logger.error(f"Error in technical analysis: {e}")
            st.error("❌ Error performing technical analysis")
            return {}

    def _calculate_technical_metrics(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate technical feasibility metrics for each municipality"""
        try:
            tech_data = data.copy()

            # Calculate total biogas potential
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]
            tech_data['total_biogas_potential'] = tech_data[biogas_columns].sum(axis=1)

            # Daily biogas production
            tech_data['daily_biogas_production'] = tech_data['total_biogas_potential'] / 365

            # Technical feasibility classification
            tech_data['technical_feasibility'] = pd.cut(
                tech_data['daily_biogas_production'],
                bins=[0, 50, 200, 1000, np.inf],
                labels=['Não Viável', 'Pequena Escala', 'Média Escala', 'Grande Escala'],
                ordered=True
            )

            # Recommended plant capacity (with safety margin)
            tech_data['recommended_plant_capacity'] = (
                tech_data['daily_biogas_production'] *
                self.technical_factors['safety_margin_factor']
            )

            # Digester volume calculation
            tech_data['digester_volume_m3'] = (
                tech_data['recommended_plant_capacity'] *
                self.technical_factors['digester_retention_days']
            )

            # Electricity generation potential (kWh/day)
            tech_data['electricity_generation_kwh_day'] = (
                tech_data['daily_biogas_production'] *
                6.0 *  # kWh per m³ biogas
                self.technical_factors['electricity_generation_efficiency'] *
                self.technical_factors['plant_capacity_factor']
            )

            # Heat generation potential (kWh/day)
            tech_data['heat_generation_kwh_day'] = (
                tech_data['daily_biogas_production'] *
                6.0 *
                self.technical_factors['heat_recovery_efficiency'] *
                self.technical_factors['plant_capacity_factor']
            )

            # Biomethane production potential (m³/day)
            tech_data['biomethane_production_m3_day'] = (
                tech_data['daily_biogas_production'] *
                0.6 *  # 60% methane content
                self.technical_factors['biogas_to_biomethane_efficiency']
            )

            # Equipment sizing
            tech_data = self._calculate_equipment_sizing(tech_data)

            # Implementation complexity score (1-5 scale)
            tech_data['implementation_complexity'] = self._calculate_implementation_complexity(tech_data)

            return tech_data

        except Exception as e:
            self.logger.error(f"Error calculating technical metrics: {e}")
            return data

    def _calculate_equipment_sizing(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate equipment sizing requirements"""
        try:
            # Gas engine sizing (kW)
            data['gas_engine_capacity_kw'] = np.ceil(
                data['electricity_generation_kwh_day'] / 24  # Average hourly output
            )

            # Gas storage sizing (m³)
            data['gas_storage_volume_m3'] = (
                data['daily_biogas_production'] * 0.5  # 12-hour storage capacity
            )

            # Digestate storage sizing (m³)
            data['digestate_storage_m3'] = (
                data['digester_volume_m3'] * 0.3  # 30% of digester volume
            )

            # Substrate storage sizing (m³)
            data['substrate_storage_m3'] = (
                data['daily_biogas_production'] *
                self.technical_factors['substrate_preparation_factor'] *
                7  # 7 days storage
            )

            return data

        except Exception as e:
            self.logger.error(f"Error calculating equipment sizing: {e}")
            return data

    def _calculate_implementation_complexity(self, data: pd.DataFrame) -> pd.Series:
        """Calculate implementation complexity score based on various factors"""
        try:
            complexity_score = pd.Series(index=data.index, data=1.0)  # Base score

            # Scale factor (larger plants are more complex)
            scale_factor = pd.cut(
                data['daily_biogas_production'],
                bins=[0, 100, 500, 2000, np.inf],
                labels=[1, 2, 3, 4]
            ).astype(float)

            # Technology complexity factor
            tech_factor = pd.cut(
                data['gas_engine_capacity_kw'],
                bins=[0, 50, 200, 1000, np.inf],
                labels=[1, 2, 3, 4]
            ).astype(float)

            # Combined complexity score
            complexity_score = (scale_factor + tech_factor) / 2

            return complexity_score.fillna(1.0)

        except Exception as e:
            self.logger.error(f"Error calculating implementation complexity: {e}")
            return pd.Series(index=data.index, data=1.0)

    def _render_technical_overview(self, data: pd.DataFrame) -> None:
        """Render technical feasibility overview"""
        try:
            st.markdown("#### ⚙️ Technical Feasibility Overview")

            # Calculate summary metrics
            total_plants = len(data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']])
            total_capacity = data['gas_engine_capacity_kw'].sum()
            total_electricity = data['electricity_generation_kwh_day'].sum() * 365 / 1000  # MWh/year
            avg_plant_size = data['recommended_plant_capacity'].mean()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Technically Viable Plants",
                    f"{total_plants}",
                    f"{total_plants / len(data) * 100:.1f}% of municipalities",
                    help="Plants with daily production ≥ 50 m³/day"
                )

            with col2:
                st.metric(
                    "Total Electrical Capacity",
                    f"{total_capacity:.0f} kW",
                    help="Combined electrical generation capacity"
                )

            with col3:
                st.metric(
                    "Annual Electricity Generation",
                    f"{total_electricity:.0f} MWh/year",
                    help="Total annual electricity generation potential"
                )

            with col4:
                st.metric(
                    "Average Plant Size",
                    f"{avg_plant_size:.0f} m³/day",
                    help="Average recommended plant capacity"
                )

            # Technical feasibility distribution
            if 'technical_feasibility' in data.columns:
                feasibility_counts = data['technical_feasibility'].value_counts()

                col1, col2 = st.columns(2)

                with col1:
                    fig_feasibility = px.pie(
                        values=feasibility_counts.values,
                        names=feasibility_counts.index,
                        title='Technical Feasibility Distribution',
                        color_discrete_map={
                            'Grande Escala': '#2E8B57',
                            'Média Escala': '#32CD32',
                            'Pequena Escala': '#FFD700',
                            'Não Viável': '#DC143C'
                        }
                    )
                    st.plotly_chart(fig_feasibility, use_container_width=True)

                with col2:
                    # Plant capacity distribution
                    viable_data = data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']]
                    if len(viable_data) > 0:
                        fig_capacity = px.histogram(
                            viable_data,
                            x='recommended_plant_capacity',
                            nbins=20,
                            title='Plant Capacity Distribution (Viable Plants)',
                            labels={'recommended_plant_capacity': 'Plant Capacity (m³/day)', 'count': 'Number of Plants'}
                        )
                        st.plotly_chart(fig_capacity, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error rendering technical overview: {e}")

    def _render_plant_sizing_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render plant sizing and design analysis"""
        try:
            st.markdown("#### 📏 Plant Sizing and Design Analysis")

            # Filter viable plants
            viable_plants = data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']]

            if len(viable_plants) == 0:
                st.warning("⚠️ No technically viable plants found with current parameters")
                return {}

            # Plant sizing recommendations
            col1, col2 = st.columns(2)

            with col1:
                # Equipment sizing chart
                fig_equipment = go.Figure()

                fig_equipment.add_trace(go.Scatter(
                    x=viable_plants['daily_biogas_production'],
                    y=viable_plants['gas_engine_capacity_kw'],
                    mode='markers',
                    name='Gas Engine',
                    marker=dict(color='blue', size=8),
                    hovertemplate='Biogas: %{x:.0f} m³/day<br>Engine: %{y:.0f} kW<extra></extra>'
                ))

                fig_equipment.update_layout(
                    title='Gas Engine Sizing vs Biogas Production',
                    xaxis_title='Daily Biogas Production (m³/day)',
                    yaxis_title='Gas Engine Capacity (kW)',
                    height=400
                )
                st.plotly_chart(fig_equipment, use_container_width=True)

            with col2:
                # Digester sizing chart
                fig_digester = px.scatter(
                    viable_plants,
                    x='daily_biogas_production',
                    y='digester_volume_m3',
                    title='Digester Volume vs Biogas Production',
                    labels={
                        'daily_biogas_production': 'Daily Biogas Production (m³/day)',
                        'digester_volume_m3': 'Digester Volume (m³)'
                    },
                    hover_data=['municipio'] if 'municipio' in viable_plants.columns else None
                )
                fig_digester.update_layout(height=400)
                st.plotly_chart(fig_digester, use_container_width=True)

            # Technology recommendations table
            st.markdown("##### 🎯 Plant Design Recommendations")

            # Create plant size categories
            size_categories = {
                'Small Scale (50-200 m³/day)': viable_plants[
                    (viable_plants['daily_biogas_production'] >= 50) &
                    (viable_plants['daily_biogas_production'] < 200)
                ],
                'Medium Scale (200-1000 m³/day)': viable_plants[
                    (viable_plants['daily_biogas_production'] >= 200) &
                    (viable_plants['daily_biogas_production'] < 1000)
                ],
                'Large Scale (≥1000 m³/day)': viable_plants[
                    viable_plants['daily_biogas_production'] >= 1000
                ]
            }

            recommendations = []
            for category, plants_data in size_categories.items():
                if len(plants_data) > 0:
                    avg_capacity = plants_data['recommended_plant_capacity'].mean()
                    avg_engine = plants_data['gas_engine_capacity_kw'].mean()
                    avg_digester = plants_data['digester_volume_m3'].mean()

                    recommendations.append({
                        'Plant Scale': category,
                        'Count': len(plants_data),
                        'Avg Capacity (m³/day)': f"{avg_capacity:.0f}",
                        'Avg Engine (kW)': f"{avg_engine:.0f}",
                        'Avg Digester (m³)': f"{avg_digester:.0f}",
                        'Technology': self._get_technology_recommendation(avg_capacity)
                    })

            if recommendations:
                recommendations_df = pd.DataFrame(recommendations)
                st.dataframe(recommendations_df, use_container_width=True)

            return {
                'equipment_sizing_chart': fig_equipment,
                'digester_sizing_chart': fig_digester,
                'recommendations': recommendations
            }

        except Exception as e:
            self.logger.error(f"Error rendering plant sizing analysis: {e}")
            return {}

    def _get_technology_recommendation(self, capacity: float) -> str:
        """Get technology recommendation based on plant capacity"""
        if capacity < 200:
            return "Batch digester, small gas engine"
        elif capacity < 1000:
            return "Continuous digester, medium gas engine, basic automation"
        else:
            return "Advanced continuous digester, large gas engine, full automation, biogas upgrading"

    def _render_technology_selection(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render technology selection analysis"""
        try:
            st.markdown("#### 🚀 Technology Selection Analysis")

            # Technology options based on plant size
            technology_options = {
                'Digester Technology': {
                    'Small Scale': ['Batch Reactor', 'Simple Continuous Reactor'],
                    'Medium Scale': ['CSTR', 'Plug Flow Reactor'],
                    'Large Scale': ['Advanced CSTR', 'Two-Stage System', 'Thermophilic Digestion']
                },
                'Gas Utilization': {
                    'Small Scale': ['Direct Burning', 'Small Gas Engine'],
                    'Medium Scale': ['Gas Engine + Heat Recovery', 'Micro Turbine'],
                    'Large Scale': ['Large Gas Engine', 'Biogas Upgrading', 'Combined Heat & Power']
                },
                'Automation Level': {
                    'Small Scale': ['Manual Operation', 'Basic Controls'],
                    'Medium Scale': ['Semi-Automated', 'PLC Control'],
                    'Large Scale': ['Full Automation', 'SCADA System', 'Remote Monitoring']
                }
            }

            # Display technology matrix
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 🔧 Technology Options by Scale")
                for tech_category, options in technology_options.items():
                    with st.expander(f"{tech_category}"):
                        for scale, technologies in options.items():
                            st.markdown(f"**{scale}:**")
                            for tech in technologies:
                                st.markdown(f"• {tech}")

            with col2:
                # Technology complexity vs capacity chart
                viable_plants = data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']]

                if len(viable_plants) > 0:
                    fig_complexity = px.scatter(
                        viable_plants,
                        x='recommended_plant_capacity',
                        y='implementation_complexity',
                        title='Implementation Complexity vs Plant Capacity',
                        labels={
                            'recommended_plant_capacity': 'Plant Capacity (m³/day)',
                            'implementation_complexity': 'Implementation Complexity (1-5)'
                        },
                        hover_data=['municipio'] if 'municipio' in viable_plants.columns else None,
                        color='technical_feasibility'
                    )
                    fig_complexity.update_layout(height=400)
                    st.plotly_chart(fig_complexity, use_container_width=True)

            return {
                'technology_options': technology_options,
                'complexity_chart': fig_complexity if len(viable_plants) > 0 else None
            }

        except Exception as e:
            self.logger.error(f"Error rendering technology selection: {e}")
            return {}

    def _render_infrastructure_assessment(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render infrastructure requirements assessment"""
        try:
            st.markdown("#### 🏗️ Infrastructure Requirements Assessment")

            # Infrastructure requirements checklist
            st.markdown("##### 📋 Critical Infrastructure Requirements")

            requirements_data = []
            for requirement, description in self.infrastructure_requirements.items():
                requirements_data.append({
                    'Infrastructure Component': requirement.replace('_', ' ').title(),
                    'Description': description,
                    'Priority': 'High' if requirement in ['electrical_grid_connection', 'road_access'] else 'Medium'
                })

            requirements_df = pd.DataFrame(requirements_data)
            st.dataframe(requirements_df, use_container_width=True)

            # Infrastructure readiness assessment
            col1, col2 = st.columns(2)

            with col1:
                # Simulate infrastructure readiness scores (in real implementation, this would come from actual data)
                viable_plants = data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']]

                if len(viable_plants) > 0:
                    # Simulate infrastructure scores based on plant size and location
                    np.random.seed(42)  # For reproducible results
                    viable_plants = viable_plants.copy()
                    viable_plants['infrastructure_readiness'] = np.random.normal(0.7, 0.15, len(viable_plants))
                    viable_plants['infrastructure_readiness'] = np.clip(viable_plants['infrastructure_readiness'], 0.2, 1.0)

                    fig_infrastructure = px.histogram(
                        viable_plants,
                        x='infrastructure_readiness',
                        nbins=10,
                        title='Infrastructure Readiness Distribution',
                        labels={'infrastructure_readiness': 'Infrastructure Readiness Score', 'count': 'Number of Plants'}
                    )
                    fig_infrastructure.update_layout(height=400)
                    st.plotly_chart(fig_infrastructure, use_container_width=True)

            with col2:
                # Infrastructure investment requirements
                if len(viable_plants) > 0:
                    viable_plants['infrastructure_investment'] = (
                        viable_plants['recommended_plant_capacity'] * 200 *
                        (2 - viable_plants['infrastructure_readiness'])  # Higher cost for lower readiness
                    )

                    fig_investment = px.scatter(
                        viable_plants,
                        x='infrastructure_readiness',
                        y='infrastructure_investment',
                        title='Infrastructure Investment vs Readiness',
                        labels={
                            'infrastructure_readiness': 'Infrastructure Readiness Score',
                            'infrastructure_investment': 'Additional Investment (BRL)'
                        },
                        hover_data=['municipio'] if 'municipio' in viable_plants.columns else None
                    )
                    fig_investment.update_layout(height=400)
                    st.plotly_chart(fig_investment, use_container_width=True)

            return {
                'requirements': requirements_df,
                'readiness_distribution': fig_infrastructure if len(viable_plants) > 0 else None,
                'investment_chart': fig_investment if len(viable_plants) > 0 else None
            }

        except Exception as e:
            self.logger.error(f"Error rendering infrastructure assessment: {e}")
            return {}

    def _render_implementation_timeline(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render implementation timeline and phasing plan"""
        try:
            st.markdown("#### ⏱️ Implementation Timeline")

            # Implementation phases
            phases = {
                'Phase 1: Planning & Design (6-12 months)': [
                    'Feasibility studies',
                    'Environmental impact assessment',
                    'Engineering design',
                    'Permitting and licensing',
                    'Financial arrangements'
                ],
                'Phase 2: Infrastructure Development (12-18 months)': [
                    'Site preparation',
                    'Utility connections',
                    'Access road construction',
                    'Foundation and civil works'
                ],
                'Phase 3: Plant Construction (18-24 months)': [
                    'Equipment procurement',
                    'Installation and assembly',
                    'Control system setup',
                    'Testing and commissioning'
                ],
                'Phase 4: Operation & Optimization (Ongoing)': [
                    'Staff training',
                    'Performance optimization',
                    'Maintenance programs',
                    'Continuous improvement'
                ]
            }

            # Display implementation phases
            for phase, activities in phases.items():
                with st.expander(f"📅 {phase}"):
                    for activity in activities:
                        st.markdown(f"• {activity}")

            # Implementation priority matrix
            viable_plants = data[data['daily_biogas_production'] >= self.technical_factors['minimum_viable_biogas_m3_day']]

            if len(viable_plants) > 0 and 'municipio' in viable_plants.columns:
                # Calculate implementation priority score
                viable_plants = viable_plants.copy()

                # Normalize metrics for priority calculation
                capacity_score = (viable_plants['daily_biogas_production'] - viable_plants['daily_biogas_production'].min()) / \
                               (viable_plants['daily_biogas_production'].max() - viable_plants['daily_biogas_production'].min())

                complexity_score = 1 - ((viable_plants['implementation_complexity'] - 1) / 4)  # Invert complexity (lower is better)

                # Simulate economic viability score
                np.random.seed(42)
                economic_score = np.random.uniform(0.3, 1.0, len(viable_plants))

                viable_plants['priority_score'] = (capacity_score + complexity_score + economic_score) / 3

                # Priority categories
                viable_plants['priority_category'] = pd.cut(
                    viable_plants['priority_score'],
                    bins=[0, 0.4, 0.7, 1.0],
                    labels=['Low Priority', 'Medium Priority', 'High Priority']
                )

                # Priority distribution chart
                col1, col2 = st.columns(2)

                with col1:
                    priority_counts = viable_plants['priority_category'].value_counts()
                    fig_priority = px.pie(
                        values=priority_counts.values,
                        names=priority_counts.index,
                        title='Implementation Priority Distribution',
                        color_discrete_map={
                            'High Priority': '#2E8B57',
                            'Medium Priority': '#FFD700',
                            'Low Priority': '#DC143C'
                        }
                    )
                    st.plotly_chart(fig_priority, use_container_width=True)

                with col2:
                    # Priority vs capacity scatter
                    fig_priority_scatter = px.scatter(
                        viable_plants,
                        x='daily_biogas_production',
                        y='priority_score',
                        title='Priority Score vs Biogas Production',
                        labels={
                            'daily_biogas_production': 'Daily Biogas Production (m³/day)',
                            'priority_score': 'Implementation Priority Score'
                        },
                        color='priority_category',
                        hover_data=['municipio']
                    )
                    st.plotly_chart(fig_priority_scatter, use_container_width=True)

                # Top priority projects
                top_priority = viable_plants.nlargest(10, 'priority_score')[
                    ['municipio', 'daily_biogas_production', 'gas_engine_capacity_kw', 'priority_score', 'priority_category']
                ]

                st.markdown("##### 🎯 Top 10 Priority Projects")
                display_priority = top_priority.copy()
                display_priority.columns = ['Municipality', 'Biogas (m³/day)', 'Engine (kW)', 'Priority Score', 'Category']
                display_priority['Biogas (m³/day)'] = display_priority['Biogas (m³/day)'].round(0)
                display_priority['Engine (kW)'] = display_priority['Engine (kW)'].round(0)
                display_priority['Priority Score'] = display_priority['Priority Score'].round(3)
                st.dataframe(display_priority, use_container_width=True)

            return {
                'phases': phases,
                'priority_distribution': fig_priority if len(viable_plants) > 0 else None,
                'priority_scatter': fig_priority_scatter if len(viable_plants) > 0 else None,
                'top_priority': top_priority if len(viable_plants) > 0 else pd.DataFrame()
            }

        except Exception as e:
            self.logger.error(f"Error rendering implementation timeline: {e}")
            return {}


# Factory function
def create_technical_analyzer() -> TechnicalAnalyzer:
    """Create TechnicalAnalyzer instance"""
    return TechnicalAnalyzer()