"""
interface_metrics.py - Metrics Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for Metrics interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for metrics_operations imports
  - Sets _METRICS_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Metrics unavailable
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
- 2025.10.15.01: Initial SUGA-ISP router implementation

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

# Import protection
try:
    from metrics_operations import (
        _execute_record_metric_implementation,
        _execute_increment_counter_implementation,
        _execute_get_metrics_implementation,
        _execute_reset_metrics_implementation
    )
    _METRICS_AVAILABLE = True
    _METRICS_IMPORT_ERROR = None
except ImportError as e:
    _METRICS_AVAILABLE = False
    _METRICS_IMPORT_ERROR = str(e)
    _execute_record_metric_implementation = None
    _execute_increment_counter_implementation = None
    _execute_get_metrics_implementation = None
    _execute_reset_metrics_implementation = None


_VALID_METRICS_OPERATIONS = [
    'record_metric', 'increment_counter', 'get_metrics', 'reset_metrics'
]


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Route metrics operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: Metrics operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Metrics interface unavailable
        ValueError: If operation is unknown or required parameters missing
    """
    # Check Metrics availability
    if not _METRICS_AVAILABLE:
        raise RuntimeError(
            f"Metrics interface unavailable: {_METRICS_IMPORT_ERROR}. "
            "This may indicate missing metrics_operations module or circular import."
        )
    
    if operation not in _VALID_METRICS_OPERATIONS:
        raise ValueError(
            f"Unknown metrics operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_METRICS_OPERATIONS)}"
        )
    
    if operation == 'record_metric':
        if 'name' not in kwargs:
            raise ValueError("metrics.record_metric requires 'name' parameter")
        if 'value' not in kwargs:
            raise ValueError("metrics.record_metric requires 'value' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"metrics.record_metric 'name' must be str, got {type(kwargs['name']).__name__}")
        return _execute_record_metric_implementation(**kwargs)
    
    elif operation == 'increment_counter':
        if 'name' not in kwargs:
            raise ValueError("metrics.increment_counter requires 'name' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"metrics.increment_counter 'name' must be str, got {type(kwargs['name']).__name__}")
        return _execute_increment_counter_implementation(**kwargs)
    
    elif operation == 'get_metrics':
        return _execute_get_metrics_implementation(**kwargs)
    
    elif operation == 'reset_metrics':
        return _execute_reset_metrics_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled metrics operation: '{operation}'")


__all__ = ['execute_metrics_operation']

# EOF
