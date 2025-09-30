"""
HTTP Client Core - HTTP Request Handling
Version: 2025.09.29.01
Daily Revision: 001
"""

import json
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class HTTPClientCore:
    """HTTP client for making requests."""
    
    def __init__(self):
        self.timeout = 30
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Lambda-Gateway/1.0'
        }
    
    def get(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP GET request."""
        return self._request('GET', url, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Dict, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP POST request."""
        return self._request('POST', url, data=data, headers=headers, timeout=timeout)
    
    def put(self, url: str, data: Dict, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP PUT request."""
        return self._request('PUT', url, data=data, headers=headers, timeout=timeout)
    
    def delete(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
        """Perform HTTP DELETE request."""
        return self._request('DELETE', url, headers=headers, timeout=timeout)
    
    def _request(self, method: str, url: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, timeout: Optional[int] = None) -> Dict:
        """Internal request handler."""
        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
        
        req = Request(url, data=request_data, headers=request_headers, method=method)
        
        try:
            with urlopen(req, timeout=timeout or self.timeout) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.status,
                    'body': json.loads(response_data) if response_data else {},
                    'headers': dict(response.headers)
                }
        except HTTPError as e:
            return {
                'status_code': e.code,
                'body': {'error': str(e)},
                'headers': dict(e.headers) if hasattr(e, 'headers') else {}
            }
        except URLError as e:
            return {
                'status_code': 0,
                'body': {'error': f'Connection error: {str(e)}'},
                'headers': {}
            }
        except Exception as e:
            return {
                'status_code': 0,
                'body': {'error': f'Request failed: {str(e)}'},
                'headers': {}
            }

_HTTP_CLIENT = HTTPClientCore()

def _execute_get_implementation(url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP GET."""
    return _HTTP_CLIENT.get(url, headers, timeout, **kwargs)

def _execute_post_implementation(url: str, data: Dict, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP POST."""
    return _HTTP_CLIENT.post(url, data, headers, timeout, **kwargs)

def _execute_put_implementation(url: str, data: Dict, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP PUT."""
    return _HTTP_CLIENT.put(url, data, headers, timeout, **kwargs)

def _execute_delete_implementation(url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, **kwargs) -> Dict:
    """Execute HTTP DELETE."""
    return _HTTP_CLIENT.delete(url, headers, timeout, **kwargs)

#EOF
