"""
gateway.py
Version: 2025.10.13.03
Description: Gateway Architecture Interface Module with WebSocket Support
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
from typing import Dict, Any, Optional
from enum import Enum

# ===== GATEWAY INTERFACE ENUMERATION =====
class GatewayInterface(Enum):
    """Enumeration of all available gateway interfaces."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    HTTP_CLIENT = "http_client"
    SINGLETON = "singleton"
    INITIALIZATION = "initialization"
    UTILITY = "utility"
    CIRCUIT_BREAKER = "circuit_breaker"

# ===== FAST PATH OPTIMIZATION =====
_FAST_PATH_ENABLED = True
_FAST_PATH_STATS = {
    'total_calls': 0,
    'fast_path_hits': 0,
    'fast_path_misses': 0
}

# ===== LAMBDA INITIALIZATION =====
def initialize_lambda():
    """
    Initialize Lambda execution environment.
    Called once at container start to warm up critical paths.
    """
    pass

# ===== CORE GATEWAY ROUTING =====
def execute_operation(interface: GatewayInterface, operation: str, *args, **kwargs):
    """
    Universal gateway routing with lazy loading.
    Routes operations to appropriate interface implementations.
    """
    global _FAST_PATH_STATS
    _FAST_PATH_STATS['total_calls'] += 1

    if interface == GatewayInterface.CACHE:
        from cache_core import (
            _execute_get_implementation,
            _execute_set_implementation,
            _execute_delete_implementation,
            _execute_clear_implementation
        )
        if operation == 'get':
            return _execute_get_implementation(kwargs.get('key'))
        elif operation == 'set':
            return _execute_set_implementation(
                kwargs.get('key'),
                kwargs.get('value'),
                kwargs.get('ttl')
            )
        elif operation == 'delete':
            return _execute_delete_implementation(kwargs.get('key'))
        elif operation == 'clear':
            return _execute_clear_implementation()
        else:
            raise ValueError(f"Unknown CACHE operation: {operation}")

    elif interface == GatewayInterface.LOGGING:
        from logging_core import (
            _execute_log_info_implementation,
            _execute_log_error_implementation,
            _execute_log_warning_implementation,
            _execute_log_debug_implementation
        )
        if operation == 'log_info':
            return _execute_log_info_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_error':
            return _execute_log_error_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_warning':
            return _execute_log_warning_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_debug':
            return _execute_log_debug_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        else:
            raise ValueError(f"Unknown LOGGING operation: {operation}")

    elif interface == GatewayInterface.SECURITY:
        from security_core import (
            _execute_validate_request_implementation,
            _execute_validate_token_implementation,
            _execute_encrypt_data_implementation,
            _execute_decrypt_data_implementation
        )
        if operation == 'validate_request':
            return _execute_validate_request_implementation(kwargs.get('request_data'))
        elif operation == 'validate_token':
            return _execute_validate_token_implementation(kwargs.get('token'))
        elif operation == 'encrypt':
            return _execute_encrypt_data_implementation(kwargs.get('data'))
        elif operation == 'decrypt':
            return _execute_decrypt_data_implementation(kwargs.get('encrypted_data'))
        else:
            raise ValueError(f"Unknown SECURITY operation: {operation}")

    elif interface == GatewayInterface.METRICS:
        from metrics_core import (
            _execute_record_metric_implementation,
            _execute_increment_counter_implementation,
            _execute_get_stats_implementation
        )
        if operation == 'record':
            return _execute_record_metric_implementation(
                kwargs.get('metric_name'),
                kwargs.get('value'),
                kwargs.get('dimensions', {})
            )
        elif operation == 'increment':
            return _execute_increment_counter_implementation(
                kwargs.get('counter_name'),
                kwargs.get('value', 1)
            )
        elif operation == 'get_metrics':
            return _execute_get_stats_implementation()
        else:
            raise ValueError(f"Unknown METRICS operation: {operation}")

    elif interface == GatewayInterface.CONFIG:
        from config_core import (
            _initialize_implementation,
            _get_parameter_implementation,
            _set_parameter_implementation,
            _get_category_implementation,
            _reload_implementation,
            _switch_preset_implementation,
            _get_state_implementation,
            _load_environment_implementation,
            _load_file_implementation,
            _validate_all_implementation
        )
        if operation == 'initialize':
            return _initialize_implementation()
        elif operation == 'get_parameter':
            return _get_parameter_implementation(
                kwargs.get('key'),
                kwargs.get('default')
            )
        elif operation == 'set_parameter':
            return _set_parameter_implementation(
                kwargs.get('key'),
                kwargs.get('value')
            )
        elif operation == 'get_category_config':
            return _get_category_implementation(
                kwargs.get('category')
            )
        elif operation == 'reload_config':
            return _reload_implementation(
                kwargs.get('validate', True)
            )
        elif operation == 'switch_preset':
            return _switch_preset_implementation(
                kwargs.get('preset_name')
            )
        elif operation == 'get_state':
            return _get_state_implementation()
        elif operation == 'load_from_environment':
            return _load_environment_implementation()
        elif operation == 'load_from_file':
            return _load_file_implementation(
                kwargs.get('filepath')
            )
        elif operation == 'validate_all_sections':
            return _validate_all_implementation()
        else:
            raise ValueError(f"Unknown CONFIG operation: {operation}")

    elif interface == GatewayInterface.HTTP_CLIENT:
        from http_client_core import (
            _make_http_request,
            websocket_connect_implementation,
            websocket_send_implementation,
            websocket_receive_implementation,
            websocket_close_implementation,
            websocket_request_implementation
        )
        if operation == 'request':
            return _make_http_request(kwargs.get('method'), kwargs.get('url'), **kwargs)
        elif operation == 'get':
            return _make_http_request('GET', kwargs.get('url'), **kwargs)
        elif operation == 'post':
            return _make_http_request('POST', kwargs.get('url'), **kwargs)
        
        # WebSocket operations
        elif operation == 'websocket_connect':
            return websocket_connect_implementation(**kwargs)
        elif operation == 'websocket_send':
            return websocket_send_implementation(**kwargs)
        elif operation == 'websocket_receive':
            return websocket_receive_implementation(**kwargs)
        elif operation == 'websocket_close':
            return websocket_close_implementation(**kwargs)
        elif operation == 'websocket_request':
            return websocket_request_implementation(**kwargs)
        
        else:
            raise ValueError(f"Unknown HTTP_CLIENT operation: {operation}")

    elif interface == GatewayInterface.UTILITY:
        from utility_core import _UTILITY
        import uuid
        if operation == 'success_response':
            return _UTILITY.create_success_response(
                kwargs.get('message'),
                kwargs.get('data')
            )
        elif operation == 'error_response':
            return _UTILITY.create_error_response(
                kwargs.get('message'),
                kwargs.get('error_code')
            )
        elif operation == 'generate_correlation_id':
            return str(uuid.uuid4())
        else:
            raise ValueError(f"Unknown UTILITY operation: {operation}")

    elif interface == GatewayInterface.SINGLETON:
        from singleton_core import _SINGLETON
        if operation == 'get':
            return _SINGLETON.get_singleton(kwargs.get('singleton_name'))
        elif operation == 'register':
            return _SINGLETON.register_singleton(
                kwargs.get('singleton_name'),
                kwargs.get('instance')
            )
        elif operation == 'reset':
            return _SINGLETON.reset_singleton(kwargs.get('singleton_name'))
        else:
            raise ValueError(f"Unknown SINGLETON operation: {operation}")

    elif interface == GatewayInterface.INITIALIZATION:
        from initialization_core import _INITIALIZATION
        if operation == 'execute':
            return _INITIALIZATION.execute_initialization(kwargs.get('init_type'))
        elif operation == 'record_stage':
            return _INITIALIZATION.record_initialization_stage(
                kwargs.get('stage'),
                kwargs.get('status')
            )
        else:
            raise ValueError(f"Unknown INITIALIZATION operation: {operation}")

    elif interface == GatewayInterface.CIRCUIT_BREAKER:
        from circuit_breaker_core import _CIRCUIT_BREAKER
        if operation == 'call':
            return _CIRCUIT_BREAKER.call(
                kwargs.get('circuit_name'),
                kwargs.get('func'),
                *args,
                **kwargs
            )
        elif operation == 'is_open':
            return _CIRCUIT_BREAKER.is_circuit_open(kwargs.get('circuit_name'))
        elif operation == 'reset':
            return _CIRCUIT_BREAKER.reset_circuit(kwargs.get('circuit_name'))
        else:
            raise ValueError(f"Unknown CIRCUIT_BREAKER operation: {operation}")

    else:
        raise ValueError(f"Unknown gateway interface: {interface}")


# ===== CACHE INTERFACE FUNCTIONS =====
def cache_get(key: str):
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key)

def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set value in cache with optional TTL."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)

def cache_delete(key: str):
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)

def cache_clear():
    """Clear all cache entries."""
    return execute_operation(GatewayInterface.CACHE, 'clear')

# ===== LOGGING INTERFACE FUNCTIONS =====
def log_info(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log info message."""
    if extra is None:
        extra = kwargs
    else:
        extra.update(kwargs)
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)

def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log error message."""
    if extra is None:
        extra = kwargs
    else:
        extra.update(kwargs)
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, extra=extra)

def log_warning(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log warning message."""
    if extra is None:
        extra = kwargs
    else:
        extra.update(kwargs)
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, error=error, extra=extra)

def log_debug(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log debug message."""
    if extra is None:
        extra = kwargs
    else:
        extra.update(kwargs)
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, error=error, extra=extra)

# ===== SECURITY INTERFACE FUNCTIONS =====
def validate_request(request_data: Dict[str, Any]) -> bool:
    """Validate request."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)

def validate_token(token: str) -> bool:
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)

def encrypt_data(data: str) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data)

# ===== METRICS INTERFACE FUNCTIONS =====
def record_metric(metric_name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', metric_name=metric_name, value=value, dimensions=dimensions)

def increment_counter(counter_name: str, value: int = 1):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', counter_name=counter_name, value=value)

# ===== CONFIG INTERFACE FUNCTIONS =====
def get_parameter(key: str, default: Any = None):
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)

def set_parameter(key: str, value: Any):
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)

def get_all_parameters() -> Dict[str, Any]:
    """Get all configuration parameters."""
    return execute_operation(GatewayInterface.CONFIG, 'get_all')

def get_category_config(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category_config', category=category)

def update_category_config(category: str, updates: Dict[str, Any]):
    """Update configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'update_category_config', category=category, updates=updates)

# ===== HTTP CLIENT INTERFACE FUNCTIONS =====
def make_request(method: str, url: str, **kwargs):
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'request', method=method, url=url, **kwargs)

def make_get_request(url: str, **kwargs):
    """Make HTTP GET request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get', url=url, **kwargs)

def make_post_request(url: str, data: Dict[str, Any], **kwargs):
    """Make HTTP POST request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'post', url=url, data=data, **kwargs)

# ===== WEBSOCKET INTERFACE FUNCTIONS =====
def websocket_connect(url: str, timeout: int = 10, **kwargs):
    """Establish WebSocket connection."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'websocket_connect', url=url, timeout=timeout, **kwargs)

def websocket_send(connection, message: Dict[str, Any], correlation_id: Optional[str] = None):
    """Send WebSocket message."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'websocket_send', 
                           connection=connection, message=message, correlation_id=correlation_id)

def websocket_receive(connection, timeout: Optional[int] = None, correlation_id: Optional[str] = None):
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'websocket_receive',
                           connection=connection, timeout=timeout, correlation_id=correlation_id)

def websocket_close(connection, correlation_id: Optional[str] = None):
    """Close WebSocket connection."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'websocket_close',
                           connection=connection, correlation_id=correlation_id)

def make_websocket_request(url: str, message: Dict[str, Any], timeout: int = 10, 
                          wait_for_response: bool = True, **kwargs):
    """
    Make complete WebSocket request (connect, send, receive, close).
    Convenience function for single request/response pattern.
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'websocket_request',
                           url=url, message=message, timeout=timeout,
                           wait_for_response=wait_for_response, **kwargs)

# ===== SINGLETON INTERFACE FUNCTIONS =====
def get_singleton(singleton_name: str):
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', singleton_name=singleton_name)

def register_singleton(singleton_name: str, instance):
    """Register singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'register', singleton_name=singleton_name, instance=instance)

# ===== INITIALIZATION INTERFACE FUNCTIONS =====
def execute_initialization_operation(init_type: str):
    """Execute initialization operation."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'execute', init_type=init_type)

def record_initialization_stage(stage: str, status: str):
    """Record initialization stage."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'record_stage', stage=stage, status=status)

# ===== UTILITY INTERFACE FUNCTIONS =====
def create_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """Create success response."""
    return execute_operation(GatewayInterface.UTILITY, 'success_response', message=message, data=data)

def create_error_response(message: str, error_code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """Create error response."""
    return execute_operation(GatewayInterface.UTILITY, 'error_response', message=message, error_code=error_code)

def generate_correlation_id() -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.UTILITY, 'generate_correlation_id')

# ===== CIRCUIT BREAKER INTERFACE FUNCTIONS =====
def execute_with_circuit_breaker(circuit_name: str, func, *args, **kwargs):
    """Execute function with circuit breaker protection."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', 
                           circuit_name=circuit_name, func=func, *args, **kwargs)

def is_circuit_open(circuit_name: str) -> bool:
    """Check if circuit breaker is open."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'is_open', circuit_name=circuit_name)

def reset_circuit_breaker(circuit_name: str):
    """Reset circuit breaker."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset', circuit_name=circuit_name)

# ===== LAMBDA RESPONSE FORMATTING =====
def format_response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Format Lambda response."""
    response = {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': headers or {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    return response

# EOF
