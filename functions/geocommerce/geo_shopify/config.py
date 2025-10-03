"""
Configuration settings for GeoCommerce Shopify integration
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ShopifyConfig:
    """Shopify API configuration class"""
    
    def __init__(self):
        self.access_token: Optional[str] = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.api_version: str = os.getenv('SHOPIFY_API_VERSION', '2024-01')
        self.timeout: int = int(os.getenv('SHOPIFY_TIMEOUT', '30'))
        
        # Additional configuration attributes
        self.shop_name: Optional[str] = os.getenv('SHOPIFY_SHOP_NAME')
        self.DEFAULT_MAP_CENTER: list = [-14.235004, -51.92528]  # Brazil center
        self.DEFAULT_MAP_ZOOM: int = 4
        self.CHART_HEIGHT: int = 400
        self.MAX_EXPORT_ROWS: int = 10000
        self.INCREMENTAL_UPDATE_DAYS: int = 7
        self.EXPORT_FORMATS: list = ['CSV', 'Excel', 'JSON']
        self.CLUSTERING_METHODS: list = ['K-means', 'DBSCAN', 'Hierarchical']
        self.MIN_CLUSTERS: int = 2
        self.MAX_CLUSTERS: int = 10
        self.DEFAULT_CLUSTERS: int = 5
    
    @classmethod
    def from_env(cls) -> 'ShopifyConfig':
        """Create config from environment variables"""
        shop_name = os.getenv('SHOPIFY_SHOP_NAME')
        access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        api_version = os.getenv('SHOPIFY_API_VERSION', '2024-01')
        
        if not shop_name or not access_token:
            raise ValueError("SHOPIFY_SHOP_NAME and SHOPIFY_ACCESS_TOKEN must be set in environment")
        
        config = cls()
        config.shop_name = shop_name
        config.access_token = access_token
        config.api_version = api_version
        return config
        
    def is_configured(self) -> bool:
        """Check if Shopify configuration is complete"""
        return bool(self.shop_name and self.access_token)
    
    def get_api_url(self) -> str:
        """Get the Shopify GraphQL API URL"""
        if not self.shop_name:
            raise ValueError("Shopify shop name not configured")
        return f"https://{self.shop_name}.myshopify.com/admin/api/{self.api_version}/graphql.json"
    
    def get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        if not self.access_token:
            raise ValueError("Shopify access token not configured")
        return {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }
    
    def validate_shopify_credentials(self) -> Dict[str, Any]:
        """Validate Shopify credentials and return validation result"""
        errors = []
        
        if not self.shop_name:
            errors.append("SHOPIFY_SHOP_NAME não está configurado")
        
        if not self.access_token:
            errors.append("SHOPIFY_ACCESS_TOKEN não está configurado")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_available_countries(self) -> list:
        """Get list of available countries for filtering"""
        return ['Brasil', 'Estados Unidos', 'Canadá', 'Reino Unido', 'Austrália']
    
    def get_provinces_for_country(self, country: str) -> list:
        """Get list of provinces/states for a specific country"""
        provinces_map = {
            'Brasil': ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia', 'Paraná', 'Rio Grande do Sul', 'Pernambuco', 'Ceará', 'Pará', 'Santa Catarina', 'Goiás', 'Maranhão', 'Paraíba', 'Espírito Santo', 'Piauí', 'Alagoas', 'Tocantins', 'Rio Grande do Norte', 'Acre', 'Rondônia', 'Roraima', 'Amapá', 'Amazonas', 'Mato Grosso', 'Mato Grosso do Sul', 'Sergipe', 'Distrito Federal'],
            'Estados Unidos': ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
            'Canadá': ['Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador', 'Northwest Territories', 'Nova Scotia', 'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan', 'Yukon'],
            'Reino Unido': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'Austrália': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia', 'Tasmania', 'Australian Capital Territory', 'Northern Territory']
        }
        return provinces_map.get(country, [])
    
    def get_cities_for_province(self, country: str, province: str) -> list:
        """Get list of cities for a specific province/state"""
        # This is a simplified implementation - in a real app, you'd have a comprehensive city database
        # For now, return some major cities for common provinces
        cities_map = {
            ('Brasil', 'São Paulo'): ['São Paulo', 'Campinas', 'Santos', 'São José dos Campos', 'Ribeirão Preto'],
            ('Brasil', 'Rio de Janeiro'): ['Rio de Janeiro', 'Niterói', 'Petrópolis', 'Nova Iguaçu', 'Duque de Caxias'],
            ('Estados Unidos', 'California'): ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'San Jose'],
            ('Estados Unidos', 'New York'): ['New York City', 'Buffalo', 'Rochester', 'Syracuse', 'Albany'],
            ('Canadá', 'Ontario'): ['Toronto', 'Ottawa', 'Mississauga', 'Brampton', 'Hamilton'],
            ('Reino Unido', 'England'): ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Leeds'],
            ('Austrália', 'New South Wales'): ['Sydney', 'Newcastle', 'Wollongong', 'Central Coast', 'Wagga Wagga']
        }
        return cities_map.get((country, province), [])
    
    def get_date_range_options(self) -> Dict[str, Dict]:
        """Get available date range options"""
        return {
            'Últimos 7 dias': {'days': 7},
            'Últimos 30 dias': {'days': 30},
            'Últimos 90 dias': {'days': 90},
            'Últimos 365 dias': {'days': 365},
            'Este ano': {'type': 'this_year'},
            'Ano passado': {'type': 'last_year'},
            'Todo o período': {'type': 'all_time'}
        }

# GraphQL query templates with proper syntax
SHOPIFY_QUERIES = {
    'orders_by_location': '''
    query GetOrdersByLocation($first: Int!, $query: String) {
        orders(first: $first, query: $query) {
            edges {
                node {
                    id
                    name
                    createdAt
                    totalPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    shippingAddress {
                        address1
                        address2
                        city
                        province
                        provinceCode
                        country
                        countryCode
                        zip
                        latitude
                        longitude
                    }
                    billingAddress {
                        address1
                        address2
                        city
                        province
                        provinceCode
                        country
                        countryCode
                        zip
                        latitude
                        longitude
                    }
                    lineItems(first: 10) {
                        edges {
                            node {
                                title
                                quantity
                                originalUnitPriceSet {
                                    shopMoney {
                                        amount
                                        currencyCode
                                    }
                                }
                                product {
                                    id
                                    title
                                    productType
                                    vendor
                                }
                            }
                        }
                    }
                }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
        }
    }
    ''',
    
    'customers_by_location': '''
    query GetCustomersByLocation($first: Int!, $query: String) {
        customers(first: $first, query: $query) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    email
                    createdAt
                    defaultAddress {
                        address1
                        address2
                        city
                        province
                        provinceCode
                        country
                        countryCode
                        zip
                        latitude
                        longitude
                    }
                    addresses(first: 5) {
                        edges {
                            node {
                                address1
                                address2
                                city
                                province
                                provinceCode
                                country
                                countryCode
                                zip
                                latitude
                                longitude
                            }
                        }
                    }
                }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
        }
    }
    ''',
    
    'products_performance': '''
    query GetProductsPerformance($first: Int!) {
        products(first: $first) {
            edges {
                node {
                    id
                    title
                    handle
                    productType
                    vendor
                    createdAt
                    updatedAt
                    totalInventory
                    variants(first: 10) {
                        edges {
                            node {
                                id
                                title
                                price
                                inventoryQuantity
                                sku
                            }
                        }
                    }
                }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
        }
    }
    ''',
    
    'sales_data': '''
    query GetSalesData($first: Int!, $query: String) {
        orders(first: $first, query: $query) {
            pageInfo {
                hasNextPage
                endCursor
            }
            edges {
                node {
                    id
                    name
                    createdAt
                    updatedAt
                    totalPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    customer {
                        id
                        email
                    }
                    lineItems(first: 50) {
                        edges {
                            node {
                                id
                                title
                                quantity
                                originalUnitPriceSet {
                                    shopMoney {
                                        amount
                                        currencyCode
                                    }
                                }
                                discountedUnitPriceSet {
                                    shopMoney {
                                        amount
                                        currencyCode
                                    }
                                }
                                totalDiscountSet {
                                    shopMoney {
                                        amount
                                        currencyCode
                                    }
                                }
                                product {
                                    id
                                    title
                                    handle
                                    productType
                                    vendor
                                }
                                variant {
                                    id
                                    title
                                    sku
                                    priceV2 {
                                        amount
                                        currencyCode
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    '''
}

# Default analysis settings
ANALYSIS_CONFIG = {
    'default_limit': 50,
    'max_limit': 250,
    'supported_countries': ['BR', 'US', 'CA', 'UK', 'AU'],
    'chart_colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
    'map_default_zoom': 6,
    'clustering_distance': 50  # km
}

# Error messages
ERROR_MESSAGES = {
    'no_connection': '❌ Não foi possível conectar ao Shopify. Verifique suas credenciais.',
    'invalid_query': '❌ Consulta GraphQL inválida. Verifique a sintaxe.',
    'rate_limit': '⚠️ Limite de taxa atingido. Aguarde alguns minutos antes de tentar novamente.',
    'no_data': 'ℹ️ Nenhum dado encontrado para os filtros selecionados.',
    'processing_error': '❌ Erro durante o processamento dos dados.',
    'connection_timeout': '⏱️ Timeout na conexão. Tente novamente em alguns minutos.',
    'unauthorized': '🔐 Acesso negado. Verifique suas credenciais do Shopify.'
}