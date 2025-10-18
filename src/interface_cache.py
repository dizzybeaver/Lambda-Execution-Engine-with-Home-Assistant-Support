"""
interface_cache.py - Cache Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.18
Description: Router for Cache interface with dispatch dictionary pattern

CHANGELOG:
- 2025.10.17.18: Added get_metadata operation (Issue #25 fix)
  - New fast path metadata retrieval operation
  - Routes to cache_core.get_metadata() for O(1) access
  - Validation ensures key parameter exists
- 2025.10.17.17: MODERNIZED with dispatch dictionary pattern
  - Converted from elif chain (7 operations) to dispatch dictionary
  - O(1) operation lookup vs O(n) elif chain
  - Reduced code from ~170 lines to ~150 lines
  - Easier to maintain and extend (add operation = 1 line)
  - Follows pattern from interface_utility.py v2025.10.17.16
  - All validation logic preserved in helper functions
- 2025.10.17.13: FIXED Issue #20 - Added import error protection
- 2025.10.17.05: Added parameter validation for all operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# ===== IMPORT PROTECTION =====

try:
    from cache_core import (
        _execute_get_implementation,
        _execute_set_implementation,
        _execute_exists_implementation,
        _execute_delete_implementation,
        _execute_clear_implementation,
        _execute_cleanup_expired_implementation,
        _execute_get_stats_implementation,
        _execute_get_metadata_implementation
    )
    _CACHE_AVAILABLE = True
    _CACHE_IMPORT_ERROR = None
except ImportError as e:
    _CACHE_AVAILABLE = False
    _CACHE_IMPORT_ERROR = str(e)
    _execute_get_implementation = None
    _execute_set_implementation = None
    _execute_exists_implementation = None
    _execute_delete_implementation = None
    _execute_clear_implementation = None
    _execute_cleanup_expired_implementation = None
    _execute_get_stats_implementation = None
    _execute_get_metadata_implementation = None


# ===== VALIDATION HELPERS =====

def _validate_key_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate key parameter exists and is string."""
    if 'key' not in kwargs:
        raise ValueError(f"cache.{operation} requires 'key' parameter")
    if not isinstance(kwargs['key'], str):
        raise TypeError(
            f"cache.{operation} 'key' must be str, got {type(kwargs['key']).__name__}"
        )


def _validate_set_params(kwargs: Dict[str, Any]) -> None:
    """Validate set operation parameters."""
    _validate_key_param(kwargs, 'set')
    if 'value' not in kwargs:
        raise ValueError("cache.set requires 'value' parameter")


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for cache operations. Only called if cache available."""
    return {
        'get': lambda **kwargs: (
            _validate_key_param(kwargs, 'get'),
            _execute_get_implementation(**kwargs)
        )[1],
        
        'set': lambda **kwargs: (
            _validate_set_params(kwargs),
            _execute_set_implementation(**kwargs)
        )[1],
        
        'exists': lambda **kwargs: (
            _validate_key_param(kwargs, 'exists'),
            _execute_exists_implementation(**kwargs)
        )[1],
        
        'delete': lambda **kwargs: (
            _validate_key_param(kwargs, 'delete'),
            _execute_delete_implementation(**kwargs)
        )[1],
        
        'get_metadata': lambda **kwargs: (
            _validate_key_param(kwargs, 'get_metadata'),
            _execute_get_metadata_implementation(**kwargs)
        )[1],
        
        'clear': _execute_clear_implementation,
        'cleanup_expired': _execute_cleanup_expired_implementation,
        'get_stats': _execute_get_stats_implementation,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _CACHE_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_cache_operation(operation: str, **kwargs) -> Any:
    """
    Route cache operation requests using dispatch dictionary pattern.
    
    Operations:
    - get: Get cached value by key
    - set: Set cached value with optional TTL
    - exists: Check if key exists
    - delete: Delete cached value
    - get_metadata: Get metadata for cache entry (fast path, Issue #25)
    - clear: Clear all cache entries
    - cleanup_expired: Remove expired entries
    - get_stats: Get cache statistics
    
    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result (type varies by operation)
        
    Raises:
        RuntimeError: If cache interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    # Check cache availability first
    if not _CACHE_AVAILABLE:
        raise RuntimeError(
            f"Cache interface unavailable: {_CACHE_IMPORT_ERROR}. "
            "This may indicate missing cache_core module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown cache operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_cache_operation']

# EOF
