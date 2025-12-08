"""
singleton_core.py
Version: 2025.10.22.01
Description: Singleton management with SINGLETON pattern, rate limiting, NO threading locks

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# ===== DESIGN DECISIONS =====

"""
SINGLETON vs CACHE INTERFACE DISTINCTION (Issue #41):

1. **SINGLETON Interface Purpose:**
   - Manages **object instances** (classes, managers, services)
   - Ensures **one instance per name** across application
   - Factory pattern support for lazy initialization
   - Examples: CacheManager, SecurityValidator, ConfigManager
   - Access patterns: Named singletons with complex initialization
   - Lifetime: Entire Lambda container lifecycle

2. **CACHE Interface Purpose:**
   - Manages **data values** (strings, dicts, primitives, serializable objects)
   - Time-based expiration (TTL)
   - LRU eviction when memory pressure detected
   - Examples: API responses, computed values, temporary data
   - Access patterns: Key-value storage with expiration
   - Lifetime: Until TTL expires or memory pressure
   - Optimized for high-frequency read/write

CRITICAL DESIGN DECISION (2025.10.22):
- NO threading locks (Lambda single-threaded - DEC-04, AP-08)
- Rate limiting for DoS protection instead of locks (LESS-21)
- SINGLETON pattern for lifecycle management (LESS-18)
"""

# ===== IMPORTS =====

import os
import sys
import time
from typing import Any, Dict, Callable, Optional
from collections import deque
from enum import Enum

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'

# ===== SINGLETON OPERATION ENUM =====

class SingletonOperation(Enum):
    """Enumeration of all singleton operations - aligned with gateway registry."""
    GET = "get"
    SET = "set"
    HAS = "has"
    DELETE = "delete"
    CLEAR = "clear"
    GET_STATS = "get_stats"
    RESET = "reset"
    # Legacy operations for backward compatibility
    RESET_ALL = "reset_all"
    EXISTS = "exists"

# ===== SINGLETON CORE =====

class SingletonCore:
    """
    Manages singleton instances across the application.
    
    CRITICAL: NO threading locks - Lambda is single-threaded (DEC-04, AP-08)
    Uses rate limiting for DoS protection instead of locks (LESS-21)
    """
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._creation_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        
        # Rate limiting (1000 ops/sec for infrastructure - LESS-21)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check rate limit (1000 ops/sec).
        
        Returns:
            True if within rate limit, False if rate limited
        """
        now = time.time() * 1000
        
        # Remove timestamps outside window
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if at limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        
        # Add timestamp
        self._rate_limiter.append(now)
        return True
    
    def get(self, name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
        """
        Get or create singleton instance.
        
        Args:
            name: Singleton name (must be non-empty string)
            factory_func: Optional factory function to create instance if not exists
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Singleton instance or None if not exists and no factory provided
            
        Raises:
            ValueError: If name is empty or None or rate limited
            Exception: If factory function raises exception
        """
        if not self._check_rate_limit():
            raise ValueError("Rate limit exceeded (1000 ops/sec)")
        
        if not name or not isinstance(name, str):
            raise ValueError("Singleton name must be a non-empty string")
        
        # Check if exists
        if name not in self._instances:
            if factory_func is None:
                return None
            
            # Create instance with error handling
            try:
                instance = factory_func()
                self._instances[name] = instance
                self._creation_times[name] = time.time()
                self._access_counts[name] = 0
            except Exception as e:
                # Don't leave partial state on failure
                raise Exception(f"Failed to create singleton '{name}': {e}") from e
        
        # Update access count and return
        if name in self._instances:
            self._access_counts[name] = self._access_counts.get(name, 0) + 1
            return self._instances[name]
        return None
    
    def set(self, name: str, instance: Any, **kwargs):
        """
        Set singleton instance.
        
        Args:
            name: Singleton name (must be non-empty string)
            instance: Instance to store (can be any type including None)
            **kwargs: Additional parameters (unused, for compatibility)
            
        Raises:
            ValueError: If name is empty or None or rate limited
        """
        if not self._check_rate_limit():
            raise ValueError("Rate limit exceeded (1000 ops/sec)")
        
        if not name or not isinstance(name, str):
            raise ValueError("Singleton name must be a non-empty string")
        
        self._instances[name] = instance
        self._creation_times[name] = time.time()
        self._access_counts[name] = 0
    
    def has(self, name: str, **kwargs) -> bool:
        """
        Check if singleton exists (gateway-aligned naming).
        
        Args:
            name: Singleton name
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            True if singleton exists, False otherwise
        """
        if not self._check_rate_limit():
            return False
        return name in self._instances
    
    def delete(self, name: str, **kwargs) -> bool:
        """
        Delete singleton instance.
        
        Args:
            name: Singleton name
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            True if deleted, False if didn't exist or rate limited
        """
        if not self._check_rate_limit():
            return False
        
        if name in self._instances:
            del self._instances[name]
            self._creation_times.pop(name, None)
            self._access_counts.pop(name, None)
            return True
        return False
    
    def clear(self, **kwargs) -> int:
        """
        Clear all singleton instances.
        
        Args:
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Count of singletons cleared (0 if rate limited)
        """
        if not self._check_rate_limit():
            return 0
        
        count = len(self._instances)
        self._instances.clear()
        self._creation_times.clear()
        self._access_counts.clear()
        return count
    
    def get_stats(self, **kwargs) -> Dict[str, Any]:
        """
        Get statistics about managed singletons.
        
        Args:
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Dictionary containing singleton statistics
        """
        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded'}
        
        total_memory = sum(
            sys.getsizeof(instance) 
            for instance in self._instances.values()
        )
        
        return {
            'total_singletons': len(self._instances),
            'singleton_names': list(self._instances.keys()),
            'singleton_types': {
                name: type(instance).__name__ 
                for name, instance in self._instances.items()
            },
            'creation_times': dict(self._creation_times),
            'access_counts': dict(self._access_counts),
            'estimated_memory_bytes': total_memory,
            'estimated_memory_kb': total_memory / 1024,
            'estimated_memory_mb': total_memory / (1024 * 1024),
            'memory_note': 'Estimates are shallow size only (sys.getsizeof)',
            'rate_limited_count': self._rate_limited_count,
            'timestamp': time.time()
        }
    
    def reset(self, **kwargs) -> bool:
        """
        Reset SINGLETON manager state (lifecycle management).
        
        Returns:
            True if reset successful, False if rate limited
        """
        if not self._check_rate_limit():
            return False
        
        try:
            # Reset rate limiter
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            return True
        except Exception:
            return False
    
    # ===== LEGACY METHODS (backward compatibility) =====
    
    def reset_all(self, **kwargs) -> int:
        """Legacy name for clear."""
        return self.clear(**kwargs)
    
    def exists(self, name: str, **kwargs) -> bool:
        """Legacy name for has."""
        return self.has(name, **kwargs)


# Global singleton manager instance
_manager_core = None


def get_singleton_manager() -> SingletonCore:
    """
    Get the singleton manager instance (SINGLETON pattern - LESS-18).
    
    Returns:
        SingletonCore instance
        
    Note:
        Uses SINGLETON pattern for lifecycle management.
        Ironic: SINGLETON interface using SINGLETON pattern for itself!
    """
    global _manager_core
    
    try:
        # Try to use gateway's SINGLETON system if available
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('singleton_manager')
        if manager is None:
            # Create and register
            if _manager_core is None:
                _manager_core = SingletonCore()
            singleton_register('singleton_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        # Fallback: use module-level singleton
        if _manager_core is None:
            _manager_core = SingletonCore()
        return _manager_core


# ===== OPERATION MAP =====

_OPERATION_MAP = {
    SingletonOperation.GET: lambda **kwargs: get_singleton_manager().get(**kwargs),
    SingletonOperation.SET: lambda **kwargs: get_singleton_manager().set(**kwargs),
    SingletonOperation.HAS: lambda **kwargs: get_singleton_manager().has(**kwargs),
    SingletonOperation.DELETE: lambda **kwargs: get_singleton_manager().delete(**kwargs),
    SingletonOperation.CLEAR: lambda **kwargs: get_singleton_manager().clear(**kwargs),
    SingletonOperation.GET_STATS: lambda **kwargs: get_singleton_manager().get_stats(**kwargs),
    SingletonOperation.RESET: lambda **kwargs: get_singleton_manager().reset(**kwargs),
    # Legacy operations
    SingletonOperation.RESET_ALL: lambda **kwargs: get_singleton_manager().reset_all(**kwargs),
    SingletonOperation.EXISTS: lambda **kwargs: get_singleton_manager().exists(**kwargs),
}


# ===== GENERIC OPERATION EXECUTION =====

def execute_singleton_operation(operation: SingletonOperation, **kwargs):
    """
    Universal singleton operation executor with error handling.
    
    Args:
        operation: SingletonOperation enum value
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result (type varies by operation)
        
    Raises:
        ValueError: If operation is invalid or required parameters missing
        Exception: If operation execution fails
    """
    if not isinstance(operation, SingletonOperation):
        raise ValueError(f"Invalid operation type: {type(operation)}")
    
    if operation not in _OPERATION_MAP:
        raise ValueError(f"Unknown singleton operation: {operation}")
    
    try:
        operation_func = _OPERATION_MAP[operation]
        return operation_func(**kwargs)
    except Exception as e:
        raise Exception(f"Singleton operation '{operation.value}' failed: {e}") from e


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_get_implementation(**kwargs):
    """Execute singleton get operation."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for get operation")
    return get_singleton_manager().get(**kwargs)


def _execute_set_implementation(**kwargs):
    """Execute singleton set operation."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for set operation")
    if 'instance' not in kwargs:
        raise ValueError("Parameter 'instance' is required for set operation")
    return get_singleton_manager().set(**kwargs)


def _execute_has_implementation(**kwargs) -> bool:
    """Execute singleton has operation."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for has operation")
    return get_singleton_manager().has(**kwargs)


def _execute_delete_implementation(**kwargs) -> bool:
    """Execute singleton delete operation."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for delete operation")
    return get_singleton_manager().delete(**kwargs)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute singleton clear operation."""
    return get_singleton_manager().clear(**kwargs)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute singleton get_stats operation."""
    return get_singleton_manager().get_stats(**kwargs)


def _execute_reset_implementation(**kwargs) -> bool:
    """Execute singleton reset operation."""
    return get_singleton_manager().reset(**kwargs)


# ===== LEGACY COMPATIBILITY =====

def _execute_reset_all_implementation(**kwargs) -> int:
    """Execute reset all singletons (legacy)."""
    return get_singleton_manager().reset_all(**kwargs)


def _execute_exists_implementation(**kwargs) -> bool:
    """Execute singleton exists check (legacy)."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for exists operation")
    return get_singleton_manager().exists(**kwargs)


# ===== EXPORTS =====

__all__ = [
    'SingletonCore',
    'SingletonOperation',
    'execute_singleton_operation',
    'get_singleton_manager',
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_has_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_get_stats_implementation',
    '_execute_reset_implementation',
    '_execute_reset_all_implementation',
    '_execute_exists_implementation'
]

# EOF
