"""
CP2B Maps - Validated Research Data Module
FAPESP 2025/08745-2 - NIPE-UNICAMP | Outubro 2025
Structured data for validated availability factors and research findings
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class AvailabilityFactors:
    """Availability correction factors for residues"""
    fc: float  # Collection factor
    fcp: float  # Competition factor
    fs: float  # Seasonal factor
    fl: float  # Logistic factor
    final_availability: float  # Final availability percentage

    def to_dict(self) -> Dict[str, float]:
        return {
            'FC (Coleta)': self.fc,
            'FCp (Competição)': self.fcp,
            'FS (Sazonal)': self.fs,
            'FL (Logístico)': self.fl,
            'Disponibilidade Final': self.final_availability
        }


@dataclass
class ResidueData:
    """Complete residue data with validated factors"""
    name: str
    generation: str  # Generation rate (kg/ton, m³/m³, etc.)
    destination: str  # Current destination
    factors: AvailabilityFactors
    justification: str  # Technical justification
    methane_potential: str  # m³ CH₄/ton MS
    moisture: str  # % moisture


# ============================================================================
# CANA-DE-AÇÚCAR (Sugar Cane) - FAPESP 2025/08745-2
# ============================================================================

CANA_RESEARCH_OVERVIEW = {
    'title': 'Disponibilidade Real de Resíduos de Cana-de-Açúcar para Produção de Biogás em São Paulo',
    'project': 'FAPESP 2025/08745-2',
    'institution': 'NIPE-UNICAMP',
    'date': 'Outubro 2025',
    'scenario': 'Cenário Realista - 2023',
    'main_results': {
        'biogas_potential': '6.077 milhões m³ CH₄/ano',
        'electricity': '13.369 GWh/ano (~6,7 milhões de residências)',
        'effective_availability': 'Palha: 25,2% | Vinhaça: 61,7% | Bagaço: 0%',
        'territorial_coverage': '512 municípios produtores, 425 usinas mapeadas',
        'cane_processed': '439 milhões de toneladas (SP, 2023)'
    },
    'key_findings': [
        '✅ Potencial realista 72% menor que teórico (devido a fatores de competição)',
        '✅ Palha responde por 92,4% do potencial de CH₄',
        '✅ 90% da cana SP está a <20km de uma usina existente',
        '⚠️ Bagaço indisponível (competição com cogeração obrigatória)',
        '📊 Validação: SIDRA vs MapBiomas (+6,5% divergência esperada)'
    ]
}

CANA_RESIDUES = {
    'bagaco': ResidueData(
        name='Bagaço de Cana-de-açúcar',
        generation='280 kg/ton cana (50% umidade)',
        destination='100% cogeração de energia elétrica e vapor de processo',
        factors=AvailabilityFactors(
            fc=1.00,
            fcp=1.00,
            fs=1.00,
            fl=1.00,
            final_availability=0.0
        ),
        justification="""
        **Bagaço é indisponível para biodigestão** devido à competição com cogeração obrigatória.

        **Justificativa Técnica:**
        - Angelo Gurgel (2015) demonstra competição acirrada entre cogeração e etanol pelo bagaço
        - Obrigatoriedade legal de autossuficiência energética das usinas
        - Receita adicional com venda de excedente elétrico ao grid
        - Investimentos já amortizados em caldeiras de alta pressão
        - Mesmo com avanço do etanol 2G, bagaço permanecerá prioritário para geração termelétrica

        **Fatores:**
        - FC = 1.00: Gerado na própria usina, captação total
        - FCp = 1.00: Obrigatório para operação (caldeiras)
        - FS = 1.00: Utilização contínua durante safra
        - FL = 1.00: Gerado no local de uso

        **Conclusão:** Disponibilidade final = **0%**
        """,
        methane_potential='175 m³ CH₄/ton MS',
        moisture='50%'
    ),

    'palha': ResidueData(
        name='Palha de Cana-de-açúcar',
        generation='280 kg/ton cana (15% umidade)',
        destination='Retorno ao solo (sustentabilidade) + Recolhimento mecanizado',
        factors=AvailabilityFactors(
            fc=0.80,
            fcp=0.65,
            fs=1.00,
            fl=0.90,
            final_availability=25.2
        ),
        justification="""
        **Palha tem 25,2% disponível** após considerar retorno obrigatório ao solo.

        **Justificativa Técnica:**
        - Embrapa recomenda retorno de 50-70% da palha ao solo para:
          • Manutenção de matéria orgânica
          • Controle de erosão
          • Ciclagem de nutrientes (N, P, K)
          • Redução de infestação de pragas
        - Modelo adota 65% de retorno (valor conservador)
        - Recolhimento excessivo causa degradação do solo

        **Fatores:**
        - FC = 0.80: 80% tecnicamente recolhível (enfardamento mecanizado)
        - FCp = 0.65: 65% deve retornar ao solo (Embrapa)
        - FS = 1.00: Safra concentrada maio-dezembro
        - FL = 0.90: 90% dentro de raio viável (20km)

        **Resultado:**
        - Geração total: 122,9 Mi ton/ano
        - **Disponível biogás: 33,0 Mi ton/ano (25,2%)**
        - Contribuição: **92,4% do potencial total de CH₄**
        """,
        methane_potential='200 m³ CH₄/ton MS',
        moisture='15%'
    ),

    'vinhaca': ResidueData(
        name='Vinhaça',
        generation='13 m³/m³ etanol produzido',
        destination='Fertirrigação obrigatória (CETESB) + Biodigestão',
        factors=AvailabilityFactors(
            fc=0.95,
            fcp=0.35,
            fs=1.00,
            fl=1.00,
            final_availability=61.7
        ),
        justification="""
        **Vinhaça tem 61,7% disponível** após fertirrigação obrigatória.

        **Justificativa Técnica:**
        - Legislação ambiental (CETESB P4.231) exige aplicação controlada no solo
        - Limites de potássio devem ser respeitados
        - Balanço hídrico de usina real (CTC) indica 30-40% fertirrigação obrigatória
        - Modelo adota 35% (cenário realista)
        - Excedente pode ser biodigerido sem prejuízo ambiental

        **Fatores:**
        - FC = 0.95: 95% captada em sistema fechado
        - FCp = 0.35: 35% fertirrigação obrigatória (dados CTC)
        - FS = 1.00: Geração contínua durante safra
        - FL = 1.00: Gerada na usina

        **Resultado:**
        - Geração total: 413,3 Mi m³/ano
        - **Disponível biogás: 272,2 Mi m³/ano (61,7%)**
        - Contribuição: **2,5% do potencial total de CH₄**
        """,
        methane_potential='20 m³ CH₄/m³ (PM base)',
        moisture='96-98%'
    ),

    'torta_filtro': ResidueData(
        name='Torta de Filtro',
        generation='35 kg/ton cana (80% umidade)',
        destination='Fertilizante orgânico + Biodigestão',
        factors=AvailabilityFactors(
            fc=0.90,
            fcp=0.40,
            fs=1.00,
            fl=1.00,
            final_availability=54.0
        ),
        justification="""
        **Torta de filtro tem 54,0% disponível** após uso como fertilizante direto.

        **Justificativa Técnica:**
        - 40% usado como fertilizante orgânico direto (prática estabelecida)
        - Rico em fósforo e matéria orgânica
        - Aplicação direta beneficia recuperação do solo
        - Excedente pode ser biodigerido

        **Fatores:**
        - FC = 0.90: 90% captada (filtração contínua)
        - FCp = 0.40: 40% usado como fertilizante direto
        - FS = 1.00: Geração contínua
        - FL = 1.00: Gerada na usina

        **Resultado:**
        - Geração total: 15,4 Mi ton/ano
        - **Disponível biogás: 8,3 Mi ton/ano (54,0%)**
        - Contribuição: **5,1% do potencial total de CH₄**
        """,
        methane_potential='175 m³ CH₄/ton MS',
        moisture='80%'
    )
}

# Contribution breakdown (for charts)
CANA_CONTRIBUTION = {
    'Palha': {'ch4': 5616, 'pct': 92.4, 'electricity': 12355},
    'Vinhaça': {'ch4': 150, 'pct': 2.5, 'electricity': 330},
    'Torta de Filtro': {'ch4': 311, 'pct': 5.1, 'electricity': 684},
    'Total': {'ch4': 6077, 'pct': 100.0, 'electricity': 13369}
}

# Top 10 municipalities (from research)
CANA_TOP_MUNICIPALITIES = [
    {'rank': 1, 'name': 'Morro Agudo', 'ch4': 86.7, 'electricity': 191, 'area': 92750},
    {'rank': 2, 'name': 'Barretos', 'ch4': 85.9, 'electricity': 189, 'area': 79145},
    {'rank': 3, 'name': 'Guaíra', 'ch4': 70.0, 'electricity': 154, 'area': 63500},
    {'rank': 4, 'name': 'Jaboticabal', 'ch4': 67.2, 'electricity': 148, 'area': 57550},
    {'rank': 5, 'name': 'Novo Horizonte', 'ch4': 60.7, 'electricity': 133, 'area': 42500},
    {'rank': 6, 'name': 'Rancharia', 'ch4': 59.6, 'electricity': 131, 'area': 52000},
    {'rank': 7, 'name': 'Valparaíso', 'ch4': 53.9, 'electricity': 118, 'area': 47300},
    {'rank': 8, 'name': 'Itápolis', 'ch4': 51.1, 'electricity': 112, 'area': 44800},
    {'rank': 9, 'name': 'Batatais', 'ch4': 49.9, 'electricity': 110, 'area': 43700},
    {'rank': 10, 'name': 'Bebedouro', 'ch4': 46.6, 'electricity': 103, 'area': 40900}
]

# Scenario comparison
CANA_SCENARIOS = {
    'Pessimista': {'ch4': 4354, 'electricity': 9578, 'delta': -28.3},
    'Realista': {'ch4': 6077, 'electricity': 13369, 'delta': 0.0},
    'Otimista': {'ch4': 10089, 'electricity': 22196, 'delta': 66.0},
    'Teórico (100%)': {'ch4': 21000, 'electricity': 46000, 'delta': 245.0}
}

# Validation data
CANA_VALIDATION = {
    'sidra_area': 5.48,  # Million hectares
    'mapbiomas_area': 5.85,  # Million hectares
    'divergence': 6.5,  # % (expected due to semi-perennial cycle)
    'coverage': 90,  # % of cane within 20km of existing plant
    'municipalities': 512,
    'plants': 425,
    'plants_biogas': 50,
    'plants_bioethanol': 375
}

# Scientific references
CANA_REFERENCES = [
    {
        'title': 'SIDRA/IBGE - Produção Agrícola Municipal (PAM 2023)',
        'url': 'https://sidra.ibge.gov.br',
        'type': 'Dados Primários'
    },
    {
        'title': 'MapBiomas Coleção 10 (2024) - Classificação de uso do solo',
        'url': 'https://mapbiomas.org',
        'type': 'Sensoriamento Remoto'
    },
    {
        'title': 'Angelo Gurgel (2015) - Competição entre etanol 2G e bioeletricidade',
        'url': None,
        'type': 'Literatura Científica'
    },
    {
        'title': 'Embrapa - Relatório Técnico 13: Balanço de Nitrogênio para Cana-de-Açúcar',
        'url': None,
        'type': 'Literatura Científica'
    },
    {
        'title': 'CETESB P4.231 - Fertirrigação com vinhaça',
        'url': None,
        'type': 'Normas Ambientais'
    },
    {
        'title': 'CTC - Balanço energético e hídrico de usina sucroenergética',
        'url': None,
        'type': 'Dados Primários'
    }
]


# ============================================================================
# OTHER CULTURES (Placeholder for future expansion)
# ============================================================================

def get_available_categories() -> List[str]:
    """Get list of available research categories"""
    return ['Agricultura', 'Pecuária', 'RSU', 'Indústria', 'Aquaponia']


def get_cultures_by_category(category: str) -> List[str]:
    """Get list of cultures/residues by category"""
    cultures = {
        'Agricultura': ['Cana-de-açúcar', 'Café', 'Citros', 'Milho', 'Soja', 'Silvicultura'],
        'Pecuária': ['Bovinocultura', 'Suinocultura', 'Avicultura'],
        'RSU': ['Poda Urbana', 'Resíduo Alimentício', 'Esgoto'],
        'Indústria': ['Laticínios', 'Cervejaria', 'Frigorífico'],
        'Aquaponia': ['Piscicultura']
    }
    return cultures.get(category, [])


def get_culture_data(culture: str) -> Dict[str, Any]:
    """Get complete research data for a specific culture"""
    if culture == 'Cana-de-açúcar':
        return {
            'overview': CANA_RESEARCH_OVERVIEW,
            'residues': CANA_RESIDUES,
            'contribution': CANA_CONTRIBUTION,
            'top_municipalities': CANA_TOP_MUNICIPALITIES,
            'scenarios': CANA_SCENARIOS,
            'validation': CANA_VALIDATION,
            'references': CANA_REFERENCES
        }
    else:
        # Placeholder for future cultures
        return None


def get_category_icon(category: str) -> str:
    """Get emoji icon for category"""
    icons = {
        'Agricultura': '🌾',
        'Pecuária': '🐄',
        'RSU': '🏙️',
        'Indústria': '🏭',
        'Aquaponia': '🐟'
    }
    return icons.get(category, '📊')


def get_culture_icon(culture: str) -> str:
    """Get emoji icon for specific culture"""
    icons = {
        'Cana-de-açúcar': '🌾',
        'Café': '☕',
        'Citros': '🍊',
        'Milho': '🌽',
        'Soja': '🫘',
        'Silvicultura': '🌲',
        'Bovinocultura': '🐄',
        'Suinocultura': '🐷',
        'Avicultura': '🐔',
        'Poda Urbana': '🌳',
        'Resíduo Alimentício': '🍽️',
        'Esgoto': '💧',
        'Laticínios': '🥛',
        'Cervejaria': '🍺',
        'Frigorífico': '🥩',
        'Piscicultura': '🐟'
    }
    return icons.get(culture, '📊')
