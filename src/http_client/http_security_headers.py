"""
http_security_headers.py - Revolutionary Gateway Architecture Security Headers
Version: 2025.09.30.01
Daily Revision: 001

Revolutionary Gateway Optimization - Complete Migration
All imports now route through gateway.py

ARCHITECTURE: INTERNAL IMPLEMENTATION
- Uses gateway.py for all operations
- No imports from deprecated gateway files
- 100% Free Tier AWS compliant

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

import logging
from typing import Dict, Any, Optional, List, Union

from gateway import (
    cache_get, cache_set,
    log_info, log_error,
    execute_operation, GatewayInterface
)

logger = logging.getLogger(__name__)

DEFAULT_SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https: wss: ws:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "geolocation=(), microphone=(), camera=(), usb=(), "
        "bluetooth=(), midi=(), payment=(), sync-xhr=(), fullscreen=(self)"
    ),
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

HOME_ASSISTANT_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.gstatic.com https://www.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self' https: wss: ws: blob:; "
        "media-src 'self' blob:; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    "X-Frame-Options": "SAMEORIGIN"
}

PRODUCTION_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "media-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload"
}

def get_security_headers(context: str = "default", **kwargs) -> Dict[str, str]:
    try:
        cache_key = f"security_headers_{context}"
        cached_headers = cache_get(cache_key)
        
        if cached_headers:
            return cached_headers
        
        if context == "home_assistant":
            headers = {**DEFAULT_SECURITY_HEADERS, **HOME_ASSISTANT_HEADERS}
        elif context == "production":
            headers = {**DEFAULT_SECURITY_HEADERS, **PRODUCTION_HEADERS}
        else:
            headers = DEFAULT_SECURITY_HEADERS.copy()
        
        cache_set(cache_key, headers, ttl=3600)
        return headers
        
    except Exception as e:
        log_error(f"Error getting security headers: {e}")
        return DEFAULT_SECURITY_HEADERS.copy()

def apply_security_headers(response: Dict[str, Any], context: str = "default") -> Dict[str, Any]:
    try:
        if 'headers' not in response:
            response['headers'] = {}
        
        security_headers = get_security_headers(context)
        response['headers'].update(security_headers)
        
        return response
    except Exception as e:
        log_error(f"Error applying security headers: {e}")
        return response

__all__ = [
    'get_security_headers',
    'apply_security_headers',
    'DEFAULT_SECURITY_HEADERS',
    'HOME_ASSISTANT_HEADERS',
    'PRODUCTION_HEADERS'
]

# EOF
