"""
Configuração de Cenários para Análise de Biogás
Sistema de cenários de disponibilidade de resíduos para produção de biogás
"""

import streamlit as st
from typing import Literal
from dataclasses import dataclass

ScenarioType = Literal['pessimistic', 'realistic', 'optimistic', 'utopian']


@dataclass
class ScenarioConfig:
    """Configuração para cada cenário de disponibilidade"""
    name: str
    factor: float  # Multiplicador aplicado nos dados
    color: str
    description: str
    icon: str


SCENARIOS = {
    'pessimistic': ScenarioConfig(
        name='Pessimista',
        factor=0.10,  # 10%
        color='#f44336',
        description='Cenário conservador: apenas 10% dos resíduos disponíveis',
        icon='📉'
    ),
    'realistic': ScenarioConfig(
        name='Realista',
        factor=0.175,  # 17.5%
        color='#2196F3',
        description='Cenário realista: 15-20% dos resíduos disponíveis',
        icon='📊'
    ),
    'optimistic': ScenarioConfig(
        name='Otimista',
        factor=0.275,  # 27.5%
        color='#4CAF50',
        description='Cenário otimista: 25-30% dos resíduos disponíveis',
        icon='📈'
    ),
    'utopian': ScenarioConfig(
        name='Extremo/Utópico',
        factor=1.0,  # 100%
        color='#9C27B0',
        description='Cenário extremo: 100% dos resíduos disponíveis (dados originais)',
        icon='🚀'
    )
}


def init_scenario_state():
    """Inicializa cenário no session state"""
    if 'scenario' not in st.session_state:
        st.session_state.scenario = 'realistic'  # Padrão: Realista


def get_current_scenario() -> ScenarioType:
    """Retorna o cenário atualmente selecionado"""
    if 'scenario' not in st.session_state:
        init_scenario_state()
    return st.session_state.scenario


def get_scenario_config(scenario: ScenarioType = None) -> ScenarioConfig:
    """Retorna configuração de um cenário"""
    if scenario is None:
        scenario = get_current_scenario()
    return SCENARIOS[scenario]


def get_scenario_factor(scenario: ScenarioType = None) -> float:
    """Retorna fator de disponibilidade do cenário atual"""
    if scenario is None:
        scenario = get_current_scenario()
    return SCENARIOS[scenario].factor


def set_scenario(scenario: ScenarioType):
    """Define o cenário atual e limpa caches"""
    if scenario in SCENARIOS:
        old_scenario = st.session_state.get('scenario', None)
        st.session_state.scenario = scenario

        # Se mudou de cenário, limpar caches para forçar recálculo
        if old_scenario != scenario and old_scenario is not None:
            st.cache_data.clear()
    else:
        raise ValueError(f"Cenário inválido: {scenario}")


def clear_scenario_caches():
    """
    Limpa todos os caches quando o cenário muda
    Força recálculo de todos os dados
    """
    st.cache_data.clear()
