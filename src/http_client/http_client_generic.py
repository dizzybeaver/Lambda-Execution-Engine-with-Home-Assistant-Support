"""
http_client_generic.py - Generic HTTP Patterns and Utilities
Version: 2025.09.24.01
Description: Reusable HTTP patterns and generic utilities using gateway interfaces

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Generic HTTP patterns for reuse across implementations
- Common utilities using utility.py gateway
- Generic validation using security.py
- Pattern caching using cache.py

PRIMARY FILE: http_client.py (interface)
SECONDARY FILE: http_client_generic.py (generic patterns)

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
from typing import Dict, Any, Optional, Union, List, Callable
import logging
import time

# Gateway imports
from . import utility
from . import security
from . import cache
from . import metrics
from . import config

logger = logging.getLogger(__name__)

# ===== GENERIC CLIENT CREATION FUNCTIONS =====

def create_generic_client(client_type: str, 
                         configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Create generic HTTP client for unsupported client types."""
    
    try:
        # Use config.py for default configuration
        default_config = {
            'timeout': config.get_parameter('http_timeout', 30),
            'retries': config.get_parameter('http_retries', 3),
            'headers': config.get_parameter('http_default_headers', {})
        }
        
        # Merge configurations
        client_config = {**default_config, **(configuration or {})}
        
        # For unsupported client types, return urllib3 as fallback
        import urllib3
        
        return urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=10, read=client_config.get('timeout', 30)),
            retries=urllib3.Retry(total=client_config.get('retries', 3))
        )
        
    except Exception as e:
        logger.error(f"Failed to create generic client: {e}")
        raise

# ===== GENERIC REQUEST PATTERNS =====

def execute_with_retry(operation: Callable,
                      max_retries: int = 3,
                      backoff_factor: float = 0.5,
                      retry_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generic retry pattern for HTTP operations."""
    
    retry_conditions = retry_conditions or ['timeout', 'connection_error', '5xx']
    
    for attempt in range(max_retries + 1):
        try:
            result = operation()
            
            # Check if retry is needed based on result
            if _should_retry(result, retry_conditions) and attempt < max_retries:
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
                continue
            
            return result
            
        except Exception as e:
            if attempt == max_retries:
                return {
                    'success': False,
                    'error': str(e),
                    'attempts': attempt + 1
                }
            
            wait_time = backoff_factor * (2 ** attempt)
            time.sleep(wait_time)
    
    return {
        'success': False,
        'error': 'Max retries exceeded',
        'attempts': max_retries + 1
    }

def batch_requests(requests: List[Dict[str, Any]],
                  batch_size: int = 10,
                  delay_between_batches: float = 0.1) -> List[Dict[str, Any]]:
    """Generic batch processing pattern for HTTP requests."""
    
    try:
        from .http_client_core import _make_request_implementation
        
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = []
            
            for request in batch:
                try:
                    result = _make_request_implementation(
                        method=request.get('method', 'GET'),
                        url=request.get('url'),
                        headers=request.get('headers'),
                        data=request.get('data'),
                        params=request.get('params'),
                        timeout=request.get('timeout')
                    )
                    batch_results.append(result)
                    
                except Exception as e:
                    batch_results.append({
                        'success': False,
                        'error': str(e),
                        'request': request
                    })
            
            results.extend(batch_results)
            
            # Delay between batches
            if i + batch_size < len(requests):
                time.sleep(delay_between_batches)
        
        metrics.increment_counter('http_client.batch_requests')
        metrics.record_value('http_client.batch_size', len(requests))
        
        return results
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return [{'success': False, 'error': str(e)} for _ in requests]

def parallel_requests(requests: List[Dict[str, Any]],
                     max_workers: int = 5) -> List[Dict[str, Any]]:
    """Generic parallel processing pattern for HTTP requests."""
    
    try:
        import concurrent.futures
        from .http_client_core import _make_request_implementation
        
        def make_single_request(request):
            try:
                return _make_request_implementation(
                    method=request.get('method', 'GET'),
                    url=request.get('url'),
                    headers=request.get('headers'),
                    data=request.get('data'),
                    params=request.get('params'),
                    timeout=request.get('timeout')
                )
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'request': request
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(make_single_request, requests))
        
        metrics.increment_counter('http_client.parallel_requests')
        metrics.record_value('http_client.parallel_count', len(requests))
        
        return results
        
    except Exception as e:
        logger.error(f"Parallel processing failed: {e}")
        return [{'success': False, 'error': str(e)} for _ in requests]

# ===== GENERIC VALIDATION PATTERNS =====

def validate_url(url: str) -> Dict[str, Any]:
    """Generic URL validation pattern."""
    
    try:
        # Use security.py for URL validation
        validation_result = security.validate_request({
            'url': url,
            'validation_type': 'url'
        })
        
        return {
            'valid': validation_result.is_valid,
            'error': validation_result.error_message if not validation_result.is_valid else None,
            'url': url
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'url': url
        }

def validate_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Generic header validation pattern."""
    
    try:
        # Use security.py for header validation
        validation_result = security.validate_request({
            'headers': headers,
            'validation_type': 'headers'
        })
        
        return {
            'valid': validation_result.is_valid,
            'error': validation_result.error_message if not validation_result.is_valid else None,
            'headers': headers
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'headers': headers
        }

def sanitize_request_data(data: Any) -> Dict[str, Any]:
    """Generic request data sanitization pattern."""
    
    try:
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Use utility.py for data sanitization if available
                if hasattr(utility, 'sanitize_value'):
                    sanitized[key] = utility.sanitize_value(value)
                else:
                    sanitized[key] = str(value) if value is not None else None
            
            return {
                'success': True,
                'sanitized_data': sanitized,
                'original_data': data
            }
        
        elif isinstance(data, (list, tuple)):
            sanitized = []
            for item in data:
                if hasattr(utility, 'sanitize_value'):
                    sanitized.append(utility.sanitize_value(item))
                else:
                    sanitized.append(str(item) if item is not None else None)
            
            return {
                'success': True,
                'sanitized_data': sanitized,
                'original_data': data
            }
        
        else:
            # For non-dict/list data, return as-is or convert to string
            sanitized = str(data) if data is not None else None
            
            return {
                'success': True,
                'sanitized_data': sanitized,
                'original_data': data
            }
        
    except Exception as e:
        logger.error(f"Data sanitization failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'original_data': data
        }

# ===== GENERIC CACHING PATTERNS =====

def cache_with_ttl(cache_key: str,
                  operation: Callable,
                  ttl: int = 300,
                  cache_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generic caching pattern with TTL."""
    
    try:
        # Check cache first
        cached_result = cache.cache_get(cache_key)
        
        if cached_result:
            metrics.increment_counter('http_client.generic_cache_hit')
            return cached_result
        
        # Execute operation
        result = operation()
        
        # Cache result if conditions are met
        should_cache = True
        if cache_conditions:
            should_cache = _evaluate_cache_conditions(result, cache_conditions)
        
        if should_cache and result.get('success', True):
            cache.cache_set(cache_key, result, ttl)
            metrics.increment_counter('http_client.generic_cache_set')
        
        return result
        
    except Exception as e:
        logger.error(f"Cache operation failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def invalidate_cache_pattern(cache_pattern: str) -> Dict[str, Any]:
    """Generic cache invalidation pattern."""
    
    try:
        # Use cache.py for pattern-based invalidation if available
        if hasattr(cache, 'invalidate_pattern'):
            result = cache.invalidate_pattern(cache_pattern)
        else:
            # Fallback to clearing all cache
            result = cache.cache_clear()
        
        return {
            'success': True,
            'pattern': cache_pattern,
            'invalidated': result
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== GENERIC HELPER FUNCTIONS =====

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
        logger.error(f"Query string building failed: {e}")
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
        logger.error(f"Header parsing failed: {e}")
        return {'all_headers': headers}

# ===== PRIVATE HELPER FUNCTIONS =====

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
    
    if 'success' in conditions and result.get('success') != conditions['success']:
        return False
    
    if 'status_code' in conditions and result.get('status_code') != conditions['status_code']:
        return False
    
    if 'max_response_size' in conditions:
        response_size = len(str(result.get('data', '')))
        if response_size > conditions['max_response_size']:
            return False
    
    return True

# EOF
