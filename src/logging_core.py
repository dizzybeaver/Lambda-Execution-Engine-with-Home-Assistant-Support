"""
logging_core.py
Version: 2025.10.14.01
Description: Unified logging with template-based messages, generic operations, and error response tracking

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

import logging
import time
import os
import json
import uuid
import threading
from typing import Dict, Any, Optional, List, Deque
from datetime import datetime, timedelta
from collections import deque
from enum import Enum

# Log message templates for ultra-fast generation
_CACHE_HIT_LOG = "Cache hit: %s (access_count=%d)"
_CACHE_MISS_LOG = "Cache miss: %s"
_HA_SUCCESS_LOG = "HA operation success: %s (%.2fms)"
_HA_ERROR_LOG = "HA operation failed: %s - %s"
_HTTP_REQUEST_LOG = "HTTP %s %s"
_HTTP_SUCCESS_LOG = "HTTP success: %d (%.2fms)"
_OPERATION_START_LOG = "Operation started: %s [%s]"
_OPERATION_SUCCESS_LOG = "Operation completed: %s (%.2fms)"
_LAMBDA_START_LOG = "Lambda invocation started [%s]"
_METRIC_RECORD_LOG = "Metric recorded: %s = %.2f"
_MODULE_LOAD_LOG = "Module loaded: %s (%.2fms)"
_MODULE_UNLOAD_LOG = "Module unloaded: %s"
_CIRCUIT_OPEN_LOG = "Circuit breaker opened: %s"
_CIRCUIT_CLOSE_LOG = "Circuit breaker closed: %s"

_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'

logger = logging.getLogger(__name__)

# ===== ENUMERATIONS =====

class LogOperation(Enum):
    """Generic logging operations."""
    LOG_INFO = "log_info"
    LOG_ERROR = "log_error"
    LOG_WARNING = "log_warning"
    LOG_DEBUG = "log_debug"
    LOG_START = "log_operation_start"
    LOG_SUCCESS = "log_operation_success"
    LOG_TEMPLATE = "log_template"


class LogTemplate(Enum):
    """Log message templates."""
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    HA_SUCCESS = "ha_success"
    HA_ERROR = "ha_error"
    HTTP_REQUEST = "http_request"
    HTTP_SUCCESS = "http_success"
    OPERATION_START = "operation_start"
    OPERATION_SUCCESS = "operation_success"
    LAMBDA_START = "lambda_start"
    METRIC_RECORD = "metric_record"
    MODULE_LOAD = "module_load"
    MODULE_UNLOAD = "module_unload"
    CIRCUIT_OPEN = "circuit_open"
    CIRCUIT_CLOSE = "circuit_close"


class ErrorLogLevel(Enum):
    """Error log level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== ERROR RESPONSE DATA STRUCTURES =====

class ErrorLogEntry:
    """Individual error log entry."""
    
    def __init__(self, 
                 error_response: Dict[str, Any],
                 correlation_id: str,
                 source_module: Optional[str] = None,
                 lambda_context = None,
                 additional_context: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.datetime = datetime.utcnow()
        self.error_response = error_response
        self.correlation_id = correlation_id
        self.source_module = source_module or "unknown"
        self.lambda_context_info = self._extract_lambda_context(lambda_context)
        self.additional_context = additional_context or {}
        
        self.error_type = self._determine_error_type(error_response)
        self.severity = self._determine_severity(error_response)
        self.status_code = error_response.get('statusCode', 500)
        
    def _extract_lambda_context(self, lambda_context) -> Dict[str, Any]:
        """Extract relevant information from Lambda context."""
        if not lambda_context:
            return {}
            
        return {
            'request_id': getattr(lambda_context, 'aws_request_id', 'unknown'),
            'function_name': getattr(lambda_context, 'function_name', 'unknown'),
            'function_version': getattr(lambda_context, 'function_version', 'unknown'),
            'memory_limit': getattr(lambda_context, 'memory_limit_in_mb', 'unknown'),
            'remaining_time': getattr(lambda_context, 'get_remaining_time_in_millis', lambda: 0)()
        }
        
    def _determine_error_type(self, error_response: Dict[str, Any]) -> str:
        """Determine error type from response."""
        body = error_response.get('body', {})
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except:
                pass
        
        if isinstance(body, dict):
            return body.get('error_type', 'UNKNOWN')
        
        status_code = error_response.get('statusCode', 500)
        
        if status_code == 400:
            return "validation_error"
        elif status_code == 401:
            return "authentication_error"
        elif status_code == 403:
            return "authorization_error"
        elif status_code == 404:
            return "not_found_error"
        elif status_code == 429:
            return "rate_limit_error"
        elif status_code >= 500:
            return "server_error"
        else:
            return "client_error"
            
    def _determine_severity(self, error_response: Dict[str, Any]) -> ErrorLogLevel:
        """Determine severity level from response."""
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


# ===== UNIFIED LOGGING CORE =====

class LoggingCore:
    """Unified logging manager with template optimization, generic operations, and error response tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._stats = {
            'info_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'debug_count': 0,
            'template_usage': 0
        }
        
        # Error response tracking
        self.max_error_entries = 1000
        self.error_entries: Deque[ErrorLogEntry] = deque(maxlen=self.max_error_entries)
        self.error_lock = threading.Lock()
        self.error_created_at = time.time()
        self.total_errors_logged = 0
    
    def log_template_fast(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """Log using template for ultra-fast performance."""
        message = f"{template.value}: {' '.join(str(arg) for arg in args)}"
        self.logger.log(level, message)
    
    def execute_log_operation(self, operation: LogOperation, *args, **kwargs) -> None:
        """Generic logging operation executor."""
        if operation == LogOperation.LOG_INFO:
            message = args[0] if args else kwargs.get('message', '')
            extra = kwargs.get('extra')
            self.log_info(message, extra)
        elif operation == LogOperation.LOG_ERROR:
            message = args[0] if args else kwargs.get('message', '')
            error = args[1] if len(args) > 1 else kwargs.get('error')
            extra = kwargs.get('extra')
            self.log_error(message, error, extra)
        elif operation == LogOperation.LOG_WARNING:
            message = args[0] if args else kwargs.get('message', '')
            extra = kwargs.get('extra')
            self.log_warning(message, extra)
        elif operation == LogOperation.LOG_DEBUG:
            message = args[0] if args else kwargs.get('message', '')
            extra = kwargs.get('extra')
            self.log_debug(message, extra)
        elif operation == LogOperation.LOG_START:
            operation_name = args[0] if args else kwargs.get('operation', '')
            correlation_id = args[1] if len(args) > 1 else kwargs.get('correlation_id', '')
            self.log_operation_start(operation_name, correlation_id)
        elif operation == LogOperation.LOG_SUCCESS:
            operation_name = args[0] if args else kwargs.get('operation', '')
            duration_ms = args[1] if len(args) > 1 else kwargs.get('duration_ms', 0)
            self.log_operation_success(operation_name, duration_ms)
        elif operation == LogOperation.LOG_TEMPLATE:
            template = args[0] if args else kwargs.get('template')
            template_args = args[1:] if len(args) > 1 else kwargs.get('args', ())
            level = kwargs.get('level', logging.INFO)
            self.log_template_fast(template, *template_args, level=level)
    
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self.logger.info(message, extra=extra or {})
        self._stats['info_count'] += 1
    
    def log_error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        if error:
            self.logger.error(f"{message}: {str(error)}", extra=extra or {}, exc_info=True)
        else:
            self.logger.error(message, extra=extra or {})
        self._stats['error_count'] += 1
    
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=extra or {})
        self._stats['warning_count'] += 1
    
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=extra or {})
        self._stats['debug_count'] += 1
    
    def log_operation_start(self, operation: str, correlation_id: str = "") -> None:
        """Log operation start."""
        if _USE_LOG_TEMPLATES:
            message = _OPERATION_START_LOG % (operation, correlation_id)
            self.logger.info(message)
            self._stats['template_usage'] += 1
        else:
            self.logger.info(f"Operation started: {operation} [{correlation_id}]")
        self._stats['info_count'] += 1
    
    def log_operation_success(self, operation: str, duration_ms: float = 0) -> None:
        """Log operation success."""
        if _USE_LOG_TEMPLATES:
            message = _OPERATION_SUCCESS_LOG % (operation, duration_ms)
            self.logger.info(message)
            self._stats['template_usage'] += 1
        else:
            self.logger.info(f"Operation completed: {operation} ({duration_ms:.2f}ms)")
        self._stats['info_count'] += 1
    
    def log_error_response(self, 
                          error_response: Dict[str, Any],
                          correlation_id: Optional[str] = None,
                          source_module: Optional[str] = None,
                          lambda_context = None,
                          additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Log an error response and return entry ID."""
        try:
            if not correlation_id:
                if lambda_context:
                    correlation_id = getattr(lambda_context, 'aws_request_id', str(uuid.uuid4()))
                else:
                    correlation_id = str(uuid.uuid4())
                    
            entry = ErrorLogEntry(
                error_response=error_response,
                correlation_id=correlation_id,
                source_module=source_module,
                lambda_context=lambda_context,
                additional_context=additional_context
            )
            
            with self.error_lock:
                self.error_entries.append(entry)
                self.total_errors_logged += 1
                
            # Record metrics if available
            try:
                from gateway import execute_operation, GatewayInterface
                execute_operation(
                    GatewayInterface.METRICS,
                    'record_error',
                    error_type=entry.error_type,
                    severity=entry.severity.value,
                    category='error_response',
                    context={
                        'status_code': entry.status_code,
                        'source_module': entry.source_module,
                        'has_lambda_context': bool(lambda_context)
                    }
                )
            except:
                pass
            
            logger.debug(f"Logged error response: {entry.id} ({entry.error_type})")
            return entry.id
            
        except Exception as e:
            logger.error(f"Failed to log error response: {e}")
            return f"error_{uuid.uuid4()}"
    
    def get_error_analytics(self, 
                           time_range_minutes: int = 60,
                           include_details: bool = False) -> Dict[str, Any]:
        """Get error analytics for specified time range."""
        try:
            cutoff_time = time.time() - (time_range_minutes * 60)
            
            with self.error_lock:
                relevant_entries = [
                    entry for entry in self.error_entries 
                    if entry.timestamp >= cutoff_time
                ]
                
            analytics = {
                'time_range_minutes': time_range_minutes,
                'total_errors': len(relevant_entries),
                'error_types': {},
                'severity_breakdown': {},
                'status_code_breakdown': {},
                'source_modules': {},
                'timestamp': time.time()
            }
            
            for entry in relevant_entries:
                analytics['error_types'][entry.error_type] = analytics['error_types'].get(entry.error_type, 0) + 1
                
                severity = entry.severity.value
                analytics['severity_breakdown'][severity] = analytics['severity_breakdown'].get(severity, 0) + 1
                
                status_code = str(entry.status_code)
                analytics['status_code_breakdown'][status_code] = analytics['status_code_breakdown'].get(status_code, 0) + 1
                
                module = entry.source_module
                analytics['source_modules'][module] = analytics['source_modules'].get(module, 0) + 1
                
            if include_details:
                analytics['entries'] = [entry.to_dict() for entry in relevant_entries[-10:]]
                
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get error analytics: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    def clear_error_logs(self, older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Clear error logs, optionally filtered by age."""
        try:
            with self.error_lock:
                if older_than_minutes is None:
                    cleared_count = len(self.error_entries)
                    self.error_entries.clear()
                else:
                    cutoff_time = time.time() - (older_than_minutes * 60)
                    original_count = len(self.error_entries)
                    self.error_entries = deque(
                        [entry for entry in self.error_entries if entry.timestamp >= cutoff_time],
                        maxlen=self.max_error_entries
                    )
                    cleared_count = original_count - len(self.error_entries)
                    
            return {
                'status': 'success',
                'cleared_count': cleared_count,
                'remaining_count': len(self.error_entries),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear error logs: {e}")
            return {'status': 'error', 'error': str(e), 'timestamp': time.time()}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive logging statistics."""
        return {
            'info_count': self._stats['info_count'],
            'error_count': self._stats['error_count'],
            'warning_count': self._stats['warning_count'],
            'debug_count': self._stats['debug_count'],
            'template_usage': self._stats['template_usage'],
            'error_responses_logged': self.total_errors_logged,
            'error_entries_stored': len(self.error_entries)
        }


# ===== SINGLETON INSTANCE =====

_MANAGER = LoggingCore()


# ===== IMPLEMENTATION FUNCTIONS FOR GATEWAY =====

def _execute_log_info_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log info operation."""
    _MANAGER.execute_log_operation(LogOperation.LOG_INFO, message, extra=extra)


def _execute_log_error_implementation(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log error operation."""
    _MANAGER.execute_log_operation(LogOperation.LOG_ERROR, message, error, extra=extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log warning operation."""
    _MANAGER.execute_log_operation(LogOperation.LOG_WARNING, message, extra=extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log debug operation."""
    _MANAGER.execute_log_operation(LogOperation.LOG_DEBUG, message, extra=extra)


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
    extra = {'operation': operation, 'duration_ms': duration_ms, 'status': 'failure', 'error_type': type(error).__name__}
    if correlation_id:
        extra['correlation_id'] = correlation_id
    if context:
        extra.update(context)
    _MANAGER.log_error(f"Operation failed: {operation} ({duration_ms:.2f}ms)", error=error, extra=extra)


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


# ===== PUBLIC INTERFACE =====

def log_template_fast(template: LogTemplate, *args, level: int = logging.INFO) -> None:
    """Public interface for fast template logging."""
    _MANAGER.log_template_fast(template, *args, level=level)


def get_logging_stats() -> Dict[str, Any]:
    """Public interface for logging statistics."""
    return _MANAGER.get_stats()


# ===== EXPORTS =====

__all__ = [
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorLogEntry',
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
