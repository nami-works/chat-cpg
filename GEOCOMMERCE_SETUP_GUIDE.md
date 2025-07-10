# GeoCommerce Shopify Integration - Setup Guide

## Overview

This guide helps you set up and resolve issues with the GeoCommerce Shopify integration module. The GeoCommerce system provides geographic analysis capabilities for e-commerce data from Shopify stores.

## 🔧 Fixed Issues

### 1. **NameError: name 'get_function_context' is not defined**
**Status: ✅ RESOLVED**

- **Root Cause**: The geocommerce module was trying to use `get_function_context` without proper import
- **Solution**: Updated `geocommerce/context.py` to properly import the function from the main `chat_cpg` module
- **Files Modified**: 
  - `geocommerce/context.py` - Added proper import path
  - `chat_cpg.py` - Added geocommerce to available functions

### 2. **GraphQL Syntax Error: syntax error, unexpected STRING (" province:"), expecting COLON**
**Status: ✅ RESOLVED**

- **Root Cause**: Malformed GraphQL queries with incorrect filter syntax
- **Solution**: Implemented proper GraphQL query templates with correct syntax
- **Files Created**: 
  - `geocommerce/config.py` - Contains validated GraphQL query templates
  - `geocommerce/shopify_connector.py` - Robust query handling with validation

### 3. **Missing GeoCommerceShopifyApp Class**
**Status: ✅ RESOLVED**

- **Root Cause**: Missing geocommerce module files
- **Solution**: Created complete geocommerce module structure
- **Files Created**:
  - `geocommerce/__init__.py` - Module initialization
  - `geocommerce/geocommerce_shopify.py` - Main application class
  - `geocommerce/context.py` - Context definitions
  - `geocommerce/config.py` - Configuration and query templates
  - `geocommerce/shopify_connector.py` - Shopify API connector

## 📋 Installation Requirements

### Required Python Packages

Add these to your project's `requirements.txt`:

```text
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
requests>=2.28.0
python-dotenv>=1.0.0
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file or set environment variables:

```bash
# Shopify API Configuration
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_private_app_access_token
SHOPIFY_API_VERSION=2024-01
SHOPIFY_TIMEOUT=30
```

### 2. Shopify Private App Setup

1. **Go to Shopify Admin** → Apps → App and sales channel settings
2. **Create Private App**:
   - Name: "GeoCommerce Analytics"
   - Contact email: your-email@domain.com
3. **Configure Admin API permissions**:
   - `read_orders` - Read access to orders
   - `read_customers` - Read access to customers  
   - `read_products` - Read access to products
4. **Copy the Access Token** - Use this as `SHOPIFY_ACCESS_TOKEN`

## 🚀 Usage

### 1. Access GeoCommerce

1. Start your Streamlit app: `streamlit run chat_cpg.py`
2. In the sidebar, select **"GeoCommerce"** from the functions dropdown
3. Click **"Load"** to activate the module

### 2. Configure Shopify Connection

1. Expand the **"Configuração da API"** section
2. Enter your shop URL (without https://): `your-shop.myshopify.com`
3. Enter your private app access token
4. Select API version (default: 2024-01)
5. Click **"Testar e salvar"** to test and save configuration

### 3. Analyze Data

Once connected, you can:

- **Pedidos por Localização**: Analyze orders by geographic location
- **Clientes por Região**: Analyze customer distribution by region
- **Performance de Produtos**: Analyze product performance metrics

## 🛠️ Troubleshooting

### Common Issues

#### Connection Errors

```
❌ Não foi possível conectar ao Shopify. Verifique suas credenciais.
```

**Solutions**:
1. Verify shop URL format (no https://, include .myshopify.com)
2. Check access token is correct and active
3. Ensure private app has required permissions
4. Verify network connectivity

#### GraphQL Errors

```
❌ Consulta GraphQL inválida. Verifique a sintaxe.
```

**Solutions**:
1. The system now includes validated GraphQL queries
2. If this persists, check Shopify API version compatibility
3. Verify the shop supports the requested data fields

#### Rate Limiting

```
⚠️ Limite de taxa atingido. Aguarde alguns minutos antes de tentar novamente.
```

**Solutions**:
1. Wait a few minutes before retrying
2. Reduce the number of records requested
3. The system automatically handles rate limiting

#### Import Errors

```
ImportError: No module named 'plotly'
```

**Solutions**:
1. Install missing dependencies: `pip install plotly pandas`
2. Ensure you're using the correct virtual environment
3. Run `pip install -r requirements.txt`

## 🔍 Advanced Configuration

### Custom Filters

Use Shopify's search syntax for location filters:

```
province:São Paulo
city:Rio de Janeiro
country:Brazil
created_at:>2023-01-01
```

### Query Limits

- **Default**: 50 records
- **Maximum**: 250 records (Shopify limit)
- **Recommended**: Start with smaller limits for testing

### API Rate Limits

The system automatically handles Shopify's rate limits:
- **Bucket Size**: 40 requests
- **Refill Rate**: 2 requests per second
- **Auto-retry**: Built-in with exponential backoff

## 📊 Data Analysis Features

### Geographic Visualization

- **Orders by City**: Bar charts of order distribution
- **Revenue by Province**: Pie charts of revenue breakdown
- **Customer Maps**: Geographic scatter plots with coordinates

### Performance Metrics

- **Product Inventory**: Top products by stock levels
- **Product Types**: Distribution analysis by category
- **Time Series**: Order patterns over time

### Export Options

- **Raw Data**: Downloadable DataFrames
- **Charts**: Interactive Plotly visualizations
- **CSV Export**: For external analysis

## 🔄 Maintenance

### Regular Updates

1. **Monitor API Changes**: Shopify occasionally updates their GraphQL schema
2. **Update Dependencies**: Keep packages current for security
3. **Test Connections**: Regularly verify API connectivity

### Backup Configuration

Store your configuration securely:
- Use environment variables for production
- Keep access tokens secure and rotated
- Document your setup for team members

## 📞 Support

### Logs and Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Error Reporting

When reporting issues, include:
1. Full error traceback
2. Shopify shop configuration (without tokens)
3. Steps to reproduce the problem
4. Expected vs actual behavior

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: All major issues resolved ✅