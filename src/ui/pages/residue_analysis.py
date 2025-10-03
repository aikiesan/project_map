"""
CP2B Maps V2 - Residue Analysis Page
Comparative residue type analysis with regional patterns
SOLID: Single Responsibility - Analyze and compare different residue types
DRY: Reuses existing chart components from analysis_charts.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import get_database_loader
from src.data.loaders.database_loader import DatabaseLoader

# Reuse existing components (DRY principle)
from src.ui.components.design_system import render_section_header, render_styled_metrics
from src.ui.components.analysis_charts import (
    create_top_municipalities_chart,
    create_regional_comparison_pie,
    create_summary_statistics_table
)
from src.ui.components.academic_footer import render_compact_academic_footer
from src.data.references.scientific_references import render_reference_button

logger = get_logger(__name__)


class ResidueAnalysisPage:
    """
    Residue type comparison and analysis page
    Follows existing page pattern: class with render() method
    """

    def __init__(self, db_loader: DatabaseLoader = None):
        """
        Initialize Residue Analysis page with dependency injection

        Args:
            db_loader: DatabaseLoader instance (uses default if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing ResidueAnalysisPage")

        # Inject dependencies
        self.database_loader = db_loader if db_loader is not None else get_database_loader()

    def render(self) -> None:
        """Main render method following existing page interface"""
        try:
            # Section header (reusing design_system)
            render_section_header(
                "📊 Análise Comparativa de Resíduos",
                icon="🔬",
                description="Comparação entre tipos de resíduos e análise de potencial regional"
            )

            # Load data
            df = self.database_loader.load_municipalities_data()
            if df is None or len(df) == 0:
                st.error("⚠️ Não foi possível carregar os dados")
                return

            # Four analysis tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Comparação de Tipos",
                "🗺️ Análise Regional",
                "💼 Portfolio de Resíduos",
                "📅 Disponibilidade Sazonal"
            ])

            with tab1:
                self._render_type_comparison(df)

            with tab2:
                self._render_regional_analysis(df)

            with tab3:
                self._render_portfolio_analysis(df)

            with tab4:
                self._render_seasonal_analysis(df)

            # Academic footer (reusing component)
            render_compact_academic_footer("_residue_analysis")

        except Exception as e:
            self.logger.error(f"Error rendering residue analysis page: {e}", exc_info=True)
            st.error("⚠️ Erro ao carregar análise de resíduos")

    def _render_type_comparison(self, df: pd.DataFrame) -> None:
        """Compare agricultural vs livestock vs urban residues"""
        st.markdown("### 📊 Comparação entre Tipos de Resíduos")

        # Calculate totals by type
        agricultural_total = df['agricultural_biogas_m3_year'].sum() if 'agricultural_biogas_m3_year' in df.columns else 0
        livestock_total = df['livestock_biogas_m3_year'].sum() if 'livestock_biogas_m3_year' in df.columns else 0
        urban_total = df['urban_biogas_m3_year'].sum() if 'urban_biogas_m3_year' in df.columns else 0
        total_biogas = agricultural_total + livestock_total + urban_total

        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌾 Agrícola", f"{agricultural_total / 1e9:.2f} Bi m³/ano")
        with col2:
            st.metric("🐄 Pecuário", f"{livestock_total / 1e9:.2f} Bi m³/ano")
        with col3:
            st.metric("🏙️ Urbano", f"{urban_total / 1e9:.2f} Bi m³/ano")
        with col4:
            st.metric("📈 Total", f"{total_biogas / 1e9:.2f} Bi m³/ano")

        st.markdown("---")

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            # Pie chart showing distribution
            fig = px.pie(
                values=[agricultural_total, livestock_total, urban_total],
                names=['Agrícola', 'Pecuário', 'Urbano'],
                title='🥧 Distribuição por Tipo de Resíduo',
                color_discrete_sequence=['#4CAF50', '#8BC34A', '#CDDC39']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Bar chart showing totals
            fig = go.Figure(data=[
                go.Bar(
                    x=['Agrícola', 'Pecuário', 'Urbano'],
                    y=[agricultural_total / 1e9, livestock_total / 1e9, urban_total / 1e9],
                    marker_color=['#4CAF50', '#8BC34A', '#CDDC39'],
                    text=[f"{agricultural_total / 1e9:.2f}", f"{livestock_total / 1e9:.2f}", f"{urban_total / 1e9:.2f}"],
                    textposition='auto'
                )
            ])
            fig.update_layout(
                title='📊 Potencial Total por Tipo (Bi m³/ano)',
                yaxis_title='Biogás (Bi m³/ano)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # Reference
        col1, col2 = st.columns([4, 1])
        with col2:
            render_reference_button('biogas_calculation', compact=True)

    def _render_regional_analysis(self, df: pd.DataFrame) -> None:
        """Regional pattern analysis for residue types"""
        st.markdown("### 🗺️ Análise Regional de Resíduos")

        # Check if region column exists
        if 'region' not in df.columns:
            st.warning("⚠️ Coluna 'region' não encontrada no banco de dados. Análise regional indisponível.")
            return

        # Regional breakdown selector
        residue_type = st.selectbox(
            "Selecione o tipo de resíduo:",
            ['agricultural_biogas_m3_year', 'livestock_biogas_m3_year', 'urban_biogas_m3_year'],
            format_func=lambda x: {
                'agricultural_biogas_m3_year': '🌾 Agrícola',
                'livestock_biogas_m3_year': '🐄 Pecuário',
                'urban_biogas_m3_year': '🏙️ Urbano'
            }[x]
        )

        # Reuse regional comparison chart from existing components (DRY)
        fig = create_regional_comparison_pie(df, residue_type)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Top municipalities by region
        st.markdown("#### 🏆 Top Municípios por Região")
        region = st.selectbox("Filtrar por região:", ['Todas'] + sorted(df['region'].unique().tolist()))

        filtered_df = df if region == 'Todas' else df[df['region'] == region]

        # Reuse top municipalities chart (DRY)
        fig = create_top_municipalities_chart(filtered_df, residue_type, limit=10)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    def _render_portfolio_analysis(self, df: pd.DataFrame) -> None:
        """Portfolio optimization - optimal substrate mix per municipality"""
        st.markdown("### 💼 Portfolio de Resíduos por Município")

        st.info("""
        **Análise de Portfolio**: Identifica a composição ideal de substratos para cada município,
        baseada em disponibilidade e potencial energético.
        """)

        # Municipality selector
        name_col = 'municipality' if 'municipality' in df.columns else 'municipio'
        selected_muni = st.selectbox(
            "Selecione um município:",
            options=df[name_col].tolist()
        )

        muni_data = df[df[name_col] == selected_muni].iloc[0]

        # Portfolio composition
        col1, col2 = st.columns([2, 1])

        with col1:
            # Stacked bar showing residue composition
            agricultural = muni_data.get('agricultural_biogas_m3_year', 0)
            livestock = muni_data.get('livestock_biogas_m3_year', 0)
            urban = muni_data.get('urban_biogas_m3_year', 0)

            fig = go.Figure(data=[
                go.Bar(name='Agrícola', x=[selected_muni], y=[agricultural], marker_color='#4CAF50'),
                go.Bar(name='Pecuário', x=[selected_muni], y=[livestock], marker_color='#8BC34A'),
                go.Bar(name='Urbano', x=[selected_muni], y=[urban], marker_color='#CDDC39')
            ])
            fig.update_layout(
                barmode='stack',
                title=f'📊 Composição de Resíduos - {selected_muni}',
                yaxis_title='Potencial de Biogás (m³/ano)',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 📈 Métricas")
            total = agricultural + livestock + urban

            st.metric("Total Biogás", f"{total:,.0f} m³/ano")

            if total > 0:
                st.metric("% Agrícola", f"{(agricultural / total * 100):.1f}%")
                st.metric("% Pecuário", f"{(livestock / total * 100):.1f}%")
                st.metric("% Urbano", f"{(urban / total * 100):.1f}%")

        # Recommendations
        st.markdown("#### 💡 Recomendações")
        dominant_type = max(
            [('Agrícola', agricultural), ('Pecuário', livestock), ('Urbano', urban)],
            key=lambda x: x[1]
        )

        st.success(f"""
        **Tipo Dominante**: {dominant_type[0]} ({dominant_type[1]:,.0f} m³/ano)

        **Estratégia Recomendada**:
        - Priorizar biodigestor especializado em resíduos {dominant_type[0].lower()}
        - Considerar co-digestão para balancear relação C/N
        - Avaliar sazonalidade da produção de resíduos
        """)

    def _render_seasonal_analysis(self, df: pd.DataFrame) -> None:
        """Seasonal availability analysis for agricultural residues"""
        st.markdown("### 📅 Disponibilidade Sazonal de Resíduos")

        st.info("""
        **Análise Sazonal**: Resíduos agrícolas têm disponibilidade sazonal baseada em ciclos de colheita.
        Importante para planejamento de biodigestores.
        """)

        # Seasonal patterns (generic - could be enhanced with real data)
        seasonal_data = pd.DataFrame({
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'Cana': [100, 95, 90, 80, 60, 40, 30, 35, 50, 70, 85, 95],
            'Café': [20, 30, 40, 60, 80, 100, 90, 70, 50, 35, 25, 20],
            'Milho': [30, 25, 60, 80, 70, 50, 40, 90, 100, 80, 50, 35],
            'Citros': [40, 50, 60, 70, 80, 90, 100, 95, 80, 70, 60, 45]
        })

        # Multi-line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=seasonal_data['Mês'], y=seasonal_data['Cana'],
                                 mode='lines+markers', name='Cana-de-açúcar',
                                 line=dict(color='#4CAF50', width=3)))
        fig.add_trace(go.Scatter(x=seasonal_data['Mês'], y=seasonal_data['Café'],
                                 mode='lines+markers', name='Café',
                                 line=dict(color='#8D6E63', width=3)))
        fig.add_trace(go.Scatter(x=seasonal_data['Mês'], y=seasonal_data['Milho'],
                                 mode='lines+markers', name='Milho',
                                 line=dict(color='#FFC107', width=3)))
        fig.add_trace(go.Scatter(x=seasonal_data['Mês'], y=seasonal_data['Citros'],
                                 mode='lines+markers', name='Citros',
                                 line=dict(color='#FF9800', width=3)))

        fig.update_layout(
            title='📈 Disponibilidade Sazonal de Resíduos Agrícolas (%)',
            xaxis_title='Mês',
            yaxis_title='Disponibilidade Relativa (%)',
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

        # Planning recommendations
        st.markdown("#### 🎯 Planejamento de Armazenamento")

        col1, col2 = st.columns(2)
        with col1:
            st.warning("""
            **Período de Pico (Jun-Ago)**:
            - Safra de café concentrada
            - Alta disponibilidade de milho
            - Necessário maior capacidade de armazenamento
            """)

        with col2:
            st.info("""
            **Período de Baixa (Dez-Fev)**:
            - Menor disponibilidade agrícola
            - Depender mais de resíduos pecuários
            - Utilizar materiais armazenados
            """)

        # Reference
        col1, col2 = st.columns([4, 1])
        with col2:
            render_reference_button('biogas_calculation', compact=True)


def create_residue_analysis_page():
    """Factory function following existing pattern"""
    page = ResidueAnalysisPage()
    page.render()
