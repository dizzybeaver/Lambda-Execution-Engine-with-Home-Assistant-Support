"""
home_assistant/ha_managers.py - Entity Management
Version: 2025.10.14.01
Description: Generic entity managers for devices/areas using Gateway services.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, List, Optional
from gateway import (
    log_info, log_error, log_debug,
    increment_counter,
    create_success_response, create_error_response
)
from ha_core import (
    ha_operation_wrapper,
    get_ha_config,
    call_service,
    get_states,
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES
)

# ===== GENERIC ENTITY MANAGER =====

class HAGenericManager:
    """Generic manager for HA entities."""
    
    def __init__(self, feature_name: str, domain: str):
        self.feature_name = feature_name
        self.domain = domain
        self._stats = {'operations': 0, 'successes': 0, 'failures': 0}
    
    def list_entities(self, ha_config: Optional[Dict] = None,
                     filters: Optional[Dict] = None) -> Dict[str, Any]:
        """List entities for this domain."""
        def _list(config, **kwargs):
            response = get_states()
            if not response.get('success'):
                return response
            
            states = response.get('data', {}).get('states', [])
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
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if key == 'state':
                        entities = [e for e in entities if e.get('state') == value]
                    elif key.startswith('attr_'):
                        attr_name = key[5:]
                        entities = [e for e in entities 
                                  if e.get('attributes', {}).get(attr_name) == value]
            
            return create_success_response('Entities listed', {
                'entities': entities,
                'count': len(entities)
            })
        
        cache_key = f'ha_{self.domain}_list'
        return ha_operation_wrapper(
            self.feature_name, 'list', _list,
            cache_key=cache_key,
            cache_ttl=HA_CACHE_TTL_ENTITIES,
            config=ha_config
        )
    
    def call_service(self, service: str, entity_id: str,
                    service_data: Optional[Dict] = None,
                    ha_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Call service on entity."""
        def _call(config, **kwargs):
            result = call_service(self.domain, service, entity_id, service_data)
            
            if result.get('success'):
                self._stats['successes'] += 1
                increment_counter(f'ha_{self.domain}_{service}')
                return create_success_response('Service called', {
                    'entity_id': entity_id,
                    'service': service
                })
            else:
                self._stats['failures'] += 1
            
            return result
        
        self._stats['operations'] += 1
        return ha_operation_wrapper(self.feature_name, service, _call, config=ha_config)
    
    def resolve_entity_id(self, identifier: str,
                         ha_config: Optional[Dict] = None) -> Optional[str]:
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
    
    def get_stats(self) -> Dict[str, int]:
        """Get manager statistics."""
        return self._stats.copy()


# ===== CONVENIENCE FUNCTIONS =====

def list_entities_by_domain(domain: str, filters: Optional[Dict] = None,
                           ha_config: Optional[Dict] = None) -> Dict[str, Any]:
    """List entities by domain."""
    manager = HAGenericManager(domain, domain)
    return manager.list_entities(ha_config, filters)


def manage_device(entity_id: str, action: str,
                 parameters: Optional[Dict] = None,
                 ha_config: Optional[Dict] = None) -> Dict[str, Any]:
    """Manage device (generic control)."""
    if not entity_id or '.' not in entity_id:
        return create_error_response('Invalid entity ID', 'INVALID_ENTITY')
    
    domain = entity_id.split('.')[0]
    manager = HAGenericManager('device', domain)
    
    # Map common actions to services
    action_map = {
        'on': 'turn_on',
        'off': 'turn_off',
        'toggle': 'toggle',
        'open': 'open',
        'close': 'close',
        'lock': 'lock',
        'unlock': 'unlock'
    }
    
    service = action_map.get(action.lower(), action)
    
    return manager.call_service(service, entity_id, parameters, ha_config)


def manage_area(area_name: str, action: str,
               parameters: Optional[Dict] = None,
               ha_config: Optional[Dict] = None) -> Dict[str, Any]:
    """Manage all devices in an area."""
    try:
        # Get all states to find area devices
        response = get_states()
        if not response.get('success'):
            return response
        
        states = response.get('data', {}).get('states', [])
        area_name_lower = area_name.lower()
        
        # Find entities in area
        area_entities = []
        for state in states:
            entity_area = state.get('attributes', {}).get('area_name', '').lower()
            if entity_area == area_name_lower:
                area_entities.append(state.get('entity_id'))
        
        if not area_entities:
            return create_error_response(f'No devices found in area: {area_name}',
                                        'AREA_NOT_FOUND')
        
        # Call action on all entities
        results = []
        for entity_id in area_entities:
            result = manage_device(entity_id, action, parameters, ha_config)
            results.append(result)
        
        successes = sum(1 for r in results if r.get('success'))
        
        return create_success_response('Area managed', {
            'area': area_name,
            'action': action,
            'devices_affected': len(results),
            'successes': successes,
            'failures': len(results) - successes
        })
        
    except Exception as e:
        log_error(f"Area management failed: {str(e)}")
        return create_error_response(str(e), 'AREA_MANAGEMENT_FAILED')


# EOF
