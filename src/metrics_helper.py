"""
metrics_helper.py - Metrics utility functions
Version: 2025.10.21.05
Description: Added aggregate_stats() to genericize stats building pattern (Phase 2 Task 2.5)

CHANGELOG:
- 2025.10.21.05: PHASE 2 TASK 2.5 - Genericize stats aggregation
  - Added: aggregate_stats() helper function
  - Purpose: Eliminate 20 LOC duplication across 4 stats functions
  - Pattern: Build standard stats with success rate calculation

- 2025.10.21.04: PHASE 2 TASK 2.4 - Genericize validation pattern
  - Added: validate_required_param() helper function
  - Purpose: Eliminate 70 LOC duplication across 7 validation functions
  - Pattern: Generic parameter validation with optional custom checks

- 2025.10.21.03: PHASE 2 TASK 2.3 - Genericize metric recording pattern
  - Added: record_metric_with_duration() helper function
  - Purpose: Eliminate 60 LOC duplication across 8 functions
  - Pattern: Record base metric + optional duration metric

- 2025.10.21.02: PHASE 2 TASK 2.2 - Genericize safe division
  - Added: safe_divide() helper function
  - Purpose: Eliminate 30 LOC duplication across 10+ division operations
  - Pattern: Safe division with zero check, optional multiplier for percentages

- 2025.10.21.01: PHASE 2 TASK 2.1 - Genericize dimension building
  - Added: build_dimensions() helper function
  - Purpose: Eliminate 40 LOC duplication across 6 functions
  - Pattern: Build dimensions with conditional fields (include only if value not None)

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

from typing import List, Dict, Optional, Any, Callable


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile value from a list of values.
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int((percentile / 100) * len(sorted_values))
    return sorted_values[min(index, len(sorted_values) - 1)]


def build_metric_key(name: str, dimensions: Optional[Dict[str, str]] = None) -> str:
    """
    Build metric key with optional dimensions.
    
    Args:
        name: Base metric name
        dimensions: Optional dimensions dictionary
        
    Returns:
        Formatted metric key with dimensions
    """
    if not dimensions:
        return name
    
    sorted_dims = sorted(dimensions.items())
    dim_str = ','.join(f"{k}={v}" for k, v in sorted_dims)
    return f"{name}[{dim_str}]"


def build_dimensions(
    base: Dict[str, str],
    **conditionals
) -> Dict[str, str]:
    """
    Build metric dimensions with conditional fields.
    
    Generic helper that eliminates duplication across 6 metric recording functions.
    Pattern: Start with base dimensions, add conditional fields only if value not None.
    
    Args:
        base: Base dimensions always included
        **conditionals: Additional dimensions to include only if value not None
        
    Returns:
        Complete dimensions dictionary
        
    Example:
        >>> build_dimensions(
        ...     {'operation': 'cache_get'},
        ...     success=True,
        ...     error_type=None  # Not included
        ... )
        {'operation': 'cache_get', 'success': 'True'}
    """
    dimensions = base.copy()
    for key, value in conditionals.items():
        if value is not None:
            dimensions[key] = str(value)
    return dimensions


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
    multiply_by: float = 1.0
) -> float:
    """
    Safe division with default for zero denominator.
    
    Generic helper that eliminates duplication across 10+ division operations.
    Pattern: Check denominator != 0, apply optional multiplier (for percentages).
    
    Args:
        numerator: Value to divide
        denominator: Value to divide by
        default: Return if denominator is 0 (default: 0.0)
        multiply_by: Optional multiplier (e.g., 100.0 for percentages)
        
    Returns:
        Result of (numerator / denominator) * multiply_by, or default if denominator is 0
        
    Examples:
        >>> safe_divide(50, 100)  # Simple division
        0.5
        >>> safe_divide(50, 100, multiply_by=100.0)  # Percentage
        50.0
        >>> safe_divide(50, 0, default=0.0)  # Division by zero
        0.0
    """
    if denominator == 0:
        return default
    return (numerator / denominator) * multiply_by


def record_metric_with_duration(
    name: str,
    dimensions: Dict[str, str],
    duration_ms: Optional[float] = None,
    count: float = 1.0
) -> bool:
    """
    Record metric with optional duration.
    
    Generic helper that eliminates duplication across 8 specialized recording functions.
    Pattern: Always record base metric, conditionally record duration metric.
    
    Args:
        name: Base metric name
        dimensions: Metric dimensions
        duration_ms: Optional duration in milliseconds (records {name}.duration_ms if > 0)
        count: Value for base metric (default: 1.0)
        
    Returns:
        True if metrics recorded successfully
        
    Example:
        >>> record_metric_with_duration(
        ...     'operation.cache_get.count',
        ...     {'operation': 'cache_get', 'success': 'True'},
        ...     duration_ms=15.3,
        ...     count=1.0
        ... )
        True  # Records both count and duration_ms metrics
    """
    from metrics_core import _MANAGER
    
    # Always record base metric
    _MANAGER.record_metric(name, count, dimensions)
    
    # Conditionally record duration metric
    if duration_ms is not None and duration_ms > 0:
        # Replace .count with .duration_ms if present, otherwise append
        duration_name = name.replace('.count', '.duration_ms') if '.count' in name else f'{name}.duration_ms'
        _MANAGER.record_metric(duration_name, duration_ms, dimensions)
    
    return True


def validate_required_param(
    kwargs: Dict[str, Any],
    param_name: str,
    expected_type: Optional[type] = None,
    operation: str = 'operation',
    validator: Optional[Callable[[Any], bool]] = None,
    error_message: Optional[str] = None
) -> Any:
    """
    Generic parameter validation with optional custom checks.
    
    Generic helper that eliminates duplication across 7 validation functions.
    Pattern: Check exists, optionally check type, optionally run custom validator.
    
    Args:
        kwargs: Dictionary to validate parameter from
        param_name: Name of required parameter
        expected_type: Optional type to enforce (e.g., str, int)
        operation: Operation name for error messages
        validator: Optional custom validation function (returns True if valid)
        error_message: Optional custom error message
        
    Returns:
        The validated parameter value
        
    Raises:
        ValueError: If parameter missing, wrong type, or fails custom validation
        
    Examples:
        >>> # Simple existence check
        >>> validate_required_param(kwargs, 'name', str, 'record_metric')
        
        >>> # With custom validator (non-empty string)
        >>> validate_required_param(
        ...     kwargs, 'name', str, 'record_metric',
        ...     validator=lambda v: bool(v.strip())
        ... )
        
        >>> # Multiple parameters
        >>> for param in ['method', 'url', 'status_code']:
        ...     validate_required_param(kwargs, param, operation='record_http')
    """
    # Check parameter exists
    if param_name not in kwargs:
        raise ValueError(
            error_message or 
            f"Metrics operation '{operation}' requires parameter '{param_name}'"
        )
    
    value = kwargs[param_name]
    
    # Check type if specified
    if expected_type and not isinstance(value, expected_type):
        raise ValueError(
            f"Metrics operation '{operation}' parameter '{param_name}' "
            f"must be {expected_type.__name__}, got {type(value).__name__}"
        )
    
    # Run custom validator if specified
    if validator and not validator(value):
        raise ValueError(
            error_message or
            f"Metrics operation '{operation}' parameter '{param_name}' validation failed"
        )
    
    return value


def aggregate_stats(
    total: int,
    success: int,
    failure: int = 0,
    **additional_stats
) -> Dict[str, Any]:
    """
    Build standard stats with success rate calculation.
    
    Generic helper that eliminates duplication across 4 stats-building functions.
    Pattern: Calculate success_rate using safe_divide, include all additional stats.
    
    Args:
        total: Total count (denominator for success_rate)
        success: Success count (numerator for success_rate)
        failure: Failure count (optional, default: 0)
        **additional_stats: Additional stats to include in result
        
    Returns:
        Dictionary with total, success, failure, success_rate, and additional stats
        
    Example:
        >>> aggregate_stats(
        ...     total=100,
        ...     success=95,
        ...     failure=5,
        ...     avg_duration_ms=123.4,
        ...     p95_duration_ms=250.0
        ... )
        {
            'total': 100,
            'success': 95,
            'failure': 5,
            'success_rate': 95.0,
            'avg_duration_ms': 123.4,
            'p95_duration_ms': 250.0
        }
    """
    return {
        'total': total,
        'success': success,
        'failure': failure,
        'success_rate': safe_divide(success, total, multiply_by=100.0),
        **additional_stats
    }


__all__ = [
    'calculate_percentile',
    'build_metric_key',
    'build_dimensions',
    'safe_divide',
    'record_metric_with_duration',
    'validate_required_param',
    'aggregate_stats',
]

# EOF
