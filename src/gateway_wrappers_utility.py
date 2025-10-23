"""
gateway_wrappers_utility.py - UTILITY Interface Wrappers
Version: 2025.10.22.03
Description: Convenience wrappers for UTILITY interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
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
    """Get utility statistics (alias for utility_get_performance_stats)."""
    return execute_operation(GatewayInterface.UTILITY, 'get_stats')


def utility_reset() -> bool:
    """Reset UTILITY manager state (lifecycle management)."""
    return execute_operation(GatewayInterface.UTILITY, 'reset')


__all__ = [
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'utility_get_stats',
    'utility_reset',
]
