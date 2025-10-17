"""
logging_manager.py - Core logging manager implementation
Version: 2025.10.14.01
Description: LoggingCore class with template optimization and error tracking

DESIGN DECISIONS:
=================
1. Threading Locks in Lambda:
   - Uses threading.Lock() (self._lock, self.error_lock) despite Lambda being single-threaded
   - Reason: Defensive programming for potential future multi-threaded use cases
   - Lambda Impact: Minimal overhead (~microseconds per lock acquisition)
   - Trade-off: Safety over micro-optimization

2. Dual Error Storage:
   - error_entries: deque(maxlen=100) - Simple error tracking
   - error_log_entries: deque(maxlen=1000) - Structured error responses with analytics
   - Reason: Different use cases - simple errors vs HTTP error responses
   - error_entries: For general exceptions and errors
   - error_log_entries: For API error responses with status codes, correlation IDs
   - Memory: ~100KB total (acceptable for 128MB Lambda)

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
from collections import deque
from datetime import datetime

from logging_types import (
    LogTemplate, ErrorEntry, ErrorLogEntry, ErrorLogLevel
)

_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'

logging.basicConfig(level=logging.INFO)


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
        if _USE_LOG_TEMPLATES:
            message = f"[OP_FAILURE]: {operation} ({duration_ms:.2f}ms)"
        else:
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
        """
        Log an error response and return entry ID.
        
        DESIGN DECISION: Stores in error_log_entries (not error_entries)
        Reason: This is for structured HTTP error responses with analytics
        error_log_entries tracks status codes, modules, severity levels
        """
        entry_id = str(uuid.uuid4())
        
        error_entry = ErrorLogEntry(
            entry_id=entry_id,
            timestamp=time.time(),
            status_code=error_response.get('statusCode', 500),
            error_message=error_response.get('body', {}).get('error', 'Unknown error'),
            correlation_id=correlation_id or str(uuid.uuid4()),
            source_module=source_module or 'unknown',
            lambda_request_id=getattr(lambda_context, 'aws_request_id', None) if lambda_context else None,
            error_level=ErrorLogLevel.from_status_code(error_response.get('statusCode', 500)),
            additional_context=additional_context
        )
        
        with self.error_lock:
            self.error_log_entries.append(error_entry)
            self.total_errors_logged += 1
        
        return entry_id
    
    def get_error_response_analytics(self) -> Dict[str, Any]:
        """Get analytics on error responses."""
        with self.error_lock:
            if not self.error_log_entries:
                return {
                    'total_errors': 0,
                    'by_status_code': {},
                    'by_module': {},
                    'by_severity': {},
                    'time_range': None
                }
            
            by_status = {}
            by_module = {}
            by_severity = {}
            
            for entry in self.error_log_entries:
                # By status code
                by_status[entry.status_code] = by_status.get(entry.status_code, 0) + 1
                # By module
                by_module[entry.source_module] = by_module.get(entry.source_module, 0) + 1
                # By severity
                severity = entry.error_level.name
                by_severity[severity] = by_severity.get(severity, 0) + 1
            
            timestamps = [e.timestamp for e in self.error_log_entries]
            
            return {
                'total_errors': len(self.error_log_entries),
                'by_status_code': by_status,
                'by_module': by_module,
                'by_severity': by_severity,
                'time_range': {
                    'start': min(timestamps),
                    'end': max(timestamps),
                    'duration_seconds': max(timestamps) - min(timestamps)
                }
            }
    
    def clear_error_response_logs(self) -> int:
        """Clear error response logs and return count of cleared entries."""
        with self.error_lock:
            count = len(self.error_log_entries)
            self.error_log_entries.clear()
            return count
    
    def get_error_entries(self) -> List[ErrorEntry]:
        """Get recent error entries."""
        return list(self.error_entries)
    
    def clear_errors(self) -> int:
        """Clear error entries and return count cleared."""
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


# ===== SINGLETON INSTANCE =====

_MANAGER = LoggingCore()


# ===== EXPORTS =====

__all__ = [
    'LoggingCore',
    '_MANAGER',
]

# EOF
