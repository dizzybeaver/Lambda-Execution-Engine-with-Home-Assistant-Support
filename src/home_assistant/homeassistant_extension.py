"""
homeassistant_extension.py - Home Assistant Integration Extension
Version: 2025.09.30.04
Daily Revision: 001

Complete Home Assistant integration with enhanced features
UPDATED: Added automation, script, input helper, notification, area, and timer support

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Revolutionary Gateway compliant (SUGA + LIGS)
- Lazy loading compatible
- 100% Free Tier AWS compliant
- Self-contained extension

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error, log_warning, log_debug,
    make_get_request, make_post_request,
    get_config_value, set_config_value,
    create_success_response, create_error_response,
    generate_correlation_id,
    validate_url, sanitize_input,
    record_metric, increment_counter,
    cache_get, cache_set,
    record_error
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
            log_debug("HA Extension already initialized")
            return create_success_response("Already initialized", {"initialized": True})
        
        if not is_ha_extension_enabled():
            log_warning("HA Extension is disabled")
            return create_error_response("Extension disabled", {"enabled": False})
        
        config = _get_ha_config_gateway()
        if not config:
            return create_error_response("Failed to load configuration", {})
        
        _ha_config_cache = config
        _ha_extension_initialized = True
        
        log_info(f"HA Extension initialized successfully [{correlation_id}]")
        record_metric("ha_extension_initialized", 1.0)
        
        return create_success_response("HA Extension initialized", {
            "base_url": config.get("base_url"),
            "timeout": config.get("timeout"),
            "verify_ssl": config.get("verify_ssl"),
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"HA Extension initialization failed: {str(e)}")
        record_error(e, "HA_EXTENSION_INIT")
        return create_error_response("Initialization failed", {"error": str(e)})


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    global _ha_extension_initialized, _ha_config_cache
    
    try:
        log_info("Cleaning up HA Extension")
        
        _ha_extension_initialized = False
        _ha_config_cache = None
        
        cache_keys = [
            "ha_extension_config",
            "ha_extension_initialized",
            "ha_exposed_entities",
            "ha_automation_list",
            "ha_script_list",
            "ha_input_helper_list",
            "ha_area_list",
            "ha_timer_list",
            "ha_media_players"
        ]
        
        for key in cache_keys:
            cache_set(key, None, ttl=0)
        
        log_info("HA Extension cleanup completed")
        return create_success_response("Cleanup completed", {})
        
    except Exception as e:
        log_error(f"HA Extension cleanup failed: {str(e)}")
        return create_error_response("Cleanup failed", {"error": str(e)})


def is_ha_extension_enabled() -> bool:
    """Check if HA extension is enabled."""
    enabled = get_config_value("HOME_ASSISTANT_ENABLED", "false").lower() == "true"
    return enabled


def _get_ha_config_gateway() -> Optional[Dict[str, Any]]:
    """Get Home Assistant configuration using gateway."""
    try:
        cache_key = "ha_extension_config"
        cached = cache_get(cache_key)
        if cached:
            log_debug("Returning cached HA config")
            return cached
        
        base_url = get_config_value("HOME_ASSISTANT_URL", "")
        access_token = get_config_value("HOME_ASSISTANT_TOKEN", "")
        timeout = int(get_config_value("HOME_ASSISTANT_TIMEOUT", "30"))
        verify_ssl = get_config_value("HOME_ASSISTANT_VERIFY_SSL", "true").lower() == "true"
        
        if not base_url or not access_token:
            log_error("HA configuration incomplete")
            return None
        
        if not validate_url(base_url):
            log_error(f"Invalid HA URL: {base_url}")
            return None
        
        config = {
            "base_url": base_url.rstrip("/"),
            "access_token": access_token,
            "timeout": timeout,
            "verify_ssl": verify_ssl
        }
        
        cache_set(cache_key, config, ttl=3600)
        
        log_debug("HA config loaded successfully")
        return config
        
    except Exception as e:
        log_error(f"Failed to get HA config: {str(e)}")
        return None


def call_ha_service(domain: str, service: str, entity_id: str, 
                   service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call Home Assistant service using gateway."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Calling HA service {domain}.{service} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "entity_id": entity_id
        }
        if service_data:
            payload.update(service_data)
        
        result = make_post_request(
            url=url,
            headers=headers,
            json_data=payload,
            timeout=config.get('timeout', 30)
        )
        
        record_metric("ha_service_call", 1.0, {
            "domain": domain,
            "service": service,
            "success": result.get("success", False),
            "correlation_id": correlation_id
        })
        
        if result.get("success", False):
            log_info(f"HA service call successful [{correlation_id}]")
            return create_success_response("HA service call successful", {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "result": result,
                "correlation_id": correlation_id
            })
        else:
            log_error(f"HA service call failed [{correlation_id}]")
            return create_error_response("HA service call failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"HA service call exception: {str(e)}")
        return create_error_response("HA service call exception", {"error": str(e)})


def get_ha_state(entity_id: str) -> Dict[str, Any]:
    """Get Home Assistant entity state using gateway."""
    try:
        correlation_id = generate_correlation_id()
        log_debug(f"Getting HA state for {entity_id} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}"
        }
        
        result = make_get_request(
            url=url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            return create_success_response("State retrieved", {
                "entity_id": entity_id,
                "state": result.get("data", {}),
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("Failed to get state", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Get HA state exception: {str(e)}")
        return create_error_response("Get state exception", {"error": str(e)})


def get_exposed_entities() -> Dict[str, Any]:
    """Get entities exposed to voice assistants."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Getting exposed entities [{correlation_id}]")
        
        cache_key = "ha_exposed_entities"
        cached = cache_get(cache_key)
        if cached:
            log_debug("Returning cached exposed entities")
            return cached
        
        config = _get_ha_config_gateway()
        url = f"{config['base_url']}/api/config/entity_registry/list"
        headers = {
            "Authorization": f"Bearer {config['access_token']}"
        }
        
        result = make_get_request(
            url=url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if not result.get("success", False):
            log_warning("Entity registry unavailable, returning all entities")
            return _get_all_entities_fallback(config)
        
        registry_data = result.get("data", [])
        
        exposed_entities = []
        for entry in registry_data:
            options = entry.get("options", {})
            conversation = options.get("conversation", {})
            cloud = options.get("cloud", {})
            alexa = cloud.get("alexa", {})
            
            should_expose = (
                conversation.get("should_expose", False) or 
                alexa.get("should_expose", False)
            )
            
            if should_expose:
                exposed_entities.append(entry.get("entity_id"))
        
        response = create_success_response(
            "Exposed entities retrieved",
            {
                "entity_ids": exposed_entities,
                "count": len(exposed_entities),
                "correlation_id": correlation_id
            }
        )
        
        cache_set(cache_key, response, ttl=300)
        
        log_info(f"Found {len(exposed_entities)} exposed entities [{correlation_id}]")
        return response
        
    except Exception as e:
        log_error(f"Get exposed entities exception: {str(e)}")
        config = _get_ha_config_gateway()
        return _get_all_entities_fallback(config)


def _get_all_entities_fallback(config: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback to return all entities if registry unavailable."""
    try:
        log_info("Using fallback: returning all entities")
        
        url = f"{config['base_url']}/api/states"
        headers = {
            "Authorization": f"Bearer {config['access_token']}"
        }
        
        result = make_get_request(
            url=url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            states = result.get("data", [])
            entity_ids = [state.get("entity_id") for state in states]
            
            return create_success_response(
                "All entities retrieved (fallback)",
                {
                    "entity_ids": entity_ids,
                    "count": len(entity_ids),
                    "fallback": True
                }
            )
        else:
            return create_error_response("Fallback failed", {"result": result})
            
    except Exception as e:
        log_error(f"Fallback exception: {str(e)}")
        return create_error_response("Fallback exception", {"error": str(e)})


def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home request."""
    try:
        from homeassistant_alexa import process_alexa_directive
        
        correlation_id = generate_correlation_id()
        log_info(f"Processing Alexa HA request [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            log_error("HA extension disabled")
            return _create_alexa_error_response("Home Assistant integration is not enabled")
        
        result = process_alexa_directive(event)
        return result
        
    except Exception as e:
        log_error(f"Alexa HA request processing failed: {str(e)}")
        return _create_alexa_error_response(str(e))


def _create_alexa_error_response(error_message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": generate_correlation_id(),
                "payloadVersion": "3"
            },
            "payload": {
                "type": "INTERNAL_ERROR",
                "message": error_message
            }
        }
    }


def trigger_ha_automation(automation_id: str, skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger Home Assistant automation."""
    try:
        from home_assistant_automation import trigger_automation
        
        config = _get_ha_config_gateway()
        return trigger_automation(automation_id, config, skip_condition)
        
    except Exception as e:
        log_error(f"Trigger automation exception: {str(e)}")
        return create_error_response("Trigger automation exception", {"error": str(e)})


def execute_ha_script(script_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute Home Assistant script."""
    try:
        from home_assistant_scripts import execute_script
        
        config = _get_ha_config_gateway()
        return execute_script(script_id, config, variables)
        
    except Exception as e:
        log_error(f"Execute script exception: {str(e)}")
        return create_error_response("Execute script exception", {"error": str(e)})


def set_ha_input_helper(helper_id: str, value: Any) -> Dict[str, Any]:
    """Set Home Assistant input helper value."""
    try:
        from home_assistant_input_helpers import set_input_helper
        
        config = _get_ha_config_gateway()
        return set_input_helper(helper_id, value, config)
        
    except Exception as e:
        log_error(f"Set input helper exception: {str(e)}")
        return create_error_response("Set input helper exception", {"error": str(e)})


def send_ha_announcement(message: str, media_player_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Send TTS announcement to Home Assistant media players."""
    try:
        from home_assistant_notifications import send_tts_announcement
        
        config = _get_ha_config_gateway()
        return send_tts_announcement(message, config, media_player_ids)
        
    except Exception as e:
        log_error(f"Send announcement exception: {str(e)}")
        return create_error_response("Send announcement exception", {"error": str(e)})


def control_ha_area(area_name: str, action: str, domain_filter: Optional[str] = None) -> Dict[str, Any]:
    """Control all devices in a Home Assistant area."""
    try:
        from home_assistant_areas import control_area_devices
        
        config = _get_ha_config_gateway()
        return control_area_devices(area_name, action, config, domain_filter)
        
    except Exception as e:
        log_error(f"Control area exception: {str(e)}")
        return create_error_response("Control area exception", {"error": str(e)})


def start_ha_timer(timer_id: str, duration: str) -> Dict[str, Any]:
    """Start Home Assistant timer."""
    try:
        from home_assistant_timers import start_timer
        
        config = _get_ha_config_gateway()
        return start_timer(timer_id, duration, config)
        
    except Exception as e:
        log_error(f"Start timer exception: {str(e)}")
        return create_error_response("Start timer exception", {"error": str(e)})


def cancel_ha_timer(timer_id: str) -> Dict[str, Any]:
    """Cancel Home Assistant timer."""
    try:
        from home_assistant_timers import cancel_timer
        
        config = _get_ha_config_gateway()
        return cancel_timer(timer_id, config)
        
    except Exception as e:
        log_error(f"Cancel timer exception: {str(e)}")
        return create_error_response("Cancel timer exception", {"error": str(e)})


__all__ = [
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'is_ha_extension_enabled',
    'call_ha_service',
    'get_ha_state',
    'get_exposed_entities',
    'process_alexa_ha_request',
    'trigger_ha_automation',
    'execute_ha_script',
    'set_ha_input_helper',
    'send_ha_announcement',
    'control_ha_area',
    'start_ha_timer',
    'cancel_ha_timer',
]

#EOF
