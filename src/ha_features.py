"""
home_assistant/ha_features.py - Home Assistant Features
Version: 2025.10.14.01
Description: HA features (automations, scripts, conversation) using Gateway services.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, List, Optional, Union
from gateway import (
    log_info, log_error, log_debug,
    cache_get, cache_set,
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

# ===== AUTOMATION OPERATIONS =====

def list_automations(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List all automations using wrapper."""
    def _list(config, **kwargs):
        response = get_states()
        if not response.get('success'):
            return response
        
        states = response.get('data', {}).get('states', [])
        automations = [
            {
                'entity_id': s.get('entity_id'),
                'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                'state': s.get('state'),
                'last_triggered': s.get('attributes', {}).get('last_triggered')
            }
            for s in states
            if s.get('entity_id', '').startswith('automation.')
        ]
        
        return create_success_response('Automations listed', {
            'automations': automations,
            'count': len(automations)
        })
    
    return ha_operation_wrapper(
        'automation', 'list', _list,
        cache_key='ha_automations',
        cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def trigger_automation(automation_id: str, skip_condition: bool = False,
                      ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Trigger automation using wrapper."""
    def _trigger(config, **kwargs):
        entity_id = _resolve_automation_id(automation_id, config)
        if not entity_id:
            return create_error_response(f'Automation not found: {automation_id}', 
                                        'NOT_FOUND')
        
        service_data = {}
        if skip_condition:
            service_data['skip_condition'] = True
        
        result = call_service('automation', 'trigger', entity_id, service_data)
        
        if result.get('success'):
            increment_counter('ha_automation_trigger')
            return create_success_response('Automation triggered', {
                'entity_id': entity_id,
                'skip_condition': skip_condition
            })
        
        return result
    
    return ha_operation_wrapper('automation', 'trigger', _trigger, config=ha_config)


def _resolve_automation_id(automation_id: str, config: Dict[str, Any]) -> Optional[str]:
    """Resolve automation ID or name to entity ID."""
    if automation_id.startswith('automation.'):
        return automation_id
    
    automations_resp = list_automations(config)
    if not automations_resp.get('success'):
        return None
    
    automations = automations_resp.get('data', {}).get('automations', [])
    automation_id_lower = automation_id.lower()
    
    # Exact match
    for auto in automations:
        entity_id = auto.get('entity_id', '')
        name = auto.get('name', '').lower()
        if entity_id.lower() == automation_id_lower or name == automation_id_lower:
            return entity_id
    
    # Fuzzy match
    names = [a.get('name', '') for a in automations]
    matched_name = fuzzy_match_name(automation_id, names)
    
    if matched_name:
        for auto in automations:
            if auto.get('name') == matched_name:
                return auto.get('entity_id')
    
    return None


# ===== SCRIPT OPERATIONS =====

def list_scripts(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List all scripts using wrapper."""
    def _list(config, **kwargs):
        response = get_states()
        if not response.get('success'):
            return response
        
        states = response.get('data', {}).get('states', [])
        scripts = [
            {
                'entity_id': s.get('entity_id'),
                'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                'state': s.get('state')
            }
            for s in states
            if s.get('entity_id', '').startswith('script.')
        ]
        
        return create_success_response('Scripts listed', {
            'scripts': scripts,
            'count': len(scripts)
        })
    
    return ha_operation_wrapper(
        'script', 'list', _list,
        cache_key='ha_scripts',
        cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def run_script(script_id: str, variables: Optional[Dict[str, Any]] = None,
              ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute script using wrapper."""
    def _run(config, **kwargs):
        entity_id = _resolve_script_id(script_id, config)
        if not entity_id:
            return create_error_response(f'Script not found: {script_id}', 'NOT_FOUND')
        
        service_data = {}
        if variables:
            service_data.update(variables)
        
        result = call_service('script', 'turn_on', entity_id, service_data)
        
        if result.get('success'):
            increment_counter('ha_script_execute')
            return create_success_response('Script executed', {
                'entity_id': entity_id,
                'variables': variables
            })
        
        return result
    
    return ha_operation_wrapper('script', 'run', _run, config=ha_config)


def _resolve_script_id(script_id: str, config: Dict[str, Any]) -> Optional[str]:
    """Resolve script ID or name to entity ID."""
    if script_id.startswith('script.'):
        return script_id
    
    scripts_resp = list_scripts(config)
    if not scripts_resp.get('success'):
        return None
    
    scripts = scripts_resp.get('data', {}).get('scripts', [])
    script_id_lower = script_id.lower()
    
    # Exact match
    for script in scripts:
        entity_id = script.get('entity_id', '')
        name = script.get('name', '').lower()
        if entity_id.lower() == script_id_lower or name == script_id_lower:
            return entity_id
    
    # Fuzzy match
    names = [s.get('name', '') for s in scripts]
    matched_name = fuzzy_match_name(script_id, names)
    
    if matched_name:
        for script in scripts:
            if script.get('name') == matched_name:
                return script.get('entity_id')
    
    return None


# ===== INPUT HELPER OPERATIONS =====

def list_input_helpers(helper_type: Optional[str] = None,
                      ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List input helpers using wrapper."""
    def _list(config, **kwargs):
        domains = ['input_boolean', 'input_select', 'input_number', 'input_text']
        if helper_type:
            if helper_type not in domains:
                return create_error_response(f'Invalid helper type: {helper_type}',
                                            'INVALID_TYPE')
            domains = [helper_type]
        
        response = get_states()
        if not response.get('success'):
            return response
        
        states = response.get('data', {}).get('states', [])
        all_helpers = {}
        
        for domain in domains:
            all_helpers[domain] = [
                {
                    'entity_id': s.get('entity_id'),
                    'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                    'state': s.get('state')
                }
                for s in states
                if s.get('entity_id', '').startswith(f'{domain}.')
            ]
        
        total_count = sum(len(h) for h in all_helpers.values())
        return create_success_response('Input helpers listed', {
            'helpers': all_helpers,
            'domains': domains,
            'total_count': total_count
        })
    
    cache_key = f'ha_input_helpers_{helper_type or "all"}'
    return ha_operation_wrapper(
        'input_helper', 'list', _list,
        cache_key=cache_key,
        cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def set_input_helper(helper_id: str, value: Union[str, int, float, bool],
                    ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Set input helper value using wrapper."""
    def _set(config, **kwargs):
        if not helper_id or '.' not in helper_id:
            return create_error_response('Invalid helper ID format', 'INVALID_FORMAT')
        
        domain = helper_id.split('.')[0]
        
        service_map = {
            'input_boolean': 'turn_on' if value else 'turn_off',
            'input_select': 'select_option',
            'input_number': 'set_value',
            'input_text': 'set_value'
        }
        
        if domain not in service_map:
            return create_error_response(f'Unsupported helper domain: {domain}',
                                        'UNSUPPORTED_DOMAIN')
        
        service = service_map[domain]
        service_data = {}
        
        if domain == 'input_select':
            service_data['option'] = str(value)
        elif domain in ['input_number', 'input_text']:
            service_data['value'] = value
        
        result = call_service(domain, service, helper_id, service_data)
        
        if result.get('success'):
            increment_counter(f'ha_input_helper_{domain}')
            return create_success_response('Input helper set', {
                'entity_id': helper_id,
                'value': value
            })
        
        return result
    
    return ha_operation_wrapper('input_helper', 'set', _set, config=ha_config)


# ===== NOTIFICATION OPERATIONS =====

def send_notification(message: str, title: Optional[str] = None,
                     target: Optional[str] = None,
                     ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Send notification using wrapper."""
    def _send(config, **kwargs):
        service_data = {'message': message}
        
        if title:
            service_data['title'] = title
        if target:
            service_data['target'] = target
        
        result = call_service('notify', 'notify', None, service_data)
        
        if result.get('success'):
            increment_counter('ha_notification_sent')
            return create_success_response('Notification sent', {
                'message': message,
                'title': title,
                'target': target
            })
        
        return result
    
    return ha_operation_wrapper('notification', 'send', _send, config=ha_config)


# ===== CONVERSATION OPERATIONS =====

def process_conversation(query: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process conversation query using wrapper."""
    def _process(config, **kwargs):
        if not query or not query.strip():
            return create_error_response('Query cannot be empty', 'EMPTY_QUERY')
        
        service_data = {'text': query}
        result = call_service('conversation', 'process', None, service_data)
        
        if result.get('success'):
            increment_counter('ha_conversation_processed')
            
            # Extract response from result
            response_data = result.get('data', {})
            if isinstance(response_data, list) and len(response_data) > 0:
                response_text = response_data[0].get('response', {}).get('speech', {}).get('plain', {}).get('speech', 'Done')
            else:
                response_text = 'Done'
            
            return create_success_response('Conversation processed', {
                'query': query,
                'response': response_text
            })
        
        return result
    
    return ha_operation_wrapper('conversation', 'process', _process, config=ha_config)


# EOF
