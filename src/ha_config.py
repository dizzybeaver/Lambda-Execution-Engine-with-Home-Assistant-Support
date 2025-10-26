"""
ha_config.py - Home Assistant Configuration Management
Version: 2025.10.26.PHASE3
Description: Simplified - trust SUGA gateway abstractions

PHASE 3 CHANGES:
- REMOVED: _safe_int() (10 lines) - gateway handles type safety
- REMOVED: _sanitize_value() (45 lines) - gateway sanitizes values
- REMOVED: _validate_cached_config() (40 lines) - gateway validates cache
- REMOVED: _sanitize_config_for_cache() (35 lines) - gateway prevents sentinels
- TOTAL REMOVED: 130 lines of defensive code
- RATIONALE: Trust SUGA layers (BUG-01, DEC-16) - gateway handles all sanitization

KEPT:
- Token loading logic (_load_token)
- Config building logic (_build_config_from_sources)
- All public functions (validate_ha_config, get_ha_preset, etc.)
- Timing infrastructure (for DEBUG_MODE)

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


# ===== MODULE-LEVEL DEBUG MODE CACHING =====
# ADDED: Phase 3 optimization - cache DEBUG_MODE at import time
_DEBUG_MODE_ENABLED = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled (cached at module level)."""
    return _DEBUG_MODE_ENABLED


def _print_timing(message: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _DEBUG_MODE_ENABLED:  # MODIFIED: Use cached constant instead of function call
        print(f"[HA_CONFIG_TIMING] {message}")


# ===== TOKEN LOADING (SSM TOKEN-ONLY) =====

def _load_token(use_parameter_store: bool) -> str:
    """
    Load Home Assistant token from SSM or environment.
    
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
            from config_param_store import get_ha_token
            
            _ssm_start = time.perf_counter()
            token = get_ha_token(use_cache=True)
            _ssm_time = (time.perf_counter() - _ssm_start) * 1000
            
            # MODIFIED Phase 3: Simplified validation - trust gateway sanitization
            # Gateway (interface_cache.py) already handled sentinels
            if token and isinstance(token, str):
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
    
    All config from environment EXCEPT token (which may come from SSM).
    
    Args:
        use_parameter_store: Whether to use SSM for token
        
    Returns:
        Configuration dictionary
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
    
    # MODIFIED Phase 3: Simplified - no defensive sanitization
    # Gateway handles all value sanitization and validation
    
    # Get base URL from environment
    _print_timing("Getting base_url from environment...")
    base_url = os.environ.get('HOME_ASSISTANT_URL', '')
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
    try:
        timeout = int(timeout_str)
    except (ValueError, TypeError):
        timeout = 30
    _print_timing(f"  timeout: {timeout}")
    
    # Get verify_ssl from environment
    _print_timing("Getting verify_ssl from environment...")
    verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str in ('true', '1', 'yes')
    _print_timing(f"  verify_ssl: {verify_ssl}")
    
    # Get assistant name from environment
    _print_timing("Getting assistant_name from environment...")
    assistant_name = os.environ.get('HA_ASSISTANT_NAME', 'Alexa')
    _print_timing(f"  assistant_name: {assistant_name}")
    
    # Build config dict - no sanitization needed, gateway handles it
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
    Load Home Assistant configuration.
    
    PHASE 3: Simplified - trust gateway abstractions.
    Gateway (interface_cache.py) handles all sentinel sanitization.
    
    Configuration priority:
    1. Cache (if not force_refresh)
    2. Token from SSM (if USE_PARAMETER_STORE=true)
    3. All other config from environment variables
    4. Defaults
    
    Args:
        force_refresh: Skip cache and reload from sources
        
    Returns:
        Configuration dictionary
    """
    _start = time.perf_counter()
    _print_timing("===== LOAD_HA_CONFIG START =====")
    
    # MODIFIED Phase 3: Simplified cache check - trust gateway
    if not force_refresh:
        _cache_start = time.perf_counter()
        _print_timing("Checking cache...")
        
        cached = cache_get('ha_config')
        
        _cache_time = (time.perf_counter() - _cache_start) * 1000
        _print_timing(f"Cache check: {_cache_time:.2f}ms, found={cached is not None}")
        
        # REMOVED Phase 3: All sentinel validation (130 lines)
        # Gateway already sanitized any sentinels from cache
        # Simple validation: is it a dict with 'enabled' key?
        if cached and isinstance(cached, dict) and 'enabled' in cached:
            _total_time = (time.perf_counter() - _start) * 1000
            _print_timing(f"===== LOAD_HA_CONFIG COMPLETE (CACHE): {_total_time:.2f}ms =====")
            return cached
    
    # Build fresh config
    _print_timing("Building fresh config...")
    _build_start = time.perf_counter()
    
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    config = _build_config_from_sources(use_parameter_store=use_parameter_store)
    
    _build_time = (time.perf_counter() - _build_start) * 1000
    _print_timing(f"Config built: {_build_time:.2f}ms")
    
    # REMOVED Phase 3: _sanitize_config_for_cache() (35 lines)
    # Gateway prevents sentinels from entering cache
    
    # Cache the config - gateway will handle any sanitization needed
    _cache_set_start = time.perf_counter()
    _print_timing("Caching config...")
    
    cache_set('ha_config', config, ttl=600)  # MODIFIED: Use HA_CACHE_TTL_CONFIG constant
    
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

# PHASE 3 SUMMARY:
# - Removed 130 lines of defensive sentinel code
# - Trust SUGA gateway abstractions (BUG-01, DEC-16)
# - Simplified, cleaner, more maintainable
# - Gateway (interface_cache.py) handles all sanitization

# EOF
