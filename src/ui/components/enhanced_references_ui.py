"""
CP2B Maps - Enhanced References UI Components
Beautiful, searchable, professional references display
"""

import streamlit as st
from typing import List, Optional, Dict, Any
import pandas as pd
from io import BytesIO

from src.data.references.enhanced_references_loader import (
    get_references_loader,
    ScientificPaper,
    CitationFormat,
    ReferenceCategory,
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_enhanced_references_header(stats: Dict[str, Any]):
    """
    Render modern teal gradient header with actual statistics

    Args:
        stats: Statistics dictionary from references loader
    """
    st.markdown("""
    <div style='background: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%);
                color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                text-align: center; border-radius: 0 0 25px 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
        <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
            📚 Referências Científicas
        </h1>
        <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
            Base acadêmica e metodológica do CP2B Maps
        </p>
        <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.85;'>
            🔬 Pesquisas Revisadas • 📊 Metodologias Validadas • 🌍 Fontes Oficiais
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats banner with actual data
    total_papers = stats.get('total_papers', 0)
    validated = stats.get('validated_papers', 0)
    complete = stats.get('complete_metadata', 0)
    year_range = stats.get('year_range', (0, 0))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>📖</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>{total_papers}</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Referências</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        categories_count = len(stats.get('by_category', {}))
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>🏷️</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>{categories_count}</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Categorias</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>✅</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>{validated}</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Validadas</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        year_text = f"{year_range[0]}-{year_range[1]}" if year_range[0] > 0 else "N/A"
        st.markdown(f"""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>📅</div>
            <div style='color: #14b8a6; font-size: 1.3rem; font-weight: 700; margin-bottom: 0.2rem;'>{year_text}</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Período</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def render_search_and_filters(loader) -> Dict[str, Any]:
    """
    Render search box and filters, return filter settings

    Args:
        loader: EnhancedReferencesLoader instance

    Returns:
        Dictionary with filter settings
    """
    st.markdown("### 🔍 Buscar e Filtrar Referências")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_query = st.text_input(
            "🔎 Buscar por palavra-chave",
            placeholder="Digite autor, título, residuo, palavra-chave...",
            help="Busca em título, autores, resumo, palavras-chave e journal"
        )

    with col2:
        # Citation format selector
        citation_format = st.selectbox(
            "📝 Formato da Citação",
            options=[CitationFormat.ABNT, CitationFormat.APA],
            format_func=lambda x: "ABNT (Brasil)" if x == CitationFormat.ABNT else "APA (Internacional)",
            help="Escolha o formato de citação preferido"
        )

    with col3:
        # Category filter
        categories = ["Todas"] + [cat.value for cat in ReferenceCategory]
        selected_category = st.selectbox(
            "🏷️ Categoria",
            options=categories,
            help="Filtrar por categoria"
        )

    # Year range filter
    col4, col5 = st.columns(2)
    with col4:
        start_year = st.number_input("📅 Ano Inicial", min_value=2000, max_value=2025, value=2020, step=1)
    with col5:
        end_year = st.number_input("📅 Ano Final", min_value=2000, max_value=2025, value=2025, step=1)

    return {
        'search_query': search_query,
        'citation_format': citation_format,
        'category': None if selected_category == "Todas" else ReferenceCategory(selected_category),
        'start_year': start_year,
        'end_year': end_year,
    }


def render_paper_card(paper: ScientificPaper, citation_format: CitationFormat, show_details: bool = False):
    """
    Render a single paper as a beautiful card

    Args:
        paper: ScientificPaper object
        citation_format: Citation format to use
        show_details: Whether to show expanded details
    """
    # Determine card color based on validation status
    if paper.has_validated_params:
        border_color = "#10b981"  # green
        badge_color = "#10b981"
        badge_text = "✅ VALIDADO"
    elif paper.metadata_confidence == "high":
        border_color = "#3b82f6"  # blue
        badge_color = "#3b82f6"
        badge_text = "🔵 ALTA CONFIANÇA"
    else:
        border_color = "#e5e7eb"  # gray
        badge_color = "#9ca3af"
        badge_text = "⏳ PENDENTE"

    # Card container
    st.markdown(f"""
    <div style='background: white; border-left: 4px solid {border_color}; border-radius: 8px;
                padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
    """, unsafe_allow_html=True)

    # Title and badge
    col1, col2 = st.columns([4, 1])

    with col1:
        # Title with DOI link
        if paper.doi:
            title_html = f'<h4 style="margin: 0 0 0.5rem 0; color: #1e293b;"><a href="https://doi.org/{paper.doi}" target="_blank" style="color: #0d9488; text-decoration: none;">{paper.title}</a></h4>'
        else:
            title_html = f'<h4 style="margin: 0 0 0.5rem 0; color: #1e293b;">{paper.title}</h4>'
        st.markdown(title_html, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background: {badge_color}; color: white; padding: 0.3rem 0.6rem;
                    border-radius: 6px; font-size: 0.75rem; font-weight: 600;
                    text-align: center; margin-top: 0.2rem;'>
            {badge_text}
        </div>
        """, unsafe_allow_html=True)

    # Citation
    citation = paper.format_citation(citation_format)
    st.markdown(f"**Citação ({citation_format.value.upper()}):**")
    st.markdown(citation)

    # Metadata row
    metadata_parts = []
    if paper.year:
        metadata_parts.append(f"📅 {paper.year}")
    if paper.sector_full:
        metadata_parts.append(f"🏷️ {paper.sector_full}")
    elif paper.sector:
        metadata_parts.append(f"🏷️ {paper.sector}")
    if paper.keywords:
        keywords_short = paper.keywords[:50] + "..." if len(paper.keywords) > 50 else paper.keywords
        metadata_parts.append(f"🔖 {keywords_short}")

    if metadata_parts:
        st.markdown(" • ".join(metadata_parts), unsafe_allow_html=False)

    # Action buttons
    button_col1, button_col2, button_col3, button_col4 = st.columns(4)

    with button_col1:
        if st.button("📋 Copiar Citação", key=f"copy_{paper.paper_id}", help="Copiar citação para área de transferência"):
            # Copy to clipboard functionality
            st.session_state[f'copied_{paper.paper_id}'] = citation
            st.success("✅ Citação copiada!", icon="📋")

    with button_col2:
        if paper.doi:
            st.markdown(f'<a href="https://doi.org/{paper.doi}" target="_blank" style="display: inline-block; padding: 0.5rem 1rem; background: #0d9488; color: white; text-decoration: none; border-radius: 6px; font-size: 0.9rem; font-weight: 500;">🔗 Abrir DOI</a>', unsafe_allow_html=True)

    with button_col3:
        if st.button("📑 BibTeX", key=f"bibtex_{paper.paper_id}", help="Exportar como BibTeX"):
            bibtex = paper.to_bibtex()
            st.code(bibtex, language="bibtex")

    with button_col4:
        details_key = f"details_{paper.paper_id}"
        if st.button("ℹ️ Detalhes", key=details_key, help="Ver mais informações"):
            show_details = not show_details

    # Expandable details
    if show_details or st.session_state.get(details_key, False):
        st.markdown("---")
        st.markdown("**📄 Informações Adicionais:**")

        details_col1, details_col2 = st.columns(2)

        with details_col1:
            if paper.abstract:
                st.markdown(f"**Resumo:** {paper.abstract}")
            if paper.publisher:
                st.markdown(f"**Editora:** {paper.publisher}")
            if paper.journal:
                st.markdown(f"**Periódico:** {paper.journal}")

        with details_col2:
            if paper.keywords:
                st.markdown(f"**Palavras-chave:** {paper.keywords}")
            if paper.primary_residue:
                st.markdown(f"**Resíduo Principal:** {paper.primary_residue}")
            if paper.validation_status:
                st.markdown(f"**Status de Validação:** {paper.validation_status}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_papers_list(papers: List[ScientificPaper], citation_format: CitationFormat, title: str = ""):
    """
    Render a list of papers with optional title

    Args:
        papers: List of ScientificPaper objects
        citation_format: Citation format to use
        title: Optional section title
    """
    if title:
        st.markdown(f"### {title}")

    if not papers:
        st.info("🔍 Nenhuma referência encontrada com os filtros aplicados.")
        return

    st.markdown(f"**{len(papers)} referências encontradas**")

    # Sort options
    sort_col1, sort_col2 = st.columns([3, 1])
    with sort_col1:
        sort_by = st.selectbox(
            "Ordenar por",
            options=["year_desc", "year_asc", "author", "title"],
            format_func=lambda x: {
                "year_desc": "Ano (mais recente primeiro)",
                "year_asc": "Ano (mais antigo primeiro)",
                "author": "Autor (A-Z)",
                "title": "Título (A-Z)"
            }[x],
            key="sort_papers"
        )

    # Sort papers
    if sort_by == "year_desc":
        papers = sorted(papers, key=lambda p: (p.year, p.authors), reverse=True)
    elif sort_by == "year_asc":
        papers = sorted(papers, key=lambda p: (p.year, p.authors))
    elif sort_by == "author":
        papers = sorted(papers, key=lambda p: p.authors.lower())
    elif sort_by == "title":
        papers = sorted(papers, key=lambda p: p.title.lower())

    # Render each paper
    for paper in papers:
        render_paper_card(paper, citation_format)


def render_export_options(papers: List[ScientificPaper], citation_format: CitationFormat):
    """
    Render export options for references

    Args:
        papers: List of papers to export
        citation_format: Citation format for export
    """
    if not papers:
        return

    st.markdown("---")
    st.markdown("### 📥 Exportar Referências")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export as BibTeX
        if st.button("📑 Exportar como BibTeX", help="Baixar todas as referências em formato BibTeX"):
            bibtex_content = "\n\n".join([paper.to_bibtex() for paper in papers])
            st.download_button(
                label="💾 Baixar BibTeX",
                data=bibtex_content,
                file_name="cp2b_referencias.bib",
                mime="text/plain",
                key="download_bibtex"
            )

    with col2:
        # Export as CSV
        if st.button("📊 Exportar como CSV", help="Baixar tabela de referências em CSV"):
            # Convert papers to DataFrame
            papers_data = []
            for paper in papers:
                papers_data.append({
                    'Título': paper.title,
                    'Autores': paper.authors,
                    'Ano': paper.year,
                    'Periódico': paper.journal,
                    'DOI': paper.doi,
                    'Setor': paper.sector_full or paper.sector,
                    'Palavras-chave': paper.keywords,
                })

            df = pd.DataFrame(papers_data)
            csv = df.to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="💾 Baixar CSV",
                data=csv,
                file_name="cp2b_referencias.csv",
                mime="text/csv",
                key="download_csv"
            )

    with col3:
        # Export as formatted text
        if st.button("📄 Exportar como Texto", help="Baixar referências formatadas em texto"):
            text_content = f"CP2B Maps - Referências Científicas\n"
            text_content += f"Formato: {citation_format.value.upper()}\n"
            text_content += f"Total: {len(papers)} referências\n"
            text_content += "=" * 80 + "\n\n"

            for i, paper in enumerate(papers, 1):
                text_content += f"{i}. {paper.format_citation(citation_format)}\n\n"

            st.download_button(
                label="💾 Baixar TXT",
                data=text_content,
                file_name="cp2b_referencias.txt",
                mime="text/plain",
                key="download_txt"
            )


def render_category_summary(stats: Dict[str, Any]):
    """
    Render summary statistics by category

    Args:
        stats: Statistics dictionary from loader
    """
    st.markdown("### 📊 Distribuição por Categoria")

    by_category = stats.get('by_category', {})

    if not by_category:
        st.info("Sem dados de categoria disponíveis.")
        return

    # Create columns for categories
    cat_cols = st.columns(len(by_category))

    category_names = {
        'agricultural': '🌾 Agrícola',
        'livestock': '🐄 Pecuário',
        'urban': '🏙️ Urbano',
        'industrial': '🏭 Industrial',
        'codigestion': '⚗️ Co-digestão',
        'methodology': '🔬 Metodologia',
        'data_source': '🗺️ Dados',
    }

    for i, (cat, count) in enumerate(by_category.items()):
        with cat_cols[i]:
            cat_name = category_names.get(cat, cat)
            st.markdown(f"""
            <div style='background: white; border-radius: 8px; padding: 1rem;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center;'>
                <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>{cat_name.split()[0]}</div>
                <div style='color: #14b8a6; font-size: 1.5rem; font-weight: 700;'>{count}</div>
                <div style='color: #6b7280; font-size: 0.8rem;'>{cat_name.split()[1]}</div>
            </div>
            """, unsafe_allow_html=True)
