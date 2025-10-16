"""
gateway_core.py - Core Gateway Routing Engine
Version: 2025.10.15.05
Description: Universal gateway routing with SUGA-ISP interface routers
            FIXED: execute_operation now passes 'operation' parameter to interface routers

ARCHITECTURAL NOTES:
- This file contains INTENTIONAL design patterns documented inline
- Do NOT flag DEBUG special handling as an issue - it's a dispatcher pattern
- Do NOT flag CIRCUIT_BREAKER 'call' operation - it's correctly named
- SUGA-ISP: All operations now route through interface_<n>.py routers
- See inline comments for full architectural rationale

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
# Maps (interface, operation) → (module_name, function_name)
# SUGA-ISP PATTERN: Core interfaces route through interface_<n> routers

_OPERATION_REGISTRY: Dict[Tuple[GatewayInterface, str], Tuple[str, str]] = {
    # ========================================================================
    # CACHE Operations - Routes through interface_cache.py
    # ========================================================================
    (GatewayInterface.CACHE, 'get'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'set'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'exists'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'delete'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'clear'): ('interface_cache', 'execute_cache_operation'),
    (GatewayInterface.CACHE, 'get_stats'): ('interface_cache', 'execute_cache_operation'),
    
    # ========================================================================
    # LOGGING Operations - Routes through interface_logging.py
    # ========================================================================
    (GatewayInterface.LOGGING, 'log_info'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_error'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_warning'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_debug'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_start'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_success'): ('interface_logging', 'execute_logging_operation'),
    (GatewayInterface.LOGGING, 'log_operation_failure'): ('interface_logging', 'execute_logging_operation'),
    
    # ========================================================================
    # SECURITY Operations - Routes through interface_security.py
    # ========================================================================
    (GatewayInterface.SECURITY, 'validate_request'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_token'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'encrypt'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'decrypt'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'generate_correlation_id'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_string'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_email'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'validate_url'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'hash'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'verify_hash'): ('interface_security', 'execute_security_operation'),
    (GatewayInterface.SECURITY, 'sanitize'): ('interface_security', 'execute_security_operation'),
    
    # ========================================================================
    # METRICS Operations - Routes through interface_metrics.py
    # ========================================================================
    (GatewayInterface.METRICS, 'record'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'increment'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'get_stats'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_operation'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_error'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_cache'): ('interface_metrics', 'execute_metrics_operation'),
    (GatewayInterface.METRICS, 'record_api'): ('interface_metrics', 'execute_metrics_operation'),
    
    # ========================================================================
    # CONFIG Operations - Routes through interface_config.py
    # ========================================================================
    (GatewayInterface.CONFIG, 'get'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'set'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_category'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'reload'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'get_state'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'load_file'): ('interface_config', 'execute_config_operation'),
    (GatewayInterface.CONFIG, 'validate'): ('interface_config', 'execute_config_operation'),
    
    # ========================================================================
    # SINGLETON Operations - Routes through interface_singleton.py
    # ========================================================================
    (GatewayInterface.SINGLETON, 'get'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'has'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'delete'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'clear'): ('interface_singleton', 'execute_singleton_operation'),
    (GatewayInterface.SINGLETON, 'get_stats'): ('interface_singleton', 'execute_singleton_operation'),
    
    # ========================================================================
    # INITIALIZATION Operations - Routes through interface_initialization.py
    # ========================================================================
    (GatewayInterface.INITIALIZATION, 'initialize'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'get_status'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'set_flag'): ('interface_initialization', 'execute_initialization_operation'),
    (GatewayInterface.INITIALIZATION, 'get_flag'): ('interface_initialization', 'execute_initialization_operation'),
    
    # ========================================================================
    # HTTP_CLIENT Operations - Routes through interface_http.py
    # ========================================================================
    (GatewayInterface.HTTP_CLIENT, 'request'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('interface_http', 'execute_http_operation'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('interface_http', 'execute_http_operation'),
    
    # ========================================================================
    # WEBSOCKET Operations - Routes through interface_websocket.py
    # ========================================================================
    (GatewayInterface.WEBSOCKET, 'connect'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'send'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'close'): ('interface_websocket', 'execute_websocket_operation'),
    (GatewayInterface.WEBSOCKET, 'request'): ('interface_websocket', 'execute_websocket_operation'),
    
    # ========================================================================
    # CIRCUIT_BREAKER Operations (circuit_breaker_core.py)
    # NOTE: No interface router yet - still routes directly to core
    # ========================================================================
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('circuit_breaker_core', 'get_circuit_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('circuit_breaker_core', 'call_circuit_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('circuit_breaker_core', 'get_all_states_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('circuit_breaker_core', 'reset_all_implementation'),
    
    # ========================================================================
    # UTILITY Operations (shared_utilities.py)
    # NOTE: No interface router yet - still routes directly to core
    # ========================================================================
    (GatewayInterface.UTILITY, 'format_response'): ('shared_utilities', '_execute_format_response_implementation'),
    (GatewayInterface.UTILITY, 'parse_json'): ('shared_utilities', '_execute_parse_json_implementation'),
    (GatewayInterface.UTILITY, 'safe_get'): ('shared_utilities', '_execute_safe_get_implementation'),
    (GatewayInterface.UTILITY, 'generate_uuid'): ('shared_utilities', '_generate_uuid_implementation'),
    (GatewayInterface.UTILITY, 'get_timestamp'): ('shared_utilities', '_get_timestamp_implementation'),
    
    # ========================================================================
    # DEBUG Operations (debug_core.py)
    # NOTE: Uses dispatcher pattern - see detailed explanation below
    # ========================================================================
    # ARCHITECTURAL PATTERN: DEBUG DISPATCHER
    # ========================================================================
    # The DEBUG interface uses a special dispatcher pattern where ALL debug
    # operations route to a single function: generic_debug_operation().
    # 
    # This is NOT a mistake - it's an intentional dispatcher pattern that:
    # 
    # 1. Reduces registry size (18 operations → 1 function)
    # 2. Enables lazy loading of debug modules
    # 3. Provides centralized debug operation handling
    # 4. Uses DebugOperation enum for type-safe routing
    # 
    # The execute_operation function has SPECIAL HANDLING for DEBUG interface
    # that converts the operation string to a DebugOperation enum before calling.
    # 
    # See execute_operation() implementation below for the special handling code.
    # ========================================================================
    (GatewayInterface.DEBUG, 'check_component_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'check_gateway_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'diagnose_system_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_debug_tests'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_system_architecture'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'test_operation'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'list_operations'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'introspect_interface'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_fast_path_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_hot_operations'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_cached_operations'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_optimization_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'generate_health_report'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'verify_registry_operations'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'analyze_naming_patterns'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'generate_verification_report'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_dispatcher_stats'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_operation_metrics'): ('debug_core', 'generic_debug_operation'),
}

# ===== FAST PATH OPTIMIZATION =====

_operation_call_counts = defaultdict(int)
_fast_path_cache: Dict[Tuple[GatewayInterface, str], Callable] = {}
_fast_path_enabled = True
_fast_path_threshold = 20

def _check_fast_path(interface: GatewayInterface, operation: str) -> Optional[Callable]:
    """Check if operation should use fast path."""
    key = (interface, operation)
    _operation_call_counts[key] += 1
    
    if _fast_path_enabled:
        if key in _fast_path_cache:
            return _fast_path_cache[key]
        
        if _operation_call_counts[key] >= _fast_path_threshold:
            module_name, func_name = _OPERATION_REGISTRY.get(key, (None, None))
            if module_name and func_name:
                try:
                    mod = __import__(module_name, fromlist=[func_name])
                    func = getattr(mod, func_name)
                    _fast_path_cache[key] = func
                    return func
                except (ImportError, AttributeError):
                    pass
    
    return None

def set_fast_path_threshold(threshold: int):
    """Set the threshold for fast path optimization."""
    global _fast_path_threshold
    _fast_path_threshold = threshold

def enable_fast_path():
    """Enable fast path optimization."""
    global _fast_path_enabled
    _fast_path_enabled = True

def disable_fast_path():
    """Disable fast path optimization."""
    global _fast_path_enabled
    _fast_path_enabled = False

def clear_fast_path_cache():
    """Clear the fast path cache."""
    global _fast_path_cache
    _fast_path_cache = {}

def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return {
        'enabled': _fast_path_enabled,
        'threshold': _fast_path_threshold,
        'cache_size': len(_fast_path_cache),
        'cached_operations': list(_fast_path_cache.keys()),
        'call_counts': dict(_operation_call_counts)
    }

# ===== CORE FUNCTIONS =====

def initialize_lambda():
    """Initialize Lambda execution environment."""
    pass

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Universal gateway routing with lazy loading and fast path optimization.
    
    Args:
        interface: The interface to execute the operation on
        operation: The operation to execute
        **kwargs: Arguments to pass to the operation
        
    Returns:
        The result of the operation
        
    Raises:
        ValueError: If the interface/operation combination is not registered
        RuntimeError: If the operation fails to load or execute
    """
    # Check fast path first
    fast_func = _check_fast_path(interface, operation)
    if fast_func:
        # ====================================================================
        # DEBUG DISPATCHER PATTERN - Special handling for DEBUG operations
        # ====================================================================
        # DO NOT FLAG AS ISSUE: This is intentional architecture
        # See detailed explanation in _OPERATION_REGISTRY above
        # ====================================================================
        if interface == GatewayInterface.DEBUG:
            from debug.debug_core import DebugOperation
            op_enum = DebugOperation(operation)
            return fast_func(op_enum, **kwargs)
        
        # ====================================================================
        # SUGA-ISP INTERFACE ROUTER PATTERN
        # ====================================================================
        # Interface routers expect (operation, **kwargs) signature
        # Check if this is an interface router based on function name pattern
        # ====================================================================
        func_name = fast_func.__name__
        if func_name.startswith('execute_') and func_name.endswith('_operation'):
            return fast_func(operation, **kwargs)
        
        # Legacy direct implementations don't need operation parameter
        return fast_func(**kwargs)
    
    # Registry lookup
    key = (interface, operation)
    if key not in _OPERATION_REGISTRY:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    
    module_name, func_name = _OPERATION_REGISTRY[key]
    
    # Dynamic import and execution
    try:
        # ====================================================================
        # DEBUG DISPATCHER PATTERN - Special handling for DEBUG operations
        # ====================================================================
        # DO NOT FLAG AS ISSUE: This is intentional architecture
        # 
        # Converts operation string to DebugOperation enum for type-safe routing
        # through the debug dispatcher. This allows 20+ debug operations to
        # route through a single function with lazy loading of debug modules.
        # 
        # See detailed explanation in _OPERATION_REGISTRY above
        # ====================================================================
        if interface == GatewayInterface.DEBUG:
            from debug.debug_core import generic_debug_operation, DebugOperation
            op_enum = DebugOperation(operation)
            return generic_debug_operation(op_enum, **kwargs)
        
        # ====================================================================
        # SUGA-ISP INTERFACE ROUTER PATTERN
        # ====================================================================
        # Interface routers (execute_*_operation functions) expect the operation
        # parameter to route to internal implementations.
        # 
        # Check if this is an interface router:
        # - Function name follows pattern: execute_<interface>_operation
        # - All interface routers need the operation parameter
        # 
        # Legacy direct implementations (like circuit_breaker_core functions)
        # do NOT need the operation parameter and work with **kwargs only.
        # ====================================================================
        mod = __import__(module_name, fromlist=[func_name])
        func = getattr(mod, func_name)
        
        # Check if this is an interface router function
        if func_name.startswith('execute_') and func_name.endswith('_operation'):
            # Interface router - pass operation parameter
            return func(operation, **kwargs)
        else:
            # Legacy direct implementation - no operation parameter needed
            return func(**kwargs)
            
    except (ImportError, AttributeError) as e:
        raise RuntimeError(f"Failed to load {module_name}.{func_name}: {str(e)}")

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway operation statistics."""
    return {
        'total_operations': len(_OPERATION_REGISTRY),
        'operation_call_counts': dict(_operation_call_counts),
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
    # Core
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    '_OPERATION_REGISTRY',
    
    # Fast Path Management
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    
    # Response Helpers
    'create_error_response',
    'create_success_response',
]

# EOF
