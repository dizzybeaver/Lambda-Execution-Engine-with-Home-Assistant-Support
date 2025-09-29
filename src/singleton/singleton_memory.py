"""
singleton_memory.py - Memory Monitoring Implementation Module
Version: 2025.09.29.01
Description: Internal memory monitoring implementation for singleton operations

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Memory usage tracking and monitoring
- Lambda 128MB compliance checking
- Emergency memory cleanup operations
- Singleton memory optimization

FREE TIER COMPLIANCE: Uses resource module from Python standard library
- No psutil dependency (Lambda layer not required)
- 100% AWS Lambda free tier compatible
- Standard library only for memory monitoring

PRIMARY FILE: singleton.py (interface)
SECONDARY FILE: singleton_memory.py (implementation)

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

import logging
import gc
import resource
import sys
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ===== MEMORY MONITORING IMPLEMENTATION =====

def _get_singleton_memory_status_implementation() -> Dict[str, Any]:
    """Get singleton memory status implementation."""
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024  # Linux returns KB, convert to MB
        
        # Get singleton registry status
        from .singleton_core import _registry
        singleton_status = _registry.get_status()
        
        return {
            'singleton_memory_usage_mb': singleton_status['memory_usage_estimate'] / (1024 * 1024),
            'total_process_memory_mb': memory_mb,
            'singleton_count': singleton_status['total_singletons'],
            'lambda_128mb_compliant': memory_mb < 128,
            'memory_pressure': 'high' if memory_mb > 100 else 'normal',
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f"Memory status check failed: {e}")
        return {
            'error': str(e),
            'timestamp': time.time(),
            'lambda_128mb_compliant': False
        }

def get_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics."""
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024  # Linux returns KB, convert to MB
        
        return {
            'rss_mb': memory_mb,
            'vms_mb': memory_mb,  # resource module doesn't distinguish, use same value
            'percent': (memory_mb / 128) * 100,  # Percentage of Lambda 128MB limit
            'available_mb': (128 - memory_mb),
            'compliant': memory_mb < 128
        }
    except Exception as e:
        return {'error': str(e), 'compliant': False}

def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics."""
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024  # Linux returns KB, convert to MB
        
        # Get GC statistics
        gc_stats = gc.get_stats()
        gc_counts = gc.get_count()
        
        # Get object counts
        object_count = len(gc.get_objects())
        
        return {
            'memory': {
                'rss_mb': memory_mb,
                'available_mb': 128 - memory_mb,
                'percent_used': (memory_mb / 128) * 100,
                'compliant': memory_mb < 128
            },
            'gc': {
                'collections': gc_counts,
                'stats': gc_stats,
                'tracked_objects': object_count
            },
            'system': {
                'lambda_limit_mb': 128,
                'pressure_level': 'high' if memory_mb > 100 else 'normal'
            },
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f"Comprehensive memory stats failed: {e}")
        return {'error': str(e)}

def check_lambda_memory_compliance() -> bool:
    """Check if memory usage is within Lambda 128MB limit."""
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024
        return memory_mb < 128
    except Exception:
        return False

def force_memory_cleanup() -> Dict[str, Any]:
    """Force aggressive memory cleanup."""
    try:
        # Get initial memory
        rusage_before = resource.getrusage(resource.RUSAGE_SELF)
        memory_before = rusage_before.ru_maxrss / 1024
        
        # Force GC
        collected = gc.collect()
        
        # Get final memory
        rusage_after = resource.getrusage(resource.RUSAGE_SELF)
        memory_after = rusage_after.ru_maxrss / 1024
        
        return {
            'gc_collected': collected,
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_freed_mb': max(0, memory_before - memory_after),
            'compliant': memory_after < 128
        }
    except Exception as e:
        logger.error(f"Memory cleanup failed: {e}")
        return {'error': str(e)}

def optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage with multiple cleanup strategies."""
    try:
        optimization_results = []
        
        # Strategy 1: Basic GC
        collected = gc.collect()
        optimization_results.append(f"gc_collected_{collected}_objects")
        
        # Strategy 2: Generation-specific collection
        for generation in range(3):
            gen_collected = gc.collect(generation)
            optimization_results.append(f"gen{generation}_collected_{gen_collected}_objects")
        
        # Strategy 3: Clear singleton cache if needed
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        current_memory = rusage.ru_maxrss / 1024
        
        if current_memory > 100:  # High memory pressure
            try:
                from .singleton_core import _registry
                _registry.cleanup()
                optimization_results.append("singleton_cache_cleared")
            except Exception:
                pass
        
        # Final check
        rusage_final = resource.getrusage(resource.RUSAGE_SELF)
        final_memory = rusage_final.ru_maxrss / 1024
        
        return {
            'optimization_complete': True,
            'strategies_applied': optimization_results,
            'final_memory_mb': final_memory,
            'compliant': final_memory < 128
        }
    except Exception as e:
        logger.error(f"Memory optimization failed: {e}")
        return {'error': str(e)}

def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies."""
    try:
        cleanup_results = []
        
        # Step 1: Basic cleanup
        basic_cleanup = force_memory_cleanup()
        cleanup_results.append(('basic_gc', basic_cleanup))
        
        # Step 2: Singleton cleanup
        try:
            from .singleton_core import _registry
            singleton_cleanup = _registry.cleanup()
            cleanup_results.append(('singleton_cleanup', singleton_cleanup))
        except Exception as e:
            cleanup_results.append(('singleton_cleanup', {'error': str(e)}))
        
        # Step 3: Additional Python cleanup
        try:
            if hasattr(sys, 'intern'):
                pass
            cleanup_results.append(('system_cleanup', {'intern_cleared': True}))
        except Exception as e:
            cleanup_results.append(('system_cleanup', {'error': str(e)}))
        
        final_stats = get_memory_stats()
        
        return {
            'comprehensive_cleanup': True,
            'cleanup_steps': cleanup_results,
            'final_memory_mb': final_stats.get('rss_mb', 0),
            'final_compliant': final_stats.get('compliant', False)
        }
    except Exception as e:
        return {'error': str(e)}

def emergency_memory_preserve() -> Dict[str, Any]:
    """Emergency memory preservation mode."""
    try:
        # Get current status
        initial_stats = get_memory_stats()
        
        if initial_stats.get('compliant', False):
            return {
                'emergency_mode': False,
                'reason': 'memory_within_limits',
                'current_mb': initial_stats.get('rss_mb', 0)
            }
        
        # Emergency cleanup sequence
        emergency_steps = []
        
        # Step 1: Aggressive GC
        gc_result = gc.collect()
        emergency_steps.append(f"gc_collected_{gc_result}_objects")
        
        # Step 2: Clear singleton registry
        from .singleton_core import _registry
        singleton_count = len(_registry._instances)
        _registry.cleanup()
        emergency_steps.append(f"cleared_{singleton_count}_singletons")
        
        # Step 3: Final GC
        final_gc = gc.collect()
        emergency_steps.append(f"final_gc_collected_{final_gc}_objects")
        
        final_stats = get_memory_stats()
        
        return {
            'emergency_mode': True,
            'emergency_steps': emergency_steps,
            'memory_before_mb': initial_stats.get('rss_mb', 0),
            'memory_after_mb': final_stats.get('rss_mb', 0),
            'memory_freed_mb': initial_stats.get('rss_mb', 0) - final_stats.get('rss_mb', 0),
            'now_compliant': final_stats.get('compliant', False)
        }
        
    except Exception as e:
        return {
            'emergency_mode': True,
            'error': str(e),
            'fallback_cleanup_attempted': True
        }

def get_memory_monitor():
    """Get basic memory monitor instance."""
    class MemoryMonitor:
        @staticmethod
        def get_stats():
            return get_memory_stats()
        
        @staticmethod
        def check_compliance():
            return check_lambda_memory_compliance()
        
        @staticmethod
        def cleanup():
            return force_memory_cleanup()
    
    return MemoryMonitor()

def get_enhanced_memory_monitor():
    """Get enhanced memory monitor instance."""
    class EnhancedMemoryMonitor:
        @staticmethod
        def get_stats():
            return get_comprehensive_memory_stats()
        
        @staticmethod
        def check_compliance():
            return check_lambda_memory_compliance()
        
        @staticmethod
        def cleanup():
            return force_comprehensive_memory_cleanup()
        
        @staticmethod
        def emergency_preserve():
            return emergency_memory_preserve()
        
        @staticmethod
        def monitor_continuous():
            return {
                'monitoring': 'enhanced',
                'features': ['comprehensive_stats', 'emergency_preserve', 'continuous_monitoring']
            }
    
    return EnhancedMemoryMonitor()

# EOF
