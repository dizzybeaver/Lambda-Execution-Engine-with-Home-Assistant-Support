"""
interfaces.py - Revolutionary Gateway Architecture Interface Definitions
Version: 2025.09.30.01
Daily Revision: 001

Revolutionary Gateway Optimization - Interface Definitions
All imports now route through gateway.py

ARCHITECTURE: INTERNAL IMPLEMENTATION
- Pure interface definitions and protocols
- Uses gateway.py for all singleton operations
- No independent singleton management
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

import logging
import time
from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from gateway import get_singleton, register_singleton, execute_operation, GatewayInterface

logger = logging.getLogger(__name__)

class InterfaceType(Enum):
    ALEXA_SMART_HOME = "alexa_smart_home"
    HTTP_API = "http_api"
    LAMBDA_HANDLER = "lambda_handler"
    VALIDATION = "validation"
    RESPONSE = "response"
    METRICS = "metrics"

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class InterfaceOperation(Enum):
    INITIALIZE = "initialize"
    VALIDATE = "validate"
    PROCESS = "process"
    CLEANUP = "cleanup"
    HEALTH_CHECK = "health_check"

@dataclass
class InterfaceContext:
    operation: InterfaceOperation
    interface_type: InterfaceType
    request_id: str = field(default_factory=lambda: f"int-{int(time.time() * 1000)}")
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InterfaceResult:
    success: bool
    status: ComponentStatus
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentHealth:
    component_name: str
    status: ComponentStatus
    last_check: float = field(default_factory=time.time)
    error_count: int = 0
    uptime_seconds: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

@runtime_checkable
class ProcessorInterface(Protocol):
    def process(self, data: Dict[str, Any], context: Optional[InterfaceContext] = None) -> InterfaceResult:
        ...
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        ...
    
    def get_health_status(self) -> ComponentHealth:
        ...

@runtime_checkable
class ValidatorInterface(Protocol):
    def validate(self, data: Dict[str, Any], validation_type: str = "standard") -> InterfaceResult:
        ...
    
    def get_validation_rules(self) -> Dict[str, Any]:
        ...
    
    def is_validation_enabled(self) -> bool:
        ...

@runtime_checkable
class ResponseInterface(Protocol):
    def create_response(self, data: Dict[str, Any], response_type: str = "success") -> Dict[str, Any]:
        ...
    
    def format_response(self, response: Dict[str, Any], format_type: str = "json") -> Dict[str, Any]:
        ...
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        ...

def get_interface_registry():
    return get_singleton("interface_registry")

def register_interface(name: str, interface: Any, interface_type: str) -> bool:
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'register_interface'):
            return registry.register_interface(name, interface, interface_type)
        return False
    except Exception as e:
        logger.error(f"Failed to register interface {name}: {e}")
        return False

def get_interface(name: str) -> Optional[Any]:
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'get_interface'):
            return registry.get_interface(name)
        return None
    except Exception as e:
        logger.error(f"Failed to get interface {name}: {e}")
        return None

def get_interface_health(name: str) -> Optional[Dict[str, Any]]:
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'get_interface_health'):
            return registry.get_interface_health(name)
        return None
    except Exception as e:
        logger.error(f"Failed to get interface health {name}: {e}")
        return None

def get_all_interfaces() -> Dict[str, Any]:
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'get_all_interfaces'):
            return registry.get_all_interfaces()
        return {}
    except Exception as e:
        logger.error(f"Failed to get all interfaces: {e}")
        return {}

def perform_health_checks() -> Dict[str, Any]:
    try:
        registry = get_interface_registry()
        if registry and hasattr(registry, 'perform_health_checks'):
            return registry.perform_health_checks()
        return {}
    except Exception as e:
        logger.error(f"Failed to perform health checks: {e}")
        return {}

def create_interface_context(operation: InterfaceOperation, 
                           interface_type: InterfaceType,
                           metadata: Optional[Dict[str, Any]] = None) -> InterfaceContext:
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
    return InterfaceResult(
        success=success,
        status=status,
        data=data,
        errors=errors or [],
        warnings=warnings or []
    )

def validate_interface_type(interface: Any, expected_type: InterfaceType) -> bool:
    try:
        if expected_type == InterfaceType.ALEXA_SMART_HOME:
            required_methods = ['process', 'validate_input']
            return all(hasattr(interface, method) for method in required_methods)
        
        elif expected_type == InterfaceType.VALIDATION:
            return isinstance(interface, ValidatorInterface) or hasattr(interface, 'validate')
        
        elif expected_type == InterfaceType.RESPONSE:
            return isinstance(interface, ResponseInterface) or hasattr(interface, 'create_response')
        
        elif expected_type == InterfaceType.HTTP_API:
            required_methods = ['process', 'validate_input']
            return all(hasattr(interface, method) for method in required_methods)
        
        return callable(interface) or hasattr(interface, 'process')
        
    except Exception as e:
        logger.error(f"Interface type validation failed: {e}")
        return False

def get_interface_summary() -> Dict[str, Any]:
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

__all__ = [
    'InterfaceType', 'ComponentStatus', 'InterfaceOperation',
    'InterfaceContext', 'InterfaceResult', 'ComponentHealth',
    'ProcessorInterface', 'ValidatorInterface', 'ResponseInterface',
    'get_interface_registry', 'register_interface', 'get_interface',
    'get_interface_health', 'get_all_interfaces', 'perform_health_checks',
    'create_interface_context', 'create_interface_result',
    'validate_interface_type', 'get_interface_summary'
]

# EOF
