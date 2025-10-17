"""
gateway_core.py - Gateway Core Implementation
Version: 2025.10.16.01
Description: Core gateway functionality with operation registry

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
from typing import Any, Dict, Optional, Tuple, Callable
from collections import defaultdict

# ===== INTERFACE ENUMERATION =====

class GatewayInterface(Enum):
    """Gateway interface enumeration."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    SINGLETON = "singleton"
    INITIALIZATION = "initialization"
    HTTP_CLIENT = "http_client"
    CIRCUIT_BREAKER = "circuit_breaker"
    UTILITY = "utility"
    WEBSOCKET = "websocket"
    DEBUG = "debug"


# ===== OPERATION REGISTRY =====
_OPERATION_REGISTRY: Dict[Tuple[GatewayInterface, str], Tuple[str, str]] = {
    # CACHE Operations
    (GatewayInterface.CACHE, 'get'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'set'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'exists'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'delete'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'clear'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'stats'): ('interface_cache', 'execute_cache_operation'),
    
    # LOGGING Operations
    (GatewayInterface.LOGGING, 'log'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_info'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_error'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_warning'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_debug'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_start'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_success'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_error'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_end'): ('interface_logging', 'execute_logging_operation'),
    
    # SECURITY Operations
    (GatewayInterface.SECURITY, 'validate_request'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_token'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'encrypt'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'decrypt'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'generate_correlation_id'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'hash'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'verify_hash'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'sanitize'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'sanitize_data'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_string'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_email'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_url'): ('interface_security', 'execute_security_operation'),
    
    # METRICS Operations
    (GatewayInterface.METRICS, 'record'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_metric'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'increment'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'increment_counter'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_stats'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_operation'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_error'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_cache'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_api'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_response'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_http'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_circuit_breaker'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_response_metrics'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_http_metrics'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_circuit_breaker_metrics'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_dispatcher_timing'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_dispatcher_stats'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_dispatcher_metrics'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_operation_metrics'): ('interface_metrics', 'execute_metrics_operation'),
    
    # CONFIG Operations
    (GatewayInterface.CONFIG, 'initialize'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'set'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_category'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'reload'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_state'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_file'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'validate'): ('interface_config', 'execute_config_operation'),
    
    # SINGLETON Operations
    (GatewayInterface.SINGLETON, 'get'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'has'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'delete'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'clear'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'get_stats'): ('interface_singleton', 'execute_singleton_operation'),
    
    # INITIALIZATION Operations
    (GatewayInterface.INITIALIZATION, 'initialize'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'get_status'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'set_flag'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'get_flag'): ('interface_initialization', 'execute_initialization_operation'),
    
    # HTTP_CLIENT Operations
    (GatewayInterface.HTTP_CLIENT, 'request'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('interface_http', 'execute_http_operation'),
    
    # CIRCUIT_BREAKER Operations
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('circuit_breaker_core', 'get_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('circuit_breaker_core', 'execute_with_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('circuit_breaker_core', 'get_all_breakers_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('circuit_breaker_core', 'reset_all_breakers_implementation'),
    
    # UTILITY Operations
    (GatewayInterface.UTILITY, 'format_response'): ('interface_utility', 'execute_utility_operation'),
    (GatewayInterface.UTILITY, 'parse_json'): ('interface_utility', 'execute_utility_operation'),
    (GatewayInterface.UTILITY, 'safe_get'): ('interface_utility', 'execute_utility_operation'),
    (GatewayInterface.UTILITY, 'generate_uuid'): ('interface_utility', 'execute_utility_operation'),
    (GatewayInterface.UTILITY, 'get_timestamp'): ('interface_utility', 'execute_utility_operation'),
    
    # WEBSOCKET Operations
    (GatewayInterface.WEBSOCKET, 'connect'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'send'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'close'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'request'): ('interface_websocket', 'execute_websocket_operation'),
    
    # DEBUG Operations
    (GatewayInterface.DEBUG, 'check_component_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'check_gateway_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'diagnose_system_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_debug_tests'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_system_architecture'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_system_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_optimization_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_dispatcher_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_operation_metrics'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_gateway_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'verify_registry_operations'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_operation_signatures'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_interface_compliance'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'check_circular_dependencies'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'measure_execution_times'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_performance_profile'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_memory_profile'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'check_memory_usage'): ('debug_core', 'generic_debug_operation'),
}

# ===== FAST PATH CACHE =====
_fast_path_cache: Dict[Tuple[GatewayInterface, str], Tuple[Callable, str, str]] = {}
_fast_path_enabled = True
_operation_call_counts = defaultdict(int)

# ===== CORE EXECUTION ENGINE =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Execute operation through the gateway.
    
    CRITICAL DISPATCHER PATTERN (2025.10.16.06):
    Some functions act as dispatchers and need the operation parameter:
    - interface_* modules: execute_*_operation(operation, **kwargs)
    - debug_core module: generic_debug_operation(operation, **kwargs)
    - Any function with 'generic' in the name
    
    Other functions are direct implementations and don't need operation parameter.
    """
    key = (interface, operation)
    
    # Track operation calls
    _operation_call_counts[key] += 1
    
    # Check fast path cache
    if _fast_path_enabled and key in _fast_path_cache:
        func, module_name, func_name = _fast_path_cache[key]
        return _call_function(func, func_name, module_name, operation, **kwargs)
    
    # Lookup in registry
    if key not in _OPERATION_REGISTRY:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    
    module_name, func_name = _OPERATION_REGISTRY[key]
    
    # Dynamic import
    import importlib
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        
        # Cache for fast path
        if _fast_path_enabled:
            _fast_path_cache[key] = (func, module_name, func_name)
        
        return _call_function(func, func_name, module_name, operation, **kwargs)
        
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}: {e}")
    except AttributeError as e:
        raise AttributeError(f"Function {func_name} not found in {module_name}: {e}")


def _call_function(func: Callable, func_name: str, module_name: str, operation: str, **kwargs) -> Any:
    """
    Call function with appropriate parameters based on function type.
    
    Dispatcher functions (interface routers, generic handlers) need operation parameter.
    Direct implementation functions don't need operation parameter.
    """
    # Dispatcher pattern detection
    is_dispatcher = (
        func_name.startswith('execute_') or
        func_name.startswith('generic_') or
        'dispatch' in func_name.lower() or
        module_name.startswith('interface_')
    )
    
    if is_dispatcher:
        return func(operation, **kwargs)
    else:
        return func(**kwargs)


# ===== FAST PATH MANAGEMENT =====

def set_fast_path_threshold(threshold: int) -> None:
    """Set the call count threshold for fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = threshold > 0

def enable_fast_path() -> None:
    """Enable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = True

def disable_fast_path() -> None:
    """Disable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = False

def clear_fast_path_cache() -> None:
    """Clear the fast path cache."""
    global _fast_path_cache
    _fast_path_cache.clear()

def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return {
        'enabled': _fast_path_enabled,
        'cached_operations': len(_fast_path_cache),
        'cache_entries': list(_fast_path_cache.keys())
    }

# ===== INITIALIZATION =====

def initialize_lambda(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize Lambda environment."""
    result = {
        'status': 'initialized',
        'registry_size': len(_OPERATION_REGISTRY),
        'fast_path_enabled': _fast_path_enabled
    }
    
    if context:
        result['context'] = context
    
    return result

# ===== STATISTICS AND DEBUGGING =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway operation statistics."""
    # FIXED 2025-10-16: Convert tuple keys to strings for JSON serialization
    operation_counts_json_safe = {}
    for key, count in _operation_call_counts.items():
        interface_name = key[0].value
        operation_name = key[1]
        json_key = f"{interface_name}.{operation_name}"
        operation_counts_json_safe[json_key] = count
    
    return {
        'total_operations': len(_OPERATION_REGISTRY),
        'operation_call_counts': operation_counts_json_safe,
        'interfaces': {
            iface.value: sum(1 for k in _OPERATION_REGISTRY if k[0] == iface) 
            for iface in GatewayInterface
        },
        'fast_path_enabled': _fast_path_enabled,
        'fast_path_cache_size': len(_fast_path_cache)
    }

def create_error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'body': {
            'error': message,
            'success': False
        }
    }

def create_success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        'statusCode': status_code,
        'body': {
            'data': data,
            'success': True
        }
    }

# ===== EXPORTS =====

__all__ = [
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    '_OPERATION_REGISTRY',
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    'create_error_response',
    'create_success_response',
]

# EOF
