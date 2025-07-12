"""
Configuration management for Shopify integration system.
"""

import os
from typing import Dict, Any
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG = {
    # Shopify API settings
    "api_version": "2024-01",
    "request_timeout": 30,
    "max_retries": 3,
    "backoff_factor": 1,
    
    # Rate limiting
    "rate_limit_buffer": 5,  # Keep 5 requests in buffer
    "rate_limit_sleep": 2,   # Default sleep time
    
    # Data sync settings
    "sync_enabled": True,
    "sync_time": "02:00",
    "sync_entities": ["products", "orders", "customers", "collections"],
    "retry_attempts": 3,
    "retry_delay_minutes": 15,
    "orders_days_back": 30,
    
    # Storage settings
    "data_dir": "shopify_data",
    "cache_expiry_hours": 24,
    "max_log_age_days": 30,
    
    # Database settings
    "db_timeout": 30,
    "db_isolation_level": None,
    
    # Performance settings
    "pagination_limit": 250,
    "max_concurrent_requests": 5,
    "connection_pool_size": 10
}

# Environment variable mappings
ENV_MAPPINGS = {
    "SHOPIFY_SHOP_NAME": "shop_name",
    "SHOPIFY_ACCESS_TOKEN": "access_token",
    "SHOPIFY_API_VERSION": "api_version",
    "SHOPIFY_SYNC_TIME": "sync_time",
    "SHOPIFY_SYNC_ENABLED": "sync_enabled",
    "SHOPIFY_DATA_DIR": "data_dir",
    "SHOPIFY_ORDERS_DAYS_BACK": "orders_days_back",
    "SHOPIFY_RETRY_ATTEMPTS": "retry_attempts",
    "SHOPIFY_CACHE_EXPIRY_HOURS": "cache_expiry_hours"
}

def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary with configuration values from environment
    """
    config = {}
    
    for env_var, config_key in ENV_MAPPINGS.items():
        value = os.getenv(env_var)
        if value is not None:
            # Convert string values to appropriate types
            if config_key in ["sync_enabled"]:
                config[config_key] = value.lower() in ["true", "1", "yes", "on"]
            elif config_key in ["orders_days_back", "retry_attempts", "cache_expiry_hours"]:
                try:
                    config[config_key] = int(value)
                except ValueError:
                    pass  # Keep default value
            else:
                config[config_key] = value
    
    return config

def get_config() -> Dict[str, Any]:
    """
    Get complete configuration by merging defaults with environment variables.
    
    Returns:
        Complete configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    env_config = load_config_from_env()
    config.update(env_config)
    
    return config

def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration and return any errors.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Dictionary with validation errors (empty if valid)
    """
    errors = {}
    
    # Check required fields for initialization
    if not config.get("shop_name"):
        errors["shop_name"] = "Shop name is required"
    
    if not config.get("access_token"):
        errors["access_token"] = "Access token is required"
    
    # Validate sync time format
    sync_time = config.get("sync_time", "02:00")
    if not isinstance(sync_time, str) or ":" not in sync_time:
        errors["sync_time"] = "Sync time must be in HH:MM format"
    else:
        try:
            hours, minutes = map(int, sync_time.split(":"))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                errors["sync_time"] = "Sync time must be valid (00:00-23:59)"
        except ValueError:
            errors["sync_time"] = "Sync time must be in HH:MM format"
    
    # Validate numeric values
    numeric_fields = {
        "orders_days_back": (1, 365),
        "retry_attempts": (1, 10),
        "cache_expiry_hours": (1, 168),  # 1 week max
        "max_log_age_days": (1, 365)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        value = config.get(field)
        if value is not None:
            try:
                int_value = int(value)
                if not (min_val <= int_value <= max_val):
                    errors[field] = f"{field} must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                errors[field] = f"{field} must be a valid integer"
    
    return errors

def get_data_dir(config: Dict[str, Any] = None) -> Path:
    """
    Get the data directory path.
    
    Args:
        config: Configuration dictionary (optional)
        
    Returns:
        Path object for data directory
    """
    if config is None:
        config = get_config()
    
    data_dir = config.get("data_dir", "shopify_data")
    return Path(data_dir)

def ensure_data_dir(config: Dict[str, Any] = None) -> Path:
    """
    Ensure the data directory exists.
    
    Args:
        config: Configuration dictionary (optional)
        
    Returns:
        Path object for data directory
    """
    data_dir = get_data_dir(config)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# Configuration presets for different environments
DEVELOPMENT_CONFIG = {
    "sync_enabled": False,
    "orders_days_back": 7,
    "retry_attempts": 1,
    "cache_expiry_hours": 1
}

PRODUCTION_CONFIG = {
    "sync_enabled": True,
    "orders_days_back": 30,
    "retry_attempts": 3,
    "cache_expiry_hours": 24
}

TESTING_CONFIG = {
    "sync_enabled": False,
    "data_dir": "test_shopify_data",
    "orders_days_back": 1,
    "retry_attempts": 1,
    "cache_expiry_hours": 1
}

def get_preset_config(preset: str) -> Dict[str, Any]:
    """
    Get configuration for a specific preset.
    
    Args:
        preset: Preset name ('development', 'production', 'testing')
        
    Returns:
        Configuration dictionary for the preset
    """
    base_config = get_config()
    
    presets = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "testing": TESTING_CONFIG
    }
    
    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}")
    
    preset_config = presets[preset]
    base_config.update(preset_config)
    
    return base_config