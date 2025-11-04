"""
ha_interface_assist.py - Assist Interface Layer (INT-HA-03)
Version: 2.0.0 - PHASE 4
Date: 2025-11-04
Description: Interface layer for Talk to Assist integration

PHASE 4: Assist Migration Complete
- Updated interface routing to match ha_assist_core implementations
- 4 routing functions correctly aligned
- Lazy imports to core layer
- ISP compliant

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
    
    UPDATED Phase 4: Interface layer routing.
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
    import ha_assist_core
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
    import ha_assist_core
    return ha_assist_core.get_assist_response_impl(conversation_id, **kwargs)


def process_conversation(message: str, context: Optional[Dict] = None, 
                        **kwargs) -> Dict[str, Any]:
    """
    Process conversation with Assist.
    
    UPDATED Phase 4: Interface layer routing.
    Routes to: ha_assist_core.process_assist_conversation_impl
    
    Args:
        message: User message text
        context: Optional conversation context
        **kwargs: Additional options
        
    Returns:
        Conversation response
        
    REF: INT-HA-03
    """
    import ha_assist_core
    return ha_assist_core.process_assist_conversation_impl(message, context, **kwargs)


def handle_pipeline(pipeline_id: str, message: str, **kwargs) -> Dict[str, Any]:
    """
    Handle Assist pipeline.
    
    UPDATED Phase 4: Interface layer routing.
    Routes to: ha_assist_core.handle_assist_pipeline_impl
    
    Args:
        pipeline_id: Pipeline/agent ID to use
        message: User message text
        **kwargs: Additional options
        
    Returns:
        Pipeline response
        
    REF: INT-HA-03
    """
    import ha_assist_core
    return ha_assist_core.handle_assist_pipeline_impl(pipeline_id, message, **kwargs)


__all__ = [
    'send_message',
    'get_response',
    'process_conversation',
    'handle_pipeline',
]

# PHASE 4 UPDATE SUMMARY:
# - Updated function signatures to match ha_assist_core implementations
# - send_message: Added conversation_id and language parameters
# - process_conversation: Changed from List[messages] to message + context
# - handle_pipeline: Changed from pipeline_data dict to pipeline_id + message
# - All routing verified correct

# EOF
