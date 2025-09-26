"""
home_assistant_devices.py - Home Assistant Device Control Module
Version: 2025.09.20.01
Description: Specialized device control functions using core generic functions with thin wrappers

IMPLEMENTS:
- Light control operations (thin wrappers around generic service calls)
- Switch control operations (variable-based approach)
- Climate control operations (using core generic functions)
- Cover/blind control operations (minimal code duplication)

ARCHITECTURE:
- Uses home_assistant_core generic functions for actual operations
- Provides convenience functions with device-specific parameters
- Minimizes code size through variable-based approach
- Lambda-optimized for 128MB memory limit

PRIMARY FILE: home_assistant.py (interface)
SECONDARY FILE: home_assistant_devices.py (specialized module)
"""

import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

# Import from core for generic functions
from .home_assistant_core import (
    _call_ha_service_generic,
    _get_ha_entity_state,
    _set_ha_entity_state,
    _get_ha_states_bulk
)

# ===== SECTION 1: LIGHT CONTROL FUNCTIONS =====

def turn_on_light(entity_id: str, brightness: Optional[int] = None, 
                 color: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Turn on light with optional brightness and color.
    Thin wrapper around generic service call.
    """
    try:
        # Build service data generically
        service_data = {}
        
        if brightness is not None:
            service_data["brightness"] = brightness
        
        if color is not None:
            service_data["color_name"] = color
        
        # Add any additional parameters
        service_data.update(kwargs)
        
        # Use core generic function
        return _call_ha_service_generic("light", "turn_on", entity_id, service_data)
        
    except Exception as e:
        logger.error(f"Error turning on light {entity_id}: {e}")
        return {
            "success": False,
            "entity_id": entity_id,
            "error": str(e),
            "service": "light.turn_on"
        }

def turn_off_light(entity_id: str) -> Dict[str, Any]:
    """Turn off light using generic service call."""
    return _call_ha_service_generic("light", "turn_off", entity_id)

def set_light_brightness(entity_id: str, brightness: int) -> Dict[str, Any]:
    """Set light brightness (0-255) using generic approach."""
    service_data = {"brightness": brightness}
    return _call_ha_service_generic("light", "turn_on", entity_id, service_data)

def set_light_color(entity_id: str, color: str) -> Dict[str, Any]:
    """Set light color using generic service call."""
    service_data = {"color_name": color}
    return _call_ha_service_generic("light", "turn_on", entity_id, service_data)

def toggle_light(entity_id: str) -> Dict[str, Any]:
    """Toggle light using generic service call."""
    return _call_ha_service_generic("light", "toggle", entity_id)

# ===== SECTION 2: SWITCH CONTROL FUNCTIONS =====

def turn_on_switch(entity_id: str) -> Dict[str, Any]:
    """Turn on switch using generic service call."""
    return _call_ha_service_generic("switch", "turn_on", entity_id)

def turn_off_switch(entity_id: str) -> Dict[str, Any]:
    """Turn off switch using generic service call."""
    return _call_ha_service_generic("switch", "turn_off", entity_id)

def toggle_switch(entity_id: str) -> Dict[str, Any]:
    """Toggle switch using generic service call."""
    return _call_ha_service_generic("switch", "toggle", entity_id)

# ===== SECTION 3: CLIMATE CONTROL FUNCTIONS =====

def set_temperature(entity_id: str, temperature: float, 
                   hvac_mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Set climate temperature with optional HVAC mode.
    Uses generic service call with variable parameters.
    """
    try:
        # Build service data generically
        service_data = {"temperature": temperature}
        
        if hvac_mode:
            service_data["hvac_mode"] = hvac_mode
        
        return _call_ha_service_generic("climate", "set_temperature", entity_id, service_data)
        
    except Exception as e:
        logger.error(f"Error setting temperature for {entity_id}: {e}")
        return {
            "success": False,
            "entity_id": entity_id,
            "error": str(e),
            "service": "climate.set_temperature"
        }

def set_hvac_mode(entity_id: str, hvac_mode: str) -> Dict[str, Any]:
    """Set HVAC mode using generic service call."""
    service_data = {"hvac_mode": hvac_mode}
    return _call_ha_service_generic("climate", "set_hvac_mode", entity_id, service_data)

def turn_on_climate(entity_id: str) -> Dict[str, Any]:
    """Turn on climate control using generic service call."""
    return _call_ha_service_generic("climate", "turn_on", entity_id)

def turn_off_climate(entity_id: str) -> Dict[str, Any]:
    """Turn off climate control using generic service call."""
    return _call_ha_service_generic("climate", "turn_off", entity_id)

# ===== SECTION 4: COVER/BLIND CONTROL FUNCTIONS =====

def open_cover(entity_id: str) -> Dict[str, Any]:
    """Open cover/blind using generic service call."""
    return _call_ha_service_generic("cover", "open_cover", entity_id)

def close_cover(entity_id: str) -> Dict[str, Any]:
    """Close cover/blind using generic service call."""
    return _call_ha_service_generic("cover", "close_cover", entity_id)

def stop_cover(entity_id: str) -> Dict[str, Any]:
    """Stop cover/blind using generic service call."""
    return _call_ha_service_generic("cover", "stop_cover", entity_id)

def set_cover_position(entity_id: str, position: int) -> Dict[str, Any]:
    """
    Set cover position (0-100) using generic service call.
    Uses variable-based approach for any position value.
    """
    service_data = {"position": position}
    return _call_ha_service_generic("cover", "set_cover_position", entity_id, service_data)

# ===== SECTION 5: FAN CONTROL FUNCTIONS =====

def turn_on_fan(entity_id: str, speed: Optional[str] = None) -> Dict[str, Any]:
    """
    Turn on fan with optional speed setting.
    Thin wrapper around generic service call.
    """
    service_data = {}
    if speed:
        service_data["speed"] = speed
    
    return _call_ha_service_generic("fan", "turn_on", entity_id, service_data)

def turn_off_fan(entity_id: str) -> Dict[str, Any]:
    """Turn off fan using generic service call."""
    return _call_ha_service_generic("fan", "turn_off", entity_id)

def set_fan_speed(entity_id: str, speed: str) -> Dict[str, Any]:
    """Set fan speed using generic service call."""
    service_data = {"speed": speed}
    return _call_ha_service_generic("fan", "set_speed", entity_id, service_data)

# ===== SECTION 6: BULK DEVICE OPERATIONS =====

def get_device_states(entity_ids: List[str]) -> Dict[str, Any]:
    """
    Get states for multiple devices efficiently.
    Uses core bulk operation for memory optimization.
    """
    return _get_ha_states_bulk(entity_ids)

def control_multiple_lights(entity_ids: List[str], action: str, 
                           **kwargs) -> Dict[str, Any]:
    """
    Control multiple lights with same action.
    Uses variable-based approach for any light operation.
    """
    try:
        results = {}
        
        for entity_id in entity_ids:
            if action == "turn_on":
                results[entity_id] = turn_on_light(entity_id, **kwargs)
            elif action == "turn_off":
                results[entity_id] = turn_off_light(entity_id)
            elif action == "toggle":
                results[entity_id] = toggle_light(entity_id)
            else:
                results[entity_id] = {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        # Calculate success rate
        successful = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "success": successful > 0,
            "total_devices": len(entity_ids),
            "successful_operations": successful,
            "failed_operations": len(entity_ids) - successful,
            "results": results,
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Error controlling multiple lights: {e}")
        return {
            "success": False,
            "error": str(e),
            "entity_ids": entity_ids,
            "action": action
        }

def control_multiple_switches(entity_ids: List[str], action: str) -> Dict[str, Any]:
    """
    Control multiple switches with same action.
    Generic approach for any switch operation.
    """
    try:
        results = {}
        
        for entity_id in entity_ids:
            if action == "turn_on":
                results[entity_id] = turn_on_switch(entity_id)
            elif action == "turn_off":
                results[entity_id] = turn_off_switch(entity_id)
            elif action == "toggle":
                results[entity_id] = toggle_switch(entity_id)
            else:
                results[entity_id] = {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        # Calculate success rate
        successful = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "success": successful > 0,
            "total_devices": len(entity_ids),
            "successful_operations": successful,
            "failed_operations": len(entity_ids) - successful,
            "results": results,
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Error controlling multiple switches: {e}")
        return {
            "success": False,
            "error": str(e),
            "entity_ids": entity_ids,
            "action": action
        }

# ===== SECTION 7: DEVICE STATE HELPERS =====

def is_device_on(entity_id: str) -> bool:
    """
    Check if device is on using generic state check.
    Works for lights, switches, fans, etc.
    """
    try:
        state_result = _get_ha_entity_state(entity_id)
        if state_result.get("success"):
            state = state_result.get("state", "").lower()
            return state == "on"
        return False
    except Exception:
        return False

def get_device_brightness(entity_id: str) -> Optional[int]:
    """Get device brightness if available."""
    try:
        state_result = _get_ha_entity_state(entity_id)
        if state_result.get("success"):
            attributes = state_result.get("attributes", {})
            return attributes.get("brightness")
        return None
    except Exception:
        return None

def get_device_temperature(entity_id: str) -> Optional[float]:
    """Get device temperature if available."""
    try:
        state_result = _get_ha_entity_state(entity_id)
        if state_result.get("success"):
            attributes = state_result.get("attributes", {})
            return attributes.get("current_temperature")
        return None
    except Exception:
        return None

# ===== SECTION 8: MODULE EXPORTS =====

__all__ = [
    # Light control
    'turn_on_light',
    'turn_off_light',
    'set_light_brightness',
    'set_light_color',
    'toggle_light',
    
    # Switch control
    'turn_on_switch',
    'turn_off_switch',
    'toggle_switch',
    
    # Climate control
    'set_temperature',
    'set_hvac_mode',
    'turn_on_climate',
    'turn_off_climate',
    
    # Cover control
    'open_cover',
    'close_cover',
    'stop_cover',
    'set_cover_position',
    
    # Fan control
    'turn_on_fan',
    'turn_off_fan',
    'set_fan_speed',
    
    # Bulk operations
    'get_device_states',
    'control_multiple_lights',
    'control_multiple_switches',
    
    # State helpers
    'is_device_on',
    'get_device_brightness',
    'get_device_temperature'
]

# EOF
