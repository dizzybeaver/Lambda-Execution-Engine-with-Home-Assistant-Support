"""
gateway.py - Revolutionary Gateway Architecture with CONFIG Integration
Version: 2025.10.04.03
Description: Universal gateway with SUGA + LIGS + ZAFP + LUGS + CONFIG support

Phase 3 CONFIG Integration Complete:
- CONFIG added to GatewayInterface enum
- CONFIG routing added to execute_operation
- Lazy-loads config_core.py when needed
- Routes 12 configuration operations
- Full backward compatibility maintained

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

import sys
import time
import json
import uuid
import threading
from typing import Dict, Any, Optional, Callable
from enum import Enum


# ===== GATEWAY INTERFACE ENUM =====

class GatewayInterface(Enum):
    """Gateway interface types - The Heart knows all Limbs."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"  # Phase 3: Configuration system integration
    HTTP_CLIENT = "http_client"
    SINGLETON = "singleton"
    CIRCUIT_BREAKER = "circuit_breaker"
    INITIALIZATION = "initialization"
    UTILITY = "utility"


# ===== FAST PATH CONFIGURATION =====

_FAST_PATH_ENABLED = False
_FAST_PATH_STATS = {
    'total_calls': 0,
    'fast_path_hits': 0,
    'fast_path_misses': 0
}

_FAST_PATH_OPERATIONS = {
    ('CACHE', 'get'),
    ('CACHE', 'set'),
    ('LOGGING', 'log_info'),
    ('LOGGING', 'log_error'),
    ('CONFIG', 'get_parameter'),  # Hot configuration access
    ('CONFIG', 'get_category_config'),  # Hot category access
}


# ===== MODULE TRACKING FOR LUGS =====

_LOADABLE_MODULES = {
    'cache': 'cache_core',
    'logging': 'logging_core',
    'security': 'security_core',
    'metrics': 'metrics_core',
    'config': 'config_core',  # Configuration core module
    'http_client': 'http_client_core',
    'singleton': 'singleton_core',
    'circuit_breaker': 'circuit_breaker_core',
}


# ===== UNIVERSAL OPERATION ROUTER =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs):
    """
    Universal operation router - The Heart's Beating Function.
    
    Routes all operations to appropriate interface implementations.
    Implements SUGA (Single Universal Gateway Architecture).
    Supports LIGS (Lazy Import Gateway System) for memory optimization.
    """
    
    # Fast path check
    if _FAST_PATH_ENABLED:
        operation_key = (interface.value.upper(), operation)
        if operation_key in _FAST_PATH_OPERATIONS:
            _FAST_PATH_STATS['fast_path_hits'] += 1
            # Fast path implementation would go here
        else:
            _FAST_PATH_STATS['fast_path_misses'] += 1
    
    _FAST_PATH_STATS['total_calls'] += 1
    
    # Route to appropriate interface
    if interface == GatewayInterface.CACHE:
        from cache_core import (
            _cache_get_implementation,
            _cache_set_implementation,
            _cache_delete_implementation,
            _cache_clear_implementation
        )
        
        if operation == 'get':
            return _cache_get_implementation(
                kwargs.get('key'),
                kwargs.get('default_value')
            )
        elif operation == 'set':
            return _cache_set_implementation(
                kwargs.get('key'),
                kwargs.get('value'),
                kwargs.get('ttl', 300)
            )
        elif operation == 'delete':
            return _cache_delete_implementation(kwargs.get('key'))
        elif operation == 'clear':
            return _cache_clear_implementation(kwargs.get('pattern'))
        else:
            raise ValueError(f"Unknown CACHE operation: {operation}")
    
    elif interface == GatewayInterface.LOGGING:
        from logging_core import (
            _log_info_implementation,
            _log_error_implementation,
            _log_warning_implementation,
            _log_debug_implementation
        )
        
        if operation == 'log_info':
            return _log_info_implementation(
                kwargs.get('message'),
                **kwargs.get('extra', {})
            )
        elif operation == 'log_error':
            return _log_error_implementation(
                kwargs.get('message'),
                kwargs.get('error'),
                **kwargs.get('extra', {})
            )
        elif operation == 'log_warning':
            return _log_warning_implementation(
                kwargs.get('message'),
                **kwargs.get('extra', {})
            )
        elif operation == 'log_debug':
            return _log_debug_implementation(
                kwargs.get('message'),
                **kwargs.get('extra', {})
            )
        else:
            raise ValueError(f"Unknown LOGGING operation: {operation}")
    
    elif interface == GatewayInterface.SECURITY:
        from security_core import (
            _validate_request_implementation,
            _validate_token_implementation,
            _encrypt_data_implementation,
            _decrypt_data_implementation
        )
        
        if operation == 'validate_request':
            return _validate_request_implementation(kwargs.get('request_data'))
        elif operation == 'validate_token':
            return _validate_token_implementation(kwargs.get('token'))
        elif operation == 'encrypt':
            return _encrypt_data_implementation(kwargs.get('data'))
        elif operation == 'decrypt':
            return _decrypt_data_implementation(kwargs.get('encrypted_data'))
        else:
            raise ValueError(f"Unknown SECURITY operation: {operation}")
    
    elif interface == GatewayInterface.METRICS:
        from metrics_core import (
            _record_metric_implementation,
            _increment_counter_implementation,
            _get_metrics_implementation
        )
        
        if operation == 'record':
            return _record_metric_implementation(
                kwargs.get('metric_name'),
                kwargs.get('value'),
                kwargs.get('dimensions', {})
            )
        elif operation == 'increment':
            return _increment_counter_implementation(
                kwargs.get('counter_name'),
                kwargs.get('value', 1)
            )
        elif operation == 'get_metrics':
            return _get_metrics_implementation()
        else:
            raise ValueError(f"Unknown METRICS operation: {operation}")
    
    elif interface == GatewayInterface.CONFIG:
        # Phase 3: Configuration system routing
        from config_core import (
            _initialize_implementation,
            _get_parameter_implementation,
            _set_parameter_implementation,
            _get_category_config_implementation,
            _reload_config_implementation,
            _switch_preset_implementation,
            _get_state_implementation,
            _load_from_environment_implementation,
            _load_from_file_implementation,
            _load_ha_config_implementation,
            _validate_ha_config_implementation,
            _validate_all_sections_implementation
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
            return _get_category_config_implementation(
                kwargs.get('category')
            )
        elif operation == 'reload_config':
            return _reload_config_implementation(
                kwargs.get('validate', True)
            )
        elif operation == 'switch_preset':
            return _switch_preset_implementation(
                kwargs.get('preset_name')
            )
        elif operation == 'get_state':
            return _get_state_implementation()
        elif operation == 'load_from_environment':
            return _load_from_environment_implementation()
        elif operation == 'load_from_file':
            return _load_from_file_implementation(
                kwargs.get('filepath')
            )
        elif operation == 'load_ha_config':
            return _load_ha_config_implementation()
        elif operation == 'validate_ha_config':
            return _validate_ha_config_implementation(
                kwargs.get('ha_config')
            )
        elif operation == 'validate_all_sections':
            return _validate_all_sections_implementation()
        else:
            raise ValueError(f"Unknown CONFIG operation: {operation}")
    
    elif interface == GatewayInterface.HTTP_CLIENT:
        from http_client_core import (
            _make_request_implementation,
            _make_get_implementation,
            _make_post_implementation
        )
        
        if operation == 'request':
            return _make_request_implementation(
                kwargs.get('method'),
                kwargs.get('url'),
                **kwargs
            )
        elif operation == 'get':
            return _make_get_implementation(
                kwargs.get('url'),
                **kwargs
            )
        elif operation == 'post':
            return _make_post_implementation(
                kwargs.get('url'),
                kwargs.get('data'),
                **kwargs
            )
        else:
            raise ValueError(f"Unknown HTTP_CLIENT operation: {operation}")
    
    elif interface == GatewayInterface.SINGLETON:
        from singleton_core import (
            _get_singleton_implementation,
            _register_singleton_implementation,
            _cleanup_singleton_implementation
        )
        
        if operation == 'get':
            return _get_singleton_implementation(kwargs.get('singleton_name'))
        elif operation == 'register':
            return _register_singleton_implementation(
                kwargs.get('singleton_name'),
                kwargs.get('instance')
            )
        elif operation == 'cleanup':
            return _cleanup_singleton_implementation(kwargs.get('target_id'))
        else:
            raise ValueError(f"Unknown SINGLETON operation: {operation}")
    
    elif interface == GatewayInterface.CIRCUIT_BREAKER:
        from circuit_breaker_core import (
            _check_circuit_implementation,
            _record_success_implementation,
            _record_failure_implementation
        )
        
        if operation == 'check':
            return _check_circuit_implementation(kwargs.get('circuit_name'))
        elif operation == 'record_success':
            return _record_success_implementation(kwargs.get('circuit_name'))
        elif operation == 'record_failure':
            return _record_failure_implementation(kwargs.get('circuit_name'))
        else:
            raise ValueError(f"Unknown CIRCUIT_BREAKER operation: {operation}")
    
    elif interface == GatewayInterface.INITIALIZATION:
        from initialization_core import (
            _execute_initialization_implementation,
            _record_stage_implementation
        )
        
        if operation == 'execute':
            return _execute_initialization_implementation(
                kwargs.get('init_type')
            )
        elif operation == 'record_stage':
            return _record_stage_implementation(
                kwargs.get('stage'),
                kwargs.get('status')
            )
        else:
            raise ValueError(f"Unknown INITIALIZATION operation: {operation}")
    
    elif interface == GatewayInterface.UTILITY:
        from utility_core import (
            _create_success_response_implementation,
            _create_error_response_implementation,
            _parse_json_implementation,
            _generate_correlation_id_implementation,
            _sanitize_response_implementation
        )
        
        if operation == 'success_response':
            return _create_success_response_implementation(
                kwargs.get('message'),
                kwargs.get('data')
            )
        elif operation == 'error_response':
            return _create_error_response_implementation(
                kwargs.get('message'),
                kwargs.get('error_code')
            )
        elif operation == 'parse_json':
            return _parse_json_implementation(kwargs.get('json_string'))
        elif operation == 'correlation_id':
            return _generate_correlation_id_implementation()
        elif operation == 'sanitize':
            return _sanitize_response_implementation(kwargs.get('data'))
        else:
            raise ValueError(f"Unknown UTILITY operation: {operation}")
    
    else:
        raise ValueError(f"Unknown interface: {interface}")


# ===== CACHE INTERFACE FUNCTIONS =====

def cache_get(key: str, default_value=None):
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default_value=default_value)


def cache_set(key: str, value, ttl: int = 300):
    """Set value in cache."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)


def cache_delete(key: str):
    """Delete value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear(pattern: str = None):
    """Clear cache entries."""
    return execute_operation(GatewayInterface.CACHE, 'clear', pattern=pattern)


# ===== LOGGING INTERFACE FUNCTIONS =====

def log_info(message: str, **extra):
    """Log info message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)


def log_error(message: str, error: Exception = None, **extra):
    """Log error message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, extra=extra)


def log_warning(message: str, **extra):
    """Log warning message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, extra=extra)


def log_debug(message: str, **extra):
    """Log debug message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, extra=extra)


# ===== SECURITY INTERFACE FUNCTIONS =====

def validate_request(request_data: Dict[str, Any]) -> bool:
    """Validate request data."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)


def validate_token(token: str) -> bool:
    """Validate authentication token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt encrypted data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data)


# ===== METRICS INTERFACE FUNCTIONS =====

def record_metric(metric_name: str, value: float, dimensions: Dict[str, Any] = None):
    """Record metric value."""
    return execute_operation(
        GatewayInterface.METRICS,
        'record',
        metric_name=metric_name,
        value=value,
        dimensions=dimensions or {}
    )


def increment_counter(counter_name: str, value: int = 1):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', counter_name=counter_name, value=value)


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


def parse_json_safely(json_string: str) -> Optional[Dict]:
    """Parse JSON safely."""
    return execute_operation(GatewayInterface.UTILITY, 'parse_json', json_string=json_string)


def generate_correlation_id() -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.UTILITY, 'correlation_id')


def sanitize_response_data(data: Any) -> Any:
    """Sanitize response data."""
    return execute_operation(GatewayInterface.UTILITY, 'sanitize', data=data)


# ===== FAST PATH MANAGEMENT =====

def enable_fast_path():
    """Enable fast path optimization."""
    global _FAST_PATH_ENABLED
    _FAST_PATH_ENABLED = True
    log_info("Fast path enabled")


def disable_fast_path():
    """Disable fast path optimization."""
    global _FAST_PATH_ENABLED
    _FAST_PATH_ENABLED = False
    log_info("Fast path disabled")


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return _FAST_PATH_STATS.copy()


def reset_fast_path_stats():
    """Reset fast path statistics."""
    _FAST_PATH_STATS['total_calls'] = 0
    _FAST_PATH_STATS['fast_path_hits'] = 0
    _FAST_PATH_STATS['fast_path_misses'] = 0


# ===== GATEWAY STATISTICS =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        'fast_path_enabled': _FAST_PATH_ENABLED,
        'fast_path_stats': _FAST_PATH_STATS.copy(),
        'loadable_modules': list(_LOADABLE_MODULES.keys()),
        'interfaces': [i.value for i in GatewayInterface]
    }


# EOF
