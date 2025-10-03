"""
Gateway Core - Revolutionary Gateway Architecture with Lambda Response Template Optimization
Version: 2025.10.02.01
Description: Central gateway with optimized Lambda response formatting

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

import json
import os
import logging
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum

# ===== LAMBDA RESPONSE TEMPLATES (Additional Template Optimization) =====

_LAMBDA_RESPONSE_TEMPLATE = '{"statusCode":%d,"body":%s,"headers":%s}'
_DEFAULT_LAMBDA_HEADERS = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}'
_LAMBDA_SUCCESS_HEADERS = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*","Cache-Control":"no-cache"}'
_LAMBDA_ERROR_HEADERS = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*","X-Error":"true"}'

_USE_LAMBDA_TEMPLATES = os.environ.get('USE_LAMBDA_TEMPLATES', 'true').lower() == 'true'

class GatewayInterface(Enum):
    """Gateway interface enumeration."""
    LOGGING = "logging"
    METRICS = "metrics"
    CACHE = "cache"
    SECURITY = "security"
    HTTP = "http"
    UTILITY = "utility"
    CONFIG = "config"
    FAST_PATH = "fast_path"

class GatewayCore:
    """Core gateway implementation with lazy loading and LUGS integration."""
    
    def __init__(self):
        self._modules = {}
        self._module_stats = {}
        self._loaded_modules = set()
    
    def _get_module(self, module_name: str):
        """Get module with lazy loading."""
        if module_name not in self._modules:
            try:
                if module_name == 'logging_core':
                    from logging_core import LoggingCore
                    self._modules[module_name] = LoggingCore()
                elif module_name == 'metrics_core':
                    from metrics_core import MetricsCore
                    self._modules[module_name] = MetricsCore()
                elif module_name == 'cache_core':
                    from cache_core import CacheCore
                    self._modules[module_name] = CacheCore()
                elif module_name == 'security_core':
                    from security_core import SecurityCore
                    self._modules[module_name] = SecurityCore()
                elif module_name == 'http_client_core':
                    from http_client_core import HTTPClientCore
                    self._modules[module_name] = HTTPClientCore()
                elif module_name == 'shared_utilities':
                    from shared_utilities import _utility_manager
                    self._modules[module_name] = _utility_manager
                else:
                    return None
                
                self._loaded_modules.add(module_name)
                self._module_stats[module_name] = {'load_time': 0, 'access_count': 0}
                
            except ImportError:
                return None
        
        if module_name in self._module_stats:
            self._module_stats[module_name]['access_count'] += 1
        
        return self._modules.get(module_name)

_gateway = GatewayCore()

# === LOGGING INTERFACE ===

def log_info(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log info message."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_info(message, extra)
    except Exception:
        pass

def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None):
    """Log error message."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_error(message, error, extra)
    except Exception:
        pass

def log_warning(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log warning message."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_warning(message, extra)
    except Exception:
        pass

def log_debug(message: str, extra: Optional[Dict[str, Any]] = None):
    """Log debug message."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_debug(message, extra)
    except Exception:
        pass

# === CACHE INTERFACE ===

def cache_get(key: str):
    """Get value from cache."""
    try:
        cache_module = _gateway._get_module('cache_core')
        return cache_module.get(key)
    except Exception:
        return None

def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache."""
    try:
        cache_module = _gateway._get_module('cache_core')
        return cache_module.set(key, value, ttl)
    except Exception:
        return False

def cache_delete(key: str) -> bool:
    """Delete value from cache."""
    try:
        cache_module = _gateway._get_module('cache_core')
        return cache_module.delete(key)
    except Exception:
        return False

# === HTTP CLIENT INTERFACE ===

def make_request(method: str, url: str, **kwargs):
    """Make HTTP request."""
    try:
        http_module = _gateway._get_module('http_client_core')
        return http_module.make_request(method, url, **kwargs)
    except Exception as e:
        return {"success": False, "error": str(e)}

def make_get_request(url: str, **kwargs):
    """Make GET request."""
    return make_request("GET", url, **kwargs)

def make_post_request(url: str, **kwargs):
    """Make POST request."""
    return make_request("POST", url, **kwargs)

# === SECURITY INTERFACE ===

def validate_request(data: Dict[str, Any], required_fields: Optional[list] = None, field_types: Optional[Dict] = None) -> Dict[str, Any]:
    """Validate request data."""
    try:
        security_module = _gateway._get_module('security_core')
        return security_module.validate_request(data, required_fields, field_types)
    except Exception:
        return {"success": False, "error": "Validation failed"}

def validate_token(token: str) -> bool:
    """Validate token."""
    try:
        security_module = _gateway._get_module('security_core')
        return security_module.validate_token(token)
    except Exception:
        return False

def sanitize_response_data(data: Any) -> Any:
    """Sanitize response data."""
    try:
        security_module = _gateway._get_module('security_core')
        return security_module.sanitize_data(data)
    except Exception:
        return data

# === METRICS INTERFACE ===

def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None):
    """Record metric."""
    try:
        metrics_module = _gateway._get_module('metrics_core')
        return metrics_module.record_metric(name, value, dimensions)
    except Exception:
        pass

def increment_counter(name: str, dimensions: Optional[Dict[str, str]] = None):
    """Increment counter metric."""
    return record_metric(name, 1.0, dimensions)

# === UTILITY INTERFACE ===

def create_success_response(message: str, data: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create success response."""
    try:
        util_module = _gateway._get_module('shared_utilities')
        return util_module.create_success_response(message, data, correlation_id)
    except Exception:
        return {
            "success": True,
            "message": message,
            "data": data or {},
            "correlation_id": correlation_id
        }

def create_error_response(message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create error response."""
    try:
        util_module = _gateway._get_module('shared_utilities')
        return util_module.create_error_response(message, error_code, details, correlation_id)
    except Exception:
        return {
            "success": False,
            "error": message,
            "error_code": error_code,
            "details": details or {},
            "correlation_id": correlation_id
        }

def generate_correlation_id() -> str:
    """Generate correlation ID."""
    try:
        util_module = _gateway._get_module('shared_utilities')
        return util_module.generate_correlation_id()
    except Exception:
        import uuid
        return str(uuid.uuid4())[:8]

def parse_json_safely(json_str: str) -> Optional[Dict[str, Any]]:
    """Parse JSON safely."""
    try:
        util_module = _gateway._get_module('shared_utilities')
        return util_module.parse_json_safely(json_str)
    except Exception:
        try:
            import json
            return json.loads(json_str)
        except:
            return None

# === LAMBDA RESPONSE INTERFACE WITH TEMPLATE OPTIMIZATION ===

def format_response(status_code: int, body: Any, headers: Optional[Dict[str, str]] = None, use_template: bool = None) -> Dict[str, Any]:
    """Format Lambda response with template optimization."""
    try:
        should_use_template = use_template if use_template is not None else _USE_LAMBDA_TEMPLATES
        
        if should_use_template:
            return _format_response_template(status_code, body, headers)
        else:
            return _format_response_legacy(status_code, body, headers)
            
    except Exception as e:
        log_error(f"Response formatting failed: {e}")
        return _format_response_legacy(status_code, body, headers)

def _format_response_template(status_code: int, body: Any, headers: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """Format response using template optimization."""
    try:
        if isinstance(body, str):
            if body.startswith('{') or body.startswith('['):
                body_json = body
            else:
                body_json = json.dumps(body)
        else:
            body_json = json.dumps(body)
        
        if headers:
            headers_json = json.dumps(headers)
        else:
            if 200 <= status_code < 300:
                headers_json = _LAMBDA_SUCCESS_HEADERS
            elif status_code >= 400:
                headers_json = _LAMBDA_ERROR_HEADERS
            else:
                headers_json = _DEFAULT_LAMBDA_HEADERS
        
        json_response = _LAMBDA_RESPONSE_TEMPLATE % (
            status_code, body_json, headers_json
        )
        
        record_metric('lambda.response_template_used', 1.0, {
            'status_code': str(status_code),
            'template_type': 'optimized'
        })
        
        return json.loads(json_response)
        
    except Exception as e:
        log_error(f"Template response formatting failed: {e}")
        return _format_response_legacy(status_code, body, headers)

def _format_response_legacy(status_code: int, body: Any, headers: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """Legacy dict-based response formatting."""
    try:
        if isinstance(body, str):
            formatted_body = body
        else:
            formatted_body = json.dumps(body)
        
        default_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
        
        if status_code >= 400:
            default_headers['X-Error'] = 'true'
        elif 200 <= status_code < 300:
            default_headers['Cache-Control'] = 'no-cache'
        
        if headers:
            default_headers.update(headers)
        
        record_metric('lambda.response_legacy_used', 1.0, {
            'status_code': str(status_code),
            'template_type': 'legacy'
        })
        
        return {
            'statusCode': status_code,
            'body': formatted_body,
            'headers': default_headers
        }
        
    except Exception as e:
        log_error(f"Legacy response formatting failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Response formatting failed"}),
            'headers': {'Content-Type': 'application/json'}
        }

def format_response_json(status_code: int, body: Any, headers: Optional[Dict[str, str]] = None) -> str:
    """Format Lambda response as JSON string (no dict parsing)."""
    try:
        if _USE_LAMBDA_TEMPLATES:
            if isinstance(body, str):
                if body.startswith('{') or body.startswith('['):
                    body_json = body
                else:
                    body_json = json.dumps(body)
            else:
                body_json = json.dumps(body)
            
            if headers:
                headers_json = json.dumps(headers)
            else:
                if 200 <= status_code < 300:
                    headers_json = _LAMBDA_SUCCESS_HEADERS
                elif status_code >= 400:
                    headers_json = _LAMBDA_ERROR_HEADERS
                else:
                    headers_json = _DEFAULT_LAMBDA_HEADERS
            
            return _LAMBDA_RESPONSE_TEMPLATE % (
                status_code, body_json, headers_json
            )
        else:
            response_dict = format_response(status_code, body, headers, use_template=False)
            return json.dumps(response_dict)
            
    except Exception as e:
        log_error(f"JSON response formatting failed: {e}")
        return json.dumps({
            'statusCode': 500,
            'body': json.dumps({"error": "Response formatting failed"}),
            'headers': {'Content-Type': 'application/json'}
        })

# === OPERATION EXECUTION INTERFACE ===

def execute_operation(interface: GatewayInterface, operation: str, **kwargs):
    """Execute operation through specified interface."""
    try:
        if interface == GatewayInterface.LOGGING:
            logging_module = _gateway._get_module('logging_core')
            return getattr(logging_module, operation)(**kwargs)
        elif interface == GatewayInterface.METRICS:
            metrics_module = _gateway._get_module('metrics_core')
            return getattr(metrics_module, operation)(**kwargs)
        elif interface == GatewayInterface.CACHE:
            cache_module = _gateway._get_module('cache_core')
            return getattr(cache_module, operation)(**kwargs)
        elif interface == GatewayInterface.SECURITY:
            security_module = _gateway._get_module('security_core')
            return getattr(security_module, operation)(**kwargs)
        elif interface == GatewayInterface.HTTP:
            http_module = _gateway._get_module('http_client_core')
            return getattr(http_module, operation)(**kwargs)
        elif interface == GatewayInterface.UTILITY:
            util_module = _gateway._get_module('shared_utilities')
            return getattr(util_module, operation)(**kwargs)
        else:
            return {"success": False, "error": f"Unknown interface: {interface}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def initialize_lambda():
    """Initialize Lambda environment."""
    try:
        record_metric('lambda.initialization', 1.0)
        return True
    except Exception:
        return False

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics."""
    try:
        return {
            'loaded_modules': list(_gateway._loaded_modules),
            'module_count': len(_gateway._loaded_modules),
            'module_stats': _gateway._module_stats,
            'template_optimization_enabled': _USE_LAMBDA_TEMPLATES
        }
    except Exception:
        return {'error': 'Failed to get stats'}

def cleanup_gateway():
    """Cleanup gateway resources."""
    try:
        _gateway._modules.clear()
        _gateway._loaded_modules.clear()
        _gateway._module_stats.clear()
        return True
    except Exception:
        return False
