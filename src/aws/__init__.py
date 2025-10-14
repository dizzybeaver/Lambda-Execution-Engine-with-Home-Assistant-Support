"""
aws/__init__.py - AWS Package Exports
Version: 2025.10.14.04
Description: Exports for AWS services package (logging, metrics, usage analytics)

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

# Logging subsystem exports
from logging_core import (
    LogOperation,
    LogTemplate,
    ErrorLogLevel,
    ErrorEntry,
    ErrorLogEntry,
    execute_logging_operation,
    log_template_fast,
    get_logging_stats,
    _execute_log_info_implementation,
    _execute_log_error_implementation,
    _execute_log_warning_implementation,
    _execute_log_debug_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_operation_failure_implementation,
    _log_error_response_internal,
    _get_error_response_analytics_internal,
    _clear_error_response_logs_internal,
)

# Metrics subsystem exports - UPDATED FOR SPLIT
from metrics_types import (
    MetricOperation,
    MetricType,
    ResponseType,
    ResponseMetrics,
    HTTPClientMetrics,
    CircuitBreakerMetrics,
)

from metrics_helper import (
    calculate_percentile,
    build_metric_key,
)

from metrics_core import (
    MetricsCore,
    _MANAGER as _metrics_manager,
)

from metrics_operations import (
    execute_metrics_operation,
    get_metrics_summary,
    _execute_record_metric_implementation,
    _execute_increment_counter_implementation,
    _execute_get_stats_implementation,
    _execute_record_operation_metric_implementation,
    _execute_record_error_response_metric_implementation,
    _execute_record_cache_metric_implementation,
    _execute_record_api_metric_implementation,
    _execute_record_response_metric_implementation,
    _execute_record_http_metric_implementation,
    _execute_record_circuit_breaker_metric_implementation,
    _execute_get_response_metrics_implementation,
    _execute_get_http_metrics_implementation,
    _execute_get_circuit_breaker_metrics_implementation,
    _execute_record_dispatcher_timing_implementation,
    _execute_get_dispatcher_stats_implementation,
    _execute_get_operation_metrics_implementation,
)

# Usage analytics exports (from existing usage_analytics.py)
from usage_analytics import (
    execute_usage_operation,
    get_usage_summary,
)

__all__ = [
    # Logging types
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
    
    # Logging operations
    'execute_logging_operation',
    'log_template_fast',
    'get_logging_stats',
    
    # Logging gateway compatibility
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
    
    # Logging error response tracking
    '_log_error_response_internal',
    '_get_error_response_analytics_internal',
    '_clear_error_response_logs_internal',
    
    # Metrics types
    'MetricOperation',
    'MetricType',
    'ResponseType',
    'ResponseMetrics',
    'HTTPClientMetrics',
    'CircuitBreakerMetrics',
    
    # Metrics helpers
    'calculate_percentile',
    'build_metric_key',
    
    # Metrics core
    'MetricsCore',
    '_metrics_manager',
    
    # Metrics operations
    'execute_metrics_operation',
    'get_metrics_summary',
    '_execute_record_metric_implementation',
    '_execute_increment_counter_implementation',
    '_execute_get_stats_implementation',
    '_execute_record_operation_metric_implementation',
    '_execute_record_error_response_metric_implementation',
    '_execute_record_cache_metric_implementation',
    '_execute_record_api_metric_implementation',
    '_execute_record_response_metric_implementation',
    '_execute_record_http_metric_implementation',
    '_execute_record_circuit_breaker_metric_implementation',
    '_execute_get_response_metrics_implementation',
    '_execute_get_http_metrics_implementation',
    '_execute_get_circuit_breaker_metrics_implementation',
    '_execute_record_dispatcher_timing_implementation',
    '_execute_get_dispatcher_stats_implementation',
    '_execute_get_operation_metrics_implementation',
    
    # Usage analytics
    'execute_usage_operation',
    'get_usage_summary',
]

# EOF
