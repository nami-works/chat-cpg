"""
RFMify - Customer Relationship Management Tool
Advanced RFM analysis and customer insights for e-commerce businesses.
"""

__version__ = "1.0.0"
__author__ = "Nami Team"
__description__ = "RFM Analysis Tool"

from .rfmify_core import RFMifyCore
from .shopify_customer_exporter import ShopifyCustomerExporter
from .rfm_analyzer import RFMAnalyzer

__all__ = [
    'RFMifyCore',
    'ShopifyCustomerExporter',
    'RFMAnalyzer'
]
