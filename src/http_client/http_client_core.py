"""
HTTP Client Core - HTTP Operations with Header and Query String Template Optimization
Version: 2025.10.02.01
Description: HTTP client with pre-compiled header templates and optimized query building

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
import os
import urllib3
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlencode, quote
import threading

# ===== HTTP HEADER TEMPLATES (Phase 2 Optimization) =====

_JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Lambda-Execution-Engine/1.0"
}

_XML_HEADERS = {
    "Content-Type": "application/xml",
    "Accept": "application/xml",
    "User-Agent": "Lambda-Execution-Engine/1.0"
}

_FORM_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "User-Agent": "Lambda-Execution-Engine/1.0"
}

_TEXT_HEADERS = {
    "Content-Type": "text/plain",
    "Accept": "text/plain",
    "User-Agent": "Lambda-Execution-Engine/1.0"
}

_HA_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Lambda-Execution-Engine-HA/1.0"
}

_PARSED_HEADERS_TEMPLATE = {
    'content_type': None,
    'content_length': 0,
    'cache_control': '',
    'server': '',
    'connection': '',
    'date': ''
}

# ===== QUERY STRING TEMPLATES (Phase 2 Optimization) =====

_QUERY_BUFFER = []
_QUERY_CACHE = {}

_USE_HTTP_TEMPLATES = os.environ.get('USE_HTTP_TEMPLATES', 'true').lower() == 'true'

def get_standard_headers(header_type: str = "json") -> Dict[str, str]:
    """Get pre-built headers based on type."""
    try:
        if _USE_HTTP_TEMPLATES:
            if header_type == "json":
                return _JSON_HEADERS.copy()
            elif header_type == "xml":
                return _XML_HEADERS.copy()
            elif header_type == "form":
                return _FORM_HEADERS.copy()
            elif header_type == "text":
                return _TEXT_HEADERS.copy()
            elif header_type == "ha":
                return _HA_HEADERS.copy()
            else:
                return _JSON_HEADERS.copy()
        else:
            return {
                "Content-Type": f"application/{header_type}",
                "Accept": f"application/{header_type}",
                "User-Agent": "Lambda-Execution-Engine/1.0"
            }
    except Exception:
        return {"Content-Type": "application/json", "User-Agent": "Lambda-Execution-Engine/1.0"}

def parse_headers_fast(headers: Dict[str, str]) -> Dict[str, Any]:
    """Fast header parsing using template."""
    try:
        if _USE_HTTP_TEMPLATES:
            result = _PARSED_HEADERS_TEMPLATE.copy()
            
            result['content_type'] = headers.get('content-type', '').split(';')[0].strip()
            result['content_length'] = int(headers.get('content-length', 0) or 0)
            result['cache_control'] = headers.get('cache-control', '')
            result['server'] = headers.get('server', '')
            result['connection'] = headers.get('connection', '')
            result['date'] = headers.get('date', '')
            
            return result
        else:
            return {
                'content_type': headers.get('content-type', '').split(';')[0].strip(),
                'content_length': int(headers.get('content-length', 0) or 0),
                'cache_control': headers.get('cache-control', ''),
                'server': headers.get('server', ''),
                'connection': headers.get('connection', ''),
                'date': headers.get('date', '')
            }
    except Exception:
        return _PARSED_HEADERS_TEMPLATE.copy()

def build_query_fast(params: Dict[str, Any]) -> str:
    """Fast query string building using template optimization."""
    try:
        if not params:
            return ""
        
        if _USE_HTTP_TEMPLATES:
            _QUERY_BUFFER.clear()
            
            for key, value in params.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        _QUERY_BUFFER.extend(f"{key}={quote(str(v))}" for v in value)
                    else:
                        _QUERY_BUFFER.append(f"{key}={quote(str(value))}")
            
            return '&'.join(_QUERY_BUFFER)
        else:
            return urlencode(params, doseq=True)
            
    except Exception:
        try:
            return urlencode(params, doseq=True)
        except:
            return ""

def merge_headers_fast(base_headers: Dict[str, str], additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Fast header merging using template base."""
    try:
        if not additional_headers:
            return base_headers.copy()
        
        if _USE_HTTP_TEMPLATES:
            result = base_headers.copy()
            result.update(additional_headers)
            return result
        else:
            result = {}
            result.update(base_headers)
            if additional_headers:
                result.update(additional_headers)
            return result
            
    except Exception:
        return base_headers.copy() if base_headers else {}

class HTTPClientCore:
    """Core HTTP client implementation with template optimization."""
    
    def __init__(self):
        self.http_pool = urllib3.PoolManager(
            num_pools=10,
            maxsize=20,
            timeout=urllib3.Timeout(connect=10, read=30),
            retries=urllib3.Retry(total=3, backoff_factor=0.3)
        )
        self._stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'template_header_usage': 0,
            'legacy_header_usage': 0,
            'template_query_usage': 0,
            'legacy_query_usage': 0
        }
        self._lock = threading.RLock()
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with template optimization."""
        start_time = time.time()
        
        with self._lock:
            self._stats['requests_made'] += 1
        
        try:
            headers = self._prepare_headers(kwargs.get('headers'), kwargs.get('content_type', 'json'))
            query_params = kwargs.get('params')
            
            if query_params:
                query_string = build_query_fast(query_params)
                if query_string:
                    separator = '&' if '?' in url else '?'
                    url = f"{url}{separator}{query_string}"
                
                if _USE_HTTP_TEMPLATES:
                    self._stats['template_query_usage'] += 1
                else:
                    self._stats['legacy_query_usage'] += 1
            
            body = kwargs.get('json')
            if body and method.upper() in ['POST', 'PUT', 'PATCH']:
                body = json.dumps(body) if not isinstance(body, str) else body
            
            response = self.http_pool.request(
                method,
                url,
                body=body,
                headers=headers,
                timeout=kwargs.get('timeout', 30)
            )
            
            response_time = (time.time() - start_time) * 1000
            parsed_response = self._parse_response(response, response_time)
            
            with self._lock:
                if parsed_response.get('success', False):
                    self._stats['successful_requests'] += 1
                else:
                    self._stats['failed_requests'] += 1
            
            return parsed_response
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            with self._lock:
                self._stats['failed_requests'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': response_time,
                'status_code': 0
            }
    
    def _prepare_headers(self, custom_headers: Optional[Dict[str, str]], content_type: str) -> Dict[str, str]:
        """Prepare headers using template optimization."""
        try:
            base_headers = get_standard_headers(content_type)
            
            if _USE_HTTP_TEMPLATES:
                self._stats['template_header_usage'] += 1
                return merge_headers_fast(base_headers, custom_headers)
            else:
                self._stats['legacy_header_usage'] += 1
                result = {
                    "Content-Type": f"application/{content_type}",
                    "User-Agent": "Lambda-Execution-Engine/1.0"
                }
                if custom_headers:
                    result.update(custom_headers)
                return result
                
        except Exception:
            return {"Content-Type": "application/json", "User-Agent": "Lambda-Execution-Engine/1.0"}
    
    def _parse_response(self, response: urllib3.HTTPResponse, response_time: float) -> Dict[str, Any]:
        """Parse HTTP response."""
        try:
            response_headers = dict(response.headers)
            parsed_headers = parse_headers_fast(response_headers)
            
            response_data = {
                'success': 200 <= response.status < 300,
                'status_code': response.status,
                'headers': response_headers,
                'parsed_headers': parsed_headers,
                'response_time_ms': response_time
            }
            
            try:
                raw_data = response.data.decode('utf-8')
                
                if parsed_headers['content_type'].startswith('application/json'):
                    response_data['json'] = json.loads(raw_data)
                    response_data['data'] = response_data['json']
                else:
                    response_data['data'] = raw_data
                    
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data['data'] = response.data
            
            return response_data
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Response parsing failed: {str(e)}',
                'status_code': getattr(response, 'status', 0),
                'response_time_ms': response_time
            }
    
    def make_ha_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make Home Assistant specific request with optimized headers."""
        ha_headers = get_standard_headers("ha")
        
        if 'headers' in kwargs:
            ha_headers = merge_headers_fast(ha_headers, kwargs['headers'])
        
        kwargs['headers'] = ha_headers
        kwargs['content_type'] = 'json'
        
        return self.make_request(method, url, **kwargs)
    
    def make_json_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make JSON request with optimized headers."""
        json_headers = get_standard_headers("json")
        
        if 'headers' in kwargs:
            json_headers = merge_headers_fast(json_headers, kwargs['headers'])
        
        kwargs['headers'] = json_headers
        kwargs['json'] = data
        kwargs['content_type'] = 'json'
        
        return self.make_request(method, url, **kwargs)
    
    def make_form_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make form request with optimized headers."""
        form_headers = get_standard_headers("form")
        
        if 'headers' in kwargs:
            form_headers = merge_headers_fast(form_headers, kwargs['headers'])
        
        kwargs['headers'] = form_headers
        
        if data:
            kwargs['body'] = urlencode(data)
        
        return self.make_request(method, url, **kwargs)
    
    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        try:
            return {
                'num_pools': len(self.http_pool.pools),
                'total_connections': sum(len(pool.pool) for pool in self.http_pool.pools.values())
            }
        except Exception:
            return {'error': 'Failed to get pool stats'}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        with self._lock:
            total_requests = self._stats['requests_made']
            success_rate = self._stats['successful_requests'] / max(total_requests, 1)
            
            template_operations = self._stats['template_header_usage'] + self._stats['template_query_usage']
            legacy_operations = self._stats['legacy_header_usage'] + self._stats['legacy_query_usage']
            total_operations = template_operations + legacy_operations
            
            template_usage_rate = template_operations / max(total_operations, 1)
            
            return {
                'requests_made': total_requests,
                'success_rate': success_rate,
                'template_usage_rate': template_usage_rate,
                'template_optimization_enabled': _USE_HTTP_TEMPLATES,
                'stats': self._stats.copy(),
                'pool_stats': self.get_connection_pool_stats()
            }
    
    def reset_stats(self):
        """Reset HTTP client statistics."""
        with self._lock:
            self._stats = {
                'requests_made': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'template_header_usage': 0,
                'legacy_header_usage': 0,
                'template_query_usage': 0,
                'legacy_query_usage': 0
            }
