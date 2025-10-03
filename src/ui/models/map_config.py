"""
CP2B Maps V2 - Map Configuration Model
Dataclass for map visualization configuration state
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class MapConfig:
    """
    Configuration object for map visualization
    Immutable configuration state for map rendering
    """

    # Layer visibility
    show_biogas: bool = True
    show_plantas: bool = False
    show_polygons: bool = False
    show_gasodutos_dist: bool = False
    show_gasodutos_transp: bool = False
    show_rodovias: bool = False
    show_regioes_admin: bool = False
    show_mapbiomas: bool = False
    show_boundary: bool = True
    show_regioes_imediatas: bool = False
    show_regioes_intermediarias: bool = False

    # Infrastructure layers
    show_etes: bool = False
    show_power_substations: bool = False
    show_transmission_lines: bool = False
    show_apps_hidrography: bool = False
    show_highways: bool = False
    show_urban_areas: bool = False

    # Data filtering
    data_column: str = "biogas_potential_m3_year"
    filter_mode: str = "Individual"
    selected_data: List[str] = field(default_factory=lambda: ["Potencial Total"])
    search_term: str = ""

    # Visualization style
    viz_type: str = "Mapa de Preenchimento (Coroplético)"

    # Map center and zoom (São Paulo State center, not city)
    center_lat: float = -22.5  # São Paulo State center latitude
    center_lon: float = -48.5  # São Paulo State center longitude
    zoom_start: int = 7

    # Display options
    map_height: int = 600
    show_legend: bool = True
    show_popup: bool = True

    def get_data_column_display_name(self) -> str:
        """Get human-readable name for data column"""
        display_names = {
            "biogas_potential_m3_year": "Potencial Total",
            "agricultural_biogas_m3_year": "Total Agrícola",
            "livestock_biogas_m3_year": "Total Pecuária",
            "urban_biogas_m3_year": "Total Urbano",
            "urban_waste_potential_m3_year": "Resíduos Urbanos",
            "rural_waste_potential_m3_year": "Resíduos Poda",
            "energy_potential_mwh_year": "Energia (MWh/ano)",
            "co2_reduction_tons_year": "Redução CO₂ (ton/ano)"
        }
        return display_names.get(self.data_column, "Potencial Total")

    def enforce_layer_mutual_exclusion(self) -> None:
        """Enforce mutual exclusion between MapBiomas and Biogas layers"""
        if self.show_mapbiomas and self.show_biogas:
            # MapBiomas takes priority - turn off biogas
            self.show_biogas = False

    def has_active_filters(self) -> bool:
        """Check if any filters are active"""
        return (
            self.data_column != "biogas_potential_m3_year" or
            bool(self.search_term) or
            self.show_mapbiomas
        )

    def get_active_filters_description(self) -> List[str]:
        """Get list of active filter descriptions"""
        filters = []

        # Data filter
        display_name = self.get_data_column_display_name()
        if display_name != "Potencial Total":
            filters.append(f"Resíduo: **{display_name}**")

        # Search filter
        if self.search_term:
            filters.append(f"Busca: **'{self.search_term}'**")

        # MapBiomas layer
        if self.show_mapbiomas:
            filters.append("MapBiomas: **Ativo**")

        return filters
