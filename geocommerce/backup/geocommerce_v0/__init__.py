"""
GeoCommerce - E-commerce Geographic Analysis Platform
Advanced geographic analysis and consumer density mapping for e-commerce businesses.
"""

__version__ = "1.0.0"
__author__ = "Chat CPG Team"
__description__ = "E-commerce Geographic Analysis Platform"

from .geocommerce_core import GeoCommerce
from .config import get_default_config, get_ecommerce_config, get_retail_config, get_startup_config
from .integration import GeoCommerceIntegration

__all__ = [
    'GeoCommerce',
    'GeoCommerceIntegration',
    'get_default_config',
    'get_ecommerce_config', 
    'get_retail_config',
    'get_startup_config'
] 