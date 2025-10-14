"""
gateway.py - Universal operation routing with registry-based dispatch
Version: 2025.10.14.02
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

# ===== OPERATION REGISTRY =====

_OPERATION_REGISTRY: Dict[Tuple[GatewayInterface, str], Tuple[str, str]] = {
    # CACHE operations
    (GatewayInterface.CACHE, 'get'): ('cache_core', '_execute_get_implementation'),
    (GatewayInterface.CACHE, 'set'): ('cache_core', '_execute_set_implementation'),
    (GatewayInterface.CACHE, 'exists'): ('cache_core', '_execute_exists_implementation'),
    (GatewayInterface.CACHE, 'delete'): ('cache_core', '_execute_delete_implementation'),
    (GatewayInterface.CACHE, 'clear'): ('cache_core', '_execute_clear_implementation'),
    (GatewayInterface.CACHE, 'get_stats'): ('cache_core', 'cache_get_stats'),
    
    # LOGGING operations
    (GatewayInterface.LOGGING, 'log_info'): ('logging_core', '_execute_log_info_implementation'),
    (GatewayInterface.LOGGING, 'log_error'): ('logging_core', '_execute_log_error_implementation'),
    (GatewayInterface.LOGGING, 'log_warning'): ('logging_core', '_execute_log_warning_implementation'),
    (GatewayInterface.LOGGING, 'log_debug'): ('logging_core', '_execute_log_debug_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_start'): ('logging_core', '_execute_log_operation_start_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_success'): ('logging_core', '_execute_log_operation_success_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_failure'): ('logging_core', '_execute_log_operation_failure_implementation'),
    
    # SECURITY operations
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
    
    # METRICS operations
    (GatewayInterface.METRICS, 'record'): ('metrics_core', '_execute_record_metric_implementation'),
    (GatewayInterface.METRICS, 'increment'): ('metrics_core', '_execute_increment_counter_implementation'),
    (GatewayInterface.METRICS, 'get_stats'): ('metrics_core', '_execute_get_stats_implementation'),
    (GatewayInterface.METRICS, 'record_operation'): ('metrics_core', '_execute_record_operation_metric_implementation'),
    (GatewayInterface.METRICS, 'record_error'): ('metrics_core', '_execute_record_error_response_metric_implementation'),
    (GatewayInterface.METRICS, 'record_cache'): ('metrics_core', '_execute_record_cache_metric_implementation'),
    (GatewayInterface.METRICS, 'record_api'): ('metrics_core', '_execute_record_api_metric_implementation'),
    
    # CONFIG operations
    (GatewayInterface.CONFIG, 'get_parameter'): ('config_core', '_get_parameter_implementation'),
    (GatewayInterface.CONFIG, 'set_parameter'): ('config_core', '_set_parameter_implementation'),
    (GatewayInterface.CONFIG, 'get_category'): ('config_core', '_get_category_implementation'),
    (GatewayInterface.CONFIG, 'reload'): ('config_core', '_reload_implementation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('config_core', '_switch_preset_implementation'),
    (GatewayInterface.CONFIG, 'get_state'): ('config_core', '_get_state_implementation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('config_core', '_load_environment_implementation'),
    (GatewayInterface.CONFIG, 'load_file'): ('config_core', '_load_file_implementation'),
    (GatewayInterface.CONFIG, 'validate'): ('config_core', '_validate_all_implementation'),
    
    # SINGLETON operations
    (GatewayInterface.SINGLETON, 'get'): ('singleton_core', '_execute_get_implementation'),
    (GatewayInterface.SINGLETON, 'has'): ('singleton_core', '_execute_has_implementation'),
    (GatewayInterface.SINGLETON, 'delete'): ('singleton_core', '_execute_delete_implementation'),
    (GatewayInterface.SINGLETON, 'clear'): ('singleton_core', '_execute_clear_implementation'),
    (GatewayInterface.SINGLETON, 'get_stats'): ('singleton_core', '_execute_get_stats_implementation'),
    
    # INITIALIZATION operations
    (GatewayInterface.INITIALIZATION, 'initialize'): ('initialization_core', '_execute_initialize_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_status'): ('initialization_core', '_execute_get_status_implementation'),
    (GatewayInterface.INITIALIZATION, 'set_flag'): ('initialization_core', '_execute_set_flag_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_flag'): ('initialization_core', '_execute_get_flag_implementation'),
    
    # HTTP_CLIENT operations
    (GatewayInterface.HTTP_CLIENT, 'request'): ('http_client_core', 'http_request_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('http_client_core', 'http_get_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('http_client_core', 'http_post_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('http_client_core', 'http_put_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('http_client_core', 'http_delete_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('http_client_core', 'get_client_state'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('http_client_core', 'reset_client_state'),
    
    # WEBSOCKET operations
    (GatewayInterface.WEBSOCKET, 'connect'): ('http_client_core', 'websocket_connect_implementation'),
    (GatewayInterface.WEBSOCKET, 'send'): ('http_client_core', 'websocket_send_implementation'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('http_client_core', 'websocket_receive_implementation'),
    (GatewayInterface.WEBSOCKET, 'close'): ('http_client_core', 'websocket_close_implementation'),
    (GatewayInterface.WEBSOCKET, 'request'): ('http_client_core', 'websocket_request_implementation'),
    
    # CIRCUIT_BREAKER operations
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('circuit_breaker_core', '_execute_get_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('circuit_breaker_core', '_execute_call_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('circuit_breaker_core', '_execute_get_all_states_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('circuit_breaker_core', '_execute_reset_all_implementation'),
    
    # UTILITY operations
    (GatewayInterface.UTILITY, 'format_response'): ('shared_utilities', '_execute_format_response_implementation'),
    (GatewayInterface.UTILITY, 'parse_json'): ('shared_utilities', '_execute_parse_json_implementation'),
    (GatewayInterface.UTILITY, 'safe_get'): ('shared_utilities', '_execute_safe_get_implementation'),
    (GatewayInterface.UTILITY, 'generate_uuid'): ('shared_utilities', '_generate_uuid_implementation'),
    (GatewayInterface.UTILITY, 'get_timestamp'): ('shared_utilities', '_get_timestamp_implementation'),
}

# ===== FAST PATH TRACKING =====

_operation_call_counts: Dict[Tuple[GatewayInterface, str], int] = {}
_fast_path_enabled = True

# ===== CORE DISPATCH FUNCTION =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """
    Universal gateway routing with lazy loading and fast-path optimization.
    
    Registry-based dispatch eliminates 150+ lines of if/elif chains.
    Integrates fast-path tracking for hot operation optimization.
    """
    global _operation_call_counts
    
    registry_key = (interface, operation)
    entry = _OPERATION_REGISTRY.get(registry_key)
    
    if not entry:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    
    module_name, func_name = entry
    
    # Fast path tracking
    if _fast_path_enabled:
        _operation_call_counts[registry_key] = _operation_call_counts.get(registry_key, 0) + 1
        
        if _operation_call_counts[registry_key] == 20:
            try:
                from fast_path import register_fast_path
                mod = __import__(module_name, fromlist=[func_name])
                func = getattr(mod, func_name)
                register_fast_path(f"{interface.value}.{operation}", func)
            except (ImportError, AttributeError):
                pass
    
    # Lazy module import
    try:
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
        'interfaces': {iface.value: sum(1 for k in _OPERATION_REGISTRY if k[0] == iface) 
                      for iface in GatewayInterface},
        'fast_path_enabled': _fast_path_enabled
    }


def create_error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'body': {'error': message, 'success': False}
    }


def create_success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized success response."""
    return {
        'statusCode': status_code,
        'body': {'data': data, 'success': True}
    }


# ===== CACHE WRAPPERS (6 functions) =====

def cache_get(key: str, default: Any = None):
    """Get cache value."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default=default)


def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set cache value."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)


def cache_exists(key: str) -> bool:
    """Check if cache key exists."""
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key)


def cache_delete(key: str):
    """Delete cache key."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear():
    """Clear all cache."""
    return execute_operation(GatewayInterface.CACHE, 'clear')


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return execute_operation(GatewayInterface.CACHE, 'get_stats')


# ===== LOGGING WRAPPERS (7 functions) =====

def log_info(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log info message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra or kwargs)


def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log error message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, extra=extra or kwargs)


def log_warning(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log warning message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, extra=extra or kwargs)


def log_debug(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
    """Log debug message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, extra=extra or kwargs)


def log_operation_start(operation: str, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
    """Log operation start."""
    return execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation=operation, correlation_id=correlation_id, context=context)


def log_operation_success(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None, result: Any = None):
    """Log operation success."""
    return execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation=operation, duration_ms=duration_ms, correlation_id=correlation_id, result=result)


def log_operation_failure(operation: str, error: Exception, duration_ms: float = 0, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
    """Log operation failure."""
    return execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation=operation, error=error, duration_ms=duration_ms, correlation_id=correlation_id, context=context)


# ===== SECURITY WRAPPERS (11 functions) =====

def validate_request(request_data: Dict[str, Any]) -> bool:
    """Validate request data."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)


def validate_token(token: str) -> bool:
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)


def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data, key=key)


def decrypt_data(data: str, key: Optional[str] = None) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', data=data, key=key)


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


# ===== METRICS WRAPPERS (7 functions) =====

def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', name=name, value=value, tags=tags)


def increment_counter(name: str, tags: Optional[Dict[str, str]] = None):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', name=name, tags=tags)


def get_metrics_stats() -> Dict[str, Any]:
    """Get metrics statistics."""
    return execute_operation(GatewayInterface.METRICS, 'get_stats')


def record_operation_metric(operation: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None):
    """Record operation metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_operation', operation=operation, success=success, duration_ms=duration_ms, error_type=error_type)


def record_error_metric(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict[str, Any]] = None):
    """Record error metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, severity=severity, category=category, context=context or {})


def record_cache_metric(operation: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0):
    """Record cache metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_cache', operation=operation, hit=hit, miss=miss, eviction=eviction, duration_ms=duration_ms)


def record_api_metric(endpoint: str, method: str = 'GET', status_code: int = 200, duration_ms: float = 0):
    """Record API metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_api', endpoint=endpoint, method=method, status_code=status_code, duration_ms=duration_ms)


# ===== CONFIG WRAPPERS (12 functions) =====

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)


def set_config(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)


def get_config_category(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category=category)


def reload_config(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'reload', validate=validate)


def switch_config_preset(preset_name: str) -> Dict[str, Any]:
    """Switch configuration preset."""
    return execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset_name=preset_name)


def get_config_state() -> Dict[str, Any]:
    """Get configuration state."""
    return execute_operation(GatewayInterface.CONFIG, 'get_state')


def load_config_from_environment() -> Dict[str, Any]:
    """Load configuration from environment."""
    return execute_operation(GatewayInterface.CONFIG, 'load_environment')


def load_config_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return execute_operation(GatewayInterface.CONFIG, 'load_file', filepath=filepath)


def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'validate')


def initialize_config() -> Dict[str, Any]:
    """Initialize configuration system."""
    return get_config_category('system')


def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return get_config_category('cache')


def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration."""
    return get_config_category('metrics')


# ===== SINGLETON WRAPPERS (5 functions) =====

def singleton_get(name: str, factory_func: Optional[Callable] = None) -> Any:
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', name=name, factory_func=factory_func)


def singleton_has(name: str) -> bool:
    """Check if singleton exists."""
    return execute_operation(GatewayInterface.SINGLETON, 'has', name=name)


def singleton_delete(name: str) -> bool:
    """Delete singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'delete', name=name)


def singleton_clear() -> int:
    """Clear all singletons."""
    return execute_operation(GatewayInterface.SINGLETON, 'clear')


def singleton_stats() -> Dict[str, Any]:
    """Get singleton statistics."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_stats')


# ===== INITIALIZATION WRAPPERS (4 functions) =====

def initialize_system() -> Dict[str, Any]:
    """Initialize system."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'initialize')


def get_initialization_status() -> Dict[str, Any]:
    """Get initialization status."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_status')


def set_initialization_flag(key: str, value: bool):
    """Set initialization flag."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'set_flag', key=key, value=value)


def get_initialization_flag(key: str) -> bool:
    """Get initialization flag."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_flag', key=key)


# ===== HTTP CLIENT WRAPPERS (7 functions) =====

def http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'request', method=method, url=url, **kwargs)


def http_get(url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP GET request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get', url=url, **kwargs)


def http_post(url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP POST request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'post', url=url, **kwargs)


def http_put(url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP PUT request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'put', url=url, **kwargs)


def http_delete(url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP DELETE request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'delete', url=url, **kwargs)


def get_http_client_state() -> Dict[str, Any]:
    """Get HTTP client state."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get_state')


def reset_http_client_state():
    """Reset HTTP client state."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'reset_state')


# ===== WEBSOCKET WRAPPERS (5 functions) =====

def websocket_connect(url: str, **kwargs) -> Any:
    """Connect to WebSocket."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', url=url, **kwargs)


def websocket_send(connection: Any, message: str) -> bool:
    """Send WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'send', connection=connection, message=message)


def websocket_receive(connection: Any, timeout: float = 30.0) -> str:
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', connection=connection, timeout=timeout)


def websocket_close(connection: Any) -> bool:
    """Close WebSocket connection."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'close', connection=connection)


def websocket_request(url: str, message: str, **kwargs) -> Any:
    """Make WebSocket request."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', url=url, message=message, **kwargs)


# ===== CIRCUIT BREAKER WRAPPERS (6 functions) =====

def get_circuit_breaker(name: str) -> Any:
    """Get circuit breaker."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)


def execute_with_circuit_breaker(name: str, func: Callable, *args, **kwargs) -> Any:
    """Execute function with circuit breaker."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', name=name, func=func, args=args, kwargs=kwargs)


def get_all_circuit_breaker_states() -> Dict[str, Dict[str, Any]]:
    """Get all circuit breaker states."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_all_states')


def reset_all_circuit_breakers():
    """Reset all circuit breakers."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset_all')


def is_circuit_breaker_open(name: str) -> bool:
    """Check if circuit breaker is open."""
    try:
        breaker = get_circuit_breaker(name)
        return breaker.get('state') == 'open' if isinstance(breaker, dict) else False
    except:
        return False


def circuit_breaker_call(name: str, func: Callable, *args, **kwargs):
    """Alias for execute_with_circuit_breaker."""
    return execute_with_circuit_breaker(name, func, *args, **kwargs)


# ===== UTILITY WRAPPERS (5 functions) =====

def format_response(status_code: int, body: Any, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Format response."""
    return execute_operation(GatewayInterface.UTILITY, 'format_response', status_code=status_code, body=body, headers=headers)


def parse_json(json_string: str, default: Any = None) -> Any:
    """Parse JSON string."""
    return execute_operation(GatewayInterface.UTILITY, 'parse_json', json_string=json_string, default=default)


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safe dictionary get."""
    return execute_operation(GatewayInterface.UTILITY, 'safe_get', data=data, key=key, default=default)


def generate_uuid() -> str:
    """Generate UUID."""
    return execute_operation(GatewayInterface.UTILITY, 'generate_uuid')


def get_timestamp() -> str:
    """Get current timestamp."""
    return execute_operation(GatewayInterface.UTILITY, 'get_timestamp')


# ===== FAST PATH MANAGEMENT (5 functions) =====

def enable_fast_path():
    """Enable fast path optimization."""
    global _fast_path_enabled
    _fast_path_enabled = True
    return {'fast_path_enabled': True}


def disable_fast_path():
    """Disable fast path optimization."""
    global _fast_path_enabled
    _fast_path_enabled = False
    return {'fast_path_enabled': False}


def reset_fast_path_stats():
    """Reset fast path statistics."""
    global _operation_call_counts
    _operation_call_counts.clear()
    return {'stats_reset': True}


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return {
        'enabled': _fast_path_enabled,
        'operation_counts': dict(_operation_call_counts),
        'hot_operations': [k for k, v in _operation_call_counts.items() if v >= 20]
    }


def mark_module_hot(module_name: str):
    """Mark module as hot for LUGS."""
    try:
        from fast_path import mark_module_hot as fpm_mark_hot
        fpm_mark_hot(module_name)
    except ImportError:
        pass


# ===== GATEWAY MANAGEMENT (2 functions) =====

def get_loaded_modules() -> Dict[str, Any]:
    """Get loaded module statistics."""
    import sys
    return {
        'total_modules': len(sys.modules),
        'gateway_modules': [m for m in sys.modules if m.endswith('_core') or m == 'gateway']
    }


# EOF
