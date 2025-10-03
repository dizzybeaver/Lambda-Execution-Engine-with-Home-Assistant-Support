"""
Home Assistant Response - Alexa Response Processing with Template Optimization
Version: 2025.10.02.01
Description: Home Assistant response processing with pre-compiled Alexa templates

Copyright 2025 Joseph Hersey

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

import json
import time
import logging
import urllib3
import uuid
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .home_assistant_core import (
    _get_ha_manager,
    HAOperationResult
)

from logging import record_request, record_error
from security import validate_request_data

# ===== ALEXA RESPONSE TEMPLATES (Phase 2 Optimization) =====

_ALEXA_RESPONSE_TEMPLATE = '''{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "Response",
            "messageId": "%s",
            "correlationToken": "%s",
            "payloadVersion": "3"
        },
        "endpoint": %s,
        "payload": %s
    }
}'''

_ALEXA_ERROR_TEMPLATE = '''{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "ErrorResponse",
            "messageId": "%s",
            "correlationToken": "%s",
            "payloadVersion": "3"
        },
        "payload": {
            "type": "%s",
            "message": "%s"
        }
    }
}'''

_ALEXA_DISCOVERY_TEMPLATE = '''{
    "event": {
        "header": {
            "namespace": "Alexa.Discovery",
            "name": "Discover.Response",
            "messageId": "%s",
            "payloadVersion": "3"
        },
        "payload": {
            "endpoints": %s
        }
    }
}'''

_ALEXA_CHANGE_REPORT_TEMPLATE = '''{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "ChangeReport",
            "messageId": "%s",
            "payloadVersion": "3"
        },
        "endpoint": %s,
        "payload": {
            "change": {
                "cause": {
                    "type": "PHYSICAL_INTERACTION"
                },
                "properties": %s
            }
        }
    }
}'''

_ALEXA_STATE_REPORT_TEMPLATE = '''{
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "StateReport",
            "messageId": "%s",
            "correlationToken": "%s",
            "payloadVersion": "3"
        },
        "endpoint": %s,
        "payload": {},
        "context": {
            "properties": %s
        }
    }
}'''

_USE_ALEXA_TEMPLATES = os.environ.get('USE_ALEXA_TEMPLATES', 'true').lower() == 'true'

@dataclass
class HAResponseStats:
    """Statistics for HA response processing."""
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    avg_processing_time_ms: float = 0.0
    last_response_time: float = 0.0
    template_usage_count: int = 0

class HAResponseProcessor:
    """Home Assistant response processor with Alexa template optimization."""
    
    def __init__(self):
        self._stats = HAResponseStats()
        self.max_response_size_bytes = 512 * 1024
        
    def process_ha_response(self, directive: Dict[str, Any], 
                          response: urllib3.HTTPResponse,
                          response_time_ms: float = None) -> Dict[str, Any]:
        """Process HTTP response from Home Assistant using template optimization."""
        start_time = time.time()
        
        try:
            if response.status != 200:
                return self._create_error_response(
                    directive, 
                    f"HA responded with status {response.status}",
                    "ENDPOINT_UNREACHABLE"
                )
            
            response_data = json.loads(response.data.decode('utf-8'))
            
            directive_header = directive.get('directive', {}).get('header', {})
            namespace = directive_header.get('namespace', 'Alexa')
            name = directive_header.get('name', '')
            
            if namespace == "Alexa.Discovery" and name == "Discover":
                result = self._create_discovery_response(response_data)
            elif namespace == "Alexa" and name == "ReportState":
                result = self._create_state_report_response(directive, response_data)
            else:
                result = self._create_success_response(directive, response_data)
            
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(True, processing_time)
            
            record_request("ha_alexa_response", None)
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(False, processing_time)
            
            record_error(e, "HA_RESPONSE_PROCESSING")
            
            return self._create_error_response(
                directive,
                f"Response processing failed: {str(e)}",
                "INTERNAL_ERROR"
            )
    
    def _create_success_response(self, directive: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Alexa success response using template optimization."""
        try:
            if _USE_ALEXA_TEMPLATES:
                message_id = str(uuid.uuid4())
                correlation_token = directive.get('directive', {}).get('header', {}).get('correlationToken', '')
                
                endpoint_data = self._build_endpoint(directive)
                endpoint_json = json.dumps(endpoint_data)
                
                payload_data = self._build_payload(response_data)
                payload_json = json.dumps(payload_data)
                
                json_response = _ALEXA_RESPONSE_TEMPLATE % (
                    message_id, correlation_token, endpoint_json, payload_json
                )
                
                self._stats.template_usage_count += 1
                return json.loads(json_response)
            else:
                return self._create_success_response_legacy(directive, response_data)
                
        except Exception as e:
            return self._create_success_response_legacy(directive, response_data)
    
    def _create_error_response(self, directive: Dict[str, Any], error_message: str, error_type: str) -> Dict[str, Any]:
        """Create Alexa error response using template optimization."""
        try:
            if _USE_ALEXA_TEMPLATES:
                message_id = str(uuid.uuid4())
                correlation_token = directive.get('directive', {}).get('header', {}).get('correlationToken', '')
                
                json_response = _ALEXA_ERROR_TEMPLATE % (
                    message_id, correlation_token, error_type, error_message
                )
                
                self._stats.template_usage_count += 1
                return json.loads(json_response)
            else:
                return self._create_error_response_legacy(directive, error_message, error_type)
                
        except Exception as e:
            return self._create_error_response_legacy(directive, error_message, error_type)
    
    def _create_discovery_response(self, endpoints_data: List[Dict]) -> Dict[str, Any]:
        """Create Alexa discovery response using template optimization."""
        try:
            if _USE_ALEXA_TEMPLATES:
                message_id = str(uuid.uuid4())
                endpoints_json = json.dumps(endpoints_data)
                
                json_response = _ALEXA_DISCOVERY_TEMPLATE % (
                    message_id, endpoints_json
                )
                
                self._stats.template_usage_count += 1
                return json.loads(json_response)
            else:
                return self._create_discovery_response_legacy(endpoints_data)
                
        except Exception as e:
            return self._create_discovery_response_legacy(endpoints_data)
    
    def _create_state_report_response(self, directive: Dict[str, Any], state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Alexa state report response using template optimization."""
        try:
            if _USE_ALEXA_TEMPLATES:
                message_id = str(uuid.uuid4())
                correlation_token = directive.get('directive', {}).get('header', {}).get('correlationToken', '')
                
                endpoint_data = self._build_endpoint(directive)
                endpoint_json = json.dumps(endpoint_data)
                
                properties = self._extract_context_properties(state_data)
                properties_json = json.dumps(properties)
                
                json_response = _ALEXA_STATE_REPORT_TEMPLATE % (
                    message_id, correlation_token, endpoint_json, properties_json
                )
                
                self._stats.template_usage_count += 1
                return json.loads(json_response)
            else:
                return self._create_state_report_response_legacy(directive, state_data)
                
        except Exception as e:
            return self._create_state_report_response_legacy(directive, state_data)
    
    def _create_success_response_legacy(self, directive: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy dict-based success response creation."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": directive.get('directive', {}).get('header', {}).get('correlationToken', ''),
                    "payloadVersion": "3"
                },
                "endpoint": self._build_endpoint(directive),
                "payload": self._build_payload(response_data)
            }
        }
    
    def _create_error_response_legacy(self, directive: Dict[str, Any], error_message: str, error_type: str) -> Dict[str, Any]:
        """Legacy dict-based error response creation."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": directive.get('directive', {}).get('header', {}).get('correlationToken', ''),
                    "payloadVersion": "3"
                },
                "payload": {
                    "type": error_type,
                    "message": error_message
                }
            }
        }
    
    def _create_discovery_response_legacy(self, endpoints_data: List[Dict]) -> Dict[str, Any]:
        """Legacy dict-based discovery response creation."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa.Discovery",
                    "name": "Discover.Response",
                    "messageId": str(uuid.uuid4()),
                    "payloadVersion": "3"
                },
                "payload": {
                    "endpoints": endpoints_data
                }
            }
        }
    
    def _create_state_report_response_legacy(self, directive: Dict[str, Any], state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy dict-based state report response creation."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "StateReport",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": directive.get('directive', {}).get('header', {}).get('correlationToken', ''),
                    "payloadVersion": "3"
                },
                "endpoint": self._build_endpoint(directive),
                "payload": {},
                "context": {
                    "properties": self._extract_context_properties(state_data)
                }
            }
        }
    
    def _build_endpoint(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Build endpoint data from directive."""
        endpoint = directive.get('directive', {}).get('endpoint', {})
        
        return {
            "scope": {
                "type": "BearerToken",
                "token": endpoint.get('scope', {}).get('token', '')
            },
            "endpointId": endpoint.get('endpointId', 'unknown'),
            "cookie": endpoint.get('cookie', {})
        }
    
    def _build_payload(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build payload from HA response data."""
        return {}
    
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

_ha_response_processor: Optional[HAResponseProcessor] = None

def _get_ha_response_processor() -> HAResponseProcessor:
    """Get HA response processor singleton."""
    global _ha_response_processor
    if _ha_response_processor is None:
        _ha_response_processor = HAResponseProcessor()
    return _ha_response_processor

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
        if not isinstance(entity_ids, list):
            return {
                "success": False,
                "error": "Invalid entity_ids format",
                "timestamp": time.time()
            }
        
        result = {
            "success": True,
            "entity_count": len(entity_ids),
            "states": states_data,
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
    """Get HA response processing statistics."""
    processor = _get_ha_response_processor()
    stats = processor._stats
    
    return {
        "total_responses": stats.total_responses,
        "successful_responses": stats.successful_responses,
        "error_responses": stats.error_responses,
        "success_rate": stats.successful_responses / max(stats.total_responses, 1),
        "avg_processing_time_ms": stats.avg_processing_time_ms,
        "template_usage_count": stats.template_usage_count,
        "template_usage_rate": stats.template_usage_count / max(stats.total_responses, 1),
        "last_response_time": stats.last_response_time
    }
