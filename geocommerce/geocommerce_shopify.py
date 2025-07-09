import streamlit as st
import pandas as pd
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback
import json

# Import our modules
from .config import (
    GeoCommerceConfig, init_streamlit_config, load_custom_css, init_session_state,
    display_success_message, display_error_message, display_info_message,
    format_currency, format_number, clear_cache
)
from .shopify_connector import ShopifyGraphQLClient, ShopifyConfig
from .api_data_processor import ShopifyDataProcessor
from .geocommerce_core import GeoCommerceAnalyzer

# Initialize Streamlit configuration
init_streamlit_config()
load_custom_css()
init_session_state()

class GeoCommerceShopifyApp:
    """Main Streamlit application for GeoCommerce with Shopify API integration"""
    
    def __init__(self):
        self.config = GeoCommerceConfig()
        self.analyzer = GeoCommerceAnalyzer()
        self.data_processor = ShopifyDataProcessor()
    
    def run(self):
        """Main application entry point"""
        st.title("🌍 GeoCommerce - Shopify API Integration")
        st.markdown("*Geographic and commercial analysis of e-commerce data*")
        
        # Sidebar for configuration and controls
        self.render_sidebar()
        
        # Main content area
        if not st.session_state.get('connection_tested', False):
            self.render_connection_setup()
        elif not st.session_state.get('shopify_data_loaded', False):
            self.render_data_fetching()
        else:
            self.render_analysis_tabs()
    
    def render_sidebar(self):
        """Render the sidebar with controls and filters"""
        st.sidebar.header("Configuration")
        
        # Connection status
        if st.session_state.get('connection_status'):
            status = st.session_state.connection_status
            if status.get('success'):
                st.sidebar.success("✅ Connected to Shopify")
                shop_info = status.get('shop_info', {})
                st.sidebar.info(f"Shop: {shop_info.get('name', 'Unknown')}")
            else:
                st.sidebar.error("❌ Connection Failed")
                st.sidebar.error(status.get('message', 'Unknown error'))
        
        # Data status
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.success("✅ Data Loaded")
            
            # Data summary
            customers_count = len(st.session_state.customers_df) if st.session_state.customers_df is not None else 0
            orders_count = len(st.session_state.orders_df) if st.session_state.orders_df is not None else 0
            
            st.sidebar.metric("Customers", customers_count)
            st.sidebar.metric("Orders", orders_count)
            
            if st.session_state.last_fetch_time:
                st.sidebar.info(f"Last updated: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Filters section
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.header("Filters")
            self.render_filters()
        
        # Cache management
        st.sidebar.header("Cache Management")
        if st.sidebar.button("Clear Cache"):
            clear_cache()
            st.sidebar.success("Cache cleared!")
            st.experimental_rerun()
        
        # Export options
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.header("Export Data")
            self.render_export_options()
    
    def render_filters(self):
        """Render data filters in the sidebar"""
        
        # Get available options from data
        customers_df = st.session_state.get('customers_df')
        orders_df = st.session_state.get('orders_df')
        
        if customers_df is not None and not customers_df.empty:
            # Province filter
            available_provinces = sorted(customers_df['province'].dropna().unique().tolist())
            selected_provinces = st.sidebar.multiselect(
                "Select Provinces",
                options=available_provinces,
                default=st.session_state.filters.get('province', [])
            )
            st.session_state.filters['province'] = selected_provinces
            
            # City filter (filtered by selected provinces)
            if selected_provinces:
                filtered_customers = customers_df[customers_df['province'].isin(selected_provinces)]
                available_cities = sorted(filtered_customers['city'].dropna().unique().tolist())
            else:
                available_cities = sorted(customers_df['city'].dropna().unique().tolist())
            
            selected_cities = st.sidebar.multiselect(
                "Select Cities",
                options=available_cities,
                default=st.session_state.filters.get('city', [])
            )
            st.session_state.filters['city'] = selected_cities
        
        # Date range filter
        if orders_df is not None and not orders_df.empty and 'created_at' in orders_df.columns:
            date_range_options = list(self.config.get_date_range_options().keys())
            selected_date_range = st.sidebar.selectbox(
                "Date Range",
                options=date_range_options,
                index=date_range_options.index(st.session_state.filters.get('date_range', 'Last 30 days'))
            )
            st.session_state.filters['date_range'] = selected_date_range
            
            # Custom date range
            if selected_date_range == 'All time':
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    custom_start = st.date_input(
                        "Start Date",
                        value=st.session_state.filters.get('custom_start_date'),
                        key="custom_start_date"
                    )
                with col2:
                    custom_end = st.date_input(
                        "End Date", 
                        value=st.session_state.filters.get('custom_end_date'),
                        key="custom_end_date"
                    )
                st.session_state.filters['custom_start_date'] = custom_start
                st.session_state.filters['custom_end_date'] = custom_end
    
    def render_export_options(self):
        """Render export options in the sidebar"""
        
        export_format = st.sidebar.selectbox(
            "Export Format",
            options=self.config.EXPORT_FORMATS
        )
        
        if st.sidebar.button("Export Data"):
            self.export_data(export_format)
    
    def export_data(self, format_type: str):
        """Export current dataset"""
        try:
            # Get filtered data
            customers_df = st.session_state.get('customers_df')
            if customers_df is not None:
                filtered_df = self.analyzer.filter_data(customers_df, st.session_state.filters)
                
                if not filtered_df.empty:
                    export_data = self.analyzer.export_data(filtered_df, format_type)
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"geocommerce_export_{timestamp}.{format_type.lower()}"
                    
                    # Offer download
                    st.sidebar.download_button(
                        label=f"Download {format_type}",
                        data=export_data,
                        file_name=filename,
                        mime=self.get_mime_type(format_type)
                    )
                    st.sidebar.success(f"Export ready for download!")
                else:
                    st.sidebar.warning("No data to export with current filters")
            else:
                st.sidebar.error("No data available for export")
        except Exception as e:
            st.sidebar.error(f"Export failed: {str(e)}")
    
    def get_mime_type(self, format_type: str) -> str:
        """Get MIME type for export format"""
        mime_types = {
            'CSV': 'text/csv',
            'Excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'JSON': 'application/json'
        }
        return mime_types.get(format_type, 'application/octet-stream')
    
    def render_connection_setup(self):
        """Render connection setup and testing"""
        st.header("🔗 Shopify API Connection")
        
        # Validate credentials
        credential_validation = self.config.validate_shopify_credentials()
        
        if not credential_validation['valid']:
            st.error("Missing Shopify API credentials!")
            st.markdown("Please ensure the following environment variables are set:")
            for error in credential_validation['errors']:
                st.markdown(f"- {error}")
            
            with st.expander("Environment Variables Setup"):
                st.markdown("""
                Create a `.env` file in your project root with:
                ```
                SHOPIFY_SHOP_NAME=your-shop-name
                SHOPIFY_ACCESS_TOKEN=your-access-token
                SHOPIFY_API_VERSION=2024-01
                ```
                """)
            return
        
        # Test connection button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Test Connection", type="primary"):
                self.test_shopify_connection()
        
        with col2:
            if st.session_state.get('connection_status'):
                status = st.session_state.connection_status
                if status.get('success'):
                    display_success_message(status.get('message', 'Connection successful'))
                else:
                    display_error_message(status.get('message', 'Connection failed'))
    
    def test_shopify_connection(self):
        """Test connection to Shopify API"""
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Testing Shopify API connection...")
            progress_bar.progress(25)
            
            # Test connection using async context manager
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async def test_connection():
                    async with ShopifyGraphQLClient() as client:
                        return await client.test_connection()
                
                result = loop.run_until_complete(test_connection())
                
                progress_bar.progress(100)
                status_text.text("Connection test completed!")
                
                # Store result in session state
                st.session_state.connection_status = result
                st.session_state.connection_tested = True
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Rerun to update UI
                st.experimental_rerun()
                
            finally:
                loop.close()
                
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")
            st.session_state.connection_status = {
                'success': False,
                'message': str(e)
            }
    
    def render_data_fetching(self):
        """Render data fetching interface"""
        st.header("📊 Fetch Shopify Data")
        
        # Data fetching options
        col1, col2 = st.columns(2)
        
        with col1:
            fetch_customers = st.checkbox("Fetch Customers", value=True)
            incremental_update = st.checkbox("Incremental Update (last 7 days)", value=False)
        
        with col2:
            fetch_orders = st.checkbox("Fetch Orders", value=True)
            max_records = st.number_input("Max Records per Type", min_value=10, max_value=10000, value=1000)
        
        # Fetch data button
        if st.button("Fetch Data from Shopify", type="primary"):
            self.fetch_shopify_data(fetch_customers, fetch_orders, incremental_update, max_records)
    
    def fetch_shopify_data(self, fetch_customers: bool, fetch_orders: bool, 
                          incremental_update: bool, max_records: int):
        """Fetch data from Shopify API"""
        try:
            # Show progress
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Initializing data fetch...")
                progress_bar.progress(10)
                
                # Calculate date for incremental update
                updated_since = None
                if incremental_update:
                    updated_since = datetime.now() - timedelta(days=self.config.INCREMENTAL_UPDATE_DAYS)
                
                # Set up async event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    customers_data = []
                    orders_data = []
                    
                    async def fetch_data():
                        async with ShopifyGraphQLClient() as client:
                            nonlocal customers_data, orders_data
                            
                            # Fetch customers
                            if fetch_customers:
                                status_text.text("Fetching customers from Shopify...")
                                progress_bar.progress(20)
                                
                                def customer_progress(count, pages):
                                    status_text.text(f"Fetched {count} customers ({pages} pages)...")
                                    # Limit progress to avoid exceeding max records
                                    progress_val = min(50, 20 + (count / max_records) * 30)
                                    progress_bar.progress(int(progress_val))
                                
                                customers_data = await client.fetch_all_customers(
                                    updated_since=updated_since,
                                    progress_callback=customer_progress
                                )
                                
                                # Limit to max_records
                                if len(customers_data) > max_records:
                                    customers_data = customers_data[:max_records]
                            
                            # Fetch orders
                            if fetch_orders:
                                status_text.text("Fetching orders from Shopify...")
                                progress_bar.progress(60)
                                
                                def order_progress(count, pages):
                                    status_text.text(f"Fetched {count} orders ({pages} pages)...")
                                    progress_val = min(90, 60 + (count / max_records) * 30)
                                    progress_bar.progress(int(progress_val))
                                
                                orders_data = await client.fetch_all_orders(
                                    created_since=updated_since,
                                    progress_callback=order_progress
                                )
                                
                                # Limit to max_records
                                if len(orders_data) > max_records:
                                    orders_data = orders_data[:max_records]
                    
                    # Run the async fetch
                    loop.run_until_complete(fetch_data())
                    
                    # Process the data
                    status_text.text("Processing data...")
                    progress_bar.progress(95)
                    
                    # Process customers
                    customers_df = pd.DataFrame()
                    if customers_data:
                        customers_df = self.data_processor.process_customers_data(customers_data)
                    
                    # Process orders
                    orders_df = pd.DataFrame()
                    if orders_data:
                        orders_df = self.data_processor.process_orders_data(orders_data)
                    
                    # Create unified dataset
                    unified_df = self.data_processor.create_unified_dataset(customers_df, orders_df)
                    
                    # Save to session state
                    st.session_state.customers_df = customers_df
                    st.session_state.orders_df = orders_df
                    st.session_state.unified_df = unified_df
                    st.session_state.shopify_data_loaded = True
                    st.session_state.last_fetch_time = datetime.now()
                    
                    # Save geocoding cache
                    self.data_processor.save_cache()
                    
                    # Complete progress
                    progress_bar.progress(100)
                    status_text.text("Data fetch completed successfully!")
                    
                    # Show success message
                    display_success_message(
                        f"Successfully fetched {len(customers_df)} customers and {len(orders_df)} orders!"
                    )
                    
                    # Clear progress indicators after a brief pause
                    import time
                    time.sleep(2)
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Rerun to show analysis tabs
                    st.experimental_rerun()
                    
                finally:
                    loop.close()
                    
        except Exception as e:
            st.error(f"Data fetch failed: {str(e)}")
            st.error("Please check your connection and try again.")
            
            # Show detailed error in expander
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    def render_analysis_tabs(self):
        """Render the main analysis interface with tabs"""
        
        # Get filtered data
        customers_df = st.session_state.get('customers_df', pd.DataFrame())
        orders_df = st.session_state.get('orders_df', pd.DataFrame())
        
        if not customers_df.empty:
            customers_df = self.analyzer.filter_data(customers_df, st.session_state.filters)
        if not orders_df.empty:
            orders_df = self.analyzer.filter_data(orders_df, st.session_state.filters)
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Overview", 
            "🗺️ Geographic Analysis", 
            "👥 Customer Analysis", 
            "📦 Order Analysis",
            "🎯 Clustering",
            "📊 Reports"
        ])
        
        with tab1:
            self.render_overview_tab(customers_df, orders_df)
        
        with tab2:
            self.render_geographic_tab(customers_df, orders_df)
        
        with tab3:
            self.render_customer_tab(customers_df)
        
        with tab4:
            self.render_order_tab(orders_df)
        
        with tab5:
            self.render_clustering_tab(customers_df)
        
        with tab6:
            self.render_reports_tab(customers_df, orders_df)
    
    def render_overview_tab(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame):
        """Render overview tab with key metrics"""
        st.header("📈 Business Overview")
        
        # Calculate metrics
        metrics = self.analyzer.calculate_basic_metrics(customers_df, orders_df)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Customers", format_number(metrics['total_customers']))
            st.metric("Customers with Coordinates", 
                     format_number(metrics['customers_with_coordinates']))
        
        with col2:
            st.metric("Total Orders", format_number(metrics['total_orders']))
            st.metric("Orders with Coordinates", 
                     format_number(metrics['orders_with_coordinates']))
        
        with col3:
            st.metric("Total Revenue", format_currency(metrics['total_revenue']))
            st.metric("Avg Order Value", format_currency(metrics['avg_order_value']))
        
        with col4:
            st.metric("Unique Cities", format_number(metrics['unique_cities']))
            st.metric("Unique Provinces", format_number(metrics['unique_provinces']))
        
        # Data quality indicators
        st.subheader("Data Quality")
        col1, col2 = st.columns(2)
        
        with col1:
            if not customers_df.empty:
                geocoding_rate = (metrics['customers_with_coordinates'] / metrics['total_customers']) * 100
                st.metric("Customer Geocoding Rate", f"{geocoding_rate:.1f}%")
        
        with col2:
            if not orders_df.empty:
                order_geocoding_rate = (metrics['orders_with_coordinates'] / metrics['total_orders']) * 100
                st.metric("Order Geocoding Rate", f"{order_geocoding_rate:.1f}%")
        
        # Quick insights
        if not orders_df.empty:
            st.subheader("Recent Activity")
            recent_orders = orders_df.head(10)
            st.dataframe(
                recent_orders[['order_id', 'total_price', 'created_at', 'shipping_city', 'shipping_province']],
                use_container_width=True
            )
    
    def render_geographic_tab(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame):
        """Render geographic analysis tab"""
        st.header("🗺️ Geographic Analysis")
        
        if customers_df.empty:
            st.warning("No customer data available for geographic analysis")
            return
        
        # Map type selection
        map_type = st.selectbox("Select Map Type", ["Distribution Map", "Heat Map"])
        
        # Create and display map
        if map_type == "Distribution Map":
            map_obj = self.analyzer.create_geographic_distribution_map(customers_df)
        else:
            map_obj = self.analyzer.create_heat_map(customers_df)
        
        # Display map using streamlit-folium
        try:
            from streamlit_folium import st_folium
            st_folium(map_obj, width=700, height=500)
        except ImportError:
            st.error("streamlit-folium not installed. Please install it to view maps.")
        
        # Province and city analysis
        st.subheader("Regional Analysis")
        
        if 'province' in customers_df.columns:
            fig1, fig2 = self.analyzer.create_province_analysis(customers_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                st.plotly_chart(fig2, use_container_width=True)
        
        # Top cities analysis
        if 'city' in customers_df.columns:
            st.subheader("Top Cities")
            fig_cities = self.analyzer.create_top_cities_analysis(customers_df)
            st.plotly_chart(fig_cities, use_container_width=True)
    
    def render_customer_tab(self, customers_df: pd.DataFrame):
        """Render customer analysis tab"""
        st.header("👥 Customer Analysis")
        
        if customers_df.empty:
            st.warning("No customer data available")
            return
        
        # Customer segmentation
        if 'total_spent' in customers_df.columns:
            st.subheader("Customer Segmentation")
            fig_segmentation = self.analyzer.create_customer_segmentation(customers_df)
            st.plotly_chart(fig_segmentation, use_container_width=True)
        
        # Customer details table
        st.subheader("Customer Details")
        
        # Prepare display columns
        display_columns = ['customer_id', 'email', 'first_name', 'last_name', 'city', 'province']
        if 'total_spent' in customers_df.columns:
            display_columns.append('total_spent')
        if 'orders_count' in customers_df.columns:
            display_columns.append('orders_count')
        
        available_columns = [col for col in display_columns if col in customers_df.columns]
        
        if available_columns:
            st.dataframe(
                customers_df[available_columns].head(100),
                use_container_width=True
            )
        
        # Customer statistics
        if 'total_spent' in customers_df.columns:
            st.subheader("Customer Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Customer Value", format_currency(customers_df['total_spent'].mean()))
            with col2:
                st.metric("Median Customer Value", format_currency(customers_df['total_spent'].median()))
            with col3:
                st.metric("Top Customer Value", format_currency(customers_df['total_spent'].max()))
    
    def render_order_tab(self, orders_df: pd.DataFrame):
        """Render order analysis tab"""
        st.header("📦 Order Analysis")
        
        if orders_df.empty:
            st.warning("No order data available")
            return
        
        # Temporal analysis
        if 'created_at' in orders_df.columns:
            st.subheader("Orders Over Time")
            fig_temporal = self.analyzer.create_temporal_analysis(orders_df)
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Order details table
        st.subheader("Recent Orders")
        
        display_columns = ['order_id', 'total_price', 'created_at', 'customer_email', 
                          'shipping_city', 'shipping_province']
        available_columns = [col for col in display_columns if col in orders_df.columns]
        
        if available_columns:
            recent_orders = orders_df.sort_values('created_at', ascending=False).head(50)
            st.dataframe(
                recent_orders[available_columns],
                use_container_width=True
            )
        
        # Order statistics
        if 'total_price' in orders_df.columns:
            st.subheader("Order Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Revenue", format_currency(orders_df['total_price'].sum()))
            with col2:
                st.metric("Average Order Value", format_currency(orders_df['total_price'].mean()))
            with col3:
                st.metric("Total Orders", format_number(len(orders_df)))
    
    def render_clustering_tab(self, customers_df: pd.DataFrame):
        """Render clustering analysis tab"""
        st.header("🎯 Customer Clustering")
        
        if customers_df.empty:
            st.warning("No customer data available for clustering")
            return
        
        # Clustering options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clustering_method = st.selectbox(
                "Clustering Method",
                options=self.config.CLUSTERING_METHODS,
                index=0
            )
        
        with col2:
            n_clusters = st.slider(
                "Number of Clusters",
                min_value=self.config.MIN_CLUSTERS,
                max_value=self.config.MAX_CLUSTERS,
                value=self.config.DEFAULT_CLUSTERS
            )
        
        with col3:
            coordinates_only = st.checkbox("Use coordinates only", value=True)
        
        # Feature selection
        available_features = ['latitude', 'longitude', 'total_spent', 'orders_count']
        if coordinates_only:
            features = ['latitude', 'longitude']
        else:
            features = [f for f in available_features if f in customers_df.columns]
        
        # Perform clustering
        if st.button("Run Clustering Analysis"):
            with st.spinner("Performing clustering analysis..."):
                clustered_df, fig, metrics = self.analyzer.perform_clustering_analysis(
                    customers_df, clustering_method, n_clusters, features
                )
                
                if not clustered_df.empty:
                    # Display results
                    st.subheader("Clustering Results")
                    
                    # Show metrics
                    if metrics:
                        col1, col2 = st.columns(2)
                        with col1:
                            if 'silhouette_score' in metrics:
                                st.metric("Silhouette Score", f"{metrics['silhouette_score']:.3f}")
                        with col2:
                            unique_clusters = clustered_df['cluster'].nunique()
                            st.metric("Clusters Found", unique_clusters)
                    
                    # Show visualization
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show cluster summary
                    cluster_summary = clustered_df.groupby('cluster').agg({
                        'customer_id': 'count',
                        'total_spent': 'mean' if 'total_spent' in clustered_df.columns else 'count',
                        'orders_count': 'mean' if 'orders_count' in clustered_df.columns else 'count'
                    }).reset_index()
                    
                    st.subheader("Cluster Summary")
                    st.dataframe(cluster_summary, use_container_width=True)
                else:
                    st.error("Clustering failed. Please check your data and try again.")
    
    def render_reports_tab(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame):
        """Render reports and export tab"""
        st.header("📊 Reports & Export")
        
        # Generate summary report
        if st.button("Generate Summary Report"):
            with st.spinner("Generating comprehensive report..."):
                report = self.analyzer.create_summary_report(customers_df, orders_df)
                
                # Display report
                st.subheader("📋 Summary Report")
                
                # Data summary
                st.markdown("### Data Summary")
                data_summary = report['data_summary']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Customers", data_summary['total_customers'])
                with col2:
                    st.metric("Total Orders", data_summary['total_orders'])
                
                # Geographic analysis
                if report['geographic_analysis']:
                    st.markdown("### Geographic Coverage")
                    geo_analysis = report['geographic_analysis']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Unique Cities", geo_analysis['unique_cities'])
                    with col2:
                        st.metric("Unique Provinces", geo_analysis['unique_provinces'])
                    with col3:
                        st.metric("Geocoding Coverage", f"{geo_analysis['geocoding_coverage']:.1f}%")
                
                # Customer analysis
                if report['customer_analysis']:
                    st.markdown("### Customer Metrics")
                    customer_analysis = report['customer_analysis']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg Customer Value", format_currency(customer_analysis['avg_customer_value']))
                        st.metric("Total Customer Value", format_currency(customer_analysis['total_customer_value']))
                    with col2:
                        st.metric("Median Customer Value", format_currency(customer_analysis['median_customer_value']))
                        st.metric("Top Customer Value", format_currency(customer_analysis['top_customer_value']))
                
                # Order analysis
                if report['order_analysis']:
                    st.markdown("### Order Metrics")
                    order_analysis = report['order_analysis']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Revenue", format_currency(order_analysis['total_revenue']))
                        st.metric("Avg Order Value", format_currency(order_analysis['avg_order_value']))
                    with col2:
                        st.metric("Median Order Value", format_currency(order_analysis['median_order_value']))
                        st.metric("Order Frequency", f"{order_analysis['order_frequency']:.2f}")
                
                # Download report
                report_json = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="Download Full Report (JSON)",
                    data=report_json,
                    file_name=f"geocommerce_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Raw data preview
        st.subheader("📄 Data Preview")
        
        if not customers_df.empty:
            with st.expander("Customer Data Preview"):
                st.dataframe(customers_df.head(10), use_container_width=True)
        
        if not orders_df.empty:
            with st.expander("Order Data Preview"):
                st.dataframe(orders_df.head(10), use_container_width=True)

def main():
    """Main function to run the Streamlit app"""
    app = GeoCommerceShopifyApp()
    app.run()

if __name__ == "__main__":
    main()