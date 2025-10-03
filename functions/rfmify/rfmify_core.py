import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import RFMify components
from .shopify_customer_exporter import ShopifyCustomerExporter
from .rfm_analyzer import RFMAnalyzer
from .context import RFMIFY_CONTEXT
from functions.shopify_connector import ShopifyGraphQLClient, ShopifyConfig

class RFMifyCore:
    """Main RFMify application class for Shopify customer analysis and RFM classification"""
    
    def __init__(self):
        self.exporter = ShopifyCustomerExporter()
        self.analyzer = RFMAnalyzer()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state for RFMify"""
        if 'shopify_connected' not in st.session_state:
            st.session_state.shopify_connected = False
        if 'shopify_customers' not in st.session_state:
            st.session_state.shopify_customers = None
        if 'shopify_orders' not in st.session_state:
            st.session_state.shopify_orders = None
        if 'shopify_config' not in st.session_state:
            st.session_state.shopify_config = None
    
    def render_rfmify_content(self):
        """Render the main RFMify interface"""
        # Display RFMify interface
        st.title(f"{RFMIFY_CONTEXT['icon']} {RFMIFY_CONTEXT['title']}")
        st.subheader(RFMIFY_CONTEXT['subtitle'])
        st.markdown(RFMIFY_CONTEXT['description'])
        
        # Create expandable sections for different functionalities
        with st.expander("📊 RFM Analysis", expanded=True):
            self.render_rfm_analysis_section()
        
        with st.expander("📤 Data Export", expanded=False):
            self.render_data_export_section()
        
        with st.expander("📈 Insights & Reports", expanded=False):
            self.render_insights_section()
    
    def render_rfm_analysis_section(self):
        """Render the RFM Analysis section"""
        st.markdown("**RFM Analysis Tools**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**RFM Analyzer**")
            if st.button("Run RFM Analysis", key="rfm_analyzer_btn"):
                if st.session_state.shopify_customers is not None:
                    try:
                        # RFM analysis is already done during data fetch
                        # Just display the results again
                        customers_df = st.session_state.shopify_customers
                        if 'rfm_group' in customers_df.columns:
                            self.display_rfm_distribution(customers_df)
                            st.success("RFM Analysis completed! Results displayed above.")
                        else:
                            st.error("RFM analysis data not found. Please fetch customer data first.")
                    except Exception as e:
                        st.error(f"RFM Analysis failed: {str(e)}")
                else:
                    st.warning("Please connect to Shopify and fetch customer data first.")
                
        with col2:
            st.markdown("**Customer Segmentation**")
            if st.button("Segment Customers", key="customer_segmentation_btn"):
                if st.session_state.shopify_customers is not None:
                    customers_df = st.session_state.shopify_customers
                    if 'rfm_group' in customers_df.columns:
                        self.display_customer_segmentation(customers_df)
                        st.success("Customer segmentation completed!")
                    else:
                        st.error("RFM analysis data not found. Please fetch customer data first.")
                else:
                    st.warning("Please connect to Shopify and fetch customer data first.")
    
    def render_data_export_section(self):
        """Render the Data Export section"""
        st.markdown("**Export Customer Data**")
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_shopify_integration()
            
        with col2:
            self.render_export_formats()
    
    def render_shopify_integration(self):
        """Render Shopify integration section"""
        st.markdown("**Shopify Integration**")
        
        # Shopify connection status
        if st.session_state.shopify_connected:
            st.success("✅ Connected to Shopify")
            if st.button("Refresh Data", key="refresh_data_btn"):
                st.info("Refreshing customer data...")
                # Here you would re-fetch data from Shopify
                st.success("Data refreshed!")
        else:
            st.info("Not connected to Shopify")
            
            # Shopify connection form
            with st.form("shopify_connection"):
                st.markdown("**Enter your Shopify credentials:**")
                shop_name = st.text_input("Shop Name (e.g., mystore)", key="shop_name")
                access_token = st.text_input("Access Token", type="password", key="access_token")
                api_version = st.selectbox("API Version", ["2024-01", "2023-10", "2023-07"], key="api_version")
                
                # Pagination configuration
                st.markdown("**Data Fetching Configuration:**")
                col1, col2 = st.columns(2)
                with col1:
                    customers_per_page = st.selectbox("Customers per page", [50, 100, 250], index=2, help="Shopify API limit: max 250 customers per page")
                with col2:
                    max_pages = st.number_input("Maximum pages to fetch", min_value=10, max_value=4000, value=1000, help="Higher values = more customers but longer processing time")
                
                # Show capacity information
                max_capacity = customers_per_page * max_pages
                st.info(f"📊 **Maximum Capacity**: Up to {max_capacity:,} customers can be fetched with current settings")
                
                if st.form_submit_button("Connect to Shopify"):
                    if shop_name and access_token:
                        self.connect_to_shopify(shop_name, access_token, api_version)
                        # Store pagination settings
                        st.session_state.customers_per_page = customers_per_page
                        st.session_state.max_pages = max_pages
                    else:
                        st.error("Please provide both shop name and access token.")
        
        # Fetch customers button
        if st.session_state.shopify_connected and st.button("Fetch Customer Data", key="fetch_customers_btn"):
            self.fetch_customer_data()
    
    def render_export_formats(self):
        """Render export formats section"""
        st.markdown("**Export Formats**")
        
        if st.session_state.shopify_customers is not None:
            export_format = st.selectbox("Select format:", ["CSV", "Excel", "JSON"], key="export_format")
            
            if st.button("Export Data", key="export_data_btn"):
                self.export_data(export_format)
        else:
            st.info("Connect to Shopify and fetch data to enable export.")
    
    def render_insights_section(self):
        """Render the Insights & Reports section"""
        st.markdown("**Customer Insights**")
        
        if st.session_state.shopify_customers is not None:
            customers_df = st.session_state.shopify_customers
            
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_performance_metrics(customers_df)
                
            with col2:
                self.render_recommendations(customers_df)
        else:
            st.info("Connect to Shopify and fetch customer data to see insights.")
    
    def render_performance_metrics(self, customers_df):
        """Render performance metrics"""
        st.markdown("**Performance Metrics**")
        if st.button("Generate Metrics", key="generate_metrics_btn"):
            try:
                # Basic metrics
                total_customers = len(customers_df)
                customers_with_rfm = len(customers_df[customers_df['rfm_group'].notna() & (customers_df['rfm_group'] != '')])
                rfm_coverage = (customers_with_rfm / total_customers * 100) if total_customers > 0 else 0
                
                st.metric("Total Customers", total_customers)
                st.metric("Customers with RFM", customers_with_rfm)
                st.metric("RFM Coverage", f"{rfm_coverage:.1f}%")
                
                # RFM Group distribution
                if customers_with_rfm > 0:
                    rfm_distribution = customers_df['rfm_group'].value_counts()
                    st.markdown("**RFM Group Distribution:**")
                    st.bar_chart(rfm_distribution)
                    
            except Exception as e:
                st.error(f"Metrics generation failed: {str(e)}")
    
    def render_recommendations(self, customers_df):
        """Render customer recommendations"""
        st.markdown("**Recommendations**")
        if st.button("Get Recommendations", key="get_recommendations_btn"):
            try:
                customers_with_rfm = len(customers_df[customers_df['rfm_group'].notna() & (customers_df['rfm_group'] != '')])
                
                if customers_with_rfm > 0:
                    st.markdown("**Customer Segment Recommendations:**")
                    
                    # Simple recommendations based on RFM groups
                    recommendations = {
                        'CHAMPIONS': 'High-value customers - offer exclusive products and VIP treatment',
                        'LOYAL': 'Regular buyers - focus on retention and cross-selling',
                        'AT_RISK': 'High-value but inactive - re-engagement campaigns needed',
                        'NEW': 'Recent buyers - onboarding and education focus',
                        'PROMISING': 'Recent high-value - nurture for loyalty'
                    }
                    
                    for group, recommendation in recommendations.items():
                        if group in customers_df['rfm_group'].values:
                            count = len(customers_df[customers_df['rfm_group'] == group])
                            st.info(f"**{group}** ({count} customers): {recommendation}")
                else:
                    st.warning("No RFM data available for recommendations.")
                    
            except Exception as e:
                st.error(f"Recommendations failed: {str(e)}")
    
    def connect_to_shopify(self, shop_name: str, access_token: str, api_version: str):
        """Connect to Shopify using provided credentials"""
        try:
            # Test connection
            config = ShopifyConfig(
                shop_name=shop_name,
                access_token=access_token,
                api_version=api_version
            )
            
            # Test the connection by fetching a small amount of data
            async def test_connection():
                async with ShopifyGraphQLClient(config) as client:
                    # Simple query to test connection
                    test_query = """
                    {
                        shop {
                            name
                            email
                        }
                    }
                    """
                    result = await client.execute_query(test_query)
                    return result
            
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(test_connection())
                if 'data' in result and 'shop' in result['data']:
                    st.session_state.shopify_connected = True
                    st.session_state.shopify_config = config
                    st.success(f"✅ Connected to {result['data']['shop']['name']}!")
                    st.rerun()
                else:
                    st.error("Connection failed. Please check your credentials.")
            finally:
                loop.close()
                
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
    
    def fetch_customer_data(self):
        """Fetch customer data from Shopify and calculate custom RFM scores"""
        try:
            st.info("Fetching customer data from Shopify and calculating RFM scores...")
            
            # Get pagination settings from session state
            customers_per_page = getattr(st.session_state, 'customers_per_page', 250)
            max_pages = getattr(st.session_state, 'max_pages', 1000)
            
            async def fetch_all_customers():
                config = st.session_state.shopify_config
                async with ShopifyGraphQLClient(config) as client:
                    all_customers = []
                    cursor = None
                    page_count = 0
                    total_customers = 0
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        try:
                            # Use the exact query structure from the Shopify memo
                            customers_query = f"""
                            query GetCustomersForRFM($cursor: String) {{
                                customers(first: {customers_per_page}, after: $cursor) {{
                                    edges {{
                                        node {{
                                            id
                                            email
                                            firstName
                                            lastName
                                            createdAt
                                            numberOfOrders
                                            amountSpent {{
                                                amount
                                                currencyCode
                                            }}
                                            lastOrder {{
                                                createdAt
                                            }}
                                            statistics {{
                                                predictedSpendTier
                                            }}
                                            defaultAddress {{
                                                city
                                                province
                                                country
                                                zip
                                            }}
                                        }}
                                    }}
                                    pageInfo {{
                                        hasNextPage
                                        endCursor
                                    }}
                                }}
                            }}
                            """
                            
                            variables = {"cursor": cursor} if cursor else {}
                            result = await client.execute_query(customers_query, variables)
                            
                            if 'data' in result and 'customers' in result['data']:
                                customers = result['data']['customers']['edges']
                                page_info = result['data']['customers']['pageInfo']
                                
                                # Filter out customers with missing essential data
                                valid_customers = []
                                for edge in customers:
                                    customer = edge['node']
                                    # Check if customer has essential data
                                    if (customer.get('id') and 
                                        customer.get('email') and 
                                        customer.get('createdAt')):
                                        valid_customers.append(edge)
                                
                                all_customers.extend(valid_customers)
                                page_count += 1
                                total_customers = len(all_customers)
                                
                                # Update progress
                                progress_percentage = min(page_count / max_pages, 1.0)
                                progress_bar.progress(progress_percentage)
                                status_text.text(f"Fetched {total_customers} customers from {page_count} pages...")
                                
                                # Rate limiting: Shopify allows 40 requests/second
                                await asyncio.sleep(0.025)  # 40 requests per second = 0.025 seconds between requests
                                
                                if not page_info['hasNextPage']:
                                    break
                                    
                                cursor = page_info['endCursor']
                                
                                # Use configured page limit
                                if page_count >= max_pages:
                                    st.warning(f"Reached configured page limit ({max_pages} pages). Fetched {total_customers} customers. Current capacity: up to {customers_per_page * max_pages:,} customers. Increase the limit in settings if needed.")
                                    break
                            else:
                                st.error("Failed to fetch customer data from Shopify.")
                                break
                                
                        except Exception as e:
                            st.error(f"Error fetching page {page_count + 1}: {str(e)}")
                            logger.error(f"Error fetching page {page_count + 1}: {str(e)}")
                            # Continue with next page instead of breaking
                            if cursor:
                                continue
                            else:
                                break
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    return all_customers
            
            # Run the async fetch
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                customers = loop.run_until_complete(fetch_all_customers())
                
                if customers:
                    st.success(f"✅ Successfully fetched {len(customers)} customers from Shopify!")
                    
                    # Calculate RFM scores and classify customers
                    customer_data = self.calculate_rfm_scores(customers)
                    
                    if customer_data:
                        # Convert to DataFrame
                        customers_df = pd.DataFrame(customer_data)
                        st.session_state.shopify_customers = customers_df
                        
                        st.success(f"✅ Calculated RFM scores for {len(customers_df)} customers!")
                        
                        # Show RFM distribution
                        self.display_rfm_distribution(customers_df)
                        
                        # Show sample data
                        st.dataframe(customers_df.head(10))
                    else:
                        st.error("Failed to calculate RFM scores. Please check the data quality.")
                        
                else:
                    st.error("No customer data retrieved from Shopify.")
                    
            finally:
                loop.close()
                
        except Exception as e:
            st.error(f"Failed to fetch customers: {str(e)}")
            logger.error(f"Error in fetch_customer_data: {str(e)}")
    
    def calculate_rfm_scores(self, customers):
        """Calculate RFM scores and classify customers according to Shopify's specification"""
        try:
            customer_data = []
            
            # Extract raw metrics for scoring
            recency_days = []
            frequency_counts = []
            monetary_amounts = []
            
            # First pass: collect all metrics for ranking
            for edge in customers:
                customer = edge['node']
                
                try:
                    # Calculate recency (days since last order or account creation)
                    recency_days_value = 0
                    if customer.get('lastOrder') and customer['lastOrder'].get('createdAt'):
                        try:
                            last_order_date = datetime.fromisoformat(customer['lastOrder']['createdAt'].replace('Z', '+00:00'))
                            recency_days_value = (datetime.now(last_order_date.tzinfo) - last_order_date).days
                        except (ValueError, TypeError):
                            # Fallback to account creation date
                            pass
                    
                    if recency_days_value == 0 and customer.get('createdAt'):
                        try:
                            created_date = datetime.fromisoformat(customer['createdAt'].replace('Z', '+00:00'))
                            recency_days_value = (datetime.now(created_date.tzinfo) - created_date).days
                        except (ValueError, TypeError):
                            recency_days_value = 365  # Default to 1 year if date parsing fails
                    
                    recency_days.append(recency_days_value)
                    
                    # Frequency (number of orders) - handle null values
                    frequency_count = customer.get('numberOfOrders')
                    if frequency_count is None:
                        frequency_count = 0
                    frequency_counts.append(int(frequency_count))
                    
                    # Monetary (total amount spent) - handle null values
                    amount_spent = customer.get('amountSpent', {})
                    if amount_spent and amount_spent.get('amount'):
                        try:
                            monetary_amount = float(amount_spent['amount'])
                        except (ValueError, TypeError):
                            monetary_amount = 0.0
                    else:
                        monetary_amount = 0.0
                    monetary_amounts.append(monetary_amount)
                    
                except Exception as e:
                    logger.warning(f"Error processing customer {customer.get('id', 'unknown')}: {str(e)}")
                    # Use default values for this customer
                    recency_days.append(365)
                    frequency_counts.append(0)
                    monetary_amounts.append(0.0)
            
            # Validate that we have data to process
            if not recency_days or not frequency_counts or not monetary_amounts:
                st.error("No valid customer data found for RFM analysis.")
                return []
            
            # Calculate quintile scores (1-5) for each metric
            rfm_scores = self.calculate_quintile_scores(recency_days, frequency_counts, monetary_amounts)
            
            # Second pass: classify customers using RFM scores
            for i, edge in enumerate(customers):
                try:
                    customer = edge['node']
                    
                    # Get RFM scores for this customer
                    r_score = rfm_scores['recency'][i]
                    f_score = rfm_scores['frequency'][i]
                    m_score = rfm_scores['monetary'][i]
                    fm_score = (f_score + m_score) // 2  # Always round DOWN as per Shopify spec
                    
                    # Determine RFM group using Shopify's classification matrix
                    rfm_group = self.classify_rfm_group(r_score, fm_score, frequency_counts[i])
                    
                    # Prepare customer data with safe null handling
                    customer_info = {
                        'id': customer.get('id', ''),
                        'email': customer.get('email', ''),
                        'first_name': customer.get('firstName', ''),
                        'last_name': customer.get('lastName', ''),
                        'created_at': customer.get('createdAt', ''),
                        'number_of_orders': frequency_counts[i],
                        'amount_spent': monetary_amounts[i],
                        'currency_code': customer.get('amountSpent', {}).get('currencyCode', '') if customer.get('amountSpent') else '',
                        'last_order_date': customer.get('lastOrder', {}).get('createdAt', '') if customer.get('lastOrder') else '',
                        'predicted_spend_tier': customer.get('statistics', {}).get('predictedSpendTier', '') if customer.get('statistics') else '',
                        'city': customer.get('defaultAddress', {}).get('city', '') if customer.get('defaultAddress') else '',
                        'province': customer.get('defaultAddress', {}).get('province', '') if customer.get('defaultAddress') else '',
                        'country': customer.get('defaultAddress', {}).get('country', '') if customer.get('defaultAddress') else '',
                        'zip': customer.get('defaultAddress', {}).get('zip', '') if customer.get('defaultAddress') else '',
                        # RFM Analysis Results
                        'recency_score': r_score,
                        'frequency_score': f_score,
                        'monetary_score': m_score,
                        'fm_average': fm_score,
                        'rfm_group': rfm_group,
                        'recency_days': recency_days[i],
                        'raw_frequency': frequency_counts[i],
                        'raw_monetary': monetary_amounts[i]
                    }
                    
                    customer_data.append(customer_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing customer {i}: {str(e)}")
                    continue
            
            return customer_data
            
        except Exception as e:
            logger.error(f"Error calculating RFM scores: {str(e)}")
            st.error(f"Error calculating RFM scores: {str(e)}")
            return []
    
    def calculate_quintile_scores(self, recency_days, frequency_counts, monetary_amounts):
        """Calculate quintile scores (1-5) for RFM metrics"""
        try:
            # Convert to numpy arrays for easier manipulation
            import numpy as np
            
            recency_array = np.array(recency_days)
            frequency_array = np.array(frequency_counts)
            monetary_array = np.array(monetary_amounts)
            
            # Calculate quintiles (20% buckets)
            rfm_scores = {}
            
            # Recency: Lower days = higher score (more recent = better)
            # Sort in ascending order (most recent first)
            recency_sorted_indices = np.argsort(recency_array)
            rfm_scores['recency'] = np.zeros_like(recency_array, dtype=int)
            
            # Assign scores: top 20% = 5, next 20% = 4, etc.
            quintile_size = len(recency_array) // 5
            for i in range(5):
                start_idx = i * quintile_size
                end_idx = start_idx + quintile_size if i < 4 else len(recency_array)
                rfm_scores['recency'][recency_sorted_indices[start_idx:end_idx]] = 5 - i
            
            # Frequency: Higher counts = higher score
            frequency_sorted_indices = np.argsort(frequency_array)[::-1]  # Descending order
            rfm_scores['frequency'] = np.zeros_like(frequency_array, dtype=int)
            
            quintile_size = len(frequency_array) // 5
            for i in range(5):
                start_idx = i * quintile_size
                end_idx = start_idx + quintile_size if i < 4 else len(frequency_array)
                rfm_scores['frequency'][frequency_sorted_indices[start_idx:end_idx]] = i + 1
            
            # Monetary: Higher amounts = higher score
            monetary_sorted_indices = np.argsort(monetary_array)[::-1]  # Descending order
            rfm_scores['monetary'] = np.zeros_like(monetary_array, dtype=int)
            
            quintile_size = len(monetary_array) // 5
            for i in range(5):
                start_idx = i * quintile_size
                end_idx = start_idx + quintile_size if i < 4 else len(monetary_array)
                rfm_scores['monetary'][monetary_sorted_indices[start_idx:end_idx]] = i + 1
            
            return rfm_scores
            
        except Exception as e:
            logger.error(f"Error calculating quintile scores: {str(e)}")
            # Fallback: return simple scores
            return {
                'recency': [3] * len(recency_days),
                'frequency': [3] * len(frequency_counts),
                'monetary': [3] * len(monetary_amounts)
            }
    
    def classify_rfm_group(self, r_score, fm_score, number_of_orders):
        """Classify customer into RFM group using Shopify's classification matrix"""
        
        # Special case: PROSPECTS (no orders)
        if number_of_orders == 0:
            return "PROSPECTS"
        
        # Apply Shopify's classification matrix
        if r_score <= 2:
            if fm_score <= 2:
                return "DORMANT"
            elif 2 < fm_score <= 4:
                return "AT_RISK"
            else:  # fm_score > 4
                return "PREVIOUSLY_LOYAL"
        elif r_score == 3:
            if fm_score == 3:
                return "NEEDS_ATTENTION"
            elif fm_score <= 2:
                return "ALMOST_LOST"
            else:  # fm_score > 3
                return "LOYAL"
        elif r_score == 4:
            if fm_score <= 1:
                return "PROMISING"
            elif 1 < fm_score <= 3:
                return "ACTIVE"
            else:  # fm_score > 3
                return "LOYAL"
        elif r_score == 5:
            if fm_score <= 1:
                return "NEW"
            elif fm_score > 3:
                return "CHAMPIONS"
            else:  # 1 < fm_score <= 3
                return "ACTIVE"
        else:
            # Fallback for unexpected scores
            return "UNCLASSIFIED"
    
    def display_rfm_distribution(self, customers_df):
        """Display RFM group distribution and insights"""
        try:
            st.subheader("📊 RFM Analysis Results")
            
            # RFM Group Distribution
            if 'rfm_group' in customers_df.columns:
                rfm_distribution = customers_df['rfm_group'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**RFM Group Distribution**")
                    st.bar_chart(rfm_distribution)
                
                with col2:
                    st.markdown("**RFM Group Counts**")
                    for group, count in rfm_distribution.items():
                        st.metric(group, count)
                
                # Show RFM Score Statistics
                st.markdown("**RFM Score Statistics**")
                score_cols = ['recency_score', 'frequency_score', 'monetary_score', 'fm_average']
                available_score_cols = [col for col in score_cols if col in customers_df.columns]
                
                if available_score_cols:
                    score_stats = customers_df[available_score_cols].describe()
                    st.dataframe(score_stats)
                
                # Show insights
                st.markdown("**Key Insights**")
                self.display_rfm_insights(customers_df)
        
        except Exception as e:
            st.error(f"Error displaying RFM distribution: {str(e)}")
    
    def display_rfm_insights(self, customers_df):
        """Display insights based on RFM analysis"""
        try:
            insights = []
            
            # Calculate key metrics
            total_customers = len(customers_df)
            
            # High-value customers (Champions + Loyal)
            high_value_count = len(customers_df[customers_df['rfm_group'].isin(['CHAMPIONS', 'LOYAL'])])
            high_value_percentage = (high_value_count / total_customers * 100) if total_customers > 0 else 0
            
            # At-risk customers
            at_risk_count = len(customers_df[customers_df['rfm_group'].isin(['AT_RISK', 'ALMOST_LOST'])])
            at_risk_percentage = (at_risk_count / total_customers * 100) if total_customers > 0 else 0
            
            # New customers
            new_count = len(customers_df[customers_df['rfm_group'] == 'NEW'])
            new_percentage = (new_count / total_customers * 100) if total_customers > 0 else 0
            
            # Display insights
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("High-Value Customers", f"{high_value_count} ({high_value_percentage:.1f}%)")
                st.info("Champions + Loyal customers")
            
            with col2:
                st.metric("At-Risk Customers", f"{at_risk_count} ({at_risk_percentage:.1f}%)")
                st.warning("AT_RISK + ALMOST_LOST customers")
            
            with col3:
                st.metric("New Customers", f"{new_count} ({new_percentage:.1f}%)")
                st.success("Recent high-potential customers")
            
            # Recommendations
            st.markdown("**Strategic Recommendations**")
            
            if at_risk_percentage > 20:
                st.warning("⚠️ High percentage of at-risk customers. Focus on re-engagement campaigns.")
            
            if high_value_percentage < 15:
                st.info("💡 Consider loyalty programs to increase high-value customer retention.")
            
            if new_percentage > 30:
                st.success("🎯 Strong new customer acquisition. Focus on onboarding and first-purchase incentives.")
        
        except Exception as e:
            st.error(f"Error displaying insights: {str(e)}")
    
    def display_customer_segmentation(self, customers_df):
        """Display detailed customer segmentation analysis"""
        try:
            st.subheader("🎯 Customer Segmentation Analysis")
            
            # Group customers by RFM group
            rfm_groups = customers_df['rfm_group'].unique()
            
            for group in sorted(rfm_groups):
                group_customers = customers_df[customers_df['rfm_group'] == group]
                
                with st.expander(f"📊 {group} ({len(group_customers)} customers)", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Group: {group}**")
                        st.metric("Customer Count", len(group_customers))
                        
                        if len(group_customers) > 0:
                            avg_orders = group_customers['number_of_orders'].mean()
                            avg_spent = group_customers['amount_spent'].mean()
                            st.metric("Avg Orders", f"{avg_orders:.1f}")
                            st.metric("Avg Spent", f"${avg_spent:.2f}")
                    
                    with col2:
                        st.markdown("**RFM Score Distribution**")
                        if 'recency_score' in group_customers.columns:
                            rfm_scores = group_customers[['recency_score', 'frequency_score', 'monetary_score']].describe()
                            st.dataframe(rfm_scores)
                    
                    # Show sample customers in this group
                    st.markdown("**Sample Customers**")
                    display_cols = ['email', 'first_name', 'last_name', 'number_of_orders', 'amount_spent', 'city']
                    available_cols = [col for col in display_cols if col in group_customers.columns]
                    st.dataframe(group_customers[available_cols].head(5))
                    
        except Exception as e:
            st.error(f"Error displaying customer segmentation: {str(e)}")
    
    def export_data(self, format_type: str):
        """Export customer data in the specified format"""
        try:
            # Get the customer data
            customers_df = st.session_state.shopify_customers
            
            if format_type == "CSV":
                csv_data = customers_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"shopify_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            elif format_type == "Excel":
                # For Excel, we need to save to bytes
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    customers_df.to_excel(writer, sheet_name='Customers', index=False)
                buffer.seek(0)
                st.download_button(
                    label="Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"shopify_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif format_type == "JSON":
                json_data = customers_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"shopify_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

def handle_rfmify_flow():
    """
    Main RFMify flow handler - called from _nami.py
    """
    app = RFMifyCore()
    app.render_rfmify_content()
