"""
interface_security.py - Security Interface Router (SUGA-ISP Architecture)
Version: 2025.10.16.02
Description: Firewall router for Security interface

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

FIXES APPLIED:
- Replaced incorrect SecurityCrypto class with proper router function
- Added execute_security_operation() router function
- Imported all security_core.py implementation functions
- Added routing for all 12 security operations
- Added sanitize_data alias support
- Added comprehensive error handling

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

# ✅ ALLOWED: Import internal files within same Security interface
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


# Valid security operations for error reporting
_VALID_SECURITY_OPERATIONS = [
    'validate_request', 'validate_token', 'encrypt', 'decrypt',
    'hash', 'verify_hash', 'sanitize', 'sanitize_data',
    'generate_correlation_id', 'validate_string', 'validate_email',
    'validate_url', 'get_stats'
]


def execute_security_operation(operation: str, **kwargs) -> Any:
    """
    Route security operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The security operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
        
    Valid operations:
        - validate_request: Validate HTTP request structure
        - validate_token: Validate authentication token
        - encrypt: Encrypt data
        - decrypt: Decrypt data
        - hash: Hash data using SHA-256
        - verify_hash: Verify data against hash
        - sanitize/sanitize_data: Sanitize input data
        - generate_correlation_id: Generate unique correlation ID
        - validate_string: Validate string constraints
        - validate_email: Validate email format
        - validate_url: Validate URL format
        - get_stats: Get security statistics
    """
    
    if operation == 'validate_request':
        return _execute_validate_request_implementation(**kwargs)
    
    elif operation == 'validate_token':
        return _execute_validate_token_implementation(**kwargs)
    
    elif operation == 'encrypt':
        return _execute_encrypt_implementation(**kwargs)
    
    elif operation == 'decrypt':
        return _execute_decrypt_implementation(**kwargs)
    
    elif operation == 'hash':
        return _execute_hash_implementation(**kwargs)
    
    elif operation == 'verify_hash':
        return _execute_verify_hash_implementation(**kwargs)
    
    elif operation == 'sanitize' or operation == 'sanitize_data':
        return _execute_sanitize_implementation(**kwargs)
    
    elif operation == 'generate_correlation_id':
        return _execute_generate_correlation_id_implementation(**kwargs)
    
    elif operation == 'validate_string':
        return _execute_validate_string_implementation(**kwargs)
    
    elif operation == 'validate_email':
        return _execute_validate_email_implementation(**kwargs)
    
    elif operation == 'validate_url':
        return _execute_validate_url_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return get_security_stats()
    
    else:
        raise ValueError(
            f"Unknown security operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_SECURITY_OPERATIONS)}"
        )


__all__ = [
    'execute_security_operation'
]

# EOF
