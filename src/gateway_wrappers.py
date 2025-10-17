"""
gateway_wrappers.py - Gateway Convenience Wrapper Functions
Version: 2025.10.17.04
Description: Wrapper functions that call execute_operation() for cleaner code

CHANGELOG:
- 2025.10.17.04: Added missing SINGLETON memory monitoring wrappers (Issue #11 fix)
  - get_memory_stats() - Get current memory usage
  - get_comprehensive_memory_stats() - Detailed memory + GC info
  - check_lambda_memory_compliance() - Check 128MB limit
  - force_memory_cleanup() - Aggressive cleanup
  - optimize_memory() - Multi-strategy optimization
  - force_comprehensive_memory_cleanup() - Full cleanup
  - emergency_memory_preserve() - Critical memory preservation
- 2025.10.16.01: Fixed initialize_config, sanitize_input, websocket_request, increment_counter

DESIGN DECISION: Memory Monitoring Functions
Reason: singleton_memory.py has comprehensive memory functions but they weren't
        exposed through gateway wrappers, making them hard to discover/use
Impact: Other modules can now easily monitor Lambda 128MB compliance
Pattern: All memory functions route through SINGLETON interface to singleton_memory.py

FIXES APPLIED (2025.10.16):
- BUG #1: Fixed initialize_config to use 'initialize' operation (was 'reload')
- BUG #2: Fixed sanitize_input parameter type from Any to str
- BUG #3: Added timeout parameter to websocket_request wrapper
- BUG #4: Fixed increment_counter value parameter type from float to int

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

from typing import Any, Dict, Optional
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

def cache_get(key: str, default: Any = None) -> Optional[Any]:
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key, default=default)

def cache_set(key: str, value: Any, ttl: Optional[float] = None, source_module: Optional[str] = None) -> None:
    """Set value in cache."""
    execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl, source_module=source_module)

def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key)

def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)

def cache_clear() -> int:
    """Clear all cache entries."""
    return execute_operation(GatewayInterface.CACHE, 'clear')

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

def log_operation_start(operation: str, **kwargs) -> None:
    """Log operation start."""
    execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation=operation, **kwargs)

def log_operation_success(operation: str, duration_ms: float, **kwargs) -> None:
    """Log operation success."""
    execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation=operation, duration_ms=duration_ms, **kwargs)

def log_operation_failure(operation: str, error: str, **kwargs) -> None:
    """Log operation failure."""
    execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation=operation, error=error, **kwargs)

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

def record_operation_metric(operation: str, duration_ms: float, success: bool = True, **kwargs) -> None:
    """Record operation metric."""
    execute_operation(GatewayInterface.METRICS, 'record_operation', operation=operation, duration_ms=duration_ms, success=success, **kwargs)

def record_error_metric(error_type: str, **kwargs) -> None:
    """Record error metric."""
    execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, **kwargs)

def record_cache_metric(operation: str, hit: bool, **kwargs) -> None:
    """Record cache metric."""
    execute_operation(GatewayInterface.METRICS, 'record_cache', operation=operation, hit=hit, **kwargs)

def record_api_metric(api: str, duration_ms: float, **kwargs) -> None:
    """Record API metric."""
    execute_operation(GatewayInterface.METRICS, 'record_api', api=api, duration_ms=duration_ms, **kwargs)

# ===== CONFIG WRAPPERS =====

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)

def set_config(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)

def get_config_category(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category=category)

def reload_config() -> Dict[str, Any]:
    """Reload configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'reload')

def switch_config_preset(preset: str) -> Dict[str, Any]:
    """Switch configuration preset."""
    return execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset=preset)

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

# ===== SINGLETON WRAPPERS =====

def singleton_get(name: str, factory_func: Optional[Any] = None) -> Optional[Any]:
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

# ===== SINGLETON MEMORY MONITORING WRAPPERS (NEW - Issue #11 Fix) =====

def get_memory_stats() -> Dict[str, Any]:
    """
    Get current memory statistics for Lambda environment.
    
    Returns standardized response with memory usage in MB, compliance status,
    and percentage of 128MB Lambda limit used.
    
    Returns:
        Dict containing:
        - rss_mb: Resident set size in megabytes
        - available_mb: Available memory (128 - current)
        - percent_used: Percentage of 128MB limit
        - compliant: Boolean if under 128MB
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_memory_stats')

def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """
    Get comprehensive memory statistics including garbage collection info.
    
    Returns detailed memory stats plus GC statistics (collections, tracked objects).
    More comprehensive than get_memory_stats() but slightly higher overhead.
    
    Returns:
        Dict containing:
        - memory: {rss_mb, available_mb, percent_used, compliant}
        - gc: {collections, stats, tracked_objects}
        - system: {lambda_limit_mb, pressure_level}
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_comprehensive_memory_stats')

def check_lambda_memory_compliance() -> Dict[str, Any]:
    """
    Check if current memory usage is within Lambda 128MB limit.
    
    Fast, lightweight check for compliance. Use this in hot paths where
    you need to quickly verify memory is within limits.
    
    Returns:
        Dict containing:
        - compliant: Boolean if under 128MB
        - current_mb: Current memory usage
        - limit_mb: Lambda limit (128)
        - margin_mb: Remaining headroom
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'check_lambda_memory_compliance')

def force_memory_cleanup() -> Dict[str, Any]:
    """
    Force aggressive memory cleanup with garbage collection.
    
    Runs gc.collect() and reports memory freed. Use when memory pressure
    is detected or before memory-intensive operations.
    
    Returns:
        Dict containing:
        - gc_collected: Number of objects collected
        - memory_before_mb: Memory before cleanup
        - memory_after_mb: Memory after cleanup
        - memory_freed_mb: Amount freed
        - compliant: Post-cleanup compliance status
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'force_memory_cleanup')

def optimize_memory() -> Dict[str, Any]:
    """
    Optimize memory usage with multiple cleanup strategies.
    
    More comprehensive than force_memory_cleanup(). Runs:
    - Multi-generation garbage collection
    - Singleton cache clearing if memory > 100MB
    - Repeated cleanup passes
    
    Use this when memory pressure is high (>100MB) or before critical operations.
    
    Returns:
        Dict containing:
        - strategies_applied: List of optimization steps taken
        - final_memory_mb: Memory after optimization
        - compliant: Compliance status
        - optimization_count: Number of strategies applied
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'optimize_memory')

def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """
    Force comprehensive memory cleanup with all strategies.
    
    Most aggressive cleanup option. Combines:
    - Multi-pass garbage collection
    - Singleton clearing
    - Module cache optimization
    
    WARNING: May impact performance. Only use when critical.
    
    Returns:
        Dict containing:
        - cleanup_phases: List of cleanup phases executed
        - memory_before_mb: Initial memory
        - memory_after_mb: Final memory
        - memory_freed_mb: Total freed
        - compliant: Final compliance status
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'force_comprehensive_memory_cleanup')

def emergency_memory_preserve() -> Dict[str, Any]:
    """
    Emergency memory preservation for critical situations.
    
    CRITICAL USE ONLY: Clears ALL singletons and forces aggressive GC.
    Only call this when approaching Lambda 128MB limit and normal
    cleanup has failed. Will disrupt application state.
    
    Returns:
        Dict containing:
        - emergency_mode: Boolean (True if emergency steps taken)
        - emergency_steps: List of emergency actions
        - memory_before_mb: Memory before emergency cleanup
        - memory_after_mb: Memory after emergency cleanup
        - memory_freed_mb: Amount freed
        - now_compliant: Compliance after emergency measures
        - correlation_id: Request correlation ID
    """
    return execute_operation(GatewayInterface.SINGLETON, 'emergency_memory_preserve')

# ===== INITIALIZATION WRAPPERS =====

def initialize_system(**kwargs) -> Dict[str, Any]:
    """Initialize system."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'initialize', **kwargs)

def get_initialization_status() -> Dict[str, Any]:
    """Get initialization status."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'get_status')

def set_initialization_flag(flag: str, value: Any) -> None:
    """Set initialization flag."""
    execute_operation(GatewayInterface.INITIALIZATION, 'set_flag', flag=flag, value=value)

def get_initialization_flag(flag: str) -> Any:
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

def reset_http_client_state() -> Dict[str, Any]:
    """Reset HTTP client state."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'reset_state')

# ===== WEBSOCKET WRAPPERS =====

def websocket_connect(url: str, **kwargs) -> Dict[str, Any]:
    """Connect to WebSocket."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'connect', url=url, **kwargs)

def websocket_send(connection_id: str, message: Any, **kwargs) -> Dict[str, Any]:
    """Send WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'send', connection_id=connection_id, message=message, **kwargs)

def websocket_receive(connection_id: str, **kwargs) -> Dict[str, Any]:
    """Receive WebSocket message."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'receive', connection_id=connection_id, **kwargs)

def websocket_close(connection_id: str, **kwargs) -> Dict[str, Any]:
    """Close WebSocket connection."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'close', connection_id=connection_id, **kwargs)

def websocket_request(url: str, message: Any, timeout: float = 30.0, **kwargs) -> Dict[str, Any]:
    """Make WebSocket request."""
    return execute_operation(GatewayInterface.WEBSOCKET, 'request', url=url, message=message, timeout=timeout, **kwargs)

# ===== CIRCUIT_BREAKER WRAPPERS =====

def get_circuit_breaker(name: str, failure_threshold: int = 5, timeout: int = 60) -> Dict[str, Any]:
    """Get circuit breaker state."""
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
    
    # CACHE
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # LOGGING
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # SECURITY
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
    
    # METRICS
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    
    # CONFIG
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # SINGLETON
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    
    # SINGLETON MEMORY MONITORING (NEW)
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    
    # INITIALIZATION
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # HTTP_CLIENT
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    
    # WEBSOCKET
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # CIRCUIT_BREAKER
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # UTILITY
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    
    # DEBUG
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
]

# EOF
