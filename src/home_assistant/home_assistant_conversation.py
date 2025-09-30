"""
home_assistant_conversation.py - Alexa Conversation Integration
Version: 2025.09.30.01
Daily Revision: 001

Alexa Custom Skill integration for Home Assistant Conversation API
Allows voice conversation with Home Assistant AI through Alexa

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant

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
from dataclasses import dataclass

from gateway import (
    log_info, log_error, log_warning, log_debug,
    make_post_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric, increment_counter,
    cache_get, cache_set
)


@dataclass
class ConversationStats:
    """Statistics for conversation processing."""
    total_conversations: int = 0
    successful_conversations: int = 0
    failed_conversations: int = 0
    avg_response_time_ms: float = 0.0
    last_conversation_time: float = 0.0


class HAConversationProcessor:
    """Processes Alexa conversations through Home Assistant."""
    
    def __init__(self):
        self._stats = ConversationStats()
        self._initialized_time = time.time()
    
    def process_conversation(self, 
                           user_text: str,
                           ha_config: Dict[str, Any],
                           conversation_id: Optional[str] = None,
                           language: str = "en") -> Dict[str, Any]:
        """
        Process conversation through Home Assistant API.
        
        Args:
            user_text: User's spoken text from Alexa
            ha_config: Home Assistant configuration
            conversation_id: Optional conversation ID for context
            language: Language code
            
        Returns:
            Dict with Alexa response structure
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Processing conversation [{correlation_id}]", {
                "text_length": len(user_text),
                "language": language
            })
            
            cache_key = f"conversation_{hash(user_text)}_{language}"
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"Using cached conversation response [{correlation_id}]")
                increment_counter("conversation_cache_hits")
                return self._create_alexa_response(cached.get("speech", ""))
            
            payload = {
                "text": user_text,
                "language": language
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            url = f"{ha_config['base_url']}/api/conversation/process"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                ha_response = result.get("response", {})
                speech_text = self._extract_speech_from_response(ha_response)
                
                cache_set(cache_key, {"speech": speech_text}, ttl=300)
                
                self._update_stats(True, processing_time)
                
                record_metric("ha_conversation_success", 1.0, {
                    "language": language,
                    "response_time_ms": processing_time
                })
                
                log_info(f"Conversation processed successfully [{correlation_id}]", {
                    "response_time_ms": processing_time
                })
                
                return self._create_alexa_response(speech_text, conversation_id)
            else:
                self._update_stats(False, processing_time)
                error_msg = result.get("error", "Unknown error")
                
                log_error(f"Conversation failed [{correlation_id}]", {
                    "error": error_msg
                })
                
                record_metric("ha_conversation_failure", 1.0, {
                    "error_type": "ha_api_error"
                })
                
                return self._create_alexa_error_response(
                    "Sorry, I couldn't process your request with Home Assistant."
                )
                
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(False, processing_time)
            
            log_error(f"Conversation exception [{correlation_id}]", {
                "error": str(e)
            })
            
            record_metric("ha_conversation_exception", 1.0, {
                "error_type": type(e).__name__
            })
            
            return self._create_alexa_error_response(
                "Sorry, I encountered an error processing your request."
            )
    
    def _extract_speech_from_response(self, ha_response: Dict[str, Any]) -> str:
        """Extract speech text from Home Assistant conversation response."""
        try:
            response_data = ha_response.get("response", {})
            
            if isinstance(response_data, dict):
                speech = response_data.get("speech", {})
                
                if isinstance(speech, dict):
                    return speech.get("plain", {}).get("speech", "No response available.")
                elif isinstance(speech, str):
                    return speech
            
            if "speech" in ha_response:
                return str(ha_response["speech"])
            
            return "Home Assistant processed your request."
            
        except Exception as e:
            log_warning(f"Error extracting speech: {e}")
            return "Response received from Home Assistant."
    
    def _create_alexa_response(self, 
                              speech_text: str,
                              conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create Alexa custom skill response."""
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": speech_text
                },
                "shouldEndSession": False
            }
        }
        
        if conversation_id:
            response["sessionAttributes"] = {
                "conversationId": conversation_id
            }
        
        return response
    
    def _create_alexa_error_response(self, error_text: str) -> Dict[str, Any]:
        """Create Alexa error response."""
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": error_text
                },
                "shouldEndSession": True
            }
        }
    
    def _update_stats(self, success: bool, processing_time_ms: float) -> None:
        """Update conversation statistics."""
        self._stats.total_conversations += 1
        self._stats.last_conversation_time = time.time()
        
        if success:
            self._stats.successful_conversations += 1
        else:
            self._stats.failed_conversations += 1
        
        if self._stats.total_conversations > 0:
            current_avg = self._stats.avg_response_time_ms
            new_avg = ((current_avg * (self._stats.total_conversations - 1)) + 
                      processing_time_ms) / self._stats.total_conversations
            self._stats.avg_response_time_ms = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation processing statistics."""
        uptime = time.time() - self._initialized_time
        
        return {
            "total_conversations": self._stats.total_conversations,
            "successful_conversations": self._stats.successful_conversations,
            "failed_conversations": self._stats.failed_conversations,
            "avg_response_time_ms": round(self._stats.avg_response_time_ms, 2),
            "success_rate": (
                self._stats.successful_conversations / self._stats.total_conversations * 100
                if self._stats.total_conversations > 0 else 0.0
            ),
            "uptime_seconds": round(uptime, 2),
            "last_conversation_age_seconds": (
                round(time.time() - self._stats.last_conversation_time, 2)
                if self._stats.last_conversation_time > 0 else None
            )
        }


_conversation_processor: Optional[HAConversationProcessor] = None


def _get_conversation_processor() -> HAConversationProcessor:
    """Get or create conversation processor singleton."""
    global _conversation_processor
    if _conversation_processor is None:
        _conversation_processor = HAConversationProcessor()
        log_info("Conversation processor initialized")
    return _conversation_processor


def process_alexa_conversation(user_text: str,
                               ha_config: Dict[str, Any],
                               session_attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process Alexa conversation request through Home Assistant.
    
    Args:
        user_text: User's spoken text from Alexa
        ha_config: Home Assistant configuration
        session_attributes: Optional Alexa session attributes
        
    Returns:
        Alexa custom skill response
    """
    processor = _get_conversation_processor()
    
    conversation_id = None
    if session_attributes:
        conversation_id = session_attributes.get("conversationId")
    
    return processor.process_conversation(
        user_text=user_text,
        ha_config=ha_config,
        conversation_id=conversation_id
    )


def get_conversation_stats() -> Dict[str, Any]:
    """Get conversation processing statistics."""
    processor = _get_conversation_processor()
    return processor.get_stats()


__all__ = [
    'HAConversationProcessor',
    'process_alexa_conversation',
    'get_conversation_stats'
]
