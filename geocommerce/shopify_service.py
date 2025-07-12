import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from .shopify_data_manager import ShopifyDataManager
from .background_scheduler import BackgroundScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyService:
    """
    High-level service for Shopify data operations.
    Provides a simple interface for the application to interact with Shopify data.
    """
    
    def __init__(self, data_dir: str = "shopify_data"):
        """
        Initialize Shopify service
        
        Args:
            data_dir: Directory for storing Shopify data
        """
        self.data_dir = data_dir
        self.data_manager = ShopifyDataManager(data_dir)
        self.scheduler = None
        self.is_initialized = False
        
        # Configuration file
        self.config_file = Path(data_dir) / "shopify_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load Shopify configuration"""
        default_config = {
            "shop_name": "",
            "access_token": "",
            "api_version": "2024-01",
            "auto_sync_enabled": True,
            "sync_time": "02:00",
            "cache_expiry_hours": 24
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            else:
                # Create config directory if it doesn't exist
                self.config_file.parent.mkdir(exist_ok=True)
                self.save_config(default_config)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
        
        return default_config
    
    def save_config(self, config: Dict):
        """Save Shopify configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
    
    def initialize(self, shop_name: str, access_token: str, api_version: str = "2024-01") -> bool:
        """
        Initialize Shopify connection and start background services
        
        Args:
            shop_name: Shopify store name
            access_token: API access token
            api_version: API version
            
        Returns:
            True if initialization was successful
        """
        try:
            # Update configuration
            self.config.update({
                "shop_name": shop_name,
                "access_token": access_token,
                "api_version": api_version
            })
            self.save_config(self.config)
            
            # Setup data manager connection
            self.data_manager.setup_shopify_connection(shop_name, access_token, api_version)
            
            # Setup background scheduler
            if self.config.get("auto_sync_enabled", True):
                self.scheduler = BackgroundScheduler(self.data_manager)
                self.scheduler.start()
            
            self.is_initialized = True
            logger.info(f"Shopify service initialized for store: {shop_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Shopify service: {str(e)}")
            return False
    
    def initialize_from_env(self) -> bool:
        """
        Initialize from environment variables
        
        Environment variables expected:
        - SHOPIFY_SHOP_NAME
        - SHOPIFY_ACCESS_TOKEN
        - SHOPIFY_API_VERSION (optional)
        
        Returns:
            True if initialization was successful
        """
        shop_name = os.getenv('SHOPIFY_SHOP_NAME')
        access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        api_version = os.getenv('SHOPIFY_API_VERSION', '2024-01')
        
        if not shop_name or not access_token:
            logger.error("Missing required environment variables: SHOPIFY_SHOP_NAME, SHOPIFY_ACCESS_TOKEN")
            return False
        
        return self.initialize(shop_name, access_token, api_version)
    
    def initialize_from_config(self) -> bool:
        """
        Initialize from stored configuration
        
        Returns:
            True if initialization was successful
        """
        shop_name = self.config.get('shop_name')
        access_token = self.config.get('access_token')
        api_version = self.config.get('api_version', '2024-01')
        
        if not shop_name or not access_token:
            logger.error("Missing shop configuration")
            return False
        
        return self.initialize(shop_name, access_token, api_version)
    
    def ensure_initialized(self) -> bool:
        """
        Ensure service is initialized, try to initialize if not
        
        Returns:
            True if service is initialized
        """
        if self.is_initialized:
            return True
        
        # Try to initialize from config
        if self.initialize_from_config():
            return True
        
        # Try to initialize from environment
        if self.initialize_from_env():
            return True
        
        return False
    
    def get_products(self, limit: int = None, fresh: bool = False) -> List[Dict]:
        """
        Get products data
        
        Args:
            limit: Maximum number of products to return
            fresh: If True, force sync from Shopify
            
        Returns:
            List of product data
        """
        if not self.ensure_initialized():
            return []
        
        if fresh:
            self.data_manager.sync_products(force_update=True)
        
        return self.data_manager.get_products_from_cache(limit)
    
    def get_orders(self, limit: int = None, fresh: bool = False) -> List[Dict]:
        """
        Get orders data
        
        Args:
            limit: Maximum number of orders to return
            fresh: If True, force sync from Shopify
            
        Returns:
            List of order data
        """
        if not self.ensure_initialized():
            return []
        
        if fresh:
            self.data_manager.sync_orders(force_update=True)
        
        return self.data_manager.get_orders_from_cache(limit)
    
    def get_customers(self, limit: int = None, fresh: bool = False) -> List[Dict]:
        """
        Get customers data
        
        Args:
            limit: Maximum number of customers to return
            fresh: If True, force sync from Shopify
            
        Returns:
            List of customer data
        """
        if not self.ensure_initialized():
            return []
        
        if fresh:
            self.data_manager.sync_customers(force_update=True)
        
        return self.data_manager.get_customers_from_cache(limit)
    
    def get_collections(self, limit: int = None, fresh: bool = False) -> List[Dict]:
        """
        Get collections data
        
        Args:
            limit: Maximum number of collections to return
            fresh: If True, force sync from Shopify
            
        Returns:
            List of collection data
        """
        if not self.ensure_initialized():
            return []
        
        if fresh:
            self.data_manager.sync_collections(force_update=True)
        
        return self.data_manager.get_collections_from_cache(limit)
    
    def sync_all_data(self, force: bool = False) -> Dict[str, bool]:
        """
        Sync all data from Shopify
        
        Args:
            force: Force sync even if data is recent
            
        Returns:
            Dictionary with sync results
        """
        if not self.ensure_initialized():
            return {}
        
        return self.data_manager.sync_all_data(force_update=force)
    
    def force_sync_now(self, entities: Optional[List[str]] = None):
        """
        Force immediate sync of specified entities
        
        Args:
            entities: List of entities to sync, or None for all
        """
        if not self.ensure_initialized():
            return
        
        if self.scheduler:
            self.scheduler.force_sync_now(entities)
        else:
            # Run sync directly if no scheduler
            if entities is None:
                entities = ["products", "orders", "customers", "collections"]
            
            for entity in entities:
                if entity == "products":
                    self.data_manager.sync_products(force_update=True)
                elif entity == "orders":
                    self.data_manager.sync_orders(force_update=True)
                elif entity == "customers":
                    self.data_manager.sync_customers(force_update=True)
                elif entity == "collections":
                    self.data_manager.sync_collections(force_update=True)
    
    def get_data_freshness(self) -> Dict[str, Any]:
        """
        Get information about data freshness
        
        Returns:
            Dictionary with freshness information
        """
        if not self.ensure_initialized():
            return {}
        
        return self.data_manager.get_data_freshness()
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """
        Get sync history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of sync history records
        """
        if not self.ensure_initialized():
            return []
        
        return self.data_manager.get_sync_history(limit)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get overall service status
        
        Returns:
            Dictionary with service status information
        """
        status = {
            "is_initialized": self.is_initialized,
            "config": {
                "shop_name": self.config.get("shop_name", ""),
                "auto_sync_enabled": self.config.get("auto_sync_enabled", True),
                "sync_time": self.config.get("sync_time", "02:00")
            },
            "data_freshness": self.get_data_freshness() if self.is_initialized else {},
            "scheduler": None
        }
        
        if self.scheduler:
            status["scheduler"] = self.scheduler.get_status()
        
        return status
    
    def update_config(self, new_config: Dict):
        """
        Update service configuration
        
        Args:
            new_config: New configuration values
        """
        self.config.update(new_config)
        self.save_config(self.config)
        
        # Update scheduler config if it exists
        if self.scheduler and 'auto_sync_enabled' in new_config:
            scheduler_config = {
                "sync_enabled": new_config.get("auto_sync_enabled", True),
                "sync_time": new_config.get("sync_time", "02:00")
            }
            self.scheduler.update_config(scheduler_config)
    
    def stop(self):
        """Stop the service and cleanup resources"""
        if self.scheduler:
            self.scheduler.stop()
        
        self.is_initialized = False
        logger.info("Shopify service stopped")
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        self.stop()

# Global service instance
_shopify_service = None

def get_shopify_service(data_dir: str = "shopify_data") -> ShopifyService:
    """
    Get or create the global Shopify service instance
    
    Args:
        data_dir: Directory for storing Shopify data
        
    Returns:
        ShopifyService instance
    """
    global _shopify_service
    
    if _shopify_service is None:
        _shopify_service = ShopifyService(data_dir)
    
    return _shopify_service