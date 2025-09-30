"""
Singleton Core - Singleton Pattern Management
Version: 2025.09.29.01
Daily Revision: 001
"""

from typing import Any, Dict, Callable, Optional
from threading import Lock

class SingletonCore:
    """Manages singleton instances across the application."""
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._lock = Lock()
    
    def get(self, name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
        """Get or create singleton instance."""
        if name not in self._instances:
            with self._lock:
                if name not in self._instances:
                    if factory_func is None:
                        raise ValueError(f"No singleton instance found for {name} and no factory provided")
                    self._instances[name] = factory_func()
        
        return self._instances[name]
    
    def set(self, name: str, instance: Any, **kwargs):
        """Set singleton instance."""
        with self._lock:
            self._instances[name] = instance
    
    def reset(self, name: str, **kwargs) -> bool:
        """Reset singleton instance."""
        with self._lock:
            if name in self._instances:
                del self._instances[name]
                return True
            return False
    
    def reset_all(self, **kwargs):
        """Reset all singleton instances."""
        with self._lock:
            self._instances.clear()
    
    def exists(self, name: str) -> bool:
        """Check if singleton exists."""
        return name in self._instances

_SINGLETON_MANAGER = SingletonCore()

def _execute_get_implementation(name: str, factory_func: Optional[Callable] = None, **kwargs) -> Any:
    """Execute singleton get."""
    return _SINGLETON_MANAGER.get(name, factory_func, **kwargs)

def _execute_set_implementation(name: str, instance: Any, **kwargs):
    """Execute singleton set."""
    return _SINGLETON_MANAGER.set(name, instance, **kwargs)

def _execute_reset_implementation(name: str, **kwargs) -> bool:
    """Execute singleton reset."""
    return _SINGLETON_MANAGER.reset(name, **kwargs)

def _execute_reset_all_implementation(**kwargs):
    """Execute reset all singletons."""
    return _SINGLETON_MANAGER.reset_all(**kwargs)

def _execute_exists_implementation(name: str, **kwargs) -> bool:
    """Execute singleton exists check."""
    return _SINGLETON_MANAGER.exists(name)

#EOF
