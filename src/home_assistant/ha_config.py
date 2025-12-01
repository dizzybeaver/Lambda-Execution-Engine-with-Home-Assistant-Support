# ha_config.py
"""
ha_config.py - Home Assistant Configuration Management
Version: 3.0.0
Description: Configuration with debug tracing and timing metrics

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
    log_error,
    generate_correlation_id,
    record_metric,
    increment_counter
)

# ===== MODULE-LEVEL DEBUG MODE =====
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Timing thresholds
HA_SLOW_CONFIG_LOAD_THRESHOLD_MS = 1000  # 1 second

def _debug_trace(correlation_id: str, step: str, **details):
    """
    Debug trace helper for HA config operations.
    
    Args:
        correlation_id: Correlation ID for request tracing
        step: Step description
        **details: Additional details to log
    """
    if _DEBUG_MODE_ENABLED:
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [CONFIG-TRACE] {step}" + (f" ({detail_str})" if detail_str else ""))


# ===== TOKEN LOADING (SSM TOKEN-ONLY) =====

def _load_token(use_parameter_store: bool, correlation_id: str) -> str:
    """
    Load Home Assistant token from SSM or environment.
    
    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. HOME_ASSISTANT_TOKEN environment variable
    3. LONG_LIVED_ACCESS_TOKEN environment variable (legacy)
    4. Empty string
    
    Args:
        use_parameter_store: Whether to try SSM first
        correlation_id: Correlation ID for tracing
        
    Returns:
        Token string (may be empty)
    """
    start_time = time.perf_counter()
    _debug_trace(correlation_id, "_load_token START", use_parameter_store=use_parameter_store)
    
    token = ''
    
    try:
        # Try SSM first if enabled
        if use_parameter_store:
            _debug_trace(correlation_id, "Attempting SSM token load")
            try:
                from config_param_store import get_ha_token
                
                ssm_start = time.perf_counter()
                token = get_ha_token(use_cache=True)
                ssm_duration_ms = (time.perf_counter() - ssm_start) * 1000
                
                record_metric('ha_config_ssm_duration_ms', ssm_duration_ms)
                
                if token and isinstance(token, str):
                    _debug_trace(correlation_id, "Token loaded from SSM", 
                                length=len(token), duration_ms=ssm_duration_ms)
                    log_info(f"[{correlation_id}] Token loaded from SSM (length={len(token)})")
                    increment_counter('ha_config_ssm_token_success')
                    return token
                else:
                    _debug_trace(correlation_id, "SSM returned no token, falling back")
                    log_warning(f"[{correlation_id}] SSM returned no token, falling back to environment")
                    increment_counter('ha_config_ssm_token_miss')
                    
            except Exception as e:
                _debug_trace(correlation_id, "SSM exception", error=str(e))
                log_error(f"[{correlation_id}] SSM error: {e}, falling back to environment")
                increment_counter('ha_config_ssm_error')
                
                if _DEBUG_MODE_ENABLED:
                    import traceback
                    log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        # Fallback to environment variables
        _debug_trace(correlation_id, "Loading token from environment")
        token = os.environ.get('HOME_ASSISTANT_TOKEN') or os.environ.get('LONG_LIVED_ACCESS_TOKEN') or ''
        
        if token:
            _debug_trace(correlation_id, "Token loaded from environment", length=len(token))
            log_info(f"[{correlation_id}] Token loaded from environment (length={len(token)})")
            increment_counter('ha_config_env_token_success')
        else:
            _debug_trace(correlation_id, "No token found in environment")
            log_error(f"[{correlation_id}] No token found in environment variables")
            increment_counter('ha_config_no_token')
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "_load_token COMPLETE", duration_ms=duration_ms, found=bool(token))
        
        return token
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "_load_token FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] Token load failed: {e}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_config_token_error')
        record_metric('ha_config_token_error_duration_ms', duration_ms)
        return ''


# ===== CONFIGURATION BUILDING =====

def _build_config_from_sources(use_parameter_store: bool, correlation_id: str) -> Dict[str, Any]:
    """
    Build configuration from sources.
    
    All config from environment EXCEPT token (which may come from SSM).
    
    Args:
        use_parameter_store: Whether to use SSM for token
        correlation_id: Correlation ID for tracing
        
    Returns:
        Configuration dictionary
    """
    start_time = time.perf_counter()
    _debug_trace(correlation_id, "_build_config_from_sources START")
    
    try:
        # Check if HA is enabled
        _debug_trace(correlation_id, "Getting enabled status")
        enabled_str = os.environ.get('HOME_ASSISTANT_ENABLED', 'true').lower()
        enabled = enabled_str in ('true', '1', 'yes')
        _debug_trace(correlation_id, "Enabled status", enabled=enabled)
        
        if not enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            _debug_trace(correlation_id, "_build_config_from_sources COMPLETE (DISABLED)", duration_ms=duration_ms)
            return {'enabled': False}
        
        # Get base URL from environment
        _debug_trace(correlation_id, "Getting base_url")
        base_url = os.environ.get('HOME_ASSISTANT_URL', '')
        
        # Get access token (SSM or environment)
        _debug_trace(correlation_id, "Getting access_token")
        token_start = time.perf_counter()
        access_token = _load_token(use_parameter_store, correlation_id)
        token_duration_ms = (time.perf_counter() - token_start) * 1000
        _debug_trace(correlation_id, "Token loaded", duration_ms=token_duration_ms, found=bool(access_token))
        
        # Get timeout from environment
        _debug_trace(correlation_id, "Getting timeout")
        timeout_str = os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')
        try:
            timeout = int(timeout_str)
        except (ValueError, TypeError):
            timeout = 30
            _debug_trace(correlation_id, "Invalid timeout, using default", default=30)
        
        # Get verify_ssl from environment
        _debug_trace(correlation_id, "Getting verify_ssl")
        verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
        verify_ssl = verify_ssl_str in ('true', '1', 'yes')
        
        # Get assistant name from environment
        _debug_trace(correlation_id, "Getting assistant_name")
        assistant_name = os.environ.get('HA_ASSISTANT_NAME', 'Alexa')
        
        # Build config dict
        config = {
            'enabled': enabled,
            'base_url': base_url,
            'access_token': access_token,
            'timeout': timeout,
            'verify_ssl': verify_ssl,
            'assistant_name': assistant_name
        }
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "_build_config_from_sources COMPLETE", duration_ms=duration_ms)
        record_metric('ha_config_build_duration_ms', duration_ms)
        
        return config
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "_build_config_from_sources FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] Config build failed: {e}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_config_build_error')
        record_metric('ha_config_build_error_duration_ms', duration_ms)
        raise


def load_ha_config(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Load Home Assistant configuration.
    
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
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "load_ha_config START", force_refresh=force_refresh)
    
    try:
        # Check cache first if not force refresh
        if not force_refresh:
            cache_start = time.perf_counter()
            _debug_trace(correlation_id, "Checking cache")
            
            cached = cache_get('ha_config')
            
            cache_duration_ms = (time.perf_counter() - cache_start) * 1000
            record_metric('ha_config_cache_check_duration_ms', cache_duration_ms)
            
            if cached and isinstance(cached, dict) and 'enabled' in cached:
                duration_ms = (time.perf_counter() - start_time) * 1000
                _debug_trace(correlation_id, "load_ha_config COMPLETE (CACHE)", duration_ms=duration_ms)
                record_metric('ha_config_load_duration_ms', duration_ms)
                increment_counter('ha_config_cache_hit')
                return cached
            else:
                _debug_trace(correlation_id, "Cache miss or invalid")
                increment_counter('ha_config_cache_miss')
        
        # Build fresh config
        _debug_trace(correlation_id, "Building fresh config")
        build_start = time.perf_counter()
        
        use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
        config = _build_config_from_sources(use_parameter_store, correlation_id)
        
        build_duration_ms = (time.perf_counter() - build_start) * 1000
        _debug_trace(correlation_id, "Config built", duration_ms=build_duration_ms)
        
        # Cache the config
        cache_set_start = time.perf_counter()
        _debug_trace(correlation_id, "Caching config")
        
        cache_set('ha_config', config, ttl=600)
        
        cache_set_duration_ms = (time.perf_counter() - cache_set_start) * 1000
        record_metric('ha_config_cache_set_duration_ms', cache_set_duration_ms)
        _debug_trace(correlation_id, "Config cached", duration_ms=cache_set_duration_ms)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Slow operation detection
        if duration_ms > HA_SLOW_CONFIG_LOAD_THRESHOLD_MS:
            log_warning(f"[{correlation_id}] Slow config load: {duration_ms:.2f}ms")
            increment_counter('ha_config_slow_load')
        
        _debug_trace(correlation_id, "load_ha_config COMPLETE", duration_ms=duration_ms)
        record_metric('ha_config_load_duration_ms', duration_ms)
        increment_counter('ha_config_load_success')
        
        return config
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "load_ha_config FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] Config load failed: {e}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_config_load_error')
        record_metric('ha_config_load_error_duration_ms', duration_ms)
        raise


def validate_ha_config(config: Dict[str, Any]) -> bool:
    """
    Validate Home Assistant configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "validate_ha_config START")
    
    try:
        if not isinstance(config, dict):
            _debug_trace(correlation_id, "Config not a dict", type=type(config).__name__)
            log_error(f"[{correlation_id}] Config is {type(config).__name__}, not dict")
            increment_counter('ha_config_validate_error_type')
            return False
        
        if not config.get('enabled', False):
            _debug_trace(correlation_id, "HA disabled")
            log_warning(f"[{correlation_id}] Home Assistant is disabled")
            increment_counter('ha_config_validate_disabled')
            return False
        
        if not config.get('base_url'):
            _debug_trace(correlation_id, "Missing base_url")
            log_error(f"[{correlation_id}] Missing base_url")
            increment_counter('ha_config_validate_error_url')
            return False
        
        if not config.get('access_token'):
            _debug_trace(correlation_id, "Missing access_token")
            log_error(f"[{correlation_id}] Missing access_token")
            increment_counter('ha_config_validate_error_token')
            return False
        
        _debug_trace(correlation_id, "validate_ha_config COMPLETE (VALID)")
        increment_counter('ha_config_validate_success')
        return True
        
    except Exception as e:
        _debug_trace(correlation_id, "validate_ha_config FAILED", error=str(e))
        log_error(f"[{correlation_id}] Validation failed: {e}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_config_validate_error')
        return False


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
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "load_ha_connection_config START")
    
    config = load_ha_config()
    
    connection_config = {
        'base_url': config.get('base_url'),
        'timeout': config.get('timeout', 30),
        'verify_ssl': config.get('verify_ssl', True)
    }
    
    _debug_trace(correlation_id, "load_ha_connection_config COMPLETE")
    return connection_config


def load_ha_preset_config(preset: str = 'default') -> Dict[str, Any]:
    """
    Load Home Assistant configuration with preset overrides.
    
    Args:
        preset: Preset name to apply
        
    Returns:
        Merged configuration dictionary
    """
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "load_ha_preset_config START", preset=preset)
    
    base_config = load_ha_config()
    preset_config = get_ha_preset(preset)
    
    # Merge preset into base config
    merged = base_config.copy()
    merged.update(preset_config)
    
    _debug_trace(correlation_id, "load_ha_preset_config COMPLETE")
    return merged


__all__ = [
    'load_ha_config',
    'validate_ha_config',
    'get_ha_preset',
    'load_ha_connection_config',
    'load_ha_preset_config'
]

# EOF
