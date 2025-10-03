"""
GeoCommerce Shopify Integration Module

This module provides Shopify integration capabilities for geographic 
commerce analysis and customer insights.
"""

__version__ = "1.0.0"
__author__ = "Nami Team"

# Import key classes and functions with graceful fallback
try:
    from .geocommerce_shopify import GeoCommerceShopifyApp
    from ..context import GEOCOMMERCE_CONTEXT
    
    __all__ = [
        'GeoCommerceShopifyApp',
        'GEOCOMMERCE_CONTEXT'
    ]
except ImportError as e:
    # Handle missing dependencies gracefully
    print(f"Warning: Some geocommerce dependencies are missing: {e}")
    __all__ = []