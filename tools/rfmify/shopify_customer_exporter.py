import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .rfm_analyzer import RFMAnalyzer

logger = logging.getLogger(__name__)

class ShopifyCustomerExporter:
    """Export Shopify customer data in various formats with RFM classification"""
    
    def __init__(self):
        self.rfm_analyzer = RFMAnalyzer()
    
    def export_customers_with_rfm(self, customers_df: pd.DataFrame, 
                                 orders_df: pd.DataFrame, 
                                 format: str = 'CSV') -> bytes:
        """Export customers data with RFM classification"""
        
        logger.info(f"Starting customer export with RFM analysis in {format} format")
        
        # Calculate RFM scores and classification
        customers_with_rfm = self.rfm_analyzer.calculate_rfm_scores(customers_df, orders_df)
        customers_with_rfm = self.rfm_analyzer.classify_rfm_segments(customers_with_rfm)
        
        # Prepare export columns (matching Shopify_clientes_csv.csv structure)
        export_columns = [
            'customer_id', 'first_name', 'last_name', 'email',
            'default_address_city', 'default_address_province', 'default_address_country',
            'default_address_zip', 'default_address_latitude', 'default_address_longitude',
            'total_spent', 'orders_count', 'rfm_segment', 'rfm_score', 'recency_score', 
            'frequency_score', 'monetary_score', 'last_order_date'
        ]
        
        # Filter to available columns
        available_columns = [col for col in export_columns if col in customers_with_rfm.columns]
        export_df = customers_with_rfm[available_columns]
        
        # Rename columns to match Shopify CSV format
        column_mapping = {
            'customer_id': 'Customer ID',
            'first_name': 'First Name', 
            'last_name': 'Last Name',
            'email': 'Email',
            'default_address_city': 'Default Address City',
            'default_address_province': 'Default Address Province Code',
            'default_address_country': 'Default Address Country Code',
            'default_address_zip': 'Default Address Zip',
            'default_address_latitude': 'Default Address Latitude',
            'default_address_longitude': 'Default Address Longitude',
            'total_spent': 'Total Spent',
            'orders_count': 'Total Orders',
            'rfm_segment': 'RFM Group',
            'rfm_score': 'RFM Score',
            'recency_score': 'Recency Score',
            'frequency_score': 'Frequency Score',
            'monetary_score': 'Monetary Score',
            'last_order_date': 'Last Order Date'
        }
        
        # Apply column mapping
        export_df = export_df.rename(columns=column_mapping)
        
        # Export in specified format
        if format.upper() == 'CSV':
            export_data = export_df.to_csv(index=False).encode('utf-8')
        elif format.upper() == 'EXCEL':
            import io
            output = io.BytesIO()
            export_df.to_excel(output, index=False, engine='openpyxl')
            export_data = output.getvalue()
        elif format.upper() == 'JSON':
            export_data = export_df.to_json(orient='records', indent=2).encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Export completed: {len(export_df)} customers in {format} format")
        return export_data
    
    def get_export_summary(self, customers_df: pd.DataFrame, 
                          orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of export data"""
        
        logger.info("Generating export summary")
        
        customers_with_rfm = self.rfm_analyzer.calculate_rfm_scores(customers_df, orders_df)
        customers_with_rfm = self.rfm_analyzer.classify_rfm_segments(customers_with_rfm)
        
        summary = {
            'total_customers': len(customers_with_rfm),
            'customers_with_rfm': customers_with_rfm['rfm_score'].notna().sum(),
            'rfm_summary': self.rfm_analyzer.get_rfm_summary(customers_with_rfm),
            'export_columns': list(customers_with_rfm.columns),
            'data_quality': {
                'complete_addresses': customers_with_rfm['default_address_city'].notna().sum() if 'default_address_city' in customers_with_rfm.columns else 0,
                'complete_coordinates': customers_with_rfm['default_address_latitude'].notna().sum() if 'default_address_latitude' in customers_with_rfm.columns else 0,
                'complete_rfm': customers_with_rfm['rfm_score'].notna().sum()
            }
        }
        
        return summary
    
    def export_shopify_csv_format(self, customers_df: pd.DataFrame, 
                                orders_df: pd.DataFrame) -> bytes:
        """Export customers data in exact Shopify CSV format with RFM group"""
        
        logger.info("Exporting in Shopify CSV format")
        
        # Calculate RFM scores and classification
        customers_with_rfm = self.rfm_analyzer.calculate_rfm_scores(customers_df, orders_df)
        customers_with_rfm = self.rfm_analyzer.classify_rfm_segments(customers_with_rfm)
        
        # Create export DataFrame with columns matching Shopify_clientes_csv.csv
        export_columns = [
            'customer_id', 'first_name', 'last_name', 'email',
            'default_address_city', 'default_address_province', 'default_address_country',
            'default_address_zip', 'default_address_latitude', 'default_address_longitude',
            'total_spent', 'orders_count', 'rfm_segment'
        ]
        
        # Filter to available columns
        available_columns = [col for col in export_columns if col in customers_with_rfm.columns]
        export_df = customers_with_rfm[available_columns]
        
        # Rename columns to match Shopify CSV format exactly
        column_mapping = {
            'customer_id': 'Customer ID',
            'first_name': 'First Name', 
            'last_name': 'Last Name',
            'email': 'Email',
            'default_address_city': 'Default Address City',
            'default_address_province': 'Default Address Province Code',
            'default_address_country': 'Default Address Country Code',
            'default_address_zip': 'Default Address Zip',
            'default_address_latitude': 'Default Address Latitude',
            'default_address_longitude': 'Default Address Longitude',
            'total_spent': 'Total Spent',
            'orders_count': 'Total Orders',
            'rfm_segment': 'RFM Group'
        }
        
        # Apply column mapping
        export_df = export_df.rename(columns=column_mapping)
        
        # Export as CSV
        export_data = export_df.to_csv(index=False).encode('utf-8')
        
        logger.info(f"Shopify CSV export completed: {len(export_df)} customers")
        return export_data
    
    def get_export_filename(self, format: str = 'CSV', prefix: str = 'shopify_customers_rfm') -> str:
        """Generate export filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{format.lower()}"
    
    def validate_export_data(self, customers_df: pd.DataFrame, 
                           orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data before export"""
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'data_quality_score': 0
        }
        
        # Check if dataframes are empty
        if customers_df.empty:
            validation_results['valid'] = False
            validation_results['errors'].append("Customers dataframe is empty")
        
        if orders_df.empty:
            validation_results['warnings'].append("Orders dataframe is empty - RFM analysis will be limited")
        
        # Check required columns
        required_customer_cols = ['customer_id']
        required_order_cols = ['customer_id', 'created_at', 'total_price']
        
        missing_customer_cols = [col for col in required_customer_cols if col not in customers_df.columns]
        if missing_customer_cols:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Missing required customer columns: {missing_customer_cols}")
        
        missing_order_cols = [col for col in required_order_cols if col not in orders_df.columns]
        if missing_order_cols:
            validation_results['warnings'].append(f"Missing order columns for RFM analysis: {missing_order_cols}")
        
        # Calculate data quality score
        if validation_results['valid']:
            # Basic quality checks
            quality_checks = 0
            total_checks = 0
            
            # Check for duplicate customer IDs
            if 'customer_id' in customers_df.columns:
                total_checks += 1
                if customers_df['customer_id'].nunique() == len(customers_df):
                    quality_checks += 1
                else:
                    validation_results['warnings'].append("Duplicate customer IDs found")
            
            # Check for missing values in key columns
            if 'customer_id' in customers_df.columns:
                total_checks += 1
                if customers_df['customer_id'].notna().all():
                    quality_checks += 1
                else:
                    validation_results['warnings'].append("Missing customer IDs found")
            
            if total_checks > 0:
                validation_results['data_quality_score'] = (quality_checks / total_checks) * 100
        
        return validation_results
