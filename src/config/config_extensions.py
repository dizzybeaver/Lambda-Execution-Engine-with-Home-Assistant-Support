"""
config_extensions.py - Configuration Extensions
Version: 2025.10.02.02
Description: Extends existing config_core.py with hot-reload and versioning

ARCHITECTURE: EXTENSION - Extends existing config_core.py
- Uses shared_utilities exclusively
- Wraps existing config_core functions
- Adds versioning layer only

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP + LUGS Compatible
"""

from typing import Dict, Any
import time

def enable_config_hot_reload(check_interval: int = 60) -> Dict[str, Any]:
    """Enable hot reload using existing config."""
    from gateway import cache_set, log_info, create_success_response
    
    config = {
        'enabled': True,
        'check_interval': check_interval,
        'last_check': time.time()
    }
    
    cache_set('config_hot_reload', config, ttl=86400)
    log_info(f"Config hot reload enabled: {check_interval}s interval")
    
    return create_success_response("Hot reload enabled", config)


def reload_config_if_changed() -> Dict[str, Any]:
    """Check and reload config if changed."""
    from gateway import cache_get, cache_set, log_info, get_parameter
    from shared_utilities import create_operation_context, close_operation_context
    
    context = create_operation_context('config', 'reload_check')
    
    try:
        hot_reload = cache_get('config_hot_reload')
        if not hot_reload or not hot_reload.get('enabled'):
            close_operation_context(context, success=True)
            return {'reloaded': False, 'reason': 'Hot reload disabled'}
        
        current_version = get_parameter('CONFIG_VERSION', '1.0.0')
        cached_version = cache_get('config_version') or '1.0.0'
        
        if current_version != cached_version:
            cache_set('config_version', current_version, ttl=86400)
            log_info(f"Config version changed: {cached_version} -> {current_version}")
            close_operation_context(context, success=True)
            return {'reloaded': True, 'old_version': cached_version, 'new_version': current_version}
        
        close_operation_context(context, success=True)
        return {'reloaded': False, 'reason': 'No changes detected'}
        
    except Exception as e:
        from shared_utilities import handle_operation_error
        return handle_operation_error('config', 'reload_check', e, context['correlation_id'])


def register_config_preset(name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Register config preset using existing validation."""
    from gateway import cache_set, validate_request, create_success_response, create_error_response
    from shared_utilities import validate_operation_parameters
    
    validation = validate_operation_parameters(
        required_params=['name', 'config'],
        name=name,
        config=config
    )
    
    if not validation['valid']:
        return create_error_response("Invalid preset", 'VALIDATION_ERROR', validation)
    
    preset_key = f"config_preset_{name}"
    cache_set(preset_key, config, ttl=86400)
    
    presets = cache_get('config_presets_list') or []
    if name not in presets:
        presets.append(name)
        cache_set('config_presets_list', presets, ttl=86400)
    
    return create_success_response(f"Preset '{name}' registered", {'name': name, 'fields': len(config)})


def switch_config_preset(name: str) -> Dict[str, Any]:
    """Switch to config preset."""
    from gateway import cache_get, cache_set, create_success_response, create_error_response, log_info
    
    preset = cache_get(f"config_preset_{name}")
    if not preset:
        return create_error_response(f"Preset '{name}' not found", 'PRESET_NOT_FOUND')
    
    cache_set('active_config_preset', name, ttl=86400)
    log_info(f"Switched to config preset: {name}")
    
    return create_success_response(f"Switched to preset '{name}'", {'preset': name})


def get_config_state() -> Dict[str, Any]:
    """Get current config state."""
    from gateway import cache_get, create_success_response
    
    state = {
        'hot_reload': cache_get('config_hot_reload') or {'enabled': False},
        'current_version': cache_get('config_version') or '1.0.0',
        'active_preset': cache_get('active_config_preset'),
        'available_presets': cache_get('config_presets_list') or []
    }
    
    return create_success_response("Config state retrieved", state)


# EOF
