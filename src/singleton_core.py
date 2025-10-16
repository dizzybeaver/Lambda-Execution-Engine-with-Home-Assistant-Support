"""
singleton_core.py
Version: 2025.10.16.01
Description: Singleton management with generic operation dispatch pattern - CRITICAL BUGS FIXED

CRITICAL FIXES:
- Fixed thread safety issues in get() method
- Added error handling wrapper to execute_singleton_operation
- Added parameter validation for required parameters
- Removed circular indirection (direct _SINGLETON_MANAGER calls)
- Added name validation
- Improved error handling for factory function failures

Copyright 2025 Joseph Hersey

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

import os
import sys
import time
from typing import Any, Dict, Callable, Optional
from threading import Lock
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
    # Legacy operations for backward compatibility
    RESET = "reset"
    RESET_ALL = "reset_all"
    EXISTS = "exists"

# ===== SINGLETON CORE =====

class SingletonCore:
    """Manages singleton instances across the application with thread safety."""
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._lock = Lock()
        self._creation_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
    
    def get(self, name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
        """
        Get or create singleton instance with full thread safety.
        
        Args:
            name: Singleton name (must be non-empty string)
            factory_func: Optional factory function to create instance if not exists
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Singleton instance or None if not exists and no factory provided
            
        Raises:
            ValueError: If name is empty or None
            Exception: If factory function raises exception
        """
        if not name or not isinstance(name, str):
            raise ValueError("Singleton name must be a non-empty string")
        
        # Thread-safe double-checked locking with proper coverage
        if name not in self._instances:
            with self._lock:
                # Double-check inside lock
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
        
        # Access count and return must be inside lock for thread safety
        with self._lock:
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
            ValueError: If name is empty or None
        """
        if not name or not isinstance(name, str):
            raise ValueError("Singleton name must be a non-empty string")
        
        with self._lock:
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
        if not name or not isinstance(name, str):
            return False
        return name in self._instances
    
    def delete(self, name: str, **kwargs) -> bool:
        """
        Delete specific singleton (gateway-aligned naming).
        
        Args:
            name: Singleton name
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            True if singleton was deleted, False if it didn't exist
            
        Note:
            Returns False when singleton doesn't exist (not an error condition)
        """
        if not name or not isinstance(name, str):
            return False
        
        with self._lock:
            if name in self._instances:
                del self._instances[name]
                self._creation_times.pop(name, None)
                self._access_counts.pop(name, None)
                return True
            return False
    
    def clear(self, **kwargs) -> int:
        """
        Clear all singletons (gateway-aligned naming).
        
        Args:
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Count of singletons that were cleared
        """
        with self._lock:
            count = len(self._instances)
            self._instances.clear()
            self._creation_times.clear()
            self._access_counts.clear()
            return count
    
    def get_stats(self, **kwargs) -> Dict[str, Any]:
        """
        Get comprehensive singleton statistics (LMMS compliance).
        
        Args:
            **kwargs: Additional parameters (unused, for compatibility)
            
        Returns:
            Dictionary containing singleton statistics
            
        Note:
            Memory estimates use sys.getsizeof() which only measures shallow size.
            Actual memory usage may be higher for complex objects with nested structures.
        """
        with self._lock:
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
                'timestamp': time.time()
            }
    
    # ===== LEGACY METHODS (backward compatibility) =====
    
    def reset(self, name: str, **kwargs) -> bool:
        """Legacy name for delete."""
        return self.delete(name, **kwargs)
    
    def reset_all(self, **kwargs) -> int:
        """Legacy name for clear."""
        return self.clear(**kwargs)
    
    def exists(self, name: str, **kwargs) -> bool:
        """Legacy name for has."""
        return self.has(name, **kwargs)


# Global singleton manager instance
_SINGLETON_MANAGER = SingletonCore()


# ===== OPERATION MAP =====

_OPERATION_MAP = {
    SingletonOperation.GET: lambda **kwargs: _SINGLETON_MANAGER.get(**kwargs),
    SingletonOperation.SET: lambda **kwargs: _SINGLETON_MANAGER.set(**kwargs),
    SingletonOperation.HAS: lambda **kwargs: _SINGLETON_MANAGER.has(**kwargs),
    SingletonOperation.DELETE: lambda **kwargs: _SINGLETON_MANAGER.delete(**kwargs),
    SingletonOperation.CLEAR: lambda **kwargs: _SINGLETON_MANAGER.clear(**kwargs),
    SingletonOperation.GET_STATS: lambda **kwargs: _SINGLETON_MANAGER.get_stats(**kwargs),
    # Legacy operations
    SingletonOperation.RESET: lambda **kwargs: _SINGLETON_MANAGER.reset(**kwargs),
    SingletonOperation.RESET_ALL: lambda **kwargs: _SINGLETON_MANAGER.reset_all(**kwargs),
    SingletonOperation.EXISTS: lambda **kwargs: _SINGLETON_MANAGER.exists(**kwargs),
}


# ===== GENERIC OPERATION EXECUTION =====

def execute_singleton_operation(operation: SingletonOperation, **kwargs):
    """
    Universal singleton operation executor with error handling.
    
    Single function that routes all singleton operations to the SingletonCore instance.
    
    Args:
        operation: SingletonOperation enum value
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from SingletonCore
        
    Raises:
        ValueError: If operation is unknown
        Exception: If operation execution fails
    """
    try:
        if _USE_GENERIC_OPERATIONS:
            operation_func = _OPERATION_MAP.get(operation)
            if operation_func is None:
                raise ValueError(f"Unknown singleton operation: {operation}")
            return operation_func(**kwargs)
        else:
            # Legacy direct dispatch
            if operation == SingletonOperation.GET:
                return _SINGLETON_MANAGER.get(**kwargs)
            elif operation == SingletonOperation.SET:
                return _SINGLETON_MANAGER.set(**kwargs)
            elif operation == SingletonOperation.HAS:
                return _SINGLETON_MANAGER.has(**kwargs)
            elif operation == SingletonOperation.DELETE:
                return _SINGLETON_MANAGER.delete(**kwargs)
            elif operation == SingletonOperation.CLEAR:
                return _SINGLETON_MANAGER.clear(**kwargs)
            elif operation == SingletonOperation.GET_STATS:
                return _SINGLETON_MANAGER.get_stats(**kwargs)
            elif operation == SingletonOperation.RESET:
                return _SINGLETON_MANAGER.reset(**kwargs)
            elif operation == SingletonOperation.RESET_ALL:
                return _SINGLETON_MANAGER.reset_all(**kwargs)
            elif operation == SingletonOperation.EXISTS:
                return _SINGLETON_MANAGER.exists(**kwargs)
            else:
                raise ValueError(f"Unknown singleton operation: {operation}")
    except Exception as e:
        # Re-raise with context
        raise Exception(f"Singleton operation '{operation.value}' failed: {e}") from e


# ===== GATEWAY-ALIGNED IMPLEMENTATIONS =====
# These functions are called by interface_singleton.py router

def _execute_get_implementation(**kwargs) -> Any:
    """
    Execute singleton get operation.
    
    Args:
        name: Singleton name (required)
        factory_func: Optional factory function (optional)
        
    Returns:
        Singleton instance or None
        
    Raises:
        ValueError: If name not provided
    """
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for get operation")
    return _SINGLETON_MANAGER.get(**kwargs)


def _execute_set_implementation(**kwargs):
    """
    Execute singleton set operation.
    
    Args:
        name: Singleton name (required)
        instance: Instance to store (required)
        
    Raises:
        ValueError: If name or instance not provided
    """
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for set operation")
    if 'instance' not in kwargs:
        raise ValueError("Parameter 'instance' is required for set operation")
    return _SINGLETON_MANAGER.set(**kwargs)


def _execute_has_implementation(**kwargs) -> bool:
    """
    Execute singleton has operation.
    
    Args:
        name: Singleton name (required)
        
    Returns:
        True if singleton exists, False otherwise
        
    Raises:
        ValueError: If name not provided
    """
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for has operation")
    return _SINGLETON_MANAGER.has(**kwargs)


def _execute_delete_implementation(**kwargs) -> bool:
    """
    Execute singleton delete operation.
    
    Args:
        name: Singleton name (required)
        
    Returns:
        True if deleted, False if didn't exist
        
    Raises:
        ValueError: If name not provided
    """
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for delete operation")
    return _SINGLETON_MANAGER.delete(**kwargs)


def _execute_clear_implementation(**kwargs) -> int:
    """
    Execute singleton clear operation.
    
    Returns:
        Count of singletons cleared
    """
    return _SINGLETON_MANAGER.clear(**kwargs)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute singleton get_stats operation.
    
    Returns:
        Dictionary containing singleton statistics
    """
    return _SINGLETON_MANAGER.get_stats(**kwargs)


# ===== LEGACY COMPATIBILITY =====

def _execute_reset_implementation(**kwargs) -> bool:
    """Execute singleton reset (legacy)."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for reset operation")
    return _SINGLETON_MANAGER.reset(**kwargs)


def _execute_reset_all_implementation(**kwargs) -> int:
    """Execute reset all singletons (legacy)."""
    return _SINGLETON_MANAGER.reset_all(**kwargs)


def _execute_exists_implementation(**kwargs) -> bool:
    """Execute singleton exists check (legacy)."""
    if 'name' not in kwargs:
        raise ValueError("Parameter 'name' is required for exists operation")
    return _SINGLETON_MANAGER.exists(**kwargs)


# ===== EXPORTS =====

__all__ = [
    'SingletonOperation',
    'SingletonCore',
    'execute_singleton_operation',
    # Gateway-aligned implementations
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_has_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_get_stats_implementation',
    # Legacy implementations
    '_execute_reset_implementation',
    '_execute_reset_all_implementation',
    '_execute_exists_implementation',
]

# EOF
