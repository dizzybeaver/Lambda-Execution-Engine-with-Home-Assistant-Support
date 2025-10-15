"""
logging_types.py - Logging type definitions and enumerations
Version: 2025.10.14.01
Description: Type definitions for unified logging system

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

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


# ===== LOGGING OPERATION ENUM =====

class LogOperation(Enum):
    """Enumeration of all logging operations."""
    LOG_INFO = "log_info"
    LOG_ERROR = "log_error"
    LOG_WARNING = "log_warning"
    LOG_DEBUG = "log_debug"
    LOG_OPERATION_START = "log_operation_start"
    LOG_OPERATION_SUCCESS = "log_operation_success"
    LOG_OPERATION_FAILURE = "log_operation_failure"
    LOG_WITH_TEMPLATE = "log_with_template"
    LOG_TEMPLATE_FAST = "log_template_fast"
    GET_ERROR_ENTRIES = "get_error_entries"
    GET_STATS = "get_stats"
    CLEAR_ERROR_ENTRIES = "clear_error_entries"
    LOG_ERROR_RESPONSE = "log_error_response"
    GET_ERROR_ANALYTICS = "get_error_analytics"
    CLEAR_ERROR_LOGS = "clear_error_logs"


class LogTemplate(Enum):
    """Pre-formatted log templates for optimal performance."""
    OPERATION_START = "[OP_START]"
    OPERATION_SUCCESS = "[OP_SUCCESS]"
    OPERATION_FAILURE = "[OP_FAIL]"
    CACHE_HIT = "[CACHE_HIT]"
    CACHE_MISS = "[CACHE_MISS]"


class ErrorLogLevel(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== ERROR ENTRY DATACLASSES =====

@dataclass
class ErrorEntry:
    """Simple error entry with metadata."""
    timestamp: float
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ErrorLogEntry:
    """Structured error response log entry."""
    id: str
    timestamp: float
    datetime: datetime
    correlation_id: str
    source_module: Optional[str]
    error_type: str
    severity: ErrorLogLevel
    status_code: int
    error_response: Dict[str, Any]
    lambda_context_info: Optional[Dict[str, Any]]
    additional_context: Optional[Dict[str, Any]]
    
    @staticmethod
    def determine_severity(error_response: Dict[str, Any]) -> ErrorLogLevel:
        """Determine severity from error response."""
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


# ===== EXPORTS =====

__all__ = [
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
]

# EOF
