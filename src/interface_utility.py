"""
interface_utility.py - UTILITY Interface Layer
Version: 3.0.0
Date: 2025-12-02
Description: Interface routing with DISPATCH pattern

ADDED: render_template to DISPATCH
ADDED: config_get to DISPATCH

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Dict, Optional, List

_CORE_AVAILABLE = False
_UTILITY = None
_RESPONSE_AVAILABLE = False

try:
    from utility_core import get_utility_manager, render_template_impl, config_get_impl
    _UTILITY = get_utility_manager()
    _CORE_AVAILABLE = True
except ImportError as e:
    pass

try:
    from response_formatters import format_response, format_response_fast, create_success_response, create_error_response
    _RESPONSE_AVAILABLE = True
except ImportError:
    pass


def _build_dispatch_dict() -> Dict[str, Any]:
    """Build DISPATCH dictionary."""
    if not _UTILITY:
        return {}
    
    return {
        'generate_uuid': _UTILITY.generate_uuid,
        'get_timestamp': _UTILITY.get_timestamp,
        'format_bytes': _UTILITY.format_bytes,
        'deep_merge': _UTILITY.deep_merge,
        'parse_json': _UTILITY.parse_json_safely,
        'safe_get': _UTILITY.safe_get,
        'format_response': lambda **kwargs: format_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        'format_response_fast': lambda **kwargs: format_response_fast(**kwargs) if _RESPONSE_AVAILABLE else None,
        'create_success_response': lambda **kwargs: create_success_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        'create_error_response': lambda **kwargs: create_error_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        'generate_correlation_id': _UTILITY.generate_correlation_id,
        'validate_data_structure': _UTILITY.validate_data_structure,
        'format_data_for_response': _UTILITY.format_data_for_response,
        'cleanup_utility_cache': _UTILITY.cleanup_cache,
        'get_utility_performance_stats': _UTILITY.get_performance_stats,
        'optimize_utility_performance': _UTILITY.optimize_performance,
        'configure_utility_caching': _UTILITY.configure_caching,
        'safe_string_conversion': _UTILITY.safe_string_conversion,
        'merge_dictionaries': _UTILITY.merge_dictionaries,
        'extract_error_details': _UTILITY.extract_error_details,
        'validate_operation_parameters': _UTILITY.validate_operation_parameters,
        'render_template': render_template_impl,
        'config_get': config_get_impl,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _CORE_AVAILABLE else {}


def execute_utility_operation(operation: str, **kwargs) -> Any:
    """Route utility operations via DISPATCH."""
    if not _CORE_AVAILABLE:
        raise RuntimeError("Utility interface unavailable: core module import failed.")
    
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(f"Unknown utility operation: '{operation}'.")
    
    if operation == 'parse_json' and 'data' not in kwargs:
        raise ValueError("parse_json requires 'data' parameter")
    if operation == 'safe_get':
        if 'dictionary' not in kwargs:
            raise ValueError("safe_get requires 'dictionary' parameter")
        if 'key_path' not in kwargs:
            raise ValueError("safe_get requires 'key_path' parameter")
    if operation == 'format_bytes' and 'size' not in kwargs:
        raise ValueError("format_bytes requires 'size' parameter")
    if operation == 'deep_merge':
        if 'dict1' not in kwargs or 'dict2' not in kwargs:
            raise ValueError("deep_merge requires 'dict1' and 'dict2' parameters")
    if operation == 'render_template':
        if 'template' not in kwargs:
            raise ValueError("render_template requires 'template' parameter")
        if 'data' not in kwargs:
            raise ValueError("render_template requires 'data' parameter")
    if operation == 'config_get' and 'key' not in kwargs:
        raise ValueError("config_get requires 'key' parameter")
    
    return _OPERATION_DISPATCH[operation](**kwargs)


def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return _UTILITY.generate_correlation_id(prefix) if _UTILITY else None


def parse_json_safely(json_str: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Parse JSON safely."""
    return _UTILITY.parse_json_safely(json_str, use_cache) if _UTILITY else None


def validate_data_structure(data: Any, expected_type: type, required_fields: Optional[List[str]] = None) -> bool:
    """Validate data structure."""
    return _UTILITY.validate_data_structure(data, expected_type, required_fields) if _UTILITY else False


def format_data_for_response(data: Any, format_type: str = "json", include_metadata: bool = True) -> Dict[str, Any]:
    """Format data for response."""
    return _UTILITY.format_data_for_response(data, format_type, include_metadata) if _UTILITY else {}


def cleanup_utility_cache() -> int:
    """Cleanup utility cache."""
    return _UTILITY.cleanup_cache() if _UTILITY else 0


def get_utility_performance_stats() -> Dict[str, Any]:
    """Get utility performance stats."""
    return _UTILITY.get_performance_stats() if _UTILITY else {}


def optimize_utility_performance() -> Dict[str, Any]:
    """Optimize utility performance."""
    return _UTILITY.optimize_performance() if _UTILITY else {}


def configure_utility_caching(enabled: bool, ttl: int = 300) -> None:
    """Configure utility caching."""
    if _UTILITY:
        _UTILITY.configure_caching(enabled, ttl)


def safe_string_conversion(data: Any, max_length: int = 10000) -> str:
    """Safe string conversion."""
    return _UTILITY.safe_string_conversion(data, max_length) if _UTILITY else "[no_utility]"


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge dictionaries."""
    return _UTILITY.merge_dictionaries(*dicts) if _UTILITY else {}


def extract_error_details(error: Exception) -> Dict[str, Any]:
    """Extract error details."""
    return _UTILITY.extract_error_details(error) if _UTILITY else {}


def validate_operation_parameters(params: Dict[str, Any], required: List[str]) -> bool:
    """Validate operation parameters."""
    return _UTILITY.validate_operation_parameters(params, required) if _UTILITY else False


def sanitize_data(data: Any) -> Any:
    """Sanitize data."""
    return _UTILITY.sanitize_data(data) if _UTILITY else data


__all__ = [
    'execute_utility_operation',
    'generate_correlation_id',
    'parse_json_safely',
    'validate_data_structure',
    'format_data_for_response',
    'cleanup_utility_cache',
    'get_utility_performance_stats',
    'optimize_utility_performance',
    'configure_utility_caching',
    'safe_string_conversion',
    'merge_dictionaries',
    'extract_error_details',
    'validate_operation_parameters',
    'sanitize_data',
]
