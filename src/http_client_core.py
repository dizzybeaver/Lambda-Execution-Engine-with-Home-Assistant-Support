"""
http_client_core.py - HTTP Client Core Implementation
Version: 2025.10.18.01
Description: Core HTTPClientCore class and gateway implementation functions.

CRITICAL FIX:
- Remove 'url' from kwargs before passing to _make_http_request
- Prevents "got multiple values for argument 'url'" error

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import time
import urllib3
from typing import Dict, Any, Optional
from http_client_utilities import get_standard_headers


class HTTPClientCore:
    """Core HTTP client with retry and circuit breaker support."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            maxsize=10,
            retries=False
        )
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        self._retry_config = {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2.0,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504}
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return self._stats.copy()
    
    def _is_retriable_error(self, status_code: int) -> bool:
        """Check if error is retriable."""
        return status_code in self._retry_config['retriable_status_codes']
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_ms = self._retry_config['backoff_base_ms']
        multiplier = self._retry_config['backoff_multiplier']
        return (base_ms * (multiplier ** attempt)) / 1000.0
    
    def _validate_timeout(self, timeout: float) -> float:
        """Validate and bound timeout value."""
        if timeout <= 0:
            return 30.0
        if timeout > 900:
            return 900.0
        return timeout
    
    def _parse_response_data(self, response_data: bytes, content_type: str) -> Any:
        """Parse response data based on content type."""
        if not response_data:
            return {}
        
        try:
            decoded = response_data.decode('utf-8')
            
            if 'application/json' in content_type.lower():
                try:
                    return json.loads(decoded)
                except json.JSONDecodeError:
                    from gateway import log_warning
                    log_warning(f"Failed to parse JSON despite content-type: {content_type}")
                    return decoded
            
            try:
                return json.loads(decoded)
            except json.JSONDecodeError:
                return decoded
                
        except UnicodeDecodeError as e:
            from gateway import log_error
            log_error(f"Failed to decode response data: {e}")
            return response_data.hex()
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request."""
        try:
            headers = get_standard_headers()
            custom_headers = kwargs.get('headers', {})
            if custom_headers:
                headers.update(custom_headers)
            
            body = kwargs.get('json')
            if body:
                body = json.dumps(body)
                headers['Content-Type'] = 'application/json'
            
            timeout = self._validate_timeout(kwargs.get('timeout', 30.0))
            
            response = self.http.request(
                method=method,
                url=url,
                body=body,
                headers=headers,
                timeout=timeout
            )
            
            self._stats['requests'] += 1
            
            if 200 <= response.status < 300:
                self._stats['successful'] += 1
                
                content_type = dict(response.headers).get('content-type', '')
                parsed_data = self._parse_response_data(response.data, content_type)
                
                return {
                    'success': True,
                    'status_code': response.status,
                    'data': parsed_data,
                    'headers': dict(response.headers)
                }
            else:
                self._stats['failed'] += 1
                error_data = response.data.decode('utf-8') if response.data else ''
                
                return {
                    'success': False,
                    'status_code': response.status,
                    'error': f"HTTP {response.status}",
                    'data': error_data
                }
                
        except urllib3.exceptions.HTTPError as e:
            from gateway import log_error
            log_error(f"HTTP request failed: {str(e)}", error=e)
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'error_type': 'HTTPError'
            }
        except json.JSONDecodeError as e:
            from gateway import log_error
            log_error(f"JSON encoding failed: {str(e)}", error=e)
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': f"JSON encoding error: {str(e)}",
                'error_type': 'JSONDecodeError'
            }
        except Exception as e:
            from gateway import log_error
            log_error(f"Unexpected HTTP error: {str(e)}", error=e)
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute HTTP request with retry logic."""
        max_attempts = self._retry_config['max_attempts']
        
        for attempt in range(max_attempts):
            result = self._execute_request(method, url, **kwargs)
            
            if result.get('success'):
                return result
            
            status_code = result.get('status_code', 0)
            if attempt < max_attempts - 1 and self._is_retriable_error(status_code):
                self._stats['retries'] += 1
                backoff = self._calculate_backoff(attempt)
                time.sleep(backoff)
                continue
            
            return result
        
        return {
            'success': False,
            'error': 'Max retry attempts exceeded',
            'attempts': max_attempts
        }


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance."""
    from gateway import execute_operation, GatewayInterface
    
    def factory():
        return HTTPClientCore()
    
    return execute_operation(
        GatewayInterface.SINGLETON,
        'get',
        name='http_client_core',
        factory_func=factory
    )


def _make_http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP request via singleton."""
    client = get_http_client()
    return client.make_request(method, url, **kwargs)


def http_request_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP request."""
    method = kwargs.pop('method', 'GET')
    url = kwargs.pop('url', '')
    return _make_http_request(method, url, **kwargs)


def http_get_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP GET."""
    url = kwargs.pop('url', '')
    return _make_http_request('GET', url, **kwargs)


def http_post_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP POST."""
    url = kwargs.pop('url', '')
    return _make_http_request('POST', url, **kwargs)


def http_put_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP PUT."""
    url = kwargs.pop('url', '')
    return _make_http_request('PUT', url, **kwargs)


def http_delete_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP DELETE."""
    url = kwargs.pop('url', '')
    return _make_http_request('DELETE', url, **kwargs)


def get_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for get state."""
    from http_client_state import get_client_state
    return get_client_state(**kwargs)


def reset_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for reset state."""
    from http_client_state import reset_client_state
    return reset_client_state(**kwargs)


__all__ = [
    'HTTPClientCore',
    'get_http_client',
    'http_request_implementation',
    'http_get_implementation',
    'http_post_implementation',
    'http_put_implementation',
    'http_delete_implementation',
    'get_state_implementation',
    'reset_state_implementation',
]

# EOF
