"""
GeoCommerce Shopify Application - Main Streamlit interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import logging

# Import context and helper functions
from .context import GEOCOMMERCE_CONTEXT, get_function_context
from .config import ShopifyConfig, ANALYSIS_CONFIG, ERROR_MESSAGES
from .shopify_connector import ShopifyConnector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoCommerceShopifyApp:
    """
    Main GeoCommerce Shopify application class
    """
    
    def __init__(self):
        self.config = ShopifyConfig()
        self.connector = None
        self._initialize_session_state()
        
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'geocommerce_connected' not in st.session_state:
            st.session_state.geocommerce_connected = False
        if 'geocommerce_data' not in st.session_state:
            st.session_state.geocommerce_data = {}
        if 'geocommerce_config' not in st.session_state:
            st.session_state.geocommerce_config = {}
    
    def render_geocommerce_content(self):
        """
        Main method to render the GeoCommerce content in Streamlit
        """
        # Get function context for display
        context_info = get_function_context('geocommerce')
        if not context_info:
            context_info = GEOCOMMERCE_CONTEXT
        
        # Header
        st.header(context_info['title'], divider='blue')
        st.subheader(context_info['subtitle'])
        
        # --- Main area columns for 'Como usar', connection status, and clear ---
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            st.markdown(context_info['description'])
        
        with col2:
            # Connection status (success or error only)
            self._render_connection_status()
        
        with col3:
            # Clear data button
            if st.button("🗑️ Limpar dados", help="Limpar todos os dados carregados"):
                self._clear_data()
                st.rerun()
        
        # --- Configuration section ---
        st.markdown("---")
        st.subheader("⚙️ Configuração Shopify")
        
        with st.expander("🔧 Configuração da API", expanded=not self._is_configured()):
            self._render_api_configuration()
        
        # --- Main functionality only if configured ---
        if self._is_configured():
            st.markdown("---")
            
            # --- Data fetch section ---
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.subheader("📊 Análise de Dados")
                
                # Analysis type selection
                analysis_type = st.selectbox(
                    "Tipo de análise:",
                    ["Pedidos por Localização", "Clientes por Região", "Performance de Produtos"],
                    help="Selecione o tipo de análise que deseja realizar"
                )
                
                # Filters
                col_filter1, col_filter2 = st.columns([0.5, 0.5])
                with col_filter1:
                    limit = st.number_input(
                        "Limite de registros:",
                        min_value=10,
                        max_value=ANALYSIS_CONFIG['max_limit'],
                        value=ANALYSIS_CONFIG['default_limit'],
                        step=10
                    )
                
                with col_filter2:
                    location_filter = st.text_input(
                        "Filtro de localização (opcional):",
                        placeholder="Ex: province:São Paulo",
                        help="Use filtros como 'province:São Paulo' ou 'city:Rio de Janeiro'"
                    )
            
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("📊 Analisar dados", type="primary"):
                    self._fetch_and_analyze_data(analysis_type, limit, location_filter)
            
            # --- Results display ---
            if st.session_state.geocommerce_data:
                st.markdown("---")
                self._render_analysis_results()
        
        else:
            st.info("🔧 Configure suas credenciais do Shopify para começar a análise.")
    
    def _render_connection_status(self):
        """Render the connection status indicator"""
        if self._is_configured():
            if st.session_state.geocommerce_connected:
                st.success("✅ Conectado")
            else:
                # Test connection button
                if st.button("🔌 Testar conexão", help="Testar conectividade com Shopify"):
                    self._test_connection()
        else:
            st.warning("⚠️ Não configurado")
    
    def _render_api_configuration(self):
        """Render API configuration form"""
        # Shop URL input
        shop_url = st.text_input(
            "Shop URL (sem https://):",
            value=st.session_state.geocommerce_config.get('shop_url', ''),
            placeholder="minha-loja.myshopify.com",
            help="URL da sua loja Shopify (sem https://)"
        )
        
        # Access token input
        access_token = st.text_input(
            "Access Token:",
            value=st.session_state.geocommerce_config.get('access_token', ''),
            type="password",
            help="Token de acesso privado do Shopify"
        )
        
        # API version selection
        api_version = st.selectbox(
            "Versão da API:",
            ["2024-01", "2023-10", "2023-07"],
            index=0,
            help="Versão da API GraphQL do Shopify"
        )
        
        # Save configuration
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            if st.button("💾 Salvar configuração", type="primary"):
                self._save_configuration(shop_url, access_token, api_version)
        
        with col2:
            if st.button("🧪 Testar e salvar"):
                if self._test_and_save_configuration(shop_url, access_token, api_version):
                    st.success("✅ Configuração salva e testada com sucesso!")
                    st.rerun()
    
    def _fetch_and_analyze_data(self, analysis_type: str, limit: int, location_filter: str):
        """Fetch and analyze data based on selected parameters"""
        if not self.connector:
            self.connector = ShopifyConnector(self.config)
        
        try:
            with st.spinner(f"Buscando dados: {analysis_type}..."):
                
                if analysis_type == "Pedidos por Localização":
                    data = self.connector.get_orders_by_location(limit, location_filter)
                    st.session_state.geocommerce_data = {
                        'type': 'orders',
                        'data': data,
                        'processed': self._process_orders_data(data)
                    }
                
                elif analysis_type == "Clientes por Região":
                    data = self.connector.get_customers_by_location(limit, location_filter)
                    st.session_state.geocommerce_data = {
                        'type': 'customers', 
                        'data': data,
                        'processed': self._process_customers_data(data)
                    }
                
                elif analysis_type == "Performance de Produtos":
                    data = self.connector.get_products_performance(limit)
                    st.session_state.geocommerce_data = {
                        'type': 'products',
                        'data': data,
                        'processed': self._process_products_data(data)
                    }
                
                st.success(f"✅ Dados carregados com sucesso! ({len(st.session_state.geocommerce_data.get('processed', []))} registros)")
                
        except Exception as e:
            st.error(f"Erro ao buscar dados: {str(e)}")
            logger.error(f"Error fetching data: {str(e)}")
    
    def _render_analysis_results(self):
        """Render analysis results with charts and tables"""
        data_info = st.session_state.geocommerce_data
        data_type = data_info.get('type')
        processed_data = data_info.get('processed', [])
        
        if not processed_data:
            st.warning(ERROR_MESSAGES['no_data'])
            return
        
        st.subheader("📈 Resultados da Análise")
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(processed_data)
        
        if data_type == 'orders':
            self._render_orders_analysis(df)
        elif data_type == 'customers':
            self._render_customers_analysis(df)
        elif data_type == 'products':
            self._render_products_analysis(df)
        
        # Raw data display
        with st.expander("🔍 Ver dados brutos"):
            st.dataframe(df)
    
    def _render_orders_analysis(self, df: pd.DataFrame):
        """Render orders analysis charts"""
        col1, col2 = st.columns([0.5, 0.5])
        
        with col1:
            # Orders by city
            if 'city' in df.columns:
                city_counts = df['city'].value_counts().head(10)
                fig = px.bar(
                    x=city_counts.index,
                    y=city_counts.values,
                    title="Pedidos por Cidade (Top 10)",
                    labels={'x': 'Cidade', 'y': 'Número de Pedidos'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue by province
            if 'province' in df.columns and 'total_price' in df.columns:
                province_revenue = df.groupby('province')['total_price'].sum().sort_values(ascending=False).head(10)
                fig = px.pie(
                    values=province_revenue.values,
                    names=province_revenue.index,
                    title="Receita por Estado (Top 10)"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_customers_analysis(self, df: pd.DataFrame):
        """Render customers analysis charts"""
        col1, col2 = st.columns([0.5, 0.5])
        
        with col1:
            # Customers by province
            if 'province' in df.columns:
                province_counts = df['province'].value_counts().head(10)
                fig = px.bar(
                    x=province_counts.values,
                    y=province_counts.index,
                    orientation='h',
                    title="Clientes por Estado (Top 10)",
                    labels={'x': 'Número de Clientes', 'y': 'Estado'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Customer distribution map (if coordinates available)
            if 'latitude' in df.columns and 'longitude' in df.columns:
                # Remove rows without coordinates
                map_df = df.dropna(subset=['latitude', 'longitude'])
                if not map_df.empty:
                    fig = px.scatter_mapbox(
                        map_df,
                        lat='latitude',
                        lon='longitude',
                        hover_name='city',
                        hover_data=['province'],
                        title="Distribuição Geográfica de Clientes",
                        mapbox_style="open-street-map",
                        zoom=ANALYSIS_CONFIG['map_default_zoom']
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    def _render_products_analysis(self, df: pd.DataFrame):
        """Render products analysis charts"""
        col1, col2 = st.columns([0.5, 0.5])
        
        with col1:
            # Top products by inventory
            if 'total_inventory' in df.columns:
                top_inventory = df.nlargest(10, 'total_inventory')
                fig = px.bar(
                    top_inventory,
                    x='title',
                    y='total_inventory',
                    title="Produtos com Maior Estoque",
                    labels={'title': 'Produto', 'total_inventory': 'Estoque Total'}
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Products by type
            if 'product_type' in df.columns:
                type_counts = df['product_type'].value_counts()
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Distribuição por Tipo de Produto"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _process_orders_data(self, data: Dict[str, Any]) -> list:
        """Process raw orders data into structured format"""
        processed = []
        edges = data.get('data', {}).get('orders', {}).get('edges', [])
        
        for edge in edges:
            node = edge.get('node', {})
            shipping_addr = node.get('shippingAddress', {})
            total_price_set = node.get('totalPriceSet', {}).get('shopMoney', {})
            
            processed.append({
                'id': node.get('id', ''),
                'name': node.get('name', ''),
                'created_at': node.get('createdAt', ''),
                'total_price': float(total_price_set.get('amount', 0)),
                'currency': total_price_set.get('currencyCode', ''),
                'city': shipping_addr.get('city', ''),
                'province': shipping_addr.get('province', ''),
                'country': shipping_addr.get('country', ''),
                'latitude': shipping_addr.get('latitude'),
                'longitude': shipping_addr.get('longitude')
            })
        
        return processed
    
    def _process_customers_data(self, data: Dict[str, Any]) -> list:
        """Process raw customers data into structured format"""
        processed = []
        edges = data.get('data', {}).get('customers', {}).get('edges', [])
        
        for edge in edges:
            node = edge.get('node', {})
            default_addr = node.get('defaultAddress', {})
            
            processed.append({
                'id': node.get('id', ''),
                'first_name': node.get('firstName', ''),
                'last_name': node.get('lastName', ''),
                'email': node.get('email', ''),
                'created_at': node.get('createdAt', ''),
                'city': default_addr.get('city', ''),
                'province': default_addr.get('province', ''),
                'country': default_addr.get('country', ''),
                'latitude': default_addr.get('latitude'),
                'longitude': default_addr.get('longitude')
            })
        
        return processed
    
    def _process_products_data(self, data: Dict[str, Any]) -> list:
        """Process raw products data into structured format"""
        processed = []
        edges = data.get('data', {}).get('products', {}).get('edges', [])
        
        for edge in edges:
            node = edge.get('node', {})
            
            processed.append({
                'id': node.get('id', ''),
                'title': node.get('title', ''),
                'handle': node.get('handle', ''),
                'product_type': node.get('productType', ''),
                'vendor': node.get('vendor', ''),
                'created_at': node.get('createdAt', ''),
                'updated_at': node.get('updatedAt', ''),
                'total_inventory': node.get('totalInventory', 0)
            })
        
        return processed
    
    def _is_configured(self) -> bool:
        """Check if Shopify API is properly configured"""
        config = st.session_state.geocommerce_config
        return bool(config.get('shop_url') and config.get('access_token'))
    
    def _save_configuration(self, shop_url: str, access_token: str, api_version: str):
        """Save configuration to session state"""
        st.session_state.geocommerce_config = {
            'shop_url': shop_url.strip(),
            'access_token': access_token.strip(), 
            'api_version': api_version
        }
        
        # Update the config object
        self.config.shop_url = shop_url.strip()
        self.config.access_token = access_token.strip()
        self.config.api_version = api_version
        
        st.success("✅ Configuração salva!")
    
    def _test_and_save_configuration(self, shop_url: str, access_token: str, api_version: str) -> bool:
        """Test and save configuration if successful"""
        # Create temporary config for testing
        temp_config = ShopifyConfig()
        temp_config.shop_url = shop_url.strip()
        temp_config.access_token = access_token.strip()
        temp_config.api_version = api_version
        
        # Test connection
        temp_connector = ShopifyConnector(temp_config)
        
        try:
            with st.spinner("Testando conexão..."):
                if temp_connector.test_connection():
                    # Save if successful
                    self._save_configuration(shop_url, access_token, api_version)
                    self.connector = temp_connector
                    st.session_state.geocommerce_connected = True
                    return True
                else:
                    st.error("❌ Falha na conexão. Verifique suas credenciais.")
                    return False
        except Exception as e:
            st.error(f"❌ Erro ao testar conexão: {str(e)}")
            return False
    
    def _test_connection(self):
        """Test current configuration"""
        if not self.connector:
            self.connector = ShopifyConnector(self.config)
        
        try:
            with st.spinner("Testando conexão..."):
                if self.connector.test_connection():
                    st.session_state.geocommerce_connected = True
                    st.success("✅ Conexão bem-sucedida!")
                else:
                    st.session_state.geocommerce_connected = False
                    st.error("❌ Falha na conexão.")
        except Exception as e:
            st.session_state.geocommerce_connected = False
            st.error(f"❌ Erro: {str(e)}")
    
    def _clear_data(self):
        """Clear all loaded data"""
        st.session_state.geocommerce_data = {}
        st.success("🗑️ Dados limpos!")
    
    def run(self):
        """Run the complete Streamlit application"""
        st.set_page_config(
            page_title="GeoCommerce Analytics",
            page_icon="🗺️",
            layout="wide"
        )
        
        self.render_geocommerce_content()