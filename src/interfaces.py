"""
interfaces.py - CONSOLIDATED: Pure Interface Definitions (Singleton Logic Removed)
Version: 2025.09.25.02
Description: Interface definitions using consolidated singleton.py gateway

CONSOLIDATION APPLIED:
- ❌ REMOVED: get_interface_registry() implementation
- ❌ REMOVED: get_dependency_container() import
- ❌ REMOVED: All singleton management logic  
- ✅ IMPORTS: All registry functions from singleton.py gateway
- ✅ MAINTAINED: All interface functionality through delegation

PURE FUNCTIONAL INTERFACE - No singleton management code

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

import logging
import time
from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

# CONSOLIDATION: Import registry functions from singleton.py gateway
from singleton import (
    get_interface_registry,
    register_interface,
    get_interface,
    get_interface_health,
    get_all_interfaces
)

logger = logging.getLogger(__name__)

# ===== SECTION 1: INTERFACE ENUMS (UNCHANGED) =====

class InterfaceType(Enum):
    """Types of interfaces supported."""
    ALEXA_SMART_HOME = "alexa_smart_home"
    HTTP_API = "http_api"
    LAMBDA_HANDLER = "lambda_handler"
    VALIDATION = "validation"
    RESPONSE = "response"
    METRICS = "metrics"

class ComponentStatus(Enum):
    """Component status for health checks."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class InterfaceOperation(Enum):
    """Interface operations."""
    INITIALIZE = "initialize"
    VALIDATE = "validate"
    PROCESS = "process"
    CLEANUP = "cleanup"
    HEALTH_CHECK = "health_check"

# ===== SECTION 2: INTERFACE DATA STRUCTURES (UNCHANGED) =====

@dataclass
class InterfaceContext:
    """Context for interface operations."""
    operation: InterfaceOperation
    interface_type: InterfaceType
    request_id: str = field(default_factory=lambda: f"int-{int(time.time() * 1000)}")
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InterfaceResult:
    """Result of interface operation."""
    success: bool
    status: ComponentStatus
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentHealth:
    """Health status of a component."""
    component_name: str
    status: ComponentStatus
    last_check: float = field(default_factory=time.time)
    error_count: int = 0
    uptime_seconds: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

# ===== SECTION 3: ABSTRACT INTERFACES (UNCHANGED) =====

@runtime_checkable
class ProcessorInterface(Protocol):
    """Interface for data processors."""
    
    def process(self, data: Dict[str, Any], context: Optional[InterfaceContext] = None) -> InterfaceResult:
        """Process data with given context."""
        ...
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        ...
    
    def get_health_status(self) -> ComponentHealth:
        """Get current health status."""
        ...

@runtime_checkable
class ValidatorInterface(Protocol):
    """Interface for validators."""
    
    def validate(self, data: Dict[str, Any], validation_type: str = "standard") -> InterfaceResult:
        """Validate data with specified type."""
        ...
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get current validation rules."""
        ...
    
    def is_validation_enabled(self) -> bool:
        """Check if validation is enabled."""
        ...

@runtime_checkable
class ResponseInterface(Protocol):
    """Interface for response handlers."""
    
    def create_response(self, data: Dict[str, Any], response_type: str = "success") -> Dict[str, Any]:
        """Create response with given data and type."""
        ...
    
    def format_response(self, response: Dict[str, Any], format_type: str = "json") -> Dict[str, Any]:
        """Format response according to type."""
        ...
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate response structure."""
        ...

# ===== SECTION 4: INTERFACE MANAGEMENT (NOW PURE DELEGATION) =====

# NOTE: All registry functions now imported from singleton.py - no local implementation needed!
# Functions available: get_interface_registry, register_interface, get_interface, 
# get_interface_health, get_all_interfaces

def perform_health_checks() -> Dict[str, Any]:
    """Perform health checks using consolidated singleton system."""
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'perform_health_checks'):
            return registry.perform_health_checks()
        return {}
    except Exception as e:
        logger.error(f"Failed to perform health checks: {e}")
        return {}

# ===== SECTION 5: UTILITY FUNCTIONS (PURE FUNCTIONAL) =====

def create_interface_context(operation: InterfaceOperation, 
                           interface_type: InterfaceType,
                           metadata: Optional[Dict[str, Any]] = None) -> InterfaceContext:
    """Create interface context for operations - pure functional."""
    return InterfaceContext(
        operation=operation,
        interface_type=interface_type,
        metadata=metadata or {}
    )

def create_interface_result(success: bool, 
                          status: ComponentStatus,
                          data: Optional[Dict[str, Any]] = None,
                          errors: Optional[List[str]] = None,
                          warnings: Optional[List[str]] = None) -> InterfaceResult:
    """Create interface result for operations - pure functional."""
    return InterfaceResult(
        success=success,
        status=status,
        data=data,
        errors=errors or [],
        warnings=warnings or []
    )

def validate_interface_type(interface: Any, expected_type: InterfaceType) -> bool:
    """Validate interface against expected type - pure functional."""
    try:
        if expected_type == InterfaceType.ALEXA_SMART_HOME:
            # Check for basic Alexa interface methods
            required_methods = ['process', 'validate_input']
            return all(hasattr(interface, method) for method in required_methods)
        
        elif expected_type == InterfaceType.VALIDATION:
            # Check for validation interface methods
            return isinstance(interface, ValidatorInterface) or hasattr(interface, 'validate')
        
        elif expected_type == InterfaceType.RESPONSE:
            # Check for response interface methods
            return isinstance(interface, ResponseInterface) or hasattr(interface, 'create_response')
        
        elif expected_type == InterfaceType.HTTP_API:
            # Check for HTTP API methods
            required_methods = ['process', 'validate_input']
            return all(hasattr(interface, method) for method in required_methods)
        
        # Default validation - check if it's callable or has process method
        return callable(interface) or hasattr(interface, 'process')
        
    except Exception as e:
        logger.error(f"Interface type validation failed: {e}")
        return False

def get_interface_summary() -> Dict[str, Any]:
    """Get summary of all interfaces - pure functional."""
    try:
        all_interfaces = get_all_interfaces()
        return {
            'total_interfaces': len(all_interfaces),
            'interface_names': list(all_interfaces.keys()),
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get interface summary: {e}")
        return {
            'total_interfaces': 0,
            'interface_names': [],
            'error': str(e),
            'timestamp': time.time()
        }

# ===== EXPORTED FUNCTIONS =====

__all__ = [
    # Enums
    'InterfaceType', 'ComponentStatus', 'InterfaceOperation',
    
    # Data structures
    'InterfaceContext', 'InterfaceResult', 'ComponentHealth',
    
    # Protocols
    'ProcessorInterface', 'ValidatorInterface', 'ResponseInterface',
    
    # Registry functions (imported from singleton.py)
    'get_interface_registry', 'register_interface', 'get_interface',
    'get_interface_health', 'get_all_interfaces', 'perform_health_checks',
    
    # Utility functions
    'create_interface_context', 'create_interface_result',
    'validate_interface_type', 'get_interface_summary'
]

# EOF - interfaces.py is now purely functional!
