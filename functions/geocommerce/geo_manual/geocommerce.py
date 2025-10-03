"""
GeoCommerce Streamlit Interface
Provides the main Streamlit interface for GeoCommerce analysis within Chat CPG.
"""

import streamlit as st
import pandas as pd
import os
import sys
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integration import GeoCommerceIntegration
from geocommerce_core import GeoCommerce

# Cache the expensive GeoCommerce instance to prevent repeated geocoding API calls
@st.cache_resource
def get_geocommerce():
    """Get cached GeoCommerce instance to minimize token usage"""
    return GeoCommerce()

# Cache analysis results by file content hash to avoid repeated processing
@st.cache_data
def analyze_customer_data(file_content: bytes, analysis_type: str) -> Dict:
    """
    Cache analysis results to avoid repeated processing
    
    Args:
        file_content: Raw file content for hash-based caching
        analysis_type: Type of analysis ('quick', 'comprehensive', 'visualizations')
    
    Returns:
        Analysis results dictionary
    """
    geocommerce = get_geocommerce()
    
    # Create temporary file for processing
    temp_path = f"temp_analysis_{hashlib.md5(file_content).hexdigest()[:8]}.csv"
    with open(temp_path, 'wb') as f:
        f.write(file_content)
    
    try:
        if analysis_type == 'quick':
            integration = GeoCommerceIntegration()
            return integration.get_quick_insights(temp_path)
        elif analysis_type == 'comprehensive':
            integration = GeoCommerceIntegration()
            return integration.analyze_for_chat_cpg(temp_path)
        elif analysis_type == 'visualizations':
            # Generate visualizations and return file paths
            geocommerce.generate_visualizations(temp_path)
            return {'status': 'success', 'message': 'Visualizations generated'}
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def handle_geocommerce_flow(handle_chat_interaction, chain, memory):
    """
    Handle the GeoCommerce analysis flow in Streamlit
    
    Args:
        handle_chat_interaction: Function to handle chat interactions
        chain: LangChain chain for processing
        memory: Conversation memory
    """
    st.title("🌍 GeoCommerce Analysis")
    st.markdown("Analyze customer geography and market opportunities for your e-commerce business.")
    
    # Initialize GeoCommerce (cached)
    try:
        geocommerce = get_geocommerce()
        st.sidebar.success("✅ GeoCommerce ready")
        
        # Show cache information
        show_cache_info()
        
    except Exception as e:
        st.error(f"Error initializing GeoCommerce: {str(e)}")
        return
    
    # Create tabs for different analysis types
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Quick Analysis", 
        "🔍 Comprehensive Analysis", 
        "📈 Visualizations", 
        "💬 Specialized Chat"
    ])
    
    with tab1:
        handle_quick_analysis_tab()
    
    with tab2:
        handle_comprehensive_analysis_tab()
    
    with tab3:
        handle_visualizations_tab()
    
    with tab4:
        handle_specialized_chat_tab(handle_chat_interaction, chain, memory)

def handle_quick_analysis_tab():
    """Handle the quick analysis tab with caching"""
    st.header("Quick Geographic Insights")
    st.markdown("Get rapid insights about your customer geography and market opportunities.")
    
    uploaded_file = st.file_uploader(
        "Upload Shopify Customer Export (CSV)", 
        type=['csv'], 
        key="quick_analysis_upload"
    )
    
    if uploaded_file is not None:
        # Show immediate feedback
        with st.status("Processing quick analysis...", expanded=True) as status:
            status.write("📁 Loading data...")
            
            try:
                # Get file content for caching
                file_content = uploaded_file.getvalue()
                
                status.write("🔍 Analyzing customer geography...")
                insights = analyze_customer_data(file_content, 'quick')
                
                status.write("✅ Analysis complete!")
                status.update(label="Quick analysis completed!", state="complete")
                
                # Display insights
                display_quick_insights(insights)
                
            except Exception as e:
                status.update(label="Analysis failed!", state="error")
                st.error(f"Error during analysis: {str(e)}")

def handle_comprehensive_analysis_tab():
    """Handle the comprehensive analysis tab with caching"""
    st.header("Comprehensive Geographic Analysis")
    st.markdown("Perform detailed analysis with full reports and recommendations.")
    
    uploaded_file = st.file_uploader(
        "Upload Shopify Customer Export (CSV)", 
        type=['csv'], 
        key="comprehensive_analysis_upload"
    )
    
    if uploaded_file is not None:
        # Show immediate feedback
        with st.status("Processing comprehensive analysis...", expanded=True) as status:
            status.write("📁 Loading data...")
            
            try:
                # Get file content for caching
                file_content = uploaded_file.getvalue()
                
                status.write("🔍 Performing comprehensive analysis...")
                results = analyze_customer_data(file_content, 'comprehensive')
                
                status.write("📊 Generating reports...")
                
                status.write("✅ Analysis complete!")
                status.update(label="Comprehensive analysis completed!", state="complete")
                
                # Display comprehensive results
                display_comprehensive_results(results)
                
            except Exception as e:
                status.update(label="Analysis failed!", state="error")
                st.error(f"Error during analysis: {str(e)}")

def handle_visualizations_tab():
    """Handle the visualizations tab with caching"""
    st.header("Geographic Visualizations")
    st.markdown("Explore interactive maps and charts of your customer data.")
    
    uploaded_file = st.file_uploader(
        "Upload Shopify Customer Export (CSV)", 
        type=['csv'], 
        key="visualizations_upload"
    )
    
    if uploaded_file is not None:
        # Show immediate feedback
        with st.status("Generating visualizations...", expanded=True) as status:
            status.write("📁 Loading data...")
            
            try:
                # Get file content for caching
                file_content = uploaded_file.getvalue()
                
                status.write("🗺️ Generating density map...")
                status.write("📊 Creating city performance charts...")
                status.write("🎯 Analyzing customer clusters...")
                
                result = analyze_customer_data(file_content, 'visualizations')
                
                status.write("✅ Visualizations ready!")
                status.update(label="Visualizations generated!", state="complete")
                
                # Display available visualization files
                display_visualization_files()
                
            except Exception as e:
                status.update(label="Visualization generation failed!", state="error")
                st.error(f"Error generating visualizations: {str(e)}")

def handle_specialized_chat_tab(handle_chat_interaction, chain, memory):
    """Handle the specialized chat tab"""
    st.header("GeoCommerce AI Assistant")
    st.markdown("Chat with our AI about your geographic analysis and market opportunities.")
    
    # Initialize session state for chat
    if "geocommerce_messages" not in st.session_state:
        st.session_state.geocommerce_messages = []
    
    # Display chat messages
    for message in st.session_state.geocommerce_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your geographic analysis..."):
        # Add user message to chat history
        st.session_state.geocommerce_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Use the chat interaction handler
                    response = handle_chat_interaction(prompt, chain, memory)
                    st.markdown(response)
                    st.session_state.geocommerce_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.geocommerce_messages.append({"role": "assistant", "content": error_msg})

# Add cache clearing functionality
def clear_geocommerce_cache():
    """Clear all GeoCommerce caches"""
    get_geocommerce.clear()
    analyze_customer_data.clear()
    st.success("Cache cleared! Fresh analysis will be performed.")

# Add cache info to sidebar
def show_cache_info():
    """Show cache information in sidebar"""
    st.sidebar.subheader("Cache Status")
    
    # Get cache info
    geocommerce = get_geocommerce()
    info = geocommerce.get_system_info()
    
    st.sidebar.metric("Cached Coordinates", info['cached_coordinates'])
    st.sidebar.metric("Shopping Locations", info['configured_shoppings'])
    
    if st.sidebar.button("🔄 Clear Cache", help="Clear all cached data for fresh analysis"):
        clear_geocommerce_cache()

def display_quick_insights(insights: Dict):
    """Display quick analysis insights"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Customers", insights.get('total_customers', 0))
    
    with col2:
        st.metric("Total Revenue", f"R$ {insights.get('total_revenue', 0):,.2f}")
    
    with col3:
        st.metric("Unique Cities", insights.get('unique_cities', 0))
    
    # Market insights
    if 'market_insights' in insights:
        st.subheader("Market Insights")
        
        # Top performing cities
        if 'top_performing_cities' in insights['market_insights']:
            st.write("**Top Performing Cities:**")
            for city in insights['market_insights']['top_performing_cities'][:5]:
                st.write(f"• {city}")
        
        # High-value clusters
        if 'high_value_clusters' in insights['market_insights']:
            clusters = insights['market_insights']['high_value_clusters']
            if clusters:
                st.write(f"**High-Value Clusters:** {len(clusters)} identified")
    
    # Recommendations
    if 'recommendations' in insights:
        st.subheader("Recommendations")
        for rec in insights['recommendations'][:3]:  # Show top 3
            with st.expander(f"{rec['title']} ({rec['priority'].title()} Priority)"):
                st.write(rec['description'])
                st.write(f"**Action:** {rec['action']}")

def display_comprehensive_results(results: Dict):
    """Display comprehensive analysis results"""
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", results['geographic_summary']['total_customers'])
    
    with col2:
        st.metric("Total Revenue", f"R$ {results['geographic_summary']['total_revenue']:,.2f}")
    
    with col3:
        st.metric("Unique Cities", results['geographic_summary']['unique_cities'])
    
    with col4:
        st.metric("Avg Order Value", f"R$ {results['geographic_summary']['avg_order_value']:.2f}")
    
    # Detailed insights
    st.subheader("Market Insights")
    
    # Top performing cities
    if results['market_insights']['top_performing_cities']:
        st.write("**Top Performing Cities:**")
        for city in results['market_insights']['top_performing_cities']:
            st.write(f"• {city}")
    
    # High-value clusters
    if results['market_insights']['high_value_clusters']:
        st.write("**High-Value Customer Clusters:**")
        for cluster in results['market_insights']['high_value_clusters']:
            st.write(f"• {cluster.get('location', 'Unknown')}: {cluster.get('high_value_customers', 0)} customers")
    
    # Recommendations
    st.subheader("Strategic Recommendations")
    for rec in results['recommendations']:
        with st.expander(f"{rec['title']} ({rec['priority'].title()} Priority)"):
            st.write(rec['description'])
            st.write(f"**Action:** {rec['action']}")
    
    # Opportunities
    st.subheader("Market Opportunities")
    for opp in results['opportunities']:
        with st.expander(f"{opp['title']} ({opp['potential'].title()} Potential)"):
            st.write(opp['description'])
            st.write(f"**Value Estimate:** {opp['value_estimate']}")
            st.write(f"**Action:** {opp['action']}")
    
    # Data files
    if results['data_files']:
        st.subheader("Generated Reports")
        for file_type, file_path in results['data_files'].items():
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"Download {file_type.replace('_', ' ').title()}",
                        data=f.read(),
                        file_name=os.path.basename(file_path),
                        mime="text/csv"
                    )

def display_visualization_files():
    """Display available visualization files"""
    st.subheader("Generated Visualizations")
    
    # Look for visualization files in the current directory
    viz_files = []
    for file in os.listdir('.'):
        if file.endswith(('.html', '.png', '.jpg', '.jpeg')):
            viz_files.append(file)
    
    if viz_files:
        for file in viz_files:
            if file.endswith('.html'):
                with open(file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # Set width to None for responsiveness
                st.components.v1.html(html_content, height=600, width=None, scrolling=True)
            else:
                st.image(file, caption=file, use_column_width=True)
    else:
        st.info("No visualization files found. Please run the analysis first.")

if __name__ == "__main__":
    # For standalone testing
    st.set_page_config(page_title="GeoCommerce Analysis", layout="wide")
    handle_geocommerce_flow(None, None, None) 