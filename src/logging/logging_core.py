"""
Logging Core - Centralized Logging Implementation
Version: 2025.09.30.02
Description: Logging implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for operation metrics

OPTIMIZATION: Phase 1 Complete
- Integrated record_operation_metrics() from shared_utilities
- Consistent metric recording patterns
- Enhanced observability

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import json
import sys
import time
from datetime import datetime
from typing import Any, Optional, Dict
from enum import Enum


class LogLevel(Enum):
    """Log levels."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LoggingCore:
    """Centralized logging with structured output and metrics integration."""
    
    def __init__(self):
        self.level = LogLevel.INFO
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method with metrics tracking."""
        start_time = time.time()
        success = True
        
        try:
            if level.value >= self.level.value:
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': level.name,
                    'message': message
                }
                
                if 'error' in kwargs and kwargs['error']:
                    log_entry['error'] = str(kwargs['error'])
                    log_entry['error_type'] = type(kwargs['error']).__name__
                
                for key, value in kwargs.items():
                    if key != 'error':
                        log_entry[key] = value
                
                print(json.dumps(log_entry), file=sys.stdout)
        except Exception:
            success = False
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics(level.name.lower(), execution_time, success)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with metrics tracking."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with metrics tracking."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with metrics tracking."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with metrics tracking."""
        self._log(LogLevel.ERROR, message, error=error, **kwargs)
    
    def set_level(self, level: LogLevel):
        """Set logging level."""
        self.level = level
    
    def _record_metrics(self, operation: str, execution_time: float, success: bool):
        """Record operation metrics using shared utilities."""
        try:
            from .shared_utilities import record_operation_metrics
            record_operation_metrics(
                interface="logging",
                operation=operation,
                execution_time=execution_time,
                success=success
            )
        except Exception:
            pass


_LOGGER = LoggingCore()


def _execute_debug_implementation(message: str, **kwargs):
    """Execute debug log operation."""
    return _LOGGER.debug(message, **kwargs)


def _execute_info_implementation(message: str, **kwargs):
    """Execute info log operation."""
    return _LOGGER.info(message, **kwargs)


def _execute_warning_implementation(message: str, **kwargs):
    """Execute warning log operation."""
    return _LOGGER.warning(message, **kwargs)


def _execute_error_implementation(message: str, error: Optional[Exception] = None, **kwargs):
    """Execute error log operation."""
    return _LOGGER.error(message, error=error, **kwargs)


def _execute_set_level_implementation(level: str, **kwargs):
    """Execute set log level operation."""
    _LOGGER.set_level(LogLevel[level.upper()])


__all__ = [
    '_execute_debug_implementation',
    '_execute_info_implementation',
    '_execute_warning_implementation',
    '_execute_error_implementation',
    '_execute_set_level_implementation',
]

# EOF
