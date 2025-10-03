"""
CP2B Maps V2 - Advanced Analysis Page
SOLID Architecture - Professional comparative analysis of biogas potential
Modular design with visual parity to Explorar Dados and Análise de Proximidade
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List, Tuple
from abc import ABC, abstractmethod

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import get_database_loader
from src.data.loaders.database_loader import DatabaseLoader
from src.data.loaders.shapefile_loader import ShapefileLoader

# Import design system components
from src.ui.components.design_system import (
    render_section_header,
    render_styled_metrics,
    render_info_banner
)

# Import chart components
from src.ui.components.analysis_charts import (
    create_top_municipalities_chart,
    create_regional_comparison_pie,
    create_summary_statistics_table,
    create_comparative_municipalities_chart,
    create_distribution_histogram
)

# Import footer and references
from src.ui.components.academic_footer import render_compact_academic_footer
from src.data.references.scientific_references import render_reference_button

logger = get_logger(__name__)


# SOLID Architecture - Interface Pattern
class AnalysisVisualization(ABC):
    """Base interface for analysis visualization components"""

    @abstractmethod
    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render analysis visualization"""
        pass


class TypeComparisonAnalyzer(AnalysisVisualization):
    """Single Responsibility: Comprehensive Agricultural vs Livestock vs Urban comparison"""

    # Residue categorization with production percentages
    AGRICULTURAL_RESIDUES = {
        'biogas_cana_m_ano': {'name': '🌾 Cana-de-açúcar', 'pct': 96.52},
        'biogas_soja_m_ano': {'name': '🫘 Soja', 'pct': 1.09},
        'biogas_milho_m_ano': {'name': '🌽 Milho', 'pct': 1.07},
        'biogas_cafe_m_ano': {'name': '☕ Café', 'pct': 0.17},
        'biogas_citros_m_ano': {'name': '🍊 Citros', 'pct': 0.15}
    }

    LIVESTOCK_RESIDUES = {
        'biogas_bovinos_m_ano': {'name': '🐄 Bovinos', 'pct': 75.0},
        'biogas_suino_m_ano': {'name': '🐷 Suínos', 'pct': 15.0},
        'biogas_aves_m_ano': {'name': '🐔 Aves', 'pct': 9.0},
        'biogas_piscicultura_m_ano': {'name': '🐟 Piscicultura', 'pct': 1.0}
    }

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render comprehensive type comparison analysis"""
        st.markdown("### 📊 Comparação Detalhada entre Tipos de Resíduos")

        # Calculate totals by type
        agricultural_total = data['agricultural_biogas_m3_year'].sum() if 'agricultural_biogas_m3_year' in data.columns else 0
        livestock_total = data['livestock_biogas_m3_year'].sum() if 'livestock_biogas_m3_year' in data.columns else 0
        urban_total = data['urban_biogas_m3_year'].sum() if 'urban_biogas_m3_year' in data.columns else 0
        total_biogas = agricultural_total + livestock_total + urban_total

        # Top KPI cards with energy equivalents
        self._render_kpi_cards(agricultural_total, livestock_total, urban_total, total_biogas)

        st.markdown("---")

        # Main comparison charts
        st.markdown("#### 📈 Visualizações Comparativas")
        col1, col2 = st.columns(2)

        with col1:
            self._render_pie_chart(agricultural_total, livestock_total, urban_total)

        with col2:
            self._render_waterfall_chart(agricultural_total, livestock_total, urban_total, total_biogas)

        st.markdown("---")

        # Detailed breakdown by specific residues
        st.markdown("#### 🔬 Detalhamento por Resíduo Específico")
        self._render_detailed_breakdown(data)

        st.markdown("---")

        # Top municipalities by type
        st.markdown("#### 🏆 Top Municípios por Tipo de Resíduo")
        self._render_top_municipalities(data)

        st.markdown("---")

        # Statistical comparison
        st.markdown("#### 📊 Comparação Estatística")
        self._render_statistical_comparison(data)

        # Reference
        col1, col2 = st.columns([4, 1])
        with col2:
            render_reference_button('biogas_calculation', compact=True)

    def _render_kpi_cards(self, agri: float, livestock: float, urban: float, total: float) -> None:
        """Render enhanced KPI cards with energy equivalents"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🌾 Agrícola",
                f"{agri / 1e9:.2f} Bi m³/ano",
                delta=f"{(agri/total*100):.1f}% do total" if total > 0 else None
            )
            # Energy equivalent
            energy_mwh = agri * 0.6 * 9.97 / 1000
            st.caption(f"⚡ {energy_mwh/1e6:.2f} M MWh/ano")

        with col2:
            st.metric(
                "🐄 Pecuário",
                f"{livestock / 1e9:.2f} Bi m³/ano",
                delta=f"{(livestock/total*100):.1f}% do total" if total > 0 else None
            )
            energy_mwh = livestock * 0.6 * 9.97 / 1000
            st.caption(f"⚡ {energy_mwh/1e6:.2f} M MWh/ano")

        with col3:
            st.metric(
                "🏙️ Urbano",
                f"{urban / 1e9:.2f} Bi m³/ano",
                delta=f"{(urban/total*100):.1f}% do total" if total > 0 else None
            )
            energy_mwh = urban * 0.6 * 9.97 / 1000
            st.caption(f"⚡ {energy_mwh/1e6:.2f} M MWh/ano")

        with col4:
            st.metric("📈 Total Estado", f"{total / 1e9:.2f} Bi m³/ano")
            # Households served (avg 300 kWh/month)
            energy_mwh = total * 0.6 * 9.97 / 1000
            households = (energy_mwh * 1000) / (300 * 12)
            st.caption(f"🏠 {households/1e6:.2f}M domicílios/ano")

    def _render_pie_chart(self, agri: float, livestock: float, urban: float) -> None:
        """Render distribution pie chart"""
        fig = px.pie(
            values=[agri, livestock, urban],
            names=['Agrícola', 'Pecuário', 'Urbano'],
            title='🥧 Distribuição por Tipo de Resíduo',
            color_discrete_sequence=['#f59e0b', '#ea580c', '#dc2626'],
            hole=0.4  # Donut chart
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>%{value:,.0f} m³/ano<br>%{percent}<extra></extra>'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    def _render_waterfall_chart(self, agri: float, livestock: float, urban: float, total: float) -> None:
        """Render waterfall chart showing contribution breakdown"""
        fig = go.Figure(go.Waterfall(
            name="Contribuição",
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Agrícola", "Pecuário", "Urbano", "Total"],
            y=[agri/1e9, livestock/1e9, urban/1e9, total/1e9],
            text=[f"{agri/1e9:.2f}", f"{livestock/1e9:.2f}", f"{urban/1e9:.2f}", f"{total/1e9:.2f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#f59e0b"}},
            totals={"marker": {"color": "#059669"}}
        ))
        fig.update_layout(
            title='💧 Contribuição Acumulada (Bi m³/ano)',
            yaxis_title='Biogás (Bi m³/ano)',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_detailed_breakdown(self, data: pd.DataFrame) -> None:
        """Render detailed breakdown by specific residue types"""
        col1, col2 = st.columns(2)

        with col1:
            # Agricultural breakdown
            with st.expander("🌾 **Detalhamento Agrícola**", expanded=True):
                agri_data = []
                for col, info in self.AGRICULTURAL_RESIDUES.items():
                    if col in data.columns:
                        total = data[col].sum()
                        agri_data.append({
                            'Resíduo': info['name'],
                            'Potencial (m³/ano)': total,
                            'Representatividade': f"{info['pct']}%"
                        })

                if agri_data:
                    df_agri = pd.DataFrame(agri_data).sort_values('Potencial (m³/ano)', ascending=False)

                    # Horizontal bar chart
                    fig = px.bar(
                        df_agri,
                        y='Resíduo',
                        x='Potencial (m³/ano)',
                        orientation='h',
                        title='Comparação de Resíduos Agrícolas',
                        color='Potencial (m³/ano)',
                        color_continuous_scale='Oranges'
                    )
                    fig.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(df_agri, use_container_width=True, hide_index=True)

        with col2:
            # Livestock breakdown
            with st.expander("🐄 **Detalhamento Pecuário**", expanded=True):
                livestock_data = []
                for col, info in self.LIVESTOCK_RESIDUES.items():
                    if col in data.columns:
                        total = data[col].sum()
                        livestock_data.append({
                            'Resíduo': info['name'],
                            'Potencial (m³/ano)': total,
                            'Representatividade': f"{info['pct']}%"
                        })

                if livestock_data:
                    df_livestock = pd.DataFrame(livestock_data).sort_values('Potencial (m³/ano)', ascending=False)

                    # Horizontal bar chart
                    fig = px.bar(
                        df_livestock,
                        y='Resíduo',
                        x='Potencial (m³/ano)',
                        orientation='h',
                        title='Comparação de Resíduos Pecuários',
                        color='Potencial (m³/ano)',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(df_livestock, use_container_width=True, hide_index=True)

    def _render_top_municipalities(self, data: pd.DataFrame) -> None:
        """Render top municipalities by type"""
        type_selector = st.selectbox(
            "Selecione o tipo de resíduo:",
            ['agricultural_biogas_m3_year', 'livestock_biogas_m3_year', 'urban_biogas_m3_year'],
            format_func=lambda x: {'agricultural_biogas_m3_year': '🌾 Agrícola', 'livestock_biogas_m3_year': '🐄 Pecuário', 'urban_biogas_m3_year': '🏙️ Urbano'}[x],
            key='type_comparison_selector'
        )

        if type_selector in data.columns:
            name_col = 'municipality' if 'municipality' in data.columns else 'municipio'

            # Top 15 municipalities
            top_data = data.nlargest(15, type_selector)[[name_col, type_selector]].copy()
            top_data.columns = ['Município', 'Potencial (m³/ano)']

            col1, col2 = st.columns([2, 1])

            with col1:
                # Horizontal bar chart
                fig = px.bar(
                    top_data,
                    y='Município',
                    x='Potencial (m³/ano)',
                    orientation='h',
                    title=f'Top 15 Municípios',
                    color='Potencial (m³/ano)',
                    color_continuous_scale='Oranges'
                )
                fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**📋 Ranking:**")
                top_data['Ranking'] = range(1, len(top_data) + 1)
                top_data['Potencial (Bi m³/ano)'] = (top_data['Potencial (m³/ano)'] / 1e9).round(3)
                st.dataframe(
                    top_data[['Ranking', 'Município', 'Potencial (Bi m³/ano)']],
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )

    def _render_statistical_comparison(self, data: pd.DataFrame) -> None:
        """Render statistical comparison between types"""
        col1, col2 = st.columns(2)

        with col1:
            # Box plot comparison
            plot_data = []
            for col, name in [('agricultural_biogas_m3_year', 'Agrícola'),
                             ('livestock_biogas_m3_year', 'Pecuário'),
                             ('urban_biogas_m3_year', 'Urbano')]:
                if col in data.columns:
                    for value in data[col].dropna():
                        if value > 0:  # Only include municipalities with production
                            plot_data.append({'Tipo': name, 'Potencial (m³/ano)': value})

            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                fig = px.box(
                    df_plot,
                    x='Tipo',
                    y='Potencial (m³/ano)',
                    title='📦 Distribuição Estatística (Box Plot)',
                    color='Tipo',
                    color_discrete_map={'Agrícola': '#f59e0b', 'Pecuário': '#ea580c', 'Urbano': '#dc2626'}
                )
                fig.update_layout(showlegend=False, height=400)
                fig.update_yaxes(type='log')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Statistical metrics table
            st.markdown("**📊 Métricas Estatísticas:**")
            stats_data = []
            for col, name in [('agricultural_biogas_m3_year', 'Agrícola'),
                             ('livestock_biogas_m3_year', 'Pecuário'),
                             ('urban_biogas_m3_year', 'Urbano')]:
                if col in data.columns:
                    series = data[col].dropna()
                    series = series[series > 0]  # Only municipalities with production
                    if len(series) > 0:
                        stats_data.append({
                            'Tipo': name,
                            'Municípios': len(series),
                            'Média (m³/ano)': f"{series.mean():,.0f}",
                            'Mediana (m³/ano)': f"{series.median():,.0f}",
                            'Desvio Padrão': f"{series.std():,.0f}",
                            'Máximo (m³/ano)': f"{series.max():,.0f}"
                        })

            if stats_data:
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True, hide_index=True)

                # Concentration index
                st.markdown("**🎯 Índice de Concentração:**")
                st.caption("Percentual do potencial total concentrado nos top 10 municípios")

                for col, name in [('agricultural_biogas_m3_year', 'Agrícola'),
                                 ('livestock_biogas_m3_year', 'Pecuário'),
                                 ('urban_biogas_m3_year', 'Urbano')]:
                    if col in data.columns:
                        total = data[col].sum()
                        top10_total = data.nlargest(10, col)[col].sum()
                        if total > 0:
                            concentration = (top10_total / total) * 100
                            st.metric(f"{name}", f"{concentration:.1f}%")


class RegionalAnalyzer(AnalysisVisualization):
    """Single Responsibility: Regional pattern analysis with interactive choropleth map"""

    def __init__(self, shapefile_loader: ShapefileLoader):
        self.logger = get_logger(self.__class__.__name__)
        self.shapefile_loader = shapefile_loader

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render regional analysis with interactive Folium map"""
        st.markdown("### 🗺️ Análise Regional de Resíduos")

        # Check for regional columns
        regional_col_imediata = 'nm_rgi' if 'nm_rgi' in data.columns else None
        regional_col_intermediaria = 'nm_rgint' if 'nm_rgint' in data.columns else None

        if not regional_col_imediata and not regional_col_intermediaria:
            st.warning("⚠️ Dados regionais não disponíveis no banco de dados")
            st.info("💡 Execute o script add_regional_classifications.py para adicionar dados regionais")
            return

        # Controls
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            # Regional level selector
            regional_options = []
            if regional_col_intermediaria:
                regional_options.append(("Regiões Intermediárias", regional_col_intermediaria, "SP_RG_Intermediarias_2024"))
            if regional_col_imediata:
                regional_options.append(("Regiões Imediatas", regional_col_imediata, "SP_RG_Imediatas_2024"))

            if regional_options:
                selected_level = st.selectbox(
                    "Nível Regional:",
                    range(len(regional_options)),
                    format_func=lambda x: regional_options[x][0],
                    key='regional_level_selector'
                )
                regional_name, regional_col, shapefile_name = regional_options[selected_level]
            else:
                st.error("Nenhum nível regional disponível")
                return

        with col2:
            # Residue type selector
            residue_type = st.selectbox(
                "Tipo de resíduo:",
                ['biogas_potential_m3_year', 'agricultural_biogas_m3_year', 'livestock_biogas_m3_year', 'urban_biogas_m3_year'],
                format_func=lambda x: {
                    'biogas_potential_m3_year': '📊 Total',
                    'agricultural_biogas_m3_year': '🌾 Agrícola',
                    'livestock_biogas_m3_year': '🐄 Pecuário',
                    'urban_biogas_m3_year': '🏙️ Urbano'
                }[x],
                key='regional_residue_selector'
            )

        with col3:
            st.markdown("**📌 Visualização:**")
            st.caption(f"Mapa coroplético de {regional_name}")

        st.markdown("---")

        # Aggregate data by region
        if residue_type in data.columns:
            regional_data = data.groupby(regional_col).agg({
                residue_type: 'sum',
                'municipality': 'count'
            }).reset_index()
            regional_data.columns = ['region', 'total_biogas', 'num_municipalities']
            regional_data['total_biogas_bi'] = regional_data['total_biogas'] / 1e9

            # Display map and statistics side by side
            col_map, col_stats = st.columns([2, 1])

            with col_map:
                st.markdown("#### 🗺️ Mapa Regional")
                self._render_regional_map(shapefile_name, regional_data, regional_col, residue_type)

            with col_stats:
                st.markdown("#### 📊 Estatísticas Regionais")

                # Top regions
                top_regions = regional_data.nlargest(10, 'total_biogas')
                st.markdown("**🏆 Top 10 Regiões:**")
                for i, row in enumerate(top_regions.itertuples(), 1):
                    st.write(f"{i}. **{row.region}**")
                    st.caption(f"   {row.total_biogas_bi:.3f} Bi m³/ano | {row.num_municipalities} municípios")

                # Summary metrics
                st.markdown("---")
                st.markdown("**📈 Resumo:**")
                st.metric("Total de Regiões", len(regional_data))
                st.metric("Potencial Total", f"{regional_data['total_biogas_bi'].sum():.2f} Bi m³/ano")
                st.metric("Média por Região", f"{regional_data['total_biogas_bi'].mean():.3f} Bi m³/ano")

            # Regional comparison bar chart
            st.markdown("---")
            st.markdown("#### 📊 Comparação Regional")

            # Show all regions sorted
            regional_sorted = regional_data.sort_values('total_biogas', ascending=True)

            fig = px.bar(
                regional_sorted,
                y='region',
                x='total_biogas_bi',
                orientation='h',
                title=f'Potencial de Biogás por Região ({regional_name})',
                labels={'total_biogas_bi': 'Biogás (Bi m³/ano)', 'region': 'Região'},
                color='total_biogas_bi',
                color_continuous_scale='Oranges',
                height=max(400, len(regional_sorted) * 25)
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    def _render_regional_map(self, shapefile_name: str, regional_data: pd.DataFrame, regional_col: str, residue_type: str) -> None:
        """Render Folium choropleth map"""
        try:
            import folium
            from streamlit_folium import st_folium
            import json

            # Load shapefile
            gdf = self.shapefile_loader.load_shapefile(shapefile_name)

            if gdf is None:
                st.warning(f"⚠️ Shapefile {shapefile_name} não encontrado")
                return

            # Match column names (try different possible names)
            region_col_in_shapefile = None
            for possible_col in ['NM_RG', 'NM_RGINT', 'NM_RGI', 'nm_rg', 'nm_rgint', 'nm_rgi']:
                if possible_col in gdf.columns:
                    region_col_in_shapefile = possible_col
                    break

            if not region_col_in_shapefile:
                st.error(f"Coluna de região não encontrada no shapefile. Colunas disponíveis: {list(gdf.columns)}")
                return

            # Merge data with shapefile
            gdf = gdf.merge(
                regional_data,
                left_on=region_col_in_shapefile,
                right_on='region',
                how='left'
            )

            # Fill NaN values
            gdf['total_biogas_bi'] = gdf['total_biogas_bi'].fillna(0)

            # Create map
            m = folium.Map(
                location=[-23.5, -48.5],  # Center of São Paulo
                zoom_start=7,
                tiles='CartoDB positron'
            )

            # Create choropleth
            folium.Choropleth(
                geo_data=gdf.to_json(),
                name='choropleth',
                data=gdf,
                columns=['region', 'total_biogas_bi'],
                key_on='feature.properties.region',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.3,
                legend_name=f'Potencial de Biogás (Bi m³/ano)',
                nan_fill_color='lightgray'
            ).add_to(m)

            # Add tooltips
            for idx, row in gdf.iterrows():
                if pd.notna(row.get('total_biogas_bi')):
                    folium.GeoJson(
                        row['geometry'],
                        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
                        tooltip=folium.Tooltip(
                            f"<b>{row.get('region', 'N/A')}</b><br>"
                            f"Potencial: {row.get('total_biogas_bi', 0):.3f} Bi m³/ano<br>"
                            f"Municípios: {int(row.get('num_municipalities', 0))}"
                        )
                    ).add_to(m)

            # Display map
            st_folium(m, width=None, height=500)

        except ImportError:
            st.error("Folium ou streamlit_folium não estão instalados")
        except Exception as e:
            self.logger.error(f"Error rendering regional map: {e}", exc_info=True)
            st.error(f"Erro ao renderizar mapa: {str(e)}")


class MunicipalPortfolioAnalyzer(AnalysisVisualization):
    """Single Responsibility: Municipal portfolio and multi-municipality comparison"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render municipal portfolio analysis with comparison feature"""
        st.markdown("### 💼 Portfolio Municipal")

        st.info("""
        **Análise de Portfolio Municipal**: Compare múltiplos municípios e identifique a composição
        ideal de substratos baseada em disponibilidade e potencial energético.
        """)

        # Municipality selector
        name_col = 'municipality' if 'municipality' in data.columns else 'municipio'

        # Single or multiple municipality selection
        analysis_mode = st.radio(
            "Modo de análise:",
            ["Individual", "Comparativo (2-5 municípios)"],
            horizontal=True
        )

        if analysis_mode == "Individual":
            self._render_single_municipality(data, name_col)
        else:
            self._render_multi_municipality_comparison(data, name_col)

    def _render_single_municipality(self, data: pd.DataFrame, name_col: str) -> None:
        """Render single municipality portfolio"""
        selected_muni = st.selectbox(
            "Selecione um município:",
            options=sorted(data[name_col].tolist())
        )

        muni_data = data[data[name_col] == selected_muni].iloc[0]

        # Portfolio composition
        col1, col2 = st.columns([2, 1])

        with col1:
            # Stacked bar showing residue composition
            agricultural = muni_data.get('agricultural_biogas_m3_year', 0)
            livestock = muni_data.get('livestock_biogas_m3_year', 0)
            urban = muni_data.get('urban_biogas_m3_year', 0)

            fig = go.Figure(data=[
                go.Bar(name='Agrícola', x=[selected_muni], y=[agricultural], marker_color='#f59e0b'),
                go.Bar(name='Pecuário', x=[selected_muni], y=[livestock], marker_color='#ea580c'),
                go.Bar(name='Urbano', x=[selected_muni], y=[urban], marker_color='#dc2626')
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

    def _render_multi_municipality_comparison(self, data: pd.DataFrame, name_col: str) -> None:
        """Render multi-municipality comparison"""
        selected_munis = st.multiselect(
            "Selecione 2-5 municípios para comparar:",
            options=sorted(data[name_col].tolist()),
            max_selections=5,
            help="Escolha entre 2 e 5 municípios para análise comparativa"
        )

        if len(selected_munis) < 2:
            st.warning("⚠️ Selecione pelo menos 2 municípios para comparação")
            return

        # Filter data for selected municipalities
        comparison_data = data[data[name_col].isin(selected_munis)].copy()

        # Comparison metrics
        st.markdown("#### 📊 Comparação de Potenciais")

        col1, col2 = st.columns(2)

        with col1:
            # Total biogas comparison
            comparison_data['total_biogas'] = (
                comparison_data.get('agricultural_biogas_m3_year', 0) +
                comparison_data.get('livestock_biogas_m3_year', 0) +
                comparison_data.get('urban_biogas_m3_year', 0)
            )

            fig = px.bar(
                comparison_data,
                x=name_col,
                y='total_biogas',
                title='Potencial Total de Biogás',
                labels={'total_biogas': 'Biogás (m³/ano)', name_col: 'Município'},
                color='total_biogas',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Residue type breakdown comparison
            residue_comparison = []
            for muni in selected_munis:
                muni_data = data[data[name_col] == muni].iloc[0]
                residue_comparison.append({
                    'Município': muni,
                    'Agrícola': muni_data.get('agricultural_biogas_m3_year', 0),
                    'Pecuário': muni_data.get('livestock_biogas_m3_year', 0),
                    'Urbano': muni_data.get('urban_biogas_m3_year', 0)
                })

            comp_df = pd.DataFrame(residue_comparison)
            fig = go.Figure()

            fig.add_trace(go.Bar(name='Agrícola', x=comp_df['Município'], y=comp_df['Agrícola'], marker_color='#f59e0b'))
            fig.add_trace(go.Bar(name='Pecuário', x=comp_df['Município'], y=comp_df['Pecuário'], marker_color='#ea580c'))
            fig.add_trace(go.Bar(name='Urbano', x=comp_df['Município'], y=comp_df['Urbano'], marker_color='#dc2626'))

            fig.update_layout(
                title='Composição por Tipo de Resíduo',
                barmode='group',
                yaxis_title='Biogás (m³/ano)'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Comparison table
        st.markdown("#### 📋 Tabela Comparativa")
        st.dataframe(comparison_data[[name_col, 'agricultural_biogas_m3_year',
                                      'livestock_biogas_m3_year', 'urban_biogas_m3_year', 'total_biogas']]
                    .sort_values('total_biogas', ascending=False),
                    use_container_width=True,
                    hide_index=True)


class SeasonalAnalyzer(AnalysisVisualization):
    """Single Responsibility: Comprehensive seasonal availability analysis with real São Paulo data"""

    # Real seasonality data for São Paulo State (based on production cycles)
    TEMPORARY_CROPS = {
        'Cana-de-açúcar': {
            'data': [15, 15, 10, 20, 25, 100, 100, 100, 80, 60, 40, 15],
            'color': '#f59e0b',
            'production': 96.52,
            'peak': 'Jun-Set (Safra Principal)'
        },
        'Soja': {
            'data': [5, 65, 100, 85, 25, 5, 5, 5, 5, 5, 5, 5],
            'color': '#84cc16',
            'production': 1.09,
            'peak': 'Fev-Abr (Colheita)'
        },
        'Milho': {
            'data': [20, 80, 100, 25, 15, 90, 100, 50, 30, 20, 20, 20],
            'color': '#fbbf24',
            'production': 1.07,
            'peak': 'Fev-Mar (Verão) + Jun-Jul (Safrinha)'
        },
        'Arroz': {
            'data': [10, 100, 100, 80, 60, 15, 10, 10, 10, 10, 10, 10],
            'color': '#a3e635',
            'production': 0.01,
            'peak': 'Fev-Abr (Colheita)'
        },
        'Algodão': {
            'data': [5, 5, 5, 100, 90, 80, 45, 40, 10, 5, 5, 5],
            'color': '#f3f4f6',
            'production': 0.01,
            'peak': 'Abr-Jun (Colheita)'
        }
    }

    PERMANENT_CROPS = {
        'Laranja': {
            'data': [40, 40, 40, 50, 25, 30, 100, 100, 85, 60, 50, 45],
            'color': '#fb923c',
            'production': 76.75,
            'peak': 'Jun-Ago (Safra Principal)'
        },
        'Café': {
            'data': [20, 25, 30, 40, 70, 100, 100, 90, 75, 40, 25, 20],
            'color': '#78350f',
            'production': 1.73,
            'peak': 'Mai-Ago (Safra)'
        },
        'Manga': {
            'data': [80, 100, 90, 60, 30, 20, 20, 20, 20, 30, 60, 80],
            'color': '#fcd34d',
            'production': 1.19,
            'peak': 'Nov-Mar (Safra)'
        },
        'Tangerina': {
            'data': [30, 30, 30, 70, 90, 100, 100, 80, 40, 30, 30, 30],
            'color': '#fdba74',
            'production': 1.82,
            'peak': 'Abr-Ago (Safra)'
        },
        'Uva': {
            'data': [100, 90, 60, 30, 30, 70, 80, 70, 40, 30, 50, 90],
            'color': '#7c3aed',
            'production': 0.86,
            'peak': 'Dez-Fev (Verão) + Jun-Ago (Inverno)'
        }
    }

    LIVESTOCK_URBAN = {
        'Bovinos (Confinado)': {
            'data': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            'color': '#92400e',
            'production': 75.0,
            'pattern': 'Ano inteiro (Confinamento)'
        },
        'Suínos': {
            'data': [85, 85, 85, 90, 100, 100, 100, 100, 95, 90, 85, 85],
            'color': '#fca5a5',
            'production': 15.0,
            'pattern': 'Maior eficiência Mai-Set (meses frios)'
        },
        'Aves': {
            'data': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            'color': '#fef3c7',
            'production': 9.0,
            'pattern': '6-7 ciclos/ano (rotação contínua)'
        },
        'RSU (Urbano)': {
            'data': [95, 95, 95, 100, 95, 105, 105, 95, 95, 95, 95, 110],
            'color': '#6b7280',
            'production': 'N/A',
            'pattern': 'Picos: Dez (férias) + Jun-Jul (férias inverno)'
        }
    }

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def render(self, data: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Render comprehensive seasonal analysis with real São Paulo data"""
        st.markdown("### 📅 Disponibilidade Sazonal de Resíduos - São Paulo")

        st.info("""
        **Análise Sazonal Baseada em Dados Reais**: Padrões de disponibilidade calibrados para o Estado de São Paulo,
        considerando ciclos de colheita, clima subtropical (Cwa/Aw) e práticas agrícolas regionais.
        """)

        # Category selector
        category = st.radio(
            "Selecione a categoria para visualização:",
            ["📊 Visão Completa", "🌾 Culturas Temporárias", "🍊 Culturas Permanentes", "🐄 Pecuário & Urbano"],
            horizontal=True
        )

        st.markdown("---")

        if category == "📊 Visão Completa":
            self._render_complete_overview()
        elif category == "🌾 Culturas Temporárias":
            self._render_category_analysis(self.TEMPORARY_CROPS, "Culturas Temporárias",
                                          "Culturas anuais com ciclos de plantio e colheita definidos")
        elif category == "🍊 Culturas Permanentes":
            self._render_category_analysis(self.PERMANENT_CROPS, "Culturas Permanentes",
                                          "Culturas perenes com safras anuais em períodos específicos")
        else:  # Pecuário & Urbano
            self._render_livestock_urban_analysis()

        # Storage and planning section
        st.markdown("---")
        self._render_storage_calculator()

        # Co-digestion optimizer
        st.markdown("---")
        self._render_codigestion_optimizer()

        # Regional variations
        st.markdown("---")
        self._render_regional_variations()

        # Reference
        col1, col2 = st.columns([4, 1])
        with col2:
            render_reference_button('biogas_calculation', compact=True)

    def _render_complete_overview(self) -> None:
        """Render complete overview with all categories"""
        st.markdown("#### 📊 Disponibilidade Anual - Todas as Categorias")

        # Select key crops from each category
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        fig = go.Figure()

        # Add main crops
        selected_overview = {
            'Cana-de-açúcar': self.TEMPORARY_CROPS['Cana-de-açúcar'],
            'Laranja': self.PERMANENT_CROPS['Laranja'],
            'Café': self.PERMANENT_CROPS['Café'],
            'Bovinos': self.LIVESTOCK_URBAN['Bovinos (Confinado)'],
            'RSU': self.LIVESTOCK_URBAN['RSU (Urbano)']
        }

        for name, info in selected_overview.items():
            fig.add_trace(go.Scatter(
                x=months,
                y=info['data'],
                mode='lines+markers',
                name=name,
                line=dict(color=info['color'], width=3),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title='Principais Fontes de Resíduos - Disponibilidade Mensal',
            xaxis_title='Mês',
            yaxis_title='Disponibilidade Relativa (%)',
            hovermode='x unified',
            showlegend=True,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary insights
        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("""
            **✅ Complementaridade Identificada:**
            - Cana (Jun-Set) + Laranja (Jun-Ago)
            - Pecuário/Urbano: Base ano inteiro
            """)

        with col2:
            st.warning("""
            **⚠️ Período Crítico:**
            - **Dez-Mar**: Menor disponibilidade agrícola
            - Depender mais de pecuário/urbano
            """)

        with col3:
            st.info("""
            **💡 Oportunidade:**
            - Co-digestão balanceada
            - Armazenamento estratégico safra
            """)

    def _render_category_analysis(self, crops_dict: Dict, title: str, description: str) -> None:
        """Render analysis for a specific crop category"""
        st.markdown(f"#### {title}")
        st.caption(description)

        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        # Main chart
        fig = go.Figure()

        for name, info in crops_dict.items():
            fig.add_trace(go.Scatter(
                x=months,
                y=info['data'],
                mode='lines+markers',
                name=name,
                line=dict(color=info['color'], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{name}</b><br>%{{y}}%<extra></extra>'
            ))

        fig.update_layout(
            title=f'Disponibilidade Sazonal - {title}',
            xaxis_title='Mês',
            yaxis_title='Disponibilidade Relativa (%)',
            hovermode='x unified',
            showlegend=True,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

        # Crop details table
        st.markdown("##### 📋 Detalhes das Culturas")

        details_data = []
        for name, info in crops_dict.items():
            details_data.append({
                'Cultura': name,
                'Representatividade': f"{info.get('production', 'N/A')}%",
                'Período de Pico': info.get('peak', info.get('pattern', 'N/A'))
            })

        df_details = pd.DataFrame(details_data)
        st.dataframe(df_details, use_container_width=True, hide_index=True)

        # Heatmap visualization
        st.markdown("##### 🌡️ Mapa de Calor - Disponibilidade Mensal")
        self._render_heatmap(crops_dict, months)

    def _render_livestock_urban_analysis(self) -> None:
        """Render analysis for livestock and urban residues"""
        st.markdown("#### 🐄 Resíduos Pecuários e Urbanos")
        st.caption("Fontes com disponibilidade contínua ou padrões específicos")

        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        fig = go.Figure()

        for name, info in self.LIVESTOCK_URBAN.items():
            fig.add_trace(go.Scatter(
                x=months,
                y=info['data'],
                mode='lines+markers',
                name=name,
                line=dict(color=info['color'], width=3),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title='Disponibilidade - Pecuário e Urbano',
            xaxis_title='Mês',
            yaxis_title='Disponibilidade Relativa (%)',
            hovermode='x unified',
            showlegend=True,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)

        # Characteristics
        st.markdown("##### 📋 Características de Produção")

        details_data = []
        for name, info in self.LIVESTOCK_URBAN.items():
            details_data.append({
                'Fonte': name,
                'Representatividade': f"{info.get('production', 'N/A')}%",
                'Padrão': info['pattern']
            })

        df_details = pd.DataFrame(details_data)
        st.dataframe(df_details, use_container_width=True, hide_index=True)

        st.success("""
        **✅ Vantagens das Fontes Contínuas:**
        - Produção estável ano inteiro
        - Menor necessidade de armazenamento
        - Base confiável para operação de biodigestores
        - Complementam sazonalidade agrícola
        """)

    def _render_heatmap(self, crops_dict: Dict, months: List[str]) -> None:
        """Render heatmap for seasonal availability"""
        # Prepare data for heatmap
        heatmap_data = []
        crop_names = []

        for name, info in crops_dict.items():
            heatmap_data.append(info['data'])
            crop_names.append(name)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=months,
            y=crop_names,
            colorscale='YlOrRd',
            text=heatmap_data,
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title="Disponibilidade (%)")
        ))

        fig.update_layout(
            title='Mapa de Calor - Disponibilidade por Cultura',
            xaxis_title='Mês',
            yaxis_title='Cultura',
            height=max(300, len(crops_dict) * 40)
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_storage_calculator(self) -> None:
        """Render strategic analysis"""
        st.markdown("#### 📊 Análise Estratégica")

        col1, col2 = st.columns(2)

        with col1:
            st.warning("""
            **⚠️ Período Crítico de Baixa (Dez-Mar):**
            - Menor disponibilidade de culturas temporárias
            - Cana em inter-safra (10-20% disponibilidade)
            - Dependência de pecuário e urbano
            - **Recomendação**: Armazenar 45-60 dias de buffer
            """)

        with col2:
            st.success("""
            **✅ Período de Abundância (Jun-Set):**
            - Pico de cana-de-açúcar (100%)
            - Safra de café e laranja
            - Milho safrinha disponível
            - **Estratégia**: Maximizar produção e ensilagem
            """)

    def _render_codigestion_optimizer(self) -> None:
        """Render co-digestion optimization suggestions"""
        st.markdown("#### ⚗️ Otimizador de Co-Digestão")

        st.info("""
        **Co-digestão Estratégica**: Mistura de diferentes substratos para balancear relação C/N
        e maximizar produção de biogás ao longo do ano.
        """)

        # Best combinations
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🌟 Combinações Recomendadas")

            combinations = [
                {
                    'name': '🌾 Cana + Pecuário',
                    'ratio': '70:30',
                    'cn_ratio': '25-28:1',
                    'benefit': 'Equilibra alto C da cana com N do pecuário'
                },
                {
                    'name': '🍊 Citros + RSU',
                    'ratio': '60:40',
                    'cn_ratio': '22-26:1',
                    'benefit': 'Acidez dos citros neutralizada por RSU'
                },
                {
                    'name': '☕ Café + Aves',
                    'ratio': '50:50',
                    'cn_ratio': '20-24:1',
                    'benefit': 'Alto teor de compostos fenólicos balanceados'
                }
            ]

            for combo in combinations:
                with st.expander(f"**{combo['name']}** - Proporção {combo['ratio']}", expanded=False):
                    st.write(f"**Relação C/N resultante:** {combo['cn_ratio']}")
                    st.write(f"**Benefício:** {combo['benefit']}")

        with col2:
            st.markdown("##### 📈 Estratégia Sazonal")

            st.markdown("""
            **Jun-Set (Alta Disponibilidade):**
            - Cana (100%) + Pecuário (base)
            - Laranja (100%) + RSU
            - Armazenar excedentes (ensilagem)

            **Dez-Mar (Baixa Disponibilidade):**
            - Utilizar silagem de cana armazenada
            - Aumentar proporção de pecuário/urbano
            - Considerar culturas permanentes (manga, goiaba)

            **Transição (Abr-Mai, Out-Nov):**
            - Balancear temporárias finalizando/iniciando
            - Ajustar proporções conforme disponibilidade
            """)

    def _render_regional_variations(self) -> None:
        """Render regional micro-variations section"""
        st.markdown("#### 🗺️ Variações Regionais de São Paulo")

        regions_data = {
            'Nordeste SP (Ribeirão Preto)': {
                'dominant': 'Cana + Café + Citros',
                'peak': 'Jun-Set',
                'strategy': 'Especialização em cana, complementar com café'
            },
            'Noroeste SP (S.J. Rio Preto)': {
                'dominant': 'Citros + Pecuário',
                'peak': 'Jun-Ago',
                'strategy': 'Co-digestão citros-pecuário balanceada'
            },
            'Oeste SP (Pres. Prudente)': {
                'dominant': 'Soja + Milho + Pecuário',
                'peak': 'Fev-Mar (Soja) + Jun-Jul (Milho)',
                'strategy': 'Rotação temporal com duas safras'
            },
            'Sul SP (Itapetininga)': {
                'dominant': 'Misto + Eucalipto',
                'peak': 'Jun-Ago (Eucalipto)',
                'strategy': 'Diversificação multi-substrato'
            },
            'Metropolitana SP': {
                'dominant': 'RSU + Poda Urbana',
                'peak': 'Ano inteiro (picos Dez, Jun-Jul)',
                'strategy': 'Foco urbano com pequena produção agrícola'
            }
        }

        selected_region = st.selectbox(
            "Selecione uma região:",
            list(regions_data.keys())
        )

        region_info = regions_data[selected_region]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Fontes Dominantes", region_info['dominant'])

        with col2:
            st.metric("Período de Pico", region_info['peak'])

        with col3:
            st.success(f"**Estratégia:** {region_info['strategy']}")

        st.caption("💡 As variações regionais refletem especialização agrícola, clima e infraestrutura local")


class AdvancedAnalysisPage:
    """
    Main orchestrator for Advanced Analysis Page
    Implements Dependency Inversion Principle with clean component composition
    """

    def __init__(self, db_loader: DatabaseLoader = None, shapefile_loader: ShapefileLoader = None):
        """Initialize with dependency injection"""
        self.logger = get_logger(self.__class__.__name__)
        self.database_loader = db_loader if db_loader is not None else get_database_loader()
        self.shapefile_loader = shapefile_loader if shapefile_loader is not None else ShapefileLoader()

        # Initialize analysis components
        self.type_comparison = TypeComparisonAnalyzer()
        self.regional_analysis = RegionalAnalyzer(self.shapefile_loader)
        self.municipal_portfolio = MunicipalPortfolioAnalyzer()
        self.seasonal_analysis = SeasonalAnalyzer()

    def _render_modern_header(self) -> None:
        """Render modern orange gradient header (visual parity with other pages)"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #ea580c 100%);
                    color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                    text-align: center; border-radius: 0 0 25px 25px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
            <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
                📊 Análises Avançadas
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
                Análise comparativa profissional de potencial de biogás
            </p>
            <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.8;'>
                🔬 Comparações Detalhadas • 🗺️ Análise Regional • 💼 Portfolio Municipal • 📅 Sazonalidade
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render(self) -> None:
        """Main render method with SOLID architecture"""
        try:
            # Modern gradient header
            self._render_modern_header()

            # Load data
            df = self.database_loader.load_municipalities_data()
            if df is None or len(df) == 0:
                st.error("⚠️ Não foi possível carregar os dados")
                return

            # Configuration for all analyzers
            config = {}

            # Main analysis tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Comparação de Tipos",
                "🗺️ Análise Regional",
                "💼 Portfolio Municipal",
                "📅 Disponibilidade Sazonal"
            ])

            with tab1:
                self.type_comparison.render(df, config)

            with tab2:
                self.regional_analysis.render(df, config)

            with tab3:
                self.municipal_portfolio.render(df, config)

            with tab4:
                self.seasonal_analysis.render(df, config)

            # Academic footer
            render_compact_academic_footer()

        except Exception as e:
            self.logger.error(f"Error rendering advanced analysis page: {e}", exc_info=True)
            st.error("⚠️ Erro ao carregar análises avançadas")


def create_residue_analysis_page():
    """Factory function to create Advanced Analysis page"""
    page = AdvancedAnalysisPage()
    page.render()
