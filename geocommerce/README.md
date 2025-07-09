# GeoCommerce - Shopify API Integration

A comprehensive geographic and commercial analysis tool for e-commerce data with direct Shopify API integration.

## Features

### 🔗 Shopify API Integration
- Direct connection to Shopify GraphQL Admin API
- Real-time data fetching for customers and orders
- Intelligent rate limiting and error handling
- Incremental updates support

### 🗺️ Geographic Analysis
- Interactive maps with customer distribution
- Heat maps for revenue analysis
- Province and city-based analytics
- Geocoding with multiple providers (Google Maps, Nominatim)

### 👥 Customer Analytics
- Customer segmentation by spending patterns
- RFM-like analysis
- Geographic distribution insights
- Customer lifetime value analysis

### 📦 Order Analytics
- Temporal analysis of orders and revenue
- Order pattern recognition
- Geographic order distribution
- Product performance analysis

### 🎯 Advanced Analytics
- K-Means, DBSCAN, and Hierarchical clustering
- Performance metrics and KPIs
- Comprehensive reporting
- Data export in multiple formats (CSV, Excel, JSON)

### 🚀 Performance Optimizations
- Intelligent caching system
- Streamlit session state management
- Async data processing
- Progress tracking for long operations

## Installation

### 1. Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file in your project root with your Shopify credentials:

```env
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_VERSION=2024-01

# Optional: Google Maps API for enhanced geocoding
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### 3. Shopify App Setup
To use this system, you need a Shopify private app with the following permissions:

**Required Scopes:**
- `read_customers`
- `read_orders`
- `read_products` (optional)

**To create a private app:**
1. Go to your Shopify admin panel
2. Navigate to Settings > Apps and sales channels
3. Click "Develop apps"
4. Create a new app and configure the Admin API scopes
5. Generate API credentials

## Usage

### Running the Application

Run the Streamlit application:

```bash
streamlit run geocommerce/geocommerce_shopify.py
```

Or use the main entry point:

```python
from geocommerce import GeoCommerceShopifyApp

app = GeoCommerceShopifyApp()
app.run()
```

### Application Workflow

1. **Connection Testing**: Test your Shopify API connection
2. **Data Fetching**: Fetch customers and orders from Shopify
3. **Analysis**: Explore various analytics tabs
4. **Export**: Download reports and data

### Key Components

#### Shopify Connector
```python
from geocommerce import ShopifyGraphQLClient

async def fetch_data():
    async with ShopifyGraphQLClient() as client:
        customers = await client.fetch_all_customers()
        orders = await client.fetch_all_orders()
        return customers, orders
```

#### Data Processing
```python
from geocommerce import ShopifyDataProcessor

processor = ShopifyDataProcessor()
customers_df = processor.process_customers_data(customers_data)
orders_df = processor.process_orders_data(orders_data)
```

#### Analysis
```python
from geocommerce import GeoCommerceAnalyzer

analyzer = GeoCommerceAnalyzer()
metrics = analyzer.calculate_basic_metrics(customers_df, orders_df)
map_obj = analyzer.create_geographic_distribution_map(customers_df)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SHOPIFY_SHOP_NAME` | Your Shopify shop name (without .myshopify.com) | Yes |
| `SHOPIFY_ACCESS_TOKEN` | Private app access token | Yes |
| `SHOPIFY_API_VERSION` | Shopify API version (default: 2024-01) | No |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key for enhanced geocoding | No |

### Application Settings

The application can be configured through the `GeoCommerceConfig` class:

```python
from geocommerce import GeoCommerceConfig

config = GeoCommerceConfig()
config.DEFAULT_MAP_ZOOM = 8
config.MAX_EXPORT_ROWS = 50000
```

## Features Overview

### 📈 Overview Tab
- Key business metrics
- Data quality indicators
- Recent activity summary

### 🗺️ Geographic Analysis Tab
- Interactive distribution maps
- Heat maps
- Province and city analytics
- Top performing locations

### 👥 Customer Analysis Tab
- Customer segmentation
- Value distribution
- Customer details table
- Statistics and insights

### 📦 Order Analysis Tab
- Temporal trends
- Order patterns
- Revenue analysis
- Recent orders view

### 🎯 Clustering Tab
- Multiple clustering algorithms
- Geographic and behavioral clustering
- Silhouette score analysis
- Cluster summaries

### 📊 Reports Tab
- Comprehensive summary reports
- JSON export
- Data preview
- Performance metrics

## Data Processing

### Geocoding
The system uses a multi-tier geocoding approach:

1. **Shopify Coordinates**: Uses coordinates provided by Shopify if available
2. **Google Maps API**: Primary geocoding service (if configured)
3. **Nominatim**: Fallback free geocoding service
4. **Caching**: Results are cached to avoid redundant API calls

### Data Schema

**Processed Customer Data:**
- `customer_id`, `email`, `first_name`, `last_name`
- `city`, `province`, `country`, `zip`
- `latitude`, `longitude`
- `total_spent`, `orders_count`
- `created_at`, `updated_at`

**Processed Order Data:**
- `order_id`, `total_price`, `created_at`
- `customer_id`, `customer_email`
- `shipping_city`, `shipping_province`, `shipping_country`
- `shipping_latitude`, `shipping_longitude`
- `product_title`, `quantity`, `price`

## Performance Considerations

### Caching Strategy
- Geocoding results are cached permanently
- Shopify API responses can be cached per session
- Streamlit's `@st.cache_data` for expensive computations

### Rate Limiting
- Shopify API: 40 requests/second (configurable)
- Nominatim: 1 request/second
- Google Maps: Based on your quota

### Memory Management
- Large datasets are processed in chunks
- Export operations are limited to configurable row counts
- Session state is managed efficiently

## Troubleshooting

### Common Issues

**Connection Failed:**
- Verify your `.env` file contains correct credentials
- Check if your Shopify app has the required scopes
- Ensure your access token is valid

**Geocoding Issues:**
- High geocoding failure rates may indicate data quality issues
- Consider enabling Google Maps API for better results
- Check the geocoding cache file for errors

**Performance Issues:**
- Reduce the number of records fetched in one operation
- Clear cache if memory usage is high
- Use incremental updates for large datasets

**Map Display Issues:**
- Ensure `streamlit-folium` is installed
- Check if coordinates are valid
- Verify map tiles are accessible

### Logging
The application uses Python's logging module. Set the log level for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

### Main Classes

- `GeoCommerceShopifyApp`: Main Streamlit application
- `ShopifyGraphQLClient`: Shopify API client
- `ShopifyDataProcessor`: Data transformation utilities
- `GeoCommerceAnalyzer`: Analysis and visualization methods
- `GeoCommerceConfig`: Configuration management

### Key Methods

- `test_connection()`: Test Shopify API connection
- `fetch_all_customers()`: Fetch all customers with pagination
- `fetch_all_orders()`: Fetch all orders with pagination
- `process_customers_data()`: Transform customer data
- `process_orders_data()`: Transform order data
- `create_geographic_distribution_map()`: Generate interactive maps
- `perform_clustering_analysis()`: Run clustering algorithms

## Contributing

When contributing to this project:

1. Follow PEP 8 style guidelines
2. Add type hints to new functions
3. Include docstrings for all public methods
4. Test with various data sizes and edge cases
5. Update this README for new features

## License

This project is developed as part of the GeoCommerce system for e-commerce analytics.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the error logs
3. Verify your Shopify API configuration
4. Test with a smaller dataset first