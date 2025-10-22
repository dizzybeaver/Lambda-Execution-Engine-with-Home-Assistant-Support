"""
logging_manager.py - Core logging manager (SECURITY HARDENED)
Version: 2025.10.21.03
Description: LoggingCore class with rate limiting and validation

SECURITY ENHANCEMENTS (2025.10.21.03):
- Fixed ErrorEntry dataclass usage
- Rate limiting: MAX_LOGS_PER_INVOCATION to prevent log flooding
- LOG_LEVEL validation: Prevents misconfiguration
- Invocation tracking: Reset log count per Lambda invocation
- Enhanced error tracking with limits

CHANGELOG:
- 2025.10.21.03: Fixed ErrorEntry usage (removed ErrorLogEntry)
- 2025.10.21.02: SECURITY HARDENING - Rate limiting + LOG_LEVEL validation
- 2025.10.21.01: Added singleton docs + DEBUG_MODE support + documentation standards
- 2025.10.18.01: Fixed ErrorLogLevel enum usage (Issue #15)
- 2025.10.17.04: Removed threading locks (Issue #14)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from collections import deque
from datetime import datetime

from logging_types import LogTemplate, ErrorEntry, ErrorLogLevel

# ===== CONFIGURATION =====

_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'false').lower() == 'true'
MAX_LOGS_PER_INVOCATION = int(os.environ.get('MAX_LOGS_PER_INVOCATION', '500'))
LOG_RATE_LIMIT_ENABLED = os.environ.get('LOG_RATE_LIMIT_ENABLED', 'true').lower() == 'true'
VALID_LOG_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}

# ===== DEBUG_MODE SUPPORT =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled for flow visibility."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str, component: str = 'LOGGING_MANAGER'):
    """Print debug message if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[{component}_DEBUG] {msg}")

_print_debug("Loading logging_manager.py module")

# ===== LOGGING CONFIGURATION =====

def _get_validated_log_level() -> int:
    """Get and validate LOG_LEVEL environment variable."""
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    if log_level_str not in VALID_LOG_LEVELS:
        print(f"[LOGGING_MANAGER_WARNING] Invalid LOG_LEVEL='{log_level_str}', "
              f"must be one of {VALID_LOG_LEVELS}. Defaulting to INFO.")
        log_level_str = 'INFO'
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map[log_level_str]
    _print_debug(f"Log level set to: {log_level_str} ({level})")
    return level

logging.basicConfig(
    level=_get_validated_log_level(),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ===== RATE LIMITING TRACKER =====

class RateLimitTracker:
    """Track log count per Lambda invocation for rate limiting."""
    
    def __init__(self):
        self.invocation_id = None
        self.log_count = 0
        self.limit_warning_shown = False
    
    def reset_for_invocation(self, invocation_id: str):
        """Reset counter for new Lambda invocation."""
        self.invocation_id = invocation_id
        self.log_count = 0
        self.limit_warning_shown = False
        _print_debug(f"Rate limit tracker reset for invocation: {invocation_id}")
    
    def increment(self) -> bool:
        """Increment log count and check if limit exceeded."""
        self.log_count += 1
        
        if not LOG_RATE_LIMIT_ENABLED:
            return True
        
        if self.log_count > MAX_LOGS_PER_INVOCATION:
            if not self.limit_warning_shown:
                print(f"[LOGGING_MANAGER_RATE_LIMIT] Log limit of {MAX_LOGS_PER_INVOCATION} "
                      f"exceeded for invocation {self.invocation_id}. Suppressing further logs.")
                self.limit_warning_shown = True
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        return {
            'invocation_id': self.invocation_id,
            'log_count': self.log_count,
            'limit': MAX_LOGS_PER_INVOCATION,
            'limit_exceeded': self.log_count > MAX_LOGS_PER_INVOCATION if LOG_RATE_LIMIT_ENABLED else False,
            'rate_limiting_enabled': LOG_RATE_LIMIT_ENABLED
        }

_RATE_LIMITER = RateLimitTracker()

# ===== LOGGING CORE =====

class LoggingCore:
    """Unified logging manager with template optimization and rate limiting."""
    
    def __init__(self):
        """Initialize logging core."""
        self.logger = logging.getLogger('SUGA-ISP')
        self._templates: Dict[str, LogTemplate] = {}
        self._template_hits = 0
        self._template_misses = 0
        self._error_log: deque = deque(maxlen=100)
        self._error_count_by_type: Dict[str, int] = {}
        
        _print_debug("LoggingCore initialized with rate limiting")
    
    def set_invocation_id(self, invocation_id: str):
        """Set Lambda invocation ID and reset rate limiter."""
        _RATE_LIMITER.reset_for_invocation(invocation_id)
    
    def log(self, message: str, level: int = logging.INFO, **kwargs) -> None:
        """Core logging with rate limiting."""
        if not _RATE_LIMITER.increment():
            return
        
        if _USE_LOG_TEMPLATES:
            template_key = self._get_template_key(message)
            
            if template_key in self._templates:
                template = self._templates[template_key]
                self._template_hits += 1
                self.logger.log(level, f"[T{id(template)}] {message}", extra=kwargs)
            else:
                self._templates[template_key] = message
                self._template_misses += 1
                self.logger.log(level, message, extra=kwargs)
        else:
            self.logger.log(level, message, extra=kwargs)
    
    def log_error_with_tracking(self, message: str, error: Optional[str] = None, 
                               level: ErrorLogLevel = ErrorLogLevel.MEDIUM, **kwargs) -> None:
        """Log error with tracking and rate limiting."""
        if not _RATE_LIMITER.increment():
            return
        
        entry = ErrorEntry(
            timestamp=datetime.now(),
            error_type=kwargs.get('error_type', 'UnknownError'),
            message=message,
            level=level,
            details=error
        )
        
        self._error_log.append(entry)
        
        error_type = entry.error_type
        self._error_count_by_type[error_type] = self._error_count_by_type.get(error_type, 0) + 1
        
        level_map = {
            ErrorLogLevel.LOW: logging.WARNING,
            ErrorLogLevel.MEDIUM: logging.ERROR,
            ErrorLogLevel.HIGH: logging.ERROR,
            ErrorLogLevel.CRITICAL: logging.CRITICAL
        }
        
        log_level = level_map.get(level, logging.ERROR)
        self.logger.log(log_level, f"{message}: {error}" if error else message, extra=kwargs)
    
    def reset(self) -> bool:
        """
        Reset logging core to initial state (Phase 1 addition).
        
        Clears all logs, templates, errors, and resets counters.
        Useful for testing and debugging.
        
        Returns:
            True on success
        """
        self._templates.clear()
        self._template_hits = 0
        self._template_misses = 0
        self._error_log.clear()
        self._error_count_by_type.clear()
        
        # Reset rate limiter
        global _RATE_LIMITER
        _RATE_LIMITER.log_count = 0
        _RATE_LIMITER.limit_warning_shown = False
        
        _print_debug("LoggingCore reset complete")
        return True
    
    def _get_template_key(self, message: str) -> str:
        """Generate template key from message."""
        return message[:100]
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics."""
        return {
            'templates_cached': len(self._templates),
            'template_hits': self._template_hits,
            'template_misses': self._template_misses,
            'hit_rate': (self._template_hits / (self._template_hits + self._template_misses) * 100
                        if (self._template_hits + self._template_misses) > 0 else 0.0)
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error tracking statistics."""
        return {
            'total_errors': len(self._error_log),
            'errors_by_type': self._error_count_by_type.copy(),
            'recent_errors': [
                {
                    'timestamp': entry.timestamp.isoformat(),
                    'type': entry.error_type,
                    'message': entry.message,
                    'level': entry.level.value
                }
                for entry in list(self._error_log)[-10:]
            ]
        }
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        return _RATE_LIMITER.get_stats()

# ===== MODULE-LEVEL SINGLETON =====

_LOGGING_CORE = LoggingCore()
_print_debug("Module-level singleton _LOGGING_CORE created")

def get_logging_core() -> LoggingCore:
    """
    Get the logging core singleton (Phase 1 SINGLETON integration).
    
    SINGLETON Pattern:
    Tries to use SINGLETON interface for lifecycle management.
    Falls back to module-level singleton if SINGLETON unavailable.
    
    Returns:
        LoggingCore instance
    """
    global _LOGGING_CORE
    
    # Try SINGLETON interface first (Phase 1)
    try:
        from gateway import singleton_get, singleton_register
        
        core = singleton_get('logging_core')
        if core is None:
            if _LOGGING_CORE is None:
                _LOGGING_CORE = LoggingCore()
            singleton_register('logging_core', _LOGGING_CORE)
            core = _LOGGING_CORE
        
        return core
    except (ImportError, Exception):
        # Fallback to module-level singleton
        return _LOGGING_CORE

# ===== EXPORTS =====

__all__ = [
    'LoggingCore',
    'get_logging_core',
    'RateLimitTracker'
]

# EOF
