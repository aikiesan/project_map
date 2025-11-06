"""
CP2B Maps - Enhanced Scientific References Data Loader
Loads and processes scientific papers from Panorama_CP2B database
Combines existing references with validated research papers
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import streamlit as st

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class CitationFormat(Enum):
    """Citation format types"""
    ABNT = "abnt"  # Brazilian standard
    APA = "apa"    # American Psychological Association


class ReferenceCategory(Enum):
    """Reference categories for organization"""
    AGRICULTURAL = "agricultural"
    LIVESTOCK = "livestock"
    URBAN = "urban"
    INDUSTRIAL = "industrial"
    CODIGESTION = "codigestion"
    METHODOLOGY = "methodology"
    DATA_SOURCE = "data_source"


@dataclass
class ScientificPaper:
    """Scientific paper data model"""
    paper_id: int
    title: str
    authors: str
    year: int
    journal: str
    doi: str

    # Optional fields
    abstract: str = ""
    keywords: str = ""
    publisher: str = ""
    external_url: str = ""

    # Classification
    sector: str = ""
    sector_full: str = ""
    primary_residue: str = ""
    category: Optional[ReferenceCategory] = None

    # Validation
    validation_status: str = ""
    has_validated_params: bool = False
    metadata_confidence: str = ""

    # Metadata
    pdf_filename: str = ""
    codename_short: str = ""

    def __post_init__(self):
        """Post-initialization processing"""
        # Auto-categorize based on sector
        if self.sector:
            self.category = self._infer_category()

    def _infer_category(self) -> Optional[ReferenceCategory]:
        """Infer category from sector and residue"""
        sector_lower = self.sector.lower()
        residue_lower = self.primary_residue.lower()

        # Check for agricultural
        if any(x in sector_lower for x in ['cana', 'citros', 'cafe', 'milho', 'soja', 'ag_']):
            return ReferenceCategory.AGRICULTURAL

        # Check for livestock
        if any(x in sector_lower for x in ['bovino', 'suino', 'aves', 'pc_']):
            return ReferenceCategory.LIVESTOCK

        # Check for urban
        if any(x in sector_lower for x in ['urbano', 'rsu', 'lodo', 'ur_']):
            return ReferenceCategory.URBAN

        # Check for industrial
        if any(x in sector_lower for x in ['industrial', 'in_']):
            return ReferenceCategory.INDUSTRIAL

        # Check for co-digestion in keywords or title
        if any(x in (self.keywords + self.title).lower() for x in ['co-digest', 'codigest', 'co-ferm']):
            return ReferenceCategory.CODIGESTION

        # Check for methodology
        if any(x in (self.keywords + self.title).lower() for x in ['method', 'protocol', 'standard', 'vdi', 'iso']):
            return ReferenceCategory.METHODOLOGY

        return None

    def is_complete(self) -> bool:
        """Check if paper has complete metadata"""
        required_fields = [self.title, self.authors, self.journal]
        return all(field and field.strip() for field in required_fields)

    def format_citation(self, format_type: CitationFormat = CitationFormat.ABNT) -> str:
        """
        Format citation in specified format

        Args:
            format_type: Citation format (ABNT or APA)

        Returns:
            Formatted citation string
        """
        if format_type == CitationFormat.ABNT:
            return self._format_abnt()
        elif format_type == CitationFormat.APA:
            return self._format_apa()
        else:
            return self._format_abnt()  # Default to ABNT

    def _format_abnt(self) -> str:
        """Format citation in ABNT style"""
        # ABNT format: AUTHOR. Title. Journal, v. X, n. Y, p. A-B, Year.
        citation_parts = []

        # Authors (uppercase last names)
        if self.authors:
            # Simple uppercase for now (proper ABNT would need more parsing)
            authors_formatted = self.authors.upper()
            citation_parts.append(authors_formatted)

        # Title
        if self.title:
            citation_parts.append(f"{self.title}.")

        # Journal info
        if self.journal:
            journal_part = f"**{self.journal}**"
            if self.year:
                journal_part += f", {self.year}."
            citation_parts.append(journal_part)
        elif self.year:
            citation_parts.append(f"{self.year}.")

        # DOI
        if self.doi:
            doi_part = f"DOI: [{self.doi}](https://doi.org/{self.doi})"
            citation_parts.append(doi_part)

        return " ".join(citation_parts)

    def _format_apa(self) -> str:
        """Format citation in APA style"""
        # APA format: Author, A. A. (Year). Title. Journal Name, Volume(Issue), pages. DOI
        citation_parts = []

        # Authors (APA format)
        if self.authors:
            citation_parts.append(f"{self.authors}")

        # Year
        if self.year:
            citation_parts.append(f"({self.year}).")

        # Title
        if self.title:
            citation_parts.append(f"{self.title}.")

        # Journal
        if self.journal:
            citation_parts.append(f"*{self.journal}*.")

        # DOI
        if self.doi:
            doi_part = f"[https://doi.org/{self.doi}](https://doi.org/{self.doi})"
            citation_parts.append(doi_part)

        return " ".join(citation_parts)

    def to_bibtex(self) -> str:
        """Export as BibTeX entry"""
        # Generate BibTeX key
        first_author = self.authors.split(';')[0].split(',')[0].strip() if self.authors else "Unknown"
        key = f"{first_author.replace(' ', '')}{self.year}"

        # Build BibTeX entry
        bibtex = f"@article{{{key},\n"
        bibtex += f"  author = {{{self.authors}}},\n"
        bibtex += f"  title = {{{self.title}}},\n"
        if self.journal:
            bibtex += f"  journal = {{{self.journal}}},\n"
        bibtex += f"  year = {{{self.year}}},\n"
        if self.doi:
            bibtex += f"  doi = {{{self.doi}}},\n"
        if self.keywords:
            bibtex += f"  keywords = {{{self.keywords}}},\n"
        if self.publisher:
            bibtex += f"  publisher = {{{self.publisher}}},\n"
        bibtex += "}\n"

        return bibtex

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'journal': self.journal,
            'doi': self.doi,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'publisher': self.publisher,
            'external_url': self.external_url,
            'sector': self.sector,
            'sector_full': self.sector_full,
            'primary_residue': self.primary_residue,
            'category': self.category.value if self.category else None,
            'validation_status': self.validation_status,
            'has_validated_params': self.has_validated_params,
            'metadata_confidence': self.metadata_confidence,
        }


class EnhancedReferencesLoader:
    """
    Enhanced references loader combining existing and Panorama papers
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.papers: List[ScientificPaper] = []
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data"
        self.papers_file = self.data_dir / "panorama_scientific_papers.json"

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_papers(_self) -> List[ScientificPaper]:
        """
        Load all scientific papers from Panorama database
        Cached for 1 hour

        Returns:
            List of ScientificPaper objects
        """
        try:
            if not _self.papers_file.exists():
                _self.logger.warning(f"Papers file not found: {_self.papers_file}")
                return []

            with open(_self.papers_file, 'r', encoding='utf-8') as f:
                raw_papers = json.load(f)

            papers = []
            for raw_paper in raw_papers:
                try:
                    paper = ScientificPaper(
                        paper_id=raw_paper.get('paper_id', 0),
                        title=raw_paper.get('title', '').strip(),
                        authors=raw_paper.get('authors', '').strip(),
                        year=raw_paper.get('publication_year', 0),
                        journal=raw_paper.get('journal', '').strip(),
                        doi=raw_paper.get('doi', '').strip(),
                        abstract=raw_paper.get('abstract', '').strip(),
                        keywords=raw_paper.get('keywords', '').strip(),
                        publisher=raw_paper.get('publisher', '').strip(),
                        external_url=raw_paper.get('external_url', '').strip(),
                        sector=raw_paper.get('sector', '').strip(),
                        sector_full=raw_paper.get('sector_full', '').strip(),
                        primary_residue=raw_paper.get('primary_residue', '').strip(),
                        validation_status=raw_paper.get('validation_status', '').strip(),
                        has_validated_params=bool(raw_paper.get('has_validated_params', 0)),
                        metadata_confidence=raw_paper.get('metadata_confidence', '').strip(),
                        pdf_filename=raw_paper.get('pdf_filename', '').strip(),
                        codename_short=raw_paper.get('codename_short', '').strip(),
                    )

                    # Only add papers with minimum required data
                    if paper.title and paper.authors and paper.year:
                        papers.append(paper)

                except Exception as e:
                    _self.logger.error(f"Error parsing paper: {e}")
                    continue

            _self.logger.info(f"✅ Loaded {len(papers)} scientific papers from Panorama database")
            return papers

        except Exception as e:
            _self.logger.error(f"Failed to load papers: {e}", exc_info=True)
            return []

    def get_papers_by_category(self, category: ReferenceCategory) -> List[ScientificPaper]:
        """Get papers filtered by category"""
        if not self.papers:
            self.papers = self.load_papers()

        return [p for p in self.papers if p.category == category]

    def get_papers_by_year(self, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[ScientificPaper]:
        """Get papers filtered by year range"""
        if not self.papers:
            self.papers = self.load_papers()

        filtered = self.papers

        if start_year:
            filtered = [p for p in filtered if p.year >= start_year]
        if end_year:
            filtered = [p for p in filtered if p.year <= end_year]

        return filtered

    def search_papers(self, query: str) -> List[ScientificPaper]:
        """
        Search papers by keyword in title, authors, keywords, abstract

        Args:
            query: Search query string

        Returns:
            List of matching papers
        """
        if not self.papers:
            self.papers = self.load_papers()

        query_lower = query.lower()
        results = []

        for paper in self.papers:
            # Search in multiple fields
            searchable_text = " ".join([
                paper.title,
                paper.authors,
                paper.keywords,
                paper.abstract,
                paper.journal,
            ]).lower()

            if query_lower in searchable_text:
                results.append(paper)

        return results

    def get_papers_by_residue(self, residue: str) -> List[ScientificPaper]:
        """Get papers related to specific residue"""
        if not self.papers:
            self.papers = self.load_papers()

        residue_lower = residue.lower()
        return [p for p in self.papers if residue_lower in p.primary_residue.lower()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the references database"""
        if not self.papers:
            self.papers = self.load_papers()

        # Count by category
        category_counts = {}
        for category in ReferenceCategory:
            count = len([p for p in self.papers if p.category == category])
            if count > 0:
                category_counts[category.value] = count

        # Count by year
        year_counts = {}
        for paper in self.papers:
            year = paper.year
            year_counts[year] = year_counts.get(year, 0) + 1

        # Count validated vs pending
        validated = len([p for p in self.papers if p.has_validated_params])

        # Count complete vs incomplete
        complete = len([p for p in self.papers if p.is_complete()])

        return {
            'total_papers': len(self.papers),
            'by_category': category_counts,
            'by_year': dict(sorted(year_counts.items(), reverse=True)),
            'validated_papers': validated,
            'complete_metadata': complete,
            'year_range': (min(year_counts.keys()), max(year_counts.keys())) if year_counts else (0, 0),
        }


# Factory function with caching
@st.cache_resource
def get_references_loader() -> EnhancedReferencesLoader:
    """
    Get cached references loader instance

    Returns:
        Cached EnhancedReferencesLoader instance
    """
    return EnhancedReferencesLoader()
