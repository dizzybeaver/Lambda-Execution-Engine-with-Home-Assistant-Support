"""
http_client_generic.py - Generic HTTP Patterns
Version: 2025.09.30.02
Daily Revision: 002 - Gateway Architecture Compliance

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Uses gateway.py for all operations
- Generic HTTP patterns for reuse
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

import json
import time
from typing import Dict, Any, Optional, List, Callable
import logging

from gateway import (
    validate_request,
    create_success_response, create_error_response,
    sanitize_response_data,
    log_info, log_error,
    cache_get, cache_set, cache_clear,
    record_metric,
    get_parameter,
    execute_operation, GatewayInterface
)

logger = logging.getLogger(__name__)

def create_generic_client(client_type: str, configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Create generic HTTP client for unsupported client types."""
    try:
        default_config = {
            'timeout': get_parameter('http_timeout', 30),
            'retries': get_parameter('http_retries', 3),
            'headers': get_parameter('http_default_headers', {})
        }
        
        client_config = {**default_config, **(configuration or {})}
        
        import urllib3
        return urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10, read=client_config.get('timeout', 30)),
            retries=urllib3.Retry(total=client_config.get('retries', 3))
        )
    except Exception as e:
        log_error(f"Failed to create generic client: {e}")
        raise

def execute_with_retry(operation: Callable, max_retries: int = 3, 
                      backoff_factor: float = 0.5,
                      retry_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generic retry pattern for HTTP operations."""
    retry_conditions = retry_conditions or ['timeout', 'connection_error', '5xx']
    
    for attempt in range(max_retries):
        try:
            result = operation()
            
            if result.get('success', True):
                record_metric('http_operation.success', 1.0, {'attempt': attempt + 1})
                return result
            
            if not _should_retry(result, retry_conditions):
                return result
            
            if attempt < max_retries - 1:
                delay = backoff_factor * (2 ** attempt)
                time.sleep(delay)
                log_info(f"Retrying operation, attempt {attempt + 2}/{max_retries}")
        
        except Exception as e:
            if attempt == max_retries - 1:
                log_error(f"Operation failed after {max_retries} attempts: {e}")
                return create_error_response(f"Operation failed: {str(e)}")
            
            delay = backoff_factor * (2 ** attempt)
            time.sleep(delay)
    
    return create_error_response("Operation failed after all retries")

def execute_with_caching(operation: Callable, cache_key: str, ttl: int = 300,
                        cache_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generic caching pattern for HTTP operations."""
    try:
        cached_result = cache_get(cache_key)
        
        if cached_result:
            record_metric('http_operation.cache_hit', 1.0)
            return cached_result
        
        record_metric('http_operation.cache_miss', 1.0)
        result = operation()
        
        should_cache = True
        if cache_conditions:
            should_cache = _evaluate_cache_conditions(result, cache_conditions)
        
        if should_cache and result.get('success', True):
            cache_set(cache_key, result, ttl)
        
        return result
    
    except Exception as e:
        log_error(f"Cached operation failed: {e}")
        return create_error_response(f"Operation failed: {str(e)}")

def execute_with_timeout(operation: Callable, timeout_seconds: float) -> Dict[str, Any]:
    """Generic timeout pattern for HTTP operations."""
    import threading
    
    result = {'success': False, 'error': 'Operation timed out'}
    exception = None
    
    def worker():
        nonlocal result, exception
        try:
            result = operation()
        except Exception as e:
            exception = e
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        record_metric('http_operation.timeout', 1.0)
        return create_error_response("Operation timed out")
    
    if exception:
        log_error(f"Operation failed: {exception}")
        return create_error_response(str(exception))
    
    return result

def batch_execute(operations: List[Callable], parallel: bool = False) -> List[Dict[str, Any]]:
    """Generic batch execution pattern."""
    if parallel:
        return _execute_parallel(operations)
    else:
        return _execute_sequential(operations)

def _execute_sequential(operations: List[Callable]) -> List[Dict[str, Any]]:
    """Execute operations sequentially."""
    results = []
    for operation in operations:
        try:
            result = operation()
            results.append(result)
        except Exception as e:
            log_error(f"Batch operation failed: {e}")
            results.append(create_error_response(str(e)))
    return results

def _execute_parallel(operations: List[Callable]) -> List[Dict[str, Any]]:
    """Execute operations in parallel."""
    import concurrent.futures
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(op) for op in operations]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                log_error(f"Parallel operation failed: {e}")
                results.append(create_error_response(str(e)))
    
    return results

def invalidate_cache_pattern(cache_pattern: str) -> Dict[str, Any]:
    """Invalidate cached results matching pattern."""
    try:
        result = cache_clear()
        return create_success_response("Cache invalidated", {'pattern': cache_pattern})
    except Exception as e:
        log_error(f"Cache invalidation failed: {e}")
        return create_error_response(str(e))

def build_query_string(params: Dict[str, Any]) -> str:
    """Generic query string builder."""
    try:
        query_parts = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    for item in value:
                        query_parts.append(f"{key}={str(item)}")
                else:
                    query_parts.append(f"{key}={str(value)}")
        return '&'.join(query_parts)
    except Exception as e:
        log_error(f"Query string building failed: {e}")
        return ''

def parse_response_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Generic response header parsing."""
    try:
        parsed = {
            'content_type': headers.get('content-type', '').split(';')[0].strip(),
            'content_length': int(headers.get('content-length', 0)) if headers.get('content-length') else 0,
            'cache_control': headers.get('cache-control', ''),
            'expires': headers.get('expires', ''),
            'etag': headers.get('etag', ''),
            'last_modified': headers.get('last-modified', ''),
            'server': headers.get('server', ''),
            'all_headers': headers
        }
        return parsed
    except Exception as e:
        log_error(f"Header parsing failed: {e}")
        return {'all_headers': headers}

def _should_retry(result: Dict[str, Any], retry_conditions: List[str]) -> bool:
    """Check if result meets retry conditions."""
    if not result.get('success', True):
        error = result.get('error', '').lower()
        status_code = result.get('status_code', 0)
        
        for condition in retry_conditions:
            if condition == 'timeout' and 'timeout' in error:
                return True
            elif condition == 'connection_error' and any(term in error for term in ['connection', 'network']):
                return True
            elif condition == '5xx' and 500 <= status_code < 600:
                return True
    return False

def _evaluate_cache_conditions(result: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """Evaluate if result meets caching conditions."""
    if not result.get('success', True):
        return False
    
    if 'status_codes' in conditions:
        status_code = result.get('status_code', 0)
        if status_code not in conditions['status_codes']:
            return False
    
    if 'min_response_size' in conditions:
        size = len(str(result.get('data', '')))
        if size < conditions['min_response_size']:
            return False
    
    return True
