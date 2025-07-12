import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyConnector:
    """
    Handles Shopify API connections and data fetching with robust error handling,
    rate limiting, and pagination support.
    """
    
    def __init__(self, shop_name: str, access_token: str, api_version: str = "2024-01"):
        """
        Initialize Shopify connector
        
        Args:
            shop_name: Shopify store name (without .myshopify.com)
            access_token: Shopify Admin API access token
            api_version: Shopify API version (default: 2024-01)
        """
        self.shop_name = shop_name
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://{shop_name}.myshopify.com/admin/api/{api_version}"
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting
        self.rate_limit_remaining = 40
        self.rate_limit_reset_time = None
        
        # Set headers
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _handle_rate_limit(self):
        """Handle Shopify API rate limiting"""
        if self.rate_limit_remaining <= 2:
            if self.rate_limit_reset_time:
                sleep_time = max(1, self.rate_limit_reset_time - time.time())
                logger.info(f"Rate limit approaching, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            else:
                # Default wait time if no reset time available
                time.sleep(2)
    
    def _update_rate_limit_info(self, response: requests.Response):
        """Update rate limit information from response headers"""
        if 'X-Shopify-Shop-Api-Call-Limit' in response.headers:
            call_limit = response.headers['X-Shopify-Shop-Api-Call-Limit']
            current_calls, max_calls = map(int, call_limit.split('/'))
            self.rate_limit_remaining = max_calls - current_calls
            
            # Calculate reset time (approximate)
            self.rate_limit_reset_time = time.time() + 1
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """
        Make a request to Shopify API with error handling and rate limiting
        
        Args:
            endpoint: API endpoint (relative to base_url)
            method: HTTP method
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data or None if error
        """
        self._handle_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30
            )
            
            self._update_rate_limit_info(response)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get('Retry-After', 2))
                logger.warning(f"Rate limit exceeded, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return self._make_request(endpoint, method, params, data)
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return None
    
    def get_paginated_data(self, endpoint: str, params: Dict = None, limit: int = 250) -> List[Dict]:
        """
        Fetch all data from a paginated endpoint
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            limit: Number of items per page (max 250)
            
        Returns:
            List of all items
        """
        all_data = []
        page_info = None
        
        if params is None:
            params = {}
        
        params['limit'] = min(limit, 250)
        
        while True:
            if page_info:
                params['page_info'] = page_info
            
            response = self._make_request(endpoint, params=params)
            
            if not response:
                break
            
            # Extract data based on endpoint type
            endpoint_key = endpoint.split('.')[0]  # e.g., 'products' from 'products.json'
            
            if endpoint_key in response:
                data = response[endpoint_key]
                all_data.extend(data)
                
                # Check for pagination
                if len(data) < params['limit']:
                    break
                    
                # Get next page info
                link_header = response.get('link')
                if link_header:
                    # Parse link header for next page
                    page_info = self._parse_link_header(link_header)
                    if not page_info:
                        break
                else:
                    break
            else:
                break
        
        return all_data
    
    def _parse_link_header(self, link_header: str) -> Optional[str]:
        """Parse link header for pagination"""
        if not link_header:
            return None
        
        links = link_header.split(',')
        for link in links:
            if 'rel="next"' in link:
                # Extract page_info from URL
                url_part = link.split(';')[0].strip('<>')
                if 'page_info=' in url_part:
                    return url_part.split('page_info=')[1].split('&')[0]
        
        return None
    
    def get_products(self, **kwargs) -> List[Dict]:
        """Fetch all products"""
        return self.get_paginated_data('products.json', params=kwargs)
    
    def get_orders(self, **kwargs) -> List[Dict]:
        """Fetch all orders"""
        return self.get_paginated_data('orders.json', params=kwargs)
    
    def get_customers(self, **kwargs) -> List[Dict]:
        """Fetch all customers"""
        return self.get_paginated_data('customers.json', params=kwargs)
    
    def get_variants(self, **kwargs) -> List[Dict]:
        """Fetch all product variants"""
        return self.get_paginated_data('variants.json', params=kwargs)
    
    def get_collections(self, **kwargs) -> List[Dict]:
        """Fetch all collections"""
        return self.get_paginated_data('collections.json', params=kwargs)
    
    def get_inventory_levels(self, **kwargs) -> List[Dict]:
        """Fetch inventory levels"""
        return self.get_paginated_data('inventory_levels.json', params=kwargs)
    
    def get_shop_info(self) -> Optional[Dict]:
        """Get shop information"""
        response = self._make_request('shop.json')
        return response.get('shop') if response else None
    
    def test_connection(self) -> bool:
        """Test if connection to Shopify is working"""
        try:
            shop_info = self.get_shop_info()
            return shop_info is not None
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False