"""
GeoCommerce Integration with Chat CPG
Integration layer to connect GeoCommerce analysis with the Chat CPG system.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geocommerce_core import GeoCommerce
from config import get_default_config

class GeoCommerceIntegration:
    """
    Integration layer between GeoCommerce and Chat CPG
    
    Provides methods to:
    - Analyze customer geography for Chat CPG insights
    - Generate geographic recommendations
    - Identify market opportunities
    - Export data in Chat CPG compatible formats
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize GeoCommerce integration
        
        Args:
            config: Optional configuration dictionary
        """
        self.geocommerce = GeoCommerce(config)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def analyze_for_chat_cpg(self, shopify_data_path: str) -> Dict:
        """
        Perform comprehensive analysis for Chat CPG integration
        
        Args:
            shopify_data_path: Path to Shopify customer export
            
        Returns:
            Dictionary with analysis results formatted for Chat CPG
        """
        print("🔍 Starting GeoCommerce analysis for Chat CPG...")
        
        # Generate comprehensive analysis
        summary = self.geocommerce.generate_comprehensive_report(shopify_data_path)
        
        # Format results for Chat CPG
        chat_cpg_insights = {
            'analysis_timestamp': summary['analysis_timestamp'],
            'geographic_summary': {
                'total_customers': summary['total_customers'],
                'total_revenue': summary['total_revenue'],
                'unique_cities': summary['unique_cities'],
                'unique_ceps': summary['unique_ceps'],
                'avg_order_value': summary['avg_order_value']
            },
            'market_insights': self._generate_market_insights(summary),
            'recommendations': self._generate_recommendations(summary),
            'opportunities': self._identify_opportunities(summary),
            'data_files': self._get_output_files(summary['analysis_timestamp'])
        }
        
        # Save Chat CPG formatted results
        self._save_chat_cpg_results(chat_cpg_insights)
        
        print("✅ GeoCommerce analysis completed for Chat CPG!")
        return chat_cpg_insights
    
    def _generate_market_insights(self, summary: Dict) -> Dict:
        """Generate market insights from analysis summary"""
        insights = {
            'top_performing_cities': [],
            'high_value_clusters': [],
            'density_distribution': {},
            'shopping_mall_performance': {}
        }
        
        # Top performing cities
        if 'top_cities' in summary:
            insights['top_performing_cities'] = summary['top_cities'][:5]
        
        # High-value clusters
        if 'high_value_clusters' in summary:
            insights['high_value_clusters'] = summary['high_value_clusters']
        
        # Density distribution
        if 'density_summary' in summary:
            insights['density_distribution'] = summary['density_summary']
        
        # Shopping mall performance
        if 'shopping_distribution' in summary:
            insights['shopping_mall_performance'] = summary['shopping_distribution']
        
        return insights
    
    def _generate_recommendations(self, summary: Dict) -> List[Dict]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Market expansion recommendations
        if summary.get('unique_cities', 0) < 50:
            recommendations.append({
                'type': 'market_expansion',
                'priority': 'high',
                'title': 'Expand Geographic Reach',
                'description': f'Currently serving {summary.get("unique_cities", 0)} cities. Consider expanding to new markets.',
                'action': 'Identify top 10 cities for expansion based on customer density analysis'
            })
        
        # High-value customer targeting
        if summary.get('high_value_clusters'):
            recommendations.append({
                'type': 'customer_targeting',
                'priority': 'high',
                'title': 'Focus on High-Value Clusters',
                'description': f'Found {len(summary["high_value_clusters"])} high-value customer clusters near shopping malls.',
                'action': 'Develop targeted marketing campaigns for these geographic areas'
            })
        
        # Revenue optimization
        avg_order = summary.get('avg_order_value', 0)
        if avg_order < 200:
            recommendations.append({
                'type': 'revenue_optimization',
                'priority': 'medium',
                'title': 'Increase Average Order Value',
                'description': f'Current average order value is R$ {avg_order:.2f}.',
                'action': 'Implement upselling strategies and bundle offers'
            })
        
        # Geographic density optimization
        density_summary = summary.get('density_summary', {})
        if density_summary.get('low_density_areas', 0) > density_summary.get('high_density_areas', 0):
            recommendations.append({
                'type': 'geographic_optimization',
                'priority': 'medium',
                'title': 'Optimize Geographic Distribution',
                'description': 'More low-density areas than high-density areas detected.',
                'action': 'Focus marketing efforts on high-density areas and improve penetration'
            })
        
        return recommendations
    
    def _identify_opportunities(self, summary: Dict) -> List[Dict]:
        """Identify market opportunities based on analysis"""
        opportunities = []
        
        # Underserved areas
        if 'density_summary' in summary:
            low_density = summary['density_summary'].get('low_density_areas', 0)
            if low_density > 0:
                opportunities.append({
                    'type': 'underserved_markets',
                    'potential': 'high',
                    'title': 'Underserved Geographic Areas',
                    'description': f'{low_density} areas with low customer density identified.',
                    'value_estimate': f'Potential {low_density * 100} new customers',
                    'action': 'Develop market penetration strategies for these areas'
                })
        
        # Shopping mall proximity opportunities
        if 'shopping_distribution' in summary:
            shopping_data = summary['shopping_distribution']
            if len(shopping_data) > 0:
                # Find shopping malls with fewer customers
                min_customers = min(shopping_data.values())
                min_shopping = min(shopping_data, key=shopping_data.get)
                
                opportunities.append({
                    'type': 'shopping_mall_opportunity',
                    'potential': 'medium',
                    'title': f'Expand Near {min_shopping}',
                    'description': f'Only {min_customers} customers near {min_shopping}.',
                    'value_estimate': f'Potential 50-100 new customers',
                    'action': f'Develop targeted campaigns for {min_shopping} area'
                })
        
        # High-value customer opportunities
        if 'high_value_clusters' in summary:
            clusters = summary['high_value_clusters']
            if clusters:
                total_high_value = sum(cluster.get('high_value_customers', 0) for cluster in clusters)
                opportunities.append({
                    'type': 'high_value_expansion',
                    'potential': 'high',
                    'title': 'High-Value Customer Expansion',
                    'description': f'{total_high_value} high-value customers identified in clusters.',
                    'value_estimate': f'Potential R$ {total_high_value * 500:.2f} additional revenue',
                    'action': 'Develop VIP programs and exclusive offers for these customers'
                })
        
        return opportunities
    
    def _get_output_files(self, timestamp: str) -> Dict:
        """Get paths to generated output files"""
        output_dir = os.path.join(self.base_dir, 'output')
        
        files = {
            'processed_data': os.path.join(output_dir, f'shopify_processed_{timestamp}.csv'),
            'density_analysis': os.path.join(output_dir, f'customer_density_{timestamp}.csv'),
            'city_analysis': os.path.join(output_dir, f'city_density_{timestamp}.csv'),
            'clusters_analysis': os.path.join(output_dir, f'high_value_clusters_{timestamp}.csv'),
            'summary_report': os.path.join(output_dir, f'geocommerce_summary_{timestamp}.json')
        }
        
        # Check which files actually exist
        existing_files = {}
        for key, filepath in files.items():
            if os.path.exists(filepath):
                existing_files[key] = filepath
        
        return existing_files
    
    def _save_chat_cpg_results(self, insights: Dict):
        """Save Chat CPG formatted results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.base_dir, 'output')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Chat CPG insights
        chat_cpg_file = os.path.join(output_dir, f'chat_cpg_insights_{timestamp}.json')
        with open(chat_cpg_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Chat CPG insights saved to: {chat_cpg_file}")
    
    def get_quick_insights(self, shopify_data_path: str) -> Dict:
        """
        Get quick insights without full analysis
        
        Args:
            shopify_data_path: Path to Shopify customer export
            
        Returns:
            Dictionary with quick insights
        """
        print("⚡ Generating quick insights...")
        
        # Process data without saving files
        try:
            df_shopify = self.geocommerce.process_shopify_data(shopify_data_path)
        except Exception as e:
            logger.error(f"Error processing Shopify data: {e}")
            raise Exception(f"Failed to process Shopify data: {str(e)}")
        
        quick_insights = {
            'total_customers': len(df_shopify),
            'total_revenue': float(df_shopify['Total Spent'].sum()),
            'unique_cities': df_shopify['Default Address City'].nunique(),
            'unique_ceps': df_shopify['cep'].nunique(),
            'avg_order_value': float(df_shopify['Total Spent'].sum() / df_shopify['Total Orders'].sum()),
            'top_cities': df_shopify['Default Address City'].value_counts().head(5).to_dict(),
            'shopping_distribution': df_shopify['nearest_shopping'].value_counts().to_dict()
        }
        
        return quick_insights
    
    def export_for_chat_cpg(self, insights: Dict, format: str = 'json') -> str:
        """
        Export insights in Chat CPG compatible format
        
        Args:
            insights: Analysis insights dictionary
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.base_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        if format.lower() == 'json':
            filepath = os.path.join(output_dir, f'chat_cpg_export_{timestamp}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(insights, f, ensure_ascii=False, indent=2)
        
        elif format.lower() == 'csv':
            # Export key metrics as CSV
            import pandas as pd
            
            # Create summary DataFrame
            summary_data = {
                'metric': [
                    'total_customers', 'total_revenue', 'unique_cities', 
                    'unique_ceps', 'avg_order_value'
                ],
                'value': [
                    insights['geographic_summary']['total_customers'],
                    insights['geographic_summary']['total_revenue'],
                    insights['geographic_summary']['unique_cities'],
                    insights['geographic_summary']['unique_ceps'],
                    insights['geographic_summary']['avg_order_value']
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            filepath = os.path.join(output_dir, f'chat_cpg_summary_{timestamp}.csv')
            df_summary.to_csv(filepath, index=False)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"📤 Chat CPG export saved to: {filepath}")
        return filepath

def main():
    """Main function to demonstrate integration"""
    print("🔗 GeoCommerce Chat CPG Integration")
    print("=" * 50)
    
    # Initialize integration
    integration = GeoCommerceIntegration()
    
    # Check for Shopify data
    shopify_file = os.path.join(os.path.dirname(__file__), 'customers_export.csv')
    
    if os.path.exists(shopify_file):
        print(f"📊 Found Shopify data: {shopify_file}")
        
        # Get quick insights
        print("\n⚡ Getting quick insights...")
        quick_insights = integration.get_quick_insights(shopify_file)
        
        print(f"   - Total customers: {quick_insights['total_customers']:,}")
        print(f"   - Total revenue: R$ {quick_insights['total_revenue']:,.2f}")
        print(f"   - Unique cities: {quick_insights['unique_cities']}")
        print(f"   - Average order value: R$ {quick_insights['avg_order_value']:.2f}")
        
        # Perform full analysis
        print("\n🔍 Performing full analysis for Chat CPG...")
        insights = integration.analyze_for_chat_cpg(shopify_file)
        
        print(f"\n📋 Analysis Summary:")
        print(f"   - Market insights: {len(insights['market_insights'])} categories")
        print(f"   - Recommendations: {len(insights['recommendations'])} actionable items")
        print(f"   - Opportunities: {len(insights['opportunities'])} identified")
        print(f"   - Output files: {len(insights['data_files'])} generated")
        
        # Export for Chat CPG
        print("\n📤 Exporting for Chat CPG...")
        export_path = integration.export_for_chat_cpg(insights, 'json')
        print(f"   - Export completed: {export_path}")
        
    else:
        print(f"⚠️ Shopify data file not found: {shopify_file}")
        print("Please place your Shopify customer export as 'customers_export.csv' in the geocommerce directory")
    
    print("\n" + "=" * 50)
    print("🎯 GeoCommerce Chat CPG integration ready!")

if __name__ == "__main__":
    main() 