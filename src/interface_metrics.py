"""
interface_metrics.py - Metrics Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Metrics interface

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

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

from typing import Any

# ✅ ALLOWED: Import internal files within same Metrics interface
from metrics_operations import (
    _execute_record_metric_implementation,
    _execute_increment_counter_implementation,
    _execute_get_stats_implementation,
    _execute_record_operation_metric_implementation,
    _execute_record_error_response_metric_implementation,
    _execute_record_cache_metric_implementation,
    _execute_record_api_metric_implementation
)


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Route metrics operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The metrics operation to execute ('record_metric', 'increment_counter', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'record' or operation == 'record_metric':
        return _execute_record_metric_implementation(**kwargs)
    
    elif operation == 'increment' or operation == 'increment_counter':
        return _execute_increment_counter_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return _execute_get_stats_implementation(**kwargs)
    
    elif operation == 'record_operation' or operation == 'record_operation_metric':
        return _execute_record_operation_metric_implementation(**kwargs)
    
    elif operation == 'record_error' or operation == 'record_error_metric':
        return _execute_record_error_response_metric_implementation(**kwargs)
    
    elif operation == 'record_cache' or operation == 'record_cache_metric':
        return _execute_record_cache_metric_implementation(**kwargs)
    
    elif operation == 'record_api' or operation == 'record_api_metric':
        return _execute_record_api_metric_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown metrics operation: {operation}")


__all__ = [
    'execute_metrics_operation'
]

# EOF
