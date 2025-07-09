"""
GeoCommerce - Shopify API Integration

A comprehensive geographic and commercial analysis tool for e-commerce data
with direct Shopify API integration.

Author: GeoCommerce Development Team
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "GeoCommerce Development Team"
__description__ = "Geographic and commercial analysis of e-commerce data with Shopify API integration"

# Main imports
from .config import GeoCommerceConfig
from .shopify_connector import ShopifyGraphQLClient, ShopifyConfig
from .api_data_processor import ShopifyDataProcessor, GeocodingService
from .geocommerce_core import GeoCommerceAnalyzer
from .geocommerce_shopify import GeoCommerceShopifyApp

__all__ = [
    'GeoCommerceConfig',
    'ShopifyGraphQLClient', 
    'ShopifyConfig',
    'ShopifyDataProcessor',
    'GeocodingService',
    'GeoCommerceAnalyzer',
    'GeoCommerceShopifyApp'
]