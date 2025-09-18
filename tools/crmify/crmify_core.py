import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .rfm_analyzer import RFMAnalyzer
from .shopify_customer_exporter import ShopifyCustomerExporter

logger = logging.getLogger(__name__)

class RFMifyCore:
    """Core RFM functionality for customer analysis and insights"""
    
    def __init__(self):
        self.rfm_analyzer = RFMAnalyzer()
        self.customer_exporter = ShopifyCustomerExporter()
        
    def analyze_customer_segments(self, customers_df: pd.DataFrame, 
                                orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive customer segmentation analysis"""
        
        logger.info("Starting customer segmentation analysis")
        
        if customers_df.empty:
            return {'error': 'No customer data provided'}
        
        # Calculate RFM scores and segments
        customers_with_rfm = self.rfm_analyzer.calculate_rfm_scores(customers_df, orders_df)
        customers_with_rfm = self.rfm_analyzer.classify_rfm_segments(customers_with_rfm)
        
        # Get RFM summary
        rfm_summary = self.rfm_analyzer.get_rfm_summary(customers_with_rfm)
        
        # Get customer recommendations
        recommendations = self.rfm_analyzer.get_customer_recommendations(customers_with_rfm)
        
        # Segment analysis
        segment_analysis = {}
        for segment in customers_with_rfm['rfm_segment'].unique():
            if pd.notna(segment):
                segment_data = customers_with_rfm[customers_with_rfm['rfm_segment'] == segment]
                segment_analysis[segment] = {
                    'count': len(segment_data),
                    'percentage': (len(segment_data) / len(customers_with_rfm)) * 100,
                    'avg_total_spent': segment_data['total_spent'].mean() if 'total_spent' in segment_data.columns else 0,
                    'avg_orders': segment_data['orders_count'].mean() if 'orders_count' in segment_data.columns else 0
                }
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'total_customers': len(customers_with_rfm),
            'rfm_summary': rfm_summary,
            'segment_analysis': segment_analysis,
            'recommendations': recommendations,
            'data_quality': {
                'customers_with_rfm': rfm_summary.get('customers_with_rfm', 0),
                'rfm_coverage': (rfm_summary.get('customers_with_rfm', 0) / len(customers_with_rfm)) * 100 if len(customers_with_rfm) > 0 else 0
            }
        }
        
        logger.info(f"Customer segmentation analysis completed for {len(customers_with_rfm)} customers")
        return analysis_results
    
    def generate_customer_insights(self, customers_df: pd.DataFrame, 
                                 orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate actionable customer insights"""
        
        logger.info("Generating customer insights")
        
        insights = {
            'timestamp': datetime.now().isoformat(),
            'key_metrics': {},
            'trends': {},
            'opportunities': [],
            'risks': [],
            'recommendations': []
        }
        
        if customers_df.empty:
            return insights
        
        # Key metrics
        if 'total_spent' in customers_df.columns:
            insights['key_metrics']['total_revenue'] = customers_df['total_spent'].sum()
            insights['key_metrics']['avg_customer_value'] = customers_df['total_spent'].mean()
            insights['key_metrics']['median_customer_value'] = customers_df['total_spent'].median()
            insights['key_metrics']['top_customer_value'] = customers_df['total_spent'].max()
        
        if 'orders_count' in customers_df.columns:
            insights['key_metrics']['total_orders'] = customers_df['orders_count'].sum()
            insights['key_metrics']['avg_orders_per_customer'] = customers_df['orders_count'].mean()
        
        # Geographic insights
        if 'default_address_city' in customers_df.columns:
            top_cities = customers_df['default_address_city'].value_counts().head(5)
            insights['key_metrics']['top_cities'] = top_cities.to_dict()
        
        # Customer value distribution
        if 'total_spent' in customers_df.columns:
            value_quartiles = customers_df['total_spent'].quantile([0.25, 0.5, 0.75])
            insights['key_metrics']['value_quartiles'] = {
                'q1': value_quartiles[0.25],
                'median': value_quartiles[0.5],
                'q3': value_quartiles[0.75]
            }
        
        # Opportunities
        if 'total_spent' in customers_df.columns:
            # High-value customers
            high_value_threshold = customers_df['total_spent'].quantile(0.8)
            high_value_customers = customers_df[customers_df['total_spent'] >= high_value_threshold]
            
            if len(high_value_customers) > 0:
                insights['opportunities'].append({
                    'type': 'High-Value Customer Retention',
                    'description': f'Focus on {len(high_value_customers)} high-value customers',
                    'potential_value': high_value_customers['total_spent'].sum(),
                    'action': 'Develop VIP programs and exclusive offers'
                })
            
            # Low-value customers with potential
            low_value_threshold = customers_df['total_spent'].quantile(0.2)
            low_value_customers = customers_df[customers_df['total_spent'] <= low_value_threshold]
            
            if len(low_value_customers) > 0:
                insights['opportunities'].append({
                    'type': 'Customer Development',
                    'description': f'Develop {len(low_value_customers)} low-value customers',
                    'potential_value': len(low_value_customers) * customers_df['total_spent'].mean(),
                    'action': 'Implement upselling and cross-selling strategies'
                })
        
        # Risks
        if 'orders_count' in customers_df.columns:
            # One-time buyers
            one_time_buyers = customers_df[customers_df['orders_count'] == 1]
            if len(one_time_buyers) > 0:
                insights['risks'].append({
                    'type': 'Customer Churn Risk',
                    'description': f'{len(one_time_buyers)} one-time buyers at risk of churn',
                    'risk_level': 'Medium',
                    'mitigation': 'Implement re-engagement campaigns and loyalty programs'
                })
        
        # Recommendations
        insights['recommendations'] = [
            {
                'priority': 'High',
                'action': 'Implement RFM-based segmentation',
                'description': 'Use RFM analysis to create targeted marketing campaigns',
                'expected_impact': 'Improved customer retention and revenue'
            },
            {
                'priority': 'Medium',
                'action': 'Develop customer lifecycle programs',
                'description': 'Create onboarding, engagement, and retention programs',
                'expected_impact': 'Increased customer lifetime value'
            },
            {
                'priority': 'Medium',
                'action': 'Geographic targeting',
                'description': 'Analyze customer distribution and optimize marketing by location',
                'expected_impact': 'Better market penetration and efficiency'
            }
        ]
        
        logger.info(f"Customer insights generated with {len(insights['opportunities'])} opportunities and {len(insights['risks'])} risks")
        return insights
    
    def export_customer_data(self, customers_df: pd.DataFrame, 
                           orders_df: pd.DataFrame, 
                           format: str = 'CSV',
                           include_rfm: bool = True) -> Dict[str, Any]:
        """Export customer data with optional RFM analysis"""
        
        logger.info(f"Exporting customer data in {format} format with RFM: {include_rfm}")
        
        try:
            if include_rfm:
                export_data = self.customer_exporter.export_customers_with_rfm(
                    customers_df, orders_df, format
                )
                filename = self.customer_exporter.get_export_filename(format, 'crmify_customers_rfm')
            else:
                # Export without RFM
                if format.upper() == 'CSV':
                    export_data = customers_df.to_csv(index=False).encode('utf-8')
                elif format.upper() == 'EXCEL':
                    import io
                    output = io.BytesIO()
                    customers_df.to_excel(output, index=False, engine='openpyxl')
                    export_data = output.getvalue()
                elif format.upper() == 'JSON':
                    export_data = customers_df.to_json(orient='records', indent=2).encode('utf-8')
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                filename = f"crmify_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format.lower()}"
            
            # Get export summary
            export_summary = self.customer_exporter.get_export_summary(customers_df, orders_df)
            
            return {
                'success': True,
                'export_data': export_data,
                'filename': filename,
                'format': format,
                'summary': export_summary
            }
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'format': format
            }
    
    def get_customer_dashboard_data(self, customers_df: pd.DataFrame, 
                                  orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Get data for customer dashboard visualization"""
        
        logger.info("Preparing customer dashboard data")
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'charts': {},
            'tables': {}
        }
        
        if customers_df.empty:
            return dashboard_data
        
        # Basic metrics
        dashboard_data['metrics']['total_customers'] = len(customers_df)
        
        if 'total_spent' in customers_df.columns:
            dashboard_data['metrics']['total_revenue'] = customers_df['total_spent'].sum()
            dashboard_data['metrics']['avg_customer_value'] = customers_df['total_spent'].mean()
        
        if 'orders_count' in customers_df.columns:
            dashboard_data['metrics']['total_orders'] = customers_df['orders_count'].sum()
            dashboard_data['metrics']['avg_orders_per_customer'] = customers_df['orders_count'].mean()
        
        # Geographic distribution
        if 'default_address_city' in customers_df.columns:
            city_distribution = customers_df['default_address_city'].value_counts().head(10)
            dashboard_data['charts']['city_distribution'] = {
                'labels': city_distribution.index.tolist(),
                'values': city_distribution.values.tolist()
            }
        
        # Customer value distribution
        if 'total_spent' in customers_df.columns:
            value_bins = [0, 100, 500, 1000, 5000, float('inf')]
            value_labels = ['$0-100', '$100-500', '$500-1K', '$1K-5K', '$5K+']
            
            value_distribution = pd.cut(customers_df['total_spent'], bins=value_bins, labels=value_labels)
            value_counts = value_distribution.value_counts()
            
            dashboard_data['charts']['value_distribution'] = {
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist()
            }
        
        # RFM analysis if available
        try:
            customers_with_rfm = self.rfm_analyzer.calculate_rfm_scores(customers_df, orders_df)
            customers_with_rfm = self.rfm_analyzer.classify_rfm_segments(customers_with_rfm)
            
            if 'rfm_segment' in customers_with_rfm.columns:
                rfm_distribution = customers_with_rfm['rfm_segment'].value_counts()
                dashboard_data['charts']['rfm_distribution'] = {
                    'labels': rfm_distribution.index.tolist(),
                    'values': rfm_distribution.values.tolist()
                }
                
                # RFM segment table
                segment_summary = customers_with_rfm.groupby('rfm_segment').agg({
                    'customer_id': 'count',
                    'total_spent': 'mean' if 'total_spent' in customers_with_rfm.columns else 'count'
                }).reset_index()
                
                dashboard_data['tables']['rfm_segments'] = segment_summary.to_dict('records')
        
        except Exception as e:
            logger.warning(f"RFM analysis failed: {e}")
        
        # Recent customers table
        if 'created_at' in customers_df.columns:
            recent_customers = customers_df.nlargest(10, 'created_at')
            dashboard_data['tables']['recent_customers'] = recent_customers.to_dict('records')
        
        logger.info("Customer dashboard data prepared successfully")
        return dashboard_data
    
    def validate_data(self, customers_df: pd.DataFrame, 
                     orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Validate customer and order data"""
        
        logger.info("Validating customer and order data")
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'data_quality_score': 0
        }
        
        # Validate customers dataframe
        if customers_df.empty:
            validation_results['valid'] = False
            validation_results['errors'].append("Customers dataframe is empty")
        else:
            # Check required columns
            required_customer_cols = ['customer_id']
            missing_customer_cols = [col for col in required_customer_cols if col not in customers_df.columns]
            if missing_customer_cols:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Missing required customer columns: {missing_customer_cols}")
            
            # Check data quality
            if 'customer_id' in customers_df.columns:
                duplicate_ids = customers_df['customer_id'].duplicated().sum()
                if duplicate_ids > 0:
                    validation_results['warnings'].append(f"Found {duplicate_ids} duplicate customer IDs")
                
                missing_ids = customers_df['customer_id'].isna().sum()
                if missing_ids > 0:
                    validation_results['warnings'].append(f"Found {missing_ids} missing customer IDs")
        
        # Validate orders dataframe
        if not orders_df.empty:
            required_order_cols = ['customer_id', 'created_at', 'total_price']
            missing_order_cols = [col for col in required_order_cols if col not in orders_df.columns]
            if missing_order_cols:
                validation_results['warnings'].append(f"Missing order columns for RFM analysis: {missing_order_cols}")
        
        # Calculate data quality score
        quality_checks = 0
        total_checks = 0
        
        if not customers_df.empty:
            total_checks += 1
            if 'customer_id' in customers_df.columns and customers_df['customer_id'].notna().all():
                quality_checks += 1
            
            total_checks += 1
            if 'customer_id' in customers_df.columns and customers_df['customer_id'].nunique() == len(customers_df):
                quality_checks += 1
        
        if total_checks > 0:
            validation_results['data_quality_score'] = (quality_checks / total_checks) * 100
        
        logger.info(f"Data validation completed. Quality score: {validation_results['data_quality_score']}%")
        return validation_results
