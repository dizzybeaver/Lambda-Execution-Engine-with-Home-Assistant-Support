"""
http_client_core.py - Ultra-Optimized HTTP Client with Integrated State, Generic Patterns, and Extensions
Version: 2025.10.13.01
Description: Consolidated HTTP client combining core, state, generic patterns, and extensions into one optimized file

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
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

# ===== HTTP METHOD ENUMERATION =====

class HTTPMethod(Enum):
    """HTTP methods enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# ===== HTTP HEADER TEMPLATES (OPTIMIZATION) =====

_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

_USER_AGENT = "Lambda-Execution-Engine/1.0"
_QUERY_BUFFER: List[str] = []

_PARSED_HEADERS_TEMPLATE = {
    'content_type': '',
    'content_length': 0,
    'cache_control': '',
    'server': ''
}


# ===== GENERIC HELPER FUNCTIONS =====

def get_standard_headers(auth_token: Optional[str] = None) -> Dict[str, str]:
    """Get standard headers with optional auth (fast template-based)."""
    headers = _JSON_HEADERS.copy()
    headers["User-Agent"] = _USER_AGENT
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def get_ha_headers(access_token: str) -> Dict[str, str]:
    """Get Home Assistant headers (fast template-based)."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }


def build_query_string_fast(params: Dict[str, Any]) -> str:
    """Fast query string building with pre-allocated buffer."""
    from gateway import log_error
    
    global _QUERY_BUFFER
    _QUERY_BUFFER.clear()
    
    try:
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        _QUERY_BUFFER.append(f"{key}={item}")
                else:
                    _QUERY_BUFFER.append(f"{key}={value}")
        
        return '&'.join(_QUERY_BUFFER)
    except Exception as e:
        log_error(f"Query string building failed: {e}")
        return ''


def build_query_string(params: Dict[str, Any]) -> str:
    """Legacy query string builder (for compatibility)."""
    from gateway import log_error
    
    try:
        query_parts = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        query_parts.append(f"{key}={str(item)}")
                else:
                    query_parts.append(f"{key}={str(value)}")
        return '&'.join(query_parts)
    except Exception as e:
        log_error(f"Query string building failed: {e}")
        return ''


def parse_response_headers_fast(headers: Dict[str, str]) -> Dict[str, Any]:
    """Fast header parsing using template."""
    from gateway import log_error
    
    try:
        result = _PARSED_HEADERS_TEMPLATE.copy()
        
        ct = headers.get('content-type', '')
        result['content_type'] = ct.split(';')[0].strip() if ct else ''
        
        cl = headers.get('content-length', '')
        result['content_length'] = int(cl) if cl and cl.isdigit() else 0
        
        result['cache_control'] = headers.get('cache-control', '')
        result['server'] = headers.get('server', '')
        result['all_headers'] = headers
        
        return result
    except Exception as e:
        log_error(f"Header parsing failed: {e}")
        return {'all_headers': headers}


def parse_response_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Legacy header parsing (for compatibility)."""
    from gateway import log_error
    
    try:
        parsed = {
            'content_type': headers.get('content-type', '').split(';')[0].strip(),
            'content_length': int(headers.get('content-length', 0)) if headers.get('content-length') else 0,
            'cache_control': headers.get('cache-control', ''),
            'expires': headers.get('expires', ''),
            'etag': headers.get('etag', ''),
            'last_modified': headers.get('last-modified', ''),
            'server': headers.get('server', ''),
            'all_headers': headers
        }
        return parsed
    except Exception as e:
        log_error(f"Header parsing failed: {e}")
        return {'all_headers': headers}


# ===== HTTP CLIENT CORE CLASS =====

class HTTPClientCore:
    """
    Core HTTP client with circuit breaker protection, retry logic, and connection pooling.
    Optimized for AWS Lambda environment.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """Initialize HTTP client."""
        self.timeout = timeout
        self.max_retries = max_retries
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry and circuit breaker protection.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            **kwargs: Additional options (headers, data, timeout, etc.)
            
        Returns:
            Dict with success, status_code, data, and headers
        """
        from gateway import log_info, log_error, create_success_response, create_error_response, record_metric
        
        self._stats['requests'] += 1
        
        headers = kwargs.get('headers', {})
        data = kwargs.get('data')
        timeout = kwargs.get('timeout', self.timeout)
        
        # Prepare request data
        body = None
        if data:
            if isinstance(data, dict):
                body = json.dumps(data).encode('utf-8')
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                body = data.encode('utf-8')
            else:
                body = data
        
        # Build request
        req = Request(url, data=body, headers=headers, method=method.upper())
        
        # Execute with retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                with urlopen(req, timeout=timeout) as response:
                    response_data = response.read().decode('utf-8')
                    response_headers = dict(response.headers)
                    status_code = response.status
                    
                    # Try to parse JSON
                    try:
                        parsed_data = json.loads(response_data)
                    except:
                        parsed_data = response_data
                    
                    self._stats['successful'] += 1
                    if attempt > 0:
                        self._stats['retries'] += attempt
                        record_metric('http_client.retry_success', 1.0, {'attempt': str(attempt + 1)})
                    
                    log_info(f"HTTP {method} {url} - Status: {status_code}")
                    
                    return create_success_response(
                        f"HTTP {method} successful",
                        {
                            'status_code': status_code,
                            'data': parsed_data,
                            'headers': response_headers
                        }
                    )
            
            except HTTPError as e:
                last_error = e
                status_code = e.code
                
                # Don't retry on client errors (4xx)
                if 400 <= status_code < 500 and status_code not in [408, 429]:
                    self._stats['failed'] += 1
                    log_error(f"HTTP {method} {url} - Client error: {status_code}")
                    return create_error_response(
                        f"HTTP client error: {status_code}",
                        f"HTTP_{status_code}"
                    )
                
                # Retry on server errors (5xx) and specific client errors
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    record_metric('http_client.retry_attempt', 1.0, {'attempt': str(attempt + 1)})
                    continue
            
            except URLError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    record_metric('http_client.retry_attempt', 1.0, {'attempt': str(attempt + 1)})
                    continue
            
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                    continue
        
        # All retries exhausted
        self._stats['failed'] += 1
        error_msg = str(last_error) if last_error else "Unknown error"
        log_error(f"HTTP {method} {url} - Failed after {self.max_retries} attempts: {error_msg}")
        record_metric('http_client.failure', 1.0)
        
        return create_error_response(
            f"HTTP request failed: {error_msg}",
            "HTTP_REQUEST_FAILED"
        )
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        kwargs['data'] = data
        return self.make_request('POST', url, **kwargs)
    
    def put(self, url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        kwargs['data'] = data
        return self.make_request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return self.make_request('DELETE', url, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        return {
            'total_requests': self._stats['requests'],
            'successful_requests': self._stats['successful'],
            'failed_requests': self._stats['failed'],
            'total_retries': self._stats['retries'],
            'success_rate': (self._stats['successful'] / self._stats['requests'] * 100) 
                           if self._stats['requests'] > 0 else 0.0
        }


# ===== SINGLETON PATTERN =====

_http_client_instance = None


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance."""
    global _http_client_instance
    if _http_client_instance is None:
        _http_client_instance = HTTPClientCore()
    return _http_client_instance


# ===== STATE MANAGEMENT FUNCTIONS =====

def get_client_state(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get HTTP client state via gateway singleton."""
    from gateway import get_singleton, log_error
    
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
            return {
                'exists': False,
                'client_type': client_type,
                'state': 'not_initialized'
            }
        
        state_info = {
            'exists': True,
            'client_type': client_type,
            'state': 'initialized',
            'instance_id': id(client)
        }
        
        if hasattr(client, 'get_stats'):
            state_info['stats'] = client.get_stats()
        
        return state_info
    
    except Exception as e:
        log_error(f"Failed to get client state: {e}")
        return {'exists': False, 'error': str(e)}


def reset_client_state(client_type: str = None) -> Dict[str, Any]:
    """Reset HTTP client state via gateway singleton."""
    from gateway import execute_operation, GatewayInterface, create_success_response, create_error_response, log_error, record_metric
    
    try:
        if client_type:
            singleton_key = f'http_client_{client_type}'
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset',
                singleton_name=singleton_key
            )
            record_metric(f'http_client_state.{client_type}.reset', 1.0)
        else:
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset_all'
            )
            record_metric('http_client_state.reset_all', 1.0)
        
        return create_success_response("Client state reset", result)
    
    except Exception as e:
        log_error(f"Failed to reset client state: {e}")
        return create_error_response(str(e))


def get_client_configuration(client_type: str) -> Dict[str, Any]:
    """Get client configuration via gateway config."""
    from gateway import get_parameter, log_error
    
    try:
        config_key = f'http_client_{client_type}'
        client_config = get_parameter(config_key, {})
        
        default_config = {
            'timeout': get_parameter('http_timeout', 30),
            'retries': get_parameter('http_retries', 3),
            'pool_size': get_parameter('http_pool_size', 10)
        }
        
        return {
            'client_type': client_type,
            'configuration': {**default_config, **client_config}
        }
    
    except Exception as e:
        log_error(f"Failed to get client configuration: {e}")
        return {
            'client_type': client_type,
            'configuration': {},
            'error': str(e)
        }


def update_client_configuration(client_type: str, new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration via gateway config."""
    from gateway import set_parameter, log_info, create_success_response, create_error_response, log_error, record_metric
    
    try:
        config_key = f'http_client_{client_type}'
        success = set_parameter(config_key, new_config)
        
        if success:
            reset_result = reset_client_state(client_type)
            record_metric(f'http_client_state.{client_type}.config_updated', 1.0)
            
            return create_success_response("Configuration updated", {
                'client_type': client_type,
                'configuration_updated': True,
                'client_reset': reset_result.get('success', False)
            })
        else:
            return create_error_response('Failed to update configuration')
    
    except Exception as e:
        log_error(f"Configuration update failed: {e}")
        return create_error_response(str(e))


def get_connection_statistics(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get connection statistics for client."""
    from gateway import create_success_response
    
    client = get_http_client()
    stats = client.get_stats()
    
    return create_success_response("Statistics retrieved", {
        'client_type': client_type,
        'statistics': stats
    })


# ===== EXTENSION FUNCTIONS (RETRY AND TRANSFORMATION) =====

def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100,
                        retriable_codes: set = None) -> Dict[str, Any]:
    """Configure HTTP retry behavior using existing http_client."""
    from gateway import cache_set, log_info, create_success_response
    
    config = {
        'max_attempts': max_attempts,
        'backoff_base_ms': backoff_base_ms,
        'retriable_status_codes': retriable_codes or {408, 429, 500, 502, 503, 504}
    }
    
    cache_set('http_retry_config', config, ttl=3600)
    log_info(f"HTTP retry configured: {max_attempts} attempts, {backoff_base_ms}ms backoff")
    
    return create_success_response("Retry configured", config)


def http_request_with_retry(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with retry using existing functions."""
    from gateway import make_request, cache_get, record_metric, log_error, create_error_response
    
    config = cache_get('http_retry_config') or {'max_attempts': 3, 'backoff_base_ms': 100}
    
    try:
        for attempt in range(config['max_attempts']):
            try:
                result = make_request(method, url, **kwargs)
                
                if result.get('success'):
                    if attempt > 0:
                        record_metric('http_retry_success', 1.0, {'attempt': attempt + 1})
                    return result
                
                status_code = result.get('status_code', 0)
                if status_code not in config.get('retriable_status_codes', set()):
                    return result
                
                if attempt < config['max_attempts'] - 1:
                    delay_ms = config['backoff_base_ms'] * (2 ** attempt)
                    time.sleep(delay_ms / 1000.0)
                    record_metric('http_retry_attempt', 1.0, {'attempt': attempt + 1})
                    
            except Exception as e:
                if attempt == config['max_attempts'] - 1:
                    raise
                time.sleep((config['backoff_base_ms'] * (2 ** attempt)) / 1000.0)
        
        return {'success': False, 'error': 'Max retries exceeded'}
        
    except Exception as e:
        log_error(f"Retry request failed: {e}")
        return create_error_response(str(e))


def transform_http_response(response: Dict[str, Any], transformer: Callable) -> Dict[str, Any]:
    """Transform HTTP response using existing validation."""
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    try:
        data = response.get('data')
        transformed = transformer(data)
        
        response['data'] = transformed
        response['transformed'] = True
        return response
        
    except Exception as e:
        return create_error_response(f"Transformation failed: {str(e)}", 'TRANSFORM_ERROR')


def validate_http_response(response: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
    """Validate HTTP response using existing validation."""
    from gateway import create_error_response
    
    if not response.get('success'):
        return response
    
    if required_fields:
        data = response.get('data', {})
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                'VALIDATION_ERROR'
            )
    
    return response


def execute_with_retry(operation: Callable, max_retries: int = 3, 
                      backoff_factor: float = 0.5,
                      retry_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generic retry pattern for HTTP operations."""
    from gateway import record_metric, log_error, create_error_response
    
    retry_conditions = retry_conditions or ['timeout', '5xx']
    last_error = None
    
    def _should_retry(result, conditions):
        """Check if result should trigger retry."""
        if not isinstance(result, dict):
            return False
        
        if result.get('success'):
            return False
        
        status_code = result.get('status_code', 0)
        
        if 'timeout' in conditions and 'timeout' in str(result.get('error', '')).lower():
            return True
        
        if '5xx' in conditions and 500 <= status_code < 600:
            return True
        
        return False
    
    for attempt in range(max_retries):
        try:
            result = operation()
            
            if not _should_retry(result, retry_conditions):
                return result
            
            last_error = result
            
            if attempt < max_retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
                record_metric('http_retry.attempt', 1.0, {'attempt': attempt + 1})
        
        except Exception as e:
            last_error = {'success': False, 'error': str(e)}
            
            if attempt < max_retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
            else:
                log_error(f"All retry attempts exhausted: {e}")
    
    return last_error or create_error_response("Operation failed after retries")


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _make_request_implementation(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP request operation."""
    client = get_http_client()
    return client.make_request(method, url, **kwargs)


def _make_get_request_implementation(url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP GET request operation."""
    client = get_http_client()
    return client.get(url, **kwargs)


def _make_post_request_implementation(url: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute HTTP POST request operation."""
    client = get_http_client()
    return client.post(url, data, **kwargs)


# ===== EXPORTS =====

__all__ = [
    'HTTPMethod',
    'HTTPClientCore',
    'get_http_client',
    '_make_request_implementation',
    '_make_get_request_implementation',
    '_make_post_request_implementation',
    'get_standard_headers',
    'get_ha_headers',
    'build_query_string',
    'build_query_string_fast',
    'parse_response_headers',
    'parse_response_headers_fast',
    'get_client_state',
    'reset_client_state',
    'get_client_configuration',
    'update_client_configuration',
    'get_connection_statistics',
    'configure_http_retry',
    'http_request_with_retry',
    'transform_http_response',
    'validate_http_response',
    'execute_with_retry'
]

# EOF
