"""
Fast Path - ZAFP with Template Integration
Version: 2025.10.03.01
Description: Zero-abstraction fast path with template optimization integration

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
import threading
import os
from typing import Dict, Any, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum

_ENABLE_ZAFP_TEMPLATES = os.environ.get('ENABLE_ZAFP_TEMPLATES', 'true').lower() == 'true'

# Template operations for fast path detection
_TEMPLATE_OPERATIONS = {
    'create_success_response',
    'create_error_response',
    'cache_key_generation',
    'metric_dimensions',
    'log_message_formatting',
    'lambda_response_wrapper',
    'http_headers',
    'parse_json'
}

# Pre-compiled common templates for CRITICAL paths
_SUCCESS_TEMPLATE = '{"success":true,"message":"%s","timestamp":%d,"data":%s}'
_ERROR_TEMPLATE = '{"success":false,"error":"%s","timestamp":%d}'
_CACHE_KEY_TEMPLATE = "%s_%s"
_METRIC_DIM_TEMPLATE = '{"operation":"%s","status":"%s"}'


class HotPathLevel(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    CRITICAL = "critical"


@dataclass
class PathMetrics:
    """Metrics for fast path analysis."""
    operation_name: str
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    last_call_time: float = 0.0
    hot_path_level: HotPathLevel = HotPathLevel.COLD
    modules_used: Set[str] = None
    cache_hit_rate: float = 0.0
    template_used: bool = False
    
    def __post_init__(self):
        if self.modules_used is None:
            self.modules_used = set()


class ZAFPTemplateManager:
    """ZAFP manager with template optimization integration."""
    
    def __init__(self):
        self._path_metrics: Dict[str, PathMetrics] = {}
        self._lock = threading.RLock()
        self._template_cache: Dict[str, str] = {}
        self._stats = {
            'fast_path_executions': 0,
            'template_optimized_paths': 0,
            'critical_path_executions': 0,
            'performance_improvements': 0
        }
        
        if _ENABLE_ZAFP_TEMPLATES:
            self._precompute_common_templates()
    
    def _precompute_common_templates(self):
        """Pre-compute most common template results."""
        common_messages = ["Operation successful", "Request completed", "OK"]
        for msg in common_messages:
            key = f"success_{msg}_empty"
            self._template_cache[key] = _SUCCESS_TEMPLATE % (msg, "%d", "{}")
        
        common_errors = ["Invalid request", "Not found", "Timeout"]
        for error in common_errors:
            key = f"error_{error}"
            self._template_cache[key] = _ERROR_TEMPLATE % (error, "%d")
    
    def track_operation(self, operation_name: str, duration_ms: float, 
                       modules_used: Set[str] = None, cache_hit: bool = False,
                       template_used: bool = False):
        """Track operation performance with template awareness."""
        with self._lock:
            if operation_name not in self._path_metrics:
                self._path_metrics[operation_name] = PathMetrics(
                    operation_name=operation_name,
                    modules_used=modules_used or set(),
                    template_used=template_used
                )
            
            metrics = self._path_metrics[operation_name]
            metrics.call_count += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
            metrics.last_call_time = time.time()
            
            if template_used:
                metrics.template_used = True
            
            if cache_hit:
                hits = metrics.cache_hit_rate * (metrics.call_count - 1) + 1
                metrics.cache_hit_rate = hits / metrics.call_count
            else:
                hits = metrics.cache_hit_rate * (metrics.call_count - 1)
                metrics.cache_hit_rate = hits / metrics.call_count
            
            old_level = metrics.hot_path_level
            metrics.hot_path_level = self._analyze_hot_path_level(operation_name, metrics)
            
            if old_level != metrics.hot_path_level:
                if metrics.hot_path_level == HotPathLevel.CRITICAL:
                    self._stats['critical_path_executions'] += 1
    
    def _analyze_hot_path_level(self, operation_name: str, metrics: PathMetrics) -> HotPathLevel:
        """Analyze operation for hot path promotion with template awareness."""
        is_template_op = operation_name in _TEMPLATE_OPERATIONS
        
        if is_template_op and metrics.template_used:
            if metrics.call_count >= 5 and metrics.avg_duration_ms < 10:
                return HotPathLevel.WARM
            elif metrics.call_count >= 15 and metrics.avg_duration_ms < 5:
                return HotPathLevel.HOT
            elif metrics.call_count >= 40:
                return HotPathLevel.CRITICAL
        else:
            if metrics.call_count >= 10 and metrics.avg_duration_ms < 20:
                return HotPathLevel.WARM
            elif metrics.call_count >= 30 and metrics.avg_duration_ms < 10:
                return HotPathLevel.HOT
            elif metrics.call_count >= 100:
                return HotPathLevel.CRITICAL
        
        return HotPathLevel.COLD
    
    def execute_fast_path(self, operation_name: str, *args, **kwargs) -> Any:
        """Execute operation with ZAFP + template optimization."""
        start_time = time.time()
        
        try:
            if operation_name in self._path_metrics:
                metrics = self._path_metrics[operation_name]
                
                if metrics.hot_path_level == HotPathLevel.CRITICAL and _ENABLE_ZAFP_TEMPLATES:
                    result = self._execute_critical_path(operation_name, metrics, *args, **kwargs)
                    self._stats['critical_path_executions'] += 1
                    self._stats['template_optimized_paths'] += 1
                elif metrics.hot_path_level == HotPathLevel.HOT:
                    result = self._execute_hot_path(operation_name, metrics, *args, **kwargs)
                    self._stats['fast_path_executions'] += 1
                else:
                    result = self._execute_regular_path(operation_name, *args, **kwargs)
            else:
                result = self._execute_regular_path(operation_name, *args, **kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if operation_name in self._path_metrics:
                if duration_ms < self._path_metrics[operation_name].avg_duration_ms * 0.8:
                    self._stats['performance_improvements'] += 1
            
            cache_hit = kwargs.get('_cache_hit', False)
            modules_used = kwargs.get('_modules_used', set())
            template_used = kwargs.get('_template_used', False)
            
            self.track_operation(operation_name, duration_ms, modules_used, cache_hit, template_used)
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.track_operation(operation_name, duration_ms, set(), False, False)
            raise e
    
    def _execute_critical_path(self, operation_name: str, metrics: PathMetrics, *args, **kwargs) -> Any:
        """Execute with zero-abstraction template optimization for CRITICAL paths."""
        
        if operation_name == "create_success_response":
            message = args[0] if args else kwargs.get('message', '')
            data = args[1] if len(args) > 1 else kwargs.get('data', {})
            
            timestamp = int(time.time())
            data_json = '{}' if not data else json.dumps(data)
            json_str = _SUCCESS_TEMPLATE % (message, timestamp, data_json)
            return json.loads(json_str)
        
        elif operation_name == "create_error_response":
            message = args[0] if args else kwargs.get('message', '')
            timestamp = int(time.time())
            json_str = _ERROR_TEMPLATE % (message, timestamp)
            return json.loads(json_str)
        
        elif operation_name == "cache_key_generation":
            prefix = args[0] if args else kwargs.get('prefix', '')
            suffix = args[1] if len(args) > 1 else kwargs.get('suffix', '')
            return _CACHE_KEY_TEMPLATE % (prefix, suffix)
        
        elif operation_name == "metric_dimensions":
            operation = args[0] if args else kwargs.get('operation', '')
            status = args[1] if len(args) > 1 else kwargs.get('status', '')
            return json.loads(_METRIC_DIM_TEMPLATE % (operation, status))
        
        return self._execute_hot_path(operation_name, metrics, *args, **kwargs)
    
    def _execute_hot_path(self, operation_name: str, metrics: PathMetrics, *args, **kwargs) -> Any:
        """Execute with hot path optimizations."""
        return self._execute_regular_path(operation_name, *args, **kwargs)
    
    def _execute_regular_path(self, operation_name: str, *args, **kwargs) -> Any:
        """Execute regular path."""
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ZAFP statistics."""
        with self._lock:
            total_ops = sum(m.call_count for m in self._path_metrics.values())
            hot_ops = sum(m.call_count for m in self._path_metrics.values() 
                         if m.hot_path_level in [HotPathLevel.HOT, HotPathLevel.CRITICAL])
            
            return {
                'total_operations': total_ops,
                'tracked_operations': len(self._path_metrics),
                'fast_path_executions': self._stats['fast_path_executions'],
                'critical_path_executions': self._stats['critical_path_executions'],
                'template_optimized_paths': self._stats['template_optimized_paths'],
                'performance_improvements': self._stats['performance_improvements'],
                'hot_operation_percentage': (hot_ops / total_ops * 100) if total_ops > 0 else 0
            }


_MANAGER = ZAFPTemplateManager()


def execute_fast_path(operation_name: str, *args, **kwargs) -> Any:
    """Public interface for fast path execution."""
    return _MANAGER.execute_fast_path(operation_name, *args, **kwargs)


def track_operation_performance(operation_name: str, duration_ms: float, 
                               modules_used: Set[str] = None, cache_hit: bool = False,
                               template_used: bool = False):
    """Public interface for operation tracking."""
    _MANAGER.track_operation(operation_name, duration_ms, modules_used, cache_hit, template_used)


def get_fast_path_stats() -> Dict[str, Any]:
    """Public interface for fast path statistics."""
    return _MANAGER.get_stats()


def enable_fast_path():
    """Enable fast path optimization."""
    global _ENABLE_ZAFP_TEMPLATES
    _ENABLE_ZAFP_TEMPLATES = True


def disable_fast_path():
    """Disable fast path optimization."""
    global _ENABLE_ZAFP_TEMPLATES
    _ENABLE_ZAFP_TEMPLATES = False


__all__ = [
    'HotPathLevel',
    'PathMetrics',
    'execute_fast_path',
    'track_operation_performance',
    'get_fast_path_stats',
    'enable_fast_path',
    'disable_fast_path',
]
