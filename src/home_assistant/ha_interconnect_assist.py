"""
ha_interconnect_assist.py - Assist Interface Gateway
Version: 2.0.0
Date: 2025-12-02
Description: Gateway wrapper for Talk to Assist operations

MODIFIED: Use execute_ha_operation() for CR-1 pattern routing
KEPT: Input validation

Architecture:
ha_interconnect_assist.py → ha_interconnect_core → ha_interface_assist.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List
from gateway import create_error_response


def assist_send_message(message: str, context: Optional[Dict] = None, 
                       **kwargs) -> Dict[str, Any]:
    """Send message to Talk to Assist."""
    if not isinstance(message, str) or not message.strip():
        return create_error_response('Invalid message format', 'INVALID_INPUT')
    if context is not None and not isinstance(context, dict):
        return create_error_response('context must be a dictionary', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ASSIST,
        'send_message',
        message=message,
        context=context,
        **kwargs
    )


def assist_get_response(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """Get response from Assist."""
    if not isinstance(conversation_id, str) or not conversation_id:
        return create_error_response('Invalid conversation_id', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ASSIST,
        'get_response',
        conversation_id=conversation_id,
        **kwargs
    )


def assist_process_conversation(messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """Process multi-turn conversation with Assist."""
    if not isinstance(messages, list):
        return create_error_response('messages must be a list', 'INVALID_INPUT')
    if not messages:
        return create_error_response('messages cannot be empty', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ASSIST,
        'process_conversation',
        messages=messages,
        **kwargs
    )


def assist_handle_pipeline(pipeline_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Assist pipeline processing."""
    if not isinstance(pipeline_data, dict):
        return create_error_response('pipeline_data must be a dictionary', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ASSIST,
        'handle_pipeline',
        pipeline_data=pipeline_data,
        **kwargs
    )


__all__ = [
    'assist_send_message',
    'assist_get_response',
    'assist_process_conversation',
    'assist_handle_pipeline',
]
