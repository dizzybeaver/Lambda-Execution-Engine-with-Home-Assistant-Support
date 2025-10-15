"""
aws/metrics_helper.py - Metrics utility functions
Version: 2025.10.14.04
Description: Helper functions for metrics operations

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


__all__ = [
    'calculate_percentile',
    'build_metric_key',
]

# EOF
