# ha_interconnect_validation.py
"""
ha_interconnect_validation.py - Input Validation Helpers
Version: 1.0.0
Date: 2025-11-05
Purpose: Shared validation functions for HA gateway

SECURITY:
- Type checking for all parameters
- Boundary validation for numeric inputs
- String sanitization for entity IDs
- Injection protection for endpoints
- Error detection for invalid formats

Architecture:
Validation helpers used by all HA gateway wrappers:
- ha_interconnect_alexa.py
- ha_interconnect_devices.py
- ha_interconnect_assist.py

Pattern:
Leaf module (no HA imports, no circular dependencies)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any


def _validate_entity_id(entity_id: str) -> bool:
    """
    Validate entity ID format.
    
    Rules:
    - Must be string
    - Length ≥3 characters
    - Must contain '.' separator
    - No injection characters
    
    Args:
        entity_id: Entity ID to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_entity_id('light.living_room')
        True
        >>> _validate_entity_id('invalid')
        False
        >>> _validate_entity_id('light.<script>')
        False
    """
    if not isinstance(entity_id, str):
        return False
    if not entity_id or len(entity_id) < 3:
        return False
    if '.' not in entity_id:
        return False
    # Basic sanitization check - prevent injection
    if any(c in entity_id for c in ['<', '>', '"', "'", '&', ';', '`']):
        return False
    return True


def _validate_domain(domain: str) -> bool:
    """
    Validate domain name.
    
    Rules:
    - Must be string
    - Length ≥2 characters
    - Alphanumeric with underscores only
    - No special characters
    
    Args:
        domain: Domain to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_domain('light')
        True
        >>> _validate_domain('climate_control')
        True
        >>> _validate_domain('x')
        False
        >>> _validate_domain('light<script>')
        False
    """
    if not isinstance(domain, str):
        return False
    if not domain or len(domain) < 2:
        return False
    # Must be alphanumeric with underscores
    if not all(c.isalnum() or c == '_' for c in domain):
        return False
    return True


def _validate_event(event: Dict[str, Any]) -> bool:
    """
    Validate event dictionary structure.
    
    Rules:
    - Must be dictionary
    - Cannot be empty
    - Basic type checking
    
    Args:
        event: Event to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_event({'type': 'discovery'})
        True
        >>> _validate_event({})
        False
        >>> _validate_event(None)
        False
    """
    if not isinstance(event, dict):
        return False
    if not event:
        return False
    return True


def _validate_threshold(threshold: float) -> bool:
    """
    Validate threshold value.
    
    Rules:
    - Must be numeric (int or float)
    - Range: 0.0 to 1.0 (inclusive)
    - Represents percentage/probability
    
    Args:
        threshold: Threshold to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_threshold(0.6)
        True
        >>> _validate_threshold(1.0)
        True
        >>> _validate_threshold(1.5)
        False
        >>> _validate_threshold(-0.1)
        False
    """
    if not isinstance(threshold, (int, float)):
        return False
    if threshold < 0.0 or threshold > 1.0:
        return False
    return True

def _validate_endpoint(endpoint: str) -> bool:
    """
    Validate API endpoint.
    
    Rules:
    - Must be string
    - Length ≥2 characters
    - Must start with '/'
    - No injection characters
    - No newlines/carriage returns
    
    Args:
        endpoint: Endpoint to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_endpoint('/api/states')
        True
        >>> _validate_endpoint('/api/services/light/turn_on')
        True
        >>> _validate_endpoint('api/states')
        False
        >>> _validate_endpoint('/api/states<script>')
        False
    """
    if not isinstance(endpoint, str):
        return False
    if not endpoint or len(endpoint) < 2:
        return False
    # Must start with /
    if not endpoint.startswith('/'):
        return False
    # Basic injection protection
    if any(c in endpoint for c in ['<', '>', '"', "'", '&', ';', '`', '\n', '\r']):
        return False
    return True


def _validate_http_method(method: str) -> bool:
    """
    Validate HTTP method.
    
    Rules:
    - Must be string
    - Must be in whitelist
    - Case-insensitive check
    
    Args:
        method: HTTP method to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_http_method('GET')
        True
        >>> _validate_http_method('post')
        True
        >>> _validate_http_method('INVALID')
        False
    """
    if not isinstance(method, str):
        return False
    valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    return method.upper() in valid_methods


def _validate_message(message: str) -> bool:
    """
    Validate message string.
    
    Rules:
    - Must be string
    - Length ≥1 character
    - Maximum 10KB (10,000 chars)
    - Prevents abuse/DoS
    
    Args:
        message: Message to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> _validate_message('Hello')
        True
        >>> _validate_message('')
        False
        >>> _validate_message('x' * 10001)
        False
    """
    if not isinstance(message, str):
        return False
    if not message or len(message) < 1:
        return False
    # Length limit (prevent DoS)
    if len(message) > 10000:  # 10KB max
        return False
    return True


# ====================
# EXPORTS
# ====================

__all__ = [
    '_validate_entity_id',
    '_validate_domain',
    '_validate_event',
    '_validate_threshold',
    '_validate_endpoint',
    '_validate_http_method',
    '_validate_message',
]

# SECURITY NOTE:
# These validators provide first-line defense against:
# - Type confusion attacks
# - Injection attacks (XSS, SQL, command)
# - DoS via oversized inputs
# - Format confusion
# - Boundary violations
#
# Always validate at gateway layer before passing to interfaces.

# EOF
