"""
logging_manager.py - Core logging manager implementation
Version: 2025.10.21.01
Description: LoggingCore class with template optimization and error tracking

MAJOR DESIGN DECISION - Module-Level Singleton:
===============================================
LoggingCore uses module-level singleton (_LOGGING_CORE) instead of SINGLETON interface.

WHY: Performance-critical hot-path optimization
- Logging called on EVERY operation (10-100+ times per Lambda invocation)
- SINGLETON interface adds gateway routing overhead (~1-5µs per call)
- With 100 log calls: 100-500µs wasted per invocation
- Module-level access: Direct reference, ~0.1µs (10-50x faster)

TRADE-OFFS:
- Pro: Zero routing overhead, maximum performance
- Pro: Python guarantees singleton at module level
- Pro: Simpler initialization (no factory needed)
- Con: Cannot use singleton_clear() from gateway
- Con: Less consistent with other interfaces
- DECISION: Performance critical enough to warrant exception

REFERENCES:
- DEC-04: Lambda single-threaded (no locking needed)
- LESS-06: Hot-path optimization principles
- DEC-XX: Module-level singleton for logging (this decision)
- See: Logging Optimization Plan (2025-10-21) for full analysis

CHANGELOG:
- 2025.10.21.01: Added singleton documentation + DEBUG_MODE support + documentation standards
- 2025.10.18.01: Fixed ErrorLogLevel enum usage (Issue #15) - HIGH/MEDIUM/LOW/CRITICAL
- 2025.10.17.04: Removed threading locks (Issue #14) - Lambda single-threaded optimization
- 2025.10.17.03: Fixed inconsistent error log limits (Issue #10) - Both use 100 limit
- 2025.10.14.01: Added design decision documentation for threading and dual storage

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
from typing import Dict, Any, Optional, List
from collections import deque
from datetime import datetime

from logging_types import (
    LogTemplate, ErrorEntry, ErrorLogEntry, ErrorLogLevel
)

# Configuration
_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'

# DEBUG_MODE support (DEC-22)
def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled for flow visibility."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str, component: str = 'LOGGING_MANAGER'):
    """Print debug message if DEBUG_MODE=true (DEC-22)."""
    if _is_debug_mode():
        print(f"[{component}_DEBUG] {msg}")

# Initialize Python logging
logging.basicConfig(level=logging.INFO)


class LoggingCore:
    """
    Unified logging manager with template optimization and generic operations.
    
    LAMBDA OPTIMIZED: No threading locks (single-threaded per container).
    MODULE-LEVEL SINGLETON: For hot-path performance (see header docs).
    """
    
    def __init__(self):
        """Initialize logging core with tracking structures."""
        _print_debug("Initializing LoggingCore")
        
        # Core logger instance
        self.logger = logging.getLogger('LambdaExecutionEngine')
        _print_debug(f"Logger initialized: {self.logger.name}")
        
        # Error tracking (Fixed Issue #10: consistent 100 limit)
        self.max_error_entries = 100
        self.error_entries: deque = deque(maxlen=100)
        self.error_log_entries: deque = deque(maxlen=100)
        self.operation_logs: deque = deque(maxlen=1000)
        _print_debug(f"Tracking initialized: error_entries={len(self.error_entries)}, "
                    f"error_log_entries={len(self.error_log_entries)}, "
                    f"operation_logs={len(self.operation_logs)}")
        
        # Template counters (no lock needed in single-threaded Lambda)
        self._template_hits = 0
        self._template_fallbacks = 0
        _print_debug("Template counters initialized")
    
    # ===== CORE LOGGING =====
    
    def log(self, message: str, level: int = logging.INFO, **kwargs) -> None:
        """
        Core logging with optional metadata.
        
        Args:
            message: Log message
            level: Python logging level (INFO, WARNING, ERROR, etc.)
            **kwargs: Additional metadata to include in log
        """
        _print_debug(f"log() called: level={level}, message='{message[:50]}...'")
        self.logger.log(level, message, extra=kwargs)
    
    def log_template_fast(self, template: LogTemplate, *args, level: int = logging.INFO) -> None:
        """
        Log using template for ultra-fast performance.
        
        Uses pre-formatted templates to minimize string formatting overhead.
        Falls back to string conversion if templates disabled.
        
        Args:
            template: LogTemplate enum value
            *args: Arguments to format into template
            level: Python logging level
        """
        # DESIGN: Branch optimization - check once at module level
        if _USE_LOG_TEMPLATES:
            message = template.value.format(*args) if args else template.value
            self._template_hits += 1
            _print_debug(f"Template hit: {template.name}, hits={self._template_hits}")
        else:
            message = str(args[0]) if args else template.value
            self._template_fallbacks += 1
            _print_debug(f"Template fallback, fallbacks={self._template_fallbacks}")
        
        self.logger.log(level, message)
    
    # ===== ERROR TRACKING =====
    
    def log_error(self, message: str, error_code: Optional[str] = None,
                  correlation_id: Optional[str] = None, **kwargs) -> None:
        """
        Log error with tracking.
        
        Adds error to tracking deque for analytics and debugging.
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            correlation_id: Optional correlation ID for request tracking
            **kwargs: Additional context
        """
        _print_debug(f"log_error() called: error_code={error_code}, "
                    f"correlation_id={correlation_id}")
        
        entry = ErrorEntry(
            timestamp=time.time(),
            error_type=error_code or 'UNKNOWN_ERROR',
            message=str(message)
        )
        
        self.error_entries.append(entry)
        _print_debug(f"Error entry added, total={len(self.error_entries)}")
        
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
        
        Used for HTTP error responses with analytics tracking.
        
        Args:
            message: Error message
            status_code: HTTP status code (default 500)
            error_code: Optional error code
            correlation_id: Optional correlation ID
            level: ErrorLogLevel severity
            **kwargs: Additional context
            
        Returns:
            Dict containing error response structure
        """
        _print_debug(f"log_error_response() called: status={status_code}, "
                    f"level={level.value}, correlation_id={correlation_id}")
        
        # DESIGN: Structured error response for API consistency
        error_response = {
            'error': error_code or 'INTERNAL_ERROR',
            'message': message,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat(),
            'correlation_id': correlation_id
        }
        
        # Track for analytics
        entry = ErrorLogEntry(
            id=correlation_id or f"err_{int(time.time()*1000)}",
            timestamp=time.time(),
            datetime=datetime.now(),
            correlation_id=correlation_id or 'unknown',
            source_module='logging_manager',
            error_type=error_code or 'INTERNAL_ERROR',
            severity=level,
            status_code=status_code,
            error_response=error_response,
            lambda_context_info=None,
            additional_context=kwargs
        )
        
        self.error_log_entries.append(entry)
        _print_debug(f"Error response entry added, total={len(self.error_log_entries)}")
        
        # Log with appropriate level
        log_level = {
            ErrorLogLevel.LOW: logging.INFO,
            ErrorLogLevel.MEDIUM: logging.WARNING,
            ErrorLogLevel.HIGH: logging.ERROR,
            ErrorLogLevel.CRITICAL: logging.CRITICAL
        }.get(level, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"[{error_code}] {message}",
            extra={
                'correlation_id': correlation_id,
                'status_code': status_code,
                'severity': level.value,
                **kwargs
            }
        )
        
        return error_response
    
    # ===== OPERATION TRACKING =====
    
    def log_operation_start(self, operation: str, correlation_id: Optional[str] = None,
                           **kwargs) -> None:
        """
        Log operation start for performance tracking.
        
        Args:
            operation: Operation name
            correlation_id: Optional correlation ID
            **kwargs: Additional context
        """
        _print_debug(f"Operation start: {operation}, correlation_id={correlation_id}")
        
        self.logger.info(
            f"Operation started: {operation}",
            extra={
                'correlation_id': correlation_id,
                'operation': operation,
                **kwargs
            }
        )
    
    def log_operation_success(self, operation: str, duration_ms: float,
                             correlation_id: Optional[str] = None, **kwargs) -> None:
        """
        Log operation success with duration.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            correlation_id: Optional correlation ID
            **kwargs: Additional context
        """
        _print_debug(f"Operation success: {operation}, duration={duration_ms:.2f}ms, "
                    f"correlation_id={correlation_id}")
        
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
        """
        Log operation failure.
        
        Args:
            operation: Operation name
            error: Error description
            correlation_id: Optional correlation ID
            **kwargs: Additional context
        """
        _print_debug(f"Operation failure: {operation}, error={error}, "
                    f"correlation_id={correlation_id}")
        
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
        """
        Get analytics from error response logs.
        
        Provides counts by status code, error code, and severity level.
        
        Returns:
            Dict with analytics breakdown
        """
        _print_debug(f"get_error_response_analytics() called, "
                    f"entries={len(self.error_log_entries)}")
        
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
            by_code[entry.error_type] = by_code.get(entry.error_type, 0) + 1
            
            # Count by severity
            severity = entry.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        analytics = {
            'total_errors': len(self.error_log_entries),
            'by_status_code': by_status,
            'by_error_code': by_code,
            'by_severity': by_severity
        }
        _print_debug(f"Analytics: {analytics['total_errors']} errors")
        return analytics
    
    # ===== STATS =====
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dict with counts for errors, operations, template usage
        """
        stats = {
            'error_count': len(self.error_entries),
            'error_response_count': len(self.error_log_entries),
            'operation_log_count': len(self.operation_logs),
            'template_hits': self._template_hits,
            'template_fallbacks': self._template_fallbacks
        }
        _print_debug(f"get_stats() called: {stats}")
        return stats
    
    # ===== CLEANUP =====
    
    def clear_errors(self) -> int:
        """Clear error entries and return count cleared."""
        count = len(self.error_entries)
        self.error_entries.clear()
        _print_debug(f"clear_errors(): cleared {count} entries")
        return count
    
    def clear_error_responses(self) -> int:
        """Clear error response entries and return count cleared."""
        count = len(self.error_log_entries)
        self.error_log_entries.clear()
        _print_debug(f"clear_error_responses(): cleared {count} entries")
        return count
    
    def clear_operation_logs(self) -> int:
        """Clear operation logs and return count cleared."""
        count = len(self.operation_logs)
        self.operation_logs.clear()
        _print_debug(f"clear_operation_logs(): cleared {count} entries")
        return count
    
    def clear_all(self) -> Dict[str, int]:
        """
        Clear all tracking data.
        
        Returns:
            Dict with counts of cleared entries by type
        """
        _print_debug("clear_all() called")
        result = {
            'errors_cleared': self.clear_errors(),
            'error_responses_cleared': self.clear_error_responses(),
            'operation_logs_cleared': self.clear_operation_logs()
        }
        _print_debug(f"clear_all() result: {result}")
        return result


# ===== MODULE-LEVEL SINGLETON =====
# DESIGN: Direct module-level instance for hot-path performance
# See header MAJOR DESIGN DECISION for rationale

_print_debug("Creating module-level singleton _LOGGING_CORE")
_LOGGING_CORE = LoggingCore()
_MANAGER = _LOGGING_CORE  # Alias for compatibility with logging_core.py
_print_debug("Module-level singleton created")


# ===== MODULE EXPORTS =====

__all__ = [
    'LoggingCore',
    '_LOGGING_CORE',
    '_MANAGER',
]

# EOF
