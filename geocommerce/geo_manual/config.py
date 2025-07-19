"""
GeoCommerce Configuration System
Centralized configuration management for the GeoCommerce platform.
"""

import os
from typing import Dict, List, Tuple, Optional

# Base directory for GeoCommerce
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
CACHE_PATH = os.path.join(BASE_DIR, 'geocoding_cache.json')
DEFAULT_SHOPIFY_FILE = os.path.join(BASE_DIR, 'customers_export.csv')
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Default shopping mall coordinates
DEFAULT_SHOPPINGS_COORDS = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

# Geocoding settings
GEOCODING_CONFIG = {
    'user_agent': 'geocommerce_platform',
    'timeout': 10,
    'rate_limit_delay': 3,  # seconds
    'max_retries': 3,
    'cache_enabled': True,
    'cache_path': CACHE_PATH
}

# Analysis settings
ANALYSIS_CONFIG = {
    'density_bins': [0, 1, 5, 10, 20, float('inf')],
    'density_labels': ['Baixa', 'Média-Baixa', 'Média', 'Alta', 'Muito Alta'],
    'high_value_min_revenue': 1000,  # R$
    'high_value_max_distance': 15,   # km
    'top_cities_limit': 10,
    'min_customers_for_analysis': 1
}

# Output settings
OUTPUT_CONFIG = {
    'include_timestamp': True,
    'output_formats': ['csv', 'json'],
    'compression': False,
    'output_directory': DEFAULT_OUTPUT_DIR,
    'create_output_dir': True
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': os.path.join(BASE_DIR, 'geocommerce.log'),
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Performance settings
PERFORMANCE_CONFIG = {
    'batch_size': 100,
    'progress_update_interval': 10,
    'memory_limit_mb': 1024,
    'enable_multiprocessing': False,
    'max_concurrent_requests': 1  # For geocoding API
}

# Streamlit settings (for future web interface)
STREAMLIT_CONFIG = {
    'page_title': 'GeoCommerce - E-commerce Geographic Analysis',
    'page_icon': '🗺️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'theme': {
        'primaryColor': '#FF6B6B',
        'backgroundColor': '#FFFFFF',
        'secondaryBackgroundColor': '#F0F2F6',
        'textColor': '#262730'
    }
}

# Map visualization settings
MAP_CONFIG = {
    'default_zoom': 8,
    'default_center': (-23.564738, -46.668939),  # São Paulo
    'map_style': 'carto-positron',
    'heatmap_radius': 20,
    'marker_size': 8,
    'color_scheme': {
        'low_density': '#FFEDA0',
        'medium_density': '#FEB24C',
        'high_density': '#F03B20',
        'very_high_density': '#BD0026'
    }
}

# Business intelligence settings
BI_CONFIG = {
    'revenue_thresholds': {
        'low': 100,
        'medium': 500,
        'high': 1000,
        'premium': 2000
    },
    'distance_thresholds': {
        'very_close': 5,
        'close': 10,
        'medium': 15,
        'far': 25
    },
    'customer_segments': {
        'new_customer': 1,
        'returning_customer': 2,
        'loyal_customer': 5,
        'vip_customer': 10
    }
}

def get_default_config() -> Dict:
    """
    Get complete default configuration dictionary
    
    Returns:
        Dictionary with all configuration settings
    """
    return {
        'system': {
            'name': 'GeoCommerce',
            'version': '1.0.0',
            'base_dir': BASE_DIR
        },
        'paths': {
            'cache': CACHE_PATH,
            'shopify': DEFAULT_SHOPIFY_FILE,
            'output': DEFAULT_OUTPUT_DIR
        },
        'shoppings': DEFAULT_SHOPPINGS_COORDS,
        'geocoding': GEOCODING_CONFIG,
        'analysis': ANALYSIS_CONFIG,
        'output': OUTPUT_CONFIG,
        'logging': LOGGING_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'streamlit': STREAMLIT_CONFIG,
        'map': MAP_CONFIG,
        'business_intelligence': BI_CONFIG
    }

def get_ecommerce_config() -> Dict:
    """
    Get configuration optimized for e-commerce analysis
    
    Returns:
        Dictionary with e-commerce focused settings
    """
    config = get_default_config()
    
    # E-commerce specific optimizations
    config['analysis']['high_value_min_revenue'] = 500  # Lower threshold for e-commerce
    config['analysis']['high_value_max_distance'] = 20  # Larger radius for online customers
    config['business_intelligence']['revenue_thresholds']['low'] = 50  # Lower minimum for online
    
    return config

def get_retail_config() -> Dict:
    """
    Get configuration optimized for retail/physical store analysis
    
    Returns:
        Dictionary with retail focused settings
    """
    config = get_default_config()
    
    # Retail specific optimizations
    config['analysis']['high_value_min_revenue'] = 1500  # Higher threshold for retail
    config['analysis']['high_value_max_distance'] = 10   # Smaller radius for physical stores
    config['business_intelligence']['distance_thresholds']['very_close'] = 2  # Tighter proximity
    
    return config

def get_startup_config() -> Dict:
    """
    Get configuration optimized for startup/small business analysis
    
    Returns:
        Dictionary with startup focused settings
    """
    config = get_default_config()
    
    # Startup specific optimizations
    config['analysis']['high_value_min_revenue'] = 200   # Lower threshold for startups
    config['analysis']['high_value_max_distance'] = 30   # Larger radius for market expansion
    config['performance']['batch_size'] = 50             # Smaller batches for limited resources
    config['performance']['memory_limit_mb'] = 512       # Lower memory usage
    
    return config

def validate_config(config: Dict) -> bool:
    """
    Validate configuration settings
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check required sections
        required_sections = ['system', 'paths', 'shoppings', 'geocoding', 'analysis']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required configuration section: {section}")
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
        
        # Check geocoding settings
        if config['geocoding']['timeout'] <= 0:
            print("❌ Geocoding timeout must be positive")
            return False
        
        if config['geocoding']['rate_limit_delay'] < 0:
            print("❌ Rate limit delay cannot be negative")
            return False
        
        print("✅ Configuration validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def create_custom_config(shoppings: Dict[str, Tuple[float, float]], 
                        analysis_settings: Optional[Dict] = None,
                        geocoding_settings: Optional[Dict] = None) -> Dict:
    """
    Create custom configuration with specific settings
    
    Args:
        shoppings: Dictionary of shopping mall coordinates
        analysis_settings: Optional custom analysis settings
        geocoding_settings: Optional custom geocoding settings
        
    Returns:
        Custom configuration dictionary
    """
    config = get_default_config()
    
    # Update shopping coordinates
    config['shoppings'] = shoppings
    
    # Update analysis settings if provided
    if analysis_settings:
        config['analysis'].update(analysis_settings)
    
    # Update geocoding settings if provided
    if geocoding_settings:
        config['geocoding'].update(geocoding_settings)
    
    return config

def save_config(config: Dict, filepath: str) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        filepath: Path to save configuration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def load_config(filepath: str) -> Optional[Dict]:
    """
    Load configuration from file
    
    Args:
        filepath: Path to configuration file
        
    Returns:
        Configuration dictionary or None if failed
    """
    try:
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if validate_config(config):
            return config
        else:
            print("❌ Loaded configuration failed validation")
            return None
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

if __name__ == "__main__":
    # Test configuration system
    print("🧪 Testing GeoCommerce Configuration System...")
    print("=" * 50)
    
    # Test default configuration
    print("\n1. Testing default configuration...")
    default_config = get_default_config()
    validate_config(default_config)
    
    # Test e-commerce configuration
    print("\n2. Testing e-commerce configuration...")
    ecommerce_config = get_ecommerce_config()
    validate_config(ecommerce_config)
    
    # Test retail configuration
    print("\n3. Testing retail configuration...")
    retail_config = get_retail_config()
    validate_config(retail_config)
    
    # Test startup configuration
    print("\n4. Testing startup configuration...")
    startup_config = get_startup_config()
    validate_config(startup_config)
    
    # Test custom configuration
    print("\n5. Testing custom configuration...")
    custom_shoppings = {
        'Test Mall': (-23.564738, -46.668939),
        'Test Center': (-22.956909, -43.176186)
    }
    custom_config = create_custom_config(custom_shoppings)
    validate_config(custom_config)
    
    print("\n" + "=" * 50)
    print("✅ Configuration system testing completed!")
    
    # Display current settings
    print(f"\n📋 Current Configuration Summary:")
    print(f"   - System: {default_config['system']['name']} v{default_config['system']['version']}")
    print(f"   - Shopping locations: {list(default_config['shoppings'].keys())}")
    print(f"   - Geocoding timeout: {default_config['geocoding']['timeout']}s")
    print(f"   - High value min revenue: R$ {default_config['analysis']['high_value_min_revenue']}")
    print(f"   - High value max distance: {default_config['analysis']['high_value_max_distance']}km") 