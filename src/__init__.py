"""
__init__.py - Lambda Execution Engine Package Initialization
Version: 2025.10.14.01
Description: Package entry point that exports all gateway functions and interfaces

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

# Import all gateway exports - gateway.py is the SUGA hub
from gateway import (
    # Core
    GatewayInterface,
    execute_operation,
    initialize_lambda,
    get_gateway_stats,
    
    # Fast Path Management
    set_fast_path_threshold,
    enable_fast_path,
    disable_fast_path,
    clear_fast_path_cache,
    get_fast_path_stats,
    
    # Response Helpers
    create_error_response,
    create_success_response,
    
    # Configuration Helpers
    initialize_config,
    get_cache_config,
    get_metrics_config,
    
    # Circuit Breaker Helpers
    is_circuit_breaker_open,
    get_circuit_breaker_state,
    
    # CACHE Interface
    cache_get,
    cache_set,
    cache_exists,
    cache_delete,
    cache_clear,
    cache_stats,
    
    # LOGGING Interface
    log_info,
    log_error,
    log_warning,
    log_debug,
    log_operation_start,
    log_operation_success,
    log_operation_failure,
    
    # SECURITY Interface
    validate_request,
    validate_token,
    encrypt_data,
    decrypt_data,
    generate_correlation_id,
    validate_string,
    validate_email,
    validate_url,
    hash_data,
    verify_hash,
    sanitize_input,
    
    # METRICS Interface
    record_metric,
    increment_counter,
    get_metrics_stats,
    record_operation_metric,
    record_error_metric,
    record_cache_metric,
    record_api_metric,
    
    # CONFIG Interface
    get_config,
    set_config,
    get_config_category,
    reload_config,
    switch_config_preset,
    get_config_state,
    load_config_from_environment,
    load_config_from_file,
    validate_all_config,
    
    # SINGLETON Interface
    singleton_get,
    singleton_has,
    singleton_delete,
    singleton_clear,
    singleton_stats,
    
    # INITIALIZATION Interface
    initialize_system,
    get_initialization_status,
    set_initialization_flag,
    get_initialization_flag,
    
    # HTTP_CLIENT Interface
    http_request,
    http_get,
    http_post,
    http_put,
    http_delete,
    get_http_client_state,
    reset_http_client_state,
    
    # WEBSOCKET Interface
    websocket_connect,
    websocket_send,
    websocket_receive,
    websocket_close,
    websocket_request,
    
    # CIRCUIT_BREAKER Interface
    get_circuit_breaker,
    execute_with_circuit_breaker,
    get_all_circuit_breaker_states,
    reset_all_circuit_breakers,
    
    # UTILITY Interface
    format_response,
    parse_json,
    safe_get,
    generate_uuid,
    get_timestamp,
    
    # DEBUG Interface
    check_component_health,
    check_gateway_health,
    diagnose_system_health,
    run_debug_tests,
    validate_system_architecture,
)

# Re-export everything
__all__ = [
    # Core
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    
    # Fast Path Management
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    
    # Response Helpers
    'create_error_response',
    'create_success_response',
    
    # Configuration Helpers
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    
    # Circuit Breaker Helpers
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    
    # CACHE Interface
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # LOGGING Interface
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # SECURITY Interface
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
    
    # METRICS Interface
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    
    # CONFIG Interface
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # SINGLETON Interface
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    
    # INITIALIZATION Interface
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # HTTP_CLIENT Interface
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_http_client_state',
    'reset_http_client_state',
    
    # WEBSOCKET Interface
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # CIRCUIT_BREAKER Interface
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # UTILITY Interface
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    
    # DEBUG Interface
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
]

# EOF
