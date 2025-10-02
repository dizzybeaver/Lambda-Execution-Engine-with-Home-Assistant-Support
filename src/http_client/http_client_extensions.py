"""
http_client_extensions.py - HTTP Client Extensions
Version: 2025.10.02.02
Description: Extends existing http_client_core.py with retry and transformations

ARCHITECTURE: EXTENSION - Extends existing http_client_core.py
- Uses shared_utilities for ALL operations
- Uses gateway functions exclusively
- Minimal new code, maximum reuse

OPTIMIZATION: Phase 3 - Extensions Only
- Retry configuration wrapper
- Transformation helpers using existing validation
- Connection pool manager (thin wrapper)

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP + LUGS Compatible
"""

from typing import Dict, Any, Optional, Callable
import time

def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100,
                        retriable_codes: set = None) -> Dict[str, Any]:
    """Configure HTTP retry behavior using existing http_client."""
    from gateway import cache_set, log_info, create_success_response
    
    config = {
        'max_attempts': max_attempts,
        'backoff_base_ms': backoff_base_ms,
        'retriable_status_codes': retriable_codes or {408, 429, 500, 502, 503, 504}
    }
    
    cache_set('http_retry_config', config, ttl=3600)
    log_info(f"HTTP retry configured: {max_attempts} attempts, {backoff_base_ms}ms backoff")
    
    return create_success_response("Retry configured", config)


def http_request_with_retry(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with retry using existing functions."""
    from gateway import make_request, cache_get, record_metric
    from shared_utilities import handle_operation_error, create_operation_context, close_operation_context
    
    context = create_operation_context('http_client', 'request_with_retry', method=method, url=url)
    config = cache_get('http_retry_config') or {'max_attempts': 3, 'backoff_base_ms': 100}
    
    try:
        for attempt in range(config['max_attempts']):
            try:
                result = make_request(method, url, **kwargs)
                
                if result.get('success'):
                    if attempt > 0:
                        record_metric('http_retry_success', 1.0, {'attempt': attempt + 1})
                    close_operation_context(context, success=True, result=result)
                    return result
                
                status_code = result.get('status_code', 0)
                if status_code not in config.get('retriable_status_codes', set()):
                    close_operation_context(context, success=False)
                    return result
                
                if attempt < config['max_attempts'] - 1:
                    delay_ms = config['backoff_base_ms'] * (2 ** attempt)
                    time.sleep(delay_ms / 1000.0)
                    record_metric('http_retry_attempt', 1.0, {'attempt': attempt + 1})
                    
            except Exception as e:
                if attempt == config['max_attempts'] - 1:
                    raise
                time.sleep((config['backoff_base_ms'] * (2 ** attempt)) / 1000.0)
        
        close_operation_context(context, success=False)
        return {'success': False, 'error': 'Max retries exceeded'}
        
    except Exception as e:
        return handle_operation_error('http_client', 'request_with_retry', e, context['correlation_id'])


def transform_http_response(response: Dict[str, Any], transformer: Callable) -> Dict[str, Any]:
    """Transform HTTP response using existing validation."""
    from gateway import validate_request, create_success_response, create_error_response
    
    if not response.get('success'):
        return response
    
    try:
        data = response.get('data')
        transformed = transformer(data)
        
        response['data'] = transformed
        response['transformed'] = True
        return response
        
    except Exception as e:
        return create_error_response(f"Transformation failed: {str(e)}", 'TRANSFORM_ERROR')


def validate_http_response(response: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
    """Validate HTTP response using existing validation."""
    from gateway import validate_request
    from shared_utilities import validate_operation_parameters
    
    data = response.get('data', {})
    
    validation = validate_operation_parameters(
        required_params=required_fields or [],
        **data
    )
    
    return {
        'valid': validation['valid'],
        'errors': validation.get('errors', []),
        'response': response
    }


# Common transformers
def flatten_response(data: Dict) -> Dict:
    """Flatten nested dict."""
    def _flatten(obj, parent=''):
        items = []
        for k, v in obj.items():
            key = f"{parent}.{k}" if parent else k
            if isinstance(v, dict):
                items.extend(_flatten(v, key).items())
            else:
                items.append((key, v))
        return dict(items)
    return _flatten(data)


def extract_fields(data: Dict, fields: list) -> Dict:
    """Extract specific fields."""
    return {f: data.get(f) for f in fields if f in data}


# EOF
