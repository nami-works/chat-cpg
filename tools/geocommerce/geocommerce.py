import streamlit as st
import pandas as pd
import sys
import os
import json
import time
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import traceback
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default shopping mall coordinates (can be customized via config)
DEFAULT_SHOPPINGS_COORDS = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

# --- Utility functions ---
def format_number(value: float) -> str:
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
    if pd.isna(value) or value == 0:
        return f"R$ 0,00"
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"${value:,.2f}"

# --- Session state initialization ---
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
    if 'data_loaded' not in st.session_state:
        st.session_state['data_loaded'] = False
    if 'customers_df' not in st.session_state:
        st.session_state['customers_df'] = None
    if 'orders_df' not in st.session_state:
        st.session_state['orders_df'] = None
    if 'unified_df' not in st.session_state:
        st.session_state['unified_df'] = None
    if 'last_fetch_time' not in st.session_state:
        st.session_state['last_fetch_time'] = None
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
    if 'geocoding_cache' not in st.session_state:
        st.session_state['geocoding_cache'] = {}
    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = None

# --- Geocoding and ETL functionality ---
class GeoCommerceETL:
    """Enhanced ETL functionality for GeoCommerce with geocoding capabilities"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent='geocommerce_platform')
        self.shoppings_coords = DEFAULT_SHOPPINGS_COORDS
        self.cache_file = 'geocommerce/coordinates_cache.json'
        self.cache = self.load_coordinates_cache()
        # Update session state with loaded cache
        st.session_state['geocoding_cache'] = self.cache
        # Define retry window (7 days in seconds)
        self.retry_window_days = 7
        self.retry_window_seconds = self.retry_window_days * 24 * 3600
    
    def load_coordinates_cache(self) -> Dict[str, Any]:
        """Load coordinates cache from JSON file with enhanced structure"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Convert legacy format to new format if needed
                cache = {}
                for cep, data in cache_data.items():
                    if isinstance(data, list) and len(data) == 2:
                        # Legacy format: [lat, lng] -> convert to new format
                        cache[cep] = {
                          'coordinates': (data[0], data[1]),
                          'timestamp': datetime.now().isoformat(),
                          'status': 'success'
                        }
                    elif isinstance(data, dict):
                        # New format: already structured
                        if 'coordinates' in data and isinstance(data['coordinates'], list):
                            # Convert list coordinates to tuple
                            data['coordinates'] = (data['coordinates'][0], data['coordinates'][1])
                        cache[cep] = data
                    else:
                        # Invalid format, skip
                        logger.warning(f"Invalid cache entry for CEP {cep}: {data}")
                        continue
                
                logger.info(f"Loaded {len(cache)} coordinates from cache file")
                return cache
            else:
                logger.info("No cache file found, starting with empty cache")
                return {}
        except Exception as e:
            logger.error(f"Error loading coordinates cache: {e}")
            return {}
    
    def save_coordinates_cache(self):
        """Save coordinates cache to JSON file with enhanced structure"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # Load existing cache from file to merge with current session cache
            existing_cache = {}
            if os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        for cep, data in existing_data.items():
                            if isinstance(data, dict):
                                existing_cache[cep] = data
                            elif isinstance(data, list) and len(data) == 2:
                                # Convert legacy format
                                existing_cache[cep] = {
                                  'coordinates': (data[0], data[1]),
                                  'timestamp': datetime.now().isoformat(),
                                  'status': 'success'
                                }
                except Exception as e:
                    logger.warning(f"Error loading existing cache for merge: {e}")
            
            # Merge existing cache with current session cache
            merged_cache = existing_cache.copy()
            for cep, data in self.cache.items():
                if isinstance(data, dict):
                    merged_cache[cep] = data
                elif isinstance(data, tuple) and len(data) == 2:
                    # Convert tuple coordinates to new format
                    merged_cache[cep] = {
                    'coordinates': data,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                    }
            
            # Convert tuples to lists for JSON serialization
            cache_data = {}
            for cep, data in merged_cache.items():
                if isinstance(data, dict):
                    # Convert tuple coordinates to list for JSON serialization
                    if 'coordinates' in data and isinstance(data['coordinates'], tuple):
                        data_copy = data.copy()
                        data_copy['coordinates'] = [data['coordinates'][0], data['coordinates'][1]]
                        cache_data[cep] = data_copy
                    else:
                        cache_data[cep] = data
                else:
                    # Fallback for any remaining tuple data
                    cache_data[cep] = {
                      'coordinates': [data[0], data[1] if isinstance(data, tuple) else data],
                      'timestamp': datetime.now().isoformat(),
                      'status': 'success'
                    }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(cache_data)} coordinates to cache file (merged with existing)")
        except Exception as e:
            logger.error(f"Error saving coordinates cache: {e}")
    
    def should_retry_geocoding(self, cep: str) -> bool:
        """Check if we should retry geocoding for a CEP based on retry window"""
        if cep not in self.cache:
            return True
        
        cache_entry = self.cache[cep]
        
        # If it's a successful entry, no need to retry
        if isinstance(cache_entry, dict) and cache_entry.get('status') == 'success':
            return False
        
        # If its a failed entry, check the timestamp
        if isinstance(cache_entry, dict) and cache_entry.get('status') == 'failed':
            try:
                last_attempt = datetime.fromisoformat(cache_entry['timestamp'])
                time_since_last_attempt = (datetime.now() - last_attempt).total_seconds()
                
                # Retry if enough time has passed
                return time_since_last_attempt >= self.retry_window_seconds
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing timestamp for CEP {cep}: {e}")
                return True
        
        # For legacy format or invalid entries, retry
        return True
    
    def get_coordinates(self, cep: str) -> Tuple[float, float]:
        """Get coordinates for a CEP with intelligent caching and retry logic"""
        # Debug: Log what we're looking for
        logger.info(f"Looking for CEP: '{cep}' in cache (size: {len(self.cache)})")
        
        # Check if we should retry geocoding
        if not self.should_retry_geocoding(cep):
            logger.info(f"Skipping CEP '{cep}' - within retry window")
            cache_entry = self.cache[cep]
            if isinstance(cache_entry, dict) and cache_entry.get('status') == 'success':
                logger.info(f"Cache HIT for CEP: {cep} (success)")
                return cache_entry['coordinates']
            else:
                return (None, None)
        
        # Check cache first for successful entries
        if cep in self.cache:
            cache_entry = self.cache[cep]
            if isinstance(cache_entry, dict) and cache_entry.get('status') == 'success':
                logger.info(f"Cache HIT for CEP: {cep} (success)")
                return cache_entry['coordinates']
            elif isinstance(cache_entry, tuple):
                # Legacy format
                logger.info(f"Cache HIT for CEP: {cep} (legacy format)")
                return cache_entry
        
        logger.info(f"Cache MISS for CEP: {cep} - attempting geocoding")
        
        # If not in cache or failed before, geocode and add to cache
        try:
            location = self.geolocator.geocode(
                {'postalcode': cep, 'country': 'Brazil'}, 
                timeout=5
            )
            
            if location:
                coords = (location.latitude, location.longitude)
                # Add successful result to cache
                self.cache[cep] = {
                   'coordinates': coords,
                   'timestamp': datetime.now().isoformat(),
                   'status': 'success'
                }
                logger.info(f"Successfully geocoded CEP '{cep}': {coords}")
            else:
                coords = (None, None)
                # Add failed attempt to cache with timestamp
                self.cache[cep] = {
                'coordinates': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed'
                }
                logger.warning(f"Failed to geocode CEP '{cep}' - no location found")
                
        except Exception as e:
            logger.warning(f"Error geocoding CEP '{cep}': {e}")
            coords = (None, None)
            # Add failed attempt to cache with timestamp
            self.cache[cep] = {
            'coordinates': None,
            'timestamp': datetime.now().isoformat(),
            'status': 'failed'
            }

        # Update session state
        st.session_state['geocoding_cache'] = self.cache
        
        # Save to file cache immediately for failed attempts, periodically for successes
        if coords == (None, None):
            # Failed attempt - save immediately to preserve the failure record
            self.save_coordinates_cache()
        elif len(self.cache) % 10 == 0:
            # Successful attempt - save periodically
            self.save_coordinates_cache()
        
        # Rate limiting for API calls
        time.sleep(3 + random.random())
        return coords


    def calculate_distance(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates"""
        if None in coords1 or None in coords2:
            return float('inf')
        return round(geodesic(coords1, coords2).km, 2)

    def process_shopify_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process Shopify customer data with geocoding and distance calculations"""
        logger.info("Processing Shopify customer data...")
        
        # Log initial data info
        logger.info(f"Processing {len(df)} rows from uploaded CSV")
        logger.info(f"Columns found: {list(df.columns)}")
        
        # Check for required columns and map them
        column_mapping = {
            'Default Address Zip': 'cep',
            'Total Spent': 'total_spent',
            'Total Orders': 'total_orders',
            'Customer ID': 'customer_id',
            'Default Address City': 'city',
            'Default Address Province': 'state',
            'Email': 'email',
            'First Name': 'first_name',
            'Last Name': 'last_name'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Check for required columns after mapping
        required_columns = ['cep', 'total_spent', 'total_orders']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas obrigatórias não encontradas: {missing_columns}")
            st.info("Colunas esperadas: Default Address Zip, Total Spent, Total Orders")
            return df
        
        # Clean and prepare data
        df['cep'] = df['cep'].astype(str).fillna('')
        df['cep'] = df['cep'].str.replace('-', '').str.strip()
        df['cep'] = df['cep'].str.zfill(8)
        
        # Filter out rows with empty CEPs
        initial_count = len(df)
        df = df[df['cep'] != '00000000'].copy()
        final_count = len(df)
        
        logger.info(f"Filtered out {initial_count - final_count} rows with invalid CEPs")
        logger.info(f"Processing {final_count} valid customer records")
        
        # Convert Total Spent to numeric, handling currency formatting
        df['total_spent'] = df['total_spent'].astype(str).fillna('0')
        df['total_spent'] = pd.to_numeric(
            df['total_spent'].str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        df['total_orders'] = pd.to_numeric(df['total_orders'], errors='coerce').fillna(0)
        
        # Add coordinate columns
        df['latitude'] = None
        df['longitude'] = None
        
        # Process coordinates for unique CEPs
        unique_ceps = df['cep'].unique()
        logger.info(f"Processing {len(unique_ceps)} unique CEPs...")
        
        # Show progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Track successfully processed CEPs
        processed_count = 0
        total_ceps = len(unique_ceps)
        
        for i, cep in enumerate(unique_ceps):
            coords = self.get_coordinates(cep)
            
            # Always count this CEP as processed (success or failure)
            processed_count += 1
            
            # If coordinates were successfully obtained, update DataFrame
            if coords[0] is not None and coords[1] is not None:
                df.loc[df['cep'] == cep, ['latitude', 'longitude']] = [coords[0], coords[1]]
            
            # Update progress every 10 items or always (for responsiveness)
            if i % 10 == 0 or processed_count > 0:
                progress_percentage = (processed_count / total_ceps) * 100
                progress_decimal = processed_count / total_ceps  # Value between 0.0 and 1.0 for st.progress()
                progress_bar.progress(progress_decimal)
                status_text.text(f"{processed_count} of {total_ceps} CEPs processed ({progress_percentage:.1f}%)")
        
        progress_bar.progress(100)
        status_text.text("Geocodificação concluída!")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
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
        if shopping_columns:
            df['nearest_shopping'] = df[shopping_columns].idxmin(axis=1).str.replace('distance_', '')
            df['distance_to_nearest'] = df[shopping_columns].min(axis=1)
        
        # Save cache after processing is complete
        self.save_coordinates_cache()
        
        logger.info("Shopify data processing completed!")
        return df

# --- Main App Class ---
class GeoCommerceManualApp:
    def __init__(self):
        self.etl = GeoCommerceETL()
        if 'geocommerce_initialized' not in st.session_state:
            init_session_state()
            st.session_state.geocommerce_initialized = True

    def run(self):
        st.set_page_config(
            page_title='GeoCommerce - Manual Analytics',
            page_icon='🌍',
            layout='wide',
            initial_sidebar_state='expanded'
        )
        init_session_state()
        self.render_sidebar()
        self.render_data_upload()
        if st.session_state.get('data_loaded', False):
            st.markdown("---")
            self.render_analysis_tabs()

    def render_geocommerce_content(self):
        """Render GeoCommerce content within Nami (integrated mode)"""
        # Render sidebar for filters and export options
        self.render_sidebar()
        # Render main content
        self.render_data_upload()
        if st.session_state.get('data_loaded', False):
            st.markdown("---")
            self.render_analysis_tabs()

    def render_sidebar(self):
        st.sidebar.header("Configuração")
        if st.session_state.get('data_loaded'):
            st.sidebar.success("✅ Dados carregados")
            customers_count = len(st.session_state.customers_df) if st.session_state.customers_df is not None else 0
            st.sidebar.metric("Clientes", customers_count)
            if st.session_state.last_fetch_time:
                st.sidebar.info(f"Última atualização: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M')}")
        
        st.sidebar.header("Filtros")
        if st.session_state.get('data_loaded'):
            self.render_filters()
        st.sidebar.header("Gerenciamento de Cache")
        if st.sidebar.button("Limpar Cache"):
            self.clear_cache()
            st.sidebar.success("Cache limpo!")
            st.rerun()
        if st.session_state.get('data_loaded'):
            st.sidebar.header("Exportar Dados")
            self.render_export_options()

    def render_data_upload(self):
        st.header("📁 Upload de Dados (CSV)")
        
        # Show expected format
        with st.expander("📋 Formato esperado do CSV", expanded=False):
            st.markdown("""
            **Colunas obrigatórias:**
            - `Default Address Zip` - CEP do cliente
            - `Total Spent` - Valor total gasto
            - `Total Orders` - Número total de pedidos
            
            **Colunas opcionais:**
            - `Customer ID` - ID do cliente
            - `Default Address City` - Cidade
            - `Default Address Province` - Estado
            - `Email` - Email do cliente
            - `First Name` - Nome
            - `Last Name` - Sobrenome
            """)
        
        uploaded_file = st.file_uploader(
            "Faça upload do arquivo de clientes (CSV exportado do Shopify ou compatível)",
            type=['csv'],
            key="manual_data_upload"
        )
        
        if uploaded_file is not None:
            try:
                # Load raw data
                df = pd.read_csv(uploaded_file)
                st.success(f"Dados carregados: {df.shape[0]} linhas, {df.shape[1]} colunas.")
                
                # Process data with ETL
                if st.button("🔄 Analisar dados", type="primary"):
                    with st.spinner("Processando dados..."):
                        processed_df = self.etl.process_shopify_data(df)
                        
                        # Store processed data
                        st.session_state.customers_df = processed_df
                        st.session_state.orders_df = pd.DataFrame()  # No orders in manual mode
                        st.session_state.unified_df = processed_df  # For compatibility
                        st.session_state.data_loaded = True
                        st.session_state.last_fetch_time = datetime.now()
                        st.session_state.uploaded_file = uploaded_file
                        st.session_state.processed_data = processed_df
                        
                        st.success("✅ Dados processados com sucesso!")
                        
                        # Show processing results
                        geocoded_count = processed_df[processed_df['latitude'].notna()].shape[0]
                        total_count = len(processed_df)
                        geocoding_rate = (geocoded_count / total_count) * 100
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total de registros", total_count)
                        with col2:
                            st.metric("Geocodificados", geocoded_count)
                        with col3:
                            st.metric("Taxa de sucesso", f"{geocoding_rate:.1f}%")
                        
                        # Show processed data preview
                        with st.expander("📄 Prévia dos dados processados", expanded=False):
                            display_cols = ['customer_id', 'cep', 'city', 'state', 'total_spent', 'latitude', 'longitude', 'nearest_shopping']
                            available_cols = [col for col in display_cols if col in processed_df.columns]
                            st.dataframe(processed_df[available_cols].head(5), use_container_width=True)
                        
                        st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao carregar o arquivo: {str(e)}")
                st.error("Verifique se o arquivo está no formato correto.")

    def render_filters(self):
        df = st.session_state.get('customers_df')
        if df is not None and not df.empty:
            # State filter
            if 'state' in df.columns:
                states = sorted(df['state'].dropna().unique())
                selected_states = st.sidebar.multiselect(
                    "Selecionar Estados",
                    options=states,
                    default=st.session_state.filters.get('states', states[:3])
                )
                st.session_state.filters['states'] = selected_states
            
            # City filter
            if 'city' in df.columns:
                cities = sorted(df['city'].dropna().unique())
                selected_cities = st.sidebar.multiselect(
                    "Selecionar Cidades",
                    options=cities,
                    default=st.session_state.filters.get('cities', cities[:3])
                )
                st.session_state.filters['cities'] = selected_cities
            
            # Shopping mall filter
            if 'nearest_shopping' in df.columns:
                shoppings = sorted(df['nearest_shopping'].dropna().unique())
                selected_shoppings = st.sidebar.multiselect(
                    "Selecionar Shopping Centers",
                    options=shoppings,
                    default=st.session_state.filters.get('shoppings', shoppings[:3])
                )
                st.session_state.filters['shoppings'] = selected_shoppings

    def render_export_options(self):
        export_format = st.sidebar.selectbox(
            "Formato de Exportação",
            options=["CSV", "JSON"]
        )
        if st.sidebar.button("Exportar Dados"):
            self.export_data(export_format)

    def export_data(self, format_type: str):
        try:
            df = st.session_state.get('customers_df')
            if df is not None and not df.empty:
                if format_type == "CSV":
                    export_data = df.to_csv(index=False).encode('utf-8')
                    mime = 'text/csv'
                else:
                    export_data = df.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8')
                    mime = 'application/json'
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geocommerce_export_{timestamp}.{format_type.lower()}"
                st.sidebar.download_button(
                    label=f"Download {format_type}",
                    data=export_data,
                    file_name=filename,
                    mime=mime
                )
                st.sidebar.success(f"Export pronto para download!")
            else:
                st.sidebar.warning("Nenhum dado para exportar com os filtros atuais")
        except Exception as e:
            st.sidebar.error(f"Falha na exportação: {str(e)}")

    def clear_cache(self):
        """Clear session cache"""
        st.session_state.clear()
        init_session_state()
        
    def render_analysis_tabs(self):
        df = st.session_state.get('customers_df', pd.DataFrame())
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Visão Geral",
            "🗺️ Análise Geográfica",
            "👥 Análise de Clientes",
            "🎯 Agrupamento",
            "📊 Relatórios"
        ])
        with tab1:
            self.render_overview_tab(df)
        with tab2:
            self.render_geographic_tab(df)
        with tab3:
            self.render_customer_tab(df)
        with tab4:
            self.render_clustering_tab(df)
        with tab5:
            self.render_reports_tab(df)

    def render_overview_tab(self, df: pd.DataFrame):
        st.header("📈 Visão Geral do Negócio")
        if df.empty:
            st.info("Carregue um arquivo CSV para ver os dados.")
            return
        
        # Calculate basic metrics from the DataFrame
        total_customers = len(df)
        total_revenue = df['total_spent'].sum() if 'total_spent' in df.columns else 0
        unique_cities = df['city'].nunique() if 'city' in df.columns else 0
        unique_states = df['state'].nunique() if 'state' in df.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Clientes", format_number(total_customers))
        with col2:
            st.metric("Total de Pedidos", format_number(df['total_orders'].sum() if 'total_orders' in df.columns else total_customers))
        with col3:
            st.metric("Receita Total", format_currency(total_revenue))
        with col4:
            st.metric("Cidades Únicas", format_number(unique_cities))
        
        # Data quality indicators
        st.subheader("Qualidade dos Dados")
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'total_spent' in df.columns:
                st.metric("Valor Médio do Cliente", format_currency(df['total_spent'].mean()))
        with col2:
            if 'total_orders' in df.columns:
                st.metric("Pedidos por Cliente", f"{df['total_orders'].mean():.1f}")
        with col3:
            if 'latitude' in df.columns:
                geocoded_count = df[df['latitude'].notna()].shape[0]
                geocoding_rate = (geocoded_count / total_customers) * 100
                st.metric("Taxa de Geocodificação", f"{geocoding_rate:.1f}%")

    def render_geographic_tab(self, df: pd.DataFrame):
        st.header("🗺️ Análise Geográfica")
        if df.empty:
            st.warning("Nenhum dado disponível para análise geográfica")
            return
        
        # Check if we have coordinates data
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            st.warning("Dados de coordenadas não encontrados. Certifique-se de que os dados foram geocodificados.")
            return
        
        # Filter data with valid coordinates
        valid_coords_df = df[df['latitude'].notna() & df['longitude'].notna()].copy()
        
        if valid_coords_df.empty:
            st.warning("Nenhum dado com coordenadas válidas encontrado.")
            return
        
        # Geographic metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Clientes Geocodificados", len(valid_coords_df))
        with col2:
            geocoding_rate = (len(valid_coords_df) / len(df)) * 100

        # Interactive Map Visualization
        st.subheader("🗺️ Mapa Interativo de Densidade de Clientes")
        
        try:
            import folium
            from folium import plugins
            
            # Create base map centered on Brazil
            m = folium.Map(
                location=[-15.7801, -47.9292],  # Brasília
                zoom_start=5,
                tiles='OpenStreetMap'
            )
            
            # Group data by CEP for density analysis
            if 'cep' in valid_coords_df.columns:
                cep_analysis = valid_coords_df.groupby('cep').agg({
                    'customer_id': 'count',
                    'total_spent': 'sum',
                    'latitude': 'first',
                    'longitude': 'first',
                    'nearest_shopping': 'first'
                }).reset_index()
                
                # Flatten column names if they are multi-level
                if isinstance(cep_analysis.columns, pd.MultiIndex):
                    cep_analysis.columns = [col[1] if col[1] else col[0] for col in cep_analysis.columns]
                
                # Add density categories
                def categorize_density(customer_count):
                    if customer_count >= 10:
                        return 'Muito Alta'
                    elif customer_count >= 5:
                        return 'Alta'
                    elif customer_count >= 2:
                        return 'Média'
                    else:
                        return 'Baixa'
                
                cep_analysis['density_category'] = cep_analysis['customer_id'].apply(categorize_density)
                
                # Color mapping for density categories
                color_map = {
                    'Muito Alta': 'red',
                    'Alta': 'orange', 
                    'Média': 'yellow',
                    'Baixa': 'green'
                }
                
                # Add markers to map
                for _, row in cep_analysis.iterrows():
                    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                        color = color_map.get(row['density_category'], 'blue')
                        
                        # Popup content
                        popup_content = f"""
                        <b>CEP: {row['cep']}</b><br>
                        Clientes: {row['customer_id']}<br>
                        Receita: R$ {row['total_spent']:,.2f}<br>
                        Densidade: {row['density_category']}<br>
                        Shopping Mais Próximo: {row['nearest_shopping']}
                        """
                        
                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=row['customer_id'] * 2,  # Size based on customer count
                            popup=popup_content,
                            color=color,
                            fill=True,
                            fillOpacity=0.7
                        ).add_to(m)
                
                # Add shopping mall markers
                for shopping, coords in self.etl.shoppings_coords.items():
                    folium.Marker(
                        location=coords,
                        popup=f"<b>{shopping}</b><br>Shopping Center",
                        icon=folium.Icon(color='red', icon='shopping-cart')
                    ).add_to(m)
                
                # Add legend
                legend_html = '''
                <div style="position: fixed; 
                            bottom: 50px; left: 50px; width: 200px; height: 120px; 
                            background-color: white; border:2px solid grey; z-index:9999; 
                            font-size:14px; padding: 10px">
                <p><b>Densidade de Clientes</b></p>
                <p><i class="fa fa-circle" style="color:red"></i> Muito Alta (10+ clientes)</p>
                <p><i class="fa fa-circle" style="color:orange"></i> Alta (5-9 clientes)</p>
                <p><i class="fa fa-circle" style="color:yellow"></i> Média (2-4 clientes)</p>
                <p><i class="fa fa-circle" style="color:green"></i> Baixa (1 cliente)</p>
                <p><i class="fa fa-shopping-cart" style="color:red"></i> Shopping Center</p>
                </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
                
                # Display the map
                st.components.v1.html(m._repr_html_(), height=600)
                
                # Show density statistics
                st.subheader("📊 Estatísticas de Densidade por CEP")
                density_stats = cep_analysis.groupby('density_category').agg({
                    'customer_id': ['count', 'sum'],
                    'total_spent': 'sum'
                }).round(2)
                density_stats.columns = ['CEPs', 'Total Clientes', 'Receita Total']
                st.dataframe(density_stats, use_container_width=True)
                
            else:
                # Fallback: show individual customer markers
                for _, row in valid_coords_df.iterrows():
                    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                        popup_content = f"""
                        <b>Cliente: {row.get('customer_id', 'N/A')}</b><br>
                        CEP: {row.get('cep', 'N/A')}<br>
                        Receita: R$ {row.get('total_spent', 0):,.2f}<br>
                        Shopping: {row.get('nearest_shopping', 'N/A')}
                        """
                        
                        folium.CircleMarker(
                            location=[row['latitude'], row['longitude']],
                            radius=5,
                            popup=popup_content,
                            color='blue',
                            fill=True,
                            fillOpacity=0.6
                        ).add_to(m)
                
                st.components.v1.html(m._repr_html_(), height=600)
                
        except ImportError:
            st.warning("📦 Biblioteca 'folium' não encontrada. Para visualizar o mapa interativo, instale com: `pip install folium`")
            st.info("Mapa interativo indisponível. Mostrando dados em formato tabular.")
        except Exception as e:
            st.error(f"❌ Erro ao criar mapa interativo: {str(e)}")
            st.info("Mapa interativo indisponível. Mostrando dados em formato tabular.")

    def render_customer_tab(self, df: pd.DataFrame):
        st.header("👥 Análise de Clientes")
        if df.empty:
            st.warning("Nenhum dado de cliente disponível")
            return
        
        display_columns = ['customer_id', 'email', 'first_name', 'last_name', 'city', 'state', 'total_spent', 'total_orders', 'nearest_shopping']
        available_columns = [col for col in display_columns if col in df.columns]
        if available_columns:
            st.dataframe(df[available_columns].head(100), use_container_width=True)
        
        if 'total_spent' in df.columns:
            st.subheader("Estatísticas dos Clientes")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor Médio do Cliente", format_currency(df['total_spent'].mean()))
            with col2:
                st.metric("Valor Mediano do Cliente", format_currency(df['total_spent'].median()))
            with col3:
                st.metric("Valor do Melhor Cliente", format_currency(df['total_spent'].max()))

    def render_clustering_tab(self, df: pd.DataFrame):
        st.header("🎯 Agrupamento de Clientes")
        if df.empty:
            st.warning("Nenhum dado de cliente disponível para agrupamento")
            return
        
        # Check if we have the necessary data for clustering
        if 'total_spent' not in df.columns:
            st.warning("Dados de gastos não encontrados. Certifique-se de que o CSV contém a coluna 'total_spent'.")
            return
        
        # Customer segmentation based on spending
        st.subheader("Segmentação por Valor Gasto")
        
        # Define spending categories
        spending_categories = {
            'Baixo': (0, 100),
            'Médio': (100, 500),
            'Alto': (500, 1000),
            'Premium': (1000, float('inf'))
        }
        
        # Categorize customers
        def categorize_spending(spent):
            for category, (min_val, max_val) in spending_categories.items():
                if min_val <= spent < max_val:
                    return category
            return 'Premium'
        
        df_with_categories = df.copy()
        df_with_categories['spending_category'] = df_with_categories['total_spent'].apply(categorize_spending)
        
        # Show segmentation results
        category_counts = df_with_categories['spending_category'].value_counts()
        st.bar_chart(category_counts)
        
        # Category statistics
        st.subheader("Estatísticas por Categoria")
        category_stats = df_with_categories.groupby('spending_category').agg({
            'total_spent': ['count', 'mean', 'sum'],
            'total_orders': 'mean' if 'total_orders' in df.columns else 'count'
        }).round(2)
        
        st.dataframe(category_stats)
        
        # Geographic distribution by category
        if 'city' in df.columns:
            st.subheader("Distribuição Geográfica por Categoria")
            geo_category = df_with_categories.groupby(['city', 'spending_category']).size().unstack(fill_value=0)
            st.dataframe(geo_category.head(10))
        
        # Shopping mall analysis by category
        if 'nearest_shopping' in df.columns:
            st.subheader("Análise por Shopping Centers e Categoria")
            shopping_category = df_with_categories.groupby(['nearest_shopping', 'spending_category']).size().unstack(fill_value=0)
            st.dataframe(shopping_category)

    def render_reports_tab(self, df: pd.DataFrame):
        st.header("📊 Relatórios e Exportação")
        if st.button("Gerar Relatório Resumido"):
            with st.spinner("Gerando relatório abrangente..."):
                # Generate comprehensive report
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'data_summary': {
                        'total_customers': len(df),
                        'total_revenue': df['total_spent'].sum() if 'total_spent' in df.columns else 0,
                        'unique_cities': df['city'].nunique() if 'city' in df.columns else 0,
                        'unique_states': df['state'].nunique() if 'state' in df.columns else 0,
                        'avg_order_value': df['total_spent'].mean() if 'total_spent' in df.columns else 0,
                        'geocoding_success_rate': (df[df['latitude'].notna()].shape[0] / len(df)) * 100 if 'latitude' in df.columns else 0
                    },
                    'geographic_analysis': {
                        'top_cities': df['city'].value_counts().head(5).to_dict() if 'city' in df.columns else {},
                        'top_states': df['state'].value_counts().head(5).to_dict() if 'state' in df.columns else {},
                        'revenue_by_city': df.groupby('city')['total_spent'].sum().sort_values(ascending=False).head(5).to_dict() if 'total_spent' in df.columns and 'city' in df.columns else {},
                        'shopping_analysis': df.groupby('nearest_shopping').agg({
                            'customer_id': 'count',
                            'total_spent': 'sum'
                        }).to_dict() if 'nearest_shopping' in df.columns else {}
                    },
                    'customer_analysis': {
                        'avg_customer_value': df['total_spent'].mean() if 'total_spent' in df.columns else 0,
                        'median_customer_value': df['total_spent'].median() if 'total_spent' in df.columns else 0,
                        'top_customer_value': df['total_spent'].max() if 'total_spent' in df.columns else 0,
                        'total_customer_value': df['total_spent'].sum() if 'total_spent' in df.columns else 0
                    }
                }
                
                st.subheader("📋 Relatório Resumido")
                st.json(report)
                
                # Download report
                report_json = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="Baixar Relatório Completo (JSON)",
                    data=report_json,
                    file_name=f"relatorio_geocommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        st.subheader("📄 Prévia dos Dados")
        if not df.empty:
            with st.expander("Prévia dos Dados de Clientes"):
                st.dataframe(df.head(10), use_container_width=True)

# --- Main Entrypoint ---
def main():
    app = GeoCommerceManualApp()
    app.run()

if __name__ == "__main__":
    main()
