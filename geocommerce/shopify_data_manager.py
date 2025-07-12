import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
import threading
from contextlib import contextmanager

from .shopify_connector import ShopifyConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyDataManager:
    """
    Manages local storage and caching of Shopify data with automatic daily updates.
    Provides real-time access to cached data while maintaining data freshness.
    """
    
    def __init__(self, data_dir: str = "shopify_data"):
        """
        Initialize data manager
        
        Args:
            data_dir: Directory to store local data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database setup
        self.db_path = self.data_dir / "shopify_data.db"
        self.init_database()
        
        # JSON cache directory
        self.json_cache_dir = self.data_dir / "json_cache"
        self.json_cache_dir.mkdir(exist_ok=True)
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Last update timestamps
        self.last_update_file = self.data_dir / "last_update.json"
        self.load_last_update_info()
        
        # Shopify connector (will be initialized when needed)
        self.connector = None
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    handle TEXT,
                    product_type TEXT,
                    vendor TEXT,
                    tags TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    published_at TEXT,
                    variants TEXT,
                    options TEXT,
                    images TEXT,
                    data_json TEXT,
                    last_synced TEXT
                )
            ''')
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    order_number TEXT,
                    email TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    cancelled_at TEXT,
                    closed_at TEXT,
                    processed_at TEXT,
                    total_price REAL,
                    subtotal_price REAL,
                    total_tax REAL,
                    currency TEXT,
                    financial_status TEXT,
                    fulfillment_status TEXT,
                    customer_id INTEGER,
                    billing_address TEXT,
                    shipping_address TEXT,
                    line_items TEXT,
                    data_json TEXT,
                    last_synced TEXT
                )
            ''')
            
            # Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    email TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    last_order_id INTEGER,
                    last_order_name TEXT,
                    orders_count INTEGER,
                    state TEXT,
                    total_spent REAL,
                    note TEXT,
                    phone TEXT,
                    addresses TEXT,
                    tags TEXT,
                    data_json TEXT,
                    last_synced TEXT
                )
            ''')
            
            # Collections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collections (
                    id INTEGER PRIMARY KEY,
                    handle TEXT,
                    title TEXT,
                    updated_at TEXT,
                    body_html TEXT,
                    sort_order TEXT,
                    template_suffix TEXT,
                    published_at TEXT,
                    published_scope TEXT,
                    data_json TEXT,
                    last_synced TEXT
                )
            ''')
            
            # Sync history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT,
                    sync_started TEXT,
                    sync_completed TEXT,
                    records_processed INTEGER,
                    status TEXT,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
    
    def load_last_update_info(self):
        """Load last update information from file"""
        try:
            if self.last_update_file.exists():
                with open(self.last_update_file, 'r') as f:
                    self.last_update = json.load(f)
            else:
                self.last_update = {}
        except Exception as e:
            logger.error(f"Error loading last update info: {str(e)}")
            self.last_update = {}
    
    def save_last_update_info(self):
        """Save last update information to file"""
        try:
            with open(self.last_update_file, 'w') as f:
                json.dump(self.last_update, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving last update info: {str(e)}")
    
    def setup_shopify_connection(self, shop_name: str, access_token: str, api_version: str = "2024-01"):
        """
        Setup Shopify connection
        
        Args:
            shop_name: Shopify store name
            access_token: API access token
            api_version: API version
        """
        self.connector = ShopifyConnector(shop_name, access_token, api_version)
        
        # Test connection
        if not self.connector.test_connection():
            raise ConnectionError("Failed to connect to Shopify API")
        
        logger.info(f"Successfully connected to Shopify store: {shop_name}")
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def sync_products(self, force_update: bool = False) -> bool:
        """
        Sync products from Shopify
        
        Args:
            force_update: Force update even if recently synced
            
        Returns:
            True if sync was successful
        """
        if not self.connector:
            logger.error("Shopify connector not initialized")
            return False
        
        entity_type = "products"
        
        # Check if we need to update
        if not force_update and not self._should_update(entity_type):
            logger.info(f"Products are up to date, skipping sync")
            return True
        
        sync_start = datetime.now().isoformat()
        
        try:
            # Record sync start
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sync_history (entity_type, sync_started, status)
                    VALUES (?, ?, ?)
                ''', (entity_type, sync_start, 'in_progress'))
                sync_id = cursor.lastrowid
                conn.commit()
            
            # Fetch products from Shopify
            logger.info("Fetching products from Shopify...")
            products = self.connector.get_products()
            
            if not products:
                logger.warning("No products retrieved from Shopify")
                return False
            
            # Store products in database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing products
                cursor.execute("DELETE FROM products")
                
                # Insert new products
                for product in products:
                    cursor.execute('''
                        INSERT INTO products (
                            id, title, handle, product_type, vendor, tags, status,
                            created_at, updated_at, published_at, variants, options,
                            images, data_json, last_synced
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product.get('id'),
                        product.get('title'),
                        product.get('handle'),
                        product.get('product_type'),
                        product.get('vendor'),
                        ','.join(product.get('tags', [])),
                        product.get('status'),
                        product.get('created_at'),
                        product.get('updated_at'),
                        product.get('published_at'),
                        json.dumps(product.get('variants', [])),
                        json.dumps(product.get('options', [])),
                        json.dumps(product.get('images', [])),
                        json.dumps(product),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
            
            # Save to JSON cache
            self._save_to_json_cache(entity_type, products)
            
            # Update sync history
            sync_end = datetime.now().isoformat()
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET sync_completed = ?, records_processed = ?, status = ?
                    WHERE id = ?
                ''', (sync_end, len(products), 'completed', sync_id))
                conn.commit()
            
            # Update last sync time
            self.last_update[entity_type] = sync_end
            self.save_last_update_info()
            
            logger.info(f"Successfully synced {len(products)} products")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing products: {str(e)}")
            
            # Update sync history with error
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                ''', ('failed', str(e), sync_id))
                conn.commit()
            
            return False
    
    def sync_orders(self, force_update: bool = False, days_back: int = 30) -> bool:
        """
        Sync orders from Shopify
        
        Args:
            force_update: Force update even if recently synced
            days_back: How many days back to fetch orders
            
        Returns:
            True if sync was successful
        """
        if not self.connector:
            logger.error("Shopify connector not initialized")
            return False
        
        entity_type = "orders"
        
        if not force_update and not self._should_update(entity_type):
            logger.info(f"Orders are up to date, skipping sync")
            return True
        
        sync_start = datetime.now().isoformat()
        
        try:
            # Record sync start
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sync_history (entity_type, sync_started, status)
                    VALUES (?, ?, ?)
                ''', (entity_type, sync_start, 'in_progress'))
                sync_id = cursor.lastrowid
                conn.commit()
            
            # Fetch orders from Shopify
            logger.info("Fetching orders from Shopify...")
            
            # Get orders from the last X days
            created_at_min = (datetime.now() - timedelta(days=days_back)).isoformat()
            orders = self.connector.get_orders(created_at_min=created_at_min)
            
            if not orders:
                logger.warning("No orders retrieved from Shopify")
                return False
            
            # Store orders in database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing orders
                cursor.execute("DELETE FROM orders")
                
                # Insert new orders
                for order in orders:
                    cursor.execute('''
                        INSERT INTO orders (
                            id, order_number, email, created_at, updated_at, cancelled_at,
                            closed_at, processed_at, total_price, subtotal_price, total_tax,
                            currency, financial_status, fulfillment_status, customer_id,
                            billing_address, shipping_address, line_items, data_json, last_synced
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        order.get('id'),
                        order.get('order_number'),
                        order.get('email'),
                        order.get('created_at'),
                        order.get('updated_at'),
                        order.get('cancelled_at'),
                        order.get('closed_at'),
                        order.get('processed_at'),
                        float(order.get('total_price', 0)),
                        float(order.get('subtotal_price', 0)),
                        float(order.get('total_tax', 0)),
                        order.get('currency'),
                        order.get('financial_status'),
                        order.get('fulfillment_status'),
                        order.get('customer', {}).get('id'),
                        json.dumps(order.get('billing_address', {})),
                        json.dumps(order.get('shipping_address', {})),
                        json.dumps(order.get('line_items', [])),
                        json.dumps(order),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
            
            # Save to JSON cache
            self._save_to_json_cache(entity_type, orders)
            
            # Update sync history
            sync_end = datetime.now().isoformat()
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET sync_completed = ?, records_processed = ?, status = ?
                    WHERE id = ?
                ''', (sync_end, len(orders), 'completed', sync_id))
                conn.commit()
            
            # Update last sync time
            self.last_update[entity_type] = sync_end
            self.save_last_update_info()
            
            logger.info(f"Successfully synced {len(orders)} orders")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing orders: {str(e)}")
            
            # Update sync history with error
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                ''', ('failed', str(e), sync_id))
                conn.commit()
            
            return False
    
    def sync_customers(self, force_update: bool = False) -> bool:
        """
        Sync customers from Shopify
        
        Args:
            force_update: Force update even if recently synced
            
        Returns:
            True if sync was successful
        """
        if not self.connector:
            logger.error("Shopify connector not initialized")
            return False
        
        entity_type = "customers"
        
        if not force_update and not self._should_update(entity_type):
            logger.info(f"Customers are up to date, skipping sync")
            return True
        
        sync_start = datetime.now().isoformat()
        
        try:
            # Record sync start
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sync_history (entity_type, sync_started, status)
                    VALUES (?, ?, ?)
                ''', (entity_type, sync_start, 'in_progress'))
                sync_id = cursor.lastrowid
                conn.commit()
            
            # Fetch customers from Shopify
            logger.info("Fetching customers from Shopify...")
            customers = self.connector.get_customers()
            
            if not customers:
                logger.warning("No customers retrieved from Shopify")
                return False
            
            # Store customers in database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing customers
                cursor.execute("DELETE FROM customers")
                
                # Insert new customers
                for customer in customers:
                    cursor.execute('''
                        INSERT INTO customers (
                            id, email, first_name, last_name, created_at, updated_at,
                            last_order_id, last_order_name, orders_count, state, total_spent,
                            note, phone, addresses, tags, data_json, last_synced
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        customer.get('id'),
                        customer.get('email'),
                        customer.get('first_name'),
                        customer.get('last_name'),
                        customer.get('created_at'),
                        customer.get('updated_at'),
                        customer.get('last_order_id'),
                        customer.get('last_order_name'),
                        customer.get('orders_count', 0),
                        customer.get('state'),
                        float(customer.get('total_spent', 0)),
                        customer.get('note'),
                        customer.get('phone'),
                        json.dumps(customer.get('addresses', [])),
                        ','.join(customer.get('tags', [])),
                        json.dumps(customer),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
            
            # Save to JSON cache
            self._save_to_json_cache(entity_type, customers)
            
            # Update sync history
            sync_end = datetime.now().isoformat()
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET sync_completed = ?, records_processed = ?, status = ?
                    WHERE id = ?
                ''', (sync_end, len(customers), 'completed', sync_id))
                conn.commit()
            
            # Update last sync time
            self.last_update[entity_type] = sync_end
            self.save_last_update_info()
            
            logger.info(f"Successfully synced {len(customers)} customers")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing customers: {str(e)}")
            
            # Update sync history with error
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                ''', ('failed', str(e), sync_id))
                conn.commit()
            
            return False
    
    def sync_collections(self, force_update: bool = False) -> bool:
        """
        Sync collections from Shopify
        
        Args:
            force_update: Force update even if recently synced
            
        Returns:
            True if sync was successful
        """
        if not self.connector:
            logger.error("Shopify connector not initialized")
            return False
        
        entity_type = "collections"
        
        if not force_update and not self._should_update(entity_type):
            logger.info(f"Collections are up to date, skipping sync")
            return True
        
        sync_start = datetime.now().isoformat()
        
        try:
            # Record sync start
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sync_history (entity_type, sync_started, status)
                    VALUES (?, ?, ?)
                ''', (entity_type, sync_start, 'in_progress'))
                sync_id = cursor.lastrowid
                conn.commit()
            
            # Fetch collections from Shopify
            logger.info("Fetching collections from Shopify...")
            collections = self.connector.get_collections()
            
            if not collections:
                logger.warning("No collections retrieved from Shopify")
                return False
            
            # Store collections in database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing collections
                cursor.execute("DELETE FROM collections")
                
                # Insert new collections
                for collection in collections:
                    cursor.execute('''
                        INSERT INTO collections (
                            id, handle, title, updated_at, body_html, sort_order,
                            template_suffix, published_at, published_scope, data_json, last_synced
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        collection.get('id'),
                        collection.get('handle'),
                        collection.get('title'),
                        collection.get('updated_at'),
                        collection.get('body_html'),
                        collection.get('sort_order'),
                        collection.get('template_suffix'),
                        collection.get('published_at'),
                        collection.get('published_scope'),
                        json.dumps(collection),
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
            
            # Save to JSON cache
            self._save_to_json_cache(entity_type, collections)
            
            # Update sync history
            sync_end = datetime.now().isoformat()
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET sync_completed = ?, records_processed = ?, status = ?
                    WHERE id = ?
                ''', (sync_end, len(collections), 'completed', sync_id))
                conn.commit()
            
            # Update last sync time
            self.last_update[entity_type] = sync_end
            self.save_last_update_info()
            
            logger.info(f"Successfully synced {len(collections)} collections")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing collections: {str(e)}")
            
            # Update sync history with error
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_history 
                    SET status = ?, error_message = ?
                    WHERE id = ?
                ''', ('failed', str(e), sync_id))
                conn.commit()
            
            return False
    
    def sync_all_data(self, force_update: bool = False) -> Dict[str, bool]:
        """
        Sync all data types from Shopify
        
        Args:
            force_update: Force update even if recently synced
            
        Returns:
            Dictionary with sync results for each data type
        """
        results = {}
        
        # Sync in order of dependencies
        results['collections'] = self.sync_collections(force_update)
        results['products'] = self.sync_products(force_update)
        results['customers'] = self.sync_customers(force_update)
        results['orders'] = self.sync_orders(force_update)
        
        return results
    
    def _should_update(self, entity_type: str, max_age_hours: int = 24) -> bool:
        """
        Check if entity should be updated based on last sync time
        
        Args:
            entity_type: Type of entity to check
            max_age_hours: Maximum age in hours before update is needed
            
        Returns:
            True if update is needed
        """
        if entity_type not in self.last_update:
            return True
        
        last_sync = datetime.fromisoformat(self.last_update[entity_type])
        age_hours = (datetime.now() - last_sync).total_seconds() / 3600
        
        return age_hours >= max_age_hours
    
    def _save_to_json_cache(self, entity_type: str, data: List[Dict]):
        """
        Save data to JSON cache file
        
        Args:
            entity_type: Type of entity
            data: Data to save
        """
        try:
            cache_file = self.json_cache_dir / f"{entity_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Also save as latest
            latest_file = self.json_cache_dir / f"{entity_type}_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving to JSON cache: {str(e)}")
    
    def get_products_from_cache(self, limit: int = None) -> List[Dict]:
        """Get products from local cache"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT data_json FROM products ORDER BY updated_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [json.loads(row[0]) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting products from cache: {str(e)}")
            return []
    
    def get_orders_from_cache(self, limit: int = None) -> List[Dict]:
        """Get orders from local cache"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT data_json FROM orders ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [json.loads(row[0]) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting orders from cache: {str(e)}")
            return []
    
    def get_customers_from_cache(self, limit: int = None) -> List[Dict]:
        """Get customers from local cache"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT data_json FROM customers ORDER BY updated_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [json.loads(row[0]) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting customers from cache: {str(e)}")
            return []
    
    def get_collections_from_cache(self, limit: int = None) -> List[Dict]:
        """Get collections from local cache"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT data_json FROM collections ORDER BY updated_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [json.loads(row[0]) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting collections from cache: {str(e)}")
            return []
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """Get sync history"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM sync_history 
                    ORDER BY sync_started DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting sync history: {str(e)}")
            return []
    
    def get_data_freshness(self) -> Dict[str, Any]:
        """Get information about data freshness"""
        freshness_info = {}
        
        for entity_type in ['products', 'orders', 'customers', 'collections']:
            if entity_type in self.last_update:
                last_sync = datetime.fromisoformat(self.last_update[entity_type])
                age_hours = (datetime.now() - last_sync).total_seconds() / 3600
                
                freshness_info[entity_type] = {
                    'last_sync': self.last_update[entity_type],
                    'age_hours': round(age_hours, 2),
                    'needs_update': age_hours >= 24
                }
            else:
                freshness_info[entity_type] = {
                    'last_sync': None,
                    'age_hours': None,
                    'needs_update': True
                }
        
        return freshness_info