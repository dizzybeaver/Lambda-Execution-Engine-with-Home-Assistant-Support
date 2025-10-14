"""
logging_core.py - Unified logging with dispatcher timing integration
Version: 2025.10.15.02
Description: Complete logging with templates, error tracking, and dispatcher timing (Phase 4 Task #7)

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
import uuid
from typing import Dict, Any, Optional, List
from enum import Enum
from collections import deque
from dataclasses import dataclass
from datetime import datetime

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'
_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    LOG_TEMPLATE_FAST = "log_template_fast"
    GET_ERROR_ENTRIES = "get_error_entries"
    GET_STATS = "get_stats"
    CLEAR_ERROR_ENTRIES = "clear_error_entries"
    LOG_ERROR_RESPONSE = "log_error_response"
    GET_ERROR_ANALYTICS = "get_error_analytics"
    CLEAR_ERROR_LOGS = "clear_error_logs"


class LogTemplate(Enum):
    """Pre-formatted log templates for optimal performance."""
    OPERATION_START = "[OP_START]"
    OPERATION_SUCCESS = "[OP_SUCCESS]"
    OPERATION_FAILURE = "[OP_FAIL]"
    CACHE_HIT = "[CACHE_HIT]"
    CACHE_MISS = "[CACHE_MISS]"


class ErrorLogLevel(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== ERROR ENTRY DATACLASSES =====

@dataclass
class ErrorEntry:
    """Simple error entry with metadata."""
    timestamp: float
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ErrorLogEntry:
    """Structured error response log entry."""
    id: str
    timestamp: float
    datetime: datetime
    correlation_id: str
    source_module: Optional[str]
    error_type: str
    severity: ErrorLogLevel
    status_code: int
    error_response: Dict[str, Any]
    lambda_context_info: Optional[Dict[str, Any]]
    additional_context: Optional[Dict[str, Any]]
    
    @staticmethod
    def determine_severity(error_response: Dict[str, Any]) -> ErrorLogLevel:
        """Determine severity from error response."""
        status_code = error_response.get('statusCode', 500)
        
        if status_code >= 500:
            return ErrorLogLevel.HIGH
        elif status_code in [401, 403]:
            return ErrorLogLevel.MEDIUM
        elif status_code == 429:
            return ErrorLogLevel.MEDIUM
        else:
            return ErrorLogLevel.LOW
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'datetime': self.datetime.isoformat(),
            'correlation_id': self.correlation_id,
            'source_module': self.source_module,
            'error_type': self.error_type,
            'severity': self.severity.value,
            'status_code': self.status_code,
            'error_response': self.error_response,
            'lambda_context': self.lambda_context_info,
            'additional_context': self.additional_context
        }


# ===== LOGGING CORE IMPLEMENTATION =====

class LoggingCore:
    """Unified logging manager with template optimization and generic operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._stats = {
            'info_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'debug_count': 0,
            'template_usage': {},
            'operation_starts': 0,
            'operation_successes': 0,
            'operation_failures': 0
        }
        
        # Error response tracking
        self.max_error_entries = 1000
        self.error_entries: deque = deque(maxlen=100)  # Simple errors
        self.error_log_entries: deque = deque(maxlen=self.max_error_entries)  # Structured errors
        self.error_lock = threading.Lock()
        self.error_created_at = time.time()
        self.total_errors_logged = 0
    
    def log_template_fast(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """Log using template for ultra-fast performance."""
        message = f"{template.value}: {' '.join(str(arg) for arg in args)}"
        self.logger.log(level, message)
        with self._lock:
            self._stats['template_usage'][template.value] = self._stats['template_usage'].get(template.value, 0) + 1
    
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(message, extra=extra or {})
        with self._lock:
            self._stats['info_count'] += 1
    
    def log_error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        if error:
            self.logger.error(f"{message}: {str(error)}", extra=extra or {}, exc_info=True)
        else:
            self.logger.error(message, extra=extra or {})
        
        with self._lock:
            self._stats['error_count'] += 1
            self.total_errors_logged += 1
            # Store in simple error entries
            self.error_entries.append(ErrorEntry(
                timestamp=time.time(),
                error_type=type(error).__name__ if error else 'Unknown',
                message=message,
                stack_trace=str(error) if error else None,
                context=extra
            ))
    
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=extra or {})
        with self._lock:
            self._stats['warning_count'] += 1
    
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=extra or {})
        with self._lock:
            self._stats['debug_count'] += 1
    
    def log_operation_start(self, operation: str, correlation_id: str = "") -> None:
        """Log operation start."""
        if _USE_LOG_TEMPLATES:
            message = f"[OP_START]: {operation} [{correlation_id}]"
            self.logger.info(message)
        else:
            self.logger.info(f"Operation started: {operation} [{correlation_id}]")
        with self._lock:
            self._stats['info_count'] += 1
            self._stats['operation_starts'] += 1
    
    def log_operation_success(self, operation: str, duration_ms: float = 0, result: Any = None, correlation_id: str = "") -> None:
        """Log operation success."""
        if _USE_LOG_TEMPLATES:
            message = f"[OP_SUCCESS]: {operation} ({duration_ms:.2f}ms)"
        else:
            message = f"Operation completed: {operation} ({duration_ms:.2f}ms)"
        
        extra = {}
        if correlation_id:
            extra['correlation_id'] = correlation_id
        if result:
            extra['result_summary'] = str(result)[:100]
        
        self.logger.info(message, extra=extra if extra else None)
        with self._lock:
            self._stats['info_count'] += 1
            self._stats['operation_successes'] += 1
    
    def log_operation_failure(self, operation: str, error: Exception, duration_ms: float = 0, correlation_id: str = "", context: Optional[Dict[str, Any]] = None) -> None:
        """Log operation failure."""
        message = f"Operation failed: {operation} ({duration_ms:.2f}ms)"
        extra = {'operation': operation, 'duration_ms': duration_ms, 'status': 'failure'}
        if correlation_id:
            extra['correlation_id'] = correlation_id
        if context:
            extra.update(context)
        
        self.log_error(message, error, extra)
        with self._lock:
            self._stats['operation_failures'] += 1
    
    def log_with_template(self, template_name: str, **params) -> None:
        """Log using template string."""
        templates = {
            'cache_hit': "Cache hit for key: {key}",
            'cache_miss': "Cache miss for key: {key}",
            'operation_timing': "Operation {name} took {duration_ms:.2f}ms"
        }
        
        if template_name in templates:
            message = templates[template_name].format(**params)
            self.logger.info(message)
            with self._lock:
                self._stats['info_count'] += 1
                self._stats['template_usage'][template_name] = self._stats['template_usage'].get(template_name, 0) + 1
    
    def log_error_response(self, 
                          error_response: Dict[str, Any],
                          correlation_id: Optional[str] = None,
                          source_module: Optional[str] = None,
                          lambda_context = None,
                          additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Log an error response and return entry ID."""
        entry_id = str(uuid.uuid4())
        current_time = time.time()
        
        # Extract lambda context info if provided
        lambda_context_info = None
        if lambda_context:
            lambda_context_info = {
                'request_id': getattr(lambda_context, 'aws_request_id', None),
                'function_name': getattr(lambda_context, 'function_name', None),
                'memory_limit': getattr(lambda_context, 'memory_limit_in_mb', None),
                'remaining_time': getattr(lambda_context, 'get_remaining_time_in_millis', lambda: None)()
            }
        
        # Determine error type and severity
        error_body = error_response.get('body', {})
        if isinstance(error_body, str):
            error_type = 'GenericError'
        else:
            error_type = error_body.get('error', {}).get('type', 'UnknownError')
        
        severity = ErrorLogEntry.determine_severity(error_response)
        
        # Create structured log entry
        entry = ErrorLogEntry(
            id=entry_id,
            timestamp=current_time,
            datetime=datetime.fromtimestamp(current_time),
            correlation_id=correlation_id or '',
            source_module=source_module,
            error_type=error_type,
            severity=severity,
            status_code=error_response.get('statusCode', 500),
            error_response=error_response,
            lambda_context_info=lambda_context_info,
            additional_context=additional_context
        )
        
        with self.error_lock:
            self.error_log_entries.append(entry)
            self.total_errors_logged += 1
        
        # Also log to standard logger
        self.logger.error(f"Error response logged: {error_type} [{severity.value}] - {entry_id}")
        
        return entry_id
    
    def get_error_entries(self) -> List[Dict[str, Any]]:
        """Get simple error entries."""
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
    
    def get_error_analytics(self, time_range_minutes: int = 60, include_details: bool = False) -> Dict[str, Any]:
        """Get error response analytics."""
        current_time = time.time()
        cutoff_time = current_time - (time_range_minutes * 60)
        
        with self.error_lock:
            recent_entries = [e for e in self.error_log_entries if e.timestamp >= cutoff_time]
            
            analytics = {
                'time_range_minutes': time_range_minutes,
                'total_errors': len(recent_entries),
                'errors_by_type': {},
                'errors_by_severity': {level.value: 0 for level in ErrorLogLevel},
                'errors_by_status_code': {},
                'errors_by_module': {}
            }
            
            for entry in recent_entries:
                # By type
                analytics['errors_by_type'][entry.error_type] = analytics['errors_by_type'].get(entry.error_type, 0) + 1
                
                # By severity
                analytics['errors_by_severity'][entry.severity.value] += 1
                
                # By status code
                status_code = str(entry.status_code)
                analytics['errors_by_status_code'][status_code] = analytics['errors_by_status_code'].get(status_code, 0) + 1
                
                # By module
                if entry.source_module:
                    analytics['errors_by_module'][entry.source_module] = analytics['errors_by_module'].get(entry.source_module, 0) + 1
            
            if include_details:
                analytics['recent_errors'] = [entry.to_dict() for entry in recent_entries[-10:]]
            
            return analytics
    
    def clear_error_entries(self) -> int:
        """Clear simple error entries."""
        with self._lock:
            count = len(self.error_entries)
            self.error_entries.clear()
            return count
    
    def clear_error_logs(self, older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Clear error logs older than specified minutes."""
        with self.error_lock:
            if older_than_minutes is None:
                cleared_count = len(self.error_log_entries)
                self.error_log_entries.clear()
            else:
                current_time = time.time()
                cutoff_time = current_time - (older_than_minutes * 60)
                original_count = len(self.error_log_entries)
                self.error_log_entries = deque(
                    (e for e in self.error_log_entries if e.timestamp >= cutoff_time),
                    maxlen=self.max_error_entries
                )
                cleared_count = original_count - len(self.error_log_entries)
            
            return {
                'cleared_count': cleared_count,
                'remaining_count': len(self.error_log_entries)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            return {
                'info_count': self._stats['info_count'],
                'error_count': self._stats['error_count'],
                'warning_count': self._stats['warning_count'],
                'debug_count': self._stats['debug_count'],
                'template_usage': self._stats['template_usage'].copy(),
                'error_responses_logged': self.total_errors_logged,
                'error_entries_stored': len(self.error_entries),
                'error_log_entries_stored': len(self.error_log_entries),
                'operation_starts': self._stats['operation_starts'],
                'operation_successes': self._stats['operation_successes'],
                'operation_failures': self._stats['operation_failures']
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
    return execute_logging_operation(LogOperation.LOG_INFO, message, extra=extra)


def _execute_log_error_implementation(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log error operation."""
    return execute_logging_operation(LogOperation.LOG_ERROR, message, error=error, extra=extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log warning operation."""
    return execute_logging_operation(LogOperation.LOG_WARNING, message, extra=extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log debug operation."""
    return execute_logging_operation(LogOperation.LOG_DEBUG, message, extra=extra)


def _execute_log_operation_start_implementation(operation: str, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Execute log operation start."""
    if not correlation_id:
        from gateway import execute_operation, GatewayInterface
        correlation_id = execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
    
    execute_logging_operation(LogOperation.LOG_OPERATION_START, operation, correlation_id)
    return correlation_id


def _execute_log_operation_success_implementation(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None, result: Any = None, **kwargs) -> None:
    """Execute log operation success."""
    return execute_logging_operation(LogOperation.LOG_OPERATION_SUCCESS, operation, duration_ms, result, correlation_id)


def _execute_log_operation_failure_implementation(operation: str, error: Exception, duration_ms: float = 0, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log operation failure."""
    return execute_logging_operation(LogOperation.LOG_OPERATION_FAILURE, operation, error, duration_ms, correlation_id, context)


# ===== PUBLIC INTERFACE =====

def log_template_fast(template: LogTemplate, *args, level: int = logging.INFO) -> None:
    """Public interface for fast template logging."""
    _MANAGER.log_template_fast(template, *args, level=level)


def get_logging_stats() -> Dict[str, Any]:
    """Public interface for logging statistics."""
    return _MANAGER.get_stats()


# ===== ERROR RESPONSE TRACKING INTERNAL FUNCTIONS =====

def _log_error_response_internal(error_response: Dict[str, Any], 
                                correlation_id: Optional[str] = None,
                                source_module: Optional[str] = None,
                                lambda_context = None,
                                additional_context: Optional[Dict[str, Any]] = None) -> str:
    """Internal implementation for logging error responses."""
    return _MANAGER.log_error_response(
        error_response=error_response,
        correlation_id=correlation_id,
        source_module=source_module,
        lambda_context=lambda_context,
        additional_context=additional_context
    )


def _get_error_response_analytics_internal(time_range_minutes: int = 60,
                                          include_details: bool = False) -> Dict[str, Any]:
    """Internal implementation for getting error response analytics."""
    return _MANAGER.get_error_analytics(time_range_minutes, include_details)


def _clear_error_response_logs_internal(older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
    """Internal implementation for clearing error response logs."""
    return _MANAGER.clear_error_logs(older_than_minutes)


# ===== EXPORTS =====

__all__ = [
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorLogEntry',
    'ErrorEntry',
    'LoggingCore',
    'execute_logging_operation',
    'log_template_fast',
    'get_logging_stats',
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
    '_log_error_response_internal',
    '_get_error_response_analytics_internal',
    '_clear_error_response_logs_internal',
]

# EOF
