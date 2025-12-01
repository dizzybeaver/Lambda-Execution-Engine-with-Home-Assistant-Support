# ha_interconnect_assist.py
"""
ha_interconnect_assist.py - Assist Interface Gateway
Version: 1.0.0
Date: 2025-11-05
Purpose: Gateway wrapper for Talk to Assist operations

SECURITY:
- Input validation on all functions
- Message size limits
- Type checking for parameters
- Error handling for invalid inputs

Architecture:
ha_interconnect_assist.py → ha_interface_assist.py → ha_assist_core.py

Functions: 4 Assist operations
- Send message
- Get response
- Process conversation
- Handle pipeline

Pattern:
Validates input → Routes to interface → Returns response

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List
from home.assistant.ha_interconnect_validation import _validate_message
from gateway import create_error_response


def assist_send_message(message: str, context: Optional[Dict] = None, 
                       **kwargs) -> Dict[str, Any]:
    """
    Send message to Talk to Assist.
    
    Gateway function for assist messages.
    Routes to: ha_interface_assist.send_message
    
    Args:
        message: Message text to send
        context: Optional conversation context
        **kwargs: Additional options
        
    Returns:
        Assist response
        
    Security:
        - Validates message format and length
        - Validates context is dictionary if provided
        - Prevents DoS via oversized messages
        
    REF: INT-HA-03
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_message(message):
        return create_error_response('Invalid message format', 'INVALID_INPUT')
    if context is not None and not isinstance(context, dict):
        return create_error_response('context must be a dictionary', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_assist as ha_interface_assist
    return ha_interface_assist.send_message(message, context, **kwargs)


def assist_get_response(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get response from Assist.
    
    Gateway function for retrieving assist responses.
    Routes to: ha_interface_assist.get_response
    
    Args:
        conversation_id: Conversation ID to get response for
        **kwargs: Additional options
        
    Returns:
        Assist response data
        
    Security:
        - Validates conversation_id is non-empty string
        - Prevents invalid conversation access
        
    REF: INT-HA-03
    """
    # ADDED: Input validation (CRIT-03)
    if not isinstance(conversation_id, str) or not conversation_id:
        return create_error_response('Invalid conversation_id', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_assist as ha_interface_assist
    return ha_interface_assist.get_response(conversation_id, **kwargs)


def assist_process_conversation(messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """
    Process multi-turn conversation with Assist.
    
    Gateway function for conversation processing.
    Routes to: ha_interface_assist.process_conversation
    
    Args:
        messages: List of conversation messages
        **kwargs: Additional options
        
    Returns:
        Conversation response
        
    Security:
        - Validates messages is list
        - Validates messages is non-empty
        - Prevents empty conversation processing
        
    REF: INT-HA-03
    """
    # ADDED: Input validation (CRIT-03)
    if not isinstance(messages, list):
        return create_error_response('messages must be a list', 'INVALID_INPUT')
    if not messages:
        return create_error_response('messages cannot be empty', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_assist as ha_interface_assist
    return ha_interface_assist.process_conversation(messages, **kwargs)


def assist_handle_pipeline(pipeline_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Assist pipeline processing.
    
    Gateway function for pipeline operations.
    Routes to: ha_interface_assist.handle_pipeline
    
    Args:
        pipeline_data: Pipeline configuration and data
        **kwargs: Additional options
        
    Returns:
        Pipeline response
        
    Security:
        - Validates pipeline_data is dictionary
        - Prevents invalid pipeline execution
        
    REF: INT-HA-03
    """
    # ADDED: Input validation (CRIT-03)
    if not isinstance(pipeline_data, dict):
        return create_error_response('pipeline_data must be a dictionary', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_assist as ha_interface_assist
    return ha_interface_assist.handle_pipeline(pipeline_data, **kwargs)


# ====================
# EXPORTS
# ====================

__all__ = [
    'assist_send_message',
    'assist_get_response',
    'assist_process_conversation',
    'assist_handle_pipeline',
]

# ASSIST GATEWAY WRAPPER:
# - 4 functions for Talk to Assist operations
# - Input validation via ha_interconnect_validation
# - Error responses via gateway.create_error_response
# - Routes to ha_interface_assist (interface layer)
# - Lazy imports for performance

# EOF
