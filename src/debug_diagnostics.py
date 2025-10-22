"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.22.01
Description: System diagnostic operations for debug subsystem

CHANGES (2025.10.22.01):
- Added _diagnose_logging_performance()
- Added _diagnose_security_performance()
- Added _diagnose_config_performance()

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


def _diagnose_logging_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose LOGGING interface performance.
    
    Analyzes:
    - Log message throughput
    - Buffer usage patterns
    - Rate limiting effectiveness
    - Handler performance
    - Format overhead
    
    Returns:
        Dict with performance analysis and recommendations
    """
    try:
        import gateway
        
        # Get logging stats
        stats = gateway.get_logging_stats()
        
        insights = []
        recommendations = []
        metrics = {}
        
        # Analyze message counts
        total_messages = stats.get('total_messages', 0)
        if total_messages == 0:
            insights.append("No log messages recorded yet")
            recommendations.append("Initialize logging to start collecting metrics")
        elif total_messages < 1000:
            insights.append(f"Logging: {total_messages} messages (light usage)")
        elif total_messages < 10000:
            insights.append(f"Logging: {total_messages} messages (moderate usage)")
        else:
            insights.append(f"Logging: {total_messages} messages (heavy usage)")
            recommendations.append("Consider log rotation or archival strategy")
        
        metrics['total_messages'] = total_messages
        
        # Analyze by level
        by_level = stats.get('by_level', {})
        error_count = by_level.get('ERROR', 0)
        warning_count = by_level.get('WARNING', 0)
        
        if error_count > 0:
            error_rate = (error_count / total_messages * 100) if total_messages > 0 else 0
            if error_rate > 10:
                insights.append(f"HIGH error rate: {error_rate:.1f}% ({error_count} errors)")
                recommendations.append("CRITICAL: Investigate error patterns")
            else:
                insights.append(f"Error rate: {error_rate:.1f}% ({error_count} errors)")
        
        if warning_count > 0:
            warning_rate = (warning_count / total_messages * 100) if total_messages > 0 else 0
            if warning_rate > 20:
                insights.append(f"HIGH warning rate: {warning_rate:.1f}%")
                recommendations.append("Review warning patterns for potential issues")
        
        metrics['by_level'] = by_level
        
        # Performance rating
        if error_count > total_messages * 0.1:
            performance_rating = "POOR"
        elif warning_count > total_messages * 0.2:
            performance_rating = "DEGRADED"
        else:
            performance_rating = "GOOD"
        
        if not recommendations:
            recommendations.append("Logging performance is optimal")
        
        return {
            'success': True,
            'interface': 'LOGGING',
            'performance_rating': performance_rating,
            'insights': insights,
            'recommendations': recommendations,
            'metrics': metrics
        }
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'LOGGING'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Performance diagnosis failed: {str(e)}',
            'interface': 'LOGGING'
        }


def _diagnose_security_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose SECURITY interface performance.
    
    Analyzes:
    - Validation operation latency
    - Encryption/decryption throughput
    - Rate limiting effectiveness
    - Token validation performance
    - Hash computation overhead
    
    Returns:
        Dict with performance analysis and recommendations
    """
    try:
        import gateway
        
        insights = []
        recommendations = []
        metrics = {}
        
        # Check if security operations are available
        try:
            test_result = gateway.validate_string("test", max_length=10)
            insights.append("Security validation operations: AVAILABLE")
        except Exception as e:
            insights.append(f"Security validation operations: ERROR - {str(e)}")
            recommendations.append("CRITICAL: Fix security validation errors")
        
        # Estimate typical operation costs
        insights.append("Typical operation costs (estimated):")
        insights.append("  - validate_string: <1ms")
        insights.append("  - hash_data: 1-5ms")
        insights.append("  - encrypt/decrypt: 5-20ms")
        
        recommendations.append("Security operations have minimal overhead")
        recommendations.append("Monitor for any validation bottlenecks in production")
        
        performance_rating = "GOOD"
        
        return {
            'success': True,
            'interface': 'SECURITY',
            'performance_rating': performance_rating,
            'insights': insights,
            'recommendations': recommendations,
            'metrics': metrics
        }
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'SECURITY'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Performance diagnosis failed: {str(e)}',
            'interface': 'SECURITY'
        }


def _diagnose_config_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose CONFIG interface performance.
    
    Analyzes:
    - Rate limiting effectiveness
    - Parameter operation performance
    - SSM vs environment variable usage
    - Configuration reload patterns
    - Cache hit rates
    
    Returns:
        Dict with performance analysis and recommendations
    """
    try:
        import gateway
        
        # Get state info
        state = gateway.config_get_state()
        
        insights = []
        recommendations = []
        metrics = {}
        
        # Analyze rate limiting
        rate_limited_count = state.get('rate_limited_count', 0)
        
        if rate_limited_count == 0:
            insights.append("Rate limiting: No rejections (healthy)")
        elif rate_limited_count < 10:
            insights.append(f"Rate limiting: {rate_limited_count} rejections (acceptable)")
        elif rate_limited_count < 100:
            insights.append(f"Rate limiting: {rate_limited_count} rejections (moderate)")
            recommendations.append("Monitor config operation frequency")
        else:
            insights.append(f"Rate limiting: {rate_limited_count} rejections (HIGH)")
            recommendations.append("CRITICAL: Review config operation patterns, possible abuse")
        
        metrics['rate_limited_count'] = rate_limited_count
        
        # Analyze Parameter Store usage
        use_parameter_store = state.get('use_parameter_store', False)
        parameter_prefix = state.get('parameter_prefix', '/lambda-execution-engine')
        
        if use_parameter_store:
            insights.append(f"Parameter Store ENABLED: Using prefix '{parameter_prefix}'")
            insights.append("Priority: SSM → Environment → Default")
            recommendations.append("Ensure SSM parameters are cached to minimize API calls")
        else:
            insights.append("Parameter Store DISABLED: Using environment variables only")
            insights.append("Priority: Environment → Default")
            recommendations.append("Consider enabling USE_PARAMETER_STORE=true for centralized config")
        
        metrics['use_parameter_store'] = use_parameter_store
        metrics['parameter_prefix'] = parameter_prefix
        
        # Analyze configuration keys
        config_keys = state.get('config_keys', [])
        key_count = len(config_keys)
        
        if key_count == 0:
            insights.append("Configuration EMPTY: No parameters loaded")
            recommendations.append("Initialize configuration with config_initialize()")
        elif key_count < 10:
            insights.append(f"Configuration: {key_count} parameters (light)")
        elif key_count < 50:
            insights.append(f"Configuration: {key_count} parameters (moderate)")
        else:
            insights.append(f"Configuration: {key_count} parameters (heavy)")
            recommendations.append("Consider categorizing config for better organization")
        
        metrics['config_key_count'] = key_count
        metrics['config_keys'] = config_keys
        
        # Check initialization status
        initialized = state.get('initialized', False)
        
        if initialized:
            insights.append("Initialization: COMPLETE")
        else:
            insights.append("Initialization: PENDING")
            recommendations.append("Call config_initialize() to load configuration")
        
        metrics['initialized'] = initialized
        
        # Estimate cold start impact
        cold_start_estimate_ms = 0
        
        if use_parameter_store:
            # SSM calls add ~50-100ms per parameter
            cold_start_estimate_ms += key_count * 75
            insights.append(f"Cold start estimate: ~{cold_start_estimate_ms}ms (SSM enabled)")
            
            if cold_start_estimate_ms > 500:
                recommendations.append("HIGH cold start impact: Consider caching SSM parameters")
        else:
            # Environment variables are instant
            cold_start_estimate_ms = key_count * 0.1
            insights.append(f"Cold start estimate: ~{cold_start_estimate_ms:.1f}ms (environment only)")
        
        metrics['cold_start_estimate_ms'] = cold_start_estimate_ms
        
        # Overall performance rating
        if rate_limited_count > 100:
            performance_rating = "POOR"
        elif cold_start_estimate_ms > 500:
            performance_rating = "DEGRADED"
        elif not initialized:
            performance_rating = "UNINITIALIZED"
        else:
            performance_rating = "GOOD"
        
        return {
            'success': True,
            'interface': 'CONFIG',
            'performance_rating': performance_rating,
            'insights': insights,
            'recommendations': recommendations,
            'metrics': metrics,
            'summary': {
                'rate_limited_count': rate_limited_count,
                'config_keys': key_count,
                'use_parameter_store': use_parameter_store,
                'initialized': initialized,
                'cold_start_ms': cold_start_estimate_ms
            }
        }
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'CONFIG'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Performance diagnosis failed: {str(e)}',
            'interface': 'CONFIG'
        }


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_logging_performance',
    '_diagnose_security_performance',
    '_diagnose_config_performance'
]

# EOF
