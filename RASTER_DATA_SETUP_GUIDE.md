# 🗺️ CP2B Maps - Guia de Configuração de Dados Raster

## 📋 Visão Geral

Este guia explica como configurar dados raster para análise geoespacial no CP2B Maps, incluindo dados do MapBiomas, imagens de satélite e outros dados georreferenciados.

---

## 📁 Estrutura de Diretórios

```
CP2B_Maps_V2/
├── data/
│   ├── rasters/                    # ← Adicione seus arquivos raster aqui
│   │   ├── mapbiomas_agro_2023.tif
│   │   ├── satellite_ndvi.tif
│   │   └── elevation_sp.tif
│   ├── database/
│   └── shapefiles/
```

---

## 🗂️ Tipos de Dados Suportados

### ✅ Formatos Aceitos
- **GeoTIFF (*.tif, *.tiff)** - Formato recomendado
- **IMG (*.img)** - Imagens ERDAS
- **HDF (*.hdf)** - Dados científicos hierárquicos
- **NetCDF (*.nc)** - Dados climáticos

### 📊 Tipos de Dados Recomendados

#### 1. **Dados MapBiomas** 🌾
```
Arquivo: mapbiomas_agropecuaria_sp_2023.tif
Fonte: https://mapbiomas.org/
Uso: Análise de uso e cobertura do solo agrícola
Classes: Pastagem, Agricultura anual, Agricultura perene, etc.
```

#### 2. **Índices de Vegetação** 🌱
```
Arquivo: ndvi_sp_2023.tif
Fonte: Sentinel-2, Landsat
Uso: Monitoramento da vegetação
Valores: -1 a +1 (NDVI)
```

#### 3. **Modelo Digital de Elevação** ⛰️
```
Arquivo: dem_saopaulo_30m.tif
Fonte: SRTM, ALOS
Uso: Análise topográfica
Valores: Elevação em metros
```

#### 4. **Dados Climáticos** 🌡️
```
Arquivo: precipitacao_anual_sp.tif
Fonte: WorldClim, INMET
Uso: Análise climática
Valores: Precipitação em mm/ano
```

---

## 📥 Como Obter Dados Raster

### 1. **MapBiomas** (Recomendado)
- **Site**: https://mapbiomas.org/
- **Acesso**: https://plataforma.mapbiomas.org/map
- **Dados São Paulo**:
  - Navegue até São Paulo
  - Selecione "Agropecuária"
  - Baixe o raster da coleção mais recente
  - Formato: GeoTIFF

### 2. **INPE (Instituto Nacional de Pesquisas Espaciais)**
- **Site**: http://www.dpi.inpe.br/
- **Catálogo**: http://www.dgi.inpe.br/catalogo/
- **Dados**: Landsat, CBERS, Sentinel

### 3. **IBGE (Geociências)**
- **Site**: https://www.ibge.gov.br/geociencias/
- **Downloads**: https://downloads.ibge.gov.br/
- **Dados**: Base cartográfica, relevo

### 4. **Google Earth Engine**
- **Site**: https://earthengine.google.com/
- **Acesso**: Requer cadastro
- **Dados**: Sentinel, Landsat, MODIS

### 5. **USGS Earth Explorer**
- **Site**: https://earthexplorer.usgs.gov/
- **Dados**: Landsat, SRTM, ASTER

---

## ⚙️ Configuração Passo a Passo

### **Passo 1: Preparar o Diretório**
```bash
# Verificar se o diretório existe
ls -la data/rasters/

# Se não existir, será criado automaticamente pelo CP2B Maps
```

### **Passo 2: Baixar Dados do MapBiomas**

1. **Acesse**: https://plataforma.mapbiomas.org/map
2. **Configure**:
   - Território: São Paulo
   - Tema: Agropecuária
   - Ano: 2023 (mais recente)
3. **Baixe**:
   - Clique em "Baixar dados"
   - Selecione formato GeoTIFF
   - Escolha resolução 30m

### **Passo 3: Organizar Arquivos**
```bash
# Copiar arquivos para o diretório correto
cp ~/Downloads/mapbiomas_*.tif data/rasters/

# Verificar arquivos
ls -la data/rasters/
```

### **Passo 4: Verificar Configuração**
1. **Abra o CP2B Maps**
2. **Navegue**: Raster Analysis
3. **Verificar**: Lista de arquivos raster disponíveis

---

## 🔧 Especificações Técnicas

### **Requisitos dos Arquivos Raster**

#### ✅ **Sistema de Coordenadas**
- **Recomendado**: EPSG:4326 (WGS84) ou EPSG:31983 (SIRGAS 2000)
- **Suportado**: Qualquer CRS válido (conversão automática)

#### ✅ **Resolução Espacial**
- **Ótima**: 30m (compatível com Landsat)
- **Aceitável**: 10m - 250m
- **Máxima**: 1km

#### ✅ **Extensão Geográfica**
- **Foco**: Estado de São Paulo
- **Coordenadas**:
  - Norte: -19.5°
  - Sul: -25.5°
  - Leste: -44.0°
  - Oeste: -53.5°

#### ✅ **Formato de Dados**
- **Tipo**: Int16, Float32, Byte
- **NoData**: Valores NoData definidos
- **Compressão**: LZW recomendada

### **Exemplo de Especificação MapBiomas**
```
Driver: GTiff/GeoTIFF
Files: mapbiomas_agro_sp_2023.tif
Size is 50000, 30000
Coordinate System is:
GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84",6378137,298.257223563]],
    PRIMEM["Greenwich",0],
    CS[ellipsoidal,2],
        AXIS["latitude",north],
        AXIS["longitude",east],
    UNIT["degree",0.0174532925199433]]
Origin = (-53.500000000000000,-19.500000000000000)
Pixel Size = (0.000269978401727861,-0.000269978401727861)
```

---

## 🧪 Teste de Configuração

### **Script de Verificação**
Use o script de teste integrado:
```bash
# Executar teste
streamlit run test_application_functionality.py --server.port 8502

# Verificar seção "Raster Loading Testing"
```

### **Verificação Manual**
1. **Abrir CP2B Maps**: http://localhost:8501
2. **Navegar**: Raster Analysis
3. **Verificar**:
   - ✅ Lista de arquivos raster aparece
   - ✅ Arquivo pode ser selecionado
   - ✅ Mapa carrega corretamente
   - ✅ Classes do MapBiomas são exibidas

---

## 🚨 Solução de Problemas

### **❌ "Found 0 raster files"**
**Problema**: Nenhum arquivo raster encontrado
**Soluções**:
1. Verificar se arquivos estão em `data/rasters/`
2. Confirmar formato (.tif, .tiff)
3. Verificar permissões de leitura
4. Recarregar página

### **❌ "Error loading raster"**
**Problema**: Erro ao carregar arquivo raster
**Soluções**:
1. Verificar se arquivo está corrompido
2. Confirmar sistema de coordenadas
3. Verificar se gdal/rasterio estão instalados
4. Converter para GeoTIFF padrão

### **❌ "Memory error"**
**Problema**: Arquivo raster muito grande
**Soluções**:
1. Reduzir resolução espacial
2. Recortar área de interesse
3. Usar compressão LZW
4. Converter para Int16 se possível

### **❌ "Projection error"**
**Problema**: Sistema de coordenadas incompatível
**Soluções**:
1. Reprojetar para EPSG:4326
2. Usar gdalwarp para conversão
3. Verificar definição de CRS

---

## 📊 Dados de Exemplo para Teste

### **Dataset Básico** (Recomendado para primeiros testes)
```bash
# Baixar dados de exemplo (simulado)
wget https://exemplo.com/mapbiomas_sp_sample.tif -O data/rasters/
```

### **Criar Raster de Teste**
```python
# Script para criar raster de teste
import numpy as np
import rasterio
from rasterio.transform import from_bounds

# Área de São Paulo (exemplo)
bounds = (-53.5, -25.5, -44.0, -19.5)  # oeste, sul, leste, norte
width, height = 1000, 600

# Criar dados simulados
data = np.random.randint(1, 50, size=(height, width), dtype=np.uint8)

# Salvar como GeoTIFF
transform = from_bounds(*bounds, width, height)

with rasterio.open(
    'data/rasters/teste_sp.tif',
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype=data.dtype,
    crs='EPSG:4326',
    transform=transform,
    compress='lzw'
) as dst:
    dst.write(data, 1)

print("Arquivo de teste criado: data/rasters/teste_sp.tif")
```

---

## 📈 Otimização de Performance

### **1. Tamanho de Arquivo**
- **Máximo recomendado**: 500MB por arquivo
- **Usar compressão**: LZW ou DEFLATE
- **Pyramid/Overview**: Gerar para arquivos grandes

### **2. Resolução Espacial**
- **Análise municipal**: 30m-100m suficiente
- **Análise regional**: 250m-1km aceitável
- **Análise local**: 10m-30m necessário

### **3. Cache e Memória**
- **Cache automático**: Habilitado por padrão
- **Limite de memória**: 2GB por operação
- **Cleanup**: Automático após 1 hora

---

## 📞 Suporte

### **Problemas com Dados Raster**
- **Email**: support@cp2bmaps.com
- **GitHub Issues**: https://github.com/cp2bmaps/issues
- **Documentação**: https://docs.cp2bmaps.com/raster

### **Recursos Adicionais**
- **Tutorial GDAL**: https://gdal.org/tutorials/
- **Rasterio Docs**: https://rasterio.readthedocs.io/
- **MapBiomas API**: https://mapbiomas.org/api

---

**🎯 Resultado Esperado**: Após seguir este guia, você terá dados raster funcionais no CP2B Maps, permitindo análises geoespaciais avançadas com dados do MapBiomas e outras fontes de satélite.

---

*Última atualização: 29 de setembro de 2024*
*Versão: 2.0*