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
    validate_request_implementation,
    validate_token_implementation,
    encrypt_data_implementation,
    decrypt_data_implementation,
    generate_correlation_id_implementation,
    validate_string_implementation,
    validate_email_implementation,
    validate_url_implementation,
    hash_data_implementation,
    verify_hash_implementation,
    sanitize_input_implementation
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
        return validate_request_implementation(**kwargs)
    
    elif operation == 'validate_token':
        return validate_token_implementation(**kwargs)
    
    elif operation == 'encrypt_data':
        return encrypt_data_implementation(**kwargs)
    
    elif operation == 'decrypt_data':
        return decrypt_data_implementation(**kwargs)
    
    elif operation == 'generate_correlation_id':
        return generate_correlation_id_implementation(**kwargs)
    
    elif operation == 'validate_string':
        return validate_string_implementation(**kwargs)
    
    elif operation == 'validate_email':
        return validate_email_implementation(**kwargs)
    
    elif operation == 'validate_url':
        return validate_url_implementation(**kwargs)
    
    elif operation == 'hash_data':
        return hash_data_implementation(**kwargs)
    
    elif operation == 'verify_hash':
        return verify_hash_implementation(**kwargs)
    
    elif operation == 'sanitize_input':
        return sanitize_input_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown security operation: {operation}")


__all__ = [
    'execute_security_operation'
]

# EOF
