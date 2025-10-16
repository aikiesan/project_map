"""
CP2B Maps - Proximity Analysis Page
100% V1 Parity - Current GitHub Version
Professional layout with purple gradient header, 50/50 split, top controls
"""

from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Geospatial imports
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    folium = None
    st_folium = None

from config.settings import settings
from src.utils.logging_config import get_logger
from src.core.proximity_analyzer import get_proximity_analyzer
from src.data.loaders.mapbiomas_loader import get_mapbiomas_loader
from src.data.loaders.database_loader import DatabaseLoader
from src.data.loaders.shapefile_loader import ShapefileLoader

logger = get_logger(__name__)


class ProximityAnalysisPage:
    """
    Professional proximity analysis page - V1 Current Version Parity

    Layout:
    1. Purple gradient header
    2. 3-column controls (radius | options | status)
    3. 50/50 split (map | results)
    4. Instruction cards when empty
    """

    def __init__(self):
        """Initialize with dependency injection"""
        self.logger = get_logger(self.__class__.__name__)
        self.mapbiomas_loader = get_mapbiomas_loader()
        self.proximity_analyzer = get_proximity_analyzer(raster_loader=self.mapbiomas_loader)
        self.database_loader = DatabaseLoader()
        self.shapefile_loader = ShapefileLoader()

        # Initialize session state
        if 'proximity_center' not in st.session_state:
            st.session_state.proximity_center = None
        if 'proximity_radius' not in st.session_state:
            st.session_state.proximity_radius = 30  # V1 default
        if 'proximity_results' not in st.session_state:
            st.session_state.proximity_results = None

    def render(self) -> None:
        """Render proximity analysis page (V1 current structure)"""
        try:
            # 1. Purple gradient header (V1 style)
            self._render_header()

            # 2. Top controls (3 columns)
            radius_km, enable_raster, enable_municipal = self._render_controls()

            # 3. Separator
            st.markdown("---")

            # 4. Main 50/50 layout
            self._render_main_content(radius_km, enable_raster, enable_municipal)

        except Exception as e:
            self.logger.error(f"Error rendering proximity page: {e}", exc_info=True)
            st.error("⚠️ Erro ao carregar análise de proximidade.")

    def _render_header(self) -> None:
        """Render modern purple gradient header with stats"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #9333ea 100%);
                    color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                    text-align: center; border-radius: 0 0 25px 25px;
                    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);'>
            <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; font-family: "Montserrat", sans-serif;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                🎯 Análise de Proximidade
            </h1>
            <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
                Análise especializada de uso do solo e potencial de biogás por raio de captação
            </p>
            <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.85;'>
                📍 Geoanálise • 🗺️ MapBiomas • 🌾 Resíduos Agrícolas
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _render_controls(self) -> Tuple[int, bool, bool]:
        """
        Render top controls in 3 columns

        Returns:
            Tuple of (radius_km, enable_raster, enable_municipal)
        """
        st.markdown("### 🎛️ Configuração da Análise")

        col1, col2, col3 = st.columns([1.5, 2, 2])

        # Column 1: Radius selection
        with col1:
            radius_km = st.selectbox(
                "📏 Raio de Captação:",
                options=[10, 30, 50],
                index=1,  # Default 30km (V1 default)
                help="Raio da área de análise em quilômetros"
            )
            st.session_state.proximity_radius = radius_km
            st.caption(f"🎯 **{radius_km} km** a partir do clique")
            st.caption("📍 Válido apenas para **São Paulo**")

        # Column 2: Analysis options
        with col2:
            enable_raster = st.checkbox(
                "🌾 Análise de Culturas (MapBiomas)",
                value=True,
                help="Analisa o uso real do solo usando dados do MapBiomas"
            )
            enable_municipal = st.checkbox(
                "🏘️ Dados Municipais",
                value=True,
                help="Inclui dados de potencial de biogás dos municípios"
            )

        # Column 3: Status/actions
        with col3:
            if st.session_state.proximity_center:
                center_lat, center_lon = st.session_state.proximity_center
                st.success(f"📍 Centro: {center_lat:.4f}, {center_lon:.4f}")

                if st.button("🗑️ Limpar Centro", width='stretch'):
                    st.session_state.proximity_center = None
                    st.session_state.proximity_results = None
                    st.rerun()
            else:
                st.info("👆 Clique no mapa abaixo para definir o centro")
                st.caption("🗺️ Funciona apenas dentro do estado de São Paulo")

        return radius_km, enable_raster, enable_municipal

    def _render_main_content(
        self,
        radius_km: int,
        enable_raster: bool,
        enable_municipal: bool
    ) -> None:
        """Render main 50/50 layout (map | results)"""
        col_map, col_results = st.columns([1, 1])

        with col_map:
            self._render_map_section(radius_km)

        with col_results:
            self._render_results_section(radius_km, enable_raster, enable_municipal)

    def _render_map_section(self, radius_km: int) -> None:
        """Render map section (left column)"""
        st.markdown("### 🗺️ Mapa de Análise de Proximidade")

        if not HAS_FOLIUM:
            st.error("🔧 Sistema de mapas não disponível")
            return

        # Create map
        m = self._create_proximity_map(radius_km)

        # Display map
        map_data = st_folium(
            m,
            key="proximity_map",
            width=None,  # Full column width
            height=650,
            returned_objects=["last_clicked"]
        )

        # Handle map clicks
        if map_data and map_data.get("last_clicked") and map_data["last_clicked"].get("lat"):
            new_center = (
                map_data["last_clicked"]["lat"],
                map_data["last_clicked"]["lng"]
            )

            # Only update if significantly different
            if not st.session_state.proximity_center or \
               abs(st.session_state.proximity_center[0] - new_center[0]) > 0.001 or \
               abs(st.session_state.proximity_center[1] - new_center[1]) > 0.001:

                st.session_state.proximity_center = new_center
                st.session_state.proximity_results = None  # Clear cache
                st.toast(f"📍 Novo centro: {new_center[0]:.4f}, {new_center[1]:.4f}", icon="🎯")
                st.rerun()

    def _render_results_section(
        self,
        radius_km: int,
        enable_raster: bool,
        enable_municipal: bool
    ) -> None:
        """Render results section (right column)"""
        st.markdown("### 📊 Resultados da Análise")

        if st.session_state.proximity_center:
            # Run analysis if not cached
            if st.session_state.proximity_results is None:
                with st.spinner("🔍 Analisando área selecionada..."):
                    results = self._perform_analysis(
                        radius_km,
                        enable_raster,
                        enable_municipal
                    )
                    st.session_state.proximity_results = results

            # Display results
            if st.session_state.proximity_results:
                self._display_results(st.session_state.proximity_results, radius_km)
        else:
            # Show instruction cards (V1 style)
            self._render_instruction_cards()

    def _render_instruction_cards(self) -> None:
        """Render V1-style instruction cards (3 steps)"""
        # Welcome message
        st.markdown("""
        <div style='background: linear-gradient(135deg, #E8F5E8 0%, #F0F8F0 100%);
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid #2E8B57; margin-bottom: 1rem;'>
            <h4 style='margin-top: 0; color: #2E8B57;'>🎯 Bem-vindo à Análise de Proximidade!</h4>
            <p style='margin-bottom: 0; font-size: 1rem;'>
                Descubra o potencial de biogás em qualquer região de São Paulo clicando no mapa.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🚀 Como usar (3 passos simples):")

        step1, step2, step3 = st.columns(3)

        with step1:
            st.markdown("""
            <div style='
                text-align: center; padding: 1.2rem 0.8rem;
                border: 2px solid #4CAF50; border-radius: 12px;
                background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
                box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
                min-height: 140px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 2.2rem; margin-bottom: 0.8rem;'>📏</div>
                <div style='font-weight: bold; font-size: 1rem; color: #2E7D32; margin-bottom: 0.5rem;'>
                    1. Escolha o Raio
                </div>
                <div style='font-size: 0.85rem; color: #4A4A4A; line-height: 1.3;'>
                    Selecione 10km, 30km ou<br>50km acima
                </div>
            </div>
            """, unsafe_allow_html=True)

        with step2:
            st.markdown("""
            <div style='
                text-align: center; padding: 1.2rem 0.8rem;
                border: 2px solid #2196F3; border-radius: 12px;
                background: linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%);
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
                min-height: 140px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 2.2rem; margin-bottom: 0.8rem;'>🗺️</div>
                <div style='font-weight: bold; font-size: 1rem; color: #1565C0; margin-bottom: 0.5rem;'>
                    2. Clique no Mapa
                </div>
                <div style='font-size: 0.85rem; color: #4A4A4A; line-height: 1.3;'>
                    Defina o centro da<br>sua análise
                </div>
            </div>
            """, unsafe_allow_html=True)

        with step3:
            st.markdown("""
            <div style='
                text-align: center; padding: 1.2rem 0.8rem;
                border: 2px solid #FF9800; border-radius: 12px;
                background: linear-gradient(135deg, #fff8f0 0%, #ffe8cc 100%);
                box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15);
                min-height: 140px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 2.2rem; margin-bottom: 0.8rem;'>📊</div>
                <div style='font-weight: bold; font-size: 1rem; color: #E65100; margin-bottom: 0.5rem;'>
                    3. Veja os Resultados
                </div>
                <div style='font-size: 0.85rem; color: #4A4A4A; line-height: 1.3;'>
                    Análise automática<br>em segundos
                </div>
            </div>
            """, unsafe_allow_html=True)

    def _create_proximity_map(self, radius_km: int) -> folium.Map:
        """Create proximity map with circle and marker"""
        m = folium.Map(
            location=settings.DEFAULT_CENTER,
            zoom_start=7,
            tiles='CartoDB positron',
            prefer_canvas=True
        )

        # Add fullscreen
        folium.plugins.Fullscreen().add_to(m)

        # Add state boundary
        try:
            state_boundary = self.shapefile_loader.load_state_boundary()
            if state_boundary is not None:
                folium.GeoJson(
                    state_boundary,
                    style_function=lambda feature: {
                        'color': '#2E8B57',
                        'weight': 2,
                        'opacity': 0.8,
                        'fillOpacity': 0.05,
                        'dashArray': '5, 5'
                    },
                    tooltip="São Paulo State"
                ).add_to(m)
        except Exception as e:
            self.logger.warning(f"Could not load state boundary: {e}")

        # Add proximity circle and marker if center is defined
        if st.session_state.proximity_center:
            center = st.session_state.proximity_center

            # Marker
            folium.Marker(
                location=center,
                popup=f"📍 <b>Centro de Análise</b><br>🎯 Raio: {radius_km} km",
                tooltip="🎯 Centro da Análise de Proximidade",
                icon=folium.Icon(color='red', icon='screenshot', prefix='glyphicon')
            ).add_to(m)

            # Circle
            folium.Circle(
                location=center,
                radius=radius_km * 1000,  # km to meters
                color='#667eea',  # Purple (matches header)
                fill=True,
                fillColor='#667eea',
                fillOpacity=0.15,
                weight=2,
                popup=f"Raio de Captação: {radius_km}km"
            ).add_to(m)

        return m

    def _perform_analysis(
        self,
        radius_km: int,
        enable_raster: bool,
        enable_municipal: bool
    ) -> Dict:
        """Perform proximity analysis"""
        center_lat, center_lon = st.session_state.proximity_center
        results = {}

        # Raster analysis (MapBiomas)
        if enable_raster:
            try:
                raster_results = self.proximity_analyzer.analyze_proximity(
                    center_lat, center_lon, radius_km
                )
                results['raster'] = raster_results
            except Exception as e:
                self.logger.error(f"Raster analysis failed: {e}")
                results['raster'] = None

        # Municipal analysis
        if enable_municipal:
            try:
                # Calculate municipalities within radius
                municipalities_df = self._calculate_municipalities_in_radius(
                    center_lat, center_lon, radius_km
                )
                results['municipal'] = municipalities_df
            except Exception as e:
                self.logger.error(f"Municipal analysis failed: {e}")
                results['municipal'] = None

        return results

    def _calculate_municipalities_in_radius(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> Optional[pd.DataFrame]:
        """
        Calculate which municipalities fall within the specified radius

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers

        Returns:
            DataFrame with municipalities within radius and their distances
        """
        try:
            # Load all municipalities data
            df = self.database_loader.load_municipalities_data()

            if df is None or df.empty:
                self.logger.warning("No municipality data available")
                return None

            # Calculate distance using haversine formula
            def haversine_distance(lat1, lon1, lat2, lon2):
                """Calculate distance between two points on Earth in kilometers"""
                R = 6371  # Earth radius in kilometers

                lat1_rad = np.radians(lat1)
                lat2_rad = np.radians(lat2)
                delta_lat = np.radians(lat2 - lat1)
                delta_lon = np.radians(lon2 - lon1)

                a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

                return R * c

            # Calculate distance for each municipality
            df['distance_km'] = df.apply(
                lambda row: haversine_distance(
                    center_lat, center_lon,
                    row['latitude'], row['longitude']
                ),
                axis=1
            )

            # Filter municipalities within radius
            municipalities_in_radius = df[df['distance_km'] <= radius_km].copy()

            # Sort by distance
            municipalities_in_radius = municipalities_in_radius.sort_values('distance_km')

            self.logger.info(
                f"Found {len(municipalities_in_radius)} municipalities within {radius_km}km radius"
            )

            return municipalities_in_radius

        except Exception as e:
            self.logger.error(f"Failed to calculate municipalities in radius: {e}", exc_info=True)
            return None

    def _create_land_use_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create pie chart for land use distribution"""
        fig = px.pie(
            df,
            values='Área (ha)',
            names='Tipo de Uso',
            title='📊 Distribuição de Uso do Solo por Área',
            hole=0.4,  # Donut chart
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<br>Percentual: %{percent}<extra></extra>'
        )

        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            )
        )

        return fig

    def _create_land_use_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create horizontal bar chart for land use by area"""
        fig = px.bar(
            df,
            x='Área (ha)',
            y='Tipo de Uso',
            orientation='h',
            title='📊 Uso do Solo por Área (Hectares)',
            color='Área (ha)',
            color_continuous_scale='Greens',
            text_auto='.2s'
        )

        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Área: %{x:,.0f} ha<extra></extra>'
        )

        fig.update_layout(
            height=max(400, len(df) * 30),  # Dynamic height based on number of items
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            xaxis_title="Área (hectares)",
            yaxis_title=""
        )

        return fig

    def _create_municipality_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create bar chart for municipalities ranked by biogas potential"""
        # Limit to top 15 municipalities for readability
        df_top = df.nlargest(15, 'biogas_potential_m3_day').copy()

        fig = px.bar(
            df_top,
            x='biogas_potential_m3_day',
            y='municipality',
            orientation='h',
            title='🏆 Top 15 Municípios por Potencial de Biogás',
            color='biogas_potential_m3_day',
            color_continuous_scale='Purples',
            text_auto='.2s',
            hover_data=['distance_km']
        )

        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Potencial: %{x:,.0f} m³/dia<br>Distância: %{customdata[0]:.1f} km<extra></extra>'
        )

        fig.update_layout(
            height=max(450, len(df_top) * 35),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            xaxis_title="Potencial de Biogás (m³/dia)",
            yaxis_title=""
        )

        return fig

    def _display_results(self, results: Dict, radius_km: int) -> None:
        """Display analysis results with visualization options"""
        center_lat, center_lon = st.session_state.proximity_center

        # ========== MapBiomas Results ==========
        if results.get('raster'):
            st.markdown(f"#### 🌾 Uso do Solo (MapBiomas) - Raio {radius_km}km")
            st.caption(f"Centro: {center_lat:.4f}, {center_lon:.4f}")

            raster_data = results['raster']

            if raster_data:
                # Convert to DataFrame
                df = pd.DataFrame([
                    {'Tipo de Uso': uso, 'Área (ha)': area}
                    for uso, area in raster_data.items()
                ]).sort_values('Área (ha)', ascending=False)

                # Summary metrics
                total_area = df['Área (ha)'].sum()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏞️ Área Total", f"{total_area:,.0f} ha")
                with col2:
                    st.metric("📊 Tipos de Uso", len(df))
                with col3:
                    # Calculate agricultural percentage
                    agri_keywords = ['🌾', '🌱', '☕', '🍊', '🌴', '🌲']
                    agri_area = df[df['Tipo de Uso'].apply(
                        lambda x: any(k in x for k in agri_keywords)
                    )]['Área (ha)'].sum()
                    agri_pct = (agri_area / total_area * 100) if total_area > 0 else 0
                    st.metric("🌾 Área Agrícola", f"{agri_pct:.1f}%")

                # Visualization selector
                viz_option = st.radio(
                    "Selecione o tipo de visualização:",
                    options=['📊 Gráfico de Pizza', '📊 Gráfico de Barras', '📋 Tabela'],
                    horizontal=True,
                    key='mapbiomas_viz'
                )

                # Display selected visualization
                if viz_option == '📊 Gráfico de Pizza':
                    fig = self._create_land_use_pie_chart(df)
                    st.plotly_chart(fig, use_container_width=True)
                elif viz_option == '📊 Gráfico de Barras':
                    fig = self._create_land_use_bar_chart(df)
                    st.plotly_chart(fig, use_container_width=True)
                else:  # Table
                    st.dataframe(df, use_container_width=True, hide_index=True)

            else:
                st.warning("⚠️ Nenhum dado encontrado na área")

        # ========== Municipal Results ==========
        if results.get('municipal') is not None and not isinstance(results['municipal'], dict):
            st.markdown("---")
            st.markdown(f"#### 🏘️ Municípios na Área - Raio {radius_km}km")

            municipalities_df = results['municipal']

            if municipalities_df is not None and not municipalities_df.empty:
                # Summary metrics
                num_municipalities = len(municipalities_df)
                total_biogas = municipalities_df['biogas_potential_m3_day'].sum()
                avg_distance = municipalities_df['distance_km'].mean()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏘️ Municípios", num_municipalities)
                with col2:
                    st.metric("💨 Potencial Total", f"{total_biogas:,.0f} m³/dia")
                with col3:
                    st.metric("📏 Distância Média", f"{avg_distance:.1f} km")

                # Visualization selector
                muni_viz_option = st.radio(
                    "Selecione o tipo de visualização:",
                    options=['📋 Tabela Completa', '🏆 Ranking (Top 15)'],
                    horizontal=True,
                    key='municipal_viz'
                )

                # Display selected visualization
                if muni_viz_option == '📋 Tabela Completa':
                    # Prepare table with selected columns
                    display_df = municipalities_df[[
                        'municipality', 'distance_km', 'biogas_potential_m3_day',
                        'energy_potential_kwh_day', 'population'
                    ]].copy()

                    display_df.columns = [
                        'Município', 'Distância (km)', 'Biogás (m³/dia)',
                        'Energia (kWh/dia)', 'População'
                    ]

                    # Format numbers
                    display_df['Distância (km)'] = display_df['Distância (km)'].apply(lambda x: f"{x:.1f}")
                    display_df['Biogás (m³/dia)'] = display_df['Biogás (m³/dia)'].apply(lambda x: f"{x:,.0f}")
                    display_df['Energia (kWh/dia)'] = display_df['Energia (kWh/dia)'].apply(lambda x: f"{x:,.0f}")
                    display_df['População'] = display_df['População'].apply(lambda x: f"{x:,.0f}")

                    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

                else:  # Ranking chart
                    fig = self._create_municipality_bar_chart(municipalities_df)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("ℹ️ Nenhum município encontrado neste raio")
        elif results.get('municipal') == {"status": "not_implemented"}:
            st.markdown("---")
            st.markdown("#### 🏘️ Análise Municipal")
            st.info("Dados municipais em desenvolvimento")


def create_proximity_analysis_page() -> ProximityAnalysisPage:
    """Factory function"""
    return ProximityAnalysisPage()
