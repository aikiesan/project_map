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
        'title': 'IBGE/SIDRA - Produção Agrícola Municipal (PAM 2023)',
        'url': 'https://sidra.ibge.gov.br',
        'type': 'Dados Primários',
        'year': 2023
    },
    {
        'title': 'MapBiomas - Coleção 10.0 - Cobertura e Uso do Solo Brasil (2024)',
        'url': 'https://mapbiomas.org',
        'type': 'Sensoriamento Remoto',
        'year': 2024
    },
    {
        'title': 'Angelo Costa Gurgel (2015) - Competição entre etanol de segunda geração e bioeletricidade pelo uso do bagaço de cana-de-açúcar. Tese UNICAMP',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2015
    },
    {
        'title': 'Embrapa (2001) - Relatório Técnico 13: Modelo de Balanço de Nitrogênio para Cana-de-Açúcar',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2001
    },
    {
        'title': 'CTC (2020) - Balanço Hídrico e Energético de Usina Sucroenergética',
        'url': None,
        'type': 'Dados Primários',
        'year': 2020
    },
    {
        'title': 'CETESB P4.231 (2015) - Norma técnica para aplicação de vinhaça no solo',
        'url': None,
        'type': 'Normas Ambientais',
        'year': 2015
    }
]


# ============================================================================
# AVICULTURA (Poultry) - FAPESP 2025/08745-2
# ============================================================================

AVICULTURA_RESEARCH_OVERVIEW = {
    'title': 'Potencial Real de Biogás da Avicultura no Estado de São Paulo',
    'project': 'FAPESP 2025/08745-2',
    'institution': 'CP2B (Centro Paulista de Estudos em Biogás e Bioprodutos)',
    'date': 'Maio 2024',
    'scenario': 'Cenário Realista - Metodologia Conservadora',
    'main_results': {
        'biogas_potential': '728,2 milhões m³/ano',
        'electricity': '1.041 GWh/ano (~578.500 domicílios)',
        'effective_availability': 'Dejeto de Aves: 40% disponível',
        'territorial_coverage': '58,4 milhões de aves em granjas comerciais',
        'residue_available': '1,25 milhões ton/ano (dejeto disponível)'
    },
    'key_findings': [
        '✅ Potencial realista 81,72% menor que teórico (fatores de competição)',
        '✅ Co-digestão obrigatória (relação C/N: 4,66-11,55)',
        '⚠️ Forte competição com mercado de fertilizantes (FCp = 50%)',
        '💡 Biofertilizante como coproduto: 1,25 milhões ton/ano',
        '📍 Concentração em polos: Bastos (epicentro), Salto, Tatuí, Ourinhos',
        '🔬 Validação: 15 artigos científicos brasileiros e paulistas'
    ]
}

AVICULTURA_RESIDUES = {
    'dejeto_aves': ResidueData(
        name='Dejeto de Aves (Cama de Frango)',
        generation='1,58 kg resíduo/kg produto | 0,15 kg/ave/dia',
        destination='50% fertilizante orgânico + 40% biodigestão disponível',
        factors=AvailabilityFactors(
            fc=0.90,
            fcp=0.50,
            fs=1.00,
            fl=0.90,
            final_availability=40.5
        ),
        justification="""
        **Dejeto de aves tem 40,5% disponível** após competição com fertilizante.
        
        **Justificativa Técnica:**
        - Mercado consolidado de fertilizante orgânico (alto valor NPK)
        - Guerini Filho (2019): exclui cama de frango da disponibilidade real
        - Dos Santos (2023): valor econômico US$ 0,03/kg como fertilizante
        - Linhares (2022): alto teor de N, P₂O₅, K₂O crucial para solos tropicais
        - Redução da dependência de fertilizantes importados
        
        **Co-digestão Obrigatória:**
        - Relação C/N de 4,66-11,55 (muito baixa, ótimo: 25-30)
        - Acúmulo de amônia (NH₃) inibe microrganismos metanogênicos
        - Necessidade de substratos ricos em carbono (palha, bagaço)
        
        **Fatores:**
        - FC = 0.90: 90% coletável em sistemas confinados
        - FCp = 0.50: 50% competido por fertilizante orgânico
        - FS = 1.00: Geração contínua ao longo do ano
        - FL = 0.90: 90% dentro de raio viável (20-30 km)
        
        **Resultado:**
        - Geração total: 3,12 milhões ton/ano
        - **Disponível biogás: 1,25 milhões ton/ano (40,5%)**
        - **Redução de 81,72% do potencial teórico**
        
        **Nota sobre Resíduos Complementares:**
        GP Index 1,58 já incorpora carcaças mortas nas granjas (0,50 t/t produção).
        Resíduos de abatedouro e incubatório não foram quantificados (ver seção Limitações).
        """,
        methane_potential='360 m³/ton ST (BMP = 0,36 m³/kg ST)',
        moisture='60-75% (ST = 25-30%)'
    )
}

# Resíduos Complementares - NÃO QUANTIFICADOS (dados insuficientes)
AVICULTURA_RESIDUES_COMPLEMENTARY = {
    'note': """
    **Resíduos Complementares Não Quantificados no Escopo CP2B:**
    
    Estudos brasileiros validaram BMP para resíduos adicionais da cadeia avícola, 
    porém estes foram excluídos do cálculo de disponibilidade real devido a:
    """,
    'residues': [
        {
            'type': 'Efluente de Abatedouro (Frigorífico)',
            'components': 'Vísceras, sangue, penas, gorduras',
            'bmp_literature': '0,41 m³ CH₄/kg DQO (Sunada et al., 2012)',
            'fc': '95-100% (captação centralizada)',
            'fcp': '85-95% (competição com mercado rendering consolidado)',
            'barriers': [
                'Farinha de vísceras/penas: US$ 400-700/ton (10-50× mais que biogás)',
                'Sangue desidratado: US$ 800-1.200/ton (maior valor)',
                'Gordura animal: US$ 600-900/ton (biodiesel, sabão)',
                'Volume líquido imenso: 15 L efluente/ave (transporte inviável)',
                'Heterogeneidade: inibição por ácidos graxos de cadeia longa'
            ],
            'status': '❌ Excluído: competição rendering > 85%'
        },
        {
            'type': 'Resíduo de Incubatório (Hatchery)',
            'components': 'Cascas de ovos, embriões não eclodidos, pintinhos refugados',
            'bmp_literature': '0,14-0,16 m³ CH₄/kg SV em co-digestão (Matter et al., 2017)',
            'fc': '100% (incubatórios centralizados)',
            'fcp': '30-40% (competição com compostagem/corretivo calcário)',
            'barriers': [
                'Alto teor de cálcio: 371-400 g Ca/L (incrustação, inibição)',
                'Requer trituração industrial + diluição 4% ST',
                'Co-digestão obrigatória com água residuária suína',
                'Escala pequena: <5% vs. cama de aviário'
            ],
            'status': '⏸️ Fase 2: requer validação operacional'
        }
    ],
    'conclusion': """
    O GP Index 1,58 (Forster-Carneiro et al., 2013) já incorpora carcaças mortas 
    geradas nas granjas (0,50 t/t produção), cobrindo parcialmente o potencial de 
    mortalidade. Resíduos de abatedouro foram excluídos pela alta competição com 
    mercado rendering (FCp > 85%), e resíduos de incubatório pela complexidade 
    operacional (Ca, co-digestão) vs. retorno marginal.
    """
}

# Contribution breakdown (single residue type)
AVICULTURA_CONTRIBUTION = {
    'Dejeto de Aves': {'ch4': 728.2, 'pct': 100.0, 'electricity': 1041},
    'Total': {'ch4': 728.2, 'pct': 100.0, 'electricity': 1041}
}

# Top 10 municipalities (from report - Bastos as epicenter)
AVICULTURA_TOP_MUNICIPALITIES = [
    {'rank': 1, 'name': 'Bastos', 'ch4': 180.5, 'electricity': 258, 'birds': 14500000},
    {'rank': 2, 'name': 'Salto', 'ch4': 48.2, 'electricity': 69, 'birds': 3850000},
    {'rank': 3, 'name': 'Tatuí', 'ch4': 42.1, 'electricity': 60, 'birds': 3360000},
    {'rank': 4, 'name': 'Ourinhos', 'ch4': 38.7, 'electricity': 55, 'birds': 3090000},
    {'rank': 5, 'name': 'Rancharia', 'ch4': 35.3, 'electricity': 50, 'birds': 2820000},
    {'rank': 6, 'name': 'Itapetininga', 'ch4': 31.9, 'electricity': 46, 'birds': 2550000},
    {'rank': 7, 'name': 'Avaré', 'ch4': 28.5, 'electricity': 41, 'birds': 2280000},
    {'rank': 8, 'name': 'Itatiba', 'ch4': 25.1, 'electricity': 36, 'birds': 2010000},
    {'rank': 9, 'name': 'Cerquilho', 'ch4': 21.7, 'electricity': 31, 'birds': 1740000},
    {'rank': 10, 'name': 'Mogi Mirim', 'ch4': 18.3, 'electricity': 26, 'birds': 1460000}
]

# Scenario comparison
AVICULTURA_SCENARIOS = {
    'Pessimista': {'ch4': 509.7, 'electricity': 728, 'delta': -30.0},
    'Realista': {'ch4': 728.2, 'electricity': 1041, 'delta': 0.0},
    'Otimista': {'ch4': 1164.5, 'electricity': 1666, 'delta': 60.0},
    'Teórico (100%)': {'ch4': 3983.2, 'electricity': 5690, 'delta': 447.0}
}

# Validation data
AVICULTURA_VALIDATION = {
    'total_birds': 58.4,  # Million birds
    'farms': 2850,  # Licensed commercial farms
    'theoretical_reduction': 81.72,  # % reduction from theoretical
    'coverage': 92,  # % of production within 30km clusters
    'municipalities': 387,
    'main_cluster': 'Bastos',
    'cluster_contribution': 24.8,  # % of total potential (Bastos epicenter)
    'biofertilizer_coproduct': 1.25  # Million tons/year
}

# Scientific references
AVICULTURA_REFERENCES = [
    {
        'title': 'Mendes et al. (2023) - An overview of the integrated biogas production through agro-industrial and livestock residues in the Brazilian São Paulo state. WIREs Energy and Environment',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2023
    },
    {
        'title': 'Ribeiro, Barros & Tiago Filho (2016) - Power generation potential in posture aviaries in Brazil in the context of a circular economy. Sustainable Energy Technologies and Assessments',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2016
    },
    {
        'title': 'Ribeiro et al. (2018) - Feasibility of biogas and energy generation from poultry manure in Brazil. Waste Management & Research',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2018
    },
    {
        'title': 'Dos Santos, Vieira & de Nóbrega (2018) - Assessment of potential biogas production from multiple organic wastes in Brazil. Resources, Conservation & Recycling',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2018
    },
    {
        'title': 'Linhares et al. (2022) - Monitoring of ammonia concentrations from coir-husk litter of Brazilian poultry house using diode laser photoacoustic spectroscopy. Environmental Monitoring and Assessment',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2022
    },
    {
        'title': 'Silva, Santos & Oliveira (2021) - Determination of methane generation potential and evaluation of kinetic models in poultry wastes. Biocatalysis and Agricultural Biotechnology',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2021
    },
    {
        'title': 'Araújo dos Santos et al. (2023) - Reducing the environmental impacts of Brazilian chicken meat production using different waste recovery strategies. Journal of Environmental Management',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2023
    },
    {
        'title': 'Forster-Carneiro et al. (2013) - Biorefinery study of availability of agriculture residues and wastes for integrated biorefineries in Brazil. Resources, Conservation and Recycling',
        'url': None,
        'type': 'Dados Primários',
        'year': 2013
    },
    {
        'title': 'Guerini Filho et al. (2019) - Biomass availability assessment for biogas or methane production in Rio Grande do Sul, Brazil. Biomass Conversion and Biorefinery',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2019
    },
    {
        'title': 'Paranhos et al. (2020) - Methane production by co-digestion of poultry manure and lignocellulosic biomass. Bioresource Technology',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2020
    },
    {
        'title': 'Risso Errera et al. (2025) - Policy, regulatory issues, and case studies of full-scale projects. In: Biogas Science and Technology. Elsevier',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2025
    },
    {
        'title': 'Pedroza et al. (2021) - Methane and Electricity Production from Poultry Litter Digestion in the Amazon Region of Brazil. Waste and Biomass Valorization',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2021
    },
    {
        'title': 'Sousa et al. (2012) - Chemical and microbiological characterization of quail wastes. ASABE Annual International Meeting',
        'url': None,
        'type': 'Dados Primários',
        'year': 2012
    },
    {
        'title': 'Tessaro et al. (2015) - Energy capacity of broiler litter used as a substrate for biogas production in southwestern Paraná. Global Science and Technology',
        'url': None,
        'type': 'Literatura Científica',
        'year': 2015
    },
    {
        'title': 'IBGE - Censo Agropecuário e Produção da Pecuária Municipal (PPM)',
        'url': 'https://www.ibge.gov.br',
        'type': 'Dados Primários',
        'year': 2023
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
    elif culture == 'Avicultura':
        return {
            'overview': AVICULTURA_RESEARCH_OVERVIEW,
            'residues': AVICULTURA_RESIDUES,
            'contribution': AVICULTURA_CONTRIBUTION,
            'top_municipalities': AVICULTURA_TOP_MUNICIPALITIES,
            'scenarios': AVICULTURA_SCENARIOS,
            'validation': AVICULTURA_VALIDATION,
            'references': AVICULTURA_REFERENCES
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
