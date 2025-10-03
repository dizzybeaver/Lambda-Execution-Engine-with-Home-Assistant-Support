"""
HTTP Client Response - Response Processing with Template Optimization
Version: 2025.10.02.01
Description: HTTP response processing and transformation with pre-compiled templates

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
import xml.etree.ElementTree as ET
import os
from typing import Dict, Any, Optional, List
import logging

from gateway import (
    validate_request,
    create_success_response, create_error_response,
    sanitize_response_data,
    log_info, log_error,
    cache_get, cache_set,
    record_metric,
    execute_operation, GatewayInterface
)

logger = logging.getLogger(__name__)

# ===== HTTP RESPONSE TEMPLATES (Phase 3 Optimization) =====

_HTTP_SUCCESS_TEMPLATE = '{"success":true,"status_code":%d,"data":%s,"headers":%s}'
_HTTP_ERROR_TEMPLATE = '{"success":false,"status_code":%d,"error":"%s","headers":%s}'
_HTTP_REDIRECT_TEMPLATE = '{"success":true,"status_code":%d,"redirect_url":"%s","headers":%s}'
_HTTP_TIMEOUT_TEMPLATE = '{"success":false,"status_code":408,"error":"Request timeout","timeout_seconds":%d}'
_HTTP_CONNECTION_ERROR_TEMPLATE = '{"success":false,"status_code":0,"error":"Connection failed","details":"%s"}'

_DEFAULT_HEADERS_JSON = '{"Content-Type":"application/json","Cache-Control":"no-cache"}'
_EMPTY_DATA_JSON = '{}'

_USE_HTTP_TEMPLATES = os.environ.get('USE_HTTP_TEMPLATES', 'true').lower() == 'true'

def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response using template optimization."""
    try:
        if _USE_HTTP_TEMPLATES:
            return _process_response_template(response_data, expected_format, validation_rules)
        else:
            return _process_response_legacy(response_data, expected_format, validation_rules)
    except Exception as e:
        log_error(f"Response processing failed: {e}")
        return create_error_response(f"Failed to process response: {str(e)}")

def _process_response_template(response_data: Dict[str, Any], expected_format: str,
                             validation_rules: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Process response using template optimization."""
    try:
        parsed_data = _parse_response_format(response_data, expected_format)
        
        if validation_rules:
            validation_result = validate_request(
                parsed_data,
                required_fields=validation_rules.get('required_fields', []),
                field_types=validation_rules.get('field_types', {})
            )
            
            if not validation_result.get('success'):
                record_metric('response.validation_failed', 1.0)
                return validation_result
        
        sanitized_data = sanitize_response_data(parsed_data)
        status_code = response_data.get('status_code', 200)
        headers = response_data.get('headers', {})
        
        if 200 <= status_code < 300:
            data_json = json.dumps(sanitized_data)
            headers_json = json.dumps(headers) if headers else _DEFAULT_HEADERS_JSON
            
            json_response = _HTTP_SUCCESS_TEMPLATE % (
                status_code, data_json, headers_json
            )
            
            record_metric('response.template_used', 1.0, {'type': 'success'})
            record_metric('response.processed', 1.0, {'format': expected_format})
            
            return json.loads(json_response)
        
        elif 300 <= status_code < 400:
            redirect_url = response_data.get('location', '')
            headers_json = json.dumps(headers) if headers else _DEFAULT_HEADERS_JSON
            
            json_response = _HTTP_REDIRECT_TEMPLATE % (
                status_code, redirect_url, headers_json
            )
            
            record_metric('response.template_used', 1.0, {'type': 'redirect'})
            
            return json.loads(json_response)
        
        else:
            error_message = response_data.get('error', f'HTTP {status_code}')
            headers_json = json.dumps(headers) if headers else _DEFAULT_HEADERS_JSON
            
            json_response = _HTTP_ERROR_TEMPLATE % (
                status_code, error_message, headers_json
            )
            
            record_metric('response.template_used', 1.0, {'type': 'error'})
            
            return json.loads(json_response)
            
    except Exception as e:
        log_error(f"Template response processing failed: {e}")
        return _process_response_legacy(response_data, expected_format, validation_rules)

def _process_response_legacy(response_data: Dict[str, Any], expected_format: str,
                           validation_rules: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Legacy dict-based response processing."""
    parsed_data = _parse_response_format(response_data, expected_format)
    
    if validation_rules:
        validation_result = validate_request(
            parsed_data,
            required_fields=validation_rules.get('required_fields', []),
            field_types=validation_rules.get('field_types', {})
        )
        
        if not validation_result.get('success'):
            record_metric('response.validation_failed', 1.0)
            return validation_result
    
    sanitized_data = sanitize_response_data(parsed_data)
    
    record_metric('response.processed', 1.0, {'format': expected_format})
    
    return create_success_response("Response processed successfully", {
        'parsed_data': sanitized_data,
        'format': expected_format,
        'original_status': response_data.get('status_code')
    })

def create_timeout_response(timeout_seconds: int) -> Dict[str, Any]:
    """Create timeout response using template optimization."""
    try:
        if _USE_HTTP_TEMPLATES:
            json_response = _HTTP_TIMEOUT_TEMPLATE % timeout_seconds
            record_metric('response.template_used', 1.0, {'type': 'timeout'})
            return json.loads(json_response)
        else:
            return {
                "success": False,
                "status_code": 408,
                "error": "Request timeout",
                "timeout_seconds": timeout_seconds
            }
    except Exception as e:
        log_error(f"Timeout response creation failed: {e}")
        return create_error_response("Request timeout")

def create_connection_error_response(error_details: str) -> Dict[str, Any]:
    """Create connection error response using template optimization."""
    try:
        if _USE_HTTP_TEMPLATES:
            json_response = _HTTP_CONNECTION_ERROR_TEMPLATE % error_details
            record_metric('response.template_used', 1.0, {'type': 'connection_error'})
            return json.loads(json_response)
        else:
            return {
                "success": False,
                "status_code": 0,
                "error": "Connection failed",
                "details": error_details
            }
    except Exception as e:
        log_error(f"Connection error response creation failed: {e}")
        return create_error_response("Connection failed")

def validate_response(response: Dict[str, Any], 
                     validation_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate response against schema."""
    try:
        validation_result = validate_request(
            response,
            required_fields=validation_schema.get('required_fields', []),
            field_types=validation_schema.get('field_types', {})
        )
        
        record_metric('response.validation_attempted', 1.0)
        
        if validation_result.get('success'):
            record_metric('response.validation_success', 1.0)
        else:
            record_metric('response.validation_failed', 1.0)
        
        return validation_result
        
    except Exception as e:
        log_error(f"Response validation failed: {e}")
        return create_error_response(f"Validation error: {str(e)}")

def extract_response_data(response: Dict[str, Any], extraction_path: str) -> Any:
    """Extract specific data from response using dot notation path."""
    try:
        current_data = response
        path_parts = extraction_path.split('.')
        
        for part in path_parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            elif isinstance(current_data, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current_data):
                    current_data = current_data[index]
                else:
                    return None
            else:
                return None
        
        record_metric('response.data_extracted', 1.0)
        return current_data
        
    except Exception as e:
        log_error(f"Data extraction failed: {e}")
        return None

def transform_response(response: Dict[str, Any], 
                      transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply transformations to response data."""
    try:
        transformed_data = response.copy()
        
        for transformation in transformations:
            transform_type = transformation.get('type')
            
            if transform_type == 'rename_field':
                old_name = transformation.get('from')
                new_name = transformation.get('to')
                if old_name in transformed_data:
                    transformed_data[new_name] = transformed_data.pop(old_name)
            
            elif transform_type == 'convert_type':
                field_name = transformation.get('field')
                target_type = transformation.get('target_type')
                if field_name in transformed_data:
                    try:
                        if target_type == 'int':
                            transformed_data[field_name] = int(transformed_data[field_name])
                        elif target_type == 'float':
                            transformed_data[field_name] = float(transformed_data[field_name])
                        elif target_type == 'str':
                            transformed_data[field_name] = str(transformed_data[field_name])
                    except (ValueError, TypeError):
                        log_error(f"Type conversion failed for field {field_name}")
            
            elif transform_type == 'add_field':
                field_name = transformation.get('field')
                field_value = transformation.get('value')
                transformed_data[field_name] = field_value
        
        record_metric('response.transformed', 1.0, {'transform_count': len(transformations)})
        return create_success_response("Response transformed", transformed_data)
        
    except Exception as e:
        log_error(f"Response transformation failed: {e}")
        return create_error_response(f"Transformation error: {str(e)}")

def _parse_response_format(response_data: Dict[str, Any], expected_format: str) -> Any:
    """Parse response data based on expected format."""
    try:
        raw_data = response_data.get('data', response_data.get('body', ''))
        
        if expected_format.lower() == 'json':
            if isinstance(raw_data, str):
                return json.loads(raw_data)
            elif isinstance(raw_data, dict):
                return raw_data
            else:
                return {'raw_data': raw_data}
        
        elif expected_format.lower() == 'xml':
            if isinstance(raw_data, str):
                root = ET.fromstring(raw_data)
                return _xml_to_dict(root)
            else:
                return {'raw_data': raw_data}
        
        elif expected_format.lower() == 'text':
            return {'text': str(raw_data)}
        
        else:
            return {'raw_data': raw_data}
    
    except json.JSONDecodeError as e:
        log_error(f"JSON parsing failed: {e}")
        return {'parse_error': str(e), 'raw_data': raw_data}
    
    except ET.ParseError as e:
        log_error(f"XML parsing failed: {e}")
        return {'parse_error': str(e), 'raw_data': raw_data}
    
    except Exception as e:
        log_error(f"Format parsing failed: {e}")
        return {'parse_error': str(e), 'raw_data': raw_data}

def _xml_to_dict(element) -> Dict[str, Any]:
    """Convert XML element to dictionary."""
    result = {}
    
    if element.text and element.text.strip():
        result['text'] = element.text.strip()
    
    for attr_name, attr_value in element.attrib.items():
        result[f'@{attr_name}'] = attr_value
    
    for child in element:
        child_data = _xml_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    
    return result

def cache_response(cache_key: str, response: Dict[str, Any], ttl: int = 300) -> bool:
    """Cache response data."""
    try:
        cache_set(cache_key, response, ttl)
        record_metric('response.cached', 1.0)
        return True
    except Exception as e:
        log_error(f"Response caching failed: {e}")
        return False

def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response data."""
    try:
        cached_data = cache_get(cache_key)
        if cached_data:
            record_metric('response.cache_hit', 1.0)
            return cached_data
        else:
            record_metric('response.cache_miss', 1.0)
            return None
    except Exception as e:
        log_error(f"Cache retrieval failed: {e}")
        record_metric('response.cache_error', 1.0)
        return None

def get_response_stats() -> Dict[str, Any]:
    """Get response processing statistics."""
    try:
        return execute_operation(
            GatewayInterface.METRICS,
            "get_metrics_summary",
            metric_prefix="response"
        )
    except Exception as e:
        log_error(f"Failed to get response stats: {e}")
        return {}
