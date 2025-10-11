"""
home_assistant_core.py
Version: 2025.10.11.01
Description: Home Assistant Common Functions

Copyright 2025 Joseph Hersey

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

from gateway import (
    cache_get, cache_set,
    validate_request,
    get_singleton, register_singleton,
    make_request, make_get_request, make_post_request,
    create_success_response, create_error_response,
    log_info, log_error, log_debug,
    execute_operation, GatewayInterface
)

logger = logging.getLogger(__name__)

@dataclass
class HAConfig:
    base_url: str
    access_token: str
    timeout: int = 30
    max_retries: int = 3
    ssl_verify: bool = True

class HAManagerState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing" 
    CONNECTED = "connected"
    ERROR = "error"

class HAManager:
    def __init__(self):
        self._config: Optional[HAConfig] = None
        self._state = HAManagerState.UNINITIALIZED
        self._last_request_time = 0
        self._request_count = 0
        self._error_count = 0
        log_debug("HA Manager created using gateway interfaces")
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            self._state = HAManagerState.INITIALIZING
            
            validation_result = validate_request({
                'base_url': config.get('base_url'),
                'access_token': config.get('access_token'),
                'config_type': 'home_assistant'
            })
            
            if not validation_result:
                log_error(f"HA config validation failed")
                self._state = HAManagerState.ERROR
                return False
            
            self._config = HAConfig(
                base_url=config['base_url'].rstrip('/'),
                access_token=config['access_token'],
                timeout=config.get('timeout', 30),
                max_retries=config.get('max_retries', 3),
                ssl_verify=config.get('ssl_verify', True)
            )
            
            test_result = self._test_connection()
            
            if test_result.get('success', False):
                self._state = HAManagerState.CONNECTED
                log_info("HA Manager initialized successfully")
                return True
            else:
                self._state = HAManagerState.ERROR
                log_error(f"HA connection test failed: {test_result.get('error')}")
                return False
                
        except Exception as e:
            log_error(f"HA Manager initialization failed: {e}")
            self._state = HAManagerState.ERROR
            return False
    
    def _test_connection(self) -> Dict[str, Any]:
        try:
            if not self._config:
                return {'success': False, 'error': 'No configuration available'}
            
            result = make_get_request(
                url=f"{self._config.base_url}/api/",
                headers=self._get_auth_headers(),
                timeout=self._config.timeout
            )
            
            return result
            
        except Exception as e:
            log_error(f"HA connection test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_auth_headers(self) -> Dict[str, str]:
        if not self._config:
            return {}
        return {
            'Authorization': f'Bearer {self._config.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        return {
            'state': self._state.value,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'error_rate': (self._error_count / max(self._request_count, 1)) * 100,
            'last_request_time': self._last_request_time,
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time()),
            'connected': self._state == HAManagerState.CONNECTED
        }

def _initialize_ha_manager_implementation() -> Dict[str, Any]:
    try:
        if not os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true':
            return {
                'success': False,
                'error': 'Home Assistant extension not enabled',
                'enabled': False
            }
        
        ha_config = {
            'base_url': execute_operation(GatewayInterface.CONFIG, 'get_parameter', name='home_assistant_url'),
            'access_token': execute_operation(GatewayInterface.CONFIG, 'get_parameter', name='home_assistant_token'),
            'timeout': execute_operation(GatewayInterface.CONFIG, 'get_parameter', name='home_assistant_timeout', default=30)
        }
        
        if not ha_config['base_url'] or not ha_config['access_token']:
            return {
                'success': False,
                'error': 'Home Assistant URL or token not configured'
            }
        
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            ha_manager = HAManager()
            register_singleton('ha_manager', ha_manager)
        
        init_success = ha_manager.initialize(ha_config)
        
        return {
            'success': init_success,
            'enabled': True,
            'manager_state': ha_manager._state.value if hasattr(ha_manager, '_state') else 'unknown'
        }
        
    except Exception as e:
        log_error(f"HA manager initialization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _cleanup_ha_manager_implementation() -> Dict[str, Any]:
    try:
        result = execute_operation(GatewayInterface.SINGLETON, 'cleanup', target_id='ha_manager')
        return {
            'success': True,
            'cleanup_result': result
        }
    except Exception as e:
        log_error(f"HA manager cleanup failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def _call_ha_service_implementation(domain: str, service: str, 
                                  entity_id: Optional[str] = None,
                                  service_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.call_service(domain, service, entity_id, service_data)
    except Exception as e:
        log_error(f"HA service call failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_entity_state_implementation(entity_id: str) -> Dict[str, Any]:
    try:
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.get_entity_state(entity_id)
    except Exception as e:
        log_error(f"HA get entity state failed: {e}")
        return {'success': False, 'error': str(e)}

def _set_ha_entity_state_implementation(entity_id: str, state: str, 
                                      attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            return {'success': False, 'error': 'HA manager not initialized'}
        
        return ha_manager.set_entity_state(entity_id, state, attributes)
    except Exception as e:
        log_error(f"HA set entity state failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_connection_status_implementation() -> Dict[str, Any]:
    try:
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            return {'status': 'disabled', 'error': 'HA manager not initialized'}
        
        if hasattr(ha_manager, '_state'):
            return {'status': ha_manager._state.value}
        else:
            return {'status': 'unknown'}
    except Exception as e:
        log_error(f"HA connection status check failed: {e}")
        return {'status': 'error', 'error': str(e)}

def _process_ha_webhook_implementation(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validation_result = validate_request({
            'webhook_data': webhook_data,
            'validation_type': 'webhook'
        })
        
        if not validation_result:
            return {
                'success': False,
                'error': 'Webhook validation failed'
            }
        
        return {
            'success': True,
            'webhook_data': webhook_data,
            'processed_at': time.time()
        }
    except Exception as e:
        log_error(f"HA webhook processing failed: {e}")
        return {'success': False, 'error': str(e)}

def _get_ha_health_metrics_implementation() -> Dict[str, Any]:
    try:
        ha_manager = get_singleton('ha_manager')
        if not ha_manager:
            return {
                'healthy': False,
                'error': 'HA manager not initialized'
            }
        
        metrics = ha_manager.get_health_metrics()
        http_health = execute_operation(GatewayInterface.HTTP_CLIENT, 'health_check')
        
        return {
            'healthy': metrics.get('connected', False) and http_health.get('healthy', False),
            'ha_metrics': metrics,
            'http_health': http_health,
            'timestamp': time.time()
        }
    except Exception as e:
        log_error(f"HA health metrics failed: {e}")
        return {
            'healthy': False,
            'error': str(e),
            'timestamp': time.time()
        }

# EOF
