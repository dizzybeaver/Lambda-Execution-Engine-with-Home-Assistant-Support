"""
utility_cross_interface.py - Cross-Interface Utilities (Internal)
Version: 2025.10.16.04
Description: Shared utilities that integrate with other interfaces via gateway

SUGA-ISP: Internal module - only accessed via interface_utility.py

IMPORTANT: All gateway imports are lazy (inside functions) to avoid circular dependencies.
All cross-interface operations include comprehensive error handling.

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import time
import uuid
import os
import concurrent.futures
from typing import Dict, Any, Optional, List, Callable
import logging as stdlib_logging

logger = stdlib_logging.getLogger(__name__)


# ===== CROSS-INTERFACE SHARED UTILITIES =====

def cache_operation_result(operation_name: str, func: Callable, ttl: int = 300, 
                          cache_key_prefix: str = None, **kwargs) -> Any:
    """
    Generic caching wrapper for any interface operation.
    Eliminates duplicate caching patterns across interfaces.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        cache_prefix = cache_key_prefix or operation_name
        cache_key = f"{cache_prefix}_{hash(str(kwargs))}"
        
        try:
            cached = execute_operation(GatewayInterface.CACHE, 'get', key=cache_key)
            if cached is not None:
                return cached
        except Exception as e:
            logger.warning(f"Cache get failed, executing without cache: {str(e)}")
        
        result = func(**kwargs)
        
        if result is not None:
            try:
                execute_operation(GatewayInterface.CACHE, 'set', key=cache_key, value=result, ttl=ttl)
            except Exception as e:
                logger.warning(f"Cache set failed: {str(e)}")
        
        return result
        
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return func(**kwargs)


def record_operation_metrics(interface: str, operation: str, duration: float, 
                            success: bool = True, correlation_id: Optional[str] = None):
    """
    Generic metrics recording for any interface operation.
    Eliminates duplicate metrics patterns across interfaces.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        metric_name = f"{interface}_{operation}_duration"
        tags = {
            'interface': interface,
            'operation': operation,
            'success': str(success)
        }
        
        if correlation_id:
            tags['correlation_id'] = correlation_id
        
        execute_operation(GatewayInterface.METRICS, 'record_metric', 
                         name=metric_name, value=duration, tags=tags)
        
        if not success:
            error_metric = f"{interface}_{operation}_error"
            execute_operation(GatewayInterface.METRICS, 'record_metric',
                             name=error_metric, value=1.0, tags=tags)
    
    except Exception as e:
        logger.warning(f"Failed to record metrics: {str(e)}")


def handle_operation_error(interface: str, operation: str, error: Exception,
                          correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Unified error handling with logging and metrics.
    Eliminates duplicate error handling patterns across interfaces.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        # Generate correlation ID if not provided
        corr_id = correlation_id or str(uuid.uuid4())
        
        error_response = {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'interface': interface,
            'operation': operation,
            'correlation_id': corr_id,
            'timestamp': time.time()
        }
        
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_error',
                             message=f"{interface}.{operation} failed",
                             error=error,
                             extra={'correlation_id': corr_id})
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
        
        try:
            execute_operation(GatewayInterface.METRICS, 'record_metric',
                             name=f"{interface}_operation_error",
                             value=1.0,
                             tags={'operation': operation, 'error_type': type(error).__name__})
        except Exception as e:
            logger.warning(f"Failed to record error metric: {str(e)}")
        
        try:
            sanitized = execute_operation(GatewayInterface.SECURITY, 'sanitize_data', data=error_response)
            return sanitized.get('sanitized_data', error_response)
        except Exception:
            return error_response
    
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': time.time()
        }


def create_operation_context(interface: str, operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create operation context with correlation tracking.
    Eliminates duplicate context creation patterns across interfaces.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        context = {
            'interface': interface,
            'operation': operation,
            'correlation_id': str(uuid.uuid4()),
            'start_time': time.time(),
            'parameters': kwargs
        }
        
        try:
            execute_operation(GatewayInterface.METRICS, 'record_metric',
                             name=f"{interface}_operation_started",
                             value=1.0,
                             tags={'operation': operation, 'correlation_id': context['correlation_id']})
        except Exception as e:
            logger.warning(f"Failed to record operation start metric: {str(e)}")
        
        return context
    
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return {
            'interface': interface,
            'operation': operation,
            'correlation_id': str(uuid.uuid4()),
            'start_time': time.time(),
            'parameters': kwargs
        }


def close_operation_context(context: Dict[str, Any], success: bool = True, 
                           result: Any = None) -> Dict[str, Any]:
    """
    Close operation context and record final metrics.
    Eliminates duplicate context closing patterns across interfaces.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        duration = time.time() - context.get('start_time', time.time())
        interface = context.get('interface', 'unknown')
        operation = context.get('operation', 'unknown')
        correlation_id = context.get('correlation_id', '')
        
        record_operation_metrics(interface, operation, duration, success, correlation_id=correlation_id)
        
        try:
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                             message=f"{interface}.{operation} completed",
                             extra={'correlation_id': correlation_id, 'duration': duration, 'success': success})
        except Exception as e:
            logger.warning(f"Failed to log operation completion: {str(e)}")
        
        return {
            'success': success,
            'duration': duration,
            'correlation_id': correlation_id,
            'result': result
        }
    
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return {
            'success': success,
            'duration': time.time() - context.get('start_time', time.time()),
            'correlation_id': context.get('correlation_id', ''),
            'result': result
        }


def batch_cache_operations(operations: List[Dict[str, Any]], ttl: int = 300) -> List[Any]:
    """
    Batch cache multiple operations for efficiency.
    Reduces cache overhead for bulk operations.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        results = []
        for op in operations:
            cache_key = op.get('cache_key')
            func = op.get('func')
            kwargs = op.get('kwargs', {})
            
            if cache_key:
                try:
                    cached = execute_operation(GatewayInterface.CACHE, 'get', key=cache_key)
                    if cached is not None:
                        results.append(cached)
                        continue
                except Exception as e:
                    logger.warning(f"Cache get failed in batch operation: {str(e)}")
            
            result = func(**kwargs) if func else None
            
            if result is not None and cache_key:
                try:
                    execute_operation(GatewayInterface.CACHE, 'set', key=cache_key, value=result, ttl=ttl)
                except Exception as e:
                    logger.warning(f"Cache set failed in batch operation: {str(e)}")
            
            results.append(result)
        
        return results
    
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return [op.get('func')(**op.get('kwargs', {})) if op.get('func') else None for op in operations]


def parallel_operation_execution(operations: List[Callable], max_workers: int = 5,
                                timeout: float = 30.0) -> Dict[str, Any]:
    """
    Execute multiple operations in parallel with timeout protection.
    Eliminates duplicate parallel execution patterns.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        results = []
        success_count = 0
        error_count = 0
        
        # Validate max_workers
        max_workers = max(1, min(max_workers, os.cpu_count() or 1))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    execute_operation,
                    GatewayInterface.SINGLETON,
                    'execute_with_timeout',
                    func=op,
                    timeout=timeout
                )
                for op in operations
            ]
            
            for future in concurrent.futures.as_completed(futures, timeout=timeout):
                try:
                    result = future.result()
                    if isinstance(result, dict) and 'error' in result:
                        error_count += 1
                    else:
                        success_count += 1
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel operation failed: {str(e)}")
                    error_count += 1
                    results.append({'error': str(e), 'error_type': type(e).__name__})
        
        return {
            'results': results,
            'total_count': len(operations),
            'success_count': success_count,
            'error_count': error_count,
            'all_succeeded': error_count == 0
        }
    
    except ImportError as e:
        logger.error(f"Gateway import failed: {str(e)}")
        return {
            'results': [],
            'total_count': len(operations),
            'success_count': 0,
            'error_count': len(operations),
            'all_succeeded': False,
            'error': str(e)
        }


def aggregate_interface_metrics(interface: str, time_range_minutes: int = 60) -> Dict[str, Any]:
    """
    Aggregate metrics for an interface over time range.
    Provides common metrics aggregation pattern.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        return execute_operation(
            GatewayInterface.METRICS,
            'aggregate_metrics',
            interface=interface,
            time_range_minutes=time_range_minutes
        )
    except Exception as e:
        logger.error(f"Failed to aggregate metrics: {str(e)}")
        return {
            'error': str(e),
            'interface': interface,
            'metrics': {}
        }


def optimize_interface_memory(interface: str) -> Dict[str, Any]:
    """
    Optimize memory usage for an interface.
    Eliminates duplicate memory optimization patterns.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        execute_operation(GatewayInterface.CACHE, 'clear')
        
        # Note: Can't import SharedUtilityCore here (circular), so just return status
        return {
            'interface': interface,
            'optimizations': ['cache_cleared'],
            'timestamp': int(time.time())
        }
    except Exception as e:
        logger.error(f"Failed to optimize memory: {str(e)}")
        return {
            'interface': interface,
            'optimizations': [],
            'error': str(e),
            'timestamp': int(time.time())
        }


def validate_aws_free_tier_compliance(interface: str) -> Dict[str, Any]:
    """
    Validate AWS free tier compliance for an interface.
    Provides common compliance checking pattern.
    """
    try:
        from gateway import execute_operation, GatewayInterface
        
        interface_config = execute_operation(
            GatewayInterface.CONFIG,
            'get_interface_configuration',
            interface=interface,
            environment='production'
        )
        
        metrics_summary = execute_operation(
            GatewayInterface.METRICS,
            'get_metrics_summary',
            metric_names=[f"{interface}_"]
        )
        
        invocations = metrics_summary.get('metric_aggregations', {}).get(f"{interface}_operation_count", {}).get('count', 0)
        
        free_tier_limit = 1000000
        compliance = {
            'interface': interface,
            'invocations': invocations,
            'free_tier_limit': free_tier_limit,
            'compliant': invocations < free_tier_limit,
            'utilization_percentage': (invocations / free_tier_limit) * 100,
            'headroom': free_tier_limit - invocations
        }
        
        return compliance
    
    except Exception as e:
        logger.error(f"Failed to validate AWS compliance: {str(e)}")
        return {
            'interface': interface,
            'error': str(e),
            'compliant': None
        }


# ===== MODULE EXPORTS =====

__all__ = [
    'cache_operation_result',
    'record_operation_metrics',
    'handle_operation_error',
    'create_operation_context',
    'close_operation_context',
    'batch_cache_operations',
    'parallel_operation_execution',
    'aggregate_interface_metrics',
    'optimize_interface_memory',
    'validate_aws_free_tier_compliance',
]

# EOF
