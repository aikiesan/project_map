"""
Map Export Component for CP2B Maps
Export map visualizations to various formats (PNG, HTML, PDF)
SOLID: Single Responsibility - Handle map exports
"""

import streamlit as st
import folium
from folium import plugins
import base64
from io import BytesIO
from typing import Optional
import datetime
from pathlib import Path

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def export_map_to_html(map_obj: folium.Map, filename: Optional[str] = None) -> bytes:
    """
    Export Folium map to HTML format

    Args:
        map_obj: Folium Map object
        filename: Optional filename (auto-generated if None)

    Returns:
        HTML content as bytes
    """
    try:
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cp2b_map_{timestamp}.html"

        # Save to bytes buffer
        html_buffer = BytesIO()
        map_obj.save(html_buffer, close_file=False)
        html_buffer.seek(0)
        html_content = html_buffer.getvalue()

        logger.info(f"Map exported to HTML: {filename}")
        return html_content

    except Exception as e:
        logger.error(f"Error exporting map to HTML: {e}")
        raise


def create_map_screenshot_button(map_obj: folium.Map) -> None:
    """
    Create download button for map HTML export

    Args:
        map_obj: Folium Map object to export
    """
    try:
        st.markdown("#### 📥 Exportar Mapa")

        col1, col2 = st.columns(2)

        with col1:
            # HTML Export
            html_content = export_map_to_html(map_obj)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            st.download_button(
                label="💾 Download HTML",
                data=html_content,
                file_name=f"cp2b_map_{timestamp}.html",
                mime="text/html",
                help="Exportar mapa interativo em HTML",
                width='stretch'
            )

        with col2:
            # Instructions for screenshot
            with st.expander("📸 Como tirar screenshot"):
                st.markdown("""
                **Instruções para captura de imagem:**

                1. **Windows**:
                   - `Windows + Shift + S` → Selecionar área
                   - Ou use a Ferramenta de Captura

                2. **Mac**:
                   - `Cmd + Shift + 4` → Selecionar área

                3. **Linux**:
                   - `PrtScn` ou ferramenta do sistema

                💡 **Dica**: Maximize o mapa antes de capturar!
                """)

        logger.debug("Map export buttons rendered")

    except Exception as e:
        logger.error(f"Error creating export buttons: {e}")
        st.error("Erro ao criar botões de exportação")


def render_export_panel_compact(map_obj: folium.Map) -> None:
    """
    Compact export panel for sidebar integration

    Args:
        map_obj: Folium Map object to export
    """
    try:
        st.markdown("**📥 Exportar Mapa**")

        html_content = export_map_to_html(map_obj)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="💾 Download HTML",
            data=html_content,
            file_name=f"cp2b_map_{timestamp}.html",
            mime="text/html",
            help="Mapa interativo em HTML",
            use_container_width=True,
            key=f"export_map_{timestamp}"
        )

        st.caption("💡 Para imagem: use ferramenta de captura do sistema")

    except Exception as e:
        logger.error(f"Error rendering compact export panel: {e}")


def get_map_export_info() -> str:
    """
    Get information about map export capabilities

    Returns:
        Info text about exports
    """
    return """
    ### 📥 Opções de Exportação

    **Formatos Disponíveis:**
    - **HTML**: Mapa interativo completo (recomendado)
    - **PNG/JPG**: Via captura de tela do sistema

    **Conteúdo Incluído no Export:**
    - ✅ Todas as camadas visíveis
    - ✅ Municípios e dados de biogás
    - ✅ Plantas e infraestrutura
    - ✅ Controles de zoom e navegação
    - ✅ Popups e tooltips interativos

    **Como usar o HTML exportado:**
    1. Baixe o arquivo
    2. Abra em qualquer navegador
    3. Funciona offline!
    """


def create_quick_export_button(
    map_obj: folium.Map,
    button_text: str = "📥 Exportar",
    icon_only: bool = False
) -> None:
    """
    Create quick export button (minimal UI)

    Args:
        map_obj: Folium Map to export
        button_text: Button label
        icon_only: Show only icon if True
    """
    try:
        html_content = export_map_to_html(map_obj)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        label = "📥" if icon_only else button_text

        st.download_button(
            label=label,
            data=html_content,
            file_name=f"cp2b_map_{timestamp}.html",
            mime="text/html",
            help="Exportar mapa como HTML interativo"
        )

    except Exception as e:
        logger.error(f"Error creating quick export button: {e}")
