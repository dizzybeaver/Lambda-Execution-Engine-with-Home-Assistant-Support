"""
http_client_core.py - Core HTTP Client Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Lightweight HTTP operations
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, Optional

_DEFAULT_TIMEOUT = 30
_DEFAULT_HEADERS = {
    "User-Agent": "Lambda-Gateway/1.0",
    "Content-Type": "application/json"
}

def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs
) -> Dict[str, Any]:
    """Execute HTTP GET request."""
    request_headers = _DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    try:
        req = urllib.request.Request(url, headers=request_headers, method='GET')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            response_headers = dict(response.headers)
            
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = body
            
            return {
                "status_code": status_code,
                "body": body_json,
                "headers": response_headers,
                "success": 200 <= status_code < 300
            }
    
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "body": e.read().decode('utf-8') if e.fp else None,
            "headers": dict(e.headers) if e.headers else {},
            "success": False,
            "error": str(e)
        }
    
    except urllib.error.URLError as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e.reason)
        }
    
    except Exception as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e)
        }

def http_post(
    url: str,
    data: Any = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs
) -> Dict[str, Any]:
    """Execute HTTP POST request."""
    request_headers = _DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    if data is not None:
        if isinstance(data, (dict, list)):
            post_data = json.dumps(data).encode('utf-8')
            request_headers['Content-Type'] = 'application/json'
        elif isinstance(data, str):
            post_data = data.encode('utf-8')
        else:
            post_data = str(data).encode('utf-8')
    else:
        post_data = None
    
    try:
        req = urllib.request.Request(
            url,
            data=post_data,
            headers=request_headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            response_headers = dict(response.headers)
            
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = body
            
            return {
                "status_code": status_code,
                "body": body_json,
                "headers": response_headers,
                "success": 200 <= status_code < 300
            }
    
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "body": e.read().decode('utf-8') if e.fp else None,
            "headers": dict(e.headers) if e.headers else {},
            "success": False,
            "error": str(e)
        }
    
    except urllib.error.URLError as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e.reason)
        }
    
    except Exception as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e)
        }

def http_put(
    url: str,
    data: Any = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs
) -> Dict[str, Any]:
    """Execute HTTP PUT request."""
    request_headers = _DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    if data is not None:
        if isinstance(data, (dict, list)):
            post_data = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            post_data = data.encode('utf-8')
        else:
            post_data = str(data).encode('utf-8')
    else:
        post_data = None
    
    try:
        req = urllib.request.Request(
            url,
            data=post_data,
            headers=request_headers,
            method='PUT'
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            response_headers = dict(response.headers)
            
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = body
            
            return {
                "status_code": status_code,
                "body": body_json,
                "headers": response_headers,
                "success": 200 <= status_code < 300
            }
    
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "body": e.read().decode('utf-8') if e.fp else None,
            "headers": dict(e.headers) if e.headers else {},
            "success": False,
            "error": str(e)
        }
    
    except Exception as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e)
        }

def http_delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = _DEFAULT_TIMEOUT,
    **kwargs
) -> Dict[str, Any]:
    """Execute HTTP DELETE request."""
    request_headers = _DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    try:
        req = urllib.request.Request(url, headers=request_headers, method='DELETE')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            response_headers = dict(response.headers)
            
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = body
            
            return {
                "status_code": status_code,
                "body": body_json,
                "headers": response_headers,
                "success": 200 <= status_code < 300
            }
    
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "body": e.read().decode('utf-8') if e.fp else None,
            "headers": dict(e.headers) if e.headers else {},
            "success": False,
            "error": str(e)
        }
    
    except Exception as e:
        return {
            "status_code": 0,
            "body": None,
            "headers": {},
            "success": False,
            "error": str(e)
        }
