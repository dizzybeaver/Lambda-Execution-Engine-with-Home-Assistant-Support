"""
gateway_wrappers.py - Gateway Convenience Wrapper Functions
Version: 2025.10.20.02
Description: Wrapper functions that call execute_operation() for cleaner code

CHANGELOG:
- 2025.10.20.02: CRITICAL FIX - Renamed 'operation' to 'operation_name' in 5 functions
  - Fixed record_operation_metric() parameter conflict
  - Fixed record_cache_metric() parameter conflict
  - Fixed log_operation_start() parameter conflict
  - Fixed log_operation_success() parameter conflict
  - Fixed log_operation_failure() parameter conflict
  - Resolves RuntimeError: "got multiple values for argument 'operation'"
- 2025.10.20.01: Added 4 new SECURITY wrappers for cache validation (Cache Ultra-Optimization Phase 2)
  - validate_cache_key() - Validate cache key format and safety
  - validate_ttl() - Validate TTL value is within acceptable range
  - validate_module_name() - Validate module name for LUGS dependency tracking
  - validate_number_range() - Generic numeric validation with bounds checking

CRITICAL BUG FIX (2025.10.20.02):
Problem: execute_operation(interface, operation, **kwargs) has 'operation' as positional parameter.
         Passing 'operation' in kwargs created conflict: "got multiple values for argument 'operation'"
Solution: Renamed parameter from 'operation' to 'operation_name' in all affected functions.
Impact: 5 functions fixed across METRICS and LOGGING interfaces.

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

from typing import Any, Dict, Optional, Callable, Tuple
from gateway_core import GatewayInterface, execute_operation

# ===== CONFIGURATION HELPERS =====

def initialize_config(**kwargs) -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)

def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='cache')

def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='metrics')

# ===== CIRCUIT BREAKER HELPERS =====

def is_circuit_breaker_open(name: str) -> bool:
    """Check if circuit breaker is open."""
    state = execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)
    return state.get('state') == 'open'

def get_circuit_breaker_state(name: str) -> Dict[str, Any]:
    """Get circuit breaker state."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)

# ===== CACHE WRAPPERS =====

def cache_get(key: str) -> Any:
    """Get cached value."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key)

def cache_set(key: str, value: Any, ttl: Optional[float] = None, **kwargs) -> None:
    """Set cached value."""
    execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl, **kwargs)

def cache_exists(key: str) -> bool:
    """Check if cache key exists."""
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key)

def cache_delete(key: str) -> bool:
    """Delete cache key."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)

def cache_clear() -> None:
    """Clear all cache."""
    execute_operation(GatewayInterface.CACHE, 'clear')

def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return execute_operation(GatewayInterface.CACHE, 'get_stats')

# ===== LOGGING WRAPPERS =====

def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, **kwargs)

def log_error(message: str, error: Optional[Exception] = None, **kwargs) -> None:
    """Log error message."""
    execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, **kwargs)

def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, **kwargs)

def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, **kwargs)

def log_operation_start(operation_name: str, **kwargs) -> None:
    """
    Log operation start.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation being started
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation_name=operation_name, **kwargs)

def log_operation_success(operation_name: str, duration_ms: float, **kwargs) -> None:
    """
    Log operation success.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation that succeeded
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation_name=operation_name, duration_ms=duration_ms, **kwargs)

def log_operation_failure(operation_name: str, error: str, **kwargs) -> None:
    """
    Log operation failure.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation that failed
        error: Error description
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation_name=operation_name, error=error, **kwargs)

# ===== SECURITY WRAPPERS =====

def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate HTTP request."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request=request)

def validate_token(token: str) -> bool:
    """Validate authentication token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)

def encrypt_data(data: str) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)

def decrypt_data(data: str) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', data=data)

def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id', prefix=prefix)

def validate_string(value: str, **kwargs) -> bool:
    """Validate string."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_string', value=value, **kwargs)

def validate_email(email: str) -> bool:
    """Validate email address."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_email', email=email)

def validate_url(url: str) -> bool:
    """Validate URL."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_url', url=url)

def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """Hash data."""
    return execute_operation(GatewayInterface.SECURITY, 'hash', data=data, algorithm=algorithm)

def verify_hash(data: str, hash_value: str, algorithm: str = 'sha256') -> bool:
    """Verify hash."""
    return execute_operation(GatewayInterface.SECURITY, 'verify_hash', data=data, hash_value=hash_value, algorithm=algorithm)

def sanitize_input(data: str) -> str:
    """Sanitize input data."""
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)

def sanitize_for_log(data: Any) -> Any:
    """
    Sanitize data for safe logging - removes PII and sensitive fields.
    
    Related CVE: CVE-LOG-001 (Sensitive Data Exposure in Logs)
    """
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)

# ===== NEW CACHE SECURITY VALIDATORS (2025.10.20) =====

def validate_cache_key(key: str) -> None:
    """
    Validate cache key format and safety.
    
    Validates cache keys against security rules:
    - Length: 1-255 characters
    - Characters: [a-zA-Z0-9_\\-:.]
    - Rejects: control characters, path traversal, special characters
    
    Args:
        key: Cache key to validate
        
    Raises:
        ValueError: If key is invalid with specific reason
    
    Related CVE: CVE-SUGA-2025-001 (Cache Key Injection)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_cache_key', key=key)

def validate_ttl(ttl: float) -> None:
    """
    Validate TTL (time-to-live) value is within acceptable range.
    
    Validates TTL boundaries:
    - Minimum: 1 second (prevents rapid churn)
    - Maximum: 86400 seconds / 24 hours (prevents resource exhaustion)
    - Rejects: NaN, infinity, negative values
    
    Args:
        ttl: Time-to-live in seconds
        
    Raises:
        ValueError: If TTL is out of bounds with specific reason
    
    Related CVE: CVE-SUGA-2025-002 (TTL Boundary Exploitation)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_ttl', ttl=ttl)

def validate_module_name(module_name: str) -> None:
    """
    Validate module name for LUGS (Lazy Unload with Graceful State) dependency tracking.
    
    Validates module names against security rules:
    - Pattern: Valid Python identifier (letters, digits, underscores)
    - Length: 1-100 characters
    - Rejects: path separators, control characters, special characters
    
    Args:
        module_name: Python module name to validate
        
    Raises:
        ValueError: If module name is invalid with specific reason
    
    Related CVE: CVE-SUGA-2025-004 (LUGS Dependency Poisoning)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_module_name', module_name=module_name)

def validate_number_range(value: float, min_value: float, max_value: float, name: str = "value") -> None:
    """
    Generic numeric validation with bounds checking.
    
    Validates numeric values are within specified range and not special values:
    - Range: min_value <= value <= max_value
    - Rejects: NaN, infinity (positive or negative)
    
    Args:
        value: Numeric value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)
        name: Name of value for error messages (default: "value")
        
    Raises:
        ValueError: If value is out of range or special value with specific reason
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_number_range', 
                     value=value, min_value=min_value, max_value=max_value, name=name)

# ===== METRICS WRAPPERS =====

def record_metric(name: str, value: float, **kwargs) -> None:
    """Record metric."""
    execute_operation(GatewayInterface.METRICS, 'record', name=name, value=value, **kwargs)

def increment_counter(name: str, value: int = 1, **kwargs) -> None:
    """Increment counter."""
    execute_operation(GatewayInterface.METRICS, 'increment', name=name, value=value, **kwargs)

def get_metrics_stats() -> Dict[str, Any]:
    """Get metrics statistics."""
    return execute_operation(GatewayInterface.METRICS, 'get_stats')

def record_operation_metric(operation_name: str, duration_ms: float, success: bool = True, **kwargs) -> None:
    """
    Record operation metric.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation being recorded
        duration_ms: Operation duration in milliseconds
        success: Whether operation succeeded (default: True)
        **kwargs: Additional metric dimensions
    """
    execute_operation(GatewayInterface.METRICS, 'record_operation', operation_name=operation_name, duration_ms=duration_ms, success=success, **kwargs)

def record_error_metric(error_type: str, **kwargs) -> None:
    """Record error metric."""
    execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, **kwargs)

def record_cache_metric(operation_name: str, hit: bool, **kwargs) -> None:
    """
    Record cache metric.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of cache operation (e.g. 'get', 'set')
        hit: Whether cache operation was a hit (True) or miss (False)
        **kwargs: Additional metric dimensions
    """
    execute_operation(GatewayInterface.METRICS, 'record_cache', operation_name=operation_name, hit=hit, **kwargs)

def record_api_metric(endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs) -> None:
    """Record API metric."""
    execute_operation(GatewayInterface.METRICS, 'record_api', endpoint=endpoint, method=method, status_code=status_code, duration_ms=duration_ms, **kwargs)

# ===== CONFIG WRAPPERS =====

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return execute_operation(GatewayInterface.CONFIG, 'get', key=key, default=default)

def set_config(key: str, value: Any) -> None:
    """Set configuration value."""
    execute_operation(GatewayInterface.CONFIG, 'set', key=key, value=value)

def get_config_category(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category=category)

def reload_config() -> None:
    """Reload configuration."""
    execute_operation(GatewayInterface.CONFIG, 'reload')

def switch_config_preset(preset: str) -> None:
    """Switch configuration preset."""
    execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset=preset)

def get_config_state() -> Dict[str, Any]:
    """Get configuration state."""
    return execute_operation(GatewayInterface.CONFIG, 'get_state')

def load_config_from_environment() -> None:
    """Load configuration from environment variables."""
    execute_operation(GatewayInterface.CONFIG, 'load_from_environment')

def load_config_from_file(file_path: str) -> None:
    """Load configuration from file."""
    execute_operation(GatewayInterface.CONFIG, 'load_from_file', file_path=file_path)

def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_all')

# ===== SINGLETON WRAPPERS =====

def singleton_get(key: str) -> Any:
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', key=key)

def singleton_has(key: str) -> bool:
    """Check if singleton exists."""
    return execute_operation(GatewayInterface.SINGLETON, 'has', key=key)

def singleton_delete(key: str) -> bool:
    """Delete singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'delete', key=key)

def singleton_clear() -> None:
    """Clear all singletons."""
    execute_operation(GatewayInterface.SINGLETON, 'clear')

def singleton_stats() -> Dict[str, Any]:
    """Get singleton statistics."""
    return execute_operation(GatewayInterface.SINGLETON, 'stats')

# ===== SINGLETON MEMORY WRAPPERS =====

def get_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_memory_stats')

def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics including GC info."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_comprehensive_memory_stats')

def check_lambda_memory_compliance() -> Dict[str, Any]:
    """Check if memory usage is within Lambda 128MB limit."""
    return execute_operation(GatewayInterface.SINGLETON, 'check_lambda_memory_compliance')

def force_memory_cleanup() -> Dict[str, Any]:
    """Force aggressive memory cleanup."""
    return execute_operation(GatewayInterface.SINGLETON, 'force_memory_cleanup')

def optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage with multi-strategy approach."""
    return execute_operation(GatewayInterface.SINGLETON, 'optimize_memory')

def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies."""
    return execute_operation(GatewayInterface.SINGLETON, 'force_comprehensive_memory_cleanup')

def emergency_memory_preserve() -> Dict[str, Any]:
    """Emergency memory preservation for critical situations."""
    return execute_operation(GatewayInterface.SINGLETON, 'emergency_memory_preserve')

# ===== INITIALIZATION WRAPPERS =====

def initialize_system(**kwargs) -> Dict[str, Any]:
    """Initialize system."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'initialize', **kwargs)

def get_initialization_status() -> Dict[str, Any]:
    """Get initialization status."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_status')

def set_initialization_flag(flag: str, value: bool) -> None:
    """Set initialization flag."""
    execute_operation(GatewayInterface.INITIALIZATION, 'set_flag', flag=flag, value=value)

def get_initialization_flag(flag: str) -> bool:
    """Get initialization flag."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_flag', flag=flag)

# ===== HTTP_CLIENT WRAPPERS =====

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

def reset_http_client_state() -> None:
    """Reset HTTP client state."""
    execute_operation(GatewayInterface.HTTP_CLIENT, 'reset_state')

# ===== WEBSOCKET WRAPPERS =====

def websocket_connect(url: str, **kwargs) -> Dict[str, Any]:
    """Connect to WebSocket."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', url=url, **kwargs)

def websocket_send(connection_id: str, message: Any, **kwargs) -> None:
    """Send WebSocket message."""
    execute_operation(GatewayInterface.WEBSOCKET, 'send', connection_id=connection_id, message=message, **kwargs)

def websocket_receive(connection_id: str, **kwargs) -> Any:
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', connection_id=connection_id, **kwargs)

def websocket_close(connection_id: str, **kwargs) -> None:
    """Close WebSocket connection."""
    execute_operation(GatewayInterface.WEBSOCKET, 'close', connection_id=connection_id, **kwargs)

def websocket_request(url: str, message: Any, timeout: Optional[float] = None, **kwargs) -> Any:
    """Make WebSocket request (connect, send, receive, close)."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', url=url, message=message, timeout=timeout, **kwargs)

# ===== CIRCUIT_BREAKER WRAPPERS =====

def get_circuit_breaker(name: str, failure_threshold: int = 5, timeout: float = 60.0) -> Any:
    """Get circuit breaker."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name, failure_threshold=failure_threshold, timeout=timeout)

def execute_with_circuit_breaker(name: str, func: Any, args: tuple = (), **kwargs) -> Any:
    """Execute function with circuit breaker protection."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'call', name=name, func=func, args=args, **kwargs)

def get_all_circuit_breaker_states() -> Dict[str, Dict[str, Any]]:
    """Get all circuit breaker states."""
    return execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get_all_states')

def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers."""
    execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'reset_all')

# ===== UTILITY WRAPPERS =====

def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Format HTTP response."""
    return execute_operation(GatewayInterface.UTILITY, 'format_response', status_code=status_code, body=body, headers=headers)

def parse_json(data: str) -> Dict[str, Any]:
    """Parse JSON string."""
    return execute_operation(GatewayInterface.UTILITY, 'parse_json', data=data)

def safe_get(dictionary: Dict, key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    return execute_operation(GatewayInterface.UTILITY, 'safe_get', dictionary=dictionary, key_path=key_path, default=default)

def generate_uuid() -> str:
    """Generate UUID."""
    return execute_operation(GatewayInterface.UTILITY, 'generate_uuid')

def get_timestamp() -> float:
    """Get current timestamp."""
    return execute_operation(GatewayInterface.UTILITY, 'get_timestamp')

def time_operation(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Time an operation execution.
    
    Wrapper for UTILITY interface time_operation function.
    Executes function and returns result with duration in milliseconds.
    
    Args:
        func: Function to execute and time
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Tuple of (result, duration_ms)
        
    Example:
        >>> result, duration = time_operation(expensive_function, arg1, arg2)
        >>> log_info(f"Operation completed in {duration:.2f}ms")
        >>> record_metric('operation.duration_ms', duration)
    """
    return execute_operation(GatewayInterface.UTILITY, 'time_operation', func=func, args=args, kwargs=kwargs)

# ===== DEBUG WRAPPERS =====

def check_component_health(component: str) -> Dict[str, Any]:
    """Check component health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_component_health', component=component)

def check_gateway_health() -> Dict[str, Any]:
    """Check gateway health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_gateway_health')

def diagnose_system_health() -> Dict[str, Any]:
    """Diagnose system health."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_system_health')

def run_debug_tests() -> Dict[str, Any]:
    """Run debug tests."""
    return execute_operation(GatewayInterface.DEBUG, 'run_debug_tests')

def validate_system_architecture() -> Dict[str, Any]:
    """Validate system architecture."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_system_architecture')

# ===== EXPORTS =====

__all__ = [
    # Configuration Helpers
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    
    # Circuit Breaker Helpers
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    
    # CACHE wrappers
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # LOGGING wrappers
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # SECURITY wrappers (includes 4 NEW cache validators)
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
    'sanitize_for_log',
    'sanitize_input',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
    
    # METRICS wrappers
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    
    # CONFIG wrappers
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # SINGLETON wrappers (includes memory monitoring)
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    
    # INITIALIZATION wrappers
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # HTTP_CLIENT wrappers
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    
    # WEBSOCKET wrappers
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # CIRCUIT_BREAKER wrappers
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # UTILITY wrappers
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'time_operation',  # NEW in 2025.10.21.01
    
    # DEBUG wrappers
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
]

# EOF
