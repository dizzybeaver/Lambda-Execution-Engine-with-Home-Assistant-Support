"""
security_core.py
Version: 2025.10.14.01
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
import uuid
import time
from typing import Dict, Any, Optional
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
    GENERATE_CORRELATION_ID = "generate_correlation_id"


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
            'decryptions': 0,
            'hashes': 0,
            'correlation_ids_generated': 0
        }
        self._default_key = "lambda-execution-engine-default-key-2025"
    
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
            key = args[1] if len(args) > 1 else kwargs.get('key', self._default_key)
            return self.encrypt_data(data, key)
        elif operation == SecurityOperation.DECRYPT:
            data = args[0] if args else kwargs.get('data')
            key = args[1] if len(args) > 1 else kwargs.get('key', self._default_key)
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
        elif operation == SecurityOperation.GENERATE_CORRELATION_ID:
            return self.generate_correlation_id()
        return None
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate request structure - supports both Custom Skill and Smart Home formats."""
        self._stats['validations'] += 1
        
        if not isinstance(request, dict):
            self._stats['failed_validations'] += 1
            return False
        
        # Check for Smart Home directive format
        if 'directive' in request:
            directive = request['directive']
            if not all(key in directive for key in ['header', 'endpoint', 'payload']):
                self._stats['failed_validations'] += 1
                return False
            
            header = directive['header']
            if not all(key in header for key in ['namespace', 'name', 'messageId', 'payloadVersion']):
                self._stats['failed_validations'] += 1
                return False
            
            self._stats['successful_validations'] += 1
            return True
        
        # Check for Custom Skill format
        if 'version' in request and 'session' in request and 'request' in request:
            req_data = request['request']
            if 'type' not in req_data or 'requestId' not in req_data:
                self._stats['failed_validations'] += 1
                return False
            
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def validate_token(self, token: str) -> bool:
        """Validate token format."""
        self._stats['validations'] += 1
        
        if not isinstance(token, str):
            self._stats['failed_validations'] += 1
            return False
        
        is_valid = bool(re.match(ValidationPattern.TOKEN.value, token))
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length and format."""
        self._stats['validations'] += 1
        
        if not isinstance(value, str):
            self._stats['failed_validations'] += 1
            return False
        
        is_valid = min_length <= len(value) <= max_length
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        self._stats['validations'] += 1
        
        if not isinstance(email, str):
            self._stats['failed_validations'] += 1
            return False
        
        is_valid = bool(re.match(ValidationPattern.EMAIL.value, email))
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._stats['validations'] += 1
        
        if not isinstance(url, str):
            self._stats['failed_validations'] += 1
            return False
        
        is_valid = bool(re.match(ValidationPattern.URL.value, url))
        if is_valid:
            self._stats['successful_validations'] += 1
        else:
            self._stats['failed_validations'] += 1
        
        return is_valid
    
    def encrypt_data(self, data: str, key: Optional[str] = None) -> str:
        """Encrypt data using XOR with key (simple encryption for demo)."""
        self._stats['encryptions'] += 1
        
        if key is None:
            key = self._default_key
        
        try:
            data_bytes = data.encode('utf-8')
            key_bytes = key.encode('utf-8')
            
            encrypted = bytearray()
            for i, byte in enumerate(data_bytes):
                encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return base64.b64encode(bytes(encrypted)).decode('utf-8')
        except Exception:
            return data
    
    def decrypt_data(self, encrypted_data: str, key: Optional[str] = None) -> str:
        """Decrypt data using XOR with key."""
        self._stats['decryptions'] += 1
        
        if key is None:
            key = self._default_key
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            key_bytes = key.encode('utf-8')
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return bytes(decrypted).decode('utf-8')
        except Exception:
            return encrypted_data
    
    def hash_data(self, data: str) -> str:
        """Generate SHA-256 hash of data."""
        self._stats['hashes'] += 1
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify data matches hash."""
        computed_hash = self.hash_data(data)
        return hmac.compare_digest(computed_hash, hash_value)
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data to prevent XSS."""
        if isinstance(data, str):
            sanitized = data.replace('<', '&lt;').replace('>', '&gt;')
            sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
            return sanitized
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data
    
    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracking."""
        self._stats['correlation_ids_generated'] += 1
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())
        return f"corr-{timestamp}-{unique_id}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            'total_validations': self._stats['validations'],
            'successful_validations': self._stats['successful_validations'],
            'failed_validations': self._stats['failed_validations'],
            'validation_success_rate': (
                self._stats['successful_validations'] / self._stats['validations'] * 100
            ) if self._stats['validations'] > 0 else 0,
            'encryptions_performed': self._stats['encryptions'],
            'decryptions_performed': self._stats['decryptions'],
            'hashes_computed': self._stats['hashes'],
            'correlation_ids_generated': self._stats['correlation_ids_generated']
        }


# Singleton instance
_MANAGER = SecurityCore()


# Gateway implementation functions
def _execute_validate_request_implementation(request: Dict[str, Any], **kwargs) -> bool:
    """Execute validate request operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_REQUEST, request)


def _execute_validate_token_implementation(token: str, **kwargs) -> bool:
    """Execute validate token operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_TOKEN, token)


def _execute_encrypt_data_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute encrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.ENCRYPT, data, key=key)


def _execute_decrypt_data_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute decrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.DECRYPT, data, key=key)


def _execute_generate_correlation_id_implementation(**kwargs) -> str:
    """Execute generate correlation ID operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.GENERATE_CORRELATION_ID)


def _execute_validate_string_implementation(value: str, min_length: int = 0, max_length: int = 1000, **kwargs) -> bool:
    """Execute validate string operation."""
    return _MANAGER.execute_security_operation(
        SecurityOperation.VALIDATE_STRING, 
        value, 
        min_length=min_length, 
        max_length=max_length
    )


def _execute_validate_email_implementation(email: str, **kwargs) -> bool:
    """Execute validate email operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_EMAIL, email)


def _execute_validate_url_implementation(url: str, **kwargs) -> bool:
    """Execute validate URL operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_URL, url)


def _execute_hash_data_implementation(data: str, **kwargs) -> str:
    """Execute hash data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.HASH, data)


def _execute_verify_hash_implementation(data: str, hash_value: str, **kwargs) -> bool:
    """Execute verify hash operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VERIFY_HASH, data, hash_value=hash_value)


def _execute_sanitize_input_implementation(data: Any, **kwargs) -> Any:
    """Execute sanitize input operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.SANITIZE, data)


# Public interface functions
def validate_string_input(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """Public interface for string validation."""
    return _MANAGER.validate_string(value, min_length, max_length)


def validate_email_input(email: str) -> bool:
    """Public interface for email validation."""
    return _MANAGER.validate_email(email)


def validate_url_input(url: str) -> bool:
    """Public interface for URL validation."""
    return _MANAGER.validate_url(url)


def get_security_stats() -> Dict[str, Any]:
    """Public interface for security statistics."""
    return _MANAGER.get_stats()


__all__ = [
    'SecurityOperation',
    'ValidationPattern',
    'SecurityCore',
    'validate_string_input',
    'validate_email_input',
    'validate_url_input',
    'get_security_stats',
    '_execute_validate_request_implementation',
    '_execute_validate_token_implementation',
    '_execute_encrypt_data_implementation',
    '_execute_decrypt_data_implementation',
    '_execute_generate_correlation_id_implementation',
    '_execute_validate_string_implementation',
    '_execute_validate_email_implementation',
    '_execute_validate_url_implementation',
    '_execute_hash_data_implementation',
    '_execute_verify_hash_implementation',
    '_execute_sanitize_input_implementation',
]

# EOF
