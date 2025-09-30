"""
gateway.py - Phase 5: ZAFP Integration
Version: 2025.09.29.07
Daily Revision: Phase 5 Zero-Abstraction Fast Path Integrated

Revolutionary Gateway with ZAFP
- Single Universal Gateway Architecture (SUGA)
- Lazy Import Gateway System (LIGS)
- Zero-Abstraction Fast Path (ZAFP)
100% Free Tier AWS compliant
"""

import time
from typing import Any, Dict, Optional
from enum import Enum

class GatewayInterface(str, Enum):
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

_modules_loaded = {}
_fast_path_enabled = True

def _load_module(module_name: str) -> Any:
    """Lazy load module on first use."""
    if module_name not in _modules_loaded:
        if module_name == "cache_core":
            import cache_core
            _modules_loaded[module_name] = cache_core
        elif module_name == "logging_core":
            import logging_core
            _modules_loaded[module_name] = logging_core
        elif module_name == "security_core":
            import security_core
            _modules_loaded[module_name] = security_core
        elif module_name == "metrics_core":
            import metrics_core
            _modules_loaded[module_name] = metrics_core
        elif module_name == "singleton_core":
            import singleton_core
            _modules_loaded[module_name] = singleton_core
        elif module_name == "http_client_core":
            import http_client_core
            _modules_loaded[module_name] = http_client_core
        elif module_name == "utility_core":
            import utility_core
            _modules_loaded[module_name] = utility_core
        elif module_name == "initialization_core":
            import initialization_core
            _modules_loaded[module_name] = initialization_core
        elif module_name == "lambda_core":
            import lambda_core
            _modules_loaded[module_name] = lambda_core
        elif module_name == "circuit_breaker_core":
            import circuit_breaker_core
            _modules_loaded[module_name] = circuit_breaker_core
        elif module_name == "config_core":
            import config_core
            _modules_loaded[module_name] = config_core
        elif module_name == "debug_core":
            import debug_core
            _modules_loaded[module_name] = debug_core
        elif module_name == "fast_path":
            import fast_path
            _modules_loaded[module_name] = fast_path
    
    return _modules_loaded.get(module_name)

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Universal operation execution with ZAFP support.
    Routes hot operations through fast path, others through normal path.
    """
    operation_key = f"{interface.value}.{operation}"
    
    if _fast_path_enabled:
        fast_path = _load_module("fast_path")
        if fast_path and fast_path.is_hot_operation(operation_key):
            fast_func = fast_path.get_fast_path_system().get_fast_path(operation_key)
            if fast_func:
                start = time.time()
                result = fast_func(**kwargs)
                exec_time = (time.time() - start) * 1000
                fast_path.track_operation(operation_key, exec_time)
                return result
    
    start = time.time()
    result = _execute_normal_path(interface, operation, **kwargs)
    exec_time = (time.time() - start) * 1000
    
    if _fast_path_enabled:
        fast_path = _load_module("fast_path")
        if fast_path:
            fast_path.track_operation(operation_key, exec_time)
    
    return result

def _execute_normal_path(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """Execute operation through normal gateway path."""
    module_name = f"{interface.value}_core"
    module = _load_module(module_name)
    
    if not module:
        raise ImportError(f"Module {module_name} not found")
    
    func_name = f"execute_{operation}"
    if hasattr(module, func_name):
        func = getattr(module, func_name)
        return func(**kwargs)
    
    generic_func_name = f"execute_generic_{interface.value}_operation"
    if hasattr(module, generic_func_name):
        func = getattr(module, generic_func_name)
        return func(operation, **kwargs)
    
    raise AttributeError(f"Operation {operation} not found in {module_name}")

def cache_get(key: str, default_value: Any = None, **kwargs) -> Any:
    """Get value from cache with ZAFP."""
    return execute_operation(GatewayInterface.CACHE, "get", key=key, default_value=default_value, **kwargs)

def cache_set(key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
    """Set value in cache with ZAFP."""
    return execute_operation(GatewayInterface.CACHE, "set", key=key, value=value, ttl=ttl, **kwargs)

def cache_delete(key: str, **kwargs) -> bool:
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, "delete", key=key, **kwargs)

def cache_clear(**kwargs) -> bool:
    """Clear all cache."""
    return execute_operation(GatewayInterface.CACHE, "clear", **kwargs)

def log_info(message: str, **kwargs) -> None:
    """Log info message with ZAFP."""
    execute_operation(GatewayInterface.LOGGING, "info", message=message, **kwargs)

def log_error(message: str, **kwargs) -> None:
    """Log error message with ZAFP."""
    execute_operation(GatewayInterface.LOGGING, "error", message=message, **kwargs)

def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    execute_operation(GatewayInterface.LOGGING, "warning", message=message, **kwargs)

def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    execute_operation(GatewayInterface.LOGGING, "debug", message=message, **kwargs)

def validate_request(request: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Validate request."""
    return execute_operation(GatewayInterface.SECURITY, "validate_request", request=request, **kwargs)

def validate_token(token: str, **kwargs) -> Dict[str, Any]:
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, "validate_token", token=token, **kwargs)

def encrypt_data(data: Any, **kwargs) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, "encrypt", data=data, **kwargs)

def decrypt_data(encrypted: str, **kwargs) -> Any:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, "decrypt", encrypted=encrypted, **kwargs)

def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Record metric with ZAFP."""
    return execute_operation(GatewayInterface.METRICS, "record", name=name, value=value, dimensions=dimensions, **kwargs)

def increment_counter(name: str, **kwargs) -> bool:
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, "increment", name=name, **kwargs)

def get_singleton(name: str, **kwargs) -> Any:
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, "get", name=name, **kwargs)

def register_singleton(name: str, instance: Any, **kwargs) -> bool:
    """Register singleton."""
    return execute_operation(GatewayInterface.SINGLETON, "register", name=name, instance=instance, **kwargs)

def make_request(url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, "request", url=url, method=method, **kwargs)

def make_get_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make GET request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, "get", url=url, **kwargs)

def make_post_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make POST request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, "post", url=url, **kwargs)

def create_success_response(message: str, data: Any = None, **kwargs) -> Dict[str, Any]:
    """Create success response."""
    return execute_operation(GatewayInterface.UTILITY, "create_success", message=message, data=data, **kwargs)

def create_error_response(error: str, details: Any = None, **kwargs) -> Dict[str, Any]:
    """Create error response."""
    return execute_operation(GatewayInterface.UTILITY, "create_error", error=error, details=details, **kwargs)

def parse_json_safely(json_str: str, **kwargs) -> Any:
    """Parse JSON safely."""
    return execute_operation(GatewayInterface.UTILITY, "parse_json", json_str=json_str, **kwargs)

def generate_correlation_id(**kwargs) -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.UTILITY, "generate_correlation_id", **kwargs)

def execute_initialization_operation(init_type: str, **kwargs) -> Dict[str, Any]:
    """Execute initialization operation."""
    return execute_operation(GatewayInterface.INITIALIZATION, "execute_operation", init_type=init_type, **kwargs)

def record_initialization_stage(stage: str, **kwargs) -> Dict[str, Any]:
    """Record initialization stage."""
    return execute_operation(GatewayInterface.INITIALIZATION, "record_stage", stage=stage, **kwargs)

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics including ZAFP stats."""
    stats = {
        "modules_loaded": list(_modules_loaded.keys()),
        "loaded_count": len(_modules_loaded),
        "fast_path_enabled": _fast_path_enabled
    }
    
    if _fast_path_enabled:
        fast_path = _load_module("fast_path")
        if fast_path:
            stats["fast_path_stats"] = fast_path.get_fast_path_stats()
    
    return stats

def enable_fast_path() -> None:
    """Enable ZAFP."""
    global _fast_path_enabled
    _fast_path_enabled = True

def disable_fast_path() -> None:
    """Disable ZAFP."""
    global _fast_path_enabled
    _fast_path_enabled = False

def reset_fast_path_stats() -> None:
    """Reset ZAFP statistics."""
    if _fast_path_enabled:
        fast_path = _load_module("fast_path")
        if fast_path:
            fast_path.reset_fast_path_stats()

def get_fast_path_stats() -> Dict[str, Any]:
    """Get ZAFP statistics."""
    if _fast_path_enabled:
        fast_path = _load_module("fast_path")
        if fast_path:
            return fast_path.get_fast_path_stats()
    return {"fast_path_enabled": False}

# EOF
