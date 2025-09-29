"""
CP2B Maps V2 - Chart Utilities Module
Shared chart generation utilities to eliminate code duplication
Standardized visualization components for consistent styling
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple, Union
import datetime

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ChartStyles:
    """Standard chart styling constants"""

    # Color palettes
    PRIMARY_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    BIOGAS_COLORS = ['#2E8B57', '#32CD32', '#FFD700', '#FF6347', '#4169E1']
    VIABILITY_COLORS = {
        'Excelente': '#2E8B57',
        'Boa': '#32CD32',
        'Moderada': '#FFD700',
        'Baixa': '#DC143C',
        'High Priority': '#2E8B57',
        'Medium Priority': '#FFD700',
        'Low Priority': '#DC143C'
    }

    # Layout settings
    DEFAULT_HEIGHT = 400
    LARGE_HEIGHT = 600
    SMALL_HEIGHT = 300

    # Font settings
    TITLE_FONT = dict(size=16, family="Arial, sans-serif")
    AXIS_FONT = dict(size=12, family="Arial, sans-serif")
    LEGEND_FONT = dict(size=10, family="Arial, sans-serif")


class ChartGenerator:
    """
    Professional chart generation utilities with consistent styling
    Features: Standardized charts, accessibility support, export functionality
    """

    def __init__(self):
        """Initialize Chart Generator"""
        self.logger = get_logger(self.__class__.__name__)
        self.styles = ChartStyles()

    def create_biogas_distribution_pie(self,
                                     data: pd.DataFrame,
                                     value_column: str,
                                     name_column: str,
                                     title: str = "Biogas Distribution",
                                     height: int = None) -> go.Figure:
        """
        Create standardized pie chart for biogas distribution

        Args:
            data: DataFrame with data
            value_column: Column name for values
            name_column: Column name for labels
            title: Chart title
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.DEFAULT_HEIGHT

            # Filter out zero values
            chart_data = data[data[value_column] > 0].copy()

            if len(chart_data) == 0:
                return self._create_empty_chart("No data available for pie chart")

            fig = px.pie(
                chart_data,
                values=value_column,
                names=name_column,
                title=title,
                color_discrete_sequence=self.styles.BIOGAS_COLORS
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
            )

            fig.update_layout(
                height=height,
                title_font=self.styles.TITLE_FONT,
                legend=dict(font=self.styles.LEGEND_FONT),
                showlegend=True
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating pie chart: {e}")
            return self._create_error_chart("Error creating pie chart")

    def create_municipality_ranking_bar(self,
                                      data: pd.DataFrame,
                                      value_column: str,
                                      name_column: str = 'municipio',
                                      title: str = "Municipality Ranking",
                                      top_n: int = 15,
                                      color_column: Optional[str] = None,
                                      height: int = None) -> go.Figure:
        """
        Create standardized bar chart for municipality rankings

        Args:
            data: DataFrame with municipality data
            value_column: Column for ranking values
            name_column: Column for municipality names
            title: Chart title
            top_n: Number of top municipalities to show
            color_column: Optional column for color coding
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.DEFAULT_HEIGHT

            # Get top N municipalities
            top_data = data.nlargest(top_n, value_column)

            if len(top_data) == 0:
                return self._create_empty_chart("No data available for ranking")

            # Create bar chart
            if color_column and color_column in top_data.columns:
                fig = px.bar(
                    top_data,
                    x=value_column,
                    y=name_column,
                    orientation='h',
                    title=title,
                    color=color_column,
                    color_discrete_map=self.styles.VIABILITY_COLORS
                )
            else:
                fig = px.bar(
                    top_data,
                    x=value_column,
                    y=name_column,
                    orientation='h',
                    title=title,
                    color_discrete_sequence=[self.styles.PRIMARY_COLORS[0]]
                )

            # Reverse y-axis to show highest values at top
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=height,
                title_font=self.styles.TITLE_FONT,
                xaxis_title=self._format_column_name(value_column),
                yaxis_title="Municipality"
            )

            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>'
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating bar chart: {e}")
            return self._create_error_chart("Error creating bar chart")

    def create_scatter_plot(self,
                          data: pd.DataFrame,
                          x_column: str,
                          y_column: str,
                          title: str = "Scatter Plot",
                          color_column: Optional[str] = None,
                          size_column: Optional[str] = None,
                          hover_data: Optional[List[str]] = None,
                          height: int = None) -> go.Figure:
        """
        Create standardized scatter plot

        Args:
            data: DataFrame with data
            x_column: X-axis column
            y_column: Y-axis column
            title: Chart title
            color_column: Optional column for color coding
            size_column: Optional column for bubble size
            hover_data: Additional columns for hover info
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.DEFAULT_HEIGHT

            # Filter out null values
            plot_data = data.dropna(subset=[x_column, y_column])

            if len(plot_data) == 0:
                return self._create_empty_chart("No valid data for scatter plot")

            # Create scatter plot
            fig = px.scatter(
                plot_data,
                x=x_column,
                y=y_column,
                title=title,
                color=color_column,
                size=size_column,
                hover_data=hover_data,
                color_discrete_sequence=self.styles.PRIMARY_COLORS
            )

            fig.update_layout(
                height=height,
                title_font=self.styles.TITLE_FONT,
                xaxis_title=self._format_column_name(x_column),
                yaxis_title=self._format_column_name(y_column)
            )

            fig.update_traces(
                marker=dict(line=dict(width=1, color='white')),
                hovertemplate='<b>%{hovertext}</b><br>%{xaxis.title.text}: %{x}<br>%{yaxis.title.text}: %{y}<extra></extra>'
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating scatter plot: {e}")
            return self._create_error_chart("Error creating scatter plot")

    def create_time_series_chart(self,
                               data: pd.DataFrame,
                               x_column: str,
                               y_column: str,
                               title: str = "Time Series",
                               line_columns: Optional[List[str]] = None,
                               height: int = None) -> go.Figure:
        """
        Create standardized time series chart

        Args:
            data: DataFrame with time series data
            x_column: Time column
            y_column: Value column
            title: Chart title
            line_columns: Additional columns for multiple lines
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.DEFAULT_HEIGHT

            fig = go.Figure()

            # Add main line
            fig.add_trace(go.Scatter(
                x=data[x_column],
                y=data[y_column],
                mode='lines+markers',
                name=self._format_column_name(y_column),
                line=dict(color=self.styles.PRIMARY_COLORS[0], width=3),
                marker=dict(size=6)
            ))

            # Add additional lines if specified
            if line_columns:
                for i, col in enumerate(line_columns):
                    if col in data.columns:
                        color_idx = (i + 1) % len(self.styles.PRIMARY_COLORS)
                        fig.add_trace(go.Scatter(
                            x=data[x_column],
                            y=data[col],
                            mode='lines+markers',
                            name=self._format_column_name(col),
                            line=dict(color=self.styles.PRIMARY_COLORS[color_idx], width=2),
                            marker=dict(size=4)
                        ))

            fig.update_layout(
                title=title,
                height=height,
                title_font=self.styles.TITLE_FONT,
                xaxis_title=self._format_column_name(x_column),
                yaxis_title="Value",
                hovermode='x unified'
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating time series chart: {e}")
            return self._create_error_chart("Error creating time series chart")

    def create_histogram(self,
                       data: pd.DataFrame,
                       column: str,
                       title: str = "Distribution",
                       bins: int = 20,
                       height: int = None) -> go.Figure:
        """
        Create standardized histogram

        Args:
            data: DataFrame with data
            column: Column to plot
            title: Chart title
            bins: Number of bins
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.DEFAULT_HEIGHT

            # Filter out null and infinite values
            plot_data = data[column].replace([np.inf, -np.inf], np.nan).dropna()

            if len(plot_data) == 0:
                return self._create_empty_chart("No valid data for histogram")

            fig = px.histogram(
                x=plot_data,
                nbins=bins,
                title=title,
                color_discrete_sequence=[self.styles.PRIMARY_COLORS[0]]
            )

            fig.update_layout(
                height=height,
                title_font=self.styles.TITLE_FONT,
                xaxis_title=self._format_column_name(column),
                yaxis_title="Count",
                bargap=0.1
            )

            fig.update_traces(
                hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating histogram: {e}")
            return self._create_error_chart("Error creating histogram")

    def create_multi_metric_chart(self,
                                data: pd.DataFrame,
                                metrics: Dict[str, str],
                                title: str = "Multi-Metric Analysis",
                                chart_type: str = "bar",
                                top_n: int = 10) -> go.Figure:
        """
        Create multi-metric comparison chart

        Args:
            data: DataFrame with data
            metrics: Dictionary of {metric_name: column_name}
            title: Chart title
            chart_type: Type of chart ('bar', 'line', 'area')
            top_n: Number of top entries to show

        Returns:
            Plotly figure object
        """
        try:
            if len(metrics) == 0:
                return self._create_empty_chart("No metrics specified")

            # Create subplots
            fig = make_subplots(
                rows=len(metrics),
                cols=1,
                subplot_titles=list(metrics.keys()),
                vertical_spacing=0.08
            )

            # Get top municipalities for consistency
            first_metric = list(metrics.values())[0]
            top_data = data.nlargest(top_n, first_metric)

            if len(top_data) == 0:
                return self._create_empty_chart("No data available for multi-metric chart")

            for i, (metric_name, column) in enumerate(metrics.items(), 1):
                if column not in top_data.columns:
                    continue

                if chart_type == "bar":
                    trace = go.Bar(
                        x=top_data.get('municipio', top_data.index),
                        y=top_data[column],
                        name=metric_name,
                        marker_color=self.styles.PRIMARY_COLORS[i-1 % len(self.styles.PRIMARY_COLORS)]
                    )
                elif chart_type == "line":
                    trace = go.Scatter(
                        x=top_data.get('municipio', top_data.index),
                        y=top_data[column],
                        mode='lines+markers',
                        name=metric_name,
                        line=dict(color=self.styles.PRIMARY_COLORS[i-1 % len(self.styles.PRIMARY_COLORS)])
                    )
                else:  # area
                    trace = go.Scatter(
                        x=top_data.get('municipio', top_data.index),
                        y=top_data[column],
                        fill='tonexty' if i > 1 else 'tozeroy',
                        name=metric_name,
                        line=dict(color=self.styles.PRIMARY_COLORS[i-1 % len(self.styles.PRIMARY_COLORS)])
                    )

                fig.add_trace(trace, row=i, col=1)

            fig.update_layout(
                title=title,
                height=len(metrics) * 250,
                title_font=self.styles.TITLE_FONT,
                showlegend=False
            )

            # Update x-axis for better readability
            fig.update_xaxes(tickangle=45)

            return fig

        except Exception as e:
            self.logger.error(f"Error creating multi-metric chart: {e}")
            return self._create_error_chart("Error creating multi-metric chart")

    def create_correlation_heatmap(self,
                                 data: pd.DataFrame,
                                 columns: List[str],
                                 title: str = "Correlation Matrix",
                                 height: int = None) -> go.Figure:
        """
        Create correlation heatmap

        Args:
            data: DataFrame with data
            columns: Columns to include in correlation
            title: Chart title
            height: Chart height

        Returns:
            Plotly figure object
        """
        try:
            height = height or self.styles.LARGE_HEIGHT

            # Filter columns that exist in data
            valid_columns = [col for col in columns if col in data.columns]

            if len(valid_columns) < 2:
                return self._create_empty_chart("Need at least 2 valid columns for correlation")

            # Calculate correlation matrix
            corr_data = data[valid_columns].corr()

            fig = go.Figure(data=go.Heatmap(
                z=corr_data.values,
                x=corr_data.columns,
                y=corr_data.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_data.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.2f}<extra></extra>'
            ))

            fig.update_layout(
                title=title,
                height=height,
                title_font=self.styles.TITLE_FONT,
                xaxis_title="Variables",
                yaxis_title="Variables"
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating correlation heatmap: {e}")
            return self._create_error_chart("Error creating correlation heatmap")

    def create_gauge_chart(self,
                         value: float,
                         title: str = "Performance Gauge",
                         max_value: float = 100,
                         thresholds: Optional[Dict[str, float]] = None) -> go.Figure:
        """
        Create gauge chart for KPI display

        Args:
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            thresholds: Dictionary of threshold names and values

        Returns:
            Plotly figure object
        """
        try:
            if thresholds is None:
                thresholds = {'Poor': 30, 'Good': 70, 'Excellent': 90}

            # Create gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': title},
                delta={'reference': max_value * 0.8},
                gauge={
                    'axis': {'range': [None, max_value]},
                    'bar': {'color': self._get_gauge_color(value, thresholds, max_value)},
                    'steps': self._create_gauge_steps(thresholds, max_value),
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_value * 0.9
                    }
                }
            ))

            fig.update_layout(
                height=300,
                title_font=self.styles.TITLE_FONT
            )

            return fig

        except Exception as e:
            self.logger.error(f"Error creating gauge chart: {e}")
            return self._create_error_chart("Error creating gauge chart")

    def create_summary_metrics_display(self,
                                     metrics: Dict[str, Any],
                                     title: str = "Summary Metrics") -> None:
        """
        Create summary metrics display using Streamlit

        Args:
            metrics: Dictionary of metric_name: {value, delta, help}
            title: Section title
        """
        try:
            st.markdown(f"#### {title}")

            # Calculate number of columns
            num_metrics = len(metrics)
            cols = st.columns(min(num_metrics, 4))

            for i, (metric_name, metric_data) in enumerate(metrics.items()):
                col_idx = i % 4
                with cols[col_idx]:
                    if isinstance(metric_data, dict):
                        value = metric_data.get('value', 0)
                        delta = metric_data.get('delta')
                        help_text = metric_data.get('help', '')
                    else:
                        value = metric_data
                        delta = None
                        help_text = ''

                    # Format value appropriately
                    formatted_value = self._format_metric_value(value)

                    st.metric(
                        label=metric_name,
                        value=formatted_value,
                        delta=delta,
                        help=help_text
                    )

        except Exception as e:
            self.logger.error(f"Error creating summary metrics: {e}")
            st.error("Error displaying summary metrics")

    # Helper methods

    def _format_column_name(self, column: str) -> str:
        """Format column name for display"""
        return column.replace('_', ' ').title()

    def _format_metric_value(self, value: Union[int, float, str]) -> str:
        """Format metric value for display"""
        try:
            if isinstance(value, (int, float)):
                if value >= 1e9:
                    return f"{value / 1e9:.1f}B"
                elif value >= 1e6:
                    return f"{value / 1e6:.1f}M"
                elif value >= 1e3:
                    return f"{value / 1e3:.1f}K"
                else:
                    return f"{value:.0f}" if value == int(value) else f"{value:.2f}"
            else:
                return str(value)
        except Exception:
            return str(value)

    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            height=self.styles.DEFAULT_HEIGHT,
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return fig

    def _create_error_chart(self, message: str) -> go.Figure:
        """Create error chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ {message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            height=self.styles.DEFAULT_HEIGHT,
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return fig

    def _get_gauge_color(self, value: float, thresholds: Dict[str, float], max_value: float) -> str:
        """Get color for gauge based on value and thresholds"""
        percentage = (value / max_value) * 100

        if percentage >= thresholds.get('Excellent', 90):
            return "green"
        elif percentage >= thresholds.get('Good', 70):
            return "yellow"
        else:
            return "red"

    def _create_gauge_steps(self, thresholds: Dict[str, float], max_value: float) -> List[Dict[str, Any]]:
        """Create gauge steps based on thresholds"""
        steps = []
        sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1])

        for i, (name, value) in enumerate(sorted_thresholds):
            if i == 0:
                steps.append({'range': [0, value], 'color': 'lightgray'})
            else:
                prev_value = sorted_thresholds[i-1][1]
                steps.append({'range': [prev_value, value], 'color': 'gray'})

        # Add final step
        last_threshold = sorted_thresholds[-1][1]
        if last_threshold < max_value:
            steps.append({'range': [last_threshold, max_value], 'color': 'lightgreen'})

        return steps


# Factory function
@st.cache_resource
def get_chart_generator() -> ChartGenerator:
    """Get cached ChartGenerator instance"""
    return ChartGenerator()


# Convenience functions for common charts
def create_biogas_pie_chart(data: pd.DataFrame, **kwargs) -> go.Figure:
    """Convenience function for biogas pie charts"""
    chart_gen = get_chart_generator()
    return chart_gen.create_biogas_distribution_pie(data, **kwargs)


def create_municipality_ranking(data: pd.DataFrame, **kwargs) -> go.Figure:
    """Convenience function for municipality rankings"""
    chart_gen = get_chart_generator()
    return chart_gen.create_municipality_ranking_bar(data, **kwargs)


def create_standard_scatter(data: pd.DataFrame, **kwargs) -> go.Figure:
    """Convenience function for scatter plots"""
    chart_gen = get_chart_generator()
    return chart_gen.create_scatter_plot(data, **kwargs)


def create_correlation_matrix(data: pd.DataFrame, **kwargs) -> go.Figure:
    """Convenience function for correlation heatmaps"""
    chart_gen = get_chart_generator()
    return chart_gen.create_correlation_heatmap(data, **kwargs)


def display_summary_metrics(metrics: Dict[str, Any], **kwargs) -> None:
    """Convenience function for summary metrics"""
    chart_gen = get_chart_generator()
    return chart_gen.create_summary_metrics_display(metrics, **kwargs)