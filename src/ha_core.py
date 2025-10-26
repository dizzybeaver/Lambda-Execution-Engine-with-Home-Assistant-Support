"""
ha_config.py - Home Assistant Configuration Management
Version: 2025.10.26.PHASE3
Description: SSM token-only + Simplified validation (trust gateway)

CHANGELOG:
- 2025.10.26.PHASE3: Code quality improvements - simplified sentinel validation
  * REMOVED: _safe_int() function (10 lines) - no longer needed, gateway handles sentinels
  * REMOVED: _sanitize_value() function (45 lines) - gateway sanitizes at cache layer
  * REMOVED: _validate_cached_config() function (40 lines) - trust gateway sanitization
  * REMOVED: _sanitize_config_for_cache() function (35 lines) - gateway handles this
  * SIMPLIFIED: load_ha_config() - removed defensive sentinel checks
  * TOTAL REDUCTION: 130 lines of defensive code removed
  * RATIONALE: Gateway (interface_cache.py) handles all sentinel sanitization (BUG-01, DEC-16)
- 2025.10.26.PHASE2: Performance optimization - replaced custom timing with gateway metrics
- 2025.10.20.TOKEN_ONLY_FIXED: Adapted for token-only SSM
  
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
    token = ''
    
    # Try SSM first if enabled
    if use_parameter_store:
        try:
            from config_param_store import get_ha_token
            
            token = get_ha_token(use_cache=True)
            
            # Basic type check (gateway handles sentinel sanitization)
            if not isinstance(token, str):
                log_error(f"[TOKEN LOAD] SSM returned unexpected type: {type(token).__name__}")
                token = None
            
            if token:
                log_info(f"[TOKEN LOAD] Token loaded from SSM (length={len(token)})")
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
    
    All config from environment EXCEPT token (which may come from SSM).
    
    Args:
        use_parameter_store: Whether to use SSM for token
        
    Returns:
        Configuration dictionary
    """
    # Check if HA is enabled
    enabled_str = os.environ.get('HOME_ASSISTANT_ENABLED', 'true').lower()
    enabled = enabled_str in ('true', '1', 'yes')
    
    if not enabled:
        return {'enabled': False}
    
    # Get base URL from environment
    base_url = os.environ.get('HOME_ASSISTANT_URL', '').strip()
    
    # Get access token (SSM or environment)
    access_token = _load_token(use_parameter_store)
    
    # Get timeout from environment
    timeout_str = os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')
    try:
        timeout = int(timeout_str)
    except (ValueError, TypeError):
        timeout = 30
    
    # Get verify_ssl from environment
    verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str in ('true', '1', 'yes')
    
    # Get assistant name from environment
    assistant_name = os.environ.get('HA_ASSISTANT_NAME', 'Alexa').strip()
    if not assistant_name:
        assistant_name = 'Alexa'
    
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
    Load Home Assistant configuration.
    
    Configuration priority:
    1. Cache (if not force_refresh) - gateway handles sentinel sanitization
    2. Token from SSM (if USE_PARAMETER_STORE=true)
    3. All other config from environment variables
    4. Defaults
    
    Args:
        force_refresh: Skip cache and reload from sources
        
    Returns:
        Configuration dictionary
        
    Note: Gateway (interface_cache.py) handles all sentinel sanitization.
          We trust the gateway abstraction layer (SUGA compliance).
    """
    # Check cache first
    if not force_refresh:
        cached = cache_get('ha_config')
        
        if cached is not None:
            # Simple validation: Gateway already sanitized, just verify it's a dict
            if isinstance(cached, dict):
                increment_counter('ha_config_cache_hit')
                return cached
            else:
                # Unexpected type from cache (should never happen with gateway)
                log_error(f"[CONFIG] Cached config is {type(cached).__name__}, invalidating")
                increment_counter('ha_config_cache_invalid')
                cache_delete('ha_config')
        else:
            increment_counter('ha_config_cache_miss')
    else:
        increment_counter('ha_config_force_refresh')
    
    # Build fresh config
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    config = _build_config_from_sources(use_parameter_store=use_parameter_store)
    
    # Validate config before caching
    if not isinstance(config, dict):
        log_error(f"[CONFIG] _build_config_from_sources returned {type(config).__name__}, not dict!")
        increment_counter('ha_config_build_error')
        return {'enabled': False}
    
    # Cache the config (gateway will handle any sentinel sanitization automatically)
    cache_set('ha_config', config, ttl=300)
    
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
