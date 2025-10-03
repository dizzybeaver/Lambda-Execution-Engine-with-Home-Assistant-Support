"""
Gateway Core - Revolutionary Gateway with Lambda Response Templates
Version: 2025.10.03.02
Description: Single Universal Gateway with Lambda response template optimization

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
import os
from typing import Dict, Any, Optional, Union, Tuple

# Lambda response templates for ultra-fast response generation
_LAMBDA_RESPONSE_TEMPLATE = '{"statusCode":%d,"body":%s,"headers":%s}'
_LAMBDA_SUCCESS_BODY = '{"success":true,"data":%s}'
_LAMBDA_ERROR_BODY = '{"success":false,"error":"%s","code":"%s"}'

_DEFAULT_HEADERS_JSON = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}'
_CORS_HEADERS_JSON = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,PUT,DELETE,OPTIONS","Access-Control-Allow-Headers":"Content-Type,Authorization"}'
_ERROR_HEADERS_JSON = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*","X-Error":"true"}'

_USE_LAMBDA_TEMPLATES = os.environ.get('USE_LAMBDA_TEMPLATES', 'true').lower() == 'true'
_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'

from enum import Enum

class GatewayOperation(Enum):
    """Enumeration of all gateway operations with module/method routing."""
    LOG_INFO = ("logging_core", "log_info")
    LOG_ERROR = ("logging_core", "log_error")
    LOG_WARNING = ("logging_core", "log_warning")
    LOG_DEBUG = ("logging_core", "log_debug")
    LOG_OPERATION_START = ("logging_core", "log_operation_start")
    LOG_OPERATION_SUCCESS = ("logging_core", "log_operation_success")
    
    CACHE_GET = ("cache_core", "get")
    CACHE_SET = ("cache_core", "set")
    CACHE_DELETE = ("cache_core", "delete")
    CACHE_CLEAR = ("cache_core", "clear")
    
    VALIDATE_REQUEST = ("security_core", "validate_request")
    VALIDATE_TOKEN = ("security_core", "validate_token")
    ENCRYPT_DATA = ("security_core", "encrypt_data")
    DECRYPT_DATA = ("security_core", "decrypt_data")
    
    RECORD_METRIC = ("metrics_core", "record_metric")
    INCREMENT_COUNTER = ("metrics_core", "record_metric")
    
    MAKE_REQUEST = ("http_client_core", "make_request")
    MAKE_GET_REQUEST = ("http_client_core", "make_request")
    MAKE_POST_REQUEST = ("http_client_core", "make_request")
    GET_STANDARD_HEADERS = ("http_client_core", "get_standard_headers")
    PARSE_HEADERS_FAST = ("http_client_core", "parse_headers_fast")
    BUILD_QUERY_FAST = ("http_client_core", "build_query_fast")
    
    CREATE_SUCCESS_RESPONSE = ("shared_utilities", "create_success_response")
    CREATE_ERROR_RESPONSE = ("shared_utilities", "create_error_response")
    PARSE_JSON_SAFELY = ("shared_utilities", "parse_json_safely")
    GENERATE_CORRELATION_ID = ("shared_utilities", "generate_correlation_id")
    
    GET_SINGLETON = ("config_core", "get_singleton")
    REGISTER_SINGLETON = ("config_core", "register_singleton")
    EXECUTE_INIT_OPERATION = ("config_core", "execute_initialization_operation")
    RECORD_INIT_STAGE = ("config_core", "record_initialization_stage")


class GatewayCore:
    """Revolutionary gateway with lazy loading."""
    
    def __init__(self):
        self._modules = {}
        self._module_lock = __import__('threading').RLock()
    
    def _get_module(self, module_name: str):
        """Get or load module lazily."""
        if module_name not in self._modules:
            with self._module_lock:
                if module_name not in self._modules:
                    self._modules[module_name] = __import__(module_name, fromlist=[''])
        return self._modules[module_name]
    
    def execute_operation(self, operation: GatewayOperation, *args, **kwargs):
        """Execute gateway operation."""
        module_name, method_name = operation.value
        try:
            module = self._get_module(module_name)
            method = getattr(module, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            return self._handle_error(operation, e)
    
    def _handle_error(self, operation: GatewayOperation, error: Exception):
        """Handle operation errors."""
        return None


_gateway = GatewayCore()


def execute_gateway_operation(operation: GatewayOperation, *args, **kwargs):
    """Execute gateway operation with generic dispatcher."""
    if _USE_GENERIC_OPERATIONS:
        return _gateway.execute_operation(operation, *args, **kwargs)
    else:
        return None


def format_lambda_response_fast(status_code: int, body: Any, 
                                headers: Optional[Dict[str, str]] = None,
                                error_code: Optional[str] = None) -> Dict[str, Any]:
    """Format Lambda response using templates for ultra-fast performance."""
    if not _USE_LAMBDA_TEMPLATES:
        return format_lambda_response_legacy(status_code, body, headers)
    
    try:
        if status_code >= 200 and status_code < 300:
            body_json = json.dumps(body) if not isinstance(body, str) else body
            if headers:
                headers_json = json.dumps(headers)
            else:
                headers_json = _DEFAULT_HEADERS_JSON
            
            lambda_json = _LAMBDA_RESPONSE_TEMPLATE % (status_code, body_json, headers_json)
            return json.loads(lambda_json)
        else:
            error_msg = body if isinstance(body, str) else str(body)
            error_body = _LAMBDA_ERROR_BODY % (error_msg, error_code or "ERROR")
            
            if headers:
                headers_json = json.dumps(headers)
            else:
                headers_json = _ERROR_HEADERS_JSON
            
            lambda_json = _LAMBDA_RESPONSE_TEMPLATE % (status_code, error_body, headers_json)
            return json.loads(lambda_json)
            
    except Exception:
        return format_lambda_response_legacy(status_code, body, headers)


def format_lambda_response_legacy(status_code: int, body: Any, 
                                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Legacy Lambda response formatting."""
    return {
        'statusCode': status_code,
        'body': json.dumps(body) if not isinstance(body, str) else body,
        'headers': headers or {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }


def format_response(status_code: int, data: Any) -> Dict[str, Any]:
    """Format response with template optimization."""
    return format_lambda_response_fast(status_code, data)


def format_response_json(success: bool, data: Any = None, error: str = None) -> str:
    """Format JSON response body."""
    if success:
        body = {'success': True, 'data': data or {}}
    else:
        body = {'success': False, 'error': error or 'Unknown error'}
    return json.dumps(body)


def log_info(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log info message."""
    return execute_gateway_operation(GatewayOperation.LOG_INFO, message, extra)


def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None):
    """Log error message."""
    return execute_gateway_operation(GatewayOperation.LOG_ERROR, message, error, extra)


def log_warning(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log warning message."""
    return execute_gateway_operation(GatewayOperation.LOG_WARNING, message, extra)


def log_debug(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log debug message."""
    return execute_gateway_operation(GatewayOperation.LOG_DEBUG, message, extra)


def cache_get(key: str, default: Any = None):
    """Get value from cache."""
    return execute_gateway_operation(GatewayOperation.CACHE_GET, key, default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set value in cache."""
    return execute_gateway_operation(GatewayOperation.CACHE_SET, key, value, ttl)


def cache_delete(key: str):
    """Delete value from cache."""
    return execute_gateway_operation(GatewayOperation.CACHE_DELETE, key)


def cache_clear():
    """Clear all cache."""
    return execute_gateway_operation(GatewayOperation.CACHE_CLEAR)


def validate_request(request: Dict[str, Any]):
    """Validate request."""
    return execute_gateway_operation(GatewayOperation.VALIDATE_REQUEST, request)


def validate_token(token: str):
    """Validate token."""
    return execute_gateway_operation(GatewayOperation.VALIDATE_TOKEN, token)


def encrypt_data(data: str, key: str):
    """Encrypt data."""
    return execute_gateway_operation(GatewayOperation.ENCRYPT_DATA, data, key)


def decrypt_data(data: str, key: str):
    """Decrypt data."""
    return execute_gateway_operation(GatewayOperation.DECRYPT_DATA, data, key)


def record_metric(name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None):
    """Record metric."""
    return execute_gateway_operation(GatewayOperation.RECORD_METRIC, name, value, dimensions)


def increment_counter(name: str, dimensions: Optional[Dict[str, str]] = None):
    """Increment counter."""
    return execute_gateway_operation(GatewayOperation.INCREMENT_COUNTER, name, dimensions)


def make_request(method: str, url: str, **kwargs):
    """Make HTTP request."""
    return execute_gateway_operation(GatewayOperation.MAKE_REQUEST, method, url, **kwargs)


def make_get_request(url: str, **kwargs):
    """Make GET request."""
    return execute_gateway_operation(GatewayOperation.MAKE_GET_REQUEST, 'GET', url, **kwargs)


def make_post_request(url: str, **kwargs):
    """Make POST request."""
    return execute_gateway_operation(GatewayOperation.MAKE_POST_REQUEST, 'POST', url, **kwargs)


def get_standard_headers(content_type: str = 'json'):
    """Get standard HTTP headers."""
    return execute_gateway_operation(GatewayOperation.GET_STANDARD_HEADERS, content_type)


def parse_headers_fast(headers_dict: Dict[str, str]):
    """Parse HTTP headers."""
    return execute_gateway_operation(GatewayOperation.PARSE_HEADERS_FAST, headers_dict)


def build_query_fast(params: Dict[str, Any]):
    """Build query string."""
    return execute_gateway_operation(GatewayOperation.BUILD_QUERY_FAST, params)


def create_success_response(message: str, data: Optional[Dict[str, Any]] = None):
    """Create success response."""
    return execute_gateway_operation(GatewayOperation.CREATE_SUCCESS_RESPONSE, message, data)


def create_error_response(message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
    """Create error response."""
    return execute_gateway_operation(GatewayOperation.CREATE_ERROR_RESPONSE, message, error_code, details)


def generate_correlation_id():
    """Generate correlation ID."""
    return execute_gateway_operation(GatewayOperation.GENERATE_CORRELATION_ID)


def parse_json_safely(json_str: str):
    """Parse JSON safely."""
    return execute_gateway_operation(GatewayOperation.PARSE_JSON_SAFELY, json_str)


def get_singleton(name: str):
    """Get singleton instance."""
    return execute_gateway_operation(GatewayOperation.GET_SINGLETON, name)


def register_singleton(name: str, instance):
    """Register singleton instance."""
    return execute_gateway_operation(GatewayOperation.REGISTER_SINGLETON, name, instance)


def execute_initialization_operation(init_type: str, stage: str, **kwargs):
    """Execute initialization operation."""
    return execute_gateway_operation(GatewayOperation.EXECUTE_INIT_OPERATION, init_type, stage, **kwargs)


def record_initialization_stage(stage: str, **kwargs):
    """Record initialization stage."""
    return execute_gateway_operation(GatewayOperation.RECORD_INIT_STAGE, stage, **kwargs)


def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        'loaded_modules': len(_gateway._modules),
        'modules': list(_gateway._modules.keys())
    }


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    try:
        from fast_path import get_fast_path_stats as _get_stats
        return _get_stats()
    except Exception:
        return {}


def enable_fast_path():
    """Enable fast path optimization."""
    try:
        from fast_path import enable_fast_path as _enable
        _enable()
    except Exception:
        pass


def disable_fast_path():
    """Disable fast path optimization."""
    try:
        from fast_path import disable_fast_path as _disable
        _disable()
    except Exception:
        pass


def reset_fast_path_stats():
    """Reset fast path statistics."""
    pass


__all__ = [
    'GatewayOperation',
    'execute_gateway_operation',
    'format_lambda_response_fast',
    'format_response',
    'format_response_json',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'cache_get',
    'cache_set',
    'cache_delete',
    'cache_clear',
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'record_metric',
    'increment_counter',
    'make_request',
    'make_get_request',
    'make_post_request',
    'get_standard_headers',
    'parse_headers_fast',
    'build_query_fast',
    'create_success_response',
    'create_error_response',
    'generate_correlation_id',
    'parse_json_safely',
    'get_singleton',
    'register_singleton',
    'execute_initialization_operation',
    'record_initialization_stage',
    'get_gateway_stats',
    'get_fast_path_stats',
    'enable_fast_path',
    'disable_fast_path',
    'reset_fast_path_stats',
]
