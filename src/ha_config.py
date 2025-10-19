"""
ha_config.py - Configuration Management
Version: 2025.10.19.04
Description: Configuration loading with correct SSM Parameter Store priority

CHANGELOG:
- 2025.10.19.04: PERFORMANCE + PRIORITY FIX - Corrected configuration lookup sequence
  - FIXED: Now tries SSM FIRST when USE_PARAMETER_STORE=true, then env fallback
  - FIXED: Skips boto3/SSM loading completely when USE_PARAMETER_STORE=false
  - Added comprehensive logging for each lookup step (SSM success/failure/fallback)
  - Performance: Conditional boto3 import only when needed
  - Maintains backward compatibility with environment-only configuration
  - Resolves issue where env vars take precedence over SSM parameters
- 2025.10.18.03: FIXED Issue #29 - Added type safety for int conversion
- 2025.10.18.02: FIXED Issue #28 - Added SSM Parameter Store support (CRITICAL)
- 2025.10.18.01: Fixed cache validation, type checking

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

# Cache key for configuration
HA_CONFIG_CACHE_KEY = 'ha_configuration'
HA_CONFIG_TTL = 600


def _safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with type checking.
    
    Handles edge cases where value might be:
    - Already an int
    - A string that can be converted
    - None or an unexpected type (returns default)
    
    Args:
        value: Value to convert to int
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError):
            log_warning(f"Cannot convert '{value}' to int, using default {default}")
            return default
    
    # Unexpected type (e.g., object, dict, list)
    log_warning(f"Unexpected type {type(value)} for int conversion, using default {default}")
    return default


def _get_config_value(key: str, env_var: str, default: Any = '') -> Any:
    """
    Get configuration value with CORRECT priority sequence.
    
    PERFORMANCE OPTIMIZATION: Conditional loading based on USE_PARAMETER_STORE.
    
    Priority when USE_PARAMETER_STORE=true:
    1. SSM Parameter Store (FIRST - primary source)
    2. Environment variable (FALLBACK only)
    3. Default value (last resort)
    
    Priority when USE_PARAMETER_STORE=false:
    1. Environment variable (skip SSM completely)
    2. Default value
    
    Args:
        key: Parameter Store key (e.g., 'home_assistant/url')
        env_var: Environment variable name (e.g., 'HOME_ASSISTANT_URL')
        default: Default value if not found
        
    Returns:
        Configuration value (always a string or default type)
    """
    use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
    
    # === CONDITIONAL IMPORT: Only load SSM client if needed ===
    if use_ssm:
        try:
            # Import SSM parameter getter (only when USE_PARAMETER_STORE=true)
            from config_param_store import get_parameter as ssm_get_parameter
            
            log_debug(f"[PRIORITY 1] Attempting SSM lookup for: {key}")
            
            # Try SSM Parameter Store FIRST
            value = ssm_get_parameter(key, default=None)
            
            if value is not None and value != '':
                # SUCCESS: Found in SSM
                log_info(f"[SSM SUCCESS] Loaded {key} from Parameter Store")
                return str(value) if not isinstance(value, bool) else value
            else:
                # NOT FOUND in SSM, will fallback to environment
                log_warning(f"[SSM MISS] Parameter {key} not found in SSM, falling back to environment variable {env_var}")
                
        except ImportError as e:
            log_error(f"[SSM ERROR] Cannot import config_param_store: {e}. Falling back to environment.")
        except Exception as e:
            log_warning(f"[SSM ERROR] Failed to load {key} from Parameter Store: {e}. Falling back to environment.")
    else:
        log_debug(f"[SSM SKIPPED] USE_PARAMETER_STORE=false, skipping SSM lookup for {key}")
    
    # === PRIORITY 2: Environment Variable Fallback ===
    value = os.getenv(env_var)
    
    if value is not None and value != '':
        log_info(f"[ENV SUCCESS] Loaded {key} from environment variable {env_var}")
        return value
    
    # === PRIORITY 3: Default Value ===
    log_debug(f"[DEFAULT] Using default value for {key}: {default}")
    return default


def _build_config_from_sources() -> Dict[str, Any]:
    """
    Build configuration dict from SSM and environment variables.
    
    PERFORMANCE NOTE: This function respects USE_PARAMETER_STORE flag.
    If false, SSM lookups are skipped entirely (no boto3 import).
    
    Returns:
        Configuration dictionary with validated types
    """
    return {
        'enabled': os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true',
        'base_url': _get_config_value('home_assistant/url', 'HOME_ASSISTANT_URL', ''),
        'access_token': _get_config_value('home_assistant/token', 'HOME_ASSISTANT_TOKEN', ''),
        'timeout': _safe_int(_get_config_value('home_assistant/timeout', 'HOME_ASSISTANT_TIMEOUT', '30'), 30),
        'verify_ssl': _get_config_value('home_assistant/verify_ssl', 'HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true',
        'assistant_name': _get_config_value('home_assistant/assistant_name', 'HA_ASSISTANT_NAME', 'Jarvis')
    }


def load_ha_config() -> Dict[str, Any]:
    """
    Load HA configuration from SSM Parameter Store or environment.
    
    CRITICAL: Always returns a dict, never a response object.
    Cache stores raw config dict, not wrapped responses.
    
    Configuration priority (when USE_PARAMETER_STORE=true):
    1. Cache (if valid)
    2. SSM Parameter Store (PRIMARY SOURCE)
    3. Environment variables (FALLBACK)
    4. Default values
    
    When USE_PARAMETER_STORE=false:
    1. Cache (if valid)
    2. Environment variables (ONLY SOURCE)
    3. Default values
    
    Returns:
        Configuration dictionary
    """
    # Check cache first
    cached_config = cache_get(HA_CONFIG_CACHE_KEY)
    if cached_config and isinstance(cached_config, dict):
        log_debug("Using cached HA configuration")
        return cached_config
    
    log_info("Loading HA configuration from sources (cache miss)")
    
    # Build fresh config from sources (respects USE_PARAMETER_STORE)
    config = _build_config_from_sources()
    
    # Cache the config
    cache_set(HA_CONFIG_CACHE_KEY, config, ttl=HA_CONFIG_TTL)
    
    log_info(f"HA configuration loaded: enabled={config['enabled']}, "
            f"base_url_present={bool(config['base_url'])}, "
            f"token_present={bool(config['access_token'])}")
    
    return config


def validate_ha_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate Home Assistant configuration.
    
    Args:
        config: Configuration dict to validate (loads if None)
        
    Returns:
        Validation response dictionary
    """
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
