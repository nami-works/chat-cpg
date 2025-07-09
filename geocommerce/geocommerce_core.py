import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium import plugins
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import warnings
warnings.filterwarnings('ignore')

from .config import GeoCommerceConfig, format_currency, format_number, validate_coordinates

class GeoCommerceAnalyzer:
    """Core analyzer for GeoCommerce data"""
    
    def __init__(self):
        self.config = GeoCommerceConfig()
    
    def filter_data(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the dataset"""
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Province filter
        if filters.get('province') and len(filters['province']) > 0:
            filtered_df = filtered_df[filtered_df['province'].isin(filters['province'])]
        
        # City filter
        if filters.get('city') and len(filters['city']) > 0:
            filtered_df = filtered_df[filtered_df['city'].isin(filters['city'])]
        
        # Date range filter
        if 'created_at' in filtered_df.columns:
            date_range = filters.get('date_range')
            if date_range and date_range != 'All time':
                date_ranges = self.config.get_date_range_options()
                if date_range in date_ranges and date_ranges[date_range]:
                    cutoff_date = datetime.now() - date_ranges[date_range]
                    filtered_df = filtered_df[filtered_df['created_at'] >= cutoff_date]
            
            # Custom date range
            if filters.get('custom_start_date'):
                filtered_df = filtered_df[filtered_df['created_at'] >= filters['custom_start_date']]
            if filters.get('custom_end_date'):
                filtered_df = filtered_df[filtered_df['created_at'] <= filters['custom_end_date']]
        
        return filtered_df
    
    def calculate_basic_metrics(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic metrics from the data"""
        metrics = {
            'total_customers': len(customers_df) if not customers_df.empty else 0,
            'total_orders': len(orders_df) if not orders_df.empty else 0,
            'total_revenue': 0,
            'avg_order_value': 0,
            'customers_with_coordinates': 0,
            'orders_with_coordinates': 0,
            'unique_cities': 0,
            'unique_provinces': 0,
            'unique_countries': 0
        }
        
        if not customers_df.empty:
            metrics['customers_with_coordinates'] = customers_df[
                customers_df['latitude'].notna() & customers_df['longitude'].notna()
            ].shape[0]
            metrics['unique_cities'] = customers_df['city'].nunique()
            metrics['unique_provinces'] = customers_df['province'].nunique()
            metrics['unique_countries'] = customers_df['country'].nunique()
        
        if not orders_df.empty:
            metrics['total_revenue'] = orders_df['total_price'].sum()
            metrics['avg_order_value'] = orders_df['total_price'].mean()
            metrics['orders_with_coordinates'] = orders_df[
                orders_df['shipping_latitude'].notna() & orders_df['shipping_longitude'].notna()
            ].shape[0]
        
        return metrics
    
    def create_geographic_distribution_map(self, df: pd.DataFrame, 
                                         lat_col: str = 'latitude', 
                                         lng_col: str = 'longitude',
                                         title: str = "Geographic Distribution") -> folium.Map:
        """Create a geographic distribution map"""
        
        # Filter data with valid coordinates
        map_data = df[df[lat_col].notna() & df[lng_col].notna()].copy()
        
        if map_data.empty:
            # Create empty map centered on Brazil
            m = folium.Map(
                location=self.config.DEFAULT_MAP_CENTER,
                zoom_start=self.config.DEFAULT_MAP_ZOOM,
                tiles='OpenStreetMap'
            )
            return m
        
        # Calculate map center
        center_lat = map_data[lat_col].mean()
        center_lng = map_data[lng_col].mean()
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=self.config.DEFAULT_MAP_ZOOM,
            tiles='OpenStreetMap'
        )
        
        # Add points to map
        for idx, row in map_data.iterrows():
            popup_text = f"""
            <b>Location:</b> {row.get('city', 'Unknown')}, {row.get('province', 'Unknown')}<br>
            <b>Customer:</b> {row.get('email', 'N/A')}<br>
            <b>Orders:</b> {row.get('orders_count', 0)}<br>
            <b>Total Spent:</b> {format_currency(row.get('total_spent', 0))}
            """
            
            folium.Marker(
                location=[row[lat_col], row[lng_col]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Add marker cluster for better performance with many points
        if len(map_data) > 100:
            marker_cluster = plugins.MarkerCluster().add_to(m)
            for idx, row in map_data.iterrows():
                popup_text = f"""
                <b>Location:</b> {row.get('city', 'Unknown')}, {row.get('province', 'Unknown')}<br>
                <b>Customer:</b> {row.get('email', 'N/A')}<br>
                <b>Orders:</b> {row.get('orders_count', 0)}<br>
                <b>Total Spent:</b> {format_currency(row.get('total_spent', 0))}
                """
                
                folium.Marker(
                    location=[row[lat_col], row[lng_col]],
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(marker_cluster)
        
        return m
    
    def create_heat_map(self, df: pd.DataFrame, 
                       lat_col: str = 'latitude', 
                       lng_col: str = 'longitude',
                       weight_col: str = 'total_spent') -> folium.Map:
        """Create a heat map of customer distribution"""
        
        # Filter data with valid coordinates
        map_data = df[df[lat_col].notna() & df[lng_col].notna()].copy()
        
        if map_data.empty:
            # Create empty map
            m = folium.Map(
                location=self.config.DEFAULT_MAP_CENTER,
                zoom_start=self.config.DEFAULT_MAP_ZOOM
            )
            return m
        
        # Calculate map center
        center_lat = map_data[lat_col].mean()
        center_lng = map_data[lng_col].mean()
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=self.config.DEFAULT_MAP_ZOOM,
            tiles='OpenStreetMap'
        )
        
        # Prepare heat map data
        heat_data = []
        for idx, row in map_data.iterrows():
            weight = row.get(weight_col, 1) if weight_col in map_data.columns else 1
            heat_data.append([row[lat_col], row[lng_col], weight])
        
        # Add heat map layer
        plugins.HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)
        
        return m
    
    def create_province_analysis(self, df: pd.DataFrame) -> Tuple[go.Figure, go.Figure]:
        """Create province-based analysis charts"""
        
        if df.empty or 'province' not in df.columns:
            # Return empty figures
            fig1 = go.Figure()
            fig1.update_layout(title="No data available for province analysis")
            fig2 = go.Figure()
            fig2.update_layout(title="No data available for province analysis")
            return fig1, fig2
        
        # Group by province
        province_stats = df.groupby('province').agg({
            'customer_id': 'nunique' if 'customer_id' in df.columns else 'count',
            'total_spent': 'sum' if 'total_spent' in df.columns else 'count',
            'orders_count': 'sum' if 'orders_count' in df.columns else 'count'
        }).reset_index()
        
        province_stats.columns = ['province', 'customers', 'revenue', 'orders']
        province_stats = province_stats.sort_values('revenue', ascending=False)
        
        # Customer distribution by province
        fig1 = px.bar(
            province_stats.head(10),
            x='province',
            y='customers',
            title='Top 10 Provinces by Customer Count',
            labels={'customers': 'Number of Customers', 'province': 'Province'},
            color='customers',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=self.config.CHART_HEIGHT)
        
        # Revenue distribution by province
        fig2 = px.bar(
            province_stats.head(10),
            x='province',
            y='revenue',
            title='Top 10 Provinces by Revenue',
            labels={'revenue': 'Total Revenue (R$)', 'province': 'Province'},
            color='revenue',
            color_continuous_scale='Greens'
        )
        fig2.update_layout(height=self.config.CHART_HEIGHT)
        
        return fig1, fig2
    
    def create_temporal_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Create temporal analysis of orders/customers"""
        
        if df.empty or 'created_at' not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="No temporal data available")
            return fig
        
        # Ensure created_at is datetime
        df = df.copy()
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        
        # Group by date
        daily_stats = df.groupby('date').agg({
            'total_price': 'sum' if 'total_price' in df.columns else 'count',
            'order_id': 'nunique' if 'order_id' in df.columns else 'count'
        }).reset_index()
        
        daily_stats.columns = ['date', 'revenue', 'orders']
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add revenue line
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='blue'),
                yaxis='y'
            )
        )
        
        # Add orders line on secondary y-axis
        fig.add_trace(
            go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['orders'],
                mode='lines+markers',
                name='Orders',
                line=dict(color='red'),
                yaxis='y2'
            )
        )
        
        # Update layout
        fig.update_layout(
            title='Revenue and Orders Over Time',
            xaxis_title='Date',
            yaxis=dict(title='Revenue (R$)', side='left'),
            yaxis2=dict(title='Number of Orders', side='right', overlaying='y'),
            height=self.config.CHART_HEIGHT,
            hovermode='x unified'
        )
        
        return fig
    
    def create_customer_segmentation(self, df: pd.DataFrame) -> go.Figure:
        """Create customer segmentation analysis"""
        
        if df.empty or 'total_spent' not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="No customer data available for segmentation")
            return fig
        
        # Create RFM-like segmentation based on available data
        customer_metrics = df.groupby('customer_id').agg({
            'total_spent': 'sum',
            'orders_count': 'sum',
            'created_at': 'max' if 'created_at' in df.columns else 'count'
        }).reset_index()
        
        # Define spending segments
        spending_percentiles = customer_metrics['total_spent'].quantile([0.25, 0.5, 0.75, 1.0])
        
        def categorize_customer(spent):
            if spent <= spending_percentiles[0.25]:
                return 'Low Value'
            elif spent <= spending_percentiles[0.5]:
                return 'Medium Value'
            elif spent <= spending_percentiles[0.75]:
                return 'High Value'
            else:
                return 'VIP'
        
        customer_metrics['segment'] = customer_metrics['total_spent'].apply(categorize_customer)
        
        # Count customers in each segment
        segment_counts = customer_metrics['segment'].value_counts()
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=segment_counts.index,
            values=segment_counts.values,
            hole=0.3,
            textinfo='label+percent',
            marker_colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        )])
        
        fig.update_layout(
            title='Customer Segmentation by Spending',
            height=self.config.CHART_HEIGHT
        )
        
        return fig
    
    def perform_clustering_analysis(self, df: pd.DataFrame, 
                                   method: str = 'K-Means', 
                                   n_clusters: int = 5,
                                   features: List[str] = None) -> Tuple[pd.DataFrame, go.Figure, Dict]:
        """Perform clustering analysis on customer data"""
        
        if df.empty:
            return df, go.Figure(), {}
        
        # Default features for clustering
        if features is None:
            available_features = []
            potential_features = ['latitude', 'longitude', 'total_spent', 'orders_count']
            for feature in potential_features:
                if feature in df.columns:
                    available_features.append(feature)
            features = available_features
        
        if not features:
            return df, go.Figure(), {}
        
        # Prepare data for clustering
        clustering_data = df[features].dropna()
        
        if clustering_data.empty or len(clustering_data) < n_clusters:
            return df, go.Figure(), {}
        
        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(clustering_data)
        
        # Perform clustering
        if method == 'K-Means':
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif method == 'DBSCAN':
            clusterer = DBSCAN(eps=0.5, min_samples=5)
        else:  # Hierarchical
            from sklearn.cluster import AgglomerativeClustering
            clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        
        cluster_labels = clusterer.fit_predict(scaled_data)
        
        # Add cluster labels to dataframe
        result_df = df.copy()
        result_df['cluster'] = -1  # Default for rows not included in clustering
        result_df.loc[clustering_data.index, 'cluster'] = cluster_labels
        
        # Calculate silhouette score
        metrics = {}
        if len(set(cluster_labels)) > 1:
            silhouette_avg = silhouette_score(scaled_data, cluster_labels)
            metrics['silhouette_score'] = silhouette_avg
        
        # Create visualization
        if 'latitude' in features and 'longitude' in features:
            # Geographic clustering visualization
            fig = px.scatter_mapbox(
                result_df[result_df['cluster'] >= 0],
                lat='latitude',
                lon='longitude',
                color='cluster',
                hover_data=['city', 'province', 'total_spent'],
                mapbox_style='open-street-map',
                title=f'{method} Clustering Results',
                height=600,
                zoom=5
            )
        else:
            # 2D scatter plot of first two features
            if len(features) >= 2:
                fig = px.scatter(
                    result_df[result_df['cluster'] >= 0],
                    x=features[0],
                    y=features[1],
                    color='cluster',
                    title=f'{method} Clustering Results',
                    height=self.config.CHART_HEIGHT
                )
            else:
                fig = go.Figure()
                fig.update_layout(title="Insufficient features for visualization")
        
        return result_df, fig, metrics
    
    def create_top_cities_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Create top cities analysis"""
        
        if df.empty or 'city' not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="No city data available")
            return fig
        
        # Group by city
        city_stats = df.groupby('city').agg({
            'customer_id': 'nunique' if 'customer_id' in df.columns else 'count',
            'total_spent': 'sum' if 'total_spent' in df.columns else 'count',
            'orders_count': 'sum' if 'orders_count' in df.columns else 'count'
        }).reset_index()
        
        city_stats.columns = ['city', 'customers', 'revenue', 'orders']
        city_stats = city_stats.sort_values('revenue', ascending=True).tail(15)
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=city_stats['city'],
                x=city_stats['revenue'],
                orientation='h',
                marker_color='lightblue',
                text=city_stats['revenue'].apply(lambda x: format_currency(x)),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='Top 15 Cities by Revenue',
            xaxis_title='Revenue (R$)',
            yaxis_title='City',
            height=500
        )
        
        return fig
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate key performance metrics"""
        
        metrics = {}
        
        if df.empty:
            return metrics
        
        # Customer metrics
        if 'customer_id' in df.columns:
            metrics['total_customers'] = df['customer_id'].nunique()
        
        # Order metrics
        if 'order_id' in df.columns:
            metrics['total_orders'] = df['order_id'].nunique()
        
        # Revenue metrics
        if 'total_price' in df.columns:
            metrics['total_revenue'] = df['total_price'].sum()
            metrics['avg_order_value'] = df['total_price'].mean()
            metrics['median_order_value'] = df['total_price'].median()
        
        # Geographic coverage
        if 'city' in df.columns:
            metrics['cities_served'] = df['city'].nunique()
        if 'province' in df.columns:
            metrics['provinces_served'] = df['province'].nunique()
        
        # Coordinate coverage
        if 'latitude' in df.columns and 'longitude' in df.columns:
            valid_coords = df[df['latitude'].notna() & df['longitude'].notna()]
            metrics['geocoding_coverage'] = len(valid_coords) / len(df) * 100 if len(df) > 0 else 0
        
        return metrics
    
    def export_data(self, df: pd.DataFrame, format_type: str = 'CSV') -> bytes:
        """Export data in specified format"""
        
        if df.empty:
            return b''
        
        # Limit export size
        if len(df) > self.config.MAX_EXPORT_ROWS:
            df = df.head(self.config.MAX_EXPORT_ROWS)
        
        if format_type == 'CSV':
            return df.to_csv(index=False).encode('utf-8')
        elif format_type == 'Excel':
            import io
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            return output.getvalue()
        elif format_type == 'JSON':
            return df.to_json(orient='records', indent=2).encode('utf-8')
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def create_summary_report(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Create a comprehensive summary report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'data_summary': {},
            'geographic_analysis': {},
            'customer_analysis': {},
            'order_analysis': {},
            'performance_metrics': {}
        }
        
        # Data summary
        report['data_summary'] = {
            'total_customers': len(customers_df) if not customers_df.empty else 0,
            'total_orders': len(orders_df) if not orders_df.empty else 0,
            'date_range': {
                'start': customers_df['created_at'].min().isoformat() if not customers_df.empty and 'created_at' in customers_df.columns else None,
                'end': customers_df['created_at'].max().isoformat() if not customers_df.empty and 'created_at' in customers_df.columns else None
            }
        }
        
        # Geographic analysis
        if not customers_df.empty:
            report['geographic_analysis'] = {
                'unique_cities': customers_df['city'].nunique() if 'city' in customers_df.columns else 0,
                'unique_provinces': customers_df['province'].nunique() if 'province' in customers_df.columns else 0,
                'geocoding_coverage': len(customers_df[customers_df['latitude'].notna()]) / len(customers_df) * 100 if 'latitude' in customers_df.columns else 0
            }
        
        # Customer analysis
        if not customers_df.empty:
            total_spent_col = 'total_spent' if 'total_spent' in customers_df.columns else None
            if total_spent_col:
                report['customer_analysis'] = {
                    'avg_customer_value': customers_df[total_spent_col].mean(),
                    'median_customer_value': customers_df[total_spent_col].median(),
                    'top_customer_value': customers_df[total_spent_col].max(),
                    'total_customer_value': customers_df[total_spent_col].sum()
                }
        
        # Order analysis
        if not orders_df.empty:
            total_price_col = 'total_price' if 'total_price' in orders_df.columns else None
            if total_price_col:
                report['order_analysis'] = {
                    'avg_order_value': orders_df[total_price_col].mean(),
                    'median_order_value': orders_df[total_price_col].median(),
                    'total_revenue': orders_df[total_price_col].sum(),
                    'order_frequency': len(orders_df) / len(customers_df) if not customers_df.empty else 0
                }
        
        # Performance metrics
        report['performance_metrics'] = self.calculate_performance_metrics(
            customers_df if not customers_df.empty else orders_df
        )
        
        return report