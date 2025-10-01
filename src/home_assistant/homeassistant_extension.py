"""
homeassistant_extension.py - Home Assistant Integration Extension
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Complete Home Assistant integration with ultra-optimized architecture

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Revolutionary Gateway compliant (SUGA + LIGS)
- Ultra-optimized with ha_common shared utilities
- Lazy loading compatible
- 100% Free Tier AWS compliant
- Self-contained extension

Licensed under the Apache License, Version 2.0
"""

import os
import time
from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error, log_warning,
    make_get_request, make_post_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric,
    cache_get, cache_set, cache_clear
)


_ha_extension_initialized = False
_ha_config_cache = None


def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension."""
    global _ha_extension_initialized, _ha_config_cache
    
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Initializing HA Extension [{correlation_id}]")
        
        if _ha_extension_initialized:
            return create_success_response("Already initialized", {"initialized": True})
        
        if not is_ha_extension_enabled():
            log_warning("HA Extension is disabled")
            return create_error_response("Extension disabled", {"enabled": False})
        
        config = _get_ha_config()
        if not config:
            return create_error_response("Failed to load configuration", {})
        
        _ha_config_cache = config
        _ha_extension_initialized = True
        
        log_info(f"HA Extension initialized [{correlation_id}]")
        record_metric("ha_extension_initialized", 1.0)
        
        return create_success_response("HA Extension initialized", {
            "base_url": config.get("base_url"),
            "timeout": config.get("timeout"),
            "verify_ssl": config.get("verify_ssl"),
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"HA Extension initialization failed: {str(e)}")
        return create_error_response("Initialization failed", {"error": str(e)})


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    global _ha_extension_initialized, _ha_config_cache
    
    try:
        cache_clear()
        _ha_config_cache = None
        _ha_extension_initialized = False
        
        log_info("HA Extension cleanup complete")
        return create_success_response("Extension cleanup complete", {})
        
    except Exception as e:
        log_error(f"HA Extension cleanup failed: {str(e)}")
        return create_error_response("Cleanup failed", {"error": str(e)})


def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv("HOME_ASSISTANT_ENABLED", "false").lower() == "true"


def _get_ha_config() -> Dict[str, Any]:
    """Get Home Assistant configuration."""
    global _ha_config_cache
    
    if _ha_config_cache:
        return _ha_config_cache
    
    cached = cache_get("ha_config")
    if cached:
        return cached
    
    config = {
        "base_url": os.getenv("HOME_ASSISTANT_URL", ""),
        "access_token": os.getenv("HOME_ASSISTANT_TOKEN", ""),
        "timeout": int(os.getenv("HOME_ASSISTANT_TIMEOUT", "30")),
        "verify_ssl": os.getenv("HOME_ASSISTANT_VERIFY_SSL", "true").lower() == "true"
    }
    
    cache_set("ha_config", config, ttl=3600)
    return config


def call_ha_service(
    domain: str,
    service: str,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call Home Assistant service."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Calling HA service {domain}.{service} on {entity_id} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config()
        
        url = f"{config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        payload = {}
        if entity_id:
            payload["entity_id"] = entity_id
        if service_data:
            payload.update(service_data)
        
        result = make_post_request(
            url=url,
            headers=headers,
            json_data=payload,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            record_metric("ha_service_success", 1.0)
            return create_success_response("Service call successful", {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "correlation_id": correlation_id
            })
        else:
            record_metric("ha_service_failure", 1.0)
            return create_error_response("Service call failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Call HA service exception: {str(e)}")
        return create_error_response("Call HA service exception", {"error": str(e)})


def get_ha_state(entity_id: str) -> Dict[str, Any]:
    """Get Home Assistant entity state."""
    try:
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {})
        
        config = _get_ha_config()
        
        cache_key = f"ha_state_{entity_id}"
        cached = cache_get(cache_key)
        if cached:
            return create_success_response("State retrieved from cache", {"state": cached})
        
        url = f"{config['base_url']}/api/states/{entity_id}"
        headers = {"Authorization": f"Bearer {config['access_token']}"}
        
        result = make_get_request(url=url, headers=headers, timeout=config.get('timeout', 30))
        
        if result.get("success", False):
            state_data = result.get("data", {})
            cache_set(cache_key, state_data, ttl=60)
            return create_success_response("State retrieved", {"state": state_data})
        else:
            return create_error_response("Failed to get state", {"result": result})
        
    except Exception as e:
        log_error(f"Get HA state exception: {str(e)}")
        return create_error_response("Get HA state exception", {"error": str(e)})


def trigger_ha_automation(automation_id: str, skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger Home Assistant automation."""
    try:
        from home_assistant_automation import trigger_automation
        return trigger_automation(automation_id, _get_ha_config(), skip_condition)
    except Exception as e:
        log_error(f"Trigger automation exception: {str(e)}")
        return create_error_response("Trigger automation exception", {"error": str(e)})


def execute_ha_script(script_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute Home Assistant script."""
    try:
        from home_assistant_scripts import execute_script
        return execute_script(script_id, _get_ha_config(), variables)
    except Exception as e:
        log_error(f"Execute script exception: {str(e)}")
        return create_error_response("Execute script exception", {"error": str(e)})


def set_ha_input_helper(helper_id: str, value: Any) -> Dict[str, Any]:
    """Set Home Assistant input helper value."""
    try:
        from home_assistant_input_helpers import set_input_helper
        return set_input_helper(helper_id, value, _get_ha_config())
    except Exception as e:
        log_error(f"Set input helper exception: {str(e)}")
        return create_error_response("Set input helper exception", {"error": str(e)})


def send_ha_announcement(message: str, media_player_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Send TTS announcement to Home Assistant media players."""
    try:
        from home_assistant_notifications import send_tts_announcement
        return send_tts_announcement(message, _get_ha_config(), media_player_ids)
    except Exception as e:
        log_error(f"Send announcement exception: {str(e)}")
        return create_error_response("Send announcement exception", {"error": str(e)})


def control_ha_area(area_name: str, action: str, domain_filter: Optional[str] = None) -> Dict[str, Any]:
    """Control all devices in a Home Assistant area."""
    try:
        from home_assistant_areas import control_area_devices
        return control_area_devices(area_name, action, _get_ha_config(), domain_filter)
    except Exception as e:
        log_error(f"Control area exception: {str(e)}")
        return create_error_response("Control area exception", {"error": str(e)})


def start_ha_timer(timer_id: str, duration: str) -> Dict[str, Any]:
    """Start Home Assistant timer."""
    try:
        from home_assistant_timers import start_timer
        return start_timer(timer_id, duration, _get_ha_config())
    except Exception as e:
        log_error(f"Start timer exception: {str(e)}")
        return create_error_response("Start timer exception", {"error": str(e)})


def cancel_ha_timer(timer_id: str) -> Dict[str, Any]:
    """Cancel Home Assistant timer."""
    try:
        from home_assistant_timers import cancel_timer
        return cancel_timer(timer_id, _get_ha_config())
    except Exception as e:
        log_error(f"Cancel timer exception: {str(e)}")
        return create_error_response("Cancel timer exception", {"error": str(e)})


__all__ = [
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'is_ha_extension_enabled',
    'call_ha_service',
    'get_ha_state',
    'trigger_ha_automation',
    'execute_ha_script',
    'set_ha_input_helper',
    'send_ha_announcement',
    'control_ha_area',
    'start_ha_timer',
    'cancel_ha_timer',
]
