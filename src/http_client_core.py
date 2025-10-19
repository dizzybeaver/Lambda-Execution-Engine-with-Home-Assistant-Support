"""
http_client_core.py - HTTP Client Core Implementation (JSON FIX)
Version: 2025.10.19.JSON_FIX
Description: CRITICAL FIX - Handle 'json' kwarg correctly (was ignoring it!)

BUG FIX:
- BEFORE: Only looked for 'body' kwarg, ignored 'json' kwarg
- AFTER: Properly handles 'json' kwarg by encoding it to JSON bytes
- IMPACT: Home Assistant API calls were sending NO BODY DATA!

CHANGELOG:
- 2025.10.19.JSON_FIX: Fix json kwarg handling in _execute_request
- 2025.10.19.SELECTIVE: Use preloaded urllib3 from lambda_preload
- 2025.10.18.03: Encode JSON body to bytes (matches working Lambda)
- 2025.10.18.02: Added SSL verification support (CRITICAL)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import time
from typing import Dict, Any, Optional

# Import preloaded urllib3 classes (already initialized during Lambda INIT!)
from lambda_preload import PoolManager, Timeout

from http_client_utilities import get_standard_headers


class HTTPClientCore:
    """Core HTTP client with retry and circuit breaker support."""
    
    def __init__(self):
        # Read SSL verification setting from environment
        # Defaults to True (verify SSL) for security
        verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
        verify_ssl = verify_ssl_env != 'false'
        
        # Set cert_reqs based on verification setting
        cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
        
        # Use preloaded classes (NO IMPORT OVERHEAD!)
        self.http = PoolManager(
            cert_reqs=cert_reqs,
            timeout=Timeout(connect=10.0, read=30.0),
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
        
        # Log SSL configuration (debug only)
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            from gateway import log_debug
            log_debug(f"HTTP client initialized: verify_ssl={verify_ssl}, cert_reqs={cert_reqs}")
    
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
        delay_ms = base_ms * (multiplier ** attempt)
        return delay_ms / 1000.0
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request with error handling."""
        try:
            self._stats['requests'] += 1
            
            # Get headers (add standard headers if not provided)
            headers = kwargs.get('headers', {})
            if not headers:
                headers = get_standard_headers()
            elif not isinstance(headers, dict):
                headers = get_standard_headers()
            
            # Handle JSON body encoding (CRITICAL FIX 2025.10.19.JSON_FIX)
            body = None
            
            if kwargs.get('json'):
                # JSON mode - encode 'json' kwarg to bytes
                json_data = kwargs.get('json')
                body = json.dumps(json_data).encode('utf-8')
                headers.setdefault('Content-Type', 'application/json')
            elif kwargs.get('body'):
                # Body mode - use 'body' kwarg directly
                body = kwargs.get('body')
                if isinstance(body, str):
                    body = body.encode('utf-8')
            
            # Execute request
            response = self.http.request(
                method,
                url,
                headers=headers,
                body=body,
                timeout=kwargs.get('timeout')
            )
            
            # Parse response
            status_code = response.status
            success = 200 <= status_code < 300
            
            # Try to decode response body
            response_data = None
            try:
                response_body = response.data.decode('utf-8')
                if response_body:
                    response_data = json.loads(response_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = response.data
            
            if success:
                self._stats['successful'] += 1
            else:
                self._stats['failed'] += 1
            
            return {
                'success': success,
                'status_code': status_code,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            from gateway import log_error
            log_error(f"HTTP request failed: {str(e)}", error=e)
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
