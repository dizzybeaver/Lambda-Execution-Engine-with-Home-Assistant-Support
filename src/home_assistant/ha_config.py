"""
ha_config.py - HA Configuration Constants
Version: 1.0.1
Date: 2025-12-03
Description: Centralized configuration for Home Assistant integration

FIXED: Added missing load_ha_config() function

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os

# Cache TTLs (seconds)
HA_CACHE_TTL_STATE = 300      # 5 minutes - device states
HA_CACHE_TTL_DOMAIN = 600     # 10 minutes - domain lists
HA_CACHE_TTL_FUZZY = 300      # 5 minutes - fuzzy search
HA_CACHE_TTL_CONFIG = 3600    # 1 hour - HA configuration

# API Timeouts (seconds)
HA_API_TIMEOUT = 30           # REST API calls
HA_WEBSOCKET_TIMEOUT = 10     # WebSocket operations
HA_CONNECT_TIMEOUT = 5        # Connection establishment

# Retry Configuration
HA_MAX_RETRIES = 3
HA_RETRY_BACKOFF = 2.0        # Exponential backoff multiplier

# Validation Patterns
HA_ENTITY_ID_PATTERN = r'^[a-z_]+\.[a-z0-9_]+$'
HA_DOMAIN_PATTERN = r'^[a-z_]+$'
HA_SERVICE_PATTERN = r'^[a-z_]+$'

# Feature Flags (loaded from environment)
# Use gateway.config_get for typed retrieval
from gateway import config_get

HA_ENABLED = config_get('HOME_ASSISTANT_ENABLED', default=False)
HA_CACHE_ENABLED = config_get('HA_CACHE_ENABLED', default=True)
HA_METRICS_ENABLED = config_get('HA_METRICS_ENABLED', default=True)
HA_DEBUG_MODE = config_get('DEBUG_MODE', default=False)


# FIXED: Added missing load_ha_config function
def load_ha_config():
    """
    Load Home Assistant configuration from environment.
    
    Returns:
        Dict containing:
        - base_url: Home Assistant URL
        - access_token: Long-lived access token
        - timeout: Request timeout
        - verify_ssl: SSL verification flag
    """
    # Get from environment or SSM
    base_url = os.getenv('HOME_ASSISTANT_URL', 'http://homeassistant.local:8123')
    
    # Token from SSM if enabled
    use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
    if use_ssm:
        # Lazy import
        import gateway
        token = gateway.config_get('/lambda-execution-engine/home_assistant/token')
    else:
        token = os.getenv('HOME_ASSISTANT_TOKEN', '')
    
    return {
        'base_url': base_url,
        'access_token': token,
        'timeout': HA_API_TIMEOUT,
        'verify_ssl': os.getenv('HA_VERIFY_SSL', 'true').lower() == 'true'
    }


__all__ = [
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_DOMAIN',
    'HA_CACHE_TTL_FUZZY',
    'HA_CACHE_TTL_CONFIG',
    'HA_API_TIMEOUT',
    'HA_WEBSOCKET_TIMEOUT',
    'HA_CONNECT_TIMEOUT',
    'HA_MAX_RETRIES',
    'HA_RETRY_BACKOFF',
    'HA_ENTITY_ID_PATTERN',
    'HA_DOMAIN_PATTERN',
    'HA_SERVICE_PATTERN',
    'HA_ENABLED',
    'HA_CACHE_ENABLED',
    'HA_METRICS_ENABLED',
    'HA_DEBUG_MODE',
    'load_ha_config',
]
