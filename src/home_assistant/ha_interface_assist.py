"""
ha_interface_assist.py - Assist Interface Layer (INT-HA-03)
Version: 2.0.0
Date: 2025-11-04
Description: Interface layer for Talk to Assist integration

Architecture:
ha_interconnect.py → ha_interface_assist.py (THIS FILE) → ha_assist_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional


def send_message(message: str, conversation_id: Optional[str] = None,
                language: str = 'en', **kwargs) -> Dict[str, Any]:
    """
    Send message to Talk to Assist.
    
    Routes to: ha_assist_core.send_assist_message_impl
    
    Args:
        message: Message text
        conversation_id: Optional conversation ID for context
        language: Language code (default: 'en')
        **kwargs: Additional options
        
    Returns:
        Assist response
        
    REF: INT-HA-03
    """
    
    import home_assistant.ha_assist_core as ha_assist_core
    return ha_assist_core.send_assist_message_impl(message, conversation_id, language, **kwargs)


def get_response(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get response from Assist.
    
    Interface layer routing.
    Routes to: ha_assist_core.get_assist_response_impl
    
    Args:
        conversation_id: Conversation ID
        **kwargs: Additional options
        
    Returns:
        Response data
        
    REF: INT-HA-03
    """
    import home_assistant.ha_alexa_core as ha_assist_core
    return ha_assist_core.get_assist_response_impl(conversation_id, **kwargs)


def process_conversation(message: str, context: Optional[Dict] = None, 
                        **kwargs) -> Dict[str, Any]:
    """
    Process conversation with Assist.
    
    Routes to: ha_assist_core.process_assist_conversation_impl
    
    Args:
        message: User message text
        context: Optional conversation context
        **kwargs: Additional options
        
    Returns:
        Conversation response
        
    REF: INT-HA-03
    """
    import home_assistant.ha_alexa_core as ha_assist_core
    return ha_assist_core.process_assist_conversation_impl(message, context, **kwargs)


def handle_pipeline(pipeline_id: str, message: str, **kwargs) -> Dict[str, Any]:
    """
    Handle Assist pipeline.
    
    Routes to: ha_assist_core.handle_assist_pipeline_impl
    
    Args:
        pipeline_id: Pipeline/agent ID to use
        message: User message text
        **kwargs: Additional options
        
    Returns:
        Pipeline response
        
    REF: INT-HA-03
    """
    import home_assistant.ha_alexa_core as ha_assist_core
    return ha_assist_core.handle_assist_pipeline_impl(pipeline_id, message, **kwargs)


__all__ = [
    'send_message',
    'get_response',
    'process_conversation',
    'handle_pipeline',
]

# EOF
