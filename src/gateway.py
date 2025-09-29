"""
gateway.py - Universal Gateway: Single Entry Point for All Operations
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Single Universal Gateway Architecture (SUGA)
Replaces 11 separate gateway files with ONE universal routing gateway
FREE TIER COMPLIANCE: 100% - Reduces memory footprint within free tier limits
"""

import sys
from enum import Enum
from typing import Any, Dict, Optional, Callable
import importlib

class GatewayInterface(Enum):
    """All available interfaces in the system."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    SINGLETON = "singleton"
    HTTP_CLIENT = "http_client"
    UTILITY = "utility"
    INITIALIZATION = "initialization"
    LAMBDA = "lambda"
    CIRCUIT_BREAKER = "circuit_breaker"
    CONFIG = "config"
    DEBUG = "debug"

class OperationType(Enum):
    """Universal operation types across all interfaces."""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    CREATE = "create"
    UPDATE = "update"
    VALIDATE = "validate"
    CHECK = "check"
    STATUS = "status"
    OPTIMIZE = "optimize"
    CLEANUP = "cleanup"
    RESET = "reset"
    BACKUP = "backup"
    RESTORE = "restore"
    EXECUTE = "execute"
    RECORD = "record"
    TRACK = "track"
    MONITOR = "monitor"

_CORE_MODULES = {}
_LAZY_CACHE = {}

class LazyModule:
    """Lazy-loading module proxy that imports only when accessed."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._module = None
    
    def __getattr__(self, name: str) -> Any:
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
            _LAZY_CACHE[self.module_name] = self._module
        return getattr(self._module, name)

def _get_core_module(interface: GatewayInterface):
    """Lazy load core modules only when needed."""
    module_map = {
        GatewayInterface.CACHE: "cache_core",
        GatewayInterface.LOGGING: "logging_core",
        GatewayInterface.SECURITY: "security_core",
        GatewayInterface.METRICS: "metrics_core",
        GatewayInterface.SINGLETON: "singleton_core",
        GatewayInterface.HTTP_CLIENT: "http_client_core",
        GatewayInterface.UTILITY: "utility_core",
        GatewayInterface.INITIALIZATION: "initialization_core",
        GatewayInterface.LAMBDA: "lambda_core",
        GatewayInterface.CIRCUIT_BREAKER: "circuit_breaker_core",
        GatewayInterface.CONFIG: "config_core",
        GatewayInterface.DEBUG: "debug_core",
    }
    
    module_name = module_map.get(interface)
    if not module_name:
        raise ValueError(f"Unknown interface: {interface}")
    
    if module_name not in _CORE_MODULES:
        _CORE_MODULES[module_name] = LazyModule(module_name)
    
    return _CORE_MODULES[module_name]

def execute_operation(
    interface: GatewayInterface,
    operation: str,
    **kwargs
) -> Any:
    """
    Universal operation executor.
    
    Args:
        interface: Target interface to route to
        operation: Operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Result from the core module operation
    """
    core_module = _get_core_module(interface)
    
    if not hasattr(core_module, operation):
        raise AttributeError(
            f"Interface {interface.value} does not support operation '{operation}'"
        )
    
    operation_func = getattr(core_module, operation)
    return operation_func(**kwargs)

def cache_get(key: str, default: Any = None, namespace: str = "default") -> Any:
    """Get value from cache."""
    return execute_operation(
        GatewayInterface.CACHE,
        "cache_get",
        key=key,
        default=default,
        namespace=namespace
    )

def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    namespace: str = "default"
) -> bool:
    """Set value in cache."""
    return execute_operation(
        GatewayInterface.CACHE,
        "cache_set",
        key=key,
        value=value,
        ttl=ttl,
        namespace=namespace
    )

def cache_delete(key: str, namespace: str = "default") -> bool:
    """Delete value from cache."""
    return execute_operation(
        GatewayInterface.CACHE,
        "cache_delete",
        key=key,
        namespace=namespace
    )

def cache_clear(namespace: str = "default") -> bool:
    """Clear cache namespace."""
    return execute_operation(
        GatewayInterface.CACHE,
        "cache_clear",
        namespace=namespace
    )

def cache_exists(key: str, namespace: str = "default") -> bool:
    """Check if key exists in cache."""
    return execute_operation(
        GatewayInterface.CACHE,
        "cache_exists",
        key=key,
        namespace=namespace
    )

def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    execute_operation(
        GatewayInterface.LOGGING,
        "log_debug",
        message=message,
        **kwargs
    )

def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    execute_operation(
        GatewayInterface.LOGGING,
        "log_info",
        message=message,
        **kwargs
    )

def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    execute_operation(
        GatewayInterface.LOGGING,
        "log_warning",
        message=message,
        **kwargs
    )

def log_error(message: str, **kwargs) -> None:
    """Log error message."""
    execute_operation(
        GatewayInterface.LOGGING,
        "log_error",
        message=message,
        **kwargs
    )

def log_critical(message: str, **kwargs) -> None:
    """Log critical message."""
    execute_operation(
        GatewayInterface.LOGGING,
        "log_critical",
        message=message,
        **kwargs
    )

def validate_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Validate incoming request."""
    return execute_operation(
        GatewayInterface.SECURITY,
        "validate_request",
        event=event
    )

def validate_token(token: str) -> bool:
    """Validate authentication token."""
    return execute_operation(
        GatewayInterface.SECURITY,
        "validate_token",
        token=token
    )

def sanitize_input(data: Any) -> Any:
    """Sanitize user input."""
    return execute_operation(
        GatewayInterface.SECURITY,
        "sanitize_input",
        data=data
    )

def record_metric(name: str, value: float, unit: str = "None", **kwargs) -> None:
    """Record custom metric."""
    execute_operation(
        GatewayInterface.METRICS,
        "record_metric",
        name=name,
        value=value,
        unit=unit,
        **kwargs
    )

def track_execution_time(operation_name: str, duration: float) -> None:
    """Track execution time."""
    execute_operation(
        GatewayInterface.METRICS,
        "track_execution_time",
        operation_name=operation_name,
        duration=duration
    )

def track_memory_usage(memory_mb: float) -> None:
    """Track memory usage."""
    execute_operation(
        GatewayInterface.METRICS,
        "track_memory_usage",
        memory_mb=memory_mb
    )

def get_singleton(name: str, factory: Optional[Callable] = None) -> Any:
    """Get or create singleton instance."""
    return execute_operation(
        GatewayInterface.SINGLETON,
        "get_singleton",
        name=name,
        factory=factory
    )

def reset_singleton(name: str) -> bool:
    """Reset singleton instance."""
    return execute_operation(
        GatewayInterface.SINGLETON,
        "reset_singleton",
        name=name
    )

def http_get(url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP GET request."""
    return execute_operation(
        GatewayInterface.HTTP_CLIENT,
        "http_get",
        url=url,
        **kwargs
    )

def http_post(url: str, data: Any = None, **kwargs) -> Dict[str, Any]:
    """Execute HTTP POST request."""
    return execute_operation(
        GatewayInterface.HTTP_CLIENT,
        "http_post",
        url=url,
        data=data,
        **kwargs
    )

def validate_type(value: Any, expected_type: type) -> bool:
    """Validate value type."""
    return execute_operation(
        GatewayInterface.UTILITY,
        "validate_type",
        value=value,
        expected_type=expected_type
    )

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    return execute_operation(
        GatewayInterface.UTILITY,
        "deep_merge",
        dict1=dict1,
        dict2=dict2
    )

def initialize_lambda() -> Dict[str, Any]:
    """Initialize Lambda environment."""
    return execute_operation(
        GatewayInterface.INITIALIZATION,
        "initialize_lambda"
    )

def build_response(status_code: int, body: Any, **kwargs) -> Dict[str, Any]:
    """Build Lambda response."""
    return execute_operation(
        GatewayInterface.LAMBDA,
        "build_response",
        status_code=status_code,
        body=body,
        **kwargs
    )

def build_alexa_response(speech: str, **kwargs) -> Dict[str, Any]:
    """Build Alexa response."""
    return execute_operation(
        GatewayInterface.LAMBDA,
        "build_alexa_response",
        speech=speech,
        **kwargs
    )

def circuit_breaker_call(
    operation: Callable,
    fallback: Optional[Callable] = None,
    **kwargs
) -> Any:
    """Execute operation with circuit breaker."""
    return execute_operation(
        GatewayInterface.CIRCUIT_BREAKER,
        "circuit_breaker_call",
        operation=operation,
        fallback=fallback,
        **kwargs
    )

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return execute_operation(
        GatewayInterface.CONFIG,
        "get_config",
        key=key,
        default=default
    )

def set_config(key: str, value: Any) -> bool:
    """Set configuration value."""
    return execute_operation(
        GatewayInterface.CONFIG,
        "set_config",
        key=key,
        value=value
    )

def debug_inspect(obj: Any, **kwargs) -> Dict[str, Any]:
    """Inspect object for debugging."""
    return execute_operation(
        GatewayInterface.DEBUG,
        "debug_inspect",
        obj=obj,
        **kwargs
    )

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    return {
        "loaded_modules": list(_LAZY_CACHE.keys()),
        "cached_interfaces": list(_CORE_MODULES.keys()),
        "available_interfaces": [i.value for i in GatewayInterface],
        "total_operations": len(OperationType)
    }

def clear_gateway_cache() -> None:
    """Clear gateway module cache."""
    _CORE_MODULES.clear()
    _LAZY_CACHE.clear()
    
    for module_name in list(sys.modules.keys()):
        if module_name.endswith('_core'):
            del sys.modules[module_name]
