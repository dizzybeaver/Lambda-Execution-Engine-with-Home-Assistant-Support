"""
home_assistant_core.py - UPDATED: Home Assistant Core Implementation
Version: 2025.09.24.10
Description: Updated core Home Assistant implementation using ultra-pure http_client.py interface

UPDATES APPLIED:
- ✅ HTTP CLIENT: Replaced urllib3 usage with ultra-pure http_client.py interface
- ✅ GATEWAY INTEGRATION: Uses cache.py, security.py, singleton.py gateways
- ✅ MEMORY OPTIMIZATION: Maintained 128MB Lambda constraints
- ✅ COST PROTECTION: Integrated cost protection checks

ARCHITECTURE:
- Internal implementation used by home_assistant.py primary gateway
- Uses main module services only (no independent singletons)
- Memory-optimized for AWS Lambda 128MB limit
- Generic function patterns to minimize code duplication

GATEWAY ACCESS:
- PRIMARY FILE: home_assistant.py (interface)
- SECONDARY FILE: home_assistant_core.py (this implementation)

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

import json
import time
import logging
import os
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Gateway imports - using ultra-pure http_client
from . import cache
from . import security
from . import singleton
from . import config
from . import utility
from . import http_client

logger = logging.getLogger(__name__)

# ===== SECTION 1: INTERNAL DATA STRUCTURES =====

@dataclass
class HAConfig:
    """Home Assistant configuration structure."""
    base_url: str
    access_token: str
    timeout: int = 30
    max_retries: int = 3
    ssl_verify: bool = True

class HAManagerState(Enum):
    """Internal HA manager states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing" 
    CONNECTED = "connected"
    ERROR = "error"

# ===== SECTION 2: SINGLETON HA MANAGER =====

class HAManager:
    """Internal Home Assistant manager using gateway interfaces."""
    
    def __init__(self):
        self._config: Optional[HAConfig] = None
        self._state = HAManagerState.UNINITIALIZED
        self._last_request_time = 0
        self._request_count = 0
        self._error_count = 0
        
        logger.debug("HA Manager created using gateway interfaces")
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize HA manager with configuration."""
        try:
            self._state = HAManagerState.INITIALIZING
            
            # Validate configuration using security.py
            validation_result = security.validate_request({
                'base_url': config.get('base_url'),
                'access_token': config.get('access_token'),
                'config_type': 'home_assistant'
            })
            
            if not validation_result.is_valid:
                logger.error(f"HA config validation failed: {validation_result.error_message}")
                self._state = HAManagerState.ERROR
                return False
            
            self._config = HAConfig(
                base_url=config['base_url'].rstrip('/'),
                access_token=config['access_token'],
                timeout=config.get('timeout', 30),
                max_retries=config.get('max_retries', 3),
                ssl_verify=config.get('ssl_verify', True)
            )
            
            # Test connection using ultra-pure http_client
            test_result = self._test_connection()
            
            if test_result.get('success', False):
                self._state = HAManagerState.CONNECTED
                logger.info("HA Manager initialized successfully")
                return True
            else:
                self._state = HAManagerState.ERROR
                logger.error(f"HA connection test failed: {test_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"HA Manager initialization failed: {e}")
            self._state = HAManagerState.ERROR
            return False
    
    def _test_connection(self) -> Dict[str, Any]:
        """Test Home Assistant connection using ultra-pure http_client."""
        try:
            if not self._config:
                return {'success': False, 'error': 'No configuration available'}
            
            # Use ultra-pure http_client interface
            result = http_client.make_request(
                method=http_client.HttpMethod.GET,
                url=f"{self._config.base_url}/api/",
                headers=self._get_auth_headers(),
                timeout=self._config.timeout
            )
            
            return result
            
        except Exception as e:
            logger.error(f"HA connection test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if not self._config:
            return {}
        
        return {
            'Authorization': f'Bearer {self._config.access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Lambda-HA-Extension/1.0'
        }
    
    def call_service(self, domain: str, service: str, 
                    entity_id: Optional[str] = None,
                    service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call Home Assistant service using ultra-pure http_client."""
        try:
            if self._state != HAManagerState.CONNECTED:
                return {'success': False, 'error': 'HA Manager not connected'}
            
            # Check cost protection
            if utility.is_cost_protection_active():
                return {'success': False, 'error': 'Cost protection active'}
            
            # Build service call data
            call_data = {
                'domain': domain,
                'service': service
            }
            
            if entity_id:
                call_data['target'] = {'entity_id': entity_id}
            
            if service_data:
                call_data['service_data'] = service_data
            
            # Cache key for service calls
            cache_key = f"ha_service:{domain}:{service}:{entity_id or 'none'}"
            
            # Use ultra-pure http_client
            result = http_client.make_request(
                method=http_client.HttpMethod.POST,
                url=f"{self._config.base_url}/api/services/{domain}/{service}",
                headers=self._get_auth_headers(),
                data=call_data,
                timeout=self._config.timeout
            )
            
            self._last_request_time = time.time()
            self._request_count += 1
            
            if not result.get('success', False):
                self._error_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"HA service call failed: {e}")
            self._error_count += 1
            return {'success': False, 'error': str(e)}
    
    def get_entity_state(self, entity_id: str) -> Dict[str, Any]:
        """Get entity state using ultra-pure http_client."""
        try:
            if self._state != HAManagerState.CONNECTED:
                return {'success': False, 'error': 'HA Manager not connected'}
            
            # Check cache first
            cache_key = f"ha_state:{entity_id}"
            cached_state = cache.cache_get(cache_key)
            
            if cached_state:
                return cached_state
            
            # Use ultra-pure http_client
            result = http_client.make_request(
                method=http_client.HttpMethod.GET,
                url=f"{self._config.base_url}/api/states/{entity_id}",
                headers=self._get_auth_headers(),
                timeout=self._config.timeout
            )
            
            self._last_request_time = time.time()
            self._request_count += 1
            
            if result.get('success', False):
                # Cache state for 30 seconds
                cache.cache_set(cache_key, result, 30)
            else:
                self._error_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"HA get entity state failed: {e}")
            self._error_count += 1
            return {'success': False, 'error': str(e)}
    
    def set_entity_state(self, entity_id: str, state: str, 
                        attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Set entity state using ultra-pure http_client."""
        try:
            if self._state != HAManagerState.CONNECTED:
                return {'success': False, 'error': 'HA Manager not connected'}
            
            state_data = {
                'state': state,
                'attributes': attributes or {}
            }
            
            # Use ultra-pure http_client
            result = http_client.make_request(
                method=http_client.HttpMethod.POST,
                url=f"{self._config.base_url}/api/states/{entity_id}",
                headers=self._get_auth_headers(),
                data=state_data,
                timeout=self._config.timeout
            )
            
            self._last_request_time = time.time()
            self._request_count += 1
            
            if result.get('success', False):
                # Clear cached state
                cache_key = f"ha_state:{entity_id}"
                cache.cache_clear() # Clear specific key if available
            else:
                self._error_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"HA set entity state failed: {e}")
            self._error_count += 1
            return {'success': False, 'error': str(e)}
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get HA manager health metrics."""
        return {
            'state': self._state.value,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'error_rate': (self._error_count / max(self._request_count, 1)) * 100,
            'last_request_time': self._last_request_time,
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time()),
            'connected': self._state == HAManagerState.CONNECTED
        }

# ===== IMPLEMENTATION FUNCTIONS =====

def _initialize_ha_manager_implementation() -> Dict[str, Any]:
    """Initialize HA manager implementation."""
    try:
        # Check if extension is enabled
        if not os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true':
            return {
                'success': False,
                'error': 'Home Assistant extension not enabled',
                'enabled': False
            }
        
        # Get configuration from config.py
        ha_config = {
            'base_url': config.get_parameter('home_assistant_url'),
            'access_token': config.get_parameter('home_assistant_token'),
            'timeout': config.get_parameter('home_assistant_timeout', 30)
        }
        
        if not ha_config['base_url'] or not ha_config['access_token']:
            return {
                'success': False,
                'error': 'Home Assistant URL or token not configured'
            }
        
        # Get or create HA manager via singleton.py
        ha_manager = singleton.get_singleton('ha_manager', factory=HAManager)
        
        # Initialize the manager
        init_success = ha_manager.initialize(ha_config)
        
        return {
            'success': init_success,
            'enabled': True,
            'manager_state': ha_manager._state.value if hasattr(ha_manager, '_state') else 'unknown'
        }
        
    except Exception as e:
        logger.error(f"HA manager initialization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _cleanup_ha_manager_implementation() -> Dict[str, Any]:
    """Cleanup HA manager implementation."""
    try:
        # Use singleton.py to reset HA manager
        result = singleton.manage_singletons('reset', 'ha_manager')
        
        return {
            'success': True,
            'cleanup_result': result
        }
        
    except Exception as e:
        logger.error(f"HA manager cleanup failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _call_ha_service_implementation(domain: str, service: str, 
                                  entity_id: Optional[str] = None,
                                  service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call HA service implementation."""
    try:
        ha_manager = singleton.get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.call_service(domain, service, entity_id, service_data)
        
    except Exception as e:
        logger.error(f"HA service call failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_entity_state_implementation(entity_id: str) -> Dict[str, Any]:
    """Get HA entity state implementation."""
    try:
        ha_manager = singleton.get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.get_entity_state(entity_id)
        
    except Exception as e:
        logger.error(f"HA get entity state failed: {e}")
        return {'success': False, 'error': str(e)}

def _set_ha_entity_state_implementation(entity_id: str, state: str, 
                                      attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Set HA entity state implementation."""
    try:
        ha_manager = singleton.get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.set_entity_state(entity_id, state, attributes)
        
    except Exception as e:
        logger.error(f"HA set entity state failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_connection_status_implementation() -> Dict[str, Any]:
    """Get HA connection status implementation."""
    try:
        ha_manager = singleton.get_singleton('ha_manager')
        if not ha_manager:
            return {'status': 'disabled', 'error': 'HA manager not initialized'}
        
        if hasattr(ha_manager, '_state'):
            return {'status': ha_manager._state.value}
        else:
            return {'status': 'unknown'}
        
    except Exception as e:
        logger.error(f"HA connection status check failed: {e}")
        return {'status': 'error', 'error': str(e)}

def _process_ha_webhook_implementation(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process HA webhook implementation."""
    try:
        # Use security.py for webhook validation
        validation_result = security.validate_request({
            'webhook_data': webhook_data,
            'validation_type': 'webhook'
        })
        
        if not validation_result.is_valid:
            return {
                'success': False,
                'error': f'Webhook validation failed: {validation_result.error_message}'
            }
        
        # Process webhook data
        return {
            'success': True,
            'webhook_data': webhook_data,
            'processed_at': time.time()
        }
        
    except Exception as e:
        logger.error(f"HA webhook processing failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_health_metrics_implementation() -> Dict[str, Any]:
    """Get HA health metrics implementation."""
    try:
        ha_manager = singleton.get_singleton('ha_manager')
        if not ha_manager:
            return {
                'healthy': False,
                'error': 'HA manager not initialized'
            }
        
        metrics = ha_manager.get_health_metrics()
        
        # Use http_client health check
        http_health = http_client.health_check()
        
        return {
            'healthy': metrics.get('connected', False) and http_health.get('healthy', False),
            'ha_metrics': metrics,
            'http_health': http_health,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"HA health metrics failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'timestamp': time.time()
        }

# EOF
