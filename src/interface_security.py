"""
interface_security.py - Security Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Security interface

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

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

# ✅ ALLOWED: Import internal files within same Security interface
from security_core import (
    _execute_validate_request_implementation,
    _execute_validate_token_implementation,
    _execute_encrypt_data_implementation,
    _execute_decrypt_data_implementation,
    _execute_generate_correlation_id_implementation,
    _execute_validate_string_implementation,
    _execute_validate_email_implementation,
    _execute_validate_url_implementation,
    _execute_hash_data_implementation,
    _execute_verify_hash_implementation,
    _execute_sanitize_input_implementation
)


def execute_security_operation(operation: str, **kwargs) -> Any:
    """
    Route security operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The security operation to execute ('validate_request', 'encrypt_data', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'validate_request':
        return _execute_validate_request_implementation(**kwargs)
    
    elif operation == 'validate_token':
        return _execute_validate_token_implementation(**kwargs)
    
    elif operation == 'encrypt' or operation == 'encrypt_data':
        return _execute_encrypt_data_implementation(**kwargs)
    
    elif operation == 'decrypt' or operation == 'decrypt_data':
        return _execute_decrypt_data_implementation(**kwargs)
    
    elif operation == 'generate_correlation_id':
        return _execute_generate_correlation_id_implementation(**kwargs)
    
    elif operation == 'validate_string':
        return _execute_validate_string_implementation(**kwargs)
    
    elif operation == 'validate_email':
        return _execute_validate_email_implementation(**kwargs)
    
    elif operation == 'validate_url':
        return _execute_validate_url_implementation(**kwargs)
    
    elif operation == 'hash' or operation == 'hash_data':
        return _execute_hash_data_implementation(**kwargs)
    
    elif operation == 'verify_hash':
        return _execute_verify_hash_implementation(**kwargs)
    
    elif operation == 'sanitize' or operation == 'sanitize_input':
        return _execute_sanitize_input_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown security operation: {operation}")


__all__ = [
    'execute_security_operation'
]

# EOF
