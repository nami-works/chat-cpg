"""
Shopify Connector Module
Provides Shopify API integration capabilities for various tools.
"""

__version__ = "1.0.0"
__author__ = "Nami Team"
__description__ = "Shopify API Integration Module"

from .shopify_connector import ShopifyGraphQLClient, ShopifyConfig, RateLimiter

__all__ = [
    'ShopifyGraphQLClient',
    'ShopifyConfig', 
    'RateLimiter'
]
