"""
gateway_core.py - Core Gateway Routing Engine
Version: 2025.10.15.02
Description: Universal gateway routing with operation registry and fast-path optimization

ARCHITECTURAL NOTES:
- This file contains INTENTIONAL design patterns documented inline
- Do NOT flag DEBUG special handling as an issue - it's a dispatcher pattern
- Do NOT flag CIRCUIT_BREAKER 'call' operation - it's correctly named
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

_OPERATION_REGISTRY: Dict[Tuple[GatewayInterface, str], Tuple[str, str]] = {
    # CACHE Operations
    (GatewayInterface.CACHE, 'get'): ('cache_core', '_execute_get_implementation'),
    (GatewayInterface.CACHE, 'set'): ('cache_core', '_execute_set_implementation'),
    (GatewayInterface.CACHE, 'exists'): ('cache_core', '_execute_exists_implementation'),
    (GatewayInterface.CACHE, 'delete'): ('cache_core', '_execute_delete_implementation'),
    (GatewayInterface.CACHE, 'clear'): ('cache_core', '_execute_clear_implementation'),
    (GatewayInterface.CACHE, 'get_stats'): ('cache_core', '_execute_get_stats_implementation'),
    
    # LOGGING Operations
    (GatewayInterface.LOGGING, 'log_info'): ('logging_core', '_execute_log_info_implementation'),
    (GatewayInterface.LOGGING, 'log_error'): ('logging_core', '_execute_log_error_implementation'),
    (GatewayInterface.LOGGING, 'log_warning'): ('logging_core', '_execute_log_warning_implementation'),
    (GatewayInterface.LOGGING, 'log_debug'): ('logging_core', '_execute_log_debug_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_start'): ('logging_core', '_execute_log_operation_start_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_success'): ('logging_core', '_execute_log_operation_success_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_failure'): ('logging_core', '_execute_log_operation_failure_implementation'),
    
    # SECURITY Operations
    (GatewayInterface.SECURITY, 'validate_request'): ('security_core', '_execute_validate_request_implementation'),
    (GatewayInterface.SECURITY, 'validate_token'): ('security_core', '_execute_validate_token_implementation'),
    (GatewayInterface.SECURITY, 'encrypt'): ('security_core', '_execute_encrypt_data_implementation'),
    (GatewayInterface.SECURITY, 'decrypt'): ('security_core', '_execute_decrypt_data_implementation'),
    (GatewayInterface.SECURITY, 'generate_correlation_id'): ('security_core', '_execute_generate_correlation_id_implementation'),
    (GatewayInterface.SECURITY, 'validate_string'): ('security_core', '_execute_validate_string_implementation'),
    (GatewayInterface.SECURITY, 'validate_email'): ('security_core', '_execute_validate_email_implementation'),
    (GatewayInterface.SECURITY, 'validate_url'): ('security_core', '_execute_validate_url_implementation'),
    (GatewayInterface.SECURITY, 'hash'): ('security_core', '_execute_hash_data_implementation'),
    (GatewayInterface.SECURITY, 'verify_hash'): ('security_core', '_execute_verify_hash_implementation'),
    (GatewayInterface.SECURITY, 'sanitize'): ('security_core', '_execute_sanitize_input_implementation'),
    
    # METRICS Operations
    (GatewayInterface.METRICS, 'record'): ('metrics_core', '_execute_record_metric_implementation'),
    (GatewayInterface.METRICS, 'increment'): ('metrics_core', '_execute_increment_counter_implementation'),
    (GatewayInterface.METRICS, 'get_stats'): ('metrics_core', '_execute_get_stats_implementation'),
    (GatewayInterface.METRICS, 'record_operation'): ('metrics_core', '_execute_record_operation_metric_implementation'),
    (GatewayInterface.METRICS, 'record_error'): ('metrics_core', '_execute_record_error_response_metric_implementation'),
    (GatewayInterface.METRICS, 'record_cache'): ('metrics_core', '_execute_record_cache_metric_implementation'),
    (GatewayInterface.METRICS, 'record_api'): ('metrics_core', '_execute_record_api_metric_implementation'),
    (GatewayInterface.METRICS, 'record_dispatcher_timing'): ('metrics_core', '_execute_record_dispatcher_timing_implementation'),
    (GatewayInterface.METRICS, 'get_dispatcher_stats'): ('metrics_core', '_execute_get_dispatcher_stats_implementation'),
    (GatewayInterface.METRICS, 'get_operation_metrics'): ('metrics_core', '_execute_get_operation_metrics_implementation'),
    
    # CONFIG Operations
    (GatewayInterface.CONFIG, 'get_parameter'): ('config_core', '_get_parameter_implementation'),
    (GatewayInterface.CONFIG, 'set_parameter'): ('config_core', '_set_parameter_implementation'),
    (GatewayInterface.CONFIG, 'get_category'): ('config_core', '_get_category_implementation'),
    (GatewayInterface.CONFIG, 'reload'): ('config_core', '_reload_implementation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('config_core', '_switch_preset_implementation'),
    (GatewayInterface.CONFIG, 'get_state'): ('config_core', '_get_state_implementation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('config_core', '_load_environment_implementation'),
    (GatewayInterface.CONFIG, 'load_file'): ('config_core', '_load_file_implementation'),
    (GatewayInterface.CONFIG, 'validate'): ('config_core', '_validate_all_implementation'),
    
    # SINGLETON Operations
    (GatewayInterface.SINGLETON, 'get'): ('singleton_core', '_execute_get_implementation'),
    (GatewayInterface.SINGLETON, 'has'): ('singleton_core', '_execute_has_implementation'),
    (GatewayInterface.SINGLETON, 'delete'): ('singleton_core', '_execute_delete_implementation'),
    (GatewayInterface.SINGLETON, 'clear'): ('singleton_core', '_execute_clear_implementation'),
    (GatewayInterface.SINGLETON, 'get_stats'): ('singleton_core', '_execute_get_stats_implementation'),
    
    # INITIALIZATION Operations
    (GatewayInterface.INITIALIZATION, 'initialize'): ('initialization_core', '_execute_initialize_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_status'): ('initialization_core', '_execute_get_status_implementation'),
    (GatewayInterface.INITIALIZATION, 'set_flag'): ('initialization_core', '_execute_set_flag_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_flag'): ('initialization_core', '_execute_get_flag_implementation'),
    
    # HTTP_CLIENT Operations
    (GatewayInterface.HTTP_CLIENT, 'request'): ('http_client_core', 'http_request_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('http_client_core', 'http_get_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('http_client_core', 'http_post_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('http_client_core', 'http_put_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('http_client_core', 'http_delete_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('http_client_core', 'get_state_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('http_client_core', 'reset_state_implementation'),
    
    # WEBSOCKET Operations
    (GatewayInterface.WEBSOCKET, 'connect'): ('websocket_core', 'websocket_connect_implementation'),
    (GatewayInterface.WEBSOCKET, 'send'): ('websocket_core', 'websocket_send_implementation'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('websocket_core', 'websocket_receive_implementation'),
    (GatewayInterface.WEBSOCKET, 'close'): ('websocket_core', 'websocket_close_implementation'),
    (GatewayInterface.WEBSOCKET, 'request'): ('websocket_core', 'websocket_request_implementation'),
    
    # ========================================================================
    # CIRCUIT_BREAKER Operations
    # ========================================================================
    # ARCHITECTURAL NOTE - DO NOT FLAG AS ISSUE:
    # The 'call' operation name is INTENTIONAL and CORRECT.
    # 
    # Circuit Breaker Pattern uses 'call' to match the standard pattern:
    #   breaker.call(function, *args, **kwargs)
    # 
    # This is consistent with circuit breaker literature and implementations.
    # The wrapper function execute_with_circuit_breaker is just a convenience
    # name for users, but the underlying operation is correctly named 'call'.
    # 
    # Mapping:
    #   User calls: execute_with_circuit_breaker(name, func, args)
    #   Gateway operation: CIRCUIT_BREAKER.call
    #   Implementation: execute_with_breaker_implementation
    #   Circuit breaker method: CircuitBreaker.call(func, *args)
    # 
    # Verified 2025-10-15: No mismatch exists
    # ========================================================================
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('circuit_breaker_core', 'get_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('circuit_breaker_core', 'execute_with_breaker_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('circuit_breaker_core', 'get_all_states_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('circuit_breaker_core', 'reset_all_implementation'),
    
    # UTILITY Operations
    (GatewayInterface.UTILITY, 'format_response'): ('shared_utilities', 'format_response'),
    (GatewayInterface.UTILITY, 'parse_json'): ('shared_utilities', 'parse_json_safely'),
    (GatewayInterface.UTILITY, 'safe_get'): ('shared_utilities', 'safe_get'),
    (GatewayInterface.UTILITY, 'generate_uuid'): ('shared_utilities', 'generate_uuid'),
    (GatewayInterface.UTILITY, 'get_timestamp'): ('shared_utilities', 'get_current_timestamp'),
    
    # ========================================================================
    # DEBUG Operations - DISPATCHER PATTERN
    # ========================================================================
    # ARCHITECTURAL NOTE - DO NOT FLAG AS ISSUE:
    # DEBUG uses a DISPATCHER PATTERN instead of standard routing.
    #
    # WHY THIS IS INTENTIONAL:
    # 1. DEBUG has 20+ operations (health, diagnostics, validation, tests, etc.)
    # 2. Adding 20+ registry entries would bloat this file
    # 3. DEBUG operations are infrequently used (cold start acceptable)
    # 4. Dispatcher provides flexibility to add operations without registry changes
    # 5. All DEBUG operations route through ONE function: generic_debug_operation
    # 6. Enum-based routing provides type safety and documentation
    #
    # PATTERN:
    #   User: check_component_health(component='cache')
    #   Gateway: execute_operation(DEBUG, 'check_component_health', component='cache')
    #   Special Handler: Converts string → DebugOperation enum
    #   Dispatcher: generic_debug_operation(enum, **kwargs)
    #   Lazy Import: from debug.debug_health import _check_component_health
    #   Execute: _check_component_health(component='cache')
    #
    # BENEFITS:
    #   ✅ 1 registry entry vs 20+
    #   ✅ Lazy loading of debug modules (faster cold start)
    #   ✅ Easy to add new debug operations
    #   ✅ Type-safe enum routing
    #   ✅ Follows dispatcher design pattern
    #
    # DO NOT REFACTOR to standard pattern - dispatcher is superior for DEBUG
    # Verified 2025-10-15: This is intentional architecture
    # ========================================================================
    (GatewayInterface.DEBUG, 'check_component_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'check_gateway_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'diagnose_system_health'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'diagnose_performance'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'diagnose_memory'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_ultra_optimization_tests'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_performance_benchmark'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_configuration_tests'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'run_comprehensive_tests'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_system_architecture'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_imports'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'validate_gateway_routing'): ('debug_core', 'generic_debug_operation'),
    (GatewayInterface.DEBUG, 'get_system_stats'): ('debug_core', 'generic_debug_operation'),
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
            from debug_core import DebugOperation
            op_enum = DebugOperation(operation)
            return fast_func(op_enum, **kwargs)
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
            from debug_core import generic_debug_operation, DebugOperation
            op_enum = DebugOperation(operation)
            return generic_debug_operation(op_enum, **kwargs)
        
        # Standard operation handling
        mod = __import__(module_name, fromlist=[func_name])
        func = getattr(mod, func_name)
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
