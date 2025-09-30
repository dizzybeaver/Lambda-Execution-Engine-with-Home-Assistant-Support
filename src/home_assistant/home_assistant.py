"""
home_assistant.py - Revolutionary Gateway Architecture Extension
Version: 2025.09.30.01
Daily Revision: 001

Revolutionary Gateway Optimization - Complete Migration
All imports now route through gateway.py

ARCHITECTURE: EXTERNAL EXTENSION
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

import logging
import time
import os
from typing import Dict, Any, Optional, Union, List
from enum import Enum

from gateway import (
    get_singleton, register_singleton,
    validate_request,
    make_request, make_get_request, make_post_request,
    create_success_response, create_error_response,
    log_info, log_error,
    execute_operation, GatewayInterface
)

from .home_assistant_core import (
    _initialize_ha_manager_implementation,
    _cleanup_ha_manager_implementation,
    _call_ha_service_implementation,
    _get_ha_entity_state_implementation,
    _set_ha_entity_state_implementation,
    _get_ha_connection_status_implementation,
    _process_ha_webhook_implementation,
    _get_ha_health_metrics_implementation
)

logger = logging.getLogger(__name__)

class HAConnectionStatus(Enum):
    DISABLED = "disabled"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class HAServiceResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"

def initialize_ha_extension() -> Dict[str, Any]:
    return _initialize_ha_manager_implementation()

def cleanup_ha_extension() -> Dict[str, Any]:
    return _cleanup_ha_manager_implementation()

def call_ha_service(domain: str, service: str, 
                    entity_id: Optional[str] = None,
                    service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _call_ha_service_implementation(domain, service, entity_id, service_data)

def get_ha_state(entity_id: str) -> Dict[str, Any]:
    return _get_ha_entity_state_implementation(entity_id)

def set_ha_state(entity_id: str, state: str, 
                 attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _set_ha_entity_state_implementation(entity_id, state, attributes)

def get_ha_connection_status() -> Dict[str, Any]:
    return _get_ha_connection_status_implementation()

def process_ha_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    return _process_ha_webhook_implementation(webhook_data)

def get_ha_health() -> Dict[str, Any]:
    return _get_ha_health_metrics_implementation()

def is_ha_extension_enabled() -> bool:
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'

__all__ = [
    'HAConnectionStatus',
    'HAServiceResult',
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'call_ha_service',
    'get_ha_state',
    'set_ha_state',
    'get_ha_connection_status',
    'process_ha_webhook',
    'get_ha_health',
    'is_ha_extension_enabled'
]

# EOF
