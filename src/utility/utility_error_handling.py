"""
utility_error_handling.py
Version: 2025.10.04.04
Description: Generic error handling with template-based error context generation

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

import traceback
import time
import json
from typing import Dict, Any, Optional

# ===== ERROR CONTEXT TEMPLATES =====

_ERROR_CONTEXT_TEMPLATE = '{"interface":"%s","operation":"%s","correlation_id":"%s","timestamp":%f}'
_ERROR_RESPONSE_TEMPLATE = '{"success":false,"error":"%s","error_type":"%s","timestamp":%f,"correlation_id":"%s","interface":"%s","operation":"%s"}'
_ERROR_RESPONSE_SIMPLE = '{"success":false,"error":"%s","error_type":"%s","timestamp":%f}'

_SENSITIVE_PATTERNS = ['password', 'token', 'key', 'secret', 'credential', 'auth']


def sanitize_error(error: Exception) -> Dict[str, Any]:
    """Sanitize error for safe logging and response."""
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': time.time()
    }
    
    error_str = str(error).lower()
    
    if any(pattern in error_str for pattern in _SENSITIVE_PATTERNS):
        error_data['error_message'] = f"{type(error).__name__}: [Sensitive information removed]"
        error_data['sanitized'] = True
    else:
        error_data['sanitized'] = False
    
    return error_data


def create_error_context_fast(interface: str, operation: str, 
                              correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Fast error context creation using template."""
    try:
        import gateway
        corr_id = correlation_id or gateway.generate_correlation_id()
    except Exception:
        import uuid
        corr_id = str(uuid.uuid4())[:8]
    
    timestamp = time.time()
    
    try:
        json_str = _ERROR_CONTEXT_TEMPLATE % (interface, operation, corr_id, timestamp)
        return json.loads(json_str)
    except Exception:
        return {
            'interface': interface,
            'operation': operation,
            'correlation_id': corr_id,
            'timestamp': timestamp
        }


def create_error_context(interface: str, operation: str, 
                        correlation_id: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
    """Create error context for consistent error handling."""
    try:
        import gateway
        corr_id = correlation_id or gateway.generate_correlation_id()
    except Exception:
        import uuid
        corr_id = str(uuid.uuid4())[:8]
    
    context = {
        'interface': interface,
        'operation': operation,
        'correlation_id': corr_id,
        'timestamp': time.time()
    }
    
    if kwargs:
        context.update(kwargs)
    
    return context


def format_error_response_fast(error: Exception, interface: str, operation: str,
                               correlation_id: str) -> Dict[str, Any]:
    """Fast error response formatting using template."""
    sanitized = sanitize_error(error)
    timestamp = time.time()
    
    try:
        json_str = _ERROR_RESPONSE_TEMPLATE % (
            sanitized['error_message'],
            sanitized['error_type'],
            timestamp,
            correlation_id,
            interface,
            operation
        )
        return json.loads(json_str)
    except Exception:
        return {
            'success': False,
            'error': sanitized['error_message'],
            'error_type': sanitized['error_type'],
            'timestamp': timestamp,
            'correlation_id': correlation_id,
            'interface': interface,
            'operation': operation
        }


def format_error_response(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Format error into standardized response structure."""
    sanitized = sanitize_error(error)
    
    response = {
        'success': False,
        'error': sanitized['error_message'],
        'error_type': sanitized['error_type'],
        'timestamp': sanitized['timestamp'],
        'correlation_id': context.get('correlation_id', 'unknown'),
        'interface': context.get('interface', 'unknown'),
        'operation': context.get('operation', 'unknown')
    }
    
    if context.get('include_traceback', False):
        response['traceback'] = traceback.format_exc()
    
    return response


def log_error_with_context(error: Exception, operation: str, 
                          interface: str = 'unknown',
                          correlation_id: Optional[str] = None,
                          **additional_context) -> None:
    """Log error with full context information."""
    try:
        import gateway
        
        sanitized = sanitize_error(error)
        
        log_data = {
            'error_type': sanitized['error_type'],
            'error_message': sanitized['error_message'],
            'interface': interface,
            'operation': operation,
            'correlation_id': correlation_id or 'unknown',
            'sanitized': sanitized.get('sanitized', False),
            **additional_context
        }
        
        gateway.log_error(
            f"Error in {interface}.{operation}",
            error=error,
            **log_data
        )
    except Exception:
        pass


def record_error_metrics(error: Exception, interface: str, 
                        operation: str = 'unknown',
                        **dimensions) -> None:
    """Record error metrics for monitoring."""
    try:
        import gateway
        
        sanitized = sanitize_error(error)
        
        metric_dimensions = {
            'interface': interface,
            'operation': operation,
            'error_type': sanitized['error_type'],
            **dimensions
        }
        
        gateway.record_metric(
            f"{interface}_error_count",
            1.0,
            dimensions=metric_dimensions
        )
    except Exception:
        pass


def handle_and_format_error(error: Exception, interface: str, 
                           operation: str, 
                           correlation_id: Optional[str] = None,
                           log_error: bool = True,
                           record_metrics: bool = True,
                           **additional_context) -> Dict[str, Any]:
    """Comprehensive error handling with fast-path templates."""
    
    if correlation_id and not additional_context and log_error and record_metrics:
        response = format_error_response_fast(error, interface, operation, correlation_id)
        
        if log_error:
            log_error_with_context(error, operation, interface, correlation_id)
        
        if record_metrics:
            record_error_metrics(error, interface, operation)
        
        return response
    else:
        context = create_error_context(interface, operation, correlation_id, **additional_context)
        
        if log_error:
            log_error_with_context(error, operation, interface, context['correlation_id'], **additional_context)
        
        if record_metrics:
            record_error_metrics(error, interface, operation)
        
        return format_error_response(error, context)


__all__ = [
    'sanitize_error',
    'format_error_response',
    'format_error_response_fast',
    'log_error_with_context',
    'record_error_metrics',
    'create_error_context',
    'create_error_context_fast',
    'handle_and_format_error',
]

# EOF
