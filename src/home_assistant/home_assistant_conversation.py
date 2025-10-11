"""
home_assistant_conversation.py
Version: 2025.10.11.01
Description: Home Assistant Natural Language processing through HA Conversation API

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
from typing import Dict, Any, Optional

from gateway import (
    log_info, create_success_response, create_error_response,
    generate_correlation_id, record_metric, increment_counter
)

from ha_common import (
    HABaseManager, call_ha_api, SingletonManager, is_ha_available,
    get_ha_config, HA_CACHE_TTL_STATE
)


class HAConversationManager(HABaseManager):
    """Manages Home Assistant conversation processing with gateway integration."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_conversations': 0,
            'successful_conversations': 0,
            'failed_conversations': 0,
            'cache_hits': 0
        }
    
    def get_feature_name(self) -> str:
        return "conversation"
    
    def process(
        self,
        user_text: str,
        ha_config: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Process conversation with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_conversation', 'process',
                                          text_length=len(user_text),
                                          language=language,
                                          has_conversation_id=bool(conversation_id))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_conversation', 'process',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            cache_key = f"{user_text}_{language}_{conversation_id or 'none'}"
            
            def _process_conversation():
                endpoint = "/api/conversation/process"
                
                payload = {
                    "text": user_text,
                    "language": language
                }
                
                if conversation_id:
                    payload["conversation_id"] = conversation_id
                
                result = call_ha_api(endpoint, config, method='POST', data=payload)
                
                if not result.get('success'):
                    return result
                
                response_data = result.get('data', {})
                
                return {
                    'success': True,
                    'response': response_data.get('response', {}).get('speech', {}).get('plain', {}).get('speech', ''),
                    'conversation_id': response_data.get('conversation_id'),
                    'card': response_data.get('response', {}).get('card')
                }
            
            result = cache_operation_result(
                operation_name="conversation_process",
                func=_process_conversation,
                ttl=HA_CACHE_TTL_STATE,
                cache_key_prefix=f"ha_conversation_{cache_key}"
            )
            
            self._stats['total_conversations'] += 1
            if result.get('success'):
                self._stats['successful_conversations'] += 1
            else:
                self._stats['failed_conversations'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_conversation_process')
            
            return result
            
        except Exception as e:
            self._stats['failed_conversations'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_conversation', 'process', e, context['correlation_id'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics with extended metrics."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        
        if self._stats['total_conversations'] > 0:
            base_stats['success_rate'] = (
                self._stats['successful_conversations'] / self._stats['total_conversations'] * 100
            )
            base_stats['cache_hit_rate'] = (
                self._stats['cache_hits'] / self._stats['total_conversations'] * 100
            )
        
        return base_stats


_singleton_manager = SingletonManager()


def get_conversation_manager() -> HAConversationManager:
    """Get or create conversation manager singleton."""
    return _singleton_manager.get_or_create(
        'conversation_manager',
        HAConversationManager
    )


def process_alexa_conversation(
    user_text: str,
    ha_config: Optional[Dict[str, Any]] = None,
    session_attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process Alexa conversation with Alexa-specific formatting."""
    from shared_utilities import (
        create_operation_context, close_operation_context, handle_operation_error
    )
    
    context = create_operation_context('ha_conversation', 'alexa_process',
                                      text_length=len(user_text))
    
    try:
        conversation_id = session_attributes.get('conversation_id') if session_attributes else None
        
        manager = get_conversation_manager()
        result = manager.process(
            user_text=user_text,
            ha_config=ha_config,
            conversation_id=conversation_id,
            language='en'
        )
        
        if not result.get('success'):
            close_operation_context(context, success=False)
            return create_error_response(
                "Conversation processing failed",
                {'result': result}
            )
        
        alexa_response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': result.get('response', 'I could not process that request.')
                },
                'shouldEndSession': False
            },
            'sessionAttributes': {
                'conversation_id': result.get('conversation_id')
            }
        }
        
        close_operation_context(context, success=True)
        
        return create_success_response(
            "Conversation processed successfully",
            {'alexa_response': alexa_response}
        )
        
    except Exception as e:
        close_operation_context(context, success=False)
        return handle_operation_error('ha_conversation', 'alexa_process', e, context['correlation_id'])


def get_conversation_stats() -> Dict[str, Any]:
    """Get conversation processing statistics."""
    manager = get_conversation_manager()
    return manager.get_stats()


def cleanup_conversation() -> Dict[str, Any]:
    """Cleanup conversation manager resources."""
    try:
        _singleton_manager.cleanup('conversation_manager')
        return create_success_response("Conversation manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'HAConversationManager',
    'get_conversation_manager',
    'process_alexa_conversation',
    'get_conversation_stats',
    'cleanup_conversation'
]
