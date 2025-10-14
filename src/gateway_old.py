"""
gateway.py - Universal operation routing with registry-based dispatch
Version: 2025.10.14.05
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
    (GatewayInterface.METRICS, 'get_stats'): ('metrics_core', '_execute_get_stats_implementation'),
    (GatewayInterface.METRICS, 'record_operation'): ('metrics_core', '_execute_record_operation_metric_implementation'),
    (GatewayInterface.METRICS, 'record_error'): ('metrics_core', '_execute_record_error_response_metric_implementation'),
    (GatewayInterface.METRICS, 'record_cache'): ('metrics_core', '_execute_record_cache_metric_implementation'),
    (GatewayInterface.METRICS, 'record_api'): ('metrics_core', '_execute_record_api_metric_implementation'),
    (GatewayInterface.CONFIG, 'get_parameter'): ('config_core', '_get_parameter_implementation'),
    (GatewayInterface.CONFIG, 'set_parameter'): ('config_core', '_set_parameter_implementation'),
    (GatewayInterface.CONFIG, 'get_category'): ('config_core', '_get_category_implementation'),
    (GatewayInterface.CONFIG, 'reload'): ('config_core', '_reload_implementation'),
    (GatewayInterface.CONFIG, 'switch_preset'): ('config_core', '_switch_preset_implementation'),
    (GatewayInterface.CONFIG, 'get_state'): ('config_core', '_get_state_implementation'),
    (GatewayInterface.CONFIG, 'load_environment'): ('config_core', '_load_environment_implementation'),
    (GatewayInterface.CONFIG, 'load_file'): ('config_core', '_load_file_implementation'),
    (GatewayInterface.CONFIG, 'validate'): ('config_core', '_validate_all_implementation'),
    (GatewayInterface.SINGLETON, 'get'): ('singleton_core', '_execute_get_implementation'),
    (GatewayInterface.SINGLETON, 'has'): ('singleton_core', '_execute_has_implementation'),
    (GatewayInterface.SINGLETON, 'delete'): ('singleton_core', '_execute_delete_implementation'),
    (GatewayInterface.SINGLETON, 'clear'): ('singleton_core', '_execute_clear_implementation'),
    (GatewayInterface.SINGLETON, 'get_stats'): ('singleton_core', '_execute_get_stats_implementation'),
    (GatewayInterface.INITIALIZATION, 'initialize'): ('initialization_core', '_execute_initialize_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_status'): ('initialization_core', '_execute_get_status_implementation'),
    (GatewayInterface.INITIALIZATION, 'set_flag'): ('initialization_core', '_execute_set_flag_implementation'),
    (GatewayInterface.INITIALIZATION, 'get_flag'): ('initialization_core', '_execute_get_flag_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'request'): ('http_client_core', 'http_request_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('http_client_core', 'http_get_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('http_client_core', 'http_post_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('http_client_core', 'http_put_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('http_client_core', 'http_delete_implementation'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('http_client_core', 'get_client_state'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('http_client_core', 'reset_client_state'),
    (GatewayInterface.WEBSOCKET, 'connect'): ('http_client_core', 'websocket_connect_implementation'),
    (GatewayInterface.WEBSOCKET, 'send'): ('http_client_core', 'websocket_send_implementation'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('http_client_core', 'websocket_receive_implementation'),
    (GatewayInterface.WEBSOCKET, 'close'): ('http_client_core', 'websocket_close_implementation'),
    (GatewayInterface.WEBSOCKET, 'request'): ('http_client_core', 'websocket_request_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get'): ('circuit_breaker_core', '_execute_get_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'call'): ('circuit_breaker_core', '_execute_call_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'get_all_states'): ('circuit_breaker_core', '_execute_get_all_states_implementation'),
    (GatewayInterface.CIRCUIT_BREAKER, 'reset_all'): ('circuit_breaker_core', '_execute_reset_all_implementation'),
    (GatewayInterface.UTILITY, 'format_response'): ('shared_utilities', '_execute_format_response_implementation'),
    (GatewayInterface.UTILITY, 'parse_json'): ('shared_utilities', '_execute_parse_json_implementation'),
    (GatewayInterface.UTILITY, 'safe_get'): ('shared_utilities', '_execute_safe_get_implementation'),
    (GatewayInterface.UTILITY, 'generate_uuid'): ('shared_utilities', '_generate_uuid_implementation'),
    (GatewayInterface.UTILITY, 'get_timestamp'): ('shared_utilities', '_get_timestamp_implementation'),
}

# ===== FAST PATH TRACKING =====

_operation_call_counts: Dict[Tuple[GatewayInterface, str], int] = {}
_fast_path_enabled = True

# ===== CORE DISPATCH =====

def execute_operation(interface: GatewayInterface, operation: str, **kwargs) -> Any:
    """Universal gateway routing with lazy loading and fast-path optimization."""
    global _operation_call_counts
    registry_key = (interface, operation)
    entry = _OPERATION_REGISTRY.get(registry_key)
    if not entry:
        raise ValueError(f"Unknown operation: {interface.value}.{operation}")
    module_name, func_name = entry
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

for interface_name, operation, wrapper_name in _WRAPPER_SPECS:
    interface = getattr(GatewayInterface, interface_name)
    globals()[wrapper_name] = _create_wrapper(interface, operation)

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
        breaker = get_circuit_breaker(name=name)
        return breaker.get('state') == 'open' if isinstance(breaker, dict) else False
    except:
        return False

def circuit_breaker_call(name: str, func: Callable, *args, **kwargs):
    """Alias for execute_with_circuit_breaker."""
    return execute_with_circuit_breaker(name=name, func=func, args=args, kwargs=kwargs)

# ===== FAST PATH MANAGEMENT =====

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

# ===== GATEWAY MANAGEMENT =====

def get_loaded_modules() -> Dict[str, Any]:
    """Get loaded module statistics."""
    import sys
    return {
        'total_modules': len(sys.modules),
        'gateway_modules': [m for m in sys.modules if m.endswith('_core') or m == 'gateway']
    }

# ===== EXPORTS =====

__all__ = [
    # Core
    'GatewayInterface',
    'execute_operation',
    'get_gateway_stats',
    'create_error_response',
    'create_success_response',
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
    'get_config',
    'set_config',
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
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    # Initialization (4)
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    # HTTP Client (7)
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    # WebSocket (5)
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    # Circuit Breaker (6)
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    'is_circuit_breaker_open',
    'circuit_breaker_call',
    # Utility (5)
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    # Fast Path (5)
    'enable_fast_path',
    'disable_fast_path',
    'reset_fast_path_stats',
    'get_fast_path_stats',
    'mark_module_hot',
    # Gateway (1)
    'get_loaded_modules',
]
# EOF
