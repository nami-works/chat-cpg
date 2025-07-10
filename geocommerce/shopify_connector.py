"""
Shopify GraphQL connector with robust error handling and query validation
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time

from .config import ShopifyConfig, SHOPIFY_QUERIES, ERROR_MESSAGES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyConnector:
    """
    Robust Shopify GraphQL connector with comprehensive error handling
    """
    
    def __init__(self, config: ShopifyConfig):
        self.config = config
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_remaining = 40  # Shopify default bucket size
        
    def _validate_query(self, query: str) -> bool:
        """
        Validate GraphQL query syntax
        
        Args:
            query: GraphQL query string
            
        Returns:
            bool: True if query appears valid
        """
        # Basic syntax validation
        if not query.strip():
            return False
            
        # Check for balanced braces
        if query.count('{') != query.count('}'):
            logger.error("GraphQL query has unbalanced braces")
            return False
            
        # Check for proper query structure
        query_lower = query.lower().strip()
        if not (query_lower.startswith('query') or query_lower.startswith('mutation')):
            logger.error("GraphQL query must start with 'query' or 'mutation'")
            return False
            
        return True
    
    def _rate_limit_delay(self):
        """Implement rate limiting to respect Shopify's API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Shopify allows 2 requests per second
        min_interval = 0.5
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _handle_api_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle and validate API response
        
        Args:
            response: HTTP response object
            
        Returns:
            Dict with response data
            
        Raises:
            Exception: For various API errors
        """
        # Update rate limit info
        if 'X-Shopify-Shop-Api-Call-Limit' in response.headers:
            limit_info = response.headers['X-Shopify-Shop-Api-Call-Limit']
            used, total = map(int, limit_info.split('/'))
            self.rate_limit_remaining = total - used
            logger.info(f"API calls used: {used}/{total}")
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise Exception(ERROR_MESSAGES['unauthorized'])
        elif response.status_code == 429:
            raise Exception(ERROR_MESSAGES['rate_limit'])
        elif response.status_code == 408:
            raise Exception(ERROR_MESSAGES['connection_timeout'])
        elif response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from Shopify API")
        
        # Handle GraphQL errors
        if 'errors' in data:
            error_messages = []
            for error in data['errors']:
                error_msg = error.get('message', 'Unknown GraphQL error')
                location = error.get('locations', [])
                if location:
                    line = location[0].get('line', 'unknown')
                    column = location[0].get('column', 'unknown')
                    error_msg += f" at line {line}, column {column}"
                error_messages.append(error_msg)
            
            full_error = "GraphQL errors: " + "; ".join(error_messages)
            logger.error(full_error)
            raise Exception(ERROR_MESSAGES['invalid_query'])
        
        return data
    
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query with comprehensive error handling
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Dict with query results
        """
        if not self.config.is_configured():
            raise Exception(ERROR_MESSAGES['no_connection'])
        
        # Validate query syntax
        if not self._validate_query(query):
            raise Exception(ERROR_MESSAGES['invalid_query'])
        
        # Apply rate limiting
        self._rate_limit_delay()
        
        # Prepare request
        payload = {
            'query': query
        }
        if variables:
            payload['variables'] = variables
        
        try:
            logger.info(f"Executing GraphQL query: {query[:100]}...")
            if variables:
                logger.info(f"With variables: {variables}")
            
            response = self.session.post(
                self.config.get_api_url(),
                headers=self.config.get_headers(),
                json=payload,
                timeout=self.config.timeout
            )
            
            return self._handle_api_response(response)
            
        except requests.exceptions.ConnectTimeout:
            logger.error("Connection timeout")
            raise Exception(ERROR_MESSAGES['connection_timeout'])
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            raise Exception(ERROR_MESSAGES['no_connection'])
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def get_orders_by_location(self, limit: int = 50, location_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get orders filtered by location with proper query construction
        
        Args:
            limit: Number of orders to fetch
            location_filter: Optional location filter (e.g., 'province:São Paulo')
            
        Returns:
            Dict with orders data
        """
        query = SHOPIFY_QUERIES['orders_by_location']
        
        variables = {
            'first': min(limit, 250),  # Shopify max limit
            'query': location_filter or ""
        }
        
        return self.execute_query(query, variables)
    
    def get_customers_by_location(self, limit: int = 50, location_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Get customers filtered by location
        
        Args:
            limit: Number of customers to fetch
            location_filter: Optional location filter
            
        Returns:
            Dict with customers data
        """
        query = SHOPIFY_QUERIES['customers_by_location']
        
        variables = {
            'first': min(limit, 250),
            'query': location_filter or ""
        }
        
        return self.execute_query(query, variables)
    
    def get_products_performance(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get products performance data
        
        Args:
            limit: Number of products to fetch
            
        Returns:
            Dict with products data
        """
        query = SHOPIFY_QUERIES['products_performance']
        
        variables = {
            'first': min(limit, 250)
        }
        
        return self.execute_query(query, variables)
    
    def test_connection(self) -> bool:
        """
        Test Shopify API connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Simple query to test connection
            test_query = '''
            query {
                shop {
                    name
                    email
                    myshopifyDomain
                    plan {
                        displayName
                    }
                }
            }
            '''
            
            result = self.execute_query(test_query)
            shop_name = result.get('data', {}).get('shop', {}).get('name', 'Unknown')
            logger.info(f"Successfully connected to Shopify shop: {shop_name}")
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False