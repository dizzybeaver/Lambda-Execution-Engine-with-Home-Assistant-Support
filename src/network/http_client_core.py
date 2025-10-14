"""
http_client_core.py - HTTP Client Core Implementation
Version: 2025.10.14.01
Description: Core HTTPClientCore class and gateway implementation functions.
             Internal module - accessed via http_client.py interface.

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
import urllib3
from typing import Dict, Any, Optional
from network.http_client_utilities import get_standard_headers


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
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request."""
        from gateway import create_success_response, create_error_response
        
        headers = kwargs.get('headers', get_standard_headers())
        body = kwargs.get('body')
        
        try:
            if body and isinstance(body, dict):
                body = json.dumps(body)
            
            response = self.http.request(
                method,
                url,
                headers=headers,
                body=body
            )
            
            try:
                data = json.loads(response.data.decode('utf-8'))
            except:
                data = response.data.decode('utf-8')
            
            return create_success_response(
                f"{method} request successful",
                {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'data': data
                }
            )
            
        except Exception as e:
            return create_error_response(f"Request failed: {str(e)}", 'HTTP_ERROR')
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        from gateway import log_info, log_error, increment_counter
        
        max_attempts = self._retry_config['max_attempts']
        
        self._stats['requests'] += 1
        
        for attempt in range(max_attempts):
            response = self._execute_request(method, url, **kwargs)
            
            if response.get('success'):
                self._stats['successful'] += 1
                increment_counter('http_client.success')
                return response
            
            status_code = response.get('data', {}).get('status_code', 0)
            
            if not self._is_retriable_error(status_code) or attempt == max_attempts - 1:
                self._stats['failed'] += 1
                increment_counter('http_client.failure')
                return response
            
            self._stats['retries'] += 1
            backoff = self._calculate_backoff(attempt)
            log_info(f"Retry {attempt + 1}/{max_attempts} after {backoff}s")
            time.sleep(backoff)
        
        self._stats['failed'] += 1
        return response


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


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def http_request_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP request."""
    method = kwargs.get('method', 'GET')
    url = kwargs.get('url', '')
    return _make_http_request(method, url, **kwargs)


def http_get_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP GET."""
    url = kwargs.get('url', '')
    return _make_http_request('GET', url, **kwargs)


def http_post_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP POST."""
    url = kwargs.get('url', '')
    return _make_http_request('POST', url, **kwargs)


def http_put_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP PUT."""
    url = kwargs.get('url', '')
    return _make_http_request('PUT', url, **kwargs)


def http_delete_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP DELETE."""
    url = kwargs.get('url', '')
    return _make_http_request('DELETE', url, **kwargs)


def get_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for get state."""
    from network.http_client_state import get_client_state
    return get_client_state(**kwargs)


def reset_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for reset state."""
    from network.http_client_state import reset_client_state
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
