"""
http_client_response.py - HTTP Response Processing
Version: 2025.09.24.01
Description: HTTP response processing and transformation using gateway interfaces

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Response parsing and validation using utility.py
- Error handling using security.py validation
- Metrics collection using metrics.py
- Response caching using cache.py

PRIMARY FILE: http_client.py (interface)
SECONDARY FILE: http_client_response.py (response processing)

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
from typing import Dict, Any, Optional, Union, List
import logging

# Gateway imports
from . import utility
from . import security
from . import metrics
from . import cache

logger = logging.getLogger(__name__)

# ===== RESPONSE PROCESSING FUNCTIONS =====

def process_response(response_data: Dict[str, Any],
                    expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response using gateway interfaces."""
    
    try:
        # Use utility.py for response validation if available
        if hasattr(utility, 'validate_response'):
            validation_result = utility.validate_response(response_data)
            if not validation_result.get('valid', True):
                return {
                    'success': False,
                    'error': f'Response validation failed: {validation_result.get("error")}',
                    'original_response': response_data
                }
        
        # Parse response based on expected format
        parsed_response = _parse_response_format(response_data, expected_format)
        
        # Apply validation rules if provided
        if validation_rules:
            validation_result = security.validate_request({
                'response_data': parsed_response,
                'validation_rules': validation_rules
            })
            
            if not validation_result.is_valid:
                return {
                    'success': False,
                    'error': f'Response validation failed: {validation_result.error_message}',
                    'original_response': response_data
                }
        
        # Record response metrics
        metrics.increment_counter('response.processed')
        metrics.record_value('response.size', len(str(parsed_response)))
        
        return {
            'success': True,
            'processed_data': parsed_response,
            'format': expected_format,
            'original_response': response_data
        }
        
    except Exception as e:
        logger.error(f"Response processing failed: {e}")
        metrics.increment_counter('response.processing_error')
        return {
            'success': False,
            'error': str(e),
            'original_response': response_data
        }

def extract_response_data(response: Dict[str, Any],
                         extraction_rules: Dict[str, str]) -> Dict[str, Any]:
    """Extract specific data from response using rules."""
    
    try:
        extracted_data = {}
        response_data = response.get('json') or response.get('data') or response
        
        for key, path in extraction_rules.items():
            try:
                value = _extract_nested_value(response_data, path)
                extracted_data[key] = value
            except (KeyError, TypeError, IndexError):
                extracted_data[key] = None
        
        return {
            'success': True,
            'extracted_data': extracted_data
        }
        
    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

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
        
        return {
            'success': True,
            'transformed_data': transformed_data,
            'original_response': response
        }
        
    except Exception as e:
        logger.error(f"Response transformation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'original_response': response
        }

# ===== RESPONSE CACHING FUNCTIONS =====

def cache_response(response: Dict[str, Any],
                  cache_key: str,
                  ttl: int = 300,
                  conditions: Optional[Dict[str, Any]] = None) -> bool:
    """Cache response using cache.py gateway with conditions."""
    
    try:
        # Check caching conditions
        if conditions:
            if not _evaluate_cache_conditions(response, conditions):
                return False
        
        # Use cache.py for response caching
        success = cache.cache_set(cache_key, response, ttl)
        
        if success:
            metrics.increment_counter('response.cached')
        
        return success
        
    except Exception as e:
        logger.error(f"Response caching failed: {e}")
        return False

def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response using cache.py gateway."""
    
    try:
        cached_response = cache.cache_get(cache_key)
        
        if cached_response:
            metrics.increment_counter('response.cache_hit')
        else:
            metrics.increment_counter('response.cache_miss')
        
        return cached_response
        
    except Exception as e:
        logger.error(f"Cache retrieval failed: {e}")
        return None

# ===== RESPONSE AGGREGATION FUNCTIONS =====

def aggregate_responses(responses: List[Dict[str, Any]],
                       aggregation_type: str = 'merge') -> Dict[str, Any]:
    """Aggregate multiple responses using specified strategy."""
    
    try:
        if not responses:
            return {'success': False, 'error': 'No responses to aggregate'}
        
        if aggregation_type == 'merge':
            return _merge_responses(responses)
        elif aggregation_type == 'array':
            return _array_responses(responses)
        elif aggregation_type == 'latest':
            return _latest_response(responses)
        else:
            return {'success': False, 'error': f'Unknown aggregation type: {aggregation_type}'}
        
    except Exception as e:
        logger.error(f"Response aggregation failed: {e}")
        return {'success': False, 'error': str(e)}

# ===== HELPER FUNCTIONS =====

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
    
    result = {}
    
    # Add attributes
    if element.attrib:
        result.update(element.attrib)
    
    # Add text content
    if element.text and element.text.strip():
        if len(element) == 0:
            return element.text.strip()
        result['text'] = element.text.strip()
    
    # Add child elements
    for child in element:
        child_data = _xml_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    
    return result

def _extract_nested_value(data: Any, path: str) -> Any:
    """Extract nested value using dot notation path."""
    
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                current = current[index]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid list index: {key}")
        else:
            raise TypeError(f"Cannot access key '{key}' on type {type(current)}")
    
    return current

def _evaluate_cache_conditions(response: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """Evaluate whether response meets caching conditions."""
    
    # Check status code condition
    if 'status_code' in conditions:
        required_status = conditions['status_code']
        actual_status = response.get('status_code', 0)
        if actual_status != required_status:
            return False
    
    # Check success condition
    if 'success' in conditions:
        required_success = conditions['success']
        actual_success = response.get('success', False)
        if actual_success != required_success:
            return False
    
    # Check data size condition
    if 'max_size' in conditions:
        max_size = conditions['max_size']
        response_size = len(str(response))
        if response_size > max_size:
            return False
    
    return True

def _merge_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple responses into single response."""
    
    merged = {
        'success': all(r.get('success', False) for r in responses),
        'merged_data': {},
        'source_count': len(responses)
    }
    
    for response in responses:
        data = response.get('json') or response.get('data') or {}
        if isinstance(data, dict):
            merged['merged_data'].update(data)
    
    return merged

def _array_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine responses into array format."""
    
    return {
        'success': True,
        'data': [r.get('json') or r.get('data') for r in responses],
        'source_count': len(responses)
    }

def _latest_response(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return the latest response based on timestamp."""
    
    if not responses:
        return {'success': False, 'error': 'No responses provided'}
    
    # Sort by timestamp if available, otherwise return last in list
    sorted_responses = sorted(responses, 
                             key=lambda r: r.get('timestamp', 0), 
                             reverse=True)
    
    latest = sorted_responses[0]
    latest['aggregation_type'] = 'latest'
    
    return latest

# EOF
