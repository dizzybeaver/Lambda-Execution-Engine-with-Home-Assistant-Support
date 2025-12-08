"""
http_client_core.py - HTTP Client Core Implementation 
Version: 2025.10.22-1
Description: HTTP Client Core

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import time
from typing import Dict, Any, Optional
from collections import deque

# Import preloaded urllib3 classes (already initialized during Lambda INIT!)
from lambda_preload import PoolManager, Timeout

from http_client_utilities import get_standard_headers


class HTTPClientCore:
    """Core HTTP client with retry, circuit breaker, rate limiting, and SINGLETON support."""
    
    def __init__(self):
        # Read SSL verification setting from environment
        # Defaults to True (verify SSL) for security
        verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
        verify_ssl = verify_ssl_env != 'false'
        
        # Set cert_reqs based on verification setting
        cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
        
        # Use preloaded classes (NO IMPORT OVERHEAD!)
        self.http = PoolManager(
            cert_reqs=cert_reqs,
            timeout=Timeout(connect=10.0, read=30.0),
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
        
        # Rate limiting (500 ops/sec - lower than CONFIG due to HTTP overhead)
        # Uses deque for O(1) operations (LESS-21)
        self._rate_limiter = deque(maxlen=500)  # 500 requests per second
        self._rate_limit_window_ms = 1000  # 1 second window
        self._rate_limited_count = 0
        
        # Log SSL configuration (debug only)
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            from gateway import log_debug
            log_debug(f"HTTP client initialized: verify_ssl={verify_ssl}, cert_reqs={cert_reqs}")
    
    def _check_rate_limit(self) -> bool:
        """
        Check if operation is within rate limits.
        
        Returns:
            bool: True if operation allowed, False if rate limited
            
        Rate Limiting Strategy:
        - 500 operations per second (lower than CONFIG due to HTTP overhead)
        - Uses deque with maxlen for automatic eviction
        - O(1) append and popleft operations
        - Tracks violations for monitoring
        
        REF: LESS-21 (Rate limiting essential for DoS protection)
        """
        now = time.time() * 1000  # Current time in milliseconds
        
        # Remove timestamps outside the window (older than 1 second)
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if we're at the limit
        if len(self._rate_limiter) >= 500:
            self._rate_limited_count += 1
            return False
        
        # Add current timestamp
        self._rate_limiter.append(now)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics including rate limiting.
        
        Returns:
            Dict with stats: requests, successful, failed, retries, rate_limited
        """
        stats = self._stats.copy()
        stats['rate_limited'] = self._rate_limited_count
        stats['rate_limiter_size'] = len(self._rate_limiter)
        return stats
    
    def reset(self) -> bool:
        """
        Reset HTTP client state.
        
        Returns:
            bool: True if reset successful, False if rate limited
            
        Resets:
        - HTTP connection pool (closes connections)
        - Statistics counters
        - Rate limiter state
        
        REF: LESS-18 (SINGLETON pattern requires reset for lifecycle management)
        """
        if not self._check_rate_limit():
            return False
        
        try:
            # Close existing connection pool
            if hasattr(self, 'http') and self.http:
                self.http.clear()
            
            # Reset statistics
            self._stats = {
                'requests': 0,
                'successful': 0,
                'failed': 0,
                'retries': 0
            }
            
            # Reset rate limiter
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            # Recreate connection pool
            verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
            verify_ssl = verify_ssl_env != 'false'
            cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
            
            self.http = PoolManager(
                cert_reqs=cert_reqs,
                timeout=Timeout(connect=10.0, read=30.0),
                maxsize=10,
                retries=False
            )
            
            return True
            
        except Exception as e:
            from gateway import log_error
            log_error(f"HTTP client reset failed: {str(e)}", error=e)
            return False
    
    def _is_retriable_error(self, status_code: int) -> bool:
        """Check if error is retriable."""
        return status_code in self._retry_config['retriable_status_codes']
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_ms = self._retry_config['backoff_base_ms']
        multiplier = self._retry_config['backoff_multiplier']
        delay_ms = base_ms * (multiplier ** attempt)
        return delay_ms / 1000.0
    
    def _execute_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Execute single HTTP request with error handling.
        
        Rate Limiting:
        - Checks rate limit before executing request
        - Returns rate limit error if exceeded
        """
        # Check rate limit BEFORE executing request
        if not self._check_rate_limit():
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'error_type': 'RateLimitError',
                'rate_limited': True
            }
        
        try:
            self._stats['requests'] += 1
            
            # Get headers (add standard headers if not provided)
            headers = kwargs.get('headers', {})
            if not headers:
                headers = get_standard_headers()
            elif not isinstance(headers, dict):
                headers = get_standard_headers()
            
            # Handle JSON body encoding (CRITICAL FIX 2025.10.19.JSON_FIX)
            body = None
            
            if kwargs.get('json'):
                # JSON mode - encode 'json' kwarg to bytes
                json_data = kwargs.get('json')
                body = json.dumps(json_data).encode('utf-8')
                headers.setdefault('Content-Type', 'application/json')
            elif kwargs.get('body'):
                # Body mode - use 'body' kwarg directly
                body = kwargs.get('body')
                if isinstance(body, str):
                    body = body.encode('utf-8')
            
            # Execute request
            response = self.http.request(
                method,
                url,
                headers=headers,
                body=body,
                timeout=kwargs.get('timeout')
            )
            
            # Parse response
            status_code = response.status
            success = 200 <= status_code < 300
            
            # Try to decode response body
            response_data = None
            try:
                response_body = response.data.decode('utf-8')
                if response_body:
                    response_data = json.loads(response_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                response_data = response.data
            
            if success:
                self._stats['successful'] += 1
            else:
                self._stats['failed'] += 1
            
            return {
                'success': success,
                'status_code': status_code,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            from gateway import log_error
            log_error(f"HTTP request failed: {str(e)}", error=e)
            self._stats['failed'] += 1
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Execute HTTP request with retry logic."""
        max_attempts = self._retry_config['max_attempts']
        
        for attempt in range(max_attempts):
            result = self._execute_request(method, url, **kwargs)
            
            # Don't retry rate limit errors
            if result.get('rate_limited'):
                return result
            
            if result.get('success'):
                return result
            
            status_code = result.get('status_code', 0)
            if attempt < max_attempts - 1 and self._is_retriable_error(status_code):
                self._stats['retries'] += 1
                backoff = self._calculate_backoff(attempt)
                time.sleep(backoff)
                continue
            
            return result
        
        return {
            'success': False,
            'error': 'Max retry attempts exceeded',
            'attempts': max_attempts
        }


# SINGLETON Pattern Implementation (LESS-18)
_http_client_core = None


def get_http_client_manager() -> HTTPClientCore:
    """
    Get HTTP client manager SINGLETON instance.
    
    Returns:
        HTTPClientCore: The singleton HTTP client manager
        
    SINGLETON Pattern:
    - First tries gateway singleton registry (preferred)
    - Falls back to module-level singleton if gateway unavailable
    - Ensures single instance across all operations
    - Provides lifecycle management via reset()
    
    REF: LESS-18 (SINGLETON pattern essential for lifecycle management)
    REF: RULE-01 (Always use gateway for cross-interface operations)
    """
    global _http_client_core
    
    try:
        # Try to use gateway singleton registry (preferred path)
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('http_client_manager')
        if manager is None:
            # Create new instance and register it
            if _http_client_core is None:
                _http_client_core = HTTPClientCore()
            singleton_register('http_client_manager', _http_client_core)
            manager = _http_client_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback: use module-level singleton if gateway unavailable
        if _http_client_core is None:
            _http_client_core = HTTPClientCore()
        return _http_client_core


def get_http_client() -> HTTPClientCore:
    """
    Get singleton HTTP client instance (legacy compatibility).
    
    Note: Use get_http_client_manager() for new code.
    This function maintained for backward compatibility.
    """
    return get_http_client_manager()


def _make_http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Execute HTTP request via singleton."""
    client = get_http_client_manager()
    return client.make_request(method, url, **kwargs)


def http_request_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP request."""
    method = kwargs.pop('method', 'GET')
    url = kwargs.pop('url', '')
    return _make_http_request(method, url, **kwargs)


def http_get_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP GET."""
    url = kwargs.pop('url', '')
    return _make_http_request('GET', url, **kwargs)


def http_post_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP POST."""
    url = kwargs.pop('url', '')
    return _make_http_request('POST', url, **kwargs)


def http_put_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP PUT."""
    url = kwargs.pop('url', '')
    return _make_http_request('PUT', url, **kwargs)


def http_delete_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for HTTP DELETE."""
    url = kwargs.pop('url', '')
    return _make_http_request('DELETE', url, **kwargs)


def http_reset_implementation(**kwargs) -> Dict[str, Any]:
    """
    Gateway implementation for HTTP client reset.
    
    Returns:
        Dict with success status and reset result
        
    REF: LESS-18 (Reset operation essential for lifecycle management)
    """
    client = get_http_client_manager()
    success = client.reset()
    return {
        'success': success,
        'message': 'HTTP client reset successful' if success else 'HTTP client reset failed or rate limited'
    }


def get_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for get state."""
    from http_client_state import get_client_state
    return get_client_state(**kwargs)


def reset_state_implementation(**kwargs) -> Dict[str, Any]:
    """Gateway implementation for reset state."""
    from http_client_state import reset_client_state
    return reset_client_state(**kwargs)


__all__ = [
    'HTTPClientCore',
    'get_http_client_manager',
    'get_http_client',
    'http_request_implementation',
    'http_get_implementation',
    'http_post_implementation',
    'http_put_implementation',
    'http_delete_implementation',
    'http_reset_implementation',
    'get_state_implementation',
    'reset_state_implementation',
]

# EOF
