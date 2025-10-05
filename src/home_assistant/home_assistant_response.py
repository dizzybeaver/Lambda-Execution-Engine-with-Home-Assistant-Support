"""
home_assistant_response.py - Home Assistant Response Processing Module
Version: 2025.10.04.04
Description: Specialized response processing for Home Assistant

DEPLOYMENT FIX: Removed relative imports for Lambda compatibility

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import time
import logging
import urllib3
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from home_assistant_core import _get_ha_manager, HAOperationResult
except ImportError:
    _get_ha_manager = None
    HAOperationResult = None

try:
    from logging import record_request, record_error
except ImportError:
    def record_request(*args, **kwargs): pass
    def record_error(*args, **kwargs): pass

try:
    from security import validate_request_data
except ImportError:
    def validate_request_data(data):
        return {"valid": True}

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
    """Home Assistant response processor using designated gateways."""
    
    def __init__(self):
        self._stats = HAResponseStats()
        self.max_response_size_bytes = 512 * 1024
        
    def process_ha_response(self, directive: Dict[str, Any], 
                          response: urllib3.HTTPResponse,
                          response_time_ms: float = None) -> Dict[str, Any]:
        """Process HTTP response from Home Assistant."""
        start_time = time.time()
        
        try:
            validation_result = validate_request_data(directive)
            if not validation_result.get("valid", False):
                return self._create_error_response(
                    "Invalid directive structure",
                    validation_result
                )
            
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
            
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(result.get("success", False), processing_time)
            
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
            header = directive.get('header', {})
            endpoint = directive.get('endpoint', {})
            
            response = {
                "success": True,
                "event": {
                    "header": {
                        "namespace": header.get('namespace', 'Alexa'),
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": header.get('messageId', 'unknown'),
                        "correlationToken": header.get('correlationToken')
                    },
                    "endpoint": endpoint,
                    "payload": {}
                },
                "context": {
                    "properties": self._extract_context_properties(response_data)
                },
                "timestamp": time.time()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating success response: {e}")
            return self._create_error_response("Response formatting error", {"error": str(e)})
    
    def _create_error_response(self, error_message: str, 
                             error_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create error response with consistent format."""
        return {
            "success": False,
            "error": error_message,
            "error_details": error_details or {},
            "timestamp": time.time()
        }
    
    def _extract_context_properties(self, response_data: Any) -> List[Dict[str, Any]]:
        """Extract context properties from HA response."""
        properties = []
        
        try:
            if isinstance(response_data, list):
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
        
        if self._stats.total_responses > 0:
            current_avg = self._stats.avg_processing_time_ms
            new_avg = ((current_avg * (self._stats.total_responses - 1)) + processing_time_ms) / self._stats.total_responses
            self._stats.avg_processing_time_ms = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get response processor statistics."""
        return {
            "total_responses": self._stats.total_responses,
            "successful_responses": self._stats.successful_responses,
            "error_responses": self._stats.error_responses,
            "avg_processing_time_ms": self._stats.avg_processing_time_ms,
            "last_response_time": self._stats.last_response_time,
            "success_rate": (
                (self._stats.successful_responses / self._stats.total_responses * 100)
                if self._stats.total_responses > 0 else 0.0
            )
        }

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
    """Process Alexa directive response from Home Assistant."""
    processor = _get_ha_response_processor()
    return processor.process_ha_response(directive, response, response_time_ms)

def process_ha_service_response(service_call: Dict[str, Any],
                              response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process Home Assistant service call response."""
    try:
        validation_result = validate_request_data(service_call)
        if not validation_result.get("valid", False):
            return {
                "success": False,
                "error": "Invalid service call structure",
                "details": validation_result,
                "timestamp": time.time()
            }
        
        result = {
            "success": True,
            "service": service_call.get("service", "unknown"),
            "entity_id": service_call.get("entity_id"),
            "response_data": response_data,
            "timestamp": time.time()
        }
        
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
    """Process Home Assistant state query response."""
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
    return processor.get_stats()

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
    'process_ha_alexa_response',
    'process_ha_service_response', 
    'process_ha_state_response',
    'get_ha_response_stats',
    'reset_ha_response_processor',
    'HAResponseStats',
    'HAResponseProcessor'
]

# EOF
