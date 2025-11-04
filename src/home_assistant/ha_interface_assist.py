"""
ha_interface_assist.py - Assist Interface Layer (INT-HA-03)
Version: 1.0.0 - PHASE 1
Date: 2025-11-03
Description: Interface layer for Talk to Assist integration

PHASE 1: Setup & Structure
- Created Assist interface routing layer
- 4 routing functions to ha_assist_core
- Lazy imports to core layer
- ISP compliant

Architecture:
ha_interconnect.py → ha_interface_assist.py → ha_assist_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List


def send_message(message: str, conversation_id: Optional[str] = None, 
                **kwargs) -> Dict[str, Any]:
    """
    Send message to Talk to Assist.
    
    Interface layer routing.
    Routes to: ha_assist_core.send_message_impl
    
    Args:
        message: Message text
        conversation_id: Optional conversation ID
        **kwargs: Additional options
        
    Returns:
        Assist response
    """
    import ha_assist_core
    return ha_assist_core.send_message_impl(message, conversation_id, **kwargs)


def get_response(message_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get response from Assist.
    
    Interface layer routing.
    Routes to: ha_assist_core.get_response_impl
    
    Args:
        message_id: Message ID
        **kwargs: Additional options
        
    Returns:
        Response data
    """
    import ha_assist_core
    return ha_assist_core.get_response_impl(message_id, **kwargs)


def process_conversation(messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """
    Process multi-turn conversation.
    
    Interface layer routing.
    Routes to: ha_assist_core.process_conversation_impl
    
    Args:
        messages: Conversation messages
        **kwargs: Additional options
        
    Returns:
        Conversation response
    """
    import ha_assist_core
    return ha_assist_core.process_conversation_impl(messages, **kwargs)


def handle_pipeline(pipeline_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Assist pipeline.
    
    Interface layer routing.
    Routes to: ha_assist_core.handle_pipeline_impl
    
    Args:
        pipeline_data: Pipeline configuration
        **kwargs: Additional options
        
    Returns:
        Pipeline response
    """
    import ha_assist_core
    return ha_assist_core.handle_pipeline_impl(pipeline_data, **kwargs)


__all__ = [
    'send_message',
    'get_response',
    'process_conversation',
    'handle_pipeline',
]

# EOF
