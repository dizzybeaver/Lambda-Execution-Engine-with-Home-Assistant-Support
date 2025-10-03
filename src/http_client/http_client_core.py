"""
HTTP Client Core - HTTP Request Handling with Template Optimization
Version: 2025.10.03.01
Description: HTTP client with retry, connection pooling, and template-optimized headers

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
from typing import Dict, Any, Optional, Callable
from urllib.parse import urlencode, quote
import threading

# ===== HTTP HEADER TEMPLATES (Template Optimization) =====

_JSON_HEADERS = '{"Content-Type":"application/json","Accept":"application/json"}'
_XML_HEADERS = '{"Content-Type":"application/xml","Accept":"application/xml"}'
_FORM_HEADERS = '{"Content-Type":"application/x-www-form-urlencoded","Accept":"application/json"}'
_TEXT_HEADERS = '{"Content-Type":"text/plain","Accept":"text/plain"}'
_HA_HEADERS = '{"Content-Type":"application/json","Accept":"application/json"}'

_PARSED_HEADERS_TEMPLATE = '{"content_type":"%s","content_length":%d,"server":"%s"}'

_QUERY_BUFFER = []

_USE_HTTP_TEMPLATES = os.environ.get('USE_HTTP_TEMPLATES', 'true').lower() == 'true'

def get_standard_headers(content_type: str = 'json') -> Dict[str, str]:
    """Get standard HTTP headers using template optimization."""
    try:
        if _USE_HTTP_TEMPLATES:
            if content_type == 'json':
                return json.loads(_JSON_HEADERS)
            elif content_type == 'xml':
                return json.loads(_XML_HEADERS)
            elif content_type == 'form':
                return json.loads(_FORM_HEADERS)
            elif content_type == 'text':
                return json.loads(_TEXT_HEADERS)
            elif content_type == 'ha':
                return json.loads(_HA_HEADERS)
            else:
                return json.loads(_JSON_HEADERS)
        else:
            return {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
    except Exception:
        return {"Content-Type": "application/json"}

def parse_headers_fast(headers_dict: Dict[str, str]) -> Dict[str, Any]:
    """Parse HTTP headers using template optimization."""
    try:
        if _USE_HTTP_TEMPLATES and headers_dict:
            content_type = headers_dict.get('content-type', headers_dict.get('Content-Type', 'unknown'))
            content_length = int(headers_dict.get('content-length', headers_dict.get('Content-Length', 0)))
            server = headers_dict.get('server', headers_dict.get('Server', 'unknown'))
            
            json_str = _PARSED_HEADERS_TEMPLATE % (content_type, content_length, server)
            parsed = json.loads(json_str)
            
            for key, value in headers_dict.items():
                if key.lower() not in ['content-type', 'content-length', 'server']:
                    parsed[key.lower()] = value
            
            return parsed
        else:
            return {key.lower(): value for key, value in (headers_dict or {}).items()}
    except Exception:
        return {key.lower(): value for key, value in (headers_dict or {}).items()}

def build_query_fast(params: Dict[str, Any]) -> str:
    """Build query string using template optimization."""
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
                
                with self._lock:
                    if _USE_HTTP_TEMPLATES:
                        self._stats['template_query_usage'] += 1
                    else:
                        self._stats['legacy_query_usage'] += 1
            
            body = None
            if kwargs.get('data'):
                if isinstance(kwargs['data'], dict):
                    body = json.dumps(kwargs['data']).encode('utf-8')
                else:
                    body = kwargs['data']
            
            timeout_val = kwargs.get('timeout', 30)
            
            response = self.http_pool.request(
                method,
                url,
                body=body,
                headers=headers,
                timeout=timeout_val
            )
            
            response_data = response.data.decode('utf-8') if response.data else None
            
            result = {
                'success': True,
                'status_code': response.status,
                'data': json.loads(response_data) if response_data else None,
                'headers': dict(response.headers),
                'response_time_ms': int((time.time() - start_time) * 1000)
            }
            
            with self._lock:
                self._stats['successful_requests'] += 1
            
            return result
            
        except Exception as e:
            with self._lock:
                self._stats['failed_requests'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def _prepare_headers(self, custom_headers: Optional[Dict], content_type: str) -> Dict[str, str]:
        """Prepare headers using template optimization."""
        try:
            base_headers = get_standard_headers(content_type)
            
            with self._lock:
                if _USE_HTTP_TEMPLATES:
                    self._stats['template_header_usage'] += 1
                else:
                    self._stats['legacy_header_usage'] += 1
            
            if custom_headers:
                return merge_headers_fast(base_headers, custom_headers)
            
            return base_headers
            
        except Exception:
            return {"Content-Type": "application/json"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HTTP client statistics."""
        with self._lock:
            total_header_ops = self._stats['template_header_usage'] + self._stats['legacy_header_usage']
            total_query_ops = self._stats['template_query_usage'] + self._stats['legacy_query_usage']
            
            header_template_rate = self._stats['template_header_usage'] / max(total_header_ops, 1)
            query_template_rate = self._stats['template_query_usage'] / max(total_query_ops, 1)
            
            success_rate = self._stats['successful_requests'] / max(self._stats['requests_made'], 1)
            
            return {
                'requests_made': self._stats['requests_made'],
                'successful_requests': self._stats['successful_requests'],
                'failed_requests': self._stats['failed_requests'],
                'success_rate': success_rate,
                'header_template_usage_rate': header_template_rate,
                'query_template_usage_rate': query_template_rate,
                'template_optimization_enabled': _USE_HTTP_TEMPLATES,
                'stats': self._stats.copy()
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

# EOF
