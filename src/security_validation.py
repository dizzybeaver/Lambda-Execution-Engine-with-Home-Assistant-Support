"""
security_validation.py - ADDITION: Metrics Security Validations
Version: 2025.10.21.01
Description: Add metric name and dimension value validation functions

ADD THESE FUNCTIONS to the existing security_validation.py file.

CHANGELOG:
- 2025.10.21.01: Added metrics security validations
  - validate_metric_name() - Prevent metric name injection (CVE-SUGA-2025-001 pattern)
  - validate_dimension_value() - Prevent dimension value injection
  - validate_metric_value() - Prevent NaN/Infinity/invalid numeric values
  
REF: Finding 5.1 (Metric name validation)
REF: Finding 5.3 (Dimension value validation)
REF: Finding 5.5 (Input type validation)
REF: CVE-SUGA-2025-001 (Cache key injection pattern - similar attack vector)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import re
import math
from typing import Any


# ===== METRICS SECURITY VALIDATIONS =====

def validate_metric_name(name: str) -> None:
    """
    Validate metric name for security and sanity.
    
    Security Rules:
    - Length: 1-200 characters
    - Characters: [a-zA-Z0-9_.-] only
    - No path separators (/, \\)
    - No control characters
    - No leading/trailing whitespace
    - Cannot start/end with . or -
    
    Attack Vectors Prevented:
    - Path traversal: "../../system/password"
    - Control character injection: "\\x00\\x01\\x02"
    - Memory exhaustion: "x" * 10000
    - Code injection via special characters
    
    REF: Finding 5.1 (Unvalidated metric names)
    REF: CVE-SUGA-2025-001 pattern (similar to cache key injection)
    
    Args:
        name: Metric name to validate
        
    Raises:
        ValueError: If name is invalid with specific reason
        
    Example:
        >>> validate_metric_name("operation.cache.hit")  # ✅ Valid
        >>> validate_metric_name("../../etc/passwd")     # ❌ Raises ValueError
        >>> validate_metric_name("x" * 300)              # ❌ Raises ValueError
    """
    # Check empty/whitespace
    if not name or not name.strip():
        raise ValueError("Metric name cannot be empty or whitespace")
    
    # Auto-strip for safety
    name = name.strip()
    
    # Check length
    if len(name) > 200:
        raise ValueError(
            f"Metric name too long: {len(name)} characters (max: 200). "
            f"This may be a memory exhaustion attack."
        )
    
    if len(name) < 1:
        raise ValueError("Metric name must be at least 1 character")
    
    # Check character set - only alphanumeric, underscore, dot, hyphen
    if not re.match(r'^[a-zA-Z0-9_.\-]+$', name):
        raise ValueError(
            f"Metric name contains invalid characters: '{name}'. "
            f"Allowed characters: [a-zA-Z0-9_.-]"
        )
    
    # Check for path separators (security: prevent traversal)
    if '/' in name or '\\' in name:
        raise ValueError(
            f"Metric name cannot contain path separators: '{name}'. "
            f"This may be a path traversal attack."
        )
    
    # Check for leading/trailing special chars (data quality)
    if name.startswith(('.', '-')) or name.endswith(('.', '-')):
        raise ValueError(
            f"Metric name cannot start or end with '.' or '-': '{name}'"
        )
    
    # Passed all checks
    return


def validate_dimension_value(value: str) -> None:
    """
    Validate metric dimension value for security.
    
    Security Rules:
    - Length: 1-100 characters
    - No control characters (\\x00-\\x1F, \\x7F-\\x9F)
    - No path separators (/, \\)
    - Must be printable
    
    Attack Vectors Prevented:
    - Path traversal in dimensions: {'user': '../../etc/passwd'}
    - Control character injection: {'status': '\\x00' * 1000}
    - Memory exhaustion: {'operation': 'x' * 10000}
    
    REF: Finding 5.3 (Dimension value injection)
    
    Args:
        value: Dimension value to validate (will be converted to string)
        
    Raises:
        ValueError: If value is invalid with specific reason
        
    Example:
        >>> validate_dimension_value("success")      # ✅ Valid
        >>> validate_dimension_value("../../passwd") # ❌ Raises ValueError
        >>> validate_dimension_value("\\x00\\x01")   # ❌ Raises ValueError
    """
    # Convert to string if not already
    value = str(value)
    
    # Check empty/whitespace
    if not value or not value.strip():
        raise ValueError("Dimension value cannot be empty or whitespace")
    
    # Auto-strip for safety
    value = value.strip()
    
    # Check length
    if len(value) > 100:
        raise ValueError(
            f"Dimension value too long: {len(value)} characters (max: 100). "
            f"This may be a memory exhaustion attack."
        )
    
    # Check for control characters
    if not value.isprintable():
        raise ValueError(
            f"Dimension value contains non-printable characters. "
            f"This may be a control character injection attack."
        )
    
    # Check for path separators (security: prevent traversal)
    if '/' in value or '\\' in value:
        raise ValueError(
            f"Dimension value cannot contain path separators: '{value}'. "
            f"This may be a path traversal attack."
        )
    
    # Passed all checks
    return


def validate_metric_value(value: float, allow_negative: bool = True) -> None:
    """
    Validate metric numeric value is valid.
    
    Validates that metric values are valid floats:
    - Rejects: NaN (Not a Number)
    - Rejects: Infinity (positive or negative)
    - Optionally rejects: Negative values (for counters, timings)
    
    Attack Vectors Prevented:
    - NaN injection causing calculation errors
    - Infinity causing overflow
    - Negative durations causing confusion
    
    REF: Finding 5.5 (Missing input type validation)
    REF: Bug #13 (Input validation for negative durations)
    
    Args:
        value: Numeric value to validate
        allow_negative: Whether negative values are allowed (default: True)
        
    Raises:
        ValueError: If value is invalid with specific reason
        
    Example:
        >>> validate_metric_value(123.45)           # ✅ Valid
        >>> validate_metric_value(float('nan'))     # ❌ Raises ValueError
        >>> validate_metric_value(float('inf'))     # ❌ Raises ValueError
        >>> validate_metric_value(-5.0, False)      # ❌ Raises ValueError
    """
    # Check for NaN
    if math.isnan(value):
        raise ValueError(
            f"Metric value cannot be NaN (Not a Number). "
            f"This indicates a calculation error or invalid input."
        )
    
    # Check for infinity
    if math.isinf(value):
        raise ValueError(
            f"Metric value cannot be infinity. "
            f"Value: {value}. This may cause overflow or calculation errors."
        )
    
    # Check for negative (if not allowed)
    if not allow_negative and value < 0:
        raise ValueError(
            f"Metric value cannot be negative: {value}. "
            f"This is likely an error (e.g., negative duration)."
        )
    
    # Passed all checks
    return


# ===== USAGE EXAMPLES =====

if __name__ == '__main__':
    # Example: Metric name validation
    try:
        validate_metric_name("operation.cache.hit")
        print("✅ Valid metric name")
    except ValueError as e:
        print(f"❌ Invalid: {e}")
    
    try:
        validate_metric_name("../../etc/passwd")
        print("✅ Valid metric name")
    except ValueError as e:
        print(f"❌ Invalid: {e}")  # Expected
    
    # Example: Dimension value validation
    try:
        validate_dimension_value("success")
        print("✅ Valid dimension value")
    except ValueError as e:
        print(f"❌ Invalid: {e}")
    
    try:
        validate_dimension_value("\x00\x01\x02")
        print("✅ Valid dimension value")
    except ValueError as e:
        print(f"❌ Invalid: {e}")  # Expected
    
    # Example: Metric value validation
    try:
        validate_metric_value(123.45)
        print("✅ Valid metric value")
    except ValueError as e:
        print(f"❌ Invalid: {e}")
    
    try:
        validate_metric_value(float('nan'))
        print("✅ Valid metric value")
    except ValueError as e:
        print(f"❌ Invalid: {e}")  # Expected


# ===== EXPORTS =====

__all__ = [
    'validate_metric_name',
    'validate_dimension_value',
    'validate_metric_value',
]

# EOF - Add these functions to existing security_validation.py
