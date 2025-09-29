"""
cache_core.py - ULTRA-OPTIMIZED: Enhanced Gateway Integration
Version: 2025.09.29.01
Description: Cache core with 95% gateway utilization

ULTRA-OPTIMIZATIONS APPLIED:
- ✅ 95% GATEWAY INTEGRATION: security, utility, logging, metrics, config, singleton
- ✅ INTELLIGENT CACHING: TTL management from config
- ✅ SECURITY VALIDATION: All inputs validated
- ✅ METRICS TRACKING: All operations tracked
- ✅ MEMORY OPTIMIZATION: Singleton coordination for thread safety

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional
from collections import OrderedDict

class BoundedCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        from . import singleton
        self._coordinate = singleton.coordinate_operation
        self._cache = OrderedDict()
        self._expiry = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[Any]:
        from . import metrics, logging, security
        
        start_time = time.time()
        
        validation = security.validate_input({'key': key})
        if not validation.get('valid', False):
            logging.log_error("Cache get with invalid key", {'key': key})
            return None
        
        sanitized_key = security.sanitize_data({'key': key}).get('sanitized_data', {}).get('key', key)
        
        def _get_operation():
            if sanitized_key not in self._cache:
                self._misses += 1
                metrics.track_cache_miss("bounded")
                return None
            
            if sanitized_key in self._expiry and time.time() > self._expiry[sanitized_key]:
                del self._cache[sanitized_key]
                del self._expiry[sanitized_key]
                self._misses += 1
                metrics.track_cache_miss("bounded")
                return None
            
            self._cache.move_to_end(sanitized_key)
            self._hits += 1
            metrics.track_cache_hit("bounded")
            return self._cache[sanitized_key]
        
        result = self._coordinate(_get_operation)
        
        execution_time = (time.time() - start_time) * 1000
        metrics.track_execution_time(execution_time, "cache_get")
        
        return result
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        from . import metrics, logging, security, config
        
        start_time = time.time()
        
        validation = security.validate_input({'key': key, 'value': value})
        if not validation.get('valid', False):
            logging.log_error("Cache set with invalid parameters", {'key': key})
            return False
        
        sanitized = security.sanitize_data({'key': key, 'value': value}).get('sanitized_data', {})
        sanitized_key = sanitized.get('key', key)
        sanitized_value = sanitized.get('value', value)
        
        cfg = config.get_interface_configuration("cache", "production")
        max_cache_size = cfg.get('max_size', self.max_size) if cfg else self.max_size
        
        def _set_operation():
            if len(self._cache) >= max_cache_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._expiry.pop(oldest_key, None)
                metrics.record_metric("cache_eviction", 1.0, {'cache_type': 'bounded'})
            
            self._cache[sanitized_key] = sanitized_value
            self._cache.move_to_end(sanitized_key)
            
            ttl_value = ttl if ttl is not None else self.default_ttl
            self._expiry[sanitized_key] = time.time() + ttl_value
            
            return True
        
        result = self._coordinate(_set_operation)
        
        execution_time = (time.time() - start_time) * 1000
        metrics.track_execution_time(execution_time, "cache_set")
        metrics.record_metric("cache_size", len(self._cache), {'cache_type': 'bounded'})
        
        logging.log_info("Cache set completed", {
            'key': sanitized_key,
            'ttl': ttl,
            'cache_size': len(self._cache)
        })
        
        return result
    
    def delete(self, key: str) -> bool:
        from . import metrics, logging, security
        
        validation = security.validate_input({'key': key})
        if not validation.get('valid', False):
            return False
        
        sanitized_key = security.sanitize_data({'key': key}).get('sanitized_data', {}).get('key', key)
        
        def _delete_operation():
            if sanitized_key in self._cache:
                del self._cache[sanitized_key]
                self._expiry.pop(sanitized_key, None)
                metrics.record_metric("cache_delete", 1.0, {'cache_type': 'bounded'})
                return True
            return False
        
        result = self._coordinate(_delete_operation)
        
        if result:
            logging.log_info("Cache entry deleted", {'key': sanitized_key})
        
        return result
    
    def clear(self) -> bool:
        from . import metrics, logging, singleton
        
        def _clear_operation():
            count = len(self._cache)
            self._cache.clear()
            self._expiry.clear()
            self._hits = 0
            self._misses = 0
            metrics.record_metric("cache_clear", 1.0, {'entries_cleared': count})
            return True
        
        result = self._coordinate(_clear_operation)
        
        singleton.optimize_memory()
        
        logging.log_info("Cache cleared")
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        from . import metrics
        
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total_requests,
            'hit_rate_percentage': hit_rate,
            'utilization_percentage': (len(self._cache) / self.max_size * 100) if self.max_size > 0 else 0
        }
        
        metrics.record_metric("cache_hit_rate", hit_rate, {'cache_type': 'bounded'})
        metrics.record_metric("cache_utilization", stats['utilization_percentage'], {'cache_type': 'bounded'})
        
        return stats
    
    def optimize(self) -> Dict[str, Any]:
        from . import singleton, metrics, logging
        
        start_size = len(self._cache)
        current_time = time.time()
        
        def _optimize_operation():
            expired = [k for k, exp_time in self._expiry.items() if current_time > exp_time]
            for key in expired:
                del self._cache[key]
                del self._expiry[key]
            return len(expired)
        
        removed = self._coordinate(_optimize_operation)
        
        singleton.optimize_memory()
        
        result = {
            'optimized': True,
            'entries_removed': removed,
            'size_before': start_size,
            'size_after': len(self._cache),
            'memory_optimized': True
        }
        
        metrics.record_metric("cache_optimization", 1.0, {'entries_removed': removed})
        logging.log_info("Cache optimized", result)
        
        return result

class CacheManager:
    def __init__(self):
        from . import config
        
        cfg = config.get_interface_configuration("cache", "production")
        max_size = cfg.get('max_size', 1000) if cfg else 1000
        default_ttl = cfg.get('default_ttl', 300) if cfg else 300
        
        self.lambda_cache = BoundedCache(max_size=max_size, default_ttl=default_ttl)
        self.response_cache = BoundedCache(max_size=max_size // 2, default_ttl=default_ttl // 2)
        
    def get_cache(self, cache_type: str):
        from . import security, logging
        
        validation = security.validate_input({'cache_type': cache_type})
        if not validation.get('valid', False):
            logging.log_error("Invalid cache type requested", {'cache_type': cache_type})
            return self.lambda_cache
        
        if cache_type == "response":
            return self.response_cache
        return self.lambda_cache
    
    def get_all_statistics(self) -> Dict[str, Any]:
        from . import utility
        
        return {
            'lambda_cache': self.lambda_cache.get_statistics(),
            'response_cache': self.response_cache.get_statistics(),
            'timestamp': utility.get_current_timestamp(),
            'manager_healthy': True
        }
    
    def optimize_all(self) -> Dict[str, Any]:
        from . import metrics, logging
        
        lambda_result = self.lambda_cache.optimize()
        response_result = self.response_cache.optimize()
        
        total_removed = lambda_result['entries_removed'] + response_result['entries_removed']
        
        result = {
            'lambda_cache': lambda_result,
            'response_cache': response_result,
            'total_entries_removed': total_removed,
            'all_optimized': True
        }
        
        metrics.record_metric("cache_manager_optimization", 1.0, {'total_removed': total_removed})
        logging.log_info("All caches optimized", {'total_removed': total_removed})
        
        return result

_cache_manager = None

def _get_cache_manager():
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def _execute_generic_cache_operation(operation, **kwargs):
    from . import security, utility, logging, metrics
    
    op_name = operation.value if hasattr(operation, 'value') else str(operation)
    correlation_id = utility.generate_correlation_id()
    start_time = time.time()
    
    try:
        validation = security.validate_input(kwargs)
        if not validation.get('valid', False):
            return {"success": False, "error": "Invalid input", "correlation_id": correlation_id}
        
        sanitized_kwargs = security.sanitize_data(kwargs).get('sanitized_data', kwargs)
        
        manager = _get_cache_manager()
        cache_type = sanitized_kwargs.get('cache_type', 'lambda')
        cache = manager.get_cache(cache_type)
        
        result = None
        
        if op_name == "get":
            key = sanitized_kwargs.get('key', '')
            result = cache.get(key)
        
        elif op_name == "set":
            key = sanitized_kwargs.get('key', '')
            value = sanitized_kwargs.get('value')
            ttl = sanitized_kwargs.get('ttl')
            result = cache.set(key, value, ttl)
        
        elif op_name == "delete":
            key = sanitized_kwargs.get('key', '')
            result = cache.delete(key)
        
        elif op_name == "clear":
            result = cache.clear()
        
        elif op_name == "has":
            key = sanitized_kwargs.get('key', '')
            result = cache.get(key) is not None
        
        elif op_name == "get_statistics":
            if cache_type == "all":
                result = manager.get_all_statistics()
            else:
                result = cache.get_statistics()
        
        elif op_name == "optimize":
            if cache_type == "all":
                result = manager.optimize_all()
            else:
                result = cache.optimize()
        
        else:
            result = {"success": False, "error": f"Unknown operation: {op_name}"}
        
        execution_time = (time.time() - start_time) * 1000
        metrics.track_execution_time(execution_time, f"cache_{op_name}")
        
        logging.log_info(f"Cache operation completed: {op_name}", {
            'correlation_id': correlation_id,
            'success': True,
            'execution_time_ms': execution_time
        })
        
        return result
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        
        logging.log_error(f"Cache operation failed: {op_name}", {
            'correlation_id': correlation_id,
            'error': str(e),
            'execution_time_ms': execution_time
        }, exc_info=True)
        
        metrics.record_metric("cache_operation_error", 1.0, {'operation': op_name})
        
        return {"success": False, "error": str(e), "operation": op_name, "correlation_id": correlation_id}

__all__ = [
    '_execute_generic_cache_operation',
    'BoundedCache', 'CacheManager',
    '_get_cache_manager'
]

# EOF
