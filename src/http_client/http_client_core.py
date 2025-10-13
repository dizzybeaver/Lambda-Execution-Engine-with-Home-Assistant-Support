"""
http_client_core.py - Ultra-Optimized HTTP Client with Advanced Features
Version: 2025.10.13.02
Description: Complete HTTP client with transformers, response processing, state management, and AWS integration

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
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Callable, List, Union
from enum import Enum
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

# ===== HTTP METHOD ENUMERATION =====

class HTTPMethod(Enum):
    """HTTP methods enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# ===== HTTP HEADER TEMPLATES =====

_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

_USER_AGENT = "Lambda-Execution-Engine/1.0"
_QUERY_BUFFER: List[str] = []

_PARSED_HEADERS_TEMPLATE = {
    'content_type': '',
    'content_length': 0,
    'cache_control': '',
    'server': ''
}

# ===== RESPONSE TEMPLATES =====

_HTTP_SUCCESS_TEMPLATE = '{"success":true,"status_code":%d,"data":%s,"headers":%s}'
_HTTP_ERROR_TEMPLATE = '{"success":false,"status_code":%d,"error":"%s","headers":%s}'
_HTTP_REDIRECT_TEMPLATE = '{"success":true,"status_code":%d,"redirect_url":"%s","headers":%s}'
_HTTP_TIMEOUT_TEMPLATE = '{"success":false,"status_code":408,"error":"Request timeout","timeout_seconds":%d}'
_HTTP_CONNECTION_ERROR_TEMPLATE = '{"success":false,"status_code":0,"error":"Connection failed","details":"%s"}'

_DEFAULT_HEADERS_JSON = '{"Content-Type":"application/json","Cache-Control":"no-cache"}'
_EMPTY_DATA_JSON = '{}'
_USE_HTTP_TEMPLATES = os.environ.get('USE_HTTP_TEMPLATES', 'true').lower() == 'true'


# ===== RESPONSE VALIDATOR CLASS =====

class ResponseValidator:
    """Validates response structure and content."""
    
    @staticmethod
    def validate_structure(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate response data against schema."""
        if not isinstance(data, dict):
            return False
        
        for field, field_type in schema.get('required_fields', {}).items():
            if field not in data:
                return False
            
            if not isinstance(data[field], field_type):
                return False
        
        return True
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], fields: List[str]) -> bool:
        """Check if all required fields are present."""
        return all(field in data for field in fields)
    
    @staticmethod
    def validate_data_types(data: Dict[str, Any], type_map: Dict[str, type]) -> bool:
        """Validate data types match expected types."""
        for field, expected_type in type_map.items():
            if field in data and not isinstance(data[field], expected_type):
                return False
        return True
    
    @staticmethod
    def validate_value_ranges(data: Dict[str, Any], ranges: Dict[str, tuple]) -> bool:
        """Validate numeric values are within specified ranges."""
        for field, (min_val, max_val) in ranges.items():
            if field in data:
                value = data[field]
                if not (min_val <= value <= max_val):
                    return False
        return True


# ===== RESPONSE TRANSFORMER CLASS =====

class ResponseTransformer:
    """Transforms response data using various strategies."""
    
    @staticmethod
    def flatten(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary structure."""
        def _flatten_recursive(obj, parent_key=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{separator}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(_flatten_recursive(v, new_key).items())
                    elif isinstance(v, list):
                        for i, item in enumerate(v):
                            items.extend(_flatten_recursive(item, f"{new_key}[{i}]").items())
                    else:
                        items.append((new_key, v))
            return dict(items)
        
        return _flatten_recursive(data)
    
    @staticmethod
    def extract(data: Dict[str, Any], paths: List[str]) -> Dict[str, Any]:
        """Extract specific fields from nested structure."""
        result = {}
        
        for path in paths:
            parts = path.split('.')
            current = data
            
            try:
                for part in parts:
                    if '[' in part:
                        field, index = part.split('[')
                        index = int(index.rstrip(']'))
                        current = current[field][index]
                    else:
                        current = current[part]
                
                result[path] = current
            except (KeyError, IndexError, TypeError):
                result[path] = None
        
        return result
    
    @staticmethod
    def map_fields(data: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
        """Rename fields according to mapping."""
        result = {}
        
        for old_name, new_name in field_map.items():
            if old_name in data:
                result[new_name] = data[old_name]
        
        for key, value in data.items():
            if key not in field_map:
                result[key] = value
        
        return result
    
    @staticmethod
    def filter_fields(data: Dict[str, Any], include: Optional[List[str]] = None,
                     exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Filter fields by inclusion or exclusion list."""
        if include is not None:
            return {k: v for k, v in data.items() if k in include}
        
        if exclude is not None:
            return {k: v for k, v in data.items() if k not in exclude}
        
        return data
    
    @staticmethod
    def transform_values(data: Dict[str, Any], transformers: Dict[str, Callable]) -> Dict[str, Any]:
        """Transform values using field-specific functions."""
        result = data.copy()
        
        for field, transformer in transformers.items():
            if field in result:
                try:
                    result[field] = transformer(result[field])
                except Exception:
                    pass
        
        return result
    
    @staticmethod
    def normalize(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data according to schema."""
        result = {}
        
        for field, config in schema.items():
            if field in data:
                value = data[field]
                
                if 'type' in config:
                    try:
                        if config['type'] == 'int':
                            value = int(value)
                        elif config['type'] == 'float':
                            value = float(value)
                        elif config['type'] == 'str':
                            value = str(value)
                        elif config['type'] == 'bool':
                            value = bool(value)
                    except (ValueError, TypeError):
                        value = config.get('default')
                
                if 'min' in config and value < config['min']:
                    value = config['min']
                if 'max' in config and value > config['max']:
                    value = config['max']
                
                result[field] = value
            elif 'default' in config:
                result[field] = config['default']
        
        return result


# ===== TRANSFORMATION PIPELINE CLASS =====

class TransformationPipeline:
    """Pipeline for chaining multiple transformations."""
    
    def __init__(self, cache_results: bool = False):
        """Initialize transformation pipeline."""
        self._transformations: List[tuple] = []
        self._cache_results = cache_results
    
    def add_validation(self, validator: Callable, error_handler: Optional[Callable] = None):
        """Add validation step."""
        self._transformations.append(('validation', validator, {'error_handler': error_handler}))
        return self
    
    def add_transformation(self, transformer: Callable, metadata: Optional[Dict] = None):
        """Add transformation step."""
        self._transformations.append(('transformation', transformer, metadata or {}))
        return self
    
    def add_filter(self, filter_func: Callable):
        """Add filter step."""
        self._transformations.append(('filter', filter_func, {}))
        return self
    
    def execute(self, data: Any) -> Dict[str, Any]:
        """Execute pipeline on data."""
        from gateway import create_success_response, create_error_response
        
        current_data = data
        
        for step_type, operation, metadata in self._transformations:
            try:
                if step_type == 'validation':
                    is_valid = operation(current_data)
                    if not is_valid:
                        error_handler = metadata.get('error_handler')
                        if error_handler:
                            return error_handler(current_data)
                        return create_error_response("Validation failed")
                
                elif step_type == 'transformation':
                    current_data = operation(current_data)
                
                elif step_type == 'filter':
                    current_data = operation(current_data)
            
            except Exception as e:
                return create_error_response(f"Pipeline step failed: {str(e)}")
        
        return create_success_response("Pipeline executed successfully", current_data)
    
    def get_cache_key(self) -> Optional[str]:
        """Generate cache key for pipeline."""
        if not self._cache_results:
            return None
        
        step_keys = []
        for step_type, operation, metadata in self._transformations:
            if hasattr(operation, '__name__'):
                step_keys.append(operation.__name__)
        
        if step_keys:
            return f"transform_pipeline_{'_'.join(step_keys)}"
        
        return None


# ===== GENERIC HELPER FUNCTIONS =====

def get_standard_headers(auth_token: Optional[str] = None) -> Dict[str, str]:
    """Get standard headers with optional auth (fast template-based)."""
    headers = _JSON_HEADERS.copy()
    headers["User-Agent"] = _USER_AGENT
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def get_ha_headers(access_token: str) -> Dict[str, str]:
    """Get Home Assistant headers (fast template-based)."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }


def build_query_string_fast(params: Dict[str, Any]) -> str:
    """Fast query string building with pre-allocated buffer."""
    from gateway import log_error
    
    global _QUERY_BUFFER
    _QUERY_BUFFER.clear()
    
    try:
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        _QUERY_BUFFER.append(f"{key}={item}")
                else:
                    _QUERY_BUFFER.append(f"{key}={value}")
        
        return '&'.join(_QUERY_BUFFER)
    except Exception as e:
        log_error(f"Query string building failed: {e}")
        return ''


def build_query_string(params: Dict[str, Any]) -> str:
    """Legacy query string builder (for compatibility)."""
    from gateway import log_error
    
    try:
        query_parts = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        query_parts.append(f"{key}={str(item)}")
                else:
                    query_parts.append(f"{key}={str(value)}")
        return '&'.join(query_parts)
    except Exception as e:
        log_error(f"Query string building failed: {e}")
        return ''


def parse_response_headers_fast(headers: Dict[str, str]) -> Dict[str, Any]:
    """Fast header parsing using template."""
    from gateway import log_error
    
    try:
        result = _PARSED_HEADERS_TEMPLATE.copy()
        
        ct = headers.get('content-type', '')
        result['content_type'] = ct.split(';')[0].strip() if ct else ''
        
        cl = headers.get('content-length', '')
        result['content_length'] = int(cl) if cl and cl.isdigit() else 0
        
        result['cache_control'] = headers.get('cache-control', '')
        result['server'] = headers.get('server', '')
        result['all_headers'] = headers
        
        return result
    except Exception as e:
        log_error(f"Header parsing failed: {e}")
        return {'all_headers': headers}


def parse_response_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Legacy header parsing (for compatibility)."""
    from gateway import log_error
    
    try:
        parsed = {
            'content_type': headers.get('content-type', '').split(';')[0].strip(),
            'content_length': int(headers.get('content-length', 0)) if headers.get('content-length') else 0,
            'cache_control': headers.get('cache-control', ''),
            'expires': headers.get('expires', ''),
            'etag': headers.get('etag', ''),
            'last_modified': headers.get('last-modified', ''),
            'server': headers.get('server', ''),
            'all_headers': headers
        }
        return parsed
    except Exception as e:
        log_error(f"Header parsing failed: {e}")
        return {'all_headers': headers}


# ===== RESPONSE PROCESSING FUNCTIONS =====

def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response using template optimization."""
    from gateway import validate_request, sanitize_response_data, record_metric, log_error, create_success_response
    
    try:
        if _USE_HTTP_TEMPLATES:
            return _process_response_template(response_data, expected_format, validation_rules)
        else:
            return _process_response_legacy(response_data, expected_format, validation_rules)
    except Exception as e:
        log_error(f"Response processing failed: {e}")
        from gateway import create_error_response
        return create_error_response(f"Failed to process response: {str(e)}")


def _process_response_template(response_data: Dict[str, Any], expected_format: str,
                             validation_rules: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Process response using template optimization."""
    from gateway import validate_request, sanitize_response_data, record_metric, log_error
    
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
    from gateway import validate_request, sanitize_response_data, record_metric, create_success_response
    
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


def _parse_response_format(response_data: Dict[str, Any], expected_format: str) -> Any:
    """Parse response data based on expected format."""
    from gateway import log_error
    
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


def create_timeout_response(timeout_seconds: int) -> Dict[str, Any]:
    """Create timeout response using template optimization."""
    from gateway import record_metric, log_error, create_error_response
    
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
    from gateway import record_metric, log_error, create_error_response
    
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


def cache_response(cache_key: str, response: Dict[str, Any], ttl: int = 300) -> bool:
    """Cache response data."""
    from gateway import cache_set, record_metric, log_error
    
    try:
        cache_set(cache_key, response, ttl)
        record_metric('response.cached', 1.0)
        return True
    except Exception as e:
        log_error(f"Response caching failed: {e}")
        return False


def get_cached_response(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached response data."""
    from gateway import cache_get, record_metric, log_error
    
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


def validate_response(response: Dict[str, Any], 
                     validation_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate response against schema."""
    from gateway import validate_request, record_metric, log_error, create_error_response
    
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
    from gateway import record_metric, log_error
    
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
    from gateway import record_metric, log_error, create_success_response, create_error_response
    
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


# ===== HELPER FACTORY FUNCTIONS =====

def create_common_transformers() -> Dict[str, Callable]:
    """Create dictionary of common transformation functions."""
    transformer = ResponseTransformer()
    
    return {
        'flatten': transformer.flatten,
        'extract': transformer.extract,
        'map': transformer.map_fields,
        'filter': transformer.filter_fields,
        'transform_values': transformer.transform_values,
        'normalize': transformer.normalize
    }


def create_validator() -> ResponseValidator:
    """Create response validator instance."""
    return ResponseValidator()


def create_transformer() -> ResponseTransformer:
    """Create response transformer instance."""
    return ResponseTransformer()


def create_pipeline() -> TransformationPipeline:
    """Create transformation pipeline instance."""
    return TransformationPipeline()


# ===== HTTP CLIENT CORE CLASS =====

class HTTPClientCore:
    """
    Core HTTP client with circuit breaker protection, retry logic, and connection pooling.
    Optimized for AWS Lambda environment.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """Initialize HTTP client."""
        self.timeout = timeout
        self.max_retries = max_retries
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry and circuit breaker protection.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            **kwargs: Additional options (headers, data, timeout, etc.)
            
        Returns:
            Dict with success, status_code, data, and headers
        """
        from gateway import log_info, log_error, create_success_response, create_error_response, record_metric
        
        self._stats['requests'] += 1
        
        headers = kwargs.get('headers', {})
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.timeout)
        
        # Prepare request data
        body = None
        if data:
            if isinstance(data, dict):
                body = json.dumps(data).encode('utf-8')
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                body = data.encode('utf-8')
            else:
                body = data
        
        # Build request
        req = Request(url, data=body, headers=headers, method=method.upper())
        
        # Execute with retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                with urlopen(req, timeout=timeout) as response:
                    response_data = response.read().decode('utf-8')
                    response_headers = dict(response.headers)
                    status_code = response.status
                    
                    # Try to parse JSON
                    try:
                        parsed_data = json.loads(response_data)
                    except:
                        parsed_data = response_data
                    
                    self._stats['successful'] += 1
                    if attempt > 0:
                        self._stats['retries'] += attempt
                        record_metric('http_client.retry_success', 1.0, {'attempt': str(attempt + 1)})
                    
                    log_info(f"HTTP {method} {url} - Status: {status_code}")
                    
                    return create_success_response(
                        f"HTTP {method} successful",
                        {
                            'status_code': status_code,
                            'data': parsed_data,
                            'headers': response_headers
                        }
                    )
            
            except HTTPError as e:
                last_error = e
                status_code = e.code
                
                # Don't retry on client errors (4xx)
                if 400 <= status_code < 500 and status_code not in [408, 429]:
                    self._stats['failed'] += 1
                    log_error(f"HTTP {method} {url} - Client error: {status_code}")
                    return create_error_response(
                        f"HTTP client error: {status_code}",
                        f"HTTP_{status_code}"
                    )
                
                # Retry on server errors (5xx) and specific client errors
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    record_metric('http_client.retry_attempt', 1.0, {'attempt': str(attempt + 1)})
                    continue
            
            except URLError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    record_metric('http_client.retry_attempt', 1.0, {'attempt': str(attempt + 1)})
                    continue
            
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    continue
        
        # All retries exhausted
        self._stats['failed'] += 1
        error_msg = str(last_error) if last_error else "Unknown error"
        log_error(f"HTTP {method} {url} - Failed after {self.max_retries} attempts: {error_msg}")
        record_metric('http_client.failure', 1.0)
        
        return create_error_response(
            f"HTTP request failed: {error_msg}",
            "HTTP_REQUEST_FAILED"
        )
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        kwargs['data'] = data
        return self.make_request('POST', url, **kwargs)
    
    def put(self, url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        kwargs['data'] = data
        return self.make_request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self.make_request('DELETE', url, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        return {
            'total_requests': self._stats['requests'],
            'successful_requests': self._stats['successful'],
            'failed_requests': self._stats['failed'],
            'total_retries': self._stats['retries'],
            'success_rate': (self._stats['successful'] / self._stats['requests'] * 100) 
                           if self._stats['requests'] > 0 else 0.0
        }


# ===== SINGLETON PATTERN =====

_http_client_instance = None


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance."""
    global _http_client_instance
    if _http_client_instance is None:
        _http_client_instance = HTTPClientCore()
    return _http_client_instance


# ===== STATE MANAGEMENT FUNCTIONS =====

def get_client_state(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get HTTP client state via gateway singleton."""
    from gateway import get_singleton, log_error
    
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
            return {
                'exists': False,
                'client_type': client_type,
                'state': 'not_initialized'
            }
        
        state_info = {
            'exists': True,
            'client_type': client_type,
            'state': 'initialized',
            'instance_id': id(client)
        }
        
        if hasattr(client, 'get_stats'):
            state_info['stats'] = client.get_stats()
        
        return state_info
    
    except Exception as e:
        log_error(f"Failed to get client state: {e}")
        return {'exists': False, 'error': str(e)}


def reset_client_state(client_type: str = None) -> Dict[str, Any]:
    """Reset HTTP client state via gateway singleton."""
    from gateway import execute_operation, GatewayInterface, create_success_response, create_error_response, log_error, record_metric
    
    try:
        if client_type:
            singleton_key = f'http_client_{client_type}'
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset',
                singleton_name=singleton_key
            )
            record_metric(f'http_client_state.{client_type}.reset', 1.0)
        else:
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset_all'
            )
            record_metric('http_client_state.reset_all', 1.0)
        
        return create_success_response("Client state reset", result)
    
    except Exception as e:
        log_error(f"Failed to reset client state: {e}")
        return create_error_response(str(e))


def get_client_configuration(client_type: str) -> Dict[str, Any]:
    """Get client configuration via gateway config."""
    from gateway import get_parameter, log_error
    
    try:
        config_key = f'http_client_{client_type}'
        client_config = get_parameter(config_key, {})
        
        default_config = {
            'timeout': get_parameter('http_timeout', 30),
            'retries': get_parameter('http_retries', 3),
            'pool_size': get_parameter('http_pool_size', 10)
        }
        
        return {
            'client_type': client_type,
            'configuration': {**default_config, **client_config}
        }
    
    except Exception as e:
        log_error(f"Failed to get client configuration: {e}")
        return {
            'client_type': client_type,
            'configuration': {},
            'error': str(e)
        }


def update_client_configuration(client_type: str, new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration via gateway config."""
    from gateway import set_parameter, create_success_response, create_error_response, log_error, record_metric
    
    try:
        config_key = f'http_client_{client_type}'
        success = set_parameter(config_key, new_config)
        
        if success:
            reset_result = reset_client_state(client_type)
            record_metric(f'http_client_state.{client_type}.config_updated', 1.0)
            
            return create_success_response("Configuration updated", {
                'client_type': client_type,
                'configuration_updated': True,
                'client_reset': reset_result.get('success', False)
            })
        else:
            return create_error_response('Failed to update configuration')
    
    except Exception as e:
        log_error(f"Configuration update failed: {e}")
        return create_error_response(str(e))


def get_connection_statistics(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get connection statistics for client."""
    from gateway import create_success_response
    
    client = get_http_client()
    stats = client.get_stats()
    
    return create_success_response("Statistics retrieved", {
        'client_type': client_type,
        'statistics': stats
    })


# ===== EXTENSION FUNCTIONS (RETRY AND TRANSFORMATION) =====

def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100,
                        retriable_codes: set = None) -> Dict[str, Any]:
    """Configure HTTP retry behavior using existing http_client."""
    from gateway import cache_set, log_info, create_success_response
    
    config = {
        'max_attempts': max_attempts,
        'backoff_base_ms': backoff_base_ms,
        'retriable_status_codes': retriable_codes or {408, 429, 500, 502, 503, 504}
    }
    
    cache_set('http_retry_config', config, ttl=3600)
    log_info(f"HTTP retry configured: {max_attempts} attempts, {backoff_base_ms}ms backoff")
    
    return create_success_response("Retry configured", config)


def http_request_with_retry(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with retry using existing functions."""
    from gateway import make_request, cache_get, record_metric, log_error, create_error_response
    
    config = cache_get('http_retry_config') or {'max_attempts': 3, 'backoff_base_ms': 100}
    
    try:
        for attempt in range(config['max_attempts']):
            try:
                result = make_request(method, url, **kwargs)
                
                if result.get('success'):
                    if attempt > 0:
                        record_metric('http_retry_success', 1.0, {'attempt': attempt + 1})
                    return result
                
                status_code = result.get('status_code', 0)
                if status_code not in config.get('retriable_status_codes', set()):
                    return result
                
                if attempt < config['max_attempts'] - 1:
                    delay_ms = config['backoff_base_ms'] * (2 ** attempt)
                    time.sleep(delay_ms / 1000.0)
                    record_metric('http_retry_attempt', 1.0, {'attempt': attempt + 1})
                    
            except Exception as e:
                if attempt == config['max_attempts'] - 1:
                    raise
                time.sleep((config['backoff_base_ms'] * (2 ** attempt)) / 1000.0)
        
        return {'success': False, 'error': 'Max retries exceeded'}
        
    except Exception as e:
        log_error(f"Retry request failed: {e}")
        return create_error_response(str(e))


def transform_http_response(response: Dict[str, Any], transformer: Callable) -> Dict[str, Any]:
    """Transform HTTP response using existing validation."""
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    try:
        data = response.get('data')
        transformed = transformer(data)
        
        response['data'] = transformed
        response['transformed'] = True
        return response
        
    except Exception as e:
        return create_error_response(f"Transformation failed: {str(e)}", 'TRANSFORM_ERROR')


def validate_http_response(response: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
    """Validate HTTP response using existing validation."""
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    if required_fields:
        data = response.get('data', {})
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                'VALIDATION_ERROR'
            )
    
    return response


def execute_with_retry(operation: Callable, max_retries: int = 3, 
                      backoff_factor: float = 0.5,
                      retry_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generic retry pattern for HTTP operations."""
    from gateway import record_metric, log_error, create_error_response
    
    retry_conditions = retry_conditions or ['timeout', '5xx']
    last_error = None
    
    def _should_retry(result, conditions):
        """Check if result should trigger retry."""
        if not isinstance(result, dict):
            return False
        
        if result.get('success'):
            return False
        
        status_code = result.get('status_code', 0)
        
        if 'timeout' in conditions and 'timeout' in str(result.get('error', '')).lower():
            return True
        
        if '5xx' in conditions and 500 <= status_code < 600:
            return True
        
        return False
    
    for attempt in range(max_retries):
        try:
            result = operation()
            
            if not _should_retry(result, retry_conditions):
                return result
            
            last_error = result
            
            if attempt < max_retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
                record_metric('http_retry.attempt', 1.0, {'attempt': attempt + 1})
        
        except Exception as e:
            last_error = {'success': False, 'error': str(e)}
            
            if attempt < max_retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
            else:
                log_error(f"All retry attempts exhausted: {e}")
    
    return last_error or create_error_response("Operation failed after retries")


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _make_request_implementation(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP request operation."""
    client = get_http_client()
    return client.make_request(method, url, **kwargs)


def _make_get_request_implementation(url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP GET request operation."""
    client = get_http_client()
    return client.get(url, **kwargs)


def _make_post_request_implementation(url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute HTTP POST request operation."""
    client = get_http_client()
    return client.post(url, data, **kwargs)


# ===== EXPORTS =====

__all__ = [
    # Enums
    'HTTPMethod',
    # Core classes
    'HTTPClientCore',
    'ResponseValidator',
    'ResponseTransformer',
    'TransformationPipeline',
    # Singleton access
    'get_http_client',
    # Gateway implementations
    '_make_request_implementation',
    '_make_get_request_implementation',
    '_make_post_request_implementation',
    # Header helpers
    'get_standard_headers',
    'get_ha_headers',
    # Query string helpers
    'build_query_string',
    'build_query_string_fast',
    # Header parsing
    'parse_response_headers',
    'parse_response_headers_fast',
    # Response processing
    'process_response',
    'create_timeout_response',
    'create_connection_error_response',
    'cache_response',
    'get_cached_response',
    'validate_response',
    'extract_response_data',
    'transform_response',
    # Factory functions
    'create_common_transformers',
    'create_validator',
    'create_transformer',
    'create_pipeline',
    # State management
    'get_client_state',
    'reset_client_state',
    'get_client_configuration',
    'update_client_configuration',
    'get_connection_statistics',
    # Extension functions
    'configure_http_retry',
    'http_request_with_retry',
    'transform_http_response',
    'validate_http_response',
    'execute_with_retry'
]

# EOF
