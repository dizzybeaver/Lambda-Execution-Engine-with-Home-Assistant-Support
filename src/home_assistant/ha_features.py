"""
ha_features.py
Version: 2025.10.13.06
Description: Consolidated HA features using generic wrapper (Phase 3)
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

# ===== AUTOMATION OPERATIONS =====

def list_automations(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List all automations using generic wrapper."""
    def _list(config, **kwargs):
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return response
        
        states = response.get('data', [])
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
        
        return {
            'success': True,
            'data': {'automations': automations, 'count': len(automations)}
        }
    
    return ha_operation_wrapper(
        'automation', 'list', _list,
        cache_key='ha_automations', cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def trigger_automation(
    automation_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    skip_condition: bool = False
) -> Dict[str, Any]:
    """Trigger automation using generic wrapper."""
    def _trigger(config, **kwargs):
        entity_id = _resolve_automation_id(automation_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Automation not found: {automation_id}'
            }
        
        service_data = {
            'entity_id': entity_id,
            'skip_condition': skip_condition
        }
        
        result = call_ha_service('automation', 'trigger', config, entity_id, service_data)
        if result.get('success'):
            increment_counter('ha_automation_trigger')
            return {
                'success': True,
                'data': {'entity_id': entity_id, 'skip_condition': skip_condition}
            }
        return result
    
    return ha_operation_wrapper(
        'automation', 'trigger', _trigger,
        config=ha_config
    )


def toggle_automation(
    automation_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Toggle automation on/off using generic wrapper."""
    def _toggle(config, **kwargs):
        entity_id = _resolve_automation_id(automation_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Automation not found: {automation_id}'
            }
        
        result = call_ha_service('automation', 'toggle', config, entity_id)
        if result.get('success'):
            increment_counter('ha_automation_toggle')
            return {
                'success': True,
                'data': {'entity_id': entity_id}
            }
        return result
    
    return ha_operation_wrapper(
        'automation', 'toggle', _toggle,
        config=ha_config
    )


def _resolve_automation_id(automation_id: str, config: Dict[str, Any]) -> Optional[str]:
    """Resolve automation ID or name to entity ID."""
    if automation_id.startswith('automation.'):
        return automation_id
    
    automations_resp = list_automations(config)
    if not automations_resp.get('success'):
        return None
    
    automations = automations_resp.get('data', {}).get('automations', [])
    automation_id_lower = automation_id.lower()
    
    for auto in automations:
        entity_id = auto.get('entity_id', '')
        name = auto.get('name', '').lower()
        if entity_id.lower() == automation_id_lower or name == automation_id_lower:
            return entity_id
    
    names = [auto.get('name', '') for auto in automations]
    matched_name = fuzzy_match_name(automation_id, names)
    
    if matched_name:
        for auto in automations:
            if auto.get('name') == matched_name:
                return auto.get('entity_id')
    
    return None


# ===== SCRIPT OPERATIONS =====

def list_scripts(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List all scripts using generic wrapper."""
    def _list(config, **kwargs):
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return response
        
        states = response.get('data', [])
        scripts = [
            {
                'entity_id': s.get('entity_id'),
                'name': s.get('attributes', {}).get('friendly_name', s.get('entity_id')),
                'state': s.get('state'),
                'last_triggered': s.get('attributes', {}).get('last_triggered')
            }
            for s in states
            if s.get('entity_id', '').startswith('script.')
        ]
        
        return {
            'success': True,
            'data': {'scripts': scripts, 'count': len(scripts)}
        }
    
    return ha_operation_wrapper(
        'script', 'list', _list,
        cache_key='ha_scripts', cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def run_script(
    script_id: str,
    variables: Optional[Dict[str, Any]] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute script using generic wrapper."""
    def _run(config, **kwargs):
        entity_id = _resolve_script_id(script_id, config)
        if not entity_id:
            return {
                'success': False,
                'error': f'Script not found: {script_id}'
            }
        
        service_data = {'entity_id': entity_id}
        if variables:
            service_data.update(variables)
        
        result = call_ha_service('script', 'turn_on', config, entity_id, service_data)
        if result.get('success'):
            increment_counter('ha_script_execute')
            return {
                'success': True,
                'data': {'entity_id': entity_id, 'variables': variables}
            }
        return result
    
    return ha_operation_wrapper(
        'script', 'run', _run,
        config=ha_config
    )


def _resolve_script_id(script_id: str, config: Dict[str, Any]) -> Optional[str]:
    """Resolve script ID or name to entity ID."""
    if script_id.startswith('script.'):
        return script_id
    
    scripts_resp = list_scripts(config)
    if not scripts_resp.get('success'):
        return None
    
    scripts = scripts_resp.get('data', {}).get('scripts', [])
    script_id_lower = script_id.lower()
    
    for script in scripts:
        entity_id = script.get('entity_id', '')
        name = script.get('name', '').lower()
        if entity_id.lower() == script_id_lower or name == script_id_lower:
            return entity_id
    
    names = [script.get('name', '') for script in scripts]
    matched_name = fuzzy_match_name(script_id, names)
    
    if matched_name:
        for script in scripts:
            if script.get('name') == matched_name:
                return script.get('entity_id')
    
    return None


# ===== INPUT HELPER OPERATIONS =====

def list_input_helpers(
    helper_type: Optional[str] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List input helpers using generic wrapper."""
    def _list(config, **kwargs):
        domains = ['input_boolean', 'input_select', 'input_number', 'input_text']
        if helper_type:
            if helper_type not in domains:
                return {
                    'success': False,
                    'error': f'Invalid helper type: {helper_type}'
                }
            domains = [helper_type]
        
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return response
        
        states = response.get('data', [])
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
        return {
            'success': True,
            'data': {
                'helpers': all_helpers,
                'domains': domains,
                'total_count': total_count
            }
        }
    
    cache_key = f'ha_input_helpers_{helper_type or "all"}'
    return ha_operation_wrapper(
        'input_helper', 'list', _list,
        cache_key=cache_key, cache_ttl=HA_CACHE_TTL_ENTITIES,
        config=ha_config
    )


def set_input_helper(
    helper_id: str,
    value: Union[str, int, float, bool],
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Set input helper value using generic wrapper."""
    def _set(config, **kwargs):
        if not helper_id or '.' not in helper_id:
            return {
                'success': False,
                'error': 'Invalid helper ID format'
            }
        
        domain = helper_id.split('.')[0]
        
        if domain == 'input_boolean':
            result = _set_boolean_helper(helper_id, value, config)
        elif domain == 'input_select':
            result = _set_select_helper(helper_id, value, config)
        elif domain == 'input_number':
            result = _set_number_helper(helper_id, value, config)
        elif domain == 'input_text':
            result = _set_text_helper(helper_id, value, config)
        else:
            return {
                'success': False,
                'error': f'Unsupported input helper type: {domain}'
            }
        
        if result.get('success'):
            increment_counter(f'ha_input_helper_{domain}_set')
            return {
                'success': True,
                'data': {'entity_id': helper_id, 'domain': domain, 'value': value}
            }
        return result
    
    return ha_operation_wrapper(
        'input_helper', 'set', _set,
        config=ha_config
    )


def _set_boolean_helper(entity_id: str, value: Union[str, bool], config: Dict[str, Any]) -> Dict[str, Any]:
    """Set input_boolean value."""
    if isinstance(value, bool):
        service = 'turn_on' if value else 'turn_off'
    elif isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ['true', 'on', 'yes', '1']:
            service = 'turn_on'
        elif value_lower in ['false', 'off', 'no', '0']:
            service = 'turn_off'
        else:
            return {'success': False, 'error': f'Invalid boolean value: {value}'}
    else:
        return {'success': False, 'error': f'Invalid boolean value type: {type(value)}'}
    
    return call_ha_service('input_boolean', service, config, entity_id)


def _set_select_helper(entity_id: str, value: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Set input_select option."""
    service_data = {'entity_id': entity_id, 'option': str(value)}
    return call_ha_service('input_select', 'select_option', config, entity_id, service_data)


def _set_number_helper(entity_id: str, value: Union[str, int, float], config: Dict[str, Any]) -> Dict[str, Any]:
    """Set input_number value."""
    try:
        numeric_value = float(value)
    except (ValueError, TypeError):
        return {'success': False, 'error': f'Invalid numeric value: {value}'}
    
    service_data = {'entity_id': entity_id, 'value': numeric_value}
    return call_ha_service('input_number', 'set_value', config, entity_id, service_data)


def _set_text_helper(entity_id: str, value: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Set input_text value."""
    service_data = {'entity_id': entity_id, 'value': str(value)}
    return call_ha_service('input_text', 'set_value', config, entity_id, service_data)


# ===== NOTIFICATION OPERATIONS =====

def send_notification(
    message: str,
    title: Optional[str] = None,
    target: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Send notification using generic wrapper."""
    def _send(config, **kwargs):
        service_data = {'message': message}
        if title:
            service_data['title'] = title
        if data:
            service_data['data'] = data
        
        service = target if target else 'notify'
        result = call_ha_service('notify', service, config, service_data=service_data)
        
        if result.get('success'):
            increment_counter('ha_notification_sent')
            return {
                'success': True,
                'data': {'message': message, 'title': title, 'target': target}
            }
        return result
    
    return ha_operation_wrapper(
        'notification', 'send', _send,
        config=ha_config
    )


# ===== CONVERSATION OPERATIONS =====

def process_conversation(
    text: str,
    conversation_id: Optional[str] = None,
    language: Optional[str] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process conversation using generic wrapper."""
    def _process(config, **kwargs):
        service_data = {'text': text}
        if conversation_id:
            service_data['conversation_id'] = conversation_id
        if language:
            service_data['language'] = language
        
        result = call_ha_service('conversation', 'process', config, service_data=service_data)
        
        if result.get('success'):
            increment_counter('ha_conversation_processed')
            response_data = result.get('data', {})
            return {
                'success': True,
                'data': {
                    'text': text,
                    'response': response_data.get('response', {}).get('speech', {}).get('plain', {}).get('speech', ''),
                    'conversation_id': response_data.get('conversation_id')
                }
            }
        return result
    
    return ha_operation_wrapper(
        'conversation', 'process', _process,
        config=ha_config
    )


__all__ = [
    # Automation
    'list_automations',
    'trigger_automation',
    'toggle_automation',
    # Scripts
    'list_scripts',
    'run_script',
    # Input Helpers
    'list_input_helpers',
    'set_input_helper',
    # Notifications
    'send_notification',
    # Conversation
    'process_conversation',
]

# EOF
