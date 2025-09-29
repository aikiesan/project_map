"""
CP2B Maps V2 - Analysis Orchestrator
Main analysis page that coordinates all specialized analysis modules
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import datetime

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader

# Import specialized analysis modules
from src.ui.pages.economic_analysis import create_economic_analyzer
from src.ui.pages.environmental_analysis import create_environmental_analyzer
from src.ui.pages.technical_analysis import create_technical_analyzer
from src.ui.pages.regional_analysis import create_regional_analyzer

logger = get_logger(__name__)


class AnalysisOrchestrator:
    """
    Main analysis orchestrator that coordinates all specialized analysis modules
    Features: Comprehensive biogas analysis with scenario planning
    """

    def __init__(self):
        """Initialize Analysis Orchestrator"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing AnalysisOrchestrator component")

        # Initialize specialized analyzers
        self.economic_analyzer = create_economic_analyzer()
        self.environmental_analyzer = create_environmental_analyzer()
        self.technical_analyzer = create_technical_analyzer()
        self.regional_analyzer = create_regional_analyzer()

    def render(self) -> Dict[str, Any]:
        """
        Render comprehensive analysis page with all modules

        Returns:
            Dictionary with complete analysis results
        """
        try:
            st.markdown("# 📈 Advanced Biogas Analysis & Planning")
            st.markdown("### Comprehensive scenario planning, feasibility analysis, and strategic planning")

            # Load and prepare data
            analysis_data = self._load_analysis_data()
            if analysis_data is None or len(analysis_data) == 0:
                st.error("⚠️ No data available for analysis")
                return {}

            # Scenario configuration
            scenario_config = self._render_scenario_configuration()

            # Analysis tabs for better organization
            tab1, tab2, tab3, tab4 = st.tabs([
                "💰 Economic Analysis",
                "🌍 Environmental Analysis",
                "🔧 Technical Analysis",
                "🗺️ Regional Analysis"
            ])

            results = {}

            with tab1:
                economic_results = self.economic_analyzer.render_economic_analysis(analysis_data, scenario_config)
                results['economic'] = economic_results

            with tab2:
                environmental_results = self.environmental_analyzer.render_environmental_analysis(analysis_data, scenario_config)
                results['environmental'] = environmental_results

            with tab3:
                technical_results = self.technical_analyzer.render_technical_analysis(analysis_data, scenario_config)
                results['technical'] = technical_results

            with tab4:
                regional_results = self.regional_analyzer.render_regional_analysis(analysis_data, scenario_config)
                results['regional'] = regional_results

            # Executive summary
            self._render_executive_summary(results, scenario_config)

            # Export functionality
            self._render_export_options(results, analysis_data)

            return {
                'analysis_data': analysis_data,
                'scenario_config': scenario_config,
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Error rendering analysis orchestrator: {e}", exc_info=True)
            st.error("⚠️ Failed to render analysis page. Check logs for details.")
            return {}

    def _load_analysis_data(self) -> Optional[pd.DataFrame]:
        """Load and prepare data for comprehensive analysis"""
        try:
            data = database_loader.load_municipalities_data()
            if data is None:
                return None

            # Data quality validation
            required_columns = ['municipio', 'populacao']
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]

            if not all(col in data.columns for col in required_columns):
                self.logger.warning("Missing required columns in data")
                return None

            if len(biogas_columns) == 0:
                self.logger.warning("No biogas columns found in data")
                return None

            # Data preprocessing
            data = data.dropna(subset=required_columns)

            # Fill missing biogas values with 0
            for col in biogas_columns:
                data[col] = data[col].fillna(0)

            # Calculate total biogas potential for filtering
            data['total_biogas_potential'] = data[biogas_columns].sum(axis=1)

            # Filter out municipalities with zero biogas potential
            data = data[data['total_biogas_potential'] > 0]

            self.logger.info(f"Loaded {len(data)} municipalities for analysis")
            return data

        except Exception as e:
            self.logger.error(f"Error loading analysis data: {e}")
            return None

    def _render_scenario_configuration(self) -> Dict[str, Any]:
        """Render scenario configuration interface"""
        try:
            st.markdown("## ⚙️ Scenario Configuration")

            with st.expander("🎛️ Analysis Parameters", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    scenario_type = st.selectbox(
                        "Analysis Scenario",
                        ["Conservative", "Realistic", "Optimistic"],
                        index=1,
                        help="Select the scenario for analysis assumptions"
                    )

                with col2:
                    time_horizon = st.slider(
                        "Time Horizon (years)",
                        min_value=5,
                        max_value=25,
                        value=20,
                        help="Analysis time horizon for projections"
                    )

                with col3:
                    market_penetration = st.slider(
                        "Market Penetration (%)",
                        min_value=10,
                        max_value=100,
                        value=60,
                        help="Expected market penetration rate"
                    )

                # Advanced parameters
                col4, col5 = st.columns(2)

                with col4:
                    technology_advancement = st.selectbox(
                        "Technology Advancement",
                        ["Current", "Moderate Improvement", "High Improvement"],
                        index=1,
                        help="Expected technology advancement level"
                    )

                with col5:
                    policy_support = st.selectbox(
                        "Policy Support Level",
                        ["Minimal", "Current", "Enhanced", "Aggressive"],
                        index=2,
                        help="Level of government policy support"
                    )

            return {
                'scenario_type': scenario_type.lower(),
                'time_horizon': time_horizon,
                'market_penetration': market_penetration / 100,
                'technology_advancement': technology_advancement.lower(),
                'policy_support': policy_support.lower(),
                'analysis_date': datetime.datetime.now()
            }

        except Exception as e:
            self.logger.error(f"Error rendering scenario configuration: {e}")
            return {
                'scenario_type': 'realistic',
                'time_horizon': 20,
                'market_penetration': 0.6,
                'technology_advancement': 'moderate improvement',
                'policy_support': 'enhanced',
                'analysis_date': datetime.datetime.now()
            }

    def _render_executive_summary(self, results: Dict[str, Any], scenario_config: Dict[str, Any]) -> None:
        """Render executive summary of all analysis results"""
        try:
            st.markdown("## 📋 Executive Summary")
            st.markdown(f"**Analysis Date:** {scenario_config['analysis_date'].strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Scenario:** {scenario_config['scenario_type'].title()} | **Time Horizon:** {scenario_config['time_horizon']} years")

            # Key performance indicators
            col1, col2, col3, col4 = st.columns(4)

            # Economic KPIs
            economic_data = results.get('economic', {})
            if economic_data:
                total_investment = economic_data.get('economic_factors', {}).get('total_investment', 0)
                total_revenue = economic_data.get('roi_results', {}).get('total_revenue', 0)

            with col1:
                st.metric(
                    "Total Investment Potential",
                    f"R$ {total_investment / 1e9:.1f}B" if 'total_investment' in locals() else "N/A",
                    help="Total investment required for all viable projects"
                )

            # Environmental KPIs
            environmental_data = results.get('environmental', {})
            if environmental_data:
                co2_reduction = environmental_data.get('co2_results', {}).get('total_co2_reduction', 0)

            with col2:
                st.metric(
                    "CO2 Reduction Potential",
                    f"{co2_reduction / 1e6:.2f}M tons/year" if 'co2_reduction' in locals() else "N/A",
                    help="Annual CO2 equivalent reduction potential"
                )

            # Technical KPIs
            technical_data = results.get('technical', {})
            if technical_data:
                viable_plants = technical_data.get('sizing_results', {}).get('viable_plants_count', 0)

            with col3:
                st.metric(
                    "Viable Projects",
                    f"{viable_plants}" if 'viable_plants' in locals() else "N/A",
                    help="Number of technically and economically viable projects"
                )

            # Regional KPIs
            regional_data = results.get('regional', {})
            if regional_data:
                job_creation = regional_data.get('development_results', {}).get('total_jobs', 0)

            with col4:
                st.metric(
                    "Job Creation Potential",
                    f"{job_creation:.0f}" if 'job_creation' in locals() else "N/A",
                    help="Total direct and indirect jobs created"
                )

            # Key insights
            st.markdown("### 🔍 Key Insights")

            insights = []

            # Economic insights
            if economic_data and 'feasibility_results' in economic_data:
                insights.append("💰 **Economic:** Strong economic viability identified in major agricultural regions")

            # Environmental insights
            if environmental_data and 'sustainability_results' in environmental_data:
                insights.append("🌍 **Environmental:** Significant potential for carbon footprint reduction and circular economy development")

            # Technical insights
            if technical_data and 'technology_results' in technical_data:
                insights.append("🔧 **Technical:** Technology solutions available for all project scales with appropriate automation levels")

            # Regional insights
            if regional_data and 'prioritization_results' in regional_data:
                insights.append("🗺️ **Regional:** Clear investment priorities identified with balanced regional development potential")

            for insight in insights:
                st.markdown(f"• {insight}")

            # Next steps
            st.markdown("### 🚀 Recommended Next Steps")
            next_steps = [
                "1. **Priority Project Development:** Focus on high-priority municipalities identified in regional analysis",
                "2. **Policy Framework Implementation:** Develop supportive policies based on recommendations",
                "3. **Infrastructure Development:** Invest in critical infrastructure for viable projects",
                "4. **Technology Transfer:** Establish partnerships for technology development and transfer",
                "5. **Monitoring and Evaluation:** Implement performance tracking systems"
            ]

            for step in next_steps:
                st.markdown(step)

        except Exception as e:
            self.logger.error(f"Error rendering executive summary: {e}")

    def _render_export_options(self, results: Dict[str, Any], data: pd.DataFrame) -> None:
        """Render export options for analysis results"""
        try:
            st.markdown("## 📤 Export Analysis Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📊 Export Economic Analysis", type="secondary"):
                    economic_data = results.get('economic', {}).get('adjusted_data', pd.DataFrame())
                    if not economic_data.empty:
                        csv = economic_data.to_csv(index=False)
                        st.download_button(
                            label="Download Economic Data (CSV)",
                            data=csv,
                            file_name=f"economic_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )

            with col2:
                if st.button("🌍 Export Environmental Analysis", type="secondary"):
                    environmental_data = results.get('environmental', {}).get('environmental_data', pd.DataFrame())
                    if not environmental_data.empty:
                        csv = environmental_data.to_csv(index=False)
                        st.download_button(
                            label="Download Environmental Data (CSV)",
                            data=csv,
                            file_name=f"environmental_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )

            with col3:
                if st.button("🗺️ Export Regional Analysis", type="secondary"):
                    regional_data = results.get('regional', {}).get('regional_data', pd.DataFrame())
                    if not regional_data.empty:
                        csv = regional_data.to_csv(index=False)
                        st.download_button(
                            label="Download Regional Data (CSV)",
                            data=csv,
                            file_name=f"regional_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )

            # Comprehensive report export
            if st.button("📋 Generate Comprehensive Report", type="primary"):
                report_data = self._generate_comprehensive_report(results, data)
                st.download_button(
                    label="Download Complete Analysis Report (CSV)",
                    data=report_data,
                    file_name=f"cp2b_comprehensive_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )

        except Exception as e:
            self.logger.error(f"Error rendering export options: {e}")

    def _generate_comprehensive_report(self, results: Dict[str, Any], data: pd.DataFrame) -> str:
        """Generate comprehensive analysis report"""
        try:
            # Combine all analysis results into a single dataset
            comprehensive_data = data.copy()

            # Add economic metrics
            economic_data = results.get('economic', {}).get('adjusted_data', pd.DataFrame())
            if not economic_data.empty:
                economic_cols = ['investment_cost', 'total_annual_revenue', 'payback_years', 'npv']
                for col in economic_cols:
                    if col in economic_data.columns:
                        comprehensive_data[f'economic_{col}'] = economic_data[col]

            # Add environmental metrics
            environmental_data = results.get('environmental', {}).get('environmental_data', pd.DataFrame())
            if not environmental_data.empty:
                env_cols = ['co2_reduction_tons_year', 'water_saving_million_liters_year', 'fertilizer_replacement_tons_year']
                for col in env_cols:
                    if col in environmental_data.columns:
                        comprehensive_data[f'environmental_{col}'] = environmental_data[col]

            # Add technical metrics
            technical_data = results.get('technical', {}).get('technical_data', pd.DataFrame())
            if not technical_data.empty:
                tech_cols = ['technical_feasibility', 'recommended_plant_capacity', 'gas_engine_capacity_kw']
                for col in tech_cols:
                    if col in technical_data.columns:
                        comprehensive_data[f'technical_{col}'] = technical_data[col]

            # Add regional metrics
            regional_data = results.get('regional', {}).get('regional_data', pd.DataFrame())
            if not regional_data.empty:
                regional_cols = ['priority_score', 'priority_category', 'investment_readiness']
                for col in regional_cols:
                    if col in regional_data.columns:
                        comprehensive_data[f'regional_{col}'] = regional_data[col]

            return comprehensive_data.to_csv(index=False)

        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            return data.to_csv(index=False)


# Factory function
@st.cache_resource
def get_analysis_orchestrator() -> AnalysisOrchestrator:
    """Get cached Analysis Orchestrator instance"""
    return AnalysisOrchestrator()


# Main page class for backward compatibility
class AnalysisPage:
    """Main Analysis Page - delegates to orchestrator"""

    def __init__(self):
        self.orchestrator = get_analysis_orchestrator()

    def render(self) -> Dict[str, Any]:
        """Render analysis page"""
        return self.orchestrator.render()