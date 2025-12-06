"""
ha_alexa_core.py - Alexa Core Implementation (INT-HA-01)
Version: 4.2.0
Date: 2025-12-06
Description: Core implementation for Alexa Smart Home integration

CHANGES (4.2.0 - STATE ENRICHMENT FIX):
- FIXED: Enrich response with fresh state in context.properties
- ADDED: Fetch entity state after successful control
- ADDED: Build Alexa-compliant context.properties
- ADDED: Response logging for debugging
- Result: Alexa UI updates immediately with correct state

CHANGES (4.1.0 - STATE SYNC FIX):
- FIXED: Cache invalidation after control actions

CHANGES (4.0.0 - LWA MIGRATION):
- MODIFIED: All functions accept oauth_token parameter
- MODIFIED: Pass oauth_token to devices_call_ha_api
- REMOVED: Token loading from config

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any
from datetime import datetime, timezone

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter, generate_correlation_id,
    render_template
)

# Import templates
from home_assistant.ha_alexa_templates import (
    ALEXA_ERROR_RESPONSE,
    ALEXA_ACCEPT_GRANT_RESPONSE
)


def process_directive_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive implementation.
    
    LWA Migration: Accepts oauth_token parameter.
    
    Args:
        event: Alexa directive event dictionary
        oauth_token: OAuth token from directive (LWA)
        **kwargs: Additional options
        
    Returns:
        Alexa response dictionary
    """
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        try:
            import home_assistant.ha_interconnect as ha_interconnect
        except ImportError as e:
            log_error(f"[{correlation_id}] ha_interconnect not available: {e}")
            increment_counter('ha_alexa_import_error')
            return _create_error_response({}, 'INTERNAL_ERROR', 'HA interconnect unavailable')
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        # Metric tracking for directive types
        increment_counter('alexa_directive_received')
        increment_counter(f'alexa_directive_{namespace}')
        
        # Route to appropriate handler (pass oauth_token)
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            return handle_discovery_impl(event, oauth_token=oauth_token, **kwargs)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            return handle_accept_grant_impl(event, oauth_token=oauth_token, **kwargs)
        else:
            return _forward_to_ha_alexa(event, oauth_token, correlation_id)
        
    except Exception as e:
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        increment_counter('alexa_directive_error')
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device discovery implementation.
    
    LWA Migration: Accepts and uses oauth_token parameter.
    
    Args:
        event: Alexa discovery event
        oauth_token: OAuth token from directive (LWA)
        **kwargs: Additional options
        
    Returns:
        Discovery response with device list
    """
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        import home_assistant.ha_interconnect as ha_interconnect
        
        # LWA Migration: Pass oauth_token to API call
        result = ha_interconnect.devices_call_ha_api(
            '/api/alexa/smart_home',
            method='POST',
            data=event,
            oauth_token=oauth_token  # LWA token
        )
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            log_error(f"[{correlation_id}] Discovery failed: {error_msg}")
            increment_counter('alexa_discovery_failed')
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Discovery failed: {error_msg}')
        
        response_data = result.get('data')
        
        if not response_data:
            log_error(f"[{correlation_id}] No discovery data returned")
            increment_counter('alexa_discovery_no_data')
            return _create_error_response({}, 'INTERNAL_ERROR', 'No discovery data')
        
        # Filter invalid capability combinations
        filtered_response = _filter_discovery_response(response_data, correlation_id)
        
        increment_counter('alexa_discovery_success')
        return filtered_response
        
    except Exception as e:
        log_error(f"[{correlation_id}] Discovery error: {str(e)}")
        increment_counter('alexa_discovery_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Discovery error: {str(e)}')


def handle_control_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device control implementation.
    
    LWA Migration: Accepts and uses oauth_token parameter.
    
    Args:
        event: Alexa control event
        oauth_token: OAuth token from directive (LWA)
        **kwargs: Additional options
        
    Returns:
        Control response
    """
    correlation_id = generate_correlation_id()
    
    increment_counter('alexa_control_request')
    
    result = _forward_to_ha_alexa(event, oauth_token, correlation_id)
    return result


def handle_power_control_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Handle Alexa power control implementation."""
    increment_counter('alexa_power_control')
    return handle_control_impl(event, oauth_token=oauth_token, **kwargs)


def handle_brightness_control_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Handle Alexa brightness control implementation."""
    increment_counter('alexa_brightness_control')
    return handle_control_impl(event, oauth_token=oauth_token, **kwargs)


def handle_thermostat_control_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Handle Alexa thermostat control implementation."""
    increment_counter('alexa_thermostat_control')
    return handle_control_impl(event, oauth_token=oauth_token, **kwargs)


def handle_accept_grant_impl(event: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa AcceptGrant directive implementation.
    
    LWA Migration: OAuth flow managed by Alexa/HA, Lambda just acknowledges.
    
    Args:
        event: Alexa AcceptGrant event
        oauth_token: OAuth token from directive (LWA)
        **kwargs: Additional options
        
    Returns:
        AcceptGrant response
    """
    correlation_id = generate_correlation_id()
    directive = event.get('directive', {})
    header = directive.get('header', {})
    
    log_info(f"[{correlation_id}] AcceptGrant received")
    increment_counter('alexa_accept_grant')
    
    return render_template(
        ALEXA_ACCEPT_GRANT_RESPONSE,
        correlation_token=header.get('correlationToken')
    )


# ===== HELPER FUNCTIONS =====

def _forward_to_ha_alexa(event: Dict[str, Any], oauth_token: str, correlation_id: str) -> Dict[str, Any]:
    """
    Forward directive to Home Assistant's native Alexa endpoint.
    
    Enhanced to fetch fresh state and enrich response with context.properties.
    
    Args:
        event: Alexa directive event
        oauth_token: OAuth token from directive (LWA)
        correlation_id: Correlation ID for logging
        
    Returns:
        Enriched HA response with fresh state
    """
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        import home_assistant.ha_interconnect as ha_interconnect
        
        # Extract entity_id and directive info
        directive = event.get('directive', {})
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId')
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        
        log_debug(f"[{correlation_id}] Control directive: {namespace} for {entity_id}")
        
        # Forward to HA
        result = ha_interconnect.devices_call_ha_api(
            '/api/alexa/smart_home',
            method='POST',
            data=event,
            oauth_token=oauth_token
        )
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            error_code = result.get('error_code', 'UNKNOWN')
            log_error(f"[{correlation_id}] HA API call failed: {error_code} - {error_msg}")
            increment_counter('alexa_forward_ha_failed')
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'HA error: {error_msg}')
        
        response_data = result.get('data')
        
        if not response_data:
            log_error(f"[{correlation_id}] HA returned success but no data")
            increment_counter('alexa_forward_no_data')
            return _create_error_response({}, 'INTERNAL_ERROR', 'No response data from HA')
        
        # FIXED: Invalidate cache for controlled entity
        if entity_id:
            try:
                ha_interconnect.devices_invalidate_entity_cache(entity_id)
                log_debug(f"[{correlation_id}] Invalidated cache for {entity_id}")
            except Exception as cache_error:
                log_warning(f"[{correlation_id}] Cache invalidation failed: {cache_error}")
        
        # ADDED: Enrich response with fresh state
        if entity_id and namespace != 'Alexa.Discovery':
            try:
                enriched_response = _enrich_response_with_state(
                    response_data, 
                    entity_id, 
                    oauth_token, 
                    correlation_id,
                    ha_interconnect
                )
                
                # Log response structure for debugging
                log_info(f"[{correlation_id}] Response enriched with fresh state for {entity_id}")
                increment_counter('alexa_response_enriched')
                
                return enriched_response
                
            except Exception as enrich_error:
                log_warning(f"[{correlation_id}] State enrichment failed: {enrich_error}")
                # Fall back to original response
                increment_counter('alexa_enrichment_failed')
        
        increment_counter('alexa_forward_success')
        return response_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to forward to HA: {str(e)}")
        increment_counter('alexa_forward_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Connection error: {str(e)}')


def _enrich_response_with_state(response: Dict[str, Any], entity_id: str, 
                                oauth_token: str, correlation_id: str,
                                ha_interconnect) -> Dict[str, Any]:
    """
    Enrich Alexa response with fresh device state in context.properties.
    
    Args:
        response: Original HA response
        entity_id: Entity ID to fetch state for
        oauth_token: OAuth token for HA API
        correlation_id: Correlation ID for logging
        ha_interconnect: HA interconnect module
        
    Returns:
        Response enriched with fresh state
    """
    try:
        # Fetch fresh state from HA
        state_result = ha_interconnect.devices_get_by_id(entity_id, oauth_token=oauth_token)
        
        if not state_result.get('success'):
            log_warning(f"[{correlation_id}] Could not fetch fresh state for {entity_id}")
            return response
        
        entity_state = state_result.get('data', {})
        
        # Build context.properties from fresh state
        properties = _build_context_properties(entity_id, entity_state, correlation_id)
        
        if not properties:
            log_debug(f"[{correlation_id}] No properties built for {entity_id}")
            return response
        
        # Ensure response has context structure
        if 'context' not in response:
            response['context'] = {}
        
        # Replace/add properties with fresh state
        response['context']['properties'] = properties
        
        log_debug(f"[{correlation_id}] Added {len(properties)} properties to context")
        
        return response
        
    except Exception as e:
        log_error(f"[{correlation_id}] State enrichment error: {str(e)}")
        return response


def _build_context_properties(entity_id: str, entity_state: Dict[str, Any], 
                              correlation_id: str) -> list:
    """
    Build Alexa context.properties from HA entity state.
    
    Args:
        entity_id: Entity ID
        entity_state: HA entity state
        correlation_id: Correlation ID for logging
        
    Returns:
        List of Alexa property objects
    """
    properties = []
    
    try:
        state = entity_state.get('state', '').lower()
        attributes = entity_state.get('attributes', {})
        domain = entity_id.split('.')[0] if '.' in entity_id else 'unknown'
        
        # Current timestamp
        now = datetime.now(timezone.utc).isoformat()
        
        # Power state (for lights, switches, etc.)
        if domain in ['light', 'switch', 'fan']:
            power_value = 'ON' if state == 'on' else 'OFF'
            properties.append({
                'namespace': 'Alexa.PowerController',
                'name': 'powerState',
                'value': power_value,
                'timeOfSample': now,
                'uncertaintyInMilliseconds': 500
            })
        
        # Brightness (for dimmable lights)
        if domain == 'light' and 'brightness' in attributes:
            # HA brightness: 0-255, Alexa: 0-100
            brightness_255 = attributes.get('brightness', 0)
            brightness_100 = int((brightness_255 / 255) * 100)
            
            properties.append({
                'namespace': 'Alexa.BrightnessController',
                'name': 'brightness',
                'value': brightness_100,
                'timeOfSample': now,
                'uncertaintyInMilliseconds': 500
            })
        
        # Color temperature (for lights)
        if domain == 'light' and 'color_temp' in attributes:
            properties.append({
                'namespace': 'Alexa.ColorTemperatureController',
                'name': 'colorTemperatureInKelvin',
                'value': attributes.get('color_temp', 2700),
                'timeOfSample': now,
                'uncertaintyInMilliseconds': 500
            })
        
        # Contact sensor
        if domain == 'binary_sensor' and attributes.get('device_class') == 'door':
            contact_value = 'DETECTED' if state == 'on' else 'NOT_DETECTED'
            properties.append({
                'namespace': 'Alexa.ContactSensor',
                'name': 'detectionState',
                'value': contact_value,
                'timeOfSample': now,
                'uncertaintyInMilliseconds': 500
            })
        
        # Temperature
        if domain == 'climate':
            if 'current_temperature' in attributes:
                properties.append({
                    'namespace': 'Alexa.TemperatureSensor',
                    'name': 'temperature',
                    'value': {
                        'value': attributes.get('current_temperature'),
                        'scale': 'FAHRENHEIT'  # or CELSIUS based on HA config
                    },
                    'timeOfSample': now,
                    'uncertaintyInMilliseconds': 500
                })
            
            if 'temperature' in attributes:
                properties.append({
                    'namespace': 'Alexa.ThermostatController',
                    'name': 'targetSetpoint',
                    'value': {
                        'value': attributes.get('temperature'),
                        'scale': 'FAHRENHEIT'
                    },
                    'timeOfSample': now,
                    'uncertaintyInMilliseconds': 500
                })
        
        log_debug(f"[{correlation_id}] Built {len(properties)} properties for {entity_id}")
        
    except Exception as e:
        log_error(f"[{correlation_id}] Property building error: {str(e)}")
    
    return properties


def _create_error_response(header: Dict[str, Any], error_type: str,
                          error_message: str) -> Dict[str, Any]:
    """Create Alexa error response using template."""
    return render_template(
        ALEXA_ERROR_RESPONSE,
        correlation_token=header.get('correlationToken', ''),
        error_type=error_type,
        error_message=error_message
    )


def _filter_discovery_response(response: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Filter discovery response to remove invalid capability combinations."""
    try:
        endpoints = response.get('event', {}).get('payload', {}).get('endpoints', [])
        
        if not endpoints:
            return response
        
        log_debug(f"[{correlation_id}] Filtering {len(endpoints)} endpoints")
        
        filtered_endpoints = []
        filtered_count = 0
        
        for endpoint in endpoints:
            filtered_endpoint = _filter_endpoint_capabilities(endpoint, correlation_id)
            filtered_endpoints.append(filtered_endpoint)
            
            # Track if filtering occurred
            orig_caps = len(endpoint.get('capabilities', []))
            new_caps = len(filtered_endpoint.get('capabilities', []))
            if new_caps < orig_caps:
                filtered_count += 1
        
        # Update response with filtered endpoints
        response['event']['payload']['endpoints'] = filtered_endpoints
        
        if filtered_count > 0:
            log_info(f"[{correlation_id}] Filtered capabilities on {filtered_count} devices")
            increment_counter('alexa_discovery_filtered', filtered_count)
        
        return response
        
    except Exception as e:
        log_error(f"[{correlation_id}] Filtering error: {e}")
        increment_counter('alexa_discovery_filter_error')
        return response


def _filter_endpoint_capabilities(endpoint: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Filter invalid capability combinations for single endpoint."""
    try:
        capabilities = endpoint.get('capabilities', [])
        
        if not capabilities:
            return endpoint
        
        # Check for invalid combinations
        has_power_controller = any(
            cap.get('interface') == 'Alexa.PowerController' 
            for cap in capabilities
        )
        
        has_contact_sensor = any(
            cap.get('interface') == 'Alexa.ContactSensor'
            for cap in capabilities
        )
        
        # Remove ContactSensor from power devices
        if has_power_controller and has_contact_sensor:
            friendly_name = endpoint.get('friendlyName', 'Unknown')
            log_warning(
                f"[{correlation_id}] Removing ContactSensor from power device: {friendly_name}"
            )
            
            # Filter out ContactSensor
            filtered_capabilities = [
                cap for cap in capabilities
                if cap.get('interface') != 'Alexa.ContactSensor'
            ]
            
            endpoint['capabilities'] = filtered_capabilities
            increment_counter('alexa_capability_contactsensor_removed')
        
        return endpoint
        
    except Exception as e:
        log_error(f"[{correlation_id}] Endpoint filtering error: {e}")
        return endpoint


__all__ = [
    'process_directive_impl',
    'handle_discovery_impl',
    'handle_control_impl',
    'handle_power_control_impl',
    'handle_brightness_control_impl',
    'handle_thermostat_control_impl',
    'handle_accept_grant_impl',
]

# EOF
