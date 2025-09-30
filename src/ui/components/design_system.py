"""
Beautiful Design Components for CP2B Maps V2
Ported from V1 - Minimalistic and modern UI components following design best practices
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def render_page_header(
    title: str,
    subtitle: str = "",
    description: str = "",
    icon: str = "🗺️",
    show_stats: bool = True,
    municipality_count: int = 645,
    custom_metrics: Optional[Dict[str, Any]] = None
):
    """
    Render a beautiful, minimalistic page header with gradient background

    Args:
        title: Main page title
        subtitle: Secondary title/tagline
        description: Brief description text
        icon: Icon for the page
        show_stats: Whether to show municipality statistics
        municipality_count: Number of municipalities
        custom_metrics: Custom metrics to display
    """

    # Custom CSS for beautiful headers
    st.markdown("""
    <style>
    .main-header {
        padding: 2rem 0 1rem 0;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .header-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        font-weight: 300;
    }

    .header-description {
        font-size: 1rem;
        opacity: 0.8;
        margin-bottom: 0;
        font-weight: 400;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    .stats-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 1.5rem;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .stat-item {
        text-align: center;
        background: rgba(255, 255, 255, 0.15);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .page-breadcrumb {
        background: #f8f9fa;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }

    .breadcrumb-text {
        color: #495057;
        font-size: 0.9rem;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    header_html = f"""
    <div class="main-header">
        <div class="header-icon">{icon}</div>
        <h1 class="header-title">{title}</h1>
        {f'<div class="header-subtitle">{subtitle}</div>' if subtitle else ''}
        {f'<div class="header-description">{description}</div>' if description else ''}
    """

    # Add statistics if requested
    if show_stats or custom_metrics:
        header_html += '<div class="stats-container">'

        if show_stats:
            header_html += f"""
            <div class="stat-item">
                <div class="stat-number">{municipality_count}</div>
                <div class="stat-label">Municípios</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">SP</div>
                <div class="stat-label">Estado</div>
            </div>
            """

        if custom_metrics:
            for metric_value, metric_label in custom_metrics.items():
                header_html += f"""
                <div class="stat-item">
                    <div class="stat-number">{metric_value}</div>
                    <div class="stat-label">{metric_label}</div>
                </div>
                """

        header_html += '</div>'

    header_html += '</div>'

    st.markdown(header_html, unsafe_allow_html=True)

def render_green_header():
    """Render V1's signature green gradient header - Análise de Potencial de Biogás"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2E8B57 0%, #228B22 50%, #32CD32 100%);
                color: white; padding: 1.5rem; margin: -1rem -1rem 1rem -1rem;
                text-align: center; border-radius: 0 0 15px 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);'>
        <h1 style='margin: 0; font-size: 2.2rem; font-weight: 700;'>🗺️ Análise de Potencial de Biogás</h1>
        <p style='margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9;'>
            645 municípios de São Paulo
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, icon: str = "", description: str = "", level: int = 2):
    """
    Render a beautiful section header

    Args:
        title: Section title
        icon: Optional icon
        description: Optional description
        level: Header level (2-4)
    """

    header_tag = f"h{level}"
    icon_text = f"{icon} " if icon else ""

    st.markdown(f"""
    <div style="
        padding: 1rem 0 0.5rem 0;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 1.5rem;
    ">
        <{header_tag} style="
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 0.5rem;
        ">{icon_text}{title}</{header_tag}>
        {f'<p style="color: #6c757d; margin-bottom: 0; font-size: 0.95rem;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)

def render_feature_card(title: str, description: str, icon: str = "⭐", recommended: bool = False):
    """
    Render a feature card with modern styling and hover effects

    Args:
        title: Card title
        description: Card description
        icon: Icon for the card
        recommended: Whether to show recommended badge
    """

    recommended_badge = """
    <div style="
        position: absolute;
        top: -8px;
        right: -8px;
        background: #28a745;
        color: white;
        border-radius: 12px;
        padding: 4px 8px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    ">Recomendado</div>
    """ if recommended else ""

    st.markdown(f"""
    <div style="
        position: relative;
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 16px rgba(0,0,0,0.15)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';">
        {recommended_badge}
        <div style="
            font-size: 2rem;
            margin-bottom: 1rem;
            text-align: center;
        ">{icon}</div>
        <h4 style="
            color: #2c3e50;
            margin-bottom: 0.75rem;
            text-align: center;
            font-weight: 600;
        ">{title}</h4>
        <p style="
            color: #6c757d;
            margin-bottom: 0;
            text-align: center;
            line-height: 1.5;
        ">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def render_info_banner(message: str, banner_type: str = "info", icon: str = "ℹ️"):
    """
    Render a styled info banner

    Args:
        message: Message to display
        banner_type: Type of banner (info, success, warning, error)
        icon: Icon for the banner
    """

    colors = {
        "info": {"bg": "#d1ecf1", "border": "#bee5eb", "text": "#0c5460"},
        "success": {"bg": "#d4edda", "border": "#c3e6cb", "text": "#155724"},
        "warning": {"bg": "#fff3cd", "border": "#ffeaa7", "text": "#856404"},
        "error": {"bg": "#f8d7da", "border": "#f5c6cb", "text": "#721c24"}
    }

    color_scheme = colors.get(banner_type, colors["info"])

    st.markdown(f"""
    <div style="
        background-color: {color_scheme['bg']};
        border: 1px solid {color_scheme['border']};
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: {color_scheme['text']};
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <div style="font-size: 1.2rem;">{icon}</div>
        <div style="flex: 1; line-height: 1.5;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_breadcrumb(pages: List[str], current_page: str):
    """
    Render a breadcrumb navigation

    Args:
        pages: List of page names in order
        current_page: Current active page
    """

    breadcrumb_items = []
    for i, page in enumerate(pages):
        if page == current_page:
            breadcrumb_items.append(f'<span style="font-weight: 600; color: #667eea;">{page}</span>')
        else:
            breadcrumb_items.append(f'<span style="color: #6c757d;">{page}</span>')

    breadcrumb_text = ' → '.join(breadcrumb_items)

    st.markdown(f"""
    <div class="page-breadcrumb">
        <div class="breadcrumb-text">{breadcrumb_text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_enhanced_tabs(tab_names: List[str]):
    """
    Render enhanced, bigger tabs for better UX with V1 styling

    Args:
        tab_names: List of tab names

    Returns:
        Streamlit tabs object
    """

    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 1rem 2rem;
        background: white;
        border-radius: 8px;
        border: 2px solid transparent;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #e9ecef;
        transform: translateY(-1px);
    }

    .stTabs [aria-selected="true"] {
        background: #667eea !important;
        color: white !important;
        border-color: #5a67d8 !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    return st.tabs(tab_names)

def render_loading_animation(message: str = "Carregando dados..."):
    """Render a beautiful loading animation with V1 styling"""

    html_content = f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        text-align: center;
    ">
        <div style="
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        "></div>
        <div style="
            color: #6c757d;
            font-size: 1rem;
            font-weight: 500;
        ">{message}</div>
    </div>

    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """

    st.markdown(html_content, unsafe_allow_html=True)

# Predefined headers for common pages
def header_main_map():
    """Header for main map page"""
    render_page_header(
        title="Potencial de Biogás em São Paulo",
        subtitle="Análise Territorial do Potencial Energético",
        description="Explore o potencial teórico de produção de biogás a partir de resíduos orgânicos nos municípios paulistas",
        icon="🌱",
        show_stats=True
    )

def header_data_explorer():
    """Header for data explorer page"""
    render_page_header(
        title="Explorador de Dados",
        subtitle="Análise Detalhada e Comparativa",
        description="Analise, compare e explore os dados de potencial de biogás com ferramentas interativas avançadas",
        icon="🔍",
        show_stats=True
    )

def header_proximity_analysis():
    """Header for proximity analysis page"""
    render_page_header(
        title="Análise de Proximidade",
        subtitle="Análise Espacial Avançada",
        description="Analise municípios em raios específicos e identifique oportunidades regionais de desenvolvimento",
        icon="🎯",
        show_stats=True
    )

def header_advanced_analysis():
    """Header for advanced analysis page"""
    render_page_header(
        title="Análises Avançadas",
        subtitle="Insights Profissionais e Relatórios",
        description="Ferramentas avançadas para análise profissional do potencial de biogás e geração de relatórios",
        icon="📊",
        custom_metrics={"10+": "Análises", "645": "Municípios"}
    )

def render_styled_metrics(metrics_data: List[Dict[str, str]], columns: int = 4):
    """
    Render metrics in styled gradient cards with V1 styling

    Args:
        metrics_data: List of dicts with 'label', 'value', 'delta' keys
        columns: Number of columns to display
    """

    cols = st.columns(columns)

    for idx, metric in enumerate(metrics_data):
        with cols[idx % columns]:
            label = metric.get('label', '')
            value = metric.get('value', '')
            delta = metric.get('delta', '')
            icon = metric.get('icon', '📊')

            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                border: 1px solid #e9ecef;
                transition: all 0.2s ease;
                text-align: center;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="
                    color: #6c757d;
                    font-size: 0.9rem;
                    font-weight: 500;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{label}</div>
                <div style="
                    color: #2c3e50;
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 0.25rem;
                ">{value}</div>
                {f'<div style="color: #28a745; font-size: 0.85rem; font-weight: 500;">{delta}</div>' if delta else ''}
            </div>
            """, unsafe_allow_html=True)

def render_styled_table(dataframe, title: str = "", max_height: int = 400):
    """
    Render a styled table with zebra striping and V1 aesthetics

    Args:
        dataframe: Pandas DataFrame to display
        title: Optional table title
        max_height: Maximum height for scrolling
    """

    if title:
        st.markdown(f"""
        <div style="
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e9ecef;
        ">{title}</div>
        """, unsafe_allow_html=True)

    # Style the dataframe
    st.dataframe(
        dataframe,
        use_container_width=True,
        height=max_height
    )

def render_sidebar_section(title: str, icon: str = ""):
    """
    Render a styled sidebar section header with V1 styling

    Args:
        title: Section title
        icon: Optional icon
    """

    icon_text = f"{icon} " if icon else ""

    st.markdown(f"""
    <div style="
        color: #2c3e50;
        font-weight: 600;
        font-size: 1rem;
        margin-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    ">{icon_text}{title}</div>
    """, unsafe_allow_html=True)

def render_styled_expander(title: str, content_func, icon: str = "", expanded: bool = False):
    """
    Render a styled expander with V1 aesthetics

    Args:
        title: Expander title
        content_func: Function to call to render content inside
        icon: Optional icon
        expanded: Whether to start expanded
    """

    icon_text = f"{icon} " if icon else ""

    with st.expander(f"{icon_text}{title}", expanded=expanded):
        content_func()

def render_gradient_button(label: str, key: str, on_click=None, button_type: str = "primary"):
    """
    Render a button with gradient styling

    Args:
        label: Button label
        key: Unique button key
        on_click: Optional callback
        button_type: 'primary' (green) or 'secondary' (purple)
    """

    if button_type == "primary":
        gradient = "linear-gradient(135deg, #2E8B57 0%, #32CD32 100%)"
    else:
        gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    st.markdown(f"""
    <style>
    .stButton > button[key="{key}"] {{
        background: {gradient} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}

    .stButton > button[key="{key}"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if on_click:
        return st.button(label, key=key, on_click=on_click)
    else:
        return st.button(label, key=key)

def load_global_css():
    """
    Load global CSS styling from file
    """
    css_path = Path(__file__).parent.parent / "styles" / "global.css"

    if css_path.exists():
        with open(css_path, 'r') as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        logger.warning(f"Global CSS file not found at {css_path}")