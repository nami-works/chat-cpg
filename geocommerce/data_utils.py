"""
Data utility functions for processing and analyzing Shopify data.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def products_to_dataframe(products: List[Dict]) -> pd.DataFrame:
    """
    Convert products list to pandas DataFrame for analysis
    
    Args:
        products: List of product dictionaries
        
    Returns:
        DataFrame with product data
    """
    if not products:
        return pd.DataFrame()
    
    try:
        # Extract key product information
        product_data = []
        for product in products:
            # Basic product info
            product_info = {
                'id': product.get('id'),
                'title': product.get('title'),
                'handle': product.get('handle'),
                'product_type': product.get('product_type'),
                'vendor': product.get('vendor'),
                'status': product.get('status'),
                'created_at': product.get('created_at'),
                'updated_at': product.get('updated_at'),
                'published_at': product.get('published_at'),
                'tags': ','.join(product.get('tags', [])),
                'variant_count': len(product.get('variants', [])),
                'image_count': len(product.get('images', []))
            }
            
            # Get price information from variants
            variants = product.get('variants', [])
            if variants:
                prices = [float(v.get('price', 0)) for v in variants if v.get('price')]
                if prices:
                    product_info['min_price'] = min(prices)
                    product_info['max_price'] = max(prices)
                    product_info['avg_price'] = sum(prices) / len(prices)
                
                # Get inventory information
                inventories = [int(v.get('inventory_quantity', 0)) for v in variants if v.get('inventory_quantity') is not None]
                if inventories:
                    product_info['total_inventory'] = sum(inventories)
                    product_info['min_inventory'] = min(inventories)
                    product_info['max_inventory'] = max(inventories)
            
            product_data.append(product_info)
        
        return pd.DataFrame(product_data)
        
    except Exception as e:
        logger.error(f"Error converting products to DataFrame: {str(e)}")
        return pd.DataFrame()

def orders_to_dataframe(orders: List[Dict]) -> pd.DataFrame:
    """
    Convert orders list to pandas DataFrame for analysis
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        DataFrame with order data
    """
    if not orders:
        return pd.DataFrame()
    
    try:
        order_data = []
        for order in orders:
            order_info = {
                'id': order.get('id'),
                'order_number': order.get('order_number'),
                'email': order.get('email'),
                'created_at': order.get('created_at'),
                'updated_at': order.get('updated_at'),
                'processed_at': order.get('processed_at'),
                'cancelled_at': order.get('cancelled_at'),
                'closed_at': order.get('closed_at'),
                'total_price': float(order.get('total_price', 0)),
                'subtotal_price': float(order.get('subtotal_price', 0)),
                'total_tax': float(order.get('total_tax', 0)),
                'total_discounts': float(order.get('total_discounts', 0)),
                'currency': order.get('currency'),
                'financial_status': order.get('financial_status'),
                'fulfillment_status': order.get('fulfillment_status'),
                'customer_id': order.get('customer', {}).get('id'),
                'line_items_count': len(order.get('line_items', [])),
                'gateway': order.get('gateway'),
                'source_name': order.get('source_name'),
                'tags': ','.join(order.get('tags', []))
            }
            
            # Extract line items information
            line_items = order.get('line_items', [])
            if line_items:
                quantities = [int(item.get('quantity', 0)) for item in line_items]
                order_info['total_quantity'] = sum(quantities)
                order_info['unique_products'] = len(set(item.get('product_id') for item in line_items))
            
            order_data.append(order_info)
        
        return pd.DataFrame(order_data)
        
    except Exception as e:
        logger.error(f"Error converting orders to DataFrame: {str(e)}")
        return pd.DataFrame()

def customers_to_dataframe(customers: List[Dict]) -> pd.DataFrame:
    """
    Convert customers list to pandas DataFrame for analysis
    
    Args:
        customers: List of customer dictionaries
        
    Returns:
        DataFrame with customer data
    """
    if not customers:
        return pd.DataFrame()
    
    try:
        customer_data = []
        for customer in customers:
            customer_info = {
                'id': customer.get('id'),
                'email': customer.get('email'),
                'first_name': customer.get('first_name'),
                'last_name': customer.get('last_name'),
                'created_at': customer.get('created_at'),
                'updated_at': customer.get('updated_at'),
                'last_order_id': customer.get('last_order_id'),
                'last_order_name': customer.get('last_order_name'),
                'orders_count': customer.get('orders_count', 0),
                'state': customer.get('state'),
                'total_spent': float(customer.get('total_spent', 0)),
                'phone': customer.get('phone'),
                'tags': ','.join(customer.get('tags', [])),
                'accepts_marketing': customer.get('accepts_marketing', False),
                'addresses_count': len(customer.get('addresses', []))
            }
            
            # Calculate customer lifetime value metrics
            if customer_info['orders_count'] > 0:
                customer_info['avg_order_value'] = customer_info['total_spent'] / customer_info['orders_count']
            
            customer_data.append(customer_info)
        
        return pd.DataFrame(customer_data)
        
    except Exception as e:
        logger.error(f"Error converting customers to DataFrame: {str(e)}")
        return pd.DataFrame()

def analyze_sales_trends(orders_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze sales trends from orders data
    
    Args:
        orders_df: DataFrame with order data
        
    Returns:
        Dictionary with sales trend analysis
    """
    if orders_df.empty:
        return {}
    
    try:
        # Convert datetime columns
        orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])
        orders_df['date'] = orders_df['created_at'].dt.date
        
        # Daily sales analysis
        daily_sales = orders_df.groupby('date').agg({
            'total_price': ['sum', 'count', 'mean'],
            'total_quantity': 'sum'
        }).flatten()
        
        # Monthly trends
        orders_df['month'] = orders_df['created_at'].dt.to_period('M')
        monthly_sales = orders_df.groupby('month').agg({
            'total_price': ['sum', 'count', 'mean'],
            'total_quantity': 'sum'
        })
        
        # Top products by revenue
        if 'line_items' in orders_df.columns:
            # This would need more complex processing of line_items
            pass
        
        return {
            'total_orders': len(orders_df),
            'total_revenue': orders_df['total_price'].sum(),
            'avg_order_value': orders_df['total_price'].mean(),
            'daily_avg_orders': orders_df.groupby('date')['id'].count().mean(),
            'daily_avg_revenue': orders_df.groupby('date')['total_price'].sum().mean(),
            'top_currencies': orders_df['currency'].value_counts().to_dict(),
            'financial_status_breakdown': orders_df['financial_status'].value_counts().to_dict(),
            'fulfillment_status_breakdown': orders_df['fulfillment_status'].value_counts().to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sales trends: {str(e)}")
        return {}

def analyze_customer_segments(customers_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze customer segments based on RFM (Recency, Frequency, Monetary) analysis
    
    Args:
        customers_df: DataFrame with customer data
        
    Returns:
        Dictionary with customer segment analysis
    """
    if customers_df.empty:
        return {}
    
    try:
        # Basic customer analysis
        analysis = {
            'total_customers': len(customers_df),
            'avg_total_spent': customers_df['total_spent'].mean(),
            'avg_orders_per_customer': customers_df['orders_count'].mean(),
            'customers_with_orders': (customers_df['orders_count'] > 0).sum(),
            'top_states': customers_df['state'].value_counts().head(10).to_dict(),
            'marketing_acceptance_rate': customers_df['accepts_marketing'].mean()
        }
        
        # Customer segmentation based on spending
        customers_df['spending_segment'] = pd.cut(
            customers_df['total_spent'], 
            bins=[0, 50, 200, 500, float('inf')],
            labels=['Low', 'Medium', 'High', 'VIP']
        )
        
        analysis['spending_segments'] = customers_df['spending_segment'].value_counts().to_dict()
        
        # Customer segmentation based on order frequency
        customers_df['frequency_segment'] = pd.cut(
            customers_df['orders_count'],
            bins=[0, 1, 3, 10, float('inf')],
            labels=['One-time', 'Occasional', 'Regular', 'Frequent']
        )
        
        analysis['frequency_segments'] = customers_df['frequency_segment'].value_counts().to_dict()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing customer segments: {str(e)}")
        return {}

def analyze_product_performance(products_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze product performance metrics
    
    Args:
        products_df: DataFrame with product data
        
    Returns:
        Dictionary with product performance analysis
    """
    if products_df.empty:
        return {}
    
    try:
        analysis = {
            'total_products': len(products_df),
            'avg_price': products_df['avg_price'].mean() if 'avg_price' in products_df.columns else 0,
            'price_range': {
                'min': products_df['min_price'].min() if 'min_price' in products_df.columns else 0,
                'max': products_df['max_price'].max() if 'max_price' in products_df.columns else 0
            },
            'product_types': products_df['product_type'].value_counts().to_dict(),
            'vendors': products_df['vendor'].value_counts().to_dict(),
            'status_breakdown': products_df['status'].value_counts().to_dict(),
            'products_with_inventory': (products_df['total_inventory'] > 0).sum() if 'total_inventory' in products_df.columns else 0
        }
        
        # Inventory analysis
        if 'total_inventory' in products_df.columns:
            analysis['inventory_stats'] = {
                'total_inventory': products_df['total_inventory'].sum(),
                'avg_inventory_per_product': products_df['total_inventory'].mean(),
                'out_of_stock_products': (products_df['total_inventory'] == 0).sum(),
                'low_stock_products': (products_df['total_inventory'] <= 10).sum()
            }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing product performance: {str(e)}")
        return {}

def generate_business_insights(products_df: pd.DataFrame, orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive business insights from all data
    
    Args:
        products_df: DataFrame with product data
        orders_df: DataFrame with order data
        customers_df: DataFrame with customer data
        
    Returns:
        Dictionary with business insights
    """
    insights = {
        'generated_at': datetime.now().isoformat(),
        'data_summary': {
            'products_count': len(products_df),
            'orders_count': len(orders_df),
            'customers_count': len(customers_df)
        }
    }
    
    # Add individual analyses
    if not products_df.empty:
        insights['product_analysis'] = analyze_product_performance(products_df)
    
    if not orders_df.empty:
        insights['sales_analysis'] = analyze_sales_trends(orders_df)
    
    if not customers_df.empty:
        insights['customer_analysis'] = analyze_customer_segments(customers_df)
    
    # Cross-analysis insights
    if not orders_df.empty and not customers_df.empty:
        try:
            # Customer lifetime value analysis
            if 'total_spent' in customers_df.columns and 'total_price' in orders_df.columns:
                insights['clv_analysis'] = {
                    'avg_customer_lifetime_value': customers_df['total_spent'].mean(),
                    'top_10_percent_clv': customers_df['total_spent'].quantile(0.9),
                    'customer_retention_rate': (customers_df['orders_count'] > 1).mean()
                }
        except Exception as e:
            logger.error(f"Error in cross-analysis: {str(e)}")
    
    return insights

def export_data_to_csv(data: Dict[str, List[Dict]], output_dir: str = "exports"):
    """
    Export Shopify data to CSV files
    
    Args:
        data: Dictionary with data lists (products, orders, customers, etc.)
        output_dir: Directory to save CSV files
    """
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    for entity_type, entity_data in data.items():
        if not entity_data:
            continue
        
        try:
            if entity_type == 'products':
                df = products_to_dataframe(entity_data)
            elif entity_type == 'orders':
                df = orders_to_dataframe(entity_data)
            elif entity_type == 'customers':
                df = customers_to_dataframe(entity_data)
            else:
                # Generic conversion for other data types
                df = pd.DataFrame(entity_data)
            
            if not df.empty:
                output_file = os.path.join(output_dir, f"{entity_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                df.to_csv(output_file, index=False)
                logger.info(f"Exported {len(df)} {entity_type} records to {output_file}")
        
        except Exception as e:
            logger.error(f"Error exporting {entity_type} to CSV: {str(e)}")

def filter_data_by_date_range(data: List[Dict], date_field: str, start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Filter data by date range
    
    Args:
        data: List of data dictionaries
        date_field: Field name containing the date
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        Filtered list of data
    """
    filtered_data = []
    
    for item in data:
        try:
            item_date = datetime.fromisoformat(item[date_field].replace('Z', '+00:00'))
            if start_date <= item_date <= end_date:
                filtered_data.append(item)
        except (KeyError, ValueError, TypeError):
            continue
    
    return filtered_data

def search_products(products: List[Dict], query: str, fields: List[str] = None) -> List[Dict]:
    """
    Search products by query string
    
    Args:
        products: List of product dictionaries
        query: Search query
        fields: Fields to search in (default: title, tags, product_type, vendor)
        
    Returns:
        List of matching products
    """
    if not query:
        return products
    
    if fields is None:
        fields = ['title', 'tags', 'product_type', 'vendor']
    
    query_lower = query.lower()
    matching_products = []
    
    for product in products:
        for field in fields:
            field_value = product.get(field, '')
            if isinstance(field_value, list):
                field_value = ' '.join(field_value)
            
            if query_lower in str(field_value).lower():
                matching_products.append(product)
                break
    
    return matching_products