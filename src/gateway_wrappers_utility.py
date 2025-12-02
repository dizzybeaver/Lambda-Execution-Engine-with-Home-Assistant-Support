"""
gateway_wrappers_utility.py - UTILITY Interface Wrappers
Version: 3.0.0
Date: 2025-12-02
Description: Convenience wrappers for UTILITY interface operations

ADDED: render_template - Template rendering wrapper
ADDED: config_get - Typed config retrieval wrapper

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation


def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict[str, Any]:
    """Format HTTP response."""
    return execute_operation(GatewayInterface.UTILITY, 'format_response', status_code=status_code, body=body, headers=headers)


def parse_json(data: str) -> Dict[str, Any]:
    """Parse JSON string."""
    return execute_operation(GatewayInterface.UTILITY, 'parse_json', data=data)


def safe_get(dictionary: Dict, key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    return execute_operation(GatewayInterface.UTILITY, 'safe_get', dictionary=dictionary, key_path=key_path, default=default)


def generate_uuid() -> str:
    """Generate UUID."""
    return execute_operation(GatewayInterface.UTILITY, 'generate_uuid')


def get_timestamp() -> float:
    """Get current timestamp."""
    return execute_operation(GatewayInterface.UTILITY, 'get_timestamp')


def utility_get_stats() -> Dict[str, Any]:
    """Get utility statistics."""
    return execute_operation(GatewayInterface.UTILITY, 'get_stats')


def utility_reset() -> bool:
    """Reset UTILITY manager state."""
    return execute_operation(GatewayInterface.UTILITY, 'reset')


# ADDED: Template rendering wrapper
def render_template(template: dict, **data) -> dict:
    """
    Render template with data substitution.
    
    Automatically adds correlation ID, logging, and metrics.
    
    Args:
        template: JSON template with {placeholders}
        **data: Data for substitution
        
    Returns:
        Rendered response dict
    """
    return execute_operation(GatewayInterface.UTILITY, 'render_template', template=template, data=data)


# ADDED: Config get wrapper
def config_get(key: str, default=None) -> Any:
    """
    Get typed configuration value.
    
    Type conversion based on default value type.
    
    Args:
        key: Environment variable name
        default: Default value (determines type)
        
    Returns:
        Typed configuration value
    """
    return execute_operation(GatewayInterface.UTILITY, 'config_get', key=key, default=default)


__all__ = [
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'utility_get_stats',
    'utility_reset',
    'render_template',
    'config_get',
]
