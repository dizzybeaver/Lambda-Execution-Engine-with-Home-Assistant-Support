"""
http_client_aws.py - AWS-Specific HTTP Client Operations
Version: 2025.09.24.01
Description: AWS-specific HTTP client operations using gateway interfaces and thin wrappers

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Thin wrappers around AWS services using boto3
- Leverages cache.py for AWS response caching
- Uses security.py for AWS credential validation
- Uses config.py for AWS endpoint configuration
- Uses metrics.py for AWS service tracking

GATEWAY LEVERAGE:
- Eliminates custom AWS session management through singleton.py
- Reduces credential handling code through security.py
- Provides unified caching through cache.py

PRIMARY FILE: http_client.py (interface)
SECONDARY FILE: http_client_aws.py (AWS implementation)

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

# Gateway imports for maximum leverage
from . import cache
from . import security
from . import singleton
from . import metrics
from . import config

logger = logging.getLogger(__name__)

# ===== AWS CLIENT CREATION FUNCTIONS =====

def create_boto3_client(configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Create AWS boto3 client with configuration from config.py."""
    
    try:
        config_params = configuration or {}
        
        # Use config.py for AWS configuration
        aws_config = {
            'region_name': config.get_parameter('aws_region', 'us-east-1'),
            'retries': config.get_parameter('aws_retries', {'max_attempts': 3}),
            'read_timeout': config.get_parameter('aws_read_timeout', 30),
            'connect_timeout': config.get_parameter('aws_connect_timeout', 10)
        }
        
        # Merge with provided configuration
        aws_config.update(config_params)
        
        # Create boto3 config
        boto_config = Config(
            retries=aws_config.get('retries'),
            read_timeout=aws_config.get('read_timeout'),
            connect_timeout=aws_config.get('connect_timeout')
        )
        
        # Use security.py for credential validation
        credential_validation = security.validate_request({
            'service': 'aws',
            'credentials': aws_config
        })
        
        if not credential_validation.is_valid:
            raise ValueError(f"AWS credential validation failed: {credential_validation.error_message}")
        
        # Create boto3 session
        session = boto3.Session(region_name=aws_config.get('region_name'))
        
        return session
        
    except Exception as e:
        logger.error(f"Failed to create AWS client: {e}")
        raise

def get_aws_service_client(service_name: str, 
                          configuration: Optional[Dict[str, Any]] = None) -> Any:
    """Get AWS service client using singleton.py."""
    
    singleton_key = f'aws_client_{service_name}'
    
    # Use singleton.py for AWS client management
    client = singleton.get_singleton(singleton_key, mode='thread_safe')
    
    if not client:
        try:
            # Get boto3 session
            session = create_boto3_client(configuration)
            
            # Create service client
            service_config = configuration or {}
            client = session.client(service_name, **service_config)
            
            # Store in singleton
            singleton.get_singleton(singleton_key, factory=lambda: client)
            
            metrics.increment_counter(f'aws_client.{service_name}.created')
            
        except Exception as e:
            logger.error(f"Failed to create AWS {service_name} client: {e}")
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
        
        # Check cache.py for cached response
        if use_cache:
            cached_response = cache.cache_get(cache_key)
            if cached_response:
                metrics.increment_counter(f'aws_api.{service}.cache_hit')
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
            cache_ttl = config.get_parameter('aws_cache_ttl', 300)
            cache.cache_set(cache_key, result, cache_ttl)
        
        # Record metrics
        metrics.record_value(f'aws_api.{service}.duration', duration)
        metrics.increment_counter(f'aws_api.{service}.success')
        
        return result
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        metrics.increment_counter(f'aws_api.{service}.error.{error_code}')
        
        return {
            'success': False,
            'error': str(e),
            'error_code': error_code,
            'service': service,
            'operation': operation
        }
    except Exception as e:
        metrics.increment_counter(f'aws_api.{service}.exception')
        logger.error(f"AWS API call failed: {e}")
        
        return {
            'success': False,
            'error': str(e),
            'service': service,
            'operation': operation
        }

def invoke_lambda_function(function_name: str,
                          payload: Optional[Dict[str, Any]] = None,
                          invocation_type: str = 'RequestResponse') -> Dict[str, Any]:
    """Invoke AWS Lambda function with caching."""
    
    return make_aws_api_call(
        service='lambda',
        operation='invoke',
        parameters={
            'FunctionName': function_name,
            'Payload': json.dumps(payload or {}),
            'InvocationType': invocation_type
        },
        use_cache=False  # Lambda invocations shouldn't be cached
    )

def get_s3_object(bucket: str, key: str, use_cache: bool = True) -> Dict[str, Any]:
    """Get S3 object with optional caching."""
    
    return make_aws_api_call(
        service='s3',
        operation='get_object',
        parameters={
            'Bucket': bucket,
            'Key': key
        },
        use_cache=use_cache
    )

def put_s3_object(bucket: str, key: str, body: Any, 
                 metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Put S3 object."""
    
    return make_aws_api_call(
        service='s3',
        operation='put_object',
        parameters={
            'Bucket': bucket,
            'Key': key,
            'Body': body,
            'Metadata': metadata or {}
        },
        use_cache=False  # Write operations shouldn't be cached
    )

def send_sns_message(topic_arn: str, message: str, 
                    subject: Optional[str] = None) -> Dict[str, Any]:
    """Send SNS message."""
    
    parameters = {
        'TopicArn': topic_arn,
        'Message': message
    }
    
    if subject:
        parameters['Subject'] = subject
    
    return make_aws_api_call(
        service='sns',
        operation='publish',
        parameters=parameters,
        use_cache=False  # Messaging shouldn't be cached
    )

def get_parameter_store_value(parameter_name: str, decrypt: bool = False) -> Dict[str, Any]:
    """Get AWS Systems Manager Parameter Store value."""
    
    return make_aws_api_call(
        service='ssm',
        operation='get_parameter',
        parameters={
            'Name': parameter_name,
            'WithDecryption': decrypt
        },
        use_cache=True  # Parameter Store values can be cached
    )

# ===== AWS HEALTH CHECK FUNCTIONS =====

def check_aws_service_health(services: Optional[List[str]] = None) -> Dict[str, Any]:
    """Check health of AWS services."""
    
    default_services = ['lambda', 's3', 'sns', 'ssm']
    check_services = services or default_services
    
    health_results = {}
    overall_healthy = True
    
    for service in check_services:
        try:
            # Simple health check - list resources or get service status
            if service == 'lambda':
                result = make_aws_api_call(service, 'list_functions', {'MaxItems': 1})
            elif service == 's3':
                result = make_aws_api_call(service, 'list_buckets')
            elif service == 'sns':
                result = make_aws_api_call(service, 'list_topics', {'MaxItems': 1})
            elif service == 'ssm':
                result = make_aws_api_call(service, 'describe_parameters', {'MaxResults': 1})
            else:
                result = {'success': False, 'error': f'Health check not implemented for {service}'}
            
            health_results[service] = {
                'healthy': result.get('success', False),
                'response_time': result.get('duration', 0),
                'error': result.get('error') if not result.get('success') else None
            }
            
            if not result.get('success'):
                overall_healthy = False
                
        except Exception as e:
            health_results[service] = {
                'healthy': False,
                'error': str(e)
            }
            overall_healthy = False
    
    return {
        'overall_healthy': overall_healthy,
        'services': health_results,
        'timestamp': time.time()
    }

# EOF
