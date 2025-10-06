"""
Analysis and Charts Module for CP2B Maps
Enhanced chart library ported from V1 with improvements
Professional data visualization for biogas analysis
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from typing import Optional, Dict, List, Any

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_top_municipalities_chart(df: pd.DataFrame, display_col: str, title: str = "", limit: int = 15) -> Optional[go.Figure]:
    """
    Create top municipalities ranking chart

    Args:
        df: DataFrame with municipality data
        display_col: Column to rank by
        title: Chart title
        limit: Number of top municipalities to show

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or display_col not in df.columns:
            return None

        # Get municipality name column (flexible naming)
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'
        if name_col not in df.columns:
            logger.warning("Municipality name column not found")
            return None

        top_data = df.nlargest(limit, display_col).copy()

        fig = px.bar(
            top_data,
            x=name_col,
            y=display_col,
            title=f'🏆 Top {limit} Municípios - {title}' if title else f'🏆 Top {limit} Municípios',
            labels={display_col: 'Potencial (m³/ano)', name_col: 'Município'},
            color=display_col,
            color_continuous_scale='Greens',  # V1 green theme
            text_auto='.2s'
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=450,
            showlegend=False,
            xaxis_title="Município",
            yaxis_title="Potencial (m³/ano)",
            font=dict(size=12),
            hovermode='x unified'
        )

        fig.update_traces(textposition='outside')

        return fig

    except Exception as e:
        logger.error(f"Error creating top municipalities chart: {e}")
        return None


def create_distribution_histogram(df: pd.DataFrame, display_col: str, title: str = "") -> Optional[go.Figure]:
    """
    Create distribution histogram with statistics

    Args:
        df: DataFrame with data
        display_col: Column to analyze
        title: Chart title

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or display_col not in df.columns:
            return None

        data = df[display_col].dropna()

        if len(data) == 0:
            return None

        fig = px.histogram(
            df,
            x=display_col,
            title=f'📊 Distribuição - {title}' if title else '📊 Distribuição de Valores',
            nbins=30,
            labels={display_col: 'Potencial (m³/ano)'},
            color_discrete_sequence=['#2E8B57'],  # V1 green
            marginal="box"  # Add box plot for statistics
        )

        # Add mean line
        mean_val = data.mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {mean_val:,.0f}",
            annotation_position="top"
        )

        # Add median line
        median_val = data.median()
        fig.add_vline(
            x=median_val,
            line_dash="dot",
            line_color="blue",
            annotation_text=f"Mediana: {median_val:,.0f}",
            annotation_position="bottom"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Potencial (m³/ano)",
            yaxis_title="Frequência (Número de Municípios)",
            showlegend=False
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating distribution histogram: {e}")
        return None


def create_box_plot_analysis(df: pd.DataFrame, display_col: str, group_col: Optional[str] = None, title: str = "") -> Optional[go.Figure]:
    """
    Create box plot for outlier detection and distribution analysis

    Args:
        df: DataFrame with data
        display_col: Column to analyze
        group_col: Optional grouping column (e.g., region)
        title: Chart title

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or display_col not in df.columns:
            return None

        if group_col and group_col in df.columns:
            # Grouped box plot
            fig = px.box(
                df,
                x=group_col,
                y=display_col,
                title=f'📦 Análise de Distribuição por {group_col} - {title}' if title else f'📦 Box Plot - {group_col}',
                labels={display_col: 'Potencial (m³/ano)', group_col: 'Grupo'},
                color=group_col,
                points="outliers"  # Show only outliers as points
            )
            fig.update_layout(xaxis_tickangle=-45)
        else:
            # Single box plot
            fig = px.box(
                df,
                y=display_col,
                title=f'📦 Análise de Outliers - {title}' if title else '📦 Box Plot',
                labels={display_col: 'Potencial (m³/ano)'},
                points="all",  # Show all points
                color_discrete_sequence=['#2E8B57']
            )

        fig.update_layout(
            height=450,
            yaxis_title="Potencial (m³/ano)",
            showlegend=True if group_col else False
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating box plot: {e}")
        return None


def create_scatter_correlation(df: pd.DataFrame, x_col: str, y_col: str, size_col: Optional[str] = None, title: str = "") -> Optional[go.Figure]:
    """
    Create scatter plot for correlation analysis

    Args:
        df: DataFrame with data
        x_col: Column for x-axis
        y_col: Column for y-axis
        size_col: Optional column for bubble size
        title: Chart title

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or x_col not in df.columns or y_col not in df.columns:
            return None

        # Get municipality name column
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'
        hover_name = name_col if name_col in df.columns else None

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            size=size_col if size_col and size_col in df.columns else None,
            color=y_col,
            hover_name=hover_name,
            title=f'🔍 Análise de Correlação - {title}' if title else '🔍 Scatter Plot',
            labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()},
            color_continuous_scale='Viridis',
            size_max=40,
            trendline="ols"  # Add trend line
        )

        fig.update_layout(
            height=450,
            showlegend=False
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        return None


def create_municipality_ranking_table(df: pd.DataFrame, display_col: str, limit: int = 20) -> Optional[pd.DataFrame]:
    """
    Create municipality ranking table with key metrics

    Args:
        df: DataFrame with data
        display_col: Column to rank by
        limit: Number of municipalities to include

    Returns:
        Formatted DataFrame or None if error
    """
    try:
        if df.empty or display_col not in df.columns:
            return None

        # Get municipality name column
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'
        pop_col = 'population' if 'population' in df.columns else 'populacao'

        if name_col not in df.columns:
            return None

        ranking_df = df.nlargest(limit, display_col)[[name_col, display_col]].copy()

        # Add ranking position
        ranking_df.insert(0, 'Posição', range(1, len(ranking_df) + 1))

        # Add per capita if population available
        if pop_col in df.columns:
            ranking_df['Per Capita'] = ranking_df.apply(
                lambda row: df.loc[df[name_col] == row[name_col], display_col].values[0] /
                           df.loc[df[name_col] == row[name_col], pop_col].values[0]
                if df.loc[df[name_col] == row[name_col], pop_col].values[0] > 0 else 0,
                axis=1
            )

        # Format column names
        ranking_df.columns = [
            col.replace('_', ' ').title() if col not in ['Posição', 'Per Capita'] else col
            for col in ranking_df.columns
        ]

        return ranking_df

    except Exception as e:
        logger.error(f"Error creating ranking table: {e}")
        return None


def create_summary_statistics_table(df: pd.DataFrame, display_col: str) -> Optional[pd.DataFrame]:
    """
    Create summary statistics table

    Args:
        df: DataFrame with data
        display_col: Column to analyze

    Returns:
        Statistics DataFrame or None if error
    """
    try:
        if df.empty or display_col not in df.columns:
            return None

        data = df[display_col].dropna()

        if len(data) == 0:
            return None

        stats = {
            '📊 Contagem': f"{len(data):,}",
            '📈 Média': f"{data.mean():,.2f}",
            '🎯 Mediana': f"{data.median():,.2f}",
            '📉 Desvio Padrão': f"{data.std():,.2f}",
            '⬇️ Mínimo': f"{data.min():,.2f}",
            '⬆️ Máximo': f"{data.max():,.2f}",
            '◼️ Q1 (25%)': f"{data.quantile(0.25):,.2f}",
            '◼️ Q3 (75%)': f"{data.quantile(0.75):,.2f}",
            '📏 Amplitude': f"{(data.max() - data.min()):,.2f}"
        }

        return pd.DataFrame(list(stats.items()), columns=['Estatística', 'Valor'])

    except Exception as e:
        logger.error(f"Error creating statistics table: {e}")
        return None


def create_regional_comparison_pie(df: pd.DataFrame, display_col: str, region_col: str = 'region') -> Optional[go.Figure]:
    """
    Create regional comparison pie chart

    Args:
        df: DataFrame with data
        display_col: Column to sum by region
        region_col: Region column name

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or display_col not in df.columns or region_col not in df.columns:
            return None

        regional_data = df.groupby(region_col)[display_col].sum().reset_index()
        regional_data = regional_data.sort_values(display_col, ascending=False)

        fig = px.pie(
            regional_data,
            values=display_col,
            names=region_col,
            title='🗺️ Distribuição Regional do Potencial',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.3  # Donut chart
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Potencial: %{value:,.0f} m³/ano<br>Percentual: %{percent}<extra></extra>'
        )

        fig.update_layout(height=450)

        return fig

    except Exception as e:
        logger.error(f"Error creating regional pie chart: {e}")
        return None


def create_multi_source_comparison_bar(df: pd.DataFrame, source_columns: Dict[str, str], municipality_name: Optional[str] = None) -> Optional[go.Figure]:
    """
    Create comparison chart for different biogas sources

    Args:
        df: DataFrame with data
        source_columns: Dictionary mapping column names to labels
        municipality_name: Optional municipality to filter by

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty:
            return None

        # Get municipality name column
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'

        # Filter by municipality if specified
        if municipality_name and name_col in df.columns:
            df_filtered = df[df[name_col] == municipality_name]
            title = f'🌾 Composição por Fonte - {municipality_name}'
        else:
            df_filtered = df
            title = '🌾 Composição Total por Fonte - Estado de SP'

        if df_filtered.empty:
            return None

        # Calculate totals for each source
        source_totals = {}
        for col, label in source_columns.items():
            if col in df_filtered.columns:
                total = df_filtered[col].sum()
                if total > 0:
                    source_totals[label] = total

        if not source_totals:
            return None

        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(source_totals.keys()),
                y=list(source_totals.values()),
                marker_color='#2E8B57',
                text=[f"{v:,.0f}" for v in source_totals.values()],
                textposition='auto'
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title="Fonte de Biogás",
            yaxis_title="Potencial (m³/ano)",
            height=450,
            showlegend=False,
            xaxis_tickangle=-45
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating multi-source comparison: {e}")
        return None


def create_comparative_municipalities_chart(df: pd.DataFrame, municipality_list: List[str], metric_columns: List[str]) -> Optional[go.Figure]:
    """
    Create comparative bar chart for selected municipalities across multiple metrics

    Args:
        df: DataFrame with data
        municipality_list: List of municipality names to compare
        metric_columns: List of metric columns to compare

    Returns:
        Plotly figure or None if error
    """
    try:
        if df.empty or not municipality_list or not metric_columns:
            return None

        # Get municipality name column
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'

        if name_col not in df.columns:
            return None

        # Filter data
        df_filtered = df[df[name_col].isin(municipality_list)].copy()

        if df_filtered.empty:
            return None

        # Create grouped bar chart
        fig = go.Figure()

        for metric in metric_columns:
            if metric in df_filtered.columns:
                fig.add_trace(go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=df_filtered[name_col],
                    y=df_filtered[metric],
                    text=df_filtered[metric].apply(lambda x: f"{x:,.0f}"),
                    textposition='auto'
                ))

        fig.update_layout(
            title='📊 Comparação entre Municípios Selecionados',
            xaxis_title="Município",
            yaxis_title="Valor",
            barmode='group',
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis_tickangle=-45
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating comparative municipalities chart: {e}")
        return None
