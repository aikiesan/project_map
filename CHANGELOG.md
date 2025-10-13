# Changelog

All notable changes to the CP2B Maps V2 project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-10-13

### 🎉 Major Release - Complete Platform Rewrite

#### Added
- **Modern Modular Architecture**: Complete rewrite with clean separation of concerns
- **8 Comprehensive Analysis Modules**:
  - 🏠 Main Map Page with interactive visualizations
  - 🔍 Data Explorer with charts, rankings, and statistics
  - 📊 Advanced Residue Analysis
  - 🎯 Proximity Analysis with customizable radius
  - 🍊 Bagacinho AI Assistant with RAG
  - 📚 Scientific References System
  - 🔬 Validated Research Data Page
  - ℹ️ About Page with methodology

- **Bagacinho AI Assistant**:
  - Integration with Google Gemini API
  - RAG (Retrieval-Augmented Generation) system
  - Context-aware responses based on municipal data
  - Chat history and conversation management

- **WCAG 2.1 Level A Accessibility**:
  - Complete keyboard navigation
  - Screen reader support (NVDA, JAWS, ORCA, VoiceOver)
  - Alternative text for all visualizations
  - Semantic HTML structure with ARIA landmarks
  - Portuguese language identification
  - Skip links and focus indicators

- **Scientific Reference System**:
  - 20+ peer-reviewed references
  - Auto-citation in ABNT format
  - Interactive popovers with full reference details
  - Categorized by substrate, co-digestion, data sources, methodology

- **Validated Research Data**:
  - FAPESP 2025/08745-2 research integration
  - Conservative availability factors
  - Agricultural, livestock, and MSW data
  - Complementary aviculture residues

- **Advanced Geospatial Features**:
  - Multiple map types (choropleth, proportional circles, heatmap)
  - MapBiomas land use/cover integration
  - Shapefile and raster data processing
  - Natural Breaks (Jenks) classification
  - Custom proximity analysis engine

- **Professional UI Components**:
  - V1-style green gradient headers
  - Modern design system with consistent styling
  - Loading states and animations
  - Enhanced data visualizations with Plotly
  - Export functionality (CSV, Excel)

- **Performance Optimizations**:
  - Smart caching with @st.cache_resource and @st.cache_data
  - Session state management to prevent reruns
  - Lazy loading of heavy modules
  - Memory monitoring utilities
  - Optimized raster processing

- **Scenario System**:
  - Support for multiple data scenarios
  - Easy switching between datasets
  - Scenario-specific configurations

#### Changed
- **Project Structure**: Reorganized into modular src/ directory
- **Data Loading**: Centralized data loaders with caching
- **Configuration Management**: Unified settings in config/ directory
- **Logging**: Professional logging configuration with levels
- **Error Handling**: Comprehensive error handling across all modules

#### Technical Improvements
- Python 3.8+ compatibility
- Streamlit 1.31+ with latest features
- GeoPandas for geospatial operations
- Folium for interactive maps
- Plotly for professional charts
- Rasterio for raster data processing
- SQLite database for municipal data
- Psutil for resource monitoring

#### Documentation
- Comprehensive README with installation guide
- ACCESSIBILITY_GUIDE.md for WCAG compliance
- DEPLOYMENT.md for Streamlit Cloud deployment
- DEVELOPMENT_STATUS.md tracking project phases
- Inline code documentation and docstrings

---

## [1.x] - 2024 (Legacy Version)

### Features (Archived)
- Basic municipal biogas potential mapping
- Simple data visualization
- Initial implementation of analysis features
- Foundation for V2 development

**Note**: V1 repository maintained separately at [cp2b_maps](https://github.com/aikiesan/cp2b_maps)

---

## Recent Commits (October 2025)

### [7cefbdf] - 2025-10-13
**fix: Add defensive initialization for session state page instances**
- Added defensive checks to prevent missing page instances
- Improved session state robustness

### [cf824c8] - 2025-10-12
**feat: Add Avicultura validated research data with complementary residues**
- Added poultry farming residue data
- Integrated complementary residues into research data page

### [386b606] - 2025-10-11
**Fix: Resolve Streamlit multiple rerun issue and deprecation warnings**
- Fixed multiple rerun bugs causing performance issues
- Resolved Streamlit deprecation warnings
- Improved tab rendering performance

### [a679fdf] - 2025-10-10
**perf: Fix multiple reloads and eliminate tab style flashing**
- Eliminated CSS loading on every rerun
- Fixed tab style flashing issue
- Optimized page load performance

### [7e8a020] - 2025-10-09
**feat: Add validated research data page and optimize app loading**
- New Validated Research Data page
- Optimized app initialization
- Improved loading times

### [4330888] - 2025-10-08
**docs: Add INPI SHA-256 hash report for software registration**
- Added INPI documentation for software registration
- Generated SHA-256 hash reports

### [44194b8] - 2025-10-07
**feat: Implement scenario system and fix performance issues**
- Introduced scenario selection system
- Fixed performance bottlenecks
- Improved data loading efficiency

### [007f284] - 2025-10-06
**feat: Activate Bagacinho IA assistant and UX improvements**
- Activated AI assistant functionality
- Enhanced user experience
- Integrated Google Gemini API

### [1520268] - 2025-10-05
**Fix horizontal legend bar in top-right corner with overlapping numbers**
- Fixed map legend positioning
- Resolved number overlap issues

### [c14de6b] - 2025-10-04
**Fix map legend duplication and implement layer management**
- Eliminated duplicate legends
- Improved layer control system

---

## Version Numbering

CP2B Maps follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes

---

## Roadmap

### v2.1.0 (Planned - Q1 2026)
- [ ] WCAG 2.1 Level AA compliance
- [ ] Additional AI assistant features
- [ ] Enhanced data export formats (GeoJSON, KML)
- [ ] Mobile-responsive design improvements
- [ ] Docker containerization
- [ ] API endpoints for external integrations

### v2.2.0 (Planned - Q2 2026)
- [ ] Multi-language support (English, Spanish)
- [ ] Advanced statistical analysis modules
- [ ] Temporal data analysis (historical trends)
- [ ] Economic feasibility calculator
- [ ] Environmental impact assessment tools
- [ ] Integration with external biogas databases

### v3.0.0 (Future)
- [ ] Real-time data updates
- [ ] Collaborative features (user accounts, sharing)
- [ ] Machine learning predictions
- [ ] Extended coverage (other Brazilian states)
- [ ] Mobile application

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**For detailed development status, see [DEVELOPMENT_STATUS.md](docs/DEVELOPMENT_STATUS.md)**
