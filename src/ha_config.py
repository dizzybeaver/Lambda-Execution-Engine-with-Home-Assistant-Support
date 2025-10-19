"""
ha_config.py - Configuration Management  
Version: 2025.10.19.07
Description: SSM-first configuration with proper sentinel handling

CHANGELOG:
- 2025.10.19.07: FINAL VERSION - Works with sentinel-aware config_param_store
  - Proper SSM priority when USE_PARAMETER_STORE=true
  - Environment fallback when SSM fails
  - Compatible with fixed config_param_store.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional
from gateway import (
    log_info, log_error, log_debug, log_warning,
    cache_get, cache_set,
    create_success_response, create_error_response
)

HA_CONFIG_CACHE_KEY = 'ha_configuration'
HA_CONFIG_TTL = 600


def _safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except:
            return default
    return default


def _get_config_value(key: str, env_var: str, default: Any = '') -> Any:
    """
    Get configuration value with proper SSM priority.
    
    When USE_PARAMETER_STORE=true:
    1. SSM Parameter Store FIRST
    2. Environment variable FALLBACK
    3. Default value
    
    When USE_PARAMETER_STORE=false:
    1. Environment variable ONLY
    2. Default value
    """
    use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
    
    if use_ssm:
        try:
            from config_param_store import get_parameter as ssm_get_parameter
            
            value = ssm_get_parameter(key, default=None)
            
            if value is not None and value != '':
                log_info(f"[SSM SUCCESS] {key}")
                return str(value) if not isinstance(value, bool) else value
            else:
                log_warning(f"[SSM MISS] {key}, trying environment")
                
        except Exception as e:
            log_error(f"[SSM ERROR] {key}: {e}, trying environment")
    
    # Environment fallback (or primary if SSM disabled)
    value = os.getenv(env_var)
    
    if value is not None and value != '':
        log_info(f"[ENV SUCCESS] {key}")
        return value
    
    # Default
    log_debug(f"[DEFAULT] {key}")
    return default


def _build_config_from_sources() -> Dict[str, Any]:
    """Build configuration from SSM/environment."""
    return {
        'enabled': os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true',
        'base_url': _get_config_value('home_assistant/url', 'HOME_ASSISTANT_URL', ''),
        'access_token': _get_config_value('home_assistant/token', 'HOME_ASSISTANT_TOKEN', ''),
        'timeout': _safe_int(_get_config_value('home_assistant/timeout', 'HOME_ASSISTANT_TIMEOUT', '30'), 30),
        'verify_ssl': _get_config_value('home_assistant/verify_ssl', 'HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true',
        'assistant_name': _get_config_value('home_assistant/assistant_name', 'HA_ASSISTANT_NAME', 'Jarvis')
    }


def load_ha_config() -> Dict[str, Any]:
    """Load HA configuration with caching."""
    # Check cache
    cached_config = cache_get(HA_CONFIG_CACHE_KEY)
    if cached_config and isinstance(cached_config, dict):
        return cached_config
    
    # Build fresh config
    config = _build_config_from_sources()
    
    # Cache it
    cache_set(HA_CONFIG_CACHE_KEY, config, ttl=HA_CONFIG_TTL)
    
    return config


def validate_ha_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate HA configuration."""
    if config is None:
        config = load_ha_config()
    
    if not isinstance(config, dict):
        return create_error_response('Invalid config type', 'INVALID_CONFIG_TYPE')
    
    errors = []
    
    if not config.get('enabled'):
        return create_success_response('HA disabled', {'valid': True, 'enabled': False})
    
    if not config.get('base_url'):
        errors.append('HOME_ASSISTANT_URL not configured')
    
    if not config.get('access_token'):
        errors.append('HOME_ASSISTANT_TOKEN not configured')
    
    if errors:
        return create_error_response('Invalid configuration', 'INVALID_CONFIG', {'errors': errors})
    
    return create_success_response('Configuration valid', {'valid': True})


def get_ha_preset(preset_name: str = 'default') -> Dict[str, Any]:
    """Get HA preset configuration."""
    presets = {
        'default': {'cache_ttl_state': 60, 'cache_ttl_entities': 300, 'retry_attempts': 3, 'timeout': 30},
        'fast': {'cache_ttl_state': 30, 'cache_ttl_entities': 150, 'retry_attempts': 2, 'timeout': 15},
        'slow': {'cache_ttl_state': 120, 'cache_ttl_entities': 600, 'retry_attempts': 5, 'timeout': 60}
    }
    return presets.get(preset_name, presets['default'])


def load_ha_connection_config() -> Dict[str, Any]:
    """Load connection-specific configuration."""
    return {
        'base_url': _get_config_value('home_assistant/url', 'HOME_ASSISTANT_URL', ''),
        'access_token': _get_config_value('home_assistant/token', 'HOME_ASSISTANT_TOKEN', ''),
        'timeout': _safe_int(_get_config_value('home_assistant/timeout', 'HOME_ASSISTANT_TIMEOUT', '30'), 30),
        'verify_ssl': _get_config_value('home_assistant/verify_ssl', 'HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
    }


def load_ha_preset_config(preset: str = 'default') -> Dict[str, Any]:
    """Load preset configuration merged with connection config."""
    connection = load_ha_connection_config()
    preset_config = get_ha_preset(preset)
    return {**connection, **preset_config}


__all__ = [
    'load_ha_config',
    'validate_ha_config',
    'get_ha_preset',
    'load_ha_connection_config',
    'load_ha_preset_config'
]

# EOF
