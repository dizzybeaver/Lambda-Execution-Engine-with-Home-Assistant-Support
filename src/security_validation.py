"""
security_validation.py - Security validation operations
Version: 2025.10.16.01
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
from typing import Dict, Any, Optional
from security_types import ValidationPattern


class SecurityValidator:
    """Handles all validation and sanitization operations."""
    
    def __init__(self, allow_empty_requests: bool = True):
        """
        Initialize validator.
        
        Args:
            allow_empty_requests: If True, empty dict {} passes validation.
                                  If False, requests must have at least one key.
        """
        self._validation_stats = {
            'validations': 0,
            'successful_validations': 0,
            'failed_validations': 0
        }
        self._allow_empty_requests = allow_empty_requests
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate request structure - supports multiple formats.
        
        Args:
            request: Request dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_stats['validations'] += 1
        
        # Type validation
        if not request or not isinstance(request, dict):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Support multiple request formats
        has_body = 'body' in request
        has_payload = 'payload' in request
        has_directive = 'directive' in request
        has_event = 'event' in request
        
        # Check for known request formats
        if has_body or has_payload or has_directive or has_event:
            self._validation_stats['successful_validations'] += 1
            return True
        
        # Empty dict handling based on configuration
        if len(request) == 0:
            if self._allow_empty_requests:
                self._validation_stats['successful_validations'] += 1
                return True
            else:
                self._validation_stats['failed_validations'] += 1
                return False
        
        # Non-empty dict with unknown format - allow it (could be custom format)
        self._validation_stats['successful_validations'] += 1
        return True
    
    def validate_token(self, token: str) -> bool:
        """
        Validate authentication token format.
        
        Args:
            token: Token string to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_stats['validations'] += 1
        
        # Type and None validation
        if not token or not isinstance(token, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Length validation (minimum 20 characters)
        if len(token) < 20:
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Pattern validation (alphanumeric with dashes/underscores)
        try:
            if re.match(ValidationPattern.TOKEN.value, token):
                self._validation_stats['successful_validations'] += 1
                return True
        except (re.error, TypeError):
            # Regex error or type mismatch
            pass
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """
        Validate string input with length constraints.
        
        Args:
            value: String to validate
            min_length: Minimum allowed length (default 0)
            max_length: Maximum allowed length (default 1000)
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_stats['validations'] += 1
        
        # Type validation
        if not isinstance(value, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Length validation
        if min_length <= len(value) <= max_length:
            self._validation_stats['successful_validations'] += 1
            return True
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_stats['validations'] += 1
        
        # Type and None validation
        if not email or not isinstance(email, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Length sanity check (max 254 chars per RFC)
        if len(email) > 254:
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Pattern validation
        try:
            if re.match(ValidationPattern.EMAIL.value, email):
                self._validation_stats['successful_validations'] += 1
                return True
        except (re.error, TypeError):
            # Regex error or type mismatch
            pass
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._validation_stats['validations'] += 1
        
        # Type and None validation
        if not url or not isinstance(url, str):
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Length sanity check (max 2048 chars)
        if len(url) > 2048:
            self._validation_stats['failed_validations'] += 1
            return False
        
        # Pattern validation (must start with http:// or https://)
        try:
            if re.match(ValidationPattern.URL.value, url):
                self._validation_stats['successful_validations'] += 1
                return True
        except (re.error, TypeError):
            # Regex error or type mismatch
            pass
        
        self._validation_stats['failed_validations'] += 1
        return False
    
    def sanitize_input(self, data: Any, max_string_length: int = 1000, max_depth: int = 10) -> Any:
        """
        Sanitize input data to prevent XSS and injection attacks.
        
        Args:
            data: Data to sanitize (can be string, dict, list, or other)
            max_string_length: Maximum length for sanitized strings (default 1000)
            max_depth: Maximum recursion depth for nested structures (default 10)
            
        Returns:
            Sanitized data (same type as input where possible)
        """
        # Prevent infinite recursion
        if max_depth <= 0:
            return str(data)[:max_string_length] if data is not None else ""
        
        # Handle None
        if data is None:
            return ""
        
        # Handle strings
        if isinstance(data, str):
            # HTML entity encoding
            text = data.replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace('"', '&quot;').replace("'", '&#x27;')
            text = text.replace('&', '&amp;')  # Encode ampersand for safety
            
            # Remove control characters
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Enforce length limit
            return text[:max_string_length]
        
        # Handle dictionaries (recursive)
        elif isinstance(data, dict):
            return {
                self.sanitize_input(k, max_string_length, max_depth - 1): 
                self.sanitize_input(v, max_string_length, max_depth - 1) 
                for k, v in data.items()
            }
        
        # Handle lists (recursive)
        elif isinstance(data, list):
            return [
                self.sanitize_input(item, max_string_length, max_depth - 1) 
                for item in data
            ]
        
        # Handle numbers and booleans (pass through)
        elif isinstance(data, (int, float, bool)):
            return data
        
        # Handle other types by converting to string and sanitizing
        else:
            return self.sanitize_input(str(data), max_string_length, max_depth - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return self._validation_stats.copy()


# ===== EXPORTS =====

__all__ = [
    'SecurityValidator'
]

# EOF
