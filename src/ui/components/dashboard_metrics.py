"""
CP2B Maps V2 - Dashboard Metrics Component
Handles metrics dashboard rendering
Single Responsibility: Display state-wide biogas statistics
"""

import streamlit as st
import pandas as pd
from typing import Optional

from src.utils.logging_config import get_logger
from src.data.loaders.database_loader import DatabaseLoader, get_database_loader
from src.core.biogas_calculator import BiogasCalculator, get_biogas_calculator
from src.ui.components.design_system import render_styled_metrics

logger = get_logger(__name__)


class DashboardMetrics:
    """
    Renders live dashboard metrics strip
    Shows state-wide biogas potential statistics
    """

    def __init__(self,
                 db_loader: Optional[DatabaseLoader] = None,
                 calculator: Optional[BiogasCalculator] = None):
        """
        Initialize dashboard metrics component
        
        Args:
            db_loader: DatabaseLoader instance (uses factory if None)
            calculator: BiogasCalculator instance (uses factory if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_loader = db_loader or get_database_loader()
        self.calculator = calculator or get_biogas_calculator()

    def render(self) -> None:
        """Render professional metrics dashboard"""
        try:
            # Load municipality data
            municipalities_df = self.db_loader.load_municipalities_data()

            if municipalities_df is not None and len(municipalities_df) > 0:
                # Calculate state totals
                stats = self.calculator.get_state_totals(municipalities_df)
                db_status = "Online" if self.db_loader.validate_database() else "Offline"

                # Professional metrics section with clean design
                st.markdown("""
                <div style='background: linear-gradient(135deg, #2E8B57 0%, #228B22 100%);
                            color: white; padding: 2rem; margin: 2rem 0 1rem 0;
                            border-radius: 12px; box-shadow: 0 4px 20px rgba(46,139,87,0.2);'>
                    <h3 style='margin: 0 0 1.5rem 0; font-size: 1.3rem; font-weight: 600;
                               text-align: center; font-family: "Montserrat", sans-serif;'>
                        São Paulo State Biogas Analysis Summary
                    </h3>
                    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;'>
                        <div style='text-align: center;'>
                            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.3rem;'>
                                {municipalities:,}
                            </div>
                            <div style='font-size: 0.9rem; opacity: 0.95;'>Municipalities Analyzed</div>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.3rem;'>
                                {biogas:,.0f} m³
                            </div>
                            <div style='font-size: 0.9rem; opacity: 0.95;'>Daily Biogas Potential</div>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.3rem;'>
                                {energy:,.0f} MWh
                            </div>
                            <div style='font-size: 0.9rem; opacity: 0.95;'>Annual Energy Generation</div>
                        </div>
                        <div style='text-align: center;'>
                            <div style='font-size: 2rem; font-weight: 700; margin-bottom: 0.3rem;'>
                                {co2:,.0f} t
                            </div>
                            <div style='font-size: 0.9rem; opacity: 0.95;'>CO₂ Reduction Potential</div>
                        </div>
                    </div>
                    <div style='text-align: center; margin-top: 1rem; padding-top: 1rem;
                               border-top: 1px solid rgba(255,255,255,0.2);'>
                        <span style='font-size: 0.85rem; opacity: 0.9;'>System Status: {status}</span>
                    </div>
                </div>
                """.format(
                    municipalities=stats.get('total_municipalities', 0),
                    biogas=stats.get('total_biogas_m3_day', 0),
                    energy=stats.get('total_energy_mwh_year', 0),
                    co2=stats.get('total_co2_reduction_tons_year', 0),
                    status=db_status
                ), unsafe_allow_html=True)
            else:
                st.warning("Unable to load municipality data. Please check the database connection.")

        except Exception as e:
            self.logger.error(f"Error rendering dashboard metrics: {e}", exc_info=True)
            st.error("Failed to load metrics. Check logs for details.")

