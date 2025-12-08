"""
interface_utility.py - Utility Interface Layer (INT-10)
Version: 3.1.0
Date: 2025-12-02
Description: Interface layer for utility operations

Architecture:
gateway.py → interface_utility.py → utility_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Callable
from utility_core import get_utility_manager


def _format_response_impl(status_code: int, body: Any, headers: Dict = None, **kwargs):
    """Format HTTP response."""
    manager = get_utility_manager()
    formatted = {
        'statusCode': status_code,
        'body': body if isinstance(body, str) else manager.parse_json(body),
        'headers': headers or {}
    }
    return formatted


def _parse_json_impl(data: str, **kwargs):
    """Parse JSON string."""
    manager = get_utility_manager()
    return manager.parse_json(data)


def _safe_get_impl(dictionary: Dict, key_path: str, default: Any = None, **kwargs):
    """Safely get nested dictionary value."""
    manager = get_utility_manager()
    return manager.safe_get(dictionary, key_path, default)


def _generate_uuid_impl(**kwargs):
    """Generate UUID."""
    manager = get_utility_manager()
    return manager.generate_uuid()


def _get_timestamp_impl(**kwargs):
    """Get current timestamp."""
    manager = get_utility_manager()
    return manager.get_timestamp()


def _get_stats_impl(**kwargs):
    """Get utility statistics."""
    manager = get_utility_manager()
    return manager.get_stats()


def _reset_impl(**kwargs):
    """Reset utility manager state."""
    manager = get_utility_manager()
    return manager.reset()


# ADDED: Template rendering
def _render_template_impl(template: dict, data: dict, **kwargs):
    """Render template with data substitution."""
    manager = get_utility_manager()
    return manager.render_template_impl(template, data, **kwargs)


# ADDED: Typed config retrieval
def _config_get_impl(key: str, default=None, **kwargs):
    """Get typed configuration value."""
    manager = get_utility_manager()
    return manager.config_get_impl(key, default, **kwargs)


# DISPATCH dictionary for utility operations
UTILITY_DISPATCH: Dict[str, Callable] = {
    'format_response': _format_response_impl,
    'parse_json': _parse_json_impl,
    'safe_get': _safe_get_impl,
    'generate_uuid': _generate_uuid_impl,
    'get_timestamp': _get_timestamp_impl,
    'get_stats': _get_stats_impl,
    'reset': _reset_impl,
    'render_template': _render_template_impl,  # ADDED
    'config_get': _config_get_impl,  # ADDED
}


def execute_utility_operation(operation: str, **kwargs) -> Any:
    """
    Execute utility operation via dispatch.
    
    Args:
        operation: Operation name (must be in UTILITY_DISPATCH)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: Unknown operation
        
    Example:
        result = execute_utility_operation('render_template', 
                                          template=tpl, data=data)
    """
    handler = UTILITY_DISPATCH.get(operation)
    
    if handler is None:
        valid_ops = ', '.join(sorted(UTILITY_DISPATCH.keys()))
        raise ValueError(
            f"Unknown utility operation: {operation}. "
            f"Valid operations: {valid_ops}"
        )
    
    return handler(**kwargs)


__all__ = [
    'execute_utility_operation',
    'UTILITY_DISPATCH',
]
