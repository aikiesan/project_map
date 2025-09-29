"""
CP2B Maps V2 - Proximity Analysis Results Display Component
Professional results visualization with charts, statistics, and export capabilities
"""

from typing import Dict, List, Optional, Any
import streamlit as st
import pandas as pd
import numpy as np

# Visualization imports with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    px = None
    go = None

from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ProximityResults:
    """
    Professional proximity analysis results display
    Features: Interactive charts, statistical summaries, export functionality, optimization metrics
    """

    def __init__(self):
        """Initialize ProximityResults"""
        self.logger = get_logger(self.__class__.__name__)

        if not HAS_PLOTLY:
            self.logger.warning("Plotly not available - limited visualization capabilities")

    def render(self, analysis_results: Dict[str, Any]) -> None:
        """
        Render complete proximity analysis results

        Args:
            analysis_results: Results from proximity analyzer
        """
        try:
            if not analysis_results or 'error' in analysis_results:
                self._render_error_state(analysis_results)
                return

            st.markdown("## 📊 Proximity Analysis Results")

            # Results summary header
            self._render_results_header(analysis_results)

            # Main results sections
            col1, col2 = st.columns([2, 1])

            with col1:
                # Geographic and statistical analysis
                self._render_geographic_analysis(analysis_results)
                self._render_statistical_analysis(analysis_results)

            with col2:
                # Key metrics and summary
                self._render_key_metrics(analysis_results)
                self._render_feasibility_assessment(analysis_results)

            # Detailed analysis sections
            self._render_biogas_analysis(analysis_results)

            if analysis_results.get('optimization_metrics'):
                self._render_optimization_metrics(analysis_results)

            # Municipality details
            self._render_municipality_details(analysis_results)

            # Export options
            self._render_export_options(analysis_results)

        except Exception as e:
            self.logger.error(f"Error rendering proximity results: {e}")
            st.error("⚠️ Error displaying analysis results")

    def _render_error_state(self, results: Dict[str, Any]) -> None:
        """Render error state with helpful information"""
        st.error("⚠️ Analysis Error")

        if results and 'error' in results:
            st.markdown(f"**Error Message:** {results['error']}")

        if results and 'center' in results:
            center = results['center']
            st.info(f"**Analysis Center:** {center[0]:.4f}, {center[1]:.4f}")

        if results and 'radius_km' in results:
            st.info(f"**Analysis Radius:** {results['radius_km']} km")

        st.markdown("### 💡 Troubleshooting Tips:")
        st.markdown("""
        - Ensure coordinates are within São Paulo state bounds
        - Check that radius is between 1-200 km
        - Verify municipality data is loaded
        - Try a different analysis location
        """)

    def _render_results_header(self, results: Dict[str, Any]) -> None:
        """Render results summary header"""
        center = results.get('center', (0, 0))
        radius = results.get('radius_km', 0)
        municipality_count = results.get('municipalities_found', 0)

        # Header metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Analysis Center",
                f"{center[0]:.4f}, {center[1]:.4f}",
                help="Latitude, Longitude of analysis center"
            )

        with col2:
            st.metric(
                "Radius",
                f"{radius} km",
                help="Analysis radius in kilometers"
            )

        with col3:
            st.metric(
                "Municipalities",
                f"{municipality_count}",
                help="Number of municipalities found within radius"
            )

        with col4:
            # Calculate total area
            total_area = results.get('geographic_info', {}).get('total_area_km2', 0)
            st.metric(
                "Total Area",
                f"{total_area:,.1f} km²",
                help="Total analysis area"
            )

        st.markdown("---")

    def _render_geographic_analysis(self, results: Dict[str, Any]) -> None:
        """Render geographic analysis section"""
        st.markdown("### 🌍 Geographic Analysis")

        geo_info = results.get('geographic_info', {})

        if geo_info:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📍 Location Information")
                coords = geo_info.get('center_coordinates', {})
                st.write(f"**Coordinates:** {coords.get('formatted', 'N/A')}")
                st.write(f"**Region:** {geo_info.get('region_type', 'Unknown')}")
                st.write(f"**Analysis Area:** {geo_info.get('total_area_km2', 0):,.1f} km²")

            with col2:
                st.markdown("#### 👥 Population Estimates")
                st.write(f"**Estimated Population:** {geo_info.get('estimated_population', 0):,.0f}")
                st.write(f"**Area (Hectares):** {geo_info.get('total_area_ha', 0):,.1f} ha")

        # Distance distribution chart
        if HAS_PLOTLY and results.get('municipality_details'):
            self._render_distance_distribution_chart(results['municipality_details'])

    def _render_distance_distribution_chart(self, municipality_details: List[Dict[str, Any]]) -> None:
        """Render distance distribution chart"""
        try:
            if not municipality_details:
                return

            # Extract distances
            distances = [m.get('distance_km', 0) for m in municipality_details if m.get('distance_km')]

            if not distances:
                return

            # Create histogram
            fig = px.histogram(
                x=distances,
                nbins=20,
                title="Municipality Distance Distribution",
                labels={'x': 'Distance from Center (km)', 'y': 'Number of Municipalities'},
                color_discrete_sequence=['#1f77b4']
            )

            fig.update_layout(
                showlegend=False,
                height=300,
                margin=dict(t=50, b=50, l=50, r=50)
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error creating distance distribution chart: {e}")

    def _render_statistical_analysis(self, results: Dict[str, Any]) -> None:
        """Render statistical analysis section"""
        st.markdown("### 📈 Statistical Analysis")

        municipality_stats = results.get('municipality_statistics', {})

        if not municipality_stats:
            st.info("No statistical data available")
            return

        # Create tabs for different statistics
        stat_columns = list(municipality_stats.keys())
        if stat_columns:
            # Display statistics for the most important columns
            primary_columns = [col for col in stat_columns if 'biogas' in col.lower()]
            if not primary_columns:
                primary_columns = stat_columns[:2]  # First 2 columns

            for column in primary_columns:
                if column in municipality_stats:
                    self._render_column_statistics(column, municipality_stats[column])

    def _render_column_statistics(self, column_name: str, stats: Dict[str, Any]) -> None:
        """Render statistics for a specific column"""
        try:
            if 'error' in stats:
                st.warning(f"⚠️ Error in {column_name}: {stats['error']}")
                return

            # Format column name for display
            display_name = column_name.replace('_', ' ').title()
            st.markdown(f"#### 📊 {display_name}")

            # Basic statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                total_value = stats.get('total', 0)
                st.metric(
                    "Total",
                    f"{total_value:,.0f}",
                    help=f"Sum of all {display_name} values"
                )

            with col2:
                mean_value = stats.get('mean', 0)
                st.metric(
                    "Average",
                    f"{mean_value:,.0f}",
                    help=f"Average {display_name} per municipality"
                )

            with col3:
                count_non_zero = stats.get('count_non_zero', 0)
                total_count = stats.get('count', 0)
                percentage = (count_non_zero / total_count * 100) if total_count > 0 else 0
                st.metric(
                    "Coverage",
                    f"{percentage:.1f}%",
                    help=f"Percentage of municipalities with {display_name}"
                )

            # Percentile information
            percentiles = stats.get('percentiles', {})
            if percentiles:
                st.markdown("**Distribution:**")
                pcol1, pcol2, pcol3, pcol4 = st.columns(4)

                with pcol1:
                    st.write(f"25th: {percentiles.get('25th', 0):,.0f}")
                with pcol2:
                    st.write(f"50th: {stats.get('median', 0):,.0f}")
                with pcol3:
                    st.write(f"75th: {percentiles.get('75th', 0):,.0f}")
                with pcol4:
                    st.write(f"90th: {percentiles.get('90th', 0):,.0f}")

            # Create visualization if plotly available
            if HAS_PLOTLY and 'distribution' in stats:
                self._render_distribution_chart(display_name, stats)

        except Exception as e:
            self.logger.error(f"Error rendering column statistics for {column_name}: {e}")

    def _render_distribution_chart(self, column_name: str, stats: Dict[str, Any]) -> None:
        """Render distribution chart for a column"""
        try:
            distribution = stats.get('distribution', {})

            if not distribution:
                return

            # Create pie chart for distribution
            labels = ['Zero Values', 'Low Values', 'Medium Values', 'High Values']
            values = [
                distribution.get('zeros', 0),
                distribution.get('low_values', 0),
                distribution.get('medium_values', 0),
                distribution.get('high_values', 0)
            ]

            # Only include non-zero values
            filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]

            if filtered_data:
                fig = px.pie(
                    values=[item[1] for item in filtered_data],
                    names=[item[0] for item in filtered_data],
                    title=f"{column_name} Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )

                fig.update_layout(
                    height=300,
                    margin=dict(t=50, b=50, l=50, r=50),
                    showlegend=True
                )

                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error creating distribution chart: {e}")

    def _render_key_metrics(self, results: Dict[str, Any]) -> None:
        """Render key metrics summary"""
        st.markdown("### 🎯 Key Metrics")

        # Biogas potential summary
        biogas_analysis = results.get('biogas_analysis', {})
        if biogas_analysis and 'total_potential_m3_year' in biogas_analysis:
            total_potential = biogas_analysis['total_potential_m3_year']

            for source, value in total_potential.items():
                source_name = source.replace('potencial_biogas_', '').replace('_', ' ').title()
                st.metric(
                    f"Biogas {source_name}",
                    f"{value:,.0f} m³/year",
                    help=f"Annual biogas potential from {source_name.lower()}"
                )

        # Geographic metrics
        geo_info = results.get('geographic_info', {})
        if geo_info:
            municipalities_found = results.get('municipalities_found', 0)
            area_km2 = geo_info.get('total_area_km2', 0)

            if municipalities_found > 0 and area_km2 > 0:
                density = municipalities_found / area_km2
                st.metric(
                    "Municipality Density",
                    f"{density:.2f} /km²",
                    help="Municipalities per square kilometer"
                )

    def _render_feasibility_assessment(self, results: Dict[str, Any]) -> None:
        """Render feasibility assessment"""
        st.markdown("### 🏭 Feasibility Assessment")

        biogas_analysis = results.get('biogas_analysis', {})
        feasibility = biogas_analysis.get('feasibility_assessment', {})

        if feasibility:
            # Feasibility level
            level = feasibility.get('feasibility_level', 'Unknown')
            description = feasibility.get('description', 'No assessment available')

            # Color code based on level
            level_colors = {
                'Very High': '🟢',
                'High': '🔵',
                'Medium': '🟡',
                'Low': '🟠',
                'Very Low': '🔴'
            }

            icon = level_colors.get(level, '⚪')
            st.markdown(f"**{icon} Feasibility Level:** {level}")
            st.markdown(f"*{description}*")

            # Additional metrics
            if 'total_potential_m3_year' in feasibility:
                total = feasibility['total_potential_m3_year']
                st.metric("Total Potential", f"{total:,.0f} m³/year")

            if 'potential_plant_capacity_mw' in feasibility:
                capacity = feasibility['potential_plant_capacity_mw']
                st.metric("Est. Plant Capacity", f"{capacity:.1f} MW")

    def _render_biogas_analysis(self, results: Dict[str, Any]) -> None:
        """Render detailed biogas analysis"""
        st.markdown("### ⚡ Biogas Analysis Details")

        biogas_analysis = results.get('biogas_analysis', {})

        if not biogas_analysis:
            st.info("No biogas analysis data available")
            return

        # Top contributors
        top_contributors = biogas_analysis.get('top_contributors', {})
        if top_contributors:
            st.markdown("#### 🏆 Top Contributing Municipalities")

            for source, contributors in top_contributors.items():
                if contributors:
                    source_name = source.replace('potencial_biogas_', '').replace('_', ' ').title()

                    with st.expander(f"Top {source_name} Contributors"):
                        contributor_df = pd.DataFrame(contributors)
                        if not contributor_df.empty:
                            # Format the dataframe for display
                            display_df = contributor_df.copy()
                            for col in display_df.columns:
                                if col != 'nome_municipio' and pd.api.types.is_numeric_dtype(display_df[col]):
                                    display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")

                            st.dataframe(display_df, use_container_width=True)

        # Biogas potential breakdown chart
        if HAS_PLOTLY and 'total_potential_m3_year' in biogas_analysis:
            self._render_biogas_breakdown_chart(biogas_analysis['total_potential_m3_year'])

    def _render_biogas_breakdown_chart(self, potential_data: Dict[str, float]) -> None:
        """Render biogas potential breakdown chart"""
        try:
            if not potential_data:
                return

            # Prepare data for chart
            sources = []
            values = []

            for source, value in potential_data.items():
                if value > 0:
                    # Clean up source names
                    clean_name = source.replace('potencial_biogas_', '').replace('_', ' ').title()
                    sources.append(clean_name)
                    values.append(value)

            if not sources:
                return

            # Create horizontal bar chart
            fig = px.bar(
                x=values,
                y=sources,
                orientation='h',
                title="Biogas Potential by Source",
                labels={'x': 'Annual Potential (m³/year)', 'y': 'Source'},
                color=values,
                color_continuous_scale='Viridis'
            )

            fig.update_layout(
                height=300,
                margin=dict(t=50, b=50, l=150, r=50),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error creating biogas breakdown chart: {e}")

    def _render_optimization_metrics(self, results: Dict[str, Any]) -> None:
        """Render optimization metrics"""
        st.markdown("### 🎯 Location Optimization Metrics")

        optimization = results.get('optimization_metrics', {})

        if not optimization:
            st.info("No optimization metrics available")
            return

        # Transport optimization
        transport = optimization.get('transport_optimization', {})
        if transport:
            st.markdown("#### 🚛 Transport Optimization")

            col1, col2 = st.columns(2)

            with col1:
                avg_score = transport.get('average_transport_score', 0)
                st.metric("Avg Transport Score", f"{avg_score:,.0f}")

            with col2:
                optimal_supply = transport.get('optimal_supply_municipalities', 0)
                st.metric("Optimal Supply (≤25km)", f"{optimal_supply}")

        # Supply concentration
        concentration = optimization.get('supply_concentration', {})
        if concentration:
            st.markdown("#### 📍 Supply Concentration")

            # Create chart showing concentration by distance ranges
            if HAS_PLOTLY:
                self._render_concentration_chart(concentration)

    def _render_concentration_chart(self, concentration_data: Dict[str, Any]) -> None:
        """Render supply concentration chart"""
        try:
            distance_ranges = []
            municipality_counts = []
            potential_values = []

            for range_key, data in concentration_data.items():
                if isinstance(data, dict):
                    distance_ranges.append(range_key)
                    municipality_counts.append(data.get('municipality_count', 0))
                    potential_values.append(data.get('total_potential', 0))

            if not distance_ranges:
                return

            # Create subplot with secondary y-axis
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=("Supply Concentration by Distance",)
            )

            # Add municipality count bars
            fig.add_trace(
                go.Bar(
                    x=distance_ranges,
                    y=municipality_counts,
                    name="Municipality Count",
                    marker_color='lightblue'
                ),
                secondary_y=False,
            )

            # Add potential line
            fig.add_trace(
                go.Scatter(
                    x=distance_ranges,
                    y=potential_values,
                    mode='lines+markers',
                    name="Biogas Potential",
                    line=dict(color='red', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=True,
            )

            # Update layout
            fig.update_xaxes(title_text="Distance Range")
            fig.update_yaxes(title_text="Municipality Count", secondary_y=False)
            fig.update_yaxes(title_text="Biogas Potential (m³/year)", secondary_y=True)

            fig.update_layout(height=400, margin=dict(t=50, b=50, l=50, r=50))

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            self.logger.error(f"Error creating concentration chart: {e}")

    def _render_municipality_details(self, results: Dict[str, Any]) -> None:
        """Render municipality details table"""
        st.markdown("### 🏛️ Municipality Details")

        municipality_details = results.get('municipality_details', [])

        if not municipality_details:
            st.info("No municipality details available")
            return

        # Convert to DataFrame for better display
        df = pd.DataFrame(municipality_details)

        if df.empty:
            st.info("No municipality data to display")
            return

        # Format numeric columns
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) and col != 'distance_km':
                df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            elif col == 'distance_km':
                df[col] = df[col].apply(lambda x: f"{x:.2f} km" if pd.notna(x) else "N/A")

        # Display with pagination
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # Summary information
        total_municipalities = len(municipality_details)
        st.caption(f"Showing {total_municipalities} municipalities within analysis radius")

    def _render_export_options(self, results: Dict[str, Any]) -> None:
        """Render export options"""
        st.markdown("### 📥 Export Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export Summary", key="export_summary"):
                self._export_summary(results)

        with col2:
            if st.button("📋 Export Details", key="export_details"):
                self._export_detailed_results(results)

        with col3:
            if st.button("🗺️ Export for GIS", key="export_gis"):
                self._export_gis_data(results)

    def _export_summary(self, results: Dict[str, Any]) -> None:
        """Export analysis summary"""
        try:
            # Create summary data
            summary_data = {
                'Analysis Information': [
                    f"Center: {results.get('center', 'N/A')}",
                    f"Radius: {results.get('radius_km', 'N/A')} km",
                    f"Municipalities Found: {results.get('municipalities_found', 0)}",
                    f"Analysis Date: {results.get('analysis_timestamp', 'N/A')}"
                ]
            }

            # Add biogas analysis summary
            biogas_analysis = results.get('biogas_analysis', {})
            if 'total_potential_m3_year' in biogas_analysis:
                summary_data['Biogas Potential'] = [
                    f"{source}: {value:,.0f} m³/year"
                    for source, value in biogas_analysis['total_potential_m3_year'].items()
                ]

            # Convert to DataFrame
            max_length = max(len(values) for values in summary_data.values())
            for key in summary_data:
                while len(summary_data[key]) < max_length:
                    summary_data[key].append("")

            summary_df = pd.DataFrame(summary_data)

            # Create CSV
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Summary CSV",
                data=csv,
                file_name=f"proximity_analysis_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        except Exception as e:
            self.logger.error(f"Error exporting summary: {e}")
            st.error("⚠️ Error exporting summary")

    def _export_detailed_results(self, results: Dict[str, Any]) -> None:
        """Export detailed analysis results"""
        try:
            municipality_details = results.get('municipality_details', [])

            if not municipality_details:
                st.warning("No detailed data available for export")
                return

            # Convert to DataFrame
            df = pd.DataFrame(municipality_details)

            # Create CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📋 Download Detailed CSV",
                data=csv,
                file_name=f"proximity_analysis_details_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        except Exception as e:
            self.logger.error(f"Error exporting detailed results: {e}")
            st.error("⚠️ Error exporting detailed results")

    def _export_gis_data(self, results: Dict[str, Any]) -> None:
        """Export GIS-compatible data"""
        try:
            st.info("💡 GIS export functionality would generate GeoJSON or shapefile format")
            st.markdown("This feature requires additional geospatial processing and will be "
                       "implemented in future versions.")

        except Exception as e:
            self.logger.error(f"Error with GIS export: {e}")


# Factory function
def create_proximity_results() -> ProximityResults:
    """
    Create ProximityResults instance

    Returns:
        ProximityResults instance
    """
    return ProximityResults()