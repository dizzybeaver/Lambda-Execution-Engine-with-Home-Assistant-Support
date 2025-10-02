"""
logging_extensions.py - Logging Extensions
Version: 2025.10.02.02
Description: Extends existing logging_core.py with correlation and profiling

ARCHITECTURE: EXTENSION - Extends existing logging_core.py
- Uses shared_utilities and gateway exclusively
- Wraps existing logging functions
- Adds correlation layer only

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP + LUGS Compatible
"""

from typing import Dict, Any, Optional
import time

def log_with_correlation(level: str, message: str, correlation_id: str = None, **metadata) -> None:
    """Log with correlation ID using existing logging."""
    from gateway import log_info, log_error, log_warning, log_debug, generate_correlation_id
    
    cid = correlation_id or generate_correlation_id()
    enriched_metadata = {'correlation_id': cid, **metadata}
    
    log_func = {
        'INFO': log_info,
        'ERROR': log_error,
        'WARNING': log_warning,
        'DEBUG': log_debug
    }.get(level.upper(), log_info)
    
    log_func(message, extra=enriched_metadata)


def start_operation_trace(operation_name: str, module: str) -> str:
    """Start operation trace using existing context."""
    from shared_utilities import create_operation_context
    
    context = create_operation_context(module, operation_name)
    return context['correlation_id']


def end_operation_trace(correlation_id: str, success: bool = True, result: Any = None) -> None:
    """End operation trace using existing context."""
    from shared_utilities import close_operation_context
    from gateway import cache_get
    
    context = cache_get(f"operation_context_{correlation_id}")
    if context:
        close_operation_context(context, success=success, result=result)


def get_operation_trace(correlation_id: str) -> Dict[str, Any]:
    """Get operation trace using existing functions."""
    from gateway import cache_get, create_success_response, create_error_response
    
    context = cache_get(f"operation_context_{correlation_id}")
    if not context:
        return create_error_response("Trace not found", 'TRACE_NOT_FOUND')
    
    return create_success_response("Trace retrieved", context)


def record_performance_metric(operation: str, duration_ms: float) -> None:
    """Record performance metric using existing metrics."""
    from gateway import record_metric
    from shared_utilities import record_operation_metrics
    
    record_operation_metrics(
        interface='performance',
        operation=operation,
        execution_time=duration_ms,
        success=True
    )
    
    record_metric(f'perf.{operation}.duration_ms', duration_ms)


def get_performance_profile(operation: str = None) -> Dict[str, Any]:
    """Get performance profile using existing stats."""
    from shared_utilities import get_utility_performance_stats
    from gateway import create_success_response
    
    stats = get_utility_performance_stats()
    
    if operation:
        op_stats = stats.get('operation_stats', {}).get(operation, {})
        return create_success_response(f"Profile for {operation}", op_stats)
    
    return create_success_response("Performance profiles", stats)


# EOF
