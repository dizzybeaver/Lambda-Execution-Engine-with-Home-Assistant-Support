"""
Cache Core - Cache Management with Key Template Optimization
Version: 2025.10.02.01
Description: Cache operations with pre-compiled key templates for performance

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
import json
import hashlib
import os
from typing import Dict, Any, Optional, Union, List
from threading import RLock
from collections import OrderedDict

# ===== CACHE KEY TEMPLATES (Phase 1 Optimization) =====

_HA_HEALTH_KEY = "ha_health_%s"
_HA_STATS_KEY = "ha_stats_%s"
_HA_CONFIG_KEY = "ha_config_%s"
_HA_ENTITY_KEY = "ha_entity_%s"
_HA_STATE_KEY = "ha_state_%s"

_JSON_PARSE_KEY = "json_parse_%d"
_JSON_CACHE_KEY = "json_cache_%s"

_CONFIG_KEY = "config_%s_%s"
_METRIC_KEY = "metric_%s_%d"
_RESPONSE_KEY = "response_%s_%d"
_SESSION_KEY = "session_%s"
_USER_KEY = "user_%s"

_LAMBDA_CACHE_KEY = "lambda_%s_%s"
_OPERATION_KEY = "op_%s_%s_%d"

_KEY_PREFIX_MAP = {}
_CACHE_KEY_CACHE = {}

_USE_CACHE_TEMPLATES = os.environ.get('USE_CACHE_TEMPLATES', 'true').lower() == 'true'

def get_cache_key_fast(prefix: str, suffix: Union[str, int], sub_key: Optional[str] = None) -> str:
    """Fast cache key generation using templates."""
    try:
        if _USE_CACHE_TEMPLATES:
            cache_signature = f"{prefix}_{suffix}_{sub_key}"
            
            if cache_signature in _CACHE_KEY_CACHE:
                return _CACHE_KEY_CACHE[cache_signature]
            
            if prefix == "ha_health":
                key = _HA_HEALTH_KEY % suffix
            elif prefix == "ha_stats":
                key = _HA_STATS_KEY % suffix
            elif prefix == "ha_config":
                key = _HA_CONFIG_KEY % suffix
            elif prefix == "ha_entity":
                key = _HA_ENTITY_KEY % suffix
            elif prefix == "ha_state":
                key = _HA_STATE_KEY % suffix
            elif prefix == "json_parse":
                key = _JSON_PARSE_KEY % hash(str(suffix))
            elif prefix == "json_cache":
                key = _JSON_CACHE_KEY % suffix
            elif prefix == "config" and sub_key:
                key = _CONFIG_KEY % (suffix, sub_key)
            elif prefix == "metric":
                key = _METRIC_KEY % (suffix, int(time.time()))
            elif prefix == "response":
                key = _RESPONSE_KEY % (suffix, hash(str(sub_key)) if sub_key else 0)
            elif prefix == "session":
                key = _SESSION_KEY % suffix
            elif prefix == "user":
                key = _USER_KEY % suffix
            elif prefix == "lambda":
                key = _LAMBDA_CACHE_KEY % (suffix, sub_key or "default")
            elif prefix == "operation":
                key = _OPERATION_KEY % (suffix, sub_key or "default", int(time.time()))
            else:
                key = f"{prefix}_{suffix}_{sub_key}" if sub_key else f"{prefix}_{suffix}"
            
            if len(_CACHE_KEY_CACHE) < 1000:
                _CACHE_KEY_CACHE[cache_signature] = key
            
            return key
        else:
            return f"{prefix}_{suffix}_{sub_key}" if sub_key else f"{prefix}_{suffix}"
            
    except Exception:
        return f"{prefix}_{suffix}_{sub_key}" if sub_key else f"{prefix}_{suffix}"

class CacheCore:
    """Core cache implementation with template optimization."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._metadata = {}
        self._lock = RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0,
            'template_key_usage': 0,
            'legacy_key_usage': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            try:
                if key in self._cache:
                    entry = self._cache[key]
                    metadata = self._metadata.get(key, {})
                    
                    if metadata.get('expires_at', float('inf')) > time.time():
                        self._cache.move_to_end(key)
                        self._stats['hits'] += 1
                        metadata['access_count'] = metadata.get('access_count', 0) + 1
                        metadata['last_accessed'] = time.time()
                        return entry
                    else:
                        del self._cache[key]
                        self._metadata.pop(key, None)
                
                self._stats['misses'] += 1
                return default
                
            except Exception:
                self._stats['misses'] += 1
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        with self._lock:
            try:
                if ttl is None:
                    ttl = self.default_ttl
                
                if len(self._cache) >= self.max_size and key not in self._cache:
                    self._evict_oldest()
                
                self._cache[key] = value
                self._metadata[key] = {
                    'created_at': time.time(),
                    'last_accessed': time.time(),
                    'expires_at': time.time() + ttl,
                    'access_count': 1,
                    'ttl': ttl
                }
                
                self._cache.move_to_end(key)
                self._stats['sets'] += 1
                
                return True
                
            except Exception:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            try:
                if key in self._cache:
                    del self._cache[key]
                    self._metadata.pop(key, None)
                    self._stats['deletes'] += 1
                    return True
                return False
            except Exception:
                return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self._lock:
            try:
                self._cache.clear()
                self._metadata.clear()
                return True
            except Exception:
                return False
    
    def get_ha_health_data(self, suffix: str, default: Any = None) -> Any:
        """Get HA health data using template key."""
        key = get_cache_key_fast("ha_health", suffix)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.get(key, default)
    
    def set_ha_health_data(self, suffix: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set HA health data using template key."""
        key = get_cache_key_fast("ha_health", suffix)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.set(key, value, ttl)
    
    def get_ha_stats_data(self, suffix: str, default: Any = None) -> Any:
        """Get HA stats data using template key."""
        key = get_cache_key_fast("ha_stats", suffix)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.get(key, default)
    
    def set_ha_stats_data(self, suffix: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set HA stats data using template key."""
        key = get_cache_key_fast("ha_stats", suffix)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.set(key, value, ttl)
    
    def get_json_parsed_data(self, json_str: str, default: Any = None) -> Any:
        """Get parsed JSON data using template key."""
        key = get_cache_key_fast("json_parse", json_str)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.get(key, default)
    
    def set_json_parsed_data(self, json_str: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set parsed JSON data using template key."""
        key = get_cache_key_fast("json_parse", json_str)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.set(key, value, ttl)
    
    def get_config_data(self, config_type: str, config_name: str, default: Any = None) -> Any:
        """Get configuration data using template key."""
        key = get_cache_key_fast("config", config_type, config_name)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.get(key, default)
    
    def set_config_data(self, config_type: str, config_name: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set configuration data using template key."""
        key = get_cache_key_fast("config", config_type, config_name)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.set(key, value, ttl)
    
    def get_response_data(self, response_type: str, response_hash: str, default: Any = None) -> Any:
        """Get response data using template key."""
        key = get_cache_key_fast("response", response_type, response_hash)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.get(key, default)
    
    def set_response_data(self, response_type: str, response_hash: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set response data using template key."""
        key = get_cache_key_fast("response", response_type, response_hash)
        if _USE_CACHE_TEMPLATES:
            self._stats['template_key_usage'] += 1
        else:
            self._stats['legacy_key_usage'] += 1
        return self.set(key, value, ttl)
    
    def _evict_oldest(self) -> None:
        """Evict oldest entry."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._metadata.pop(oldest_key, None)
            self._stats['evictions'] += 1
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, metadata in self._metadata.items():
                if metadata.get('expires_at', float('inf')) <= current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                del self._metadata[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_operations = sum([
                self._stats['hits'],
                self._stats['misses'],
                self._stats['sets'],
                self._stats['deletes']
            ])
            
            hit_rate = self._stats['hits'] / max(self._stats['hits'] + self._stats['misses'], 1)
            template_usage_rate = self._stats['template_key_usage'] / max(total_operations, 1)
            
            return {
                'cache_size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'template_usage_rate': template_usage_rate,
                'template_optimization_enabled': _USE_CACHE_TEMPLATES,
                'stats': self._stats.copy(),
                'metadata_count': len(self._metadata)
            }
    
    def get_key_analysis(self) -> Dict[str, Any]:
        """Analyze cache key patterns."""
        with self._lock:
            key_prefixes = {}
            template_keys = 0
            legacy_keys = 0
            
            for key in self._cache.keys():
                if '_' in key:
                    prefix = key.split('_')[0]
                    key_prefixes[prefix] = key_prefixes.get(prefix, 0) + 1
                    
                    if any(template in key for template in [
                        'ha_health', 'ha_stats', 'ha_config', 'json_parse',
                        'config', 'metric', 'response', 'session', 'user'
                    ]):
                        template_keys += 1
                    else:
                        legacy_keys += 1
            
            return {
                'key_prefixes': key_prefixes,
                'template_keys': template_keys,
                'legacy_keys': legacy_keys,
                'total_keys': len(self._cache),
                'template_coverage': template_keys / max(len(self._cache), 1)
            }
