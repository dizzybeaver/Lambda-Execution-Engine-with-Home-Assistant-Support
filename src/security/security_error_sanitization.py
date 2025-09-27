"""
security_error_sanitization.py - IMMEDIATE FIX: Enhanced Error Sanitization Implementation
Version: 2025.09.27.01
Description: Enhanced error sanitization with comprehensive data protection

IMMEDIATE SECURITY FIXES APPLIED:
- ✅ ENHANCED: Comprehensive error message sanitization with pattern detection
- ✅ SECURED: Sensitive data filtering with extended keyword detection
- ✅ PROTECTED: Stack trace sanitization to prevent information disclosure
- ✅ STANDARDIZED: Consistent error response format across all interfaces
- ✅ VALIDATED: Input validation on all sanitization operations

ARCHITECTURE: SECONDARY IMPLEMENTATION - Enhanced Security
- Comprehensive sensitive data pattern detection
- Enhanced error message filtering with regex patterns
- Standardized error response format
- Integration with existing security gateway

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

import logging
import re
import traceback
from typing import Dict, Any, Optional, List, Union

# Gateway imports for enhanced security
from . import utility
from . import cache

logger = logging.getLogger(__name__)

# ===== ENHANCED SENSITIVE DATA PATTERNS =====

# Extended sensitive data patterns for comprehensive protection
ENHANCED_SENSITIVE_PATTERNS = [
    # Authentication tokens and keys
    r'(?i)(token|key|secret|password|pass|pwd)\s*[=:]\s*["\']?[a-zA-Z0-9+/=]{20,}["\']?',
    r'(?i)(bearer|basic|digest)\s+[a-zA-Z0-9+/=]{20,}',
    r'(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[=:]\s*["\']?[^\s"\']{20,}["\']?',
    
    # AWS credentials
    r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']?[A-Z0-9]{20,}["\']?',
    r'(?i)arn:aws:[a-zA-Z0-9-]+:[a-zA-Z0-9-]*:[0-9]+:[a-zA-Z0-9-/:]+',
    
    # URLs with credentials
    r'(?i)https?://[^:]+:[^@]+@[^\s]+',
    
    # Personal data
    r'(?i)(email|mail)\s*[=:]\s*["\']?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}["\']?',
    r'(?i)(phone|tel)\s*[=:]\s*["\']?[\d\s\-\+\(\)]{10,}["\']?',
    
    # Database connection strings
    r'(?i)(jdbc|mongodb|mysql|postgresql)://[^\s]+',
    
    # File paths that might contain sensitive data
    r'(?i)(C:\\|/home/|/Users/)[^\s]*\.(key|pem|p12|pfx|crt)',
    
    # IP addresses in private ranges
    r'\b(?:10\.|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b'
]

# Extended sensitive keywords
EXTENDED_SENSITIVE_KEYWORDS = [
    'password', 'secret', 'token', 'key', 'credential', 'auth', 'bearer',
    'session', 'cookie', 'jwt', 'oauth', 'api_key', 'access_token',
    'refresh_token', 'private_key', 'public_key', 'certificate', 'cert',
    'ssl', 'tls', 'encryption', 'decrypt', 'hash', 'signature', 'nonce',
    'salt', 'seed', 'entropy', 'random', 'uuid', 'guid', 'username',
    'userid', 'user_id', 'email', 'phone', 'ssn', 'social_security',
    'credit_card', 'card_number', 'account_number', 'routing_number'
]

# Stack trace patterns to remove
STACK_TRACE_PATTERNS = [
    r'File "([^"]+)", line \d+, in [^\n]+\n\s*[^\n]+',
    r'Traceback \(most recent call last\):[^\n]*(?:\n\s+[^\n]*)*',
    r'(?i)error:\s*[^\n]*(?:\n\s+at\s+[^\n]*)*',
    r'(?i)exception:\s*[^\n]*(?:\n\s+[^\n]*)*'
]

# ===== ENHANCED ERROR SANITIZATION FUNCTIONS =====

def enhanced_error_sanitization(error_data: Any, **kwargs) -> Dict[str, Any]:
    """
    Enhanced error sanitization with comprehensive data protection.
    Replaces sensitive information and standardizes error format.
    """
    try:
        # Input validation using utility gateway
        if not utility.validate_input_exists(error_data):
            return {"error": "Invalid error data", "sanitized": True}
        
        # Convert to standardized format
        if isinstance(error_data, Exception):
            error_dict = {
                "type": type(error_data).__name__,
                "message": str(error_data),
                "traceback": traceback.format_exc() if kwargs.get("include_traceback", False) else None
            }
        elif isinstance(error_data, dict):
            error_dict = error_data.copy()
        else:
            error_dict = {"message": str(error_data)}
        
        # Apply enhanced sanitization
        sanitized_error = {}
        
        # Sanitize error message
        if "message" in error_dict and error_dict["message"]:
            sanitized_error["message"] = _sanitize_error_message(error_dict["message"])
        else:
            sanitized_error["message"] = "An error occurred"
        
        # Sanitize error type (safe to include)
        if "type" in error_dict:
            sanitized_error["type"] = str(error_dict["type"])[:50]  # Limit length
        
        # Add error code if present (sanitized)
        if "code" in error_dict:
            code = str(error_dict["code"])
            if not _contains_sensitive_data(code):
                sanitized_error["code"] = code[:20]
        
        # Add timestamp
        sanitized_error["timestamp"] = utility.get_current_timestamp()
        
        # Add sanitization flag
        sanitized_error["sanitized"] = True
        
        # Remove traceback information to prevent information disclosure
        # (Never include full stack traces in production)
        
        return sanitized_error
        
    except Exception as e:
        logger.error(f"Error sanitization failed: {str(e)}")
        return {
            "error": "Error processing failed",
            "sanitized": True,
            "timestamp": utility.get_current_timestamp()
        }

def _sanitize_error_message(message: str) -> str:
    """Sanitize error message by removing sensitive information."""
    try:
        if not isinstance(message, str):
            return "Invalid error message format"
        
        sanitized = message
        
        # Apply enhanced sensitive pattern filtering
        for pattern in ENHANCED_SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        # Remove stack trace information
        for pattern in STACK_TRACE_PATTERNS:
            sanitized = re.sub(pattern, '[STACK_TRACE_REMOVED]', sanitized, flags=re.MULTILINE)
        
        # Replace sensitive keywords in context
        for keyword in EXTENDED_SENSITIVE_KEYWORDS:
            # Replace key-value pairs containing sensitive keywords
            pattern = rf'(?i){keyword}\s*[=:]\s*[^\s,\}}]*'
            sanitized = re.sub(pattern, f'{keyword}=[REDACTED]', sanitized)
        
        # Limit message length to prevent excessive information disclosure
        if len(sanitized) > 500:
            sanitized = sanitized[:500] + "...[TRUNCATED]"
        
        # Remove file paths that might contain sensitive information
        sanitized = re.sub(r'(?i)[a-zA-Z]:[\\\/][^\s]*', '[PATH_REMOVED]', sanitized)
        sanitized = re.sub(r'\/[a-zA-Z0-9_\/\.-]*\/[a-zA-Z0-9_\.-]*', '[PATH_REMOVED]', sanitized)
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Message sanitization failed: {str(e)}")
        return "Error message could not be processed safely"

def _contains_sensitive_data(text: str) -> bool:
    """Check if text contains sensitive data patterns."""
    try:
        if not isinstance(text, str):
            return True  # Err on the side of caution
        
        # Check against sensitive patterns
        for pattern in ENHANCED_SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                return True
        
        # Check for sensitive keywords
        text_lower = text.lower()
        for keyword in EXTENDED_SENSITIVE_KEYWORDS:
            if keyword in text_lower:
                return True
        
        return False
        
    except Exception:
        return True  # Err on the side of caution

def sanitize_response_data(response_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Sanitize response data to remove sensitive information.
    Ensures safe data for external use.
    """
    try:
        if not isinstance(response_data, dict):
            return {"error": "Invalid response format", "sanitized": True}
        
        sanitized_response = {}
        
        # Safe fields that can be included
        safe_fields = [
            'status', 'success', 'timestamp', 'correlation_id', 'operation',
            'duration_ms', 'response_time', 'version', 'sanitized'
        ]
        
        # Copy safe fields
        for field in safe_fields:
            if field in response_data:
                sanitized_response[field] = response_data[field]
        
        # Handle error data specially
        if 'error' in response_data:
            sanitized_response['error'] = enhanced_error_sanitization(
                response_data['error'], **kwargs
            )
        
        # Handle data field with sensitive filtering
        if 'data' in response_data and response_data['data']:
            sanitized_response['data'] = _sanitize_data_field(response_data['data'])
        
        # Handle message field
        if 'message' in response_data:
            message = str(response_data['message'])
            if not _contains_sensitive_data(message):
                sanitized_response['message'] = message[:200]  # Limit length
            else:
                sanitized_response['message'] = "Operation completed"
        
        # Add sanitization flag
        sanitized_response['sanitized'] = True
        
        return sanitized_response
        
    except Exception as e:
        logger.error(f"Response data sanitization failed: {str(e)}")
        return {
            "error": "Response processing failed",
            "sanitized": True,
            "timestamp": utility.get_current_timestamp()
        }

def _sanitize_data_field(data: Any) -> Any:
    """Sanitize data field recursively."""
    try:
        if isinstance(data, dict):
            sanitized_dict = {}
            for key, value in data.items():
                key_str = str(key).lower()
                
                # Skip sensitive keys entirely
                if any(sensitive in key_str for sensitive in EXTENDED_SENSITIVE_KEYWORDS):
                    sanitized_dict[key] = "[REDACTED]"
                else:
                    sanitized_dict[key] = _sanitize_data_field(value)
            
            return sanitized_dict
            
        elif isinstance(data, list):
            return [_sanitize_data_field(item) for item in data[:100]]  # Limit list size
            
        elif isinstance(data, str):
            if _contains_sensitive_data(data):
                return "[REDACTED]"
            else:
                return data[:200]  # Limit string length
                
        else:
            # For other types, convert to string and check
            str_value = str(data)
            if _contains_sensitive_data(str_value):
                return "[REDACTED]"
            else:
                return str_value[:100]
                
    except Exception as e:
        logger.error(f"Data field sanitization failed: {str(e)}")
        return "[SANITIZATION_FAILED]"

def create_safe_error_response(error: Union[Exception, str, Dict], 
                             correlation_id: Optional[str] = None,
                             **kwargs) -> Dict[str, Any]:
    """
    Create a safe error response with enhanced sanitization.
    Standard format for all error responses.
    """
    try:
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = utility.generate_correlation_id()
        
        # Apply enhanced error sanitization
        sanitized_error = enhanced_error_sanitization(error, **kwargs)
        
        # Create standardized response
        safe_response = {
            "success": False,
            "error": sanitized_error,
            "correlation_id": correlation_id,
            "timestamp": utility.get_current_timestamp(),
            "sanitized": True
        }
        
        # Add optional context (if safe)
        if kwargs.get("operation"):
            operation = str(kwargs["operation"])
            if not _contains_sensitive_data(operation):
                safe_response["operation"] = operation[:50]
        
        return safe_response
        
    except Exception as e:
        logger.error(f"Safe error response creation failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "type": "SafeErrorResponseFailure",
                "message": "Error response could not be processed safely",
                "sanitized": True
            },
            "correlation_id": correlation_id or "unknown",
            "timestamp": utility.get_current_timestamp(),
            "sanitized": True
        }

# EOF
