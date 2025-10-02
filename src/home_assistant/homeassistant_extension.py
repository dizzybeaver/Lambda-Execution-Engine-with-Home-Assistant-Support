"""
homeassistant_extension.py - Phase 4: Extension Interfaces Implementation
Version: 2025.10.02.01
Daily Revision: Project B Assistant Name Implementation

Revolutionary Gateway Optimization - Phase 4 Implementation
- Migrated to use gateway.py universal routing
- All imports consolidated from gateway module
- Lazy loading compatible
- 100% Free Tier AWS compliant
- Assistant Name Customization Support

Home Assistant Integration for Lambda Execution Engine
Self-contained extension using gateway interfaces for all operations.
"""

import time
import os
import re
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
HA_ASSISTANT_NAME_CACHE_KEY = "ha_assistant_name"

def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension with gateway architecture."""
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
        if not config.get("base_url") or not config.get("access_token"):
            return {"success": False, "error": "Missing URL or token"}
            
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = make_get_request(
            url=f"{config['base_url']}/api/",
            headers=headers,
            timeout=config.get("timeout", 30)
        )
        
        return response
        
    except Exception as e:
        log_error(f"HA connection test failed: {str(e)}")
        return {"success": False, "error": str(e)}

def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    try:
        cache_keys = [
            HA_INITIALIZATION_CACHE_KEY,
            HA_CONFIG_CACHE_KEY,
            HA_MANAGER_CACHE_KEY,
            HA_ASSISTANT_NAME_CACHE_KEY
        ]
        
        for key in cache_keys:
            cache_delete(key)
        
        log_info("HA extension cleanup completed")
        return create_success_response("HA extension cleanup completed")
        
    except Exception as e:
        log_error(f"HA extension cleanup failed: {str(e)}")
        return create_error_response("HA extension cleanup failed", {"error": str(e)})

def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status."""
    try:
        manager_data = cache_get(HA_MANAGER_CACHE_KEY)
        
        if not manager_data:
            return create_error_response("HA manager not initialized")
            
        status_data = {
            "state": manager_data.get("state", "unknown"),
            "initialized_at": manager_data.get("created_at"),
            "last_activity": manager_data.get("last_activity"),
            "uptime_seconds": time.time() - manager_data.get("created_at", time.time())
        }
        
        return create_success_response("HA status retrieved", status_data)
        
    except Exception as e:
        log_error(f"HA status check failed: {str(e)}")
        return create_error_response("HA status check failed", {"error": str(e)})

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower() == "true"

def get_ha_assistant_name() -> str:
    """Get configured Home Assistant assistant name."""
    try:
        cached_name = cache_get(HA_ASSISTANT_NAME_CACHE_KEY)
        if cached_name:
            return cached_name
            
        name = _get_assistant_name_from_config()
        
        cache_set(HA_ASSISTANT_NAME_CACHE_KEY, name, ttl=3600)
        
        log_debug(f"Assistant name retrieved: {name}")
        return name
        
    except Exception as e:
        log_error(f"Failed to get assistant name: {str(e)}")
        return "Home Assistant"

def _get_assistant_name_from_config() -> str:
    """Get assistant name from environment variable or Parameter Store."""
    env_name = os.environ.get("HA_ASSISTANT_NAME")
    if env_name:
        validated_name = validate_assistant_name(env_name)
        if validated_name["is_valid"]:
            return validated_name["name"]
        else:
            log_warning(f"Invalid assistant name in environment: {env_name}, using default")
    
    try:
        import boto3
        
        ssm = boto3.client('ssm')
        parameter_name = "/lambda-execution-engine/homeassistant/assistant_name"
        
        response = ssm.get_parameter(Name=parameter_name)
        param_name = response['Parameter']['Value']
        
        validated_name = validate_assistant_name(param_name)
        if validated_name["is_valid"]:
            log_info(f"Using assistant name from Parameter Store: {validated_name['name']}")
            return validated_name["name"]
        else:
            log_warning(f"Invalid assistant name in Parameter Store: {param_name}, using default")
            
    except Exception as e:
        log_debug(f"Could not retrieve assistant name from Parameter Store: {str(e)}")
    
    return "Home Assistant"

def validate_assistant_name(name: str) -> Dict[str, Any]:
    """Validate assistant name according to Alexa requirements."""
    try:
        if not name or not isinstance(name, str):
            return {
                "is_valid": False,
                "error": "Name must be a non-empty string",
                "name": "Home Assistant"
            }
        
        name = name.strip()
        
        if not name:
            return {
                "is_valid": False,
                "error": "Name cannot be empty or whitespace only",
                "name": "Home Assistant"
            }
        
        if len(name) < 2 or len(name) > 25:
            return {
                "is_valid": False,
                "error": "Name must be 2-25 characters long",
                "name": "Home Assistant"
            }
        
        if not re.match(r'^[a-zA-Z0-9\s]+$', name):
            return {
                "is_valid": False,
                "error": "Name can only contain letters, numbers, and spaces",
                "name": "Home Assistant"
            }
        
        name_lower = name.lower()
        
        forbidden_words = [
            "alexa", "amazon", "echo", "computer", "wake", "up"
        ]
        
        for forbidden in forbidden_words:
            if forbidden in name_lower:
                return {
                    "is_valid": False,
                    "error": f"Name cannot contain forbidden word: {forbidden}",
                    "name": "Home Assistant"
                }
        
        if name_lower.isdigit():
            return {
                "is_valid": False,
                "error": "Name cannot be numbers only",
                "name": "Home Assistant"
            }
        
        processed_name = name.title()
        
        return {
            "is_valid": True,
            "name": processed_name,
            "original": name
        }
        
    except Exception as e:
        log_error(f"Assistant name validation failed: {str(e)}")
        return {
            "is_valid": False,
            "error": f"Validation error: {str(e)}",
            "name": "Home Assistant"
        }

def set_assistant_name(name: str) -> Dict[str, Any]:
    """Set and validate new assistant name."""
    try:
        validation_result = validate_assistant_name(name)
        
        if not validation_result["is_valid"]:
            return create_error_response("Invalid assistant name", validation_result)
        
        validated_name = validation_result["name"]
        
        cache_set(HA_ASSISTANT_NAME_CACHE_KEY, validated_name, ttl=3600)
        
        log_info(f"Assistant name updated to: {validated_name}")
        
        return create_success_response("Assistant name updated", {
            "name": validated_name,
            "original": validation_result.get("original", name)
        })
        
    except Exception as e:
        log_error(f"Failed to set assistant name: {str(e)}")
        return create_error_response("Failed to set assistant name", {"error": str(e)})

def get_assistant_name_status() -> Dict[str, Any]:
    """Get assistant name configuration status."""
    try:
        current_name = get_ha_assistant_name()
        
        env_name = os.environ.get("HA_ASSISTANT_NAME")
        param_name = None
        
        try:
            import boto3
            ssm = boto3.client('ssm')
            response = ssm.get_parameter(Name="/lambda-execution-engine/homeassistant/assistant_name")
            param_name = response['Parameter']['Value']
        except:
            param_name = None
        
        status = {
            "current_name": current_name,
            "environment_variable": env_name,
            "parameter_store": param_name,
            "source": "default"
        }
        
        if env_name and validate_assistant_name(env_name)["is_valid"]:
            status["source"] = "environment_variable"
        elif param_name and validate_assistant_name(param_name)["is_valid"]:
            status["source"] = "parameter_store"
        
        return create_success_response("Assistant name status retrieved", status)
        
    except Exception as e:
        log_error(f"Failed to get assistant name status: {str(e)}")
        return create_error_response("Failed to get assistant name status", {"error": str(e)})

def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get comprehensive Home Assistant diagnostic information."""
    try:
        config = _get_ha_config_gateway()
        status = get_ha_status()
        assistant_status = get_assistant_name_status()
        
        diagnostic_info = {
            "timestamp": time.time(),
            "ha_enabled": config.get("enabled", False),
            "connection_status": status.get("data", {}).get("state", "unknown"),
            "assistant_name": assistant_status.get("data", {}).get("current_name", "Home Assistant"),
            "assistant_name_source": assistant_status.get("data", {}).get("source", "default"),
            "configuration": {
                "base_url_configured": bool(config.get("base_url")),
                "token_configured": bool(config.get("access_token")),
                "timeout": config.get("timeout", 30),
                "ssl_verify": config.get("verify_ssl", True)
            },
            "environment_variables": {
                "HOME_ASSISTANT_ENABLED": os.environ.get("HOME_ASSISTANT_ENABLED"),
                "HA_ASSISTANT_NAME": os.environ.get("HA_ASSISTANT_NAME"),
                "HA_FEATURE_PRESET": os.environ.get("HA_FEATURE_PRESET"),
                "HA_TIMEOUT": os.environ.get("HA_TIMEOUT"),
                "HA_VERIFY_SSL": os.environ.get("HA_VERIFY_SSL")
            }
        }
        
        if config.get("enabled", False):
            try:
                connection_test = _test_ha_connection_gateway(config)
                diagnostic_info["connection_test"] = {
                    "success": connection_test.get("success", False),
                    "error": connection_test.get("error")
                }
            except Exception as test_error:
                diagnostic_info["connection_test"] = {
                    "success": False,
                    "error": str(test_error)
                }
        
        return create_success_response("Diagnostic info retrieved", diagnostic_info)
        
    except Exception as e:
        log_error(f"Failed to get diagnostic info: {str(e)}")
        return create_error_response("Failed to get diagnostic info", {"error": str(e)})

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Home Assistant request using gateway interfaces."""
    try:
        correlation_id = generate_correlation_id()
        
        log_info("Processing Alexa HA request", {"correlation_id": correlation_id})
        
        if not is_ha_extension_enabled():
            return create_error_response("Home Assistant integration disabled")
        
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        
        record_metric("alexa_ha_request", {"namespace": namespace, "name": name})
        
        if namespace == "Alexa.Discovery" and name == "Discover":
            return _handle_discovery_request(event, correlation_id)
        elif namespace == "Alexa.PowerController":
            return _handle_power_controller_request(event, correlation_id)
        else:
            log_warning(f"Unsupported Alexa directive: {namespace}.{name}")
            return create_error_response(f"Unsupported directive: {namespace}.{name}")
            
    except Exception as e:
        log_error(f"Alexa HA request processing failed: {str(e)}")
        return create_error_response("Request processing failed", {"error": str(e)})

def _handle_discovery_request(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa device discovery request."""
    try:
        log_info("Processing device discovery", {"correlation_id": correlation_id})
        
        endpoints = []
        
        sample_endpoint = {
            "endpointId": "light.sample_light",
            "manufacturerName": "Home Assistant",
            "friendlyName": "Sample Light",
            "description": "Sample smart light",
            "displayCategories": ["LIGHT"],
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
        
        endpoints.append(sample_endpoint)
        
        response = {
            "event": {
                "header": {
                    "namespace": "Alexa.Discovery",
                    "name": "Discover.Response",
                    "payloadVersion": "3",
                    "messageId": correlation_id
                },
                "payload": {
                    "endpoints": endpoints
                }
            }
        }
        
        log_info(f"Discovery completed with {len(endpoints)} endpoints")
        return response
        
    except Exception as e:
        log_error(f"Discovery request failed: {str(e)}")
        return create_error_response("Discovery failed", {"error": str(e)})

def _handle_power_controller_request(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Handle Alexa power controller request."""
    try:
        directive = event.get("directive", {})
        header = directive.get("header", {})
        endpoint = directive.get("endpoint", {})
        
        entity_id = endpoint.get("endpointId", "")
        command = header.get("name", "")
        
        log_info(f"Power control: {command} for {entity_id}", {"correlation_id": correlation_id})
        
        response = {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "payloadVersion": "3",
                    "messageId": correlation_id,
                    "correlationToken": header.get("correlationToken")
                },
                "endpoint": {
                    "endpointId": entity_id
                },
                "payload": {}
            }
        }
        
        return response
        
    except Exception as e:
        log_error(f"Power controller request failed: {str(e)}")
        return create_error_response("Power control failed", {"error": str(e)})
