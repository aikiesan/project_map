"""
CP2B Maps - Accessible Visualizations
WCAG 2.1 Level A compliant maps and charts with alternative text
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, List, Any
import folium

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AccessibleChart:
    """
    WCAG 2.1 Level A compliant chart wrapper for Plotly
    Provides alternative text and data table alternatives (WCAG 1.1.1)
    """

    def __init__(self, title: str, description: str):
        """
        Initialize accessible chart

        Args:
            title: Chart title
            description: Chart description for screen readers
        """
        self.title = title
        self.description = description
        self.logger = get_logger(self.__class__.__name__)

    def render_accessible_plotly_chart(
        self,
        fig: go.Figure,
        data_summary: str,
        width: str = 'stretch'
    ):
        """
        Render Plotly chart with WCAG 2.1 Level A compliance

        Args:
            fig: Plotly figure
            data_summary: Summary of chart data for screen readers
            width: Chart width ('stretch' or 'content')
        """
        try:
            # Update layout for accessibility (WCAG 2.4.6)
            fig.update_layout(
                title={
                    'text': self.title,
                    'x': 0.5,
                    'font': {'size': 18}
                },
                font={'size': 14},
                template="plotly_white"
            )

            # Main chart display
            st.plotly_chart(fig, width=width)

            # Alternative text for screen readers (WCAG 1.1.1)
            alt_text_html = f"""
            <div class="sr-only" aria-label="Descrição do gráfico">
                <h3>Descrição do Gráfico: {self.title}</h3>
                <p><strong>Descrição:</strong> {self.description}</p>
                <p><strong>Resumo dos Dados:</strong> {data_summary}</p>
            </div>
            """

            st.markdown(alt_text_html, unsafe_allow_html=True)

            # Text alternative in expandable section
            with st.expander("📊 Descrição Detalhada do Gráfico (Alternativa de Texto)"):
                st.markdown(f"**Título:** {self.title}")
                st.markdown(f"**Descrição:** {self.description}")
                st.markdown(f"**Resumo dos Dados:** {data_summary}")

                # Extract data for table alternative
                chart_data = self._extract_chart_data(fig)
                if chart_data is not None and not chart_data.empty:
                    st.markdown("**Dados do Gráfico em Formato de Tabela:**")
                    st.dataframe(chart_data, width='stretch')

        except Exception as e:
            self.logger.error(f"Error rendering accessible chart: {e}")
            st.plotly_chart(fig, width=width)

    def _extract_chart_data(self, fig: go.Figure) -> Optional[pd.DataFrame]:
        """
        Extract data from Plotly figure for tabular display

        Args:
            fig: Plotly figure

        Returns:
            DataFrame with chart data
        """
        try:
            data_list = []

            for trace in fig.data:
                if hasattr(trace, 'x') and hasattr(trace, 'y'):
                    for i, (x_val, y_val) in enumerate(zip(trace.x, trace.y)):
                        data_list.append({
                            'Série': trace.name or f'Série {i+1}',
                            'Eixo X': x_val,
                            'Eixo Y': y_val
                        })

            return pd.DataFrame(data_list) if data_list else None

        except Exception as e:
            self.logger.error(f"Error extracting chart data: {e}")
            return None

    def create_bar_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None
    ):
        """
        Create accessible bar chart

        Args:
            data: DataFrame with chart data
            x_column: X-axis column name
            y_column: Y-axis column name
            color_column: Optional color grouping column
        """
        try:
            fig = px.bar(
                data,
                x=x_column,
                y=y_column,
                color=color_column,
                title=self.title
            )

            # Generate data summary
            total_records = len(data)
            max_value = data[y_column].max()
            min_value = data[y_column].min()
            avg_value = data[y_column].mean()

            data_summary = (
                f"Gráfico de barras com {total_records} registros. "
                f"Valor máximo: {max_value:.1f}, "
                f"valor mínimo: {min_value:.1f}, "
                f"média: {avg_value:.1f}."
            )

            self.render_accessible_plotly_chart(fig, data_summary)

        except Exception as e:
            self.logger.error(f"Error creating accessible bar chart: {e}")

    def create_line_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        color_column: Optional[str] = None
    ):
        """
        Create accessible line chart

        Args:
            data: DataFrame with chart data
            x_column: X-axis column name
            y_column: Y-axis column name
            color_column: Optional color grouping column
        """
        try:
            fig = px.line(
                data,
                x=x_column,
                y=y_column,
                color=color_column,
                title=self.title
            )

            # Generate data summary
            total_points = len(data)
            trend = "crescente" if data[y_column].iloc[-1] > data[y_column].iloc[0] else "decrescente"

            data_summary = (
                f"Gráfico de linha com {total_points} pontos de dados. "
                f"Tendência geral: {trend}. "
                f"Valor inicial: {data[y_column].iloc[0]:.1f}, "
                f"valor final: {data[y_column].iloc[-1]:.1f}."
            )

            self.render_accessible_plotly_chart(fig, data_summary)

        except Exception as e:
            self.logger.error(f"Error creating accessible line chart: {e}")


class AccessibleMap:
    """
    WCAG 2.1 Level A compliant map wrapper for Folium
    Provides alternative text and data alternatives (WCAG 1.1.1)
    """

    def __init__(self, title: str, description: str):
        """
        Initialize accessible map

        Args:
            title: Map title
            description: Map description for screen readers
        """
        self.title = title
        self.description = description
        self.logger = get_logger(self.__class__.__name__)
        self.accessibility_features = {}

    def render_accessible_folium_map(
        self,
        folium_map: folium.Map,
        map_data_summary: str,
        alternative_data: Optional[pd.DataFrame] = None
    ):
        """
        Render Folium map with WCAG 2.1 Level A compliance

        Args:
            folium_map: Folium map object
            map_data_summary: Summary of map data for screen readers
            alternative_data: DataFrame with map data for tabular alternative
        """
        try:
            # Map heading (WCAG 1.3.1)
            st.markdown(f"## {self.title}")

            # Map description for screen readers (WCAG 1.1.1)
            map_alt_text = f"""
            <div class="sr-only" aria-label="Descrição do mapa">
                <h3>Descrição do Mapa: {self.title}</h3>
                <p><strong>Descrição:</strong> {self.description}</p>
                <p><strong>Resumo dos Dados:</strong> {map_data_summary}</p>
                <p><strong>Instruções:</strong> Use as alternativas de texto abaixo para acessar os dados do mapa em formato de tabela.</p>
            </div>
            """

            st.markdown(map_alt_text, unsafe_allow_html=True)

            # Display the map
            st.components.v1.html(folium_map._repr_html_(), height=500)

            # Alternative text and data (WCAG 1.1.1)
            with st.expander("🗺️ Descrição Detalhada do Mapa (Alternativa de Texto)"):
                st.markdown(f"**Título:** {self.title}")
                st.markdown(f"**Descrição:** {self.description}")
                st.markdown(f"**Resumo dos Dados:** {map_data_summary}")

                # Accessibility features summary
                if self.accessibility_features:
                    st.markdown("**Camadas do Mapa:**")
                    for layer_name, info in self.accessibility_features.items():
                        st.markdown(f"- **{layer_name}**: {info['description']} ({info['feature_count']} elementos)")

                # Tabular alternative
                if alternative_data is not None and not alternative_data.empty:
                    st.markdown("**Dados do Mapa em Formato de Tabela:**")
                    st.dataframe(alternative_data, width='stretch')

                    # Summary statistics
                    self._render_data_summary(alternative_data)

        except Exception as e:
            self.logger.error(f"Error rendering accessible map: {e}")
            st.components.v1.html(folium_map._repr_html_(), height=500)

    def add_accessible_layer(
        self,
        layer_data: Any,
        layer_name: str,
        description: str
    ):
        """
        Add layer with accessibility metadata

        Args:
            layer_data: Layer data
            layer_name: Name of the layer
            description: Description of the layer
        """
        try:
            # Store accessibility information
            self.accessibility_features[layer_name] = {
                'description': description,
                'feature_count': len(layer_data) if hasattr(layer_data, '__len__') else 1,
                'data_summary': self._generate_layer_summary(layer_data)
            }

        except Exception as e:
            self.logger.error(f"Error adding accessible layer: {e}")

    def _generate_layer_summary(self, layer_data: Any) -> str:
        """Generate summary for layer data"""
        try:
            if hasattr(layer_data, '__len__'):
                return f"Camada com {len(layer_data)} elementos"
            else:
                return "Camada com dados geoespaciais"
        except:
            return "Dados da camada disponíveis"

    def _render_data_summary(self, data: pd.DataFrame):
        """Render summary statistics for map data"""
        try:
            st.markdown("**Estatísticas Resumidas:**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total de Registros", len(data))

            with col2:
                numeric_cols = data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.metric("Colunas Numéricas", len(numeric_cols))

            with col3:
                if len(numeric_cols) > 0:
                    avg_value = data[numeric_cols[0]].mean()
                    st.metric(f"Média de {numeric_cols[0]}", f"{avg_value:.1f}")

        except Exception as e:
            self.logger.error(f"Error rendering data summary: {e}")

    def generate_comprehensive_alt_text(self) -> str:
        """
        Generate comprehensive alternative text for the entire map

        Returns:
            Comprehensive alternative text description
        """
        try:
            alt_text = f"Mapa interativo: {self.title}. "
            alt_text += f"{self.description} "

            if self.accessibility_features:
                alt_text += f"O mapa contém {len(self.accessibility_features)} camadas de dados: "

                for layer_name, info in self.accessibility_features.items():
                    alt_text += f"{layer_name} ({info['feature_count']} elementos), "

                alt_text = alt_text.rstrip(', ')

            alt_text += ". Use as alternativas de texto abaixo para acessar os dados em formato de tabela."

            return alt_text

        except Exception as e:
            self.logger.error(f"Error generating alt text: {e}")
            return f"Mapa interativo: {self.title}. {self.description}"


def create_audio_data_summary(data: pd.DataFrame, column_name: str) -> str:
    """
    Generate audio-friendly data summary for screen readers

    Args:
        data: DataFrame with data
        column_name: Column to summarize

    Returns:
        Audio-friendly summary text
    """
    try:
        if column_name not in data.columns:
            return f"Dados sobre {column_name} não disponíveis."

        total_records = len(data)
        max_value = data[column_name].max()
        min_value = data[column_name].min()
        avg_value = data[column_name].mean()

        summary = f"Resumo dos dados para {column_name}: "
        summary += f"Total de {total_records} registros. "
        summary += f"Valor mais alto: {max_value:.0f}. "
        summary += f"Valor mais baixo: {min_value:.0f}. "
        summary += f"Valor médio: {avg_value:.0f}."

        return summary

    except Exception as e:
        logger.error(f"Error creating audio summary: {e}")
        return f"Resumo dos dados para {column_name} não disponível."


def announce_visualization_update(visualization_type: str, update_description: str):
    """
    Announce visualization updates to screen readers

    Args:
        visualization_type: Type of visualization (map, chart, etc.)
        update_description: Description of the update
    """
    try:
        announcement = f"{visualization_type} atualizado: {update_description}"

        announcement_html = f"""
        <div aria-live="polite" aria-atomic="true" class="sr-only">
            {announcement}
        </div>
        """

        st.markdown(announcement_html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Error announcing visualization update: {e}")