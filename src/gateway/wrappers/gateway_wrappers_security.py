"""
gateway_wrappers_security.py - SECURITY Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for SECURITY interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation


def validate_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate HTTP request."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request=request)


def validate_token(token: str) -> bool:
    """Validate authentication token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)


def encrypt_data(data: str) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)


def decrypt_data(data: str) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', data=data)


def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id', prefix=prefix)


def validate_string(value: str, **kwargs) -> bool:
    """Validate string."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_string', value=value, **kwargs)


def validate_email(email: str) -> bool:
    """Validate email address."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_email', email=email)


def validate_url(url: str) -> bool:
    """Validate URL."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_url', url=url)


def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """Hash data."""
    return execute_operation(GatewayInterface.SECURITY, 'hash', data=data, algorithm=algorithm)


def verify_hash(data: str, hash_value: str, algorithm: str = 'sha256') -> bool:
    """Verify hash."""
    return execute_operation(GatewayInterface.SECURITY, 'verify_hash', data=data, hash_value=hash_value, algorithm=algorithm)


def sanitize_input(data: str) -> str:
    """Sanitize input data."""
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)


def sanitize_for_log(data: Any) -> Any:
    """
    Sanitize data for safe logging - removes PII and sensitive fields.
    
    Related CVE: CVE-LOG-001 (Sensitive Data Exposure in Logs)
    """
    return execute_operation(GatewayInterface.SECURITY, 'sanitize', data=data)


# ===== CACHE SECURITY VALIDATORS (2025.10.20) =====

def validate_cache_key(key: str) -> None:
    """
    Validate cache key format and safety.
    
    Validates cache keys against security rules:
    - Length: 1-255 characters
    - Characters: [a-zA-Z0-9_\\-:.]
    - Rejects: control characters, path traversal, special characters
    
    Args:
        key: Cache key to validate
        
    Raises:
        ValueError: If key is invalid with specific reason
    
    Related CVE: CVE-SUGA-2025-001 (Cache Key Injection)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_cache_key', key=key)


def validate_ttl(ttl: float) -> None:
    """
    Validate TTL (time-to-live) value is within acceptable range.
    
    Validates TTL boundaries:
    - Minimum: 1 second (prevents rapid churn)
    - Maximum: 86400 seconds / 24 hours (prevents resource exhaustion)
    - Rejects: NaN, infinity, negative values
    
    Args:
        ttl: Time-to-live in seconds
        
    Raises:
        ValueError: If TTL is out of bounds with specific reason
    
    Related CVE: CVE-SUGA-2025-002 (TTL Boundary Exploitation)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_ttl', ttl=ttl)


def validate_module_name(module_name: str) -> None:
    """
    Validate module name for LUGS (Lazy Unload with Graceful State) dependency tracking.
    
    Validates module names against security rules:
    - Pattern: Valid Python identifier (letters, digits, underscores)
    - Length: 1-100 characters
    - Rejects: path separators, control characters, special characters
    
    Args:
        module_name: Python module name to validate
        
    Raises:
        ValueError: If module name is invalid with specific reason
    
    Related CVE: CVE-SUGA-2025-004 (LUGS Dependency Poisoning)
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_module_name', module_name=module_name)


def validate_number_range(value: float, min_value: float, max_value: float, name: str = "value") -> None:
    """
    Generic numeric validation with bounds checking.
    
    Validates numeric values are within specified range and not special values:
    - Range: min_value <= value <= max_value
    - Rejects: NaN, infinity (positive or negative)
    
    Args:
        value: Numeric value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)
        name: Name of value for error messages (default: "value")
        
    Raises:
        ValueError: If value is out of range or special value with specific reason
    """
    execute_operation(GatewayInterface.SECURITY, 'validate_number_range', 
                     value=value, min_value=min_value, max_value=max_value, name=name)


__all__ = [
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'generate_correlation_id',
    'validate_string',
    'validate_email',
    'validate_url',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    'sanitize_for_log',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
]
