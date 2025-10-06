"""
CP2B Maps - Professional Raster Map Viewer Component
Advanced UI component for raster data visualization and analysis
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import pandas as pd

# Geospatial imports with error handling
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
from src.data.loaders.raster_loader import get_raster_loader
from src.data.loaders.mapbiomas_loader import get_mapbiomas_loader, MAPBIOMAS_CLASS_NAMES
from src.core.geospatial_analysis import get_geospatial_analyzer

logger = get_logger(__name__)


class RasterMapViewer:
    """
    Professional raster map viewer with interactive controls
    Features: Layer management, class selection, analysis tools, export capabilities
    """

    def __init__(self):
        """Initialize RasterMapViewer"""
        self.logger = get_logger(self.__class__.__name__)
        self.raster_loader = get_raster_loader()
        self.mapbiomas_loader = get_mapbiomas_loader()
        self.geospatial_analyzer = get_geospatial_analyzer()

        if not HAS_FOLIUM:
            self.logger.error("Folium not available - map functionality disabled")

    def render(self, municipality_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Render the complete raster map viewer interface

        Args:
            municipality_data: Optional municipality data for overlay

        Returns:
            Dictionary with map state and user interactions
        """
        if not HAS_FOLIUM:
            st.error("⚠️ Map functionality requires folium library")
            return {}

        try:
            st.markdown("## 🗺️ Advanced Raster Analysis")

            # Create layout columns
            col1, col2 = st.columns([1, 3])

            with col1:
                # Render control panel
                map_controls = self._render_control_panel()

            with col2:
                # Render map
                map_state = self._render_map(map_controls, municipality_data)

            # Render analysis results if available
            if map_state.get('analysis_results'):
                self._render_analysis_results(map_state['analysis_results'])

            return {
                'map_controls': map_controls,
                'map_state': map_state,
                'last_clicked': map_state.get('last_clicked')
            }

        except Exception as e:
            self.logger.error(f"Error rendering raster map viewer: {e}")
            st.error("⚠️ Error rendering map viewer")
            return {}

    def _render_control_panel(self) -> Dict[str, Any]:
        """
        Render the map control panel

        Returns:
            Dictionary with control settings
        """
        controls = {}

        st.markdown("### 🎛️ Map Controls")

        # Raster file selection
        available_rasters = self.raster_loader.list_available_rasters()
        mapbiomas_files = self.mapbiomas_loader.get_available_mapbiomas_files()

        if available_rasters:
            raster_options = {f"{r['filename']} ({r['size_mb']}MB)": r['path']
                            for r in available_rasters}

            selected_raster = st.selectbox(
                "📊 Select Raster Layer:",
                options=list(raster_options.keys()),
                help="Choose a raster file for analysis"
            )
            controls['raster_path'] = raster_options.get(selected_raster)
            controls['raster_filename'] = selected_raster.split(' (')[0] if selected_raster else None
        else:
            st.warning("⚠️ No raster files found in data/rasters/")
            st.info("""
            **Para usar a análise raster:**
            1. Adicione arquivos .tif ou .tiff no diretório `data/rasters/`
            2. Dados MapBiomas e imagens de satélite são suportados
            3. Recarregue a página após adicionar os arquivos
            """)

            # Show data directory path
            raster_dir = self.raster_loader.raster_dir
            st.code(f"Diretório de rasters: {raster_dir}")

            controls['raster_path'] = None
            controls['raster_filename'] = None

        # MapBiomas class selection (if MapBiomas file selected)
        is_mapbiomas = (controls['raster_filename'] and
                       any(keyword in controls['raster_filename'].lower()
                           for keyword in ['mapbiomas', 'agropecuaria']))

        if is_mapbiomas:
            st.markdown("#### 🌾 Agricultural Classes")

            # All classes checkbox
            select_all = st.checkbox("Select All Classes", value=True)

            if select_all:
                selected_classes = list(MAPBIOMAS_CLASS_NAMES.keys())
            else:
                selected_classes = []

                # Individual class selection
                for class_id, names in MAPBIOMAS_CLASS_NAMES.items():
                    class_name = names['pt']
                    color = self.mapbiomas_loader.get_class_color(class_id)

                    if st.checkbox(
                        f"🎨 {class_name}",
                        key=f"class_{class_id}",
                        help=f"Class ID: {class_id}, Color: {color}"
                    ):
                        selected_classes.append(class_id)

            controls['selected_classes'] = selected_classes if not select_all else None
        else:
            controls['selected_classes'] = None

        # Layer opacity
        controls['opacity'] = st.slider(
            "🔍 Layer Opacity:",
            min_value=0.1,
            max_value=1.0,
            value=settings.RASTER_OPACITY_DEFAULT,
            step=0.1,
            help="Adjust raster layer transparency"
        )

        # Analysis tools
        st.markdown("#### 🔬 Analysis Tools")

        controls['enable_analysis'] = st.checkbox(
            "Enable Radius Analysis",
            help="Click on map to analyze area within radius"
        )

        if controls['enable_analysis']:
            controls['analysis_radius'] = st.slider(
                "📏 Analysis Radius (km):",
                min_value=1.0,
                max_value=100.0,
                value=settings.DEFAULT_ANALYSIS_RADIUS_KM,
                step=1.0
            )
        else:
            controls['analysis_radius'] = None

        # Map base layer
        controls['basemap'] = st.selectbox(
            "🗺️ Base Map:",
            options=['OpenStreetMap', 'CartoDB positron', 'CartoDB dark_matter', 'Satellite'],
            help="Choose base map style"
        )

        return controls

    def _render_map(self, controls: Dict[str, Any], municipality_data: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """
        Render the interactive map

        Args:
            controls: Map control settings
            municipality_data: Optional municipality data

        Returns:
            Map state dictionary
        """
        try:
            # Create base map
            center_lat, center_lon = settings.DEFAULT_CENTER

            # Set base map tiles
            tiles_map = {
                'OpenStreetMap': 'OpenStreetMap',
                'CartoDB positron': 'CartoDB positron',
                'CartoDB dark_matter': 'CartoDB dark_matter',
                'Satellite': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            }

            tiles = tiles_map.get(controls['basemap'], 'OpenStreetMap')

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=settings.DEFAULT_ZOOM,
                tiles=tiles,
                attr='CP2B Maps' if controls['basemap'] == 'Satellite' else None
            )

            # Add raster layer if selected
            if controls['raster_path']:
                self._add_raster_layer(m, controls)

            # Add municipality data if provided
            if municipality_data is not None:
                self._add_municipality_layer(m, municipality_data)

            # Add analysis tools
            if controls['enable_analysis']:
                self._add_analysis_tools(m)

            # Render map with Streamlit
            map_data = st_folium(
                m,
                key="raster_map",
                width=None,
                height=600,
                returned_objects=["last_clicked", "last_object_clicked"]
            )

            # Process map interactions
            analysis_results = None
            if (controls['enable_analysis'] and
                map_data['last_clicked'] and
                controls['raster_path']):

                click_lat = map_data['last_clicked']['lat']
                click_lon = map_data['last_clicked']['lng']

                analysis_results = self._perform_analysis(
                    controls['raster_path'],
                    click_lat,
                    click_lon,
                    controls['analysis_radius']
                )

            return {
                'map_data': map_data,
                'analysis_results': analysis_results,
                'last_clicked': map_data.get('last_clicked')
            }

        except Exception as e:
            self.logger.error(f"Error rendering map: {e}")
            st.error("⚠️ Error rendering map")
            return {}

    def _add_raster_layer(self, map_obj, controls: Dict[str, Any]) -> None:
        """Add raster layer to map"""
        try:
            # Load raster data
            data, metadata = self.raster_loader.load_raster(
                controls['raster_path'],
                max_size=settings.MAX_RASTER_SIZE
            )

            if data is None or metadata is None:
                st.warning(f"⚠️ Failed to load raster: {controls['raster_filename']}")
                return

            # Check if it's a MapBiomas file
            is_mapbiomas = any(keyword in controls['raster_filename'].lower()
                             for keyword in ['mapbiomas', 'agropecuaria'])

            if is_mapbiomas:
                # Use MapBiomas processing
                overlay = self.mapbiomas_loader.create_folium_overlay(
                    data, metadata,
                    selected_classes=controls['selected_classes'],
                    opacity=controls['opacity']
                )

                if overlay:
                    # Create feature group
                    raster_group = folium.FeatureGroup(
                        name=f"MapBiomas - {controls['raster_filename']}",
                        show=True
                    )
                    overlay.add_to(raster_group)
                    raster_group.add_to(map_obj)

                    # Add legend
                    legend_html = self.mapbiomas_loader.create_legend_html(
                        selected_classes=controls['selected_classes'],
                        language=settings.MAPBIOMAS_LEGEND_LANGUAGE
                    )
                    map_obj.get_root().html.add_child(folium.Element(legend_html))

            else:
                # Generic raster processing
                img_base64 = self.raster_loader.create_base64_image(data, metadata)

                if img_base64:
                    bounds = metadata['bounds']
                    folium_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

                    overlay = folium.raster_layers.ImageOverlay(
                        image=img_base64,
                        bounds=folium_bounds,
                        opacity=controls['opacity'],
                        interactive=True,
                        cross_origin=False,
                        zindex=1
                    )

                    # Create feature group
                    raster_group = folium.FeatureGroup(
                        name=f"Raster - {controls['raster_filename']}",
                        show=True
                    )
                    overlay.add_to(raster_group)
                    raster_group.add_to(map_obj)

            # Add layer control
            folium.LayerControl().add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding raster layer: {e}")
            st.warning("⚠️ Error adding raster layer to map")

    def _add_municipality_layer(self, map_obj, municipality_data: pd.DataFrame) -> None:
        """Add municipality data layer to map"""
        try:
            if 'lat' not in municipality_data.columns or 'lon' not in municipality_data.columns:
                return

            # Create municipality markers
            municipality_group = folium.FeatureGroup(name="Municipalities", show=True)

            for idx, row in municipality_data.iterrows():
                if pd.notna(row['lat']) and pd.notna(row['lon']):
                    # Create popup content
                    popup_text = f"<b>{row.get('nome_municipio', 'Unknown')}</b>"
                    if 'potencial_biogas_total' in row:
                        popup_text += f"<br>Biogas Potential: {row['potencial_biogas_total']:.1f} m³/ano"

                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=5,
                        popup=popup_text,
                        color='blue',
                        fillColor='lightblue',
                        fillOpacity=0.7
                    ).add_to(municipality_group)

            municipality_group.add_to(map_obj)

        except Exception as e:
            self.logger.error(f"Error adding municipality layer: {e}")

    def _add_analysis_tools(self, map_obj) -> None:
        """Add analysis tools to map"""
        try:
            # Add click instructions
            instruction_html = """
            <div style="
                position: fixed;
                top: 10px; left: 10px; width: 250px; height: auto;
                background-color: white; border: 2px solid #007acc; z-index: 9999;
                font-size: 12px; padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
            ">
            <h4 style="margin-top: 0; color: #007acc;">🔬 Analysis Mode</h4>
            <p style="margin: 5px 0;">Click anywhere on the map to analyze land use within the selected radius.</p>
            </div>
            """
            map_obj.get_root().html.add_child(folium.Element(instruction_html))

        except Exception as e:
            self.logger.error(f"Error adding analysis tools: {e}")

    def _perform_analysis(self, raster_path: str, lat: float, lon: float, radius_km: float) -> Dict[str, Any]:
        """
        Perform raster analysis at clicked location

        Args:
            raster_path: Path to raster file
            lat: Click latitude
            lon: Click longitude
            radius_km: Analysis radius

        Returns:
            Analysis results dictionary
        """
        try:
            # Check if it's a MapBiomas file
            is_mapbiomas = any(keyword in Path(raster_path).name.lower()
                             for keyword in ['mapbiomas', 'agropecuaria'])

            if is_mapbiomas:
                # Use MapBiomas analysis
                results = self.mapbiomas_loader.analyze_radius_area(
                    raster_path, lat, lon, radius_km
                )
            else:
                # Use generic geospatial analysis
                results = self.geospatial_analyzer.analyze_raster_in_circle(
                    raster_path, lat, lon, radius_km
                )

            if results:
                self.logger.info(f"Analysis completed at ({lat:.4f}, {lon:.4f}) with {radius_km}km radius")

            return results

        except Exception as e:
            self.logger.error(f"Error performing analysis: {e}")
            return {}

    def _render_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        Render analysis results panel

        Args:
            results: Analysis results dictionary
        """
        try:
            if not results:
                return

            st.markdown("---")
            st.markdown("### 📊 Analysis Results")

            # Display metadata if available
            if '_metadata' in results:
                metadata = results['_metadata']
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Analysis Center",
                        f"{metadata.get('center_lat', 0):.4f}, {metadata.get('center_lon', 0):.4f}"
                    )

                with col2:
                    st.metric(
                        "Radius",
                        f"{metadata.get('radius_km', 0)} km"
                    )

                with col3:
                    st.metric(
                        "Total Area",
                        f"{metadata.get('total_analyzed_area_ha', 0):.1f} ha"
                    )

            # Display class results
            class_results = {k: v for k, v in results.items() if not k.startswith('_')}

            if class_results:
                st.markdown("#### 🌾 Land Use Classes")

                # Create DataFrame for display
                display_data = []
                for class_name, data in class_results.items():
                    if isinstance(data, dict) and 'area_ha' in data:
                        display_data.append({
                            'Class': class_name,
                            'Area (ha)': f"{data['area_ha']:.1f}",
                            'Percentage': f"{data.get('percentage', 0):.1f}%",
                            'Pixels': data.get('pixel_count', 0)
                        })

                if display_data:
                    df_display = pd.DataFrame(display_data)
                    st.dataframe(df_display, use_container_width=True)

                    # Export option
                    if st.button("📥 Export Results"):
                        csv = df_display.to_csv(index=False)
                        st.download_button(
                            key="download_raster_viewer_csv",
                            label="Download CSV",
                            data=csv,
                            file_name=f"raster_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

        except Exception as e:
            self.logger.error(f"Error rendering analysis results: {e}")
            st.error("⚠️ Error displaying analysis results")


# Factory function for easy access
def create_raster_map_viewer() -> RasterMapViewer:
    """
    Create RasterMapViewer instance

    Returns:
        RasterMapViewer instance
    """
    return RasterMapViewer()