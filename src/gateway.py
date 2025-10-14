"""
gateway.py - Universal Lambda Gateway with SUGA Architecture
Version: 2025.10.14.02
Description: Central routing hub for all Lambda operations with lazy loading and consolidated utility support

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

from enum import Enum
from typing import Any, Dict, Optional


class GatewayInterface(Enum):
    """Gateway interface enumeration."""
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
            _execute_generate_correlation_id_implementation,
            _execute_validate_string_implementation,
            _execute_validate_email_implementation,
            _execute_validate_url_implementation,
            _execute_hash_data_implementation,
            _execute_verify_hash_implementation,
            _execute_sanitize_input_implementation
        )
        
        if operation == 'validate_request':
            return _execute_validate_request_implementation(kwargs.get('request_data'))
        elif operation == 'validate_token':
            return _execute_validate_token_implementation(kwargs.get('token'))
        elif operation == 'encrypt':
            return _execute_encrypt_data_implementation(
                kwargs.get('data'), 
                key=kwargs.get('key')
            )
        elif operation == 'decrypt':
            return _execute_decrypt_data_implementation(
                kwargs.get('encrypted_data'), 
                key=kwargs.get('key')
            )
        elif operation == 'generate_correlation_id':
            return _execute_generate_correlation_id_implementation()
        elif operation == 'validate_string':
            return _execute_validate_string_implementation(
                kwargs.get('value'),
                min_length=kwargs.get('min_length', 0),
                max_length=kwargs.get('max_length', 1000)
            )
        elif operation == 'validate_email':
            return _execute_validate_email_implementation(kwargs.get('email'))
        elif operation == 'validate_url':
            return _execute_validate_url_implementation(kwargs.get('url'))
        elif operation == 'hash':
            return _execute_hash_data_implementation(kwargs.get('data'))
        elif operation == 'verify_hash':
            return _execute_verify_hash_implementation(
                kwargs.get('data'),
                kwargs.get('hash_value')
            )
        elif operation == 'sanitize':
            return _execute_sanitize_input_implementation(kwargs.get('data'))
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
                kwargs.get('operation_name'),
                kwargs.get('duration_ms'),
                kwargs.get('success', True)
            )
        elif operation == 'record_error_response':
            return _execute_record_error_response_metric_implementation(
                kwargs.get('operation_name'),
                kwargs.get('error_code')
            )
        elif operation == 'record_cache':
            return _execute_record_cache_metric_implementation(
                kwargs.get('operation'),
                kwargs.get('hit', False)
            )
        elif operation == 'record_api':
            return _execute_record_api_metric_implementation(
                kwargs.get('endpoint'),
                kwargs.get('status_code'),
                kwargs.get('duration_ms')
            )
        else:
            raise ValueError(f"Unknown METRICS operation: {operation}")

    elif interface == GatewayInterface.CONFIG:
        from config_core import (
            _execute_get_parameter_implementation,
            _execute_set_parameter_implementation,
            _execute_get_category_config_implementation,
            _execute_reload_config_implementation,
            _execute_switch_preset_implementation,
            _execute_get_state_implementation
        )
        if operation == 'get_parameter':
            return _execute_get_parameter_implementation(kwargs.get('key'), kwargs.get('default'))
        elif operation == 'set_parameter':
            return _execute_set_parameter_implementation(kwargs.get('key'), kwargs.get('value'))
        elif operation == 'get_category_config':
            return _execute_get_category_config_implementation(kwargs.get('category'))
        elif operation == 'reload_config':
            return _execute_reload_config_implementation(kwargs.get('validate', True))
        elif operation == 'switch_preset':
            return _execute_switch_preset_implementation(kwargs.get('preset_name'))
        elif operation == 'get_state':
            return _execute_get_state_implementation()
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
            _execute_initialize_implementation,
            _execute_get_config_implementation,
            _execute_is_initialized_implementation,
            _execute_reset_implementation
        )
        if operation == 'initialize':
            return _execute_initialize_implementation(**kwargs)
        elif operation == 'get_config':
            return _execute_get_config_implementation(**kwargs)
        elif operation == 'is_initialized':
            return _execute_is_initialized_implementation(**kwargs)
        elif operation == 'reset':
            return _execute_reset_implementation(**kwargs)
        else:
            raise ValueError(f"Unknown INITIALIZATION operation: {operation}")

    elif interface == GatewayInterface.UTILITY:
        from shared_utilities import (
            _generate_uuid_implementation,
            _get_timestamp_implementation,
            _format_bytes_implementation,
            _deep_merge_implementation,
            _execute_format_response_implementation,
            _execute_parse_json_implementation,
            _execute_safe_get_implementation
        )
        
        if operation == 'generate_uuid':
            return _generate_uuid_implementation()
        elif operation == 'get_timestamp':
            return _get_timestamp_implementation()
        elif operation == 'format_bytes':
            return _format_bytes_implementation(kwargs.get('size'))
        elif operation == 'deep_merge':
            return _deep_merge_implementation(kwargs.get('dict1'), kwargs.get('dict2'))
        elif operation == 'format_response':
            return _execute_format_response_implementation(
                kwargs.get('status_code'),
                kwargs.get('body'),
                kwargs.get('headers'),
                kwargs.get('use_template', True)
            )
        elif operation == 'parse_json':
            return _execute_parse_json_implementation(kwargs.get('data'))
        elif operation == 'safe_get':
            return _execute_safe_get_implementation(
                kwargs.get('dictionary'),
                kwargs.get('key_path'),
                kwargs.get('default')
            )
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


# ===== GATEWAY WRAPPER FUNCTIONS =====

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


def cache_delete(key: str):
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear():
    """Clear all cache entries."""
    return execute_operation(GatewayInterface.CACHE, 'clear')


def log_info(message: str, extra: Optional[Dict] = None):
    """Log info message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)


def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict] = None):
    """Log error message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, extra=extra)


def log_warning(message: str, extra: Optional[Dict] = None):
    """Log warning message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, extra=extra)


def log_debug(message: str, extra: Optional[Dict] = None):
    """Log debug message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, extra=extra)


def validate_request(request_data: Dict) -> bool:
    """Validate request."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)


def validate_token(token: str) -> bool:
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)


def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data, key=key)


def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data, key=key)


def generate_correlation_id() -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')


def validate_string(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """Validate string."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_string', value=value, min_length=min_length, max_length=max_length)


def validate_email(email: str) -> bool:
    """Validate email."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_email', email=email)


def validate_url(url: str) -> bool:
    """Validate URL."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_url', url=url)


def hash_data(data: str) -> str:
    """Hash data."""
    return execute_operation(GatewayInterface.SECURITY, 'hash', data=data)


def verify_hash(data: str, hash_value: str) -> bool:
    """Verify hash."""
    return execute_operation(GatewayInterface.SECURITY, 'verify_hash', data=data, hash_value=hash_value)


def sanitize_input(data: Any) -> Any:
    """Sanitize input."""
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)


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


def make_request(url: str, method: str = 'GET', data: Any = None, headers: Optional[Dict] = None, timeout: int = 30):
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'make_request', url=url, method=method, data=data, headers=headers, timeout=timeout)


def make_get_request(url: str, headers: Optional[Dict] = None, timeout: int = 30):
    """Make HTTP GET request."""
    return make_request(url, method='GET', headers=headers, timeout=timeout)


def make_post_request(url: str, data: Any = None, headers: Optional[Dict] = None, timeout: int = 30):
    """Make HTTP POST request."""
    return make_request(url, method='POST', data=data, headers=headers, timeout=timeout)


def get_singleton(key: str, factory: Optional[Any] = None):
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', key=key, factory=factory)


def register_singleton(key: str, instance: Any):
    """Register singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'register', key=key, instance=instance)


def execute_initialization_operation(operation: str, **kwargs):
    """Execute initialization operation."""
    return execute_operation(GatewayInterface.INITIALIZATION, operation, **kwargs)


def record_initialization_stage(stage: str, success: bool = True):
    """Record initialization stage."""
    return record_metric(f'initialization_{stage}', value=1.0 if success else 0.0)


def parse_json_safely(json_str: str):
    """Parse JSON safely."""
    from shared_utilities import parse_json_safely as _parse_json
    return _parse_json(json_str)


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
    'generate_correlation_id',
    'validate_string',
    'validate_email',
    'validate_url',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    'record_metric',
    'increment_counter',
    'get_parameter',
    'set_parameter',
    'make_request',
    'make_get_request',
    'make_post_request',
    'get_singleton',
    'register_singleton',
    'execute_initialization_operation',
    'record_initialization_stage',
    'parse_json_safely',
]

# EOF
