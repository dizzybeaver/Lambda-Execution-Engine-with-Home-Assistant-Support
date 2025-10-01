"""
home_assistant_conversation.py - Alexa Conversation Integration
Version: 2025.09.30.07
Daily Revision: Performance Optimization Phase 2

Phase 2: Consolidated cache + entity minimization

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional

from gateway import (
    log_info, log_error, log_warning,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric, increment_counter
)

from ha_common import (
    HABaseManager,
    call_ha_api,
    SingletonManager,
    get_consolidated_cache,
    set_consolidated_cache
)


class HAConversationManager(HABaseManager):
    """Manages Home Assistant conversation processing."""
    
    def __init__(self):
        super().__init__()
        self._initialized_time = time.time()
    
    def get_feature_name(self) -> str:
        return "conversation"
    
    def process(
        self,
        user_text: str,
        ha_config: Dict[str, Any],
        conversation_id: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Process conversation through Home Assistant API."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Processing conversation [{correlation_id}]", {
                "text_length": len(user_text),
                "language": language
            })
            
            cache_key = f"{hash(user_text)}_{language}"
            cache_data = get_consolidated_cache()
            conversations = cache_data.get("conversations", {})
            
            if cache_key in conversations:
                cached_response = conversations[cache_key]
                if time.time() - cached_response.get("timestamp", 0) < 300:
                    self.record_cache_hit()
                    increment_counter("conversation_cache_hits")
                    return self._create_alexa_response(cached_response.get("speech", ""))
            
            self.record_cache_miss()
            
            payload = {
                "text": user_text,
                "language": language
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            result = call_ha_api(
                endpoint="/api/conversation/process",
                ha_config=ha_config,
                method="POST",
                data=payload
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                ha_response = result.get("data", {})
                speech_text = self._extract_speech(ha_response)
                
                conversations[cache_key] = {
                    "speech": speech_text,
                    "timestamp": time.time()
                }
                cache_data["conversations"] = conversations
                set_consolidated_cache(cache_data, ttl=300)
                
                self.record_success()
                record_metric("ha_conversation_success", 1.0, {
                    "language": language,
                    "response_time_ms": processing_time
                })
                
                log_info(f"Conversation processed [{correlation_id}]", {
                    "response_time_ms": processing_time
                })
                
                return self._create_alexa_response(speech_text, conversation_id)
            else:
                self.record_failure()
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
            self.record_failure()
            log_error(f"Conversation exception [{correlation_id}]: {str(e)}")
            return self._create_alexa_error_response(
                "Sorry, an error occurred while processing your request."
            )
    
    def _extract_speech(self, ha_response: Dict[str, Any]) -> str:
        """Extract speech text from Home Assistant response."""
        response = ha_response.get("response", {})
        speech = response.get("speech", {})
        plain = speech.get("plain", {})
        return plain.get("speech", "I processed your request.")
    
    def _create_alexa_response(
        self,
        speech_text: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Alexa-formatted response."""
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
        """Create Alexa-formatted error response."""
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
    
    def get_extended_stats(self) -> Dict[str, Any]:
        """Get extended conversation statistics."""
        stats = self.get_stats()
        uptime = time.time() - self._initialized_time
        
        stats.update({
            "uptime_seconds": round(uptime, 2),
            "avg_cache_hit_rate": (
                stats["cache_hits"] / (stats["cache_hits"] + stats["cache_misses"]) * 100
                if (stats["cache_hits"] + stats["cache_misses"]) > 0 else 0.0
            )
        })
        
        return stats


def process_alexa_conversation(
    user_text: str,
    ha_config: Dict[str, Any],
    session_attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process Alexa conversation request through Home Assistant."""
    manager = SingletonManager.get_instance(HAConversationManager)
    
    conversation_id = None
    if session_attributes:
        conversation_id = session_attributes.get("conversationId")
    
    return manager.process(
        user_text=user_text,
        ha_config=ha_config,
        conversation_id=conversation_id
    )


def get_conversation_stats() -> Dict[str, Any]:
    """Get conversation processing statistics."""
    manager = SingletonManager.get_instance(HAConversationManager)
    return manager.get_extended_stats()


__all__ = [
    "process_alexa_conversation",
    "get_conversation_stats"
]
