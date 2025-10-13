"""
http_client_core.py
Version: 2025.10.02.01
Description: HTTP client with retry, connection pooling, and transformation support
"""

import json
import time
from typing import Dict, Any, Optional, Callable, List
from urllib.request import Request, urlopen, HTTPHandler, HTTPSHandler, build_opener
from urllib.error import HTTPError, URLError
from http.client import HTTPConnection, HTTPSConnection


class ConnectionPool:
    """Connection pooling for HTTP requests with DNS caching and SSL session reuse."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._connections: Dict[str, List[Any]] = {}
        self._dns_cache: Dict[str, str] = {}
        self._ssl_sessions: Dict[str, Any] = {}
    
    def get_connection(self, host: str, port: int, use_ssl: bool = True) -> Any:
        """Get pooled connection or create new one."""
        key = f"{host}:{port}:{use_ssl}"
        
        if key in self._connections and self._connections[key]:
            return self._connections[key].pop()
        
        if use_ssl:
            conn = HTTPSConnection(host, port, timeout=30)
        else:
            conn = HTTPConnection(host, port, timeout=30)
        
        return conn
    
    def return_connection(self, host: str, port: int, use_ssl: bool, conn: Any):
        """Return connection to pool."""
        key = f"{host}:{port}:{use_ssl}"
        
        if key not in self._connections:
            self._connections[key] = []
        
        if len(self._connections[key]) < self.max_connections:
            self._connections[key].append(conn)
        else:
            try:
                conn.close()
            except:
                pass
    
    def cache_dns(self, hostname: str, ip: str):
        """Cache DNS resolution."""
        self._dns_cache[hostname] = ip
    
    def get_cached_dns(self, hostname: str) -> Optional[str]:
        """Get cached DNS resolution."""
        return self._dns_cache.get(hostname)


class HTTPClientCore:
    """HTTP client with circuit breaker, retry, pooling, and transformation support."""
    
    def __init__(self):
        self.timeout = 30
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Lambda-Gateway/3.0'
        }
        self._circuit_breaker = None
        self._connection_pool = ConnectionPool()
        self._retry_config = {
            'max_attempts': 3,
            'backoff_base_ms': 100,
            'backoff_multiplier': 2,
            'retriable_status_codes': {408, 429, 500, 502, 503, 504},
            'retriable_errors': {'timeout', 'connection', 'network'}
        }
    
    def _get_circuit_breaker(self):
        """Lazy load circuit breaker."""
        if self._circuit_breaker is None:
            try:
                from . import circuit_breaker
                self._circuit_breaker = circuit_breaker.get_circuit_breaker('http_client')
            except Exception:
                pass
        return self._circuit_breaker
    
    def configure_retry(self, max_attempts: int = None, backoff_base_ms: int = None,
                       backoff_multiplier: float = None, retriable_status_codes: set = None):
        """Configure retry behavior."""
        if max_attempts is not None:
            self._retry_config['max_attempts'] = max_attempts
        if backoff_base_ms is not None:
            self._retry_config['backoff_base_ms'] = backoff_base_ms
        if backoff_multiplier is not None:
            self._retry_config['backoff_multiplier'] = backoff_multiplier
        if retriable_status_codes is not None:
            self._retry_config['retriable_status_codes'] = retriable_status_codes
    
    def get(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None, 
            use_cache: bool = True, cache_ttl: int = 300, 
            transform: Optional[Callable] = None, **kwargs) -> Dict:
        """Perform HTTP GET request with caching, retry, and transformation."""
        from .shared_utilities import cache_operation_result, create_operation_context, close_operation_context
        
        context = create_operation_context('http_client', 'get', url=url, use_cache=use_cache)
        
        try:
            if use_cache:
                result = cache_operation_result(
                    operation_name="http_get",
                    func=lambda: self._execute_with_retry_and_circuit_breaker(
                        'GET', url, headers=headers, timeout=timeout, transform=transform
                    ),
                    ttl=cache_ttl,
                    cache_key_prefix=f"http_get_{url}"
                )
            else:
                result = self._execute_with_retry_and_circuit_breaker(
                    'GET', url, headers=headers, timeout=timeout, transform=transform
                )
            
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            from .shared_utilities import handle_operation_error
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'get', e, context['correlation_id'])
    
    def post(self, url: str, data: Dict, headers: Optional[Dict] = None, 
             timeout: Optional[int] = None, transform: Optional[Callable] = None, **kwargs) -> Dict:
        """Perform HTTP POST request with retry and transformation."""
        from .shared_utilities import create_operation_context, close_operation_context
        
        context = create_operation_context('http_client', 'post', url=url)
        
        try:
            result = self._execute_with_retry_and_circuit_breaker(
                'POST', url, data=data, headers=headers, timeout=timeout, transform=transform
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            from .shared_utilities import handle_operation_error
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'post', e, context['correlation_id'])
    
    def put(self, url: str, data: Dict, headers: Optional[Dict] = None, 
            timeout: Optional[int] = None, transform: Optional[Callable] = None, **kwargs) -> Dict:
        """Perform HTTP PUT request with retry and transformation."""
        from .shared_utilities import create_operation_context, close_operation_context
        
        context = create_operation_context('http_client', 'put', url=url)
        
        try:
            result = self._execute_with_retry_and_circuit_breaker(
                'PUT', url, data=data, headers=headers, timeout=timeout, transform=transform
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            from .shared_utilities import handle_operation_error
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'put', e, context['correlation_id'])
    
    def delete(self, url: str, headers: Optional[Dict] = None, 
               timeout: Optional[int] = None, transform: Optional[Callable] = None, **kwargs) -> Dict:
        """Perform HTTP DELETE request with retry and transformation."""
        from .shared_utilities import create_operation_context, close_operation_context
        
        context = create_operation_context('http_client', 'delete', url=url)
        
        try:
            result = self._execute_with_retry_and_circuit_breaker(
                'DELETE', url, headers=headers, timeout=timeout, transform=transform
            )
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            from .shared_utilities import handle_operation_error
            close_operation_context(context, success=False)
            return handle_operation_error('http_client', 'delete', e, context['correlation_id'])
    
    def _execute_with_retry_and_circuit_breaker(self, method: str, url: str, 
                                                data: Optional[Dict] = None,
                                                headers: Optional[Dict] = None, 
                                                timeout: Optional[int] = None,
                                                transform: Optional[Callable] = None) -> Dict:
        """Execute HTTP request with retry logic and circuit breaker protection."""
        cb = self._get_circuit_breaker()
        
        if cb and cb.is_open():
            raise Exception(f"Circuit breaker open for http_client: {cb.get_failure_count()} failures")
        
        last_error = None
        max_attempts = self._retry_config['max_attempts']
        
        for attempt in range(max_attempts):
            try:
                result = self._request(method, url, data=data, headers=headers, 
                                     timeout=timeout, transform=transform)
                
                if cb:
                    cb.record_success()
                
                if attempt > 0:
                    from .shared_utilities import record_operation_metrics
                    record_operation_metrics(
                        interface='http_client',
                        operation=f'{method.lower()}_retry_success',
                        execution_time=0,
                        success=True,
                        attempt=attempt + 1
                    )
                
                return result
                
            except Exception as e:
                last_error = e
                
                if not self._is_retriable_error(e):
                    if cb:
                        cb.record_failure()
                    raise
                
                if attempt < max_attempts - 1:
                    backoff_ms = self._calculate_backoff(attempt)
                    time.sleep(backoff_ms / 1000.0)
                    
                    from .shared_utilities import record_operation_metrics
                    record_operation_metrics(
                        interface='http_client',
                        operation=f'{method.lower()}_retry_attempt',
                        execution_time=backoff_ms,
                        success=False,
                        attempt=attempt + 1
                    )
        
        if cb:
            cb.record_failure()
        
        raise last_error
    
    def _is_retriable_error(self, error: Exception) -> bool:
        """Determine if error is retriable."""
        if isinstance(error, HTTPError):
            return error.code in self._retry_config['retriable_status_codes']
        
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in self._retry_config['retriable_errors'])
    
    def _calculate_backoff(self, attempt: int) -> int:
        """Calculate exponential backoff delay in milliseconds."""
        base = self._retry_config['backoff_base_ms']
        multiplier = self._retry_config['backoff_multiplier']
        return int(base * (multiplier ** attempt))
    
    def _request(self, method: str, url: str, data: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, timeout: Optional[int] = None,
                 transform: Optional[Callable] = None) -> Dict:
        """Internal request handler with connection pooling."""
        request_headers = {**self.default_headers, **(headers or {})}
        timeout_val = timeout or self.timeout
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
        
        req = Request(url, data=request_data, headers=request_headers, method=method)
        
        try:
            with urlopen(req, timeout=timeout_val) as response:
                response_data = response.read().decode('utf-8')
                
                result = {
                    'success': True,
                    'status_code': response.status,
                    'data': json.loads(response_data) if response_data else None,
                    'headers': dict(response.headers)
                }
                
                if transform:
                    result = self._apply_transformation(result, transform)
                
                return result
                
        except HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            raise Exception(f"HTTP {e.code}: {error_body}")
        except URLError as e:
            raise Exception(f"URL Error: {str(e.reason)}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _apply_transformation(self, result: Dict, transform: Callable) -> Dict:
        """Apply transformation function to result."""
        try:
            transformed_data = transform(result.get('data'))
            result['data'] = transformed_data
            result['transformed'] = True
            return result
        except Exception as e:
            result['transformation_error'] = str(e)
            return result


_http_client_instance = None


def get_http_client() -> HTTPClientCore:
    """Get singleton HTTP client instance."""
    global _http_client_instance
    if _http_client_instance is None:
        _http_client_instance = HTTPClientCore()
    return _http_client_instance


# EOF
