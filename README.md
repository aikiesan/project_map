# CP2B Maps V2 - Plataforma de Análise de Potencial de Geração de Biogás para Municípios Paulistas

[![Proprietary License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io)
[![WCAG 2.1 Level A](https://img.shields.io/badge/Accessibility-WCAG%202.1%20Level%20A-blue.svg)](https://www.w3.org/WAI/WCAG21/quickref/)

Plataforma profissional de análise de potencial de geração de biogás para municípios do Estado de São Paulo, desenvolvida com arquitetura moderna e conformidade com padrões de acessibilidade WCAG 2.1 Nível A.

---

## 🌟 Características Principais

### 📊 **Análise Geoespacial Avançada**
- Mapas interativos com múltiplas camadas (coroplético, círculos proporcionais, heatmap)
- Integração com dados MapBiomas para análise de uso do solo
- Análise de proximidade com raio personalizável
- Visualizações profissionais com Plotly e Folium
- Exportação de dados e mapas

### 🤖 **Assistente IA - Bagacinho**
- Chatbot inteligente com integração Google Gemini
- RAG (Retrieval-Augmented Generation) para consultas contextuais
- Acesso direto aos dados de 645 municípios paulistas
- Respostas baseadas em dados reais e referências científicas

### 🔬 **Dados Validados de Pesquisa**
- Fatores de disponibilidade validados pela pesquisa FAPESP 2025/08745-2
- Metodologia conservadora para estimativas realistas
- Dados de agricultura, pecuária e RSU (Resíduos Sólidos Urbanos)
- Resíduos complementares de avicultura

### 📚 **Sistema de Referências Científicas**
- Banco de dados com 20+ referências científicas
- Citações automáticas em formato ABNT
- Categorias: substratos, co-digestão, fontes de dados, metodologia
- Popovers interativos com informações detalhadas

### ♿ **Acessibilidade WCAG 2.1 Nível A**
- Navegação completa por teclado
- Suporte a leitores de tela (NVDA, JAWS, ORCA, VoiceOver)
- Texto alternativo para todas as visualizações
- Estrutura semântica com marcos ARIA
- Interface nativa em português brasileiro

### 📈 **8 Módulos de Análise**
1. **🏠 Mapa Principal** - Visualização interativa dos dados municipais
2. **🔍 Explorar Dados** - Gráficos, rankings, estatísticas e comparações
3. **📊 Análises Avançadas** - Análise de resíduos por tipo e região
4. **🎯 Análise de Proximidade** - Análise espacial com raio personalizável
5. **🍊 Bagacinho IA** - Assistente inteligente com RAG
6. **📚 Referências Científicas** - Banco de referências acadêmicas
7. **🔬 Dados Validados** - Fatores de disponibilidade validados
8. **ℹ️ Sobre o CP2B Maps** - Informações do projeto e metodologia

---

## 🏗️ Arquitetura do Projeto

```
cp2b_maps_v2/
├── app.py                          # Entry point da aplicação Streamlit
├── requirements.txt                # Dependências Python
├── packages.txt                    # Dependências do sistema (GDAL, etc.)
│
├── config/                         # Configurações
│   ├── settings.py                 # Configurações centralizadas
│   └── scenario_config.py          # Sistema de cenários
│
├── src/                            # Código fonte
│   ├── accessibility/              # Sistema de acessibilidade WCAG 2.1
│   │   ├── core.py                 # Gerenciador de acessibilidade
│   │   ├── settings.py             # Configurações de acessibilidade
│   │   └── components/             # Componentes acessíveis
│   │
│   ├── ai/                         # Inteligência Artificial
│   │   ├── gemini_integration.py   # Integração Google Gemini
│   │   └── bagacinho_rag.py        # Sistema RAG
│   │
│   ├── core/                       # Lógica de negócio
│   │   ├── biogas_calculator.py    # Cálculos de potencial de biogás
│   │   ├── geospatial_analysis.py  # Análises geoespaciais
│   │   └── proximity_analyzer.py   # Análise de proximidade
│   │
│   ├── data/                       # Camada de acesso a dados
│   │   ├── loaders/                # Carregadores de dados
│   │   ├── processors/             # Processadores de dados
│   │   ├── references/             # Sistema de referências
│   │   └── research_data.py        # Dados validados de pesquisa
│   │
│   ├── ui/                         # Interface do usuário
│   │   ├── pages/                  # Páginas da aplicação
│   │   ├── components/             # Componentes reutilizáveis
│   │   ├── styles/                 # Temas e estilos
│   │   └── utils/                  # Utilitários de UI
│   │
│   └── utils/                      # Utilitários gerais
│       ├── logging_config.py       # Configuração de logs
│       └── memory_monitor.py       # Monitor de memória
│
├── data/                           # Dados da aplicação
│   ├── database/                   # Banco de dados SQLite
│   ├── shapefile/                  # Arquivos shapefile (GIS)
│   ├── rasters/                    # Dados raster (MapBiomas)
│   └── Dados_Por_Municipios_SP.xls # Dados municipais
│
├── docs/                           # Documentação técnica
│   ├── ACCESSIBILITY_GUIDE.md      # Guia de acessibilidade
│   ├── DEPLOYMENT.md               # Guia de deployment
│   └── DEVELOPMENT_STATUS.md       # Status de desenvolvimento
│
└── .streamlit/                     # Configurações Streamlit
    └── secrets.toml                # Secrets (API keys, etc.)
```

---

## 🔧 Acesso à Aplicação

### **⚠️ Software Proprietário - Código Fechado**

Este é um software proprietário desenvolvido pela equipe de pesquisa CP2B Maps. O código-fonte não está disponível para download ou modificação.

### **🌐 Acesso Web**

A aplicação está disponível como uma plataforma web para uso por:
- Institutos de pesquisa
- Universidades
- Organizações focadas em energia renovável
- Pesquisadores na área de biogás

**Para acessar a aplicação web:**
- **URL**: [A ser divulgada após deployment]
- **Acesso**: Contate a equipe através do GitHub Issues para solicitar acesso

### **📊 Acesso aos Dados**

Pesquisadores e instituições podem solicitar:
- **Acesso à plataforma web** para visualização e análise
- **Exportação de dados** para fins acadêmicos (com atribuição apropriada)
- **Colaborações** em projetos de pesquisa relacionados
- **Integração de dados** em pesquisas sobre biogás e energia renovável

### **🤝 Solicitação de Acesso**

Para solicitar acesso ou colaboração:
1. Abra uma [Issue no GitHub](https://github.com/aikiesan/cp2b_maps_v2/issues)
2. Descreva sua instituição e propósito de uso
3. Aguarde resposta da equipe (geralmente 3-5 dias úteis)

### **📝 Registro INPI**

Este software está em processo de registro no INPI (Instituto Nacional da Propriedade Industrial) sob propriedade da equipe de pesquisa CP2B Maps.

---

## 📊 Stack Tecnológica

### **Core**
- **Python** 3.8+ - Linguagem principal
- **Streamlit** 1.31+ - Framework web interativo

### **Geoespacial**
- **GeoPandas** - Manipulação de dados geoespaciais
- **Shapely** - Operações geométricas
- **Folium** - Mapas interativos
- **Rasterio** - Processamento de dados raster
- **MapBiomas** - Dados de uso do solo

### **Visualização**
- **Plotly** - Gráficos interativos
- **Matplotlib** - Visualizações estáticas

### **Inteligência Artificial**
- **Google Gemini API** - Modelo de linguagem
- **Custom RAG System** - Retrieval-Augmented Generation

### **Dados**
- **Pandas** - Manipulação de dados tabulares
- **NumPy** - Computação numérica
- **SQLite** - Banco de dados local
- **OpenPyXL/XLRD** - Leitura de arquivos Excel

### **Performance & Utilidades**
- **Psutil** - Monitoramento de recursos
- **Pillow** - Processamento de imagens
- **Jenkspy** - Classificação de dados (Natural Breaks)

---

## 🚀 Deployment

### **Streamlit Community Cloud (Recomendado)**

1. Faça push do código para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Configure secrets (se necessário)
5. Deploy!

**Consulte** [DEPLOYMENT.md](docs/DEPLOYMENT.md) para instruções detalhadas.

### **Outras Opções**
- **Docker**: Containerização para deploy em qualquer plataforma
- **AWS/GCP/Azure**: Cloud providers com suporte Streamlit
- **Heroku**: Platform-as-a-Service

---

## 📖 Uso

### **Navegação Básica**

1. **Selecione o tipo de resíduo** na barra lateral
2. **Escolha o tipo de mapa** (coroplético, círculos, heatmap)
3. **Explore os dados** nos diferentes módulos
4. **Use o Bagacinho IA** para consultas específicas
5. **Exporte dados** em CSV/Excel conforme necessário

### **Análise de Proximidade**

1. Acesse a aba "🎯 Análise de Proximidade"
2. Selecione um município de referência
3. Defina o raio de análise (km)
4. Visualize municípios próximos e estatísticas agregadas

### **Consultas com IA**

1. Acesse "🍊 Bagacinho IA"
2. Digite sua pergunta sobre os dados
3. Receba respostas contextualizadas com referências

### **Acessibilidade**

- **Navegação por teclado**: Use Tab para navegar
- **Leitores de tela**: Ative o "Modo Leitor de Tela" na sidebar
- **Atalhos**: Alt+M (mapas), Alt+D (dados), Alt+A (análise)

**Consulte** [ACCESSIBILITY_GUIDE.md](docs/ACCESSIBILITY_GUIDE.md) para detalhes completos sobre acessibilidade.

---

## 🔬 Dados e Metodologia

### **Fontes de Dados**
- **IBGE**: Dados demográficos e territoriais
- **MapBiomas**: Uso e cobertura do solo
- **Pesquisa FAPESP**: Fatores de disponibilidade validados
- **Literatura Científica**: Parâmetros de conversão de biogás

### **Metodologia de Cálculo**
- Potencial de biogás calculado por tipo de resíduo
- Fatores de conversão baseados em literatura revisada por pares
- Metodologia conservadora para estimativas realistas
- Consideração de sazonalidade e disponibilidade

### **Referências Científicas**
O sistema inclui 20+ referências científicas categorizadas:
- Substratos agrícolas (café, citrus, milho, cana, soja)
- Substratos de pecuária (bovinos, suínos, aves)
- Co-digestão (combinações de substratos)
- Fontes de dados (MapBiomas, IBGE, EPE)

---

## 🤝 Colaboração e Feedback

### **⚠️ Código Fechado - Sem Contribuições Externas de Código**

Este é um software proprietário. Não aceitamos pull requests ou contribuições diretas ao código-fonte.

### **Como Você Pode Colaborar:**

1. **Reportar Bugs**: Use [GitHub Issues](https://github.com/aikiesan/cp2b_maps_v2/issues) para reportar problemas encontrados na aplicação web
2. **Sugerir Features**: Compartilhe ideias para novas funcionalidades através de Issues
3. **Feedback de UX/UI**: Envie feedback sobre usabilidade e experiência do usuário
4. **Parcerias de Pesquisa**: Proponha colaborações acadêmicas e projetos de pesquisa
5. **Validação de Dados**: Contribua com validação científica dos dados e metodologias

### **Pesquisa Colaborativa**

Estamos abertos a colaborações com:
- Universidades e centros de pesquisa
- Institutos de energia renovável
- Organizações focadas em sustentabilidade
- Pesquisadores da área de biogás e bioenergia

**Contato**: Abra uma Issue descrevendo sua proposta de colaboração.

---

## 📊 Status de Desenvolvimento

**Versão Atual**: 2.0.0

- ✅ **Fase 1 Completa**: Infraestrutura core e funcionalidades básicas
- 🚧 **Fase 2 Em Andamento**: Integração de dados e features avançadas (~70% completo)
- ⏳ **Fase 3 Planejada**: Otimização de performance e testes
- ⏳ **Fase 4 Planejada**: Deployment e documentação final

**Consulte** [DEVELOPMENT_STATUS.md](docs/DEVELOPMENT_STATUS.md) para status detalhado.

---

## 📄 Licença

Este projeto é **software proprietário** com todos os direitos reservados à equipe de pesquisa CP2B Maps.

**Copyright © 2025 CP2B Maps Research Team. All Rights Reserved.**

- O código-fonte não está disponível para distribuição
- O acesso é restrito à plataforma web oficial
- Uso comercial não autorizado sem permissão expressa
- Veja o arquivo [LICENSE](LICENSE) para detalhes completos sobre termos e condições

### Uso de Dados

Dados exportados da plataforma para fins acadêmicos devem incluir citação apropriada:

```
CP2B Maps V2 - Plataforma de Análise de Potencial de Geração de Biogás para
Municípios Paulistas. (2025). CP2B Research Team. Acesso via web application.
```

---

## 🏆 Reconhecimentos

### **Pesquisa**
Este projeto é resultado de pesquisa financiada pela **FAPESP** (Fundação de Amparo à Pesquisa do Estado de São Paulo):
- Processo FAPESP: 2025/08745-2
- Área: Energia Renovável e Biogás

### **Tecnologias**
- Streamlit Community pelo excelente framework
- Google Gemini pela API de IA
- MapBiomas pela disponibilização de dados de uso do solo
- IBGE pelos dados oficiais brasileiros

### **Equipe**
Desenvolvido pela **equipe de pesquisa CP2B Maps** com foco em sustentabilidade energética e desenvolvimento de ferramentas de análise acessíveis.

---

## 📞 Contato e Suporte

### **Repositório GitHub**
https://github.com/aikiesan/cp2b_maps_v2

### **Issues e Sugestões**
https://github.com/aikiesan/cp2b_maps_v2/issues

### **Documentação Completa**
- [Guia de Acessibilidade](docs/ACCESSIBILITY_GUIDE.md)
- [Guia de Deployment](docs/DEPLOYMENT.md)
- [Status de Desenvolvimento](docs/DEVELOPMENT_STATUS.md)

---

## 📚 Histórico de Versões

**v2.0.0** (Outubro 2025)
- Arquitetura profissional modular
- Sistema de acessibilidade WCAG 2.1 Nível A
- Assistente IA Bagacinho com RAG
- Dados validados de pesquisa FAPESP
- Sistema de referências científicas
- 8 módulos de análise completos

**v1.x** (Repositório legado)
- Versão inicial com funcionalidades básicas
- Repositório: [cp2b_maps](https://github.com/aikiesan/cp2b_maps)

**Consulte** [CHANGELOG.md](CHANGELOG.md) para histórico completo.

---

<div align="center">

**🌱 Construído com ❤️ para promover energia renovável e sustentabilidade no Brasil 🌱**

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Made in Brazil](https://img.shields.io/badge/Made%20in-Brazil-green?style=for-the-badge)](https://github.com/aikiesan/cp2b_maps_v2)

</div>
