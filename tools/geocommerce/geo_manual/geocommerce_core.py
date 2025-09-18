"""
GeoCommerce - E-commerce Geographic Analysis Platform
Advanced geographic proximity analysis and consumer density mapping for e-commerce businesses.
"""

import pandas as pd
import os
import json
import time
import random
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base directory for GeoCommerce
base_dir = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(base_dir, 'geocoding_cache.json')

# Default shopping mall coordinates (can be customized via config)
DEFAULT_SHOPPINGS_COORDS = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

@dataclass
class CustomerData:
    """Data class for customer information"""
    customer_id: str
    cep: str
    city: str
    state: str
    total_spent: float
    total_orders: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearest_shopping: Optional[str] = None
    distance_to_nearest: Optional[float] = None

@dataclass
class DensityAnalysis:
    """Data class for density analysis results"""
    cep: str
    customer_count: int
    total_revenue: float
    total_orders: int
    avg_order_value: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearest_shopping: Optional[str] = None
    distance_to_nearest: Optional[float] = None

class GeoCommerce:
    """
    GeoCommerce - E-commerce Geographic Analysis Platform
    
    Provides comprehensive geographic analysis for e-commerce businesses including:
    - Customer density mapping
    - Shopping mall proximity analysis
    - High-value customer clustering
    - Revenue optimization insights
    - Market expansion recommendations
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize GeoCommerce system
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._get_default_config()
        self.cache = self._load_cache()
        self.geolocator = Nominatim(user_agent=self.config['geocoding']['user_agent'])
        self.shoppings_coords = self.config['shoppings']
        
        logger.info("GeoCommerce initialized successfully")
        logger.info(f"Loaded {len(self.cache)} cached coordinates")
        logger.info(f"Configured {len(self.shoppings_coords)} shopping locations")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'geocoding': {
                'user_agent': 'geocommerce_platform',
                'timeout': 10,
                'rate_limit_delay': 3,
                'max_retries': 3
            },
            'analysis': {
                'density_bins': [0, 1, 5, 10, 20, float('inf')],
                'density_labels': ['Baixa', 'Média-Baixa', 'Média', 'Alta', 'Muito Alta'],
                'high_value_min_revenue': 1000,
                'high_value_max_distance': 15,
                'top_cities_limit': 10
            },
            'output': {
                'include_timestamp': True,
                'output_formats': ['csv', 'json'],
                'compression': False
            },
            'shoppings': DEFAULT_SHOPPINGS_COORDS
        }
    
    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load coordinate cache from file"""
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """Save coordinate cache to file"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def get_coordinates(self, cep: str) -> Tuple[float, float]:
        """
        Get coordinates for a CEP with intelligent caching
        
        Args:
            cep: Brazilian postal code
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        if cep in self.cache:
            return self.cache[cep]

        try:
            location = self.geolocator.geocode(
                {'postalcode': cep, 'country': 'Brazil'}, 
                timeout=self.config['geocoding']['timeout']
            )
            coords = (location.latitude, location.longitude) if location else (None, None)
        except Exception as e:
            logger.warning(f"Error geocoding CEP {cep}: {e}")
            coords = (None, None)

        if coords != (None, None):
            self.cache[cep] = coords
            self._save_cache()
        
        # Rate limiting
        time.sleep(self.config['geocoding']['rate_limit_delay'] + random.random())
        return coords

    def calculate_distance(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates
        
        Args:
            coords1: First coordinate tuple (lat, lon)
            coords2: Second coordinate tuple (lat, lon)
            
        Returns:
            Distance in kilometers
        """
        if None in coords1 or None in coords2:
            return float('inf')
        return round(geodesic(coords1, coords2).km, 2)

    def process_shopify_data(self, shopify_csv_path: str) -> pd.DataFrame:
        """
        Process Shopify customer export data
        
        Args:
            shopify_csv_path: Path to Shopify customer export CSV
            
        Returns:
            Processed DataFrame with coordinates and shopping mall distances
        """
        logger.info("Processing Shopify customer data...")
        
        # Load Shopify data
        df = pd.read_csv(shopify_csv_path)
        
        # Log initial data info
        logger.info(f"Loaded {len(df)} rows from Shopify CSV")
        logger.info(f"Columns found: {list(df.columns)}")
        
        # Check for required columns
        required_columns = ['Default Address Zip', 'Total Spent', 'Total Orders']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and prepare data - handle NaN values properly
        df['cep'] = df['Default Address Zip'].astype(str).fillna('')
        df['cep'] = df['cep'].str.replace('-', '').str.strip()
        df['cep'] = df['cep'].str.zfill(8)
        
        # Filter out rows with empty CEPs
        initial_count = len(df)
        df = df[df['cep'] != '00000000'].copy()
        final_count = len(df)
        
        logger.info(f"Filtered out {initial_count - final_count} rows with invalid CEPs")
        logger.info(f"Processing {final_count} valid customer records")
        
        # Convert Total Spent to numeric, handling currency formatting and NaN values
        df['Total Spent'] = df['Total Spent'].astype(str).fillna('0')
        df['Total Spent'] = pd.to_numeric(
            df['Total Spent'].str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        df['Total Orders'] = pd.to_numeric(df['Total Orders'], errors='coerce').fillna(0)
        
        # Validate we have data to process
        if len(df) == 0:
            raise ValueError("No valid customer records found after data cleaning")
        
        logger.info(f"Data validation complete. Processing {len(df)} customer records")
        
        # Add coordinate columns
        df['latitude'] = None
        df['longitude'] = None
        
        # Process coordinates for unique CEPs
        unique_ceps = df['cep'].unique()
        logger.info(f"Processing {len(unique_ceps)} unique CEPs...")
        
        for i, cep in enumerate(unique_ceps):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(unique_ceps)} CEPs processed")
            
            coords = self.get_coordinates(cep)
            df.loc[df['cep'] == cep, ['latitude', 'longitude']] = [coords[0], coords[1]]
        
        # Calculate distances to shopping malls
        for shopping, coords_shop in self.shoppings_coords.items():
            df[f'distance_{shopping}'] = df.apply(
                lambda row: self.calculate_distance(
                    (row['latitude'], row['longitude']), 
                    coords_shop
                ) if row['latitude'] and row['longitude'] else float('inf'),
                axis=1
            )
        
        # Find nearest shopping mall
        shopping_columns = [f'distance_{shopping}' for shopping in self.shoppings_coords.keys()]
        df['nearest_shopping'] = df[shopping_columns].idxmin(axis=1).str.replace('distance_', '')
        df['distance_to_nearest'] = df[shopping_columns].min(axis=1)
        
        logger.info("Shopify data processing completed!")
        return df

    def analyze_customer_density(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze customer density by geographic areas
        
        Args:
            df: Processed Shopify DataFrame
            
        Returns:
            DataFrame with density analysis by CEP
        """
        logger.info("Analyzing customer density...")
        
        # Group by CEP to get density metrics
        density_analysis = df.groupby('cep').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'latitude': 'first',
            'longitude': 'first',
            'nearest_shopping': 'first',
            'distance_to_nearest': 'first'
        }).reset_index()
        
        density_analysis.columns = [
            'cep', 'customer_count', 'total_revenue', 'total_orders',
            'latitude', 'longitude', 'nearest_shopping', 'distance_to_nearest'
        ]
        
        # Calculate average order value
        density_analysis['avg_order_value'] = (
            density_analysis['total_revenue'] / density_analysis['total_orders']
        ).fillna(0)
        
        # Add density categories
        density_analysis['density_category'] = pd.cut(
            density_analysis['customer_count'],
            bins=self.config['analysis']['density_bins'],
            labels=self.config['analysis']['density_labels']
        )
        
        logger.info(f"Density analysis completed for {len(density_analysis)} geographic areas")
        return density_analysis

    def analyze_city_density(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze customer density by city
        
        Args:
            df: Processed Shopify DataFrame
            
        Returns:
            DataFrame with city-level density analysis
        """
        logger.info("Analyzing city-level density...")
        
        city_density = df.groupby('Default Address City').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'cep': 'nunique'  # Number of unique CEPs
        }).reset_index()
        
        city_density.columns = ['city', 'total_customers', 'total_revenue', 'total_orders', 'unique_ceps']
        city_density['avg_order_value'] = city_density['total_revenue'] / city_density['total_orders']
        city_density['customers_per_cep'] = city_density['total_customers'] / city_density['unique_ceps']
        
        return city_density.sort_values('total_customers', ascending=False)

    def identify_high_value_clusters(self, df: pd.DataFrame, 
                                   min_revenue: Optional[float] = None,
                                   max_distance: Optional[float] = None) -> pd.DataFrame:
        """
        Identify high-value customer clusters near shopping malls
        
        Args:
            df: Processed Shopify DataFrame
            min_revenue: Minimum revenue threshold (uses config default if None)
            max_distance: Maximum distance threshold (uses config default if None)
            
        Returns:
            DataFrame with high-value cluster analysis
        """
        logger.info("Identifying high-value customer clusters...")
        
        min_revenue = min_revenue or self.config['analysis']['high_value_min_revenue']
        max_distance = max_distance or self.config['analysis']['high_value_max_distance']
        
        # Filter high-value customers within reasonable distance
        high_value = df[
            (df['Total Spent'] >= min_revenue) & 
            (df['distance_to_nearest'] <= max_distance)
        ].copy()
        
        # Group by shopping mall and analyze
        clusters = high_value.groupby('nearest_shopping').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'distance_to_nearest': 'mean'
        }).reset_index()
        
        clusters.columns = ['shopping', 'high_value_customers', 'total_revenue', 'total_orders', 'avg_distance']
        clusters['avg_customer_value'] = clusters['total_revenue'] / clusters['high_value_customers']
        
        return clusters.sort_values('total_revenue', ascending=False)

    def generate_comprehensive_report(self, shopify_csv_path: str, output_dir: Optional[str] = None) -> Dict:
        """
        Generate comprehensive analysis report
        
        Args:
            shopify_csv_path: Path to Shopify customer export
            output_dir: Output directory (uses base_dir if None)
            
        Returns:
            Dictionary with analysis summary
        """
        if output_dir is None:
            output_dir = base_dir
        
        logger.info("Generating comprehensive GeoCommerce report...")
        
        # Process Shopify data
        df_shopify = self.process_shopify_data(shopify_csv_path)
        
        # Analyze density
        df_density = self.analyze_customer_density(df_shopify)
        df_city_density = self.analyze_city_density(df_shopify)
        df_clusters = self.identify_high_value_clusters(df_shopify)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        df_shopify.to_csv(os.path.join(output_dir, f'shopify_processed_{timestamp}.csv'), index=False)
        df_density.to_csv(os.path.join(output_dir, f'customer_density_{timestamp}.csv'), index=False)
        df_city_density.to_csv(os.path.join(output_dir, f'city_density_{timestamp}.csv'), index=False)
        df_clusters.to_csv(os.path.join(output_dir, f'high_value_clusters_{timestamp}.csv'), index=False)
        
        # Generate summary statistics
        summary = {
            'analysis_timestamp': timestamp,
            'total_customers': len(df_shopify),
            'total_revenue': float(df_shopify['Total Spent'].sum()),
            'total_orders': int(df_shopify['Total Orders'].sum()),
            'unique_ceps': df_shopify['cep'].nunique(),
            'unique_cities': df_shopify['Default Address City'].nunique(),
            'avg_order_value': float(df_shopify['Total Spent'].sum() / df_shopify['Total Orders'].sum()),
            'top_cities': df_city_density.head(self.config['analysis']['top_cities_limit']).to_dict('records'),
            'shopping_distribution': df_shopify['nearest_shopping'].value_counts().to_dict(),
            'high_value_clusters': df_clusters.to_dict('records'),
            'density_summary': {
                'total_areas': len(df_density),
                'high_density_areas': len(df_density[df_density['density_category'] == 'Muito Alta']),
                'medium_density_areas': len(df_density[df_density['density_category'] == 'Alta']),
                'low_density_areas': len(df_density[df_density['density_category'] == 'Baixa'])
            }
        }
        
        # Save summary
        with open(os.path.join(output_dir, f'geocommerce_summary_{timestamp}.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("Comprehensive GeoCommerce report generated successfully!")
        return summary

    def generate_visualizations(self, shopify_csv_path: str) -> None:
        """
        Generate interactive visualizations for geographic analysis
        
        Args:
            shopify_csv_path: Path to Shopify customer export
        """
        logger.info("Generating interactive visualizations...")
        
        try:
            # Process Shopify data
            df_shopify = self.process_shopify_data(shopify_csv_path)
            
            # Generate density analysis
            df_density = self.analyze_customer_density(df_shopify)
            
            # Generate city density analysis
            df_city_density = self.analyze_city_density(df_shopify)
            
            # Generate high-value clusters
            df_clusters = self.identify_high_value_clusters(df_shopify)
            
            # Create visualizations
            self._create_density_map(df_density)
            self._create_city_chart(df_city_density)
            self._create_cluster_analysis(df_clusters)
            
            logger.info("Visualizations generated successfully!")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            raise
    
    def _create_density_map(self, df_density: pd.DataFrame) -> None:
        """Create interactive density map"""
        try:
            import folium
            from folium import plugins
            
            # Create base map centered on Brazil
            m = folium.Map(
                location=[-15.7801, -47.9292],  # Brasília
                zoom_start=5,
                tiles='OpenStreetMap'
            )
            
            # Add density markers
            for _, row in df_density.iterrows():
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    # Color based on density category
                    color_map = {
                        'Muito Alta': 'red',
                        'Alta': 'orange', 
                        'Média': 'yellow',
                        'Baixa': 'green'
                    }
                    color = color_map.get(row['density_category'], 'blue')
                    
                    # Popup content
                    popup_content = f"""
                    <b>CEP: {row['cep']}</b><br>
                    Customers: {row['customer_count']}<br>
                    Revenue: R$ {row['total_revenue']:,.2f}<br>
                    Density: {row['density_category']}<br>
                    Nearest Shopping: {row['nearest_shopping']}
                    """
                    
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=row['customer_count'] * 2,  # Size based on customer count
                        popup=popup_content,
                        color=color,
                        fill=True,
                        fillOpacity=0.7
                    ).add_to(m)
            
            # Save map
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            map_path = f'customer_density_map_{timestamp}.html'
            m.save(map_path)
            
            logger.info(f"Density map saved: {map_path}")
            
        except ImportError:
            logger.warning("folium not available, skipping density map generation")
        except Exception as e:
            logger.error(f"Error creating density map: {e}")
    
    def _create_city_chart(self, df_city_density: pd.DataFrame) -> None:
        """Create city performance chart"""
        try:
            import plotly.express as px
            
            # Create bar chart of top cities by revenue
            top_cities = df_city_density.head(10)
            
            fig = px.bar(
                top_cities,
                x='city',
                y='total_revenue',
                title='Top Cities by Revenue',
                labels={'total_revenue': 'Total Revenue (R$)', 'city': 'City'},
                color='total_customers',
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500
            )
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = f'city_performance_{timestamp}.html'
            fig.write_html(chart_path)
            
            logger.info(f"City chart saved: {chart_path}")
            
        except ImportError:
            logger.warning("plotly not available, skipping city chart generation")
        except Exception as e:
            logger.error(f"Error creating city chart: {e}")
    
    def _create_cluster_analysis(self, df_clusters: pd.DataFrame) -> None:
        """Create high-value cluster analysis chart"""
        try:
            import plotly.express as px
            
            if len(df_clusters) > 0:
                fig = px.scatter(
                    df_clusters,
                    x='avg_distance',
                    y='total_revenue',
                    size='high_value_customers',
                    color='avg_customer_value',
                    hover_name='shopping',
                    title='High-Value Customer Clusters by Shopping Mall',
                    labels={
                        'avg_distance': 'Average Distance (km)',
                        'total_revenue': 'Total Revenue (R$)',
                        'high_value_customers': 'High-Value Customers',
                        'avg_customer_value': 'Average Customer Value (R$)'
                    }
                )
                
                # Save chart
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chart_path = f'cluster_analysis_{timestamp}.html'
                fig.write_html(chart_path)
                
                logger.info(f"Cluster analysis saved: {chart_path}")
            else:
                logger.info("No high-value clusters found for visualization")
                
        except ImportError:
            logger.warning("plotly not available, skipping cluster analysis generation")
        except Exception as e:
            logger.error(f"Error creating cluster analysis: {e}")

    def get_system_info(self) -> Dict:
        """Get system information and status"""
        return {
            'system_name': 'GeoCommerce',
            'version': '1.0.0',
            'cached_coordinates': len(self.cache),
            'configured_shoppings': len(self.shoppings_coords),
            'shopping_locations': list(self.shoppings_coords.keys()),
            'config': self.config
        }

def main():
    """Main function to demonstrate GeoCommerce usage"""
    print("🚀 Starting GeoCommerce - E-commerce Geographic Analysis Platform")
    print("=" * 60)
    
    # Initialize GeoCommerce
    geocommerce = GeoCommerce()
    
    # Display system info
    info = geocommerce.get_system_info()
    print(f"System: {info['system_name']} v{info['version']}")
    print(f"Cached coordinates: {info['cached_coordinates']}")
    print(f"Shopping locations: {info['shopping_locations']}")
    
    # Check for Shopify data
    shopify_file = os.path.join(base_dir, 'customers_export.csv')
    
    if os.path.exists(shopify_file):
        print(f"\n📊 Found Shopify data: {shopify_file}")
        print("Processing customer data and generating comprehensive report...")
        
        try:
            summary = geocommerce.generate_comprehensive_report(shopify_file)
            print(f"\n✅ Analysis completed successfully!")
            print(f"   - Total customers: {summary['total_customers']:,}")
            print(f"   - Total revenue: R$ {summary['total_revenue']:,.2f}")
            print(f"   - Unique cities: {summary['unique_cities']}")
            print(f"   - High-value clusters: {len(summary['high_value_clusters'])}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    else:
        print(f"\n⚠️ Shopify data file not found: {shopify_file}")
        print("Please place your Shopify customer export as 'customers_export.csv' in the geocommerce directory")
    
    print("\n" + "=" * 60)
    print("🎯 GeoCommerce ready for e-commerce geographic analysis!")

if __name__ == "__main__":
    main() 