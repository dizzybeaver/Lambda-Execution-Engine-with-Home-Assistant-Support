"""
Debug Core - LUGS Comprehensive Diagnostics
Version: 2025.10.03.03
Description: Real-time monitoring and diagnostics for LUGS system

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
import sys
from typing import Dict, Any, List, Optional


class LUGSDiagnostics:
    """Comprehensive LUGS diagnostics and monitoring."""
    
    def __init__(self):
        self._baseline_memory = self._get_memory_usage_mb()
        self._stats_history: List[Dict[str, Any]] = []
        self._max_history = 100
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except:
            return 0.0
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health."""
        try:
            from gateway import get_lugs_stats
            from cache_core import cache_get_stats
            from fast_path import get_fast_path_stats
            
            lugs_stats = get_lugs_stats()
            cache_stats = cache_get_stats()
            fast_path_stats = get_fast_path_stats()
            
            current_memory = self._get_memory_usage_mb()
            memory_saved = self._baseline_memory - current_memory
            
            health_score = self._calculate_health_score(
                lugs_stats, cache_stats, fast_path_stats
            )
            
            return {
                'timestamp': time.time(),
                'health_score': health_score,
                'status': self._get_status_level(health_score),
                'memory': {
                    'current_mb': current_memory,
                    'baseline_mb': self._baseline_memory,
                    'saved_mb': memory_saved,
                    'utilization_percent': (current_memory / 128) * 100
                },
                'lugs': lugs_stats,
                'cache': cache_stats,
                'fast_path': fast_path_stats,
                'recommendations': self._generate_recommendations(
                    lugs_stats, cache_stats, fast_path_stats, current_memory
                )
            }
        except Exception as e:
            return {
                'timestamp': time.time(),
                'health_score': 0,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _calculate_health_score(
        self,
        lugs_stats: Dict[str, Any],
        cache_stats: Dict[str, Any],
        fast_path_stats: Dict[str, Any]
    ) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        if lugs_stats.get('unload_success_rate', 0) < 80:
            score -= 10
        
        if cache_stats.get('cache_hit_rate', 0) < 70:
            score -= 15
        
        if lugs_stats.get('modules_resident', 0) > 10:
            score -= 10
        
        if lugs_stats.get('emergency_unloads', 0) > 0:
            score -= 20
        
        if fast_path_stats.get('fast_path_hit_rate', 0) < 5:
            score -= 5
        
        return max(0, min(100, score))
    
    def _get_status_level(self, health_score: float) -> str:
        """Get status level from health score."""
        if health_score >= 90:
            return 'EXCELLENT'
        elif health_score >= 75:
            return 'GOOD'
        elif health_score >= 60:
            return 'FAIR'
        elif health_score >= 40:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _generate_recommendations(
        self,
        lugs_stats: Dict[str, Any],
        cache_stats: Dict[str, Any],
        fast_path_stats: Dict[str, Any],
        current_memory: float
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if lugs_stats.get('unload_success_rate', 0) < 80:
            recommendations.append(
                "LUGS unload success rate is low. Check for cache dependencies blocking unloads."
            )
        
        if cache_stats.get('cache_hit_rate', 0) < 70:
            recommendations.append(
                "Cache hit rate is below optimal. Consider increasing cache TTLs for frequently accessed data."
            )
        
        if lugs_stats.get('modules_resident', 0) > 8:
            recommendations.append(
                f"High number of resident modules ({lugs_stats.get('modules_resident')}). "
                "LUGS enforcement may be needed."
            )
        
        if lugs_stats.get('emergency_unloads', 0) > 0:
            recommendations.append(
                "Emergency unloads detected. Memory pressure high. Consider optimization."
            )
        
        if current_memory > 100:
            recommendations.append(
                f"Memory usage ({current_memory:.1f}MB) approaching limit. "
                "Aggressive LUGS optimization recommended."
            )
        
        if fast_path_stats.get('hot_operations', 0) > 0:
            recommendations.append(
                f"Hot operations detected ({fast_path_stats.get('hot_operations')}). "
                "Fast paths protecting critical modules."
            )
        
        if not recommendations:
            recommendations.append("System operating optimally. No action required.")
        
        return recommendations
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time."""
        if len(self._stats_history) < 2:
            return {'status': 'INSUFFICIENT_DATA', 'samples': len(self._stats_history)}
        
        recent = self._stats_history[-10:]
        
        memory_trend = self._calculate_trend([s['memory']['current_mb'] for s in recent])
        cache_trend = self._calculate_trend([s['cache']['cache_hit_rate'] for s in recent])
        
        return {
            'samples': len(recent),
            'time_range_seconds': recent[-1]['timestamp'] - recent[0]['timestamp'],
            'trends': {
                'memory': memory_trend,
                'cache_hit_rate': cache_trend
            },
            'latest_health_score': recent[-1].get('health_score', 0)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return 'STABLE'
        
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff_percent = ((second_half - first_half) / max(first_half, 0.1)) * 100
        
        if diff_percent > 10:
            return 'INCREASING'
        elif diff_percent < -10:
            return 'DECREASING'
        else:
            return 'STABLE'
    
    def record_stats_snapshot(self) -> None:
        """Record current stats snapshot."""
        snapshot = self.get_system_health()
        
        self._stats_history.append(snapshot)
        
        if len(self._stats_history) > self._max_history:
            self._stats_history.pop(0)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        try:
            from gateway import get_lugs_manager
            from cache_core import cache_get_stats
            
            manager = get_lugs_manager()
            cache_stats = cache_get_stats()
            
            current_memory = self._get_memory_usage_mb()
            memory_saved = self._baseline_memory - current_memory
            
            baseline_gb_seconds = (self._baseline_memory / 1000) * 0.18
            current_gb_seconds = (current_memory / 1000) * 0.18
            gb_seconds_saved = baseline_gb_seconds - current_gb_seconds
            
            baseline_capacity = 400000
            optimized_capacity = int(baseline_capacity / (current_gb_seconds / baseline_gb_seconds))
            
            return {
                'timestamp': time.time(),
                'memory_optimization': {
                    'baseline_mb': self._baseline_memory,
                    'current_mb': current_memory,
                    'saved_mb': memory_saved,
                    'reduction_percent': (memory_saved / max(self._baseline_memory, 1)) * 100
                },
                'cost_optimization': {
                    'baseline_gb_seconds': baseline_gb_seconds,
                    'current_gb_seconds': current_gb_seconds,
                    'saved_gb_seconds': gb_seconds_saved,
                    'reduction_percent': (gb_seconds_saved / max(baseline_gb_seconds, 1)) * 100
                },
                'free_tier_impact': {
                    'baseline_capacity': baseline_capacity,
                    'optimized_capacity': optimized_capacity,
                    'capacity_increase_percent': (
                        (optimized_capacity - baseline_capacity) / baseline_capacity * 100
                    )
                },
                'lugs_effectiveness': {
                    'modules_loaded': manager._stats.get('modules_loaded', 0),
                    'modules_unloaded': manager._stats.get('modules_unloaded', 0),
                    'cache_hit_no_load': manager._stats.get('cache_hit_no_load', 0),
                    'unload_success_rate': (
                        manager._stats.get('modules_unloaded', 0) /
                        max(manager._stats.get('modules_loaded', 1), 1) * 100
                    )
                },
                'cache_effectiveness': {
                    'hit_rate': cache_stats.get('cache_hit_rate', 0),
                    'total_hits': cache_stats.get('cache_hits', 0),
                    'total_misses': cache_stats.get('cache_misses', 0)
                }
            }
        except Exception as e:
            return {
                'timestamp': time.time(),
                'error': str(e),
                'status': 'ERROR'
            }


_diagnostics_instance = LUGSDiagnostics()


def get_system_health() -> Dict[str, Any]:
    """Get system health report."""
    return _diagnostics_instance.get_system_health()


def get_performance_trends() -> Dict[str, Any]:
    """Get performance trends."""
    return _diagnostics_instance.get_performance_trends()


def get_optimization_report() -> Dict[str, Any]:
    """Get optimization effectiveness report."""
    return _diagnostics_instance.get_optimization_report()


def record_stats_snapshot() -> None:
    """Record current stats snapshot."""
    _diagnostics_instance.record_stats_snapshot()


__all__ = [
    'LUGSDiagnostics',
    'get_system_health',
    'get_performance_trends',
    'get_optimization_report',
    'record_stats_snapshot'
]
