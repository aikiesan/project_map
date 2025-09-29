"""
CP2B Maps V2 - Economic Analysis Module
Financial calculations, ROI analysis, and economic feasibility for biogas projects
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

logger = get_logger(__name__)


class EconomicAnalyzer:
    """
    Economic analysis engine for biogas projects
    Features: ROI calculation, feasibility analysis, financial projections
    """

    def __init__(self):
        """Initialize Economic Analyzer"""
        self.logger = get_logger(self.__class__.__name__)

        # Economic parameters (industry standards for Brazil)
        self.economic_factors = {
            'biogas_price_brl_m3': 0.85,  # BRL per m³ biogas
            'electricity_price_brl_kwh': 0.55,  # BRL per kWh
            'investment_cost_brl_m3_capacity': 1200,  # BRL per m³ daily capacity
            'operational_cost_percentage': 0.05,  # 5% of investment per year
            'carbon_credit_brl_ton': 45,  # BRL per ton CO2
            'plant_lifetime_years': 20,
            'discount_rate': 0.08  # 8% annual discount rate
        }

    def render_economic_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render comprehensive economic analysis

        Args:
            data: Municipality data with biogas calculations
            scenario_config: Scenario parameters

        Returns:
            Dictionary with economic analysis results
        """
        try:
            st.markdown("## 💰 Economic Feasibility Analysis")
            st.markdown("### Financial viability and investment return calculations")

            # Apply scenario adjustments
            adjusted_data = self._apply_economic_scenario(data, scenario_config)

            # Economic overview
            self._render_economic_overview(adjusted_data, scenario_config)

            # Feasibility charts
            feasibility_results = self._render_feasibility_charts(adjusted_data)

            # ROI Analysis
            roi_results = self._render_roi_analysis(adjusted_data, scenario_config)

            # Risk analysis
            risk_results = self._render_risk_analysis(adjusted_data, scenario_config)

            return {
                'adjusted_data': adjusted_data,
                'feasibility_results': feasibility_results,
                'roi_results': roi_results,
                'risk_results': risk_results,
                'economic_factors': self.economic_factors
            }

        except Exception as e:
            self.logger.error(f"Error in economic analysis: {e}")
            st.error("❌ Error performing economic analysis")
            return {}

    def _apply_economic_scenario(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
        """Apply economic scenario factors to data"""
        try:
            adjusted_data = data.copy()
            scenario_factors = self._get_scenario_factors(scenario_config.get('scenario_type', 'realistic'))

            # Apply scenario multipliers to biogas potential
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]

            for col in biogas_columns:
                if col in adjusted_data.columns:
                    adjusted_data[col] = adjusted_data[col] * scenario_factors.get('biogas_multiplier', 1.0)

            # Calculate economic metrics
            adjusted_data = self._calculate_economic_metrics(adjusted_data, scenario_factors)

            return adjusted_data

        except Exception as e:
            self.logger.error(f"Error applying economic scenario: {e}")
            return data

    def _get_scenario_factors(self, scenario_type: str) -> Dict[str, float]:
        """Get economic factors based on scenario type"""
        scenarios = {
            'conservative': {
                'biogas_multiplier': 0.7,
                'cost_multiplier': 1.3,
                'price_multiplier': 0.8,
                'efficiency_multiplier': 0.8
            },
            'realistic': {
                'biogas_multiplier': 1.0,
                'cost_multiplier': 1.0,
                'price_multiplier': 1.0,
                'efficiency_multiplier': 1.0
            },
            'optimistic': {
                'biogas_multiplier': 1.4,
                'cost_multiplier': 0.8,
                'price_multiplier': 1.2,
                'efficiency_multiplier': 1.2
            }
        }
        return scenarios.get(scenario_type, scenarios['realistic'])

    def _calculate_economic_metrics(self, data: pd.DataFrame, scenario_factors: Dict[str, float]) -> pd.DataFrame:
        """Calculate economic metrics for each municipality"""
        try:
            # Calculate total biogas potential
            biogas_columns = [col for col in data.columns if 'biogas' in col.lower() and 'nm_ano' in col]
            data['total_biogas_potential'] = data[biogas_columns].sum(axis=1)

            # Calculate revenue streams
            data['annual_biogas_revenue'] = (
                data['total_biogas_potential'] *
                self.economic_factors['biogas_price_brl_m3'] *
                scenario_factors.get('price_multiplier', 1.0)
            )

            # Calculate electricity revenue (assuming 50% efficiency)
            kwh_per_m3_biogas = 6.0  # Typical conversion
            data['annual_electricity_revenue'] = (
                data['total_biogas_potential'] *
                kwh_per_m3_biogas *
                self.economic_factors['electricity_price_brl_kwh'] *
                scenario_factors.get('price_multiplier', 1.0) *
                scenario_factors.get('efficiency_multiplier', 1.0)
            )

            # Calculate carbon credit revenue
            co2_reduction_kg_per_m3 = 2.3  # kg CO2 avoided per m³ biogas
            data['annual_carbon_revenue'] = (
                data['total_biogas_potential'] *
                co2_reduction_kg_per_m3 / 1000 *  # Convert to tons
                self.economic_factors['carbon_credit_brl_ton']
            )

            # Total annual revenue
            data['total_annual_revenue'] = (
                data['annual_biogas_revenue'] +
                data['annual_electricity_revenue'] +
                data['annual_carbon_revenue']
            )

            # Calculate investment costs
            data['investment_cost'] = (
                data['total_biogas_potential'] *
                self.economic_factors['investment_cost_brl_m3_capacity'] *
                scenario_factors.get('cost_multiplier', 1.0)
            )

            # Calculate annual operational costs
            data['annual_operational_cost'] = (
                data['investment_cost'] *
                self.economic_factors['operational_cost_percentage']
            )

            # Net annual cash flow
            data['net_annual_cash_flow'] = data['total_annual_revenue'] - data['annual_operational_cost']

            # Calculate ROI and payback
            data = self._calculate_financial_metrics(data)

            return data

        except Exception as e:
            self.logger.error(f"Error calculating economic metrics: {e}")
            return data

    def _calculate_financial_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced financial metrics"""
        try:
            # Simple payback period (years)
            data['payback_years'] = np.where(
                data['net_annual_cash_flow'] > 0,
                data['investment_cost'] / data['net_annual_cash_flow'],
                np.inf
            )

            # NPV calculation
            years = self.economic_factors['plant_lifetime_years']
            discount_rate = self.economic_factors['discount_rate']

            # Simplified NPV calculation
            npv_factor = sum(1 / (1 + discount_rate) ** year for year in range(1, years + 1))
            data['npv'] = (data['net_annual_cash_flow'] * npv_factor) - data['investment_cost']

            # IRR approximation (simplified)
            data['estimated_irr'] = np.where(
                data['payback_years'] <= years,
                1 / data['payback_years'],
                0
            )

            # Economic viability classification
            data['economic_viability'] = pd.cut(
                data['payback_years'],
                bins=[0, 5, 10, 15, np.inf],
                labels=['Excelente', 'Boa', 'Moderada', 'Baixa'],
                ordered=True
            )

            return data

        except Exception as e:
            self.logger.error(f"Error calculating financial metrics: {e}")
            return data

    def _render_economic_overview(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> None:
        """Render economic overview metrics"""
        try:
            st.markdown("#### 📊 Economic Overview")

            # Calculate summary metrics
            total_investment = data['investment_cost'].sum() if 'investment_cost' in data.columns else 0
            total_annual_revenue = data['total_annual_revenue'].sum() if 'total_annual_revenue' in data.columns else 0
            viable_municipalities = len(data[data['payback_years'] <= 10]) if 'payback_years' in data.columns else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Investment Required",
                    f"R$ {total_investment / 1e9:.1f}B" if total_investment >= 1e9 else f"R$ {total_investment / 1e6:.0f}M",
                    help="Total investment needed for all municipalities"
                )

            with col2:
                st.metric(
                    "Annual Revenue Potential",
                    f"R$ {total_annual_revenue / 1e6:.0f}M",
                    help="Total annual revenue across all municipalities"
                )

            with col3:
                st.metric(
                    "Economically Viable Cities",
                    f"{viable_municipalities}",
                    f"{viable_municipalities / len(data) * 100:.1f}% of total",
                    help="Cities with payback period ≤ 10 years"
                )

            with col4:
                avg_payback = data['payback_years'].replace([np.inf, -np.inf], np.nan).mean()
                st.metric(
                    "Average Payback Period",
                    f"{avg_payback:.1f} years" if not pd.isna(avg_payback) else "N/A",
                    help="Average payback period for viable projects"
                )

        except Exception as e:
            self.logger.error(f"Error rendering economic overview: {e}")

    def _render_feasibility_charts(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Render economic feasibility charts"""
        try:
            st.markdown("#### 📈 Economic Feasibility Charts")

            # Filter data for better visualization
            chart_data = data.copy()

            # Replace infinite values with NaN for plotting
            chart_data = chart_data.replace([np.inf, -np.inf], np.nan)

            col1, col2 = st.columns(2)

            with col1:
                # Payback period distribution
                fig_payback = px.histogram(
                    chart_data[chart_data['payback_years'] <= 30],  # Cap at 30 years for visualization
                    x='payback_years',
                    nbins=20,
                    title='Distribution of Payback Periods',
                    labels={'payback_years': 'Payback Period (years)', 'count': 'Number of Municipalities'},
                    color_discrete_sequence=['#1f77b4']
                )
                fig_payback.update_layout(height=400)
                st.plotly_chart(fig_payback, use_container_width=True)

            with col2:
                # Economic viability pie chart
                if 'economic_viability' in chart_data.columns:
                    viability_counts = chart_data['economic_viability'].value_counts()
                    fig_viability = px.pie(
                        values=viability_counts.values,
                        names=viability_counts.index,
                        title='Economic Viability Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_viability.update_layout(height=400)
                    st.plotly_chart(fig_viability, use_container_width=True)

            # Investment vs Revenue scatter plot
            fig_scatter = px.scatter(
                chart_data.dropna(subset=['investment_cost', 'total_annual_revenue']),
                x='investment_cost',
                y='total_annual_revenue',
                hover_data=['municipio', 'payback_years'] if 'municipio' in chart_data.columns else ['payback_years'],
                title='Investment vs Annual Revenue',
                labels={
                    'investment_cost': 'Investment Cost (BRL)',
                    'total_annual_revenue': 'Annual Revenue (BRL)'
                },
                color='payback_years',
                color_continuous_scale='RdYlGn_r',  # Red for high payback, green for low
                size='total_biogas_potential',
                size_max=20
            )
            fig_scatter.add_shape(
                type='line',
                x0=chart_data['investment_cost'].min(),
                y0=chart_data['investment_cost'].min() * 0.1,  # 10% return line
                x1=chart_data['investment_cost'].max(),
                y1=chart_data['investment_cost'].max() * 0.1,
                line=dict(color='red', dash='dash'),
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)

            return {
                'payback_distribution': fig_payback,
                'viability_distribution': fig_viability if 'economic_viability' in chart_data.columns else None,
                'investment_revenue_scatter': fig_scatter
            }

        except Exception as e:
            self.logger.error(f"Error rendering feasibility charts: {e}")
            return {}

    def _render_roi_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render Return on Investment analysis"""
        try:
            st.markdown("#### 💹 ROI and Financial Analysis")

            # Top 10 most profitable municipalities
            if 'npv' in data.columns and 'municipio' in data.columns:
                top_municipalities = data.nlargest(10, 'npv')[['municipio', 'npv', 'payback_years', 'total_annual_revenue']]

                st.markdown("##### 🏆 Top 10 Most Profitable Municipalities")

                # Format the data for display
                display_data = top_municipalities.copy()
                display_data['npv'] = display_data['npv'].apply(lambda x: f"R$ {x/1e6:.2f}M" if not pd.isna(x) else "N/A")
                display_data['payback_years'] = display_data['payback_years'].apply(lambda x: f"{x:.1f}" if not pd.isna(x) and x != np.inf else "N/A")
                display_data['total_annual_revenue'] = display_data['total_annual_revenue'].apply(lambda x: f"R$ {x/1e6:.2f}M" if not pd.isna(x) else "N/A")

                display_data.columns = ['Municipality', 'NPV', 'Payback (years)', 'Annual Revenue']
                st.dataframe(display_data, use_container_width=True)

                # NPV vs Investment chart
                fig_npv = px.scatter(
                    data.dropna(subset=['investment_cost', 'npv']),
                    x='investment_cost',
                    y='npv',
                    hover_data=['municipio', 'payback_years'],
                    title='Net Present Value vs Investment Cost',
                    labels={
                        'investment_cost': 'Investment Cost (BRL)',
                        'npv': 'Net Present Value (BRL)'
                    },
                    color='payback_years',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_npv.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
                fig_npv.update_layout(height=500)
                st.plotly_chart(fig_npv, use_container_width=True)

            return {
                'top_municipalities': top_municipalities if 'npv' in data.columns else pd.DataFrame(),
                'npv_chart': fig_npv if 'npv' in data.columns else None
            }

        except Exception as e:
            self.logger.error(f"Error rendering ROI analysis: {e}")
            return {}

    def _render_risk_analysis(self, data: pd.DataFrame, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Render risk analysis and sensitivity analysis"""
        try:
            st.markdown("#### ⚠️ Risk Analysis")

            # Risk categories based on payback periods and NPV
            risk_data = data.copy()

            # Define risk categories
            def categorize_risk(row):
                if pd.isna(row.get('payback_years')) or row.get('payback_years', np.inf) >= 15:
                    return 'Alto Risco'
                elif row.get('payback_years', np.inf) >= 10:
                    return 'Risco Moderado'
                elif row.get('payback_years', np.inf) >= 5:
                    return 'Baixo Risco'
                else:
                    return 'Muito Baixo Risco'

            risk_data['risk_category'] = risk_data.apply(categorize_risk, axis=1)

            # Risk distribution
            col1, col2 = st.columns(2)

            with col1:
                risk_counts = risk_data['risk_category'].value_counts()
                fig_risk = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title='Risk Distribution',
                    color_discrete_map={
                        'Muito Baixo Risco': '#2E8B57',
                        'Baixo Risco': '#32CD32',
                        'Risco Moderado': '#FFD700',
                        'Alto Risco': '#DC143C'
                    }
                )
                st.plotly_chart(fig_risk, use_container_width=True)

            with col2:
                # Risk metrics table
                risk_summary = risk_data.groupby('risk_category').agg({
                    'municipio': 'count',
                    'total_biogas_potential': 'sum',
                    'investment_cost': 'sum'
                }).round(2)

                risk_summary.columns = ['Municipalities', 'Total Biogas (m³/year)', 'Total Investment (BRL)']
                st.markdown("##### Risk Summary by Category")
                st.dataframe(risk_summary, use_container_width=True)

            # Sensitivity analysis
            st.markdown("##### 🔄 Sensitivity Analysis")
            sensitivity_params = ['Biogas Price', 'Investment Cost', 'Operational Cost', 'Efficiency']
            selected_param = st.selectbox("Parameter to analyze:", sensitivity_params)

            if selected_param:
                self._render_sensitivity_chart(data, selected_param)

            return {
                'risk_distribution': fig_risk,
                'risk_summary': risk_summary
            }

        except Exception as e:
            self.logger.error(f"Error rendering risk analysis: {e}")
            return {}

    def _render_sensitivity_chart(self, data: pd.DataFrame, parameter: str):
        """Render sensitivity analysis chart for a specific parameter"""
        try:
            # Create sensitivity ranges
            base_value = 1.0
            variations = np.arange(0.7, 1.4, 0.1)  # -30% to +30%

            # Calculate NPV for each variation (simplified)
            sensitivity_results = []

            for variation in variations:
                # Apply variation to the selected parameter
                modified_data = data.copy()

                if parameter == 'Biogas Price':
                    modified_data['total_annual_revenue'] *= variation
                elif parameter == 'Investment Cost':
                    modified_data['investment_cost'] *= variation
                elif parameter == 'Operational Cost':
                    modified_data['annual_operational_cost'] *= variation
                elif parameter == 'Efficiency':
                    modified_data['total_biogas_potential'] *= variation
                    modified_data['total_annual_revenue'] *= variation

                # Recalculate NPV
                modified_data['net_annual_cash_flow'] = modified_data['total_annual_revenue'] - modified_data['annual_operational_cost']

                years = self.economic_factors['plant_lifetime_years']
                discount_rate = self.economic_factors['discount_rate']
                npv_factor = sum(1 / (1 + discount_rate) ** year for year in range(1, years + 1))
                modified_data['npv'] = (modified_data['net_annual_cash_flow'] * npv_factor) - modified_data['investment_cost']

                avg_npv = modified_data['npv'].mean()
                sensitivity_results.append({
                    'variation': (variation - 1) * 100,  # Convert to percentage
                    'avg_npv': avg_npv
                })

            # Create sensitivity chart
            sensitivity_df = pd.DataFrame(sensitivity_results)

            fig_sensitivity = px.line(
                sensitivity_df,
                x='variation',
                y='avg_npv',
                title=f'Sensitivity Analysis: {parameter}',
                labels={
                    'variation': f'{parameter} Variation (%)',
                    'avg_npv': 'Average NPV (BRL)'
                }
            )
            fig_sensitivity.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
            fig_sensitivity.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="Base Case")

            st.plotly_chart(fig_sensitivity, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error rendering sensitivity chart: {e}")


# Factory function
def create_economic_analyzer() -> EconomicAnalyzer:
    """Create EconomicAnalyzer instance"""
    return EconomicAnalyzer()