"""
homeassistant_extension.py - Home Assistant Integration Extension
Version: 2025.09.30.06
Daily Revision: Performance Optimization Phase 1

Revolutionary Gateway + Performance Optimization
- Uses ha_common for shared functionality
- Lazy loading for all feature modules
- 11-14MB memory reduction target
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error, log_warning,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric,
    cache_get, cache_set, cache_clear
)

from ha_common import get_ha_config, validate_ha_config


_ha_extension_initialized = False


def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension."""
    global _ha_extension_initialized
    
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Initializing HA Extension [{correlation_id}]")
        
        if _ha_extension_initialized:
            return create_success_response("Already initialized", {"initialized": True})
        
        if not is_ha_extension_enabled():
            log_warning("HA Extension is disabled")
            return create_error_response("Extension disabled", {"enabled": False})
        
        config = get_ha_config()
        if not validate_ha_config(config):
            return create_error_response("Invalid configuration", {})
        
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
    global _ha_extension_initialized
    
    try:
        cache_clear()
        _ha_extension_initialized = False
        
        log_info("HA Extension cleanup complete")
        return create_success_response("Extension cleanup complete", {})
        
    except Exception as e:
        log_error(f"HA Extension cleanup failed: {str(e)}")
        return create_error_response("Cleanup failed", {"error": str(e)})


def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    import os
    return os.getenv("HOME_ASSISTANT_ENABLED", "false").lower() == "true"


def call_ha_service(
    domain: str,
    service: str,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call Home Assistant service."""
    try:
        from ha_common import call_ha_service as ha_call_service
        return ha_call_service(domain, service, get_ha_config(), entity_id, service_data)
    except Exception as e:
        log_error(f"Call HA service exception: {str(e)}")
        return create_error_response("Call HA service exception", {"error": str(e)})


def get_ha_state(entity_id: str) -> Dict[str, Any]:
    """Get Home Assistant entity state."""
    try:
        from ha_common import get_entity_state
        return get_entity_state(entity_id, get_ha_config())
    except Exception as e:
        log_error(f"Get HA state exception: {str(e)}")
        return create_error_response("Get HA state exception", {"error": str(e)})


def trigger_ha_automation(automation_id: str, skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger Home Assistant automation with lazy loading."""
    try:
        from home_assistant_automation import trigger_automation
        return trigger_automation(automation_id, get_ha_config(), skip_condition)
    except Exception as e:
        log_error(f"Trigger automation exception: {str(e)}")
        return create_error_response("Trigger automation exception", {"error": str(e)})


def execute_ha_script(script_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute Home Assistant script with lazy loading."""
    try:
        from home_assistant_scripts import execute_script
        return execute_script(script_id, get_ha_config(), variables)
    except Exception as e:
        log_error(f"Execute script exception: {str(e)}")
        return create_error_response("Execute script exception", {"error": str(e)})


def set_ha_input_helper(helper_id: str, value: Any) -> Dict[str, Any]:
    """Set Home Assistant input helper value with lazy loading."""
    try:
        from home_assistant_input_helpers import set_input_helper
        return set_input_helper(helper_id, value, get_ha_config())
    except Exception as e:
        log_error(f"Set input helper exception: {str(e)}")
        return create_error_response("Set input helper exception", {"error": str(e)})


def send_ha_announcement(message: str, media_player_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Send TTS announcement to Home Assistant media players with lazy loading."""
    try:
        from home_assistant_notifications import send_tts_announcement
        return send_tts_announcement(message, get_ha_config(), media_player_ids)
    except Exception as e:
        log_error(f"Send announcement exception: {str(e)}")
        return create_error_response("Send announcement exception", {"error": str(e)})


def control_ha_area(area_name: str, action: str, domain: Optional[str] = None) -> Dict[str, Any]:
    """Control devices in Home Assistant area with lazy loading."""
    try:
        from home_assistant_areas import control_area
        return control_area(area_name, action, get_ha_config(), domain)
    except Exception as e:
        log_error(f"Control area exception: {str(e)}")
        return create_error_response("Control area exception", {"error": str(e)})


def start_ha_timer(timer_name: str, duration: str) -> Dict[str, Any]:
    """Start Home Assistant timer with lazy loading."""
    try:
        from home_assistant_timers import start_timer
        return start_timer(timer_name, duration, get_ha_config())
    except Exception as e:
        log_error(f"Start timer exception: {str(e)}")
        return create_error_response("Start timer exception", {"error": str(e)})


def cancel_ha_timer(timer_id: str) -> Dict[str, Any]:
    """Cancel Home Assistant timer with lazy loading."""
    try:
        from home_assistant_timers import cancel_timer
        return cancel_timer(timer_id, get_ha_config())
    except Exception as e:
        log_error(f"Cancel timer exception: {str(e)}")
        return create_error_response("Cancel timer exception", {"error": str(e)})


def process_alexa_ha_request(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive with lazy loading."""
    try:
        from homeassistant_alexa import process_alexa_directive
        return process_alexa_directive(directive, get_ha_config())
    except Exception as e:
        log_error(f"Process Alexa request exception: {str(e)}")
        return create_error_response("Process Alexa request exception", {"error": str(e)})


def get_exposed_entities() -> Dict[str, Any]:
    """Get exposed Home Assistant entities with lazy loading."""
    try:
        from homeassistant_alexa import get_exposed_entities as get_entities
        return get_entities(get_ha_config())
    except Exception as e:
        log_error(f"Get exposed entities exception: {str(e)}")
        return create_error_response("Get exposed entities exception", {"error": str(e)})


__all__ = [
    "initialize_ha_extension",
    "cleanup_ha_extension",
    "is_ha_extension_enabled",
    "call_ha_service",
    "get_ha_state",
    "trigger_ha_automation",
    "execute_ha_script",
    "set_ha_input_helper",
    "send_ha_announcement",
    "control_ha_area",
    "start_ha_timer",
    "cancel_ha_timer",
    "process_alexa_ha_request",
    "get_exposed_entities"
]
