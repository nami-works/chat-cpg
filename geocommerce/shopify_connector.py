import os
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ShopifyConfig:
    """Configuration for Shopify API connection"""
    shop_name: str
    access_token: str
    api_version: str
    
    @classmethod
    def from_env(cls) -> 'ShopifyConfig':
        """Create config from environment variables"""
        shop_name = os.getenv('SHOPIFY_SHOP_NAME')
        access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
        api_version = os.getenv('SHOPIFY_API_VERSION', '2024-01')
        
        if not shop_name or not access_token:
            raise ValueError("SHOPIFY_SHOP_NAME and SHOPIFY_ACCESS_TOKEN must be set in environment")
        
        return cls(
            shop_name=shop_name,
            access_token=access_token,
            api_version=api_version
        )

class RateLimiter:
    """Rate limiter for Shopify API (40 requests/second)"""
    
    def __init__(self, max_requests: int = 40, time_window: int = 1):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)

class ShopifyGraphQLClient:
    """GraphQL client for Shopify Admin API"""
    
    def __init__(self, config: Optional[ShopifyConfig] = None):
        self.config = config or ShopifyConfig.from_env()
        self.base_url = f"https://{self.config.shop_name}.myshopify.com/admin/api/{self.config.api_version}/graphql.json"
        self.headers = {
            'X-Shopify-Access-Token': self.config.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.rate_limiter = RateLimiter()
        self.session = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query with error handling and rate limiting"""
        await self.rate_limiter.wait_if_needed()
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            async with self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get('Retry-After', 2))
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    return await self.execute_query(query, variables)
                
                response.raise_for_status()
                result = await response.json()
                
                if 'errors' in result:
                    error_messages = [error['message'] for error in result['errors']]
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                return result
                
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP error executing query: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Shopify API"""
        query = """
        {
            shop {
                name
                email
                domain
                currencyCode
                primaryDomain {
                    url
                }
            }
        }
        """
        
        try:
            result = await self.execute_query(query)
            shop_info = result.get('data', {}).get('shop', {})
            return {
                'success': True,
                'shop_info': shop_info,
                'message': f"Successfully connected to {shop_info.get('name', 'Unknown Shop')}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to connect: {str(e)}"
            }
    
    async def fetch_customers_paginated(self, limit: int = 50, cursor: Optional[str] = None, 
                                      updated_since: Optional[datetime] = None) -> Dict:
        """Fetch customers with pagination"""
        
        # Build the updated_at filter if provided
        updated_filter = ""
        if updated_since:
            updated_filter = f'updated_at:>"{updated_since.isoformat()}"'
        
        # Build the after clause for pagination
        after_clause = f', after: "{cursor}"' if cursor else ""
        
        query = f"""
        {{
            customers(first: {limit}{after_clause}, query: "{updated_filter}") {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                edges {{
                    node {{
                        id
                        email
                        firstName
                        lastName
                        ordersCount
                        totalSpent
                        createdAt
                        updatedAt
                        defaultAddress {{
                            id
                            zip
                            city
                            province
                            country
                            latitude
                            longitude
                            coordinatesValidated
                            address1
                            address2
                        }}
                        addresses {{
                            id
                            zip
                            city
                            province
                            country
                            latitude
                            longitude
                            coordinatesValidated
                            address1
                            address2
                        }}
                    }}
                }}
            }}
        }}
        """
        
        return await self.execute_query(query)
    
    async def fetch_orders_paginated(self, limit: int = 50, cursor: Optional[str] = None,
                                   created_since: Optional[datetime] = None) -> Dict:
        """Fetch orders with pagination"""
        
        # Build the created_at filter if provided
        created_filter = ""
        if created_since:
            created_filter = f'created_at:>"{created_since.isoformat()}"'
        
        # Build the after clause for pagination
        after_clause = f', after: "{cursor}"' if cursor else ""
        
        query = f"""
        {{
            orders(first: {limit}{after_clause}, query: "{created_filter}") {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                edges {{
                    node {{
                        id
                        totalPrice
                        createdAt
                        updatedAt
                        customer {{
                            id
                            email
                        }}
                        shippingAddress {{
                            zip
                            city
                            province
                            country
                            latitude
                            longitude
                            address1
                            address2
                        }}
                        billingAddress {{
                            zip
                            city
                            province
                            country
                            latitude
                            longitude
                            address1
                            address2
                        }}
                        lineItems(first: 10) {{
                            edges {{
                                node {{
                                    id
                                    title
                                    quantity
                                    price
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        
        return await self.execute_query(query)
    
    async def fetch_all_customers(self, updated_since: Optional[datetime] = None, 
                                progress_callback=None) -> List[Dict]:
        """Fetch all customers with progress tracking"""
        all_customers = []
        cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            result = await self.fetch_customers_paginated(cursor=cursor, updated_since=updated_since)
            
            customers_data = result.get('data', {}).get('customers', {})
            edges = customers_data.get('edges', [])
            
            customers_batch = [edge['node'] for edge in edges]
            all_customers.extend(customers_batch)
            
            if progress_callback:
                progress_callback(len(all_customers), page_count)
            
            page_info = customers_data.get('pageInfo', {})
            if not page_info.get('hasNextPage', False):
                break
            
            cursor = page_info.get('endCursor')
        
        return all_customers
    
    async def fetch_all_orders(self, created_since: Optional[datetime] = None,
                             progress_callback=None) -> List[Dict]:
        """Fetch all orders with progress tracking"""
        all_orders = []
        cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            result = await self.fetch_orders_paginated(cursor=cursor, created_since=created_since)
            
            orders_data = result.get('data', {}).get('orders', {})
            edges = orders_data.get('edges', [])
            
            orders_batch = [edge['node'] for edge in edges]
            all_orders.extend(orders_batch)
            
            if progress_callback:
                progress_callback(len(all_orders), page_count)
            
            page_info = orders_data.get('pageInfo', {})
            if not page_info.get('hasNextPage', False):
                break
            
            cursor = page_info.get('endCursor')
        
        return all_orders

# Convenience function for synchronous usage
def create_client() -> ShopifyGraphQLClient:
    """Create a Shopify GraphQL client"""
    return ShopifyGraphQLClient()