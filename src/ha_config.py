"""
ha_config.py - Configuration Management
Version: 2025.10.18.02
Description: Configuration loading with SSM Parameter Store support

CHANGELOG:
- 2025.10.18.02: FIXED Issue #28 - Added SSM Parameter Store support (CRITICAL)
  - Now reads from SSM when USE_PARAMETER_STORE=true
  - Uses gateway.execute_operation(CONFIG, 'get_parameter') for smart loading
  - Falls back to environment variables if SSM unavailable
  - Maintains backward compatibility with env-only configuration
  - Fixes connection failure when token in SSM Parameter Store
- 2025.10.18.01: Fixed cache validation, type checking

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional
from gateway import (
    log_info, log_error, log_debug, log_warning,
    cache_get, cache_set, execute_operation, GatewayInterface,
    create_success_response, create_error_response
)

# Cache key for configuration
HA_CONFIG_CACHE_KEY = 'ha_configuration'
HA_CONFIG_TTL = 600


def _get_config_value(key: str, env_var: str, default: Any = '') -> Any:
    """
    Get configuration value with SSM Parameter Store support.
    
    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. Environment variable
    3. Default value
    
    Args:
        key: Parameter Store key (e.g., 'homeassistant/url')
        env_var: Environment variable name (e.g., 'HOME_ASSISTANT_URL')
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
    
    if use_ssm:
        try:
            # Try to get from SSM via config interface
            # Config interface checks SSM first, then env, then defaults
            value = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key=key,
                default=None
            )
            
            if value is not None:
                log_debug(f"Loaded {key} from Parameter Store")
                return value
                
        except Exception as e:
            log_warning(f"Failed to load {key} from Parameter Store: {e}")
    
    # Fallback to environment variable
    value = os.getenv(env_var, default)
    if value != default:
        log_debug(f"Loaded {key} from environment variable {env_var}")
    else:
        log_debug(f"Using default value for {key}")
    
    return value


def _build_config_from_sources() -> Dict[str, Any]:
    """Build configuration dict from SSM and environment variables."""
    return {
        'enabled': os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true',
        'base_url': _get_config_value('homeassistant/url', 'HOME_ASSISTANT_URL', ''),
        'access_token': _get_config_value('homeassistant/token', 'HOME_ASSISTANT_TOKEN', ''),
        'timeout': int(_get_config_value('homeassistant/timeout', 'HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': _get_config_value('homeassistant/verify_ssl', 'HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true',
        'assistant_name': _get_config_value('homeassistant/assistant_name', 'HA_ASSISTANT_NAME', 'Jarvis')
    }


def load_ha_config() -> Dict[str, Any]:
    """
    Load HA configuration from SSM Parameter Store or environment.
    
    CRITICAL: Always returns a dict, never a response object.
    Cache stores raw config dict, not wrapped responses.
    
    Configuration priority:
    1. Cache (if valid)
    2. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    3. Environment variables
    4. Emergency fallback dict
    """
    try:
        # Try cache first
        cached = cache_get(HA_CONFIG_CACHE_KEY)
        
        # CRITICAL: Validate cached value is actually a dict
        if cached is not None:
            if isinstance(cached, dict):
                # Verify it has expected structure (not a response wrapper)
                if 'enabled' in cached and 'base_url' in cached:
                    log_debug("Using cached HA configuration")
                    return cached
                else:
                    log_warning(f"Cached config has wrong structure: {list(cached.keys())}")
            else:
                log_warning(f"Cached config is {type(cached)}, not dict - rebuilding")
        
        # Build fresh config from SSM/environment
        config = _build_config_from_sources()
        
        # Validate we got actual values
        if config['enabled']:
            if not config.get('base_url'):
                log_error("HOME_ASSISTANT_URL not configured")
            if not config.get('access_token'):
                log_error("HOME_ASSISTANT_TOKEN not configured")
        
        # Cache the raw dict (NOT a response wrapper)
        cache_set(HA_CONFIG_CACHE_KEY, config, ttl=HA_CONFIG_TTL)
        
        use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
        log_info(f"HA configuration loaded (SSM: {use_ssm})")
        
        return config
        
    except Exception as e:
        log_error(f"Failed to load HA config: {str(e)}")
        # Emergency fallback - always return a valid dict
        return {
            'enabled': os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true',
            'base_url': os.getenv('HOME_ASSISTANT_URL', ''),
            'access_token': os.getenv('HOME_ASSISTANT_TOKEN', ''),
            'timeout': 30,
            'verify_ssl': True,
            'assistant_name': 'Jarvis'
        }


def validate_ha_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate HA configuration."""
    if config is None:
        config = load_ha_config()
    
    # Type check
    if not isinstance(config, dict):
        return create_error_response(
            f'Config is {type(config)}, not dict',
            'INVALID_CONFIG_TYPE'
        )
    
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
        'base_url': _get_config_value('homeassistant/url', 'HOME_ASSISTANT_URL', ''),
        'access_token': _get_config_value('homeassistant/token', 'HOME_ASSISTANT_TOKEN', ''),
        'timeout': int(_get_config_value('homeassistant/timeout', 'HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': _get_config_value('homeassistant/verify_ssl', 'HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
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
