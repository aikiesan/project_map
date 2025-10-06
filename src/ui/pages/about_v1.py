"""
CP2B Maps - Modern About Page
Professional design with indigo gradient banner matching other pages
"""

import streamlit as st
from src.data.references.scientific_references import render_reference_button
from src.ui.components.substrate_info import render_substrate_information
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def render_about_v1_page():
    """Render modern About page with indigo gradient header"""

    # Modern indigo gradient header (institutional/professional theme)
    _render_modern_header()

    # Quick about stats
    _render_stats_banner()

    # Main content sections
    col1, col2 = st.columns([2, 1])

    with col1:
        # Mission, Vision, Values
        _render_institutional_context()

        # Methodology
        _render_methodology_section()

        # Features
        _render_features_section()

    with col2:
        # Quick stats sidebar
        _render_sidebar_info()

        # Application guide
        _render_quick_guide()

    # Strategic alignment
    st.markdown("---")
    _render_strategic_alignment()

    # Footer
    _render_footer()


def _render_modern_header() -> None:
    """Render modern indigo gradient header (institutional/professional theme)"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4f46e5 0%, #4338ca 50%, #3730a3 100%);
                color: white; padding: 2.5rem; margin: -1rem -1rem 2rem -1rem;
                text-align: center; border-radius: 0 0 25px 25px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
        <h1 style='margin: 0; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.5px;'>
            ℹ️ Sobre o CP2B Maps
        </h1>
        <p style='margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 300;'>
            Centro Paulista de Estudos em Biogás e Bioprodutos
        </p>
        <div style='margin-top: 15px; font-size: 0.95rem; opacity: 0.85;'>
            🎓 FAPESP 2024/01112-1 • 🔬 Pesquisa & Inovação • 🌱 Sustentabilidade
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_stats_banner() -> None:
    """Render key statistics banner"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(79,70,229,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>🗺️</div>
            <div style='color: #4f46e5; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>645</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Municípios</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(79,70,229,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>📊</div>
            <div style='color: #4f46e5; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>15+</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Substratos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(79,70,229,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>🔬</div>
            <div style='color: #4f46e5; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>50+</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Referências</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.2rem;
                    box-shadow: 0 2px 8px rgba(79,70,229,0.15); border: 1px solid #e5e7eb;
                    text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 0.3rem;'>⚡</div>
            <div style='color: #4f46e5; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.2rem;'>100%</div>
            <div style='color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>Open Source</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def _render_institutional_context():
    """Render institutional context section"""
    st.markdown("### 🏛️ Contexto Institucional")

    # Mission
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                border-left: 4px solid #8b5cf6;'>
        <h4 style='margin: 0 0 0.8rem 0; color: #5b21b6;'>🎯 Missão</h4>
        <p style='margin: 0; color: #6b21a8; line-height: 1.6;'>
            Desenvolver pesquisas, tecnologias e soluções inovadoras de biogás com motivação
            industrial, ambiental e social, promovendo o aproveitamento inteligente de resíduos
            para o desenvolvimento sustentável.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Vision
    st.markdown("""
    <div style='background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                border-left: 4px solid #3b82f6;'>
        <h4 style='margin: 0 0 0.8rem 0; color: #1e40af;'>🔮 Visão</h4>
        <p style='margin: 0; color: #1e3a8a; line-height: 1.6;'>
            Ser referência nacional e internacional na gestão eficiente e sustentável de resíduos
            urbanos e agropecuários, transformando o estado de São Paulo em vitrine de soluções
            inteligentes em biogás.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Values
    st.markdown("""
    <div style='background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
                border-left: 4px solid #10b981;'>
        <h4 style='margin: 0 0 0.8rem 0; color: #065f46;'>⚖️ Valores</h4>
        <ul style='margin: 0; padding-left: 1.5rem; color: #047857; line-height: 1.8;'>
            <li>Abordagem transdisciplinar para soluções inovadoras</li>
            <li>Bioeconomia circular e valorização de resíduos</li>
            <li>Compromisso com a agenda de descarbonização até 2050</li>
            <li>Educação como instrumento de transformação social</li>
            <li>Desenvolvimento de projetos com abordagem local e replicação</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def _render_methodology_section():
    """Render methodology overview"""
    st.markdown("### ⚙️ Metodologia de Cálculo")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                border-left: 4px solid #f59e0b;'>
        <h4 style='margin: 0 0 0.8rem 0; color: #92400e;'>📐 Padrões Internacionais</h4>
        <p style='margin: 0; color: #78350f; line-height: 1.6;'>
            Os cálculos seguem metodologias internacionalmente reconhecidas:
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Methodology steps
    steps = [
        ("📊", "Produção de Resíduos", "Dados oficiais do IBGE (agricultura, pecuária, urbano)"),
        ("🔬", "Fatores de Conversão", "Literatura científica revisada por pares"),
        ("⚗️", "Potencial de Metano", "m³ CH₄/ton resíduo (base seca)"),
        ("⚡", "Energia Total", "Conversão para MWh/ano e equivalentes")
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


def _render_features_section():
    """Render application features"""
    st.markdown("### 🛠️ Funcionalidades do Aplicativo")

    features = [
        ("🗺️", "Mapas Interativos", "Visualização geoespacial com Folium e filtros dinâmicos"),
        ("📊", "Análises Estatísticas", "Correlações, comparações e rankings municipais"),
        ("🎯", "Análise de Proximidade", "Identificação de oportunidades regionais"),
        ("📈", "Dados Exportáveis", "CSV, relatórios e dados filtrados"),
        ("🔬", "Base Científica", "Todas as metodologias com referências acadêmicas"),
        ("♿", "Acessibilidade", "WCAG 2.1 Nível A para inclusão digital")
    ]

    for icon, title, description in features:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem;
                    border-left: 4px solid #4f46e5; box-shadow: 0 1px 4px rgba(0,0,0,0.06);'>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <div style='font-size: 1.8rem;'>{icon}</div>
                <div style='flex: 1;'>
                    <div style='font-weight: 600; color: #1e293b; margin-bottom: 0.2rem;'>{title}</div>
                    <div style='color: #64748b; font-size: 0.9rem;'>{description}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_sidebar_info():
    """Render sidebar with quick info"""
    st.markdown("### 📋 Informações Rápidas")

    st.markdown("""
    <div style='background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
                border: 2px solid #ef4444;'>
        <h5 style='margin: 0 0 0.5rem 0; color: #991b1b;'>🎓 Financiamento</h5>
        <p style='margin: 0; color: #7f1d1d; font-size: 0.95rem;'>
            <strong>FAPESP</strong><br>
            Processo: 2024/01112-1
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
                border: 2px solid #0ea5e9;'>
        <h5 style='margin: 0 0 0.5rem 0; color: #075985;'>📍 Abrangência</h5>
        <p style='margin: 0; color: #0c4a6e; font-size: 0.95rem;'>
            <strong>Estado de São Paulo</strong><br>
            645 municípios mapeados
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
                border: 2px solid #22c55e;'>
        <h5 style='margin: 0 0 0.5rem 0; color: #14532d;'>🔬 Tecnologia</h5>
        <p style='margin: 0; color: #15803d; font-size: 0.95rem;'>
            Python • Streamlit<br>
            GeoPandas • Plotly • Folium
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_quick_guide():
    """Render quick navigation guide"""
    st.markdown("### 📖 Guia Rápido")

    guide = [
        ("🏠", "Mapa Principal", "Visualize potencial por município"),
        ("🔍", "Explorar Dados", "Análise detalhada com gráficos"),
        ("📊", "Análises Avançadas", "Comparações e sazonalidade"),
        ("🎯", "Proximidade", "Análise espacial por raio"),
        ("📚", "Referências", "Base científica completa")
    ]

    for icon, title, description in guide:
        st.markdown(f"""
        <div style='background: white; border-radius: 8px; padding: 0.8rem;
                    margin-bottom: 0.6rem; border: 1px solid #e5e7eb;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
            <div style='display: flex; align-items: center; gap: 0.8rem;'>
                <div style='font-size: 1.5rem;'>{icon}</div>
                <div>
                    <div style='font-weight: 600; color: #111827; font-size: 0.9rem;'>{title}</div>
                    <div style='color: #6b7280; font-size: 0.8rem;'>{description}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_strategic_alignment():
    """Render strategic alignment section"""
    st.markdown("### 🎯 Alinhamento Estratégico")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    border-radius: 12px; padding: 1.5rem; height: 100%;
                    border-left: 4px solid #f59e0b;'>
            <h4 style='margin: 0 0 1rem 0; color: #92400e;'>🔬 Eixo Tecnologias</h4>
            <ul style='margin: 0; padding-left: 1.5rem; color: #78350f; line-height: 1.8;'>
                <li>Desenvolvimento de software</li>
                <li>Ferramentas de apoio à decisão</li>
                <li>Transferência de tecnologia</li>
                <li>Capacitação em análise geoespacial</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    border-radius: 12px; padding: 1.5rem; height: 100%;
                    border-left: 4px solid #3b82f6;'>
            <h4 style='margin: 0 0 1rem 0; color: #1e40af;'>🏛️ Eixo Gestão</h4>
            <ul style='margin: 0; padding-left: 1.5rem; color: #1e3a8a; line-height: 1.8;'>
                <li>Políticas públicas baseadas em dados</li>
                <li>Priorização de investimentos</li>
                <li>Identificação de oportunidades PPP</li>
                <li>Gestão municipal de resíduos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def _render_footer():
    """Render footer with branding"""
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    color: white; border-radius: 12px; padding: 1.5rem; text-align: center;'>
            <h3 style='margin: 0 0 0.5rem 0; color: white;'>Centro Paulista de Estudos em Biogás e Bioprodutos</h3>
            <p style='margin: 0; opacity: 0.9; font-size: 0.95rem;'>
                Financiamento: <strong>FAPESP - Processo 2024/01112-1</strong>
            </p>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.8; font-size: 0.85rem;'>
                🌐 Open Source • 📚 Baseado em Ciência • ♿ Acessível
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        try:
            st.image("logotipo-full-black.png", width=250)
        except:
            logger.warning("Logo not found")
            st.markdown("""
            <div style='background: #f8fafc; border-radius: 12px; padding: 2rem;
                        text-align: center; border: 2px solid #e2e8f0;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🗺️</div>
                <div style='font-weight: 700; color: #1e293b;'>CP2B MAPS</div>
            </div>
            """, unsafe_allow_html=True)
