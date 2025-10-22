"""
metrics_helper.py - Metrics utility functions
Version: 2025.10.21.01
Description: Helper functions for metrics operations with security validations

PHASE 1 CHANGES:
✅ Added dimension value validation to build_metric_key()
✅ Prevents dimension value injection attacks (Finding 5.3)
✅ Uses gateway for validation per SIMA pattern (RULE-01)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import List, Dict, Optional


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
    
    SECURITY:
    - Validates all dimension values (Finding 5.3)
    - Prevents path traversal attacks in dimensions
    - Prevents control character injection
    
    Args:
        name: Base metric name
        dimensions: Optional dimensions dictionary
        
    Returns:
        Formatted metric key with dimensions
        
    Raises:
        ValueError: If any dimension value is invalid
    """
    if not dimensions:
        return name
    
    # Validate dimension values (Finding 5.3)
    # Import from gateway per SIMA pattern (RULE-01)
    from gateway import validate_dimension_value
    
    for key, value in dimensions.items():
        validate_dimension_value(str(value))
    
    # Build key with sorted dimensions for consistency
    sorted_dims = sorted(dimensions.items())
    dim_str = ','.join(f"{k}={v}" for k, v in sorted_dims)
    return f"{name}[{dim_str}]"


__all__ = [
    'calculate_percentile',
    'build_metric_key',
]

# EOF
