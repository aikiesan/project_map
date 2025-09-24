"""
CP2B Maps V2 - Enhanced Sidebar Component
Professional sidebar with municipality search, filters, and real-time results
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from config.settings import settings
from src.utils.logging_config import get_logger
from src.data import database_loader
from src.core import biogas_calculator

logger = get_logger(__name__)


class Sidebar:
    """
    Enhanced sidebar component with search and filtering capabilities
    Features: Municipality search, biogas filters, population filters, real-time results
    """

    def __init__(self):
        """Initialize Sidebar component"""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing Sidebar component")

        # Cache municipality data for faster filtering
        self.municipalities_df = None
        self._load_municipality_data()

    def _load_municipality_data(self) -> None:
        """Load and cache municipality data"""
        try:
            self.municipalities_df = database_loader.load_municipalities_data()
            if self.municipalities_df is not None:
                self.logger.info(f"Loaded {len(self.municipalities_df)} municipalities for sidebar")
            else:
                self.logger.warning("No municipality data available for sidebar")
        except Exception as e:
            self.logger.error(f"Error loading municipality data: {e}")

    def render(self) -> Dict[str, Any]:
        """
        Render enhanced sidebar with search and filters

        Returns:
            Dictionary with search results and filter selections
        """
        try:
            st.sidebar.markdown("# 🎛️ CP2B Maps V2")
            st.sidebar.markdown("### Control Panel")

            # Search functionality
            search_results = self._render_search_section()

            # Filter controls
            filter_results = self._render_filter_section()

            # Statistics section
            stats_results = self._render_statistics_section(search_results, filter_results)

            # Combine all results
            sidebar_data = {
                'search': search_results,
                'filters': filter_results,
                'statistics': stats_results,
                'municipalities_df': self.municipalities_df
            }

            # Show real-time results count
            self._render_results_counter(sidebar_data)

            return sidebar_data

        except Exception as e:
            self.logger.error(f"Error rendering sidebar: {e}", exc_info=True)
            st.sidebar.error("⚠️ Sidebar error. Check logs.")
            return {}

    def _render_search_section(self) -> Dict[str, Any]:
        """Render municipality search functionality"""
        st.sidebar.markdown("#### 🔍 Municipality Search")

        search_results = {
            'query': '',
            'selected_municipalities': [],
            'search_mode': 'name'
        }

        if self.municipalities_df is None:
            st.sidebar.warning("⚠️ Municipality data not available")
            return search_results

        # Search mode selection
        search_mode = st.sidebar.radio(
            "Search by:",
            options=['name', 'biogas_potential', 'population'],
            format_func=lambda x: {
                'name': '📍 Municipality Name',
                'biogas_potential': '⚡ Biogas Potential',
                'population': '👥 Population'
            }[x],
            key="search_mode"
        )
        search_results['search_mode'] = search_mode

        # Search input based on mode
        if search_mode == 'name':
            search_query = st.sidebar.text_input(
                "Search municipalities:",
                placeholder="Type municipality name...",
                help="Search by municipality name (partial matches supported)",
                key="municipality_search"
            )
            search_results['query'] = search_query

            # Auto-complete suggestions
            if search_query:
                matching_municipalities = self._get_name_matches(search_query)
                if matching_municipalities:
                    selected = st.sidebar.multiselect(
                        f"Found {len(matching_municipalities)} matches:",
                        options=matching_municipalities,
                        help="Select municipalities to highlight on map",
                        key="selected_municipalities"
                    )
                    search_results['selected_municipalities'] = selected

        elif search_mode == 'biogas_potential':
            biogas_range = self._get_biogas_range_filter()
            search_results['biogas_range'] = biogas_range

        elif search_mode == 'population':
            pop_range = self._get_population_range_filter()
            search_results['population_range'] = pop_range

        return search_results

    def _render_filter_section(self) -> Dict[str, Any]:
        """Render advanced filtering controls"""
        st.sidebar.markdown("#### 🎚️ Advanced Filters")

        filter_results = {}

        if self.municipalities_df is None:
            st.sidebar.warning("⚠️ No data for filtering")
            return filter_results

        with st.sidebar.expander("🔧 Filter Options", expanded=True):
            # Biogas potential filter
            biogas_values = self.municipalities_df['biogas_potential_m3_day'].fillna(0)
            biogas_min, biogas_max = st.slider(
                "Biogas Potential (m³/day)",
                min_value=float(biogas_values.min()),
                max_value=float(biogas_values.max()),
                value=(float(biogas_values.min()), float(biogas_values.max())),
                format="%.0f",
                help="Filter municipalities by daily biogas potential",
                key="biogas_filter"
            )
            filter_results['biogas_range'] = (biogas_min, biogas_max)

            # Population filter
            if 'population' in self.municipalities_df.columns:
                pop_values = self.municipalities_df['population'].fillna(0)
                pop_min, pop_max = st.slider(
                    "Population",
                    min_value=int(pop_values.min()),
                    max_value=int(pop_values.max()),
                    value=(int(pop_values.min()), int(pop_values.max())),
                    format="%d",
                    help="Filter municipalities by population size",
                    key="population_filter"
                )
                filter_results['population_range'] = (pop_min, pop_max)

            # Energy potential filter
            if 'energy_potential_kwh_day' in self.municipalities_df.columns:
                energy_values = self.municipalities_df['energy_potential_kwh_day'].fillna(0)
                energy_min, energy_max = st.slider(
                    "Energy Potential (kWh/day)",
                    min_value=float(energy_values.min()),
                    max_value=float(energy_values.max()),
                    value=(float(energy_values.min()), float(energy_values.max())),
                    format="%.0f",
                    help="Filter municipalities by daily energy potential",
                    key="energy_filter"
                )
                filter_results['energy_range'] = (energy_min, energy_max)

        return filter_results

    def _render_statistics_section(self,
                                 search_results: Dict[str, Any],
                                 filter_results: Dict[str, Any]) -> Dict[str, Any]:
        """Render real-time statistics based on current selection"""
        st.sidebar.markdown("#### 📊 Selection Statistics")

        stats_results = {}

        if self.municipalities_df is None:
            st.sidebar.warning("⚠️ No data for statistics")
            return stats_results

        # Apply filters to get current selection
        filtered_df = self._apply_filters(self.municipalities_df, search_results, filter_results)

        if len(filtered_df) == 0:
            st.sidebar.warning("⚠️ No municipalities match current filters")
            return stats_results

        # Calculate statistics for filtered data
        total_municipalities = len(filtered_df)
        total_biogas = filtered_df['biogas_potential_m3_day'].sum()
        total_energy = filtered_df['energy_potential_kwh_day'].sum() if 'energy_potential_kwh_day' in filtered_df.columns else 0
        total_population = filtered_df['population'].sum() if 'population' in filtered_df.columns else 0

        # Display metrics
        st.sidebar.metric("Selected Municipalities", f"{total_municipalities:,}")
        st.sidebar.metric("Total Biogas Potential", f"{total_biogas:,.0f} m³/day")
        st.sidebar.metric("Total Energy Potential", f"{total_energy:,.0f} kWh/day")

        if total_population > 0:
            st.sidebar.metric("Total Population", f"{total_population:,}")

        # Performance indicators
        if total_municipalities > 0:
            avg_biogas = total_biogas / total_municipalities
            st.sidebar.metric("Average Biogas/Municipality", f"{avg_biogas:,.0f} m³/day")

        stats_results = {
            'filtered_df': filtered_df,
            'total_municipalities': total_municipalities,
            'total_biogas': total_biogas,
            'total_energy': total_energy,
            'total_population': total_population,
            'avg_biogas': avg_biogas if total_municipalities > 0 else 0
        }

        return stats_results

    def _render_results_counter(self, sidebar_data: Dict[str, Any]) -> None:
        """Show real-time results counter"""
        stats = sidebar_data.get('statistics', {})
        total_results = stats.get('total_municipalities', 0)
        total_available = len(self.municipalities_df) if self.municipalities_df is not None else 0

        if total_available > 0:
            percentage = (total_results / total_available) * 100
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**Results:** {total_results:,} of {total_available:,} municipalities ({percentage:.1f}%)")

            # Progress bar
            st.sidebar.progress(percentage / 100, text=f"Showing {percentage:.1f}% of data")

    def _get_name_matches(self, query: str, limit: int = 20) -> List[str]:
        """Get municipality name matches for search query"""
        if not query or self.municipalities_df is None:
            return []

        # Case-insensitive partial matching
        mask = self.municipalities_df['nome_municipio'].str.contains(
            query, case=False, na=False, regex=False
        )
        matches = self.municipalities_df[mask]['nome_municipio'].tolist()

        return matches[:limit]  # Limit results for performance

    def _get_biogas_range_filter(self) -> Tuple[float, float]:
        """Get biogas potential range filter"""
        if self.municipalities_df is None:
            return (0.0, 1000.0)

        biogas_values = self.municipalities_df['biogas_potential_m3_day'].fillna(0)

        return st.sidebar.slider(
            "Biogas Range (m³/day)",
            min_value=float(biogas_values.min()),
            max_value=float(biogas_values.max()),
            value=(float(biogas_values.min()), float(biogas_values.max())),
            help="Filter by biogas potential range",
            key="biogas_search_range"
        )

    def _get_population_range_filter(self) -> Tuple[int, int]:
        """Get population range filter"""
        if self.municipalities_df is None or 'population' not in self.municipalities_df.columns:
            return (0, 100000)

        pop_values = self.municipalities_df['population'].fillna(0)

        return st.sidebar.slider(
            "Population Range",
            min_value=int(pop_values.min()),
            max_value=int(pop_values.max()),
            value=(int(pop_values.min()), int(pop_values.max())),
            help="Filter by population range",
            key="population_search_range"
        )

    def _apply_filters(self,
                      df: pd.DataFrame,
                      search_results: Dict[str, Any],
                      filter_results: Dict[str, Any]) -> pd.DataFrame:
        """Apply all filters to municipality data"""
        filtered_df = df.copy()

        try:
            # Apply search filters
            if search_results.get('selected_municipalities'):
                filtered_df = filtered_df[
                    filtered_df['nome_municipio'].isin(search_results['selected_municipalities'])
                ]

            # Apply biogas range filter
            biogas_range = filter_results.get('biogas_range')
            if biogas_range:
                filtered_df = filtered_df[
                    (filtered_df['biogas_potential_m3_day'] >= biogas_range[0]) &
                    (filtered_df['biogas_potential_m3_day'] <= biogas_range[1])
                ]

            # Apply population range filter
            population_range = filter_results.get('population_range')
            if population_range and 'population' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['population'] >= population_range[0]) &
                    (filtered_df['population'] <= population_range[1])
                ]

            # Apply energy range filter
            energy_range = filter_results.get('energy_range')
            if energy_range and 'energy_potential_kwh_day' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['energy_potential_kwh_day'] >= energy_range[0]) &
                    (filtered_df['energy_potential_kwh_day'] <= energy_range[1])
                ]

        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")

        return filtered_df

    def get_filtered_municipalities(self) -> Optional[pd.DataFrame]:
        """Get currently filtered municipalities (for external use)"""
        # This method can be called by other components to get current filter state
        if hasattr(st.session_state, 'sidebar_data'):
            return st.session_state.sidebar_data.get('statistics', {}).get('filtered_df')
        return self.municipalities_df