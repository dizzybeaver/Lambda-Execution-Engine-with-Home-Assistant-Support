"""
home_assistant/ha_config.py - Configuration Management
Version: 2025.10.14.01
Description: Configuration loading using Gateway services.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional
from gateway import (
    log_info, log_error, log_debug,
    cache_get, cache_set,
    create_success_response, create_error_response
)

# Cache key for configuration
HA_CONFIG_CACHE_KEY = 'ha_configuration'
HA_CONFIG_TTL = 600

# ===== CONFIGURATION LOADING =====

def load_ha_config() -> Dict[str, Any]:
    """Load HA configuration from environment."""
    cached = cache_get(HA_CONFIG_CACHE_KEY)
    if cached:
        log_debug("Using cached HA configuration")
        return cached
    
    config = {
        'enabled': os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true',
        'base_url': os.getenv('HOME_ASSISTANT_URL', ''),
        'access_token': os.getenv('HOME_ASSISTANT_TOKEN', ''),
        'timeout': int(os.getenv('HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true',
        'assistant_name': os.getenv('HA_ASSISTANT_NAME', 'Jarvis')
    }
    
    cache_set(HA_CONFIG_CACHE_KEY, config, ttl=HA_CONFIG_TTL)
    log_debug("HA configuration loaded from environment")
    
    return config


def validate_ha_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate HA configuration."""
    if config is None:
        config = load_ha_config()
    
    errors = []
    
    if not config.get('enabled'):
        return create_success_response('HA disabled', {'valid': True, 'enabled': False})
    
    if not config.get('base_url'):
        errors.append('HOME_ASSISTANT_URL not configured')
    
    if not config.get('access_token'):
        errors.append('HOME_ASSISTANT_TOKEN not configured')
    
    if config.get('timeout', 0) <= 0:
        errors.append('Invalid timeout value')
    
    if errors:
        return create_error_response('Invalid configuration', 'INVALID_CONFIG', 
                                    {'errors': errors})
    
    return create_success_response('Configuration valid', {'valid': True})


def get_ha_preset(preset_name: str = 'default') -> Dict[str, Any]:
    """Get HA preset configuration."""
    presets = {
        'default': {
            'cache_ttl_state': 60,
            'cache_ttl_entities': 300,
            'retry_attempts': 3,
            'timeout': 30
        },
        'fast': {
            'cache_ttl_state': 30,
            'cache_ttl_entities': 150,
            'retry_attempts': 2,
            'timeout': 15
        },
        'slow': {
            'cache_ttl_state': 120,
            'cache_ttl_entities': 600,
            'retry_attempts': 5,
            'timeout': 60
        }
    }
    
    return presets.get(preset_name, presets['default'])


def load_ha_connection_config() -> Dict[str, Any]:
    """Load connection-specific configuration."""
    return {
        'base_url': os.getenv('HOME_ASSISTANT_URL', ''),
        'access_token': os.getenv('HOME_ASSISTANT_TOKEN', ''),
        'timeout': int(os.getenv('HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
    }


def load_ha_preset_config(preset: str = 'default') -> Dict[str, Any]:
    """Load preset configuration merged with connection config."""
    connection = load_ha_connection_config()
    preset_config = get_ha_preset(preset)
    
    return {**connection, **preset_config}


# EOF
