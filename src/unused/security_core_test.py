"""
security_core.py
Version: 2025.10.15.02
Description: Security validation with dispatcher timing integration (Phase 4 Task #7)

PHASE 4 TASK #7 - Ultra-Integration:
- Added _record_dispatcher_metric() to use centralized METRICS operation
- Now uses gateway.execute_operation(METRICS, 'record_dispatcher_timing')
- Aligns with cache_core and logging_core pattern

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
        """Validate request structure."""
        self._stats['validations'] += 1
        try:
            if not request or not isinstance(request, dict):
                self._stats['failed_validations'] += 1
                return False
            
            if 'version' in request and 'session' in request:
                self._stats['successful_validations'] += 1
                return True
            
            if 'directive' in request and 'header' in request['directive']:
                self._stats['successful_validations'] += 1
                return True
            
            self._stats['failed_validations'] += 1
            return False
        except Exception:
            self._stats['failed_validations'] += 1
            return False
    
    def validate_token(self, token: str) -> bool:
        """Validate token format."""
        self._stats['validations'] += 1
        if not token or not isinstance(token, str):
            self._stats['failed_validations'] += 1
            return False
        
        if re.match(ValidationPattern.TOKEN.value, token):
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string constraints."""
        self._stats['validations'] += 1
        if not isinstance(value, str):
            self._stats['failed_validations'] += 1
            return False
        
        if min_length <= len(value) <= max_length:
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        self._stats['validations'] += 1
        if not email or not isinstance(email, str):
            self._stats['failed_validations'] += 1
            return False
        
        if re.match(ValidationPattern.EMAIL.value, email):
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._stats['validations'] += 1
        if not url or not isinstance(url, str):
            self._stats['failed_validations'] += 1
            return False
        
        if re.match(ValidationPattern.URL.value, url):
            self._stats['successful_validations'] += 1
            return True
        
        self._stats['failed_validations'] += 1
        return False
    
    def encrypt_data(self, data: str, key: str) -> str:
        """Encrypt data using simple XOR (demo only)."""
        self._stats['encryptions'] += 1
        try:
            encrypted = bytearray()
            for i, char in enumerate(data.encode()):
                encrypted.append(char ^ ord(key[i % len(key)]))
            return base64.b64encode(bytes(encrypted)).decode()
        except Exception:
            return ""
    
    def decrypt_data(self, encrypted_data: str, key: str) -> str:
        """Decrypt data using simple XOR (demo only)."""
        self._stats['decryptions'] += 1
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ ord(key[i % len(key)]))
            return decrypted.decode()
        except Exception:
            return ""
    
    def hash_data(self, data: str) -> str:
        """Hash data using SHA-256."""
        self._stats['hashes'] += 1
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify data against hash."""
        computed_hash = self.hash_data(data)
        return hmac.compare_digest(computed_hash, hash_value)
    
    def sanitize_input(self, data: Any) -> str:
        """Sanitize input data."""
        if data is None:
            return ""
        
        text = str(data)
        text = re.sub(r'[<>"\']', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:1000]
    
    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID."""
        self._stats['correlation_ids_generated'] += 1
        return str(uuid.uuid4())


_MANAGER = SecurityCore()


def _record_dispatcher_metric(operation: SecurityOperation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation (Phase 4 Task #7)."""
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


# ===== IMPLEMENTATION WRAPPERS =====

def _execute_validate_request_implementation(request: Dict[str, Any], **kwargs) -> bool:
    """Execute validate request operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_REQUEST, request)


def _execute_validate_token_implementation(token: str, **kwargs) -> bool:
    """Execute validate token operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_TOKEN, token)


def _execute_validate_string_implementation(value: str, min_length: int = 0, max_length: int = 1000, **kwargs) -> bool:
    """Execute validate string operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_STRING, value, min_length, max_length)


def _execute_validate_email_implementation(email: str, **kwargs) -> bool:
    """Execute validate email operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_EMAIL, email)


def _execute_validate_url_implementation(url: str, **kwargs) -> bool:
    """Execute validate URL operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_URL, url)


def _execute_encrypt_data_implementation(data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute encrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.ENCRYPT, data, key or _MANAGER._default_key)


def _execute_decrypt_data_implementation(encrypted_data: str, key: Optional[str] = None, **kwargs) -> str:
    """Execute decrypt data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.DECRYPT, encrypted_data, key or _MANAGER._default_key)


def _execute_hash_data_implementation(data: str, **kwargs) -> str:
    """Execute hash data operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.HASH, data)


def _execute_verify_hash_implementation(data: str, hash_value: str, **kwargs) -> bool:
    """Execute verify hash operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.VERIFY_HASH, data, hash_value)


def _execute_sanitize_input_implementation(data: Any, **kwargs) -> str:
    """Execute sanitize input operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.SANITIZE, data)


def _execute_generate_correlation_id_implementation(**kwargs) -> str:
    """Execute generate correlation ID operation."""
    return _MANAGER.execute_security_operation(SecurityOperation.GENERATE_CORRELATION_ID)


# ===== EXPORTS =====

__all__ = [
    'SecurityOperation',
    'ValidationPattern',
    '_execute_validate_request_implementation',
    '_execute_validate_token_implementation',
    '_execute_validate_string_implementation',
    '_execute_validate_email_implementation',
    '_execute_validate_url_implementation',
    '_execute_encrypt_data_implementation',
    '_execute_decrypt_data_implementation',
    '_execute_hash_data_implementation',
    '_execute_verify_hash_implementation',
    '_execute_sanitize_input_implementation',
    '_execute_generate_correlation_id_implementation',
]

# EOF
