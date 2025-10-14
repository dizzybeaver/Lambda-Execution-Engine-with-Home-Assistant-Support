"""
gateway.py - Universal Lambda Gateway with SUGA Architecture
Version: 2025.10.14.04
Description: COMPLETE ultra-optimized central routing hub - ALL functionality included

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
    BATCH = "batch"

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
    
    # CONFIG operations (COMPLETE)
    (GatewayInterface.CONFIG, 'get_parameter'): ('config_core', '_get_parameter_implementation'),
    (GatewayInterface.CONFIG, 'set_parameter'): ('config_core', '_set_parameter_implementation'),
    (GatewayInterface.CONFIG, 'get_category'): ('config_core', '_get_category_implementation'),
    (GatewayInterface.CONFIG, 'get_category_config'): ('config_core', '_get_category_implementation'),
    (GatewayInterface.CONFIG, 'reload'): ('config_core', '_reload_implementation'),
    (GatewayInterface.CONFIG, 'reload_config'): ('config_core', '_reload_implementation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('config_core', '_switch_preset_implementation'),
    (GatewayInterface.CONFIG, 'get_state'): ('config_core', '_get_state_implementation'),
    (GatewayInterface.CONFIG, 'load_from_environment'): ('config_core', '_load_environment_implementation'),
    (GatewayInterface.CONFIG, 'load_from_file'): ('config_core', '_load_file_implementation'),
    (GatewayInterface.CONFIG, 'validate_all_sections'): ('config_core', '_validate_all_implementation'),
    (GatewayInterface.CONFIG, 'initialize'): ('config_core', '_initialize_implementation'),
    
    # SINGLETON operations
    (GatewayInterface.SINGLETON, 'get'): ('singleton_core', '_execute_get_implementation'),
    (GatewayInterface.SINGLETON, 'set'): ('singleton_core', '_execute_set_implementation'),
    (GatewayInterface.SINGLETON, 'reset'): ('singleton_core', '_execute_reset_implementation'),
    (GatewayInterface.SINGLETON, 'reset_all'): ('singleton_core', '_execute_reset_all_implementation'),
    (GatewayInterface.SINGLETON, 'exists'): ('singleton_core', '_execute_exists_implementation'),
    
    # INITIALIZATION operations
    (GatewayInterface.INITIALIZATION, 'initialize'): ('initialization_core', '_execute_initialize_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_config'): ('initialization_core', '_execute_get_config_implementation'),
    (GatewayInterface.INITIALIZATION, 'is_initialized'): ('initialization_core', '_execute_is_initialized_implementation'),
    (GatewayInterface.INITIALIZATION, 'reset'): ('initialization_core', '_execute_reset_implementation'),
    
    # HTTP_CLIENT operations
    (GatewayInterface.HTTP_CLIENT, 'make_request'): ('http_client_core', '_make_http_request'),
    (GatewayInterface.HTTP_CLIENT, 'get_client'): ('http_client_core', 'get_http_client'),
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
                register_fast_path(f"{interface.value}.{operation}", func, module_name)
            except (ImportError, AttributeError):
                pass
    
    # Lazy import and execute
    module = __import__(module_name, fromlist=[func_name])
    func = getattr(module, func_name)
    
    return func(**kwargs)

# ===== INITIALIZATION =====

def initialize_lambda():
    """Initialize Lambda execution environment."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'initialize')

# ===== RESPONSE HELPERS =====

def create_error_response(message: str, status_code: int = 500, **kwargs) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        'statusCode': status_code,
        'body': {'error': message, 'success': False, **kwargs}
    }

def create_success_response(data: Any, status_code: int = 200, message: str = None, **kwargs) -> Dict[str, Any]:
    """Create standardized success response."""
    response = {'data': data, 'success': True, 'statusCode': status_code}
    if message:
        response['message'] = message
    response.update(kwargs)
    return {'statusCode': status_code, 'body': response}

def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Format Lambda response."""
    if isinstance(body, dict):
        import json
        body_str = json.dumps(body)
    else:
        body_str = str(body)
    
    return {
        'statusCode': status_code,
        'body': body_str,
        'headers': headers or {'Content-Type': 'application/json'}
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

def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data, key=key)

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
    """Sanitize input data."""
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)

# ===== METRICS WRAPPERS (7 functions) =====

def record_metric(metric_name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None, **kwargs):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', metric_name=metric_name, value=value, dimensions=dimensions or kwargs.get('tags'))

def increment_counter(counter_name: str, value: int = 1):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', counter_name=counter_name, value=value)

def get_metrics_stats() -> Dict[str, Any]:
    """Get metrics statistics."""
    return execute_operation(GatewayInterface.METRICS, 'get_stats')

def record_operation_metric(operation: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None):
    """Record operation metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_operation', operation=operation, success=success, duration_ms=duration_ms, error_type=error_type)

def record_error_metric(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None):
    """Record error metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, severity=severity, category=category, context=context or {})

def record_cache_metric(operation: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0):
    """Record cache metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_cache', operation=operation, hit=hit, miss=miss, eviction=eviction, duration_ms=duration_ms)

def record_api_metric(endpoint: str, method: str = 'GET', status_code: int = 200, duration_ms: float = 0):
    """Record API metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_api', endpoint=endpoint, method=method, status_code=status_code, duration_ms=duration_ms)

# ===== CONFIG WRAPPERS (12 functions) =====

def get_parameter(key: str, default: Any = None):
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)

def set_parameter(key: str, value: Any):
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
    return execute_operation(GatewayInterface.CONFIG, 'load_from_environment')

def load_config_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return execute_operation(GatewayInterface.CONFIG, 'load_from_file', filepath=filepath)

def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration sections."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_all_sections')

def initialize_config() -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'initialize')

def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration category."""
    return get_config_category('cache')

def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration category."""
    return get_config_category('metrics')

# ===== SINGLETON WRAPPERS (5 functions) =====

def get_singleton(name: str, factory_func: Optional[Callable] = None, **kwargs):
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', name=name, factory_func=factory_func, **kwargs)

def register_singleton(name: str, instance: Any):
    """Register singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'set', name=name, instance=instance)

def reset_singleton(name: str):
    """Reset singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'reset', name=name)

def reset_all_singletons():
    """Reset all singleton instances."""
    return execute_operation(GatewayInterface.SINGLETON, 'reset_all')

def singleton_exists(name: str) -> bool:
    """Check if singleton exists."""
    return execute_operation(GatewayInterface.SINGLETON, 'exists', name=name)

# ===== HTTP CLIENT WRAPPERS (5 functions) =====

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'make_request', method=method, url=url, **kwargs)

def make_get_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make GET request."""
    return make_request('GET', url, **kwargs)

def make_post_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make POST request."""
    return make_request('POST', url, **kwargs)

def make_put_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make PUT request."""
    return make_request('PUT', url, **kwargs)

def make_delete_request(url: str, **kwargs) -> Dict[str, Any]:
    """Make DELETE request."""
    return make_request('DELETE', url, **kwargs)

# ===== WEBSOCKET WRAPPERS (5 functions) =====

def websocket_connect(url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Connect to WebSocket."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', url=url, timeout=timeout, **kwargs)

def websocket_send(connection: Any, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Send WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'send', connection=connection, message=message, **kwargs)

def websocket_receive(connection: Any, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', connection=connection, timeout=timeout, **kwargs)

def websocket_close(connection: Any, **kwargs) -> Dict[str, Any]:
    """Close WebSocket connection."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'close', connection=connection, **kwargs)

def make_websocket_request(url: str, message: Dict[str, Any], timeout: int = 10, wait_for_response: bool = True, **kwargs) -> Dict[str, Any]:
    """Make complete WebSocket request."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', url=url, message=message, timeout=timeout, wait_for_response=wait_for_response, **kwargs)

# ===== CIRCUIT BREAKER WRAPPERS (6 functions) =====

def get_circuit_breaker(name: str, failure_threshold: int = 5, timeout: int = 60):
    """Get circuit breaker instance."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name, failure_threshold=failure_threshold, timeout=timeout)

def execute_with_circuit_breaker(breaker_name: str, func: Callable, *args, **kwargs):
    """Execute function with circuit breaker protection."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', name=breaker_name, func=func, args=args, **kwargs)

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
        state = breaker.get_state()
        return state.get('state') == 'open'
    except:
        return False

def circuit_breaker_call(name: str, func: Callable, *args, **kwargs):
    """Alias for execute_with_circuit_breaker."""
    return execute_with_circuit_breaker(name, func, *args, **kwargs)

# ===== UTILITY WRAPPERS (3 functions) =====

def parse_json_safely(data: str) -> Dict[str, Any]:
    """Parse JSON safely."""
    try:
        import json
        return json.loads(data)
    except:
        return {}

def safe_get(dictionary: Dict, key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    try:
        return execute_operation(GatewayInterface.UTILITY, 'safe_get', dictionary=dictionary, key_path=key_path, default=default)
    except:
        return default

def generate_uuid() -> str:
    """Generate UUID."""
    try:
        return execute_operation(GatewayInterface.UTILITY, 'generate_uuid')
    except:
        import uuid
        return str(uuid.uuid4())

# ===== INITIALIZATION WRAPPERS (4 functions) =====

def execute_initialization_operation(operation: str, **kwargs):
    """Execute initialization operation."""
    return execute_operation(GatewayInterface.INITIALIZATION, operation, **kwargs)

def record_initialization_stage(stage: str, **kwargs):
    """Record initialization stage."""
    return log_info(f"Initialization stage: {stage}", extra=kwargs)

def is_initialized() -> bool:
    """Check if Lambda is initialized."""
    try:
        return execute_operation(GatewayInterface.INITIALIZATION, 'is_initialized')
    except:
        return False

def get_initialization_config() -> Dict[str, Any]:
    """Get initialization configuration."""
    try:
        return execute_operation(GatewayInterface.INITIALIZATION, 'get_config')
    except:
        return {}

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
        'tracked_operations': len(_operation_call_counts),
        'hot_operations': sum(1 for count in _operation_call_counts.values() if count >= 20),
        'total_calls': sum(_operation_call_counts.values()),
        'operation_counts': {f"{k[0].value}.{k[1]}": v for k, v in sorted(_operation_call_counts.items(), key=lambda x: x[1], reverse=True)[:20]}
    }

def mark_module_hot(module_name: str):
    """Mark module as hot to prevent LUGS unloading."""
    try:
        from fast_path import should_protect_module, register_fast_path
        return should_protect_module(module_name)
    except ImportError:
        return False

# ===== GATEWAY STATS (2 functions) =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    interfaces = {}
    for (iface, op), _ in _OPERATION_REGISTRY.items():
        interfaces[iface.value] = interfaces.get(iface.value, 0) + 1
    
    return {
        'registered_operations': len(_OPERATION_REGISTRY),
        'interfaces': len(interfaces),
        'operations_by_interface': interfaces,
        'fast_path_stats': get_fast_path_stats()
    }

def get_loaded_modules() -> list:
    """Get list of loaded modules."""
    import sys
    return list(sys.modules.keys())

# ===== EXPORTS =====

__all__ = [
    # Core
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'create_error_response',
    'create_success_response',
    'format_response',
    # Cache (6)
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    # Logging (7)
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    # Security (11)
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'generate_correlation_id',
    'validate_string',
    'validate_email',
    'validate_url',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    # Metrics (7)
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    # Config (12)
    'get_parameter',
    'set_parameter',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    # Singleton (5)
    'get_singleton',
    'register_singleton',
    'reset_singleton',
    'reset_all_singletons',
    'singleton_exists',
    # HTTP Client (5)
    'make_request',
    'make_get_request',
    'make_post_request',
    'make_put_request',
    'make_delete_request',
    # WebSocket (5)
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'make_websocket_request',
    # Circuit Breaker (6)
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    'is_circuit_breaker_open',
    'circuit_breaker_call',
    # Utility (3)
    'parse_json_safely',
    'safe_get',
    'generate_uuid',
    # Initialization (4)
    'execute_initialization_operation',
    'record_initialization_stage',
    'is_initialized',
    'get_initialization_config',
    # Fast Path (5)
    'enable_fast_path',
    'disable_fast_path',
    'reset_fast_path_stats',
    'get_fast_path_stats',
    'mark_module_hot',
    # Gateway Stats (2)
    'get_gateway_stats',
    'get_loaded_modules',
]

# EOF
