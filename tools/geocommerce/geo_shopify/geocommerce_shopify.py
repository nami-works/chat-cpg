import streamlit as st
import pandas as pd
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback
import json

# Import our modules
from .config import ShopifyConfig, SHOPIFY_QUERIES, ANALYSIS_CONFIG, ERROR_MESSAGES
from tools.shopify_connector import ShopifyGraphQLClient
from .api_data_processor import ShopifyDataProcessor
from .geocommerce_core import GeoCommerceAnalyzer
from tools.geocommerce.context import GEOCOMMERCE_CONTEXT

def init_streamlit_config():
    """Initialize Streamlit configuration for standalone mode"""
    st.set_page_config(
        page_title='GeoCommerce - Shopify Analytics',
        page_icon='🌍',
        layout='wide',
        initial_sidebar_state='expanded'
    )

def clear_cache():
    """Clear all cached data and reset session state"""
    keys_to_clear = [
        'customers_df', 'orders_df', 'unified_df', 'shopify_data_loaded',
        'last_fetch_time', 'connection_status', 'connection_tested',
        'filters', 'geo_filter', 'order_filter', 'customer_filter',
        'date_filter', 'current_filters'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def display_success_message(message: str):
    """Display a success message"""
    st.success(message)

def display_error_message(message: str):
    """Display an error message"""
    st.error(message)

def format_number(value: float) -> str:
    """Format a number with appropriate suffixes (K, M, B)"""
    if pd.isna(value) or value == 0:
        return "0"
    
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:,.0f}"

def format_currency(value: float, currency: str = "BRL") -> str:
    """Format a currency value"""
    if pd.isna(value) or value == 0:
        return f"R$ 0,00"
    
    # Format as Brazilian Real by default
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"${value:,.2f}"

def init_session_state():
    if 'filters' not in st.session_state:
        st.session_state['filters'] = {}
    if 'geo_filter' not in st.session_state:
        st.session_state['geo_filter'] = {}
    if 'order_filter' not in st.session_state:
        st.session_state['order_filter'] = {}
    if 'customer_filter' not in st.session_state:
        st.session_state['customer_filter'] = {}
    if 'date_filter' not in st.session_state:
        st.session_state['date_filter'] = {}
    if 'time_granularity' not in st.session_state:
        st.session_state['time_granularity'] = 'Daily'
    if 'current_filters' not in st.session_state:
        st.session_state['current_filters'] = {}
    if 'connection_status' not in st.session_state:
        st.session_state['connection_status'] = None
    if 'connection_tested' not in st.session_state:
        st.session_state['connection_tested'] = False
    if 'shopify_data_loaded' not in st.session_state:
        st.session_state['shopify_data_loaded'] = False
    if 'customers_df' not in st.session_state:
        st.session_state['customers_df'] = None
    if 'orders_df' not in st.session_state:
        st.session_state['orders_df'] = None
    if 'unified_df' not in st.session_state:
        st.session_state['unified_df'] = None
    if 'last_fetch_time' not in st.session_state:
        st.session_state['last_fetch_time'] = None

class GeoCommerceShopifyApp:
    """Main Streamlit application for GeoCommerce with Shopify API integration"""
    
    def __init__(self):
        self.config = ShopifyConfig.from_env()
        self.analyzer = GeoCommerceAnalyzer()
        self.data_processor = ShopifyDataProcessor()
        # Initialize session state if not already done
        if 'geocommerce_initialized' not in st.session_state:
            init_session_state()
            st.session_state.geocommerce_initialized = True
    
    def run(self):
        """Main application entry point (standalone mode)"""
        # Initialize Streamlit configuration only in standalone mode
        init_streamlit_config()
        init_session_state()
        
        # Sidebar for configuration and controls
        self.render_sidebar()
        
        # Main content area - always show data fetching interface
        if not st.session_state.get('connection_tested', False):
            self.render_connection_setup()
        else:
            # Always show data fetching interface, even after data is loaded
            self.render_data_fetching()
            
            # Show analysis tabs if data is loaded
            if st.session_state.get('shopify_data_loaded', False):
                st.markdown("---")  # Add separator
                self.render_analysis_tabs()
    
    def render_geocommerce_content(self):
        """Render GeoCommerce content within Nami (integrated mode)"""


        # --- Main area columns for 'Como usar', connection status, and clear cache ---
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            st.markdown(GEOCOMMERCE_CONTEXT['description'])
                
        with col2:
            # Connection status (success or error only)
            if st.session_state.get('connection_status'):
                status = st.session_state.connection_status
                if status.get('success'):
                    st.success("✅ Conectado")
                else:
                    st.error("❌ Falha na conexão")
                    st.error(status.get('message', 'Erro desconhecido'))
        with col3:
            # Clear cache button
            if st.button("Limpar Cache"):
                clear_cache()
                st.success("Cache limpo!")
                st.rerun()

        # --- End new columns ---

        # Main content area - always show data fetching interface
        if not st.session_state.get('connection_tested', False):
            self.render_connection_setup()
        else:
            # Always show data fetching interface, even after data is loaded
            self.render_data_fetching()
            
            # Show analysis tabs if data is loaded
            if st.session_state.get('shopify_data_loaded', False):
                st.markdown("---")  # Add separator
                self.render_analysis_tabs()
    
    def render_sidebar(self):
        """Render the sidebar with controls and filters"""
        st.sidebar.header("Configuração")
        
        # Connection status
        if st.session_state.get('connection_status'):
            status = st.session_state.connection_status
            if status.get('success'):
                st.sidebar.success("✅ Conectado")
                shop_info = status.get('shop_info', {})
                st.sidebar.info(f"Loja: {shop_info.get('name', 'Desconhecida')}")
            else:
                st.sidebar.error("❌ Falha na conexão")
                st.sidebar.error(status.get('message', 'Erro desconhecido'))
        
        # Data status
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.success("✅ Dados carregados")
            
            # Data summary
            customers_count = len(st.session_state.customers_df) if st.session_state.customers_df is not None else 0
            orders_count = len(st.session_state.orders_df) if st.session_state.orders_df is not None else 0
            
            st.sidebar.metric("Clientes", customers_count)
            st.sidebar.metric("Pedidos", orders_count)
            
            if st.session_state.last_fetch_time:
                st.sidebar.info(f"Última atualização: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Filters section
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.header("Filtros")
            self.render_filters()
        
        # Cache management
        st.sidebar.header("Gerenciamento de Cache")
        if st.sidebar.button("Limpar Cache"):
            clear_cache()
            st.sidebar.success("Cache limpo!")
            st.rerun()
        
        # Export options
        if st.session_state.get('shopify_data_loaded'):
            st.sidebar.header("Exportar Dados")
            self.render_export_options()
    
    def render_filters(self):
        """Render data filters in the sidebar"""
        
        # Get available options from data
        customers_df = st.session_state.get('customers_df')
        orders_df = st.session_state.get('orders_df')
        
        if customers_df is not None and not customers_df.empty:
            # Country filter
            available_countries = self.config.get_available_countries()
            selected_countries = st.sidebar.multiselect(
                "Selecionar Países",
                options=available_countries,
                default=st.session_state.filters.get('countries', ["Brasil"])
            )
            st.session_state.filters['countries'] = selected_countries
            
            # Province filter - depends on country selection
            if selected_countries:
                if len(selected_countries) == 1:
                    # Single country selected - show only provinces from that country
                    available_provinces = self.config.get_provinces_for_country(selected_countries[0])
                    default_provinces = st.session_state.filters.get('provinces', [])
                    # Filter out provinces that don't belong to the selected country
                    valid_provinces = [p for p in default_provinces if p in available_provinces]
                else:
                    # Multiple countries selected - show all provinces from all selected countries
                    all_provinces = []
                    for country in selected_countries:
                        all_provinces.extend(self.config.get_provinces_for_country(country))
                    available_provinces = sorted(list(set(all_provinces)))
                    valid_provinces = st.session_state.filters.get('provinces', [])
            else:
                available_provinces = []
                valid_provinces = []
            
            selected_provinces = st.sidebar.multiselect(
                "Selecionar Estados",
                options=available_provinces,
                default=valid_provinces
            )
            st.session_state.filters['provinces'] = selected_provinces
            
            # City filter - depends on province selection
            if selected_provinces and selected_countries:
                if len(selected_countries) == 1 and len(selected_provinces) == 1:
                    # Single country and single province - show only cities from that province
                    available_cities = self.config.get_cities_for_province(selected_countries[0], selected_provinces[0])
                    default_cities = st.session_state.filters.get('cities', [])
                    # Filter out cities that don't belong to the selected province
                    valid_cities = [c for c in default_cities if c in available_cities]
                else:
                    # Multiple provinces or countries - show all cities from selected provinces
                    all_cities = []
                    for country in selected_countries:
                        for province in selected_provinces:
                            cities = self.config.get_cities_for_province(country, province)
                            all_cities.extend(cities)
                    available_cities = sorted(list(set(all_cities)))
                    valid_cities = st.session_state.filters.get('cities', [])
            else:
                available_cities = []
                valid_cities = []
            
            selected_cities = st.sidebar.multiselect(
                "Selecionar Cidades",
                options=available_cities,
                default=valid_cities
            )
            st.session_state.filters['cities'] = selected_cities
        
        # Date range filter
        if orders_df is not None and not orders_df.empty and 'created_at' in orders_df.columns:
            date_range_options = list(self.config.get_date_range_options().keys())
            selected_date_range = st.sidebar.selectbox(
                "Período",
                options=date_range_options,
                index=date_range_options.index(st.session_state.filters.get('date_range', 'Últimos 30 dias'))
            )
            st.session_state.filters['date_range'] = selected_date_range
            
            # Custom date range
            if selected_date_range == 'Todo o período':
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    custom_start = st.date_input(
                        "Data Inicial",
                        value=st.session_state.filters.get('custom_start_date'),
                        key="custom_start_date"
                    )
                with col2:
                    custom_end = st.date_input(
                        "Data Final", 
                        value=st.session_state.filters.get('custom_end_date'),
                        key="custom_end_date"
                    )
                st.session_state.filters['custom_start_date'] = custom_start
                st.session_state.filters['custom_end_date'] = custom_end
    
    def render_export_options(self):
        """Render export options in the sidebar"""
        
        export_format = st.sidebar.selectbox(
            "Formato de Exportação",
            options=self.config.EXPORT_FORMATS
        )
        
        if st.sidebar.button("Exportar Dados"):
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
        st.header("🔗 Conexão com API")
        
        # Validate credentials
        credential_validation = self.config.validate_shopify_credentials()
        
        if not credential_validation['valid']:
            st.error("Credenciais da API não encontradas!")
            st.markdown("Certifique-se de que as seguintes variáveis de ambiente estão configuradas:")
            for error in credential_validation['errors']:
                st.markdown(f"- {error}")
            
            with st.expander("Configuração de Variáveis de Ambiente"):
                st.markdown("""
                Crie um arquivo `.env` na raiz do projeto com:
                ```
                SHOPIFY_SHOP_NAME=seu-nome-da-loja
                SHOPIFY_ACCESS_TOKEN=seu-token-de-acesso
                SHOPIFY_API_VERSION=2024-01
                ```
                """)
            return
        
        # Test connection button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Testar Conexão", type="primary"):
                self.test_shopify_connection()
        
        with col2:
            if st.session_state.get('connection_status'):
                status = st.session_state.connection_status
                if status.get('success'):
                    display_success_message(status.get('message', 'Conexão bem-sucedida'))
                else:
                    display_error_message(status.get('message', 'Falha na conexão'))
    
    def test_shopify_connection(self):
        """Test connection to Shopify API"""
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Testando conexão com a API...")
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
                status_text.text("Teste de conexão concluído!")
                
                # Store result in session state
                st.session_state.connection_status = result
                st.session_state.connection_tested = True
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Rerun to update UI
                st.rerun()
                
            finally:
                loop.close()
                
        except Exception as e:
            st.error(f"Teste de conexão falhou: {str(e)}")
            st.session_state.connection_status = {
                'success': False,
                'message': str(e)
            }
    
    def render_data_fetching(self):
        """Render data fetching interface"""
        
        # Show current data status if data is loaded
        if st.session_state.get('shopify_data_loaded', False):
            st.subheader("📊 Configurações de Consulta")
            st.info("💡 Modifique as configurações abaixo e clique em 'Analisar dados' para atualizar os dados com novos filtros.")
            
            # Show current data summary
            customers_count = len(st.session_state.customers_df) if st.session_state.customers_df is not None else 0
            orders_count = len(st.session_state.orders_df) if st.session_state.orders_df is not None else 0
            
            col_status1, col_status2, col_status3 = st.columns(3)
            with col_status1:
                st.metric("Clientes Atuais", format_number(customers_count))
            with col_status2:
                st.metric("Pedidos Atuais", format_number(orders_count))
            with col_status3:
                if st.session_state.last_fetch_time:
                    st.metric("Última Atualização", st.session_state.last_fetch_time.strftime('%H:%M'))
            
            st.markdown("---")

        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        
        with col1:
            # Data fetching options
            data_type = st.selectbox(
                "📊 Usar dados de:",
                options=["Clientes", "Pedidos", "Clientes e Pedidos"],
                index=2,  # Default to "Clientes e Pedidos"
                help=(
                    "Análise de Clientes: Selecione 'Clientes' para distribuição geográfica e segmentação\n"
                    "Análise de Receita: Selecione 'Pedidos' para métricas financeiras e padrões de compra\n"
                    "Análise Completa: Selecione 'Clientes e Pedidos' para insights completos do negócio\n"
                )
            )
            incremental_update = st.checkbox(
                "Atualizar apenas últimos 7 dias",
                value=False,
                help="Atualiza apenas dados recentes, mantendo os dados mais antigos inalterados"
            )
        
        with col2:
            # Date filters
            self.render_date_filters()
        
        with col3:
            # Geographic and Value filters in the same column
            self.render_geographic_filters()

        with col4:
            self.render_order_value_filters()

        with col5:
            self.render_customer_filters()
        
        # Fetch data button
        button_text = "Atualizar dados" if st.session_state.get('shopify_data_loaded', False) else "Carregar dados"
        if st.button(button_text, type="primary"):
                # Convert data type selection to boolean flags
                fetch_customers = data_type in ["Clientes", "Clientes e Pedidos"]
                fetch_orders = data_type in ["Pedidos", "Clientes e Pedidos"]
                
                # Collect filter parameters
                filter_params = self.collect_filter_parameters()
                self.fetch_shopify_data(fetch_customers, fetch_orders, incremental_update, filter_params)
    
    def render_date_filters(self):
        """Render date range filters"""
        # Date range type
        date_range_type = st.selectbox(
            "📅 Períodos",
            options=[
                "Últimos 7 dias",
                "Últimos 30 dias",
                "Últimos 90 dias",
                "Últimos 365 dias",
                "Período personalizado",
                "Todo o período"
                ],
            index=0
        )
        
        if date_range_type == "Últimos 7 dias":
            st.session_state.date_filter = {
                'type': 'last_n_days',
                'days': 7
            }
        elif date_range_type == "Últimos 30 dias":
            st.session_state.date_filter = {
                'type': 'last_n_days',
                'days': 30
            }
        elif date_range_type == "Últimos 90 dias":
            st.session_state.date_filter = {
                'type': 'last_n_days',
                'days': 90
            }
        elif date_range_type == "Últimos 365 dias":
            st.session_state.date_filter = {
                'type': 'last_n_days',
                'days': 365
            }
        elif date_range_type == "Período personalizado":
            start_date = st.date_input("Data Inicial", value=datetime.now() - timedelta(days=30))
            end_date = st.date_input("Data Final", value=datetime.now())
            st.session_state.date_filter = {
                'type': 'custom_range',
                'start_date': start_date,
                'end_date': end_date
            }
        else:  # Todo o período
            st.session_state.date_filter = {
                'type': 'all_time'
            }
    
    def render_geographic_filters(self):
        """Render geographic filters (stacked vertically)"""
        # Country filter
        available_countries = self.config.get_available_countries()
        selected_countries = st.multiselect(
            "🌍 Países",
            options=available_countries,
            default=st.session_state.get('geo_filter', {}).get('countries', ["Brasil"])
        )
        st.session_state.geo_filter = st.session_state.get('geo_filter', {})
        st.session_state.geo_filter['countries'] = selected_countries

        # Province filter
        if selected_countries:
            if len(selected_countries) == 1:
                available_provinces = self.config.get_provinces_for_country(selected_countries[0])
                default_provinces = st.session_state.geo_filter.get('provinces', [])
                valid_provinces = [p for p in default_provinces if p in available_provinces]
            else:
                all_provinces = []
                for country in selected_countries:
                    all_provinces.extend(self.config.get_provinces_for_country(country))
                available_provinces = sorted(list(set(all_provinces)))
                valid_provinces = st.session_state.geo_filter.get('provinces', [])
        else:
            available_provinces = []
            valid_provinces = []

        selected_provinces = st.multiselect(
            "🗺️ Estados",
            options=available_provinces,
            default=valid_provinces
        )
        st.session_state.geo_filter['provinces'] = selected_provinces

        # City filter
        if selected_countries:
            all_provinces = []
            for country in selected_countries:
                all_provinces.extend(self.config.get_provinces_for_country(country))
            all_cities = []
            for country in selected_countries:
                for province in all_provinces:
                    cities = self.config.get_cities_for_province(country, province)
                    all_cities.extend(cities)
            available_cities = sorted(list(set(all_cities)))
            valid_cities = st.session_state.geo_filter.get('cities', [])
        else:
            available_cities = []
            valid_cities = []

        selected_cities = st.multiselect(
            "🌇 Cidades",
            options=available_cities,
            default=valid_cities
        )
        st.session_state.geo_filter['cities'] = selected_cities

        # Geographic radius (for proximity analysis) - optional with checkbox
        limit_radius = st.checkbox(
            "📍 Limitar raio (km)",
            value=st.session_state.geo_filter.get('limit_radius', False),
            help="Ativar para limitar análise por raio geográfico"
        )
        st.session_state.geo_filter['limit_radius'] = limit_radius

        if limit_radius:
            radius_km = st.number_input(
                "Raio Geográfico (km)",
                min_value=1,
                max_value=1000,
                value=st.session_state.geo_filter.get('radius_km', 50),
                help="Para análise baseada em proximidade"
            )
            st.session_state.geo_filter['radius_km'] = radius_km
    
    def render_order_value_filters(self):
        """Render order value filters"""
        # Minimum order value
        min_order_value = st.number_input(
            "Valor Mínimo do Pedido (R$)",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=10.0
        )
        st.session_state.order_filter = st.session_state.get('order_filter', {})
        st.session_state.order_filter['min_value'] = min_order_value
        
        # Maximum order value
        max_order_value = st.number_input(
            "Valor Máximo do Pedido (R$)",
            min_value=0.0,
            max_value=100000.0,
            value=10000.0,
            step=100.0
        )
        st.session_state.order_filter['max_value'] = max_order_value
        
        # Set default order and payment status filters (confirmed and paid orders only)
        st.session_state.order_filter['statuses'] = ["aberto", "fechado", "entregue"]
        st.session_state.order_filter['payment_statuses'] = ["pago", "autorizado"]
    
    def render_customer_filters(self):
        """Render customer-specific filters"""
        # Customer type filter
        customer_types = st.multiselect(
            "Tipos de Cliente",
            options=["novo", "recorrente", "vip", "inativo"],
            default=["novo", "recorrente", "vip"]
        )
        st.session_state.customer_filter = st.session_state.get('customer_filter', {})
        st.session_state.customer_filter['types'] = customer_types
        
        # Customer tags
        customer_tags = st.multiselect(
            "Tags do Cliente",
            options=["atacado", "varejo", "vip", "newsletter", "fidelidade"],
            default=[]
        )
        st.session_state.customer_filter['tags'] = customer_tags
    
    def collect_filter_parameters(self) -> Dict:
        """Collect all filter parameters into a single dictionary"""
        filter_params = {
            'date_filter': st.session_state.get('date_filter', {}),
            'geo_filter': st.session_state.get('geo_filter', {}),
            'order_filter': st.session_state.get('order_filter', {}),
            'customer_filter': st.session_state.get('customer_filter', {}),
            'time_granularity': st.session_state.get('time_granularity', 'Daily')
        }
        
        return filter_params
    
    def apply_filters_to_data(self, df: pd.DataFrame, filter_params: Dict, data_type: str) -> pd.DataFrame:
        """Apply filters to the fetched data"""
        if df.empty or not filter_params:
            return df
        
        filtered_df = df.copy()
        
        # Apply geographic filters
        geo_filter = filter_params.get('geo_filter', {})
        if geo_filter:
            # Country filter
            countries = geo_filter.get('countries', [])
            if countries and 'country' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['country'].isin(countries)]
            
            # Province filter
            provinces = geo_filter.get('provinces', [])
            if provinces and 'province' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['province'].isin(provinces)]
            
            # City filter
            cities = geo_filter.get('cities', [])
            if cities and 'city' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['city'].isin(cities)]
            
            # Radius filter (if enabled)
            if geo_filter.get('limit_radius', False) and 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
                radius_km = geo_filter.get('radius_km', 50)
                # This would require implementing radius-based filtering logic
                # For now, we'll skip this as it requires more complex geospatial calculations
        
        # Apply order value filters (for orders and unified data)
        if data_type in ['orders', 'unified']:
            order_filter = filter_params.get('order_filter', {})
            if order_filter:
                # Order value range
                min_value = order_filter.get('min_value', 0)
                max_value = order_filter.get('max_value', float('inf'))
                
                if 'total_price' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['total_price'] >= min_value) & 
                        (filtered_df['total_price'] <= max_value)
                    ]
        
        # Apply customer filters (for customers and unified data)
        if data_type in ['customers', 'unified']:
            customer_filter = filter_params.get('customer_filter', {})
            if customer_filter:
                # Orders count range
                min_orders = customer_filter.get('min_orders', 0)
                max_orders = customer_filter.get('max_orders', float('inf'))
                
                if 'orders_count' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['orders_count'] >= min_orders) & 
                        (filtered_df['orders_count'] <= max_orders)
                    ]
        
        return filtered_df
    
    def apply_remaining_filters(self, df: pd.DataFrame, filter_params: Dict, data_type: str) -> pd.DataFrame:
        """Apply filters that couldn't be applied at the API level"""
        if df.empty or not filter_params:
            return df
        
        filtered_df = df.copy()
        
        # Note: Geographic filters are now applied at API level for single selections
        # Only apply geographic filters post-fetch for multiple selections or radius filtering
        geo_filter = filter_params.get('geo_filter', {})
        if geo_filter:
            # Apply geographic filters only for multiple selections (not handled at API level)
            countries = geo_filter.get('countries', [])
            if countries and len(countries) > 1 and 'country' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['country'].isin(countries)]
            
            provinces = geo_filter.get('provinces', [])
            if provinces and len(provinces) > 1 and 'province' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['province'].isin(provinces)]
            
            cities = geo_filter.get('cities', [])
            if cities and len(cities) > 1 and 'city' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['city'].isin(cities)]
            
            # Radius filter (always handled post-fetch)
            if geo_filter.get('limit_radius', False) and 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
                radius_km = geo_filter.get('radius_km', 50)
                # This would require implementing radius-based filtering logic
                # For now, we'll skip this as it requires more complex geospatial calculations
        
        # Apply order value filters (for orders and unified data)
        if data_type in ['orders', 'unified']:
            order_filter = filter_params.get('order_filter', {})
            if order_filter:
                # Order value range
                min_value = order_filter.get('min_value', 0)
                max_value = order_filter.get('max_value', float('inf'))
                
                if 'total_price' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['total_price'] >= min_value) & 
                        (filtered_df['total_price'] <= max_value)
                    ]
        
        # Apply customer filters (for customers and unified data)
        if data_type in ['customers', 'unified']:
            customer_filter = filter_params.get('customer_filter', {})
            if customer_filter:
                # Orders count range
                min_orders = customer_filter.get('min_orders', 0)
                max_orders = customer_filter.get('max_orders', float('inf'))
                
                if 'orders_count' in filtered_df.columns:
                    filtered_df = filtered_df[
                        (filtered_df['orders_count'] >= min_orders) & 
                        (filtered_df['orders_count'] <= max_orders)
                    ]
        
        return filtered_df
    
    def get_filter_summary(self, filter_params: Dict) -> str:
        """Generate a summary of applied filters"""
        if not filter_params:
            return ""
        
        summary_parts = []
        
        # Date filter summary
        date_filter = filter_params.get('date_filter', {})
        if date_filter:
            if date_filter.get('type') == 'last_n_days':
                days = date_filter.get('days', 30)
                summary_parts.append(f"Last {days} days")
            elif date_filter.get('type') == 'custom_range':
                start = date_filter.get('start_date')
                end = date_filter.get('end_date')
                if start and end:
                    summary_parts.append(f"{start} to {end}")
        
        # Geographic filter summary
        geo_filter = filter_params.get('geo_filter', {})
        if geo_filter:
            countries = geo_filter.get('countries', [])
            provinces = geo_filter.get('provinces', [])
            cities = geo_filter.get('cities', [])
            
            if countries and countries != ["Brazil"]:
                summary_parts.append(f"Countries: {', '.join(countries)}")
            if provinces and provinces != ["All"]:
                summary_parts.append(f"Provinces: {', '.join(provinces)}")
            if cities and cities != ["All"]:
                summary_parts.append(f"Cities: {', '.join(cities)}")
        
        # Order filter summary
        order_filter = filter_params.get('order_filter', {})
        if order_filter:
            min_val = order_filter.get('min_value', 0)
            max_val = order_filter.get('max_value', 10000)
            if min_val > 0 or max_val < 10000:
                summary_parts.append(f"Order value: R${min_val}-{max_val}")
        
        # Customer filter summary
        customer_filter = filter_params.get('customer_filter', {})
        if customer_filter:
            min_orders = customer_filter.get('min_orders', 0)
            max_orders = customer_filter.get('max_orders', 1000)
            if min_orders > 0 or max_orders < 1000:
                summary_parts.append(f"Orders per customer: {min_orders}-{max_orders}")
        
        return "; ".join(summary_parts) if summary_parts else ""
    
    def get_api_optimization_info(self, filter_params: Dict) -> str:
        """Get information about which filters were optimized at API level"""
        if not filter_params:
            return ""
        
        optimized_parts = []
        
        # Geographic filters applied at API level
        geo_filter = filter_params.get('geo_filter', {})
        if geo_filter:
            countries = geo_filter.get('countries', [])
            provinces = geo_filter.get('provinces', [])
            cities = geo_filter.get('cities', [])
            
            if countries and len(countries) == 1:
                optimized_parts.append(f"Country: {countries[0]}")
            if provinces and len(provinces) == 1:
                optimized_parts.append(f"Province: {provinces[0]}")
            if cities and len(cities) == 1:
                optimized_parts.append(f"City: {cities[0]}")
        
        # Date filters applied at API level
        date_filter = filter_params.get('date_filter', {})
        if date_filter:
            if date_filter.get('type') == 'last_n_days':
                days = date_filter.get('days', 30)
                optimized_parts.append(f"Last {days} days")
            elif date_filter.get('type') == 'custom_range':
                start = date_filter.get('start_date')
                if start:
                    optimized_parts.append(f"From {start}")
        
        return "; ".join(optimized_parts) if optimized_parts else ""
    
    def fetch_shopify_data(self, fetch_customers: bool, fetch_orders: bool, 
                          incremental_update: bool, filter_params: Dict = None):
        """Fetch data from Shopify API"""
        try:
            # Show animated spinner and status updates
            with st.spinner("🔄 Iniciando carregamento de dados..."):
                status_placeholder = st.empty()
                
                # Calculate date for incremental update and apply filters
                updated_since = None
                created_since = None
                
                if incremental_update:
                    updated_since = datetime.now() - timedelta(days=self.config.INCREMENTAL_UPDATE_DAYS)
                
                # Apply date filters if provided
                if filter_params and filter_params.get('date_filter'):
                    date_filter = filter_params['date_filter']
                    if date_filter.get('type') == 'last_n_days':
                        days_back = date_filter.get('days', 30)
                        created_since = datetime.now() - timedelta(days=days_back)
                    elif date_filter.get('type') == 'custom_range':
                        start_date = date_filter.get('start_date')
                        if start_date:
                            created_since = datetime.combine(start_date, datetime.min.time())
                
                # Store filter parameters for later use
                st.session_state.current_filters = filter_params or {}
                
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
                                status_placeholder.info("Carregando clientes do Shopify...")
                                
                                def customer_progress(count, pages):
                                    status_placeholder.info(f"{count} clientes carregados...")
                                
                                # Extract geographic filters for API-level filtering
                                geo_filters = filter_params.get('geo_filter', {}) if filter_params else None
                                
                                customers_data = await client.fetch_all_customers(
                                    updated_since=updated_since,
                                    progress_callback=customer_progress,
                                    geo_filters=geo_filters
                                )
                            
                            # Fetch orders
                            if fetch_orders:
                                status_placeholder.info("Carregando pedidos do Shopify...")
                                
                                def order_progress(count, pages):
                                    status_placeholder.info(f"{count} pedidos carregados...")
                                
                                # Extract filters for API-level filtering (removed order_filters for compatibility)
                                geo_filters = filter_params.get('geo_filter', {}) if filter_params else None
                                
                                orders_data = await client.fetch_all_orders(
                                    created_since=created_since,
                                    progress_callback=order_progress,
                                    geo_filters=geo_filters
                                )
                    
                    # Run the async fetch
                    loop.run_until_complete(fetch_data())
                    
                    # Process the data
                    status_placeholder.info("Processando dados...")
                    
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
                    
                    # Apply remaining filters that couldn't be applied at API level
                    if filter_params:
                        customers_df = self.apply_remaining_filters(customers_df, filter_params, 'customers')
                        orders_df = self.apply_remaining_filters(orders_df, filter_params, 'orders')
                        unified_df = self.apply_remaining_filters(unified_df, filter_params, 'unified')
                    
                    # Save to session state
                    st.session_state.customers_df = customers_df
                    st.session_state.orders_df = orders_df
                    st.session_state.unified_df = unified_df
                    st.session_state.shopify_data_loaded = True
                    st.session_state.last_fetch_time = datetime.now()
                    
                    # Save geocoding cache
                    self.data_processor.save_cache()
                    
                    # Show success
                    status_placeholder.success("Dados carregados com sucesso!")
                    
                    # Show success message with filter summary
                    filter_summary = self.get_filter_summary(filter_params)
                    display_success_message(
                        f"{len(customers_df)} clientes e {len(orders_df)} pedidos carregados!"
                    )
                    
                    # Show filter summary with API optimization info
                    if filter_summary:
                        api_optimized = self.get_api_optimization_info(filter_params)
                        if api_optimized:
                            st.success(f"🚀 API-optimized filters: {api_optimized}")
                        st.info(f"🔍 Applied filters: {filter_summary}")
                    
                    # Brief pause for user to see success
                    time.sleep(2)
                    status_placeholder.empty()
                    
                    # Rerun to show analysis tabs
                    st.rerun()
                
                finally:
                    loop.close()
                    
        except Exception as e:
            st.error(f"Carregamento de dados falhou: {str(e)}")
            st.error("Por favor, verifique sua conexão e tente novamente.")
            
            # Show detailed error in expander
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    def render_analysis_tabs(self):
        """Render the main analysis interface with tabs"""
        
        # Get already filtered data from session state
        customers_df = st.session_state.get('customers_df', pd.DataFrame())
        orders_df = st.session_state.get('orders_df', pd.DataFrame())
        

        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Visão Geral", 
            "🗺️ Análise Geográfica", 
            "👥 Análise de Clientes", 
            "📦 Análise de Pedidos",
            "🎯 Agrupamento",
            "📊 Relatórios"
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
        st.header("📈 Visão Geral do Negócio")
        
        # Calculate metrics
        metrics = self.analyzer.calculate_basic_metrics(customers_df, orders_df)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Clientes", format_number(metrics['total_customers']))
            st.metric("Clientes com Coordenadas", 
                     format_number(metrics['customers_with_coordinates']))
        
        with col2:
            st.metric("Total de Pedidos", format_number(metrics['total_orders']))
            st.metric("Pedidos com Coordenadas", 
                     format_number(metrics['orders_with_coordinates']))
        
        with col3:
            st.metric("Receita Total", format_currency(metrics['total_revenue']))
            st.metric("Valor Médio do Pedido", format_currency(metrics['avg_order_value']))
        
        with col4:
            st.metric("Cidades Únicas", format_number(metrics['unique_cities']))
            st.metric("Estados Únicos", format_number(metrics['unique_provinces']))
        
        # Data quality indicators
        st.subheader("Qualidade dos Dados")
        col1, col2 = st.columns(2)
        
        with col1:
            if not customers_df.empty:
                geocoding_rate = (metrics['customers_with_coordinates'] / metrics['total_customers']) * 100
                st.metric("Taxa de Geocodificação de Clientes", f"{geocoding_rate:.1f}%")
        
        with col2:
            if not orders_df.empty:
                order_geocoding_rate = (metrics['orders_with_coordinates'] / metrics['total_orders']) * 100
                st.metric("Taxa de Geocodificação de Pedidos", f"{order_geocoding_rate:.1f}%")
        
        # Quick insights
        if not orders_df.empty:
            st.subheader("Atividade Recente")
            recent_orders = orders_df.head(10)
            st.dataframe(
                recent_orders[['order_id', 'total_price', 'created_at', 'shipping_city', 'shipping_province']],
                use_container_width=True
            )
    
    def render_geographic_tab(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame):
        """Render geographic analysis tab"""
        st.header("🗺️ Análise Geográfica")
        
        if customers_df.empty:
            st.warning("Nenhum dado de cliente disponível para análise geográfica")
            return
        
        # Map type selection
        map_type = st.selectbox("Selecionar Tipo de Mapa", ["Mapa de Distribuição", "Mapa de Calor"])
        
        # Create and display map
        if map_type == "Mapa de Distribuição":
            map_obj = self.analyzer.create_geographic_distribution_map(customers_df)
        else:
            map_obj = self.analyzer.create_heat_map(customers_df)
        
        # Display map using streamlit-folium
        try:
            from streamlit_folium import st_folium
            st_folium(map_obj, width=700, height=500)
        except ImportError:
            st.error("streamlit-folium não instalado. Por favor, instale para visualizar mapas.")
        
        # Province and city analysis
        st.subheader("Análise Regional")
        
        if 'province' in customers_df.columns:
            fig1, fig2 = self.analyzer.create_province_analysis(customers_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                st.plotly_chart(fig2, use_container_width=True)
        
        # Top cities analysis
        if 'city' in customers_df.columns:
            st.subheader("Principais Cidades")
            fig_cities = self.analyzer.create_top_cities_analysis(customers_df)
            st.plotly_chart(fig_cities, use_container_width=True)
    
    def render_customer_tab(self, customers_df: pd.DataFrame):
        """Render customer analysis tab"""
        st.header("👥 Análise de Clientes")
        
        if customers_df.empty:
            st.warning("Nenhum dado de cliente disponível")
            return
        
        # Customer segmentation
        if 'total_spent' in customers_df.columns:
            st.subheader("Segmentação de Clientes")
            fig_segmentation = self.analyzer.create_customer_segmentation(customers_df)
            st.plotly_chart(fig_segmentation, use_container_width=True)
        
        # Customer details table
        st.subheader("Detalhes dos Clientes")
        
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
            st.subheader("Estatísticas dos Clientes")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Valor Médio do Cliente", format_currency(customers_df['total_spent'].mean()))
            with col2:
                st.metric("Valor Mediano do Cliente", format_currency(customers_df['total_spent'].median()))
            with col3:
                st.metric("Valor do Melhor Cliente", format_currency(customers_df['total_spent'].max()))
    
    def render_order_tab(self, orders_df: pd.DataFrame):
        """Render order analysis tab"""
        st.header("📦 Análise de Pedidos")
        
        if orders_df.empty:
            st.warning("Nenhum dado de pedido disponível")
            return
        
        # Temporal analysis
        if 'created_at' in orders_df.columns:
            st.subheader("Pedidos ao Longo do Tempo")
            fig_temporal = self.analyzer.create_temporal_analysis(orders_df)
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Order details table
        st.subheader("Pedidos Recentes")
        
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
            st.subheader("Estatísticas dos Pedidos")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Receita Total", format_currency(orders_df['total_price'].sum()))
            with col2:
                st.metric("Valor Médio do Pedido", format_currency(orders_df['total_price'].mean()))
            with col3:
                st.metric("Total de Pedidos", format_number(len(orders_df)))
    
    def render_clustering_tab(self, customers_df: pd.DataFrame):
        """Render clustering analysis tab"""
        st.header("🎯 Agrupamento de Clientes")
        
        if customers_df.empty:
            st.warning("Nenhum dado de cliente disponível para agrupamento")
            return
        
        # Clustering options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clustering_method = st.selectbox(
                "Método de Agrupamento",
                options=self.config.CLUSTERING_METHODS,
                index=0
            )
        
        with col2:
            n_clusters = st.slider(
                "Número de Grupos",
                min_value=self.config.MIN_CLUSTERS,
                max_value=self.config.MAX_CLUSTERS,
                value=self.config.DEFAULT_CLUSTERS
            )
        
        with col3:
            coordinates_only = st.checkbox("Usar apenas coordenadas", value=True)
        
        # Feature selection
        available_features = ['latitude', 'longitude', 'total_spent', 'orders_count']
        if coordinates_only:
            features = ['latitude', 'longitude']
        else:
            features = [f for f in available_features if f in customers_df.columns]
        
        # Perform clustering
        if st.button("Executar Análise de Agrupamento"):
            with st.spinner("Executando análise de agrupamento..."):
                clustered_df, fig, metrics = self.analyzer.perform_clustering_analysis(
                    customers_df, clustering_method, n_clusters, features
                )
                
                if not clustered_df.empty:
                    # Display results
                    st.subheader("Resultados do Agrupamento")
                    
                    # Show metrics
                    if metrics:
                        col1, col2 = st.columns(2)
                        with col1:
                            if 'silhouette_score' in metrics:
                                st.metric("Pontuação Silhueta", f"{metrics['silhouette_score']:.3f}")
                        with col2:
                            unique_clusters = clustered_df['cluster'].nunique()
                            st.metric("Grupos Encontrados", unique_clusters)
                    
                    # Show visualization
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show cluster summary
                    cluster_summary = clustered_df.groupby('cluster').agg({
                        'customer_id': 'count',
                        'total_spent': 'mean' if 'total_spent' in clustered_df.columns else 'count',
                        'orders_count': 'mean' if 'orders_count' in clustered_df.columns else 'count'
                    }).reset_index()
                    
                    st.subheader("Resumo dos Grupos")
                    st.dataframe(cluster_summary, use_container_width=True)
                else:
                    st.error("Agrupamento falhou. Verifique seus dados e tente novamente.")
    
    def render_reports_tab(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame):
        """Render reports and export tab"""
        st.header("📊 Relatórios e Exportação")
        
        # Generate summary report
        if st.button("Gerar Relatório Resumido"):
            with st.spinner("Gerando relatório abrangente..."):
                report = self.analyzer.create_summary_report(customers_df, orders_df)
                
                # Display report
                st.subheader("📋 Relatório Resumido")
                
                # Data summary
                st.markdown("### Resumo dos Dados")
                data_summary = report['data_summary']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Clientes", data_summary['total_customers'])
                with col2:
                    st.metric("Total de Pedidos", data_summary['total_orders'])
                
                # Geographic analysis
                if report['geographic_analysis']:
                    st.markdown("### Cobertura Geográfica")
                    geo_analysis = report['geographic_analysis']
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cidades Únicas", geo_analysis['unique_cities'])
                    with col2:
                        st.metric("Estados Únicos", geo_analysis['unique_provinces'])
                    with col3:
                        st.metric("Cobertura de Geocodificação", f"{geo_analysis['geocoding_coverage']:.1f}%")
                
                # Customer analysis
                if report['customer_analysis']:
                    st.markdown("### Métricas dos Clientes")
                    customer_analysis = report['customer_analysis']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Valor Médio do Cliente", format_currency(customer_analysis['avg_customer_value']))
                        st.metric("Valor Total dos Clientes", format_currency(customer_analysis['total_customer_value']))
                    with col2:
                        st.metric("Valor Mediano do Cliente", format_currency(customer_analysis['median_customer_value']))
                        st.metric("Valor do Melhor Cliente", format_currency(customer_analysis['top_customer_value']))
                
                # Order analysis
                if report['order_analysis']:
                    st.markdown("### Métricas dos Pedidos")
                    order_analysis = report['order_analysis']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Receita Total", format_currency(order_analysis['total_revenue']))
                        st.metric("Valor Médio do Pedido", format_currency(order_analysis['avg_order_value']))
                    with col2:
                        st.metric("Valor Mediano do Pedido", format_currency(order_analysis['median_order_value']))
                        st.metric("Frequência de Pedidos", f"{order_analysis['order_frequency']:.2f}")
                
                # Download report
                report_json = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="Baixar Relatório Completo (JSON)",
                    data=report_json,
                    file_name=f"relatorio_geocommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Raw data preview
        st.subheader("📄 Prévia dos Dados")
        
        if not customers_df.empty:
            with st.expander("Prévia dos Dados de Clientes"):
                st.dataframe(customers_df.head(10), use_container_width=True)
        
        if not orders_df.empty:
            with st.expander("Prévia dos Dados de Pedidos"):
                st.dataframe(orders_df.head(10), use_container_width=True)

def main():
    """Main function to run the Streamlit app"""
    app = GeoCommerceShopifyApp()
    app.run()

if __name__ == "__main__":
    main()