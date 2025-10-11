"""
Home Assistant Timers - Gateway-Optimized Timer Management
Version: 2025.10.03.02
Description: Revolutionary gateway-integrated timer management with zero custom error handling

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

import time
import re
from typing import Dict, Any, Optional, Union

from gateway import (
    log_info,
    create_success_response,
    increment_counter
)

from ha_common import (
    get_ha_config,
    call_ha_service,
    get_entity_state,
    batch_get_states,
    is_ha_available,
    HA_CACHE_TTL_STATE
)


class HATimerManager:
    """Manages Home Assistant timers with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'operations': 0,
            'successes': 0,
            'failures': 0,
            'by_action': {
                'start': {'operations': 0, 'successes': 0},
                'cancel': {'operations': 0, 'successes': 0},
                'pause': {'operations': 0, 'successes': 0},
                'finish': {'operations': 0, 'successes': 0}
            }
        }
    
    def get_feature_name(self) -> str:
        return "timer"
    
    def start_timer(
        self,
        timer_id: str,
        duration: Union[str, int],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start timer with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_timer', 'start',
                                          timer_id=timer_id, duration=str(duration))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'start',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_timer_id(timer_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'start',
                    ValueError(f"Timer not found: {timer_id}"),
                    context['correlation_id']
                )
            
            duration_str = self._parse_duration(duration)
            
            service_data = {
                "entity_id": entity_id,
                "duration": duration_str
            }
            
            result = call_ha_service("timer", "start", config, entity_id, service_data)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_action']['start']['operations'] += 1
                self._stats['by_action']['start']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_timer_start')
            
            return create_success_response(
                f"Timer {entity_id} started for {duration_str}",
                {
                    'entity_id': entity_id,
                    'duration': duration_str,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_timer', 'start', e, context['correlation_id'])
    
    def cancel_timer(
        self,
        timer_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Cancel timer with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_timer', 'cancel', timer_id=timer_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'cancel',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_timer_id(timer_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'cancel',
                    ValueError(f"Timer not found: {timer_id}"),
                    context['correlation_id']
                )
            
            result = call_ha_service("timer", "cancel", config, entity_id)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_action']['cancel']['operations'] += 1
                self._stats['by_action']['cancel']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_timer_cancel')
            
            return create_success_response(
                f"Timer {entity_id} cancelled",
                {
                    'entity_id': entity_id,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_timer', 'cancel', e, context['correlation_id'])
    
    def pause_timer(
        self,
        timer_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pause timer with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_timer', 'pause', timer_id=timer_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'pause',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_timer_id(timer_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'pause',
                    ValueError(f"Timer not found: {timer_id}"),
                    context['correlation_id']
                )
            
            result = call_ha_service("timer", "pause", config, entity_id)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_action']['pause']['operations'] += 1
                self._stats['by_action']['pause']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_timer_pause')
            
            return create_success_response(
                f"Timer {entity_id} paused",
                {
                    'entity_id': entity_id,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_timer', 'pause', e, context['correlation_id'])
    
    def finish_timer(
        self,
        timer_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Finish timer with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_timer', 'finish', timer_id=timer_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'finish',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_timer_id(timer_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'finish',
                    ValueError(f"Timer not found: {timer_id}"),
                    context['correlation_id']
                )
            
            result = call_ha_service("timer", "finish", config, entity_id)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_action']['finish']['operations'] += 1
                self._stats['by_action']['finish']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_timer_finish')
            
            return create_success_response(
                f"Timer {entity_id} finished",
                {
                    'entity_id': entity_id,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_timer', 'finish', e, context['correlation_id'])
    
    def list_timers(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List timers with circuit breaker and caching."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_timer', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_timer', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_timers():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'state': state.get('state'),
                        'duration': state.get('attributes', {}).get('duration'),
                        'remaining': state.get('attributes', {}).get('remaining')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith('timer.')
                ]
            
            timers = cache_operation_result(
                operation_name="list_timers",
                func=_get_timers,
                ttl=HA_CACHE_TTL_STATE,
                cache_key_prefix="ha_timers"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(timers)} timers",
                {
                    'timers': timers,
                    'count': len(timers)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_timer', 'list', e, context['correlation_id'])
    
    def _parse_duration(self, duration: Union[str, int]) -> str:
        """Parse duration into HH:MM:SS format."""
        if isinstance(duration, int):
            return f"00:{duration:02d}:00"
        
        duration_str = str(duration)
        
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 3:
                return duration_str
            elif len(parts) == 2:
                return f"00:{duration_str}"
        
        text_match = re.match(r'(\d+)\s*(hour|minute|second|min|sec|hr|h|m|s)s?', duration_str, re.IGNORECASE)
        if text_match:
            value = int(text_match.group(1))
            unit = text_match.group(2).lower()
            
            if unit in ['hour', 'hr', 'h']:
                return f"{value:02d}:00:00"
            elif unit in ['minute', 'min', 'm']:
                return f"00:{value:02d}:00"
            elif unit in ['second', 'sec', 's']:
                return f"00:00:{value:02d}"
        
        try:
            minutes = int(duration_str)
            return f"00:{minutes:02d}:00"
        except ValueError:
            return "00:10:00"
    
    def _resolve_timer_id(self, timer_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve timer ID to entity ID."""
        if timer_id.startswith('timer.'):
            return timer_id
        
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return None
        
        states = response.get('data', [])
        timer_id_lower = timer_id.lower()
        
        for state in states:
            entity_id = state.get('entity_id', '')
            if not entity_id.startswith('timer.'):
                continue
            
            friendly_name = state.get('attributes', {}).get('friendly_name', '').lower()
            
            if entity_id.lower() == timer_id_lower or friendly_name == timer_id_lower:
                return entity_id
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timer manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successes'] / self._stats['operations'] * 100)
                           if self._stats['operations'] > 0 else 0.0
        }


_timer_manager = HATimerManager()


def start_timer(timer_id: str, duration: Union[str, int],
               ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Start timer via manager."""
    return _timer_manager.start_timer(timer_id, duration, ha_config)


def cancel_timer(timer_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cancel timer via manager."""
    return _timer_manager.cancel_timer(timer_id, ha_config)


def pause_timer(timer_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Pause timer via manager."""
    return _timer_manager.pause_timer(timer_id, ha_config)


def finish_timer(timer_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Finish timer via manager."""
    return _timer_manager.finish_timer(timer_id, ha_config)


def list_timers(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List timers via manager."""
    return _timer_manager.list_timers(ha_config)


def get_timer_stats() -> Dict[str, Any]:
    """Get timer manager statistics."""
    return _timer_manager.get_stats()


__all__ = [
    'HATimerManager',
    'start_timer',
    'cancel_timer',
    'pause_timer',
    'finish_timer',
    'list_timers',
    'get_timer_stats',
]

# EOF
