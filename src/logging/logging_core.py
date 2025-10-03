"""
Logging Core - Template Optimized with Generic Operations
Version: 2025.10.03.01
Description: Structured logging with template-based message generation and generic operations

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
from typing import Dict, Any, Optional
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


class LoggingCore:
    """Core logging manager with template optimization and generic operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._stats = {
            'info_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'debug_count': 0,
            'template_usage': 0
        }
    
    def log_template_fast(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """Log using template for ultra-fast performance."""
        if not _USE_LOG_TEMPLATES:
            self._log_template_legacy(template, *args, level=level)
            return
        
        try:
            if template == LogTemplate.CACHE_HIT:
                message = _CACHE_HIT_LOG % (args[0], args[1]) if len(args) >= 2 else "Cache hit"
            elif template == LogTemplate.CACHE_MISS:
                message = _CACHE_MISS_LOG % args[0] if args else "Cache miss"
            elif template == LogTemplate.HA_SUCCESS:
                message = _HA_SUCCESS_LOG % (args[0], args[1]) if len(args) >= 2 else "HA success"
            elif template == LogTemplate.HA_ERROR:
                message = _HA_ERROR_LOG % (args[0], args[1]) if len(args) >= 2 else "HA error"
            elif template == LogTemplate.HTTP_REQUEST:
                message = _HTTP_REQUEST_LOG % (args[0], args[1]) if len(args) >= 2 else "HTTP request"
            elif template == LogTemplate.HTTP_SUCCESS:
                message = _HTTP_SUCCESS_LOG % (args[0], args[1]) if len(args) >= 2 else "HTTP success"
            elif template == LogTemplate.OPERATION_START:
                message = _OPERATION_START_LOG % (args[0], args[1]) if len(args) >= 2 else "Operation start"
            elif template == LogTemplate.OPERATION_SUCCESS:
                message = _OPERATION_SUCCESS_LOG % (args[0], args[1]) if len(args) >= 2 else "Operation success"
            elif template == LogTemplate.LAMBDA_START:
                message = _LAMBDA_START_LOG % args[0] if args else "Lambda start"
            elif template == LogTemplate.METRIC_RECORD:
                message = _METRIC_RECORD_LOG % (args[0], args[1]) if len(args) >= 2 else "Metric recorded"
            elif template == LogTemplate.MODULE_LOAD:
                message = _MODULE_LOAD_LOG % (args[0], args[1]) if len(args) >= 2 else "Module loaded"
            elif template == LogTemplate.MODULE_UNLOAD:
                message = _MODULE_UNLOAD_LOG % args[0] if args else "Module unloaded"
            elif template == LogTemplate.CIRCUIT_OPEN:
                message = _CIRCUIT_OPEN_LOG % args[0] if args else "Circuit opened"
            elif template == LogTemplate.CIRCUIT_CLOSE:
                message = _CIRCUIT_CLOSE_LOG % args[0] if args else "Circuit closed"
            else:
                message = " ".join(str(arg) for arg in args)
            
            self.logger.log(level, message)
            self._stats['template_usage'] += 1
            
        except Exception:
            self._log_template_legacy(template, *args, level=level)
    
    def _log_template_legacy(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """Legacy template logging."""
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            'info_count': self._stats['info_count'],
            'error_count': self._stats['error_count'],
            'warning_count': self._stats['warning_count'],
            'debug_count': self._stats['debug_count'],
            'template_usage': self._stats['template_usage']
        }


_MANAGER = LoggingCore()


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


def log_template_fast(template: LogTemplate, *args, level: int = logging.INFO) -> None:
    """Public interface for fast template logging."""
    _MANAGER.log_template_fast(template, *args, level=level)


def get_logging_stats() -> Dict[str, Any]:
    """Public interface for logging statistics."""
    return _MANAGER.get_stats()


__all__ = [
    'LogOperation',
    'LogTemplate',
    'log_template_fast',
    'get_logging_stats',
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
]
