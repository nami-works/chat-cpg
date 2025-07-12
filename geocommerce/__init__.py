"""
Geocommerce Package - Shopify Data Integration System

This package provides a comprehensive solution for managing Shopify data locally
with automatic daily updates and real-time access to cached data.

Main Components:
- ShopifyConnector: Handles API connections to Shopify
- ShopifyDataManager: Manages local storage and caching
- BackgroundScheduler: Handles automatic daily updates
- ShopifyService: High-level interface for the application

Usage:
    from geocommerce import get_shopify_service
    
    # Initialize the service
    service = get_shopify_service()
    service.initialize("your-shop-name", "your-access-token")
    
    # Get data
    products = service.get_products()
    orders = service.get_orders()
    customers = service.get_customers()
"""

from .shopify_connector import ShopifyConnector
from .shopify_data_manager import ShopifyDataManager
from .background_scheduler import BackgroundScheduler
from .shopify_service import ShopifyService, get_shopify_service

# Version information
__version__ = "1.0.0"
__author__ = "ChatCPG Team"
__email__ = "support@chatcpg.com"

# Export main classes and functions
__all__ = [
    "ShopifyConnector",
    "ShopifyDataManager", 
    "BackgroundScheduler",
    "ShopifyService",
    "get_shopify_service"
]

# Package metadata
__title__ = "geocommerce"
__description__ = "Shopify Data Integration System with Local Storage and Background Updates"
__url__ = "https://github.com/chatcpg/geocommerce"
__license__ = "MIT"