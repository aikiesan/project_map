"""
CP2B Maps - Enhanced Map Visualizations
Advanced visualization system with proportional circles, heat maps, and choropleth maps
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple

# Geospatial imports with error handling
try:
    import folium
    from folium import plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    folium = None
    plugins = None

# Visualization imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.colors import LinearSegmentedColormap
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from src.accessibility.core import AccessibilityManager
from src.accessibility.components.accessible_components import accessible_selectbox, accessible_button
from src.utils.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class EnhancedMapVisualizations:
    """
    Professional enhanced map visualization system
    Features: Multiple visualization types, interactive controls, accessibility compliance
    """

    def __init__(self):
        """Initialize enhanced map visualizations"""
        self.accessibility_manager = AccessibilityManager()
        self.logger = get_logger(self.__class__.__name__)

    def create_enhanced_map(self, data: pd.DataFrame, visualization_type: str,
                           config: Dict[str, Any]) -> Optional[folium.Map]:
        """
        Create enhanced map with specified visualization type

        Args:
            data: Municipality data with lat/lon
            visualization_type: Type of visualization
            config: Visualization configuration

        Returns:
            Folium map object or None
        """
        if not HAS_FOLIUM:
            self.logger.error("Folium library required for map visualizations")
            return None

        try:
            # Create base map
            center_lat = config.get('center_lat', settings.DEFAULT_CENTER[0])
            center_lon = config.get('center_lon', settings.DEFAULT_CENTER[1])
            zoom = config.get('zoom', settings.DEFAULT_ZOOM)

            # Base map style
            tiles_map = {
                'OpenStreetMap': 'OpenStreetMap',
                'CartoDB Positron': 'CartoDB positron',
                'CartoDB Dark Matter': 'CartoDB dark_matter',
                'Satellite': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            }

            tiles = tiles_map.get(config.get('basemap', 'OpenStreetMap'), 'OpenStreetMap')

            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom,
                tiles=tiles,
                attr='CP2B Maps' if config.get('basemap') == 'Satellite' else None
            )

            # Apply visualization based on type
            if visualization_type == "Proportional Circles":
                self._add_proportional_circles(m, data, config)
            elif visualization_type == "Heat Map":
                self._add_heat_map(m, data, config)
            elif visualization_type == "Choropleth":
                self._add_choropleth_map(m, data, config)
            elif visualization_type == "Cluster Map":
                self._add_cluster_map(m, data, config)
            elif visualization_type == "Density Contours":
                self._add_density_contours(m, data, config)
            elif visualization_type == "Graduated Symbols":
                self._add_graduated_symbols(m, data, config)

            # Add legend and controls
            self._add_enhanced_controls(m, visualization_type, config)

            return m

        except Exception as e:
            self.logger.error(f"Error creating enhanced map: {e}")
            return None

    def _add_proportional_circles(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add proportional circles visualization"""
        try:
            # Get the metric for circle sizing
            metric_column = config.get('metric_column', 'potencial_biogas_total')
            min_radius = config.get('min_radius', 5)
            max_radius = config.get('max_radius', 30)
            opacity = config.get('opacity', 0.7)
            color_scheme = config.get('color_scheme', 'Blues')

            if metric_column not in data.columns:
                self.logger.warning(f"Metric column {metric_column} not found in data")
                return

            # Normalize values for circle sizes
            values = data[metric_column].fillna(0)
            min_val, max_val = values.min(), values.max()

            if max_val > min_val:
                normalized_values = (values - min_val) / (max_val - min_val)
                radii = min_radius + (normalized_values * (max_radius - min_radius))
            else:
                radii = pd.Series([min_radius] * len(data), index=data.index)

            # Color mapping
            colors = self._get_color_palette(color_scheme, len(data))
            color_map = self._create_color_mapping(values, color_scheme)

            # Create feature group
            circle_group = folium.FeatureGroup(
                name=f"Círculos Proporcionais - {metric_column}",
                show=True
            )

            for idx, row in data.iterrows():
                if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                    # Circle color based on value
                    circle_color = color_map.get(idx, '#3388ff')

                    # Popup content
                    popup_content = self._create_detailed_popup(row, metric_column)

                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=radii[idx],
                        popup=folium.Popup(popup_content, max_width=300),
                        color='white',
                        weight=2,
                        fillColor=circle_color,
                        fillOpacity=opacity,
                        tooltip=f"{row.get('nome_municipio', 'Município')}: {row.get(metric_column, 0):,.0f}"
                    ).add_to(circle_group)

            circle_group.add_to(m)

            # Add proportional circles legend
            self._add_proportional_legend(m, min_val, max_val, min_radius, max_radius, metric_column)

        except Exception as e:
            self.logger.error(f"Error adding proportional circles: {e}")

    def _add_heat_map(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add heat map visualization"""
        try:
            metric_column = config.get('metric_column', 'potencial_biogas_total')
            intensity = config.get('intensity', 0.6)
            radius = config.get('heat_radius', 25)

            if metric_column not in data.columns:
                return

            # Prepare heat map data
            heat_data = []
            for idx, row in data.iterrows():
                if pd.notna(row.get('lat')) and pd.notna(row.get('lon')) and pd.notna(row.get(metric_column)):
                    # Normalize the metric value for heat intensity
                    intensity_value = max(0.1, min(1.0, row[metric_column] / data[metric_column].max()))
                    heat_data.append([row['lat'], row['lon'], intensity_value])

            if heat_data:
                # Create heat map
                heat_map = plugins.HeatMap(
                    heat_data,
                    min_opacity=0.2,
                    max_zoom=18,
                    radius=radius,
                    blur=15,
                    gradient={
                        0.0: 'blue',
                        0.3: 'cyan',
                        0.5: 'lime',
                        0.7: 'yellow',
                        1.0: 'red'
                    }
                )

                # Create feature group
                heat_group = folium.FeatureGroup(
                    name=f"Mapa de Calor - {metric_column}",
                    show=True
                )

                heat_map.add_to(heat_group)
                heat_group.add_to(m)

                # Add heat map legend
                self._add_heat_map_legend(m, metric_column)

        except Exception as e:
            self.logger.error(f"Error adding heat map: {e}")

    def _add_choropleth_map(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add choropleth map visualization"""
        try:
            metric_column = config.get('metric_column', 'potencial_biogas_total')
            color_scheme = config.get('color_scheme', 'YlOrRd')

            # For choropleth, we need polygon data
            # This is a simplified version using circle markers with color coding
            if metric_column not in data.columns:
                return

            values = data[metric_column].fillna(0)

            # Create color mapping
            if HAS_MATPLOTLIB:
                # Use matplotlib colormap
                cmap = plt.get_cmap(color_scheme)
                norm = mcolors.Normalize(vmin=values.min(), vmax=values.max())

                choropleth_group = folium.FeatureGroup(
                    name=f"Mapa Coroplético - {metric_column}",
                    show=True
                )

                for idx, row in data.iterrows():
                    if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                        # Get color for this value
                        rgba_color = cmap(norm(row[metric_column]))
                        hex_color = mcolors.to_hex(rgba_color)

                        popup_content = self._create_detailed_popup(row, metric_column)

                        folium.CircleMarker(
                            location=[row['lat'], row['lon']],
                            radius=15,
                            popup=folium.Popup(popup_content, max_width=300),
                            color='white',
                            weight=2,
                            fillColor=hex_color,
                            fillOpacity=0.7,
                            tooltip=f"{row.get('nome_municipio', 'Município')}: {row.get(metric_column, 0):,.0f}"
                        ).add_to(choropleth_group)

                choropleth_group.add_to(m)

                # Add choropleth legend
                self._add_choropleth_legend(m, values.min(), values.max(), color_scheme, metric_column)

        except Exception as e:
            self.logger.error(f"Error adding choropleth map: {e}")

    def _add_cluster_map(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add cluster map visualization"""
        try:
            from folium import plugins

            cluster_group = plugins.MarkerCluster(
                name="Agrupamentos de Municípios",
                show=True
            )

            metric_column = config.get('metric_column', 'potencial_biogas_total')

            for idx, row in data.iterrows():
                if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                    popup_content = self._create_detailed_popup(row, metric_column)

                    # Create marker with custom icon based on value
                    value = row.get(metric_column, 0)
                    icon_color = self._get_icon_color(value, data[metric_column])

                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{row.get('nome_municipio', 'Município')}: {value:,.0f}",
                        icon=folium.Icon(color=icon_color, icon='leaf', prefix='fa')
                    ).add_to(cluster_group)

            cluster_group.add_to(m)

        except Exception as e:
            self.logger.error(f"Error adding cluster map: {e}")

    def _add_density_contours(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add density contour visualization"""
        try:
            # This would require more advanced geospatial processing
            # For now, we'll create a simplified density visualization
            metric_column = config.get('metric_column', 'potencial_biogas_total')

            # Create density-based circles with varying opacity
            if metric_column not in data.columns:
                return

            values = data[metric_column].fillna(0)
            max_value = values.max()

            density_group = folium.FeatureGroup(
                name=f"Contornos de Densidade - {metric_column}",
                show=True
            )

            for idx, row in data.iterrows():
                if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                    # Density-based opacity and size
                    density_factor = row[metric_column] / max_value if max_value > 0 else 0
                    opacity = max(0.1, density_factor)
                    radius = 10 + (density_factor * 20)

                    folium.CircleMarker(
                        location=[row['lat'], row['lon']],
                        radius=radius,
                        color='#ff6b6b',
                        fillColor='#ff6b6b',
                        fillOpacity=opacity,
                        weight=1,
                        popup=f"{row.get('nome_municipio', 'Município')}: {row.get(metric_column, 0):,.0f}"
                    ).add_to(density_group)

            density_group.add_to(m)

        except Exception as e:
            self.logger.error(f"Error adding density contours: {e}")

    def _add_graduated_symbols(self, m: folium.Map, data: pd.DataFrame, config: Dict):
        """Add graduated symbols visualization"""
        try:
            metric_column = config.get('metric_column', 'potencial_biogas_total')
            symbol_type = config.get('symbol_type', 'circle')

            if metric_column not in data.columns:
                return

            values = data[metric_column].fillna(0)

            # Create size categories
            percentiles = np.percentile(values[values > 0], [25, 50, 75, 90])

            graduated_group = folium.FeatureGroup(
                name=f"Símbolos Graduados - {metric_column}",
                show=True
            )

            for idx, row in data.iterrows():
                if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
                    value = row[metric_column]

                    # Determine size and color based on percentiles
                    if value <= percentiles[0]:
                        size, color = 8, '#ffffcc'
                    elif value <= percentiles[1]:
                        size, color = 12, '#c7e9b4'
                    elif value <= percentiles[2]:
                        size, color = 16, '#7fcdbb'
                    elif value <= percentiles[3]:
                        size, color = 20, '#40b6c4'
                    else:
                        size, color = 25, '#2c7fb8'

                    popup_content = self._create_detailed_popup(row, metric_column)

                    if symbol_type == 'circle':
                        folium.CircleMarker(
                            location=[row['lat'], row['lon']],
                            radius=size,
                            popup=folium.Popup(popup_content, max_width=300),
                            color='white',
                            weight=2,
                            fillColor=color,
                            fillOpacity=0.8,
                            tooltip=f"{row.get('nome_municipio', 'Município')}: {value:,.0f}"
                        ).add_to(graduated_group)

            graduated_group.add_to(m)

            # Add graduated symbols legend
            self._add_graduated_legend(m, percentiles, metric_column)

        except Exception as e:
            self.logger.error(f"Error adding graduated symbols: {e}")

    def _create_detailed_popup(self, row: pd.Series, metric_column: str) -> str:
        """Create detailed popup content for markers"""
        try:
            municipality = row.get('nome_municipio', 'Município não identificado')
            main_value = row.get(metric_column, 0)

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: #2c7fb8; margin-bottom: 10px;">{municipality}</h4>

                <table style="font-size: 12px;">
                    <tr>
                        <td><strong>{metric_column}:</strong></td>
                        <td>{main_value:,.0f}</td>
                    </tr>
                    <tr>
                        <td><strong>População:</strong></td>
                        <td>{row.get('população', 0):,.0f}</td>
                    </tr>
                    <tr>
                        <td><strong>Área:</strong></td>
                        <td>{row.get('area_km2', 0):.1f} km²</td>
                    </tr>
                </table>

                <div style="margin-top: 10px; padding-top: 5px; border-top: 1px solid #ddd; font-size: 10px; color: #666;">
                    CP2B Maps - Análise de Biogás
                </div>
            </div>
            """
            return popup_html
        except:
            return f"<b>{row.get('nome_municipio', 'Município')}</b><br>Valor: {row.get(metric_column, 0):,.0f}"

    def _get_color_palette(self, scheme: str, n_colors: int) -> List[str]:
        """Get color palette for visualization"""
        try:
            if HAS_MATPLOTLIB:
                if scheme in ['Blues', 'Reds', 'Greens', 'YlOrRd', 'viridis', 'plasma']:
                    cmap = plt.get_cmap(scheme)
                    colors = [mcolors.to_hex(cmap(i / n_colors)) for i in range(n_colors)]
                    return colors
        except:
            pass

        # Fallback color palette
        return ['#3388ff', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']

    def _create_color_mapping(self, values: pd.Series, color_scheme: str) -> Dict:
        """Create color mapping for values"""
        try:
            colors = self._get_color_palette(color_scheme, len(values))
            # Sort values and assign colors
            sorted_indices = values.argsort()
            color_mapping = {}

            for i, idx in enumerate(sorted_indices):
                color_idx = int(i * (len(colors) - 1) / (len(values) - 1))
                color_mapping[idx] = colors[color_idx]

            return color_mapping
        except:
            return {}

    def _get_icon_color(self, value: float, values: pd.Series) -> str:
        """Get icon color based on value percentile"""
        try:
            percentile = (values < value).mean() * 100

            if percentile >= 90:
                return 'red'
            elif percentile >= 75:
                return 'orange'
            elif percentile >= 50:
                return 'yellow'
            elif percentile >= 25:
                return 'lightblue'
            else:
                return 'blue'
        except:
            return 'blue'

    def _add_enhanced_controls(self, m: folium.Map, viz_type: str, config: Dict):
        """Add enhanced controls to the map"""
        try:
            # Add layer control
            folium.LayerControl().add_to(m)

            # Add fullscreen button
            plugins.Fullscreen(
                position='topright',
                title='Expandir Tela Cheia',
                title_cancel='Sair da Tela Cheia',
                force_separate_button=True
            ).add_to(m)

            # Add measure control
            plugins.MeasureControl(
                primary_length_unit='kilometers',
                secondary_length_unit='meters',
                primary_area_unit='sqkilometers',
                secondary_area_unit='hectares',
                position='bottomleft'
            ).add_to(m)

        except Exception as e:
            self.logger.error(f"Error adding controls: {e}")

    def _add_proportional_legend(self, m: folium.Map, min_val: float, max_val: float,
                                min_radius: int, max_radius: int, metric: str):
        """Add proportional circles legend"""
        try:
            legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px;
                       background: rgba(255,255,255,0.9); border: 2px solid #007acc;
                       z-index: 9999; padding: 15px; border-radius: 10px;
                       box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <h4 style="margin-top: 0; color: #007acc; font-size: 14px;">
                    📊 Círculos Proporcionais
                </h4>
                <p style="margin: 5px 0; font-size: 12px;"><strong>{metric}</strong></p>
                <div style="text-align: center;">
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: {max_radius}px; height: {max_radius}px;
                                   border-radius: 50%; background: #3388ff; opacity: 0.7; vertical-align: middle;"></span>
                        <span style="font-size: 10px; margin-left: 5px;">{max_val:,.0f}</span>
                    </div>
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: {min_radius}px; height: {min_radius}px;
                                   border-radius: 50%; background: #3388ff; opacity: 0.7; vertical-align: middle;"></span>
                        <span style="font-size: 10px; margin-left: 5px;">{min_val:,.0f}</span>
                    </div>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
        except:
            pass

    def _add_heat_map_legend(self, m: folium.Map, metric: str):
        """Add heat map legend"""
        try:
            legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px;
                       background: rgba(255,255,255,0.9); border: 2px solid #007acc;
                       z-index: 9999; padding: 15px; border-radius: 10px;">
                <h4 style="margin-top: 0; color: #007acc; font-size: 14px;">
                    🔥 Mapa de Calor
                </h4>
                <p style="margin: 5px 0; font-size: 12px;"><strong>{metric}</strong></p>
                <div style="font-size: 10px;">
                    <div><span style="color: blue;">■</span> Baixo</div>
                    <div><span style="color: yellow;">■</span> Médio</div>
                    <div><span style="color: red;">■</span> Alto</div>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
        except:
            pass

    def _add_choropleth_legend(self, m: folium.Map, min_val: float, max_val: float,
                              color_scheme: str, metric: str):
        """Add choropleth legend"""
        try:
            legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px;
                       background: rgba(255,255,255,0.9); border: 2px solid #007acc;
                       z-index: 9999; padding: 15px; border-radius: 10px;">
                <h4 style="margin-top: 0; color: #007acc; font-size: 14px;">
                    🗺️ Mapa Coroplético
                </h4>
                <p style="margin: 5px 0; font-size: 12px;"><strong>{metric}</strong></p>
                <div style="font-size: 10px;">
                    <div>Min: {min_val:,.0f}</div>
                    <div>Max: {max_val:,.0f}</div>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
        except:
            pass

    def _add_graduated_legend(self, m: folium.Map, percentiles: np.ndarray, metric: str):
        """Add graduated symbols legend"""
        try:
            legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px;
                       background: rgba(255,255,255,0.9); border: 2px solid #007acc;
                       z-index: 9999; padding: 15px; border-radius: 10px;">
                <h4 style="margin-top: 0; color: #007acc; font-size: 14px;">
                    ⭐ Símbolos Graduados
                </h4>
                <p style="margin: 5px 0; font-size: 12px;"><strong>{metric}</strong></p>
                <div style="font-size: 10px;">
                    <div><span style="color: #2c7fb8;">●</span> > {percentiles[3]:,.0f}</div>
                    <div><span style="color: #40b6c4;">●</span> > {percentiles[2]:,.0f}</div>
                    <div><span style="color: #7fcdbb;">●</span> > {percentiles[1]:,.0f}</div>
                    <div><span style="color: #c7e9b4;">●</span> > {percentiles[0]:,.0f}</div>
                    <div><span style="color: #ffffcc;">●</span> Menor</div>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
        except:
            pass


def create_enhanced_map_visualizations() -> EnhancedMapVisualizations:
    """Create EnhancedMapVisualizations instance"""
    return EnhancedMapVisualizations()


# For testing
if __name__ == "__main__":
    visualizer = create_enhanced_map_visualizations()
    print("Enhanced Map Visualizations initialized successfully!")