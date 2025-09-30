"""
__init__.py - Revolutionary Gateway Architecture Module Initialization
Version: 2025.09.30.01
Daily Revision: 001

Revolutionary Gateway Optimization - Complete Migration
All imports now route through gateway.py (SUGA + LIGS + ZAFP)
Single Universal Gateway Architecture with Lazy Loading and Fast Path

ARCHITECTURE: Module initialization exports
- Imports from gateway.py only (universal gateway)
- Backward compatible function exports
- Zero breaking changes for existing code
- 100% Free Tier AWS compliant

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

from gateway import (
    cache_get,
    cache_set,
    cache_delete,
    cache_clear,
    log_info,
    log_error,
    log_warning,
    log_debug,
    validate_request,
    validate_token,
    encrypt_data,
    decrypt_data,
    record_metric,
    increment_counter,
    make_request,
    make_get_request,
    make_post_request,
    create_success_response,
    create_error_response,
    parse_json_safely,
    generate_correlation_id,
    execute_initialization_operation,
    record_initialization_stage,
    get_singleton,
    register_singleton,
    execute_operation,
    GatewayInterface,
    get_gateway_stats,
    get_fast_path_stats,
    enable_fast_path,
    disable_fast_path,
    reset_fast_path_stats
)

__all__ = [
    'cache_get',
    'cache_set',
    'cache_delete',
    'cache_clear',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'record_metric',
    'increment_counter',
    'make_request',
    'make_get_request',
    'make_post_request',
    'create_success_response',
    'create_error_response',
    'parse_json_safely',
    'generate_correlation_id',
    'execute_initialization_operation',
    'record_initialization_stage',
    'get_singleton',
    'register_singleton',
    'execute_operation',
    'GatewayInterface',
    'get_gateway_stats',
    'get_fast_path_stats',
    'enable_fast_path',
    'disable_fast_path',
    'reset_fast_path_stats'
]

# EOF
