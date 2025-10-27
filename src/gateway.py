"""
gateway.py - Universal Lambda Gateway (Consolidated Module)
Version: 2025.10.26.01
Description: Single entry point consolidating gateway_core and gateway_wrappers

CHANGELOG:
- 2025.10.26.01: PHASE 5 EXTRACTION - Added performance reporting export
  - ADDED: get_performance_report to METRICS wrappers imports and exports
  - Makes performance reporting available system-wide via gateway module
- 2025.10.22.04: CLEANUP - Removed legacy HTTP_CLIENT function names
  - Removed: get_http_client_state (use http_get_state)
  - Removed: reset_http_client_state (use http_reset_state)
  - Standardized on new naming convention
- 2025.10.22.03: CRITICAL FIX - Updated HTTP_CLIENT wrapper imports for refactoring
- 2025.10.21.03: SECURITY FIX - Added sanitize_for_log to imports and exports

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Import all from gateway_core
from gateway_core import (
    GatewayInterface,
    execute_operation,
    initialize_lambda,
    get_gateway_stats,
    _OPERATION_REGISTRY,
    set_fast_path_threshold,
    enable_fast_path,
    disable_fast_path,
    clear_fast_path_cache,
    get_fast_path_stats,
    create_error_response,
    create_success_response,
)

# Import all from gateway_wrappers
from gateway_wrappers import (
    # Configuration Helpers
    initialize_config,
    get_cache_config,
    get_metrics_config,
    
    # Circuit Breaker Helpers
    is_circuit_breaker_open,
    get_circuit_breaker_state,
    
    # CACHE wrappers
    cache_get,
    cache_set,
    cache_exists,
    cache_delete,
    cache_clear,
    cache_stats,
    
    # LOGGING wrappers
    log_info,
    log_error,
    log_warning,
    log_debug,
    log_operation_start,
    log_operation_success,
    log_operation_failure,
    
    # SECURITY wrappers
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
    sanitize_for_log,
    validate_cache_key,
    validate_ttl,
    validate_module_name,
    validate_number_range,
    
    # METRICS wrappers
    record_metric,
    increment_counter,
    get_metrics_stats,
    record_operation_metric,
    record_error_metric,
    record_cache_metric,
    record_api_metric,
    get_performance_report,  # ADDED Phase 5
    
    # CONFIG wrappers
    get_config,
    set_config,
    get_config_category,
    reload_config,
    switch_config_preset,
    get_config_state,
    load_config_from_environment,
    load_config_from_file,
    validate_all_config,
    
    # SINGLETON wrappers
    singleton_get,
    singleton_has,
    singleton_delete,
    singleton_clear,
    singleton_stats,
    get_memory_stats,
    get_comprehensive_memory_stats,
    check_lambda_memory_compliance,
    force_memory_cleanup,
    optimize_memory,
    force_comprehensive_memory_cleanup,
    emergency_memory_preserve,
    
    # INITIALIZATION wrappers
    initialize_system,
    get_initialization_status,
    set_initialization_flag,
    get_initialization_flag,
    
    # HTTP_CLIENT wrappers
    http_request,
    http_get,
    http_post,
    http_put,
    http_delete,
    http_reset,
    http_get_state,
    http_reset_state,
    
    # WEBSOCKET wrappers
    websocket_connect,
    websocket_send,
    websocket_receive,
    websocket_close,
    websocket_request,
    
    # CIRCUIT_BREAKER wrappers
    get_circuit_breaker,
    execute_with_circuit_breaker,
    get_all_circuit_breaker_states,
    reset_all_circuit_breakers,
    
    # UTILITY wrappers
    format_response,
    parse_json,
    safe_get,
    generate_uuid,
    get_timestamp,
    
    # DEBUG wrappers
    check_component_health,
    check_gateway_health,
    diagnose_system_health,
    run_debug_tests,
    validate_system_architecture,
)

# ===== MASTER EXPORTS =====

__all__ = [
    # Core (from gateway_core)
    'GatewayInterface',
    'execute_operation',
    'initialize_lambda',
    'get_gateway_stats',
    
    # Fast Path Management (from gateway_core)
    'set_fast_path_threshold',
    'enable_fast_path',
    'disable_fast_path',
    'clear_fast_path_cache',
    'get_fast_path_stats',
    
    # Response Helpers (from gateway_core)
    'create_error_response',
    'create_success_response',
    
    # Configuration Helpers (from gateway_wrappers)
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    
    # Circuit Breaker Helpers (from gateway_wrappers)
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    
    # Generated Wrappers - CACHE (from gateway_wrappers)
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # Generated Wrappers - LOGGING (from gateway_wrappers)
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # Generated Wrappers - SECURITY (from gateway_wrappers)
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
    'sanitize_for_log',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
    
    # Generated Wrappers - METRICS (from gateway_wrappers) ← UPDATED Phase 5
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'get_performance_report',  # ADDED Phase 5
    
    # Generated Wrappers - CONFIG (from gateway_wrappers)
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # Generated Wrappers - SINGLETON (from gateway_wrappers)
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
    
    # Generated Wrappers - INITIALIZATION (from gateway_wrappers)
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # Generated Wrappers - HTTP_CLIENT (CLEANED UP 2025.10.22.04)
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'http_reset',
    'http_get_state',
    'http_reset_state',
    
    # Generated Wrappers - WEBSOCKET (from gateway_wrappers)
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # Generated Wrappers - CIRCUIT_BREAKER (from gateway_wrappers)
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # Generated Wrappers - UTILITY (from gateway_wrappers)
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    
    # Generated Wrappers - DEBUG (from gateway_wrappers)
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
]

# EOF
