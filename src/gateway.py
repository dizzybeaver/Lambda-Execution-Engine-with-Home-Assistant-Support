"""
gateway.py - Revolutionary Gateway Architecture with Universal Fast Path
Version: 2025.10.07.04
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
from typing import Dict, Any, Optional
from enum import Enum

# ===== GATEWAY INTERFACE ENUMERATION =====

class GatewayInterface(Enum):
    """Enumeration of all available gateway interfaces."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    HTTP_CLIENT = "http_client"
    SINGLETON = "singleton"
    INITIALIZATION = "initialization"
    UTILITY = "utility"
    CIRCUIT_BREAKER = "circuit_breaker"

# ===== FAST PATH OPTIMIZATION =====

_FAST_PATH_ENABLED = True
_FAST_PATH_STATS = {
    'total_calls': 0,
    'fast_path_hits': 0,
    'fast_path_misses': 0
}

# ===== LAMBDA INITIALIZATION =====

def initialize_lambda():
    """
    Initialize Lambda execution environment.
    Called once at container start to warm up critical paths.
    """
    pass

# ===== CORE GATEWAY ROUTING =====

def execute_operation(interface: GatewayInterface, operation: str, *args, **kwargs):
    """
    Universal gateway routing with lazy loading.
    Routes operations to appropriate interface implementations.
    """
    global _FAST_PATH_STATS
    _FAST_PATH_STATS['total_calls'] += 1
    
    if interface == GatewayInterface.CACHE:
        from cache_core import (
            _execute_get_implementation,
            _execute_set_implementation,
            _execute_delete_implementation,
            _execute_clear_implementation
        )
        
        if operation == 'get':
            return _execute_get_implementation(kwargs.get('key'))
        elif operation == 'set':
            return _execute_set_implementation(
                kwargs.get('key'),
                kwargs.get('value'),
                kwargs.get('ttl')
            )
        elif operation == 'delete':
            return _execute_delete_implementation(kwargs.get('key'))
        elif operation == 'clear':
            return _execute_clear_implementation()
        else:
            raise ValueError(f"Unknown CACHE operation: {operation}")
    
    elif interface == GatewayInterface.LOGGING:
        from logging_core import (
            _execute_log_info_implementation,
            _execute_log_error_implementation,
            _execute_log_warning_implementation,
            _execute_log_debug_implementation
        )
        
        if operation == 'log_info':
            return _execute_log_info_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_error':
            return _execute_log_error_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_warning':
            return _execute_log_warning_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        elif operation == 'log_debug':
            return _execute_log_debug_implementation(
                kwargs.get('message'),
                extra=kwargs.get('extra')
            )
        else:
            raise ValueError(f"Unknown LOGGING operation: {operation}")
    
    elif interface == GatewayInterface.SECURITY:
        from security_core import (
            _execute_validate_request_implementation,
            _execute_validate_token_implementation,
            _execute_encrypt_data_implementation,
            _execute_decrypt_data_implementation
        )
        
        if operation == 'validate_request':
            return _execute_validate_request_implementation(kwargs.get('request_data'))
        elif operation == 'validate_token':
            return _execute_validate_token_implementation(kwargs.get('token'))
        elif operation == 'encrypt':
            return _execute_encrypt_data_implementation(kwargs.get('data'))
        elif operation == 'decrypt':
            return _execute_decrypt_data_implementation(kwargs.get('encrypted_data'))
        else:
            raise ValueError(f"Unknown SECURITY operation: {operation}")
    
    elif interface == GatewayInterface.METRICS:
        from metrics_core import (
            _execute_record_metric_implementation,
            _execute_increment_counter_implementation,
            _execute_get_stats_implementation
        )
        
        if operation == 'record':
            return _execute_record_metric_implementation(
                kwargs.get('metric_name'),
                kwargs.get('value'),
                kwargs.get('dimensions', {})
            )
        elif operation == 'increment':
            return _execute_increment_counter_implementation(
                kwargs.get('counter_name'),
                kwargs.get('value', 1)
            )
        elif operation == 'get_metrics':
            return _execute_get_stats_implementation()
        else:
            raise ValueError(f"Unknown METRICS operation: {operation}")
    
    elif interface == GatewayInterface.CONFIG:
        from config_core import (
            _get_parameter_implementation,
            _set_parameter_implementation,
            _get_all_parameters_implementation
        )
        
        if operation == 'get_parameter':
            return _get_parameter_implementation(
                kwargs.get('parameter_name'),
                kwargs.get('default_value')
            )
        elif operation == 'set_parameter':
            return _set_parameter_implementation(
                kwargs.get('parameter_name'),
                kwargs.get('value')
            )
        elif operation == 'get_all':
            return _get_all_parameters_implementation()
        else:
            raise ValueError(f"Unknown CONFIG operation: {operation}")
    
    elif interface == GatewayInterface.HTTP_CLIENT:
        from http_client_core import (
            _make_request_implementation,
            _make_get_request_implementation,
            _make_post_request_implementation
        )
        
        if operation == 'request':
            return _make_request_implementation(
                kwargs.get('method'),
                kwargs.get('url'),
                **{k: v for k, v in kwargs.items() if k not in ['method', 'url']}
            )
        elif operation == 'get':
            return _make_get_request_implementation(
                kwargs.get('url'),
                **{k: v for k, v in kwargs.items() if k != 'url'}
            )
        elif operation == 'post':
            return _make_post_request_implementation(
                kwargs.get('url'),
                kwargs.get('data'),
                **{k: v for k, v in kwargs.items() if k not in ['url', 'data']}
            )
        else:
            raise ValueError(f"Unknown HTTP_CLIENT operation: {operation}")
    
    elif interface == GatewayInterface.SINGLETON:
        from singleton_core import (
            _get_singleton_implementation,
            _register_singleton_implementation
        )
        
        if operation == 'get':
            return _get_singleton_implementation(kwargs.get('singleton_name'))
        elif operation == 'register':
            return _register_singleton_implementation(
                kwargs.get('singleton_name'),
                kwargs.get('instance')
            )
        else:
            raise ValueError(f"Unknown SINGLETON operation: {operation}")
    
    elif interface == GatewayInterface.INITIALIZATION:
        from initialization_core import (
            _execute_initialization_implementation,
            _record_stage_implementation
        )
        
        if operation == 'execute':
            return _execute_initialization_implementation(kwargs.get('init_type'))
        elif operation == 'record_stage':
            return _record_stage_implementation(
                kwargs.get('stage'),
                kwargs.get('status')
            )
        else:
            raise ValueError(f"Unknown INITIALIZATION operation: {operation}")
    
    elif interface == GatewayInterface.UTILITY:
        from utility_core import _UTILITY
        import uuid
        
        if operation == 'success_response':
            message = kwargs.get('message', '')
            data = kwargs.get('data')
            return {
                'success': True,
                'message': message,
                'data': data,
                'timestamp': str(uuid.uuid4())
            }
        elif operation == 'error_response':
            message = kwargs.get('message', '')
            error_code = kwargs.get('error_code', 'GENERIC_ERROR')
            return {
                'success': False,
                'error': message,
                'error_code': error_code,
                'timestamp': str(uuid.uuid4())
            }
        elif operation == 'parse_json':
            return _UTILITY.parse_json(kwargs.get('json_string', ''))
        elif operation == 'correlation_id':
            return str(uuid.uuid4())
        elif operation == 'sanitize':
            data = kwargs.get('data')
            if isinstance(data, str):
                return data.replace('<', '&lt;').replace('>', '&gt;')
            return data
        else:
            raise ValueError(f"Unknown UTILITY operation: {operation}")
    
    elif interface == GatewayInterface.CIRCUIT_BREAKER:
        from circuit_breaker_core import (
            _execute_with_circuit_breaker_implementation,
            _get_circuit_state_implementation
        )
        
        if operation == 'execute':
            return _execute_with_circuit_breaker_implementation(
                kwargs.get('circuit_name'),
                kwargs.get('func'),
                *args,
                **kwargs
            )
        elif operation == 'get_state':
            return _get_circuit_state_implementation(kwargs.get('circuit_name'))
        else:
            raise ValueError(f"Unknown CIRCUIT_BREAKER operation: {operation}")
    
    else:
        raise ValueError(f"Unknown interface: {interface}")

# ===== CACHE INTERFACE FUNCTIONS =====

def cache_get(key: str):
    """Get value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key)

def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    """Set value in cache."""
    return execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)

def cache_delete(key: str):
    """Delete value from cache."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)

def cache_clear():
    """Clear all cache."""
    return execute_operation(GatewayInterface.CACHE, 'clear')

# ===== LOGGING INTERFACE FUNCTIONS =====

def log_info(message: str, **extra):
    """Log info message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)

def log_error(message: str, **extra):
    """Log error message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, extra=extra)

def log_warning(message: str, **extra):
    """Log warning message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, extra=extra)

def log_debug(message: str, **extra):
    """Log debug message."""
    return execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, extra=extra)

# ===== SECURITY INTERFACE FUNCTIONS =====

def validate_request(request_data: Dict[str, Any]) -> bool:
    """Validate request."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_request', request_data=request_data)

def validate_token(token: str) -> bool:
    """Validate token."""
    return execute_operation(GatewayInterface.SECURITY, 'validate_token', token=token)

def encrypt_data(data: str) -> str:
    """Encrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'encrypt', data=data)

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data."""
    return execute_operation(GatewayInterface.SECURITY, 'decrypt', encrypted_data=encrypted_data)

# ===== METRICS INTERFACE FUNCTIONS =====

def record_metric(metric_name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None):
    """Record metric."""
    return execute_operation(GatewayInterface.METRICS, 'record', metric_name=metric_name, value=value, dimensions=dimensions)

def increment_counter(counter_name: str, value: int = 1):
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', counter_name=counter_name, value=value)

# ===== CONFIG INTERFACE FUNCTIONS =====

def get_parameter(parameter_name: str, default_value: Any = None):
    """Get configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', parameter_name=parameter_name, default_value=default_value)

def set_parameter(parameter_name: str, value: Any):
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', parameter_name=parameter_name, value=value)

def get_all_parameters() -> Dict[str, Any]:
    """Get all configuration parameters."""
    return execute_operation(GatewayInterface.CONFIG, 'get_all')

def get_category_config(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category_config', category=category)

def update_category_config(category: str, updates: Dict[str, Any]):
    """Update configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'update_category_config', category=category, updates=updates)

# ===== HTTP CLIENT INTERFACE FUNCTIONS =====

def make_request(method: str, url: str, **kwargs):
    """Make HTTP request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'request', method=method, url=url, **kwargs)

def make_get_request(url: str, **kwargs):
    """Make HTTP GET request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get', url=url, **kwargs)

def make_post_request(url: str, data: Dict[str, Any], **kwargs):
    """Make HTTP POST request."""
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'post', url=url, data=data, **kwargs)

# ===== SINGLETON INTERFACE FUNCTIONS =====

def get_singleton(singleton_name: str):
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', singleton_name=singleton_name)

def register_singleton(singleton_name: str, instance):
    """Register singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'register', singleton_name=singleton_name, instance=instance)

# ===== INITIALIZATION INTERFACE FUNCTIONS =====

def execute_initialization_operation(init_type: str):
    """Execute initialization operation."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'execute', init_type=init_type)

def record_initialization_stage(stage: str, status: str):
    """Record initialization stage."""
    return execute_operation(GatewayInterface.INITIALIZATION, 'record_stage', stage=stage, status=status)

# ===== UTILITY INTERFACE FUNCTIONS =====

def create_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """Create success response."""
    return execute_operation(GatewayInterface.UTILITY, 'success_response', message=message, data=data)

def create_error_response(message: str, error_code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """Create error response."""
    return execute_operation(GatewayInterface.UTILITY, 'error_response', message=message, error_code=error_code)

def parse_json_safely(json_string: str) -> Optional[Dict]:
    """Parse JSON safely."""
    return execute_operation(GatewayInterface.UTILITY, 'parse_json', json_string=json_string)

def generate_correlation_id() -> str:
    """Generate correlation ID."""
    return execute_operation(GatewayInterface.UTILITY, 'correlation_id')

def sanitize_response_data(data: Any) -> Any:
    """Sanitize response data."""
    return execute_operation(GatewayInterface.UTILITY, 'sanitize', data=data)

# ===== LAMBDA RESPONSE FORMATTER =====

def format_response(status_code: int, body: Any) -> Dict[str, Any]:
    """
    Format HTTP response for AWS Lambda/API Gateway.
    
    Creates standard Lambda proxy integration response format.
    Used by lambda_function.py to format API Gateway responses.
    
    Args:
        status_code: HTTP status code (200, 400, 500, etc.)
        body: Response body (will be JSON-encoded)
    
    Returns:
        Dict with statusCode, body, and headers for API Gateway
    """
    return {
        'statusCode': status_code,
        'body': json.dumps(body) if not isinstance(body, str) else body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

# ===== GATEWAY STATS =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway performance statistics."""
    return {
        'fast_path_enabled': _FAST_PATH_ENABLED,
        'total_calls': _FAST_PATH_STATS['total_calls'],
        'fast_path_hits': _FAST_PATH_STATS['fast_path_hits'],
        'fast_path_misses': _FAST_PATH_STATS['fast_path_misses'],
        'hit_rate': _FAST_PATH_STATS['fast_path_hits'] / max(_FAST_PATH_STATS['total_calls'], 1)
    }

def get_fast_path_stats() -> Dict[str, int]:
    """Get fast path statistics."""
    return _FAST_PATH_STATS.copy()

def enable_fast_path():
    """Enable fast path optimization."""
    global _FAST_PATH_ENABLED
    _FAST_PATH_ENABLED = True

def disable_fast_path():
    """Disable fast path optimization."""
    global _FAST_PATH_ENABLED
    _FAST_PATH_ENABLED = False

def reset_fast_path_stats():
    """Reset fast path statistics."""
    _FAST_PATH_STATS['total_calls'] = 0
    _FAST_PATH_STATS['fast_path_hits'] = 0
    _FAST_PATH_STATS['fast_path_misses'] = 0

# EOF
