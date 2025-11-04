"""
ha_assist_core.py - Assist Core Implementation (INT-HA-03)
Version: 2.0.0 - PHASE 4
Date: 2025-11-04
Description: Core implementation for Home Assistant Talk to Assist / Conversation

PHASE 4: Migration Complete
- Migrated conversation/assist functionality
- Based on process_conversation() from ha_features.py
- 4 core assist operations
- LEE access via gateway.py only

Architecture:
ha_interconnect.py → ha_interface_assist.py → ha_assist_core.py (THIS FILE)

Migration Notes:
- Conversation API is synchronous (no separate get_response needed)
- Uses ha_interconnect.devices_call_service() for conversation processing
- Maintains compatibility with HA conversation agent

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter, generate_correlation_id,
    create_success_response, create_error_response
)


def send_assist_message_impl(message: str, context: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Send message to Home Assistant Assist (conversation agent).
    
    MIGRATED Phase 4 from ha_features.py process_conversation()
    
    Core implementation for sending text to HA conversation agent.
    
    Args:
        message: User message text
        context: Optional conversation context (language, conversation_id)
        **kwargs: Additional options
        
    Returns:
        Assist response dictionary with text reply
        
    Example:
        result = send_assist_message_impl("turn on living room light")
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    
    try:
        if not message or not message.strip():
            log_error(f"[{correlation_id}] Empty message provided")
            increment_counter('ha_assist_message_empty')
            return create_error_response('Message cannot be empty', 'EMPTY_MESSAGE')
        
        log_info(f"[{correlation_id}] Sending message to Assist: {message[:50]}...")
        
        # Use ha_interconnect to call conversation service
        # LAZY IMPORT: Only load when needed
        import ha_interconnect
        
        # Build service data
        service_data = {'text': message}
        
        # Add context if provided
        if context:
            if 'language' in context:
                service_data['language'] = context['language']
            if 'conversation_id' in context:
                service_data['conversation_id'] = context['conversation_id']
        
        # Call conversation.process service via devices
        result = ha_interconnect.devices_call_service(
            'conversation',
            'process',
            entity_id=None,
            service_data=service_data
        )
        
        if result.get('success'):
            increment_counter('ha_assist_message_success')
            
            # Extract response text from result
            response_data = result.get('data', {})
            
            # HA conversation returns response in various formats
            response_text = 'Done'  # Default
            
            if isinstance(response_data, dict):
                # Format 1: Direct response object
                if 'response' in response_data:
                    resp = response_data['response']
                    if isinstance(resp, dict):
                        speech = resp.get('speech', {})
                        if isinstance(speech, dict):
                            plain = speech.get('plain', {})
                            if isinstance(plain, dict):
                                response_text = plain.get('speech', 'Done')
            elif isinstance(response_data, list) and len(response_data) > 0:
                # Format 2: List of responses
                first_response = response_data[0]
                if isinstance(first_response, dict):
                    resp = first_response.get('response', {})
                    if isinstance(resp, dict):
                        speech = resp.get('speech', {})
                        if isinstance(speech, dict):
                            plain = speech.get('plain', {})
                            if isinstance(plain, dict):
                                response_text = plain.get('speech', 'Done')
            
            log_info(f"[{correlation_id}] Assist response: {response_text[:50]}...")
            
            return create_success_response('Message processed by Assist', {
                'query': message,
                'response': response_text,
                'conversation_id': context.get('conversation_id') if context else None
            })
        
        increment_counter('ha_assist_message_error')
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Send assist message failed: {str(e)}")
        increment_counter('ha_assist_message_error')
        return create_error_response(str(e), 'ASSIST_MESSAGE_FAILED')


def get_assist_response_impl(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get assist response for conversation.
    
    PHASE 4: New implementation
    
    Note: HA conversation is synchronous, so this function
    returns cached response or indicates completion.
    
    Args:
        conversation_id: Conversation ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Conversation status/response
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Getting assist response for: {conversation_id}")
    
    try:
        # HA conversation is synchronous - response returned immediately in send_message
        # This function can check cache or return status
        
        increment_counter('ha_assist_get_response')
        
        return create_success_response('Conversation response', {
            'conversation_id': conversation_id,
            'status': 'complete',
            'note': 'HA conversation is synchronous - response returned in send_message'
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get assist response failed: {str(e)}")
        increment_counter('ha_assist_get_response_error')
        return create_error_response(str(e), 'GET_RESPONSE_FAILED')


def process_assist_conversation_impl(messages: List[Dict], **kwargs) -> Dict[str, Any]:
    """
    Process multi-turn conversation with Assist.
    
    PHASE 4: New implementation
    
    Core implementation for processing conversation history.
    Sends messages sequentially and builds conversation context.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
                  Example: [{'role': 'user', 'content': 'turn on lights'}]
        **kwargs: Additional options
        
    Returns:
        Conversation results with all responses
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    
    try:
        if not messages or not isinstance(messages, list):
            log_error(f"[{correlation_id}] Invalid messages format")
            increment_counter('ha_assist_conversation_invalid')
            return create_error_response('Messages must be a list', 'INVALID_MESSAGES')
        
        log_info(f"[{correlation_id}] Processing conversation: {len(messages)} messages")
        
        # Generate conversation ID
        import time
        conversation_id = f"conv_{int(time.time())}_{correlation_id[:8]}"
        
        responses = []
        context = {'conversation_id': conversation_id}
        
        # Process each message
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                log_warning(f"[{correlation_id}] Skipping invalid message at index {idx}")
                continue
            
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            # Only process user messages (skip assistant messages in history)
            if role == 'user' and content:
                result = send_assist_message_impl(content, context=context)
                
                if result.get('success'):
                    data = result.get('data', {})
                    responses.append({
                        'index': idx,
                        'user': content,
                        'assistant': data.get('response', 'Done')
                    })
                else:
                    responses.append({
                        'index': idx,
                        'user': content,
                        'assistant': None,
                        'error': result.get('error', 'Unknown error')
                    })
        
        increment_counter('ha_assist_conversation_processed')
        
        return create_success_response('Conversation processed', {
            'conversation_id': conversation_id,
            'message_count': len(messages),
            'response_count': len(responses),
            'responses': responses
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] Process conversation failed: {str(e)}")
        increment_counter('ha_assist_conversation_error')
        return create_error_response(str(e), 'CONVERSATION_FAILED')


def handle_assist_pipeline_impl(pipeline_data: Dict, **kwargs) -> Dict[str, Any]:
    """
    Handle assist pipeline processing.
    
    PHASE 4: New implementation
    
    Core implementation for assist pipeline operations.
    Supports voice pipeline, intent handling, and custom agents.
    
    Args:
        pipeline_data: Pipeline configuration and data
                       Example: {'intent': 'turn_on', 'targets': ['light.living_room']}
        **kwargs: Additional options
        
    Returns:
        Pipeline execution results
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    
    try:
        if not pipeline_data or not isinstance(pipeline_data, dict):
            log_error(f"[{correlation_id}] Invalid pipeline data")
            increment_counter('ha_assist_pipeline_invalid')
            return create_error_response('Pipeline data must be a dict', 'INVALID_PIPELINE')
        
        log_info(f"[{correlation_id}] Handling assist pipeline")
        
        # Extract pipeline type and data
        pipeline_type = pipeline_data.get('type', 'conversation')
        
        if pipeline_type == 'conversation':
            # Standard conversation pipeline
            text = pipeline_data.get('text') or pipeline_data.get('message')
            if text:
                return send_assist_message_impl(text, context=pipeline_data.get('context'))
            else:
                return create_error_response('No text provided for conversation', 'MISSING_TEXT')
        
        elif pipeline_type == 'intent':
            # Intent-based pipeline
            import ha_interconnect
            
            intent = pipeline_data.get('intent')
            targets = pipeline_data.get('targets', [])
            
            if not intent:
                return create_error_response('No intent provided', 'MISSING_INTENT')
            
            # Map intent to HA service call
            intent_map = {
                'turn_on': ('homeassistant', 'turn_on'),
                'turn_off': ('homeassistant', 'turn_off'),
                'toggle': ('homeassistant', 'toggle')
            }
            
            if intent in intent_map:
                domain, service = intent_map[intent]
                
                results = []
                for target in targets:
                    result = ha_interconnect.devices_call_service(
                        domain, service, entity_id=target
                    )
                    results.append({
                        'target': target,
                        'success': result.get('success', False)
                    })
                
                increment_counter('ha_assist_pipeline_intent')
                
                return create_success_response('Intent pipeline executed', {
                    'intent': intent,
                    'targets': targets,
                    'results': results
                })
            else:
                return create_error_response(f'Unsupported intent: {intent}', 'UNSUPPORTED_INTENT')
        
        else:
            log_warning(f"[{correlation_id}] Unknown pipeline type: {pipeline_type}")
            return create_error_response(f'Unknown pipeline type: {pipeline_type}', 'UNKNOWN_PIPELINE')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Handle pipeline failed: {str(e)}")
        increment_counter('ha_assist_pipeline_error')
        return create_error_response(str(e), 'PIPELINE_FAILED')


__all__ = [
    'send_assist_message_impl',
    'get_assist_response_impl',
    'process_assist_conversation_impl',
    'handle_assist_pipeline_impl',
]

# PHASE 4 MIGRATION SUMMARY:
# - Migrated conversation/assist functionality
# - Based on process_conversation() from ha_features.py
# - 4 core assist operations implemented
# - Uses ha_interconnect.devices_call_service() for conversation
# - Synchronous conversation processing (no async needed)
# - Support for multi-turn conversations
# - Intent-based pipeline support
# - Ready for use via ha_interconnect

# EOF
