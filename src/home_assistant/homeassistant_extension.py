"""
homeassistant_extension.py
Version: 2025.10.13.03
Description: Home Assistant Alexa Smart Home integration with fixed imports

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

import os
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug, cache_get, cache_set,
    get_parameter, create_success_response, create_error_response
)
from ha_alexa import AlexaSmartHomeManager
from ha_core import is_ha_available, get_ha_config

HA_ASSISTANT_NAME_CACHE_KEY = "ha_assistant_name"

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    try:
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"Processing Alexa directive: {namespace}.{name}")
        
        manager = AlexaSmartHomeManager()
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            result = manager.handle_discovery()
            return _format_discovery_response(result, header)
            
        elif namespace == 'Alexa.PowerController':
            result = manager.handle_power_control(directive)
            return result
            
        elif namespace == 'Alexa.BrightnessController':
            result = manager.handle_brightness_control(directive)
            return result
            
        elif namespace == 'Alexa.ThermostatController':
            result = manager.handle_thermostat_control(directive)
            return result
            
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            result = manager.handle_accept_grant(directive)
            return result
            
        else:
            log_error(f"Unsupported directive: {namespace}.{name}")
            return _create_error_response(
                header,
                'INVALID_DIRECTIVE',
                f'Directive {namespace}.{name} not supported'
            )
            
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_error_response(
            event.get('directive', {}).get('header', {}),
            'INTERNAL_ERROR',
            str(e)
        )

def _format_discovery_response(result: Dict[str, Any], header: Dict[str, Any]) -> Dict[str, Any]:
    """Format discovery result as Alexa response."""
    if not result.get('success'):
        return _create_error_response(header, 'INTERNAL_ERROR', 
                                     result.get('message', 'Discovery failed'))
    
    endpoints = result.get('data', {}).get('endpoints', [])
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa.Discovery',
                'name': 'Discover.Response',
                'messageId': header.get('messageId', 'unknown'),
                'payloadVersion': '3'
            },
            'payload': {
                'endpoints': endpoints
            }
        }
    }

def _create_error_response(header: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': header.get('messageId', 'unknown'),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }

def get_ha_assistant_name() -> str:
    """Get configured assistant name with caching."""
    cached = cache_get(HA_ASSISTANT_NAME_CACHE_KEY)
    if cached:
        return cached
    
    name = os.getenv('HA_ASSISTANT_NAME', '')
    
    if not name:
        name = get_parameter('home_assistant_assistant_name', 'Home Assistant')
    
    cache_set(HA_ASSISTANT_NAME_CACHE_KEY, name, ttl=3600)
    return name

def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status."""
    try:
        available = is_ha_available()
        config = get_ha_config()
        
        return create_success_response("HA status retrieved", {
            'enabled': is_ha_extension_enabled(),
            'available': available,
            'configured': bool(config),
            'assistant_name': get_ha_assistant_name()
        })
        
    except Exception as e:
        log_error(f"Failed to get HA status: {str(e)}")
        return create_error_response(str(e))

def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information about HA integration."""
    try:
        from ha_alexa import AlexaSmartHomeManager
        
        manager = AlexaSmartHomeManager()
        stats = manager.get_stats()
        
        config = get_ha_config()
        
        return create_success_response("Diagnostic info retrieved", {
            'enabled': is_ha_extension_enabled(),
            'available': is_ha_available(),
            'configured': bool(config),
            'config_keys': list(config.keys()) if config else [],
            'alexa_stats': stats,
            'assistant_name': get_ha_assistant_name()
        })
        
    except Exception as e:
        log_error(f"Failed to get diagnostic info: {str(e)}")
        return create_error_response(str(e))

# EOF
