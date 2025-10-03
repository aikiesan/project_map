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
    Render professional academic footer component
    Single responsibility: Display methodology, data sources, and citation tools
    """
    try:
        st.markdown("---")
        st.markdown("### 📚 Informações Acadêmicas e Metodologia")

        # Three-column layout for organized information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📊 Fontes de Dados")
            st.markdown("""
            • **MapBIOMAS** Coleção 10.0
            • **IBGE** Censo Agropecuário 2017
            • **EPE** Dados Energéticos 2024
            • **SEADE** Dados Socioeconômicos
            • **Shapefiles** Geoespaciais SP
            """)

        with col2:
            st.markdown("#### 🔬 Metodologia")
            st.markdown("""
            • **Fatores de Conversão** calibrados para SP
            • **Relação C/N Ótima**: 20-30:1
            • **BMP Testing** validação laboratorial
            • **Análise Geoespacial** SIG avançado
            • **Validação** com dados de campo
            """)

        with col3:
            st.markdown("#### 📝 Citações")

            # ABNT format download
            abnt_citations = generate_abnt_citations()
            st.download_button(
                key="download_abnt_full",
                label="📥 Download ABNT",
                data=abnt_citations,
                file_name=f"cp2b_referencias_abnt_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                help="Baixar referências em formato ABNT"
            )

            # APA format download
            apa_citations = generate_apa_citations()
            st.download_button(
                key="download_apa_full",
                label="📥 Download APA",
                data=apa_citations,
                file_name=f"cp2b_referencias_apa_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                help="Baixar referências em formato APA"
            )

        # Version and update information
        st.caption(
            f"CP2B Maps V2 | "
            f"Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y')} | "
            f"Versão 2.0.0 | "
            f"São Paulo State - 645 municípios"
        )

        logger.debug("Academic footer rendered successfully")

    except Exception as e:
        logger.error(f"Error rendering academic footer: {e}", exc_info=True)
        st.error("⚠️ Erro ao carregar rodapé acadêmico")


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
