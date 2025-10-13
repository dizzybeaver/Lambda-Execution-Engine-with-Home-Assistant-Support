"""
homeassistant_extension.py
Version: 2025.10.11.01
Description: Home Assistant Alexa Smart Home integration using REST API

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@@ -19,22 +18,23 @@
"""

import os
from typing import Dict, Any, Optional
from gateway import log_info, log_error, log_debug, cache_get, cache_set






HA_ASSISTANT_NAME_CACHE_KEY = "ha_assistant_name"


def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'


def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive using REST API."""
    try:
        from homeassistant_alexa import AlexaSmartHomeManager
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
@@ -44,7 +44,6 @@ def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:

        manager = AlexaSmartHomeManager()

        # Route to appropriate handler
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            result = manager.handle_discovery()
            return _format_discovery_response(result, header)
@@ -60,9 +59,8 @@ def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
        elif namespace == 'Alexa.ThermostatController':
            result = manager.handle_thermostat_control(directive)
            return result

        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            # Store OAuth grant code for account linking
            result = manager.handle_accept_grant(directive)
            result = manager.handle_accept_grant(directive)
            return result

@@ -82,11 +80,11 @@ def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
            str(e)
        )


def _format_discovery_response(result: Dict[str, Any], header: Dict[str, Any]) -> Dict[str, Any]:
    """Format discovery result as Alexa response."""
    if not result.get('success'):
        return _create_error_response(header, 'INTERNAL_ERROR', result.get('message', 'Discovery failed'))


    endpoints = result.get('data', {}).get('endpoints', [])

@@ -104,7 +102,6 @@ def _format_discovery_response(result: Dict[str, Any], header: Dict[str, Any]) -
        }
    }


def _create_error_response(header: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
@@ -122,88 +119,58 @@ def _create_error_response(header: Dict[str, Any], error_type: str, message: str
        }
    }


def get_ha_assistant_name() -> str:
    """Get configured assistant name with caching."""
    cached = cache_get(HA_ASSISTANT_NAME_CACHE_KEY)
    if cached:
        return cached

    from gateway import get_parameter
    
    # Check environment variable first
    name = os.getenv('HA_ASSISTANT_NAME', '')

    # Fallback to Parameter Store
    if not name:
        name = get_parameter('home_assistant_assistant_name', 'Home Assistant')

    cache_set(HA_ASSISTANT_NAME_CACHE_KEY, name, ttl=3600)
    return name


def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status."""
    try:
        from ha_common import is_ha_available, get_ha_config, call_ha_api
        
        if not is_ha_available():
            return {
                'success': False,
                'message': 'Circuit breaker open'
            }
        
        config = get_ha_config()
        result = call_ha_api('/api/', config)

        return {
            'success': result.get('success', False),
            'message': result.get('data', {}).get('message', 'Unknown')
        }



    except Exception as e:
        log_error(f"HA status check failed: {str(e)}")
        return {
            'success': False,
            'message': str(e)
        }


def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information."""
    try:
        status = get_ha_status()

        return {
            'success': True,
            'data': {
                'ha_enabled': is_ha_extension_enabled(),
                'connection_status': 'connected' if status.get('success') else 'disconnected',
                'assistant_name': get_ha_assistant_name()
            }
        }






    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_assistant_name_status() -> Dict[str, Any]:
    """Get assistant name configuration status."""
    try:
        return {
            'success': True,
            'data': {
                'assistant_name': get_ha_assistant_name(),
                'source': 'environment' if os.getenv('HA_ASSISTANT_NAME') else 'parameter_store'
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# EOF
