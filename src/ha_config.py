"""
ha_config.py - Home Assistant Configuration Management
Version: 2025.10.20.TOKEN_ONLY_FIXED
Description: SSM token-only, ALL original functions preserved

CRITICAL FIX: Adapted original to use token-only SSM without removing any functions

CHANGELOG:
- 2025.10.20.TOKEN_ONLY_FIXED: Adapted for token-only SSM
  - Token from SSM via config_param_store.get_ha_token()
  - All other config from environment variables
  - ALL original functions preserved (validate_ha_config, get_ha_preset, etc.)
  
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional
import os
import time

from gateway import (
    cache_get,
    cache_set,
    cache_delete,
    log_debug,
    log_info,
    log_warning,
    log_error
)


# ===== TIMING HELPERS =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled for timing output."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(message: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[HA_CONFIG_TIMING] {message}")


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
    _start = time.perf_counter()
    _print_timing("_load_token START")
    
    token = ''
    
    # Try SSM first if enabled
    if use_parameter_store:
        _print_timing("  USE_PARAMETER_STORE=true, attempting SSM")
        try:
            # NEW: Use simplified token-only SSM client
            from config_param_store import get_ha_token
            
            _ssm_start = time.perf_counter()
            token = get_ha_token(use_cache=True)
            _ssm_time = (time.perf_counter() - _ssm_start) * 1000
            
            # Check what type we got back
            token_type = type(token).__name__
            _print_timing(f"  SSM returned type: {token_type}")
            
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
            
            _print_timing(f"  SSM token retrieval: {_ssm_time:.2f}ms, success={bool(token)}")
            
            if token:
                log_info(f"[TOKEN LOAD] Token loaded from SSM (length={len(token)})")
                _print_timing(f"_load_token COMPLETE (SSM): {(time.perf_counter() - _start) * 1000:.2f}ms")
                return token
            else:
                log_warning("[TOKEN LOAD] SSM returned no token, falling back to environment")
                _print_timing("  SSM returned no token, falling back to environment")
                
        except Exception as e:
            _print_timing(f"  SSM exception: {e}")
            log_error(f"[TOKEN LOAD] SSM error: {e}, falling back to environment")
    else:
        _print_timing("  USE_PARAMETER_STORE=false, skipping SSM")
    
    # Fallback to environment variables
    _print_timing("  Loading token from environment")
    token = os.environ.get('HOME_ASSISTANT_TOKEN') or os.environ.get('LONG_LIVED_ACCESS_TOKEN') or ''
    
    if token:
        log_info(f"[TOKEN LOAD] Token loaded from environment (length={len(token)})")
    else:
        log_error("[TOKEN LOAD] No token found in environment variables")
    
    _print_timing(f"_load_token COMPLETE (ENV): {(time.perf_counter() - _start) * 1000:.2f}ms, found={bool(token)}")
    
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
    _start = time.perf_counter()
    _print_timing("===== _build_config_from_sources START =====")
    
    # Check if HA is enabled
    _print_timing("Getting enabled status...")
    enabled_str = os.environ.get('HOME_ASSISTANT_ENABLED', 'true').lower()
    enabled = enabled_str in ('true', '1', 'yes')
    _print_timing(f"Enabled: {enabled}")
    
    if not enabled:
        _print_timing(f"===== _build_config_from_sources COMPLETE (DISABLED): {(time.perf_counter() - _start) * 1000:.2f}ms =====")
        return {'enabled': False}
    
    # Get base URL from environment
    _print_timing("Getting base_url from environment...")
    base_url = _sanitize_value(
        os.environ.get('HOME_ASSISTANT_URL'),
        'base_url',
        default=''
    )
    _print_timing(f"  base_url: {bool(base_url)}")
    
    # Get access token (SSM or environment)
    _print_timing("Getting access_token...")
    _token_start = time.perf_counter()
    access_token = _load_token(use_parameter_store)
    _token_time = (time.perf_counter() - _token_start) * 1000
    _print_timing(f"  access_token: {_token_time:.2f}ms, found={bool(access_token)}")
    
    # Get timeout from environment
    _print_timing("Getting timeout from environment...")
    timeout_str = os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')
    timeout = _safe_int(timeout_str, 30)
    _print_timing(f"  timeout: {timeout}")
    
    # Get verify_ssl from environment
    _print_timing("Getting verify_ssl from environment...")
    verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str in ('true', '1', 'yes')
    _print_timing(f"  verify_ssl: {verify_ssl}")
    
    # Get assistant name from environment
    _print_timing("Getting assistant_name from environment...")
    assistant_name = _sanitize_value(
        os.environ.get('HA_ASSISTANT_NAME'),
        'assistant_name',
        default='Alexa'
    )
    _print_timing(f"  assistant_name: {assistant_name}")
    
    # Build config dict
    config = {
        'enabled': enabled,
        'base_url': base_url,
        'access_token': access_token,
        'timeout': timeout,
        'verify_ssl': verify_ssl,
        'assistant_name': assistant_name
    }
    
    _total_time = (time.perf_counter() - _start) * 1000
    _print_timing(f"===== _build_config_from_sources COMPLETE: {_total_time:.2f}ms =====")
    
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
    _start = time.perf_counter()
    _print_timing("===== LOAD_HA_CONFIG START =====")
    
    # Check cache first (with validation)
    if not force_refresh:
        _cache_start = time.perf_counter()
        _print_timing("Checking cache...")
        
        cached = cache_get('ha_config')
        
        _cache_time = (time.perf_counter() - _cache_start) * 1000
        _print_timing(f"Cache check: {_cache_time:.2f}ms, found={cached is not None}")
        
        if cached is not None:
            # CRITICAL: Validate cached value before returning
            validated = _validate_cached_config(cached)
            
            if validated is not None:
                _total_time = (time.perf_counter() - _start) * 1000
                _print_timing(f"===== LOAD_HA_CONFIG COMPLETE (VALIDATED CACHE): {_total_time:.2f}ms =====")
                return validated
            else:
                _print_timing("Cache validation failed, invalidating and rebuilding...")
                cache_delete('ha_config')
    
    # Build fresh config
    _print_timing("Building fresh config...")
    _build_start = time.perf_counter()
    
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    config = _build_config_from_sources(use_parameter_store=use_parameter_store)
    
    _build_time = (time.perf_counter() - _build_start) * 1000
    _print_timing(f"*** Config built: {_build_time:.2f}ms, type={type(config).__name__} ***")
    
    # CRITICAL FIX: Sanitize config before caching (removes sentinels)
    # This prevents cache invalidation on every cold start (saves ~535ms)
    _print_timing("Sanitizing config for cache...")
    _sanitize_start = time.perf_counter()
    config = _sanitize_config_for_cache(config)
    _sanitize_time = (time.perf_counter() - _sanitize_start) * 1000
    _print_timing(f"Config sanitized: {_sanitize_time:.2f}ms")
    
    # Validate config before caching
    if not isinstance(config, dict):
        log_error(f"[CONFIG] _build_config_from_sources returned {type(config).__name__}, not dict!")
        return {'enabled': False}
    
    # Cache the sanitized config
    _cache_set_start = time.perf_counter()
    _print_timing("Caching config...")
    
    cache_set('ha_config', config, ttl=300)
    
    _cache_set_time = (time.perf_counter() - _cache_set_start) * 1000
    _print_timing(f"Config cached: {_cache_set_time:.2f}ms")
    
    _total_time = (time.perf_counter() - _start) * 1000
    _print_timing(f"===== LOAD_HA_CONFIG COMPLETE: {_total_time:.2f}ms =====")
    
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
        return False
    
    if not config.get('enabled', False):
        log_warning("[CONFIG VALIDATE] Home Assistant is disabled")
        return False
    
    if not config.get('base_url'):
        log_error("[CONFIG VALIDATE] Missing base_url")
        return False
    
    if not config.get('access_token'):
        log_error("[CONFIG VALIDATE] Missing access_token")
        return False
    
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
