"""
Gateway Core - Revolutionary Gateway Architecture with Complete Template Optimization Integration
Version: 2025.10.03.01
Description: Central gateway with all template optimization modules integrated

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

# ===== LAMBDA RESPONSE TEMPLATES =====

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
    ERROR_CONTEXT = "error_context"
    HEALTH_DATA = "health_data"

class GatewayCore:
    """Core gateway implementation with lazy loading and complete module integration."""
    
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
                elif module_name == 'error_context_core':
                    from error_context_core import ErrorContextManager, get_error_context_manager
                    self._modules[module_name] = get_error_context_manager()
                elif module_name == 'health_data_core':
                    from health_data_core import HealthDataManager, get_health_data_manager
                    self._modules[module_name] = get_health_data_manager()
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

# ===== LOGGING INTERFACE =====

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

def log_cache_hit(key: str, correlation_id: str, access_count: int, source_module: str):
    """Log cache hit using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_cache_hit(key, correlation_id, access_count, source_module)
    except Exception:
        pass

def log_cache_miss(key: str, correlation_id: str):
    """Log cache miss using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_cache_miss(key, correlation_id)
    except Exception:
        pass

def log_http_request(method: str, url: str, correlation_id: str):
    """Log HTTP request using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_http_request(method, url, correlation_id)
    except Exception:
        pass

def log_http_success(method: str, url: str, response_time_ms: int, status_code: int, correlation_id: str):
    """Log HTTP success using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_http_success(method, url, response_time_ms, status_code, correlation_id)
    except Exception:
        pass

def log_operation_start(interface: str, operation: str, correlation_id: str):
    """Log operation start using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_operation_start(interface, operation, correlation_id)
    except Exception:
        pass

def log_operation_success(interface: str, operation: str, duration_ms: int, correlation_id: str):
    """Log operation success using template optimization."""
    try:
        logging_module = _gateway._get_module('logging_core')
        return logging_module.log_operation_success(interface, operation, duration_ms, correlation_id)
    except Exception:
        pass

# ===== HTTP CLIENT INTERFACE =====

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

def get_standard_headers(content_type: str = 'json'):
    """Get standard HTTP headers using template optimization."""
    try:
        http_module = _gateway._get_module('http_client_core')
        return http_module.get_standard_headers(content_type)
    except Exception:
        return {"Content-Type": "application/json"}

def parse_headers_fast(headers_dict: Dict[str, str]):
    """Parse HTTP headers using template optimization."""
    try:
        http_module = _gateway._get_module('http_client_core')
        return http_module.parse_headers_fast(headers_dict)
    except Exception:
        return {}

def build_query_fast(params: Dict[str, Any]):
    """Build query string using template optimization."""
    try:
        http_module = _gateway._get_module('http_client_core')
        return http_module.build_query_fast(params)
    except Exception:
        return ""

# ===== ERROR CONTEXT INTERFACE =====

def create_error_context(interface: str, operation: str, correlation_id: Optional[str] = None, 
                        error_code: Optional[str] = None, details: Optional[Dict] = None, 
                        use_cache: bool = True) -> Dict[str, Any]:
    """Create error context using template optimization."""
    try:
        error_module = _gateway._get_module('error_context_core')
        return error_module.create_error_context(interface, operation, correlation_id, error_code, details, use_cache)
    except Exception:
        return {
            'interface': interface,
            'operation': operation,
            'correlation_id': correlation_id or 'unknown',
            'timestamp': 0.0
        }

def create_validation_error_context(field: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create validation error context using specialized template."""
    try:
        error_module = _gateway._get_module('error_context_core')
        return error_module.create_validation_context(field, correlation_id)
    except Exception:
        return {
            'interface': 'validation',
            'field': field,
            'correlation_id': correlation_id or 'unknown'
        }

def create_http_error_context(operation: str, url: str, status_code: int, 
                             correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create HTTP error context using specialized template."""
    try:
        error_module = _gateway._get_module('error_context_core')
        return error_module.create_http_context(operation, url, status_code, correlation_id)
    except Exception:
        return {
            'interface': 'http',
            'operation': operation,
            'url': url,
            'status_code': status_code,
            'correlation_id': correlation_id or 'unknown'
        }

def create_cache_error_context(operation: str, key: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create cache error context using specialized template."""
    try:
        error_module = _gateway._get_module('error_context_core')
        return error_module.create_cache_context(operation, key, correlation_id)
    except Exception:
        return {
            'interface': 'cache',
            'operation': operation,
            'key': key,
            'correlation_id': correlation_id or 'unknown'
        }

def create_ha_error_context(operation: str, entity_id: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create Home Assistant error context using specialized template."""
    try:
        error_module = _gateway._get_module('error_context_core')
        return error_module.create_ha_context(operation, entity_id, correlation_id)
    except Exception:
        return {
            'interface': 'homeassistant',
            'operation': operation,
            'entity_id': entity_id,
            'correlation_id': correlation_id or 'unknown'
        }

def generate_correlation_id() -> str:
    """Generate correlation ID using fast template-based counter."""
    try:
        error_module = _gateway._get_module('error_context_core')
        if hasattr(error_module, 'generate_correlation_id_fast'):
            from error_context_core import generate_correlation_id_fast
            return generate_correlation_id_fast()
        else:
            import time
            return f"corr-{int(time.time() * 1000)}"
    except Exception:
        import time
        return f"corr-{int(time.time() * 1000)}"

# ===== HEALTH DATA INTERFACE =====

def get_health_data(component: str, use_cache: bool = True) -> Dict[str, Any]:
    """Get health data for component using template optimization."""
    try:
        health_module = _gateway._get_module('health_data_core')
        return health_module.get_health_data(component, use_cache)
    except Exception:
        return {
            'component_name': component,
            'status': 'unknown',
            'error': 'Health module unavailable'
        }

def update_health_data(component: str, health_data: Dict[str, Any], store_in_history: bool = True):
    """Update health data for component."""
    try:
        health_module = _gateway._get_module('health_data_core')
        return health_module.update_health_data(component, health_data, store_in_history)
    except Exception:
        pass

def get_combined_health(components: Optional[list] = None) -> Dict[str, Any]:
    """Get combined health data for multiple components."""
    try:
        health_module = _gateway._get_module('health_data_core')
        return health_module.get_combined_health(components)
    except Exception:
        return {
            'overall_status': 'unknown',
            'overall_score': 0.0,
            'components': {},
            'error': 'Health module unavailable'
        }

def get_health_trends(component: Optional[str] = None, time_window_seconds: int = 3600):
    """Get health trends for component within time window."""
    try:
        health_module = _gateway._get_module('health_data_core')
        return health_module.get_health_trends(component, time_window_seconds)
    except Exception:
        return []

def clear_health_cache(component: Optional[str] = None):
    """Clear health cache for component or all components."""
    try:
        health_module = _gateway._get_module('health_data_core')
        return health_module.clear_health_cache(component)
    except Exception:
        pass

# ===== CACHE INTERFACE =====

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

def cache_clear() -> bool:
    """Clear cache."""
    try:
        cache_module = _gateway._get_module('cache_core')
        return cache_module.clear()
    except Exception:
        return False

# ===== SECURITY INTERFACE =====

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

def encrypt_data(data: str) -> str:
    """Encrypt data."""
    try:
        security_module = _gateway._get_module('security_core')
        return security_module.encrypt_data(data)
    except Exception:
        return data

def decrypt_data(data: str) -> str:
    """Decrypt data."""
    try:
        security_module = _gateway._get_module('security_core')
        return security_module.decrypt_data(data)
    except Exception:
        return data

# ===== METRICS INTERFACE =====

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

# ===== UTILITY INTERFACE =====

def create_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create success response."""
    try:
        utility_module = _gateway._get_module('shared_utilities')
        return utility_module.create_success_response(message, data)
    except Exception:
        return {"success": True, "message": message, "data": data}

def create_error_response(error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create error response."""
    try:
        utility_module = _gateway._get_module('shared_utilities')
        return utility_module.create_error_response(error, details)
    except Exception:
        return {"success": False, "error": error, "details": details}

def parse_json_safely(json_str: str) -> Optional[Dict[str, Any]]:
    """Parse JSON safely."""
    try:
        return json.loads(json_str)
    except Exception:
        return None

# ===== SINGLETON MANAGEMENT =====

_singletons = {}

def get_singleton(name: str):
    """Get singleton instance."""
    return _singletons.get(name)

def register_singleton(name: str, instance: Any):
    """Register singleton instance."""
    _singletons[name] = instance

def execute_operation(interface: GatewayInterface, operation: str, **kwargs):
    """Execute operation through gateway interface."""
    pass

# ===== LAMBDA RESPONSE FORMATTING =====

def format_response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Format Lambda response using template optimization."""
    try:
        if _USE_LAMBDA_TEMPLATES:
            if headers:
                headers_json = json.dumps(headers)
            else:
                headers_json = _DEFAULT_LAMBDA_HEADERS if status_code == 200 else _LAMBDA_ERROR_HEADERS
            
            body_json = json.dumps(body)
            response_str = _LAMBDA_RESPONSE_TEMPLATE % (status_code, body_json, headers_json)
            return json.loads(response_str)
        else:
            return {
                "statusCode": status_code,
                "body": json.dumps(body),
                "headers": headers or {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }
    except Exception:
        return {
            "statusCode": status_code,
            "body": json.dumps(body),
            "headers": {"Content-Type": "application/json"}
        }

def format_response_json(status_code: int, body: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Format Lambda response with pre-serialized JSON body."""
    try:
        if _USE_LAMBDA_TEMPLATES:
            if headers:
                headers_json = json.dumps(headers)
            else:
                headers_json = _DEFAULT_LAMBDA_HEADERS if status_code == 200 else _LAMBDA_ERROR_HEADERS
            
            response_str = _LAMBDA_RESPONSE_TEMPLATE % (status_code, body, headers_json)
            return json.loads(response_str)
        else:
            return {
                "statusCode": status_code,
                "body": body,
                "headers": headers or {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }
    except Exception:
        return {
            "statusCode": status_code,
            "body": body,
            "headers": {"Content-Type": "application/json"}
        }

# ===== INITIALIZATION INTERFACE =====

def execute_initialization_operation(operation_type: str, **kwargs):
    """Execute initialization operation."""
    pass

def record_initialization_stage(stage: str, **kwargs):
    """Record initialization stage."""
    pass

# ===== GATEWAY STATISTICS =====

def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics including module loading and template usage."""
    stats = {
        'loaded_modules': list(_gateway._loaded_modules),
        'module_stats': _gateway._module_stats.copy(),
        'template_optimization_enabled': {
            'lambda_responses': _USE_LAMBDA_TEMPLATES
        }
    }
    
    try:
        logging_module = _gateway._get_module('logging_core')
        if hasattr(logging_module, 'get_stats'):
            stats['logging'] = logging_module.get_stats()
    except:
        pass
    
    try:
        http_module = _gateway._get_module('http_client_core')
        if hasattr(http_module, 'get_stats'):
            stats['http_client'] = http_module.get_stats()
    except:
        pass
    
    try:
        error_module = _gateway._get_module('error_context_core')
        if hasattr(error_module, 'get_stats'):
            stats['error_context'] = error_module.get_stats()
    except:
        pass
    
    try:
        health_module = _gateway._get_module('health_data_core')
        if hasattr(health_module, 'get_stats'):
            stats['health_data'] = health_module.get_stats()
    except:
        pass
    
    return stats

def get_fast_path_stats():
    """Get fast path statistics."""
    return {}

def enable_fast_path():
    """Enable fast path optimization."""
    pass

def disable_fast_path():
    """Disable fast path optimization."""
    pass

def reset_fast_path_stats():
    """Reset fast path statistics."""
    pass

# EOF
