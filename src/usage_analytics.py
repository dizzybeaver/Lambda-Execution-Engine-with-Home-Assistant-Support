"""
usage_analytics.py - Lambda Module Usage Analytics
Version: 2025.10.07.01
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, List, Set
import time


_usage_data = {
    'total_invocations': 0,
    'module_usage': {},
    'request_types': {}
}


def record_request_usage(loaded_modules: List[str], request_type: str) -> None:
    """Record Lambda request usage analytics."""
    global _usage_data
    
    _usage_data['total_invocations'] += 1
    
    # Record module usage
    for module in loaded_modules:
        if module not in _usage_data['module_usage']:
            _usage_data['module_usage'][module] = 0
        _usage_data['module_usage'][module] += 1
    
    # Record request type
    if request_type not in _usage_data['request_types']:
        _usage_data['request_types'][request_type] = 0
    _usage_data['request_types'][request_type] += 1


def get_usage_summary() -> Dict[str, Any]:
    """Get usage analytics summary."""
    return {
        'total_invocations': _usage_data['total_invocations'],
        'unique_modules': len(_usage_data['module_usage']),
        'module_usage': _usage_data['module_usage'],
        'request_types': _usage_data['request_types'],
        'timestamp': time.time()
    }


def reset_usage_stats() -> None:
    """Reset usage statistics."""
    global _usage_data
    _usage_data = {
        'total_invocations': 0,
        'module_usage': {},
        'request_types': {}
    }

# EOF
