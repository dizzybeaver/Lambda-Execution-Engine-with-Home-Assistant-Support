"""
http_client.py - HTTP Client Operations Primary Gateway Interface
Version: 2025.09.27.01
Description: Ultra-pure gateway for HTTP client operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE
- Function declarations ONLY - no implementation code
- Pure delegation to http_client_core.py
- External access point for HTTP client operations
- Ultra-optimized for 128MB Lambda constraint

PRIMARY GATEWAY FUNCTIONS:
- make_request() - HTTP request operations (GET, POST, etc.)
- get_http_status() - HTTP client status and health monitoring
- get_aws_client() - AWS service client management

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

from typing import Dict, Any
from .http_client_core import generic_http_operation, HTTPOperation

# ===== SECTION 1: PRIMARY GATEWAY INTERFACE FUNCTIONS =====

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    Primary gateway function for HTTP request operations.
    Pure delegation to http_client_core implementation.
    """
    return generic_http_operation(
        HTTPOperation.MAKE_REQUEST,
        method=method,
        url=url,
        **kwargs
    )

def get_http_status() -> Dict[str, Any]:
    """
    Primary gateway function for HTTP client status monitoring.
    Pure delegation to http_client_core implementation.
    """
    return generic_http_operation(HTTPOperation.GET_STATUS)

def get_aws_client(service_name: str) -> Any:
    """
    Primary gateway function for AWS service client management.
    Pure delegation to http_client_core implementation.
    """
    return generic_http_operation(
        HTTPOperation.GET_AWS_CLIENT,
        service_name=service_name
    )

# ===== SECTION 2: MODULE EXPORTS =====

__all__ = [
    'make_request',
    'get_http_status',
    'get_aws_client'
]

# EOF
