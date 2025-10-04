"""
Gateway - Revolutionary LUGS Integration (Lazy Unload Gateway System)
Version: 2025.10.03.03
Description: Universal gateway with LUGS memory optimization

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
import time
import threading
from typing import Dict, Any, Optional, Set, List
from enum import Enum

# LUGS Configuration
LUGS_ENABLED = True
LUGS_UNLOAD_DELAY = 30  # seconds
LUGS_MAX_RESIDENT_MODULES = 8
LUGS_MEMORY_PRESSURE_THRESHOLD = 100  # MB

# Module Categories
CORE_MODULES = {
    'gateway', 'cache_core', 'logging_core', 'singleton_core',
    'config_core', 'lambda_core'
}

HIGH_PRIORITY_UNLOAD = {
    'home_assistant_automation', 'home_assistant_scripts',
    'home_assistant_input_helpers', 'home_assistant_notifications',
    'home_assistant_areas', 'home_assistant_timers',
    'home_assistant_conversation', 'homeassistant_alexa',
    'home_assistant_devices', 'home_assistant_scenes',
    'home_assistant_climate', 'home_assistant_sensors',
    'home_assistant_weather'
}

CONDITIONAL_UNLOAD = {
    'http_client_core', 'security_core', 'metrics_core',
    'ha_common', 'circuit_breaker_core'
}


class UnloadPolicy(Enum):
    """Module unload policies."""
    IMMEDIATE = "immediate"
    DEFERRED = "deferred"
    MEMORY_PRESSURE = "memory"
    TIME_BASED = "time"
    NEVER = "never"


class LUGSManager:
    """LUGS - Lazy Unload Gateway System Manager."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._modules_loaded = {}
        self._module_load_times = {}
        self._module_last_use = {}
        self._module_ref_counts = {}
        self._unload_scheduled = {}
        self._cache_dependencies = {}
        self._hot_modules = set()
        
        self._stats = {
            'modules_loaded': 0,
            'modules_unloaded': 0,
            'modules_reloaded': 0,
            'cache_hit_no_load': 0,
            'unload_failed': 0,
            'emergency_unloads': 0,
            'memory_saved_mb': 0.0
        }
        
        self._policies = self._init_policies()
    
    def _init_policies(self) -> Dict[str, UnloadPolicy]:
        """Initialize unload policies for all modules."""
        policies = {}
        
        for module in CORE_MODULES:
            policies[module] = UnloadPolicy.NEVER
        
        for module in HIGH_PRIORITY_UNLOAD:
            policies[module] = UnloadPolicy.IMMEDIATE
        
        for module in CONDITIONAL_UNLOAD:
            policies[module] = UnloadPolicy.TIME_BASED
        
        return policies
    
    def track_module_load(self, module_name: str, module_obj: Any) -> None:
        """Track module loading."""
        with self._lock:
            current_time = time.time()
            
            if module_name not in self._modules_loaded:
                self._stats['modules_loaded'] += 1
            else:
                self._stats['modules_reloaded'] += 1
            
            self._modules_loaded[module_name] = module_obj
            self._module_load_times[module_name] = current_time
            self._module_last_use[module_name] = current_time
            self._module_ref_counts[module_name] = 1
    
    def track_module_use(self, module_name: str) -> None:
        """Track module usage."""
        with self._lock:
            self._module_last_use[module_name] = time.time()
    
    def increment_ref_count(self, module_name: str) -> None:
        """Increment module reference count."""
        with self._lock:
            self._module_ref_counts[module_name] = \
                self._module_ref_counts.get(module_name, 0) + 1
    
    def decrement_ref_count(self, module_name: str) -> None:
        """Decrement module reference count."""
        with self._lock:
            if module_name in self._module_ref_counts:
                self._module_ref_counts[module_name] -= 1
    
    def add_cache_dependency(self, cache_key: str, module_name: str) -> None:
        """Track cache dependency on module."""
        with self._lock:
            if cache_key not in self._cache_dependencies:
                self._cache_dependencies[cache_key] = set()
            self._cache_dependencies[cache_key].add(module_name)
    
    def remove_cache_dependency(self, cache_key: str) -> None:
        """Remove cache dependency."""
        with self._lock:
            if cache_key in self._cache_dependencies:
                del self._cache_dependencies[cache_key]
    
    def mark_hot_module(self, module_name: str) -> None:
        """Mark module as hot (protect from unload)."""
        with self._lock:
            self._hot_modules.add(module_name)
    
    def can_unload(self, module_name: str) -> bool:
        """Check if module can be safely unloaded."""
        with self._lock:
            if module_name in CORE_MODULES:
                return False
            
            if module_name in self._hot_modules:
                return False
            
            if self._module_ref_counts.get(module_name, 0) > 1:
                return False
            
            for deps in self._cache_dependencies.values():
                if module_name in deps:
                    return False
            
            return True
    
    def unload_module(self, module_name: str) -> bool:
        """Safely unload module from memory."""
        if not LUGS_ENABLED:
            return False
        
        if not self.can_unload(module_name):
            with self._lock:
                self._stats['unload_failed'] += 1
            return False
        
        try:
            with self._lock:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                if module_name in self._modules_loaded:
                    del self._modules_loaded[module_name]
                
                if module_name in self._module_load_times:
                    del self._module_load_times[module_name]
                
                if module_name in self._module_ref_counts:
                    del self._module_ref_counts[module_name]
                
                self._stats['modules_unloaded'] += 1
            
            import gc
            gc.collect()
            
            return True
            
        except Exception as e:
            with self._lock:
                self._stats['unload_failed'] += 1
            return False
    
    def schedule_unload(self, module_name: str, delay: Optional[float] = None) -> None:
        """Schedule module unload after delay."""
        if not LUGS_ENABLED:
            return
        
        policy = self._policies.get(module_name, UnloadPolicy.DEFERRED)
        
        if policy == UnloadPolicy.NEVER:
            return
        
        if policy == UnloadPolicy.IMMEDIATE:
            delay = 0
        elif delay is None:
            delay = LUGS_UNLOAD_DELAY
        
        unload_time = time.time() + delay
        
        with self._lock:
            self._unload_scheduled[module_name] = unload_time
    
    def process_scheduled_unloads(self) -> List[str]:
        """Process scheduled module unloads."""
        if not LUGS_ENABLED:
            return []
        
        current_time = time.time()
        unloaded = []
        
        with self._lock:
            to_unload = [
                name for name, unload_time in self._unload_scheduled.items()
                if current_time >= unload_time
            ]
        
        for module_name in to_unload:
            if self.unload_module(module_name):
                unloaded.append(module_name)
                with self._lock:
                    if module_name in self._unload_scheduled:
                        del self._unload_scheduled[module_name]
        
        return unloaded
    
    def check_memory_pressure(self) -> bool:
        """Check if memory pressure requires unloading."""
        try:
            import resource
            memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            return memory_mb > LUGS_MEMORY_PRESSURE_THRESHOLD
        except:
            return False
    
    def emergency_unload(self) -> List[str]:
        """Emergency unload under memory pressure."""
        if not LUGS_ENABLED:
            return []
        
        unloaded = []
        
        modules_to_unload = []
        with self._lock:
            for module_name in list(self._modules_loaded.keys()):
                if module_name not in CORE_MODULES and module_name not in self._hot_modules:
                    modules_to_unload.append(module_name)
        
        for module_name in modules_to_unload:
            if self.can_unload(module_name):
                if self.unload_module(module_name):
                    unloaded.append(module_name)
        
        if unloaded:
            with self._lock:
                self._stats['emergency_unloads'] += 1
            
            import gc
            gc.collect()
        
        return unloaded
    
    def enforce_module_limit(self) -> List[str]:
        """Enforce maximum resident module limit."""
        if not LUGS_ENABLED:
            return []
        
        unloaded = []
        
        with self._lock:
            loaded_count = len(self._modules_loaded)
            
            if loaded_count <= LUGS_MAX_RESIDENT_MODULES:
                return []
            
            non_core = [
                name for name in self._modules_loaded.keys()
                if name not in CORE_MODULES and name not in self._hot_modules
            ]
            
            non_core.sort(key=lambda n: self._module_last_use.get(n, 0))
            
            to_unload = loaded_count - LUGS_MAX_RESIDENT_MODULES
            candidates = non_core[:to_unload]
        
        for module_name in candidates:
            if self.can_unload(module_name):
                if self.unload_module(module_name):
                    unloaded.append(module_name)
        
        return unloaded
    
    def get_stats(self) -> Dict[str, Any]:
        """Get LUGS statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'modules_resident': len(self._modules_loaded),
                'modules_scheduled_unload': len(self._unload_scheduled),
                'cache_dependencies': len(self._cache_dependencies),
                'hot_modules': len(self._hot_modules),
                'unload_success_rate': (
                    self._stats['modules_unloaded'] / 
                    max(self._stats['modules_loaded'], 1) * 100
                ) if self._stats['modules_loaded'] > 0 else 0,
                'cache_hit_no_load_rate': (
                    self._stats['cache_hit_no_load'] /
                    max(self._stats['modules_loaded'], 1) * 100
                ) if self._stats['modules_loaded'] > 0 else 0
            })
        
        return stats
    
    def optimize(self) -> Dict[str, Any]:
        """Run LUGS optimization cycle."""
        if not LUGS_ENABLED:
            return {'optimizations': 0}
        
        optimizations = 0
        
        scheduled = self.process_scheduled_unloads()
        optimizations += len(scheduled)
        
        if self.check_memory_pressure():
            emergency = self.emergency_unload()
            optimizations += len(emergency)
        
        limited = self.enforce_module_limit()
        optimizations += len(limited)
        
        return {
            'optimizations': optimizations,
            'scheduled_unloads': len(scheduled),
            'emergency_unloads': len(self.emergency_unload()) if self.check_memory_pressure() else 0,
            'limit_enforced': len(limited)
        }


_lugs_manager = LUGSManager()


def get_lugs_manager() -> LUGSManager:
    """Get LUGS manager instance."""
    return _lugs_manager


def track_module_load(module_name: str, module_obj: Any) -> None:
    """Track module load for LUGS."""
    _lugs_manager.track_module_load(module_name, module_obj)


def track_module_use(module_name: str) -> None:
    """Track module usage for LUGS."""
    _lugs_manager.track_module_use(module_name)


def schedule_module_unload(module_name: str, delay: Optional[float] = None) -> None:
    """Schedule module for unloading."""
    _lugs_manager.schedule_unload(module_name, delay)


def add_cache_module_dependency(cache_key: str, module_name: str) -> None:
    """Add cache dependency on module."""
    _lugs_manager.add_cache_dependency(cache_key, module_name)


def remove_cache_module_dependency(cache_key: str) -> None:
    """Remove cache dependency."""
    _lugs_manager.remove_cache_dependency(cache_key)


def mark_module_hot(module_name: str) -> None:
    """Mark module as hot (protect from unload)."""
    _lugs_manager.mark_hot_module(module_name)


def optimize_lugs() -> Dict[str, Any]:
    """Run LUGS optimization cycle."""
    return _lugs_manager.optimize()


def get_lugs_stats() -> Dict[str, Any]:
    """Get LUGS statistics."""
    return _lugs_manager.get_stats()


__all__ = [
    'LUGSManager',
    'get_lugs_manager',
    'track_module_load',
    'track_module_use',
    'schedule_module_unload',
    'add_cache_module_dependency',
    'remove_cache_module_dependency',
    'mark_module_hot',
    'optimize_lugs',
    'get_lugs_stats',
    'LUGS_ENABLED',
    'CORE_MODULES',
    'HIGH_PRIORITY_UNLOAD'
]
