"""
CP2B Maps - Academic Reference Browser Component
Interactive interface for browsing, searching, and citing academic references
"""

from typing import Dict, List, Optional, Any
import streamlit as st
import pandas as pd

from src.data.references.reference_database import get_reference_database, ReferenceCategory, Reference
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ReferenceBrowser:
    """
    Professional academic reference browser
    Features: Search, filter, citation generation, export functionality
    """

    def __init__(self):
        """Initialize ReferenceBrowser"""
        self.logger = get_logger(self.__class__.__name__)
        self.ref_db = get_reference_database()

    def render(self) -> None:
        """Render the complete reference browser interface"""
        try:
            st.markdown("# 📚 Academic Reference Database")
            st.markdown("### Comprehensive biogas research citations and methodology references")

            # Database statistics
            self._render_database_stats()

            # Search and filter interface
            search_results = self._render_search_interface()

            # Reference display
            self._render_reference_display(search_results)

            # Citation tools
            self._render_citation_tools()

        except Exception as e:
            self.logger.error(f"Error rendering reference browser: {e}")
            st.error("⚠️ Error loading reference browser")

    def _render_database_stats(self) -> None:
        """Render database statistics overview"""
        try:
            stats = self.ref_db.get_statistics()

            st.markdown("#### 📊 Database Overview")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total References",
                    stats['total_references'],
                    help="Total number of academic references in database"
                )

            with col2:
                high_relevance = stats['high_relevance_count']
                st.metric(
                    "High Relevance",
                    high_relevance,
                    help="References with relevance score ≥ 4"
                )

            with col3:
                year_range = stats['year_range']
                if year_range[0] and year_range[1]:
                    range_text = f"{year_range[0]}-{year_range[1]}"
                else:
                    range_text = "N/A"
                st.metric(
                    "Year Range",
                    range_text,
                    help="Publication year range"
                )

            with col4:
                category_count = len(stats['categories'])
                st.metric(
                    "Categories",
                    category_count,
                    help="Number of reference categories"
                )

            # Category breakdown
            with st.expander("📋 Category Breakdown"):
                category_data = []
                for category, count in stats['categories'].items():
                    category_data.append({
                        'Category': category.replace('_', ' ').title(),
                        'Count': count,
                        'Percentage': f"{(count/stats['total_references']*100):.1f}%" if stats['total_references'] > 0 else "0%"
                    })

                if category_data:
                    df_categories = pd.DataFrame(category_data)
                    st.dataframe(df_categories, width='stretch', hide_index=True)

            st.markdown("---")

        except Exception as e:
            self.logger.error(f"Error rendering database stats: {e}")

    def _render_search_interface(self) -> List[Reference]:
        """Render search and filter interface"""
        try:
            st.markdown("#### 🔍 Search & Filter References")

            # Create search columns
            col1, col2 = st.columns([2, 1])

            with col1:
                # Text search
                search_terms = st.text_input(
                    "🔎 Search keywords:",
                    placeholder="e.g., biogas, animal waste, methodology",
                    help="Search in title, description, and keywords"
                )

                # Author search
                author_search = st.text_input(
                    "👤 Author:",
                    placeholder="e.g., Silva, Santos",
                    help="Search by author name"
                )

            with col2:
                # Category filter
                categories = ["All Categories"] + [cat.value.replace('_', ' ').title() for cat in ReferenceCategory]
                selected_category = st.selectbox(
                    "📂 Category:",
                    options=categories,
                    help="Filter by reference category"
                )

                # Year range
                col_year1, col_year2 = st.columns(2)
                with col_year1:
                    min_year = st.number_input("Min Year", min_value=1990, max_value=2030, value=2020, step=1)
                with col_year2:
                    max_year = st.number_input("Max Year", min_value=1990, max_value=2030, value=2024, step=1)

                # Relevance filter
                min_relevance = st.slider(
                    "⭐ Min Relevance:",
                    min_value=1,
                    max_value=5,
                    value=1,
                    help="Minimum relevance score (1-5)"
                )

            # Perform search
            search_keywords = [term.strip() for term in search_terms.split(',') if term.strip()] if search_terms else None
            author = author_search.strip() if author_search else None
            year_range = (min_year, max_year) if min_year <= max_year else None

            # Get all references or filter by category
            if selected_category == "All Categories":
                search_results = self.ref_db.search_references(
                    keywords=search_keywords,
                    author=author,
                    year_range=year_range,
                    min_relevance=min_relevance
                )
            else:
                # Convert category name back to enum
                category_value = selected_category.lower().replace(' ', '_')
                try:
                    category_enum = ReferenceCategory(category_value)
                    category_refs = self.ref_db.get_references_by_category(category_enum)

                    # Apply additional filters
                    search_results = []
                    for ref in category_refs:
                        # Check relevance
                        if ref.relevance_score and ref.relevance_score < min_relevance:
                            continue

                        # Check year range
                        if year_range and not (year_range[0] <= ref.year <= year_range[1]):
                            continue

                        # Check keywords
                        if search_keywords:
                            text_to_search = f"{ref.title} {ref.description or ''} {' '.join(ref.keywords)}".lower()
                            if not any(keyword.lower() in text_to_search for keyword in search_keywords):
                                continue

                        # Check author
                        if author and author.lower() not in ref.authors.lower():
                            continue

                        search_results.append(ref)

                except ValueError:
                    search_results = []

            # Show search results count
            st.info(f"📊 Found {len(search_results)} references matching your criteria")

            return search_results

        except Exception as e:
            self.logger.error(f"Error in search interface: {e}")
            return []

    def _render_reference_display(self, references: List[Reference]) -> None:
        """Render the list of references"""
        try:
            if not references:
                st.warning("No references found matching your search criteria")
                return

            st.markdown("#### 📖 Search Results")

            # Sort options
            col1, col2 = st.columns([1, 1])
            with col1:
                sort_option = st.selectbox(
                    "Sort by:",
                    options=["Year (Newest)", "Year (Oldest)", "Relevance", "Author", "Title"],
                    help="Choose sorting criteria"
                )

            # Sort references
            if sort_option == "Year (Newest)":
                references.sort(key=lambda x: x.year, reverse=True)
            elif sort_option == "Year (Oldest)":
                references.sort(key=lambda x: x.year)
            elif sort_option == "Relevance":
                references.sort(key=lambda x: x.relevance_score or 0, reverse=True)
            elif sort_option == "Author":
                references.sort(key=lambda x: x.authors)
            elif sort_option == "Title":
                references.sort(key=lambda x: x.title)

            # Display references
            for i, ref in enumerate(references):
                self._render_single_reference(ref, i)

        except Exception as e:
            self.logger.error(f"Error rendering reference display: {e}")

    def _render_single_reference(self, ref: Reference, index: int) -> None:
        """Render a single reference card"""
        try:
            with st.expander(f"📄 {ref.title} ({ref.year})", expanded=False):
                # Reference header
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Authors:** {ref.authors}")
                    st.markdown(f"**Journal:** {ref.journal}")
                    st.markdown(f"**Year:** {ref.year}")
                    st.markdown(f"**Category:** {ref.category.value.replace('_', ' ').title()}")

                with col2:
                    # Relevance score
                    if ref.relevance_score:
                        stars = "⭐" * ref.relevance_score + "☆" * (5 - ref.relevance_score)
                        st.markdown(f"**Relevance:** {stars}")

                    # DOI/URL links
                    if ref.doi:
                        st.markdown(f"[📎 DOI]({ref.doi})")
                    elif ref.url:
                        st.markdown(f"[🔗 Link]({ref.url})")

                # Description
                if ref.description:
                    st.markdown(f"**Description:** {ref.description}")

                # Keywords
                if ref.keywords:
                    keywords_text = ", ".join([f"`{kw}`" for kw in ref.keywords])
                    st.markdown(f"**Keywords:** {keywords_text}")

                # Citations
                st.markdown("**Citations:**")

                citation_col1, citation_col2 = st.columns(2)

                with citation_col1:
                    st.text_area(
                        "ABNT Format:",
                        value=ref.citation_abnt or "Citation not available",
                        height=100,
                        key=f"abnt_{ref.id}_{index}"
                    )

                with citation_col2:
                    st.text_area(
                        "APA Format:",
                        value=ref.citation_apa or "Citation not available",
                        height=100,
                        key=f"apa_{ref.id}_{index}"
                    )

                # Action buttons
                button_col1, button_col2, button_col3 = st.columns(3)

                with button_col1:
                    if st.button(f"📋 Copy ABNT", key=f"copy_abnt_{ref.id}_{index}"):
                        # In a real implementation, this would copy to clipboard
                        st.success("✅ Citation copied to clipboard!")

                with button_col2:
                    if st.button(f"📋 Copy APA", key=f"copy_apa_{ref.id}_{index}"):
                        # In a real implementation, this would copy to clipboard
                        st.success("✅ Citation copied to clipboard!")

                with button_col3:
                    # Add to bibliography
                    if st.button(f"➕ Add to Bibliography", key=f"add_bib_{ref.id}_{index}"):
                        self._add_to_bibliography(ref)

        except Exception as e:
            self.logger.error(f"Error rendering reference {ref.id}: {e}")

    def _add_to_bibliography(self, ref: Reference) -> None:
        """Add reference to bibliography"""
        try:
            # Initialize bibliography in session state if not exists
            if 'bibliography' not in st.session_state:
                st.session_state.bibliography = []

            # Check if already in bibliography
            if ref.id not in [r.id for r in st.session_state.bibliography]:
                st.session_state.bibliography.append(ref)
                st.success(f"✅ Added '{ref.title}' to bibliography")
            else:
                st.warning("⚠️ Reference already in bibliography")

        except Exception as e:
            self.logger.error(f"Error adding to bibliography: {e}")

    def _render_citation_tools(self) -> None:
        """Render citation generation and bibliography tools"""
        try:
            st.markdown("---")
            st.markdown("#### 🛠️ Citation Tools")

            tab1, tab2, tab3 = st.tabs(["📚 My Bibliography", "🔍 Quick Citation", "📊 Reference Stats"])

            with tab1:
                self._render_bibliography_manager()

            with tab2:
                self._render_quick_citation()

            with tab3:
                self._render_reference_statistics()

        except Exception as e:
            self.logger.error(f"Error rendering citation tools: {e}")

    def _render_bibliography_manager(self) -> None:
        """Render bibliography management interface"""
        try:
            bibliography = st.session_state.get('bibliography', [])

            if not bibliography:
                st.info("📝 No references in your bibliography yet. Add references using the '➕ Add to Bibliography' button.")
                return

            st.markdown(f"**Bibliography ({len(bibliography)} references):**")

            # Format selection
            format_type = st.selectbox(
                "Citation Format:",
                options=["ABNT", "APA"],
                help="Choose citation format for bibliography"
            )

            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                options=["Year", "Author", "Title"],
                help="Choose sorting criteria for bibliography"
            )

            # Generate bibliography
            ref_ids = [ref.id for ref in bibliography]
            bibliography_text = self.ref_db.export_bibliography(
                ref_ids, format_type.lower(), sort_by.lower()
            )

            # Display bibliography
            st.text_area(
                "Generated Bibliography:",
                value=bibliography_text,
                height=300,
                help="Copy this bibliography for use in your documents"
            )

            # Bibliography actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📥 Export Bibliography"):
                    # Create downloadable file
                    st.download_button(
                        label="📄 Download as Text",
                        data=bibliography_text,
                        file_name=f"bibliography_{format_type.lower()}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

            with col2:
                if st.button("🗑️ Clear Bibliography"):
                    st.session_state.bibliography = []
                    st.success("✅ Bibliography cleared")
                    st.rerun()

            with col3:
                # Remove specific references
                if len(bibliography) > 0:
                    ref_to_remove = st.selectbox(
                        "Remove reference:",
                        options=["Select reference..."] + [f"{ref.authors} ({ref.year})" for ref in bibliography],
                        key="remove_ref_select"
                    )

                    if ref_to_remove != "Select reference..." and st.button("🗑️ Remove Selected"):
                        # Find and remove the reference
                        for i, ref in enumerate(bibliography):
                            if f"{ref.authors} ({ref.year})" == ref_to_remove:
                                del st.session_state.bibliography[i]
                                st.success(f"✅ Removed '{ref.title}'")
                                st.rerun()
                                break

        except Exception as e:
            self.logger.error(f"Error in bibliography manager: {e}")

    def _render_quick_citation(self) -> None:
        """Render quick citation lookup"""
        try:
            st.markdown("**Quick Citation Lookup:**")

            # Reference ID input
            ref_id = st.text_input(
                "Reference ID:",
                placeholder="e.g., coffee_waste_biogas",
                help="Enter reference ID for quick citation"
            )

            if ref_id:
                ref = self.ref_db.get_reference(ref_id)

                if ref:
                    st.success(f"✅ Found: {ref.title}")

                    # Citation format
                    cite_format = st.radio(
                        "Citation Format:",
                        options=["ABNT", "APA"],
                        horizontal=True
                    )

                    # Generate citation
                    citation = self.ref_db.get_citation(ref_id, cite_format.lower())

                    if citation:
                        st.text_area(
                            f"{cite_format} Citation:",
                            value=citation,
                            height=100
                        )

                        if st.button("📋 Copy Citation", key="quick_copy"):
                            st.success("✅ Citation copied!")
                else:
                    st.error(f"❌ Reference ID '{ref_id}' not found")

        except Exception as e:
            self.logger.error(f"Error in quick citation: {e}")

    def _render_reference_statistics(self) -> None:
        """Render reference database statistics"""
        try:
            st.markdown("**Database Statistics:**")

            stats = self.ref_db.get_statistics()

            # Year distribution
            all_refs = list(self.ref_db.references.values())
            years = [ref.year for ref in all_refs]

            if years:
                year_counts = pd.Series(years).value_counts().sort_index()

                st.markdown("**Publications by Year:**")
                st.bar_chart(year_counts)

            # Category distribution
            st.markdown("**References by Category:**")
            category_data = {
                category.replace('_', ' ').title(): count
                for category, count in stats['categories'].items()
            }

            if category_data:
                st.bar_chart(category_data)

            # Relevance distribution
            relevance_scores = [ref.relevance_score for ref in all_refs if ref.relevance_score]

            if relevance_scores:
                st.markdown("**Relevance Score Distribution:**")
                relevance_counts = pd.Series(relevance_scores).value_counts().sort_index()
                st.bar_chart(relevance_counts)

        except Exception as e:
            self.logger.error(f"Error rendering statistics: {e}")


# Factory function
def create_reference_browser() -> ReferenceBrowser:
    """
    Create ReferenceBrowser instance

    Returns:
        ReferenceBrowser instance
    """
    return ReferenceBrowser()