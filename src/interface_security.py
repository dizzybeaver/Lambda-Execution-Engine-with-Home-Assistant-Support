"""
interface_security.py - Security Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for Security interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for security_core imports
  - Sets _SECURITY_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Security unavailable
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'data' parameter for encrypt/decrypt/hash operations
  - Validates 'value' parameter for validation operations
  - Type checking for all string parameters
  - Clear error messages for missing/invalid parameters
- 2025.10.16.02: Replaced incorrect SecurityCrypto class with proper router function
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

from typing import Any, Dict

# Import protection
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


_VALID_SECURITY_OPERATIONS = [
    'validate_request', 'validate_token', 'encrypt', 'decrypt',
    'hash', 'verify_hash', 'sanitize', 'sanitize_data',
    'generate_correlation_id', 'validate_string', 'validate_email',
    'validate_url', 'get_stats'
]


def execute_security_operation(operation: str, **kwargs) -> Any:
    """
    Route security operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
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
    
    if operation not in _VALID_SECURITY_OPERATIONS:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_SECURITY_OPERATIONS)}"
        )
    
    if operation == 'validate_request':
        if 'request' not in kwargs:
            raise ValueError("security.validate_request requires 'request' parameter")
        return _execute_validate_request_implementation(**kwargs)
    
    elif operation == 'validate_token':
        if 'token' not in kwargs:
            raise ValueError("security.validate_token requires 'token' parameter")
        if not isinstance(kwargs['token'], str):
            raise TypeError(f"security.validate_token 'token' must be str, got {type(kwargs['token']).__name__}")
        return _execute_validate_token_implementation(**kwargs)
    
    elif operation == 'encrypt':
        if 'data' not in kwargs:
            raise ValueError("security.encrypt requires 'data' parameter")
        if not isinstance(kwargs['data'], str):
            raise TypeError(f"security.encrypt 'data' must be str, got {type(kwargs['data']).__name__}")
        return _execute_encrypt_implementation(**kwargs)
    
    elif operation == 'decrypt':
        if 'data' not in kwargs:
            raise ValueError("security.decrypt requires 'data' parameter")
        if not isinstance(kwargs['data'], str):
            raise TypeError(f"security.decrypt 'data' must be str, got {type(kwargs['data']).__name__}")
        return _execute_decrypt_implementation(**kwargs)
    
    elif operation == 'hash':
        if 'data' not in kwargs:
            raise ValueError("security.hash requires 'data' parameter")
        if not isinstance(kwargs['data'], str):
            raise TypeError(f"security.hash 'data' must be str, got {type(kwargs['data']).__name__}")
        return _execute_hash_implementation(**kwargs)
    
    elif operation == 'verify_hash':
        if 'data' not in kwargs:
            raise ValueError("security.verify_hash requires 'data' parameter")
        if 'hash_value' not in kwargs:
            raise ValueError("security.verify_hash requires 'hash_value' parameter")
        if not isinstance(kwargs['data'], str):
            raise TypeError(f"security.verify_hash 'data' must be str, got {type(kwargs['data']).__name__}")
        if not isinstance(kwargs['hash_value'], str):
            raise TypeError(f"security.verify_hash 'hash_value' must be str, got {type(kwargs['hash_value']).__name__}")
        return _execute_verify_hash_implementation(**kwargs)
    
    elif operation in ['sanitize', 'sanitize_data']:
        if 'data' not in kwargs:
            raise ValueError(f"security.{operation} requires 'data' parameter")
        return _execute_sanitize_implementation(**kwargs)
    
    elif operation == 'generate_correlation_id':
        return _execute_generate_correlation_id_implementation(**kwargs)
    
    elif operation == 'validate_string':
        if 'value' not in kwargs:
            raise ValueError("security.validate_string requires 'value' parameter")
        if not isinstance(kwargs['value'], str):
            raise TypeError(f"security.validate_string 'value' must be str, got {type(kwargs['value']).__name__}")
        return _execute_validate_string_implementation(**kwargs)
    
    elif operation == 'validate_email':
        if 'value' not in kwargs:
            raise ValueError("security.validate_email requires 'value' parameter")
        if not isinstance(kwargs['value'], str):
            raise TypeError(f"security.validate_email 'value' must be str, got {type(kwargs['value']).__name__}")
        return _execute_validate_email_implementation(**kwargs)
    
    elif operation == 'validate_url':
        if 'value' not in kwargs:
            raise ValueError("security.validate_url requires 'value' parameter")
        if not isinstance(kwargs['value'], str):
            raise TypeError(f"security.validate_url 'value' must be str, got {type(kwargs['value']).__name__}")
        return _execute_validate_url_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return get_security_stats(**kwargs)
    
    else:
        raise ValueError(f"Unhandled security operation: '{operation}'")


__all__ = ['execute_security_operation']

# EOF
