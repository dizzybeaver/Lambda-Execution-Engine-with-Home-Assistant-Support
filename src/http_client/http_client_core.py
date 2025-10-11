"""
http_client_core.py
Version: 2025.10.11.01
Description: HTTP client with retry logic and gateway implementation functions

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
import urllib3
import time
from typing import Dict, Any, Optional, Callable
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods enumeration."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class HTTPClientCore:
    """Core HTTP client with retry and circuit breaker support."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            maxsize=10,
            retries=False  # Manual retry logic
        )
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        self._circuit_breakers = {}
        self._retry_config = {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2.0,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504}
        }
    
    def get_standard_headers(self) -> Dict[str, str]:
        """Get standard HTTP headers."""
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'LambdaExecutionEngine/1.0'
        }
    
    def _is_retriable_error(self, status_code: int) -> bool:
        """Check if error is retriable."""
        return status_code in self._retry_config['retriable_status_codes']
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base = self._retry_config['backoff_base_ms'] / 1000.0
        multiplier = self._retry_config['backoff_multiplier']
        return base * (multiplier ** attempt)
    
    def _execute_with_retry(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute request with retry logic."""
        last_error = None
        
        for attempt in range(self._retry_config['max_attempts']):
            try:
                result = self._execute_request(method, url, **kwargs)
                
                if result['success'] or not self._is_retriable_error(result.get('status_code', 0)):
                    return result
                
                last_error = result
                
                if attempt < self._retry_config['max_attempts'] - 1:
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)
                    self._stats['retries'] += 1
                    
            except Exception as e:
                last_error = {'success': False, 'error': str(e), 'status_code': 0}
                
                if attempt < self._retry_config['max_attempts'] - 1:
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)
                    self._stats['retries'] += 1
        
        return last_error or {'success': False, 'error': 'All retries exhausted'}
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute single HTTP request."""
        self._stats['requests'] += 1
        
        try:
            headers = kwargs.get('headers', self.get_standard_headers())
            data = kwargs.get('data')
            timeout = kwargs.get('timeout', 30)
            
            if method.upper() in ['POST', 'PUT', 'PATCH']:
                body = json.dumps(data) if isinstance(data, dict) else data
                response = self.http.request(
                    method.upper(),
                    url,
                    body=body,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = self.http.request(
                    method.upper(),
                    url,
                    headers=headers,
                    timeout=timeout
                )
            
            self._stats['successful'] += 1
            
            try:
                response_data = json.loads(response.data.decode('utf-8')) if response.data else None
            except:
                response_data = response.data.decode('utf-8') if response.data else None
            
            return {
                'success': True,
                'status_code': response.status,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'status_code': 0
            }
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry support."""
        use_retry = kwargs.pop('use_retry', True)
        
        if use_retry:
            return self._execute_with_retry(method, url, **kwargs)
        else:
            return self._execute_request(method, url, **kwargs)
    
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


_http_client_instance = None


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance."""
    global _http_client_instance
    if _http_client_instance is None:
        _http_client_instance = HTTPClientCore()
    return _http_client_instance


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


__all__ = [
    'HTTPMethod',
    'HTTPClientCore',
    'get_http_client',
    '_make_request_implementation',
    '_make_get_request_implementation',
    '_make_post_request_implementation'
]

# EOF
