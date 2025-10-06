"""
CP2B Maps - Design Theme System
Centralized color palette and styling constants from V1
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

# Primary Green Gradient (V1 Signature)
GREEN_DARK = "#2E8B57"      # Sea Green
GREEN_MED = "#228B22"       # Forest Green
GREEN_LIGHT = "#32CD32"     # Lime Green
GREEN_GRADIENT = f"linear-gradient(135deg, {GREEN_DARK} 0%, {GREEN_MED} 50%, {GREEN_LIGHT} 100%)"

# Accent Purple (Interactive Elements)
PURPLE_PRIMARY = "#667eea"
PURPLE_DARK = "#764ba2"
PURPLE_LIGHT = "#5a67d8"
PURPLE_GRADIENT = f"linear-gradient(135deg, {PURPLE_PRIMARY} 0%, {PURPLE_DARK} 100%)"

# Status Colors
SUCCESS = "#28a745"
SUCCESS_BG = "#d4edda"
SUCCESS_BORDER = "#c3e6cb"
SUCCESS_TEXT = "#155724"

INFO = "#17a2b8"
INFO_BG = "#d1ecf1"
INFO_BORDER = "#bee5eb"
INFO_TEXT = "#0c5460"

WARNING = "#ffc107"
WARNING_BG = "#fff3cd"
WARNING_BORDER = "#ffeaa7"
WARNING_TEXT = "#856404"

ERROR = "#dc3545"
ERROR_BG = "#f8d7da"
ERROR_BORDER = "#f5c6cb"
ERROR_TEXT = "#721c24"

# Neutral Colors
GRAY_DARK = "#2c3e50"
GRAY_MED = "#6c757d"
GRAY_LIGHT = "#e9ecef"
GRAY_LIGHTEST = "#f8f9fa"
WHITE = "#ffffff"

# ============================================================================
# TYPOGRAPHY
# ============================================================================

FONT_SIZE_H1 = "2.5rem"
FONT_SIZE_H2 = "2rem"
FONT_SIZE_H3 = "1.5rem"
FONT_SIZE_H4 = "1.25rem"
FONT_SIZE_BODY = "1rem"
FONT_SIZE_SMALL = "0.9rem"
FONT_SIZE_TINY = "0.7rem"

FONT_WEIGHT_LIGHT = 300
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700

# ============================================================================
# SPACING
# ============================================================================

SPACING_XS = "0.25rem"
SPACING_SM = "0.5rem"
SPACING_MD = "1rem"
SPACING_LG = "1.5rem"
SPACING_XL = "2rem"
SPACING_XXL = "3rem"

# ============================================================================
# BORDERS & SHADOWS
# ============================================================================

BORDER_RADIUS_SM = "8px"
BORDER_RADIUS_MD = "10px"
BORDER_RADIUS_LG = "12px"
BORDER_RADIUS_XL = "15px"
BORDER_RADIUS_ROUND = "50%"

SHADOW_SM = "0 2px 4px rgba(0, 0, 0, 0.1)"
SHADOW_MD = "0 2px 8px rgba(0, 0, 0, 0.1)"
SHADOW_LG = "0 4px 16px rgba(0, 0, 0, 0.15)"
SHADOW_XL = "0 8px 24px rgba(0, 0, 0, 0.2)"

# Purple shadow for active elements
SHADOW_PURPLE = "0 4px 8px rgba(102, 126, 234, 0.3)"

# ============================================================================
# MAP COLORS
# ============================================================================

# Biogas Infrastructure
BIOGAS_PLANT_COLOR = "#FF6B35"      # Orange for biogas plants
PIPELINE_DIST_COLOR = "#1976D2"     # Blue for distribution
PIPELINE_TRANSP_COLOR = "#F57C00"   # Orange for transport
MUNICIPALITY_BORDER = "#2E8B57"     # Green for boundaries

# MapBiomas Land Use Colors (common classes)
MAPBIOMAS_AGRICULTURE = "#E974ED"
MAPBIOMAS_FOREST = "#006400"
MAPBIOMAS_PASTURE = "#FFD966"
MAPBIOMAS_URBAN = "#AF2A2A"
MAPBIOMAS_WATER = "#0000FF"

# ============================================================================
# CHART COLORS
# ============================================================================

# Plotly color sequence matching V1
CHART_COLORS = [
    "#1f77b4",  # Blue
    "#ff7f0e",  # Orange
    "#2ca02c",  # Green
    "#d62728",  # Red
    "#9467bd",  # Purple
    "#8c564b",  # Brown
    "#e377c2",  # Pink
    "#7f7f7f",  # Gray
    "#bcbd22",  # Yellow-green
    "#17becf"   # Cyan
]

# ============================================================================
# TRANSITIONS & ANIMATIONS
# ============================================================================

TRANSITION_FAST = "0.2s ease"
TRANSITION_MED = "0.3s ease"
TRANSITION_SLOW = "0.5s ease"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_status_colors(status_type: str = "info") -> dict:
    """
    Get color scheme for status banners

    Args:
        status_type: Type of status (info, success, warning, error)

    Returns:
        Dictionary with bg, border, and text colors
    """
    colors = {
        "info": {"bg": INFO_BG, "border": INFO_BORDER, "text": INFO_TEXT},
        "success": {"bg": SUCCESS_BG, "border": SUCCESS_BORDER, "text": SUCCESS_TEXT},
        "warning": {"bg": WARNING_BG, "border": WARNING_BORDER, "text": WARNING_TEXT},
        "error": {"bg": ERROR_BG, "border": ERROR_BORDER, "text": ERROR_TEXT}
    }
    return colors.get(status_type, colors["info"])

def get_hover_style() -> str:
    """
    Get CSS for card hover effects

    Returns:
        CSS string for hover animations
    """
    return f"""
        transition: transform {TRANSITION_FAST}, box-shadow {TRANSITION_FAST};
    """

def get_card_style(elevated: bool = True) -> str:
    """
    Get CSS for styled cards

    Args:
        elevated: Whether to add shadow/elevation

    Returns:
        CSS string for card styling
    """
    shadow = SHADOW_MD if elevated else "none"
    return f"""
        background: {WHITE};
        border-radius: {BORDER_RADIUS_LG};
        padding: {SPACING_LG};
        margin: {SPACING_MD} 0;
        box-shadow: {shadow};
        border: 1px solid {GRAY_LIGHT};
    """