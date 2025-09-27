"""
http_client_aws.py - ULTRA-OPTIMIZED: AWS/Boto3 Operations with Legacy Elimination Complete
Version: 2025.09.27.01
Description: Fully optimized AWS operations with all legacy patterns eliminated and maximum gateway utilization

LEGACY ELIMINATION COMPLETED:
- ✅ REMOVED: @lru_cache decorators (replaced with cache gateway)
- ✅ REMOVED: Manual threading.RLock() (replaced with singleton gateway)
- ✅ REMOVED: Legacy boto3 client creation patterns
- ✅ REMOVED: Direct thread management (delegated to singleton gateway)
- ✅ REMOVED: Manual memory management (delegated to cache gateway)
- ✅ MODERNIZED: All patterns use gateway interfaces exclusively

ARCHITECTURE: SECONDARY IMPLEMENTATION - LEGACY-FREE
- 100% gateway interface utilization for thread safety
- Zero manual thread management or locking
- Cache gateway for all client caching and memory management
- Singleton gateway for coordination and lifecycle management
- Security gateway for all validation and sanitization

FOLLOWS PROJECT_ARCHITECTURE_REFERENCE.md - ULTRA-PURE
"""

import boto3
import time
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

# Gateway imports for maximum utilization (NO legacy imports)
from security import validate_request, ValidationLevel, sanitize_response_data
from utility import create_error_response, create_success_response, get_current_timestamp
from logging import log_error, log_info
from cache import cache_get, cache_set, cache_clear
from singleton import get_singleton, coordinate_operation, get_thread_coordinator
from metrics import record_metric
from config import get_parameter

# ===== LEGACY-FREE BOTO3 CLIENT MANAGEMENT =====

def boto3_client_optimized_implementation(service_name: str, **kwargs) -> Dict[str, Any]:
    """
    ULTRA-OPTIMIZED: Thread-safe boto3 client creation using pure gateway interfaces.
    ALL LEGACY PATTERNS ELIMINATED - Uses gateway interfaces exclusively.
    """
    
    # Validate using security gateway
    validation_result = validate_request({
        'service_name': service_name,
        'kwargs': kwargs,
        'component': 'aws_client_creation'
    }, ValidationLevel.ENHANCED)
    
    if not validation_result.get('valid', False):
        log_error('AWS service validation failed', {
            'service': service_name,
            'validation_result': validation_result
        })
        return create_error_response(f'AWS service validation failed: {service_name}')
    
    # Check cache using cache gateway (NO @lru_cache)
    cache_key = f"boto3_client_{service_name}_{hash(str(sorted(kwargs.items())))}"
    cached_client = cache_get(cache_key)
    
    if cached_client:
        record_metric('aws_client_cache_hit', 1.0, {'service': service_name})
        log_info('AWS client cache hit', {'service': service_name, 'cache_key': cache_key})
        return create_success_response({'client': cached_client, 'cached': True})
    
    # Create client using singleton gateway coordination (NO manual threading)
    def _create_client_operation():
        """Client creation operation coordinated by singleton gateway."""
        try:
            # Get AWS configuration from config gateway
            aws_config = {
                'region_name': get_parameter('aws_region', 'us-east-1'),
                'retries': get_parameter('aws_retries', {'max_attempts': 3}),
                'read_timeout': get_parameter('aws_read_timeout', 30),
                'connect_timeout': get_parameter('aws_connect_timeout', 10)
            }
            
            # Merge with provided configuration
            aws_config.update(kwargs)
            
            # Create boto3 client
            client = boto3.client(service_name, **aws_config)
            
            if not client:
                return None
            
            # Cache client using cache gateway (NO manual memory management)
            cache_ttl = kwargs.get('cache_ttl', 1800)  # 30 minutes default
            cache_set(cache_key, client, ttl=cache_ttl)
            
            record_metric('aws_client_created', 1.0, {'service': service_name})
            log_info('AWS client created successfully', {
                'service': service_name,
                'cache_ttl': cache_ttl
            })
            
            return client
            
        except Exception as e:
            log_error('AWS client creation failed', {
                'service': service_name,
                'error': str(e),
                'kwargs': str(kwargs)[:200]
            })
            return None
    
    # Execute using singleton gateway coordination (NO manual threading)
    client = coordinate_operation(_create_client_operation, {
        'operation': 'create_boto3_client',
        'service': service_name
    })
    
    if not client:
        return create_error_response(f'Failed to create AWS client for service: {service_name}')
    
    return create_success_response({
        'client': client,
        'service': service_name,
        'cached': False,
        'timestamp': get_current_timestamp()
    })

def execute_aws_api_call_implementation(service: str, operation: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    ULTRA-OPTIMIZED: Execute AWS API call using pure gateway interfaces.
    ALL LEGACY PATTERNS ELIMINATED.
    """
    
    # Context for logging and metrics
    context = {
        'service': service,
        'operation': operation,
        'component': 'aws_api_call'
    }
    
    # Validate using security gateway
    validation_result = validate_request({
        'service': service,
        'operation': operation,
        'params': params,
        'component': 'aws_api_call'
    }, ValidationLevel.ENHANCED)
    
    if not validation_result.get('valid', False):
        log_error('AWS API call validation failed', context)
        return create_error_response(f'AWS API call validation failed: {service}.{operation}')
    
    # Check cache for idempotent operations using cache gateway
    if _is_cacheable_operation(service, operation):
        cache_key = f"aws_api_{service}_{operation}_{hash(str(params) if params else '')}"
        cached_result = cache_get(cache_key)
        
        if cached_result:
            record_metric('aws_api_cache_hit', 1.0, context)
            log_info('AWS API cache hit', {**context, 'cache_key': cache_key})
            return cached_result
    
    # Get AWS client using optimized implementation
    client_result = boto3_client_optimized_implementation(service)
    if not client_result.get('success', False):
        return client_result
    
    client = client_result.get('data', {}).get('client')
    if not client:
        return create_error_response(f'Failed to get AWS client for service: {service}')
    
    # Execute API call using singleton gateway coordination
    def _execute_api_operation():
        """API execution operation coordinated by singleton gateway."""
        try:
            # Get operation method
            if not hasattr(client, operation):
                raise AttributeError(f'Operation {operation} not available for service {service}')
            
            api_method = getattr(client, operation)
            
            # Execute API call
            if params:
                result = api_method(**params)
            else:
                result = api_method()
            
            # Sanitize result using security gateway
            sanitized_result = sanitize_response_data(result)
            
            return create_success_response({
                'result': sanitized_result,
                'service': service,
                'operation': operation,
                'timestamp': get_current_timestamp()
            })
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            log_error('AWS API ClientError', {
                **context,
                'error_code': error_code,
                'error_message': error_message
            })
            
            record_metric('aws_api_error', 1.0, {**context, 'error_code': error_code})
            return create_error_response(f'AWS API error ({error_code}): {error_message}')
            
        except Exception as e:
            log_error('AWS API execution failed', {**context, 'error': str(e)})
            record_metric('aws_api_error', 1.0, {**context, 'error_type': type(e).__name__})
            return create_error_response(f'AWS API execution failed: {str(e)}')
    
    # Execute using singleton gateway coordination
    api_result = coordinate_operation(_execute_api_operation, context)
    
    # Cache successful results using cache gateway
    if (api_result.get('success', False) and 
        _is_cacheable_operation(service, operation)):
        cache_ttl = _get_cache_ttl(service, operation)
        cache_set(cache_key, api_result, ttl=cache_ttl)
        log_info('AWS API result cached', {**context, 'cache_ttl': cache_ttl})
    
    record_metric('aws_api_success', 1.0, context)
    return api_result

def cleanup_aws_clients_implementation() -> Dict[str, Any]:
    """
    ULTRA-OPTIMIZED: Clean up AWS clients using cache gateway.
    NO manual memory management.
    """
    try:
        # Clear AWS client cache using cache gateway
        cache_clear('boto3_client')
        cache_clear('aws_api')
        
        log_info('AWS clients cleaned up successfully')
        record_metric('aws_cleanup_success', 1.0)
        
        return create_success_response({
            'cleaned_up': True,
            'timestamp': get_current_timestamp()
        })
        
    except Exception as e:
        log_error('AWS cleanup failed', {'error': str(e)})
        record_metric('aws_cleanup_error', 1.0)
        return create_error_response(f'AWS cleanup failed: {str(e)}')

# ===== HELPER FUNCTIONS =====

def _is_cacheable_operation(service: str, operation: str) -> bool:
    """Determine if AWS operation is cacheable."""
    # Read-only operations that can be cached
    cacheable_operations = {
        'lambda': ['get_function', 'list_functions', 'get_function_configuration'],
        's3': ['get_object', 'head_object', 'list_objects_v2'],
        'dynamodb': ['get_item', 'query', 'scan'],
        'cloudwatch': ['get_metric_statistics', 'list_metrics']
    }
    
    service_operations = cacheable_operations.get(service, [])
    return operation in service_operations

def _get_cache_ttl(service: str, operation: str) -> int:
    """Get appropriate cache TTL for AWS operation."""
    # TTL based on operation type
    ttl_map = {
        'lambda': 300,    # 5 minutes
        's3': 600,        # 10 minutes  
        'dynamodb': 60,   # 1 minute
        'cloudwatch': 180 # 3 minutes
    }
    
    return ttl_map.get(service, 300)  # Default 5 minutes

# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'boto3_client_optimized_implementation',
    'execute_aws_api_call_implementation', 
    'cleanup_aws_clients_implementation'
]

# EOF
