# Enhanced Scientific References System

## Overview

The References page has been enhanced with a comprehensive scientific papers database from the Panorama CP2B project, providing students and researchers with access to 58 validated scientific papers with complete metadata and citation capabilities.

## What's New

### 1. **Live Statistics Dashboard**
- Real-time paper count from database
- Number of categories
- Validated papers count
- Peer-review percentage

### 2. **New "Base Panorama" Tab**
Complete scientific papers database with:
- **58 Scientific Papers** from Panorama CP2B research
- **Full Metadata**: Title, Authors, Year, Journal, DOI, Keywords, Abstract
- **Validation Status**: Papers with validated technical parameters
- **Sector Classification**: Agricultural, Livestock, Urban, Industrial, etc.

### 3. **Advanced Search & Filtering**
- **Full-Text Search**: Search across title, authors, keywords, abstract, journal
- **Category Filter**: Filter by sector (Agricultural, Livestock, Urban, Industrial, Co-digestion, Methodology, Data Sources)
- **Year Range Filter**: Filter papers by publication year
- **Sort Options**: Sort by year (newest/oldest) or by relevance

### 4. **Citation Formats**
- **ABNT Format**: Brazilian academic standard
  - Uppercase authors
  - Bold journal names
  - DOI links
- **APA Format**: International standard
  - Author (Year) format
  - Italic journal names
  - Hyperlinked DOIs

### 5. **Export Capabilities**
Export filtered results in multiple formats:
- **BibTeX**: For LaTeX documents and reference managers
- **CSV**: For spreadsheets and data analysis
- **Formatted Text**: For direct copy-paste into documents

### 6. **Professional Paper Cards**
Each paper displays:
- 📄 Title (clickable DOI link)
- 👥 Authors
- 📚 Journal name
- 📅 Publication year
- 🔬 Sector/Residue information
- ✅ Validation badges (for papers with validated parameters)
- 🏷️ Category tags

## Usage Guide

### Accessing the Enhanced References

1. Navigate to **📚 Referências Científicas** page
2. View live statistics in the header cards
3. Click on **📚 Base Panorama** tab

### Searching for Papers

1. **Keyword Search**: Type keywords in the search box
   - Example: "cana-de-açúcar", "metano", "anaerobic digestion"
   - Searches across all text fields (title, authors, keywords, abstract)

2. **Category Filter**: Select specific sector
   - Agricultural: Sugarcane, soybean, corn, coffee, citrus residues
   - Livestock: Cattle, swine, poultry manure
   - Urban: Municipal solid waste, sewage sludge
   - Industrial: Industrial organic residues
   - Co-digestion: Multi-substrate studies
   - Methodology: Technical standards and protocols
   - Data Sources: Database and data collection studies

3. **Year Range**: Adjust sliders to filter by publication year
   - Min year: Oldest papers
   - Max year: Most recent papers

4. **Sort Results**:
   - Newest first (default)
   - Oldest first
   - By relevance (when searching)

### Viewing Paper Details

Each paper card shows:
- **DOI Link**: Click title to open paper on publisher's website
- **Complete Citation**: Formatted in selected style (ABNT/APA)
- **Validation Badge**: 🔬 indicates papers with validated technical parameters
- **Category Tag**: Shows sector classification
- **Metadata**: Authors, journal, year, keywords

### Exporting References

1. Apply desired filters (search, category, year range)
2. Scroll to **📥 Exportar Referências** section
3. Choose export format:
   - **BibTeX**: Click download button for .bib file
   - **CSV**: Click download for spreadsheet
   - **Text**: Copy formatted citations

### Citation Format Switching

- Use the dropdown in filters section to switch between ABNT and APA
- All papers update instantly
- Export files reflect selected format

## Technical Details

### Architecture

**Data Layer** (`src/data/references/enhanced_references_loader.py`):
- `ScientificPaper`: Dataclass model with auto-categorization
- `EnhancedReferencesLoader`: Main loader with caching
- `CitationFormat`: Enum for ABNT/APA formats
- `ReferenceCategory`: Enum for sector categories

**UI Layer** (`src/ui/components/enhanced_references_ui.py`):
- `render_search_and_filters()`: Interactive filtering interface
- `render_papers_list()`: Paper cards with sorting
- `render_export_options()`: Multi-format export
- `render_paper_card()`: Individual paper display

**Integration** (`src/ui/pages/references_v1.py`):
- Enhanced existing references page
- Added 6th tab for Panorama database
- Live statistics from database
- Maintained all existing functionality

### Data Source

Papers extracted from `data/panorama_scientific_papers.json`:
- Source: Panorama CP2B database (`scientific_papers` table)
- 58 papers with complete metadata
- Validated parameters from CP2B research
- Sectors: Agricultural (cana, citros, café), Livestock (bovino, suíno, aves), Urban (RSU, lodo), Industrial

### Caching Strategy

- `@st.cache_resource`: Singleton loader instance
- `@st.cache_data(ttl=3600)`: Paper data cached for 1 hour
- Automatic cache invalidation on data changes
- Optimized for Streamlit performance

### SOLID Principles Applied

1. **Single Responsibility**: Each function has one clear purpose
2. **Open/Closed**: Extended without modifying existing code
3. **Liskov Substitution**: All components are replaceable
4. **Interface Segregation**: Minimal, focused interfaces
5. **Dependency Injection**: Factory pattern for loader

## Statistics

Current database contains:
- **58 Total Papers**
- **~40 Validated Papers** (with technical parameters)
- **6 Categories**: Agricultural, Livestock, Urban, Industrial, Co-digestion, Methodology
- **Year Range**: 1995-2025 (approximately)
- **~70% Peer-Review Rate**

## Future Enhancements

Potential additions:
1. Advanced filters (author search, journal filter)
2. Paper comparison tool
3. Citation network visualization
4. PDF preview/download (if available)
5. User annotations and notes
6. Collections/favorites system
7. Citation count tracking
8. Related papers suggestions

## Integration with Existing Features

The enhanced system integrates seamlessly with:
- ✅ Existing reference tabs (Agricultural, Livestock, Co-digestion, Data Sources, Methodologies)
- ✅ Conversion factors database (linked by sector/residue)
- ✅ Municipal data (papers provide validation for parameters)
- ✅ Map visualizations (papers support methodology)

## Testing

To test the enhanced references:

1. **Start the app**:
   ```bash
   streamlit run app.py
   ```

2. **Navigate to References page**

3. **Test scenarios**:
   - Search for "cana-de-açúcar" → Should find sugarcane papers
   - Filter by "Agricultural" category → Should show agricultural papers
   - Adjust year range → Papers should filter accordingly
   - Switch citation formats → Format should update instantly
   - Export to BibTeX → Should download .bib file
   - Click DOI links → Should open papers in browser

4. **Verify statistics**:
   - Check if paper count matches database
   - Verify validation percentage is reasonable
   - Confirm category counts are correct

## Troubleshooting

### Papers not loading
- Check if `data/panorama_scientific_papers.json` exists
- Verify JSON is valid (use `python -m json.tool data/panorama_scientific_papers.json`)
- Clear Streamlit cache: Settings → Clear cache

### Search not working
- Ensure search query has at least 2 characters
- Check if any papers match the search terms
- Try simpler search terms

### Export not working
- Check browser allows downloads
- Verify papers are loaded before exporting
- Try different export formats

### Formatting issues
- Clear browser cache
- Check CSS is loading properly
- Verify Streamlit version compatibility

## Branch Information

- **Branch**: `claude/scientific-references-011CUqck8tRQ7YCqmKkEgarS`
- **Status**: Ready for testing
- **Commits**:
  - Part 1: Infrastructure (loader + UI components + data)
  - Part 2: Integration with existing page

## Files Modified/Created

**Created**:
- `data/panorama_scientific_papers.json` (58 papers, ~31KB)
- `src/data/references/enhanced_references_loader.py` (~400 lines)
- `src/ui/components/enhanced_references_ui.py` (~600 lines)
- `REFERENCES_ENHANCEMENT_GUIDE.md` (this file)

**Modified**:
- `src/ui/pages/references_v1.py` (+76 lines, enhanced with new tab)

**No files deleted or broken**

## Merge Safety

This enhancement is completely additive:
- ✅ No existing functionality removed
- ✅ All original tabs still work
- ✅ No breaking changes to other pages
- ✅ Independent feature (can be disabled by hiding tab)
- ✅ SOLID principles followed
- ✅ Comprehensive error handling
- ✅ Cached for performance

Safe to merge after testing confirms no issues.

---

**For questions or issues, refer to the code documentation or ask the development team.**
