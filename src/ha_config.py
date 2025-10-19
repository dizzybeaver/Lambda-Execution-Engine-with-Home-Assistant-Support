"""
ha_config.py - Home Assistant Configuration Management
Version: 2025.10.19.TIMING_MODULE_IMPORT
Description: CRITICAL FIX - Module-level config_param_store import for performance

CHANGELOG:
- 2025.10.19.TIMING_MODULE_IMPORT: CRITICAL PERFORMANCE FIX
  - Moved config_param_store import to MODULE LEVEL (was lazy loaded in function)
  - This ensures 7.7s boto3 load happens during Lambda INIT (257ms), not first request
  - DESIGN DECISION: Always import config_param_store, even if SSM disabled
  - Reason: Import cost is negligible if USE_PARAMETER_STORE=false (boto3 won't load)
  - Root cause: Lazy import inside _get_config_value() caused 7.7s first-request penalty
  - All timing diagnostics preserved for debugging
- 2025.10.19.TIMING: Added comprehensive timing diagnostics
- 2025.10.19.07: SSM-first with environment fallback
- 2025.10.19.06: Emergency fix for environment-only mode

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).

Design Decisions:
- Module-level config_param_store import: Always import at module level
  Reason: Lazy import defeats performance optimization, causes 7.7s first-request delay
- config_param_store handles its own boto3 loading: Conditional based on USE_PARAMETER_STORE
  Reason: If SSM disabled, config_param_store import is cheap (no boto3 load)
"""

from typing import Dict, Any, Optional
import os
import time

# CRITICAL: Import config_param_store at MODULE LEVEL for performance!
# This ensures boto3 initialization (7.7s) happens during Lambda INIT, not first request
from config_param_store import get_parameter as ssm_get_parameter

from gateway import (
    cache_get,
    cache_set,
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


def _safe_int(value: str, default: int) -> int:
    """Safely convert string to int with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# ===== CONFIGURATION MANAGEMENT =====

def _get_config_value(
    key: str,
    env_var: str,
    default: Any = None,
    use_parameter_store: bool = False
) -> Optional[str]:
    """
    Get configuration value with SSM-first priority.
    
    Priority (when USE_PARAMETER_STORE=true):
    1. SSM Parameter Store (PRIMARY SOURCE)
    2. Environment variable (FALLBACK)
    3. Default value
    
    Priority (when USE_PARAMETER_STORE=false):
    1. Environment variable (PRIMARY SOURCE)
    2. Default value
    
    PERFORMANCE: config_param_store is imported at MODULE LEVEL (not here)
    to ensure boto3 initialization happens during Lambda INIT phase.
    
    Args:
        key: SSM parameter key (e.g., 'home_assistant/url')
        env_var: Environment variable name (e.g., 'HOME_ASSISTANT_URL')
        default: Default value if not found
        use_parameter_store: Whether to try SSM first
        
    Returns:
        Configuration value or None
    """
    _start = time.perf_counter()
    _print_timing(f"  _get_config_value START: key={key}, env_var={env_var}")
    _print_timing(f"    USE_PARAMETER_STORE={use_parameter_store}")
    
    # === Priority 1: SSM Parameter Store (if enabled) ===
    if use_parameter_store:
        _ssm_start = time.perf_counter()
        _print_timing(f"    Attempting SSM lookup for {key}...")
        
        # NOTE: config_param_store is ALREADY imported at module level!
        # No lazy import overhead here - ssm_get_parameter is immediately available
        value = ssm_get_parameter(key, default=None)
        
        _ssm_time = (time.perf_counter() - _ssm_start) * 1000
        _print_timing(f"    *** SSM lookup completed: {_ssm_time:.2f}ms ***")
        
        if value is not None:
            _total_time = (time.perf_counter() - _start) * 1000
            _print_timing(f"  [SSM SUCCESS] {key}: {_total_time:.2f}ms")
            return value
        else:
            _print_timing(f"    [SSM MISS] {key}: Not found in SSM, falling back to environment")
    
    # === Priority 2: Environment variable (fallback or primary if SSM disabled) ===
    _env_start = time.perf_counter()
    _print_timing(f"    Checking environment variable {env_var}...")
    
    value = os.environ.get(env_var)
    
    _env_time = (time.perf_counter() - _env_start) * 1000
    
    if value is not None:
        _total_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"  [ENV SUCCESS] {key}: {_total_time:.2f}ms")
        
        if use_parameter_store:
            log_info(f"[CONFIG] {key}: Using environment variable fallback (SSM miss)")
        else:
            log_debug(f"[CONFIG] {key}: Using environment variable (SSM disabled)")
        
        return value
    
    # === Priority 3: Default value ===
    _total_time = (time.perf_counter() - _start) * 1000
    _print_timing(f"  [DEFAULT] {key}: {_total_time:.2f}ms")
    
    if default is not None:
        log_warning(f"[CONFIG] {key}: Using default value (not found in SSM or environment)")
    
    return default


def _build_config_from_sources(use_parameter_store: bool = False) -> Dict[str, Any]:
    """
    Build configuration from SSM Parameter Store or environment variables.
    
    This function is instrumented with comprehensive timing to show exactly
    where configuration loading time is spent.
    
    Args:
        use_parameter_store: Whether to use SSM Parameter Store
        
    Returns:
        Configuration dictionary
    """
    _start = time.perf_counter()
    _print_timing("===== _build_config_from_sources START =====")
    
    # Check if HA is enabled
    _print_timing("Getting enabled status...")
    _enabled_start = time.perf_counter()
    enabled_str = os.environ.get('HOME_ASSISTANT_ENABLED', 'true').lower()
    enabled = enabled_str in ('true', '1', 'yes')
    _enabled_time = (time.perf_counter() - _enabled_start) * 1000
    _print_timing(f"Enabled check: {_enabled_time:.2f}ms, enabled={enabled}")
    
    if not enabled:
        _print_timing(f"===== _build_config_from_sources COMPLETE: {(time.perf_counter() - _start) * 1000:.2f}ms =====")
        return {'enabled': False}
    
    # Get base URL
    _print_timing("Getting base_url...")
    _url_start = time.perf_counter()
    base_url = _get_config_value(
        'home_assistant/url',
        'HOME_ASSISTANT_URL',
        use_parameter_store=use_parameter_store
    )
    _url_time = (time.perf_counter() - _url_start) * 1000
    _print_timing(f"*** base_url retrieved: {_url_time:.2f}ms ***")
    
    # Get access token
    _print_timing("Getting access_token...")
    _token_start = time.perf_counter()
    access_token = _get_config_value(
        'home_assistant/token',
        'HOME_ASSISTANT_TOKEN',
        use_parameter_store=use_parameter_store
    )
    _token_time = (time.perf_counter() - _token_start) * 1000
    _print_timing(f"*** access_token retrieved: {_token_time:.2f}ms ***")
    
    # Get timeout
    _print_timing("Getting timeout...")
    _timeout_start = time.perf_counter()
    timeout_str = _get_config_value(
        'home_assistant/timeout',
        'HOME_ASSISTANT_TIMEOUT',
        default='30',
        use_parameter_store=use_parameter_store
    )
    timeout = _safe_int(timeout_str, 30)
    _timeout_time = (time.perf_counter() - _timeout_start) * 1000
    _print_timing(f"timeout retrieved: {_timeout_time:.2f}ms")
    
    # Get verify_ssl
    _print_timing("Getting verify_ssl...")
    _ssl_start = time.perf_counter()
    verify_ssl_str = _get_config_value(
        'home_assistant/verify_ssl',
        'HOME_ASSISTANT_VERIFY_SSL',
        default='true',
        use_parameter_store=use_parameter_store
    )
    verify_ssl = verify_ssl_str.lower() in ('true', '1', 'yes')
    _ssl_time = (time.perf_counter() - _ssl_start) * 1000
    _print_timing(f"verify_ssl retrieved: {_ssl_time:.2f}ms")
    
    # Get assistant name
    _print_timing("Getting assistant_name...")
    _name_start = time.perf_counter()
    assistant_name = _get_config_value(
        'home_assistant/assistant_name',
        'HA_ASSISTANT_NAME',
        default='Alexa',
        use_parameter_store=use_parameter_store
    )
    _name_time = (time.perf_counter() - _name_start) * 1000
    _print_timing(f"assistant_name retrieved: {_name_time:.2f}ms")
    
    config = {
        'enabled': True,
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
    Load Home Assistant configuration with caching and comprehensive timing.
    
    Configuration priority:
    1. Cache (if not force_refresh)
    2. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    3. Environment variables (fallback or primary if SSM disabled)
    4. Defaults
    
    Args:
        force_refresh: Skip cache and reload from sources
        
    Returns:
        Configuration dictionary
    """
    _start = time.perf_counter()
    _print_timing("===== LOAD_HA_CONFIG START =====")
    
    # Check cache first
    if not force_refresh:
        _cache_start = time.perf_counter()
        _print_timing("Checking cache...")
        
        cached = cache_get('ha_config')
        
        _cache_time = (time.perf_counter() - _cache_start) * 1000
        _print_timing(f"Cache check: {_cache_time:.2f}ms, found={cached is not None}")
        
        if cached is not None:
            _total_time = (time.perf_counter() - _start) * 1000
            _print_timing(f"===== LOAD_HA_CONFIG COMPLETE (CACHED): {_total_time:.2f}ms =====")
            return cached
    
    # Build fresh config
    _print_timing("Building fresh config...")
    _build_start = time.perf_counter()
    
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    config = _build_config_from_sources(use_parameter_store=use_parameter_store)
    
    _build_time = (time.perf_counter() - _build_start) * 1000
    _print_timing(f"*** Config built: {_build_time:.2f}ms ***")
    
    # Cache result
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
    if not config.get('enabled', False):
        log_warning("[CONFIG] Home Assistant is disabled")
        return False
    
    if not config.get('base_url'):
        log_error("[CONFIG] Missing base_url")
        return False
    
    if not config.get('access_token'):
        log_error("[CONFIG] Missing access_token")
        return False
    
    return True


def get_ha_preset(preset: str = 'default') -> Dict[str, Any]:
    """
    Get Home Assistant preset configuration.
    
    Presets provide predefined configurations for common scenarios.
    
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
    
    Returns only connection-related settings without full config.
    
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
    
    Merges base configuration with preset values.
    
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
