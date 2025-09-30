"""
http_client_response.py - HTTP Response Processing
Version: 2025.09.30.02
Daily Revision: 002 - Gateway Architecture Compliance

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Uses gateway.py for all operations
- Response processing and transformation
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

import json
import xml.etree.ElementTree as ET
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

def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response using gateway interfaces."""
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
        
        record_metric('response.processed', 1.0, {'format': expected_format})
        
        return create_success_response("Response processed successfully", {
            'parsed_data': sanitized_data,
            'format': expected_format,
            'original_status': response_data.get('status_code')
        })
    
    except Exception as e:
        log_error(f"Response processing failed: {e}")
        return create_error_response(f"Failed to process response: {str(e)}")

def validate_response(response: Dict[str, Any], 
                     validation_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate response against schema."""
    try:
        response_data = response.get('json') or response.get('data') or response
        
        validation_result = validate_request(
            response_data,
            required_fields=validation_schema.get('required', []),
            field_types=validation_schema.get('types', {})
        )
        
        if validation_result.get('success'):
            record_metric('response.validation_passed', 1.0)
        else:
            record_metric('response.validation_failed', 1.0)
        
        return validation_result
    
    except Exception as e:
        log_error(f"Response validation failed: {e}")
        return create_error_response(f"Validation failed: {str(e)}")

def extract_response_data(response: Dict[str, Any],
                         extraction_rules: Dict[str, str]) -> Dict[str, Any]:
    """Extract specific data from response using extraction rules."""
    try:
        extracted_data = {}
        response_data = response.get('json') or response.get('data') or response
        
        for key, path in extraction_rules.items():
            try:
                value = _extract_nested_value(response_data, path)
                extracted_data[key] = value
            except (KeyError, TypeError, IndexError):
                extracted_data[key] = None
        
        return create_success_response("Data extracted successfully", {
            'extracted_data': extracted_data
        })
    
    except Exception as e:
        log_error(f"Data extraction failed: {e}")
        return create_error_response(str(e))

def transform_response(response: Dict[str, Any],
                      transformation_map: Dict[str, str]) -> Dict[str, Any]:
    """Transform response data using transformation map."""
    try:
        response_data = response.get('json') or response.get('data') or response
        transformed_data = {}
        
        for new_key, source_path in transformation_map.items():
            try:
                value = _extract_nested_value(response_data, source_path)
                transformed_data[new_key] = value
            except (KeyError, TypeError, IndexError):
                transformed_data[new_key] = None
        
        return create_success_response("Response transformed successfully", {
            'transformed_data': transformed_data,
            'original_response': response
        })
    
    except Exception as e:
        log_error(f"Response transformation failed: {e}")
        return create_error_response(str(e))

def cache_response(response: Dict[str, Any], cache_key: str, ttl: int = 300,
                  conditions: Optional[Dict[str, Any]] = None) -> bool:
    """Cache response using gateway cache with conditions."""
    try:
        if conditions and not _evaluate_cache_conditions(response, conditions):
            return False
        
        success = cache_set(cache_key, response, ttl)
        
        if success:
            record_metric('response.cached', 1.0)
        
        return success
    
    except Exception as e:
        log_error(f"Response caching failed: {e}")
        return False

def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response using gateway cache."""
    try:
        cached_response = cache_get(cache_key)
        
        if cached_response:
            record_metric('response.cache_hit', 1.0)
        else:
            record_metric('response.cache_miss', 1.0)
        
        return cached_response
    
    except Exception as e:
        log_error(f"Cache retrieval failed: {e}")
        return None

def aggregate_responses(responses: List[Dict[str, Any]],
                       aggregation_type: str = 'merge') -> Dict[str, Any]:
    """Aggregate multiple responses using specified strategy."""
    try:
        if not responses:
            return create_error_response('No responses to aggregate')
        
        if aggregation_type == 'merge':
            return _merge_responses(responses)
        elif aggregation_type == 'array':
            return _array_responses(responses)
        elif aggregation_type == 'latest':
            return _latest_response(responses)
        else:
            return create_error_response(f'Unknown aggregation type: {aggregation_type}')
    
    except Exception as e:
        log_error(f"Response aggregation failed: {e}")
        return create_error_response(str(e))

def _parse_response_format(response_data: Dict[str, Any], expected_format: str) -> Any:
    """Parse response data based on expected format."""
    raw_data = response_data.get('data', '')
    
    if expected_format == 'json':
        if response_data.get('json'):
            return response_data['json']
        elif raw_data:
            try:
                return json.loads(raw_data)
            except json.JSONDecodeError:
                return raw_data
    
    elif expected_format == 'xml':
        if raw_data:
            try:
                root = ET.fromstring(raw_data)
                return _xml_to_dict(root)
            except ET.ParseError:
                return raw_data
    
    elif expected_format == 'text':
        return raw_data
    
    elif expected_format == 'binary':
        return raw_data
    
    return raw_data

def _xml_to_dict(element) -> Dict[str, Any]:
    """Convert XML element to dictionary."""
    result = {element.tag: {} if element.attrib else None}
    children = list(element)
    
    if children:
        dd = {}
        for dc in children:
            child_dict = _xml_to_dict(dc)
            for k, v in child_dict.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        result = {element.tag: dd}
    
    if element.attrib:
        result[element.tag] = {'@attributes': element.attrib}
        if element.text:
            result[element.tag]['#text'] = element.text
    elif element.text:
        result[element.tag] = element.text
    
    return result

def _extract_nested_value(data: Any, path: str) -> Any:
    """Extract nested value using dot notation path."""
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise KeyError(f"Cannot navigate path: {path}")
    
    return current

def _evaluate_cache_conditions(response: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """Evaluate if response meets caching conditions."""
    if not response.get('success', True):
        return False
    
    if 'status_codes' in conditions:
        status_code = response.get('status_code', 0)
        if status_code not in conditions['status_codes']:
            return False
    
    if 'min_size' in conditions:
        size = len(str(response.get('data', '')))
        if size < conditions['min_size']:
            return False
    
    return True

def _merge_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge responses into single response."""
    merged_data = {}
    for response in responses:
        data = response.get('json') or response.get('data') or {}
        if isinstance(data, dict):
            merged_data.update(data)
    
    return create_success_response("Responses merged", {'merged_data': merged_data})

def _array_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate responses as array."""
    array_data = [
        response.get('json') or response.get('data') or response
        for response in responses
    ]
    return create_success_response("Responses aggregated", {'responses': array_data})

def _latest_response(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return latest response."""
    if not responses:
        return create_error_response("No responses available")
    return responses[-1]
