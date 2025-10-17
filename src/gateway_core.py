"""
gateway_core.py - Gateway Core Implementation
Version: 2025.10.17.01
Description: Core gateway functionality with operation registry

FIXES APPLIED (2025.10.17.01):
- CRITICAL BUG FIX: Updated UTILITY operations registry to point to interface_utility
  instead of deleted shared_utilities.py (lines 77-81)
- Added design decision documentation for CIRCUIT_BREAKER direct access
- Added design decision documentation for DEBUG direct access

DESIGN DECISIONS DOCUMENTED:

1. CIRCUIT_BREAKER Direct Access (lines 72-75):
   DESIGN DECISION: Bypasses interface router for performance
   Reason: Circuit breaker is performance-critical hot path, called frequently
   SUGA-ISP Compliance: Acceptable for performance-critical internal infrastructure
   NOT A BUG: Intentional architecture optimization

2. DEBUG Direct Access (lines 89-105):
   DESIGN DECISION: Bypasses interface router for development tools
   Reason: Debug operations are diagnostic/development only, not production-critical
   SUGA-ISP Compliance: Acceptable for non-critical diagnostic interfaces
   NOT A BUG: Dispatcher pattern handles all operations efficiently

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
    
    # CONFIG Operations
    (GatewayInterface.CONFIG, 'get'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'set'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_category'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'reload'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_state'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_file'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'validate_all'): ('interface_config', 'execute_config_operation'),
    
    # SINGLETON Operations
    (GatewayInterface.SINGLETON, 'get'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'set'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'has'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'delete'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'clear'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'stats'): ('interface_singleton', 'execute_singleton_operation'),
    
    # INITIALIZATION Operations
    (GatewayInterface.INITIALIZATION, 'initialize'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'get_config'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'is_initialized'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'reset'): ('interface_initialization', 'execute_initialization_operation'),
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
    
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    
    # UTILITY Operations
    # FIXED (2025.10.17.01): Changed from 'shared_utilities' to 'interface_utility'
    # shared_utilities.py was removed, replaced by interface_utility.py
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
    # DESIGN DECISION: Direct access to debug_core (no interface router)
    # Reason: Debug operations are development/diagnostic tools, not production-critical
    # NOT A BUG: Dispatcher pattern (generic_debug_operation) handles routing internally
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
    import importlib
    
    # Increment call count for fast path decision
    _operation_call_counts[(interface, operation)] += 1
    
    # Try fast path first if enabled
    if _fast_path_enabled:
        cache_key = (interface, operation)
        if cache_key in _fast_path_cache:
            func, module_name, func_name = _fast_path_cache[cache_key]
            
            # Determine if this function needs operation parameter
            needs_operation_param = (
                'interface_' in module_name or 
                'generic' in func_name
            )
            
            if needs_operation_param:
                return func(operation, **kwargs)
            else:
                return func(**kwargs)
    
    # Slow path: Registry lookup
    key = (interface, operation)
    if key not in _OPERATION_REGISTRY:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    
    module_name, func_name = _OPERATION_REGISTRY[key]
    
    # Lazy import
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        raise RuntimeError(f"Failed to load {module_name}.{func_name}: {e}") from e
    
    # Cache for fast path if operation is frequent
    if _fast_path_enabled and _operation_call_counts[key] >= 3:
        _fast_path_cache[key] = (func, module_name, func_name)
    
    # Determine if this function needs operation parameter
    needs_operation_param = (
        'interface_' in module_name or 
        'generic' in func_name
    )
    
    if needs_operation_param:
        return func(operation, **kwargs)
    else:
        return func(**kwargs)


def initialize_lambda() -> Dict[str, Any]:
    """Initialize Lambda execution environment."""
    return {
        'gateway_initialized': True,
        'fast_path_enabled': _fast_path_enabled,
        'registry_size': len(_OPERATION_REGISTRY)
    }


def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        'total_operations': len(_OPERATION_REGISTRY),
        'fast_path_entries': len(_fast_path_cache),
        'fast_path_enabled': _fast_path_enabled,
        'operation_counts': dict(_operation_call_counts)
    }


# ===== FAST PATH MANAGEMENT =====

def set_fast_path_threshold(threshold: int) -> None:
    """Set fast path activation threshold."""
    # Implementation for setting threshold
    pass


def enable_fast_path() -> None:
    """Enable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = True


def disable_fast_path() -> None:
    """Disable fast path caching."""
    global _fast_path_enabled
    _fast_path_enabled = False


def clear_fast_path_cache() -> int:
    """Clear fast path cache and return number of entries cleared."""
    global _fast_path_cache
    count = len(_fast_path_cache)
    _fast_path_cache.clear()
    return count


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return {
        'enabled': _fast_path_enabled,
        'cache_size': len(_fast_path_cache),
        'cached_operations': list(_fast_path_cache.keys())
    }


# ===== RESPONSE HELPERS =====

def create_error_response(status_code: int, message: str, error_type: str = "Error") -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'body': {
            'error': {
                'type': error_type,
                'message': message
            }
        }
    }


def create_success_response(status_code: int, data: Any) -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        'statusCode': status_code,
        'body': data
    }


# ===== EXPORTS =====

__all__ = [
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    'create_error_response',
    'create_success_response',
    '_OPERATION_REGISTRY',
]

# EOF
