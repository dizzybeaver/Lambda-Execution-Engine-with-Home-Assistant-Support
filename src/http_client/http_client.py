"""
http_client.py - ULTRA-PURE: HTTP Client Gateway Interface
Version: 2025.09.26.01
Description: Pure delegation gateway for HTTP client operations with TLS configurability

ARCHITECTURE: PRIMARY GATEWAY - PURE DELEGATION ONLY
- http_client.py (this file) = Gateway/Firewall - function declarations ONLY
- http_client_core.py = Core HTTP client implementation logic
- http_client_security.py = TLS/SSL and security implementation
- http_client_optimization.py = Connection pooling and performance optimization

ULTRA-OPTIMIZED OPERATIONS:
- HTTP request/response handling with connection pooling
- TLS/SSL configuration with bypass capability (TLS_VERIFY_BYPASS_ENABLED)
- Retry strategies and circuit breaker integration
- AWS service client optimization

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

from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Ultra-pure delegation imports
from .http_client_core import (
    _http_request_implementation,
    _http_client_configuration_implementation,
    _http_retry_implementation,
    _http_connection_pool_implementation
)

# ===== SECTION 1: HTTP REQUEST OPERATIONS =====

def http_get(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """HTTP GET request - pure delegation to core."""
    return _http_request_implementation("GET", url, headers=headers, **kwargs)

def http_post(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """HTTP POST request - pure delegation to core."""
    return _http_request_implementation("POST", url, data=data, headers=headers, **kwargs)

def http_put(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """HTTP PUT request - pure delegation to core."""
    return _http_request_implementation("PUT", url, data=data, headers=headers, **kwargs)

def http_delete(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """HTTP DELETE request - pure delegation to core."""
    return _http_request_implementation("DELETE", url, headers=headers, **kwargs)

# ===== SECTION 2: CLIENT CONFIGURATION OPERATIONS =====

def configure_http_client(config: Dict[str, Any]) -> Dict[str, Any]:
    """Configure HTTP client settings - pure delegation to core."""
    return _http_client_configuration_implementation(config)

def set_tls_verification(enabled: bool) -> Dict[str, Any]:
    """Set TLS verification (supports TLS_VERIFY_BYPASS_ENABLED) - pure delegation to core."""
    from .http_client_core import _tls_configuration_implementation
    return _tls_configuration_implementation(enabled)

def configure_connection_pool(pool_size: int, timeout: float) -> Dict[str, Any]:
    """Configure connection pool - pure delegation to core."""
    return _http_connection_pool_implementation(pool_size, timeout)

# EOS

# ===== SECTION 3: RETRY AND RELIABILITY OPERATIONS =====

def http_request_with_retry(method: str, url: str, retry_count: int = 3, **kwargs) -> Dict[str, Any]:
    """HTTP request with retry logic - pure delegation to core."""
    return _http_retry_implementation(method, url, retry_count, **kwargs)

def get_http_client_statistics() -> Dict[str, Any]:
    """Get HTTP client performance statistics - pure delegation to core."""
    from .http_client_core import _http_statistics_implementation
    return _http_statistics_implementation()

def health_check_endpoint(url: str, timeout: float = 30.0) -> Dict[str, Any]:
    """Health check endpoint - pure delegation to core."""
    from .http_client_core import _health_check_implementation
    return _health_check_implementation(url, timeout)

# ===== SECTION 4: AWS SERVICE CLIENT OPERATIONS =====

def aws_service_request(service: str, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """AWS service request - pure delegation to core."""
    from .http_client_core import _aws_service_implementation
    return _aws_service_implementation(service, operation, parameters)

def optimize_aws_client(service: str, optimization_level: str = "standard") -> Dict[str, Any]:
    """Optimize AWS client - pure delegation to core."""
    from .http_client_core import _aws_optimization_implementation
    return _aws_optimization_implementation(service, optimization_level)

# EOF
