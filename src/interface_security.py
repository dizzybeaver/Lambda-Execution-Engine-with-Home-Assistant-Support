"""
interface_security.py - Security Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.17
Description: Router for Security interface with dispatch dictionary pattern

CHANGELOG:
- 2025.10.17.17: MODERNIZED with dispatch dictionary pattern
  - Converted from elif chain (13 operations) to dispatch dictionary
  - O(1) operation lookup vs O(n) elif chain
  - Reduced code from ~230 lines to ~190 lines
  - Easier to maintain and extend (add operation = 1 line)
  - Follows pattern from interface_utility.py v2025.10.17.16
  - All validation logic preserved in helper functions
  - Supports both 'sanitize' and 'sanitize_data' aliases
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
- 2025.10.17.05: Added parameter validation for all operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# ===== IMPORT PROTECTION =====

try:
    from security_core import (
        _execute_validate_request_implementation,
        _execute_validate_token_implementation,
        _execute_encrypt_implementation,
        _execute_decrypt_implementation,
        _execute_hash_implementation,
        _execute_verify_hash_implementation,
        _execute_sanitize_implementation,
        _execute_generate_correlation_id_implementation,
        _execute_validate_string_implementation,
        _execute_validate_email_implementation,
        _execute_validate_url_implementation,
        get_security_stats
    )
    _SECURITY_AVAILABLE = True
    _SECURITY_IMPORT_ERROR = None
except ImportError as e:
    _SECURITY_AVAILABLE = False
    _SECURITY_IMPORT_ERROR = str(e)
    _execute_validate_request_implementation = None
    _execute_validate_token_implementation = None
    _execute_encrypt_implementation = None
    _execute_decrypt_implementation = None
    _execute_hash_implementation = None
    _execute_verify_hash_implementation = None
    _execute_sanitize_implementation = None
    _execute_generate_correlation_id_implementation = None
    _execute_validate_string_implementation = None
    _execute_validate_email_implementation = None
    _execute_validate_url_implementation = None
    get_security_stats = None


# ===== VALIDATION HELPERS =====

def _validate_request_param(kwargs: Dict[str, Any]) -> None:
    """Validate request parameter exists."""
    if 'request' not in kwargs:
        raise ValueError("security.validate_request requires 'request' parameter")


def _validate_token_param(kwargs: Dict[str, Any]) -> None:
    """Validate token parameter exists and is string."""
    if 'token' not in kwargs:
        raise ValueError("security.validate_token requires 'token' parameter")
    if not isinstance(kwargs['token'], str):
        raise TypeError(
            f"security.validate_token 'token' must be str, got {type(kwargs['token']).__name__}"
        )


def _validate_data_string_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate data parameter exists and is string."""
    if 'data' not in kwargs:
        raise ValueError(f"security.{operation} requires 'data' parameter")
    if not isinstance(kwargs['data'], str):
        raise TypeError(
            f"security.{operation} 'data' must be str, got {type(kwargs['data']).__name__}"
        )


def _validate_hash_params(kwargs: Dict[str, Any]) -> None:
    """Validate verify_hash parameters."""
    if 'data' not in kwargs:
        raise ValueError("security.verify_hash requires 'data' parameter")
    if 'hash_value' not in kwargs:
        raise ValueError("security.verify_hash requires 'hash_value' parameter")
    if not isinstance(kwargs['data'], str):
        raise TypeError(
            f"security.verify_hash 'data' must be str, got {type(kwargs['data']).__name__}"
        )
    if not isinstance(kwargs['hash_value'], str):
        raise TypeError(
            f"security.verify_hash 'hash_value' must be str, got {type(kwargs['hash_value']).__name__}"
        )


def _validate_value_string_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate value parameter exists and is string."""
    if 'value' not in kwargs:
        raise ValueError(f"security.{operation} requires 'value' parameter")
    if not isinstance(kwargs['value'], str):
        raise TypeError(
            f"security.{operation} 'value' must be str, got {type(kwargs['value']).__name__}"
        )


def _validate_sanitize_data_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate data parameter for sanitize operations."""
    if 'data' not in kwargs:
        raise ValueError(f"security.{operation} requires 'data' parameter")


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for security operations. Only called if security available."""
    return {
        'validate_request': lambda **kwargs: (
            _validate_request_param(kwargs),
            _execute_validate_request_implementation(**kwargs)
        )[1],
        
        'validate_token': lambda **kwargs: (
            _validate_token_param(kwargs),
            _execute_validate_token_implementation(**kwargs)
        )[1],
        
        'encrypt': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'encrypt'),
            _execute_encrypt_implementation(**kwargs)
        )[1],
        
        'decrypt': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'decrypt'),
            _execute_decrypt_implementation(**kwargs)
        )[1],
        
        'hash': lambda **kwargs: (
            _validate_data_string_param(kwargs, 'hash'),
            _execute_hash_implementation(**kwargs)
        )[1],
        
        'verify_hash': lambda **kwargs: (
            _validate_hash_params(kwargs),
            _execute_verify_hash_implementation(**kwargs)
        )[1],
        
        # Both 'sanitize' and 'sanitize_data' supported (Issue #35)
        'sanitize': lambda **kwargs: (
            _validate_sanitize_data_param(kwargs, 'sanitize'),
            _execute_sanitize_implementation(**kwargs)
        )[1],
        
        'sanitize_data': lambda **kwargs: (
            _validate_sanitize_data_param(kwargs, 'sanitize_data'),
            _execute_sanitize_implementation(**kwargs)
        )[1],
        
        'generate_correlation_id': _execute_generate_correlation_id_implementation,
        
        'validate_string': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_string'),
            _execute_validate_string_implementation(**kwargs)
        )[1],
        
        'validate_email': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_email'),
            _execute_validate_email_implementation(**kwargs)
        )[1],
        
        'validate_url': lambda **kwargs: (
            _validate_value_string_param(kwargs, 'validate_url'),
            _execute_validate_url_implementation(**kwargs)
        )[1],
        
        'get_stats': get_security_stats,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _SECURITY_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_security_operation(operation: str, **kwargs) -> Any:
    """
    Route security operation requests using dispatch dictionary pattern.
    
    Args:
        operation: Security operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Security interface unavailable
        ValueError: If operation is unknown or required parameters missing
    """
    # Check Security availability
    if not _SECURITY_AVAILABLE:
        raise RuntimeError(
            f"Security interface unavailable: {_SECURITY_IMPORT_ERROR}. "
            "This may indicate missing security_core module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_security_operation']

# EOF
