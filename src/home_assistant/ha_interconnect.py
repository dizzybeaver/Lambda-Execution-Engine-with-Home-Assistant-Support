"""
ha_interconnect.py - Home Assistant Gateway (HA-SUGA)
Version: 1.0.0 - PHASE 1
Date: 2025-11-03
Description: Gateway layer for Home Assistant extension (equivalent to LEE's gateway.py)

PHASE 1: Setup & Structure
- Created HA gateway with lazy imports
- 18 gateway wrapper functions
- Routes to 3 HA interfaces (Alexa, Devices, Assist)
- ISP compliant (no direct core imports)

Architecture:
This is the ONLY entry point for Home Assistant operations.
All HA internal calls route through this gateway.
External calls to LEE route through LEE's gateway.py.

Pattern:
ha_interconnect.py → ha_interface_*.py → ha_*_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List

# ====================
# ALEXA INTERFACE
# ====================

def alexa_process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive.
    
    Gateway function for Alexa directive processing.
    Routes to: ha_interface_alexa.process_directive
    
    Args:
        event: Alexa directive event dictionary
        **kwargs: Additional options
        
    Returns:
        Alexa response dictionary
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.process_directive(event, **kwargs)


def alexa_handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device discovery.
    
    Gateway function for Alexa discovery.
    Routes to: ha_interface_alexa.handle_discovery
    
    Args:
        event: Alexa discovery event
        **kwargs: Additional options
        
    Returns:
        Discovery response with device list
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_discovery(event, **kwargs)


def alexa_handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device control.
    
    Gateway function for Alexa control operations.
    Routes to: ha_interface_alexa.handle_control
    
    Args:
        event: Alexa control event
        **kwargs: Additional options
        
    Returns:
        Control response
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_control(event, **kwargs)


def alexa_handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa power control (on/off).
    
    Gateway function for power control.
    Routes to: ha_interface_alexa.handle_power_control
    
    Args:
        event: Alexa power control event
        **kwargs: Additional options
        
    Returns:
        Power control response
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_power_control(event, **kwargs)


def alexa_handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa brightness control.
    
    Gateway function for brightness adjustment.
    Routes to: ha_interface_alexa.handle_brightness_control
    
    Args:
        event: Alexa brightness event
        **kwargs: Additional options
        
    Returns:
        Brightness control response
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_brightness_control(event, **kwargs)


def alexa_handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa thermostat control.
    
    Gateway function for thermostat operations.
    Routes to: ha_interface_alexa.handle_thermostat_control
    
    Args:
        event: Alexa thermostat event
        **kwargs: Additional options
        
    Returns:
        Thermostat control response
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_thermostat_control(event, **kwargs)


def alexa_handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa AcceptGrant directive.
    
    Gateway function for authorization grant.
    Routes to: ha_interface_alexa.handle_accept_grant
    
    Args:
        event: Alexa AcceptGrant event
        **kwargs: Additional options
        
    Returns:
        AcceptGrant response
        
    REF: INT-HA-01
    """
    import ha_interface_alexa
    return ha_interface_alexa.handle_accept_grant(event, **kwargs)


# ====================
# DEVICES INTERFACE
# ====================

def devices_get_states(entity_ids: Optional[List[str]] = None, 
                      use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states.
    
    Gateway function for retrieving device states.
    Routes to: ha_interface_devices.get_states
    
    Args:
        entity_ids: Optional list of specific entity IDs
        use_cache: Whether to use cached states
        **kwargs: Additional options
        
    Returns:
        States response dictionary
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.get_states(entity_ids, use_cache, **kwargs)


def devices_get_by_id(entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get specific device by entity ID.
    
    Gateway function for single device retrieval.
    Routes to: ha_interface_devices.get_by_id
    
    Args:
        entity_id: Entity ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Device state dictionary
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.get_by_id(entity_id, **kwargs)


def devices_find_fuzzy(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """
    Find device using fuzzy name matching.
    
    Gateway function for fuzzy device search.
    Routes to: ha_interface_devices.find_fuzzy
    
    Args:
        search_name: Name to search for
        threshold: Matching threshold (0.0-1.0)
        **kwargs: Additional options
        
    Returns:
        Best matching entity ID or None
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.find_fuzzy(search_name, threshold, **kwargs)


def devices_update_state(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Update device state.
    
    Gateway function for state updates.
    Routes to: ha_interface_devices.update_state
    
    Args:
        entity_id: Entity ID to update
        state_data: New state data
        **kwargs: Additional options
        
    Returns:
        Update response
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.update_state(entity_id, state_data, **kwargs)


def devices_call_service(domain: str, service: str, 
                        entity_id: Optional[str] = None,
                        service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant service.
    
    Gateway function for service calls.
    Routes to: ha_interface_devices.call_service
    
    Args:
        domain: Service domain (e.g., 'light', 'switch')
        service: Service name (e.g., 'turn_on', 'turn_off')
        entity_id: Optional target entity ID
        service_data: Optional service data
        **kwargs: Additional options
        
    Returns:
        Service call response
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.call_service(domain, service, entity_id, service_data, **kwargs)


def devices_list_by_domain(domain: str, **kwargs) -> Dict[str, Any]:
    """
    List all devices in a domain.
    
    Gateway function for domain filtering.
    Routes to: ha_interface_devices.list_by_domain
    
    Args:
        domain: Domain to filter (e.g., 'light', 'switch', 'sensor')
        **kwargs: Additional options
        
    Returns:
        List of devices in domain
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.list_by_domain(domain, **kwargs)


def devices_check_status(**kwargs) -> Dict[str, Any]:
    """
    Check Home Assistant connection status.
    
    Gateway function for status checks.
    Routes to: ha_interface_devices.check_status
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Connection status
        
    REF: INT-HA-02
    """
    import ha_interface_devices
    return ha_interface_devices.check_status(**kwargs)


# ====================
# ASSIST INTERFACE
# ====================

def assist_send_message(message: str, conversation_id: Optional[str] = None, 
                       **kwargs) -> Dict[str, Any]:
    """
    Send message to Talk to Assist.
    
    Gateway function for assist messages.
    Routes to: ha_interface_assist.send_message
    
    Args:
        message: Message text to send
        conversation_id: Optional conversation ID
        **kwargs: Additional options
        
    Returns:
        Assist response
        
    REF: INT-HA-03
    """
    import ha_interface_assist
    return ha_interface_assist.send_message(message, conversation_id, **kwargs)


def assist_get_response(message_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get response from Assist.
    
    Gateway function for retrieving assist responses.
    Routes to: ha_interface_assist.get_response
    
    Args:
        message_id: Message ID to get response for
        **kwargs: Additional options
        
    Returns:
        Assist response data
        
    REF: INT-HA-03
    """
    import ha_interface_assist
    return ha_interface_assist.get_response(message_id, **kwargs)


def assist_process_conversation(messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """
    Process multi-turn conversation with Assist.
    
    Gateway function for conversation processing.
    Routes to: ha_interface_assist.process_conversation
    
    Args:
        messages: List of conversation messages
        **kwargs: Additional options
        
    Returns:
        Conversation response
        
    REF: INT-HA-03
    """
    import ha_interface_assist
    return ha_interface_assist.process_conversation(messages, **kwargs)


def assist_handle_pipeline(pipeline_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Assist pipeline processing.
    
    Gateway function for pipeline operations.
    Routes to: ha_interface_assist.handle_pipeline
    
    Args:
        pipeline_data: Pipeline configuration and data
        **kwargs: Additional options
        
    Returns:
        Pipeline response
        
    REF: INT-HA-03
    """
    import ha_interface_assist
    return ha_interface_assist.handle_pipeline(pipeline_data, **kwargs)


# ====================
# EXPORTS
# ====================

__all__ = [
    # Alexa interface (7 functions)
    'alexa_process_directive',
    'alexa_handle_discovery',
    'alexa_handle_control',
    'alexa_handle_power_control',
    'alexa_handle_brightness_control',
    'alexa_handle_thermostat_control',
    'alexa_handle_accept_grant',
    
    # Devices interface (7 functions)
    'devices_get_states',
    'devices_get_by_id',
    'devices_find_fuzzy',
    'devices_update_state',
    'devices_call_service',
    'devices_list_by_domain',
    'devices_check_status',
    
    # Assist interface (4 functions)
    'assist_send_message',
    'assist_get_response',
    'assist_process_conversation',
    'assist_handle_pipeline',
]

# EOF
