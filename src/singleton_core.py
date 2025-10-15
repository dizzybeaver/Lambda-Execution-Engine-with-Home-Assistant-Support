"""
singleton_core.py
Version: 2025.10.14.01
Description: Singleton management with generic operation dispatch pattern - PHASE 1 FIXED

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
    """Manages singleton instances across the application."""
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._lock = Lock()
        self._creation_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
    
    def get(self, name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
        """Get or create singleton instance."""
        if name not in self._instances:
            with self._lock:
                if name not in self._instances:
                    if factory_func is None:
                        return None
                    self._instances[name] = factory_func()
                    self._creation_times[name] = time.time()
                    self._access_counts[name] = 0
        
        self._access_counts[name] = self._access_counts.get(name, 0) + 1
        return self._instances[name]
    
    def set(self, name: str, instance: Any, **kwargs):
        """Set singleton instance."""
        with self._lock:
            self._instances[name] = instance
            self._creation_times[name] = time.time()
            self._access_counts[name] = 0
    
    def has(self, name: str, **kwargs) -> bool:
        """Check if singleton exists (gateway-aligned naming)."""
        return name in self._instances
    
    def delete(self, name: str, **kwargs) -> bool:
        """Delete specific singleton (gateway-aligned naming)."""
        with self._lock:
            if name in self._instances:
                del self._instances[name]
                self._creation_times.pop(name, None)
                self._access_counts.pop(name, None)
                return True
            return False
    
    def clear(self, **kwargs) -> int:
        """Clear all singletons (gateway-aligned naming). Returns count cleared."""
        with self._lock:
            count = len(self._instances)
            self._instances.clear()
            self._creation_times.clear()
            self._access_counts.clear()
            return count
    
    def get_stats(self, **kwargs) -> Dict[str, Any]:
        """Get comprehensive singleton statistics (LMMS compliance)."""
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


_SINGLETON_MANAGER = SingletonCore()


# ===== GENERIC OPERATION EXECUTION =====

def execute_singleton_operation(operation: SingletonOperation, *args, **kwargs):
    """
    Universal singleton operation executor.
    
    Single function that routes all singleton operations to the SingletonCore instance.
    """
    if not _USE_GENERIC_OPERATIONS:
        return _execute_legacy_operation(operation, *args, **kwargs)
    
    try:
        method_name = operation.value
        method = getattr(_SINGLETON_MANAGER, method_name, None)
        
        if method is None:
            return None if operation == SingletonOperation.GET else False
        
        return method(*args, **kwargs)
    except Exception:
        return None if operation == SingletonOperation.GET else False


def _execute_legacy_operation(operation: SingletonOperation, *args, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    try:
        method = getattr(_SINGLETON_MANAGER, operation.value)
        return method(*args, **kwargs)
    except Exception:
        return None if operation == SingletonOperation.GET else False


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====
# These match the gateway.py _OPERATION_REGISTRY exactly

def _execute_get_implementation(name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
    """Execute singleton get."""
    return execute_singleton_operation(SingletonOperation.GET, name, factory_func, **kwargs)


def _execute_set_implementation(name: str, instance: Any, **kwargs):
    """Execute singleton set."""
    return execute_singleton_operation(SingletonOperation.SET, name, instance, **kwargs)


def _execute_has_implementation(name: str, **kwargs) -> bool:
    """Execute singleton has check (gateway-aligned)."""
    return execute_singleton_operation(SingletonOperation.HAS, name, **kwargs)


def _execute_delete_implementation(name: str, **kwargs) -> bool:
    """Execute singleton delete (gateway-aligned)."""
    return execute_singleton_operation(SingletonOperation.DELETE, name, **kwargs)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute singleton clear all (gateway-aligned)."""
    return execute_singleton_operation(SingletonOperation.CLEAR, **kwargs)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute singleton get stats (gateway-aligned, LMMS compliance)."""
    return execute_singleton_operation(SingletonOperation.GET_STATS, **kwargs)


# ===== LEGACY COMPATIBILITY =====

def _execute_reset_implementation(name: str, **kwargs) -> bool:
    """Execute singleton reset (legacy)."""
    return execute_singleton_operation(SingletonOperation.RESET, name, **kwargs)


def _execute_reset_all_implementation(**kwargs) -> int:
    """Execute reset all singletons (legacy)."""
    return execute_singleton_operation(SingletonOperation.RESET_ALL, **kwargs)


def _execute_exists_implementation(name: str, **kwargs) -> bool:
    """Execute singleton exists check (legacy)."""
    return execute_singleton_operation(SingletonOperation.EXISTS, name, **kwargs)


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
