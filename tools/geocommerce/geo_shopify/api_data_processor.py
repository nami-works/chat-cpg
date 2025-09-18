import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
import logging
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
import os
import time
import json

class GeocodingService:
    """Enhanced geocoding service with fallback mechanisms"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.nominatim = Nominatim(user_agent="geocommerce-shopify")
        self.google_geocoder = GoogleV3(api_key=self.google_api_key) if self.google_api_key else None
        
        # Cache for geocoding results
        self.cache = {}
        self.load_cache()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_cache(self):
        """Load geocoding cache from file"""
        cache_file = 'geocommerce/geocoding_cache.json'
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load geocoding cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save geocoding cache to file"""
        cache_file = 'geocommerce/geocoding_cache.json'
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save geocoding cache: {e}")
    
    def create_cache_key(self, address_parts: Dict[str, str]) -> str:
        """Create a cache key from address parts"""
        key_parts = []
        for field in ['zip', 'city', 'province', 'country']:
            if address_parts.get(field):
                key_parts.append(str(address_parts[field]).strip().lower())
        return '|'.join(key_parts)
    
    def geocode_address(self, address_parts: Dict[str, str]) -> Tuple[Optional[float], Optional[float]]:
        """Geocode an address with caching and fallback"""
        
        # Check cache first
        cache_key = self.create_cache_key(address_parts)
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            return cached_result.get('lat'), cached_result.get('lng')
        
        # Prepare address string
        address_components = []
        for field in ['address1', 'address2', 'city', 'province', 'zip', 'country']:
            if address_parts.get(field):
                address_components.append(str(address_parts[field]).strip())
        
        address_string = ', '.join(address_components)
        
        lat, lng = None, None
        
        # Try Google Geocoding first (if available)
        if self.google_geocoder:
            try:
                location = self.google_geocoder.geocode(address_string, timeout=10)
                if location:
                    lat, lng = location.latitude, location.longitude
                    self.logger.debug(f"Google geocoded: {address_string} -> {lat}, {lng}")
            except (GeocoderTimedOut, GeocoderQuotaExceeded) as e:
                self.logger.warning(f"Google geocoding failed: {e}")
            except Exception as e:
                self.logger.warning(f"Google geocoding error: {e}")
        
        # Fallback to Nominatim if Google failed
        if lat is None or lng is None:
            try:
                time.sleep(1)  # Respect Nominatim rate limits
                location = self.nominatim.geocode(address_string, timeout=10)
                if location:
                    lat, lng = location.latitude, location.longitude
                    self.logger.debug(f"Nominatim geocoded: {address_string} -> {lat}, {lng}")
            except (GeocoderTimedOut, GeocoderQuotaExceeded) as e:
                self.logger.warning(f"Nominatim geocoding failed: {e}")
            except Exception as e:
                self.logger.warning(f"Nominatim geocoding error: {e}")
        
        # Cache the result (even if None)
        self.cache[cache_key] = {'lat': lat, 'lng': lng}
        
        return lat, lng

class ShopifyDataProcessor:
    """Process Shopify API data into GeoCommerce format"""
    
    def __init__(self):
        self.geocoding_service = GeocodingService()
        self.logger = logging.getLogger(__name__)
    
    def clean_postal_code(self, postal_code: str) -> str:
        """Clean and standardize postal codes"""
        if not postal_code:
            return ''
        
        # Remove spaces and convert to uppercase
        clean_code = re.sub(r'\s+', '', str(postal_code).upper())
        
        # Brazilian postal code format (XXXXX-XXX)
        if re.match(r'^\d{8}$', clean_code):
            clean_code = f"{clean_code[:5]}-{clean_code[5:]}"
        
        return clean_code
    
    def extract_address_info(self, address_data: Dict) -> Dict[str, Any]:
        """Extract and clean address information"""
        if not address_data:
            return {}
        
        # Get coordinates from Shopify if available
        lat = address_data.get('latitude')
        lng = address_data.get('longitude')
        
        address_info = {
            'address1': address_data.get('address1', ''),
            'address2': address_data.get('address2', ''),
            'city': address_data.get('city', ''),
            'province': address_data.get('province', ''),
            'country': address_data.get('country', ''),
            'zip': self.clean_postal_code(address_data.get('zip', '')),
            'latitude': lat,
            'longitude': lng,
            'coordinates_validated': bool(lat and lng)
        }
        
        # Geocode if coordinates are missing
        if not lat or not lng:
            geocoded_lat, geocoded_lng = self.geocoding_service.geocode_address(address_info)
            if geocoded_lat and geocoded_lng:
                address_info['latitude'] = geocoded_lat
                address_info['longitude'] = geocoded_lng
                address_info['coordinates_validated'] = True
        
        return address_info
    
    def process_customers_data(self, customers_data: List[Dict]) -> pd.DataFrame:
        """Process customers data into DataFrame"""
        
        processed_customers = []
        
        for customer in customers_data:
            # Extract basic customer info
            customer_info = {
                'customer_id': customer.get('id', '').replace('gid://shopify/Customer/', ''),
                'email': customer.get('email', ''),
                'first_name': customer.get('firstName', ''),
                'last_name': customer.get('lastName', ''),
                'orders_count': 0,  # Will be calculated from orders data
                'total_spent': 0.0,  # Will be calculated from orders data
                'created_at': customer.get('createdAt', ''),
                'updated_at': customer.get('updatedAt', '')
            }
            
            # Process default address
            default_address = customer.get('defaultAddress')
            if default_address:
                address_info = self.extract_address_info(default_address)
                customer_info.update({
                    'default_address_city': address_info.get('city', ''),
                    'default_address_province': address_info.get('province', ''),
                    'default_address_country': address_info.get('country', ''),
                    'default_address_zip': address_info.get('zip', ''),
                    'default_address_latitude': address_info.get('latitude'),
                    'default_address_longitude': address_info.get('longitude'),
                })
            
            # Process all addresses (create separate row for each address)
            addresses = customer.get('addresses', [])
            if addresses:
                for addr in addresses:
                    addr_info = self.extract_address_info(addr)
                    customer_with_address = customer_info.copy()
                    customer_with_address.update({
                        'address_id': addr.get('id', ''),
                        'city': addr_info.get('city', ''),
                        'province': addr_info.get('province', ''),
                        'country': addr_info.get('country', ''),
                        'zip': addr_info.get('zip', ''),
                        'latitude': addr_info.get('latitude'),
                        'longitude': addr_info.get('longitude'),
                        'address1': addr_info.get('address1', ''),
                        'address2': addr_info.get('address2', ''),
                    })
                    processed_customers.append(customer_with_address)
            else:
                # No addresses, use default address info
                processed_customers.append(customer_info)
        
        df = pd.DataFrame(processed_customers)
        
        # Ensure required columns exist
        required_columns = [
            'customer_id', 'email', 'first_name', 'last_name', 'orders_count', 
            'total_spent', 'city', 'province', 'country', 'zip', 
            'latitude', 'longitude'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Clean and convert data types
        df['orders_count'] = pd.to_numeric(df['orders_count'], errors='coerce').fillna(0)
        df['total_spent'] = pd.to_numeric(df['total_spent'], errors='coerce').fillna(0.0)
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        return df
    
    def process_orders_data(self, orders_data: List[Dict]) -> pd.DataFrame:
        """Process orders data into DataFrame"""
        
        processed_orders = []
        
        for order in orders_data:
            # Extract basic order info
            order_info = {
                'order_id': order.get('id', '').replace('gid://shopify/Order/', ''),
                'total_price': float(order.get('totalPrice', 0)),
                'created_at': order.get('createdAt', ''),
                'updated_at': order.get('updatedAt', ''),
            }
            
            # Customer info
            customer = order.get('customer')
            if customer:
                order_info.update({
                    'customer_id': customer.get('id', '').replace('gid://shopify/Customer/', ''),
                    'customer_email': customer.get('email', '')
                })
            
            # Shipping address
            shipping_address = order.get('shippingAddress')
            if shipping_address:
                addr_info = self.extract_address_info(shipping_address)
                order_info.update({
                    'shipping_city': addr_info.get('city', ''),
                    'shipping_province': addr_info.get('province', ''),
                    'shipping_country': addr_info.get('country', ''),
                    'shipping_zip': addr_info.get('zip', ''),
                    'shipping_latitude': addr_info.get('latitude'),
                    'shipping_longitude': addr_info.get('longitude'),
                    'shipping_address1': addr_info.get('address1', ''),
                    'shipping_address2': addr_info.get('address2', ''),
                })
            
            # Billing address
            billing_address = order.get('billingAddress')
            if billing_address:
                addr_info = self.extract_address_info(billing_address)
                order_info.update({
                    'billing_city': addr_info.get('city', ''),
                    'billing_province': addr_info.get('province', ''),
                    'billing_country': addr_info.get('country', ''),
                    'billing_zip': addr_info.get('zip', ''),
                    'billing_latitude': addr_info.get('latitude'),
                    'billing_longitude': addr_info.get('longitude'),
                })
            
            # Line items
            line_items = order.get('lineItems', {}).get('edges', [])
            if line_items:
                for item_edge in line_items:
                    item = item_edge.get('node', {})
                    order_with_item = order_info.copy()
                    
                    # Get price from variant or originalUnitPrice
                    variant = item.get('variant', {})
                    price = float(variant.get('price', 0)) if variant else float(item.get('originalUnitPrice', 0))
                    
                    order_with_item.update({
                        'line_item_id': item.get('id', ''),
                        'product_title': item.get('title', ''),
                        'quantity': int(item.get('quantity', 0)),
                        'price': price,
                    })
                    processed_orders.append(order_with_item)
            else:
                processed_orders.append(order_info)
        
        df = pd.DataFrame(processed_orders)
        
        # Ensure required columns exist
        required_columns = [
            'order_id', 'total_price', 'created_at', 'customer_id', 
            'shipping_city', 'shipping_province', 'shipping_country', 'shipping_zip',
            'shipping_latitude', 'shipping_longitude'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Clean and convert data types
        df['total_price'] = pd.to_numeric(df['total_price'], errors='coerce').fillna(0.0)
        df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df.get('price', 0), errors='coerce').fillna(0.0)
        df['shipping_latitude'] = pd.to_numeric(df['shipping_latitude'], errors='coerce')
        df['shipping_longitude'] = pd.to_numeric(df['shipping_longitude'], errors='coerce')
        df['billing_latitude'] = pd.to_numeric(df.get('billing_latitude', np.nan), errors='coerce')
        df['billing_longitude'] = pd.to_numeric(df.get('billing_longitude', np.nan), errors='coerce')
        
        # Parse dates
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
        
        return df
    
    def process_sales_data(self, sales_data: List[Dict]) -> pd.DataFrame:
        """Process sales data to match Shopify admin calculations"""
        
        processed_sales = []
        
        for order in sales_data:
            # Extract basic order info
            order_id = order.get('id', '').replace('gid://shopify/Order/', '')
            order_name = order.get('name', '')
            created_at = order.get('createdAt', '')
            
            # Get total order price from totalPriceSet
            total_price_set = order.get('totalPriceSet', {})
            shop_money = total_price_set.get('shopMoney', {})
            order_total = float(shop_money.get('amount', 0))
            
            # Customer info
            customer = order.get('customer', {})
            customer_id = customer.get('id', '').replace('gid://shopify/Customer/', '') if customer else ''
            customer_email = customer.get('email', '') if customer else ''
            
            # Process line items with sales-focused calculations
            line_items = order.get('lineItems', {}).get('edges', [])
            
            if line_items:
                for item_edge in line_items:
                    item = item_edge.get('node', {})
                    
                    # Get quantity
                    quantity = int(item.get('quantity', 0))
                    
                    # Get product info
                    product = item.get('product', {})
                    product_title = product.get('title', item.get('title', ''))
                    
                    # Calculate actual sales price (use discounted price if available, otherwise original)
                    discounted_price_set = item.get('discountedUnitPriceSet', {})
                    original_price_set = item.get('originalUnitPriceSet', {})
                    
                    if discounted_price_set and discounted_price_set.get('shopMoney'):
                        # Use discounted price (actual sales price)
                        unit_price = float(discounted_price_set['shopMoney'].get('amount', 0))
                    elif original_price_set and original_price_set.get('shopMoney'):
                        # Fallback to original price
                        unit_price = float(original_price_set['shopMoney'].get('amount', 0))
                    else:
                        # Final fallback to variant price
                        variant = item.get('variant', {})
                        price_v2 = variant.get('priceV2', {}) if variant else {}
                        unit_price = float(price_v2.get('amount', 0)) if price_v2 else 0
                    
                    # Calculate line item total sales (matches Shopify admin calculation)
                    line_item_total = quantity * unit_price
                    
                    # Get discount information
                    total_discount_set = item.get('totalDiscountSet', {})
                    line_discount = float(total_discount_set.get('shopMoney', {}).get('amount', 0)) if total_discount_set else 0
                    
                    sale_record = {
                        'order_id': order_id,
                        'order_name': order_name,
                        'created_at': created_at,
                        'customer_id': customer_id,
                        'customer_email': customer_email,
                        'order_total': order_total,
                        'line_item_id': item.get('id', ''),
                        'product_title': product_title,
                        'product_id': product.get('id', '').replace('gid://shopify/Product/', '') if product.get('id') else '',
                        'product_handle': product.get('handle', '') if product else '',
                        'product_type': product.get('productType', '') if product else '',
                        'vendor': product.get('vendor', '') if product else '',
                        'variant_id': item.get('variant', {}).get('id', '').replace('gid://shopify/ProductVariant/', '') if item.get('variant') else '',
                        'variant_title': item.get('variant', {}).get('title', '') if item.get('variant') else '',
                        'sku': item.get('variant', {}).get('sku', '') if item.get('variant') else '',
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'line_total': line_item_total,
                        'discount_amount': line_discount,
                        'net_sales': line_item_total - line_discount
                    }
                    processed_sales.append(sale_record)
            else:
                # Order without line items (shouldn't happen, but handle gracefully)
                sale_record = {
                    'order_id': order_id,
                    'order_name': order_name,
                    'created_at': created_at,
                    'customer_id': customer_id,
                    'customer_email': customer_email,
                    'order_total': order_total,
                    'line_item_id': '',
                    'product_title': '',
                    'quantity': 0,
                    'unit_price': 0,
                    'line_total': 0,
                    'discount_amount': 0,
                    'net_sales': 0
                }
                processed_sales.append(sale_record)
        
        df = pd.DataFrame(processed_sales)
        
        # Clean and convert data types
        if not df.empty:
            df['order_total'] = pd.to_numeric(df['order_total'], errors='coerce').fillna(0.0)
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
            df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0.0)
            df['line_total'] = pd.to_numeric(df['line_total'], errors='coerce').fillna(0.0)
            df['discount_amount'] = pd.to_numeric(df['discount_amount'], errors='coerce').fillna(0.0)
            df['net_sales'] = pd.to_numeric(df['net_sales'], errors='coerce').fillna(0.0)
            
            # Parse dates
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            
            # Clean text fields
            df['product_title'] = df['product_title'].fillna('').astype(str)
            df['customer_email'] = df['customer_email'].fillna('').astype(str)
        
        return df
    
    def create_unified_dataset(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Create a unified dataset by merging customers and orders"""
        
        # Calculate customer statistics from orders data
        if not orders_df.empty and 'customer_id' in orders_df.columns:
            customer_stats = orders_df.groupby('customer_id').agg({
                'order_id': 'nunique',  # Count unique orders
                'total_price': 'sum'    # Sum total spent
            }).reset_index()
            customer_stats.columns = ['customer_id', 'orders_count', 'total_spent']
        else:
            customer_stats = pd.DataFrame(columns=['customer_id', 'orders_count', 'total_spent'])
        
        # Merge customers and orders on customer_id
        if not customers_df.empty and not orders_df.empty:
            # Add calculated stats to customers_df
            customers_df = customers_df.merge(customer_stats, on='customer_id', how='left')
            customers_df['orders_count'] = customers_df['orders_count'].fillna(0)
            customers_df['total_spent'] = customers_df['total_spent'].fillna(0.0)
            
            # Rename columns to avoid conflicts
            customers_df = customers_df.rename(columns={
                'city': 'customer_city',
                'province': 'customer_province', 
                'country': 'customer_country',
                'zip': 'customer_zip',
                'latitude': 'customer_latitude',
                'longitude': 'customer_longitude'
            })
            
            unified_df = orders_df.merge(
                customers_df[['customer_id', 'email', 'first_name', 'last_name', 
                            'orders_count', 'total_spent', 'customer_city', 
                            'customer_province', 'customer_country', 'customer_zip',
                            'customer_latitude', 'customer_longitude']],
                on='customer_id',
                how='left'
            )
            
            # Use shipping address as primary location, fallback to customer address
            unified_df['city'] = unified_df['shipping_city'].fillna(unified_df['customer_city'])
            unified_df['province'] = unified_df['shipping_province'].fillna(unified_df['customer_province'])
            unified_df['country'] = unified_df['shipping_country'].fillna(unified_df['customer_country'])
            unified_df['zip'] = unified_df['shipping_zip'].fillna(unified_df['customer_zip'])
            unified_df['latitude'] = unified_df['shipping_latitude'].fillna(unified_df['customer_latitude'])
            unified_df['longitude'] = unified_df['shipping_longitude'].fillna(unified_df['customer_longitude'])
            
        elif not customers_df.empty:
            # If only customers data, add calculated stats
            customers_df = customers_df.merge(customer_stats, on='customer_id', how='left')
            customers_df['orders_count'] = customers_df['orders_count'].fillna(0)
            customers_df['total_spent'] = customers_df['total_spent'].fillna(0.0)
            unified_df = customers_df.copy()
        elif not orders_df.empty:
            unified_df = orders_df.copy()
        else:
            unified_df = pd.DataFrame()
        
        return unified_df
    
    def save_cache(self):
        """Save geocoding cache"""
        self.geocoding_service.save_cache()
    
    def get_stats(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Get processing statistics"""
        
        stats = {
            'customers_processed': len(customers_df) if not customers_df.empty else 0,
            'orders_processed': len(orders_df) if not orders_df.empty else 0,
            'customers_with_coordinates': 0,
            'orders_with_coordinates': 0,
            'unique_cities': 0,
            'unique_provinces': 0,
            'unique_countries': 0,
        }
        
        if not customers_df.empty:
            stats['customers_with_coordinates'] = customers_df[
                customers_df['latitude'].notna() & customers_df['longitude'].notna()
            ].shape[0]
            stats['unique_cities'] = customers_df['city'].nunique()
            stats['unique_provinces'] = customers_df['province'].nunique()
            stats['unique_countries'] = customers_df['country'].nunique()
        
        if not orders_df.empty:
            stats['orders_with_coordinates'] = orders_df[
                orders_df['shipping_latitude'].notna() & orders_df['shipping_longitude'].notna()
            ].shape[0]
        
        return stats