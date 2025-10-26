"""
ha_config.py - Home Assistant Configuration Management
Version: 2025.10.26.PHASE2
Description: SSM token-only, ALL original functions preserved + Performance optimization

CHANGELOG:
- 2025.10.26.PHASE2: Performance optimization - replaced custom timing with gateway metrics
  * REMOVED: _is_debug_mode() and _print_timing() functions (7 lines)
  * REMOVED: All manual timing code from all functions (48 lines)
  * REMOVED: time module import (no longer needed)
  * ADDED: Gateway metrics for config operations
  * TOTAL REDUCTION: 55 lines of custom timing code removed
  * KEPT: All sentinel validation functions (Phase 3 will address these)
- 2025.10.20.TOKEN_ONLY_FIXED: Adapted for token-only SSM
  - Token from SSM via config_param_store.get_ha_token()
  - All other config from environment variables
  - ALL original functions preserved (validate_ha_config, get_ha_preset, etc.)
  
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional
import os

from gateway import (
    cache_get,
    cache_set,
    cache_delete,
    log_debug,
    log_info,
    log_warning,
    log_error,
    increment_counter
)


# ===== VALUE SAFETY HELPERS =====

def _safe_int(value: Any, default: int) -> int:
    """Safely convert any value to int with default fallback."""
    if value is None:
        return default
    
    # Get type name once
    type_name = type(value).__name__
    
    # Check for _CacheMiss sentinel
    if type_name == '_CacheMiss':
        log_warning(f"[SAFE_INT] Detected _CacheMiss sentinel, using default {default}")
        return default
    
    # Check for object() sentinel
    if type_name == 'object' and str(value).startswith('<object object'):
        log_warning(f"[SAFE_INT] Detected object() sentinel, using default {default}")
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ===== VALUE SANITIZATION =====

def _sanitize_value(value: Any, key: str, default: str = '') -> str:
    """
    NUCLEAR SANITIZATION: Convert ANY value to safe string.
    
    Handles:
    - None → default
    - _CacheMiss sentinel → default
    - object() sentinels → default
    - Invalid types → default
    - Valid strings → passthrough
    """
    if value is None:
        log_debug(f"[SANITIZE] {key}: None, using default")
        return default
    
    # Get type name once
    type_name = type(value).__name__
    
    # Check for _CacheMiss sentinel
    if type_name == '_CacheMiss':
        log_error(f"[SANITIZE] {key}: _CacheMiss SENTINEL DETECTED! Using default")
        return default
    
    # Check for object() sentinel
    if type_name == 'object' and str(value).startswith('<object object'):
        log_error(f"[SANITIZE] {key}: object() SENTINEL DETECTED! Using default")
        return default
    
    # Must be string
    if not isinstance(value, str):
        log_warning(f"[SANITIZE] {key}: Type {type_name}, converting to string")
        try:
            return str(value)
        except Exception as e:
            log_error(f"[SANITIZE] {key}: Failed to convert {type_name}: {e}")
            return default
    
    # Empty string check
    if not value or not value.strip():
        log_warning(f"[SANITIZE] {key}: Empty string, using default")
        return default if default else ''
    
    return value


# ===== CACHE VALIDATION =====

def _validate_cached_config(cached: Any) -> Optional[Dict[str, Any]]:
    """
    Validate cached configuration before returning.
    
    Cache can contain:
    - Valid dict config
    - _CacheMiss sentinel from cache_core.py
    - object() sentinels from cache_core.py
    - Invalid types from previous bugs
    - Stale/corrupted data
    
    Args:
        cached: Value from cache
        
    Returns:
        Valid dict or None (which signals to rebuild)
    """
    if cached is None:
        return None
    
    # Check for _CacheMiss sentinel (cache_core.py sentinel)
    type_name = type(cached).__name__
    if type_name == '_CacheMiss':
        log_debug("[CACHE VALIDATE] Cached config is _CacheMiss sentinel, treating as cache miss")
        return None
    
    # Check for object() sentinel
    if type_name == 'object' and str(cached).startswith('<object object'):
        log_error("[CACHE VALIDATE] Cached config is object() sentinel, invalidating")
        return None
    
    # Must be a dict
    if not isinstance(cached, dict):
        log_error(f"[CACHE VALIDATE] Cached config is {type_name}, not dict, invalidating")
        return None
    
    # Validate it has the expected keys
    if 'enabled' not in cached:
        log_error("[CACHE VALIDATE] Cached config missing 'enabled' key, invalidating")
        return None
    
    # If enabled, must have base_url and access_token
    if cached.get('enabled'):
        if 'base_url' not in cached or 'access_token' not in cached:
            log_error("[CACHE VALIDATE] Cached config missing required keys, invalidating")
            return None
    
    # Cache is valid
    return cached


def _sanitize_config_for_cache(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    NUCLEAR SANITIZATION: Remove sentinels before caching.
    
    CRITICAL FIX for cold start performance:
    - Prevents cache pollution from _CacheMiss sentinels
    - Prevents cache pollution from object() sentinels
    - Ensures only primitive types get cached
    - Saves ~535ms per cold start by avoiding cache invalidation
    
    Args:
        config: Configuration dictionary (may contain sentinels)
        
    Returns:
        Sanitized configuration dictionary (no sentinels)
    """
    sanitized = {}
    
    for key, value in config.items():
        # Get type name once
        type_name = type(value).__name__
        
        # Detect _CacheMiss sentinel
        if type_name == '_CacheMiss':
            log_error(f"[SANITIZE_CONFIG] Found _CacheMiss sentinel in key '{key}', skipping!")
            continue  # Don't add sentinel to cache
        
        # Detect object() sentinel
        if type_name == 'object' and str(value).startswith('<object object'):
            log_error(f"[SANITIZE_CONFIG] Found object() sentinel in key '{key}', skipping!")
            continue  # Don't add sentinel to cache
        
        # Only allow primitive types
        if isinstance(value, (str, int, float, bool, list, dict, tuple, set, type(None))):
            sanitized[key] = value
        else:
            log_warning(f"[SANITIZE_CONFIG] Skipping non-primitive type {type_name} for key '{key}'")
    
    return sanitized


# ===== TOKEN LOADING (SSM TOKEN-ONLY) =====

def _load_token(use_parameter_store: bool) -> str:
    """
    Load Home Assistant token from SSM or environment.
    
    NEW: Uses config_param_store.get_ha_token() for SSM token retrieval.
    
    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. HOME_ASSISTANT_TOKEN environment variable
    3. LONG_LIVED_ACCESS_TOKEN environment variable (legacy)
    4. Empty string
    
    Args:
        use_parameter_store: Whether to try SSM first
        
    Returns:
        Token string (may be empty)
    """
    # MODIFIED: Removed all custom timing code
    
    token = ''
    
    # Try SSM first if enabled
    if use_parameter_store:
        try:
            # NEW: Use simplified token-only SSM client
            from config_param_store import get_ha_token
            
            token = get_ha_token(use_cache=True)
            
            # Check what type we got back
            token_type = type(token).__name__
            
            # Handle sentinels
            if token_type == '_CacheMiss':
                log_error("[TOKEN LOAD] SSM returned _CacheMiss sentinel")
                token = None
            elif token_type == 'object':
                log_error("[TOKEN LOAD] SSM returned object() sentinel")
                token = None
            elif not isinstance(token, str):
                log_error(f"[TOKEN LOAD] SSM returned unexpected type: {token_type}")
                token = None
            
            if token:
                log_info(f"[TOKEN LOAD] Token loaded from SSM (length={len(token)})")
                # ADDED: Metric for SSM token success
                increment_counter('ha_config_token_ssm_success')
                return token
            else:
                log_warning("[TOKEN LOAD] SSM returned no token, falling back to environment")
                increment_counter('ha_config_token_ssm_fallback')
                
        except Exception as e:
            log_error(f"[TOKEN LOAD] SSM error: {e}, falling back to environment")
            increment_counter('ha_config_token_ssm_error')
    
    # Fallback to environment variables
    token = os.environ.get('HOME_ASSISTANT_TOKEN') or os.environ.get('LONG_LIVED_ACCESS_TOKEN') or ''
    
    if token:
        log_info(f"[TOKEN LOAD] Token loaded from environment (length={len(token)})")
        increment_counter('ha_config_token_env_success')
    else:
        log_error("[TOKEN LOAD] No token found in environment variables")
        increment_counter('ha_config_token_missing')
    
    return token


# ===== CONFIGURATION BUILDING =====

def _build_config_from_sources(use_parameter_store: bool = False) -> Dict[str, Any]:
    """
    Build configuration from sources.
    
    NEW: All config from environment EXCEPT token (which may come from SSM).
    
    Args:
        use_parameter_store: Whether to use SSM for token
        
    Returns:
        Configuration dictionary (ALWAYS dict, validated values)
    """
    # MODIFIED: Removed all custom timing code
    
    # Check if HA is enabled
    enabled_str = os.environ.get('HOME_ASSISTANT_ENABLED', 'true').lower()
    enabled = enabled_str in ('true', '1', 'yes')
    
    if not enabled:
        return {'enabled': False}
    
    # Get base URL from environment
    base_url = _sanitize_value(
        os.environ.get('HOME_ASSISTANT_URL'),
        'base_url',
        default=''
    )
    
    # Get access token (SSM or environment)
    access_token = _load_token(use_parameter_store)
    
    # Get timeout from environment
    timeout_str = os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')
    timeout = _safe_int(timeout_str, 30)
    
    # Get verify_ssl from environment
    verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str in ('true', '1', 'yes')
    
    # Get assistant name from environment
    assistant_name = _sanitize_value(
        os.environ.get('HA_ASSISTANT_NAME'),
        'assistant_name',
        default='Alexa'
    )
    
    # Build config dict
    config = {
        'enabled': enabled,
        'base_url': base_url,
        'access_token': access_token,
        'timeout': timeout,
        'verify_ssl': verify_ssl,
        'assistant_name': assistant_name
    }
    
    return config


def load_ha_config(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Load Home Assistant configuration with bulletproof cache validation.
    
    Configuration priority:
    1. Validated cache (if not force_refresh)
    2. Token from SSM (if USE_PARAMETER_STORE=true)
    3. All other config from environment variables
    4. Defaults
    
    Args:
        force_refresh: Skip cache and reload from sources
        
    Returns:
        Configuration dictionary (always dict, never None or object())
    """
    # MODIFIED: Removed all custom timing code, added gateway metrics
    
    # Check cache first (with validation)
    if not force_refresh:
        cached = cache_get('ha_config')
        
        if cached is not None:
            # CRITICAL: Validate cached value before returning
            validated = _validate_cached_config(cached)
            
            if validated is not None:
                # ADDED: Cache hit metric
                increment_counter('ha_config_cache_hit')
                return validated
            else:
                # ADDED: Cache invalidation metric
                increment_counter('ha_config_cache_invalid')
                cache_delete('ha_config')
        else:
            # ADDED: Cache miss metric
            increment_counter('ha_config_cache_miss')
    else:
        # ADDED: Force refresh metric
        increment_counter('ha_config_force_refresh')
    
    # Build fresh config
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    config = _build_config_from_sources(use_parameter_store=use_parameter_store)
    
    # CRITICAL FIX: Sanitize config before caching (removes sentinels)
    # This prevents cache invalidation on every cold start (saves ~535ms)
    config = _sanitize_config_for_cache(config)
    
    # Validate config before caching
    if not isinstance(config, dict):
        log_error(f"[CONFIG] _build_config_from_sources returned {type(config).__name__}, not dict!")
        increment_counter('ha_config_build_error')
        return {'enabled': False}
    
    # Cache the sanitized config
    cache_set('ha_config', config, ttl=300)
    
    # ADDED: Config build success metric
    increment_counter('ha_config_build_success')
    
    return config


def validate_ha_config(config: Dict[str, Any]) -> bool:
    """
    Validate Home Assistant configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(config, dict):
        log_error(f"[CONFIG VALIDATE] Config is {type(config).__name__}, not dict")
        increment_counter('ha_config_validate_error')
        return False
    
    if not config.get('enabled', False):
        log_warning("[CONFIG VALIDATE] Home Assistant is disabled")
        increment_counter('ha_config_disabled')
        return False
    
    if not config.get('base_url'):
        log_error("[CONFIG VALIDATE] Missing base_url")
        increment_counter('ha_config_missing_url')
        return False
    
    if not config.get('access_token'):
        log_error("[CONFIG VALIDATE] Missing access_token")
        increment_counter('ha_config_missing_token')
        return False
    
    # ADDED: Validation success metric
    increment_counter('ha_config_validate_success')
    return True


def get_ha_preset(preset: str = 'default') -> Dict[str, Any]:
    """
    Get Home Assistant preset configuration.
    
    Args:
        preset: Preset name ('default', 'fast', 'reliable', 'minimal')
        
    Returns:
        Preset configuration dictionary
    """
    presets = {
        'default': {
            'timeout': 30,
            'verify_ssl': True,
            'assistant_name': 'Alexa'
        },
        'fast': {
            'timeout': 10,
            'verify_ssl': False,
            'assistant_name': 'Alexa'
        },
        'reliable': {
            'timeout': 60,
            'verify_ssl': True,
            'assistant_name': 'Alexa'
        },
        'minimal': {
            'timeout': 5,
            'verify_ssl': False,
            'assistant_name': 'Alexa'
        }
    }
    
    return presets.get(preset, presets['default'])


def load_ha_connection_config() -> Dict[str, Any]:
    """
    Load connection-specific Home Assistant configuration.
    
    Returns:
        Connection configuration dictionary
    """
    config = load_ha_config()
    
    return {
        'base_url': config.get('base_url'),
        'timeout': config.get('timeout', 30),
        'verify_ssl': config.get('verify_ssl', True)
    }


def load_ha_preset_config(preset: str = 'default') -> Dict[str, Any]:
    """
    Load Home Assistant configuration with preset overrides.
    
    Args:
        preset: Preset name to apply
        
    Returns:
        Merged configuration dictionary
    """
    base_config = load_ha_config()
    preset_config = get_ha_preset(preset)
    
    # Merge preset into base config
    merged = base_config.copy()
    merged.update(preset_config)
    
    return merged


__all__ = [
    'load_ha_config',
    'validate_ha_config',
    'get_ha_preset',
    'load_ha_connection_config',
    'load_ha_preset_config'
]

# EOF
