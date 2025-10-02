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
        """Render metrics dashboard strip"""
        try:
            st.markdown("---")
            
            # Load municipality data
            municipalities_df = self.db_loader.load_municipalities_data()
            
            if municipalities_df is not None and len(municipalities_df) > 0:
                # Calculate state totals
                stats = self.calculator.get_state_totals(municipalities_df)
                db_status = "✅ Online" if self.db_loader.validate_database() else "❌ Error"
                
                # Prepare metrics data
                metrics_data = [
                    {
                        'icon': '🏘️',
                        'label': 'Municipalities',
                        'value': f"{stats.get('total_municipalities', 0):,}",
                        'delta': 'Complete Coverage'
                    },
                    {
                        'icon': '⛽',
                        'label': 'Daily Biogas',
                        'value': f"{stats.get('total_biogas_m3_day', 0):,.0f} m³",
                        'delta': 'Real-time Potential'
                    },
                    {
                        'icon': '⚡',
                        'label': 'Annual Energy',
                        'value': f"{stats.get('total_energy_mwh_year', 0):,.0f} MWh",
                        'delta': 'Clean Energy'
                    },
                    {
                        'icon': '🌱',
                        'label': 'CO₂ Reduction',
                        'value': f"{stats.get('total_co2_reduction_tons_year', 0):,.0f} tons",
                        'delta': 'Per Year'
                    },
                    {
                        'icon': '🖥️',
                        'label': 'System Status',
                        'value': db_status,
                        'delta': 'All Systems Operational'
                    }
                ]
                
                # Render using design system
                render_styled_metrics(metrics_data, columns=5)
            else:
                st.warning("⚠️ Unable to load municipality data. Please check the database connection.")
        
        except Exception as e:
            self.logger.error(f"Error rendering dashboard metrics: {e}", exc_info=True)
            st.error("⚠️ Failed to load metrics. Check logs for details.")

