# Shopify Local Storage Integration 🛒

A comprehensive local storage system for Shopify data with daily background updates and real-time access.

## Quick Start

### 1. Setup Environment
```bash
# Create .env file
cat > .env << EOF
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_SYNC_TIME=02:00
SHOPIFY_SYNC_ENABLED=true
EOF
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Service
```bash
# Test connection and setup
python run_shopify_service.py init --from-env --test

# Check status
python run_shopify_service.py status
```

### 4. First Data Sync
```bash
# Manual sync to get initial data
python run_shopify_service.py sync --force

# View data summary
python run_shopify_service.py data --details
```

## Integration with Your App

### Option 1: Simple Integration
```python
from geocommerce import get_shopify_service

# Initialize once at startup
service = get_shopify_service()
service.initialize_from_env()

# Use anywhere in your app
products = service.get_products(limit=100)
orders = service.get_orders(limit=50)
customers = service.get_customers()
```

### Option 2: Chat CPG Integration
```python
# Add to your chat_cpg.py
from geocommerce import get_shopify_service

# Initialize at startup
shopify_service = get_shopify_service()
if shopify_service.initialize_from_env():
    st.success("✅ Shopify service initialized")

# Use in chat functions
def get_product_info(product_name):
    products = shopify_service.get_products()
    for product in products:
        if product_name.lower() in product.get('title', '').lower():
            return product
    return None
```

## Key Features

✅ **Daily Auto-Sync**: Updates at 2 AM daily  
✅ **Real-time Access**: Instant data from local cache  
✅ **Background Processing**: Non-blocking operations  
✅ **Error Recovery**: Automatic retry with exponential backoff  
✅ **Data Persistence**: SQLite + JSON backup  
✅ **CLI Management**: Easy monitoring and control  

## CLI Commands

```bash
# Status and monitoring
python run_shopify_service.py status
python run_shopify_service.py data --details
python run_shopify_service.py history

# Data management
python run_shopify_service.py sync --force
python run_shopify_service.py sync --entities products orders

# Configuration
python run_shopify_service.py config --preset production
python run_shopify_service.py config --sync-time 03:00
```

## Data Access Methods

### Get Products
```python
# All products (from cache)
products = service.get_products()

# Limited results
products = service.get_products(limit=50)

# Force fresh data (API call)
products = service.get_products(fresh=True)
```

### Get Orders
```python
# Recent orders
orders = service.get_orders(limit=100)

# All orders
orders = service.get_orders()
```

### Get Customers
```python
# All customers
customers = service.get_customers()

# Limited results
customers = service.get_customers(limit=200)
```

## Configuration

### Environment Variables
- `SHOPIFY_SHOP_NAME`: Your shop name (required)
- `SHOPIFY_ACCESS_TOKEN`: API access token (required)
- `SHOPIFY_SYNC_TIME`: Daily sync time (default: 02:00)
- `SHOPIFY_SYNC_ENABLED`: Enable auto-sync (default: true)
- `SHOPIFY_DATA_DIR`: Data storage directory (default: shopify_data)

### Presets
```bash
# Development: No auto-sync, minimal data
python run_shopify_service.py config --preset development

# Production: Full auto-sync, complete data
python run_shopify_service.py config --preset production

# Testing: Minimal data, no auto-sync
python run_shopify_service.py config --preset testing
```

## Data Storage

### SQLite Database
- `shopify_data/shopify_data.db`
- Structured tables for products, orders, customers, collections
- Optimized for fast queries and analysis

### JSON Cache
- `shopify_data/json_cache/`
- Raw API responses for debugging
- Timestamped files for history
- Automatic cleanup of old files

## Monitoring

### Service Status
```bash
python run_shopify_service.py status
```

Shows:
- Service initialization status
- Data freshness indicators
- Next scheduled sync time
- Background scheduler status

### Data Summary
```bash
python run_shopify_service.py data --details
```

Shows:
- Record counts for each entity
- Recent products and orders
- Data freshness metrics

### Sync History
```bash
python run_shopify_service.py history
```

Shows:
- Recent sync operations
- Success/failure status
- Error messages
- Processing statistics

## Troubleshooting

### Common Issues

1. **Service Not Initializing**
   - Check API credentials in `.env`
   - Verify shop name (without `.myshopify.com`)
   - Ensure API permissions are granted

2. **Sync Failures**
   - Check internet connection
   - Verify API rate limits
   - Review logs in `shopify_sync.log`

3. **Data Not Fresh**
   - Check scheduler status
   - Run manual sync: `python run_shopify_service.py sync --force`
   - Verify sync time configuration

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

- **API Efficiency**: Respects Shopify's 40 requests/second limit
- **Storage**: Optimized SQLite database with indexes
- **Memory**: Minimal footprint with background processing
- **Scalability**: Handles large datasets with pagination

## Security

- Environment variable-based configuration
- Secure API token storage
- Local file system permissions
- No sensitive data in logs

## Files Structure

```
geocommerce/
├── __init__.py                 # Package initialization
├── shopify_connector.py        # API communication
├── shopify_data_manager.py     # Local storage
├── background_scheduler.py     # Auto-sync scheduler
├── shopify_service.py          # High-level interface
├── config.py                   # Configuration management
└── data_utils.py              # Data analysis utilities

run_shopify_service.py          # CLI management tool
shopify_setup.md               # Detailed setup guide
SHOPIFY_LOCAL_STORAGE_SUMMARY.md # Complete implementation summary
```

## Support

For detailed documentation, see:
- `shopify_setup.md` - Complete setup guide
- `SHOPIFY_LOCAL_STORAGE_SUMMARY.md` - Implementation details

The system runs automatically in the background and provides real-time access to your Shopify data without affecting your application's UI or performance.