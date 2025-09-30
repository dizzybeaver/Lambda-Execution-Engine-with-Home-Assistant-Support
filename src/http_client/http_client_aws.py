"""
http_client_aws.py - Revolutionary Gateway Architecture AWS Operations
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

import boto3
import time
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

from gateway import (
    validate_request,
    create_success_response, create_error_response,
    log_info, log_error,
    cache_get, cache_set, cache_clear,
    get_singleton, register_singleton,
    record_metric,
    execute_operation, GatewayInterface
)

def boto3_client_optimized_implementation(service_name: str, **kwargs) -> Dict[str, Any]:
    try:
        cache_key = f"boto3_client_{service_name}"
        cached_client = cache_get(cache_key)
        
        if cached_client:
            log_info(f"Using cached boto3 client for {service_name}")
            return create_success_response("Cached client retrieved", {"client": cached_client})
        
        log_info(f"Creating new boto3 client for {service_name}")
        
        region = kwargs.get('region_name', 'us-east-1')
        client = boto3.client(service_name, region_name=region)
        
        cache_set(cache_key, client, ttl=3600)
        record_metric(f"boto3_client_created_{service_name}", 1.0)
        
        return create_success_response("Client created", {"client": client})
        
    except NoCredentialsError as e:
        log_error(f"AWS credentials not found: {e}")
        return create_error_response("AWS credentials not configured", {"error": str(e)})
    except ClientError as e:
        log_error(f"AWS client error: {e}")
        return create_error_response("AWS client creation failed", {"error": str(e)})
    except Exception as e:
        log_error(f"Unexpected error creating boto3 client: {e}")
        return create_error_response("Client creation error", {"error": str(e)})

def get_aws_service_client(service_name: str, **kwargs) -> Any:
    result = boto3_client_optimized_implementation(service_name, **kwargs)
    return result.get('data', {}).get('client') if result.get('success') else None

def invoke_aws_service(service_name: str, operation: str, **kwargs) -> Dict[str, Any]:
    try:
        client_result = boto3_client_optimized_implementation(service_name)
        
        if not client_result.get('success'):
            return client_result
        
        client = client_result.get('data', {}).get('client')
        if not client:
            return create_error_response("Client not available")
        
        operation_func = getattr(client, operation, None)
        if not operation_func:
            return create_error_response(f"Operation {operation} not found on {service_name}")
        
        result = operation_func(**kwargs)
        record_metric(f"aws_operation_{service_name}_{operation}", 1.0)
        
        return create_success_response("Operation successful", {"result": result})
        
    except ClientError as e:
        log_error(f"AWS operation error: {e}")
        return create_error_response("AWS operation failed", {"error": str(e)})
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return create_error_response("Operation error", {"error": str(e)})

__all__ = [
    'boto3_client_optimized_implementation',
    'get_aws_service_client',
    'invoke_aws_service'
]

# EOF
