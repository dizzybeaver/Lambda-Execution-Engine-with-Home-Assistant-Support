"""
singleton_core.py - Core Singleton Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Thread-safe singleton management
"""

import threading
from typing import Any, Dict, Optional, Callable

_SINGLETONS: Dict[str, Any] = {}
_LOCK = threading.RLock()

def get_singleton(name: str, factory: Optional[Callable] = None) -> Any:
    """Get or create singleton instance."""
    with _LOCK:
        if name not in _SINGLETONS:
            if factory is None:
                raise ValueError(f"Singleton '{name}' does not exist and no factory provided")
            _SINGLETONS[name] = factory()
        return _SINGLETONS[name]

def set_singleton(name: str, instance: Any) -> None:
    """Set singleton instance."""
    with _LOCK:
        _SINGLETONS[name] = instance

def exists_singleton(name: str) -> bool:
    """Check if singleton exists."""
    with _LOCK:
        return name in _SINGLETONS

def reset_singleton(name: str) -> bool:
    """Reset singleton instance."""
    with _LOCK:
        if name in _SINGLETONS:
            del _SINGLETONS[name]
            return True
        return False

def reset_all_singletons() -> int:
    """Reset all singleton instances."""
    with _LOCK:
        count = len(_SINGLETONS)
        _SINGLETONS.clear()
        return count

def get_singleton_names() -> list:
    """Get names of all singletons."""
    with _LOCK:
        return list(_SINGLETONS.keys())

def get_singleton_count() -> int:
    """Get number of singletons."""
    with _LOCK:
        return len(_SINGLETONS)

def coordinate_operation(operation: Callable, context: Optional[Dict] = None) -> Any:
    """Execute operation with thread coordination."""
    with _LOCK:
        return operation()

def get_lock() -> threading.RLock:
    """Get the global lock."""
    return _LOCK
