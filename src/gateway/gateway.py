"""
gateway.py - Central Gateway Entry Point
Version: 2025-12-08_1
Purpose: Single entry point for all LEE operations
License: Apache 2.0
"""

# FIXED: Import enum from separate file to prevent circular imports
from gateway_enums import GatewayInterface

from gateway_core import (
    execute_operation,
    get_gateway_stats,
    reset_gateway_state,
    create_error_response,
    create_success_response,
)

from gateway_wrappers_cache import *
from gateway_wrappers_logging import *
from gateway_wrappers_security import *
from gateway_wrappers_metrics import *
from gateway_wrappers_config import *
from gateway_wrappers_singleton import *
from gateway_wrappers_initialization import *
from gateway_wrappers_http_client import *
from gateway_wrappers_websocket import *
from gateway_wrappers_circuit_breaker import *
from gateway_wrappers_utility import *

# ADDED: New interface wrappers (2025-12-08_1)
from gateway_wrappers_debug import *
from gateway_wrappers_diagnosis import *
from gateway_wrappers_test import *

__all__ = [
    'GatewayInterface',
    'execute_operation',
    'get_gateway_stats',
    'reset_gateway_state',
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
    'validate_string',
    'validate_integer',
    'validate_dict',
    'validate_list',
    'validate_required_fields',
    'sanitize_input',
    'sanitize_string',
    'sanitize_dict',
    'sanitize_list',
    'encode_data',
    'decode_data',
    'hash_data',
    'compare_hashes',
    'generate_token',
    'verify_token',
    'increment_counter',
    'record_metric',
    'get_metrics_stats',
    'reset_metrics',
    'get_config_value',
    'set_config_value',
    'config_exists',
    'get_all_config',
    'singleton_register',
    'singleton_get',
    'singleton_exists',
    'singleton_clear',
    'preload_resources',
    'initialize_system',
    'get_initialization_stats',
    'reset_initialization',
    'make_request',
    'make_get_request',
    'make_post_request',
    'make_put_request',
    'make_delete_request',
    'make_patch_request',
    'http_retry_request',
    'http_get_stats',
    'ws_connect',
    'ws_send',
    'ws_receive',
    'ws_close',
    'ws_get_stats',
    'execute_with_circuit_breaker',
    'get_circuit_breaker_state',
    'reset_circuit_breaker',
    'get_all_circuit_breaker_stats',
    'get_circuit_breaker_stats',
    'set_circuit_breaker_threshold',
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'utility_get_stats',
    'utility_reset',
    'render_template',
    'config_get',
    'debug_trace',
    'debug_dump_state',
    'debug_clear_traces',
    'debug_get_traces',
    'debug_get_stats',
    'debug_enable',
    'debug_disable',
    'debug_is_enabled',
    'debug_log_memory',
    'debug_log_timing',
    'debug_log_cache_state',
    'debug_log_metrics',
    'debug_full_diagnostic',
    'debug_reset',
    # ADDED: Debug interface (2025-12-08_1)
    'debug_log',
    'debug_timing',
    'generate_correlation_id',
    'set_trace_context',
    # ADDED: Diagnosis interface (2025-12-08_1)
    'check_component_health',
    'check_system_health',
    'diagnose_system_health',
    'diagnose_memory_usage',
    'diagnose_component_performance',
    'test_module_import',
    'test_import_sequence',
    'run_diagnostic_suite',
    'get_system_info',
    # ADDED: Test interface (2025-12-08_1)
    'test_lambda_mode',
    'test_component_operation',
    'run_test_suite',
    'test_component_performance',
    'benchmark_operation',
    'test_error_scenario',
]
