"""
Academic Footer Component for CP2B Maps V2
Professional footer with methodology summary and citation exports
SOLID: Single Responsibility - Display academic information and provide citation downloads
"""

import streamlit as st
import datetime
from typing import List
from src.data.references.scientific_references import ReferenceDatabase, get_reference_database
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def generate_abnt_citations() -> str:
    """
    Generate all references in ABNT format

    Returns:
        String with all ABNT citations
    """
    try:
        db = get_reference_database()
        citations = []

        for ref in db.references.values():
            if ref.citation_abnt:
                citations.append(ref.citation_abnt)

        return "\n\n".join(citations)

    except Exception as e:
        logger.error(f"Error generating ABNT citations: {e}")
        return "Erro ao gerar citações ABNT"


def generate_apa_citations() -> str:
    """
    Generate all references in APA format

    Returns:
        String with all APA citations
    """
    try:
        db = get_reference_database()
        citations = []

        for ref in db.references.values():
            # Generate basic APA format if citation_apa not provided
            citation = ref.citation_apa if ref.citation_apa else \
                f"{ref.authors} ({ref.year}). {ref.title}. {ref.journal}."
            citations.append(citation)

        return "\n\n".join(citations)

    except Exception as e:
        logger.error(f"Error generating APA citations: {e}")
        return "Erro ao gerar citações APA"


def render_academic_footer() -> None:
    """
    Render professional academic footer with FAPESP branding
    Single responsibility: Display methodology, data sources, and institutional information
    """
    try:
        # Professional academic footer with FAPESP branding
        st.markdown("""<div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2.5rem; margin: 3rem -1rem 0 -1rem; border-top: 4px solid #2E8B57; border-radius: 0;'><div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-bottom: 2rem;'><div><h4 style='color: #2c3e50; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600; font-family: "Montserrat", sans-serif;'>Data Sources</h4><div style='color: #495057; font-size: 0.9rem; line-height: 1.8;'><strong>MapBIOMAS</strong> Collection 10.0<br><strong>IBGE</strong> Agricultural Census 2017<br><strong>EPE</strong> Energy Data 2024<br><strong>SEADE</strong> Socioeconomic Data<br><strong>Geospatial</strong> Shapefiles São Paulo</div></div><div><h4 style='color: #2c3e50; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600; font-family: "Montserrat", sans-serif;'>Methodology</h4><div style='color: #495057; font-size: 0.9rem; line-height: 1.8;'>Calibrated conversion factors for SP<br>Optimal C/N ratio: 20-30:1<br>Advanced GIS spatial analysis<br>Field data validation</div></div><div><h4 style='color: #2c3e50; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600; font-family: "Montserrat", sans-serif;'>Research Support</h4><div style='color: #495057; font-size: 0.9rem; line-height: 1.8;'><strong>FAPESP</strong><br>Fundação de Amparo à Pesquisa<br>do Estado de São Paulo<br><br><strong>Project:</strong> CP2B Maps V2<br>Biogas Potential Analysis Platform</div></div></div><div style='border-top: 1px solid #dee2e6; padding-top: 1.5rem; margin-top: 1.5rem;'><div style='display: flex; justify-content: space-between; align-items: center;'><div style='color: #6c757d; font-size: 0.85rem;'><strong>CP2B Maps V2</strong> | Version 2.0.0 | Last Updated: {update_date} | São Paulo State - 645 Municipalities</div><div style='color: #6c757d; font-size: 0.85rem;'>Powered by <strong>FAPESP</strong> Research Grant</div></div></div></div>""".format(
            update_date=datetime.datetime.now().strftime('%d/%m/%Y')
        ), unsafe_allow_html=True)

        # Citation download section (separate, clean)
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown("**Academic Citations**")

        with col2:
            abnt_citations = generate_abnt_citations()
            st.download_button(
                label="Download ABNT",
                data=abnt_citations,
                file_name=f"cp2b_referencias_abnt_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                help="Download references in ABNT format",
                key="footer_abnt"
            )

        with col3:
            apa_citations = generate_apa_citations()
            st.download_button(
                label="Download APA",
                data=apa_citations,
                file_name=f"cp2b_referencias_apa_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                help="Download references in APA format",
                key="footer_apa"
            )

        logger.debug("Academic footer rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering academic footer: {e}", exc_info=True)
        st.error("Error loading academic footer")


def render_compact_academic_footer(key_suffix: str = "") -> None:
    """
    Render compact version of academic footer (for pages with limited space)
    """
    try:
        st.markdown("---")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption(
                "📚 **Fontes**: MapBIOMAS 10.0, IBGE 2017, EPE 2024 | "
                "🔬 **Metodologia**: Fatores calibrados SP, C/N: 20-30:1 | "
                f"📅 Atualizado: {datetime.datetime.now().strftime('%d/%m/%Y')}"
            )

        with col2:
            # Quick citation export
            abnt_citations = generate_abnt_citations()
            st.download_button(
                key=f"download_refs_compact{key_suffix}",
                label="📥 Referências",
                data=abnt_citations,
                file_name=f"cp2b_refs_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                help="Baixar referências completas"
            )

    except Exception as e:
        logger.error(f"Error rendering compact footer: {e}", exc_info=True)
