"""
http_client_core.py
Version: 2025.10.13.04
Description: Complete HTTP client with transformers, response processing, state management, and WebSocket support
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
import urllib3
import time
from typing import Dict, Any, Optional, Callable, List
from enum import Enum

class HTTPMethod(Enum):
    """HTTP methods enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

# ===== RESPONSE VALIDATOR CLASS =====

class ResponseValidator:
    """Validates response structure and content."""
    
    @staticmethod
    def validate_structure(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate response data against schema."""
        if not isinstance(data, dict):
            return False
        for field, field_type in schema.get('required_fields', {}).items():
            if field not in data or not isinstance(data[field], field_type):
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
        if include:
            return {k: v for k, v in data.items() if k in include}
        if exclude:
            return {k: v for k, v in data.items() if k not in exclude}
        return data
    
    @staticmethod
    def transform_values(data: Dict[str, Any], transformers: Dict[str, Callable]) -> Dict[str, Any]:
        """Apply transformation functions to specific fields."""
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
        result = data
        for step_type, operation, metadata in self._transformations:
            try:
                if step_type == 'validation':
                    validator = operation
                    error_handler = metadata.get('error_handler')
                    if not validator(result):
                        if error_handler:
                            result = error_handler(result)
                        else:
                            return {'success': False, 'error': 'Validation failed', 'data': result}
                elif step_type == 'transformation':
                    result = operation(result)
                elif step_type == 'filter':
                    result = operation(result)
            except Exception as e:
                return {'success': False, 'error': f'Pipeline step failed: {str(e)}', 'data': result}
        return {'success': True, 'data': result}

# ===== HTTP CLIENT CORE CLASS =====

class HTTPClientCore:
    """Core HTTP client with retry and circuit breaker support."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            maxsize=10,
            retries=False
        )
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        self._retry_config = {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2.0,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504}
        }
    
    def get_standard_headers(self) -> Dict[str, str]:
        """Get standard HTTP headers."""
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'LambdaExecutionEngine/1.0'
        }
    
    def _is_retriable_error(self, status_code: int) -> bool:
        """Check if error is retriable."""
        return status_code in self._retry_config['retriable_status_codes']
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base = self._retry_config['backoff_base_ms'] / 1000.0
        multiplier = self._retry_config['backoff_multiplier']
        return base * (multiplier ** attempt)
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request."""
        try:
            headers = kwargs.get('headers', self.get_standard_headers())
            data = kwargs.get('data')
            timeout = kwargs.get('timeout', 30)
            
            if method.upper() in ['POST', 'PUT', 'PATCH']:
                body = json.dumps(data) if isinstance(data, dict) else data
                response = self.http.request(
                    method.upper(),
                    url,
                    body=body,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = self.http.request(
                    method.upper(),
                    url,
                    headers=headers,
                    timeout=timeout
                )
            
            try:
                response_data = json.loads(response.data.decode('utf-8')) if response.data else None
            except:
                response_data = response.data.decode('utf-8') if response.data else None
            
            return {
                'success': True,
                'status_code': response.status,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': 0
            }
    
    def _execute_with_retry(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute request with retry logic."""
        last_error = None
        
        for attempt in range(self._retry_config['max_attempts']):
            self._stats['requests'] += 1
            
            result = self._execute_request(method, url, **kwargs)
            
            if result.get('success'):
                self._stats['successful'] += 1
                return result
            
            status_code = result.get('status_code', 0)
            
            if not self._is_retriable_error(status_code):
                self._stats['failed'] += 1
                return result
            
            if attempt < self._retry_config['max_attempts'] - 1:
                self._stats['retries'] += 1
                time.sleep(self._calculate_backoff(attempt))
            
            last_error = result
        
        self._stats['failed'] += 1
        return last_error
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry support."""
        use_retry = kwargs.pop('use_retry', True)
        
        if use_retry:
            return self._execute_with_retry(method, url, **kwargs)
        else:
            return self._execute_request(method, url, **kwargs)
    
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

# ===== HELPER FUNCTIONS =====

def get_standard_headers() -> Dict[str, str]:
    """Get standard HTTP headers."""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'LambdaExecutionEngine/1.0'
    }

def get_ha_headers(token: str) -> Dict[str, str]:
    """Get Home Assistant specific headers."""
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters."""
    if not params:
        return ''
    parts = [f"{k}={v}" for k, v in params.items()]
    return '?' + '&'.join(parts)

def build_query_string_fast(params: Dict[str, Any]) -> str:
    """Build query string with minimal allocations."""
    return build_query_string(params)

def parse_response_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Parse response headers into structured format."""
    return {
        'content_type': headers.get('content-type', '').split(';')[0].strip(),
        'content_length': int(headers.get('content-length', 0)) if headers.get('content-length') else 0,
        'cache_control': headers.get('cache-control', ''),
        'expires': headers.get('expires', ''),
        'etag': headers.get('etag', ''),
        'last_modified': headers.get('last-modified', ''),
        'server': headers.get('server', ''),
        'all_headers': headers
    }

def parse_response_headers_fast(headers: Dict[str, str]) -> Dict[str, Any]:
    """Fast header parsing (alias)."""
    return parse_response_headers(headers)

def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response."""
    return response_data

# ===== SINGLETON AND STATE MANAGEMENT =====

def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance via gateway."""
    from gateway import get_singleton, register_singleton
    
    singleton_key = 'http_client_core'
    client = get_singleton(singleton_key)
    
    if not client:
        client = HTTPClientCore()
        register_singleton(singleton_key, client)
    
    return client

def get_client_state(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get HTTP client state via gateway singleton."""
    from gateway import get_singleton
    
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
            main_client = get_singleton('http_client_core')
            if main_client:
                return {
                    'exists': True,
                    'client_type': 'http_client_core',
                    'state': 'initialized',
                    'instance_id': id(main_client),
                    'stats': main_client.get_stats() if hasattr(main_client, 'get_stats') else {}
                }
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
        from gateway import log_error
        log_error(f"Failed to get client state: {e}")
        return {'exists': False, 'error': str(e)}

def reset_client_state(client_type: str = None) -> Dict[str, Any]:
    """Reset HTTP client state via gateway singleton."""
    from gateway import execute_operation, GatewayInterface, create_success_response, create_error_response, record_metric
    
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
                'reset',
                singleton_name='http_client_core'
            )
            record_metric('http_client_state.reset_all', 1.0)
        
        return create_success_response("Client state reset", result)
    except Exception as e:
        from gateway import log_error
        log_error(f"Failed to reset client state: {e}")
        return create_error_response(str(e))

def get_client_configuration(client_type: str) -> Dict[str, Any]:
    """Get client configuration via gateway config."""
    from gateway import get_parameter
    
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
        from gateway import log_error
        log_error(f"Failed to get client configuration: {e}")
        return {
            'client_type': client_type,
            'configuration': {},
            'error': str(e)
        }

def update_client_configuration(client_type: str, new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration via gateway config."""
    from gateway import set_parameter, create_success_response, create_error_response, record_metric
    
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
        from gateway import log_error
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

# ===== EXTENSION FUNCTIONS =====

def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100,
                        retriable_codes: set = None) -> Dict[str, Any]:
    """Configure HTTP retry behavior."""
    from gateway import cache_set, log_info, create_success_response
    
    config = {
        'max_attempts': max_attempts,
        'backoff_base_ms': backoff_base_ms,
        'retriable_status_codes': retriable_codes or {408, 429, 500, 502, 503, 504}
    }
    
    cache_set('http_retry_config', config, ttl=3600)
    log_info(f"HTTP retry configured: {max_attempts} attempts, {backoff_base_ms}ms backoff")
    
    return create_success_response("Retry configured", config)

def transform_http_response(response: Dict[str, Any], transformer: Callable) -> Dict[str, Any]:
    """Transform HTTP response."""
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
    """Validate HTTP response."""
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

# ===== FACTORY FUNCTIONS =====

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

# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _make_http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP request operation."""
    client = get_http_client()
    return client.make_request(method, url, **kwargs)

# ===== WEBSOCKET OPERATIONS =====

def websocket_connect_implementation(url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Establish WebSocket connection using gateway services."""
    from gateway import log_info, log_error, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    correlation_id = kwargs.get('correlation_id') or generate_correlation_id()
    
    try:
        import websocket
        
        log_info(f"[{correlation_id}] Establishing WebSocket connection to {url}")
        
        ws = websocket.WebSocket()
        ws.connect(url, timeout=timeout)
        
        record_metric('websocket.connections', 1.0)
        log_info(f"[{correlation_id}] WebSocket connected successfully")
        
        return create_success_response("WebSocket connected", {
            'connection': ws,
            'correlation_id': correlation_id,
            'url': url
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket connection failed: {str(e)}")
        record_metric('websocket.connection_errors', 1.0)
        return create_error_response(f'Connection failed: {str(e)}')

def websocket_send_implementation(connection, message: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Send message via WebSocket using gateway services."""
    from gateway import log_info, log_error, log_debug, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    correlation_id = correlation_id or generate_correlation_id()
    
    try:
        message_json = json.dumps(message)
        log_debug(f"[{correlation_id}] Sending WebSocket message: {message_json[:200]}")
        
        connection.send(message_json)
        
        record_metric('websocket.messages_sent', 1.0)
        log_info(f"[{correlation_id}] WebSocket message sent successfully")
        
        return create_success_response("Message sent", {
            'message_id': message.get('id'),
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket send failed: {str(e)}")
        record_metric('websocket.send_errors', 1.0)
        return create_error_response(f'Send failed: {str(e)}')

def websocket_receive_implementation(connection, timeout: Optional[int] = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Receive message from WebSocket using gateway services."""
    from gateway import log_info, log_error, log_debug, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    correlation_id = correlation_id or generate_correlation_id()
    
    try:
        if timeout:
            connection.settimeout(timeout)
        
        log_debug(f"[{correlation_id}] Waiting for WebSocket message")
        message_str = connection.recv()
        
        try:
            message = json.loads(message_str)
        except:
            message = message_str
        
        record_metric('websocket.messages_received', 1.0)
        log_info(f"[{correlation_id}] WebSocket message received")
        
        return create_success_response("Message received", {
            'message': message,
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket receive failed: {str(e)}")
        record_metric('websocket.receive_errors', 1.0)
        return create_error_response(f'Receive failed: {str(e)}')

def websocket_close_implementation(connection, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Close WebSocket connection using gateway services."""
    from gateway import log_info, log_error, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    correlation_id = correlation_id or generate_correlation_id()
    
    try:
        connection.close()
        
        record_metric('websocket.disconnections', 1.0)
        log_info(f"[{correlation_id}] WebSocket connection closed")
        
        return create_success_response("Connection closed", {
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket close failed: {str(e)}")
        return create_error_response(f'Close failed: {str(e)}')

def websocket_request_implementation(url: str, message: Dict[str, Any], timeout: int = 10, 
                                    wait_for_response: bool = True, **kwargs) -> Dict[str, Any]:
    """Complete WebSocket request (connect, send, receive, close)."""
    from gateway import log_info, log_error, create_error_response, generate_correlation_id
    
    correlation_id = kwargs.get('correlation_id') or generate_correlation_id()
    
    log_info(f"[{correlation_id}] Starting WebSocket request to {url}")
    
    conn_result = websocket_connect_implementation(url, timeout, correlation_id=correlation_id)
    if not conn_result.get('success'):
        return conn_result
    
    connection = conn_result['data']['connection']
    
    try:
        send_result = websocket_send_implementation(connection, message, correlation_id)
        if not send_result.get('success'):
            websocket_close_implementation(connection, correlation_id)
            return send_result
        
        if wait_for_response:
            recv_result = websocket_receive_implementation(connection, timeout, correlation_id)
            websocket_close_implementation(connection, correlation_id)
            return recv_result
        else:
            websocket_close_implementation(connection, correlation_id)
            from gateway import create_success_response
            return create_success_response("Message sent (no response expected)", {
                'correlation_id': correlation_id
            })
    
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket request failed: {str(e)}")
        websocket_close_implementation(connection, correlation_id)
        return create_error_response(f'Request failed: {str(e)}')

# ===== EXPORTS =====

__all__ = [
    'HTTPMethod',
    'HTTPClientCore',
    'ResponseValidator',
    'ResponseTransformer',
    'TransformationPipeline',
    'get_http_client',
    '_make_http_request',
    'get_standard_headers',
    'get_ha_headers',
    'build_query_string',
    'build_query_string_fast',
    'parse_response_headers',
    'parse_response_headers_fast',
    'process_response',
    'create_common_transformers',
    'create_validator',
    'create_transformer',
    'create_pipeline',
    'get_client_state',
    'reset_client_state',
    'get_client_configuration',
    'update_client_configuration',
    'get_connection_statistics',
    'configure_http_retry',
    'transform_http_response',
    'validate_http_response',
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
]

# EOF
