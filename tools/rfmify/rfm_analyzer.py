import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class RFMAnalyzer:
    """RFM (Recency, Frequency, Monetary) analysis for customer segmentation"""
    
    def __init__(self):
        self.rfm_segments = {
            'Champions': 'High value, recent, frequent buyers',
            'Loyal Customers': 'High value, frequent, but not recent',
            'At Risk': 'High value, not recent, not frequent',
            "Can't Lose": 'High value, not recent, not frequent',
            'New Customers': 'Recent, low frequency, low value',
            'Promising': 'Recent, low frequency, high value',
            'Need Attention': 'Low value, recent, low frequency',
            'About to Sleep': 'Low value, not recent, low frequency'
        }
    
    def calculate_rfm_scores(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM scores for each customer"""
        
        if orders_df.empty or customers_df.empty:
            logger.warning("Empty dataframes provided for RFM analysis")
            return customers_df
        
        # Group orders by customer to calculate metrics
        customer_metrics = orders_df.groupby('customer_id').agg({
            'created_at': ['max', 'count'],  # Last order date and order count
            'total_price': 'sum'             # Total spent
        }).reset_index()
        
        # Flatten column names
        customer_metrics.columns = ['customer_id', 'last_order_date', 'order_count', 'total_spent']
        
        # Calculate Recency (days since last order)
        customer_metrics['recency_days'] = (
            datetime.now() - customer_metrics['last_order_date']
        ).dt.days
        
        # Calculate RFM scores (1-5 scale)
        customer_metrics['recency_score'] = pd.qcut(
            customer_metrics['recency_days'], 
            q=5, 
            labels=[5, 4, 3, 2, 1]  # Lower days = higher score
        )
        
        customer_metrics['frequency_score'] = pd.qcut(
            customer_metrics['order_count'], 
            q=5, 
            labels=[1, 2, 3, 4, 5]  # Higher count = higher score
        )
        
        customer_metrics['monetary_score'] = pd.qcut(
            customer_metrics['total_spent'], 
            q=5, 
            labels=[1, 2, 3, 4, 5]  # Higher spent = higher score
        )
        
        # Convert scores to numeric
        customer_metrics['recency_score'] = pd.to_numeric(customer_metrics['recency_score'])
        customer_metrics['frequency_score'] = pd.to_numeric(customer_metrics['frequency_score'])
        customer_metrics['monetary_score'] = pd.to_numeric(customer_metrics['monetary_score'])
        
        # Calculate RFM score (combination of all three)
        customer_metrics['rfm_score'] = (
            customer_metrics['recency_score'] * 100 + 
            customer_metrics['frequency_score'] * 10 + 
            customer_metrics['monetary_score']
        )
        
        # Merge back with customers data
        result_df = customers_df.merge(
            customer_metrics[['customer_id', 'recency_score', 'frequency_score', 
                            'monetary_score', 'rfm_score', 'last_order_date', 
                            'order_count', 'total_spent']], 
            on='customer_id', 
            how='left'
        )
        
        logger.info(f"RFM scores calculated for {len(result_df)} customers")
        return result_df
    
    def classify_rfm_segments(self, customers_with_rfm: pd.DataFrame) -> pd.DataFrame:
        """Classify customers into RFM segments"""
        
        if customers_with_rfm.empty:
            logger.warning("Empty dataframe provided for RFM classification")
            return customers_with_rfm
        
        df = customers_with_rfm.copy()
        
        # Define RFM segment rules
        def get_rfm_segment(row):
            r, f, m = row['recency_score'], row['frequency_score'], row['monetary_score']
            
            if pd.isna(r) or pd.isna(f) or pd.isna(m):
                return 'Unknown'
            
            # Champions: High R, F, M (4-5, 4-5, 4-5)
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            
            # Loyal Customers: High F, M, Low R (1-2, 4-5, 4-5)
            elif r <= 2 and f >= 4 and m >= 4:
                return 'Loyal Customers'
            
            # At Risk: Low F, M, Low R (1-2, 1-2, 1-2)
            elif r <= 2 and f <= 2 and m <= 2:
                return 'At Risk'
            
            # Can't Lose: Low R, F, High M (1-2, 1-2, 4-5)
            elif r <= 2 and f <= 2 and m >= 4:
                return "Can't Lose"
            
            # New Customers: High R, Low F, M (4-5, 1-2, 1-2)
            elif r >= 4 and f <= 2 and m <= 2:
                return 'New Customers'
            
            # Promising: High R, Low F, High M (4-5, 1-2, 4-5)
            elif r >= 4 and f <= 2 and m >= 4:
                return 'Promising'
            
            # Need Attention: Low M, High R, Low F (1-2, 4-5, 1-2)
            elif m <= 2 and r >= 4 and f <= 2:
                return 'Need Attention'
            
            # About to Sleep: Low M, Low R, Low F (1-2, 1-2, 1-2)
            elif m <= 2 and r <= 2 and f <= 2:
                return 'About to Sleep'
            
            else:
                return 'Average'
        
        # Apply classification
        df['rfm_segment'] = df.apply(get_rfm_segment, axis=1)
        
        logger.info(f"RFM segments classified for {len(df)} customers")
        return df
    
    def get_rfm_summary(self, customers_with_rfm: pd.DataFrame) -> Dict:
        """Get summary statistics for RFM analysis"""
        
        if customers_with_rfm.empty:
            return {}
        
        summary = {
            'total_customers': len(customers_with_rfm),
            'customers_with_rfm': customers_with_rfm['rfm_score'].notna().sum(),
            'segment_distribution': customers_with_rfm['rfm_segment'].value_counts().to_dict(),
            'avg_rfm_score': customers_with_rfm['rfm_score'].mean(),
            'top_segments': customers_with_rfm['rfm_segment'].value_counts().head(3).to_dict()
        }
        
        return summary
    
    def get_customer_recommendations(self, customers_with_rfm: pd.DataFrame) -> List[Dict]:
        """Get actionable recommendations based on RFM segments"""
        
        recommendations = []
        
        if customers_with_rfm.empty:
            return recommendations
        
        # Champions - Keep them happy
        champions = customers_with_rfm[customers_with_rfm['rfm_segment'] == 'Champions']
        if len(champions) > 0:
            recommendations.append({
                'segment': 'Champions',
                'action': 'VIP Treatment',
                'description': f'Reward {len(champions)} top customers with exclusive offers and early access',
                'priority': 'High',
                'estimated_impact': 'High retention and advocacy'
            })
        
        # At Risk - Re-engage them
        at_risk = customers_with_rfm[customers_with_rfm['rfm_segment'] == 'At Risk']
        if len(at_risk) > 0:
            recommendations.append({
                'segment': 'At Risk',
                'action': 'Re-engagement Campaign',
                'description': f'Reach out to {len(at_risk)} customers with personalized offers',
                'priority': 'High',
                'estimated_impact': 'Prevent churn and recover revenue'
            })
        
        # New Customers - Nurture them
        new_customers = customers_with_rfm[customers_with_rfm['rfm_segment'] == 'New Customers']
        if len(new_customers) > 0:
            recommendations.append({
                'segment': 'New Customers',
                'action': 'Onboarding Program',
                'description': f'Develop {len(new_customers)} new customers with educational content',
                'priority': 'Medium',
                'estimated_impact': 'Increase lifetime value'
            })
        
        return recommendations
