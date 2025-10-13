"""
CP2B Maps - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas
Home Page Component - Refactored to use single-responsibility components (SOLID principles)
Orchestrates: SidebarRenderer, MapBuilder, DashboardMetrics
"""

import streamlit as st
from streamlit_folium import st_folium
from typing import Optional

from src.utils.logging_config import get_logger
from src.data.loaders.database_loader import DatabaseLoader, get_database_loader
from src.core.biogas_calculator import BiogasCalculator, get_biogas_calculator

# Import focused components (Single Responsibility Principle)
from src.ui.components.sidebar_renderer import SidebarRenderer
from src.ui.components.map_builder import MapBuilder
from src.ui.components.dashboard_metrics import DashboardMetrics

# Import supporting components
from src.ui.components.substrate_info import render_substrate_information
from src.ui.components.map_export import render_export_panel_compact

logger = get_logger(__name__)


class HomePage:
    """
    Home page orchestrator component
    
    Responsibilities:
    - Coordinate component rendering
    - Handle user interactions
    - Manage page state
    
    Delegates rendering to specialized components:
    - SidebarRenderer: Sidebar UI and configuration collection
    - MapBuilder: Map creation and visualization
    - DashboardMetrics: Statistics dashboard
    """

    def __init__(self,
                 db_loader: Optional[DatabaseLoader] = None,
                 calculator: Optional[BiogasCalculator] = None):
        """
        Initialize home page with dependency injection
        
        Args:
            db_loader: DatabaseLoader instance (uses factory if None)
            calculator: BiogasCalculator instance (uses factory if None)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing HomePage orchestrator")
        
        # Inject dependencies (Dependency Inversion Principle)
        self.db_loader = db_loader or get_database_loader()
        self.calculator = calculator or get_biogas_calculator()
        
        # Initialize focused components (Open/Closed Principle)
        self.sidebar_renderer = SidebarRenderer()
        self.map_builder = MapBuilder()
        self.dashboard = DashboardMetrics(self.db_loader, self.calculator)
        
        # Initialize session state
        if 'show_substrate_modal' not in st.session_state:
            st.session_state.show_substrate_modal = False

    def render(self) -> None:
        """
        Render complete home page by orchestrating components
        
        Architecture:
        1. Sidebar (SidebarRenderer) → Returns MapConfig
        2. Map (MapBuilder) → Renders map with config
        3. Dashboard (DashboardMetrics) → Renders stats
        4. Modals and Footer → Conditional rendering
        """
        try:
            # Step 1: Render sidebar and get configuration
            map_config = self.sidebar_renderer.render()
            
            # Step 2: Render main map section
            self._render_map_section(map_config)
            
            # Step 3: Render dashboard metrics
            self.dashboard.render()

            # Step 4: Render modals and sidebar extras
            self._render_substrate_modal()
            self._render_sidebar_extras()
            # Academic footer removed per user request
        
        except Exception as e:
            self.logger.error(f"Error rendering home page: {e}", exc_info=True)
            st.error("⚠️ Failed to render home page. Check logs for details.")

    def _render_map_section(self, map_config) -> None:
        """
        Render map section with active filters banner
        
        Args:
            map_config: MapConfig from sidebar
        """
        # Show active filters banner
        if map_config.has_active_filters():
            active_filters = map_config.get_active_filters_description()
            st.info(f"🎯 Filtros Ativos: {' | '.join(active_filters)}")
        
        # Load municipality data
        municipalities_df = self.db_loader.load_municipalities_data()
        
        if municipalities_df is None:
            st.error("⚠️ Failed to load municipality data")
            return
        
        # Build map using MapBuilder
        folium_map = self.map_builder.build_map(municipalities_df, map_config)
        
        # Store map in session for export
        st.session_state.current_map = folium_map
        
        # Display map (suppress reruns by not returning objects on initial load)
        # Use a stable key to prevent unnecessary reloads
        map_data = st_folium(
            folium_map,
            width="100%",
            height=map_config.map_height,
            returned_objects=[],  # Don't track clicks to prevent reruns
            key="main_map"
        )

    def _handle_map_click(self, clicked_data: dict) -> None:
        """
        Handle map click events
        
        Args:
            clicked_data: Clicked location data
        """
        lat = clicked_data.get('lat')
        lon = clicked_data.get('lng')
        if lat and lon:
            st.success(f"🎯 Município selecionado! Latitude: {lat:.4f}, Longitude: {lon:.4f}")

    def _render_substrate_modal(self) -> None:
        """Render substrate information modal if requested"""
        if st.session_state.get('show_substrate_modal', False):
            with st.expander("🧪 Guia Completo de Substratos para Biogás", expanded=True):
                render_substrate_information()
                if st.button("✖️ Fechar Guia", width='stretch'):
                    st.session_state.show_substrate_modal = False
                    st.rerun()

    def _render_sidebar_extras(self) -> None:
        """Render extra sidebar elements (selected municipalities, export)"""
        with st.sidebar:
            # Selected municipalities section
            if 'selected_municipalities' in st.session_state and st.session_state.selected_municipalities:
                st.markdown("---")
                st.markdown("**🎯 Municípios Selecionados:**")
                
                try:
                    municipalities_df = self.db_loader.load_municipalities_data()
                    selected_names = municipalities_df[
                        municipalities_df['municipality'].isin(st.session_state.selected_municipalities)
                    ]['municipality'].tolist()
                    
                    # Show up to 3 names
                    for name in selected_names[:3]:
                        display_name = name[:15] + "..." if len(name) > 15 else name
                        st.markdown(f"• {display_name}")
                    
                    # Show count if more than 3
                    if len(selected_names) > 3:
                        st.markdown(f"...+{len(selected_names)-3} mais")
                    
                    # Clear button
                    if st.button("🗑️ Limpar Seleção", key="clear_selection"):
                        count = len(st.session_state.selected_municipalities)
                        st.session_state.selected_municipalities.clear()
                        st.toast(f"{count} municípios removidos da seleção!", icon="🗑️")
                        st.rerun()
                except Exception as e:
                    self.logger.error(f"Error displaying selected municipalities: {e}")
            
            # Map export section
            if 'current_map' in st.session_state and st.session_state.current_map is not None:
                st.markdown("---")
                render_export_panel_compact(st.session_state.current_map)
            
            # System info
            st.markdown("---")
            st.markdown("**🖥️ Status do Sistema**")
            db_status = "✅ Online" if self.db_loader.validate_database() else "❌ Error"
            st.markdown(f"🗄️ Database: {db_status}")
            st.markdown(f"⚙️ Calculator: ✅ Ready")


# Factory function for creating HomePage instances
def create_home_page(db_loader: Optional[DatabaseLoader] = None,
                     calculator: Optional[BiogasCalculator] = None) -> HomePage:
    """
    Factory function to create HomePage instance
    
    Args:
        db_loader: Optional DatabaseLoader instance
        calculator: Optional BiogasCalculator instance
    
    Returns:
        HomePage instance
    """
    return HomePage(db_loader, calculator)
