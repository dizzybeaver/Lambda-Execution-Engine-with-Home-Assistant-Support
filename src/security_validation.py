"""
security_validation.py - Security validation operations
Version: 2025.10.14.01
Description: Input validation, sanitization, and request verification

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
from typing import Dict, Any
from security_types import ValidationPattern


class SecurityValidator:
    """Handles all validation and sanitization operations."""
    
    def __init__(self):
        self._validation_stats = {
            'validations': 0,
            'successful_validations': 0,
            'failed_validations': 0
        }
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate request structure - supports multiple formats."""
        self._validation_stats['validations'] += 1
        
        if not request or not isinstance(request, dict):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Support multiple request formats
        has_body = 'body' in request
        has_payload = 'payload' in request
        has_directive = 'directive' in request
        has_event = 'event' in request
        
        if has_body or has_payload or has_directive or has_event:
            self._validation_stats['successful_validations'] += 1
            return True
        
        # Empty dict is technically valid
        if len(request) == 0:
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_token(self, token: str) -> bool:
        """Validate authentication token format."""
        self._validation_stats['validations'] += 1
        
        if not token or not isinstance(token, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Check for minimum length and alphanumeric with dashes/underscores
        if len(token) >= 20 and re.match(ValidationPattern.TOKEN.value, token):
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string input with length constraints."""
        self._validation_stats['validations'] += 1
        
        if not isinstance(value, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        if min_length <= len(value) <= max_length:
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        self._validation_stats['validations'] += 1
        
        if not email or not isinstance(email, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        if re.match(ValidationPattern.EMAIL.value, email):
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        self._validation_stats['validations'] += 1
        
        if not url or not isinstance(url, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        if re.match(ValidationPattern.URL.value, url):
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data to prevent XSS and injection attacks."""
        if data is None:
            return ""
        
        if isinstance(data, str):
            # HTML entity encoding
            text = data.replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace('"', '&quot;').replace("'", '&#x27;')
            # Remove control characters and limit length
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:1000]  # Limit to 1000 chars
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        
        return data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self._validation_stats.copy()


# ===== EXPORTS =====

__all__ = [
    'SecurityValidator'
]

# EOF
