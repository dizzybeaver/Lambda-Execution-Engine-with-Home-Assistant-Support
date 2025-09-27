"""
metrics.py - PRIMARY GATEWAY: Universal Metrics Interface
Version: 2025.09.27.01
Description: Universal metrics gateway providing unified access to all metrics operations
through compatibility layer pattern. Supports performance metrics, system monitoring,
and analytics while maintaining Lambda memory constraints.

ARCHITECTURE: PRIMARY GATEWAY - METRICS FIREWALL
- Provides single entry point for all metrics operations
- Delegates to metrics_core.py for implementation
- Maintains compatibility with legacy function signatures
- Optimized for 128MB Lambda environment

COMPATIBILITY LAYER: Maintains backward compatibility while providing enhanced functionality
through the generic_metrics_operation delegation pattern.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union
from enum import Enum

logger = logging.getLogger(__name__)

# ===== SECTION 1: CORE METRICS OPERATIONS (COMPATIBILITY LAYER) =====

class MetricsOperation(Enum):
    """Core metrics operations for delegation pattern."""
    # Basic Operations
    RECORD_METRIC = "record_metric"
    GET_METRIC = "get_metric"
    GET_METRICS_SUMMARY = "get_metrics_summary"
    GET_PERFORMANCE_STATS = "get_performance_stats"
    
    # Advanced Analytics
    GET_SYSTEM_METRICS = "get_system_metrics"
    MONITOR_THREADS = "monitor_threads"
    
    # Management Operations
    EXPORT_METRICS = "export_metrics"
    RESET_METRICS = "reset_metrics"
    BACKUP_METRICS = "backup_metrics"
    RESTORE_METRICS = "restore_metrics"
    
    # Status and Validation
    GET_METRICS_STATUS = "get_metrics_status"
    VALIDATE_METRICS = "validate_metrics"
    
    # Performance Tracking
    TRACK_EXECUTION_TIME = "track_execution_time"
    TRACK_MEMORY_USAGE = "track_memory_usage"
    TRACK_RESPONSE_SIZE = "track_response_size"
    COUNT_INVOCATIONS = "count_invocations"

def generic_metrics_operation(operation: MetricsOperation, *args, **kwargs) -> Any:
    """Universal metrics operation handler - delegates to metrics_core implementation."""
    try:
        from . import metrics_core
        
        # Map operations to implementation functions
        operation_map = {
            MetricsOperation.RECORD_METRIC: metrics_core._record_metric_implementation,
            MetricsOperation.GET_METRIC: metrics_core._get_metric_implementation,
            MetricsOperation.GET_METRICS_SUMMARY: metrics_core._get_metric_summary_implementation,
            MetricsOperation.GET_PERFORMANCE_STATS: metrics_core._get_performance_stats_implementation,
            MetricsOperation.GET_SYSTEM_METRICS: metrics_core._get_system_metrics_implementation,
            MetricsOperation.MONITOR_THREADS: metrics_core._monitor_thread_safety_implementation,
            MetricsOperation.EXPORT_METRICS: metrics_core._export_metrics_implementation,
            MetricsOperation.RESET_METRICS: metrics_core._reset_metrics_implementation,
            MetricsOperation.BACKUP_METRICS: metrics_core._backup_metrics_implementation,
            MetricsOperation.RESTORE_METRICS: metrics_core._restore_metrics_implementation,
            MetricsOperation.GET_METRICS_STATUS: metrics_core._get_metrics_status_implementation,
            MetricsOperation.VALIDATE_METRICS: metrics_core._validate_metrics_implementation,
            MetricsOperation.TRACK_EXECUTION_TIME: metrics_core._track_execution_time_implementation,
            MetricsOperation.TRACK_MEMORY_USAGE: metrics_core._track_memory_usage_implementation,
            MetricsOperation.TRACK_RESPONSE_SIZE: metrics_core._track_response_size_implementation,
            MetricsOperation.COUNT_INVOCATIONS: metrics_core._count_invocations_implementation,
        }
        
        implementation_func = operation_map.get(operation)
        if implementation_func:
            return implementation_func(*args, **kwargs)
        else:
            logger.warning(f"Unknown metrics operation: {operation}")
            return {"success": False, "error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Metrics operation failed: {operation}, error: {str(e)}")
        return {"success": False, "error": str(e), "operation": str(operation)}

# ===== SECTION 2: BASIC METRICS RECORDING (COMPATIBILITY LAYER) =====

def record_metric(metric_name: str, value: float, dimensions: Optional[Dict[str, str]] = None, 
                 timestamp: Optional[float] = None, **kwargs) -> bool:
    """COMPATIBILITY: Record a metric using the metrics operation framework."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name=metric_name,
                                    value=value,
                                    dimensions=dimensions,
                                    timestamp=timestamp,
                                    **kwargs)

def get_metric(metric_name: str, **kwargs) -> Optional[Dict[str, Any]]:
    """COMPATIBILITY: Retrieve a specific metric using metrics operation."""
    return generic_metrics_operation(MetricsOperation.GET_METRIC,
                                    metric_name=metric_name,
                                    **kwargs)

def get_metrics_summary(metric_names: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Get comprehensive metrics summary using metrics operation."""
    return generic_metrics_operation(MetricsOperation.GET_METRICS_SUMMARY,
                                    metric_names=metric_names,
                                    **kwargs)

def get_performance_stats(metric_filter: Optional[str] = None, 
                         time_range_minutes: int = 60, **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Get performance statistics using metrics operation."""
    return generic_metrics_operation(MetricsOperation.GET_PERFORMANCE_STATS,
                                    metric_filter=metric_filter,
                                    time_range_minutes=time_range_minutes,
                                    **kwargs)

# ===== SECTION 3: LAMBDA PERFORMANCE TRACKING (COMPATIBILITY LAYER) =====

def track_execution_time(execution_time_ms: float, function_name: str = None, **kwargs) -> bool:
    """COMPATIBILITY: Track Lambda execution time using metrics operation."""
    return generic_metrics_operation(MetricsOperation.TRACK_EXECUTION_TIME,
                                    execution_time_ms=execution_time_ms,
                                    function_name=function_name,
                                    **kwargs)

def track_memory_usage(memory_used_mb: float, max_memory_mb: float = 128, **kwargs) -> bool:
    """COMPATIBILITY: Track Lambda memory usage using metrics operation."""
    return generic_metrics_operation(MetricsOperation.TRACK_MEMORY_USAGE,
                                    memory_used_mb=memory_used_mb,
                                    max_memory_mb=max_memory_mb,
                                    **kwargs)

# ===== SECTION 4: ALEXA SKILL METRICS (COMPATIBILITY LAYER) =====

def track_alexa_intent(intent_name: str, success: bool = True, response_time_ms: float = 0.0, **kwargs) -> bool:
    """COMPATIBILITY: Track Alexa intent metrics using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name=f"alexa_intent_{intent_name}",
                                    value=1.0,
                                    dimensions={"success": str(success), "intent": intent_name},
                                    **kwargs)

def track_alexa_response_type(response_type: str, **kwargs) -> bool:
    """COMPATIBILITY: Track Alexa response type using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name="alexa_response_type",
                                    value=1.0,
                                    dimensions={"type": response_type},
                                    **kwargs)

# ===== SECTION 5: HTTP CLIENT METRICS (COMPATIBILITY LAYER) =====

def track_http_request(url: str, method: str, status_code: int, response_time_ms: float = 0.0, **kwargs) -> bool:
    """COMPATIBILITY: Track HTTP request metrics using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name="http_request",
                                    value=response_time_ms,
                                    dimensions={
                                        "url": url,
                                        "method": method,
                                        "status_code": str(status_code)
                                    },
                                    **kwargs)

def track_http_error(url: str, error_type: str, **kwargs) -> bool:
    """COMPATIBILITY: Track HTTP error using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name="http_error",
                                    value=1.0,
                                    dimensions={"url": url, "error_type": error_type},
                                    **kwargs)

# ===== SECTION 6: CACHE PERFORMANCE METRICS (COMPATIBILITY LAYER) =====

def track_cache_hit(cache_type: str = "default", **kwargs) -> bool:
    """COMPATIBILITY: Track cache hit using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name="cache_hit",
                                    value=1.0,
                                    dimensions={"cache_type": cache_type},
                                    **kwargs)

def track_cache_miss(cache_type: str = "default", **kwargs) -> bool:
    """COMPATIBILITY: Track cache miss using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RECORD_METRIC,
                                    metric_name="cache_miss",
                                    value=1.0,
                                    dimensions={"cache_type": cache_type},
                                    **kwargs)

# ===== SECTION 7: FUNCTION INVOCATION TRACKING (COMPATIBILITY LAYER) =====

def count_invocations(function_name: str, **kwargs) -> bool:
    """COMPATIBILITY: Count function invocations using metrics operation."""
    return generic_metrics_operation(MetricsOperation.COUNT_INVOCATIONS,
                                    function_name=function_name,
                                    **kwargs)

def track_response_size(size_bytes: int, context: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
    """COMPATIBILITY: Track response size using metrics operation."""
    return generic_metrics_operation(MetricsOperation.TRACK_RESPONSE_SIZE,
                                    size_bytes=size_bytes,
                                    context=context,
                                    **kwargs)

# ===== SECTION 8: SYSTEM OPERATIONS MONITORING (COMPATIBILITY LAYER) =====

def monitor_thread_safety(**kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Monitor thread safety across system using metrics operation."""
    return generic_metrics_operation(MetricsOperation.MONITOR_THREADS, **kwargs)

def get_system_metrics(**kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Get comprehensive system metrics using metrics operation."""
    return generic_metrics_operation(MetricsOperation.GET_SYSTEM_METRICS, **kwargs)

# ===== SECTION 9: METRICS MANAGEMENT OPERATIONS (COMPATIBILITY LAYER) =====

def export_metrics(export_format: str = "json", **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Export metrics in specified format using metrics operation."""
    return generic_metrics_operation(MetricsOperation.EXPORT_METRICS,
                                    export_format=export_format,
                                    **kwargs)

def reset_metrics(metric_names: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Reset specified metrics using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RESET_METRICS,
                                    metric_names=metric_names,
                                    **kwargs)

def backup_metrics(backup_id: str = None, **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Create metrics backup using metrics operation."""
    return generic_metrics_operation(MetricsOperation.BACKUP_METRICS,
                                    backup_id=backup_id,
                                    **kwargs)

def restore_metrics(backup_id: str, **kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Restore metrics from backup using metrics operation."""
    return generic_metrics_operation(MetricsOperation.RESTORE_METRICS,
                                    backup_id=backup_id,
                                    **kwargs)

# ===== SECTION 10: STATUS AND VALIDATION OPERATIONS (COMPATIBILITY LAYER) =====

def get_metrics_status(**kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Get metrics system operational status using metrics operation."""
    return generic_metrics_operation(MetricsOperation.GET_METRICS_STATUS, **kwargs)

def validate_metrics(**kwargs) -> Dict[str, Any]:
    """COMPATIBILITY: Validate metrics system integrity using metrics operation."""
    return generic_metrics_operation(MetricsOperation.VALIDATE_METRICS, **kwargs)

# ===== SECTION 11: HIGH PERFORMANCE DIRECT ACCESS FUNCTIONS =====

def record_metric_fast(metric_name: str, value: float, **kwargs) -> bool:
    """HIGH PERFORMANCE: Fast metric recording for performance-critical operations."""
    try:
        # Direct cache access for performance
        from . import cache
        
        # Store metric in cache for later processing
        metric_key = f"metric_{metric_name}_{int(time.time() * 1000)}"
        metric_data = {
            'name': metric_name,
            'value': value,
            'timestamp': time.time(),
            'unit': kwargs.get('unit', 'Count')
        }
        
        return cache.cache_set_fast(metric_key, metric_data, ttl=3600)
        
    except Exception as e:
        logger.error(f"Fast metric recording failed: {str(e)}")
        return False

def get_metric_fast(metric_name: str, **kwargs) -> Optional[Dict[str, Any]]:
    """HIGH PERFORMANCE: Fast metric retrieval for performance-critical operations."""
    try:
        # Direct cache access for performance
        from . import cache
        
        # Get metric from cache
        metric_key = f"metric_{metric_name}"
        return cache.cache_get_fast(metric_key)
        
    except Exception as e:
        logger.error(f"Fast metric retrieval failed: {str(e)}")
        return None

# ===== SECTION 12: CONTEXT MANAGEMENT AND CORRELATION FUNCTIONS =====

def create_metrics_context(operation: str, **kwargs) -> Dict[str, Any]:
    """Create metrics context with correlation ID for operation tracking."""
    try:
        # Use utility gateway for correlation ID generation
        from . import utility
        
        context = {
            'operation': operation,
            'correlation_id': utility.generate_correlation_id(),
            'timestamp': time.time(),
            'context_data': kwargs
        }
        
        # Record context creation metric
        record_metric("metrics_context_created", 1.0, {
            'operation': operation,
            'correlation_id': context['correlation_id']
        })
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to create metrics context: {str(e)}")
        return {'operation': operation, 'error': str(e)}

def close_metrics_context(context: Dict[str, Any], success: bool = True, **kwargs) -> bool:
    """Close metrics context and record final metrics."""
    try:
        if 'correlation_id' in context:
            # Record context completion
            record_metric("metrics_context_completed", 1.0, {
                'operation': context.get('operation', 'unknown'),
                'correlation_id': context['correlation_id'],
                'success': str(success)
            })
            
            # Calculate duration if start time available
            if 'timestamp' in context:
                duration = time.time() - context['timestamp']
                record_metric("metrics_context_duration", duration, {
                    'operation': context.get('operation', 'unknown'),
                    'correlation_id': context['correlation_id']
                })
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to close metrics context: {str(e)}")
        return False

# EOF
