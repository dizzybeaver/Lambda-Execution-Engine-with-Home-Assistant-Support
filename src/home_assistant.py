"""
home_assistant.py - UPDATED: Home Assistant Extension with Ultra-Pure HTTP Client
Version: 2025.09.24.10
Description: Updated Home Assistant extension using ultra-pure http_client.py interface

UPDATES APPLIED:
- ✅ HTTP CLIENT: Updated to use ultra-pure http_client.py interface
- ✅ GATEWAY COMPLIANCE: Uses only primary gateway interfaces
- ✅ MEMORY OPTIMIZATION: Maintained 128MB Lambda constraints
- ✅ COST PROTECTION: Integrated cost protection via utility.py

EXTENSION ARCHITECTURE:
- Extension uses main module services only (no independent operation)
- Enabled via HOME_ASSISTANT_ENABLED environment variable
- Uses designated singletons from main module
- 128MB Lambda optimized with generic operations

GATEWAY ARCHITECTURE:
- home_assistant.py (this file) = Primary gateway for external access
- home_assistant_core.py = Internal implementation using http_client.py
- External files use this gateway only

PRIMARY INTERFACE - All external files must use this Home Assistant gateway

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

logger = logging.getLogger(__name__)

# ===== SECTION 1: IMPORTS FROM DESIGNATED GATEWAYS =====

from singleton import (
    get_singleton,
    SingletonType
)

from utility import (
    is_cost_protection_active,
    get_usage_statistics
)

from security import (
    validate_request
)

from config import (
    get_parameter
)

from http_client import (
    make_request,
    get_client,
    health_check as http_health_check,
    HttpMethod,
    ClientType
)

# Import from internal core implementation
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

# ===== SECTION 2: HOME ASSISTANT ENUMS =====

class HAConnectionStatus(Enum):
    """Home Assistant connection status."""
    DISABLED = "disabled"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class HAServiceResult(Enum):
    """Home Assistant service call results."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"
    COST_BLOCKED = "cost_blocked"

class HAEntityType(Enum):
    """Home Assistant entity types."""
    LIGHT = "light"
    SWITCH = "switch"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    CLIMATE = "climate"
    COVER = "cover"

# ===== SECTION 3: EXTENSION INITIALIZATION =====

def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension - pure delegation."""
    return _initialize_ha_manager_implementation()

def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension - pure delegation."""
    return _cleanup_ha_manager_implementation()

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'

def get_ha_connection_status() -> HAConnectionStatus:
    """Get Home Assistant connection status - pure delegation."""
    result = _get_ha_connection_status_implementation()
    return HAConnectionStatus(result.get('status', 'disabled'))

# ===== SECTION 4: HOME ASSISTANT SERVICE CALLS =====

def call_ha_service(domain: str,
                   service: str,
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call Home Assistant service - pure delegation."""
    return _call_ha_service_implementation(domain, service, entity_id, service_data)

def turn_on_entity(entity_id: str, **kwargs) -> Dict[str, Any]:
    """Turn on Home Assistant entity - thin wrapper."""
    domain = entity_id.split('.')[0] if '.' in entity_id else 'homeassistant'
    return call_ha_service(domain, 'turn_on', entity_id, kwargs)

def turn_off_entity(entity_id: str, **kwargs) -> Dict[str, Any]:
    """Turn off Home Assistant entity - thin wrapper."""
    domain = entity_id.split('.')[0] if '.' in entity_id else 'homeassistant'
    return call_ha_service(domain, 'turn_off', entity_id, kwargs)

def toggle_entity(entity_id: str, **kwargs) -> Dict[str, Any]:
    """Toggle Home Assistant entity - thin wrapper."""
    domain = entity_id.split('.')[0] if '.' in entity_id else 'homeassistant'
    return call_ha_service(domain, 'toggle', entity_id, kwargs)

# ===== SECTION 5: HOME ASSISTANT STATE OPERATIONS =====

def get_ha_entity_state(entity_id: str) -> Dict[str, Any]:
    """Get Home Assistant entity state - pure delegation."""
    return _get_ha_entity_state_implementation(entity_id)

def set_ha_entity_state(entity_id: str,
                       state: str,
                       attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Set Home Assistant entity state - pure delegation."""
    return _set_ha_entity_state_implementation(entity_id, state, attributes)

def get_multiple_entity_states(entity_ids: List[str]) -> Dict[str, Any]:
    """Get multiple entity states - generic function."""
    
    try:
        if is_cost_protection_active():
            return {
                'success': False,
                'error': 'Cost protection active - bulk operations limited',
                'cost_protected': True
            }
        
        results = {}
        for entity_id in entity_ids:
            try:
                state_result = get_ha_entity_state(entity_id)
                results[entity_id] = state_result
            except Exception as e:
                results[entity_id] = {
                    'success': False,
                    'error': str(e)
                }
        
        successful_count = sum(1 for r in results.values() if r.get('success', False))
        
        return {
            'success': successful_count > 0,
            'results': results,
            'successful_count': successful_count,
            'total_count': len(entity_ids)
        }
        
    except Exception as e:
        logger.error(f"Multiple entity state retrieval failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== SECTION 6: HOME ASSISTANT WEBHOOK PROCESSING =====

def process_ha_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process Home Assistant webhook - pure delegation."""
    return _process_ha_webhook_implementation(webhook_data)

def register_ha_webhook(webhook_id: str, webhook_name: str = None) -> Dict[str, Any]:
    """Register Home Assistant webhook - generic function."""
    
    try:
        if not is_ha_extension_enabled():
            return {
                'success': False,
                'error': 'Home Assistant extension not enabled'
            }
        
        # Use http_client for webhook registration
        ha_url = get_parameter('home_assistant_url')
        if not ha_url:
            return {
                'success': False,
                'error': 'Home Assistant URL not configured'
            }
        
        # Security validation
        validation_result = validate_request({
            'webhook_id': webhook_id,
            'webhook_name': webhook_name or webhook_id
        })
        
        if not validation_result.is_valid:
            return {
                'success': False,
                'error': f'Webhook validation failed: {validation_result.error_message}'
            }
        
        webhook_url = f"{ha_url}/api/webhook/{webhook_id}"
        
        # Test webhook endpoint
        test_result = make_request(
            method=HttpMethod.POST,
            url=webhook_url,
            data={'test': True, 'timestamp': time.time()},
            timeout=10
        )
        
        return {
            'success': test_result.get('success', False),
            'webhook_id': webhook_id,
            'webhook_url': webhook_url,
            'test_result': test_result
        }
        
    except Exception as e:
        logger.error(f"Webhook registration failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== SECTION 7: HOME ASSISTANT HEALTH AND METRICS =====

def get_ha_health_metrics() -> Dict[str, Any]:
    """Get Home Assistant health metrics - pure delegation."""
    return _get_ha_health_metrics_implementation()

def check_ha_connectivity() -> Dict[str, Any]:
    """Check Home Assistant connectivity - generic function."""
    
    try:
        if not is_ha_extension_enabled():
            return {
                'connected': False,
                'error': 'Home Assistant extension not enabled'
            }
        
        # Get HA URL from config
        ha_url = get_parameter('home_assistant_url')
        if not ha_url:
            return {
                'connected': False,
                'error': 'Home Assistant URL not configured'
            }
        
        # Use ultra-pure http_client for connectivity check
        start_time = time.time()
        
        result = make_request(
            method=HttpMethod.GET,
            url=f"{ha_url}/api/",
            timeout=5
        )
        
        response_time = time.time() - start_time
        
        return {
            'connected': result.get('success', False),
            'response_time': response_time,
            'status_code': result.get('status_code', 0),
            'ha_url': ha_url,
            'timestamp': time.time(),
            'error': result.get('error') if not result.get('success') else None
        }
        
    except Exception as e:
        logger.error(f"HA connectivity check failed: {e}")
        return {
            'connected': False,
            'error': str(e),
            'timestamp': time.time()
        }

def get_ha_system_info() -> Dict[str, Any]:
    """Get Home Assistant system information - generic function."""
    
    try:
        if not is_ha_extension_enabled():
            return {
                'success': False,
                'error': 'Home Assistant extension not enabled'
            }
        
        ha_url = get_parameter('home_assistant_url')
        if not ha_url:
            return {
                'success': False,
                'error': 'Home Assistant URL not configured'
            }
        
        # Get system info from HA API
        result = make_request(
            method=HttpMethod.GET,
            url=f"{ha_url}/api/config",
            headers={
                'Authorization': f"Bearer {get_parameter('home_assistant_token')}",
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if result.get('success') and result.get('json'):
            config_data = result['json']
            return {
                'success': True,
                'system_info': {
                    'version': config_data.get('version'),
                    'location_name': config_data.get('location_name'),
                    'time_zone': config_data.get('time_zone'),
                    'unit_system': config_data.get('unit_system', {}).get('name'),
                    'components': len(config_data.get('components', [])),
                    'config_source': config_data.get('config_source')
                },
                'response_time': result.get('duration', 0)
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to get system info'),
                'status_code': result.get('status_code', 0)
            }
        
    except Exception as e:
        logger.error(f"HA system info retrieval failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== SECTION 8: HOME ASSISTANT DISCOVERY =====

def discover_ha_entities(entity_type: Union[HAEntityType, str] = None) -> Dict[str, Any]:
    """Discover Home Assistant entities - generic function."""
    
    try:
        if not is_ha_extension_enabled():
            return {
                'success': False,
                'error': 'Home Assistant extension not enabled'
            }
        
        ha_url = get_parameter('home_assistant_url')
        if not ha_url:
            return {
                'success': False,
                'error': 'Home Assistant URL not configured'
            }
        
        # Get states from HA API
        result = make_request(
            method=HttpMethod.GET,
            url=f"{ha_url}/api/states",
            headers={
                'Authorization': f"Bearer {get_parameter('home_assistant_token')}",
                'Content-Type': 'application/json'
            },
            timeout=15
        )
        
        if result.get('success') and result.get('json'):
            all_entities = result['json']
            
            # Filter by entity type if specified
            entity_type_str = entity_type.value if hasattr(entity_type, 'value') else str(entity_type) if entity_type else None
            
            if entity_type_str:
                filtered_entities = [
                    entity for entity in all_entities 
                    if entity.get('entity_id', '').startswith(f"{entity_type_str}.")
                ]
            else:
                filtered_entities = all_entities
            
            return {
                'success': True,
                'entities': filtered_entities,
                'entity_count': len(filtered_entities),
                'total_entities': len(all_entities),
                'entity_type_filter': entity_type_str,
                'response_time': result.get('duration', 0)
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to discover entities'),
                'status_code': result.get('status_code', 0)
            }
        
    except Exception as e:
        logger.error(f"HA entity discovery failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# EOF
