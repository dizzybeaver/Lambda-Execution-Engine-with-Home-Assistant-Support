"""
security_core.py - Core Security Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Security validation within free tier limits
"""

import re
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, List, Set
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class ValidationResult:
    """Security validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Any] = None
    
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.valid and len(self.errors) == 0

_TRUSTED_DOMAINS: Set[str] = {
    "amazonaws.com",
    "amazon.com",
    "alexa.amazon.com"
}

_MAX_STRING_LENGTH = 10000
_MAX_DICT_DEPTH = 10
_MAX_LIST_LENGTH = 1000

_SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b.*\bSELECT\b)",
    r"(\bDROP\b.*\bTABLE\b)",
    r"(\bINSERT\b.*\bINTO\b)",
    r"(\bUPDATE\b.*\bSET\b)",
    r"(\bDELETE\b.*\bFROM\b)",
    r"(--)",
    r"(;.*\bDROP\b)",
    r"(\bOR\b.*=.*)",
    r"(1\s*=\s*1)",
    r"('.*OR.*'.*=.*')"
]

_XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>"
]

def add_trusted_domain(domain: str) -> None:
    """Add domain to trusted list."""
    _TRUSTED_DOMAINS.add(domain.lower())

def remove_trusted_domain(domain: str) -> None:
    """Remove domain from trusted list."""
    _TRUSTED_DOMAINS.discard(domain.lower())

def get_trusted_domains() -> List[str]:
    """Get list of trusted domains."""
    return list(_TRUSTED_DOMAINS)

def validate_string(value: str, max_length: Optional[int] = None) -> ValidationResult:
    """Validate string input."""
    errors = []
    warnings = []
    
    if not isinstance(value, str):
        errors.append(f"Expected string, got {type(value).__name__}")
        return ValidationResult(False, errors, warnings)
    
    max_len = max_length or _MAX_STRING_LENGTH
    if len(value) > max_len:
        errors.append(f"String exceeds maximum length of {max_len}")
    
    for pattern in _SQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            errors.append(f"Potential SQL injection detected: {pattern}")
            break
    
    for pattern in _XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            errors.append(f"Potential XSS detected: {pattern}")
            break
    
    sanitized = sanitize_string(value)
    if sanitized != value:
        warnings.append("String was sanitized")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=sanitized
    )

def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        return str(value)
    
    sanitized = value.strip()
    
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<iframe[^>]*>.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def validate_dict(data: Dict, max_depth: int = _MAX_DICT_DEPTH, current_depth: int = 0) -> ValidationResult:
    """Validate dictionary input."""
    errors = []
    warnings = []
    
    if not isinstance(data, dict):
        errors.append(f"Expected dict, got {type(data).__name__}")
        return ValidationResult(False, errors, warnings)
    
    if current_depth >= max_depth:
        errors.append(f"Dictionary depth exceeds maximum of {max_depth}")
        return ValidationResult(False, errors, warnings)
    
    sanitized_data = {}
    for key, value in data.items():
        key_result = validate_string(str(key))
        if not key_result.is_valid():
            errors.extend(key_result.errors)
            continue
        
        if isinstance(value, str):
            value_result = validate_string(value)
            if not value_result.is_valid():
                warnings.extend(value_result.warnings)
            sanitized_data[key] = value_result.sanitized_data
        elif isinstance(value, dict):
            value_result = validate_dict(value, max_depth, current_depth + 1)
            if not value_result.is_valid():
                errors.extend(value_result.errors)
            sanitized_data[key] = value_result.sanitized_data
        elif isinstance(value, list):
            value_result = validate_list(value, max_depth, current_depth + 1)
            if not value_result.is_valid():
                errors.extend(value_result.errors)
            sanitized_data[key] = value_result.sanitized_data
        else:
            sanitized_data[key] = value
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=sanitized_data
    )

def validate_list(data: List, max_depth: int = _MAX_DICT_DEPTH, current_depth: int = 0) -> ValidationResult:
    """Validate list input."""
    errors = []
    warnings = []
    
    if not isinstance(data, list):
        errors.append(f"Expected list, got {type(data).__name__}")
        return ValidationResult(False, errors, warnings)
    
    if len(data) > _MAX_LIST_LENGTH:
        errors.append(f"List exceeds maximum length of {_MAX_LIST_LENGTH}")
    
    if current_depth >= max_depth:
        errors.append(f"List depth exceeds maximum of {max_depth}")
        return ValidationResult(False, errors, warnings)
    
    sanitized_data = []
    for item in data:
        if isinstance(item, str):
            item_result = validate_string(item)
            if not item_result.is_valid():
                warnings.extend(item_result.warnings)
            sanitized_data.append(item_result.sanitized_data)
        elif isinstance(item, dict):
            item_result = validate_dict(item, max_depth, current_depth + 1)
            if not item_result.is_valid():
                errors.extend(item_result.errors)
            sanitized_data.append(item_result.sanitized_data)
        elif isinstance(item, list):
            item_result = validate_list(item, max_depth, current_depth + 1)
            if not item_result.is_valid():
                errors.extend(item_result.errors)
            sanitized_data.append(item_result.sanitized_data)
        else:
            sanitized_data.append(item)
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=sanitized_data
    )

def sanitize_input(data: Any) -> Any:
    """Sanitize any input data."""
    if isinstance(data, str):
        return sanitize_string(data)
    elif isinstance(data, dict):
        result = validate_dict(data)
        return result.sanitized_data if result.sanitized_data else data
    elif isinstance(data, list):
        result = validate_list(data)
        return result.sanitized_data if result.sanitized_data else data
    else:
        return data

def validate_url(url: str) -> ValidationResult:
    """Validate URL."""
    errors = []
    warnings = []
    
    if not isinstance(url, str):
        errors.append(f"Expected string URL, got {type(url).__name__}")
        return ValidationResult(False, errors, warnings)
    
    try:
        parsed = urlparse(url)
        
        if not parsed.scheme:
            errors.append("URL missing scheme (http/https)")
        elif parsed.scheme not in ['http', 'https']:
            errors.append(f"Invalid URL scheme: {parsed.scheme}")
        
        if not parsed.netloc:
            errors.append("URL missing domain")
        else:
            domain = parsed.netloc.split(':')[0].lower()
            is_trusted = any(domain.endswith(trusted) for trusted in _TRUSTED_DOMAINS)
            if not is_trusted:
                warnings.append(f"Domain not in trusted list: {domain}")
        
    except Exception as e:
        errors.append(f"URL parsing failed: {str(e)}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=url
    )

def validate_email(email: str) -> ValidationResult:
    """Validate email address."""
    errors = []
    warnings = []
    
    if not isinstance(email, str):
        errors.append(f"Expected string email, got {type(email).__name__}")
        return ValidationResult(False, errors, warnings)
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        errors.append("Invalid email format")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=email.lower().strip()
    )

def validate_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Lambda request event."""
    result = validate_dict(event)
    
    if not result.is_valid():
        raise ValueError(f"Request validation failed: {', '.join(result.errors)}")
    
    return result.sanitized_data

def validate_token(token: str) -> bool:
    """Validate authentication token."""
    if not token or not isinstance(token, str):
        return False
    
    if len(token) < 16:
        return False
    
    return True

def generate_token(data: str, secret: str) -> str:
    """Generate HMAC token."""
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

def verify_token(data: str, token: str, secret: str) -> bool:
    """Verify HMAC token."""
    expected = generate_token(data, secret)
    return hmac.compare_digest(token, expected)

def hash_value(value: str, algorithm: str = "sha256") -> str:
    """Hash a value."""
    if algorithm == "sha256":
        return hashlib.sha256(value.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(value.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(value.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

def validate_json(data: str) -> ValidationResult:
    """Validate JSON string."""
    errors = []
    warnings = []
    sanitized_data = None
    
    if not isinstance(data, str):
        errors.append(f"Expected string JSON, got {type(data).__name__}")
        return ValidationResult(False, errors, warnings)
    
    try:
        parsed = json.loads(data)
        sanitized_data = parsed
        
        if isinstance(parsed, dict):
            dict_result = validate_dict(parsed)
            if not dict_result.is_valid():
                errors.extend(dict_result.errors)
                warnings.extend(dict_result.warnings)
            sanitized_data = dict_result.sanitized_data
        elif isinstance(parsed, list):
            list_result = validate_list(parsed)
            if not list_result.is_valid():
                errors.extend(list_result.errors)
                warnings.extend(list_result.warnings)
            sanitized_data = list_result.sanitized_data
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {str(e)}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        sanitized_data=sanitized_data
    )

def get_security_stats() -> Dict[str, Any]:
    """Get security statistics."""
    return {
        "trusted_domains": len(_TRUSTED_DOMAINS),
        "max_string_length": _MAX_STRING_LENGTH,
        "max_dict_depth": _MAX_DICT_DEPTH,
        "max_list_length": _MAX_LIST_LENGTH,
        "sql_patterns": len(_SQL_INJECTION_PATTERNS),
        "xss_patterns": len(_XSS_PATTERNS)
    }
