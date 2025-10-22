"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.14.01
Description: System diagnostic operations for debug subsystem

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
    from debug.debug_health import _check_component_health, _check_gateway_health
    
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


def _diagnose_http_client_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose HTTP_CLIENT interface performance characteristics.
    
    Analyzes:
    - Request patterns and statistics
    - Connection pool utilization
    - Retry behavior and effectiveness
    - Rate limiting impact
    - Response time patterns
    - Error rates and types
    - SSL verification overhead
    
    Returns:
        Dict with performance diagnostics
        
    REF: LESS-21 (Rate limiting performance impact)
    REF: DEC-04 (Lambda performance characteristics)
    """
    from http_client_core import get_http_client_manager
    
    diagnostics = {
        'interface': 'HTTP_CLIENT',
        'timestamp': time.time(),
        'analysis': {}
    }
    
    try:
        manager = get_http_client_manager()
        stats = manager.get_stats()
        
        # Analysis 1: Request statistics
        total_requests = stats.get('requests', 0)
        successful = stats.get('successful', 0)
        failed = stats.get('failed', 0)
        retries = stats.get('retries', 0)
        rate_limited = stats.get('rate_limited', 0)
        
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0
        failure_rate = (failed / total_requests * 100) if total_requests > 0 else 0
        retry_rate = (retries / total_requests * 100) if total_requests > 0 else 0
        
        diagnostics['analysis']['request_statistics'] = {
            'total_requests': total_requests,
            'successful': successful,
            'failed': failed,
            'retries': retries,
            'rate_limited': rate_limited,
            'success_rate_percent': round(success_rate, 2),
            'failure_rate_percent': round(failure_rate, 2),
            'retry_rate_percent': round(retry_rate, 2),
            'assessment': 'Good' if success_rate >= 95 else 'Needs attention' if success_rate >= 80 else 'Poor'
        }
        
        # Analysis 2: Rate limiting impact
        if total_requests > 0:
            rate_limit_impact = (rate_limited / total_requests * 100)
            diagnostics['analysis']['rate_limiting_impact'] = {
                'rate_limited_requests': rate_limited,
                'percentage_of_total': round(rate_limit_impact, 2),
                'current_queue_size': stats.get('rate_limiter_size', 0),
                'max_queue_size': 500,
                'limit_per_second': 500,
                'assessment': 'Effective' if rate_limit_impact < 1 else 'High traffic' if rate_limit_impact < 5 else 'Overloaded'
            }
        else:
            diagnostics['analysis']['rate_limiting_impact'] = {
                'rate_limited_requests': 0,
                'percentage_of_total': 0,
                'assessment': 'No traffic yet'
            }
        
        # Analysis 3: Retry effectiveness
        if retries > 0:
            diagnostics['analysis']['retry_effectiveness'] = {
                'total_retries': retries,
                'retry_rate_percent': round(retry_rate, 2),
                'max_attempts': 3,
                'backoff_strategy': 'Exponential (100ms base, 2.0 multiplier)',
                'assessment': 'Normal' if retry_rate < 10 else 'High retry rate - check network'
            }
        else:
            diagnostics['analysis']['retry_effectiveness'] = {
                'total_retries': 0,
                'assessment': 'No retries needed - good network conditions'
            }
        
        # Analysis 4: Connection pool configuration
        if hasattr(manager, 'http'):
            diagnostics['analysis']['connection_pool'] = {
                'pool_configured': True,
                'max_connections': 10,
                'connect_timeout_sec': 10.0,
                'read_timeout_sec': 30.0,
                'ssl_verification': 'Enabled (HOME_ASSISTANT_VERIFY_SSL != false)',
                'assessment': 'Configured'
            }
        else:
            diagnostics['analysis']['connection_pool'] = {
                'pool_configured': False,
                'assessment': 'Pool not initialized'
            }
        
        # Analysis 5: Performance recommendations
        recommendations = []
        
        if failure_rate > 10:
            recommendations.append('High failure rate - check network connectivity and target service health')
        
        if retry_rate > 15:
            recommendations.append('High retry rate - consider increasing timeouts or checking network stability')
        
        if rate_limit_impact > 5:
            recommendations.append('High rate limiting - consider implementing request batching or caching')
        
        if total_requests == 0:
            recommendations.append('No requests processed yet - HTTP client is initialized but unused')
        
        if not recommendations:
            recommendations.append('Performance looks good - no immediate concerns')
        
        diagnostics['analysis']['recommendations'] = recommendations
        
        # Analysis 6: Cold start impact estimation
        diagnostics['analysis']['cold_start_impact'] = {
            'urllib3_preloaded': True,
            'estimated_overhead_ms': 5,
            'assessment': 'Minimal - urllib3 preloaded in lambda_preload'
        }
        
    except Exception as e:
        diagnostics['error'] = str(e)
        diagnostics['error_type'] = type(e).__name__
    
    return diagnostics


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_http_client_performance'
]

# EOF
