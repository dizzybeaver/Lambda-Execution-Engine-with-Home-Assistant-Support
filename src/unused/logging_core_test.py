"""
logging_core.py
Version: 2025.10.15.02
Description: Unified logging with dispatcher timing integration (Phase 4 Task #7)

PHASE 4 TASK #7 - Ultra-Integration:
- Simplified _record_dispatcher_metric() to use centralized METRICS operation
- Now uses gateway.execute_operation(METRICS, 'record_dispatcher_timing')
- Eliminates 12 lines of duplicate metric recording logic

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

import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from enum import Enum
from collections import deque
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== LOGGING OPERATION ENUM =====

class LogOperation(Enum):
    """Enumeration of all logging operations."""
    LOG_INFO = "log_info"
    LOG_ERROR = "log_error"
    LOG_WARNING = "log_warning"
    LOG_DEBUG = "log_debug"
    LOG_OPERATION_START = "log_operation_start"
    LOG_OPERATION_SUCCESS = "log_operation_success"
    LOG_OPERATION_FAILURE = "log_operation_failure"
    LOG_WITH_TEMPLATE = "log_with_template"
    GET_ERROR_ENTRIES = "get_error_entries"
    GET_STATS = "get_stats"
    CLEAR_ERROR_ENTRIES = "clear_error_entries"


@dataclass
class ErrorEntry:
    """Error entry with metadata."""
    timestamp: float
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# ===== LOGGING CORE IMPLEMENTATION =====

class LoggingCore:
    """Singleton logging manager with unified operations."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._stats = {
            'info_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'debug_count': 0,
            'template_usage': {}
        }
        self.error_entries: deque = deque(maxlen=100)
        self.total_errors_logged = 0
    
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        logger.info(message, extra=extra or {})
        with self._lock:
            self._stats['info_count'] += 1
    
    def log_error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        if error:
            logger.error(f"{message}: {str(error)}", extra=extra or {}, exc_info=True)
        else:
            logger.error(message, extra=extra or {})
        
        with self._lock:
            self._stats['error_count'] += 1
            self.total_errors_logged += 1
            self.error_entries.append(ErrorEntry(
                timestamp=time.time(),
                error_type=type(error).__name__ if error else 'Unknown',
                message=message,
                stack_trace=str(error) if error else None,
                context=extra
            ))
    
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        logger.warning(message, extra=extra or {})
        with self._lock:
            self._stats['warning_count'] += 1
    
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        logger.debug(message, extra=extra or {})
        with self._lock:
            self._stats['debug_count'] += 1
    
    def log_with_template(self, template: str, **kwargs) -> None:
        """Log with template."""
        message = template.format(**kwargs)
        logger.info(message)
        with self._lock:
            self._stats['info_count'] += 1
            if template not in self._stats['template_usage']:
                self._stats['template_usage'][template] = 0
            self._stats['template_usage'][template] += 1
    
    def get_error_entries(self) -> List[Dict[str, Any]]:
        """Get recent error entries."""
        with self._lock:
            return [
                {
                    'timestamp': e.timestamp,
                    'error_type': e.error_type,
                    'message': e.message,
                    'stack_trace': e.stack_trace,
                    'context': e.context
                }
                for e in self.error_entries
            ]
    
    def clear_error_entries(self) -> int:
        """Clear error entries."""
        with self._lock:
            count = len(self.error_entries)
            self.error_entries.clear()
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            return {
                'info_count': self._stats['info_count'],
                'error_count': self._stats['error_count'],
                'warning_count': self._stats['warning_count'],
                'debug_count': self._stats['debug_count'],
                'template_usage': self._stats['template_usage'],
                'error_responses_logged': self.total_errors_logged,
                'error_entries_stored': len(self.error_entries)
            }


_MANAGER = LoggingCore()


# ===== GENERIC OPERATION EXECUTION =====

def execute_logging_operation(operation: LogOperation, *args, **kwargs):
    """Universal logging operation executor with dispatcher performance monitoring."""
    start_time = time.time()
    
    if not _USE_GENERIC_OPERATIONS:
        result = _execute_legacy_operation(operation, *args, **kwargs)
    else:
        result = _execute_generic_operation(operation, *args, **kwargs)
    
    duration_ms = (time.time() - start_time) * 1000
    _record_dispatcher_metric(operation, duration_ms)
    
    return result


def _execute_generic_operation(operation: LogOperation, *args, **kwargs):
    """Execute logging operation using generic dispatcher."""
    try:
        method_name = operation.value
        method = getattr(_MANAGER, method_name, None)
        
        if method is None:
            return None
        
        return method(*args, **kwargs)
    except Exception as e:
        logger.error(f"Operation {operation.value} failed: {str(e)}")
        return None


def _execute_legacy_operation(operation: LogOperation, *args, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    try:
        method = getattr(_MANAGER, operation.value)
        return method(*args, **kwargs)
    except Exception as e:
        logger.error(f"Legacy operation {operation.value} failed: {str(e)}")
        return None


def _record_dispatcher_metric(operation: LogOperation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation (Phase 4 Task #7)."""
    try:
        from gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.METRICS,
            'record_dispatcher_timing',
            interface_name='LoggingCore',
            operation_name=operation.value,
            duration_ms=duration_ms
        )
    except Exception:
        pass


# ===== COMPATIBILITY LAYER =====

def _execute_log_info_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log info operation."""
    execute_logging_operation(LogOperation.LOG_INFO, message, extra)


def _execute_log_error_implementation(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log error operation."""
    execute_logging_operation(LogOperation.LOG_ERROR, message, error, extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log warning operation."""
    execute_logging_operation(LogOperation.LOG_WARNING, message, extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log debug operation."""
    execute_logging_operation(LogOperation.LOG_DEBUG, message, extra)


def _execute_log_operation_start_implementation(operation: str, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Execute log operation start."""
    if not correlation_id:
        from gateway import execute_operation, GatewayInterface
        correlation_id = execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
    extra = {'correlation_id': correlation_id, 'operation': operation}
    if context:
        extra.update(context)
    _MANAGER.log_info(f"Operation started: {operation}", extra=extra)
    return correlation_id


def _execute_log_operation_success_implementation(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None, result: Any = None, **kwargs) -> None:
    """Execute log operation success."""
    extra = {'operation': operation, 'duration_ms': duration_ms, 'status': 'success'}
    if correlation_id:
        extra['correlation_id'] = correlation_id
    if result:
        extra['result_summary'] = str(result)[:100]
    _MANAGER.log_info(f"Operation completed: {operation} ({duration_ms:.2f}ms)", extra=extra)


def _execute_log_operation_failure_implementation(operation: str, error: Exception, duration_ms: float = 0, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log operation failure."""
    extra = {'operation': operation, 'duration_ms': duration_ms, 'status': 'failure'}
    if correlation_id:
        extra['correlation_id'] = correlation_id
    if context:
        extra.update(context)
    _MANAGER.log_error(f"Operation failed: {operation} ({duration_ms:.2f}ms)", error, extra)


# ===== EXPORTS =====

__all__ = [
    'LogOperation',
    'execute_logging_operation',
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
]

# EOF
