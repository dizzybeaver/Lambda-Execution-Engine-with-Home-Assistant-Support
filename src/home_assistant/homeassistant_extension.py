"""
homeassistant_extension.py - Home Assistant Extension with Conversation Support
Version: 2025.09.30.01
Daily Revision: 001

Revolutionary Gateway Optimization with Alexa Conversation Integration
- Migrated to use gateway.py universal routing
- All imports consolidated from gateway module
- Alexa conversation support integrated
- Lazy loading compatible
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
import os
from typing import Dict, Any, Optional, List
from enum import Enum

from gateway import (
    cache_get, cache_set, cache_delete, cache_clear,
    log_info, log_error, log_warning, log_debug,
    validate_request, validate_token, encrypt_data, decrypt_data,
    record_metric, increment_counter,
    make_request, make_get_request, make_post_request,
    create_success_response, create_error_response, parse_json_safely, generate_correlation_id,
    execute_initialization_operation, record_initialization_stage,
    GatewayInterface, execute_operation
)


class HADomain(str, Enum):
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    COVER = "cover"
    LOCK = "lock"
    MEDIA_PLAYER = "media_player"


HA_INITIALIZATION_CACHE_KEY = "ha_extension_initialized"
HA_CONFIG_CACHE_KEY = "ha_extension_config"


def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension with gateway architecture."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Initializing HA extension [{correlation_id}]")
        
        cached_init = cache_get(HA_INITIALIZATION_CACHE_KEY)
        if cached_init:
            log_debug("HA extension already initialized")
            return create_success_response("HA extension already initialized", cached_init)
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension is disabled", {
                "enabled": False,
                "correlation_id": correlation_id
            })
        
        config = _get_ha_config_gateway()
        
        init_data = {
            "initialized": True,
            "timestamp": time.time(),
            "config_loaded": True,
            "correlation_id": correlation_id
        }
        
        cache_set(HA_INITIALIZATION_CACHE_KEY, init_data, ttl=3600)
        
        record_metric("ha_extension_initialized", 1.0, {
            "correlation_id": correlation_id
        })
        
        log_info(f"HA extension initialized successfully [{correlation_id}]")
        return create_success_response("HA extension initialized", init_data)
        
    except Exception as e:
        log_error(f"HA initialization failed: {str(e)}")
        return create_error_response("HA initialization failed", {"error": str(e)})


def _get_ha_config_gateway() -> Dict[str, Any]:
    """Get Home Assistant configuration from Parameter Store via gateway."""
    try:
        cached_config = cache_get(HA_CONFIG_CACHE_KEY)
        if cached_config:
            return cached_config
        
        config = {
            "enabled": is_ha_extension_enabled(),
            "base_url": os.environ.get("HA_URL", "http://homeassistant.local:8123"),
            "access_token": os.environ.get("HA_TOKEN", ""),
            "timeout": int(os.environ.get("HA_TIMEOUT", "30")),
            "verify_ssl": os.environ.get("HA_VERIFY_SSL", "true").lower() == "true"
        }
        
        cache_set(HA_CONFIG_CACHE_KEY, config, ttl=300)
        return config
        
    except Exception as e:
        log_error(f"Failed to get HA config: {str(e)}")
        return {
            "enabled": False,
            "base_url": "",
            "access_token": "",
            "timeout": 30,
            "verify_ssl": True
        }


def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower() == "true"


def call_ha_service(domain: str, service: str, entity_id: str, 
                   service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call Home Assistant service using gateway."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Calling HA service {domain}.{service} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        payload = {
            "entity_id": entity_id
        }
        
        if service_data:
            payload.update(service_data)
        
        url = f"{config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
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
            return create_success_response("HA service call successful", {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("HA service call failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Call HA service exception: {str(e)}")
        return create_error_response("Call HA service exception", {"error": str(e)})


def get_ha_state(entity_id: str) -> Dict[str, Any]:
    """Get Home Assistant entity state."""
    try:
        correlation_id = generate_correlation_id()
        log_debug(f"Getting HA state for {entity_id} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        result = make_get_request(
            url=url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        record_metric("ha_state_get", 1.0, {
            "entity_id": entity_id,
            "success": result.get("success", False),
            "correlation_id": correlation_id
        })
        
        if result.get("success", False):
            state_data = result.get("response", {})
            return create_success_response("HA state retrieved", {
                "entity_id": entity_id,
                "state": state_data.get("state"),
                "attributes": state_data.get("attributes", {}),
                "last_changed": state_data.get("last_changed"),
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("HA state retrieval failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Get HA state exception: {str(e)}")
        return create_error_response("Get HA state exception", {"error": str(e)})


def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa request for Home Assistant."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Processing Alexa HA request [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        validation = validate_request(event)
        if not validation.get("success", True):
            return create_error_response("Alexa event validation failed", {
                "validation": validation,
                "correlation_id": correlation_id
            })
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_debug(f"Alexa directive: {namespace}.{name} [{correlation_id}]")
        
        if namespace == "Alexa.Discovery":
            return _handle_alexa_discovery_gateway(directive, correlation_id)
        elif namespace == "Alexa.PowerController":
            return _handle_alexa_power_control_gateway(directive, correlation_id)
        elif namespace == "Alexa.BrightnessController":
            return _handle_alexa_brightness_control_gateway(directive, correlation_id)
        else:
            log_warning(f"Unsupported Alexa namespace: {namespace}")
            return create_error_response("Unsupported namespace", {
                "namespace": namespace,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Process Alexa HA request exception: {str(e)}")
        return create_error_response("Process Alexa HA request exception", {"error": str(e)})


def _handle_alexa_discovery_gateway(directive: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa discovery request."""
    try:
        log_info(f"Alexa discovery request [{correlation_id}]")
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/states"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        result = make_get_request(
            url=url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            states = result.get("response", [])
            endpoints = _convert_states_to_endpoints(states)
            
            return create_success_response("Discovery successful", {
                "endpoints": endpoints,
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("Discovery failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Alexa discovery exception: {str(e)}")
        return create_error_response("Alexa discovery exception", {"error": str(e)})


def _convert_states_to_endpoints(states: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert Home Assistant states to Alexa endpoints."""
    endpoints = []
    
    for state in states:
        entity_id = state.get("entity_id", "")
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        
        if domain in ["light", "switch", "scene"]:
            endpoint = {
                "endpointId": entity_id,
                "friendlyName": state.get("attributes", {}).get("friendly_name", entity_id),
                "manufacturerName": "Home Assistant",
                "description": f"{domain.title()} controlled by Home Assistant"
            }
            endpoints.append(endpoint)
    
    return endpoints


def _handle_alexa_power_control_gateway(directive: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa power control."""
    try:
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        
        header = directive.get('header', {})
        name = header.get('name', '')
        
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        service = "turn_on" if name == "TurnOn" else "turn_off"
        
        log_info(f"Alexa power control: {entity_id} -> {service} [{correlation_id}]")
        
        result = call_ha_service(domain, service, entity_id)
        
        if result.get("success", False):
            return create_success_response("Power control successful", {
                "entity_id": entity_id,
                "service": service,
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("Power control failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Alexa power control exception: {str(e)}")
        return create_error_response("Alexa power control exception", {"error": str(e)})


def _handle_alexa_brightness_control_gateway(directive: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa brightness control."""
    try:
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        
        payload = directive.get('payload', {})
        brightness = payload.get('brightness', 100)
        
        log_info(f"Alexa brightness control: {entity_id} -> {brightness}% [{correlation_id}]")
        
        result = call_ha_service("light", "turn_on", entity_id, {"brightness_pct": brightness})
        
        if result.get("success", False):
            return create_success_response("Brightness control successful", {
                "entity_id": entity_id,
                "brightness": brightness,
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("Brightness control failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Alexa brightness control exception: {str(e)}")
        return create_error_response("Alexa brightness control exception", {"error": str(e)})


def process_ha_conversation(user_text: str, 
                            conversation_id: Optional[str] = None,
                            language: str = "en") -> Dict[str, Any]:
    """
    Process conversation through Home Assistant API.
    
    Args:
        user_text: User's text input
        conversation_id: Optional conversation ID for context
        language: Language code
        
    Returns:
        Dict with conversation response
    """
    try:
        from home_assistant_conversation import process_alexa_conversation
        
        correlation_id = generate_correlation_id()
        log_info(f"Processing HA conversation [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        session_attributes = {}
        if conversation_id:
            session_attributes["conversationId"] = conversation_id
        
        result = process_alexa_conversation(
            user_text=user_text,
            ha_config=config,
            session_attributes=session_attributes
        )
        
        record_metric("ha_conversation_processed", 1.0, {
            "correlation_id": correlation_id,
            "language": language
        })
        
        return result
        
    except Exception as e:
        log_error(f"Process HA conversation exception: {str(e)}")
        return create_error_response("Conversation processing failed", {"error": str(e)})


def get_conversation_stats() -> Dict[str, Any]:
    """Get conversation processing statistics."""
    try:
        from home_assistant_conversation import get_conversation_stats
        return get_conversation_stats()
    except Exception as e:
        log_error(f"Failed to get conversation stats: {str(e)}")
        return {"error": str(e)}


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    try:
        cache_delete(HA_INITIALIZATION_CACHE_KEY)
        cache_delete(HA_CONFIG_CACHE_KEY)
        
        log_info("HA extension cleanup completed")
        return create_success_response("HA extension cleanup completed", {
            "timestamp": time.time()
        })
        
    except Exception as e:
        log_error(f"HA cleanup failed: {str(e)}")
        return create_error_response("HA cleanup failed", {"error": str(e)})


__all__ = [
    'HADomain',
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'call_ha_service',
    'get_ha_state',
    'process_alexa_ha_request',
    'process_ha_conversation',
    'get_conversation_stats',
    'is_ha_extension_enabled',
    '_get_ha_config_gateway'
]
