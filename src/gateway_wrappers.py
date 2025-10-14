"""
gateway_wrappers.py - Gateway Convenience Wrapper Functions
Version: 2025.10.14.02
Description: Dynamically generated convenience wrappers for all gateway operations

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

from typing import Dict, Any
from gateway_core import GatewayInterface, execute_operation

# ===== DYNAMIC WRAPPER GENERATION =====

def _create_wrapper(interface: GatewayInterface, operation: str):
    """Factory to generate wrapper functions."""
    def wrapper(**kwargs):
        return execute_operation(interface, operation, **kwargs)
    wrapper.__name__ = f"{interface.value}_{operation}"
    wrapper.__doc__ = f"Execute {operation} on {interface.value} interface"
    return wrapper

# Wrapper specifications for auto-generation
_WRAPPER_SPECS = [
    # CACHE wrappers
    ('CACHE', 'get', 'cache_get'),
    ('CACHE', 'set', 'cache_set'),
    ('CACHE', 'exists', 'cache_exists'),
    ('CACHE', 'delete', 'cache_delete'),
    ('CACHE', 'clear', 'cache_clear'),
    ('CACHE', 'get_stats', 'cache_stats'),
    
    # LOGGING wrappers
    ('LOGGING', 'log_info', 'log_info'),
    ('LOGGING', 'log_error', 'log_error'),
    ('LOGGING', 'log_warning', 'log_warning'),
    ('LOGGING', 'log_debug', 'log_debug'),
    ('LOGGING', 'log_operation_start', 'log_operation_start'),
    ('LOGGING', 'log_operation_success', 'log_operation_success'),
    ('LOGGING', 'log_operation_failure', 'log_operation_failure'),
    
    # SECURITY wrappers
    ('SECURITY', 'validate_request', 'validate_request'),
    ('SECURITY', 'validate_token', 'validate_token'),
    ('SECURITY', 'encrypt', 'encrypt_data'),
    ('SECURITY', 'decrypt', 'decrypt_data'),
    ('SECURITY', 'generate_correlation_id', 'generate_correlation_id'),
    ('SECURITY', 'validate_string', 'validate_string'),
    ('SECURITY', 'validate_email', 'validate_email'),
    ('SECURITY', 'validate_url', 'validate_url'),
    ('SECURITY', 'hash', 'hash_data'),
    ('SECURITY', 'verify_hash', 'verify_hash'),
    ('SECURITY', 'sanitize', 'sanitize_input'),
    
    # METRICS wrappers
    ('METRICS', 'record', 'record_metric'),
    ('METRICS', 'increment', 'increment_counter'),
    ('METRICS', 'get_stats', 'get_metrics_stats'),
    ('METRICS', 'record_operation', 'record_operation_metric'),
    ('METRICS', 'record_error', 'record_error_metric'),
    ('METRICS', 'record_cache', 'record_cache_metric'),
    ('METRICS', 'record_api', 'record_api_metric'),
    
    # CONFIG wrappers
    ('CONFIG', 'get_parameter', 'get_config'),
    ('CONFIG', 'set_parameter', 'set_config'),
    ('CONFIG', 'get_category', 'get_config_category'),
    ('CONFIG', 'reload', 'reload_config'),
    ('CONFIG', 'switch_preset', 'switch_config_preset'),
    ('CONFIG', 'get_state', 'get_config_state'),
    ('CONFIG', 'load_environment', 'load_config_from_environment'),
    ('CONFIG', 'load_file', 'load_config_from_file'),
    ('CONFIG', 'validate', 'validate_all_config'),
    
    # SINGLETON wrappers
    ('SINGLETON', 'get', 'singleton_get'),
    ('SINGLETON', 'has', 'singleton_has'),
    ('SINGLETON', 'delete', 'singleton_delete'),
    ('SINGLETON', 'clear', 'singleton_clear'),
    ('SINGLETON', 'get_stats', 'singleton_stats'),
    
    # INITIALIZATION wrappers
    ('INITIALIZATION', 'initialize', 'initialize_system'),
    ('INITIALIZATION', 'get_status', 'get_initialization_status'),
    ('INITIALIZATION', 'set_flag', 'set_initialization_flag'),
    ('INITIALIZATION', 'get_flag', 'get_initialization_flag'),
    
    # HTTP_CLIENT wrappers
    ('HTTP_CLIENT', 'request', 'http_request'),
    ('HTTP_CLIENT', 'get', 'http_get'),
    ('HTTP_CLIENT', 'post', 'http_post'),
    ('HTTP_CLIENT', 'put', 'http_put'),
    ('HTTP_CLIENT', 'delete', 'http_delete'),
    ('HTTP_CLIENT', 'get_state', 'get_http_client_state'),
    ('HTTP_CLIENT', 'reset_state', 'reset_http_client_state'),
    
    # WEBSOCKET wrappers
    ('WEBSOCKET', 'connect', 'websocket_connect'),
    ('WEBSOCKET', 'send', 'websocket_send'),
    ('WEBSOCKET', 'receive', 'websocket_receive'),
    ('WEBSOCKET', 'close', 'websocket_close'),
    ('WEBSOCKET', 'request', 'websocket_request'),
    
    # CIRCUIT_BREAKER wrappers
    ('CIRCUIT_BREAKER', 'get', 'get_circuit_breaker'),
    ('CIRCUIT_BREAKER', 'call', 'execute_with_circuit_breaker'),
    ('CIRCUIT_BREAKER', 'get_all_states', 'get_all_circuit_breaker_states'),
    ('CIRCUIT_BREAKER', 'reset_all', 'reset_all_circuit_breakers'),
    
    # UTILITY wrappers
    ('UTILITY', 'format_response', 'format_response'),
    ('UTILITY', 'parse_json', 'parse_json'),
    ('UTILITY', 'safe_get', 'safe_get'),
    ('UTILITY', 'generate_uuid', 'generate_uuid'),
    ('UTILITY', 'get_timestamp', 'get_timestamp'),
    
    # DEBUG wrappers
    ('DEBUG', 'check_component_health', 'check_component_health'),
    ('DEBUG', 'check_gateway_health', 'check_gateway_health'),
    ('DEBUG', 'diagnose_system_health', 'diagnose_system_health'),
    ('DEBUG', 'run_tests', 'run_debug_tests'),
    ('DEBUG', 'validate_system', 'validate_system_architecture'),
]

# Generate wrapper functions
for interface_name, operation, wrapper_name in _WRAPPER_SPECS:
    interface = getattr(GatewayInterface, interface_name)
    globals()[wrapper_name] = _create_wrapper(interface, operation)

# ===== HELPER FUNCTIONS =====

def initialize_config() -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='system')

def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='cache')

def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='metrics')

def is_circuit_breaker_open(name: str) -> bool:
    """Check if circuit breaker is open."""
    breaker = execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)
    return breaker.get('state') == 'open' if breaker else False

def get_circuit_breaker_state(name: str) -> str:
    """Get circuit breaker state."""
    breaker = execute_operation(GatewayInterface.CIRCUIT_BREAKER, 'get', name=name)
    return breaker.get('state', 'unknown') if breaker else 'unknown'

# ===== EXPORTS =====

__all__ = [
    # Configuration Helpers
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    
    # Circuit Breaker Helpers
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    
    # Generated Wrappers - CACHE
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # Generated Wrappers - LOGGING
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # Generated Wrappers - SECURITY
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
    
    # Generated Wrappers - METRICS
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    
    # Generated Wrappers - CONFIG
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # Generated Wrappers - SINGLETON
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    
    # Generated Wrappers - INITIALIZATION
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # Generated Wrappers - HTTP_CLIENT
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    
    # Generated Wrappers - WEBSOCKET
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # Generated Wrappers - CIRCUIT_BREAKER
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # Generated Wrappers - UTILITY
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    
    # Generated Wrappers - DEBUG
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
]

# EOF
