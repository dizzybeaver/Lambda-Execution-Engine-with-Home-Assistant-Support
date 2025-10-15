"""
security_core.py - Security core orchestrator with dispatcher timing
Version: 2025.10.14.01
Description: Central security manager coordinating validation and crypto operations

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

import time
from typing import Dict, Any, Optional

from security_types import SecurityOperation
from security_validation import SecurityValidator
from security_crypto import SecurityCrypto


class SecurityCore:
    """Core security manager orchestrating validation and crypto operations."""
    
    def __init__(self):
        self._validator = SecurityValidator()
        self._crypto = SecurityCrypto()
    
    def execute_security_operation(self, operation: SecurityOperation, *args, **kwargs) -> Any:
        """Generic security operation executor with dispatcher performance monitoring."""
        start_time = time.time()
        result = self._execute_operation_logic(operation, *args, **kwargs)
        duration_ms = (time.time() - start_time) * 1000
        _record_dispatcher_metric(operation, duration_ms)
        return result
    
    def _execute_operation_logic(self, operation: SecurityOperation, *args, **kwargs) -> Any:
        """Execute the actual operation logic."""
        if operation == SecurityOperation.VALIDATE_REQUEST:
            request = args[0] if args else kwargs.get('request')
            return self._validator.validate_request(request)
        elif operation == SecurityOperation.VALIDATE_TOKEN:
            token = args[0] if args else kwargs.get('token')
            return self._validator.validate_token(token)
        elif operation == SecurityOperation.VALIDATE_STRING:
            value = args[0] if args else kwargs.get('value')
            min_length = args[1] if len(args) > 1 else kwargs.get('min_length', 0)
            max_length = args[2] if len(args) > 2 else kwargs.get('max_length', 1000)
            return self._validator.validate_string(value, min_length, max_length)
        elif operation == SecurityOperation.VALIDATE_EMAIL:
            email = args[0] if args else kwargs.get('email')
            return self._validator.validate_email(email)
        elif operation == SecurityOperation.VALIDATE_URL:
            url = args[0] if args else kwargs.get('url')
            return self._validator.validate_url(url)
        elif operation == SecurityOperation.ENCRYPT:
            data = args[0] if args else kwargs.get('data')
            key = args[1] if len(args) > 1 else kwargs.get('key', self._crypto._default_key)
            return self._crypto.encrypt_data(data, key)
        elif operation == SecurityOperation.DECRYPT:
            data = args[0] if args else kwargs.get('data')
            key = args[1] if len(args) > 1 else kwargs.get('key', self._crypto._default_key)
            return self._crypto.decrypt_data(data, key)
        elif operation == SecurityOperation.HASH:
            data = args[0] if args else kwargs.get('data')
            return self._crypto.hash_data(data)
        elif operation == SecurityOperation.VERIFY_HASH:
            data = args[0] if args else kwargs.get('data')
            hash_value = args[1] if len(args) > 1 else kwargs.get('hash_value')
            return self._crypto.verify_hash(data, hash_value)
        elif operation == SecurityOperation.SANITIZE:
            data = args[0] if args else kwargs.get('data')
            return self._validator.sanitize_input(data)
        elif operation == SecurityOperation.GENERATE_CORRELATION_ID:
            return self._crypto.generate_correlation_id()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined security statistics."""
        validator_stats = self._validator.get_stats()
        crypto_stats = self._crypto.get_stats()
        return {**validator_stats, **crypto_stats}


# ===== MODULE SINGLETON =====

_MANAGER = SecurityCore()


def _record_dispatcher_metric(operation: SecurityOperation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation."""
    try:
        from gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.METRICS,
            'record_dispatcher_timing',
            interface_name='SecurityCore',
            operation_name=operation.value,
            duration_ms=duration_ms
        )
    except Exception:
        pass


# ===== GATEWAY IMPLEMENTATION WRAPPERS =====

def _execute_validate_request_implementation(request: Dict[str, Any], **kwargs) -> bool:
    """Execute validate request operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_REQUEST, request, **kwargs)


def _execute_validate_token_implementation(token: str, **kwargs) -> bool:
    """Execute validate token operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_TOKEN, token, **kwargs)


def _execute_encrypt_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute encrypt operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.ENCRYPT, data, key, **kwargs)


def _execute_decrypt_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute decrypt operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.DECRYPT, data, key, **kwargs)


def _execute_hash_implementation(data: str, **kwargs) -> str:
    """Execute hash operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.HASH, data, **kwargs)


def _execute_verify_hash_implementation(data: str, hash_value: str, **kwargs) -> bool:
    """Execute verify hash operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VERIFY_HASH, data, hash_value, **kwargs)


def _execute_sanitize_implementation(data: Any, **kwargs) -> Any:
    """Execute sanitize operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.SANITIZE, data, **kwargs)


def _execute_generate_correlation_id_implementation(**kwargs) -> str:
    """Execute generate correlation ID operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.GENERATE_CORRELATION_ID, **kwargs)


def _execute_validate_string_implementation(value: str, min_length: int = 0, max_length: int = 1000, **kwargs) -> bool:
    """Execute validate string operation."""
    return _MANAGER.execute_security_operation(
        SecurityOperation.VALIDATE_STRING, 
        value, 
        min_length,
        max_length,
        **kwargs
    )


def _execute_validate_email_implementation(email: str, **kwargs) -> bool:
    """Execute validate email operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_EMAIL, email, **kwargs)


def _execute_validate_url_implementation(url: str, **kwargs) -> bool:
    """Execute validate URL operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_URL, url, **kwargs)


# ===== BACKWARDS COMPATIBILITY ALIASES =====

def _execute_encrypt_data_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Alias for encrypt operation."""
    return _execute_encrypt_implementation(data, key, **kwargs)


def _execute_decrypt_data_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Alias for decrypt operation."""
    return _execute_decrypt_implementation(data, key, **kwargs)


def _execute_hash_data_implementation(data: str, **kwargs) -> str:
    """Alias for hash operation."""
    return _execute_hash_implementation(data, **kwargs)


def _execute_sanitize_input_implementation(data: Any, **kwargs) -> Any:
    """Alias for sanitize operation."""
    return _execute_sanitize_implementation(data, **kwargs)


# ===== PUBLIC INTERFACE FUNCTIONS =====

def validate_string_input(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """Public interface for string validation."""
    return _MANAGER._validator.validate_string(value, min_length, max_length)


def validate_email_input(email: str) -> bool:
    """Public interface for email validation."""
    return _MANAGER._validator.validate_email(email)


def validate_url_input(url: str) -> bool:
    """Public interface for URL validation."""
    return _MANAGER._validator.validate_url(url)


def get_security_stats() -> Dict[str, Any]:
    """Public interface for security statistics."""
    return _MANAGER.get_stats()


# ===== EXPORTS =====

__all__ = [
    'SecurityOperation',
    'SecurityCore',
    '_execute_validate_request_implementation',
    '_execute_validate_token_implementation',
    '_execute_validate_string_implementation',
    '_execute_validate_email_implementation',
    '_execute_validate_url_implementation',
    '_execute_encrypt_implementation',
    '_execute_decrypt_implementation',
    '_execute_hash_implementation',
    '_execute_verify_hash_implementation',
    '_execute_sanitize_implementation',
    '_execute_generate_correlation_id_implementation',
    '_execute_encrypt_data_implementation',
    '_execute_decrypt_data_implementation',
    '_execute_hash_data_implementation',
    '_execute_sanitize_input_implementation',
    'validate_string_input',
    'validate_email_input',
    'validate_url_input',
    'get_security_stats'
]

# EOF
