"""
http_client_integration.py - AWS-specific HTTP client operations with boto3
Version: 2025.10.13.01
Description: AWS service client integration with proper absolute imports

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

import boto3
import json
import time
from typing import Dict, Any, Optional, Union
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
import logging

# ✅ CORRECT: Absolute imports from gateway
from gateway import (
    cache_get, cache_set, cache_delete, cache_clear,
    validate_request, encrypt_data, decrypt_data,
    get_singleton, register_singleton,
    record_metric, increment_counter,
    get_parameter, set_parameter,
    log_info, log_error, log_warning,
    create_success_response, create_error_response
)

logger = logging.getLogger(__name__)

# ===== AWS CLIENT CREATION FUNCTIONS =====

def create_boto3_client(configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Create AWS boto3 client with configuration from gateway config."""
    
    try:
        config_params = configuration or {}
        
        # Use gateway config for AWS configuration
        aws_config = {
            'region_name': get_parameter('aws_region', 'us-east-1'),
            'retries': get_parameter('aws_retries', {'max_attempts': 3}),
            'read_timeout': get_parameter('aws_read_timeout', 30),
            'connect_timeout': get_parameter('aws_connect_timeout', 10)
        }
        
        # Merge with provided configuration
        aws_config.update(config_params)
        
        # Create boto3 config
        boto_config = Config(
            retries=aws_config.get('retries'),
            read_timeout=aws_config.get('read_timeout'),
            connect_timeout=aws_config.get('connect_timeout')
        )
        
        # Use gateway security for credential validation
        credential_validation = validate_request({
            'service': 'aws',
            'credentials': aws_config
        })
        
        if not credential_validation:
            log_warning("AWS credential validation returned false")
        
        # Create boto3 session
        session = boto3.Session(region_name=aws_config.get('region_name'))
        
        log_info(f"Created AWS boto3 session for region: {aws_config.get('region_name')}")
        
        return session
        
    except Exception as e:
        log_error(f"Failed to create AWS client: {e}")
        raise


def get_aws_service_client(service_name: str, 
                          configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Get AWS service client using gateway singleton."""
    
    singleton_key = f'aws_client_{service_name}'
    
    # Use gateway singleton for AWS client management
    client = get_singleton(singleton_key)
    
    if not client:
        try:
            # Get boto3 session
            session = create_boto3_client(configuration)
            
            # Create service client
            service_config = configuration or {}
            client = session.client(service_name, **service_config)
            
            # Store in gateway singleton
            register_singleton(singleton_key, client)
            
            increment_counter(f'aws_client.{service_name}.created')
            log_info(f"Created AWS {service_name} client")
            
        except Exception as e:
            log_error(f"Failed to create AWS {service_name} client: {e}")
            raise
    
    return client


# ===== AWS-SPECIFIC HTTP OPERATIONS =====

def make_aws_api_call(service: str,
                     operation: str,
                     parameters: Optional[Dict[str, Any]] = None,
                     use_cache: bool = True) -> Dict[str, Any]:
    """Make AWS API call with caching and metrics."""
    
    try:
        # Create cache key
        cache_key = f"aws_api:{service}:{operation}:{hash(str(parameters or {}))}"
        
        # Check gateway cache for cached response
        if use_cache:
            cached_response = cache_get(cache_key)
            if cached_response:
                increment_counter(f'aws_api.{service}.cache_hit')
                log_info(f"AWS API cache hit: {service}.{operation}")
                return cached_response
        
        # Get AWS service client
        client = get_aws_service_client(service)
        
        # Make API call
        start_time = time.time()
        
        if hasattr(client, operation):
            operation_func = getattr(client, operation)
            response = operation_func(**(parameters or {}))
        else:
            raise ValueError(f"Operation '{operation}' not supported for service '{service}'")
        
        duration = time.time() - start_time
        
        # Process response
        result = {
            'success': True,
            'data': response,
            'service': service,
            'operation': operation,
            'duration': duration,
            'timestamp': time.time()
        }
        
        # Cache response if successful
        if use_cache and result['success']:
            cache_ttl = get_parameter('aws_cache_ttl', 300)
            cache_set(cache_key, result, cache_ttl)
        
        # Record metrics via gateway
        record_metric(f'aws_api.{service}.duration', duration)
        increment_counter(f'aws_api.{service}.success')
        
        log_info(f"AWS API call successful: {service}.{operation} ({duration:.3f}s)")
        
        return result
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        increment_counter(f'aws_api.{service}.error.{error_code}')
        log_error(f"AWS API ClientError: {service}.{operation} - {error_code}")
        
        return {
            'success': False,
            'error': str(e),
            'error_code': error_code,
            'service': service,
            'operation': operation
        }
    
    except NoCredentialsError as e:
        increment_counter(f'aws_api.{service}.error.no_credentials')
        log_error(f"AWS API NoCredentialsError: {service}.{operation}")
        
        return {
            'success': False,
            'error': 'No AWS credentials found',
            'error_code': 'NO_CREDENTIALS',
            'service': service,
            'operation': operation
        }
    
    except Exception as e:
        increment_counter(f'aws_api.{service}.error.unknown')
        log_error(f"AWS API unknown error: {service}.{operation} - {str(e)}")
        
        return {
            'success': False,
            'error': str(e),
            'error_code': 'UNKNOWN_ERROR',
            'service': service,
            'operation': operation
        }


def batch_aws_api_calls(calls: list) -> Dict[str, Any]:
    """Execute multiple AWS API calls with gateway cache and metrics."""
    
    try:
        results = []
        total_start = time.time()
        
        for call in calls:
            service = call.get('service')
            operation = call.get('operation')
            parameters = call.get('parameters', {})
            use_cache = call.get('use_cache', True)
            
            result = make_aws_api_call(
                service=service,
                operation=operation,
                parameters=parameters,
                use_cache=use_cache
            )
            
            results.append(result)
        
        total_duration = time.time() - total_start
        
        # Record batch metrics via gateway
        record_metric('aws_api.batch.duration', total_duration)
        increment_counter('aws_api.batch.executed', len(calls))
        
        log_info(f"AWS API batch completed: {len(calls)} calls in {total_duration:.3f}s")
        
        return create_success_response("Batch AWS API calls completed", {
            'results': results,
            'call_count': len(calls),
            'duration': total_duration
        })
        
    except Exception as e:
        log_error(f"AWS API batch failed: {str(e)}")
        return create_error_response(f"Batch AWS API calls failed: {str(e)}")


def get_aws_client_stats(service_name: str) -> Dict[str, Any]:
    """Get AWS client statistics via gateway singleton."""
    
    try:
        singleton_key = f'aws_client_{service_name}'
        client = get_singleton(singleton_key)
        
        if not client:
            return create_error_response(f"AWS {service_name} client not initialized")
        
        # Get metrics from gateway
        call_count = get_parameter(f'aws_client_{service_name}_calls', 0)
        error_count = get_parameter(f'aws_client_{service_name}_errors', 0)
        
        stats = {
            'service': service_name,
            'client_exists': True,
            'call_count': call_count,
            'error_count': error_count,
            'success_rate': ((call_count - error_count) / call_count * 100) if call_count > 0 else 0.0
        }
        
        return create_success_response("AWS client stats retrieved", stats)
        
    except Exception as e:
        log_error(f"Failed to get AWS client stats: {e}")
        return create_error_response(str(e))


def reset_aws_clients() -> Dict[str, Any]:
    """Reset all AWS clients via gateway singleton."""
    
    try:
        # Get all AWS client singletons
        aws_services = ['s3', 'dynamodb', 'lambda', 'sns', 'sqs', 'ec2', 'cloudwatch']
        
        reset_count = 0
        for service in aws_services:
            singleton_key = f'aws_client_{service}'
            client = get_singleton(singleton_key)
            if client:
                # Reset handled by gateway singleton management
                register_singleton(singleton_key, None)
                reset_count += 1
        
        log_info(f"Reset {reset_count} AWS clients")
        
        return create_success_response("AWS clients reset", {
            'reset_count': reset_count
        })
        
    except Exception as e:
        log_error(f"Failed to reset AWS clients: {e}")
        return create_error_response(str(e))


# ===== EXPORTS =====

__all__ = [
    'create_boto3_client',
    'get_aws_service_client',
    'make_aws_api_call',
    'batch_aws_api_calls',
    'get_aws_client_stats',
    'reset_aws_clients'
]

# EOF
