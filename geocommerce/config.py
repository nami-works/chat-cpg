import os
import streamlit as st
from typing import Dict, List, Any
from datetime import datetime, timedelta

class GeoCommerceConfig:
    """Configuration settings for GeoCommerce"""
    
    # App Information
    APP_NAME = "GeoCommerce - Shopify API Integration"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Geographic and commercial analysis of e-commerce data with Shopify API integration"
    
    # Shopify API Settings
    SHOPIFY_API_VERSION = "2024-01"
    SHOPIFY_RATE_LIMIT = 40  # requests per second
    SHOPIFY_MAX_RETRIES = 3
    SHOPIFY_TIMEOUT = 30  # seconds
    
    # Data Fetching Settings
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 250
    INCREMENTAL_UPDATE_DAYS = 7  # Days to look back for incremental updates
    
    # Geocoding Settings
    GEOCODING_TIMEOUT = 10  # seconds
    GEOCODING_RATE_LIMIT = 1  # second between requests for Nominatim
    GEOCODING_CACHE_FILE = "geocommerce/geocoding_cache.json"
    
    # Analysis Settings
    MIN_CUSTOMERS_FOR_ANALYSIS = 10
    MIN_ORDERS_FOR_ANALYSIS = 5
    DEFAULT_MAP_ZOOM = 6
    DEFAULT_MAP_CENTER = [-14.235, -51.925]  # Brazil center
    
    # Export Settings
    MAX_EXPORT_ROWS = 100000
    EXPORT_FORMATS = ["CSV", "Excel", "JSON"]
    
    # UI Settings
    SIDEBAR_WIDTH = 300
    CHART_HEIGHT = 400
    MAP_HEIGHT = 600
    PROGRESS_UPDATE_INTERVAL = 100  # Update progress every N records
    
    # Color Schemes
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'success': '#2ca02c',
        'warning': '#ff7f0e',
        'error': '#d62728',
        'info': '#17a2b8',
        'map_markers': ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink']
    }
    
    # Brazilian States for filtering
    BRAZILIAN_STATES = [
        'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará', 
        'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
        'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará',
        'Paraíba', 'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro',
        'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia', 
        'Roraima', 'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins'
    ]
    
    # Analysis Types
    ANALYSIS_TYPES = {
        'geographic': 'Geographic Analysis',
        'temporal': 'Temporal Analysis', 
        'customer': 'Customer Analysis',
        'product': 'Product Analysis',
        'clustering': 'Clustering Analysis'
    }
    
    # Clustering Settings
    CLUSTERING_METHODS = ['K-Means', 'DBSCAN', 'Hierarchical']
    DEFAULT_CLUSTERS = 5
    MIN_CLUSTERS = 2
    MAX_CLUSTERS = 20
    
    @classmethod
    def get_env_var(cls, var_name: str, default: str = "") -> str:
        """Get environment variable with default"""
        return os.getenv(var_name, default)
    
    @classmethod
    def validate_shopify_credentials(cls) -> Dict[str, Any]:
        """Validate Shopify API credentials"""
        shop_name = cls.get_env_var('SHOPIFY_SHOP_NAME')
        access_token = cls.get_env_var('SHOPIFY_ACCESS_TOKEN')
        api_version = cls.get_env_var('SHOPIFY_API_VERSION', cls.SHOPIFY_API_VERSION)
        
        validation = {
            'valid': False,
            'shop_name': bool(shop_name),
            'access_token': bool(access_token),
            'api_version': bool(api_version),
            'errors': []
        }
        
        if not shop_name:
            validation['errors'].append("SHOPIFY_SHOP_NAME not found in environment")
        if not access_token:
            validation['errors'].append("SHOPIFY_ACCESS_TOKEN not found in environment")
        if not api_version:
            validation['errors'].append("SHOPIFY_API_VERSION not found in environment")
        
        validation['valid'] = len(validation['errors']) == 0
        
        return validation
    
    @classmethod
    def get_cache_settings(cls) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            'geocoding_cache': cls.GEOCODING_CACHE_FILE,
            'session_cache': True,
            'disk_cache': True,
            'ttl_seconds': 3600,  # 1 hour
        }
    
    @classmethod
    def get_date_range_options(cls) -> Dict[str, timedelta]:
        """Get predefined date range options"""
        return {
            'Last 7 days': timedelta(days=7),
            'Last 30 days': timedelta(days=30),
            'Last 90 days': timedelta(days=90),
            'Last 6 months': timedelta(days=180),
            'Last year': timedelta(days=365),
            'All time': None
        }

def init_streamlit_config():
    """Initialize Streamlit page configuration"""
    st.set_page_config(
        page_title=GeoCommerceConfig.APP_NAME,
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': f"""
            # {GeoCommerceConfig.APP_NAME}
            
            Version: {GeoCommerceConfig.APP_VERSION}
            
            {GeoCommerceConfig.APP_DESCRIPTION}
            
            This application provides comprehensive geographic and commercial analysis 
            of e-commerce data through direct Shopify API integration.
            """
        }
    )

def load_custom_css():
    """Load custom CSS for better UI"""
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        border: none;
        background-color: #007bff;
        color: white;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    
    .success-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    
    .sidebar .stSelectbox {
        margin-bottom: 1rem;
    }
    
    .stExpander {
        border: 1px solid #dee2e6;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .stProgress .stProgress-bar {
        background-color: #007bff;
    }
    
    /* Map container styling */
    .folium-map {
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
    
    /* Data table styling */
    .dataframe {
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
    
    /* Chart container styling */
    .js-plotly-plot {
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def display_success_message(message: str):
    """Display a success message"""
    st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)

def display_error_message(message: str):
    """Display an error message"""
    st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)

def display_info_message(message: str):
    """Display an info message"""
    st.markdown(f'<div class="info-message">{message}</div>', unsafe_allow_html=True)

def format_currency(value: float, currency: str = "BRL") -> str:
    """Format currency values"""
    if currency == "BRL":
        return f"R$ {value:,.2f}"
    else:
        return f"{currency} {value:,.2f}"

def format_number(value: int) -> str:
    """Format large numbers with thousand separators"""
    return f"{value:,}"

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate latitude and longitude coordinates"""
    return (
        lat is not None and lng is not None and
        -90 <= lat <= 90 and -180 <= lng <= 180
    )

def get_color_for_metric(value: float, thresholds: Dict[str, float]) -> str:
    """Get color based on metric value and thresholds"""
    if value >= thresholds.get('excellent', 90):
        return GeoCommerceConfig.COLORS['success']
    elif value >= thresholds.get('good', 70):
        return GeoCommerceConfig.COLORS['primary']
    elif value >= thresholds.get('fair', 50):
        return GeoCommerceConfig.COLORS['warning']
    else:
        return GeoCommerceConfig.COLORS['error']

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    return numerator / denominator if denominator != 0 else default

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis"""
    return text[:max_length] + "..." if len(text) > max_length else text

# Session state initialization
def init_session_state():
    """Initialize Streamlit session state variables"""
    default_states = {
        'shopify_data_loaded': False,
        'customers_df': None,
        'orders_df': None,
        'unified_df': None,
        'last_fetch_time': None,
        'connection_tested': False,
        'connection_status': None,
        'api_client': None,
        'cache_info': {
            'customers': 0,
            'orders': 0,
            'geocoding': 0
        },
        'filters': {
            'province': [],
            'city': [],
            'date_range': 'Last 30 days',
            'custom_start_date': None,
            'custom_end_date': None
        },
        'analysis_settings': {
            'clustering_method': 'K-Means',
            'n_clusters': 5,
            'include_coordinates_only': True
        }
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Cache management
@st.cache_data(ttl=3600)
def cached_data_processing(data_hash: str, processing_func, *args, **kwargs):
    """Cache data processing results"""
    return processing_func(*args, **kwargs)

def clear_cache():
    """Clear all Streamlit caches"""
    st.cache_data.clear()
    if 'customers_df' in st.session_state:
        st.session_state.customers_df = None
    if 'orders_df' in st.session_state:
        st.session_state.orders_df = None
    if 'unified_df' in st.session_state:
        st.session_state.unified_df = None
    st.session_state.shopify_data_loaded = False