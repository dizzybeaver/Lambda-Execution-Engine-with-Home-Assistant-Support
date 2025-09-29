"""
logging_core.py - Core Logging Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - CloudWatch free tier optimized
"""

import json
import time
import traceback
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class LogLevel(Enum):
    """Log levels."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@dataclass
class LogEntry:
    """Log entry structure."""
    level: LogLevel
    message: str
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level.name,
            "message": self.message,
            "timestamp": self.timestamp,
            "iso_timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "context": self.context,
            "correlation_id": self.correlation_id
        }

_LOG_BUFFER: List[LogEntry] = []
_LOG_LEVEL = LogLevel.INFO
_MAX_BUFFER_SIZE = 1000
_CORRELATION_ID = None

def set_log_level(level: str) -> None:
    """Set logging level."""
    global _LOG_LEVEL
    level_map = {
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "ERROR": LogLevel.ERROR,
        "CRITICAL": LogLevel.CRITICAL
    }
    _LOG_LEVEL = level_map.get(level.upper(), LogLevel.INFO)

def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for log entries."""
    global _CORRELATION_ID
    _CORRELATION_ID = correlation_id

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return _CORRELATION_ID

def _should_log(level: LogLevel) -> bool:
    """Check if message should be logged."""
    return level.value >= _LOG_LEVEL.value

def _add_to_buffer(entry: LogEntry) -> None:
    """Add entry to buffer."""
    global _LOG_BUFFER
    _LOG_BUFFER.append(entry)
    
    if len(_LOG_BUFFER) > _MAX_BUFFER_SIZE:
        _LOG_BUFFER = _LOG_BUFFER[-_MAX_BUFFER_SIZE:]

def _format_message(message: str, context: Dict[str, Any]) -> str:
    """Format log message with context."""
    if not context:
        return message
    
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())
    return f"{message} [{context_str}]"

def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    if not _should_log(LogLevel.DEBUG):
        return
    
    entry = LogEntry(
        level=LogLevel.DEBUG,
        message=message,
        timestamp=time.time(),
        context=kwargs,
        correlation_id=_CORRELATION_ID
    )
    
    _add_to_buffer(entry)
    print(f"DEBUG: {_format_message(message, kwargs)}")

def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    if not _should_log(LogLevel.INFO):
        return
    
    entry = LogEntry(
        level=LogLevel.INFO,
        message=message,
        timestamp=time.time(),
        context=kwargs,
        correlation_id=_CORRELATION_ID
    )
    
    _add_to_buffer(entry)
    print(f"INFO: {_format_message(message, kwargs)}")

def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    if not _should_log(LogLevel.WARNING):
        return
    
    entry = LogEntry(
        level=LogLevel.WARNING,
        message=message,
        timestamp=time.time(),
        context=kwargs,
        correlation_id=_CORRELATION_ID
    )
    
    _add_to_buffer(entry)
    print(f"WARNING: {_format_message(message, kwargs)}")

def log_error(message: str, **kwargs) -> None:
    """Log error message."""
    if not _should_log(LogLevel.ERROR):
        return
    
    error = kwargs.pop('error', None)
    if error:
        kwargs['error_type'] = type(error).__name__
        kwargs['error_message'] = str(error)
        kwargs['traceback'] = ''.join(traceback.format_tb(error.__traceback__)) if hasattr(error, '__traceback__') else None
    
    entry = LogEntry(
        level=LogLevel.ERROR,
        message=message,
        timestamp=time.time(),
        context=kwargs,
        correlation_id=_CORRELATION_ID
    )
    
    _add_to_buffer(entry)
    print(f"ERROR: {_format_message(message, kwargs)}")

def log_critical(message: str, **kwargs) -> None:
    """Log critical message."""
    entry = LogEntry(
        level=LogLevel.CRITICAL,
        message=message,
        timestamp=time.time(),
        context=kwargs,
        correlation_id=_CORRELATION_ID
    )
    
    _add_to_buffer(entry)
    print(f"CRITICAL: {_format_message(message, kwargs)}")

def log_exception(message: str, error: Exception, **kwargs) -> None:
    """Log exception with full context."""
    kwargs['error'] = error
    log_error(message, **kwargs)

def get_logs(
    level: Optional[str] = None,
    limit: Optional[int] = None,
    correlation_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get log entries with optional filtering."""
    logs = _LOG_BUFFER[:]
    
    if level:
        target_level = LogLevel[level.upper()]
        logs = [log for log in logs if log.level == target_level]
    
    if correlation_id:
        logs = [log for log in logs if log.correlation_id == correlation_id]
    
    if limit:
        logs = logs[-limit:]
    
    return [log.to_dict() for log in logs]

def clear_logs() -> int:
    """Clear log buffer."""
    global _LOG_BUFFER
    count = len(_LOG_BUFFER)
    _LOG_BUFFER = []
    return count

def get_log_stats() -> Dict[str, Any]:
    """Get logging statistics."""
    level_counts = {}
    for log in _LOG_BUFFER:
        level_name = log.level.name
        level_counts[level_name] = level_counts.get(level_name, 0) + 1
    
    return {
        "total_logs": len(_LOG_BUFFER),
        "by_level": level_counts,
        "current_level": _LOG_LEVEL.name,
        "buffer_size": _MAX_BUFFER_SIZE,
        "buffer_usage": f"{len(_LOG_BUFFER)}/{_MAX_BUFFER_SIZE}"
    }

def export_logs(format: str = "json") -> str:
    """Export logs in specified format."""
    logs = [log.to_dict() for log in _LOG_BUFFER]
    
    if format.lower() == "json":
        return json.dumps(logs, indent=2)
    elif format.lower() == "text":
        lines = []
        for log in logs:
            timestamp = datetime.fromtimestamp(log["timestamp"]).isoformat()
            lines.append(f"[{timestamp}] {log['level']}: {log['message']}")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported format: {format}")

def flush_logs() -> int:
    """Flush logs to output."""
    count = len(_LOG_BUFFER)
    for log in _LOG_BUFFER:
        print(json.dumps(log.to_dict()))
    clear_logs()
    return count

def search_logs(query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
    """Search logs by message content."""
    results = []
    
    for log in _LOG_BUFFER:
        message = log.message if case_sensitive else log.message.lower()
        search_term = query if case_sensitive else query.lower()
        
        if search_term in message:
            results.append(log.to_dict())
    
    return results

def get_recent_errors(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent error logs."""
    errors = [
        log for log in _LOG_BUFFER
        if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]
    ]
    
    return [log.to_dict() for log in errors[-limit:]]

def log_performance(operation: str, duration: float, **kwargs) -> None:
    """Log performance metric."""
    log_info(
        f"Performance: {operation}",
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )

def log_metric(name: str, value: float, unit: str = "None", **kwargs) -> None:
    """Log metric value."""
    log_info(
        f"Metric: {name}",
        value=value,
        unit=unit,
        **kwargs
    )
