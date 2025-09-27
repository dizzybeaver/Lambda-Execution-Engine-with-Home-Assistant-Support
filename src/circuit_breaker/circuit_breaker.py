"""
circuit_breaker.py - ULTRA-PURE: Circuit Breaker Operations Gateway Interface  
Version: 2025.09.26.01
Description: Pure delegation gateway for circuit breaker operations and failure handling

ARCHITECTURE: PRIMARY GATEWAY - PURE DELEGATION ONLY
- circuit_breaker.py (this file) = Gateway/Firewall - function declarations ONLY
- circuit_breaker_core.py = Core circuit breaker implementation logic
- circuit_breaker_policy.py = Failure policies and threshold management
- circuit_breaker_metrics.py = Circuit breaker metrics and monitoring

ULTRA-OPTIMIZED OPERATIONS:
- Circuit breaker state management (OPEN/CLOSED/HALF_OPEN)
- Service-specific failure pattern recognition
- Automatic recovery and threshold adjustment
- Integration with HTTP client and external services

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

from typing import Dict, Any, Optional, Union, List, Callable
from enum import Enum

# Ultra-pure delegation imports
from .circuit_breaker_core import (
    _circuit_breaker_execution_implementation,
    _circuit_breaker_state_implementation,
    _circuit_breaker_policy_implementation,
    _circuit_breaker_metrics_implementation
)

# ===== SECTION 1: CIRCUIT BREAKER EXECUTION OPERATIONS =====

def execute_with_circuit_breaker(service_name: str, operation: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Execute operation with circuit breaker protection - pure delegation to core."""
    return _circuit_breaker_execution_implementation(service_name, operation, *args, **kwargs)

def check_circuit_breaker_state(service_name: str) -> Dict[str, Any]:
    """Check circuit breaker state - pure delegation to core."""
    return _circuit_breaker_state_implementation("check", service_name)

def force_circuit_breaker_state(service_name: str, state: str) -> Dict[str, Any]:
    """Force circuit breaker state - pure delegation to core."""
    return _circuit_breaker_state_implementation("force", service_name, state)

# ===== SECTION 2: POLICY MANAGEMENT OPERATIONS =====

def configure_circuit_breaker_policy(service_name: str, policy: Dict[str, Any]) -> Dict[str, Any]:
    """Configure circuit breaker policy - pure delegation to core."""
    return _circuit_breaker_policy_implementation("configure", service_name, policy)

def get_circuit_breaker_policy(service_name: str) -> Dict[str, Any]:
    """Get circuit breaker policy - pure delegation to core."""
    return _circuit_breaker_policy_implementation("get", service_name)

def update_failure_threshold(service_name: str, threshold: float) -> Dict[str, Any]:
    """Update failure threshold - pure delegation to core."""
    return _circuit_breaker_policy_implementation("threshold", service_name, threshold)

# EOS

# ===== SECTION 3: MONITORING AND METRICS OPERATIONS =====

def get_circuit_breaker_metrics(service_name: str = None) -> Dict[str, Any]:
    """Get circuit breaker metrics - pure delegation to core."""
    return _circuit_breaker_metrics_implementation("get", service_name)

def record_circuit_breaker_event(service_name: str, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Record circuit breaker event - pure delegation to core."""
    return _circuit_breaker_metrics_implementation("record", service_name, event_type, details)

def reset_circuit_breaker_metrics(service_name: str) -> Dict[str, Any]:
    """Reset circuit breaker metrics - pure delegation to core."""
    return _circuit_breaker_metrics_implementation("reset", service_name)

# ===== SECTION 4: RECOVERY AND MANAGEMENT OPERATIONS =====

def attempt_circuit_breaker_recovery(service_name: str) -> Dict[str, Any]:
    """Attempt circuit breaker recovery - pure delegation to core."""
    from .circuit_breaker_core import _circuit_breaker_recovery_implementation
    return _circuit_breaker_recovery_implementation("attempt", service_name)

def get_circuit_breaker_health(service_name: str = None) -> Dict[str, Any]:
    """Get circuit breaker health status - pure delegation to core."""
    from .circuit_breaker_core import _circuit_breaker_health_implementation
    return _circuit_breaker_health_implementation(service_name)

def optimize_circuit_breaker_settings(service_name: str, optimization_level: str = "standard") -> Dict[str, Any]:
    """Optimize circuit breaker settings - pure delegation to core."""
    from .circuit_breaker_core import _circuit_breaker_optimization_implementation
    return _circuit_breaker_optimization_implementation(service_name, optimization_level)

# EOF
