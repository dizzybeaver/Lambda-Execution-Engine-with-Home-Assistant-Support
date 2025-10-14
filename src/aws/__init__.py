"""
aws/__init__.py - AWS Package Exports
Version: 2025.10.14.01
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
from aws.logging_core import (
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

# Metrics subsystem exports (from existing metrics_core.py)
from aws.metrics_core import (
    execute_metrics_operation,
    get_metrics_summary,
)

# Usage analytics exports (from existing usage_analytics.py)
from aws.usage_analytics import (
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
    
    # Metrics operations
    'execute_metrics_operation',
    'get_metrics_summary',
    
    # Usage analytics
    'execute_usage_operation',
    'get_usage_summary',
]

# EOF
