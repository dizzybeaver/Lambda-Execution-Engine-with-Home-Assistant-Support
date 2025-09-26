"""
homeassistant_extension.py - UPDATED: Coordinates with Initialization Interface
Version: 2025.09.25.01
Description: Home Assistant extension updated to coordinate with consolidated initialization interface

UPDATES APPLIED:
- ✅ INITIALIZATION COORDINATION: HA extension initialization coordinates with main initialization.py
- ✅ GATEWAY UTILIZATION: Maximizes usage of gateway functions for consistency with optimization
- ✅ INITIALIZATION DELEGATION: HA startup operations integrate with system initialization sequence
- ✅ MEMORY OPTIMIZATION: Benefits from consolidated initialization memory optimizations
- ✅ ENHANCED COORDINATION: HA extension startup coordinated through initialization interface

ARCHITECTURE: SELF-CONTAINED EXTENSION
- homeassistant_extension.py = Self-contained optional extension
- Uses ALL primary gateway interfaces for maximum functionality
- Coordinates initialization through consolidated initialization.py interface
- Isolation rule: ALL Home Assistant-specific code exists ONLY in this extension

INITIALIZATION INTEGRATION:
- HA extension initialization coordinates with system initialization sequence  
- Uses initialization interface for HA startup coordination
- Benefits from consolidated initialization metrics and health tracking
- Integrates with Lambda cold start optimization for HA services

OPTIMIZATION BENEFITS:
- Consistent initialization patterns with main system
- Shared memory optimization benefits
- Coordinated error handling and recovery
- Integrated initialization metrics tracking

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

import logging
import os
import time
from typing import Dict, Any, Optional, Union, List
from enum import Enum

# GATEWAY INTERFACE IMPORTS - Maximum utilization for consistency
from singleton import get_singleton, SingletonType, manage_singletons
from cache import cache_get, cache_set, cache_clear, CacheType
from security import validate_request, validate_input
from metrics import record_metric, get_performance_stats
from utility import (create_success_response, create_error_response, 
                     validate_string_input, sanitize_response_data, generate_correlation_id)
from logging import log_info, log_error, log_debug, log_warning
from http_client import make_request, get_http_status
from lambda import create_alexa_response, coordinate_lambda_operation

# INITIALIZATION INTERFACE INTEGRATION - Coordinate with consolidated initialization
from initialization import (
    execute_initialization_operation,
    record_initialization_stage, 
    InitializationStage,
    InitializationType
)

logger = logging.getLogger(__name__)

# ===== HOME ASSISTANT EXTENSION CONSTANTS =====

HA_CACHE_PREFIX = "ha_extension_"
HA_INITIALIZATION_CACHE_KEY = "ha_initialization_status"
HA_CONNECTION_CACHE_KEY = "ha_connection_status"

# ===== SECTION 1: HOME ASSISTANT EXTENSION ENUMS =====

class HAConnectionStatus(Enum):
    """Home Assistant connection status."""
    DISABLED = "disabled"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class HAServiceResult(Enum):
    """Home Assistant service call results."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"
    COST_BLOCKED = "cost_blocked"

class HAEntityType(Enum):
    """Home Assistant entity types."""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    COVER = "cover"

# ===== SECTION 2: HOME ASSISTANT EXTENSION INITIALIZATION =====

def initialize_ha_extension() -> Dict[str, Any]:
    """
    UPDATED: Initialize Home Assistant extension with initialization interface coordination.
    Integrates HA extension startup with consolidated initialization system.
    """
    try:
        log_info("Starting HA extension initialization with system coordination")
        
        # Check if HA extension is enabled using utility gateway
        if not is_ha_extension_enabled():
            return create_success_response("HA extension disabled", {
                "enabled": False,
                "initialization_skipped": True
            })
        
        # Coordinate HA initialization with main initialization interface
        ha_init_result = execute_initialization_operation(
            InitializationType.SYSTEM_STARTUP,
            component="home_assistant_extension",
            extension_type="home_assistant"
        )
        
        if not ha_init_result.get("success", False):
            return create_error_response("HA extension initialization coordination failed", ha_init_result)
        
        # Record HA initialization stage
        init_stage_result = record_initialization_stage(InitializationStage.CONFIGURATION, "ha_extension")
        
        # Initialize HA manager using consolidated pattern
        ha_manager_result = _initialize_ha_manager_coordinated()
        
        # Cache HA initialization status using cache gateway
        ha_status = {
            "initialized": ha_manager_result.get("success", False),
            "initialization_time": time.time(),
            "coordination_result": ha_init_result,
            "manager_result": ha_manager_result,
            "stage_result": init_stage_result
        }
        
        cache_set(HA_INITIALIZATION_CACHE_KEY, ha_status, cache_type=CacheType.MEMORY)
        
        # Record HA initialization metrics using metrics gateway
        record_metric("ha_extension_initialization", 1.0, {
            "success": ha_manager_result.get("success", False),
            "coordination_success": ha_init_result.get("success", False)
        })
        
        if ha_manager_result.get("success", False):
            return create_success_response("HA extension initialized successfully", {
                "ha_status": ha_status,
                "manager_initialized": True,
                "system_coordinated": True
            })
        else:
            return create_error_response("HA extension initialization failed", {
                "ha_status": ha_status,
                "manager_error": ha_manager_result.get("error", "Unknown error")
            })
        
    except Exception as e:
        log_error(f"HA extension initialization failed: {str(e)}")
        return create_error_response("HA extension initialization failed", {"error": str(e)})

def _initialize_ha_manager_coordinated() -> Dict[str, Any]:
    """
    Initialize HA manager with coordination through gateway functions.
    Uses consolidated initialization patterns for consistency.
    """
    try:
        # Get HA configuration using cache gateway and validate using security gateway
        ha_config = _get_ha_configuration_validated()
        
        if not ha_config.get("valid", False):
            return create_error_response("HA configuration validation failed", ha_config)
        
        config_data = ha_config.get("config", {})
        
        # Get or create HA manager using singleton gateway
        ha_manager = get_singleton(SingletonType.APPLICATION_INITIALIZER)  # Generic singleton for HA
        
        # Initialize HA manager with validated configuration
        if hasattr(ha_manager, 'initialize_ha'):
            manager_init_result = ha_manager.initialize_ha(config_data)
        else:
            # Create HA manager functionality if not available
            manager_init_result = _create_ha_manager_functionality(config_data)
        
        # Test HA connection using http_client gateway
        if manager_init_result.get("success", False):
            connection_result = _test_ha_connection_coordinated(config_data)
            
            # Cache connection status using cache gateway
            cache_set(HA_CONNECTION_CACHE_KEY, {
                "status": "connected" if connection_result.get("success", False) else "error",
                "test_result": connection_result,
                "last_test": time.time()
            }, cache_type=CacheType.MEMORY)
            
            return create_success_response("HA manager initialized and connected", {
                "manager_result": manager_init_result,
                "connection_result": connection_result
            })
        else:
            return create_error_response("HA manager initialization failed", manager_init_result)
        
    except Exception as e:
        log_error(f"HA manager coordination failed: {str(e)}")
        return create_error_response("HA manager coordination failed", {"error": str(e)})

def _get_ha_configuration_validated() -> Dict[str, Any]:
    """
    Get and validate HA configuration using gateway functions.
    """
    try:
        # Get configuration from environment
        ha_config = {
            'base_url': os.getenv('HOME_ASSISTANT_URL', '').strip(),
            'access_token': os.getenv('HOME_ASSISTANT_TOKEN', '').strip(), 
            'timeout': int(os.getenv('HOME_ASSISTANT_TIMEOUT', '30')),
            'ssl_verify': os.getenv('HOME_ASSISTANT_SSL_VERIFY', 'true').lower() == 'true'
        }
        
        # Validate configuration using utility gateway
        url_validation = validate_string_input(ha_config['base_url'], min_length=10, pattern="url")
        token_validation = validate_string_input(ha_config['access_token'], min_length=20, required=True)
        
        if not url_validation.get("is_valid", False):
            return create_error_response("Invalid HA URL configuration", url_validation)
        
        if not token_validation.get("is_valid", False):
            return create_error_response("Invalid HA token configuration", token_validation)
        
        # Additional security validation using security gateway
        security_validation = validate_input(ha_config, input_type="configuration")
        if not security_validation.get("success", True):
            return create_error_response("HA configuration security validation failed", security_validation)
        
        return create_success_response("HA configuration validated", {
            "config": ha_config,
            "valid": True
        })
        
    except Exception as e:
        log_error(f"HA configuration validation failed: {str(e)}")
        return create_error_response("HA configuration validation failed", {"error": str(e)})

def _test_ha_connection_coordinated(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test HA connection using http_client gateway for consistency.
    """
    try:
        # Test connection using http_client gateway
        test_url = f"{config['base_url']}/api/"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        connection_result = make_request(
            url=test_url,
            method="GET",
            headers=headers,
            timeout=config.get('timeout', 30)
        )
        
        if connection_result.get("success", False):
            log_info("HA connection test successful")
            return create_success_response("HA connection successful", {
                "response_status": connection_result.get("status_code", 200),
                "connection_time": connection_result.get("execution_time_ms", 0)
            })
        else:
            log_warning("HA connection test failed", {"result": connection_result})
            return create_error_response("HA connection failed", connection_result)
        
    except Exception as e:
        log_error(f"HA connection test failed: {str(e)}")
        return create_error_response("HA connection test failed", {"error": str(e)})

def _create_ha_manager_functionality(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create HA manager functionality if not available in singleton.
    """
    try:
        # Create basic HA manager functionality
        ha_manager_data = {
            "config": config,
            "state": "initialized",
            "created_at": time.time(),
            "last_activity": time.time()
        }
        
        # Cache HA manager data using cache gateway
        cache_set("ha_manager_data", ha_manager_data, cache_type=CacheType.MEMORY)
        
        return create_success_response("HA manager functionality created", ha_manager_data)
        
    except Exception as e:
        log_error(f"HA manager creation failed: {str(e)}")
        return create_error_response("HA manager creation failed", {"error": str(e)})

def cleanup_ha_extension() -> Dict[str, Any]:
    """
    UPDATED: Cleanup Home Assistant extension with initialization interface coordination.
    """
    try:
        log_info("Starting HA extension cleanup with system coordination")
        
        # Clear HA caches using cache gateway
        cache_clear(HA_INITIALIZATION_CACHE_KEY)
        cache_clear(HA_CONNECTION_CACHE_KEY)
        cache_clear("ha_manager_data")
        
        # Cleanup HA singleton if exists
        cleanup_result = manage_singletons("cleanup", "ha_manager")
        
        # Record cleanup metrics using metrics gateway
        record_metric("ha_extension_cleanup", 1.0, {
            "cache_cleared": True,
            "singleton_cleanup": cleanup_result.get("success", False)
        })
        
        return create_success_response("HA extension cleanup completed", {
            "cache_cleared": True,
            "singleton_cleanup": cleanup_result
        })
        
    except Exception as e:
        log_error(f"HA extension cleanup failed: {str(e)}")
        return create_error_response("HA extension cleanup failed", {"error": str(e)})

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    try:
        enabled_value = os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower()
        return enabled_value in ['true', '1', 'yes', 'on']
    except:
        return False

def get_ha_connection_status() -> HAConnectionStatus:
    """
    Get Home Assistant connection status using cache gateway.
    """
    try:
        if not is_ha_extension_enabled():
            return HAConnectionStatus.DISABLED
        
        # Get cached connection status using cache gateway
        connection_data = cache_get(HA_CONNECTION_CACHE_KEY, default_value={})
        
        status_str = connection_data.get("status", "disabled")
        
        # Return corresponding enum value
        for status_enum in HAConnectionStatus:
            if status_enum.value == status_str:
                return status_enum
        
        return HAConnectionStatus.DISABLED
        
    except Exception as e:
        log_error(f"HA connection status check failed: {str(e)}")
        return HAConnectionStatus.ERROR

# ===== SECTION 3: HOME ASSISTANT SERVICE OPERATIONS =====

def call_ha_service(domain: str, service: str, entity_id: Optional[str] = None,
                   service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Call Home Assistant service using coordinated gateway functions.
    """
    try:
        # Check if HA extension is enabled and initialized
        if not is_ha_extension_enabled():
            return create_error_response("HA extension is disabled")
        
        init_status = cache_get(HA_INITIALIZATION_CACHE_KEY, default_value={})
        if not init_status.get("initialized", False):
            return create_error_response("HA extension not initialized")
        
        # Validate service call parameters using utility gateway
        domain_validation = validate_string_input(domain, max_length=50, pattern="alphanumeric")
        if not domain_validation.get("is_valid", False):
            return create_error_response("Invalid HA domain", domain_validation)
        
        service_validation = validate_string_input(service, max_length=50, pattern="alphanumeric") 
        if not service_validation.get("is_valid", False):
            return create_error_response("Invalid HA service", service_validation)
        
        # Get HA configuration from cache
        ha_config_result = _get_ha_configuration_validated()
        if not ha_config_result.get("success", False):
            return create_error_response("HA configuration not available", ha_config_result)
        
        config = ha_config_result.get("data", {}).get("config", {})
        
        # Prepare service call
        service_url = f"{config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Prepare service data
        call_data = {}
        if entity_id:
            call_data["entity_id"] = entity_id
        if service_data:
            call_data.update(service_data)
        
        # Make service call using http_client gateway
        service_result = make_request(
            url=service_url,
            method="POST",
            headers=headers,
            data=call_data,
            timeout=config.get('timeout', 30)
        )
        
        # Record service call metrics using metrics gateway
        record_metric("ha_service_call", 1.0, {
            "domain": domain,
            "service": service,
            "success": service_result.get("success", False)
        })
        
        if service_result.get("success", False):
            return create_success_response("HA service call successful", {
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "response": service_result
            })
        else:
            return create_error_response("HA service call failed", service_result)
        
    except Exception as e:
        log_error(f"HA service call failed: {str(e)}")
        return create_error_response("HA service call failed", {"error": str(e)})

# ===== SECTION 4: ALEXA INTEGRATION =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Alexa request for Home Assistant using coordinated gateway functions.
    """
    try:
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled for Alexa")
        
        # Validate Alexa event using security gateway
        event_validation = validate_request(event)
        if not event_validation.get("success", True):
            return create_error_response("Alexa event validation failed", event_validation)
        
        # Extract directive information
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        # Route Alexa request based on namespace
        if 'Discovery' in namespace:
            return _handle_alexa_discovery_ha()
        elif 'PowerController' in namespace:
            return _handle_alexa_power_control_ha(directive)
        else:
            return create_error_response("Unsupported HA Alexa namespace", {
                "namespace": namespace,
                "name": name
            })
        
    except Exception as e:
        log_error(f"Alexa HA request processing failed: {str(e)}")
        return create_error_response("Alexa HA request processing failed", {"error": str(e)})

def _handle_alexa_discovery_ha() -> Dict[str, Any]:
    """Handle Alexa discovery for HA devices."""
    try:
        # Create basic HA discovery response
        discovery_response = {
            "event": {
                "header": {
                    "namespace": "Alexa.Discovery",
                    "name": "Discover.Response", 
                    "payloadVersion": "3",
                    "messageId": generate_correlation_id()
                },
                "payload": {
                    "endpoints": [
                        {
                            "endpointId": "ha-light-001",
                            "manufacturerName": "Home Assistant",
                            "friendlyName": "HA Light",
                            "description": "Home Assistant Light Control",
                            "displayCategories": ["LIGHT"],
                            "capabilities": [
                                {
                                    "type": "AlexaInterface",
                                    "interface": "Alexa.PowerController",
                                    "version": "3"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        # Record discovery metrics using metrics gateway
        record_metric("alexa_ha_discovery", 1.0, {
            "endpoint_count": len(discovery_response["event"]["payload"]["endpoints"])
        })
        
        return create_alexa_response(discovery_response)
        
    except Exception as e:
        log_error(f"Alexa HA discovery failed: {str(e)}")
        return create_error_response("Alexa HA discovery failed", {"error": str(e)})

def _handle_alexa_power_control_ha(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa power control for HA devices."""
    try:
        endpoint = directive.get('endpoint', {})
        endpoint_id = endpoint.get('endpointId', '')
        header = directive.get('header', {})
        name = header.get('name', '')
        
        # Determine HA service call based on Alexa command
        if name == "TurnOn":
            domain = "light"
            service = "turn_on"
            power_state = "ON"
        elif name == "TurnOff":
            domain = "light"
            service = "turn_off"
            power_state = "OFF"
        else:
            return create_error_response("Unsupported power control command", {"command": name})
        
        # Call HA service
        service_result = call_ha_service(domain, service, endpoint_id)
        
        if service_result.get("success", False):
            # Create Alexa response
            alexa_response = {
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": generate_correlation_id()
                    },
                    "endpoint": {
                        "endpointId": endpoint_id
                    },
                    "payload": {}
                },
                "context": {
                    "properties": [{
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": power_state,
                        "timeOfSample": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "uncertaintyInMilliseconds": 200
                    }]
                }
            }
            
            return create_alexa_response(alexa_response)
        else:
            return create_error_response("HA service call for Alexa failed", service_result)
        
    except Exception as e:
        log_error(f"Alexa HA power control failed: {str(e)}")
        return create_error_response("Alexa HA power control failed", {"error": str(e)})

# ===== SECTION 5: HA EXTENSION STATUS AND HEALTH =====

def get_ha_extension_status() -> Dict[str, Any]:
    """
    Get comprehensive HA extension status using gateway functions.
    """
    try:
        # Get initialization status from cache
        init_status = cache_get(HA_INITIALIZATION_CACHE_KEY, default_value={})
        
        # Get connection status from cache
        connection_status = cache_get(HA_CONNECTION_CACHE_KEY, default_value={})
        
        # Get performance metrics using metrics gateway
        performance_stats = get_performance_stats()
        
        extension_status = {
            "enabled": is_ha_extension_enabled(),
            "initialization": init_status,
            "connection": connection_status,
            "connection_enum": get_ha_connection_status().value,
            "performance": performance_stats,
            "timestamp": time.time()
        }
        
        return create_success_response("HA extension status retrieved", extension_status)
        
    except Exception as e:
        log_error(f"HA extension status retrieval failed: {str(e)}")
        return create_error_response("HA extension status retrieval failed", {"error": str(e)})

def ha_extension_health_check() -> Dict[str, Any]:
    """
    Comprehensive HA extension health check using gateway functions.
    """
    try:
        health_results = {}
        overall_healthy = True
        
        # Check if extension is enabled
        enabled = is_ha_extension_enabled()
        health_results["extension_enabled"] = enabled
        
        if not enabled:
            return create_success_response("HA extension health check completed", {
                "overall_healthy": True,
                "health_results": health_results,
                "note": "Extension disabled - health check skipped"
            })
        
        # Check initialization status
        init_status = cache_get(HA_INITIALIZATION_CACHE_KEY, default_value={})
        init_healthy = init_status.get("initialized", False)
        health_results["initialization_healthy"] = init_healthy
        
        if not init_healthy:
            overall_healthy = False
        
        # Check connection status
        connection_status = get_ha_connection_status()
        connection_healthy = connection_status == HAConnectionStatus.CONNECTED
        health_results["connection_healthy"] = connection_healthy
        
        if not connection_healthy:
            overall_healthy = False
        
        # Check configuration
        try:
            config_result = _get_ha_configuration_validated()
            config_healthy = config_result.get("success", False)
        except:
            config_healthy = False
        
        health_results["configuration_healthy"] = config_healthy
        
        if not config_healthy:
            overall_healthy = False
        
        health_data = {
            "overall_healthy": overall_healthy,
            "health_results": health_results,
            "timestamp": time.time()
        }
        
        return create_success_response("HA extension health check completed", health_data)
        
    except Exception as e:
        log_error(f"HA extension health check failed: {str(e)}")
        return create_error_response("HA extension health check failed", {"error": str(e)})

# EOF
