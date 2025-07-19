# GeoCommerce - Análise Geográfica

Uma ferramenta abrangente de análise geográfica e comercial para dados de e-commerce com integração direta de API.

## Funcionalidades

### 🔗 Integração com API
- Conexão direta com API GraphQL
- Busca de dados em tempo real para clientes e pedidos
- Limitação inteligente de taxa e tratamento de erros
- Suporte a atualizações incrementais

### 🗺️ Análise Geográfica
- Mapas interativos com distribuição de clientes
- Mapas de calor para análise de receita
- Análises baseadas em estado e cidade
- Geocodificação com múltiplos provedores (Google Maps, Nominatim)

### 👥 Análise de Clientes
- Segmentação de clientes por padrões de gastos
- Análise tipo RFM
- Insights de distribuição geográfica
- Análise do valor vitalício do cliente

### 📦 Análise de Pedidos
- Análise temporal de pedidos e receita
- Reconhecimento de padrões de pedidos
- Distribuição geográfica de pedidos
- Análise de performance de produtos

### 🎯 Análises Avançadas
- Agrupamento K-Means, DBSCAN e Hierárquico
- Métricas de performance e KPIs
- Relatórios abrangentes
- Exportação de dados em múltiplos formatos (CSV, Excel, JSON)

### 🚀 Otimizações de Performance
- Sistema inteligente de cache
- Gerenciamento de estado da sessão Streamlit
- Processamento assíncrono de dados
- Acompanhamento de progresso para operações longas

## Instalação

### 1. Dependências
Instale os pacotes Python necessários:

```bash
pip install -r requirements.txt
```

### 2. Configuração do Ambiente
Crie um arquivo `.env` na raiz do seu projeto com suas credenciais:

```env
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01

# Opcional: Chave da API do Google Maps para geocodificação aprimorada
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 3. Configuração da App Shopify
Para usar este sistema, você precisa de uma app privada do Shopify com as seguintes permissões:

**Permissões Necessárias:**
- `read_customers`
- `read_orders`
- `read_products` (opcional)

**Para criar uma app privada:**
1. Vá para o painel de administração do Shopify
2. Navegue para Configurações > Apps e canais de vendas
3. Clique em "Desenvolver apps"
4. Crie uma nova app e configure os escopos da API Admin
5. Gere credenciais da API

## Uso

### Executando o Aplicativo

Execute o aplicativo Streamlit:

```bash
streamlit run geocommerce/geocommerce_shopify.py
```

Ou use o ponto de entrada principal:

```python
from geocommerce import GeoCommerceShopifyApp

app = GeoCommerceShopifyApp()
app.run()
```

### Fluxo de Uso do Aplicativo

1. **Teste de Conexão**: Teste a conexão com a API da Shopify
2. **Busca de Dados**: Busque clientes e pedidos da Shopify
3. **Análise**: Explore diferentes abas de análise
4. **Exportação**: Baixe relatórios e dados

### Componentes Principais

#### Conector Shopify
```python
from geocommerce import ShopifyGraphQLClient

async def fetch_data():
    async with ShopifyGraphQLClient() as client:
        customers = await client.fetch_all_customers()
        orders = await client.fetch_all_orders()
        return customers, orders
```

#### Processamento de Dados
```python
from geocommerce import ShopifyDataProcessor

processor = ShopifyDataProcessor()
customers_df = processor.process_customers_data(customers_data)
orders_df = processor.process_orders_data(orders_data)
```

#### Análise
```python
from geocommerce import GeoCommerceAnalyzer

analyzer = GeoCommerceAnalyzer()
metrics = analyzer.calculate_basic_metrics(customers_df, orders_df)
map_obj = analyzer.create_geographic_distribution_map(customers_df)
```

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-------------|----------|
| `SHOPIFY_SHOP_NAME` | Seu nome de loja Shopify (sem .myshopify.com) | Sim |
| `SHOPIFY_ACCESS_TOKEN` | Token de acesso da app privada | Sim |
| `SHOPIFY_API_VERSION` | Versão da API da Shopify (padrão: 2024-01) | Não |
| `GOOGLE_MAPS_API_KEY` | Chave da API do Google Maps para geocodificação aprimorada | Não |

### Configurações do Aplicativo

O aplicativo pode ser configurado através da classe `GeoCommerceConfig`:

```python
from geocommerce import GeoCommerceConfig

config = GeoCommerceConfig()
config.DEFAULT_MAP_ZOOM = 8
config.MAX_EXPORT_ROWS = 50000
```

## Visão Geral de Funcionalidades

### 📈 Abas de Visão Geral
- Métricas de negócios principais
- Indicadores de qualidade dos dados
- Resumo de atividade recente

### 🗺️ Abas de Análise Geográfica
- Mapas de distribuição interativa
- Mapas de calor
- Análises de estado e cidade
- Locais com melhor performance

### 👥 Abas de Análise de Clientes
- Segmentação de clientes
- Distribuição de valor
- Tabela de detalhes dos clientes
- Estatísticas e insights

### 📦 Abas de Análise de Pedidos
- Tendências temporais
- Padrões de pedidos
- Análise de receita
- Visualização de pedidos recentes

### 🎯 Abas de Agrupamento
- Múltiplos algoritmos de agrupamento
- Agrupamento geográfico e comportamental
- Análise de pontuação de silhueta
- Resumos de clusters

### 📊 Abas de Relatórios
- Relatórios abrangentes de resumo
- Exportação JSON
- Visualização de dados
- Métricas de performance

## Processamento de Dados

### Geocodificação
O sistema utiliza uma abordagem de geocodificação multi-nível:

1. **Coordenadas do Shopify**: Usa coordenadas fornecidas pelo Shopify se disponíveis
2. **API do Google Maps**: Serviço de geocodificação principal (se configurado)
3. **Nominatim**: Serviço de geocodificação gratuito de fallback
4. **Cache**: Resultados são armazenados em cache para evitar chamadas API redundantes

### Esquema de Dados

**Dados de Cliente Processados:**
- `customer_id`, `email`, `first_name`, `last_name`
- `city`, `province`, `country`, `zip`
- `latitude`, `longitude`
- `total_spent`, `orders_count`
- `created_at`, `updated_at`

**Dados de Pedido Processados:**
- `order_id`, `total_price`, `created_at`
- `customer_id`, `customer_email`
- `shipping_city`, `shipping_province`, `shipping_country`
- `shipping_latitude`, `shipping_longitude`
- `product_title`, `quantity`, `price`

## Considerações de Desempenho

### Estratégia de Cache
- Resultados de geocodificação são armazenados permanentemente
- Respostas da API da Shopify podem ser armazenadas por sessão
- Streamlit's `@st.cache_data` para computações caras

### Limitação de Taxa
- API da Shopify: 40 requisições/segundo (configurável)
- Nominatim: 1 requisição/segundo
- Google Maps: Baseado em sua cota

### Gestão de Memória
- Conjuntos de dados grandes são processados em partes
- Operações de exportação são limitadas a contagens de linhas configuráveis
- O estado da sessão é gerenciado eficientemente

## Solução de Problemas

### Problemas Comuns

**Conexão Falhou:**
- Verifique se o arquivo `.env` contém credenciais corretas
- Verifique se sua app do Shopify tem as permissões necessárias
- Certifique-se de que seu token de acesso é válido

**Problemas de Geocodificação:**
- Taxas de falha de geocodificação altas podem indicar problemas de qualidade dos dados
- Considere habilitar a API do Google Maps para melhores resultados
- Verifique o arquivo de cache de geocodificação para erros

**Problemas de Desempenho:**
- Reduza o número de registros buscados em uma única operação
- Limpe o cache se a utilização de memória for alta
- Use atualizações incrementais para conjuntos de dados grandes

**Problemas de Exibição do Mapa:**
- Certifique-se de que `streamlit-folium` está instalado
- Verifique se as coordenadas são válidas
- Verifique se os tiles do mapa estão acessíveis

### Logging
O aplicativo usa o módulo de logging do Python. Defina o nível de log para depuração:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Referência da API

### Classes Principais

- `GeoCommerceShopifyApp`: Aplicativo Streamlit principal
- `ShopifyGraphQLClient`: Cliente da API da Shopify
- `ShopifyDataProcessor`: Utilitários de transformação de dados
- `GeoCommerceAnalyzer`: Métodos de análise e visualização
- `GeoCommerceConfig`: Gerenciamento de configurações

### Métodos Principais

- `test_connection()`: Teste a conexão com a API da Shopify
- `fetch_all_customers()`: Busque todos os clientes com paginação
- `fetch_all_orders()`: Busque todos os pedidos com paginação
- `process_customers_data()`: Transforme os dados do cliente
- `process_orders_data()`: Transforme os dados do pedido
- `create_geographic_distribution_map()`: Gere mapas interativos
- `perform_clustering_analysis()`: Execute algoritmos de agrupamento

## Contribuindo

Quando contribuindo para este projeto:

1. Siga as diretrizes de estilo PEP 8
2. Adicione anotações de tipo para novas funções
3. Inclua docstrings para todos os métodos públicos
4. Teste com diferentes tamanhos de dados e casos de borda
5. Atualize este README para novas funcionalidades

## Licença

Este projeto é desenvolvido como parte do sistema GeoCommerce para análise de e-commerce.

## Suporte

Para problemas e dúvidas:
1. Consulte a seção de solução de problemas
2. Revise os logs de erro
3. Verifique a configuração da API da Shopify
4. Teste com um conjunto de dados menor primeiro