"""
homeassistant_extension.py - Home Assistant Extension with Exposed Entity Filtering
Version: 2025.09.30.03
Daily Revision: 003

Revolutionary Gateway Optimization with Alexa Exposed Entity Integration
- Migrated to use gateway.py universal routing
- All imports consolidated from gateway module
- Alexa conversation support integrated
- Exposed entities filtering via Home Assistant entity registry
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


class InitializationType(str, Enum):
    SYSTEM_STARTUP = "system_startup"
    EXTENSION_LOAD = "extension_load"
    SERVICE_INIT = "service_init"


class InitializationStage(str, Enum):
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    HEALTH_CHECK = "health_check"


class CacheType(str, Enum):
    MEMORY = "memory"
    PERSISTENT = "persistent"


HA_INITIALIZATION_CACHE_KEY = "ha_extension_initialized"
HA_CONFIG_CACHE_KEY = "ha_extension_config"
HA_MANAGER_CACHE_KEY = "ha_manager_data"
HA_EXPOSED_ENTITIES_CACHE_KEY = "ha_exposed_entities"
HA_EXPOSED_ENTITIES_CACHE_TTL = 300


def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension with gateway architecture."""
    try:
        correlation_id = generate_correlation_id()
        
        cached_init = cache_get(HA_INITIALIZATION_CACHE_KEY)
        if cached_init:
            log_debug(f"HA extension already initialized [{correlation_id}]")
            return create_success_response("HA extension already initialized", {
                "cached": True,
                "correlation_id": correlation_id
            })
        
        log_info(f"Initializing HA extension [{correlation_id}]")
        
        record_initialization_stage(
            InitializationType.EXTENSION_LOAD.value,
            InitializationStage.CONFIGURATION.value,
            "started"
        )
        
        config = _get_ha_config_gateway()
        
        record_initialization_stage(
            InitializationType.EXTENSION_LOAD.value,
            InitializationStage.VALIDATION.value,
            "completed"
        )
        
        cache_set(HA_INITIALIZATION_CACHE_KEY, True, ttl=3600)
        cache_set(HA_CONFIG_CACHE_KEY, config, ttl=3600)
        
        record_metric("ha_extension_init", 1.0, {
            "status": "success",
            "correlation_id": correlation_id
        })
        
        log_info(f"HA extension initialized successfully [{correlation_id}]")
        return create_success_response("HA extension initialized", {
            "config": config,
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"HA extension initialization error: {str(e)}")
        return create_error_response("HA initialization error", {"error": str(e)})


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Cleaning up HA extension [{correlation_id}]")
        
        cache_delete(HA_INITIALIZATION_CACHE_KEY)
        cache_delete(HA_CONFIG_CACHE_KEY)
        cache_delete(HA_MANAGER_CACHE_KEY)
        cache_delete(HA_EXPOSED_ENTITIES_CACHE_KEY)
        
        record_metric("ha_extension_cleanup", 1.0, {"correlation_id": correlation_id})
        
        log_info(f"HA extension cleanup complete [{correlation_id}]")
        return create_success_response("HA extension cleanup complete", {
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"HA extension cleanup error: {str(e)}")
        return create_error_response("HA cleanup error", {"error": str(e)})


def _get_ha_config_gateway() -> Dict[str, Any]:
    """Get Home Assistant configuration from environment using gateway."""
    cached_config = cache_get(HA_CONFIG_CACHE_KEY)
    if cached_config:
        return cached_config
    
    config = {
        "base_url": os.getenv("HOME_ASSISTANT_URL", ""),
        "access_token": os.getenv("HOME_ASSISTANT_TOKEN", ""),
        "timeout": int(os.getenv("HOME_ASSISTANT_TIMEOUT", "30")),
        "verify_ssl": os.getenv("HOME_ASSISTANT_VERIFY_SSL", "true").lower() == "true"
    }
    
    cache_set(HA_CONFIG_CACHE_KEY, config, ttl=3600)
    return config


def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'


def call_ha_service(domain: str, service: str, entity_id: Optional[str] = None, 
                    service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call Home Assistant service using gateway."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Calling HA service {domain}.{service} on {entity_id} [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {"correlation_id": correlation_id})
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        payload = {"entity_id": entity_id}
        if service_data:
            payload.update(service_data)
        
        result = make_post_request(
            url=url,
            headers=headers,
            json_data=payload,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            record_metric("ha_service_success", 1.0, {
                "domain": domain,
                "service": service,
                "correlation_id": correlation_id
            })
            return create_success_response("Service call successful", {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "correlation_id": correlation_id
            })
        else:
            record_metric("ha_service_failure", 1.0, {
                "domain": domain,
                "service": service
            })
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
        
        if result.get("success", False):
            return create_success_response("State retrieved", {
                "entity_id": entity_id,
                "state": result.get("response", {}),
                "correlation_id": correlation_id
            })
        else:
            return create_error_response("State retrieval failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Get HA state exception: {str(e)}")
        return create_error_response("Get HA state exception", {"error": str(e)})


def get_exposed_entities() -> Dict[str, Any]:
    """Get list of entities exposed to voice assistants via entity registry."""
    try:
        correlation_id = generate_correlation_id()
        log_debug(f"Fetching exposed entities from HA [{correlation_id}]")
        
        cached_entities = cache_get(HA_EXPOSED_ENTITIES_CACHE_KEY)
        if cached_entities:
            log_debug(f"Using cached exposed entities [{correlation_id}]")
            return create_success_response("Cached exposed entities", {
                "exposed_entities": cached_entities,
                "cached": True,
                "correlation_id": correlation_id
            })
        
        config = _get_ha_config_gateway()
        
        url = f"{config['base_url']}/api/config/entity_registry/list"
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
            registry_entries = result.get("response", [])
            exposed_entities = set()
            
            for entry in registry_entries:
                entity_id = entry.get("entity_id", "")
                options = entry.get("options", {})
                
                conversation_options = options.get("conversation", {})
                cloud_options = options.get("cloud", {}).get("alexa", {})
                
                should_expose_conversation = conversation_options.get("should_expose", False)
                should_expose_cloud = cloud_options.get("should_expose", False)
                
                if should_expose_conversation or should_expose_cloud:
                    exposed_entities.add(entity_id)
            
            exposed_list = list(exposed_entities)
            cache_set(HA_EXPOSED_ENTITIES_CACHE_KEY, exposed_list, ttl=HA_EXPOSED_ENTITIES_CACHE_TTL)
            
            log_info(f"Found {len(exposed_list)} exposed entities [{correlation_id}]")
            return create_success_response("Exposed entities retrieved", {
                "exposed_entities": exposed_list,
                "count": len(exposed_list),
                "cached": False,
                "correlation_id": correlation_id
            })
        else:
            log_warning(f"Failed to fetch entity registry, allowing all entities [{correlation_id}]")
            return create_success_response("Entity registry unavailable, allowing all", {
                "exposed_entities": None,
                "fallback": True,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Get exposed entities exception: {str(e)}")
        return create_success_response("Exception getting exposed entities, allowing all", {
            "exposed_entities": None,
            "error": str(e),
            "fallback": True
        })


def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home request for Home Assistant."""
    try:
        correlation_id = generate_correlation_id()
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"Processing Alexa HA request: {namespace}.{name} [{correlation_id}]")
        
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
    """Handle Alexa discovery request with exposed entity filtering."""
    try:
        log_info(f"Alexa discovery request [{correlation_id}]")
        
        config = _get_ha_config_gateway()
        
        exposed_result = get_exposed_entities()
        exposed_entities = exposed_result.get("data", {}).get("exposed_entities")
        
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
            endpoints = _convert_states_to_endpoints(states, exposed_entities, correlation_id)
            
            record_metric("alexa_discovery", 1.0, {
                "total_states": len(states),
                "exposed_count": len(endpoints),
                "correlation_id": correlation_id
            })
            
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


def _convert_states_to_endpoints(states: List[Dict[str, Any]], 
                                 exposed_entities: Optional[List[str]], 
                                 correlation_id: str) -> List[Dict[str, Any]]:
    """Convert Home Assistant states to Alexa endpoints with exposure filtering."""
    endpoints = []
    filtered_count = 0
    
    for state in states:
        entity_id = state.get("entity_id", "")
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        
        if exposed_entities is not None and entity_id not in exposed_entities:
            filtered_count += 1
            continue
        
        if domain in ["light", "switch", "climate", "cover", "lock", "media_player"]:
            endpoint = {
                "endpointId": entity_id,
                "friendlyName": state.get("attributes", {}).get("friendly_name", entity_id),
                "description": f"Home Assistant {domain}",
                "manufacturerName": "Home Assistant",
                "displayCategories": [_get_display_category(domain)],
                "capabilities": _get_capabilities(domain)
            }
            endpoints.append(endpoint)
    
    if filtered_count > 0:
        log_info(f"Filtered {filtered_count} unexposed entities [{correlation_id}]")
    
    return endpoints


def _get_display_category(domain: str) -> str:
    """Get Alexa display category for domain."""
    category_map = {
        "light": "LIGHT",
        "switch": "SWITCH",
        "climate": "THERMOSTAT",
        "cover": "DOOR",
        "lock": "SMARTLOCK",
        "media_player": "TV"
    }
    return category_map.get(domain, "OTHER")


def _get_capabilities(domain: str) -> List[Dict[str, Any]]:
    """Get Alexa capabilities for domain."""
    base_capability = {
        "type": "AlexaInterface",
        "interface": "Alexa.PowerController",
        "version": "3",
        "properties": {
            "supported": [{"name": "powerState"}],
            "proactivelyReported": False,
            "retrievable": True
        }
    }
    
    capabilities = [base_capability]
    
    if domain == "light":
        brightness_capability = {
            "type": "AlexaInterface",
            "interface": "Alexa.BrightnessController",
            "version": "3",
            "properties": {
                "supported": [{"name": "brightness"}],
                "proactivelyReported": False,
                "retrievable": True
            }
        }
        capabilities.append(brightness_capability)
    
    if domain == "climate":
        thermostat_capability = {
            "type": "AlexaInterface",
            "interface": "Alexa.ThermostatController",
            "version": "3",
            "properties": {
                "supported": [
                    {"name": "targetSetpoint"},
                    {"name": "thermostatMode"}
                ],
                "proactivelyReported": False,
                "retrievable": True
            }
        }
        capabilities.append(thermostat_capability)
    
    return capabilities


def _handle_alexa_power_control_gateway(directive: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa power control."""
    try:
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        
        header = directive.get('header', {})
        name = header.get('name', '')
        
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        
        if name == "TurnOn":
            service = "turn_on"
        elif name == "TurnOff":
            service = "turn_off"
        else:
            return create_error_response("Invalid power control directive", {
                "name": name,
                "correlation_id": correlation_id
            })
        
        result = call_ha_service(domain, service, entity_id)
        
        if result.get("success", False):
            record_metric("alexa_power_control", 1.0, {
                "action": name,
                "domain": domain,
                "correlation_id": correlation_id
            })
            
            return create_success_response("Power control successful", {
                "entity_id": entity_id,
                "action": name,
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
        
        header = directive.get('header', {})
        name = header.get('name', '')
        
        payload = directive.get('payload', {})
        brightness = payload.get('brightness', 0)
        
        domain = entity_id.split(".")[0] if "." in entity_id else ""
        
        service_data = {"brightness_pct": brightness}
        
        result = call_ha_service(domain, "turn_on", entity_id, service_data)
        
        if result.get("success", False):
            record_metric("alexa_brightness_control", 1.0, {
                "brightness": brightness,
                "correlation_id": correlation_id
            })
            
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


__all__ = [
    'HADomain',
    'InitializationType',
    'InitializationStage',
    'CacheType',
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'call_ha_service',
    'get_ha_state',
    'get_exposed_entities',
    'process_alexa_ha_request',
    'is_ha_extension_enabled'
]

#EOF
