"""
gateway.py
Version: 2025.10.13.04
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


_FAST_PATH_ENABLED = True
_FAST_PATH_STATS = {
    'total_calls': 0,
    'fast_path_hits': 0,
    'fast_path_misses': 0
}


def initialize_lambda():
    """Initialize Lambda execution environment."""
    pass


def execute_operation(interface: GatewayInterface, operation: str, *args, **kwargs):
    """Universal gateway routing with lazy loading."""
    if interface == GatewayInterface.CACHE:
        from cache_core import (
            _execute_get_implementation,
            _execute_set_implementation,
            _execute_exists_implementation,
            _execute_delete_implementation,
            _execute_clear_implementation,
            _execute_get_stats_implementation as cache_get_stats
        )
        if operation == 'get':
            return _execute_get_implementation(kwargs.get('key'), kwargs.get('default'))
        elif operation == 'set':
            return _execute_set_implementation(kwargs.get('key'), kwargs.get('value'), kwargs.get('ttl'))
        elif operation == 'exists':
            return _execute_exists_implementation(kwargs.get('key'))
        elif operation == 'delete':
            return _execute_delete_implementation(kwargs.get('key'))
        elif operation == 'clear':
            return _execute_clear_implementation()
        elif operation == 'get_stats':
            return cache_get_stats()
        else:
            raise ValueError(f"Unknown CACHE operation: {operation}")

    elif interface == GatewayInterface.LOGGING:
        from logging_core import (
            _execute_log_info_implementation,
            _execute_log_error_implementation,
            _execute_log_warning_implementation,
            _execute_log_debug_implementation,
            _execute_log_operation_start_implementation,
            _execute_log_operation_success_implementation,
            _execute_log_operation_failure_implementation
        )
        if operation == 'log_info':
            return _execute_log_info_implementation(kwargs.get('message'), kwargs.get('extra'))
        elif operation == 'log_error':
            return _execute_log_error_implementation(kwargs.get('message'), kwargs.get('error'), kwargs.get('extra'))
        elif operation == 'log_warning':
            return _execute_log_warning_implementation(kwargs.get('message'), kwargs.get('extra'))
        elif operation == 'log_debug':
            return _execute_log_debug_implementation(kwargs.get('message'), kwargs.get('extra'))
        elif operation == 'log_operation_start':
            return _execute_log_operation_start_implementation(
                kwargs.get('operation'),
                kwargs.get('correlation_id'),
                kwargs.get('context', {})
            )
        elif operation == 'log_operation_success':
            return _execute_log_operation_success_implementation(
                kwargs.get('operation'),
                kwargs.get('duration_ms', 0),
                kwargs.get('correlation_id'),
                kwargs.get('result')
            )
        elif operation == 'log_operation_failure':
            return _execute_log_operation_failure_implementation(
                kwargs.get('operation'),
                kwargs.get('error'),
                kwargs.get('duration_ms', 0),
                kwargs.get('correlation_id'),
                kwargs.get('context', {})
            )
        else:
            raise ValueError(f"Unknown LOGGING operation: {operation}")

    elif interface == GatewayInterface.SECURITY:
        from security_core import (
            _execute_validate_request_implementation,
            _execute_validate_token_implementation,
            _execute_encrypt_data_implementation,
            _execute_decrypt_data_implementation,
            _execute_generate_correlation_id_implementation
        )
        if operation == 'validate_request':
            return _execute_validate_request_implementation(kwargs.get('request_data'))
        elif operation == 'validate_token':
            return _execute_validate_token_implementation(kwargs.get('token'))
        elif operation == 'encrypt':
            return _execute_encrypt_data_implementation(kwargs.get('data'))
        elif operation == 'decrypt':
            return _execute_decrypt_data_implementation(kwargs.get('encrypted_data'))
        elif operation == 'generate_correlation_id':
            return _execute_generate_correlation_id_implementation()
        else:
            raise ValueError(f"Unknown SECURITY operation: {operation}")

    elif interface == GatewayInterface.METRICS:
        from metrics_core import (
            _execute_record_metric_implementation,
            _execute_increment_counter_implementation,
            _execute_get_stats_implementation,
            _execute_record_operation_metric_implementation,
            _execute_record_error_response_metric_implementation,
            _execute_record_cache_metric_implementation,
            _execute_record_api_metric_implementation
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
        elif operation == 'record_operation':
            return _execute_record_operation_metric_implementation(
                kwargs.get('operation'),
                kwargs.get('success', True),
                kwargs.get('duration_ms', 0),
                kwargs.get('error_type')
            )
        elif operation == 'record_error':
            return _execute_record_error_response_metric_implementation(
                kwargs.get('error_type'),
                kwargs.get('severity', 'medium'),
                kwargs.get('category', 'internal'),
                kwargs.get('context', {})
            )
        elif operation == 'record_cache':
            return _execute_record_cache_metric_implementation(
                kwargs.get('operation'),
                kwargs.get('hit', False),
                kwargs.get('miss', False),
                kwargs.get('eviction', False),
                kwargs.get('duration_ms', 0)
            )
        elif operation == 'record_api':
            return _execute_record_api_metric_implementation(
                kwargs.get('endpoint'),
                kwargs.get('method'),
                kwargs.get('status_code'),
                kwargs.get('duration_ms'),
                kwargs.get('success', True)
            )
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
            return _get_parameter_implementation(kwargs.get('key'), kwargs.get('default'))
        elif operation == 'set_parameter':
            return _set_parameter_implementation(kwargs.get('key'), kwargs.get('value'))
        elif operation == 'get_category_config':
            return _get_category_implementation(kwargs.get('category'))
        elif operation == 'reload_config':
            return _reload_implementation(kwargs.get('validate', True))
        elif operation == 'switch_preset':
            return _switch_preset_implementation(kwargs.get('preset_name'))
        elif operation == 'get_state':
            return _get_state_implementation()
        elif operation == 'load_from_environment':
            return _load_environment_implementation()
        elif operation == 'load_from_file':
            return _load_file_implementation(kwargs.get('filepath'))
        elif operation == 'validate_all_sections':
            return _validate_all_implementation()
        else:
            raise ValueError(f"Unknown CONFIG operation: {operation}")

    elif interface == GatewayInterface.HTTP_CLIENT:
        from http_client_core import (
            _make_http_request_implementation,
            _get_http_stats_implementation
        )
        if operation == 'make_request':
            return _make_http_request_implementation(
                kwargs.get('url'),
                kwargs.get('method', 'GET'),
                kwargs.get('data'),
                kwargs.get('headers'),
                kwargs.get('timeout', 30)
            )
        elif operation == 'get_stats':
            return _get_http_stats_implementation()
        else:
            raise ValueError(f"Unknown HTTP_CLIENT operation: {operation}")

    elif interface == GatewayInterface.SINGLETON:
        from singleton_core import (
            _get_singleton_implementation,
            _register_singleton_implementation,
            _clear_singletons_implementation,
            _get_singleton_stats_implementation
        )
        if operation == 'get':
            return _get_singleton_implementation(kwargs.get('key'), kwargs.get('factory'))
        elif operation == 'register':
            return _register_singleton_implementation(kwargs.get('key'), kwargs.get('instance'))
        elif operation == 'clear':
            return _clear_singletons_implementation()
        elif operation == 'get_stats':
            return _get_singleton_stats_implementation()
        else:
            raise ValueError(f"Unknown SINGLETON operation: {operation}")

    elif interface == GatewayInterface.INITIALIZATION:
        from initialization_core import (
            _register_module_implementation,
            _initialize_all_implementation,
            _get_initialization_state_implementation
        )
        if operation == 'register_module':
            return _register_module_implementation(kwargs.get('module_name'), kwargs.get('init_function'))
        elif operation == 'initialize_all':
            return _initialize_all_implementation()
        elif operation == 'get_state':
            return _get_initialization_state_implementation()
        else:
            raise ValueError(f"Unknown INITIALIZATION operation: {operation}")

    elif interface == GatewayInterface.UTILITY:
        from utility_core import (
            _generate_uuid_implementation,
            _get_timestamp_implementation,
            _format_bytes_implementation,
            _deep_merge_implementation
        )
        if operation == 'generate_uuid':
            return _generate_uuid_implementation()
        elif operation == 'get_timestamp':
            return _get_timestamp_implementation()
        elif operation == 'format_bytes':
            return _format_bytes_implementation(kwargs.get('size'))
        elif operation == 'deep_merge':
            return _deep_merge_implementation(kwargs.get('dict1'), kwargs.get('dict2'))
        else:
            raise ValueError(f"Unknown UTILITY operation: {operation}")

    elif interface == GatewayInterface.CIRCUIT_BREAKER:
        from circuit_breaker_core import (
            _execute_with_circuit_breaker_implementation,
            _get_circuit_state_implementation,
            _reset_circuit_implementation
        )
        if operation == 'execute':
            return _execute_with_circuit_breaker_implementation(
                kwargs.get('circuit_name'),
                kwargs.get('function'),
                kwargs.get('failure_threshold', 5),
                kwargs.get('timeout', 60)
            )
        elif operation == 'get_state':
            return _get_circuit_state_implementation(kwargs.get('circuit_name'))
        elif operation == 'reset':
            return _reset_circuit_implementation(kwargs.get('circuit_name'))
        else:
            raise ValueError(f"Unknown CIRCUIT_BREAKER operation: {operation}")

    else:
        raise ValueError(f"Unknown interface: {interface}")


def create_error_response(message: str, error_code: str = "ERROR", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": message,
        "error_code": error_code
    }
    if details:
        response["details"] = details
    return response


def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response."""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response


def cache_get(key: str, default: Any = None):
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default=default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set value in cache."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)


def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key)


def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear() -> bool:
    """Clear all cache entries."""
    return execute_operation(GatewayInterface.CACHE, 'clear')


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


def record_metric(metric_name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', metric_name=metric_name, value=value, dimensions=dimensions)


def increment_counter(counter_name: str, value: int = 1):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', counter_name=counter_name, value=value)


def get_parameter(key: str, default: Any = None):
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)


def set_parameter(key: str, value: Any):
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)


__all__ = [
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'create_error_response',
    'create_success_response',
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'record_metric',
    'increment_counter',
    'get_parameter',
    'set_parameter',
]

# EOF
