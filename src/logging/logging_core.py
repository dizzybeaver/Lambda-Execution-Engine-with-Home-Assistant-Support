"""
Logging Core - Enhanced Logging with Template Optimization
Version: 2025.10.03.01
Description: Centralized logging with pre-compiled message templates for performance

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
import os
from typing import Dict, Any, Optional, Union
from enum import Enum
import threading

# ===== LOG MESSAGE TEMPLATES (Template Optimization) =====

_CACHE_HIT_LOG = "Cache hit: %s"
_CACHE_MISS_LOG = "Cache miss: %s"
_CACHE_SET_LOG = "Cache set: %s"
_CACHE_DELETE_LOG = "Cache delete: %s"

_HA_SUCCESS_LOG = "HA operation successful - %dms"
_HA_ERROR_LOG = "HA operation failed: %s"
_HA_REQUEST_LOG = "HA request: %s.%s"
_HA_RESPONSE_LOG = "HA response: %d entities"

_HTTP_REQUEST_LOG = "HTTP %s %s"
_HTTP_SUCCESS_LOG = "HTTP %s %s - %dms (%d)"
_HTTP_ERROR_LOG = "HTTP %s %s failed: %s"
_HTTP_TIMEOUT_LOG = "HTTP %s %s timeout after %ds"

_OPERATION_START_LOG = "Operation started: %s.%s"
_OPERATION_SUCCESS_LOG = "Operation completed: %s.%s - %dms"
_OPERATION_ERROR_LOG = "Operation failed: %s.%s - %s"

_LAMBDA_START_LOG = "Lambda invocation started: %s"
_LAMBDA_SUCCESS_LOG = "Lambda invocation completed - %dms"
_LAMBDA_ERROR_LOG = "Lambda invocation failed: %s"

_METRIC_RECORD_LOG = "Metric recorded: %s = %f"
_CONFIG_UPDATE_LOG = "Config updated: %s = %s"
_SECURITY_EVENT_LOG = "Security event: %s - %s"

_CACHE_EXTRA_TEMPLATE = '{"correlation_id":"%s","access_count":%d,"source_module":"%s"}'
_HA_EXTRA_TEMPLATE = '{"correlation_id":"%s","response_time_ms":%d,"operation":"%s"}'
_HTTP_EXTRA_TEMPLATE = '{"correlation_id":"%s","method":"%s","url":"%s","status_code":%d}'
_OPERATION_EXTRA_TEMPLATE = '{"correlation_id":"%s","interface":"%s","operation":"%s","duration_ms":%d}'
_METRIC_EXTRA_TEMPLATE = '{"correlation_id":"%s","metric_name":"%s","value":%f,"dimensions":%s}'

_USE_LOG_TEMPLATES = os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'

class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggingCore:
    """Core logging implementation with template optimization."""
    
    def __init__(self):
        self.logger = logging.getLogger('lambda_execution_engine')
        self._setup_logger()
        self._stats = {
            'log_count': 0,
            'template_usage': 0,
            'legacy_usage': 0,
            'level_counts': {level.value: 0 for level in LogLevel}
        }
        self._lock = threading.RLock()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _log_message(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal log message handler."""
        with self._lock:
            self._stats['log_count'] += 1
            self._stats['level_counts'][level.value] += 1
        
        log_func = getattr(self.logger, level.value.lower())
        if extra:
            log_func(message, extra=extra)
        else:
            log_func(message)
    
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log_message(LogLevel.INFO, message, extra)
    
    def log_error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        if error:
            message = f"{message}: {str(error)}"
        self._log_message(LogLevel.ERROR, message, extra)
    
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log_message(LogLevel.WARNING, message, extra)
    
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log_message(LogLevel.DEBUG, message, extra)
    
    def log_cache_hit(self, key: str, correlation_id: str, access_count: int, source_module: str):
        """Log cache hit using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _CACHE_HIT_LOG % key
                extra_json = _CACHE_EXTRA_TEMPLATE % (correlation_id, access_count, source_module)
                extra = json.loads(extra_json)
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"Cache hit: {key}"
                extra = {
                    "correlation_id": correlation_id,
                    "access_count": access_count,
                    "source_module": source_module
                }
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.DEBUG, message, extra)
            
        except Exception as e:
            self._log_message(LogLevel.DEBUG, f"Cache hit: {key}", {
                "correlation_id": correlation_id,
                "template_error": str(e)
            })
    
    def log_cache_miss(self, key: str, correlation_id: str):
        """Log cache miss using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _CACHE_MISS_LOG % key
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"Cache miss: {key}"
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.DEBUG, message, {"correlation_id": correlation_id})
            
        except Exception:
            self._log_message(LogLevel.DEBUG, f"Cache miss: {key}", {"correlation_id": correlation_id})
    
    def log_http_request(self, method: str, url: str, correlation_id: str):
        """Log HTTP request using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _HTTP_REQUEST_LOG % (method, url)
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"HTTP {method} {url}"
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.INFO, message, {"correlation_id": correlation_id})
            
        except Exception:
            self._log_message(LogLevel.INFO, f"HTTP {method} {url}", {"correlation_id": correlation_id})
    
    def log_http_success(self, method: str, url: str, response_time_ms: int, status_code: int, correlation_id: str):
        """Log HTTP success using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _HTTP_SUCCESS_LOG % (method, url, response_time_ms, status_code)
                extra_json = _HTTP_EXTRA_TEMPLATE % (correlation_id, method, url, status_code)
                extra = json.loads(extra_json)
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"HTTP {method} {url} - {response_time_ms}ms ({status_code})"
                extra = {
                    "correlation_id": correlation_id,
                    "method": method,
                    "url": url,
                    "status_code": status_code
                }
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.INFO, message, extra)
            
        except Exception:
            self._log_message(LogLevel.INFO, f"HTTP {method} {url} - {response_time_ms}ms", {
                "correlation_id": correlation_id,
                "status_code": status_code
            })
    
    def log_operation_start(self, interface: str, operation: str, correlation_id: str):
        """Log operation start using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _OPERATION_START_LOG % (interface, operation)
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"Operation started: {interface}.{operation}"
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.DEBUG, message, {
                "correlation_id": correlation_id,
                "interface": interface,
                "operation": operation
            })
            
        except Exception:
            self._log_message(LogLevel.DEBUG, f"Operation started: {interface}.{operation}", {
                "correlation_id": correlation_id
            })
    
    def log_operation_success(self, interface: str, operation: str, duration_ms: int, correlation_id: str):
        """Log operation success using template optimization."""
        try:
            if _USE_LOG_TEMPLATES:
                message = _OPERATION_SUCCESS_LOG % (interface, operation, duration_ms)
                extra_json = _OPERATION_EXTRA_TEMPLATE % (correlation_id, interface, operation, duration_ms)
                extra = json.loads(extra_json)
                with self._lock:
                    self._stats['template_usage'] += 1
            else:
                message = f"Operation completed: {interface}.{operation} - {duration_ms}ms"
                extra = {
                    "correlation_id": correlation_id,
                    "interface": interface,
                    "operation": operation,
                    "duration_ms": duration_ms
                }
                with self._lock:
                    self._stats['legacy_usage'] += 1
            
            self._log_message(LogLevel.DEBUG, message, extra)
            
        except Exception:
            self._log_message(LogLevel.DEBUG, f"Operation completed: {interface}.{operation} - {duration_ms}ms", {
                "correlation_id": correlation_id
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            total_operations = self._stats['template_usage'] + self._stats['legacy_usage']
            template_usage_rate = self._stats['template_usage'] / max(total_operations, 1)
            
            return {
                'log_count': self._stats['log_count'],
                'template_usage_rate': template_usage_rate,
                'template_optimization_enabled': _USE_LOG_TEMPLATES,
                'level_counts': self._stats['level_counts'].copy(),
                'stats': self._stats.copy()
            }
    
    def reset_stats(self):
        """Reset logging statistics."""
        with self._lock:
            self._stats = {
                'log_count': 0,
                'template_usage': 0,
                'legacy_usage': 0,
                'level_counts': {level.value: 0 for level in LogLevel}
            }

# EOF
