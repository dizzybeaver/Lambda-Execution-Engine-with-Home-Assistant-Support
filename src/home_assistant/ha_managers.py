"""
ha_managers.py
Version: 2025.10.13.07
Description: Generic entity managers for devices/areas/timers (Phase 4)
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

import re
from typing import Dict, Any, List, Optional, Union

from gateway import log_info, log_error, increment_counter
from ha_core import (
    ha_operation_wrapper,
    get_ha_config,
    call_ha_service,
    batch_get_states,
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES
)

# ===== GENERIC ENTITY MANAGER =====

class HAGenericManager:
    """Generic manager for HA entities - eliminates duplicate manager classes."""
    
    def __init__(self, feature_name: str, domain: str):
        """
        Initialize generic manager.
        
        Args:
            feature_name: Feature name for logging (e.g., 'device', 'timer')
            domain: HA domain (e.g., 'light', 'timer', 'area')
        """
        self.feature_name = feature_name
        self.domain = domain
        self._stats = {
            'operations': 0,
            'successes': 0,
            'failures': 0
        }
    
    def list_entities(
        self,
        ha_config: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List entities for this domain using generic wrapper."""
        def _list(config, **kwargs):
            response = batch_get_states(None, config, use_cache=True)
            if not response.get('success'):
                return response
            
            states = response.get('data', [])
            entities = [
                {
                    'entity_id': s.get('entity_id'),
                    'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                    'state': s.get('state'),
                    'attributes': s.get('attributes', {})
                }
                for s in states
                if s.get('entity_id', '').startswith(f'{self.domain}.')
            ]
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if key == 'state':
                        entities = [e for e in entities if e.get('state') == value]
                    elif key.startswith('attr_'):
                        attr_name = key[5:]
                        entities = [e for e in entities 
                                  if e.get('attributes', {}).get(attr_name) == value]
            
            return {
                'success': True,
                'data': {'entities': entities, 'count': len(entities)}
            }
        
        cache_key = f'ha_{self.domain}_list'
        return ha_operation_wrapper(
            self.feature_name, 'list', _list,
            cache_key=cache_key, cache_ttl=HA_CACHE_TTL_ENTITIES,
            config=ha_config
        )
    
    def call_service(
        self,
        service: str,
        entity_id: str,
        service_data: Optional[Dict[str, Any]] = None,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call service on entity using generic wrapper."""
        def _call(config, **kwargs):
            result = call_ha_service(
                self.domain,
                service,
                config,
                entity_id,
                service_data
            )
            
            if result.get('success'):
                self._stats['successes'] += 1
                increment_counter(f'ha_{self.domain}_{service}')
                return {
                    'success': True,
                    'data': {'entity_id': entity_id, 'service': service}
                }
            else:
                self._stats['failures'] += 1
            
            return result
        
        self._stats['operations'] += 1
        return ha_operation_wrapper(
            self.feature_name, service, _call,
            config=ha_config
        )
    
    def resolve_entity_id(
        self,
        identifier: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Resolve friendly name or partial ID to full entity_id."""
        if identifier.startswith(f'{self.domain}.'):
            return identifier
        
        entities_resp = self.list_entities(ha_config)
        if not entities_resp.get('success'):
            return None
        
        entities = entities_resp.get('data', {}).get('entities', [])
        identifier_lower = identifier.lower()
        
        # Exact match
        for entity in entities:
            entity_id = entity.get('entity_id', '')
            name = entity.get('name', '').lower()
            if entity_id.lower() == identifier_lower or name == identifier_lower:
                return entity_id
        
        # Fuzzy match
        names = [e.get('name', '') for e in entities]
        matched_name = fuzzy_match_name(identifier, names)
        
        if matched_name:
            for entity in entities:
                if entity.get('name') == matched_name:
                    return entity.get('entity_id')
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            'feature': self.feature_name,
            'domain': self.domain,
            **self._stats,
            'success_rate': (self._stats['successes'] / self._stats['operations'] * 100)
                           if self._stats['operations'] > 0 else 0.0
        }


# ===== PRE-CONFIGURED MANAGERS =====

_device_manager = HAGenericManager('device', 'light')
_area_manager = HAGenericManager('area', 'area')
_timer_manager = HAGenericManager('timer', 'timer')


# ===== DEVICE OPERATIONS =====

def list_devices(
    domain: Optional[str] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List devices, optionally filtered by domain."""
    def _list(config, **kwargs):
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return response
        
        states = response.get('data', [])
        
        # Device domains
        device_domains = ['light', 'switch', 'fan', 'climate', 'lock', 'cover', 'media_player']
        
        if domain:
            if domain not in device_domains:
                return {
                    'success': False,
                    'error': f'Invalid device domain: {domain}'
                }
            device_domains = [domain]
        
        devices = {}
        for dom in device_domains:
            devices[dom] = [
                {
                    'entity_id': s.get('entity_id'),
                    'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                    'state': s.get('state'),
                    'attributes': s.get('attributes', {})
                }
                for s in states
                if s.get('entity_id', '').startswith(f'{dom}.')
            ]
        
        total_count = sum(len(d) for d in devices.values())
        return {
            'success': True,
            'data': {
                'devices': devices,
                'domains': device_domains,
                'total_count': total_count
            }
        }
    
    cache_key = f'ha_devices_{domain or "all"}'
    return ha_operation_wrapper(
        'device', 'list', _list,
        cache_key=cache_key, cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def control_device(
    entity_id: str,
    action: str,
    params: Optional[Dict[str, Any]] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Control device using appropriate service."""
    def _control(config, **kwargs):
        if not entity_id or '.' not in entity_id:
            return {
                'success': False,
                'error': 'Invalid entity_id format'
            }
        
        domain = entity_id.split('.')[0]
        
        # Map actions to services
        action_map = {
            'turn_on': 'turn_on',
            'turn_off': 'turn_off',
            'toggle': 'toggle',
            'open': 'open_cover',
            'close': 'close_cover',
            'stop': 'stop_cover',
            'lock': 'lock',
            'unlock': 'unlock',
            'set_temperature': 'set_temperature',
            'set_hvac_mode': 'set_hvac_mode'
        }
        
        service = action_map.get(action, action)
        
        result = call_ha_service(domain, service, config, entity_id, params)
        
        if result.get('success'):
            increment_counter(f'ha_device_{action}')
            return {
                'success': True,
                'data': {'entity_id': entity_id, 'action': action, 'params': params}
            }
        return result
    
    return ha_operation_wrapper(
        'device', action, _control,
        config=ha_config
    )


def get_device_stats() -> Dict[str, Any]:
    """Get device manager statistics."""
    return _device_manager.get_stats()


# ===== AREA OPERATIONS =====

def list_areas(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List areas using generic manager."""
    return _area_manager.list_entities(ha_config)


def get_area_devices(
    area_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get devices in an area."""
    def _get_devices(config, **kwargs):
        # Get all devices
        devices_resp = list_devices(None, config)
        if not devices_resp.get('success'):
            return devices_resp
        
        devices = devices_resp.get('data', {}).get('devices', {})
        
        # Filter by area
        area_devices = {}
        for domain, domain_devices in devices.items():
            filtered = [
                d for d in domain_devices
                if d.get('attributes', {}).get('area_id') == area_id
            ]
            if filtered:
                area_devices[domain] = filtered
        
        total_count = sum(len(d) for d in area_devices.values())
        return {
            'success': True,
            'data': {
                'area_id': area_id,
                'devices': area_devices,
                'total_count': total_count
            }
        }
    
    return ha_operation_wrapper(
        'area', 'get_devices', _get_devices,
        config=ha_config
    )


def get_area_stats() -> Dict[str, Any]:
    """Get area manager statistics."""
    return _area_manager.get_stats()


# ===== TIMER OPERATIONS =====

def list_timers(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List timers using generic manager."""
    return _timer_manager.list_entities(ha_config)


def start_timer(
    timer_id: str,
    duration: Union[str, int],
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Start timer using generic wrapper."""
    def _start(config, **kwargs):
        entity_id = _timer_manager.resolve_entity_id(timer_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Timer not found: {timer_id}'
            }
        
        duration_str = _format_duration(duration)
        service_data = {
            'entity_id': entity_id,
            'duration': duration_str
        }
        
        result = call_ha_service('timer', 'start', config, entity_id, service_data)
        if result.get('success'):
            increment_counter('ha_timer_start')
            return {
                'success': True,
                'data': {'entity_id': entity_id, 'duration': duration_str}
            }
        return result
    
    return ha_operation_wrapper(
        'timer', 'start', _start,
        config=ha_config
    )


def cancel_timer(
    timer_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Cancel timer using generic wrapper."""
    def _cancel(config, **kwargs):
        entity_id = _timer_manager.resolve_entity_id(timer_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Timer not found: {timer_id}'
            }
        
        result = call_ha_service('timer', 'cancel', config, entity_id)
        if result.get('success'):
            increment_counter('ha_timer_cancel')
            return {
                'success': True,
                'data': {'entity_id': entity_id}
            }
        return result
    
    return ha_operation_wrapper(
        'timer', 'cancel', _cancel,
        config=ha_config
    )


def pause_timer(
    timer_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Pause timer using generic wrapper."""
    def _pause(config, **kwargs):
        entity_id = _timer_manager.resolve_entity_id(timer_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Timer not found: {timer_id}'
            }
        
        result = call_ha_service('timer', 'pause', config, entity_id)
        if result.get('success'):
            increment_counter('ha_timer_pause')
            return {
                'success': True,
                'data': {'entity_id': entity_id}
            }
        return result
    
    return ha_operation_wrapper(
        'timer', 'pause', _pause,
        config=ha_config
    )


def finish_timer(
    timer_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Finish timer using generic wrapper."""
    def _finish(config, **kwargs):
        entity_id = _timer_manager.resolve_entity_id(timer_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Timer not found: {timer_id}'
            }
        
        result = call_ha_service('timer', 'finish', config, entity_id)
        if result.get('success'):
            increment_counter('ha_timer_finish')
            return {
                'success': True,
                'data': {'entity_id': entity_id}
            }
        return result
    
    return ha_operation_wrapper(
        'timer', 'finish', _finish,
        config=ha_config
    )


def get_timer_stats() -> Dict[str, Any]:
    """Get timer manager statistics."""
    return _timer_manager.get_stats()


# ===== HELPER FUNCTIONS =====

def _format_duration(duration: Union[str, int]) -> str:
    """Format duration to HH:MM:SS format."""
    if isinstance(duration, int):
        return f"00:{duration:02d}:00"
    
    duration_str = str(duration)
    
    # Already in correct format
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 3:
            return duration_str
        elif len(parts) == 2:
            return f"00:{duration_str}"
    
    # Parse text format (e.g., "5 minutes", "2 hours")
    text_match = re.match(
        r'(\d+)\s*(hour|minute|second|min|sec|hr|h|m|s)s?',
        duration_str,
        re.IGNORECASE
    )
    if text_match:
        value = int(text_match.group(1))
        unit = text_match.group(2).lower()
        
        if unit in ['hour', 'hr', 'h']:
            return f"{value:02d}:00:00"
        elif unit in ['minute', 'min', 'm']:
            return f"00:{value:02d}:00"
        elif unit in ['second', 'sec', 's']:
            return f"00:00:{value:02d}"
    
    # Assume minutes if just a number
    try:
        minutes = int(duration_str)
        return f"00:{minutes:02d}:00"
    except ValueError:
        return "00:10:00"


__all__ = [
    # Generic Manager
    'HAGenericManager',
    # Devices
    'list_devices',
    'control_device',
    'get_device_stats',
    # Areas
    'list_areas',
    'get_area_devices',
    'get_area_stats',
    # Timers
    'list_timers',
    'start_timer',
    'cancel_timer',
    'pause_timer',
    'finish_timer',
    'get_timer_stats',
]

# EOF
