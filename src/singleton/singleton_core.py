"""
singleton_core.py - Core Singleton Implementation Module
Version: 2025.09.24.09
Description: Internal core implementation for singleton management operations

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Provides core singleton implementation logic
- Thread-safe singleton access patterns
- Memory-optimized singleton management
- Emergency mode and health monitoring

PRIMARY FILE: singleton.py (interface)
SECONDARY FILE: singleton_core.py (implementation)
"""

import logging
import threading
import weakref
import time
import gc
from typing import Dict, Any, Optional, Union, Callable
from enum import Enum

logger = logging.getLogger(__name__)

# ===== CORE SINGLETON STORAGE =====

class SingletonRegistry:
    """Thread-safe singleton registry with memory optimization."""
    
    def __init__(self):
        self._instances = {}
        self._factories = {}
        self._lock = threading.RLock()
        self._creation_times = {}
        self._access_counts = {}
        
    def get_instance(self, singleton_type: str, factory: Callable = None, mode: str = "basic", **kwargs):
        """Get or create singleton instance."""
        with self._lock:
            if singleton_type not in self._instances:
                if factory:
                    self._factories[singleton_type] = factory
                    instance = factory(**kwargs)
                else:
                    # Default factory patterns
                    instance = self._create_default_instance(singleton_type, **kwargs)
                    
                self._instances[singleton_type] = instance
                self._creation_times[singleton_type] = time.time()
                self._access_counts[singleton_type] = 0
                
            self._access_counts[singleton_type] += 1
            return self._instances[singleton_type]
    
    def _create_default_instance(self, singleton_type: str, **kwargs):
        """Create default instance based on type."""
        # Import here to avoid circular imports
        if singleton_type == "cost_protection":
            from utility_core import CostProtectionManager
            return CostProtectionManager()
        elif singleton_type == "cache_manager":
            from utility_core import CacheManager
            return CacheManager()
        elif singleton_type == "security_validator":
            from security_core import SecurityValidator
            return SecurityValidator()
        elif singleton_type == "config_manager":
            from initialization_core import ConfigManager
            return ConfigManager()
        else:
            # Generic singleton
            return type(f'Singleton_{singleton_type}', (), {})()
    
    def remove_instance(self, singleton_type: str) -> bool:
        """Remove singleton instance."""
        with self._lock:
            if singleton_type in self._instances:
                del self._instances[singleton_type]
                self._factories.pop(singleton_type, None)
                self._creation_times.pop(singleton_type, None)
                self._access_counts.pop(singleton_type, None)
                return True
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        with self._lock:
            return {
                'total_singletons': len(self._instances),
                'instances': list(self._instances.keys()),
                'creation_times': self._creation_times.copy(),
                'access_counts': self._access_counts.copy(),
                'memory_usage_estimate': len(self._instances) * 1024  # Rough estimate
            }
    
    def cleanup(self, target_id: str = None) -> Dict[str, Any]:
        """Cleanup singletons."""
        with self._lock:
            if target_id:
                removed = self.remove_instance(target_id)
                return {'cleanup_target': target_id, 'removed': removed}
            else:
                # Cleanup all
                count = len(self._instances)
                self._instances.clear()
                self._factories.clear()
                self._creation_times.clear()
                self._access_counts.clear()
                gc.collect()
                return {'cleanup_all': True, 'removed_count': count}

# Global registry instance
_registry = SingletonRegistry()

# ===== CORE IMPLEMENTATION FUNCTIONS =====

def _get_singleton_implementation(singleton_type: Union[str, Enum], 
                                mode: Union[str, Enum] = "basic",
                                factory: Callable = None,
                                **kwargs) -> Any:
    """Core singleton access implementation."""
    try:
        # Convert enum to string if needed
        if hasattr(singleton_type, 'value'):
            singleton_type = singleton_type.value
        if hasattr(mode, 'value'):
            mode = mode.value
            
        # Get instance from registry
        return _registry.get_instance(singleton_type, factory, mode, **kwargs)
        
    except Exception as e:
        logger.error(f"Singleton access failed for {singleton_type}: {e}")
        # Return basic object for emergency mode
        return type(f'Emergency_{singleton_type}', (), {})()

def _manage_singletons_implementation(operation: Union[str, Enum], 
                                    target_id: str = None,
                                    **kwargs) -> Dict[str, Any]:
    """Core singleton management implementation."""
    try:
        # Convert enum to string if needed
        if hasattr(operation, 'value'):
            operation = operation.value
            
        if operation == "status":
            return _registry.get_status()
        elif operation == "cleanup":
            return _registry.cleanup(target_id)
        elif operation == "reset":
            return _registry.cleanup(target_id)  # Reset is same as cleanup
        elif operation == "optimize":
            # Force garbage collection
            gc.collect()
            status = _registry.get_status()
            status['optimization_performed'] = True
            return status
        else:
            return {'error': f'Unknown operation: {operation}'}
            
    except Exception as e:
        logger.error(f"Singleton management failed: {e}")
        return {'error': str(e), 'operation': operation}

def _singleton_health_check_implementation() -> Dict[str, Any]:
    """Core singleton health check implementation."""
    try:
        start_time = time.time()
        status = _registry.get_status()
        
        # Basic health metrics
        health_data = {
            'status': 'healthy',
            'total_singletons': status['total_singletons'],
            'active_instances': status['instances'],
            'check_duration_ms': (time.time() - start_time) * 1000,
            'memory_estimate_kb': status['memory_usage_estimate'] // 1024,
            'timestamp': time.time()
        }
        
        # Check for potential issues
        if status['total_singletons'] > 50:
            health_data['warnings'] = ['High singleton count - consider cleanup']
        
        if status['memory_usage_estimate'] > 10 * 1024 * 1024:  # 10MB
            health_data['warnings'] = health_data.get('warnings', [])
            health_data['warnings'].append('High memory usage estimate')
            
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }

# ===== THREAD SAFETY IMPLEMENTATION =====

def _validate_thread_safety_implementation() -> bool:
    """Validate thread safety status."""
    try:
        # Check if registry lock is available
        acquired = _registry._lock.acquire(timeout=1.0)
        if acquired:
            _registry._lock.release()
            return True
        return False
    except Exception:
        return False

def _get_thread_safety_status_implementation() -> Dict[str, Any]:
    """Get thread safety status."""
    return {
        'thread_safe': _validate_thread_safety_implementation(),
        'lock_type': 'RLock',
        'registry_locked': not _registry._lock.acquire(blocking=False)
    }

def _execute_with_timeout_implementation(operation: Callable, timeout: float = 30.0, **kwargs) -> Any:
    """Execute operation with timeout."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout}s")
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(timeout))
    
    try:
        result = operation(**kwargs)
        signal.alarm(0)
        return result
    except TimeoutError:
        logger.warning(f"Operation timed out: {operation}")
        raise
    finally:
        signal.signal(signal.SIGALRM, old_handler)

def _coordinate_operation_implementation(operation: Callable, **kwargs) -> Any:
    """Coordinate thread-safe operation."""
    with _registry._lock:
        return operation(**kwargs)

def _get_thread_coordinator_implementation():
    """Get thread coordinator."""
    return _registry._lock

def _get_thread_statistics_implementation() -> Dict[str, Any]:
    """Get thread statistics."""
    return {
        'active_threads': threading.active_count(),
        'current_thread': threading.current_thread().name,
        'registry_lock_acquired': not _registry._lock.acquire(blocking=False)
    }

def _check_lock_contention_implementation() -> Dict[str, Any]:
    """Check lock contention status."""
    acquired = _registry._lock.acquire(blocking=False)
    if acquired:
        _registry._lock.release()
        contention = False
    else:
        contention = True
        
    return {
        'lock_contention_detected': contention,
        'lock_available': not contention,
        'check_timestamp': time.time()
    }

# EOF
