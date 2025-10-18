"""
gateway_core.py - Core Gateway Implementation (SUGA-ISP)
Version: 2025.10.17.18
Description: Pattern-based registry with simplified routing

CHANGELOG:
- 2025.10.17.18: MODERNIZED with pattern-based registry
  - Replaced 100+ operation registry with 12 interface mappings
  - Reduced registry from ~100 lines to 12 lines (~90% reduction)
  - Leverages dispatch dictionaries in interface routers
  - Zero breaking changes to external API
  - Easier maintenance (add operation = 1 place, not 2)
  - Consistent with interface modernization pattern
- 2025.10.17.12: Added comprehensive error handling
  - Wraps execution in try/except for robustness
  - Clear error context with interface.operation
  - Exception chaining for debugging

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
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
    WEBSOCKET = "websocket"
    CIRCUIT_BREAKER = "circuit_breaker"
    UTILITY = "utility"
    DEBUG = "debug"


# ===== PATTERN-BASED REGISTRY =====

_INTERFACE_ROUTERS: Dict[GatewayInterface, Tuple[str, str]] = {
    GatewayInterface.CACHE: ('interface_cache', 'execute_cache_operation'),
    GatewayInterface.LOGGING: ('interface_logging', 'execute_logging_operation'),
    GatewayInterface.SECURITY: ('interface_security', 'execute_security_operation'),
    GatewayInterface.METRICS: ('interface_metrics', 'execute_metrics_operation'),
    GatewayInterface.CONFIG: ('interface_config', 'execute_config_operation'),
    GatewayInterface.SINGLETON: ('interface_singleton', 'execute_singleton_operation'),
    GatewayInterface.INITIALIZATION: ('interface_initialization', 'execute_initialization_operation'),
    GatewayInterface.HTTP_CLIENT: ('interface_http', 'execute_http_operation'),
    GatewayInterface.WEBSOCKET: ('interface_websocket', 'execute_websocket_operation'),
    GatewayInterface.CIRCUIT_BREAKER: ('interface_circuit_breaker', 'execute_circuit_breaker_operation'),
    GatewayInterface.UTILITY: ('interface_utility', 'execute_utility_operation'),
    GatewayInterface.DEBUG: ('interface_debug', 'execute_debug_operation'),
}

# Legacy alias for backwards compatibility
_OPERATION_REGISTRY = _INTERFACE_ROUTERS


# ===== FAST PATH CACHE =====

_fast_path_cache: Dict[Tuple[GatewayInterface, str], Tuple[Callable, str, str]] = {}
_fast_path_enabled = True
_operation_call_counts = defaultdict(int)


# ===== CORE EXECUTION ENGINE =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Execute operation through pattern-based routing.
    
    PATTERN-BASED ROUTING (v2025.10.17.18):
    All operations for an interface route to the same function.
    The interface's dispatch dictionary handles operation routing.
    
    Benefits:
    - Simpler registry (12 entries vs 100+)
    - Easier maintenance (add operation = 1 place)
    - Leverages interface dispatch dictionaries
    - Zero breaking changes
    
    Args:
        interface: The GatewayInterface to route through
        operation: The operation name to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from interface implementation
        
    Raises:
        ValueError: If interface unknown
        RuntimeError: If module/function loading fails or execution fails
    """
    import importlib
    
    # Increment call count for fast path decision
    _operation_call_counts[(interface, operation)] += 1
    
    # Try fast path first if enabled
    if _fast_path_enabled:
        cache_key = (interface, operation)
        if cache_key in _fast_path_cache:
            func, module_name, func_name = _fast_path_cache[cache_key]
            
            try:
                # Interface routers always need operation parameter
                return func(operation, **kwargs)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to execute {interface.value}.{operation}: {str(e)}"
                ) from e
    
    # Slow path: Pattern-based routing
    if interface not in _INTERFACE_ROUTERS:
        raise ValueError(f"Unknown interface: {interface.value}")
    
    module_name, func_name = _INTERFACE_ROUTERS[interface]
    
    # Lazy import with error handling
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise RuntimeError(
            f"Failed to import module '{module_name}' for {interface.value}: {str(e)}"
        ) from e
    
    try:
        func = getattr(module, func_name)
    except AttributeError as e:
        raise RuntimeError(
            f"Function '{func_name}' not found in module '{module_name}' for {interface.value}: {str(e)}"
        ) from e
    
    # Cache for fast path if operation is frequent
    if _fast_path_enabled and _operation_call_counts[(interface, operation)] >= 3:
        _fast_path_cache[(interface, operation)] = (func, module_name, func_name)
    
    # Execute operation (interface routers always need operation parameter)
    try:
        return func(operation, **kwargs)
    except Exception as e:
        raise RuntimeError(
            f"Failed to execute {interface.value}.{operation}: {str(e)}"
        ) from e


# ===== INITIALIZATION =====

def initialize_lambda() -> Dict[str, Any]:
    """Initialize Lambda execution environment."""
    return {
        'gateway_initialized': True,
        'fast_path_enabled': _fast_path_enabled,
        'interface_count': len(_INTERFACE_ROUTERS)
    }


# ===== STATISTICS =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        'total_interfaces': len(_INTERFACE_ROUTERS),
        'fast_path_entries': len(_fast_path_cache),
        'fast_path_enabled': _fast_path_enabled,
        'operation_counts': dict(_operation_call_counts)
    }


# ===== FAST PATH MANAGEMENT =====

def set_fast_path_threshold(threshold: int) -> None:
    """Set fast path activation threshold (for future use)."""
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

def create_error_response(error: str, error_code: str, details: Any = None) -> Dict[str, Any]:
    """Create standardized error response for INTERNAL use."""
    return {
        'success': False,
        'error': error,
        'error_code': error_code,
        'details': details
    }

def create_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """Create standardized success response for INTERNAL use."""
    return {
        'success': True,
        'message': message,
        'data': data
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
    '_OPERATION_REGISTRY',  # Legacy alias
    '_INTERFACE_ROUTERS',
]

# EOF
