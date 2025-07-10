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
        self.shop_url: Optional[str] = os.getenv('SHOPIFY_SHOP_URL')
        self.access_token: Optional[str] = os.getenv('SHOPIFY_ACCESS_TOKEN')
        self.api_version: str = os.getenv('SHOPIFY_API_VERSION', '2024-01')
        self.timeout: int = int(os.getenv('SHOPIFY_TIMEOUT', '30'))
        
    def is_configured(self) -> bool:
        """Check if Shopify configuration is complete"""
        return bool(self.shop_url and self.access_token)
    
    def get_api_url(self) -> str:
        """Get the Shopify GraphQL API URL"""
        if not self.shop_url:
            raise ValueError("Shopify shop URL not configured")
        return f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
    
    def get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        if not self.access_token:
            raise ValueError("Shopify access token not configured")
        return {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
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