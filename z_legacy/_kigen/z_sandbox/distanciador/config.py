"""
Configuration file for Enhanced Distanciador
"""

import os
from typing import Dict, Tuple

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
CACHE_PATH = os.path.join(BASE_DIR, 'coordenadas_cache.json')
SHOPIFY_FILE = os.path.join(BASE_DIR, 'customers_export.csv')
BASE_CEPS_FILE = os.path.join(BASE_DIR, 'base_ceps.csv')

# Shopping mall coordinates
SHOPPINGS_COORDS = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

# Geocoding settings
GEOCODING_CONFIG = {
    'user_agent': 'enhanced_distanciador_kigen',
    'timeout': 10,
    'rate_limit_delay': 3,  # seconds
    'max_retries': 3
}

# Analysis settings
DENSITY_ANALYSIS_CONFIG = {
    'density_bins': [0, 1, 5, 10, 20, float('inf')],
    'density_labels': ['Baixa', 'Média-Baixa', 'Média', 'Alta', 'Muito Alta'],
    'high_value_min_revenue': 1000,  # R$
    'high_value_max_distance': 15,   # km
    'top_cities_limit': 10
}

# Output settings
OUTPUT_CONFIG = {
    'include_timestamp': True,
    'output_formats': ['csv', 'json'],
    'compression': False
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': os.path.join(BASE_DIR, 'distanciador.log')
}

# Data processing settings
DATA_PROCESSING_CONFIG = {
    'cep_cleanup': True,
    'currency_cleanup': True,
    'handle_missing_coords': True,
    'estimate_by_proximity': True,
    'max_iterations': 50
}

# Streamlit settings (for future web interface)
STREAMLIT_CONFIG = {
    'page_title': 'Enhanced Distanciador - Consumer Density Analysis',
    'page_icon': '🗺️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Map visualization settings
MAP_CONFIG = {
    'default_zoom': 8,
    'default_center': (-23.564738, -46.668939),  # São Paulo
    'map_style': 'carto-positron',
    'heatmap_radius': 20,
    'marker_size': 8
}

# Performance settings
PERFORMANCE_CONFIG = {
    'batch_size': 100,
    'progress_update_interval': 10,
    'memory_limit_mb': 1024,
    'enable_multiprocessing': False
}

def get_config() -> Dict:
    """Get complete configuration dictionary"""
    return {
        'base_dir': BASE_DIR,
        'paths': {
            'cache': CACHE_PATH,
            'shopify': SHOPIFY_FILE,
            'base_ceps': BASE_CEPS_FILE
        },
        'shoppings': SHOPPINGS_COORDS,
        'geocoding': GEOCODING_CONFIG,
        'analysis': DENSITY_ANALYSIS_CONFIG,
        'output': OUTPUT_CONFIG,
        'logging': LOGGING_CONFIG,
        'data_processing': DATA_PROCESSING_CONFIG,
        'streamlit': STREAMLIT_CONFIG,
        'map': MAP_CONFIG,
        'performance': PERFORMANCE_CONFIG
    }

def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        config = get_config()
        
        # Check if base directory exists
        if not os.path.exists(config['base_dir']):
            print(f"❌ Base directory does not exist: {config['base_dir']}")
            return False
        
        # Check shopping coordinates
        for shopping, coords in config['shoppings'].items():
            if not isinstance(coords, tuple) or len(coords) != 2:
                print(f"❌ Invalid coordinates for {shopping}: {coords}")
                return False
            if not all(isinstance(c, (int, float)) for c in coords):
                print(f"❌ Invalid coordinate types for {shopping}: {coords}")
                return False
        
        # Check analysis settings
        if config['analysis']['high_value_min_revenue'] < 0:
            print("❌ High value minimum revenue cannot be negative")
            return False
        
        if config['analysis']['high_value_max_distance'] <= 0:
            print("❌ High value maximum distance must be positive")
            return False
        
        print("✅ Configuration validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    # Test configuration
    print("Testing Enhanced Distanciador Configuration...")
    validate_config()
    
    # Print current settings
    config = get_config()
    print("\nCurrent Configuration:")
    print(f"Base Directory: {config['base_dir']}")
    print(f"Shopping Malls: {list(config['shoppings'].keys())}")
    print(f"Geocoding Timeout: {config['geocoding']['timeout']}s")
    print(f"High Value Min Revenue: R$ {config['analysis']['high_value_min_revenue']}")
    print(f"High Value Max Distance: {config['analysis']['high_value_max_distance']}km") 