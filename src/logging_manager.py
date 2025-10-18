"""
logging_manager.py - Core logging manager implementation
Version: 2025.10.18.01
Description: LoggingCore class with template optimization and error tracking

CHANGELOG:
- 2025.10.18.01: FIXED ErrorLogLevel enum usage (Issue #15)
  - Changed ErrorLogLevel.ERROR to ErrorLogLevel.HIGH (doesn't exist in enum)
  - Changed ErrorLogLevel.WARNING to ErrorLogLevel.MEDIUM (doesn't exist in enum)
  - Updated log_level mapping dict to include all four valid enum values
  - Enum only has: LOW, MEDIUM, HIGH, CRITICAL
- 2025.10.17.04: REMOVED threading locks for Lambda optimization (Issue #14 fix)
  - Removed self._lock and self.error_lock
  - Removed all "with self._lock:" and "with self.error_lock:" blocks
  - Lambda is definitively single-threaded per container
  - Removes ~microseconds overhead per log operation
  - Updated design decisions documentation
- 2025.10.17.03: Fixed inconsistent error log limits (Issue #10)
  - Reduced max_error_entries from 1000 to 100
  - Both error_entries and error_log_entries now use consistent 100 limit
  - Updated design decision documentation
- 2025.10.14.01: Added design decision documentation for threading and dual storage

DESIGN DECISIONS:
=================
1. Threading Locks REMOVED (UPDATED 2025.10.17.04):
   PREVIOUS: Used threading.Lock() (self._lock, self.error_lock) for "defensive programming"
   DECISION: REMOVED for Lambda optimization (Issue #14)
   Reason: Lambda is definitively single-threaded per container
   Performance Gain: Eliminates ~microseconds overhead per log operation
   Lambda Context: Single-threaded execution model is AWS Lambda architecture
   NOT A REGRESSION: Lambda will never support multi-threading per container
   Code Clarity: Explicit Lambda-specific implementation

2. Dual Error Storage (FIXED - Now Consistent Limits):
   - error_entries: deque(maxlen=100) - Simple error tracking
   - error_log_entries: deque(maxlen=100) - Structured error responses with analytics
   - Reason: Different use cases - simple errors vs HTTP error responses
   - error_entries: For general exceptions and errors
   - error_log_entries: For API error responses with status codes, correlation IDs
   - Memory: ~10KB total (100 entries × ~100 bytes each)
   - FIXED: Previously error_log_entries used maxlen=1000 (inconsistent, too large for Lambda)
   - Lambda 128MB: 10KB is 0.008% of available memory (acceptable)

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
    """Unified logging manager with template optimization and generic operations.
    
    LAMBDA OPTIMIZED: No threading locks (single-threaded per container).
    """
    
    def __init__(self):
        # REMOVED: self._lock = threading.Lock() (Issue #14 fix)
        # REMOVED: self.error_lock = threading.Lock() (Issue #14 fix)
        
        self.logger = logging.getLogger('LambdaExecutionEngine')
        self.max_error_entries = 100  # Fixed in Issue #10
        self.error_entries: deque = deque(maxlen=100)
        self.error_log_entries: deque = deque(maxlen=100)  # Fixed in Issue #10
        self.operation_logs: deque = deque(maxlen=1000)
        
        # Template counters (no lock needed in single-threaded Lambda)
        self._template_hits = 0
        self._template_fallbacks = 0
    
    # ===== CORE LOGGING =====
    
    def log(self, message: str, level: int = logging.INFO, **kwargs) -> None:
        """Core logging with optional metadata."""
        # No lock needed - Lambda is single-threaded
        self.logger.log(level, message, extra=kwargs)
    
    def log_template_fast(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """Log using template for ultra-fast performance."""
        # No lock needed - Lambda is single-threaded
        if _USE_LOG_TEMPLATES:
            message = template.value.format(*args) if args else template.value
            self._template_hits += 1
        else:
            message = str(args[0]) if args else template.value
            self._template_fallbacks += 1
        
        self.logger.log(level, message)
    
    # ===== ERROR TRACKING =====
    
    def log_error(self, message: str, error_code: Optional[str] = None,
                  correlation_id: Optional[str] = None, **kwargs) -> None:
        """Log error with tracking."""
        # No lock needed - Lambda is single-threaded
        entry = ErrorEntry(
            timestamp=time.time(),
            error_type=error_code or 'UNKNOWN_ERROR',
            message=str(message)
        )
        
        self.error_entries.append(entry)
        
        self.logger.error(
            f"[{entry.error_type}] {entry.message}",
            extra={
                'correlation_id': correlation_id,
                'error_type': entry.error_type,
                **kwargs
            }
        )
    
    def log_error_response(self, message: str, status_code: int = 500,
                          error_code: Optional[str] = None,
                          correlation_id: Optional[str] = None,
                          level: ErrorLogLevel = ErrorLogLevel.HIGH,
                          **kwargs) -> Dict[str, Any]:
        """
        Log error and return error response dict.
        
        DESIGN DECISION: Dual error storage
        - error_entries: Simple errors (exceptions, failures)
        - error_log_entries: HTTP error responses (status codes, analytics)
        Different use cases, both limited to 100 entries for Lambda safety
        """
        # No lock needed - Lambda is single-threaded
        entry = ErrorLogEntry(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            datetime=datetime.now(),
            correlation_id=correlation_id or str(uuid.uuid4()),
            source_module=None,
            error_type=error_code or 'INTERNAL_ERROR',
            severity=level,
            status_code=status_code,
            error_response={'message': str(message), 'statusCode': status_code},
            lambda_context_info=None,
            additional_context=kwargs if kwargs else None
        )
        
        self.error_log_entries.append(entry)
        
        # FIXED: Map all four valid ErrorLogLevel enum values to Python logging levels
        log_level = {
            ErrorLogLevel.LOW: logging.INFO,
            ErrorLogLevel.MEDIUM: logging.WARNING,
            ErrorLogLevel.HIGH: logging.ERROR,
            ErrorLogLevel.CRITICAL: logging.CRITICAL
        }.get(level, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"[{status_code}] [{entry.error_type}] {message}",
            extra={
                'correlation_id': entry.correlation_id,
                'status_code': status_code,
                'error_type': entry.error_type,
                **kwargs
            }
        )
        
        return {
            'error': message,
            'status_code': status_code,
            'error_code': entry.error_type,
            'correlation_id': entry.correlation_id,
            'timestamp': entry.timestamp
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent error entries."""
        # No lock needed - Lambda is single-threaded
        recent = list(self.error_entries)[-count:]
        return [
            {
                'timestamp': entry.timestamp,
                'error_type': entry.error_type,
                'message': entry.message
            }
            for entry in recent
        ]
    
    def get_recent_error_responses(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent error response entries."""
        # No lock needed - Lambda is single-threaded
        recent = list(self.error_log_entries)[-count:]
        return [
            {
                'timestamp': entry.timestamp,
                'error_type': entry.error_type,
                'status_code': entry.status_code,
                'correlation_id': entry.correlation_id,
                'severity': entry.severity.value
            }
            for entry in recent
        ]
    
    # ===== OPERATION LOGGING =====
    
    def log_operation_start(self, operation: str, correlation_id: Optional[str] = None,
                           **kwargs) -> str:
        """Log operation start and return correlation ID."""
        # No lock needed - Lambda is single-threaded
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        entry = {
            'correlation_id': correlation_id,
            'operation': operation,
            'start_time': time.time(),
            'status': 'started',
            **kwargs
        }
        
        self.operation_logs.append(entry)
        
        self.logger.info(
            f"Operation started: {operation}",
            extra={'correlation_id': correlation_id, **kwargs}
        )
        
        return correlation_id
    
    def log_operation_success(self, operation: str, duration_ms: float,
                             correlation_id: Optional[str] = None,
                             result: Optional[Any] = None, **kwargs) -> None:
        """Log operation success."""
        # No lock needed - Lambda is single-threaded
        self.logger.info(
            f"Operation succeeded: {operation} ({duration_ms:.2f}ms)",
            extra={
                'correlation_id': correlation_id,
                'duration_ms': duration_ms,
                'operation': operation,
                **kwargs
            }
        )
    
    def log_operation_failure(self, operation: str, error: str,
                             correlation_id: Optional[str] = None, **kwargs) -> None:
        """Log operation failure."""
        # No lock needed - Lambda is single-threaded
        self.logger.error(
            f"Operation failed: {operation} - {error}",
            extra={
                'correlation_id': correlation_id,
                'operation': operation,
                'error': error,
                **kwargs
            }
        )
    
    # ===== ERROR ANALYTICS =====
    
    def get_error_response_analytics(self) -> Dict[str, Any]:
        """Get analytics from error response logs."""
        # No lock needed - Lambda is single-threaded
        if not self.error_log_entries:
            return {
                'total_errors': 0,
                'by_status_code': {},
                'by_error_code': {},
                'by_severity': {}
            }
        
        by_status = {}
        by_code = {}
        by_severity = {}
        
        for entry in self.error_log_entries:
            # Count by status code
            by_status[entry.status_code] = by_status.get(entry.status_code, 0) + 1
            
            # Count by error code
            by_code[entry.error_code] = by_code.get(entry.error_code, 0) + 1
            
            # Count by severity
            severity = entry.level.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_errors': len(self.error_log_entries),
            'by_status_code': by_status,
            'by_error_code': by_code,
            'by_severity': by_severity
        }
    
    # ===== STATS =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        # No lock needed - Lambda is single-threaded
        return {
            'error_count': len(self.error_entries),
            'error_response_count': len(self.error_log_entries),
            'operation_log_count': len(self.operation_logs),
            'template_hits': self._template_hits,
            'template_fallbacks': self._template_fallbacks
        }
    
    # ===== CLEANUP =====
    
    def clear_errors(self) -> int:
        """Clear error entries."""
        # No lock needed - Lambda is single-threaded
        count = len(self.error_entries)
        self.error_entries.clear()
        return count
    
    def clear_error_responses(self) -> int:
        """Clear error response entries."""
        # No lock needed - Lambda is single-threaded
        count = len(self.error_log_entries)
        self.error_log_entries.clear()
        return count
    
    def clear_operation_logs(self) -> int:
        """Clear operation logs."""
        # No lock needed - Lambda is single-threaded
        count = len(self.operation_logs)
        self.operation_logs.clear()
        return count
    
    def clear_all(self) -> Dict[str, int]:
        """Clear all tracking data."""
        # No lock needed - Lambda is single-threaded
        return {
            'errors_cleared': self.clear_errors(),
            'error_responses_cleared': self.clear_error_responses(),
            'operation_logs_cleared': self.clear_operation_logs()
        }


# ===== GLOBAL INSTANCE =====

_LOGGING_CORE = LoggingCore()
_MANAGER = _LOGGING_CORE  # Alias for compatibility with logging_core.py


# ===== MODULE EXPORTS =====

__all__ = [
    'LoggingCore',
    '_LOGGING_CORE',
    '_MANAGER',
]

# EOF
