"""
utility_core.py - Core Utility Implementation
Version: 3.0.0
Date: 2025-12-02
Description: Core utility with template rendering and typed config

ADDED: render_template_impl - Template {placeholder} substitution with auto correlation ID
ADDED: config_get_impl - Typed config from environment with conversions

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import time
import uuid
import traceback
import os
from typing import Dict, Any, Optional, List
from collections import deque
import logging as stdlib_logging

from utility_types import UtilityMetrics, DEFAULT_MAX_JSON_CACHE_SIZE

logger = stdlib_logging.getLogger(__name__)


class SharedUtilityCore:
    """Core utility manager with SINGLETON pattern."""
    
    def __init__(self):
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
            'lugs_integrations': 0,
            'templates_rendered': 0,
            'configs_retrieved': 0
        }
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check rate limit (1000 ops/sec)."""
        now = time.time() * 1000
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        self._rate_limiter.append(now)
        return True
    
    def _start_operation_tracking(self, operation_type: str):
        """Start tracking operation."""
        if operation_type not in self._metrics:
            self._metrics[operation_type] = UtilityMetrics()
        self._metrics[operation_type].calls += 1
        return time.time()
    
    def _end_operation_tracking(self, operation_type: str, start_time: float, success: bool = True):
        """End tracking operation."""
        duration = time.time() - start_time
        if operation_type in self._metrics:
            metric = self._metrics[operation_type]
            metric.total_time += duration
            metric.last_call = start_time
            if success:
                metric.successes += 1
            else:
                metric.failures += 1
    
    # ADDED: Template rendering
    def render_template_impl(self, template: dict, data: dict, **kwargs) -> dict:
        """
        Render template with {placeholder} substitution.
        
        Features:
        - Replaces {key} with data[key]
        - Auto-injects correlation ID if not provided
        - Handles nested dicts/lists
        - Automatic logging via increment
        
        Args:
            template: JSON template with {placeholders}
            data: Data for substitution
            
        Returns:
            Rendered response dict
        """
        start_time = self._start_operation_tracking('render_template')
        
        try:
            # Auto-inject correlation ID
            if 'message_id' not in data:
                data['message_id'] = self.generate_correlation_id()
            
            # Convert template to string for substitution
            template_str = json.dumps(template)
            
            # Substitute placeholders
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                placeholder = f'{{{key}}}'
                template_str = template_str.replace(placeholder, str(value))
            
            # Parse back to dict
            result = json.loads(template_str)
            
            self._stats['templates_rendered'] += 1
            self._end_operation_tracking('render_template', start_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Template render failed: {e}")
            self._end_operation_tracking('render_template', start_time, False)
            raise
    
    # ADDED: Typed configuration
    def config_get_impl(self, key: str, default=None, **kwargs) -> Any:
        """
        Get typed configuration from environment.
        
        Args:
            key: Environment variable name
            default: Default value (determines type conversion)
            
        Returns:
            Typed configuration value
        """
        start_time = self._start_operation_tracking('config_get')
        
        try:
            value = os.getenv(key)
            
            if value is None:
                self._end_operation_tracking('config_get', start_time, True)
                return default
            
            # Type conversion based on default
            if default is None:
                result = value
            elif isinstance(default, bool):
                result = value.lower() in ('true', '1', 'yes')
            elif isinstance(default, int):
                result = int(value)
            elif isinstance(default, float):
                result = float(value)
            else:
                result = value
            
            self._stats['configs_retrieved'] += 1
            self._end_operation_tracking('config_get', start_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"Config get failed for {key}: {e}")
            self._end_operation_tracking('config_get', start_time, False)
            return default
    
    def generate_uuid(self) -> str:
        """Generate UUID."""
        start_time = self._start_operation_tracking('generate_uuid')
        try:
            if self._id_pool:
                self._stats['id_pool_reuse'] += 1
                result = self._id_pool.pop()
            else:
                result = str(uuid.uuid4())
            self._end_operation_tracking('generate_uuid', start_time, True)
            return result
        except Exception as e:
            self._end_operation_tracking('generate_uuid', start_time, False)
            raise
    
    def get_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()
    
    def generate_correlation_id(self, prefix: Optional[str] = None) -> str:
        """Generate correlation ID."""
        base_id = str(uuid.uuid4())[:8]
        return f"{prefix}-{base_id}" if prefix else base_id
    
    def format_bytes(self, size: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def parse_json_safely(self, json_str: str, use_cache: bool = True) -> Optional[Dict]:
        """Parse JSON with caching."""
        if use_cache and json_str in self._json_cache:
            return self._json_cache[json_str]
        
        try:
            result = json.loads(json_str)
            if use_cache:
                if len(self._json_cache) >= DEFAULT_MAX_JSON_CACHE_SIZE:
                    oldest = self._json_cache_order.pop(0)
                    del self._json_cache[oldest]
                self._json_cache[json_str] = result
                self._json_cache_order.append(json_str)
            return result
        except Exception:
            return None
    
    def safe_get(self, dictionary: Dict, key_path: str, default: Any = None) -> Any:
        """Safely get nested dictionary value."""
        keys = key_path.split('.')
        current = dictionary
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
    
    def validate_data_structure(self, data: Any, expected_type: type, required_fields: Optional[List[str]] = None) -> bool:
        """Validate data structure."""
        if not isinstance(data, expected_type):
            return False
        if required_fields and isinstance(data, dict):
            return all(field in data for field in required_fields)
        return True
    
    def format_data_for_response(self, data: Any, format_type: str = "json", include_metadata: bool = True) -> Dict:
        """Format data for response."""
        formatted = {"data": data, "format": format_type}
        if include_metadata:
            formatted["metadata"] = {"timestamp": int(time.time()), "type": type(data).__name__}
        return formatted
    
    def cleanup_cache(self, max_age_seconds: int = 3600) -> int:
        """Cleanup old cached data."""
        initial_size = len(self._json_cache)
        self._json_cache.clear()
        self._json_cache_order.clear()
        return initial_size
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        for operation, metric in self._metrics.items():
            stats[operation] = {
                'calls': metric.calls,
                'successes': metric.successes,
                'failures': metric.failures,
                'total_time': metric.total_time,
                'avg_time': metric.total_time / metric.calls if metric.calls > 0 else 0,
                'last_call': metric.last_call
            }
        stats['custom_stats'] = self._stats.copy()
        stats['rate_limited_count'] = self._rate_limited_count
        return stats
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize performance."""
        return {'optimizations_applied': 0, 'improvements': []}
    
    def configure_caching(self, enabled: bool, ttl: int = 300) -> None:
        """Configure caching."""
        self._cache_enabled = enabled
        self._cache_ttl = ttl
    
    def safe_string_conversion(self, data: Any, max_length: int = 10000) -> str:
        """Safely convert to string."""
        try:
            result = str(data)
            return result[:max_length] + "... [TRUNCATED]" if len(result) > max_length else result
        except Exception:
            return "[conversion_error]"
    
    def merge_dictionaries(self, *dicts: Dict) -> Dict:
        """Merge multiple dictionaries."""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result
    
    def extract_error_details(self, error: Exception) -> Dict[str, Any]:
        """Extract error details."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "args": error.args if hasattr(error, 'args') else [],
            "traceback": traceback.format_exc()
        }
    
    def validate_operation_parameters(self, params: Dict, required: List[str]) -> bool:
        """Validate operation parameters."""
        return all(param in params for param in required)
    
    def sanitize_data(self, data: Any) -> Any:
        """Sanitize sensitive data."""
        if not isinstance(data, dict):
            return data
        sensitive_keys = ['password', 'secret', 'token', 'api_key', 'private_key']
        sanitized = {}
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_data(value)
            else:
                sanitized[key] = value
        return sanitized


_UTILITY_MANAGER_INSTANCE = None

def get_utility_manager() -> SharedUtilityCore:
    """Get singleton utility manager."""
    global _UTILITY_MANAGER_INSTANCE
    if _UTILITY_MANAGER_INSTANCE is None:
        _UTILITY_MANAGER_INSTANCE = SharedUtilityCore()
    return _UTILITY_MANAGER_INSTANCE


# ADDED: Template rendering implementation
def render_template_impl(template: dict, data: dict, **kwargs) -> dict:
    """Render template (routes to manager)."""
    manager = get_utility_manager()
    return manager.render_template_impl(template, data, **kwargs)


# ADDED: Config get implementation
def config_get_impl(key: str, default=None, **kwargs) -> Any:
    """Get typed config (routes to manager)."""
    manager = get_utility_manager()
    return manager.config_get_impl(key, default, **kwargs)


__all__ = [
    'get_utility_manager',
    'render_template_impl',
    'config_get_impl',
]
