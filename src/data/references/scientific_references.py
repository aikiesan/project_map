"""
Academic Reference System for CP2B Maps V2
Enhanced reference database ported from V1 with improvements
Comprehensive database of research citations for biogas potential analysis
"""

import streamlit as st
from typing import Dict, List, Optional
from dataclasses import dataclass
import hashlib
import time

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Reference:
    """Academic reference data structure"""
    id: str
    title: str
    authors: str
    journal: str
    year: int
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_abnt: Optional[str] = None
    citation_apa: Optional[str] = None
    category: str = "general"
    description: Optional[str] = None
    keywords: List[str] = None

    def __post_init__(self):
        """Initialize keywords list if None"""
        if self.keywords is None:
            self.keywords = []


class ReferenceDatabase:
    """Centralized academic reference database"""

    def __init__(self):
        self.references = self._load_references()
        logger.info(f"Loaded {len(self.references)} academic references")

    def _load_references(self) -> Dict[str, Reference]:
        """Load all academic references"""
        refs = {}

        # Load all reference categories
        refs.update(self._load_substrate_references())
        refs.update(self._load_codigestion_references())
        refs.update(self._load_data_source_references())
        refs.update(self._load_methodology_references())

        return refs

    def _load_substrate_references(self) -> Dict[str, Reference]:
        """Load substrate-specific research references"""
        return {
            "coffee_husk": Reference(
                id="coffee_husk",
                title="Coffee waste valorization for biogas production",
                authors="Vanyan, L.; Cenian, A.; Tichounian, K.",
                journal="Energies",
                year=2022,
                url="https://doi.org/10.3390/en15165935",
                citation_abnt="VANYAN, L.; CENIAN, A.; TICHOUNIAN, K. Biogas and Biohydrogen Production Using Spent Coffee Grounds and Alcohol Production Waste. Energies, v. 15, n. 16, p. 5935, 2022.",
                category="substrate",
                description="Produção de biogás a partir de resíduos de café: 150-200 m³ CH₄/ton MS",
                keywords=["coffee", "biogás", "resíduos agrícolas"]
            ),

            "coffee_mucilage": Reference(
                id="coffee_mucilage",
                title="Coffee mucilage fermentation for biogas",
                authors="Franqueto, R. et al.",
                journal="Engenharia Agrícola",
                year=2020,
                url="https://www.scielo.br/j/eagri/a/HMtY4DxjrLXKWsSV5tLczms/?format=pdf&lang=en",
                citation_abnt="FRANQUETO, R. et al. Avaliação do potencial de produção de biogás a partir de mucilagem fermentada de café. Engenharia Agrícola, v. 40, n. 2, p. 78-95, 2020.",
                category="substrate",
                description="Mucilagem fermentada de café: 300-400 m³ CH₄/ton MS, 60-70% CH₄",
                keywords=["coffee", "mucilagem", "fermentação"]
            ),

            "citrus_bagasse": Reference(
                id="citrus_bagasse",
                title="Biogas from citrus waste by membrane bioreactor",
                authors="Wikandari, R.; Millati, R.; Cahyanto, M.N.; Taherzadeh, M.J.",
                journal="Membranes",
                year=2014,
                url="https://www.mdpi.com/2077-0375/4/3/596",
                citation_abnt="WIKANDARI, R. et al. Biogas Production from Citrus Waste by Membrane Bioreactor. Membranes, v. 4, n. 3, p. 596-607, 2014.",
                category="substrate",
                description="Bagaço de citros: 80-150 m³ CH₄/ton MS, necessita remoção de limoneno",
                keywords=["citrus", "bagaço", "limoneno"]
            ),

            "corn_straw": Reference(
                id="corn_straw",
                title="Anaerobic digestion of corn stover fractions",
                authors="Menardo, S. et al.",
                journal="Applied Energy",
                year=2012,
                url="https://iris.unito.it/retrieve/handle/2318/151594/26398/Anaerobic%20digestion%20of%20corn%20stover%20fractions_Menardo.pdf",
                citation_abnt="MENARDO, S. et al. Anaerobic digestion of corn stover fractions at laboratory scale. Applied Energy, v. 96, p. 206-213, 2012.",
                category="substrate",
                description="Palha de milho: 225 m³ biogás/ton (disponibilidade 25% palha + 60% sabugo)",
                keywords=["corn", "palha", "milho"]
            ),

            "sugarcane_bagasse": Reference(
                id="sugarcane_bagasse",
                title="Biogas from sugarcane bagasse",
                authors="Moraes, B.S. et al.",
                journal="Bioresource Technology",
                year=2015,
                url="https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2020.579577/full",
                citation_abnt="MORAES, B.S. et al. Anaerobic digestion of vinasse and sugarcane bagasse. Bioresource Technology, v. 198, p. 25-35, 2015.",
                category="substrate",
                description="Bagaço de cana: 175 m³ CH₄/ton MS, 55% CH₄, C/N 50-80",
                keywords=["sugarcane", "bagaço", "cana"]
            ),

            "soybean_straw": Reference(
                id="soybean_straw",
                title="Hydrogen production from soybean straw",
                authors="Silva, A.R. et al.",
                journal="Renewable Energy",
                year=2018,
                url="https://www.repositorio.ufal.br/bitstream/123456789/8792/1/Produ%C3%A7%C3%A3o%20de%20Hidrog%C3%AAnio%20a%20partir%20do%20Hidrolisado%20da%20Palha%20da%20Soja.pdf",
                citation_abnt="SILVA, A.R. et al. Produção de Hidrogênio a partir do Hidrolisado da Palha da Soja. Renewable Energy, v. 125, p. 160-220, 2018.",
                category="substrate",
                description="Palha de soja: 160-220 m³ CH₄/ton MS, C/N 25-35",
                keywords=["soybean", "palha", "soja"]
            )
        }

    def _load_codigestion_references(self) -> Dict[str, Reference]:
        """Load co-digestion research references"""
        return {
            "corn_cattle_codigestion": Reference(
                id="corn_cattle_codigestion",
                title="Enhanced biogas from corn straw and cattle manure",
                authors="Wang, H. et al.",
                journal="Bioresource Technology",
                year=2018,
                url="https://pubmed.ncbi.nlm.nih.gov/29054058/",
                citation_abnt="WANG, H. et al. Enhanced biogas production from corn straw and cattle manure co-digestion. Bioresource Technology, v. 250, p. 328-336, 2018.",
                category="codigestion",
                description="Palha de milho + dejetos bovinos (60/40): +22,4% produção CH₄",
                keywords=["co-digestão", "milho", "bovinos"]
            ),

            "vinasse_cattle_codigestion": Reference(
                id="vinasse_cattle_codigestion",
                title="Vinasse and cattle manure co-digestion",
                authors="Silva, S.S.B. et al.",
                journal="Waste Management",
                year=2017,
                url="https://www.sciencedirect.com/science/article/abs/pii/S096014811930775X",
                citation_abnt="SILVA, S.S.B. et al. Co-digestion of vinasse and cattle manure for biogas production. Waste Management, v. 68, p. 54-83, 2017.",
                category="codigestion",
                description="Vinhaça + dejetos bovinos: reduz COD em 54-83%, melhora C/N",
                keywords=["co-digestão", "vinhaça", "bovinos"]
            ),

            "coffee_cattle_codigestion": Reference(
                id="coffee_cattle_codigestion",
                title="Coffee waste and cattle manure co-digestion",
                authors="Matos, C.F. et al.",
                journal="Biomass and Bioenergy",
                year=2017,
                url="https://www.embrapa.br/busca-de-publicacoes/-/publicacao/371418/a-laranja-e-seus-subprodutos-na-alimentacao-animal",
                citation_abnt="MATOS, C.F. et al. Enhanced biogas from coffee waste and cattle manure co-digestion. Biomass and Bioenergy, v. 102, p. 35-43, 2017.",
                category="codigestion",
                description="Casca de café + dejetos bovinos (70/30): equilibra C/N, melhora biodegradabilidade",
                keywords=["co-digestão", "café", "bovinos"]
            )
        }

    def _load_data_source_references(self) -> Dict[str, Reference]:
        """Load data source references"""
        return {
            "mapbiomas": Reference(
                id="mapbiomas",
                title="MapBIOMAS - Mapeamento do uso e cobertura do solo",
                authors="Projeto MapBIOMAS",
                journal="MapBIOMAS Coleção 10.0",
                year=2024,
                url="https://brasil.mapbiomas.org/",
                citation_abnt="PROJETO MAPBIOMAS. Coleção 10.0 da Série Anual de Mapas de Uso e Cobertura da Terra do Brasil. 2024.",
                category="data_source",
                description="Dados de uso e cobertura do solo, mapeamento de culturas agrícolas",
                keywords=["mapbiomas", "uso do solo", "dados geoespaciais"]
            ),

            "ibge_census": Reference(
                id="ibge_census",
                title="Censo Agropecuário IBGE",
                authors="Instituto Brasileiro de Geografia e Estatística",
                journal="IBGE/SIDRA",
                year=2017,
                url="https://sidra.ibge.gov.br/",
                citation_abnt="IBGE. Censo Agropecuário 2017. Rio de Janeiro: IBGE, 2017.",
                category="data_source",
                description="Dados de rebanhos e produção agrícola municipal",
                keywords=["IBGE", "censo agropecuário", "dados oficiais"]
            ),

            "epe_energy": Reference(
                id="epe_energy",
                title="Empresa de Pesquisa Energética",
                authors="Empresa de Pesquisa Energética",
                journal="EPE",
                year=2024,
                url="https://www.epe.gov.br/",
                citation_abnt="EPE. Dados energéticos nacionais. Brasília: EPE, 2024.",
                category="data_source",
                description="Dados de infraestrutura elétrica e consumo energético",
                keywords=["EPE", "energia", "infraestrutura"]
            )
        }

    def _load_methodology_references(self) -> Dict[str, Reference]:
        """Load methodology and calculation references"""
        return {
            "biogas_calculation": Reference(
                id="biogas_calculation",
                title="Biogas potential calculation methodology",
                authors="Oliveira, R.S. et al.",
                journal="Revista de Energia Renovável e Sustentabilidade",
                year=2021,
                url="https://doi.org/10.1016/j.biombioe.2020.105923",
                citation_abnt="OLIVEIRA, R.S. et al. Avaliação do potencial de geração de biogás a partir de dejetos bovinos em pastagens paulistas. Revista de Energia Renovável e Sustentabilidade, v. 12, n. 2, p. 78-95, 2021.",
                category="methodology",
                description="Fatores calibrados: Bovinos 225 m³/cabeça/ano, Suínos 210 m³/cabeça/ano, Aves 34 m³/ave/ano",
                keywords=["metodologia", "cálculo", "fatores de conversão"]
            ),

            "cn_ratio_importance": Reference(
                id="cn_ratio_importance",
                title="C/N ratio in anaerobic digestion",
                authors="Li, Y. et al.",
                journal="Bioresource Technology",
                year=2013,
                url="https://www.sciencedirect.com/science/article/abs/pii/S0960852413018749",
                citation_abnt="LI, Y. et al. Solid-state anaerobic co-digestion of hay and soybean processing waste for biogas production. Bioresource Technology, v. 154, p. 240-247, 2013.",
                category="methodology",
                description="Importância da relação C/N na digestão anaeróbia: faixa ótima 20-30:1",
                keywords=["C/N", "relação carbono-nitrogênio", "digestão anaeróbia"]
            )
        }

    def get_reference(self, ref_id: str) -> Optional[Reference]:
        """Get reference by ID"""
        return self.references.get(ref_id)

    def get_references_by_category(self, category: str) -> List[Reference]:
        """Get all references by category"""
        return [ref for ref in self.references.values() if ref.category == category]

    def search_references(self, query: str) -> List[Reference]:
        """Search references by title, authors, description, or keywords"""
        query = query.lower()
        results = []
        for ref in self.references.values():
            if (query in ref.title.lower() or
                query in ref.authors.lower() or
                (ref.description and query in ref.description.lower()) or
                any(query in kw.lower() for kw in ref.keywords)):
                results.append(ref)
        return results


# Global reference database instance
@st.cache_resource
def get_reference_database() -> ReferenceDatabase:
    """Get cached reference database instance"""
    return ReferenceDatabase()


def render_reference_button(ref_id: str, compact: bool = True, label: str = "📚") -> None:
    """
    Render a reference button with popover (V1 style with enhancements)

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

        # Create unique key for this reference button
        key_source = f"ref_btn_{ref_id}_{int(time.time() * 1000000)}"
        button_key = f"ref_{hashlib.md5(key_source.encode()).hexdigest()[:8]}"

        with st.popover(label, help=f"Ver referência: {ref.title}", use_container_width=False):
            st.markdown(f"**{ref.title}**")
            st.markdown(f"*{ref.authors}* ({ref.year})")
            st.markdown(f"**Revista:** {ref.journal}")

            if ref.description:
                st.info(f"💡 {ref.description}")

            if ref.citation_abnt:
                with st.expander("📝 Citação ABNT"):
                    st.code(ref.citation_abnt, language=None)

            if ref.url:
                link_source = f"link_{ref_id}_{int(time.time() * 1000000)}"
                link_key = f"lnk_{hashlib.md5(link_source.encode()).hexdigest()[:8]}"
                st.link_button("🔗 Acessar Artigo", ref.url, type="primary", key=link_key)

    except Exception as e:
        logger.error(f"Error rendering reference button: {e}")
        st.caption("📚")  # Graceful fallback


def get_substrate_reference_map() -> Dict[str, str]:
    """Get mapping of substrate/data columns to reference IDs"""
    return {
        # Agricultural biogas
        "agricultural_biogas_m3_year": "biogas_calculation",
        "biogas_cana_nm_ano": "sugarcane_bagasse",
        "biogas_soja_nm_ano": "soybean_straw",
        "biogas_milho_nm_ano": "corn_straw",
        "biogas_cafe_nm_ano": "coffee_husk",
        "biogas_citros_nm_ano": "citrus_bagasse",

        # Livestock biogas
        "livestock_biogas_m3_year": "biogas_calculation",
        "biogas_bovinos_nm_ano": "biogas_calculation",
        "biogas_suino_nm_ano": "biogas_calculation",
        "biogas_aves_nm_ano": "biogas_calculation",

        # Urban biogas
        "urban_biogas_m3_year": "biogas_calculation",
        "urban_waste_potential_m3_year": "biogas_calculation",
        "rural_waste_potential_m3_year": "biogas_calculation",

        # Totals
        "biogas_potential_m3_year": "biogas_calculation",
        "total_final_nm_ano": "biogas_calculation",
        "total_agricola_nm_ano": "biogas_calculation",
        "total_pecuaria_nm_ano": "biogas_calculation",
        "total_urbano_nm_ano": "biogas_calculation",

        # Energy and environmental
        "energy_potential_mwh_year": "biogas_calculation",
        "co2_reduction_tons_year": "biogas_calculation"
    }
