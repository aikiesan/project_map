"""
CP2B Maps - Advanced Raster Analysis Page
Comprehensive MapBiomas satellite data analysis with professional tools
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any

# Geospatial imports with error handling
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

from src.accessibility.components.accessible_components import (
    accessible_button, accessible_selectbox, accessible_text_input
)
from src.accessibility.core import AccessibilityManager
from src.data.loaders.raster_loader import get_raster_loader
from src.data.loaders.mapbiomas_loader import get_mapbiomas_loader, MAPBIOMAS_CLASS_NAMES, MAPBIOMAS_COLORS
from src.core.geospatial_analysis import get_geospatial_analyzer
from src.utils.logging_config import get_logger
from config.settings import settings

# Import V1 design system
from src.ui.components.design_system import (
    render_page_header,
    render_section_header,
    render_info_banner
)

logger = get_logger(__name__)


class AdvancedRasterAnalysisPage:
    """Advanced raster analysis interface with professional MapBiomas tools"""

    def __init__(self):
        """Initialize the advanced raster analysis page"""
        self.accessibility_manager = AccessibilityManager()
        self.raster_loader = get_raster_loader()
        self.mapbiomas_loader = get_mapbiomas_loader()
        self.geospatial_analyzer = get_geospatial_analyzer()
        self.logger = get_logger(self.__class__.__name__)

    def render(self):
        """Render the advanced raster analysis page"""
        # Initialize accessibility
        self.accessibility_manager.initialize()

        # Page header with accessibility
        self.accessibility_manager.create_accessible_heading(
            "🛰️ Análise Avançada de Dados de Satélite",
            level=1
        )

        st.markdown("**Análise profissional de uso e cobertura do solo com dados MapBiomas**")

        # Check for raster availability
        available_rasters = self.raster_loader.list_available_rasters()
        if not available_rasters:
            self._render_no_data_message()
            return

        # Main interface
        self._render_analysis_interface()

    def _render_no_data_message(self):
        """Render message when no raster data is available"""
        st.warning("⚠️ Nenhum arquivo raster encontrado")

        with st.expander("🔧 Como configurar dados raster"):
            st.markdown("""
            **Para usar a análise avançada de satélite:**

            1. **Adicione arquivos raster** no diretório `data/rasters/`
            2. **Formatos suportados**: .tif, .tiff (GeoTIFF)
            3. **Dados recomendados**: MapBiomas Agropecuária
            4. **Recarregue a página** após adicionar os arquivos

            **Fontes de dados sugeridas:**
            - MapBiomas: https://mapbiomas.org/
            - INPE: http://www.dpi.inpe.br/
            - IBGE Geociências: https://www.ibge.gov.br/geociencias/
            """)

    def _render_analysis_interface(self):
        """Render the main analysis interface"""
        # Create main layout
        col_controls, col_map = st.columns([1, 2])

        with col_controls:
            analysis_controls = self._render_control_panel()

        with col_map:
            if analysis_controls.get('raster_path'):
                map_results = self._render_analysis_map(analysis_controls)

                # Display analysis results below map
                if map_results.get('analysis_results'):
                    self._render_detailed_results(map_results['analysis_results'])

    def _render_control_panel(self) -> Dict[str, Any]:
        """Render the analysis control panel"""
        controls = {}

        # Raster file selection
        st.markdown("### 🛰️ Seleção de Dados")

        available_rasters = self.raster_loader.list_available_rasters()
        raster_options = {
            f"{r['filename']} ({r['size_mb']}MB)": r['path']
            for r in available_rasters
        }

        selected_raster = accessible_selectbox(
            "Arquivo de Satélite:",
            list(raster_options.keys()),
            help_text="Selecione o arquivo de dados de satélite para análise"
        )

        if selected_raster:
            controls['raster_path'] = raster_options[selected_raster]
            controls['raster_filename'] = selected_raster.split(' (')[0]

            # MapBiomas class selection for agricultural files
            is_mapbiomas = any(keyword in selected_raster.lower()
                             for keyword in ['mapbiomas', 'agropecuaria'])

            if is_mapbiomas:
                st.markdown("### 🌾 Classes de Uso do Solo")
                controls.update(self._render_class_selection())

            # Analysis parameters
            st.markdown("### 🔬 Parâmetros de Análise")
            controls.update(self._render_analysis_parameters())

            # Visualization options
            st.markdown("### 🎨 Visualização")
            controls.update(self._render_visualization_options())

        return controls

    def _render_class_selection(self) -> Dict[str, Any]:
        """Render MapBiomas class selection interface"""
        controls = {}

        # Class selection mode
        selection_mode = accessible_selectbox(
            "Modo de Seleção:",
            ["Todas as Classes", "Seleção Personalizada", "Grupos Temáticos"],
            help_text="Escolha como selecionar as classes de uso do solo"
        )

        if selection_mode == "Todas as Classes":
            controls['selected_classes'] = None
            st.info("📊 Analisando todas as classes disponíveis")

        elif selection_mode == "Seleção Personalizada":
            selected_classes = []

            # Group classes by type
            pasture_classes = [15]
            forestry_classes = [9]
            temporary_classes = [39, 20, 40, 62, 41]
            perennial_classes = [46, 47, 35, 48]

            # Pasture
            if st.checkbox("🐄 Pastagem", value=True):
                selected_classes.extend(pasture_classes)

            # Forestry
            if st.checkbox("🌲 Silvicultura", value=True):
                selected_classes.extend(forestry_classes)

            # Temporary crops
            st.markdown("**Lavouras Temporárias:**")
            temp_options = {
                39: "Soja", 20: "Cana-de-açúcar", 40: "Arroz",
                62: "Algodão", 41: "Outras Temporárias"
            }
            for class_id, name in temp_options.items():
                if st.checkbox(f"  {name}", key=f"temp_{class_id}"):
                    selected_classes.append(class_id)

            # Perennial crops
            st.markdown("**Lavouras Perenes:**")
            peren_options = {
                46: "Café", 47: "Citros", 35: "Dendê", 48: "Outras Perenes"
            }
            for class_id, name in peren_options.items():
                if st.checkbox(f"  {name}", key=f"peren_{class_id}"):
                    selected_classes.append(class_id)

            controls['selected_classes'] = selected_classes if selected_classes else None

        else:  # Grupos Temáticos
            thematic_groups = {
                "Pecuária": [15],
                "Agricultura Anual": [39, 20, 40, 62, 41],
                "Agricultura Perene": [46, 47, 35, 48],
                "Silvicultura": [9]
            }

            selected_group = accessible_selectbox(
                "Grupo Temático:",
                list(thematic_groups.keys()),
                help_text="Selecione um grupo temático para análise"
            )

            if selected_group:
                controls['selected_classes'] = thematic_groups[selected_group]
                st.info(f"📊 Analisando: {selected_group}")

        return controls

    def _render_analysis_parameters(self) -> Dict[str, Any]:
        """Render analysis parameter controls"""
        controls = {}

        # Analysis mode
        analysis_mode = accessible_selectbox(
            "Modo de Análise:",
            ["Análise por Clique", "Análise por Região", "Análise Comparativa"],
            help_text="Selecione o tipo de análise a ser realizada"
        )
        controls['analysis_mode'] = analysis_mode

        # Radius for click analysis
        if analysis_mode in ["Análise por Clique", "Análise por Região"]:
            radius = st.slider(
                "Raio de Análise (km):",
                min_value=1.0,
                max_value=100.0,
                value=10.0,
                step=1.0,
                help="Defina o raio da área de análise"
            )
            controls['analysis_radius'] = radius

        # Statistical options
        st.markdown("**Estatísticas:**")
        controls['calculate_statistics'] = st.checkbox("Calcular estatísticas detalhadas", value=True)
        controls['generate_charts'] = st.checkbox("Gerar gráficos", value=True)
        controls['area_calculations'] = st.checkbox("Cálculos de área (hectares)", value=True)

        return controls

    def _render_visualization_options(self) -> Dict[str, Any]:
        """Render visualization option controls"""
        controls = {}

        # Map base layer
        controls['basemap'] = accessible_selectbox(
            "Mapa Base:",
            ['OpenStreetMap', 'Satellite', 'CartoDB positron', 'CartoDB dark_matter'],
            help_text="Escolha o estilo do mapa base"
        )

        # Layer opacity
        controls['opacity'] = st.slider(
            "Transparência da Camada:",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Ajuste a transparência da camada raster"
        )

        # Color scheme for non-MapBiomas data
        controls['color_scheme'] = accessible_selectbox(
            "Esquema de Cores:",
            ['viridis', 'plasma', 'inferno', 'magma', 'terrain'],
            help_text="Esquema de cores para dados não-MapBiomas"
        )

        return controls

    def _render_analysis_map(self, controls: Dict[str, Any]) -> Dict[str, Any]:
        """Render the analysis map"""
        if not HAS_FOLIUM:
            st.error("⚠️ Biblioteca folium necessária para visualização de mapas")
            return {}

        try:
            # Load raster data
            data, metadata = self.raster_loader.load_raster(
                controls['raster_path'],
                max_size=settings.MAX_RASTER_SIZE
            )

            if data is None or metadata is None:
                st.error("❌ Erro ao carregar dados raster")
                return {}

            # Create map
            center_lat, center_lon = settings.DEFAULT_CENTER
            tiles_map = {
                'OpenStreetMap': 'OpenStreetMap',
                'Satellite': ('https://server.arcgisonline.com/ArcGIS/rest/services/'
                             'World_Imagery/MapServer/tile/{z}/{y}/{x}'),
                'CartoDB positron': 'CartoDB positron',
                'CartoDB dark_matter': 'CartoDB dark_matter'
            }

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=8,
                tiles=tiles_map.get(controls['basemap'], 'OpenStreetMap')
            )

            # Add raster overlay
            self._add_enhanced_raster_overlay(m, data, metadata, controls)

            # Add analysis instructions
            if controls['analysis_mode'] == "Análise por Clique":
                instruction_html = """
                <div style="position: fixed; top: 10px; left: 10px; width: 300px;
                           background: white; border: 2px solid #007acc; z-index: 9999;
                           padding: 10px; border-radius: 5px; font-size: 12px;">
                    <h4 style="margin-top: 0; color: #007acc;">🔬 Análise Ativa</h4>
                    <p>Clique no mapa para analisar uso do solo na área selecionada.</p>
                </div>
                """
                m.get_root().html.add_child(folium.Element(instruction_html))

            # Render map
            map_data = st_folium(
                m,
                key="advanced_raster_map",
                width=None,
                height=600,
                returned_objects=["last_clicked", "last_object_clicked"]
            )

            # Process click analysis
            analysis_results = None
            if (controls['analysis_mode'] == "Análise por Clique" and
                map_data['last_clicked'] and controls.get('raster_path')):

                click_lat = map_data['last_clicked']['lat']
                click_lon = map_data['last_clicked']['lng']

                analysis_results = self._perform_advanced_analysis(
                    controls['raster_path'],
                    click_lat,
                    click_lon,
                    controls.get('analysis_radius', 10.0),
                    controls
                )

            return {
                'map_data': map_data,
                'analysis_results': analysis_results
            }

        except Exception as e:
            self.logger.error(f"Error rendering analysis map: {e}")
            st.error("❌ Erro ao renderizar mapa de análise")
            return {}

    def _add_enhanced_raster_overlay(self, map_obj, data, metadata, controls):
        """Add enhanced raster overlay to map"""
        try:
            # Check if MapBiomas file
            is_mapbiomas = any(keyword in controls['raster_filename'].lower()
                             for keyword in ['mapbiomas', 'agropecuaria'])

            if is_mapbiomas:
                # Use MapBiomas overlay
                overlay = self.mapbiomas_loader.create_folium_overlay(
                    data, metadata,
                    selected_classes=controls.get('selected_classes'),
                    opacity=controls['opacity']
                )

                if overlay:
                    # Create feature group
                    raster_group = folium.FeatureGroup(
                        name=f"MapBiomas - {controls['raster_filename'][:30]}...",
                        show=True
                    )
                    overlay.add_to(raster_group)
                    raster_group.add_to(map_obj)

                    # Add enhanced legend
                    self._add_enhanced_legend(map_obj, controls.get('selected_classes'))
            else:
                # Generic raster overlay
                img_base64 = self.raster_loader.create_base64_image(data, metadata)
                if img_base64:
                    bounds = metadata['bounds']
                    folium_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

                    overlay = folium.raster_layers.ImageOverlay(
                        image=img_base64,
                        bounds=folium_bounds,
                        opacity=controls['opacity']
                    )
                    overlay.add_to(map_obj)

            # Add layer control
            folium.LayerControl().add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding raster overlay: {e}")

    def _add_enhanced_legend(self, map_obj, selected_classes):
        """Add enhanced legend for MapBiomas data"""
        try:
            if selected_classes is None:
                selected_classes = list(MAPBIOMAS_CLASS_NAMES.keys())

            legend_items = []
            for class_id in selected_classes:
                if class_id in MAPBIOMAS_CLASS_NAMES:
                    color = MAPBIOMAS_COLORS.get(class_id, '#CCCCCC')
                    name = MAPBIOMAS_CLASS_NAMES[class_id]['pt']
                    legend_items.append(f'<li><span style="color:{color};">■</span> {name}</li>')

            legend_html = f"""
            <div style="position: fixed; bottom: 50px; right: 50px; width: 250px;
                       background: rgba(255,255,255,0.95); border: 2px solid #007acc;
                       z-index: 9999; padding: 15px; border-radius: 10px;
                       box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <h4 style="margin-top: 0; color: #007acc; text-align: center;">
                    🌾 Classes MapBiomas
                </h4>
                <ul style="list-style: none; padding: 0; margin: 0; font-size: 12px;">
                    {''.join(legend_items)}
                </ul>
                <p style="text-align: center; margin-top: 10px; font-size: 10px;
                         color: #666;">Dados: MapBiomas Brasil</p>
            </div>
            """
            map_obj.get_root().html.add_child(folium.Element(legend_html))

        except Exception as e:
            self.logger.error(f"Error adding legend: {e}")

    def _perform_advanced_analysis(self, raster_path, lat, lon, radius_km, controls):
        """Perform advanced raster analysis"""
        try:
            # Check if MapBiomas file
            is_mapbiomas = any(keyword in Path(raster_path).name.lower()
                             for keyword in ['mapbiomas', 'agropecuaria'])

            if is_mapbiomas:
                # Advanced MapBiomas analysis
                results = self.mapbiomas_loader.analyze_radius_area(
                    raster_path, lat, lon, radius_km
                )

                # Add enhanced statistics if requested
                if controls.get('calculate_statistics'):
                    results = self._enhance_mapbiomas_results(results, controls)

            else:
                # Generic analysis
                results = self.geospatial_analyzer.analyze_raster_in_circle(
                    raster_path, lat, lon, radius_km
                )

            return results

        except Exception as e:
            self.logger.error(f"Error in advanced analysis: {e}")
            return {}

    def _enhance_mapbiomas_results(self, results, controls):
        """Enhance MapBiomas results with additional statistics"""
        try:
            if not results or '_metadata' not in results:
                return results

            metadata = results['_metadata']
            total_area = metadata.get('total_analyzed_area_ha', 0)

            # Calculate additional metrics
            enhanced_results = {}

            for class_name, data in results.items():
                if not class_name.startswith('_') and isinstance(data, dict):
                    enhanced_data = data.copy()

                    # Add productivity estimates (simplified)
                    if 'area_ha' in enhanced_data:
                        area_ha = enhanced_data['area_ha']

                        # Estimate biogas potential based on land use
                        biogas_potential = self._estimate_biogas_potential(class_name, area_ha)
                        enhanced_data['estimated_biogas_m3_year'] = biogas_potential

                        # Economic value estimate
                        economic_value = self._estimate_economic_value(class_name, area_ha)
                        enhanced_data['estimated_value_brl'] = economic_value

                    enhanced_results[class_name] = enhanced_data

            # Preserve metadata
            enhanced_results['_metadata'] = metadata
            return enhanced_results

        except Exception as e:
            self.logger.error(f"Error enhancing results: {e}")
            return results

    def _estimate_biogas_potential(self, class_name, area_ha):
        """Estimate biogas potential for different land uses"""
        # Simplified biogas potential estimates (m³/ha/year)
        biogas_factors = {
            'Pastagem': 500,  # From animal waste
            'Soja': 100,      # Crop residues
            'Cana-de-açúcar': 800,  # Bagasse and vinasse
            'Arroz': 200,     # Rice straw
            'Algodão': 150,   # Cotton residues
            'Café': 300,      # Coffee pulp
            'Citros': 250     # Citrus waste
        }

        factor = biogas_factors.get(class_name, 50)  # Default low value
        return area_ha * factor

    def _estimate_economic_value(self, class_name, area_ha):
        """Estimate economic value for different land uses"""
        # Simplified economic values (BRL/ha/year)
        economic_factors = {
            'Pastagem': 800,
            'Soja': 3000,
            'Cana-de-açúcar': 2500,
            'Arroz': 2000,
            'Algodão': 3500,
            'Café': 4000,
            'Citros': 3000
        }

        factor = economic_factors.get(class_name, 500)  # Default value
        return area_ha * factor

    def _render_detailed_results(self, results):
        """Render detailed analysis results"""
        if not results:
            return

        st.markdown("---")
        self.accessibility_manager.create_accessible_heading(
            "📊 Resultados da Análise Avançada",
            level=2
        )

        # Metadata display
        if '_metadata' in results:
            metadata = results['_metadata']

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Centro da Análise",
                    f"{metadata.get('center_lat', 0):.4f}°, {metadata.get('center_lon', 0):.4f}°"
                )

            with col2:
                st.metric(
                    "Raio Analisado",
                    f"{metadata.get('radius_km', 0):.1f} km"
                )

            with col3:
                st.metric(
                    "Área Total",
                    f"{metadata.get('total_analyzed_area_ha', 0):.1f} ha"
                )

            with col4:
                total_biogas = sum(
                    data.get('estimated_biogas_m3_year', 0)
                    for key, data in results.items()
                    if not key.startswith('_') and isinstance(data, dict)
                )
                st.metric(
                    "Potencial Biogás",
                    f"{total_biogas:,.0f} m³/ano"
                )

        # Class results table
        class_results = {k: v for k, v in results.items() if not k.startswith('_')}

        if class_results:
            # Create comprehensive results table
            display_data = []

            for class_name, data in class_results.items():
                if isinstance(data, dict) and 'area_ha' in data:
                    row = {
                        'Classe': class_name,
                        'Área (ha)': f"{data['area_ha']:.1f}",
                        'Percentual (%)': f"{data.get('percentage', 0):.1f}",
                        'Pixels': f"{data.get('pixel_count', 0):,}",
                        'Biogás Estimado (m³/ano)': f"{data.get('estimated_biogas_m3_year', 0):,.0f}",
                        'Valor Econômico (R$/ano)': f"R$ {data.get('estimated_value_brl', 0):,.0f}"
                    }
                    display_data.append(row)

            if display_data:
                df_display = pd.DataFrame(display_data)
                st.dataframe(df_display, width='stretch')

                # Export options
                col1, col2 = st.columns(2)

                with col1:
                    if accessible_button("📥 Exportar CSV"):
                        csv = df_display.to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            key="download_raster_csv",
                            label="⬇️ Download CSV",
                            data=csv,
                            file_name=f"analise_raster_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

                with col2:
                    if accessible_button("📋 Relatório Detalhado"):
                        report = self._generate_detailed_report(results, display_data)
                        st.download_button(
                            key="download_raster_report",
                            label="⬇️ Download Relatório",
                            data=report,
                            file_name=f"relatorio_analise_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

    def _generate_detailed_report(self, results, display_data):
        """Generate detailed analysis report"""
        try:
            metadata = results.get('_metadata', {})

            report = f"""
RELATÓRIO DE ANÁLISE DE DADOS DE SATÉLITE
CP2B Maps - Análise Avançada MapBiomas

Data: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}

=== PARÂMETROS DA ANÁLISE ===
Centro: {metadata.get('center_lat', 0):.6f}°, {metadata.get('center_lon', 0):.6f}°
Raio: {metadata.get('radius_km', 0)} km
Área Total Analisada: {metadata.get('total_analyzed_area_ha', 0):.2f} hectares

=== RESULTADOS POR CLASSE ===
"""

            for row in display_data:
                report += f"""
Classe: {row['Classe']}
  - Área: {row['Área (ha)']} ha
  - Percentual: {row['Percentual (%)']}%
  - Pixels: {row['Pixels']}
  - Potencial Biogás: {row['Biogás Estimado (m³/ano)']} m³/ano
  - Valor Econômico: {row['Valor Econômico (R$/ano)']}
"""

            # Calculate totals
            total_biogas = sum(float(row['Biogás Estimado (m³/ano)'].replace(',', ''))
                             for row in display_data)
            total_economic = sum(float(row['Valor Econômico (R$/ano)'].replace('R$ ', '').replace(',', ''))
                               for row in display_data)

            report += f"""

=== TOTAIS ===
Potencial Total de Biogás: {total_biogas:,.0f} m³/ano
Valor Econômico Total: R$ {total_economic:,.0f}/ano

=== OBSERVAÇÕES ===
- Estimativas baseadas em fatores médios da literatura
- Valores podem variar conforme práticas locais
- Análise preliminar para planejamento
- Recomenda-se estudos detalhados para implementação

Gerado pelo CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas
"""

            return report

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return "Erro ao gerar relatório"


def render_advanced_raster_analysis_page():
    """Render the advanced raster analysis page with V1 styling"""
    # Add beautiful header
    render_page_header(
        title="Análise Avançada de Satélite",
        subtitle="Dados MapBiomas e Análise Geoespacial",
        description="Análise profissional de dados de satélite com ferramentas avançadas de visualização e estatísticas",
        icon="🛰️",
        show_stats=True
    )

    page = AdvancedRasterAnalysisPage()
    page.render()


# For direct testing
if __name__ == "__main__":
    render_advanced_raster_analysis_page()