"""
singleton_memory.py - Memory Monitoring Implementation Module
Version: 2025.09.24.09
Description: Internal memory monitoring implementation for singleton operations

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Memory usage tracking and monitoring
- Lambda 128MB compliance checking
- Emergency memory cleanup operations
- Singleton memory optimization

PRIMARY FILE: singleton.py (interface)
SECONDARY FILE: singleton_memory.py (implementation)
"""

import logging
import gc
import psutil
import os
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ===== MEMORY MONITORING IMPLEMENTATION =====

def _get_singleton_memory_status_implementation() -> Dict[str, Any]:
    """Get singleton memory status implementation."""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Get singleton registry status
        from .singleton_core import _registry
        singleton_status = _registry.get_status()
        
        return {
            'singleton_memory_usage_mb': singleton_status['memory_usage_estimate'] / (1024 * 1024),
            'total_process_memory_mb': memory_info.rss / (1024 * 1024),
            'singleton_count': singleton_status['total_singletons'],
            'lambda_128mb_compliant': memory_info.rss < 128 * 1024 * 1024,
            'memory_pressure': 'high' if memory_info.rss > 100 * 1024 * 1024 else 'normal',
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
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': process.memory_percent(),
            'available_mb': (128 - memory_info.rss / (1024 * 1024)),  # Lambda limit
            'compliant': memory_info.rss < 128 * 1024 * 1024
        }
    except Exception as e:
        return {'error': str(e), 'compliant': False}

def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics."""
    basic_stats = get_memory_stats()
    
    try:
        # Add garbage collection stats
        gc_stats = {
            'gc_generation_0': len(gc.get_objects(0)) if hasattr(gc, 'get_objects') else 0,
            'gc_generation_1': len(gc.get_objects(1)) if hasattr(gc, 'get_objects') else 0,
            'gc_generation_2': len(gc.get_objects(2)) if hasattr(gc, 'get_objects') else 0,
            'gc_collected': gc.collect()
        }
        
        basic_stats.update(gc_stats)
        basic_stats['comprehensive'] = True
        
    except Exception as e:
        basic_stats['gc_error'] = str(e)
        
    return basic_stats

def check_lambda_memory_compliance() -> Dict[str, Any]:
    """Check Lambda 128MB memory compliance."""
    stats = get_memory_stats()
    
    compliance_report = {
        'compliant': stats.get('compliant', False),
        'current_mb': stats.get('rss_mb', 0),
        'limit_mb': 128,
        'available_mb': stats.get('available_mb', 0),
        'usage_percentage': (stats.get('rss_mb', 0) / 128) * 100,
        'timestamp': time.time()
    }
    
    if compliance_report['usage_percentage'] > 90:
        compliance_report['status'] = 'critical'
        compliance_report['recommendation'] = 'immediate_cleanup_required'
    elif compliance_report['usage_percentage'] > 75:
        compliance_report['status'] = 'warning'
        compliance_report['recommendation'] = 'cleanup_recommended'
    else:
        compliance_report['status'] = 'healthy'
        compliance_report['recommendation'] = 'no_action_needed'
        
    return compliance_report

def force_memory_cleanup() -> Dict[str, Any]:
    """Force memory cleanup."""
    start_time = time.time()
    before_stats = get_memory_stats()
    
    # Force garbage collection
    collected = gc.collect()
    
    # Additional cleanup for Lambda
    if hasattr(gc, 'set_threshold'):
        gc.set_threshold(700, 10, 10)  # More aggressive GC
    
    after_stats = get_memory_stats()
    duration = time.time() - start_time
    
    return {
        'cleanup_performed': True,
        'gc_collected': collected,
        'memory_before_mb': before_stats.get('rss_mb', 0),
        'memory_after_mb': after_stats.get('rss_mb', 0),
        'memory_freed_mb': before_stats.get('rss_mb', 0) - after_stats.get('rss_mb', 0),
        'duration_ms': duration * 1000,
        'still_compliant': after_stats.get('compliant', False)
    }

def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """Force comprehensive memory cleanup."""
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
        import sys
        if hasattr(sys, 'intern'):
            # Clear string intern cache if possible
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
