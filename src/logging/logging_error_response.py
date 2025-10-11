"""
logging_error_response.py
Version: 2025.10.04.04
Description: Internal implementation for error response logging and tracking

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
import json
import uuid
from typing import Dict, Any, Optional, List, Deque
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import threading

from metrics import record_error_response_metric

logger = logging.getLogger(__name__)

# ===== SECTION 1: ERROR RESPONSE DATA STRUCTURES =====

class ErrorLogLevel(Enum):
    """Error log level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

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

# ===== SECTION 2: ERROR RESPONSE LOGGER =====

class ErrorResponseLogger:
    """Error response logger with in-memory storage and analytics."""
    
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.entries: Deque[ErrorLogEntry] = deque(maxlen=max_entries)
        self.lock = threading.Lock()
        self.created_at = time.time()
        self.total_logged = 0
        
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
            
            with self.lock:
                self.entries.append(entry)
                self.total_logged += 1
                
            try:
                record_error_response_metric(
                    error_type=entry.error_type,
                    severity=entry.severity.value,
                    category='error_response',
                    response_time_ms=0,
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
            
    def get_analytics(self, 
                     time_range_minutes: int = 60,
                     include_details: bool = False) -> Dict[str, Any]:
        """Get error analytics for specified time range."""
        try:
            cutoff_time = time.time() - (time_range_minutes * 60)
            
            with self.lock:
                relevant_entries = [
                    entry for entry in self.entries 
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
            
    def clear_logs(self, older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Clear error logs, optionally filtered by age."""
        try:
            with self.lock:
                initial_count = len(self.entries)
                
                if older_than_minutes is None:
                    self.entries.clear()
                    cleared_count = initial_count
                else:
                    cutoff_time = time.time() - (older_than_minutes * 60)
                    original_entries = list(self.entries)
                    self.entries.clear()
                    
                    for entry in original_entries:
                        if entry.timestamp >= cutoff_time:
                            self.entries.append(entry)
                            
                    cleared_count = initial_count - len(self.entries)
                    
            logger.info(f"Cleared {cleared_count} error log entries")
            
            return {
                'status': 'success',
                'cleared_count': cleared_count,
                'remaining_count': len(self.entries),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear error logs: {e}")
            return {'status': 'error', 'error': str(e), 'timestamp': time.time()}
            
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of error response logger."""
        try:
            with self.lock:
                current_count = len(self.entries)
                
            uptime = time.time() - self.created_at
            
            return {
                'status': 'healthy',
                'current_entries': current_count,
                'max_entries': self.max_entries,
                'total_logged': self.total_logged,
                'uptime_seconds': uptime,
                'memory_usage_percent': (current_count / self.max_entries) * 100,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }

# ===== SECTION 3: SINGLETON MANAGER =====

_error_response_logger: Optional[ErrorResponseLogger] = None
_logger_lock = threading.Lock()

def _get_internal_error_response_logger() -> Optional[ErrorResponseLogger]:
    """Get the internal error response logger instance."""
    global _error_response_logger
    return _error_response_logger

def _create_error_response_logger(max_entries: int = 1000) -> ErrorResponseLogger:
    """Create a new error response logger instance."""
    global _error_response_logger
    
    with _logger_lock:
        if _error_response_logger is None:
            _error_response_logger = ErrorResponseLogger(max_entries)
            logger.info(f"Created error response logger with max_entries={max_entries}")
        return _error_response_logger

def _reset_error_response_logger_internal() -> bool:
    """Reset the error response logger instance."""
    global _error_response_logger
    
    try:
        with _logger_lock:
            _error_response_logger = None
            logger.info("Error response logger reset")
        return True
    except Exception as e:
        logger.error(f"Failed to reset error response logger: {e}")
        return False

# ===== SECTION 4: INTERNAL INTERFACE FUNCTIONS =====

def _log_error_response_internal(error_response: Dict[str, Any], 
                                correlation_id: Optional[str] = None,
                                source_module: Optional[str] = None,
                                lambda_context = None,
                                additional_context: Optional[Dict[str, Any]] = None) -> str:
    """Internal implementation for logging error responses."""
    try:
        error_logger = _get_internal_error_response_logger()
        if error_logger is None:
            error_logger = _create_error_response_logger()
            
        entry_id = error_logger.log_error_response(
            error_response=error_response,
            correlation_id=correlation_id,
            source_module=source_module,
            lambda_context=lambda_context,
            additional_context=additional_context
        )
        
        return entry_id
        
    except Exception as e:
        logger.error(f"Failed to log error response: {e}")
        return f"error_{uuid.uuid4()}"

def _get_error_response_analytics_internal(time_range_minutes: int = 60,
                                          include_details: bool = False) -> Dict[str, Any]:
    """Internal implementation for getting error response analytics."""
    try:
        error_logger = _get_internal_error_response_logger()
        if error_logger is None:
            return {
                'status': 'no_logger',
                'message': 'Error response logger not initialized',
                'timestamp': time.time()
            }
            
        return error_logger.get_analytics(time_range_minutes, include_details)
        
    except Exception as e:
        logger.error(f"Failed to get error response analytics: {e}")
        return {'error': str(e), 'timestamp': time.time()}

def _clear_error_response_logs_internal(older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
    """Internal implementation for clearing error response logs."""
    try:
        error_logger = _get_internal_error_response_logger()
        if error_logger is None:
            return {
                'status': 'no_logger',
                'message': 'Error response logger not initialized',
                'timestamp': time.time()
            }
            
        return error_logger.clear_logs(older_than_minutes)
        
    except Exception as e:
        logger.error(f"Failed to clear error response logs: {e}")
        return {'status': 'error', 'error': str(e), 'timestamp': time.time()}

__all__ = [
    'ErrorLogLevel',
    'ErrorLogEntry',
    'ErrorResponseLogger',
    '_log_error_response_internal',
    '_get_error_response_analytics_internal',
    '_clear_error_response_logs_internal',
    '_get_internal_error_response_logger',
    '_create_error_response_logger',
    '_reset_error_response_logger_internal'
]

# EOF
