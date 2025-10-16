"""
Widget de Seleção de Cenário para Sidebar
Permite ao usuário escolher o cenário de disponibilidade de resíduos
"""

import streamlit as st
from config.scenario_config import (
    SCENARIOS, get_current_scenario, set_scenario, init_scenario_state
)


def render_scenario_selector():
    """Renderiza seletor de cenário na sidebar com expander"""
    # Only initialize scenario state if not already initialized
    # This prevents unnecessary state operations on every render
    if 'biogas_scenario' not in st.session_state:
        init_scenario_state()

    current = get_current_scenario()
    current_config = SCENARIOS[current]

    # USAR EXPANDER para organizar na sidebar (collapsed by default to prevent rerun)
    with st.sidebar.expander("🎯 Cenário de Disponibilidade", expanded=False):

        st.caption(
            "Selecione o percentual de resíduos disponíveis para geração de biogás:"
        )

        # Radio buttons para seleção
        options = list(SCENARIOS.keys())
        labels = [
            f"{SCENARIOS[opt].icon} **{SCENARIOS[opt].name}** ({SCENARIOS[opt].factor*100:.0f}%)"
            for opt in options
        ]

        selected_index = st.radio(
            "Escolha o cenário:",
            range(len(options)),
            format_func=lambda i: labels[i],
            index=options.index(current),
            key='scenario_selector_radio',
            label_visibility="collapsed"
        )

        selected = options[selected_index]

        # Atualizar se mudou
        if selected != current:
            set_scenario(selected)
            st.rerun()

        # Info box com descrição
        selected_config = SCENARIOS[selected]
        st.info(
            f"**{selected_config.description}**\n\n"
            f"Os valores exibidos representam **{selected_config.factor*100:.1f}%** "
            f"do potencial teórico máximo."
        )

        # Badge visual do cenário ativo
        st.markdown(
            f"""
            <div style='background: linear-gradient(90deg, {selected_config.color} 0%, {selected_config.color}dd 100%);
                        padding: 0.75rem; border-radius: 8px; color: white; text-align: center;
                        margin-top: 0.5rem; font-weight: bold; font-family: "Montserrat", sans-serif;'>
                {selected_config.icon} Ativo: {selected_config.name}
            </div>
            """,
            unsafe_allow_html=True
        )


def render_scenario_badge():
    """Renderiza badge compacto mostrando cenário atual (para usar em páginas)"""
    config = SCENARIOS[get_current_scenario()]

    st.markdown(
        f"""
        <div style='background-color: {config.color}; padding: 0.5rem 1rem;
                    border-radius: 20px; display: inline-block; color: white;
                    font-weight: bold; font-size: 0.9em; font-family: "Montserrat", sans-serif;'>
            {config.icon} Cenário: {config.name} ({config.factor*100:.1f}%)
        </div>
        """,
        unsafe_allow_html=True
    )
