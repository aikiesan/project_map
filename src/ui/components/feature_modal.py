"""
CP2B Maps - Feature Modal Component
Comprehensive modal dialogs for detailed tool information
Uses Streamlit's @st.dialog decorator for native modal support
"""

import streamlit as st
from typing import Dict, List
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


# Comprehensive tool details database
TOOL_DETAILS = {
    "mapa_principal": {
        "icon": "🗺️",
        "title": "Mapa Principal",
        "description": "Explore o potencial de biogás dos 645 municípios paulistas através de mapas interativos profissionais, com múltiplas camadas GIS e opções de visualização personalizáveis para análises geoespaciais completas.",
        "recursos": [
            "🗺️ Mapas interativos com zoom, pan e seleção de municípios",
            "🎨 Três tipos de visualização: coroplético, círculos proporcionais e heatmap",
            "📍 15+ camadas GIS: gasodutos, usinas, áreas urbanas, rodovias, ETEs",
            "🔢 Dados completos de 645 municípios paulistas",
            "💾 Exportação de mapas em formato HTML para relatórios",
            "📊 Pop-ups informativos ao clicar em municípios",
            "🎛️ Controles de opacidade e visibilidade de camadas"
        ],
        "tutorial": [
            "Acesse a aba **'🗺️ Mapa Principal'** na navegação superior",
            "Na barra lateral, selecione o **tipo de resíduo** (total, cana, soja, bovinos, etc.)",
            "Escolha o **tipo de mapa**: coroplético (cores), círculos (tamanho proporcional) ou heatmap (densidade)",
            "Ative **camadas GIS** adicionais: gasodutos, usinas de biogás, linhas de transmissão, etc.",
            "Clique em qualquer município no mapa para ver **detalhes em popup**",
            "Use os controles de **zoom (+/-)** ou **arraste o mapa** para explorar regiões específicas",
            "Exporte o mapa clicando em **'Exportar Mapa'** na barra lateral"
        ],
        "casos_uso": [
            {
                "titulo": "🎯 Identificar regiões com alto potencial de biogás",
                "descricao": "Use o mapa **coroplético** com escala de cores para visualizar rapidamente quais regiões do estado têm maior concentração de potencial energético. Ideal para análises preliminares e apresentações executivas."
            },
            {
                "titulo": "📍 Planejar localização estratégica de planta de biogás",
                "descricao": "Ative as camadas de **gasodutos** e **linhas de transmissão** para identificar municípios com alto potencial E infraestrutura próxima. Isso reduz custos de escoamento do biogás e conexão à rede elétrica."
            },
            {
                "titulo": "🔍 Análise regional para captação de resíduos",
                "descricao": "Use o mapa de **círculos proporcionais** para visualizar o potencial relativo entre municípios próximos. Combine com a camada de **rodovias** para planejar rotas logísticas de coleta de resíduos."
            }
        ],
        "saidas": "**Mapa interativo** com círculos coloridos representando municípios, **legendas** dinâmicas com escala de valores, **popups informativos** ao clicar (nome, população, potencial de biogás), **camadas GIS sobrepostas** (gasodutos, usinas, etc.), e opção de **exportação em HTML** para incorporar em relatórios.",
        "dicas": [
            "💡 Use o **zoom (+/-)** para explorar municípios específicos - o mapa suporta até nível de rua",
            "🔗 **Combine múltiplas camadas GIS** (ex: gasodutos + usinas existentes) para análise integrada de viabilidade",
            "📄 **Exporte o mapa em HTML** para incluir em relatórios interativos - o arquivo mantém todas as funcionalidades",
            "🎨 Experimente os **três tipos de mapas** para diferentes insights: coroplético para visão geral, círculos para comparação, heatmap para densidade",
            "🔍 Use os **filtros de potencial** (mínimo/máximo) para focar em municípios de tamanho específico"
        ]
    },

    "explorar_dados": {
        "icon": "🔍",
        "title": "Explorar Dados",
        "description": "Realize análises estatísticas avançadas com gráficos interativos Plotly, rankings dinâmicos, comparações entre municípios e exportação de dados para pesquisas quantitativas aprofundadas.",
        "recursos": [
            "📊 Gráficos interativos Plotly: scatter, box plot, histogram, pie chart",
            "🏆 Rankings dinâmicos: top municípios por potencial de biogás/energia/CO₂",
            "📈 Estatísticas descritivas completas: média, mediana, desvio padrão, quartis",
            "⚖️ Comparação lado a lado de múltiplos municípios",
            "📥 Exportação de dados em CSV e Excel para análises externas",
            "🔢 Tabelas interativas com ordenação e busca",
            "📉 Visualizações de distribuição e outliers"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "Na seção **Filtros**, selecione municípios específicos ou regiões de interesse",
            "Escolha o **tipo de gráfico**: scatter (correlação), box plot (distribuição), histogram (frequência) ou pie (composição)",
            "Selecione as **variáveis de interesse** para análise: biogas_total, energia, CO₂, ou por substrato específico",
            "Explore os **rankings dinâmicos** para ver os top 10, 20 ou 50 municípios",
            "Visualize as **estatísticas descritivas** (média, mediana, min, max, desvio padrão)",
            "**Exporte os dados** clicando no botão de download (CSV ou Excel) para análises em ferramentas externas"
        ],
        "casos_uso": [
            {
                "titulo": "📊 Análise estatística para pesquisa acadêmica",
                "descricao": "Use as **estatísticas descritivas** e **visualizações de distribuição** (box plot, histogram) para caracterizar o potencial de biogás no estado. Exporte os dados em CSV para análises avançadas em R, Python ou SPSS."
            },
            {
                "titulo": "🏆 Identificar municípios prioritários para investimento",
                "descricao": "Consulte o **ranking de municípios** filtrando por potencial energético + proximidade a infraestrutura. Compare os top 20 municípios usando **gráficos comparativos** para decisões de investimento."
            },
            {
                "titulo": "⚖️ Comparar desempenho entre regiões administrativas",
                "descricao": "Selecione municípios de diferentes **regiões administrativas** (Metropolitana SP, Campinas, Ribeirão Preto, etc.) e compare usando **análises lado a lado** para identificar padrões regionais."
            }
        ],
        "saidas": "**Gráficos interativos Plotly** com zoom, pan e hover tooltips; **tabelas de rankings** ordenáveis; **painéis de estatísticas** (cards com média, mediana, soma); **arquivos CSV/Excel** para download; **comparações visuais** side-by-side de municípios selecionados.",
        "dicas": [
            "📊 **Gráficos de dispersão (scatter)** são ideais para identificar correlações entre variáveis (ex: população vs. potencial)",
            "📦 **Box plots** revelam outliers e distribuições - use para identificar municípios atípicos",
            "🔢 Sempre verifique as **estatísticas numéricas** antes de interpretar gráficos para contexto numérico",
            "📥 **Exporte os dados** antes de mudanças de filtro para manter subconjuntos específicos",
            "🏆 Use rankings com **diferentes métricas** (m³/ano, MWh/ano, tonCO₂/ano) para diferentes perspectivas"
        ]
    },

    "analises_avancadas": {
        "icon": "📊",
        "title": "Análises Avançadas",
        "description": "Analise em profundidade a composição de resíduos por tipo de substrato (9 categorias) e distribuição geográfica, identificando fontes prioritárias e padrões de especialização regional.",
        "recursos": [
            "🌾 Análise por tipo de resíduo: 9 substratos (cana, soja, milho, café, citros, bovinos, suínos, aves, piscicultura)",
            "🗺️ Análise por região geográfica: regiões intermediárias e imediatas",
            "📊 Gráficos de composição: pizza, barras empilhadas, treemap",
            "📈 Gráficos de distribuição espacial por substrato",
            "🔍 Identificação de principais contribuidores por região",
            "📉 Análise de concentração e diversificação regional",
            "🎯 Detecção de especializações agrícolas/pecuárias por município"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "Na seção **Análise por Substrato**, selecione um substrato específico (ex: cana-de-açúcar)",
            "Visualize a **composição percentual** dos diferentes substratos no gráfico de pizza",
            "Na seção **Análise por Região**, selecione uma região geográfica (ex: Região Metropolitana de SP)",
            "Compare a **distribuição de substratos** naquela região usando gráficos de barras",
            "Identifique municípios com **alta especialização** em substratos específicos",
            "Use os **filtros combinados** para análises cruzadas (ex: suínos na Região de Ribeirão Preto)"
        ],
        "casos_uso": [
            {
                "titulo": "🌾 Priorização de substratos para projeto de biogás",
                "descricao": "Analise a **composição de substratos** em sua região alvo para decidir quais tipos de resíduos focar na captação. Por exemplo, se cana representa 70% do potencial, priorize parcerias com usinas sucroalcooleiras."
            },
            {
                "titulo": "🗺️ Identificar especializações regionais",
                "descricao": "Use a análise **por região geográfica** para identificar clusters especializados: regiões com alta concentração de suínos (oeste paulista), café (nordeste), ou cana (centro-norte). Isso orienta estratégias regionais específicas."
            },
            {
                "titulo": "📊 Planejar mix de substratos para co-digestão",
                "descricao": "Identifique municípios com **múltiplos substratos disponíveis** usando gráficos de composição. Co-digestão (mistura de resíduos) aumenta eficiência - municípios com cana+bovinos+aves são ideais."
            }
        ],
        "saidas": "**Gráficos de pizza** mostrando composição percentual por substrato; **gráficos de barras empilhadas** com contribuição regional; **mapas coropléticos** por substrato específico; **tabelas de ranking** por tipo de resíduo; **análises de concentração** (índice Herfindahl) mostrando diversificação ou especialização.",
        "dicas": [
            "🌾 Substratos agrícolas (cana, soja) geralmente dominam em volume, mas resíduos animais têm maior produtividade específica",
            "🔄 Use análises de **composição percentual** junto com **mapas coropléticos** para entender distribuição espacial de cada substrato",
            "🎯 Municípios com **alta especialização** (>80% um substrato) podem ter maior facilidade de captação",
            "📊 Compare **diferentes cenários** (Pessimista vs. Otimista) para ver como disponibilidade afeta composição",
            "🗺️ Regiões com **diversidade** de substratos são mais resilientes a variações sazonais"
        ]
    },

    "proximidade": {
        "icon": "🎯",
        "title": "Análise de Proximidade",
        "description": "Realize análises espaciais avançadas com raio customizável para agregação regional de potencial energético, integradas com dados de uso e cobertura do solo MapBiomas para planejamento territorial estratégico.",
        "recursos": [
            "🎯 Análise por raio personalizável (1 a 500 km)",
            "📍 Seleção de município de referência como ponto central",
            "🌍 Integração com MapBiomas: 27 classes de uso e cobertura do solo",
            "📊 Estatísticas agregadas da área de influência (soma, média, mediana)",
            "🗺️ Visualização de círculo de análise no mapa interativo",
            "📈 Gráficos de distribuição de municípios por distância",
            "🌱 Correlação entre uso do solo e potencial de biogás"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "Selecione um **município de referência** (ex: onde você planeja construir uma planta de biogás)",
            "Defina o **raio de análise** em km (ex: 50 km para viabilidade logística)",
            "Visualize os **municípios próximos** no mapa com círculo de influência",
            "Consulte as **estatísticas agregadas**: potencial total, médio, mediana da área",
            "**Opcional**: Ative a **análise MapBiomas** para ver uso do solo na área circular",
            "Analise a **distribuição de classes de uso do solo**: pastagens, agricultura, florestas, áreas urbanas",
            "**Exporte os resultados** (lista de municípios, estatísticas, gráficos)"
        ],
        "casos_uso": [
            {
                "titulo": "📍 Planejamento logístico de coleta de resíduos",
                "descricao": "Defina um **raio de 20-50 km** a partir do local planejado da planta para identificar municípios fornecedores viáveis. Avalie o potencial total captável considerando custos de transporte (regra geral: <50km é econômico para resíduos sólidos)."
            },
            {
                "titulo": "🗺️ Avaliação de disponibilidade de terras",
                "descricao": "Use a **análise MapBiomas** para verificar uso do solo na área de influência. Identifique áreas de **pastagens** ou **agricultura** que podem fornecer resíduos. Verifique proximidade de **infraestrutura elétrica** para escoamento de energia."
            },
            {
                "titulo": "🎯 Identificação de clusters regionais",
                "descricao": "Teste múltiplos municípios de referência para encontrar **clusters regionais de alto potencial**. Regiões com vários municípios próximos de alto potencial são ideais para **plantas centralizadas** que atendem múltiplas cidades."
            }
        ],
        "saidas": "**Mapa interativo** com círculo de análise e municípios destacados; **lista de municípios** na área com distâncias; **estatísticas agregadas** (soma, média, mediana, desvio padrão); **gráficos de distribuição** por distância; **análise de uso do solo MapBiomas** (27 classes, áreas em hectares, percentuais); **tabela exportável** com todos os dados.",
        "dicas": [
            "🚚 Para planejamento logístico, use **raios de 20-30 km** (viabilidade econômica para transporte diário)",
            "🌍 Para análise regional estratégica, use **raios maiores (50-100 km)** (visão de cluster)",
            "🗺️ Ative **camada de rodovias** no mapa para avaliar acessibilidade dos municípios identificados",
            "🌱 Use **dados MapBiomas** para correlacionar uso do solo com tipo de resíduo (pastagens → bovinos, agricultura → resíduos vegetais)",
            "📊 Compare **diferentes raios de análise** alterando o raio para entender sensibilidade geográfica",
            "🔄 Municípios com **distância < 30 km** geralmente são viáveis para coleta diária sem custos proibitivos"
        ]
    },

    "bagacinho_ia": {
        "icon": "🍊",
        "title": "Bagacinho IA",
        "description": "Converse com nosso assistente inteligente baseado em Google Gemini 2.5 Flash e RAG. Faça perguntas em linguagem natural sobre os dados dos 645 municípios e receba respostas fundamentadas em referências científicas.",
        "recursos": [
            "🤖 Assistente IA baseado em Google Gemini 2.5 Flash",
            "💬 Consultas em linguagem natural (pergunte em português como conversaria)",
            "📊 Acesso direto aos dados via RAG (Retrieval-Augmented Generation)",
            "📚 Respostas baseadas em referências científicas com citações",
            "🧠 Contextualização inteligente e comparações automáticas",
            "🔍 Busca fuzzy de municípios (funciona mesmo com erros de digitação)",
            "📈 Cálculos on-demand e estatísticas comparativas"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "Digite sua pergunta na **caixa de texto** (ex: 'Qual município tem maior potencial de biogás?')",
            "Pressione **Enter** ou clique em **Enviar** para processar",
            "Aguarde a **resposta da IA** (geralmente 2-5 segundos)",
            "Leia a resposta que inclui **dados numéricos** e **análises contextuais**",
            "Faça **perguntas de acompanhamento** para aprofundar (ex: 'Compare os top 5')",
            "Use o **histórico de conversa** para referência - ele lembra o contexto"
        ],
        "casos_uso": [
            {
                "titulo": "🔍 Consulta rápida de dados específicos",
                "descricao": "Pergunte diretamente: 'Qual o potencial de biogás de Campinas?' ou 'Quantos MWh/ano São Paulo pode gerar?'. Muito mais rápido que navegar tabelas ou filtrar dados manualmente."
            },
            {
                "titulo": "⚖️ Comparações entre municípios ou regiões",
                "descricao": "Pergunte: 'Compare o potencial de Ribeirão Preto e Campinas' ou 'Quais municípios têm mais potencial de suínos?'. O Bagacinho faz comparações automáticas e destaca diferenças."
            },
            {
                "titulo": "❓ Perguntas metodológicas e sobre dados",
                "descricao": "Pergunte: 'Como é calculado o potencial de biogás?' ou 'Qual a diferença entre os cenários?'. O Bagacinho explica metodologia e cita as referências científicas."
            }
        ],
        "saidas": "**Respostas em linguagem natural** com dados numéricos formatados; **citações de municípios** com valores exatos (m³/ano, MWh/ano, tons CO₂/ano); **comparações tabulares** quando relevante; **explicações contextuais** sobre metodologia; **referências científicas** citadas quando apropriado.",
        "dicas": [
            "💬 **Seja específico nas perguntas**: 'Qual município tem mais biogás de cana?' é melhor que 'Fale sobre cana'",
            "🔢 Peça **rankings e comparações**: 'Top 5 municípios' gera ranking automático",
            "❓ Pergunte **'como' e 'por quê'** para entender metodologia e contexto",
            "🔄 Use **contexto de conversa**: 'E quanto a energia?' após uma pergunta sobre biogás",
            "📊 Peça **cálculos percentuais**: 'Quantos % do total é São Paulo?' - ele calcula na hora",
            "🎯 Funciona com **erros de digitação**: 'Campinas', 'Canpinas', 'kampinas' - tudo funciona!"
        ]
    },

    "referencias": {
        "icon": "📚",
        "title": "Referências Científicas",
        "description": "Acesse nosso banco de dados curado com mais de 20 referências científicas revisadas por pares. Todas as fontes estão organizadas por categoria, com citações formatadas em ABNT e links diretos para as publicações originais.",
        "recursos": [
            "📚 20+ referências científicas de periódicos revisados por pares",
            "🔍 Busca por palavra-chave em títulos e autores",
            "📑 Citações prontas em formato ABNT para trabalhos acadêmicos",
            "🏷️ Organização por categoria: substratos, co-digestão, fontes de dados, metodologia",
            "🔗 Links diretos para publicações originais (DOI, URL)",
            "📅 Filtros por ano de publicação",
            "📖 Resumos e informações sobre cada referência"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "**Navegue por categoria**: Substratos, Co-digestão, Fontes de Dados, Metodologia",
            "Ou use a **busca por palavra-chave** (ex: 'cana', 'metano', 'bovinos')",
            "Clique em uma referência para ver **detalhes completos**",
            "**Copie a citação ABNT** clicando no botão de cópia",
            "Acesse o **link original (DOI/URL)** para ler o artigo completo (quando disponível)",
            "Use os **filtros avançados** para refinar por ano ou tipo de publicação"
        ],
        "casos_uso": [
            {
                "titulo": "📝 Citações para trabalhos acadêmicos (TCC, dissertações, artigos)",
                "descricao": "Use as **citações ABNT prontas** para referências em trabalhos científicos. Todas as referências são de fontes confiáveis (periódicos revisados por pares, relatórios técnicos oficiais, dados governamentais)."
            },
            {
                "titulo": "🔬 Validação de metodologia e fatores de conversão",
                "descricao": "Consulte as referências da categoria **Metodologia** para entender as bases científicas dos cálculos usados na plataforma. Todas as taxas de conversão (resíduo → biogás → energia) vêm de fontes publicadas."
            },
            {
                "titulo": "🌾 Pesquisa sobre substratos específicos",
                "descricao": "Use a busca ou navegue pela categoria **Substratos** para encontrar estudos sobre resíduos específicos (cana, café, citros, bovinos, etc.). Ideal para aprofundar conhecimento sobre potencial de substratos regionais."
            }
        ],
        "saidas": "**Lista de referências** organizadas por categoria; **citações ABNT** formatadas e copiáveis; **links clicáveis** para publicações originais; **informações bibliográficas** completas (autores, ano, periódico, DOI); **tags e categorias** para filtragem; **contagem de referências** por categoria.",
        "dicas": [
            "📋 **Copie citações formatadas** com um clique - ideal para bibliografias de trabalhos",
            "🔗 Verifique **links DOI permanentes** para acesso garantido a artigos científicos (repositórios permanentes)",
            "📚 Referências sobre **co-digestão** são essenciais para projetos que misturam substratos",
            "🌾 Cada **tipo de substrato** (cana, soja, café, etc.) tem pelo menos 1 referência específica",
            "📊 Use referências de **Fontes de Dados** para citar IBGE, MapBiomas, SEADE nos seus trabalhos",
            "🔍 A **busca inteligente** funciona em títulos, autores e palavras-chave - experimente termos técnicos"
        ]
    },

    "sobre": {
        "icon": "ℹ️",
        "title": "Sobre o CP2B Maps",
        "description": "Conheça o CP2B Maps em detalhes: informações sobre o projeto, equipe de pesquisa, metodologia científica validada, financiamento FAPESP e canais para colaboração ou contato com nosso time.",
        "recursos": [
            "ℹ️ Informações detalhadas sobre o projeto CP2B Maps",
            "🎓 Equipe de pesquisa e instituições envolvidas",
            "🔬 Metodologia científica completa e validação",
            "📖 Guia de uso da plataforma para novos usuários",
            "🤝 Informações sobre colaborações e parcerias",
            "📧 Canais de contato e suporte",
            "🏆 Financiamento FAPESP e reconhecimentos"
        ],
        "tutorial": [
            "Acesse a aba **🔍 Explorar Dados**",
            "Leia a seção **Sobre o Projeto** para entender contexto e objetivos",
            "Consulte **Metodologia Científica** para detalhes sobre cálculos e fontes de dados",
            "Confira **Cenários de Disponibilidade** para entender Pessimista, Realista, Otimista e Utópico",
            "Veja **Equipe de Pesquisa** para conhecer os responsáveis pelo projeto",
            "Leia **Guia de Uso** para dicas de navegação e uso eficiente da plataforma",
            "Use **Canais de Contato** para colaborações, dúvidas ou reportar problemas"
        ],
        "casos_uso": [
            {
                "titulo": "🎓 Contextualização para trabalhos acadêmicos",
                "descricao": "Leia a seção **Sobre o Projeto e Metodologia** para entender o contexto, objetivos e base científica. Use essas informações para introdução e metodologia de TCCs, dissertações ou artigos que utilizem dados da plataforma."
            },
            {
                "titulo": "📊 Entender metodologia de cálculo",
                "descricao": "Consulte a seção **Metodologia de Cálculo** para compreender como são calculados potencial de biogás, energia e CO₂. Fundamental para interpretar corretamente os resultados e citar a plataforma apropriadamente."
            },
            {
                "titulo": "🤝 Solicitar colaboração ou acesso especial",
                "descricao": "Use as informações de **Contato e Colaboração** para propor parcerias de pesquisa, solicitar dados customizados ou discutir integração da plataforma em projetos institucionais."
            }
        ],
        "saidas": "**Informações textuais** sobre projeto, equipe e metodologia; **diagramas explicativos** sobre fluxo de dados e cálculos; **tabelas de cenários** com fatores de disponibilidade; **informações de contato** (e-mail, GitHub Issues); **citação sugerida** para a plataforma em trabalhos acadêmicos.",
        "dicas": [
            "📖 **Leia a página Sobre completa** se é sua primeira vez na plataforma - contextualiza todo o sistema",
            "🔬 A seção **Metodologia** é essencial para entender limitações e premissas dos dados",
            "📊 Sempre mencione o **cenário utilizado** ao citar dados (Pessimista/Realista/Otimista/Utópico)",
            "🤝 Para **colaborações acadêmicas** ou parcerias, entre em contato - o time está aberto a colaborações",
            "📚 Combine informações daqui com a aba **Referências Científicas** para citações completas",
            "💡 O projeto é **financiado pela FAPESP** - cite isso em agradecimentos se usar os dados"
        ]
    }
}


@st.dialog(" ", width="large")
def show_feature_modal(tool_key: str):
    """
    Display comprehensive feature information in a beautifully designed tabbed modal dialog

    Args:
        tool_key: Unique identifier for the tool (e.g., 'mapa_principal')
    """

    if tool_key not in TOOL_DETAILS:
        st.error(f"Ferramenta '{tool_key}' não encontrada.")
        return

    tool = TOOL_DETAILS[tool_key]

    # Enhanced modal header with refined typography and spacing
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 2.5rem; padding-bottom: 2rem;
                border-bottom: 1px solid #e9ecef;'>
        <div style='font-size: 4rem; margin-bottom: 1rem; line-height: 1;'>
            {tool['icon']}
        </div>
        <h1 style='color: #1a202c; margin: 0 0 1rem 0; font-weight: 600;
                   font-size: 2rem; letter-spacing: -0.02em;'>
            {tool['title']}
        </h1>
        <p style='color: #718096; font-size: 1.1rem; margin: 0; line-height: 1.7;
                  max-width: 700px; margin-left: auto; margin-right: auto;'>
            {tool['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create 4 tabs with better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Visão Geral", "📚 Tutorial", "💼 Exemplos", "💡 Dicas"])

    # TAB 1: Visão Geral (Overview)
    with tab1:
        # Main Resources in a refined card
        st.markdown("""
        <div style='background: #fafbfc; border-radius: 12px; padding: 2rem;
                    border-left: 3px solid #2E8B57; margin-bottom: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
            <h3 style='color: #1a202c; margin: 0 0 1.5rem 0; font-weight: 600;
                       font-size: 1.4rem; letter-spacing: -0.01em;'>
                🎯 Principais Recursos
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Render resources with refined styling
        for recurso in tool["recursos"]:
            st.markdown(f"""
            <div style='padding: 0.5rem 0; color: #2d3748; line-height: 1.8;'>
                {recurso}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)  # Spacing

        # Expected Outputs with refined design
        st.markdown("""
        <div style='background: #fafbfc; border-radius: 12px; padding: 2rem;
                    border-left: 3px solid #2E8B57; margin-bottom: 1.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
            <h3 style='color: #1a202c; margin: 0 0 1.5rem 0; font-weight: 600;
                       font-size: 1.4rem; letter-spacing: -0.01em;'>
                📊 O que Você Verá
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background: #f0f9ff; border-left: 3px solid #3b82f6;
                    padding: 1.5rem; border-radius: 8px; color: #1e40af;
                    line-height: 1.8; margin-bottom: 2rem;'>
            {tool["saidas"]}
        </div>
        """, unsafe_allow_html=True)

        # CTA with refined styling
        if st.button("🚀 Começar a Usar", key=f"cta_overview_{tool_key}", use_container_width=True):
            st.rerun()

    # TAB 2: Tutorial
    with tab2:
        st.markdown("""
        <div style='background: #fafbfc; border-radius: 12px; padding: 2rem;
                    border-left: 3px solid #2E8B57; margin-bottom: 2.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
            <h3 style='color: #1a202c; margin: 0 0 0.75rem 0; font-weight: 600;
                       font-size: 1.4rem; letter-spacing: -0.01em;'>
                📚 Tutorial Passo a Passo
            </h3>
            <p style='color: #718096; margin: 0; line-height: 1.7;'>
                Siga estas etapas para usar esta ferramenta com sucesso
            </p>
        </div>
        """, unsafe_allow_html=True)

        for i, step in enumerate(tool["tutorial"], 1):
            st.markdown(f"""
            <div style='background: white; border-left: 3px solid #2E8B57;
                        padding: 1.5rem; margin-bottom: 1.25rem; border-radius: 10px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
                        transition: transform 0.2s ease;'>
                <div style='color: #2E8B57; font-weight: 600; margin-bottom: 0.75rem;
                            font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase;'>
                    Passo {i}
                </div>
                <div style='color: #2d3748; line-height: 1.8; font-size: 1rem;'>
                    {step}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # CTA
        if st.button("🚀 Começar a Usar", key=f"cta_tutorial_{tool_key}", use_container_width=True):
            st.rerun()

    # TAB 3: Exemplos (Use Cases)
    with tab3:
        st.markdown("""
        <div style='background: #fafbfc; border-radius: 12px; padding: 2rem;
                    border-left: 3px solid #2E8B57; margin-bottom: 2.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
            <h3 style='color: #1a202c; margin: 0 0 0.75rem 0; font-weight: 600;
                       font-size: 1.4rem; letter-spacing: -0.01em;'>
                💼 Casos de Uso Práticos
            </h3>
            <p style='color: #718096; margin: 0; line-height: 1.7;'>
                Veja exemplos reais de como esta ferramenta pode ser aplicada
            </p>
        </div>
        """, unsafe_allow_html=True)

        for caso in tool["casos_uso"]:
            with st.expander(caso["titulo"], expanded=False):
                st.markdown(f"""
                <div style='color: #2d3748; line-height: 1.8; padding: 1rem 0; font-size: 1rem;'>
                    {caso['descricao']}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # CTA
        if st.button("🚀 Começar a Usar", key=f"cta_exemplos_{tool_key}", use_container_width=True):
            st.rerun()

    # TAB 4: Dicas (Tips)
    with tab4:
        st.markdown("""
        <div style='background: #fafbfc; border-radius: 12px; padding: 2rem;
                    border-left: 3px solid #2E8B57; margin-bottom: 2.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>
            <h3 style='color: #1a202c; margin: 0 0 0.75rem 0; font-weight: 600;
                       font-size: 1.4rem; letter-spacing: -0.01em;'>
                💡 Dicas e Boas Práticas
            </h3>
            <p style='color: #718096; margin: 0; line-height: 1.7;'>
                Aproveite ao máximo esta ferramenta com estas dicas profissionais
            </p>
        </div>
        """, unsafe_allow_html=True)

        for dica in tool["dicas"]:
            st.markdown(f"""
            <div style='background: white; padding: 1.25rem 1.5rem; margin-bottom: 1rem;
                        border-radius: 10px; border-left: 3px solid #2E8B57;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.06);'>
                <div style='color: #2d3748; line-height: 1.8; font-size: 1rem;'>
                    {dica}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

        # CTA
        if st.button("🚀 Começar a Usar", key=f"cta_dicas_{tool_key}", use_container_width=True):
            st.rerun()
