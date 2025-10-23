"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.22.01
Description: System diagnostic operations for debug subsystem

CHANGELOG:
- 2025.10.22.01: Added INITIALIZATION, UTILITY, and SINGLETON diagnostics
  - Added _diagnose_initialization_performance()
  - Added _diagnose_utility_performance()
  - Added _diagnose_singleton_performance()

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

from typing import Dict, Any
import gc
import time


def _diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system health diagnosis."""
    from debug_health import _check_component_health, _check_gateway_health
    
    component_health = _check_component_health()
    gateway_health = _check_gateway_health()
    memory_info = _diagnose_memory()
    
    return {
        'success': True,
        'component_health': component_health,
        'gateway_health': gateway_health,
        'memory': memory_info
    }


def _diagnose_performance(**kwargs) -> Dict[str, Any]:
    """Performance diagnosis."""
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
        
        return {
            'success': True,
            'gateway_operations': gateway_stats.get('operations_count', 0),
            'fast_path_enabled': gateway_stats.get('fast_path_enabled', False),
            'call_counts': gateway_stats.get('call_counts', {})
        }
    except:
        return {'success': False, 'error': 'Could not diagnose performance'}


def _diagnose_memory(**kwargs) -> Dict[str, Any]:
    """Memory usage diagnosis."""
    gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []
    
    return {
        'success': True,
        'objects': len(gc.get_objects()),
        'garbage': len(gc.garbage),
        'collections': gc.get_count()
    }


def _diagnose_initialization_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose INITIALIZATION interface performance patterns.
    
    Analyzes:
    - Initialization status and timing
    - Flag usage patterns
    - Configuration size
    - Rate limiting effectiveness
    
    Returns:
        Performance diagnostics
    """
    try:
        from gateway import initialization_get_status
        
        diagnostics = {
            'interface': 'INITIALIZATION',
            'timestamp': time.time(),
            'metrics': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Get status
        status = initialization_get_status()
        
        # Basic metrics
        diagnostics['metrics']['initialized'] = status.get('initialized', False)
        diagnostics['metrics']['flag_count'] = status.get('flag_count', 0)
        diagnostics['metrics']['config_keys_count'] = len(status.get('config_keys', []))
        diagnostics['metrics']['rate_limited_count'] = status.get('rate_limited_count', 0)
        
        # Timing analysis
        if status.get('init_timestamp'):
            diagnostics['metrics']['init_duration_ms'] = status.get('init_duration_ms', 0)
            diagnostics['metrics']['uptime_seconds'] = status.get('uptime_seconds', 0)
            diagnostics['patterns']['initialized_at'] = status.get('init_timestamp')
        
        # Flag patterns
        flags = status.get('flags', {})
        if flags:
            diagnostics['patterns']['flag_types'] = {
                k: type(v).__name__ for k, v in flags.items()
            }
            diagnostics['patterns']['flag_count'] = len(flags)
        
        # Config patterns
        config_keys = status.get('config_keys', [])
        if config_keys:
            diagnostics['patterns']['config_keys'] = config_keys
            diagnostics['patterns']['config_count'] = len(config_keys)
        
        # Rate limiting analysis
        rate_limited = status.get('rate_limited_count', 0)
        if rate_limited > 0:
            diagnostics['recommendations'].append(
                f"Rate limiting active: {rate_limited} requests blocked. Consider optimizing initialization calls."
            )
        
        # Initialization timing
        init_duration = status.get('init_duration_ms', 0)
        if init_duration > 100:
            diagnostics['recommendations'].append(
                f"Slow initialization: {init_duration:.2f}ms. Review initialization complexity."
            )
        
        # Flag count
        flag_count = status.get('flag_count', 0)
        if flag_count > 50:
            diagnostics['recommendations'].append(
                f"High flag count: {flag_count}. Consider consolidating flags."
            )
        
        return diagnostics
        
    except Exception as e:
        return {
            'interface': 'INITIALIZATION',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def _diagnose_utility_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose UTILITY interface performance patterns."""
    try:
        from gateway import utility_get_performance_stats
        
        diagnostics = {
            'interface': 'UTILITY',
            'timestamp': time.time(),
            'metrics': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Get stats
        stats = utility_get_performance_stats()
        
        # Basic metrics
        diagnostics['metrics']['id_pool_size'] = stats.get('id_pool_size', 0)
        diagnostics['metrics']['json_cache_size'] = stats.get('json_cache_size', 0)
        diagnostics['metrics']['cache_enabled'] = stats.get('cache_enabled', False)
        diagnostics['metrics']['rate_limited_count'] = stats.get('rate_limited_count', 0)
        
        # Operation patterns
        operation_stats = stats.get('operation_stats', {})
        if operation_stats:
            avg_durations = {op: s['avg_duration_ms'] for op, s in operation_stats.items()}
            diagnostics['patterns']['slowest_operation'] = max(avg_durations, key=avg_durations.get) if avg_durations else None
            diagnostics['patterns']['fastest_operation'] = min(avg_durations, key=avg_durations.get) if avg_durations else None
            diagnostics['patterns']['total_operations'] = sum(s['call_count'] for s in operation_stats.values())
        
        # Cache analysis
        json_cache_size = stats.get('json_cache_size', 0)
        json_cache_limit = stats.get('json_cache_limit', 100)
        if json_cache_size > json_cache_limit * 0.8:
            diagnostics['recommendations'].append(
                f"JSON cache near limit: {json_cache_size}/{json_cache_limit}. Consider cleanup."
            )
        
        # Rate limiting analysis
        rate_limited = stats.get('rate_limited_count', 0)
        if rate_limited > 0:
            diagnostics['recommendations'].append(
                f"Rate limiting active: {rate_limited} requests blocked."
            )
        
        # ID pool analysis
        id_pool_size = stats.get('id_pool_size', 0)
        if id_pool_size < 10:
            diagnostics['recommendations'].append(
                f"Low ID pool size: {id_pool_size}. Consider replenishment."
            )
        
        return diagnostics
        
    except Exception as e:
        return {
            'interface': 'UTILITY',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def _diagnose_singleton_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose SINGLETON interface performance patterns.
    
    Analyzes:
    - Singleton count and types
    - Access patterns
    - Memory usage
    - Rate limiting effectiveness
    
    Returns:
        Performance diagnostics
    """
    try:
        from gateway import singleton_get_stats
        
        diagnostics = {
            'interface': 'SINGLETON',
            'timestamp': time.time(),
            'metrics': {},
            'patterns': {},
            'recommendations': []
        }
        
        # Get stats
        stats = singleton_get_stats()
        
        # Basic metrics
        diagnostics['metrics']['total_singletons'] = stats.get('total_singletons', 0)
        diagnostics['metrics']['rate_limited_count'] = stats.get('rate_limited_count', 0)
        diagnostics['metrics']['estimated_memory_mb'] = stats.get('estimated_memory_mb', 0)
        
        # Singleton types breakdown
        singleton_types = stats.get('singleton_types', {})
        diagnostics['metrics']['singleton_types'] = singleton_types
        
        # Access patterns
        access_counts = stats.get('access_counts', {})
        if access_counts:
            total_accesses = sum(access_counts.values())
            avg_accesses = total_accesses / len(access_counts) if access_counts else 0
            max_accesses = max(access_counts.values()) if access_counts else 0
            min_accesses = min(access_counts.values()) if access_counts else 0
            
            diagnostics['patterns']['total_accesses'] = total_accesses
            diagnostics['patterns']['average_accesses'] = avg_accesses
            diagnostics['patterns']['max_accesses'] = max_accesses
            diagnostics['patterns']['min_accesses'] = min_accesses
            diagnostics['patterns']['most_accessed'] = max(access_counts, key=access_counts.get) if access_counts else None
        
        # Creation times analysis
        creation_times = stats.get('creation_times', {})
        if creation_times:
            current_time = time.time()
            ages = {name: current_time - created for name, created in creation_times.items()}
            diagnostics['patterns']['oldest_singleton'] = max(ages, key=ages.get) if ages else None
            diagnostics['patterns']['newest_singleton'] = min(ages, key=ages.get) if ages else None
            diagnostics['patterns']['average_age_seconds'] = sum(ages.values()) / len(ages) if ages else 0
        
        # Rate limiting analysis
        rate_limited = stats.get('rate_limited_count', 0)
        if rate_limited > 0:
            diagnostics['recommendations'].append(
                f"Rate limiting active: {rate_limited} requests blocked. Consider optimizing access patterns."
            )
        
        # Memory analysis
        memory_mb = stats.get('estimated_memory_mb', 0)
        if memory_mb > 10:
            diagnostics['recommendations'].append(
                f"High memory usage: {memory_mb:.2f} MB. Review singleton lifecycle."
            )
        
        # Count analysis
        count = stats.get('total_singletons', 0)
        if count > 50:
            diagnostics['recommendations'].append(
                f"High singleton count: {count}. Consider consolidating managers."
            )
        
        return diagnostics
        
    except Exception as e:
        return {
            'interface': 'SINGLETON',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_initialization_performance',
    '_diagnose_utility_performance',
    '_diagnose_singleton_performance'
]

# EOF
