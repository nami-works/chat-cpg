# Shopify Connector Module

## 🎯 Overview

The **Shopify Connector** module provides a robust, async-ready interface for connecting to the Shopify Admin API. It's designed to be used by various tools in the Nami ecosystem that need Shopify data access.

## ✨ Key Features

### 🔗 **API Integration**
- **GraphQL Support**: Full GraphQL API integration
- **Async Operations**: Non-blocking API calls with asyncio
- **Rate Limiting**: Intelligent rate limiting (40 requests/second)
- **Error Handling**: Comprehensive error handling and retry logic

### 🚀 **Performance Features**
- **Connection Pooling**: Efficient HTTP connection management
- **Request Caching**: Optional response caching
- **Batch Processing**: Support for bulk operations
- **Progress Tracking**: Real-time progress updates for long operations

### 🛡️ **Reliability**
- **Automatic Retries**: Smart retry logic for failed requests
- **Timeout Management**: Configurable request timeouts
- **Rate Limit Respect**: Shopify API rate limit compliance
- **Connection Recovery**: Automatic connection recovery

## 🛠️ Installation

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Environment Setup**
Create a `.env` file with your Shopify credentials:

```env
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01
```

## 🚀 Quick Start

### **Basic Usage**
```python
from shopify_connector import ShopifyGraphQLClient
import asyncio

async def main():
    async with ShopifyGraphQLClient() as client:
        # Test connection
        result = await client.test_connection()
        print(f"Connection: {result['message']}")
        
        # Fetch customers
        customers = await client.fetch_all_customers()
        print(f"Found {len(customers)} customers")

# Run the async function
asyncio.run(main())
```

### **Configuration**
```python
from shopify_connector import ShopifyConfig

# Create custom configuration
config = ShopifyConfig()
config.shop_name = "my-shop"
config.access_token = "my-token"
config.api_version = "2024-01"

# Use custom config
client = ShopifyGraphQLClient(config)
```

## 📊 API Capabilities

### **Customer Operations**
- **Fetch Customers**: Get all customers with pagination
- **Filter by Date**: Get customers updated since specific date
- **Geographic Filtering**: Filter by location criteria
- **Bulk Export**: Export large customer datasets

### **Order Operations**
- **Fetch Orders**: Get all orders with pagination
- **Sales Analysis**: Comprehensive sales data extraction
- **Revenue Calculations**: Accurate revenue metrics
- **Product Performance**: Order line item analysis

### **Data Processing**
- **Pagination Support**: Handle large datasets efficiently
- **Data Validation**: Ensure data quality and completeness
- **Format Conversion**: Convert between data formats
- **Error Recovery**: Handle partial failures gracefully

## 🔧 Configuration Options

### **Environment Variables**
| Variable | Description | Default |
|----------|-------------|---------|
| `SHOPIFY_SHOP_NAME` | Your Shopify shop name | Required |
| `SHOPIFY_ACCESS_TOKEN` | Private app access token | Required |
| `SHOPIFY_API_VERSION` | API version to use | `2024-01` |

### **Client Configuration**
```python
# Custom configuration options
config = ShopifyConfig()
config.timeout = 60                    # Request timeout in seconds
config.max_retries = 5                 # Maximum retry attempts
config.rate_limit_delay = 2            # Delay between requests
```

## 📈 Performance Optimization

### **Rate Limiting Strategy**
- **Automatic Throttling**: Respects Shopify's 40 req/sec limit
- **Smart Delays**: Dynamic delay adjustment based on response times
- **Batch Optimization**: Group requests for better efficiency
- **Progress Tracking**: Real-time progress updates

### **Memory Management**
- **Streaming Processing**: Handle large datasets without memory issues
- **Garbage Collection**: Automatic cleanup of processed data
- **Connection Pooling**: Reuse HTTP connections efficiently
- **Async Processing**: Non-blocking operations

## 🚨 Error Handling

### **Common Error Types**
- **Rate Limiting**: Automatic retry with exponential backoff
- **Network Issues**: Connection timeout and retry logic
- **API Errors**: GraphQL error parsing and reporting
- **Data Validation**: Input validation and error reporting

### **Recovery Strategies**
```python
try:
    customers = await client.fetch_all_customers()
except Exception as e:
    if "rate limit" in str(e).lower():
        print("Rate limited, waiting...")
        await asyncio.sleep(60)
        customers = await client.fetch_all_customers()
    else:
        print(f"Error: {e}")
```

## 🔍 Monitoring & Debugging

### **Logging**
```python
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG)

# Client will log all operations
client = ShopifyGraphQLClient()
```

### **Performance Metrics**
```python
# Get performance information
client = ShopifyGraphQLClient()
# Monitor rate limiting and response times
```

## 🧪 Testing

### **Run Tests**
```bash
# Run all tests
python -m pytest tests/

# Run with async support
python -m pytest tests/ --asyncio-mode=auto

# Run specific test
python -m pytest tests/test_shopify_connector.py
```

### **Test Coverage**
- ✅ Connection management
- ✅ Rate limiting
- ✅ Error handling
- ✅ Data fetching
- ✅ Pagination
- ✅ Async operations

## 🔗 Integration Examples

### **With CRMify**
```python
from shopify_connector import ShopifyGraphQLClient
from crmify import CRMifyCore

async def analyze_shopify_customers():
    async with ShopifyGraphQLClient() as client:
        # Fetch data from Shopify
        customers = await client.fetch_all_customers()
        orders = await client.fetch_all_orders()
        
        # Analyze with CRMify
        crmify = CRMifyCore()
        analysis = crmify.analyze_customer_segments(customers, orders)
        
        return analysis
```

### **With GeoCommerce**
```python
from shopify_connector import ShopifyGraphQLClient
from geocommerce import GeoCommerce

async def analyze_geographic_data():
    async with ShopifyGraphQLClient() as client:
        customers = await client.fetch_all_customers()
        orders = await client.fetch_all_orders()
        
        # Process with GeoCommerce
        geocommerce = GeoCommerce()
        # ... geographic analysis
```

## 📚 API Reference

### **Classes**

#### `ShopifyGraphQLClient`
Main client for Shopify API operations.

**Methods:**
- `test_connection()`: Test API connectivity
- `fetch_all_customers()`: Get all customers
- `fetch_all_orders()`: Get all orders
- `fetch_sales_data()`: Get sales analytics

#### `ShopifyConfig`
Configuration management for Shopify API.

**Properties:**
- `shop_name`: Your Shopify shop name
- `access_token`: Private app access token
- `api_version`: API version to use

#### `RateLimiter`
Intelligent rate limiting for API requests.

**Features:**
- Automatic throttling
- Request queuing
- Dynamic delay adjustment

## 🔮 Future Enhancements

### **Planned Features**
- **Webhook Support**: Real-time data updates
- **Bulk Operations**: Efficient bulk data operations
- **Advanced Filtering**: Complex query building
- **Data Sync**: Incremental data synchronization

### **Integration Opportunities**
- **Real-time Analytics**: Live data streaming
- **Automated Workflows**: Trigger-based operations
- **Multi-shop Support**: Manage multiple stores
- **Advanced Caching**: Intelligent data caching

## 📞 Support

### **Documentation**
- **API Reference**: Complete method documentation
- **Examples**: Code samples and use cases
- **Tutorials**: Step-by-step integration guides
- **Best Practices**: Recommended implementation patterns

### **Troubleshooting**
- **Common Issues**: Frequently encountered problems
- **Debug Guides**: Step-by-step debugging
- **Performance Tips**: Optimization recommendations
- **Error Codes**: Shopify API error explanations

---

**Shopify Connector** - Reliable, fast, and efficient Shopify API integration! 🚀🔗📊
