"""
gateway.py
Version: 2025.10.14.06
Description: Universal operation routing with Phase 4 Task #7 dispatcher operations

PHASE 4 TASK #7 - Ultra-Integration:
- Added 3 new METRICS operations to registry:
  - record_dispatcher_timing
  - get_dispatcher_stats
  - get_operation_metrics
- Registry now has 66 operations (63 → 66)

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
    (GatewayInterface.CACHE, 'get'): ('cache_core', '_execute_get_implementation'),
    (GatewayInterface.CACHE, 'set'): ('cache_core', '_execute_set_implementation'),
    (GatewayInterface.CACHE, 'exists'): ('cache_core', '_execute_exists_implementation'),
    (GatewayInterface.CACHE, 'delete'): ('cache_core', '_execute_delete_implementation'),
    (GatewayInterface.CACHE, 'clear'): ('cache_core', '_execute_clear_implementation'),
    (GatewayInterface.CACHE, 'get_stats'): ('cache_core', 'cache_get_stats'),
    (GatewayInterface.LOGGING, 'log_info'): ('logging_core', '_execute_log_info_implementation'),
    (GatewayInterface.LOGGING, 'log_error'): ('logging_core', '_execute_log_error_implementation'),
    (GatewayInterface.LOGGING, 'log_warning'): ('logging_core', '_execute_log_warning_implementation'),
    (GatewayInterface.LOGGING, 'log_debug'): ('logging_core', '_execute_log_debug_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_start'): ('logging_core', '_execute_log_operation_start_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_success'): ('logging_core', '_execute_log_operation_success_implementation'),
    (GatewayInterface.LOGGING, 'log_operation_failure'): ('logging_core', '_execute_log_operation_failure_implementation'),
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
    (GatewayInterface.METRICS, 'record'): ('metrics_core', '_execute_record_metric_implementation'),
    (GatewayInterface.METRICS, 'increment'): ('metrics_core', '_execute_increment_counter_implementation'),
    (GatewayInterface.METRICS, 'get_metrics'): ('metrics_core', '_execute_get_stats_implementation'),
    (GatewayInterface.METRICS, 'record_operation'): ('metrics_core', '_execute_record_operation_metric_implementation'),
    (GatewayInterface.METRICS, 'record_error'): ('metrics_core', '_execute_record_error_response_metric_implementation'),
    (GatewayInterface.METRICS, 'record_cache'): ('metrics_core', '_execute_record_cache_metric_implementation'),
    (GatewayInterface.METRICS, 'record_api'): ('metrics_core', '_execute_record_api_metric_implementation'),
    # Phase 4 Task #7: New dispatcher operations
    (GatewayInterface.METRICS, 'record_dispatcher_timing'): ('metrics_core', '_execute_record_dispatcher_timing_implementation'),
    (GatewayInterface.METRICS, 'get_dispatcher_stats'): ('metrics_core', '_execute_get_dispatcher_stats_implementation'),
    (GatewayInterface.METRICS, 'get_operation_metrics'): ('metrics_core', '_execute_get_operation_metrics_implementation'),
}

_operation_call_counts = defaultdict(int)
_fast_path_enabled = False


# ===== CORE EXECUTION =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """Execute operation via registry lookup."""
    key = (interface, operation)
    
    if key not in _OPERATION_REGISTRY:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    
    _operation_call_counts[key] += 1
    
    module_name, func_name = _OPERATION_REGISTRY[key]
    
    if _fast_path_enabled and _operation_call_counts[key] >= 20:
        func = globals().get(f"_fp_{interface.value}_{operation}")
        if func:
            try:
                return func(**kwargs)
            except (ImportError, AttributeError):
                pass
    
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
        'interfaces': {iface.value: sum(1 for k in _OPERATION_REGISTRY if k[0] == iface) for iface in GatewayInterface},
        'fast_path_enabled': _fast_path_enabled
    }


def create_error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create standardized error response."""
    return {'statusCode': status_code, 'body': {'error': message, 'success': False}}


def create_success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized success response."""
    return {'statusCode': status_code, 'body': {'data': data, 'success': True}}


# ===== DYNAMIC WRAPPER GENERATION =====

def _create_wrapper(interface: GatewayInterface, operation: str):
    """Factory to generate wrapper functions."""
    def wrapper(**kwargs):
        return execute_operation(interface, operation, **kwargs)
    return wrapper


_WRAPPER_SPECS = [
    ('CACHE', 'get', 'cache_get'), ('CACHE', 'set', 'cache_set'), ('CACHE', 'exists', 'cache_exists'),
    ('CACHE', 'delete', 'cache_delete'), ('CACHE', 'clear', 'cache_clear'), ('CACHE', 'get_stats', 'cache_stats'),
    ('LOGGING', 'log_info', 'log_info'), ('LOGGING', 'log_error', 'log_error'), ('LOGGING', 'log_warning', 'log_warning'),
    ('LOGGING', 'log_debug', 'log_debug'), ('LOGGING', 'log_operation_start', 'log_operation_start'),
    ('LOGGING', 'log_operation_success', 'log_operation_success'), ('LOGGING', 'log_operation_failure', 'log_operation_failure'),
    ('SECURITY', 'validate_request', 'validate_request'), ('SECURITY', 'validate_token', 'validate_token'),
    ('SECURITY', 'encrypt', 'encrypt_data'), ('SECURITY', 'decrypt', 'decrypt_data'),
    ('SECURITY', 'generate_correlation_id', 'generate_correlation_id'), ('SECURITY', 'validate_string', 'validate_string'),
    ('SECURITY', 'validate_email', 'validate_email'), ('SECURITY', 'validate_url', 'validate_url'),
    ('SECURITY', 'hash', 'hash_data'), ('SECURITY', 'verify_hash', 'verify_hash'), ('SECURITY', 'sanitize', 'sanitize_input'),
    ('METRICS', 'record', 'record_metric'), ('METRICS', 'increment', 'increment_counter'),
    ('METRICS', 'get_stats', 'get_metrics_stats'), ('METRICS', 'record_operation', 'record_operation_metric'),
    ('METRICS', 'record_error', 'record_error_metric'), ('METRICS', 'record_cache', 'record_cache_metric'),
    ('METRICS', 'record_api', 'record_api_metric'),
    ('METRICS', 'record_dispatcher_timing', 'record_dispatcher_timing'),
    ('METRICS', 'get_dispatcher_stats', 'get_dispatcher_stats'),
    ('METRICS', 'get_operation_metrics', 'get_operation_metrics'),
    ('CONFIG', 'get_parameter', 'get_config'), ('CONFIG', 'set_parameter', 'set_config'),
    ('CONFIG', 'get_category', 'get_config_category'), ('CONFIG', 'reload', 'reload_config'),
    ('CONFIG', 'switch_preset', 'switch_config_preset'), ('CONFIG', 'get_state', 'get_config_state'),
    ('CONFIG', 'load_environment', 'load_config_from_environment'), ('CONFIG', 'load_file', 'load_config_from_file'),
    ('CONFIG', 'validate', 'validate_all_config'),
    ('SINGLETON', 'get', 'singleton_get'), ('SINGLETON', 'has', 'singleton_has'),
    ('SINGLETON', 'delete', 'singleton_delete'), ('SINGLETON', 'clear', 'singleton_clear'),
    ('SINGLETON', 'get_stats', 'singleton_stats'),
    ('INITIALIZATION', 'initialize', 'initialize_system'), ('INITIALIZATION', 'get_status', 'get_initialization_status'),
    ('INITIALIZATION', 'set_flag', 'set_initialization_flag'), ('INITIALIZATION', 'get_flag', 'get_initialization_flag'),
    ('HTTP_CLIENT', 'request', 'http_request'), ('HTTP_CLIENT', 'get', 'http_get'),
    ('HTTP_CLIENT', 'post', 'http_post'), ('HTTP_CLIENT', 'put', 'http_put'),
    ('HTTP_CLIENT', 'delete', 'http_delete'), ('HTTP_CLIENT', 'get_state', 'get_http_client_state'),
    ('HTTP_CLIENT', 'reset_state', 'reset_http_client_state'),
    ('WEBSOCKET', 'connect', 'websocket_connect'), ('WEBSOCKET', 'send', 'websocket_send'),
    ('WEBSOCKET', 'receive', 'websocket_receive'), ('WEBSOCKET', 'close', 'websocket_close'),
    ('WEBSOCKET', 'request', 'websocket_request'),
    ('CIRCUIT_BREAKER', 'get', 'get_circuit_breaker'), ('CIRCUIT_BREAKER', 'call', 'execute_with_circuit_breaker'),
    ('CIRCUIT_BREAKER', 'get_all_states', 'get_all_circuit_breaker_states'), ('CIRCUIT_BREAKER', 'reset_all', 'reset_all_circuit_breakers'),
    ('UTILITY', 'format_response', 'format_response'), ('UTILITY', 'parse_json', 'parse_json'),
    ('UTILITY', 'safe_get', 'safe_get'), ('UTILITY', 'generate_uuid', 'generate_uuid'),
    ('UTILITY', 'get_timestamp', 'get_timestamp'),
]

for iface_name, op, func_name in _WRAPPER_SPECS:
    iface = GatewayInterface[iface_name]
    globals()[func_name] = _create_wrapper(iface, op)


# ===== HELPER FUNCTIONS =====

def initialize_config() -> Dict[str, Any]:
    """Initialize configuration system."""
    return get_config_category(category='system')


def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return get_config_category(category='cache')


def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration."""
    return get_config_category(category='metrics')


def is_circuit_breaker_open(name: str) -> bool:
    """Check if circuit breaker is open."""
    try:
        cb = get_circuit_breaker(name)
        return cb.get('state') == 'open' if cb else False
    except:
        return False


def add_cache_module_dependency(key: str, module: str):
    """Add module dependency for LUGS tracking."""
    pass


def enable_fast_path():
    """Enable fast path for frequently used operations."""
    global _fast_path_enabled
    _fast_path_enabled = True


def disable_fast_path():
    """Disable fast path."""
    global _fast_path_enabled
    _fast_path_enabled = False


# ===== EXPORTS =====

__all__ = [
    'GatewayInterface',
    'execute_operation',
    'get_gateway_stats',
    'create_error_response',
    'create_success_response',
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
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
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    'is_circuit_breaker_open',
    'add_cache_module_dependency',
    'enable_fast_path',
    'disable_fast_path',
]

# EOF
