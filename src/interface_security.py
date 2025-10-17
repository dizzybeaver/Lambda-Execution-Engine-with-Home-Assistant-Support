"""
interface_security.py - Security Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.05
Description: Firewall router for Security interface with parameter validation

CHANGELOG:
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
        operation: The security operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    
    if operation == 'validate_request':
        _validate_request_param(kwargs, operation)
        return _execute_validate_request_implementation(**kwargs)
    
    elif operation == 'validate_token':
        _validate_token_param(kwargs, operation)
        return _execute_validate_token_implementation(**kwargs)
    
    elif operation == 'encrypt':
        _validate_data_param(kwargs, operation)
        return _execute_encrypt_implementation(**kwargs)
    
    elif operation == 'decrypt':
        _validate_data_param(kwargs, operation)
        return _execute_decrypt_implementation(**kwargs)
    
    elif operation == 'hash':
        _validate_data_param(kwargs, operation)
        return _execute_hash_implementation(**kwargs)
    
    elif operation == 'verify_hash':
        _validate_verify_hash_params(kwargs, operation)
        return _execute_verify_hash_implementation(**kwargs)
    
    elif operation == 'sanitize' or operation == 'sanitize_data':
        _validate_data_param(kwargs, operation)
        return _execute_sanitize_implementation(**kwargs)
    
    elif operation == 'generate_correlation_id':
        return _execute_generate_correlation_id_implementation(**kwargs)
    
    elif operation == 'validate_string':
        _validate_value_param(kwargs, operation)
        return _execute_validate_string_implementation(**kwargs)
    
    elif operation == 'validate_email':
        _validate_email_param(kwargs, operation)
        return _execute_validate_email_implementation(**kwargs)
    
    elif operation == 'validate_url':
        _validate_url_param(kwargs, operation)
        return _execute_validate_url_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return get_security_stats()
    
    else:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_SECURITY_OPERATIONS)}"
        )


def _validate_data_param(kwargs: dict, operation: str) -> None:
    """Validate data parameter for security operations."""
    if 'data' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'data'")
    
    data = kwargs.get('data')
    if not isinstance(data, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'data' must be string, "
            f"got {type(data).__name__}"
        )


def _validate_request_param(kwargs: dict, operation: str) -> None:
    """Validate request parameter."""
    if 'request' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'request'")
    
    request = kwargs.get('request')
    if not isinstance(request, dict):
        raise ValueError(
            f"Security operation '{operation}' parameter 'request' must be dictionary, "
            f"got {type(request).__name__}"
        )


def _validate_token_param(kwargs: dict, operation: str) -> None:
    """Validate token parameter."""
    if 'token' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'token'")
    
    token = kwargs.get('token')
    if not isinstance(token, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'token' must be string, "
            f"got {type(token).__name__}"
        )


def _validate_verify_hash_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for verify_hash operation."""
    _validate_data_param(kwargs, operation)
    
    if 'hash_value' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'hash_value'")
    
    hash_value = kwargs.get('hash_value')
    if not isinstance(hash_value, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'hash_value' must be string, "
            f"got {type(hash_value).__name__}"
        )


def _validate_value_param(kwargs: dict, operation: str) -> None:
    """Validate value parameter for validation operations."""
    if 'value' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'value'")
    
    value = kwargs.get('value')
    if not isinstance(value, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'value' must be string, "
            f"got {type(value).__name__}"
        )


def _validate_email_param(kwargs: dict, operation: str) -> None:
    """Validate email parameter."""
    if 'email' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'email'")
    
    email = kwargs.get('email')
    if not isinstance(email, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'email' must be string, "
            f"got {type(email).__name__}"
        )


def _validate_url_param(kwargs: dict, operation: str) -> None:
    """Validate url parameter."""
    if 'url' not in kwargs:
        raise ValueError(f"Security operation '{operation}' requires parameter 'url'")
    
    url = kwargs.get('url')
    if not isinstance(url, str):
        raise ValueError(
            f"Security operation '{operation}' parameter 'url' must be string, "
            f"got {type(url).__name__}"
        )


__all__ = [
    'execute_security_operation'
]

# EOF
