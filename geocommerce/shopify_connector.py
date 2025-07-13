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
                myshopifyDomain
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
    
    async def fetch_customers_paginated(self, limit: int = 250, cursor: Optional[str] = None, 
                                      updated_since: Optional[datetime] = None,
                                      geo_filters: Optional[Dict] = None) -> Dict:
        """Fetch customers with pagination and geographic filtering"""
        
        # Build the filter query
        filter_parts = []
        
        # Date filter - simplified
        if updated_since:
            # Use a simpler date format that Shopify accepts
            date_str = updated_since.strftime('%Y-%m-%d')
            filter_parts.append(f'updated_at:>={date_str}')
        
        # Geographic filters at API level - simplified approach
        if geo_filters:
            # For now, skip geographic filters at API level to avoid syntax issues
            # These will be applied post-fetch instead
            pass
        
        # Combine filters - Shopify GraphQL uses space-separated filters
        query_filter = " ".join(filter_parts) if filter_parts else ""
        
        # Build the after clause for pagination
        after_clause = f', after: "{cursor}"' if cursor else ""
        
        # Escape quotes in the query filter to prevent GraphQL syntax errors
        query_filter = query_filter.replace('"', '\\"')
        
        query = f"""
        {{
            customers(first: {limit}{after_clause}, query: "{query_filter}") {{
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
                            address1
                            address2
                        }}
                    }}
                }}
            }}
        }}
        """
        
        return await self.execute_query(query)
    
    def _get_country_code(self, country_name: str) -> Optional[str]:
        """Convert country name to ISO country code"""
        country_map = {
            'Brasil': 'BR',
            'Estados Unidos': 'US',
            'Canadá': 'CA',
            'Reino Unido': 'GB',
            'Austrália': 'AU'
        }
        return country_map.get(country_name)
    
    def _get_province_code(self, province_name: str) -> Optional[str]:
        """Convert province/state name to code"""
        # This is a simplified mapping - in production you'd want a comprehensive database
        province_map = {
            # Brazil
            'São Paulo': 'SP',
            'Rio de Janeiro': 'RJ',
            'Minas Gerais': 'MG',
            'Bahia': 'BA',
            'Paraná': 'PR',
            'Rio Grande do Sul': 'RS',
            'Pernambuco': 'PE',
            'Ceará': 'CE',
            'Pará': 'PA',
            'Santa Catarina': 'SC',
            'Goiás': 'GO',
            'Maranhão': 'MA',
            'Paraíba': 'PB',
            'Espírito Santo': 'ES',
            'Piauí': 'PI',
            'Alagoas': 'AL',
            'Tocantins': 'TO',
            'Rio Grande do Norte': 'RN',
            'Acre': 'AC',
            'Rondônia': 'RO',
            'Roraima': 'RR',
            'Amapá': 'AP',
            'Amazonas': 'AM',
            'Mato Grosso': 'MT',
            'Mato Grosso do Sul': 'MS',
            'Sergipe': 'SE',
            'Distrito Federal': 'DF',
            # US States
            'California': 'CA',
            'New York': 'NY',
            'Texas': 'TX',
            'Florida': 'FL',
            'Illinois': 'IL',
            'Pennsylvania': 'PA',
            'Ohio': 'OH',
            'Georgia': 'GA',
            'North Carolina': 'NC',
            'Michigan': 'MI',
            'New Jersey': 'NJ',
            'Virginia': 'VA',
            'Washington': 'WA',
            'Arizona': 'AZ',
            'Massachusetts': 'MA',
            'Tennessee': 'TN',
            'Indiana': 'IN',
            'Missouri': 'MO',
            'Maryland': 'MD',
            'Colorado': 'CO',
            'Minnesota': 'MN',
            'Wisconsin': 'WI',
            'South Carolina': 'SC',
            'Alabama': 'AL',
            'Louisiana': 'LA',
            'Kentucky': 'KY',
            'Oregon': 'OR',
            'Oklahoma': 'OK',
            'Connecticut': 'CT',
            'Utah': 'UT',
            'Iowa': 'IA',
            'Nevada': 'NV',
            'Arkansas': 'AR',
            'Mississippi': 'MS',
            'Kansas': 'KS',
            'West Virginia': 'WV',
            'Nebraska': 'NE',
            'Idaho': 'ID',
            'Hawaii': 'HI',
            'New Hampshire': 'NH',
            'Maine': 'ME',
            'New Mexico': 'NM',
            'Rhode Island': 'RI',
            'Montana': 'MT',
            'Delaware': 'DE',
            'South Dakota': 'SD',
            'North Dakota': 'ND',
            'Alaska': 'AK',
            'Vermont': 'VT',
            'Wyoming': 'WY'
        }
        return province_map.get(province_name)
    
    async def fetch_orders_paginated(self, limit: int = 50, cursor: Optional[str] = None,
                                   created_since: Optional[datetime] = None,
                                   geo_filters: Optional[Dict] = None,
                                   order_filters: Optional[Dict] = None) -> Dict:
        """Fetch orders with pagination and filtering"""
        
        # Build the filter query
        filter_parts = []
        
        # Date filter - simplified
        if created_since:
            # Use a simpler date format that Shopify accepts
            date_str = created_since.strftime('%Y-%m-%d')
            filter_parts.append(f'created_at:>={date_str}')
        
        # Geographic filters at API level - simplified approach
        if geo_filters:
            # For now, skip geographic filters at API level to avoid syntax issues
            # These will be applied post-fetch instead
            pass
        
        # Note: Order value filters are handled post-fetch for better compatibility
        # with Shopify's GraphQL API limitations
        
        # Combine filters - Shopify GraphQL uses space-separated filters
        query_filter = " ".join(filter_parts) if filter_parts else ""
        
        # Build the after clause for pagination
        after_clause = f', after: "{cursor}"' if cursor else ""
        
        # Escape quotes in the query filter to prevent GraphQL syntax errors
        query_filter = query_filter.replace('"', '\\"')
        
        query = f"""
        {{
            orders(first: {limit}{after_clause}, query: "{query_filter}") {{
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
                                    originalUnitPrice
                                    variant {{
                                        id
                                        price
                                    }}
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
                                progress_callback=None, geo_filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch all customers with progress tracking and filtering"""
        all_customers = []
        cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            result = await self.fetch_customers_paginated(
                cursor=cursor, 
                updated_since=updated_since,
                geo_filters=geo_filters
            )
            
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
                             progress_callback=None, geo_filters: Optional[Dict] = None,
                             order_filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch all orders with progress tracking and filtering"""
        all_orders = []
        cursor = None
        page_count = 0
        
        while True:
            page_count += 1
            result = await self.fetch_orders_paginated(
                cursor=cursor, 
                created_since=created_since,
                geo_filters=geo_filters,
                order_filters=order_filters
            )
            
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