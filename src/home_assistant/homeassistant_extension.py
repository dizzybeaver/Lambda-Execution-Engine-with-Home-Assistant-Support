"""
homeassistant_extension.py - Phase 4: Extension Interfaces Implementation
Version: 2025.09.29.06
Daily Revision: Phase 4 Gateway Migration Complete

Revolutionary Gateway Optimization - Phase 4 Implementation
- Migrated to use gateway.py universal routing
- All imports consolidated from gateway module
- Lazy loading compatible
- 100% Free Tier AWS compliant

Home Assistant Integration for Lambda Execution Engine
Self-contained extension using gateway interfaces for all operations.
"""

import time
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

def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension with gateway architecture."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Starting HA extension initialization [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_success_response("HA extension disabled", {
                "enabled": False,
                "initialization_skipped": True,
                "correlation_id": correlation_id
            })
        
        init_result = execute_operation(
            GatewayInterface.INITIALIZATION,
            "execute_operation",
            init_type=InitializationType.EXTENSION_LOAD,
            component="home_assistant_extension",
            extension_type="home_assistant"
        )
        
        if not init_result.get("success", False):
            return create_error_response("HA extension initialization failed", {
                "init_result": init_result,
                "correlation_id": correlation_id
            })
        
        stage_result = execute_operation(
            GatewayInterface.INITIALIZATION,
            "record_stage",
            stage=InitializationStage.CONFIGURATION,
            component="ha_extension"
        )
        
        ha_manager_result = _initialize_ha_manager_gateway()
        
        ha_status = {
            "initialized": ha_manager_result.get("success", False),
            "initialization_time": time.time(),
            "correlation_id": correlation_id,
            "init_result": init_result,
            "manager_result": ha_manager_result,
            "stage_result": stage_result
        }
        
        cache_set(HA_INITIALIZATION_CACHE_KEY, ha_status, ttl=3600)
        
        record_metric("ha_extension_initialization", 1.0, {
            "success": ha_manager_result.get("success", False),
            "correlation_id": correlation_id
        })
        
        if ha_manager_result.get("success", False):
            log_info(f"HA extension initialized successfully [{correlation_id}]")
            return create_success_response("HA extension initialized", ha_status)
        else:
            log_error(f"HA extension initialization failed [{correlation_id}]")
            return create_error_response("HA extension initialization failed", ha_status)
        
    except Exception as e:
        log_error(f"HA extension initialization exception: {str(e)}")
        return create_error_response("HA extension initialization exception", {"error": str(e)})

def _initialize_ha_manager_gateway() -> Dict[str, Any]:
    """Initialize HA manager using gateway operations."""
    try:
        config = _get_ha_config_gateway()
        
        if not config.get("enabled", False):
            return create_success_response("HA manager disabled", {"enabled": False})
        
        connection_test = _test_ha_connection_gateway(config)
        
        if not connection_test.get("success", False):
            log_warning("HA connection test failed", {"result": connection_test})
            return create_error_response("HA connection failed", connection_test)
        
        manager_data = {
            "config": config,
            "state": "initialized",
            "created_at": time.time(),
            "last_activity": time.time(),
            "connection_validated": True
        }
        
        cache_set(HA_MANAGER_CACHE_KEY, manager_data, ttl=3600)
        
        log_info("HA manager initialized successfully")
        return create_success_response("HA manager initialized", manager_data)
        
    except Exception as e:
        log_error(f"HA manager initialization failed: {str(e)}")
        return create_error_response("HA manager initialization failed", {"error": str(e)})

def _get_ha_config_gateway() -> Dict[str, Any]:
    """Get Home Assistant configuration using gateway."""
    cached_config = cache_get(HA_CONFIG_CACHE_KEY)
    if cached_config:
        return cached_config
    
    import os
    config = {
        "enabled": os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower() == "true",
        "base_url": os.environ.get("HOME_ASSISTANT_URL", ""),
        "access_token": os.environ.get("HOME_ASSISTANT_TOKEN", ""),
        "timeout": int(os.environ.get("HOME_ASSISTANT_TIMEOUT", "30")),
        "verify_ssl": os.environ.get("HOME_ASSISTANT_VERIFY_SSL", "true").lower() == "true"
    }
    
    cache_set(HA_CONFIG_CACHE_KEY, config, ttl=300)
    return config

def _test_ha_connection_gateway(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test Home Assistant connection using gateway HTTP client."""
    try:
        test_url = f"{config['base_url']}/api/"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        result = make_get_request(
            url=test_url,
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if result.get("success", False):
            log_info("HA connection test successful")
            return create_success_response("HA connection successful", {
                "status_code": result.get("status_code", 200),
                "execution_time_ms": result.get("execution_time_ms", 0)
            })
        else:
            log_warning("HA connection test failed", {"result": result})
            return create_error_response("HA connection failed", result)
        
    except Exception as e:
        log_error(f"HA connection test exception: {str(e)}")
        return create_error_response("HA connection test exception", {"error": str(e)})

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    import os
    return os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower() == "true"

def get_ha_status() -> Dict[str, Any]:
    """Get current Home Assistant extension status."""
    try:
        cached_status = cache_get(HA_INITIALIZATION_CACHE_KEY)
        
        if cached_status:
            return create_success_response("HA status retrieved from cache", cached_status)
        
        if not is_ha_extension_enabled():
            return create_success_response("HA extension disabled", {
                "enabled": False,
                "initialized": False
            })
        
        return create_error_response("HA extension not initialized", {
            "enabled": True,
            "initialized": False
        })
        
    except Exception as e:
        log_error(f"Get HA status failed: {str(e)}")
        return create_error_response("Get HA status failed", {"error": str(e)})

def call_ha_service(domain: str, service: str, entity_id: str, service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        
        if 'Discovery' in namespace:
            return _handle_alexa_discovery_gateway(correlation_id)
        elif 'PowerController' in namespace:
            return _handle_alexa_power_control_gateway(directive, correlation_id)
        elif 'BrightnessController' in namespace:
            return _handle_alexa_brightness_control_gateway(directive, correlation_id)
        else:
            return create_error_response("Unsupported Alexa namespace", {
                "namespace": namespace,
                "name": name,
                "correlation_id": correlation_id
            })
        
    except Exception as e:
        log_error(f"Alexa HA request processing exception: {str(e)}")
        return create_error_response("Alexa HA request exception", {"error": str(e)})

def _handle_alexa_discovery_gateway(correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa discovery for HA devices."""
    try:
        log_info(f"Handling Alexa discovery [{correlation_id}]")
        
        config = _get_ha_config_gateway()
        url = f"{config['base_url']}/api/states"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        result = make_get_request(url=url, headers=headers, timeout=config.get('timeout', 30))
        
        if not result.get("success", False):
            return create_error_response("Discovery failed", {
                "result": result,
                "correlation_id": correlation_id
            })
        
        states = result.get("response", [])
        endpoints = []
        
        for state in states:
            entity_id = state.get("entity_id", "")
            domain = entity_id.split(".")[0] if "." in entity_id else ""
            
            if domain in ["light", "switch"]:
                endpoint = {
                    "endpointId": entity_id,
                    "friendlyName": state.get("attributes", {}).get("friendly_name", entity_id),
                    "manufacturerName": "Home Assistant",
                    "description": f"HA {domain}",
                    "displayCategories": ["LIGHT" if domain == "light" else "SWITCH"],
                    "capabilities": [
                        {
                            "type": "AlexaInterface",
                            "interface": "Alexa.PowerController",
                            "version": "3",
                            "properties": {
                                "supported": [{"name": "powerState"}],
                                "proactivelyReported": False,
                                "retrievable": True
                            }
                        }
                    ]
                }
                endpoints.append(endpoint)
        
        record_metric("alexa_discovery", 1.0, {
            "device_count": len(endpoints),
            "correlation_id": correlation_id
        })
        
        log_info(f"Discovery complete: {len(endpoints)} devices [{correlation_id}]")
        return create_success_response("Discovery successful", {
            "endpoints": endpoints,
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"Alexa discovery exception: {str(e)}")
        return create_error_response("Alexa discovery exception", {"error": str(e)})

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

def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Cleaning up HA extension [{correlation_id}]")
        
        cache_delete(HA_INITIALIZATION_CACHE_KEY)
        cache_delete(HA_CONFIG_CACHE_KEY)
        cache_delete(HA_MANAGER_CACHE_KEY)
        
        record_metric("ha_extension_cleanup", 1.0, {"correlation_id": correlation_id})
        
        log_info(f"HA extension cleanup complete [{correlation_id}]")
        return create_success_response("HA extension cleanup complete", {
            "correlation_id": correlation_id
        })
        
    except Exception as e:
        log_error(f"HA extension cleanup exception: {str(e)}")
        return create_error_response("HA extension cleanup exception", {"error": str(e)})

# EOF
