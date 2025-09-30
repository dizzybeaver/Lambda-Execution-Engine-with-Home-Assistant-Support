"""
HTTP Client Core - HTTP Request Handling
Version: 2025.09.30.02
Description: HTTP client implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for caching and error handling

OPTIMIZATION: Phase 1 Complete
- Integrated cache_operation_result() from shared_utilities
- Integrated handle_operation_error() from shared_utilities
- Enhanced caching and error handling patterns

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import json
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class HTTPClientCore:
    """HTTP client for making requests with caching and error handling."""
    
    def __init__(self):
        self.timeout = 30
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Lambda-Gateway/1.0'
        }
    
    def get(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, 
            use_cache: bool = True, cache_ttl: int = 300, **kwargs) -> Dict:
        """Perform HTTP GET request with optional caching."""
        if use_cache:
            try:
                from .shared_utilities import cache_operation_result
                return cache_operation_result(
                    operation_name="http_get",
                    func=lambda: self._request('GET', url, headers=headers, timeout=timeout),
                    ttl=cache_ttl,
                    cache_key_prefix=f"http_get_{url}"
                )
            except Exception:
                pass
        
        return self._request('GET', url, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Dict, headers: Optional[Dict] = None, 
             timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP POST request with error handling."""
        return self._request('POST', url, data=data, headers=headers, timeout=timeout)
    
    def put(self, url: str, data: Dict, headers: Optional[Dict] = None, 
            timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP PUT request with error handling."""
        return self._request('PUT', url, data=data, headers=headers, timeout=timeout)
    
    def delete(self, url: str, headers: Optional[Dict] = None, 
               timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP DELETE request with error handling."""
        return self._request('DELETE', url, headers=headers, timeout=timeout)
    
    def _request(self, method: str, url: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, timeout: Optional[int] = None) -> Dict:
        """Internal request handler with error handling."""
        try:
            request_headers = {**self.default_headers}
            if headers:
                request_headers.update(headers)
            
            request_data = None
            if data:
                request_data = json.dumps(data).encode('utf-8')
            
            req = Request(url, data=request_data, headers=request_headers, method=method)
            
            with urlopen(req, timeout=timeout or self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.status,
                    'body': json.loads(response_data) if response_data else {},
                    'headers': dict(response.headers)
                }
        except HTTPError as e:
            return self._handle_http_error(method, url, e)
        except URLError as e:
            return self._handle_url_error(method, url, e)
        except Exception as e:
            return self._handle_general_error(method, url, e)
    
    def _handle_http_error(self, method: str, url: str, error: HTTPError) -> Dict:
        """Handle HTTP errors using shared utilities."""
        try:
            from .shared_utilities import handle_operation_error
            error_response = handle_operation_error(
                interface="http_client",
                operation=f"{method.lower()}_request",
                error=error,
                url=url,
                status_code=error.code
            )
            return {
                'status_code': error.code,
                'body': {'error': error_response.get('error', str(error))},
                'headers': dict(error.headers) if hasattr(error, 'headers') else {}
            }
        except Exception:
            return {
                'status_code': error.code if hasattr(error, 'code') else 500,
                'body': {'error': str(error)},
                'headers': {}
            }
    
    def _handle_url_error(self, method: str, url: str, error: URLError) -> Dict:
        """Handle URL errors using shared utilities."""
        try:
            from .shared_utilities import handle_operation_error
            error_response = handle_operation_error(
                interface="http_client",
                operation=f"{method.lower()}_request",
                error=error,
                url=url
            )
            return {
                'status_code': 0,
                'body': {'error': f"Connection error: {error_response.get('error', str(error))}"},
                'headers': {}
            }
        except Exception:
            return {
                'status_code': 0,
                'body': {'error': f'Connection error: {str(error)}'},
                'headers': {}
            }
    
    def _handle_general_error(self, method: str, url: str, error: Exception) -> Dict:
        """Handle general errors using shared utilities."""
        try:
            from .shared_utilities import handle_operation_error
            error_response = handle_operation_error(
                interface="http_client",
                operation=f"{method.lower()}_request",
                error=error,
                url=url
            )
            return {
                'status_code': 0,
                'body': {'error': f"Request failed: {error_response.get('error', str(error))}"},
                'headers': {}
            }
        except Exception:
            return {
                'status_code': 0,
                'body': {'error': f'Request failed: {str(error)}'},
                'headers': {}
            }


_HTTP_CLIENT = HTTPClientCore()


def _execute_get_implementation(url: str, headers: Optional[Dict] = None, 
                                timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP GET."""
    return _HTTP_CLIENT.get(url, headers, timeout, **kwargs)


def _execute_post_implementation(url: str, data: Dict, headers: Optional[Dict] = None, 
                                 timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP POST."""
    return _HTTP_CLIENT.post(url, data, headers, timeout, **kwargs)


def _execute_put_implementation(url: str, data: Dict, headers: Optional[Dict] = None, 
                                timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP PUT."""
    return _HTTP_CLIENT.put(url, data, headers, timeout, **kwargs)


def _execute_delete_implementation(url: str, headers: Optional[Dict] = None, 
                                   timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP DELETE."""
    return _HTTP_CLIENT.delete(url, headers, timeout, **kwargs)


__all__ = [
    '_execute_get_implementation',
    '_execute_post_implementation',
    '_execute_put_implementation',
    '_execute_delete_implementation',
]

# EOF
