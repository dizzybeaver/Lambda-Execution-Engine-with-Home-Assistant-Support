"""
ha_interface_assist.py - Assist Interface Layer (INT-HA-03)
Version: 2.0.0
Date: 2025-12-02
Description: Interface layer for Talk to Assist integration

MODIFIED: Use gateway.generate_correlation_id() instead of custom
MODIFIED: Use gateway.log_*() instead of custom debug code
ADDED: DISPATCH dictionary for CR-1 pattern
ADDED: execute_assist_operation() router function

Architecture:
ha_interconnect.py → ha_interface_assist.py → ha_assist_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional


def _send_message_impl(message: str, conversation_id: Optional[str] = None, 
                      language: str = 'en', **kwargs) -> Dict[str, Any]:
    """Send message to Assist."""
    import home_assistant.ha_assist_core as ha_assist_core
    return ha_assist_core.send_assist_message_impl(message, conversation_id, language, **kwargs)


def _get_response_impl(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """Get response from Assist."""
    import home_assistant.ha_assist_core as ha_assist_core
    return ha_assist_core.get_assist_response_impl(conversation_id, **kwargs)


def _process_conversation_impl(message: str, context: Optional[Dict] = None, 
                               **kwargs) -> Dict[str, Any]:
    """Process conversation with Assist."""
    import home_assistant.ha_assist_core as ha_assist_core
    return ha_assist_core.process_assist_conversation_impl(message, context, **kwargs)


def _handle_pipeline_impl(pipeline_id: str, message: str, **kwargs) -> Dict[str, Any]:
    """Handle Assist pipeline."""
    import home_assistant.ha_assist_core as ha_assist_core
    return ha_assist_core.handle_assist_pipeline_impl(pipeline_id, message, **kwargs)


# ADDED: DISPATCH dictionary (CR-1 pattern)
DISPATCH = {
    'send_message': _send_message_impl,
    'get_response': _get_response_impl,
    'process_conversation': _process_conversation_impl,
    'handle_pipeline': _handle_pipeline_impl,
}


# ADDED: Execute operation router (CR-1 pattern)
def execute_assist_operation(operation: str, **kwargs):
    """Execute assist operation via dispatch."""
    if operation not in DISPATCH:
        raise ValueError(f"Unknown assist operation: {operation}")
    
    handler = DISPATCH[operation]
    return handler(**kwargs)


# Maintain backward compatibility
def send_message(message: str, conversation_id: Optional[str] = None,
                language: str = 'en', **kwargs) -> Dict[str, Any]:
    """Send message."""
    return _send_message_impl(message, conversation_id, language, **kwargs)


def get_response(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """Get response."""
    return _get_response_impl(conversation_id, **kwargs)


def process_conversation(message: str, context: Optional[Dict] = None, 
                        **kwargs) -> Dict[str, Any]:
    """Process conversation."""
    return _process_conversation_impl(message, context, **kwargs)


def handle_pipeline(pipeline_id: str, message: str, **kwargs) -> Dict[str, Any]:
    """Handle pipeline."""
    return _handle_pipeline_impl(pipeline_id, message, **kwargs)


__all__ = [
    'execute_assist_operation',
    'send_message',
    'get_response',
    'process_conversation',
    'handle_pipeline',
]
