"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.22.02
Description: System diagnostic operations for debug subsystem

CHANGELOG:
- 2025.10.22.02: Added WEBSOCKET and CIRCUIT_BREAKER interface diagnostics
  - Added _diagnose_websocket_performance (connection stats, rate limiting)
  - Added _diagnose_circuit_breaker_performance (breaker stats, rejection rates)
  - Both support rate limiting analysis (LESS-21)
  - Both analyze error rates and provide recommendations

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


def _diagnose_websocket_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose WEBSOCKET interface performance.
    
    Analyzes:
    - Operation statistics (connections, messages, errors)
    - Rate limiting effectiveness
    - Success/failure rates
    - Performance recommendations
    
    REF-IDs:
    - LESS-21: Rate limiting monitoring
    - DEC-04: Lambda performance patterns
    
    Returns:
        Performance diagnostics and recommendations
    """
    from gateway import create_success_response, create_error_response
    
    diagnostics = {
        'interface': 'WEBSOCKET',
        'performance': {},
        'statistics': {},
        'analysis': {},
        'recommendations': []
    }
    
    try:
        # Get manager and statistics
        from websocket_core import get_websocket_manager
        manager = get_websocket_manager()
        
        stats_result = manager.get_stats()
        if not stats_result.get('success'):
            return create_error_response('Failed to get statistics', 'STATS_UNAVAILABLE')
        
        stats = stats_result.get('data', {})
        
        # Extract statistics
        total_ops = stats.get('total_operations', 0)
        connections = stats.get('connections_count', 0)
        messages_sent = stats.get('messages_sent_count', 0)
        messages_received = stats.get('messages_received_count', 0)
        errors = stats.get('errors_count', 0)
        rate_limited = stats.get('rate_limited_count', 0)
        
        diagnostics['statistics'] = {
            'total_operations': total_ops,
            'connections': connections,
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'errors': errors,
            'rate_limited': rate_limited
        }
        
        # Performance analysis
        if total_ops > 0:
            error_rate = (errors / total_ops) * 100
            rate_limit_impact = (rate_limited / total_ops) * 100
            
            diagnostics['analysis'] = {
                'error_rate_percent': round(error_rate, 2),
                'rate_limit_impact_percent': round(rate_limit_impact, 2),
                'average_messages_per_connection': round(messages_sent / connections, 2) if connections > 0 else 0,
                'send_receive_ratio': round(messages_sent / messages_received, 2) if messages_received > 0 else 0
            }
            
            # Performance assessment
            if error_rate < 1.0:
                diagnostics['performance']['error_rate'] = 'excellent'
            elif error_rate < 5.0:
                diagnostics['performance']['error_rate'] = 'good'
            elif error_rate < 10.0:
                diagnostics['performance']['error_rate'] = 'fair'
            else:
                diagnostics['performance']['error_rate'] = 'poor'
            
            if rate_limit_impact < 0.1:
                diagnostics['performance']['rate_limiting'] = 'minimal_impact'
            elif rate_limit_impact < 1.0:
                diagnostics['performance']['rate_limiting'] = 'low_impact'
            elif rate_limit_impact < 5.0:
                diagnostics['performance']['rate_limiting'] = 'moderate_impact'
            else:
                diagnostics['performance']['rate_limiting'] = 'high_impact'
        else:
            diagnostics['analysis']['no_operations'] = 'No operations executed yet'
        
        # Rate limiting details
        diagnostics['rate_limiting'] = {
            'max_rate': stats.get('max_rate_limit', 300),
            'window_ms': stats.get('rate_limit_window_ms', 1000),
            'current_size': stats.get('current_rate_limit_size', 0),
            'rate_limited_count': rate_limited
        }
        
        # Recommendations
        if errors > 0:
            diagnostics['recommendations'].append(
                'Review error logs for connection failures or message serialization issues'
            )
        
        if rate_limited > total_ops * 0.05:  # > 5% rate limited
            diagnostics['recommendations'].append(
                'Consider implementing request batching or throttling to reduce rate limiting'
            )
        
        if connections > 0 and messages_sent == 0:
            diagnostics['recommendations'].append(
                'Connections established but no messages sent - verify application logic'
            )
        
        if messages_sent > messages_received * 2:
            diagnostics['recommendations'].append(
                'Send/receive ratio imbalanced - verify response handling logic'
            )
        
        if not diagnostics['recommendations']:
            diagnostics['recommendations'].append('Performance looks good - no issues detected')
        
        return create_success_response('WEBSOCKET performance diagnostics complete', diagnostics)
        
    except Exception as e:
        return create_error_response(f'Performance diagnostics failed: {str(e)}', 'DIAGNOSTICS_FAILED')


def _diagnose_circuit_breaker_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose CIRCUIT_BREAKER interface performance.
    
    Analyzes:
    - Operation statistics across all breakers
    - Rate limiting effectiveness
    - Circuit breaker states and patterns
    - Success/failure rates per breaker
    - Performance recommendations
    
    REF-IDs:
    - LESS-21: Rate limiting monitoring
    - DEC-04: Lambda performance patterns
    
    Returns:
        Performance diagnostics and recommendations
    """
    from gateway import create_success_response, create_error_response
    
    diagnostics = {
        'interface': 'CIRCUIT_BREAKER',
        'performance': {},
        'statistics': {},
        'breakers': {},
        'analysis': {},
        'recommendations': []
    }
    
    try:
        # Get manager and statistics
        from circuit_breaker_core import get_circuit_breaker_manager
        manager = get_circuit_breaker_manager()
        
        stats_result = manager.get_stats()
        if not stats_result.get('success'):
            return create_error_response('Failed to get statistics', 'STATS_UNAVAILABLE')
        
        stats = stats_result.get('data', {})
        
        # Extract global statistics
        total_ops = stats.get('total_operations', 0)
        breakers_count = stats.get('breakers_count', 0)
        rate_limited = stats.get('rate_limited_count', 0)
        
        diagnostics['statistics'] = {
            'total_operations': total_ops,
            'breakers_count': breakers_count,
            'rate_limited_count': rate_limited
        }
        
        # Analyze individual breakers
        breakers_data = stats.get('breakers', {})
        total_calls = 0
        total_successful = 0
        total_failed = 0
        total_rejected = 0
        open_breakers = 0
        half_open_breakers = 0
        
        for breaker_name, breaker_state in breakers_data.items():
            breaker_stats = breaker_state.get('statistics', {})
            calls = breaker_stats.get('total_calls', 0)
            successful = breaker_stats.get('successful_calls', 0)
            failed = breaker_stats.get('failed_calls', 0)
            rejected = breaker_stats.get('rejected_calls', 0)
            state = breaker_state.get('state', 'closed')
            
            total_calls += calls
            total_successful += successful
            total_failed += failed
            total_rejected += rejected
            
            if state == 'open':
                open_breakers += 1
            elif state == 'half_open':
                half_open_breakers += 1
            
            # Per-breaker analysis
            if calls > 0:
                success_rate = (successful / calls) * 100
                failure_rate = (failed / calls) * 100
                rejection_rate = (rejected / calls) * 100
                
                diagnostics['breakers'][breaker_name] = {
                    'state': state,
                    'calls': calls,
                    'success_rate_percent': round(success_rate, 2),
                    'failure_rate_percent': round(failure_rate, 2),
                    'rejection_rate_percent': round(rejection_rate, 2),
                    'threshold': breaker_state.get('threshold', 5),
                    'current_failures': breaker_state.get('failures', 0)
                }
        
        # Overall analysis
        if total_calls > 0:
            overall_success_rate = (total_successful / total_calls) * 100
            overall_failure_rate = (total_failed / total_calls) * 100
            overall_rejection_rate = (total_rejected / total_calls) * 100
            
            diagnostics['analysis'] = {
                'total_calls': total_calls,
                'overall_success_rate_percent': round(overall_success_rate, 2),
                'overall_failure_rate_percent': round(overall_failure_rate, 2),
                'overall_rejection_rate_percent': round(overall_rejection_rate, 2),
                'open_breakers': open_breakers,
                'half_open_breakers': half_open_breakers,
                'healthy_breakers': breakers_count - open_breakers - half_open_breakers
            }
            
            # Performance assessment
            if overall_success_rate >= 95:
                diagnostics['performance']['overall'] = 'excellent'
            elif overall_success_rate >= 90:
                diagnostics['performance']['overall'] = 'good'
            elif overall_success_rate >= 80:
                diagnostics['performance']['overall'] = 'fair'
            else:
                diagnostics['performance']['overall'] = 'poor'
        else:
            diagnostics['analysis']['no_calls'] = 'No circuit breaker calls executed yet'
        
        # Rate limiting analysis
        if total_ops > 0:
            rate_limit_impact = (rate_limited / total_ops) * 100
            diagnostics['analysis']['rate_limit_impact_percent'] = round(rate_limit_impact, 2)
            
            if rate_limit_impact < 0.1:
                diagnostics['performance']['rate_limiting'] = 'minimal_impact'
            elif rate_limit_impact < 1.0:
                diagnostics['performance']['rate_limiting'] = 'low_impact'
            elif rate_limit_impact < 5.0:
                diagnostics['performance']['rate_limiting'] = 'moderate_impact'
            else:
                diagnostics['performance']['rate_limiting'] = 'high_impact'
        
        # Rate limiting details
        diagnostics['rate_limiting'] = {
            'max_rate': stats.get('max_rate_limit', 1000),
            'window_ms': stats.get('rate_limit_window_ms', 1000),
            'current_size': stats.get('current_rate_limit_size', 0),
            'rate_limited_count': rate_limited
        }
        
        # Recommendations
        if open_breakers > 0:
            diagnostics['recommendations'].append(
                f'{open_breakers} circuit breaker(s) in OPEN state - investigate failures and consider increasing thresholds'
            )
        
        if total_rejected > total_calls * 0.05:  # > 5% rejected
            diagnostics['recommendations'].append(
                'High rejection rate - circuit breakers may be too sensitive, consider increasing failure thresholds'
            )
        
        if rate_limited > total_ops * 0.05:  # > 5% rate limited
            diagnostics['recommendations'].append(
                'Consider implementing request batching or throttling to reduce rate limiting'
            )
        
        if total_failed > total_successful:
            diagnostics['recommendations'].append(
                'Failures exceed successful calls - investigate underlying service health'
            )
        
        if not diagnostics['recommendations']:
            diagnostics['recommendations'].append('Performance looks good - no issues detected')
        
        return create_success_response('CIRCUIT_BREAKER performance diagnostics complete', diagnostics)
        
    except Exception as e:
        return create_error_response(f'Performance diagnostics failed: {str(e)}', 'DIAGNOSTICS_FAILED')


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_websocket_performance',
    '_diagnose_circuit_breaker_performance'
]

# EOF
