"""
Fast Path - LUGS-Aware Hot Path Protection
Version: 2025.10.03.03
Description: Zero-abstraction fast paths with LUGS module protection

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
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class OperationHeatLevel(Enum):
    """Operation heat levels for LUGS protection."""
    COLD = "cold"           # < 5 calls
    WARM = "warm"           # 5-20 calls
    HOT = "hot"             # 20-100 calls
    CRITICAL = "critical"   # 100+ calls


@dataclass
class OperationMetrics:
    """Metrics for operation heat detection."""
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    last_call_time: float = 0.0
    heat_level: OperationHeatLevel = OperationHeatLevel.COLD
    source_module: Optional[str] = None


class LUGSAwareFastPath:
    """Fast path system with LUGS hot module protection."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._operation_metrics: Dict[str, OperationMetrics] = {}
        self._hot_paths: Dict[str, Callable] = {}
        self._protected_modules: set = set()
        
        self._stats = {
            'total_operations': 0,
            'fast_path_hits': 0,
            'hot_modules_protected': 0,
            'heat_promotions': 0
        }
        
        self._heat_thresholds = {
            OperationHeatLevel.WARM: 5,
            OperationHeatLevel.HOT: 20,
            OperationHeatLevel.CRITICAL: 100
        }
    
    def track_operation(
        self,
        operation_key: str,
        duration_ms: float,
        source_module: Optional[str] = None
    ) -> OperationHeatLevel:
        """Track operation and determine heat level."""
        current_time = time.time()
        
        with self._lock:
            self._stats['total_operations'] += 1
            
            if operation_key not in self._operation_metrics:
                self._operation_metrics[operation_key] = OperationMetrics(
                    source_module=source_module
                )
            
            metrics = self._operation_metrics[operation_key]
            metrics.call_count += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
            metrics.last_call_time = current_time
            
            old_heat = metrics.heat_level
            new_heat = self._calculate_heat_level(metrics.call_count)
            
            if new_heat != old_heat:
                metrics.heat_level = new_heat
                self._stats['heat_promotions'] += 1
                
                if new_heat in [OperationHeatLevel.HOT, OperationHeatLevel.CRITICAL]:
                    self._protect_module(source_module)
            
            return new_heat
    
    def _calculate_heat_level(self, call_count: int) -> OperationHeatLevel:
        """Calculate heat level based on call count."""
        if call_count >= self._heat_thresholds[OperationHeatLevel.CRITICAL]:
            return OperationHeatLevel.CRITICAL
        elif call_count >= self._heat_thresholds[OperationHeatLevel.HOT]:
            return OperationHeatLevel.HOT
        elif call_count >= self._heat_thresholds[OperationHeatLevel.WARM]:
            return OperationHeatLevel.WARM
        else:
            return OperationHeatLevel.COLD
    
    def _protect_module(self, module_name: Optional[str]) -> None:
        """Protect hot module from LUGS unloading."""
        if not module_name:
            return
        
        if module_name in self._protected_modules:
            return
        
        self._protected_modules.add(module_name)
        self._stats['hot_modules_protected'] += 1
        
        try:
            from gateway import mark_module_hot
            mark_module_hot(module_name)
        except ImportError:
            pass
    
    def register_fast_path(
        self,
        operation_key: str,
        fast_func: Callable,
        source_module: Optional[str] = None
    ) -> None:
        """Register a fast path for hot operation."""
        with self._lock:
            self._hot_paths[operation_key] = fast_func
            
            if operation_key not in self._operation_metrics:
                self._operation_metrics[operation_key] = OperationMetrics(
                    heat_level=OperationHeatLevel.HOT,
                    source_module=source_module
                )
            
            if source_module:
                self._protect_module(source_module)
    
    def get_fast_path(self, operation_key: str) -> Optional[Callable]:
        """Get fast path if available."""
        with self._lock:
            if operation_key in self._hot_paths:
                self._stats['fast_path_hits'] += 1
                return self._hot_paths[operation_key]
            return None
    
    def is_hot_operation(self, operation_key: str) -> bool:
        """Check if operation is hot."""
        with self._lock:
            if operation_key not in self._operation_metrics:
                return False
            
            heat = self._operation_metrics[operation_key].heat_level
            return heat in [OperationHeatLevel.HOT, OperationHeatLevel.CRITICAL]
    
    def should_protect_module(self, module_name: str) -> bool:
        """Check if module should be protected from unloading."""
        with self._lock:
            return module_name in self._protected_modules
    
    def get_heat_level(self, operation_key: str) -> OperationHeatLevel:
        """Get operation heat level."""
        with self._lock:
            if operation_key not in self._operation_metrics:
                return OperationHeatLevel.COLD
            return self._operation_metrics[operation_key].heat_level
    
    def get_stats(self) -> Dict[str, Any]:
        """Get fast path statistics."""
        with self._lock:
            stats = self._stats.copy()
            
            heat_counts = {
                OperationHeatLevel.COLD: 0,
                OperationHeatLevel.WARM: 0,
                OperationHeatLevel.HOT: 0,
                OperationHeatLevel.CRITICAL: 0
            }
            
            for metrics in self._operation_metrics.values():
                heat_counts[metrics.heat_level] += 1
            
            stats.update({
                'total_tracked_operations': len(self._operation_metrics),
                'registered_fast_paths': len(self._hot_paths),
                'protected_modules': len(self._protected_modules),
                'cold_operations': heat_counts[OperationHeatLevel.COLD],
                'warm_operations': heat_counts[OperationHeatLevel.WARM],
                'hot_operations': heat_counts[OperationHeatLevel.HOT],
                'critical_operations': heat_counts[OperationHeatLevel.CRITICAL],
                'fast_path_hit_rate': (
                    self._stats['fast_path_hits'] / 
                    max(self._stats['total_operations'], 1) * 100
                ) if self._stats['total_operations'] > 0 else 0
            })
        
        return stats
    
    def get_operation_metrics(self) -> Dict[str, OperationMetrics]:
        """Get all operation metrics."""
        with self._lock:
            return {k: v for k, v in self._operation_metrics.items()}
    
    def optimize(self) -> Dict[str, Any]:
        """Run optimization cycle."""
        optimizations = 0
        current_time = time.time()
        
        with self._lock:
            stale_operations = [
                key for key, metrics in self._operation_metrics.items()
                if current_time - metrics.last_call_time > 300
                and metrics.heat_level == OperationHeatLevel.COLD
            ]
            
            for key in stale_operations:
                del self._operation_metrics[key]
                optimizations += 1
        
        return {
            'optimizations': optimizations,
            'stale_removed': len(stale_operations)
        }


_fast_path_instance = LUGSAwareFastPath()


def track_operation(
    operation_key: str,
    duration_ms: float,
    source_module: Optional[str] = None
) -> OperationHeatLevel:
    """Track operation for heat detection."""
    return _fast_path_instance.track_operation(operation_key, duration_ms, source_module)


def register_fast_path(
    operation_key: str,
    fast_func: Callable,
    source_module: Optional[str] = None
) -> None:
    """Register fast path for operation."""
    _fast_path_instance.register_fast_path(operation_key, fast_func, source_module)


def get_fast_path(operation_key: str) -> Optional[Callable]:
    """Get fast path if available."""
    return _fast_path_instance.get_fast_path(operation_key)


def is_hot_operation(operation_key: str) -> bool:
    """Check if operation is hot."""
    return _fast_path_instance.is_hot_operation(operation_key)


def should_protect_module(module_name: str) -> bool:
    """Check if module should be protected."""
    return _fast_path_instance.should_protect_module(module_name)


def get_heat_level(operation_key: str) -> OperationHeatLevel:
    """Get operation heat level."""
    return _fast_path_instance.get_heat_level(operation_key)


def get_fast_path_stats() -> Dict[str, Any]:
    """Get fast path statistics."""
    return _fast_path_instance.get_stats()


def optimize_fast_path() -> Dict[str, Any]:
    """Run fast path optimization."""
    return _fast_path_instance.optimize()


__all__ = [
    'LUGSAwareFastPath',
    'OperationHeatLevel',
    'track_operation',
    'register_fast_path',
    'get_fast_path',
    'is_hot_operation',
    'should_protect_module',
    'get_heat_level',
    'get_fast_path_stats',
    'optimize_fast_path'
]
