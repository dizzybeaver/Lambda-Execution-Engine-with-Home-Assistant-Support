"""
lazy_loader.py
Version: 2025.09.29.01
Description: Zero-Overhead Module Loading

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

import sys
import importlib
from typing import Any, Optional, Dict
from threading import Lock

class LazyModule:
    """
    Lazy-loading module proxy that imports only when accessed.
    Reduces Lambda cold start time and memory footprint.
    """
    
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[Any] = None
        self._lock = Lock()
        self._access_count = 0
    
    def _load_module(self) -> Any:
        """Load the module if not already loaded."""
        if self._module is None:
            with self._lock:
                if self._module is None:
                    try:
                        self._module = importlib.import_module(self._module_name)
                        self._access_count += 1
                    except ImportError as e:
                        raise ImportError(f"Failed to lazy load module {self._module_name}: {e}")
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from the lazy-loaded module."""
        module = self._load_module()
        return getattr(module, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Call the lazy-loaded module if it's callable."""
        module = self._load_module()
        return module(*args, **kwargs)
    
    @property
    def is_loaded(self) -> bool:
        """Check if module is loaded."""
        return self._module is not None
    
    @property
    def access_count(self) -> int:
        """Get number of times module was accessed."""
        return self._access_count


class LazyModuleRegistry:
    """
    Registry for managing lazy-loaded modules.
    Provides analytics and optimization capabilities.
    """
    
    def __init__(self):
        self._modules: Dict[str, LazyModule] = {}
        self._lock = Lock()
    
    def register(self, module_name: str) -> LazyModule:
        """Register a module for lazy loading."""
        if module_name not in self._modules:
            with self._lock:
                if module_name not in self._modules:
                    self._modules[module_name] = LazyModule(module_name)
        return self._modules[module_name]
    
    def get(self, module_name: str) -> Optional[LazyModule]:
        """Get a registered lazy module."""
        return self._modules.get(module_name)
    
    def get_loaded_modules(self) -> list:
        """Get list of currently loaded module names."""
        return [name for name, module in self._modules.items() if module.is_loaded]
    
    def get_unloaded_modules(self) -> list:
        """Get list of registered but unloaded module names."""
        return [name for name, module in self._modules.items() if not module.is_loaded]
    
    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all registered modules."""
        stats = {}
        for name, module in self._modules.items():
            stats[name] = {
                'loaded': module.is_loaded,
                'access_count': module.access_count
            }
        return stats
    
    def reset_stats(self):
        """Reset access statistics for all modules."""
        for module in self._modules.values():
            module._access_count = 0


_REGISTRY = LazyModuleRegistry()


def create_lazy_module(module_name: str) -> LazyModule:
    """
    Create a lazy-loading module proxy.
    
    Args:
        module_name: Full module name to lazy load
        
    Returns:
        LazyModule proxy object
    """
    return _REGISTRY.register(module_name)


def get_loaded_modules() -> list:
    """Get list of currently loaded module names."""
    return _REGISTRY.get_loaded_modules()


def get_usage_stats() -> Dict[str, Dict[str, Any]]:
    """Get usage statistics for all lazy-loaded modules."""
    return _REGISTRY.get_usage_stats()


def reset_usage_stats():
    """Reset usage statistics."""
    _REGISTRY.reset_stats()
