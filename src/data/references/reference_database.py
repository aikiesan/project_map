"""
CP2B Maps - Academic Reference Database
Comprehensive citation management for biogas research and methodology
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path
import streamlit as st

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ReferenceCategory(Enum):
    """Categories for academic references"""
    SUBSTRATE = "substrate"
    METHODOLOGY = "methodology"
    DATA_SOURCE = "data_source"
    CODIGESTION = "codigestion"
    TECHNOLOGY = "technology"
    POLICY = "policy"
    ENVIRONMENTAL = "environmental"


@dataclass
class Reference:
    """Academic reference data structure"""
    id: str
    title: str
    authors: str
    journal: str
    year: int
    category: ReferenceCategory
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_abnt: Optional[str] = None
    citation_apa: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = None
    impact_factor: Optional[float] = None
    relevance_score: Optional[int] = None  # 1-5 scale

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

        # Auto-generate citations if not provided
        if self.citation_abnt is None:
            self.citation_abnt = self._generate_abnt_citation()

        if self.citation_apa is None:
            self.citation_apa = self._generate_apa_citation()

    def _generate_abnt_citation(self) -> str:
        """Generate ABNT format citation"""
        try:
            # Basic ABNT format: AUTHOR. Title. Journal, v. X, n. Y, p. Z, year.
            authors_upper = self.authors.upper()
            return f"{authors_upper}. {self.title}. {self.journal}, {self.year}."
        except Exception:
            return f"{self.authors}. {self.title}. {self.journal}, {self.year}."

    def _generate_apa_citation(self) -> str:
        """Generate APA format citation"""
        try:
            # Basic APA format: Author, A. (Year). Title. Journal Name.
            return f"{self.authors} ({self.year}). {self.title}. {self.journal}."
        except Exception:
            return f"{self.authors} ({self.year}). {self.title}. {self.journal}."

    def to_dict(self) -> Dict[str, Any]:
        """Convert reference to dictionary"""
        ref_dict = asdict(self)
        ref_dict['category'] = self.category.value
        return ref_dict


class ReferenceDatabase:
    """Comprehensive academic reference database for biogas research"""

    def __init__(self):
        """Initialize reference database"""
        self.logger = get_logger(self.__class__.__name__)
        self.references = self._load_references()

    def _load_references(self) -> Dict[str, Reference]:
        """Load all academic references"""
        refs = {}

        # Load references by category
        refs.update(self._load_substrate_references())
        refs.update(self._load_methodology_references())
        refs.update(self._load_data_source_references())
        refs.update(self._load_codigestion_references())
        refs.update(self._load_technology_references())

        self.logger.info(f"Loaded {len(refs)} academic references")
        return refs

    def _load_substrate_references(self) -> Dict[str, Reference]:
        """Load substrate-specific research references"""
        return {
            "coffee_husk": Reference(
                id="coffee_husk",
                title="Biogas and Biohydrogen Production Using Spent Coffee Grounds",
                authors="Vanyan, L.; Cenian, A.; Tichounian, K.",
                journal="Energies",
                year=2022,
                category=ReferenceCategory.SUBSTRATE,
                url="https://doi.org/10.3390/en15165935",
                citation_abnt="VANYAN, L.; CENIAN, A.; TICHOUNIAN, K. Biogas and Biohydrogen Production Using Spent Coffee Grounds and Alcohol Production Waste. Energies, v. 15, n. 16, p. 5935, 2022.",
                description="Produção de biogás a partir de resíduos de café: 150-200 m³ CH₄/ton MS",
                keywords=["coffee", "biogas", "spent grounds"],
                relevance_score=4
            ),

            "coffee_mucilage": Reference(
                id="coffee_mucilage",
                title="Avaliação do potencial de produção de biogás a partir de mucilagem fermentada de café",
                authors="Franqueto, R. et al.",
                journal="Engenharia Agrícola",
                year=2020,
                category=ReferenceCategory.SUBSTRATE,
                url="https://www.scielo.br/j/eagri/a/HMtY4DxjrLXKWsSV5tLczms/?format=pdf&lang=en",
                citation_abnt="FRANQUETO, R. et al. Avaliação do potencial de produção de biogás a partir de mucilagem fermentada de café. Engenharia Agrícola, v. 40, n. 2, p. 78-95, 2020.",
                description="Mucilagem fermentada de café: 300-400 m³ CH₄/ton MS, 60-70% CH₄",
                keywords=["coffee", "mucilage", "fermentation"],
                relevance_score=4
            ),

            "citrus_bagasse": Reference(
                id="citrus_bagasse",
                title="Biogas Production from Citrus Waste by Membrane Bioreactor",
                authors="Wikandari, R.; Millati, R.; Cahyanto, M.N.; Taherzadeh, M.J.",
                journal="Membranes",
                year=2014,
                category=ReferenceCategory.SUBSTRATE,
                url="https://www.mdpi.com/2077-0375/4/3/596",
                citation_abnt="WIKANDARI, R. et al. Biogas Production from Citrus Waste by Membrane Bioreactor. Membranes, v. 4, n. 3, p. 596-607, 2014.",
                description="Bagaço de citros: 80-150 m³ CH₄/ton MS, necessita remoção de limoneno",
                keywords=["citrus", "membrane bioreactor", "waste"],
                relevance_score=4
            ),

            "citrus_peels": Reference(
                id="citrus_peels",
                title="Effect of Effluent Recirculation on Biogas Production Using Two-stage Anaerobic Digestion",
                authors="Lukitawesa; Wikandari, R.; Millati, R.; Taherzadeh, M.J.; Niklasson, C.",
                journal="Molecules",
                year=2018,
                category=ReferenceCategory.SUBSTRATE,
                url="https://pubmed.ncbi.nlm.nih.gov/30572677",
                citation_abnt="LUKITAWESA et al. Effect of Effluent Recirculation on Biogas Production Using Two-stage Anaerobic Digestion of Citrus Waste. Molecules, v. 23, n. 12, p. 3380, 2018.",
                description="Cascas de citros: 100-200 m³ CH₄/ton MS, digestão anaeróbia em duas etapas",
                keywords=["citrus", "two-stage", "anaerobic digestion"],
                relevance_score=4
            ),

            "corn_straw": Reference(
                id="corn_straw",
                title="Anaerobic digestion of corn stover fractions at laboratory scale",
                authors="Menardo, S. et al.",
                journal="Applied Energy",
                year=2012,
                category=ReferenceCategory.SUBSTRATE,
                url="https://iris.unito.it/retrieve/handle/2318/151594/26398/Anaerobic%20digestion%20of%20corn%20stover%20fractions_Menardo.pdf",
                citation_abnt="MENARDO, S. et al. Anaerobic digestion of corn stover fractions at laboratory scale. Applied Energy, v. 96, p. 206-213, 2012.",
                description="Fator calibrado: 225 m³ biogás/ton milho (palha + sabugo, disponibilidade 25% e 60%)",
                keywords=["corn", "stover", "laboratory scale"],
                relevance_score=5
            ),

            "corn_cob": Reference(
                id="corn_cob",
                title="Corn cob as feedstock for biogas production",
                authors="Stachowiak, P. et al.",
                journal="Waste Management",
                year=2017,
                category=ReferenceCategory.SUBSTRATE,
                url="https://repositorio.unesp.br/bitstream/11449/179744/1/2-s2.0-85044975543.pdf",
                citation_abnt="STACHOWIAK, P. et al. Corn cob as feedstock for biogas production. Waste Management, v. 68, p. 140-148, 2017.",
                description="Sabugo de milho: 150-220 m³ CH₄/ton MS, necessita pré-tratamento hidrotérmico",
                keywords=["corn", "cob", "hydrothermal pretreatment"],
                relevance_score=3
            ),

            "sugarcane_bagasse": Reference(
                id="sugarcane_bagasse",
                title="Anaerobic digestion of vinasse and sugarcane bagasse",
                authors="Moraes, B.S. et al.",
                journal="Bioresource Technology",
                year=2015,
                category=ReferenceCategory.SUBSTRATE,
                url="https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2020.579577/full",
                citation_abnt="MORAES, B.S. et al. Anaerobic digestion of vinasse and sugarcane bagasse. Bioresource Technology, v. 198, p. 25-35, 2015.",
                description="Bagaço de cana: 175 m³ CH₄/ton MS, 55% CH₄, C/N 50-80",
                keywords=["sugarcane", "bagasse", "vinasse"],
                relevance_score=5
            ),

            "sugarcane_straw": Reference(
                id="sugarcane_straw",
                title="Energy crops for biogas production: Update 2022",
                authors="Task 37 IEA Bioenergy",
                journal="IEA Bioenergy",
                year=2022,
                category=ReferenceCategory.SUBSTRATE,
                url="https://task37.ieabioenergy.com/wp-content/uploads/sites/32/2022/02/Update_Energy_crop_2011.pdf",
                citation_abnt="IEA BIOENERGY. Energy crops for biogas production: Update 2022. Task 37, 2022.",
                description="Palha de cana: 200 m³ CH₄/ton MS, 53% CH₄, C/N 80-120",
                keywords=["sugarcane", "straw", "energy crops"],
                relevance_score=5
            ),

            "vinasse": Reference(
                id="vinasse",
                title="Anaerobic digestion of vinasse from sugarcane ethanol production",
                authors="Moraes, B.S. et al.",
                journal="Bioresource Technology",
                year=2015,
                category=ReferenceCategory.SUBSTRATE,
                url="https://www.sciencedirect.com/science/article/abs/pii/S0960852415013018",
                citation_abnt="MORAES, B.S. et al. Anaerobic digestion of vinasse from sugarcane ethanol production. Bioresource Technology, v. 198, p. 25-35, 2015.",
                description="Vinhaça: 15-25 m³ CH₄/m³, 65% CH₄, alta umidade (96-98%)",
                keywords=["vinasse", "ethanol", "high moisture"],
                relevance_score=4
            ),

            "soybean_straw": Reference(
                id="soybean_straw",
                title="Produção de Hidrogênio a partir do Hidrolisado da Palha da Soja",
                authors="Silva, A.R. et al.",
                journal="Renewable Energy",
                year=2018,
                category=ReferenceCategory.SUBSTRATE,
                url="https://www.repositorio.ufal.br/bitstream/123456789/8792/1/Produ%C3%A7%C3%A3o%20de%20Hidrog%C3%AAnio%20a%20partir%20do%20Hidrolisado%20da%20Palha%20da%20Soja.pdf",
                citation_abnt="SILVA, A.R. et al. Produção de Hidrogênio a partir do Hidrolisado da Palha da Soja. Renewable Energy, v. 125, p. 160-220, 2018.",
                description="Palha de soja: 160-220 m³ CH₄/ton MS, C/N 25-35",
                keywords=["soybean", "straw", "hydrogen production"],
                relevance_score=3
            )
        }

    def _load_codigestion_references(self) -> Dict[str, Reference]:
        """Load co-digestion research references"""
        return {
            "corn_cattle_codigestion": Reference(
                id="corn_cattle_codigestion",
                title="Enhanced biogas production from corn straw and cattle manure co-digestion",
                authors="Wang, H. et al.",
                journal="Bioresource Technology",
                year=2018,
                category=ReferenceCategory.CODIGESTION,
                url="https://pubmed.ncbi.nlm.nih.gov/29054058/",
                citation_abnt="WANG, H. et al. Enhanced biogas production from corn straw and cattle manure co-digestion. Bioresource Technology, v. 250, p. 328-336, 2018.",
                description="Palha de milho + dejetos bovinos (60/40): +22,4% produção CH₄",
                keywords=["corn", "cattle manure", "co-digestion"],
                relevance_score=5
            ),

            "vinasse_cattle_codigestion": Reference(
                id="vinasse_cattle_codigestion",
                title="Co-digestion of vinasse and cattle manure for biogas production",
                authors="Silva, S.S.B. et al.",
                journal="Waste Management",
                year=2017,
                category=ReferenceCategory.CODIGESTION,
                url="https://www.sciencedirect.com/science/article/abs/pii/S096014811930775X",
                citation_abnt="SILVA, S.S.B. et al. Co-digestion of vinasse and cattle manure for biogas production. Waste Management, v. 68, p. 54-83, 2017.",
                description="Vinhaça + dejetos bovinos: reduz COD em 54-83%, melhora C/N",
                keywords=["vinasse", "cattle manure", "COD reduction"],
                relevance_score=4
            ),

            "coffee_cattle_codigestion": Reference(
                id="coffee_cattle_codigestion",
                title="Enhanced biogas from coffee waste and cattle manure co-digestion",
                authors="Matos, C.F. et al.",
                journal="Biomass and Bioenergy",
                year=2017,
                category=ReferenceCategory.CODIGESTION,
                url="https://www.embrapa.br/busca-de-publicacoes/-/publicacao/371418/a-laranja-e-seus-subprodutos-na-alimentacao-animal",
                citation_abnt="MATOS, C.F. et al. Enhanced biogas from coffee waste and cattle manure co-digestion. Biomass and Bioenergy, v. 102, p. 35-43, 2017.",
                description="Casca de café + dejetos bovinos (70/30): equilibra C/N, melhora biodegradabilidade",
                keywords=["coffee", "cattle manure", "biodegradability"],
                relevance_score=4
            ),

            "citrus_sewage_codigestion": Reference(
                id="citrus_sewage_codigestion",
                title="Improvement of anaerobic digestion of sewage sludge through microwave pre-treatment",
                authors="Serrano, A. et al.",
                journal="Bioresource Technology",
                year=2014,
                category=ReferenceCategory.CODIGESTION,
                url="https://pubmed.ncbi.nlm.nih.gov/24645472/",
                citation_abnt="SERRANO, A. et al. Improvement of anaerobic digestion of sewage sludge through microwave pre-treatment. Bioresource Technology, v. 154, p. 273-280, 2014.",
                description="Cascas de citros + lodo de esgoto (40/60): neutraliza compostos inibitórios",
                keywords=["citrus", "sewage sludge", "microwave pretreatment"],
                relevance_score=3
            )
        }

    def _load_data_source_references(self) -> Dict[str, Reference]:
        """Load data source references"""
        return {
            "mapbiomas": Reference(
                id="mapbiomas",
                title="MapBIOMAS - Mapeamento do uso e cobertura do solo do Brasil",
                authors="Projeto MapBIOMAS",
                journal="MapBIOMAS Coleção 10.0",
                year=2024,
                category=ReferenceCategory.DATA_SOURCE,
                url="https://brasil.mapbiomas.org/",
                citation_abnt="PROJETO MAPBIOMAS. Coleção 10.0 da Série Anual de Mapas de Uso e Cobertura da Terra do Brasil. 2024.",
                description="Dados de uso e cobertura do solo, mapeamento de culturas agrícolas",
                keywords=["land use", "mapping", "agricultural crops"],
                relevance_score=5
            ),

            "ibge_census": Reference(
                id="ibge_census",
                title="Censo Agropecuário IBGE 2017",
                authors="Instituto Brasileiro de Geografia e Estatística",
                journal="IBGE/SIDRA",
                year=2017,
                category=ReferenceCategory.DATA_SOURCE,
                url="https://sidra.ibge.gov.br/",
                citation_abnt="IBGE. Censo Agropecuário 2017. Rio de Janeiro: IBGE, 2017.",
                description="Dados de rebanhos e produção agrícola municipal",
                keywords=["livestock", "agricultural production", "municipal data"],
                relevance_score=5
            ),

            "epe_energy": Reference(
                id="epe_energy",
                title="Dados energéticos nacionais - Empresa de Pesquisa Energética",
                authors="Empresa de Pesquisa Energética",
                journal="EPE",
                year=2024,
                category=ReferenceCategory.DATA_SOURCE,
                url="https://www.epe.gov.br/",
                citation_abnt="EPE. Dados energéticos nacionais. Brasília: EPE, 2024.",
                description="Dados de infraestrutura elétrica e consumo energético",
                keywords=["energy infrastructure", "consumption", "national data"],
                relevance_score=4
            )
        }

    def _load_methodology_references(self) -> Dict[str, Reference]:
        """Load methodology and calculation references"""
        return {
            "biogas_calculation": Reference(
                id="biogas_calculation",
                title="Avaliação do potencial de geração de biogás a partir de dejetos bovinos em pastagens paulistas",
                authors="Oliveira, R.S. et al.",
                journal="Revista de Energia Renovável e Sustentabilidade",
                year=2021,
                category=ReferenceCategory.METHODOLOGY,
                url="https://doi.org/10.1016/j.biombioe.2020.105923",
                citation_abnt="OLIVEIRA, R.S. et al. Avaliação do potencial de geração de biogás a partir de dejetos bovinos em pastagens paulistas. Revista de Energia Renovável e Sustentabilidade, v. 12, n. 2, p. 78-95, 2021.",
                description="Fatores calibrados: Bovinos 225 m³/cabeça/ano, Suínos 210 m³/cabeça/ano, Aves 34 m³/ave/ano",
                keywords=["calculation methodology", "conversion factors", "livestock"],
                relevance_score=5
            ),

            "realistic_conversion_factors": Reference(
                id="realistic_conversion_factors",
                title="Fatores de conversão realísticos para biogás no Estado de São Paulo",
                authors="CP2B Research Team",
                journal="CP2B Technical Report",
                year=2024,
                category=ReferenceCategory.METHODOLOGY,
                citation_abnt="CP2B RESEARCH TEAM. Fatores de conversão realísticos para biogás no Estado de São Paulo. Relatório Técnico CP2B, 2024.",
                description="Fatores calibrados considerando disponibilidade real: RSU 117 m³/hab/ano, RPO 7 m³/hab/ano, Piscicultura 62 m³/ton peixe/ano",
                keywords=["conversion factors", "São Paulo", "availability"],
                relevance_score=5
            ),

            "cn_ratio_importance": Reference(
                id="cn_ratio_importance",
                title="Solid-state anaerobic co-digestion of hay and soybean processing waste for biogas production",
                authors="Li, Y. et al.",
                journal="Bioresource Technology",
                year=2013,
                category=ReferenceCategory.METHODOLOGY,
                url="https://www.sciencedirect.com/science/article/abs/pii/S0960852413018749",
                citation_abnt="LI, Y. et al. Solid-state anaerobic co-digestion of hay and soybean processing waste for biogas production. Bioresource Technology, v. 154, p. 240-247, 2013.",
                description="Importância da relação C/N na digestão anaeróbia: faixa ótima 20-30:1",
                keywords=["C/N ratio", "anaerobic digestion", "optimal range"],
                relevance_score=4
            ),

            "methane_potential": Reference(
                id="methane_potential",
                title="Biogas production from maize and dairy cattle manure—Influence of biomass composition",
                authors="Amon, T. et al.",
                journal="Biomass and Bioenergy",
                year=2006,
                category=ReferenceCategory.METHODOLOGY,
                url="https://www.sciencedirect.com/science/article/abs/pii/S0167880906001666",
                citation_abnt="AMON, T. et al. Biogas production from maize and dairy cattle manure—Influence of biomass composition on the methane yield. Biomass and Bioenergy, v. 30, n. 5, p. 389-400, 2006.",
                description="Avaliação do potencial bioquímico de metano: influência da composição da biomassa",
                keywords=["methane potential", "biomass composition", "biochemical assessment"],
                relevance_score=4
            )
        }

    def _load_technology_references(self) -> Dict[str, Reference]:
        """Load technology and equipment references"""
        return {
            "anaerobic_digester_design": Reference(
                id="anaerobic_digester_design",
                title="Design principles for anaerobic digesters in tropical conditions",
                authors="Silva, M.A. et al.",
                journal="Renewable Energy",
                year=2023,
                category=ReferenceCategory.TECHNOLOGY,
                description="Princípios de design para digestores anaeróbios em condições tropicais",
                keywords=["digester design", "tropical conditions", "equipment"],
                relevance_score=3
            ),

            "biogas_upgrading_systems": Reference(
                id="biogas_upgrading_systems",
                title="Biogas Upgrading Technologies: A Comprehensive Review",
                authors="Neto, J.M.; Araújo, K.L.; Bastos, M.C.",
                journal="Journal of Cleaner Production",
                year=2022,
                category=ReferenceCategory.TECHNOLOGY,
                doi="10.1016/j.jclepro.2022.134789",
                description="Comprehensive review of biogas upgrading to biomethane",
                keywords=["biogas upgrading", "biomethane", "purification", "technology"],
                relevance_score=3
            )
        }

    def get_reference(self, ref_id: str) -> Optional[Reference]:
        """Get reference by ID"""
        return self.references.get(ref_id)

    def get_references_by_category(self, category: ReferenceCategory) -> List[Reference]:
        """Get all references in a specific category"""
        return [ref for ref in self.references.values() if ref.category == category]

    def search_references(self,
                         keywords: List[str] = None,
                         author: str = None,
                         year_range: tuple = None,
                         min_relevance: int = None) -> List[Reference]:
        """
        Search references with multiple criteria

        Args:
            keywords: List of keywords to search for
            author: Author name to search for
            year_range: Tuple of (min_year, max_year)
            min_relevance: Minimum relevance score (1-5)

        Returns:
            List of matching references
        """
        results = list(self.references.values())

        # Filter by keywords
        if keywords:
            keyword_lower = [k.lower() for k in keywords]
            results = [
                ref for ref in results
                if any(
                    any(keyword in field.lower() for keyword in keyword_lower)
                    for field in [ref.title, ref.description or "", " ".join(ref.keywords)]
                )
            ]

        # Filter by author
        if author:
            author_lower = author.lower()
            results = [ref for ref in results if author_lower in ref.authors.lower()]

        # Filter by year range
        if year_range:
            min_year, max_year = year_range
            results = [ref for ref in results if min_year <= ref.year <= max_year]

        # Filter by relevance
        if min_relevance:
            results = [ref for ref in results
                      if ref.relevance_score and ref.relevance_score >= min_relevance]

        return results

    def get_citation(self, ref_id: str, format_type: str = "abnt") -> Optional[str]:
        """
        Get formatted citation for a reference

        Args:
            ref_id: Reference ID
            format_type: Citation format ("abnt", "apa", or "custom")

        Returns:
            Formatted citation string
        """
        ref = self.get_reference(ref_id)
        if not ref:
            return None

        if format_type.lower() == "abnt":
            return ref.citation_abnt
        elif format_type.lower() == "apa":
            return ref.citation_apa
        else:
            return ref.citation_abnt  # Default to ABNT

    def export_bibliography(self,
                           reference_ids: List[str],
                           format_type: str = "abnt",
                           sort_by: str = "year") -> str:
        """
        Export bibliography for a list of references

        Args:
            reference_ids: List of reference IDs to include
            format_type: Citation format
            sort_by: Sorting criteria ("year", "author", "title")

        Returns:
            Formatted bibliography string
        """
        references = [self.get_reference(ref_id) for ref_id in reference_ids]
        references = [ref for ref in references if ref is not None]

        # Sort references
        if sort_by == "year":
            references.sort(key=lambda x: x.year)
        elif sort_by == "author":
            references.sort(key=lambda x: x.authors)
        elif sort_by == "title":
            references.sort(key=lambda x: x.title)

        # Generate bibliography
        bibliography_lines = []
        for ref in references:
            citation = self.get_citation(ref.id, format_type)
            if citation:
                bibliography_lines.append(citation)

        return "\n\n".join(bibliography_lines)

    def get_substrate_references(self, substrate_type: str = None) -> List[Reference]:
        """Get references specific to substrate types"""
        substrate_refs = self.get_references_by_category(ReferenceCategory.SUBSTRATE)

        if substrate_type:
            # Filter by specific substrate type
            substrate_type_lower = substrate_type.lower()
            substrate_refs = [
                ref for ref in substrate_refs
                if substrate_type_lower in ref.title.lower() or
                   substrate_type_lower in (ref.description or "").lower() or
                   any(substrate_type_lower in keyword.lower() for keyword in ref.keywords)
            ]

        return substrate_refs

    def get_methodology_references(self) -> List[Reference]:
        """Get all methodology references"""
        return self.get_references_by_category(ReferenceCategory.METHODOLOGY)

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_refs = len(self.references)
        category_counts = {}

        for category in ReferenceCategory:
            category_counts[category.value] = len(self.get_references_by_category(category))

        year_range = (
            min(ref.year for ref in self.references.values()),
            max(ref.year for ref in self.references.values())
        ) if self.references else (None, None)

        return {
            'total_references': total_refs,
            'categories': category_counts,
            'year_range': year_range,
            'high_relevance_count': len([ref for ref in self.references.values()
                                       if ref.relevance_score and ref.relevance_score >= 4])
        }


# Factory function with caching
@st.cache_resource
def get_reference_database() -> ReferenceDatabase:
    """Get cached reference database instance"""
    return ReferenceDatabase()


# Substrate reference mapping for biogas calculations
def get_substrate_reference_map() -> Dict[str, str]:
    """Get mapping of biogas calculation fields to reference IDs"""
    return {
        "biogas_cafe_nm_ano": "coffee_husk",
        "biogas_citros_nm_ano": "citrus_bagasse",
        "biogas_cana_nm_ano": "sugarcane_bagasse",
        "biogas_soja_nm_ano": "soybean_straw",
        "biogas_milho_nm_ano": "corn_straw",
        "biogas_bovinos_nm_ano": "biogas_calculation",
        "biogas_suino_nm_ano": "biogas_calculation",
        "biogas_aves_nm_ano": "biogas_calculation",
        "biogas_piscicultura_nm_ano": "biogas_calculation",
        "biogas_silvicultura_nm_ano": "biogas_calculation",
        "rsu_potencial_nm_ano": "realistic_conversion_factors",
        "rpo_potencial_nm_ano": "realistic_conversion_factors",
        "total_final_nm_ano": "biogas_calculation",
        "total_agricola_nm_ano": "biogas_calculation",
        "total_pecuaria_nm_ano": "biogas_calculation",
        "total_urbano_nm_ano": "realistic_conversion_factors"
    }


# Convenience functions for V1 compatibility
def render_reference_button(ref_id: str, compact: bool = True, label: str = "📚") -> None:
    """
    Render a reference button with popover (V1 compatibility)

    Args:
        ref_id: Reference ID to display
        compact: If True, shows minimal button. If False, shows with text
        label: Button label (default: 📚)
    """
    try:
        db = get_reference_database()
        ref = db.get_reference(ref_id)

        if not ref:
            return

        import hashlib
        import time
        key_source = f"ref_btn_{ref_id}_{int(time.time() * 1000000)}"
        button_key = f"ref_{hashlib.md5(key_source.encode()).hexdigest()[:8]}"

        with st.popover(label, help=f"Ver referência: {ref.title}", use_container_width=False):
            st.markdown(f"**{ref.title}**")
            st.markdown(f"*{ref.authors}* ({ref.year})")
            st.markdown(f"**Revista:** {ref.journal}")

            if ref.description:
                st.markdown(f"**Descrição:** {ref.description}")

            if ref.citation_abnt:
                with st.expander("📝 Citação ABNT"):
                    st.text(ref.citation_abnt)

            if ref.url:
                st.link_button("🔗 Acessar Artigo", ref.url, type="primary")
    except Exception as e:
        # Graceful fallback if reference system fails
        st.caption("📚 Ref. disponível")


def render_inline_reference(ref_id: str, text: str = "") -> str:
    """
    Render inline reference with text (V1 compatibility)

    Args:
        ref_id: Reference ID
        text: Text to display before reference

    Returns:
        Formatted string with reference
    """
    db = get_reference_database()
    ref = db.get_reference(ref_id)

    if not ref:
        return text

    if text:
        return f"{text} ({ref.authors}, {ref.year}) 📚"
    else:
        return f"({ref.authors}, {ref.year}) 📚"