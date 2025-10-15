"""
http_client_validation.py - HTTP Response Validation
Version: 2025.10.14.01
Description: Response validation classes and functions for HTTP client.
             Internal module - accessed via http_client.py interface.

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

from typing import Dict, Any, Optional, Callable, List
from enum import Enum


class HTTPMethod(Enum):
    """HTTP method enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ResponseValidator:
    """HTTP response validation with flexible rules."""
    
    def __init__(self):
        self._rules = []
    
    def add_status_code_rule(self, allowed_codes: List[int]):
        """Add status code validation rule."""
        def validator(response: Dict[str, Any]) -> bool:
            status = response.get('status_code', 0)
            return status in allowed_codes
        self._rules.append(validator)
        return self
    
    def add_field_rule(self, field: str, validator: Callable):
        """Add field validation rule."""
        def field_validator(response: Dict[str, Any]) -> bool:
            data = response.get('data', {})
            return validator(data.get(field))
        self._rules.append(field_validator)
        return self
    
    def add_custom_rule(self, validator: Callable):
        """Add custom validation rule."""
        self._rules.append(validator)
        return self
    
    def validate(self, response: Dict[str, Any]) -> bool:
        """Execute all validation rules."""
        return all(rule(response) for rule in self._rules)


def validate_http_response(response: Dict[str, Any], required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate HTTP response structure and content.
    
    Args:
        response: Response dictionary to validate
        required_fields: List of required fields in response data
        
    Returns:
        Response dict (unmodified if valid, error response if invalid)
    """
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    if required_fields:
        data = response.get('data', {})
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                'VALIDATION_ERROR'
            )
    
    return response


def create_validator() -> ResponseValidator:
    """Create new response validator instance."""
    return ResponseValidator()


__all__ = [
    'HTTPMethod',
    'ResponseValidator',
    'validate_http_response',
    'create_validator',
]

# EOF
