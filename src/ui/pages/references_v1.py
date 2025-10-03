"""
CP2B Maps V2 - Modern Scientific References Page
Professional design with teal gradient banner matching other pages
"""

import streamlit as st
from src.data.references.scientific_references import render_reference_button
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_references_v1_page():
    """Render modern references page with teal gradient header"""

    # Modern teal gradient header (scientific/academic theme)
    _render_modern_header()

    # Quick stats banner
    _render_stats_banner()

    # Category tabs with modern styling (5 tabs only)
    ref_tabs = st.tabs([
        "🌾 Substratos Agrícolas",
        "🐄 Resíduos Pecuários",
        "⚗️ Co-digestão",
        "🗺️ Fontes de Dados",
        "🔬 Metodologias"
    ])

    with ref_tabs[0]:  # Agricultural
        st.markdown("Pesquisas sobre potencial de biogás de resíduos de culturas agrícolas")
        st.markdown("")
        _render_category_refs("agricultural")

    with ref_tabs[1]:  # Livestock
        st.markdown("Estudos sobre dejetos animais e produção de metano")
        st.markdown("")
        _render_category_refs("livestock")

    with ref_tabs[2]:  # Co-digestion
        st.markdown("Pesquisas sobre misturas de substratos e otimização de processos")
        st.markdown("")
        _render_category_refs("codigestion")

    with ref_tabs[3]:  # Data Sources
        st.markdown("Bases de dados oficiais e institucionais utilizadas")
        st.markdown("")
        _render_data_sources()

    with ref_tabs[4]:  # Methodologies
        st.markdown("Métodos de cálculo e normas técnicas aplicadas")
        st.markdown("")
        _render_methodologies()

    # Search section
    st.markdown("---")
    _render_search_section()


def _render_modern_header() -> None:
    """Render modern teal gradient header (academic/scientific theme)"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%);
                color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                text-align: center; border-radius: 0 0 25px 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
        <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
            📚 Referências Científicas
        </h1>
        <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
            Base acadêmica e metodológica do CP2B Maps
        </p>
        <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.85;'>
            🔬 Pesquisas Revisadas • 📊 Metodologias Validadas • 🌍 Fontes Oficiais
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_stats_banner() -> None:
    """Render floating stats banner"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>📖</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>50+</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Referências</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>🏷️</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>5</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Categorias</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>🗺️</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>4</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Fontes de Dados</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(20,184,166,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>✅</div>
            <div style='color: #14b8a6; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>100%</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Peer-Reviewed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def _render_category_refs(category: str):
    """Render references by category with modern integrated card design"""
    refs = {
        "agricultural": [
            ("Bagaço de Cana-de-açúcar", "sugarcane_bagasse", "Resíduo da produção de etanol e açúcar"),
            ("Palha de Soja", "soybean_straw", "Resíduo de colheita de soja"),
            ("Resíduos de Milho", "corn_straw", "Palha e sabugo de milho"),
            ("Casca de Café", "coffee_husk", "Resíduo do beneficiamento de café"),
            ("Bagaço de Citros", "citrus_bagasse", "Resíduo da indústria de suco"),
        ],
        "livestock": [
            ("Dejetos Bovinos", "biogas_calculation", "Esterco de gado de corte e leiteiro"),
            ("Dejetos Suínos", "biogas_calculation", "Dejetos de suinocultura"),
            ("Cama de Frango", "biogas_calculation", "Resíduo de avicultura"),
        ],
        "codigestion": [
            ("Co-digestão Geral", "biogas_calculation", "Misturas otimizadas de substratos"),
        ]
    }

    for title, ref_id, description in refs.get(category, []):
        # Create container with flex layout
        col_text, col_button = st.columns([4, 1])

        with col_text:
            st.markdown(f"""
            <div style='background: white; border-radius: 10px; padding: 1.2rem 1.5rem;
                        margin-bottom: 1rem; border-left: 4px solid #14b8a6;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.08);'>
                <h4 style='margin: 0 0 0.3rem 0; color: #111827; font-size: 1.1rem;'>{title}</h4>
                <p style='margin: 0; color: #6b7280; font-size: 0.9rem;'>{description}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_button:
            st.markdown("<div style='padding-top: 1.5rem;'>", unsafe_allow_html=True)
            render_reference_button(ref_id, compact=True)
            st.markdown("</div>", unsafe_allow_html=True)


def _render_data_sources():
    """Render data sources with card design"""
    sources = [
        ("IBGE", "Instituto Brasileiro de Geografia e Estatística", "Dados de produção agrícola e pecuária", "🗺️"),
        ("MapBiomas", "Projeto MapBiomas Coleção 9", "Uso e cobertura do solo", "🛰️"),
        ("CETESB", "Companhia Ambiental do Estado de São Paulo", "Dados ambientais e regulatórios", "🌿"),
        ("EPE", "Empresa de Pesquisa Energética", "Dados energéticos nacionais", "⚡")
    ]

    for name, full_name, description, icon in sources:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                    border: 2px solid #14b8a6; box-shadow: 0 2px 8px rgba(20,184,166,0.1);'>
            <div style='display: flex; align-items: start; gap: 1rem;'>
                <div style='font-size: 2.5rem;'>{icon}</div>
                <div style='flex: 1;'>
                    <h4 style='margin: 0 0 0.3rem 0; color: #0f766e; font-size: 1.2rem;'>{name}</h4>
                    <p style='margin: 0 0 0.5rem 0; color: #115e59; font-weight: 500;'>{full_name}</p>
                    <p style='margin: 0; color: #14532d; font-size: 0.9rem;'>{description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_methodologies():
    """Render methodologies with visual flow"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
                border-left: 4px solid #06b6d4;'>
        <h4 style='margin: 0 0 1rem 0; color: #164e63;'>📐 Cálculo de Potencial de Biogás</h4>
        <p style='color: #155e75; margin-bottom: 1rem;'>
            A metodologia segue padrões internacionais de digestão anaeróbia:
        </p>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("1️⃣", "Produção de Resíduos", "Dados do IBGE (agricultura, pecuária, urbano)"),
        ("2️⃣", "Fatores de Conversão", "Literatura científica revisada por pares"),
        ("3️⃣", "Potencial de Metano", "m³ CH₄/ton resíduo (base seca)"),
        ("4️⃣", "Biogás Total", "Conversão de CH₄ para biogás (60-70% CH₄)")
    ]

    for icon, title, description in steps:
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 1rem 1.2rem;
                    margin-bottom: 0.8rem; display: flex; align-items: center; gap: 1rem;
                    border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
            <div style='font-size: 1.8rem;'>{icon}</div>
            <div style='flex: 1;'>
                <div style='font-weight: 600; color: #111827; margin-bottom: 0.2rem;'>{title}</div>
                <div style='color: #6b7280; font-size: 0.9rem;'>{description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background: #fef3c7; border-radius: 10px; padding: 1.2rem;
                border-left: 4px solid #f59e0b;'>
        <h5 style='margin: 0 0 0.8rem 0; color: #92400e;'>📚 Referências Metodológicas:</h5>
        <ul style='margin: 0; padding-left: 1.5rem; color: #78350f;'>
            <li><strong>VDI 4630</strong> - Digestão Anaeróbia (Alemanha)</li>
            <li><strong>ISO/DIS 11734</strong> - Potencial BMP</li>
            <li><strong>ABNT NBR 15849</strong> - Resíduos sólidos urbanos</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_search_section():
    """Render search section with modern styling"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                border-left: 4px solid #eab308;'>
        <h4 style='margin: 0 0 0.5rem 0; color: #854d0e;'>🔍 Buscar Referências</h4>
        <p style='margin: 0; color: #a16207; font-size: 0.95rem;'>
            Digite palavras-chave para encontrar referências específicas
        </p>
    </div>
    """, unsafe_allow_html=True)

    search_query = st.text_input(
        "Palavras-chave:",
        placeholder="Ex: cana-de-açúcar, metano, digestão anaeróbia, VDI 4630...",
        label_visibility="collapsed"
    )

    if search_query:
        _render_search_results(search_query)


def _render_search_results(query: str):
    """Render search results"""
    st.markdown(f"""
    <div style='background: #dbeafe; border-radius: 8px; padding: 1rem;
                border-left: 4px solid #3b82f6; margin-top: 1rem;'>
        <div style='color: #1e40af; font-weight: 600;'>
            🔎 Buscando por: <strong>"{query}"</strong>
        </div>
        <div style='color: #1e3a8a; margin-top: 0.5rem; font-size: 0.9rem;'>
            Funcionalidade de busca em desenvolvimento. Em breve você poderá buscar em todas as referências.
        </div>
    </div>
    """, unsafe_allow_html=True)
