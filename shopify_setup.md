# Shopify Local Storage System - Setup Guide

This guide explains how to set up and use the Shopify local storage system that provides daily background updates and real-time data access.

## Overview

The Shopify local storage system consists of:
- **ShopifyConnector**: Handles API connections with rate limiting and error handling
- **ShopifyDataManager**: Manages local SQLite database and JSON cache
- **BackgroundScheduler**: Runs daily automatic data synchronization
- **ShopifyService**: High-level interface for the application

## Features

✅ **Daily Background Updates**: Automatically syncs data at 2 AM daily  
✅ **Real-time Data Access**: Instant access to cached data  
✅ **Rate Limiting**: Respects Shopify API limits  
✅ **Error Handling**: Robust retry logic and error recovery  
✅ **Data Persistence**: SQLite database + JSON cache  
✅ **Sync History**: Track all synchronization operations  
✅ **Configurable**: Flexible configuration options  

## Installation

### 1. Install Dependencies

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Shopify API Setup

1. **Create a Private App** in your Shopify admin:
   - Go to Settings → Apps and sales channels → Develop apps
   - Create a new app
   - Configure Admin API access scopes:
     - `read_products`
     - `read_orders`
     - `read_customers`
     - `read_inventory`
     - `read_locations`

2. **Get API Credentials**:
   - Copy the **Access Token**
   - Note your **Shop Name** (the part before `.myshopify.com`)

### 3. Environment Configuration

Create a `.env` file in your project root:

```env
# Shopify API Configuration
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01

# Sync Configuration
SHOPIFY_SYNC_TIME=02:00
SHOPIFY_SYNC_ENABLED=true
SHOPIFY_ORDERS_DAYS_BACK=30

# Storage Configuration
SHOPIFY_DATA_DIR=shopify_data
SHOPIFY_CACHE_EXPIRY_HOURS=24
```

## Usage

### Method 1: Command Line Interface

Use the included CLI tool for easy management:

```bash
# Initialize the service
python run_shopify_service.py init --from-env --test

# Check status
python run_shopify_service.py status

# Manual sync
python run_shopify_service.py sync

# View data summary
python run_shopify_service.py data --details

# View sync history
python run_shopify_service.py history

# Configure settings
python run_shopify_service.py config --preset production
```

### Method 2: Python Code Integration

```python
from geocommerce import get_shopify_service

# Initialize service
service = get_shopify_service()

# Option 1: Initialize with credentials
service.initialize("your-shop-name", "your-access-token")

# Option 2: Initialize from environment
service.initialize_from_env()

# Get data (real-time from cache)
products = service.get_products(limit=100)
orders = service.get_orders(limit=50)
customers = service.get_customers()
collections = service.get_collections()

# Force fresh data (triggers API call)
fresh_products = service.get_products(fresh=True)

# Check data freshness
freshness = service.get_data_freshness()
for entity, info in freshness.items():
    print(f"{entity}: {info['age_hours']:.1f}h old")

# Manual sync
sync_results = service.sync_all_data(force=True)
```

### Method 3: Integration with Existing Application

Add this to your existing application:

```python
# In your main application file
from geocommerce import get_shopify_service
import atexit

# Initialize service at startup
shopify_service = get_shopify_service()
shopify_service.initialize_from_env()

# Register cleanup
atexit.register(shopify_service.stop)

# Use in your functions
def get_product_data():
    """Get product data from local cache"""
    return shopify_service.get_products()

def get_recent_orders():
    """Get recent orders from local cache"""
    return shopify_service.get_orders(limit=100)
```

## Configuration Options

### Basic Configuration

```python
from geocommerce import get_shopify_service

service = get_shopify_service()

# Update configuration
service.update_config({
    "sync_time": "03:00",          # Daily sync at 3 AM
    "auto_sync_enabled": True,      # Enable background sync
    "orders_days_back": 60,         # Fetch orders from last 60 days
    "cache_expiry_hours": 12        # Consider data stale after 12 hours
})
```

### Environment Presets

```bash
# Development: No auto-sync, minimal data
python run_shopify_service.py config --preset development

# Production: Full auto-sync, complete data
python run_shopify_service.py config --preset production

# Testing: Minimal data, no auto-sync
python run_shopify_service.py config --preset testing
```

## Data Storage

The system stores data in two formats:

### 1. SQLite Database (`shopify_data/shopify_data.db`)
- Structured storage for fast queries
- Tables: `products`, `orders`, `customers`, `collections`, `sync_history`
- Full-text search capabilities

### 2. JSON Cache (`shopify_data/json_cache/`)
- Raw API response data
- Timestamped files for history
- Latest files for quick access

## Monitoring and Maintenance

### Check Service Status

```bash
python run_shopify_service.py status
```

Output:
```
📊 Shopify Service Status
========================================
Initialized: ✅
Shop Name: your-shop-name
Auto Sync: ✅
Sync Time: 02:00
Scheduler Running: ✅
Next Sync: 2024-01-15T02:00:00

📈 Data Freshness
--------------------
Products: 2.3h ago ✅
Orders: 2.3h ago ✅
Customers: 2.3h ago ✅
Collections: 2.3h ago ✅
```

### View Sync History

```bash
python run_shopify_service.py history
```

### Manual Data Sync

```bash
# Sync all data
python run_shopify_service.py sync

# Sync specific entities
python run_shopify_service.py sync --entities products orders

# Force sync (ignore cache age)
python run_shopify_service.py sync --force
```

## Troubleshooting

### Common Issues

1. **Service Not Initializing**
   - Check API credentials
   - Verify shop name (without `.myshopify.com`)
   - Ensure API permissions are granted

2. **Sync Failures**
   - Check internet connection
   - Verify API rate limits not exceeded
   - Review error logs in `shopify_sync.log`

3. **Data Not Fresh**
   - Check if background scheduler is running
   - Verify sync time configuration
   - Run manual sync to test

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then use the service - you'll see detailed logs
service = get_shopify_service()
service.initialize_from_env()
```

### Log Files

- `shopify_sync.log`: Detailed sync operations
- `shopify_data/last_update.json`: Last sync timestamps
- `shopify_data/sync_history`: Database table with complete history

## Performance Considerations

- **API Rate Limits**: Shopify allows 40 requests per app per store per second
- **Data Volume**: Large stores may take several minutes for full sync
- **Storage**: SQLite database grows with data volume, plan accordingly
- **Memory**: Background scheduler runs in separate thread, minimal impact

## Security

- Store API credentials securely (use environment variables)
- Restrict file system access to data directory
- Regular backup of configuration and data
- Monitor API usage to prevent abuse

## Integration with Chat CPG

The system integrates seamlessly with your existing Chat CPG application:

```python
# In your existing chat_cpg.py or similar
from geocommerce import get_shopify_service

# Initialize during startup
shopify_service = get_shopify_service()
if shopify_service.initialize_from_env():
    print("✅ Shopify service initialized")

# Use in your chat functions
def get_product_info(product_name):
    """Get product information for chat responses"""
    products = shopify_service.get_products()
    for product in products:
        if product_name.lower() in product.get('title', '').lower():
            return product
    return None

# Add to session state for Streamlit
if 'shopify_service' not in st.session_state:
    st.session_state['shopify_service'] = shopify_service
```

## Next Steps

1. **Test the Setup**: Run the CLI commands to verify everything works
2. **Schedule Regular Monitoring**: Set up alerts for sync failures
3. **Customize Configuration**: Adjust sync times and data retention
4. **Integrate with Your App**: Add Shopify data to your existing workflows
5. **Monitor Performance**: Track API usage and sync times

The system is designed to run silently in the background while providing instant access to fresh Shopify data for your applications.