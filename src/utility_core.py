"""
utility_core.py - Core Utility Implementation (Internal)
Version: 2025.10.16.04
Description: SharedUtilityCore class with data operations, validation, and performance

SUGA-ISP: Internal module - only accessed via interface_utility.py

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import time
import uuid
import threading
import traceback
from typing import Dict, Any, Optional, List
import logging as stdlib_logging

from utility_types import UtilityMetrics, DEFAULT_MAX_JSON_CACHE_SIZE

logger = stdlib_logging.getLogger(__name__)


# ===== CONSOLIDATED UTILITY CORE =====

class SharedUtilityCore:
    """
    Core utility manager with data operations, validation, and performance tracking.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = {}
        self._cache_enabled = True
        self._cache_ttl = 300
        self._id_pool = []
        self._json_cache = {}
        self._json_cache_order = []
        self._stats = {
            'template_hits': 0,
            'template_fallbacks': 0,
            'cache_optimizations': 0,
            'id_pool_reuse': 0,
            'lugs_integrations': 0
        }
    
    # ===== TRACKING =====
    
    def _start_operation_tracking(self, operation_type: str):
        """Start tracking an operation."""
        with self._lock:
            if operation_type not in self._metrics:
                self._metrics[operation_type] = UtilityMetrics(operation_type=operation_type)
    
    def _complete_operation_tracking(self, operation_type: str, 
                                    duration_ms: float, success: bool = True,
                                    cache_hit: bool = False, used_template: bool = False):
        """Complete tracking for an operation."""
        with self._lock:
            metrics = self._metrics.get(operation_type)
            if not metrics:
                return
            
            metrics.call_count += 1
            
            if success:
                metrics.total_duration_ms += duration_ms
                metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
            else:
                metrics.error_count += 1
            
            if cache_hit:
                metrics.cache_hits += 1
            elif operation_type in ['parse_json', 'parse_json_safely']:
                metrics.cache_misses += 1
            
            if used_template:
                metrics.template_usage += 1
                self._stats['template_hits'] += 1
    
    # ===== UUID AND TIMESTAMP =====
    
    def generate_uuid(self) -> str:
        """Generate UUID with pool optimization and thread safety."""
        with self._lock:
            if self._id_pool:
                self._stats['id_pool_reuse'] += 1
                return self._id_pool.pop()
        
        return str(uuid.uuid4())
    
    def get_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    def generate_correlation_id(self, prefix: Optional[str] = None) -> str:
        """Generate correlation ID with optional prefix."""
        base_id = self.generate_uuid()
        if prefix:
            return f"{prefix}_{base_id}"
        return base_id
    
    # ===== DATA OPERATIONS =====
    
    def parse_json(self, data: str) -> Dict:
        """Parse JSON string."""
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"JSON parse error: {str(e)}")
            return {}
    
    def parse_json_safely(self, json_str: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Parse JSON safely with optional caching and size limits."""
        cache_key = hash(json_str)
        
        if use_cache:
            with self._lock:
                if cache_key in self._json_cache:
                    return self._json_cache[cache_key]
        
        try:
            parsed = json.loads(json_str)
            
            if use_cache:
                with self._lock:
                    if len(self._json_cache) >= DEFAULT_MAX_JSON_CACHE_SIZE:
                        if self._json_cache_order:
                            oldest_key = self._json_cache_order.pop(0)
                            self._json_cache.pop(oldest_key, None)
                    
                    self._json_cache[cache_key] = parsed
                    self._json_cache_order.append(cache_key)
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected parse error: {str(e)}")
            return None
    
    def deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def safe_get(self, dictionary: Dict, key_path: str, default: Any = None) -> Any:
        """Safely get nested dictionary value using dot notation."""
        try:
            keys = key_path.split('.')
            value = dictionary
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                    if value is None:
                        return default
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def format_bytes(self, size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    # ===== VALIDATION =====
    
    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000) -> Dict[str, Any]:
        """Validate string input."""
        if not isinstance(value, str):
            return {"valid": False, "error": "Value must be a string"}
        
        if len(value) < min_length:
            return {"valid": False, "error": f"String too short (min: {min_length})"}
        
        if len(value) > max_length:
            return {"valid": False, "error": f"String too long (max: {max_length})"}
        
        return {"valid": True}
    
    def validate_data_structure(self, data: Any, expected_type: type,
                               required_fields: Optional[List[str]] = None) -> bool:
        """Validate data structure."""
        if not isinstance(data, expected_type):
            return False
        
        if required_fields and isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    return False
        
        return True
    
    def validate_operation_parameters(self, required_params: List[str], 
                                     optional_params: Optional[List[str]] = None,
                                     **kwargs) -> Dict[str, Any]:
        """Generic parameter validation for any interface operation."""
        missing = [param for param in required_params if param not in kwargs]
        
        if missing:
            return {
                "valid": False,
                "missing_params": missing,
                "error": f"Missing required parameters: {', '.join(missing)}"
            }
        
        if optional_params:
            all_params = set(required_params + optional_params)
            unexpected = [k for k in kwargs.keys() if k not in all_params]
            
            if unexpected:
                return {
                    "valid": True,
                    "warning": f"Unexpected parameters: {', '.join(unexpected)}"
                }
        
        return {"valid": True}
    
    # ===== SANITIZATION =====
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data by removing sensitive fields."""
        sensitive_keys = ['password', 'secret', 'token', 'api_key', 'private_key']
        
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def safe_string_conversion(self, data: Any, max_length: int = 10000) -> str:
        """Safely convert data to string with length limits."""
        try:
            result = str(data)
            if len(result) > max_length:
                return result[:max_length] + "... [TRUNCATED]"
            return result
        except Exception:
            return "[conversion_error]"
    
    # ===== UTILITIES =====
    
    def merge_dictionaries(self, *dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple dictionaries safely."""
        try:
            result = {}
            for d in dicts:
                if isinstance(d, dict):
                    result.update(d)
            return result
        except Exception as e:
            logger.error(f"Dictionary merge error: {str(e)}")
            return {}
    
    def extract_error_details(self, error: Exception) -> Dict[str, Any]:
        """Extract detailed error information with stack trace."""
        try:
            return {
                "type": type(error).__name__,
                "message": str(error),
                "args": error.args if hasattr(error, 'args') else [],
                "traceback": traceback.format_exc()
            }
        except Exception:
            return {
                "type": "UnknownError", 
                "message": "Failed to extract error details",
                "traceback": None
            }
    
    def format_data_for_response(self, data: Any, format_type: str = "json",
                                include_metadata: bool = True) -> Dict[str, Any]:
        """Format data for response."""
        formatted = {
            "data": data,
            "format": format_type
        }
        
        if include_metadata:
            formatted["metadata"] = {
                "timestamp": int(time.time()),
                "type": type(data).__name__
            }
        
        return formatted
    
    # ===== PERFORMANCE =====
    
    def cleanup_cache(self, max_age_seconds: int = 3600) -> int:
        """Clean up old cached utility data."""
        try:
            with self._lock:
                cleared = len(self._json_cache)
                self._json_cache.clear()
                self._json_cache_order.clear()
                self._stats['lugs_integrations'] += 1
                return cleared
        except Exception as e:
            logger.error(f"Cache cleanup error: {str(e)}")
            return 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get utility performance statistics."""
        with self._lock:
            operation_stats = {}
            
            for op_type, metrics in self._metrics.items():
                cache_hit_rate = 0.0
                if metrics.cache_hits + metrics.cache_misses > 0:
                    cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
                
                error_rate = 0.0
                if metrics.call_count > 0:
                    error_rate = metrics.error_count / metrics.call_count * 100
                
                template_usage_rate = 0.0
                if metrics.call_count > 0:
                    template_usage_rate = metrics.template_usage / metrics.call_count * 100
                
                operation_stats[op_type] = {
                    "call_count": metrics.call_count,
                    "avg_duration_ms": round(metrics.avg_duration_ms, 2),
                    "cache_hit_rate_percent": round(cache_hit_rate, 2),
                    "error_rate_percent": round(error_rate, 2),
                    "template_usage_percent": round(template_usage_rate, 2),
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses,
                    "error_count": metrics.error_count,
                    "template_usage": metrics.template_usage
                }
            
            return {
                "overall_stats": self._stats,
                "operation_stats": operation_stats,
                "id_pool_size": len(self._id_pool),
                "json_cache_size": len(self._json_cache),
                "json_cache_limit": DEFAULT_MAX_JSON_CACHE_SIZE,
                "cache_enabled": self._cache_enabled,
            }
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize utility performance based on usage patterns."""
        with self._lock:
            optimizations = []
            
            for op_type, metrics in self._metrics.items():
                if metrics.avg_duration_ms > 100:
                    optimizations.append(f"High latency detected for {op_type}")
                
                cache_hit_rate = 0.0
                if metrics.cache_hits + metrics.cache_misses > 0:
                    cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
                
                if cache_hit_rate < 50 and metrics.cache_misses > 10:
                    optimizations.append(f"Low cache hit rate for {op_type}")
            
            if not self._id_pool or len(self._id_pool) < 10:
                for _ in range(20):
                    self._id_pool.append(str(uuid.uuid4()))
                optimizations.append("Replenished ID pool")
            
            if len(self._json_cache) > (DEFAULT_MAX_JSON_CACHE_SIZE * 0.9):
                optimizations.append("JSON cache approaching limit")
            
            return {
                "optimizations_applied": optimizations,
                "timestamp": int(time.time())
            }
    
    def configure_caching(self, enabled: bool, ttl: int = 300) -> bool:
        """Configure utility caching settings."""
        try:
            self._cache_enabled = enabled
            self._cache_ttl = ttl
            return True
        except Exception:
            return False


# ===== MODULE EXPORTS =====

__all__ = [
    'SharedUtilityCore',
]

# EOF
