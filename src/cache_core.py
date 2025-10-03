"""
Cache Core - Template Optimized with Generic Operations
Version: 2025.10.03.01
Description: Cache management with template-based key generation and generic operations

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

import time
import threading
import os
from typing import Dict, Any, Optional, Set
from enum import Enum
from collections import defaultdict

# Cache key templates for ultra-fast generation
_HA_HEALTH_KEY = "ha_health_%s"
_HA_STATS_KEY = "ha_stats_%s"
_HA_CONFIG_KEY = "ha_config_%s"
_JSON_PARSE_KEY = "json_parse_%s"
_CONFIG_KEY = "config_%s_%s"
_METRIC_KEY = "metric_%s_%s"
_RESPONSE_KEY = "response_%s_%s"
_SESSION_KEY = "session_%s"
_USER_KEY = "user_%s"
_LAMBDA_CACHE_KEY = "lambda_%s_%s"
_OPERATION_KEY = "operation_%s_%s"

_USE_CACHE_TEMPLATES = os.environ.get('USE_CACHE_TEMPLATES', 'true').lower() == 'true'


class CacheOperation(Enum):
    """Generic cache operations."""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    CLEAR = "clear"
    EXISTS = "exists"
    GET_TTL = "get_ttl"
    SET_TTL = "set_ttl"
    GET_STATS = "get_stats"
    CLEANUP = "cleanup"


class CacheKeyType(Enum):
    """Cache key type templates."""
    HA_HEALTH = "ha_health"
    HA_STATS = "ha_stats"
    HA_CONFIG = "ha_config"
    JSON_PARSE = "json_parse"
    CONFIG = "config"
    METRIC = "metric"
    RESPONSE = "response"
    SESSION = "session"
    USER = "user"
    LAMBDA = "lambda"
    OPERATION = "operation"
    CUSTOM = "custom"


class CacheCore:
    """Core cache manager with template optimization and generic operations."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self._access_count: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'clears': 0,
            'template_keys': 0
        }
    
    def get_cache_key_fast(self, key_type: CacheKeyType, *args) -> str:
        """Generate cache key using templates for ultra-fast performance."""
        if not _USE_CACHE_TEMPLATES:
            return self._get_cache_key_legacy(key_type, *args)
        
        try:
            if key_type == CacheKeyType.HA_HEALTH:
                return _HA_HEALTH_KEY % args[0] if args else "ha_health_default"
            elif key_type == CacheKeyType.HA_STATS:
                return _HA_STATS_KEY % args[0] if args else "ha_stats_default"
            elif key_type == CacheKeyType.HA_CONFIG:
                return _HA_CONFIG_KEY % args[0] if args else "ha_config_default"
            elif key_type == CacheKeyType.JSON_PARSE:
                return _JSON_PARSE_KEY % hash(args[0]) if args else "json_parse_default"
            elif key_type == CacheKeyType.CONFIG:
                return _CONFIG_KEY % (args[0], args[1]) if len(args) >= 2 else f"config_{args[0] if args else 'default'}"
            elif key_type == CacheKeyType.METRIC:
                return _METRIC_KEY % (args[0], args[1]) if len(args) >= 2 else f"metric_{args[0] if args else 'default'}"
            elif key_type == CacheKeyType.RESPONSE:
                return _RESPONSE_KEY % (args[0], args[1]) if len(args) >= 2 else f"response_{args[0] if args else 'default'}"
            elif key_type == CacheKeyType.SESSION:
                return _SESSION_KEY % args[0] if args else "session_default"
            elif key_type == CacheKeyType.USER:
                return _USER_KEY % args[0] if args else "user_default"
            elif key_type == CacheKeyType.LAMBDA:
                return _LAMBDA_CACHE_KEY % (args[0], args[1]) if len(args) >= 2 else f"lambda_{args[0] if args else 'default'}"
            elif key_type == CacheKeyType.OPERATION:
                return _OPERATION_KEY % (args[0], args[1]) if len(args) >= 2 else f"operation_{args[0] if args else 'default'}"
            else:
                return "_".join(str(arg) for arg in args) if args else "custom_default"
        except Exception:
            return self._get_cache_key_legacy(key_type, *args)
    
    def _get_cache_key_legacy(self, key_type: CacheKeyType, *args) -> str:
        """Legacy cache key generation."""
        parts = [key_type.value]
        parts.extend(str(arg) for arg in args)
        return "_".join(parts)
    
    def execute_cache_operation(self, operation: CacheOperation, *args, **kwargs) -> Any:
        """Generic cache operation executor."""
        if operation == CacheOperation.GET:
            return self.get(args[0] if args else kwargs.get('key'), kwargs.get('default'))
        elif operation == CacheOperation.SET:
            key = args[0] if args else kwargs.get('key')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            ttl = args[2] if len(args) > 2 else kwargs.get('ttl')
            return self.set(key, value, ttl)
        elif operation == CacheOperation.DELETE:
            return self.delete(args[0] if args else kwargs.get('key'))
        elif operation == CacheOperation.CLEAR:
            return self.clear()
        elif operation == CacheOperation.EXISTS:
            return self.exists(args[0] if args else kwargs.get('key'))
        elif operation == CacheOperation.GET_TTL:
            return self.get_ttl(args[0] if args else kwargs.get('key'))
        elif operation == CacheOperation.SET_TTL:
            key = args[0] if args else kwargs.get('key')
            ttl = args[1] if len(args) > 1 else kwargs.get('ttl')
            return self.set_ttl(key, ttl)
        elif operation == CacheOperation.GET_STATS:
            return self.get_stats()
        elif operation == CacheOperation.CLEANUP:
            max_age = args[0] if args else kwargs.get('max_age_seconds', 3600)
            return self.cleanup(max_age)
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                if key in self._ttl:
                    if time.time() > self._ttl[key]:
                        del self._cache[key]
                        del self._ttl[key]
                        self._stats['misses'] += 1
                        return default
                
                self._access_count[key] += 1
                self._stats['hits'] += 1
                return self._cache[key]
            
            self._stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            with self._lock:
                self._cache[key] = value
                if ttl:
                    self._ttl[key] = time.time() + ttl
                self._stats['sets'] += 1
                return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    if key in self._ttl:
                        del self._ttl[key]
                    if key in self._access_count:
                        del self._access_count[key]
                    self._stats['deletes'] += 1
                    return True
                return False
        except Exception:
            return False
    
    def clear(self) -> int:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._ttl.clear()
            self._access_count.clear()
            self._stats['clears'] += 1
            return count
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            if key in self._cache:
                if key in self._ttl:
                    if time.time() > self._ttl[key]:
                        del self._cache[key]
                        del self._ttl[key]
                        return False
                return True
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key."""
        with self._lock:
            if key in self._ttl:
                remaining = int(self._ttl[key] - time.time())
                return remaining if remaining > 0 else None
            return None
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        try:
            with self._lock:
                if key in self._cache:
                    self._ttl[key] = time.time() + ttl
                    return True
                return False
        except Exception:
            return False
    
    def cleanup(self, max_age_seconds: int = 3600) -> int:
        """Clean up expired entries."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, expire_time in self._ttl.items()
                if current_time > expire_time
            ]
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._ttl[key]
                if key in self._access_count:
                    del self._access_count[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'entries': len(self._cache),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate_percent': hit_rate,
                'sets': self._stats['sets'],
                'deletes': self._stats['deletes'],
                'clears': self._stats['clears'],
                'template_keys': self._stats['template_keys']
            }


_MANAGER = CacheCore()


def _execute_get_implementation(key: str, default: Any = None, **kwargs) -> Any:
    """Execute get operation."""
    return _MANAGER.execute_cache_operation(CacheOperation.GET, key, default=default)


def _execute_set_implementation(key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
    """Execute set operation."""
    return _MANAGER.execute_cache_operation(CacheOperation.SET, key, value, ttl=ttl)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Execute delete operation."""
    return _MANAGER.execute_cache_operation(CacheOperation.DELETE, key)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute clear operation."""
    return _MANAGER.execute_cache_operation(CacheOperation.CLEAR)


def get_cache_key_fast(key_type: CacheKeyType, *args) -> str:
    """Public interface for fast cache key generation."""
    return _MANAGER.get_cache_key_fast(key_type, *args)


def get_cache_stats() -> Dict[str, Any]:
    """Public interface for cache statistics."""
    return _MANAGER.get_stats()


__all__ = [
    'CacheOperation',
    'CacheKeyType',
    'get_cache_key_fast',
    'get_cache_stats',
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
]
