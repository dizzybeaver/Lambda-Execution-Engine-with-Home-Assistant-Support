"""
security_core.py - Security Operations with Generic Pattern
Version: 2025.10.10.01
Description: Security validation, encryption, and sanitization with Smart Home support

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

import re
import base64
import hashlib
import hmac
from typing import Dict, Any
from enum import Enum


class SecurityOperation(Enum):
    """Security operations enumeration."""
    VALIDATE_REQUEST = "validate_request"
    VALIDATE_TOKEN = "validate_token"
    VALIDATE_STRING = "validate_string"
    VALIDATE_EMAIL = "validate_email"
    VALIDATE_URL = "validate_url"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    HASH = "hash"
    VERIFY_HASH = "verify_hash"
    SANITIZE = "sanitize"


class ValidationPattern(Enum):
    """Validation regex patterns."""
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL = r'^https?://[^\s]+$'
    TOKEN = r'^[A-Za-z0-9-_]{20,}$'
    ALPHANUMERIC = r'^[a-zA-Z0-9]+$'
    NUMERIC = r'^\d+$'


class SecurityCore:
    """Core security manager with generic operations."""
    
    def __init__(self):
        self._stats = {
            'validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'encryptions': 0,
            'hashes': 0
        }
    
    def execute_security_operation(self, operation: SecurityOperation, *args, **kwargs) -> Any:
        """Generic security operation executor."""
        if operation == SecurityOperation.VALIDATE_REQUEST:
            request = args[0] if args else kwargs.get('request')
            return self.validate_request(request)
        elif operation == SecurityOperation.VALIDATE_TOKEN:
            token = args[0] if args else kwargs.get('token')
            return self.validate_token(token)
        elif operation == SecurityOperation.VALIDATE_STRING:
            value = args[0] if args else kwargs.get('value')
            min_length = args[1] if len(args) > 1 else kwargs.get('min_length', 0)
            max_length = args[2] if len(args) > 2 else kwargs.get('max_length', 1000)
            return self.validate_string(value, min_length, max_length)
        elif operation == SecurityOperation.VALIDATE_EMAIL:
            email = args[0] if args else kwargs.get('email')
            return self.validate_email(email)
        elif operation == SecurityOperation.VALIDATE_URL:
            url = args[0] if args else kwargs.get('url')
            return self.validate_url(url)
        elif operation == SecurityOperation.ENCRYPT:
            data = args[0] if args else kwargs.get('data')
            key = args[1] if len(args) > 1 else kwargs.get('key')
            return self.encrypt_data(data, key)
        elif operation == SecurityOperation.DECRYPT:
            data = args[0] if args else kwargs.get('data')
            key = args[1] if len(args) > 1 else kwargs.get('key')
            return self.decrypt_data(data, key)
        elif operation == SecurityOperation.HASH:
            data = args[0] if args else kwargs.get('data')
            return self.hash_data(data)
        elif operation == SecurityOperation.VERIFY_HASH:
            data = args[0] if args else kwargs.get('data')
            hash_value = args[1] if len(args) > 1 else kwargs.get('hash_value')
            return self.verify_hash(data, hash_value)
        elif operation == SecurityOperation.SANITIZE:
            data = args[0] if args else kwargs.get('data')
            return self.sanitize_input(data)
        return None
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate request structure - supports both Custom Skill and Smart Home formats."""
        self._stats['validations'] += 1
        
        if not isinstance(request, dict):
            self._stats['failed_validations'] += 1
            return False
        
        # Smart Home format: {directive: {header, payload}}
        if 'directive' in request:
            directive = request['directive']
            if isinstance(directive, dict) and 'header' in directive and 'payload' in directive:
                self._stats['successful_validations'] += 1
                return True
        
        # Custom Skill format: {version, session}
        if 'version' in request and 'session' in request:
            self._stats['successful_validations'] += 1
            return True
        
        # Health check format: {requestType: health_check}
        if 'requestType' in request:
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def validate_token(self, token: str) -> bool:
        """Validate token format."""
        self._stats['validations'] += 1
        
        if not token or not isinstance(token, str):
            self._stats['failed_validations'] += 1
            return False
        
        if len(token) < 20 or len(token) > 500:
            self._stats['failed_validations'] += 1
            return False
        
        pattern = re.compile(ValidationPattern.TOKEN.value)
        is_valid = bool(pattern.match(token))
        
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string with length constraints."""
        self._stats['validations'] += 1
        
        if not isinstance(value, str):
            self._stats['failed_validations'] += 1
            return False
        
        if len(value) < min_length or len(value) > max_length:
            self._stats['failed_validations'] += 1
            return False
        
        self._stats['successful_validations'] += 1
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        self._stats['validations'] += 1
        
        if not email or not isinstance(email, str):
            self._stats['failed_validations'] += 1
            return False
        
        pattern = re.compile(ValidationPattern.EMAIL.value)
        is_valid = bool(pattern.match(email))
        
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._stats['validations'] += 1
        
        if not url or not isinstance(url, str):
            self._stats['failed_validations'] += 1
            return False
        
        pattern = re.compile(ValidationPattern.URL.value)
        is_valid = bool(pattern.match(url))
        
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def encrypt_data(self, data: str, key: str) -> str:
        """Simple encryption using base64."""
        self._stats['encryptions'] += 1
        
        try:
            data_bytes = data.encode('utf-8')
            encoded = base64.b64encode(data_bytes)
            return encoded.decode('utf-8')
        except Exception:
            return ""
    
    def decrypt_data(self, data: str, key: str) -> str:
        """Simple decryption using base64."""
        try:
            data_bytes = data.encode('utf-8')
            decoded = base64.b64decode(data_bytes)
            return decoded.decode('utf-8')
        except Exception:
            return ""
    
    def hash_data(self, data: str) -> str:
        """Hash data using SHA-256."""
        self._stats['hashes'] += 1
        
        try:
            hash_obj = hashlib.sha256(data.encode('utf-8'))
            return hash_obj.hexdigest()
        except Exception:
            return ""
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify data matches hash."""
        computed_hash = self.hash_data(data)
        return hmac.compare_digest(computed_hash, hash_value)
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data."""
        if isinstance(data, str):
            sanitized = data.replace('<', '&lt;').replace('>', '&gt;')
            sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
            return sanitized
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            'total_validations': self._stats['validations'],
            'successful_validations': self._stats['successful_validations'],
            'failed_validations': self._stats['failed_validations'],
            'validation_success_rate': (self._stats['successful_validations'] / self._stats['validations'] * 100) if self._stats['validations'] > 0 else 0,
            'encryptions_performed': self._stats['encryptions'],
            'hashes_computed': self._stats['hashes']
        }


_MANAGER = SecurityCore()


def _execute_validate_request_implementation(request: Dict[str, Any], **kwargs) -> bool:
    """Execute validate request operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_REQUEST, request)


def _execute_validate_token_implementation(token: str, **kwargs) -> bool:
    """Execute validate token operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_TOKEN, token)


def _execute_encrypt_data_implementation(data: str, key: str, **kwargs) -> str:
    """Execute encrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.ENCRYPT, data, key)


def _execute_decrypt_data_implementation(data: str, key: str, **kwargs) -> str:
    """Execute decrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.DECRYPT, data, key)


def validate_string_input(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """Public interface for string validation."""
    return _MANAGER.validate_string(value, min_length, max_length)


def get_security_stats() -> Dict[str, Any]:
    """Public interface for security statistics."""
    return _MANAGER.get_stats()


__all__ = [
    'SecurityOperation',
    'ValidationPattern',
    'validate_string_input',
    'get_security_stats',
    '_execute_validate_request_implementation',
    '_execute_validate_token_implementation',
    '_execute_encrypt_data_implementation',
    '_execute_decrypt_data_implementation',
]

# EOF
