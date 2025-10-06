"""
CP2B Maps - UI Utilities Module
Shared utilities for UI components
"""

from .chart_helpers import (
    ChartGenerator,
    ChartStyles,
    get_chart_generator,
    create_biogas_pie_chart,
    create_municipality_ranking,
    create_standard_scatter,
    create_correlation_matrix,
    display_summary_metrics
)

__all__ = [
    'ChartGenerator',
    'ChartStyles',
    'get_chart_generator',
    'create_biogas_pie_chart',
    'create_municipality_ranking',
    'create_standard_scatter',
    'create_correlation_matrix',
    'display_summary_metrics'
]