"""
HTTP Client Core - Template Optimized with Generic HTTP Methods
Version: 2025.10.03.01
Description: HTTP client with template-based headers and generic method dispatch

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

import urllib3
import json
import time
import os
from typing import Dict, Any, Optional
from enum import Enum
from urllib.parse import urlencode

# HTTP header templates for ultra-fast generation
_JSON_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'AWS-Lambda-Python/3.12'
}

_XML_HEADERS = {
    'Content-Type': 'application/xml',
    'Accept': 'application/xml',
    'User-Agent': 'AWS-Lambda-Python/3.12'
}

_FORM_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'User-Agent': 'AWS-Lambda-Python/3.12'
}

_TEXT_HEADERS = {
    'Content-Type': 'text/plain',
    'Accept': 'text/plain',
    'User-Agent': 'AWS-Lambda-Python/3.12'
}

_HA_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'AWS-Lambda-HA-Client/1.0'
}

_USE_HTTP_TEMPLATES = os.environ.get('USE_HTTP_TEMPLATES', 'true').lower() == 'true'


class HTTPMethod(Enum):
    """HTTP method types."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HeaderType(Enum):
    """HTTP header template types."""
    JSON = "json"
    XML = "xml"
    FORM = "form"
    TEXT = "text"
    HA = "ha"
    CUSTOM = "custom"


class HTTPClientCore:
    """Core HTTP client with template optimization and generic methods."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            maxsize=10,
            timeout=urllib3.Timeout(connect=10.0, read=30.0),
            retries=urllib3.Retry(total=3, backoff_factor=0.3)
        )
        self._stats = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'template_headers_used': 0
        }
    
    def get_standard_headers(self, header_type: HeaderType = HeaderType.JSON) -> Dict[str, str]:
        """Get standard headers using templates for ultra-fast performance."""
        if not _USE_HTTP_TEMPLATES:
            return self._get_headers_legacy(header_type)
        
        self._stats['template_headers_used'] += 1
        
        if header_type == HeaderType.JSON:
            return _JSON_HEADERS.copy()
        elif header_type == HeaderType.XML:
            return _XML_HEADERS.copy()
        elif header_type == HeaderType.FORM:
            return _FORM_HEADERS.copy()
        elif header_type == HeaderType.TEXT:
            return _TEXT_HEADERS.copy()
        elif header_type == HeaderType.HA:
            return _HA_HEADERS.copy()
        else:
            return _JSON_HEADERS.copy()
    
    def _get_headers_legacy(self, header_type: HeaderType) -> Dict[str, str]:
        """Legacy header generation."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AWS-Lambda-Python/3.12'
        }
    
    def parse_headers_fast(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Fast header parsing with template awareness."""
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
    
    def execute_http_method(self, method: HTTPMethod, url: str, **kwargs) -> urllib3.HTTPResponse:
        """Generic HTTP method executor."""
        self._stats['requests'] += 1
        
        try:
            headers = kwargs.get('headers', self.get_standard_headers())
            body = kwargs.get('body')
            fields = kwargs.get('fields')
            timeout = kwargs.get('timeout')
            
            if method == HTTPMethod.GET:
                response = self.http.request('GET', url, headers=headers, timeout=timeout)
            elif method == HTTPMethod.POST:
                if body:
                    body_data = json.dumps(body) if isinstance(body, dict) else body
                    response = self.http.request('POST', url, body=body_data, headers=headers, timeout=timeout)
                else:
                    response = self.http.request('POST', url, fields=fields, headers=headers, timeout=timeout)
            elif method == HTTPMethod.PUT:
                body_data = json.dumps(body) if isinstance(body, dict) else body
                response = self.http.request('PUT', url, body=body_data, headers=headers, timeout=timeout)
            elif method == HTTPMethod.DELETE:
                response = self.http.request('DELETE', url, headers=headers, timeout=timeout)
            elif method == HTTPMethod.PATCH:
                body_data = json.dumps(body) if isinstance(body, dict) else body
                response = self.http.request('PATCH', url, body=body_data, headers=headers, timeout=timeout)
            elif method == HTTPMethod.HEAD:
                response = self.http.request('HEAD', url, headers=headers, timeout=timeout)
            elif method == HTTPMethod.OPTIONS:
                response = self.http.request('OPTIONS', url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self._stats['successful'] += 1
            return response
            
        except Exception as e:
            self._stats['failed'] += 1
            raise e
    
    def make_request(self, method: str, url: str, **kwargs) -> urllib3.HTTPResponse:
        """Make HTTP request with generic method dispatch."""
        try:
            http_method = HTTPMethod[method.upper()]
            return self.execute_http_method(http_method, url, **kwargs)
        except KeyError:
            raise ValueError(f"Invalid HTTP method: {method}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        return {
            'total_requests': self._stats['requests'],
            'successful_requests': self._stats['successful'],
            'failed_requests': self._stats['failed'],
            'success_rate': (self._stats['successful'] / self._stats['requests'] * 100) if self._stats['requests'] > 0 else 0,
            'template_headers_used': self._stats['template_headers_used']
        }


_MANAGER = HTTPClientCore()


def _execute_make_request_implementation(method: str, url: str, **kwargs) -> urllib3.HTTPResponse:
    """Execute make request operation."""
    return _MANAGER.make_request(method, url, **kwargs)


def get_standard_headers(header_type: str = 'json') -> Dict[str, str]:
    """Public interface for getting standard headers."""
    try:
        header_enum = HeaderType[header_type.upper()]
        return _MANAGER.get_standard_headers(header_enum)
    except KeyError:
        return _MANAGER.get_standard_headers(HeaderType.JSON)


def parse_headers_fast(headers: Dict[str, str]) -> Dict[str, str]:
    """Public interface for fast header parsing."""
    return _MANAGER.parse_headers_fast(headers)


def build_query_fast(params: Dict[str, Any]) -> str:
    """Public interface for fast query building."""
    return _MANAGER.build_query_fast(params)


def get_http_stats() -> Dict[str, Any]:
    """Public interface for HTTP statistics."""
    return _MANAGER.get_stats()


__all__ = [
    'HTTPMethod',
    'HeaderType',
    'get_standard_headers',
    'parse_headers_fast',
    'build_query_fast',
    'get_http_stats',
    '_execute_make_request_implementation',
]
