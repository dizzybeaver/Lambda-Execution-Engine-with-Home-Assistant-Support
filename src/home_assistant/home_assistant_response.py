"""
home_assistant_response.py - Home Assistant Response Processing Module
Version: 2025.09.20.01
Description: Specialized response processing for Home Assistant using core generic functions

IMPLEMENTS:
- HA response formatting (thin wrappers around generic response functions)
- Error handling for HA operations (using logging gateway)
- Response validation for HA data (using security gateway)
- Cache-aware response processing (memory optimized)

ARCHITECTURE:
- Uses home_assistant_core generic functions for actual operations
- Integrates with logging gateway for response tracking
- Uses security gateway for response validation
- Lambda-optimized for 128MB memory limit

PRIMARY FILE: home_assistant.py (interface)
SECONDARY FILE: home_assistant_response.py (specialized module)
"""

import json
import time
import logging
import urllib3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import from core for generic functions
from .home_assistant_core import (
    _get_ha_manager,
    HAOperationResult
)

# Use logging gateway for response tracking
from logging import record_request, record_error

# Use security gateway for validation
from security import validate_request_data

# ===== SECTION 1: RESPONSE DATA STRUCTURES =====

@dataclass
class HAResponseStats:
    """Statistics for HA response processing."""
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    avg_processing_time_ms: float = 0.0
    last_response_time: float = 0.0

# ===== SECTION 2: HA RESPONSE PROCESSOR =====

class HAResponseProcessor:
    """
    Home Assistant response processor using designated gateways.
    Memory optimized for Lambda environment.
    """
    
    def __init__(self):
        self._stats = HAResponseStats()
        self.max_response_size_bytes = 512 * 1024  # 512KB for HA responses
        
    def process_ha_response(self, directive: Dict[str, Any], 
                          response: urllib3.HTTPResponse,
                          response_time_ms: float = None) -> Dict[str, Any]:
        """
        Process HTTP response from Home Assistant.
        Uses logging gateway for tracking and security gateway for validation.
        """
        start_time = time.time()
        
        try:
            # Validate directive through security gateway
            validation_result = validate_request_data(directive)
            if not validation_result.get("valid", False):
                return self._create_error_response(
                    "Invalid directive structure",
                    validation_result
                )
            
            # Parse HTTP response
            if response.status == 200:
                try:
                    response_data = json.loads(response.data.decode('utf-8'))
                    result = self._create_success_response(directive, response_data)
                except json.JSONDecodeError as e:
                    result = self._create_error_response(
                        "Invalid JSON response from Home Assistant",
                        {"json_error": str(e)}
                    )
            else:
                result = self._create_error_response(
                    f"Home Assistant returned status {response.status}",
                    {"status_code": response.status, "response": response.data.decode('utf-8')}
                )
            
            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(result.get("success", False), processing_time)
            
            # Record through logging gateway
            if result.get("success"):
                record_request("ha_response_success", processing_time)
            else:
                record_error(Exception(result.get("error", "Unknown error")), "HA_RESPONSE")
            
            return result
            
        except Exception as e:
            error_result = self._create_error_response(str(e), {"exception": type(e).__name__})
            record_error(e, "HA_RESPONSE_PROCESSING")
            return error_result
    
    def _create_success_response(self, directive: Dict[str, Any], 
                               response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create successful HA response using generic patterns."""
        try:
            # Extract directive info
            header = directive.get("directive", {}).get("header", {})
            endpoint = directive.get("directive", {}).get("endpoint", {})
            
            return {
                "success": True,
                "event": {
                    "header": {
                        "namespace": header.get("namespace", "Alexa"),
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": header.get("messageId", "unknown"),
                        "correlationToken": header.get("correlationToken")
                    },
                    "endpoint": endpoint,
                    "payload": {}
                },
                "context": {
                    "properties": self._extract_context_properties(response_data)
                },
                "ha_response": response_data,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error creating success response: {e}")
            return self._create_error_response(str(e), {"creation_error": True})
    
    def _create_error_response(self, error_message: str, 
                             details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create error response for HA operations."""
        return {
            "success": False,
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "payloadVersion": "3",
                    "messageId": f"error-{int(time.time())}"
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": error_message
                }
            },
            "error": error_message,
            "details": details or {},
            "timestamp": time.time()
        }
    
    def _extract_context_properties(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract context properties from HA response."""
        properties = []
        
        try:
            # Handle different HA response formats generically
            if isinstance(response_data, list):
                # State list response
                for state in response_data:
                    if isinstance(state, dict) and "entity_id" in state:
                        properties.append({
                            "namespace": "Alexa.EndpointHealth",
                            "name": "connectivity",
                            "value": {"value": "OK"},
                            "timeOfSample": state.get("last_changed", time.time()),
                            "uncertaintyInMilliseconds": 0
                        })
            elif isinstance(response_data, dict):
                # Single entity response
                if "entity_id" in response_data:
                    properties.append({
                        "namespace": "Alexa.EndpointHealth", 
                        "name": "connectivity",
                        "value": {"value": "OK"},
                        "timeOfSample": response_data.get("last_changed", time.time()),
                        "uncertaintyInMilliseconds": 0
                    })
        except Exception as e:
            logger.warning(f"Error extracting context properties: {e}")
        
        return properties
    
    def _update_stats(self, success: bool, processing_time_ms: float) -> None:
        """Update response processing statistics."""
        self._stats.total_responses += 1
        self._stats.last_response_time = time.time()
        
        if success:
            self._stats.successful_responses += 1
        else:
            self._stats.error_responses += 1
        
        # Update average processing time
        if self._stats.total_responses > 0:
            current_avg = self._stats.avg_processing_time_ms
            new_avg = ((current_avg * (self._stats.total_responses - 1)) + processing_time_ms) / self._stats.total_responses
            self._stats.avg_processing_time_ms = new_avg

# ===== SECTION 3: SINGLETON ACCESS =====

_ha_response_processor: Optional[HAResponseProcessor] = None

def _get_ha_response_processor() -> HAResponseProcessor:
    """Get HA response processor singleton."""
    global _ha_response_processor
    if _ha_response_processor is None:
        _ha_response_processor = HAResponseProcessor()
    return _ha_response_processor

# ===== SECTION 4: PUBLIC INTERFACE FUNCTIONS =====

def process_ha_alexa_response(directive: Dict[str, Any], 
                            response: urllib3.HTTPResponse,
                            response_time_ms: float = None) -> Dict[str, Any]:
    """
    Process Alexa directive response from Home Assistant.
    Main interface function for HA response processing.
    """
    processor = _get_ha_response_processor()
    return processor.process_ha_response(directive, response, response_time_ms)

def process_ha_service_response(service_call: Dict[str, Any],
                              response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Home Assistant service call response.
    Generic function for any HA service response.
    """
    try:
        # Validate service call through security gateway
        validation_result = validate_request_data(service_call)
        if not validation_result.get("valid", False):
            return {
                "success": False,
                "error": "Invalid service call structure",
                "details": validation_result,
                "timestamp": time.time()
            }
        
        # Process response generically
        result = {
            "success": True,
            "service": service_call.get("service", "unknown"),
            "entity_id": service_call.get("entity_id"),
            "response_data": response_data,
            "timestamp": time.time()
        }
        
        # Record through logging gateway
        record_request("ha_service_response", None)
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "service_call": service_call,
            "timestamp": time.time()
        }
        record_error(e, "HA_SERVICE_RESPONSE")
        return error_result

def process_ha_state_response(entity_ids: List[str], 
                            states_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Home Assistant state query response.
    Handles both single and bulk state responses.
    """
    try:
        processed_states = {}
        
        for entity_id in entity_ids:
            if entity_id in states_data:
                state_data = states_data[entity_id]
                processed_states[entity_id] = {
                    "state": state_data.get("state"),
                    "attributes": state_data.get("attributes", {}),
                    "last_changed": state_data.get("last_changed"),
                    "friendly_name": state_data.get("attributes", {}).get("friendly_name", entity_id)
                }
        
        result = {
            "success": True,
            "entity_ids": entity_ids,
            "states": processed_states,
            "found_count": len(processed_states),
            "timestamp": time.time()
        }
        
        # Record through logging gateway
        record_request("ha_state_response", None)
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "entity_ids": entity_ids,
            "timestamp": time.time()
        }
        record_error(e, "HA_STATE_RESPONSE")
        return error_result

def get_ha_response_stats() -> Dict[str, Any]:
    """Get Home Assistant response processing statistics."""
    processor = _get_ha_response_processor()
    stats = processor._stats
    
    return {
        "total_responses": stats.total_responses,
        "successful_responses": stats.successful_responses,
        "error_responses": stats.error_responses,
        "success_rate": (stats.successful_responses / max(stats.total_responses, 1)) * 100,
        "avg_processing_time_ms": stats.avg_processing_time_ms,
        "last_response_time": stats.last_response_time,
        "timestamp": time.time()
    }

def reset_ha_response_processor() -> bool:
    """Reset HA response processor (for cleanup)."""
    global _ha_response_processor
    try:
        _ha_response_processor = None
        return True
    except Exception as e:
        logger.error(f"Error resetting HA response processor: {e}")
        return False

# ===== SECTION 5: MODULE EXPORTS =====

__all__ = [
    # Main processing functions
    'process_ha_alexa_response',
    'process_ha_service_response', 
    'process_ha_state_response',
    
    # Statistics and management
    'get_ha_response_stats',
    'reset_ha_response_processor',
    
    # Data structures
    'HAResponseStats',
    'HAResponseProcessor'
]

# EOF
