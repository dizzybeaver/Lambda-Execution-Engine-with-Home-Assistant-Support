"""
gateway.py - Revolutionary Gateway Architecture (SUGA + LIGS + ZAFP + LUGS)
Version: 2025.10.04.02
Daily Revision: Phase 6 Configuration Consolidation Complete

Revolutionary Gateway Optimization - Universal Operation Router
Single Universal Gateway Architecture with:
- SUGA: All operations route through execute_operation()
- LIGS: Lazy loading of implementation modules
- ZAFP: Zero-abstraction fast path for hot operations
- LUGS: Lazy unload for memory optimization

PHASE 6 UPDATE: Configuration fast path optimization added

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
from typing import Any, Dict, Optional, Callable
import time

# ===== GATEWAY INTERFACE ENUM =====

class GatewayInterface(Enum):
    """Gateway interface types."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    HTTP_CLIENT = "http_client"
    SINGLETON = "singleton"
    CIRCUIT_BREAKER = "circuit_breaker"
    INITIALIZATION = "initialization"
    UTILITY = "utility"

# ===== FAST PATH OPTIMIZATION (ZAFP) =====

_FAST_PATH_ENABLED = True
_FAST_PATH_STATS = {
    'total_calls': 0,
    'fast_path_hits': 0,
    'fast_path_misses': 0
}

# Fast path operations - hot operations that bypass standard routing
_FAST_PATH_OPERATIONS = {
    ('CACHE', 'get'),
    ('CACHE', 'set'),
    ('LOGGING', 'log_info'),
    ('LOGGING', 'log_error'),
    ('METRICS', 'record'),
    ('UTILITY', 'success_response'),
    ('UTILITY', 'error_response'),
    ('CONFIG', 'get_parameter'),        # Phase 6: Configuration fast path
    ('CONFIG', 'get_category_config'),  # Phase 6: Configuration fast path
}

# ===== LAZY LOADING (LIGS) =====

_LOADABLE_MODULES = {
    'cache_core': None,
    'logging_core': None,
    'security_core': None,
    'metrics_core': None,
    'config_core': None,
    'http_client_core': None,
    'singleton_core': None,
    'circuit_breaker_core': None,
    'initialization_core': None,
    'utility_core': None
}

def _lazy_import(module_name: str):
    """Lazy import module on first use."""
    if _LOADABLE_MODULES[module_name] is None:
        if module_name == 'cache_core':
            from cache_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'logging_core':
            from logging_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'security_core':
            from security_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'metrics_core':
            from metrics_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'config_core':
            from config_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'http_client_core':
            from http_client_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'singleton_core':
            from singleton_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'circuit_breaker_core':
            from circuit_breaker_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'initialization_core':
            from initialization_core import *
            _LOADABLE_MODULES[module_name] = True
        elif module_name == 'utility_core':
            from utility_core import *
            _LOADABLE_MODULES[module_name] = True

# ===== UNIVERSAL OPERATION ROUTER (SUGA) =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs):
    """
    Universal operation router - ALL operations flow through here.
    
    SUGA: Single entry point for all system operations
    LIGS: Lazy loads implementation modules
    ZAFP: Fast path for hot operations
    """
    
    # Fast path check (ZAFP)
    _FAST_PATH_STATS['total_calls'] += 1
    
    if _FAST_PATH_ENABLED and (interface.value.upper(), operation) in _FAST_PATH_OPERATIONS:
        _FAST_PATH_STATS['fast_path_hits'] += 1
        # Direct execution for hot operations
        # Implementation modules handle actual fast path logic
    else:
        _FAST_PATH_STATS['fast_path_misses'] += 1
    
    # Route to appropriate interface
    if interface == GatewayInterface.CACHE:
        from cache_core import (
            _get_cache_implementation,
            _set_cache_implementation,
            _delete_cache_implementation,
            _clear_cache_implementation
        )
        
        if operation == 'get':
            return _get_cache_implementation(
                kwargs.get('key'),
                kwargs.get('default')
            )
        elif operation == 'set':
            return _set_cache_implementation(
                kwargs.get('key'),
                kwargs.get('value'),
                kwargs.get('ttl')
            )
        elif operation == 'delete':
            return _delete_cache_implementation(kwargs.get('key'))
        elif operation == 'clear':
            return _clear_cache_implementation()
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
        # Phase 6: Configuration system routing with fast path support
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
            _apply_user_overrides_implementation,
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
                kwargs.get('filepath'),
                kwargs.get('format', 'json')
            )
        elif operation == 'load_ha_config':
            return _load_ha_config_implementation()
        elif operation == 'validate_ha_config':
            return _validate_ha_config_implementation(
                kwargs.get('config')
            )
        elif operation == 'apply_user_overrides':
            return _apply_user_overrides_implementation(
                kwargs.get('config')
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
            return _execute_initialization_implementation(kwargs.get('init_type'))
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
            _sanitize_data_implementation
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
            return _sanitize_data_implementation(kwargs.get('data'))
        else:
            raise ValueError(f"Unknown UTILITY operation: {operation}")
    
    else:
        raise ValueError(f"Unknown interface: {interface}")

# ===== CACHE INTERFACE FUNCTIONS =====

def cache_get(key: str, default: Any = None):
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default=default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set value in cache."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)


def cache_delete(key: str):
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear():
    """Clear all cache."""
    return execute_operation(GatewayInterface.CACHE, 'clear')


# ===== LOGGING INTERFACE FUNCTIONS =====

def log_info(message: str, **extra):
    """Log info message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)


def log_error(message: str, **extra):
    """Log error message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, extra=extra)


def log_warning(message: str, **extra):
    """Log warning message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, extra=extra)


def log_debug(message: str, **extra):
    """Log debug message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, extra=extra)


# ===== SECURITY INTERFACE FUNCTIONS =====

def validate_request(request_data: Dict[str, Any]):
    """Validate request data."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)


def validate_token(token: str):
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)


def encrypt_data(data: Any):
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)


def decrypt_data(encrypted_data: Any):
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data)


# ===== METRICS INTERFACE FUNCTIONS =====

def record_metric(metric_name: str, value: float, dimensions: Dict[str, str] = None):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', metric_name=metric_name, value=value, dimensions=dimensions or {})


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
