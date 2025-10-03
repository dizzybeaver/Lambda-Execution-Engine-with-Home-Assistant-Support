"""
HTTP Client Core - Gateway-Optimized HTTP Operations
Version: 2025.10.03.02
Description: Revolutionary gateway-integrated HTTP client with zero custom error handling

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
from typing import Any, Callable, Dict, Optional
from enum import Enum
from urllib.parse import urlencode


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HTTPClientCore:
    """Revolutionary gateway-integrated HTTP client - zero custom error handling."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=5.0, read=30.0),
            maxsize=10,
            block=False,
            retries=False
        )
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0
        }
    
    def get(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None,
            use_cache: bool = False, cache_ttl: int = 300, transform: Optional[Callable] = None) -> Dict:
        """HTTP GET with operation context and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, 
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('http_client', 'get', url=url, use_cache=use_cache)
        
        try:
            if use_cache:
                result = cache_operation_result(
                    operation_name="http_get",
                    func=lambda: self._execute_with_circuit_breaker(
                        'GET', url, headers=headers, timeout=timeout, transform=transform
                    ),
                    ttl=cache_ttl,
                    cache_key_prefix=f"http_get_{url}"
                )
            else:
                result = self._execute_with_circuit_breaker(
                    'GET', url, headers=headers, timeout=timeout, transform=transform
                )
            
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'get', e, context['correlation_id'])
    
    def post(self, url: str, data: Dict, headers: Optional[Dict] = None, 
             timeout: Optional[int] = None, transform: Optional[Callable] = None) -> Dict:
        """HTTP POST with operation context and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('http_client', 'post', url=url)
        
        try:
            result = self._execute_with_circuit_breaker(
                'POST', url, data=data, headers=headers, timeout=timeout, transform=transform
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'post', e, context['correlation_id'])
    
    def put(self, url: str, data: Dict, headers: Optional[Dict] = None, 
            timeout: Optional[int] = None, transform: Optional[Callable] = None) -> Dict:
        """HTTP PUT with operation context and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('http_client', 'put', url=url)
        
        try:
            result = self._execute_with_circuit_breaker(
                'PUT', url, data=data, headers=headers, timeout=timeout, transform=transform
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'put', e, context['correlation_id'])
    
    def delete(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None) -> Dict:
        """HTTP DELETE with operation context and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('http_client', 'delete', url=url)
        
        try:
            result = self._execute_with_circuit_breaker(
                'DELETE', url, headers=headers, timeout=timeout
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'delete', e, context['correlation_id'])
    
    def _execute_with_circuit_breaker(self, method: str, url: str, 
                                     data: Optional[Dict] = None,
                                     headers: Optional[Dict] = None,
                                     timeout: Optional[int] = None,
                                     transform: Optional[Callable] = None) -> Dict:
        """Execute HTTP request with circuit breaker protection."""
        try:
            from gateway import execute_with_circuit_breaker
            
            def _make_http_call():
                return self._request(method, url, data=data, headers=headers, 
                                   timeout=timeout, transform=transform)
            
            return execute_with_circuit_breaker(f"http_{method.lower()}_{url}", _make_http_call)
            
        except Exception:
            return self._request(method, url, data=data, headers=headers, 
                               timeout=timeout, transform=transform)
    
    def _request(self, method: str, url: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, timeout: Optional[int] = None,
                 transform: Optional[Callable] = None) -> Dict:
        """Core HTTP request - uses gateway standardized responses."""
        request_headers = headers or self.get_standard_headers()
        timeout_val = timeout or 30
        
        self._stats['requests'] += 1
        
        try:
            if data:
                body_data = json.dumps(data)
                response = self.http.request(
                    method, url, body=body_data, 
                    headers=request_headers, timeout=timeout_val
                )
            else:
                response = self.http.request(
                    method, url, headers=request_headers, timeout=timeout_val
                )
            
            self._stats['successful'] += 1
            
            try:
                response_data = json.loads(response.data.decode('utf-8')) if response.data else None
            except json.JSONDecodeError:
                response_data = response.data.decode('utf-8') if response.data else None
            
            result = {
                'success': True,
                'status_code': response.status,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
            if transform:
                result = self._apply_transformation(result, transform)
            
            return result
            
        except Exception as e:
            self._stats['failed'] += 1
            raise
    
    def _apply_transformation(self, result: Dict, transform: Callable) -> Dict:
        """Apply transformation to response data."""
        try:
            transformed_data = transform(result.get('data'))
            result['data'] = transformed_data
            result['transformed'] = True
            return result
        except Exception as e:
            result['transformation_error'] = str(e)
            return result
    
    def get_standard_headers(self, content_type: str = 'application/json') -> Dict[str, str]:
        """Get standard HTTP headers."""
        return {
            'Content-Type': content_type,
            'Accept': 'application/json',
            'User-Agent': 'Lambda-Execution-Engine/2.0'
        }
    
    def parse_headers_fast(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Fast header parsing."""
        if not headers:
            return self.get_standard_headers()
        
        parsed = {}
        for key, value in headers.items():
            parsed[key.strip().title()] = value.strip()
        
        return parsed
    
    def build_query_fast(self, params: Dict[str, Any]) -> str:
        """Fast query string building."""
        if not params:
            return ""
        return urlencode(params)
    
    def execute_http_method(self, method: HTTPMethod, url: str, **kwargs) -> Dict:
        """Generic HTTP method executor with operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('http_client', method.value.lower(), url=url)
        
        try:
            headers = kwargs.get('headers', self.get_standard_headers())
            body = kwargs.get('body')
            timeout = kwargs.get('timeout', 30)
            
            if method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
                body_data = json.dumps(body) if isinstance(body, dict) else body
                response = self.http.request(
                    method.value, url, body=body_data, 
                    headers=headers, timeout=timeout
                )
            else:
                response = self.http.request(
                    method.value, url, headers=headers, timeout=timeout
                )
            
            self._stats['successful'] += 1
            
            try:
                response_data = json.loads(response.data.decode('utf-8')) if response.data else None
            except json.JSONDecodeError:
                response_data = response.data.decode('utf-8') if response.data else None
            
            result = {
                'success': True,
                'status_code': response.status,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            self._stats['failed'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', method.value.lower(), e, context['correlation_id'])
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict:
        """Make HTTP request with method dispatch."""
        try:
            http_method = HTTPMethod[method.upper()]
            return self.execute_http_method(http_method, url, **kwargs)
        except KeyError:
            from .shared_utilities import handle_operation_error
            from .shared_utilities import create_operation_context
            context = create_operation_context('http_client', 'make_request')
            return handle_operation_error(
                'http_client', 'make_request', 
                ValueError(f"Invalid HTTP method: {method}"),
                context['correlation_id']
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        return {
            'total_requests': self._stats['requests'],
            'successful_requests': self._stats['successful'],
            'failed_requests': self._stats['failed'],
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


__all__ = [
    'HTTPMethod',
    'HTTPClientCore',
    'get_http_client',
]

# EOF
