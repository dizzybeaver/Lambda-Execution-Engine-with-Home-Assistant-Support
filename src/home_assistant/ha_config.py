"""
ha_config.py - HA Configuration Constants
Version: 1.0.3
Date: 2025-12-04
Description: Centralized configuration for Home Assistant integration

FIXED: Added 'enabled' key to config dict (critical bug fix)
FIXED: Added debug output showing config keys
FIXED: Added missing import os
FIXED: Direct boolean conversion without gateway dependency
FIXED: Added load_ha_config() function

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import sys

# Debug: Print HA_ENABLED status at import time (helps diagnose issues)
def _debug_print(msg):
    """Print to stderr for CloudWatch visibility."""
    print(f"[HA_CONFIG_DEBUG] {msg}", file=sys.stderr, flush=True)

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
# Direct os.getenv with explicit boolean conversion
_ha_enable_raw = os.getenv('HOME_ASSISTANT_ENABLE', 'false')
_debug_print(f"HOME_ASSISTANT_ENABLE={_ha_enable_raw!r}")
HA_ENABLED = _ha_enable_raw.strip().lower() in ('true', '1', 'yes')
_debug_print(f"HA_ENABLED={HA_ENABLED}")

HA_CACHE_ENABLED = os.getenv('HA_CACHE_ENABLED', 'true').strip().lower() in ('true', '1', 'yes')
HA_METRICS_ENABLED = os.getenv('HA_METRICS_ENABLED', 'true').strip().lower() in ('true', '1', 'yes')
HA_DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').strip().lower() in ('true', '1', 'yes')


def load_ha_config():
    """
    Load Home Assistant configuration from environment.
    
    Returns:
        Dict containing:
        - base_url: Home Assistant URL
        - access_token: Long-lived access token
        - timeout: Request timeout
        - verify_ssl: SSL verification flag
        - enabled: HA enabled flag (CRITICAL - checked by ha_devices_helpers)
    """
    try:
        # Get from environment
        base_url = os.getenv('HOME_ASSISTANT_URL', 'http://homeassistant.local:8123')
        _debug_print(f"base_url={base_url}")
        
        # Token from SSM if enabled
        use_ssm_raw = os.getenv('USE_PARAMETER_STORE', 'false')
        use_ssm = use_ssm_raw.strip().lower() in ('true', '1', 'yes')
        _debug_print(f"USE_PARAMETER_STORE={use_ssm_raw!r} -> {use_ssm}")
        
        if use_ssm:
            # Lazy import to avoid circular dependency
            import gateway
            token = gateway.get_config_value('/lambda-execution-engine/home_assistant/token')
            _debug_print(f"token=<from SSM, length={len(token) if token else 0}>")
        else:
            token = os.getenv('HOME_ASSISTANT_TOKEN', '')
            _debug_print(f"token=<from env, length={len(token) if token else 0}>")
        
        verify_ssl_raw = os.getenv('HA_VERIFY_SSL', 'true')
        verify_ssl = verify_ssl_raw.strip().lower() in ('true', '1', 'yes')
        
        config = {
            'base_url': base_url,
            'access_token': token,
            'timeout': HA_API_TIMEOUT,
            'verify_ssl': verify_ssl,
            'enabled': HA_ENABLED  # CRITICAL: ha_devices_helpers checks this
        }
        
        _debug_print(f"load_ha_config SUCCESS - config keys: {list(config.keys())}")
        _debug_print(f"config['enabled']={config.get('enabled')!r}")
        return config
        
    except Exception as e:
        _debug_print(f"load_ha_config FAILED: {e}")
        raise


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
