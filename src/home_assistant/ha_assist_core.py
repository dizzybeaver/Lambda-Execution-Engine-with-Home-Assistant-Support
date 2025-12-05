"""
ha_assist_core.py - Assist/Conversation Core Implementation (INT-HA-03)
Version: 1.0.0
Date: 2025-11-04
Description: Core implementation for Home Assistant Assist/Conversation feature

Architecture:
ha_interconnect.py → ha_interface_assist.py → ha_assist_core.py (THIS FILE)

Functions:
- send_assist_message_impl: Send message to Assist
- get_assist_response_impl: Get response from Assist
- process_assist_conversation_impl: Process full conversation
- handle_assist_pipeline_impl: Handle pipeline-specific operations

Based on process_conversation() from ha_features.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Dict, Any, Optional

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp
)

import home_assistant.ha_interconnect as ha_interconnect

import os
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
HA_CONVERSATION_CACHE_TTL = 60  # Cache conversation responses for 1 minute
HA_SLOW_CONVERSATION_THRESHOLD_MS = 2000  # Alert if conversation > 2s

def _debug_trace(correlation_id: str, step: str, **details):
    """
    Args:
        correlation_id: Correlation ID for request tracing
        step: Step description
        **details: Additional details to log
    """
    if _DEBUG_MODE_ENABLED:
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [ASSIST-TRACE] {step}" + (f" ({detail_str})" if detail_str else ""))


def send_assist_message_impl(message: str, conversation_id: Optional[str] = None, 
                             language: str = 'en', **kwargs) -> Dict[str, Any]:
    """
    Send message to Home Assistant Assist.
    
    Core implementation for sending messages to HA Conversation API.
    
    Args:
        message: User message text
        conversation_id: Optional conversation ID for context
        language: Language code (default: 'en')
        **kwargs: Additional options
        
    Returns:
        Assist response dictionary
        
    Example:
        result = send_assist_message_impl("Turn on the living room lights")
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        _debug_trace(correlation_id, "send_assist_message START", 
                    message_length=len(message), 
                    has_conversation_id=conversation_id is not None,
                    language=language)
        
        # Validation
        if not isinstance(message, str) or not message.strip():
            increment_counter('ha_assist_invalid_message')
            return create_error_response('Message cannot be empty', 'INVALID_MESSAGE')
        
        # Build request data
        request_data = {
            'text': message.strip(),
            'language': language or 'en'
        }
        
        if conversation_id:
            request_data['conversation_id'] = conversation_id
        
        _debug_trace(correlation_id, "Calling HA conversation API")
        
        # Call HA Conversation API via devices helper
        # Use ha_interconnect to access call_ha_api_impl from devices core
        api_result = ha_interconnect.devices_call_ha_api(
            '/api/conversation/process',
            method='POST',
            data=request_data
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if duration_ms > HA_SLOW_CONVERSATION_THRESHOLD_MS:
            log_warning(f"[{correlation_id}] Slow conversation detected: {duration_ms:.2f}ms")
            increment_counter('ha_assist_slow_conversation')
        
        record_metric('ha_assist_duration_ms', duration_ms)
        
        if api_result.get('success'):
            response_data = api_result.get('data', {})
            
            # Extract conversation response
            conversation_response = response_data.get('response', {})
            speech = conversation_response.get('speech', {})
            plain_text = speech.get('plain', {}).get('speech', '')
            
            result = {
                'text': plain_text,
                'conversation_id': response_data.get('conversation_id'),
                'language': response_data.get('language', language),
                'response_type': conversation_response.get('response_type', 'unknown'),
                'card': conversation_response.get('card'),
                'data': conversation_response.get('data'),
                'duration_ms': duration_ms
            }
            
            _debug_trace(correlation_id, "send_assist_message SUCCESS", 
                        response_length=len(plain_text),
                        response_type=result['response_type'])
            
            increment_counter('ha_assist_message_success')
            record_metric('ha_assist_response_length', float(len(plain_text)))
            
            return create_success_response('Message processed', result)
        
        _debug_trace(correlation_id, "send_assist_message FAILED", 
                    error=api_result.get('error', 'Unknown'))
        increment_counter('ha_assist_message_failure')
        return api_result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(f"[{correlation_id}] Send assist message failed: {type(e).__name__}: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_assist_error')
        record_metric('ha_assist_error_duration_ms', duration_ms)
        return create_error_response(str(e), 'ASSIST_MESSAGE_FAILED')


def get_assist_response_impl(conversation_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get response from a conversation.
    
    Note: HA Conversation API is synchronous, so this is mainly for
    retrieving cached results or polling for async operations.
    
    Args:
        conversation_id: Conversation ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Conversation response or error
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    
    try:
        _debug_trace(correlation_id, "get_assist_response", 
                    conversation_id=conversation_id)
        
        # Check cache for conversation result
        cache_key = f"ha_conversation_{conversation_id}"
        cached_result = cache_get(cache_key)
        
        if cached_result:
            _debug_trace(correlation_id, "get_assist_response CACHE HIT")
            increment_counter('ha_assist_response_cache_hit')
            return create_success_response('Conversation retrieved from cache', cached_result)
        
        _debug_trace(correlation_id, "get_assist_response CACHE MISS")
        increment_counter('ha_assist_response_cache_miss')
        return create_error_response('Conversation not found', 'CONVERSATION_NOT_FOUND')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get assist response failed: {str(e)}")
        increment_counter('ha_assist_error')
        return create_error_response(str(e), 'GET_RESPONSE_FAILED')


def process_assist_conversation_impl(message: str, context: Optional[Dict] = None, 
                                     **kwargs) -> Dict[str, Any]:
    """
    Process full conversation with Assist.
    
    Core implementation for complete conversation flow. Based on
    process_conversation() from ha_features.py.
    
    Args:
        message: User message text
        context: Optional conversation context (previous messages, user info, etc.)
        **kwargs: Additional options
        
    Returns:
        Conversation result with response and metadata
        
    Example:
        result = process_assist_conversation_impl(
            "What's the temperature in the living room?",
            context={'user_id': 'user123'}
        )
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        _debug_trace(correlation_id, "process_assist_conversation START", 
                    message_length=len(message),
                    has_context=context is not None)
        
        # Extract conversation ID from context if available
        conversation_id = None
        language = 'en'
        
        if context and isinstance(context, dict):
            conversation_id = context.get('conversation_id')
            language = context.get('language', 'en')
        
        # Send message to Assist
        _debug_trace(correlation_id, "Sending message to Assist")
        result = send_assist_message_impl(
            message=message,
            conversation_id=conversation_id,
            language=language
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            response_data = result.get('data', {})
            
            # Cache conversation result for quick retrieval
            new_conversation_id = response_data.get('conversation_id')
            if new_conversation_id:
                cache_key = f"ha_conversation_{new_conversation_id}"
                cache_set(cache_key, response_data, ttl=HA_CONVERSATION_CACHE_TTL)
                _debug_trace(correlation_id, "Cached conversation result", 
                            conversation_id=new_conversation_id)
            
            # Add processing metadata
            response_data['processing_time_ms'] = duration_ms
            response_data['timestamp'] = get_timestamp()
            
            _debug_trace(correlation_id, "process_assist_conversation SUCCESS", 
                        total_duration_ms=duration_ms)
            
            increment_counter('ha_assist_conversation_success')
            record_metric('ha_assist_conversation_duration_ms', duration_ms)
            
            return create_success_response('Conversation processed', response_data)
        
        _debug_trace(correlation_id, "process_assist_conversation FAILED")
        increment_counter('ha_assist_conversation_failure')
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(f"[{correlation_id}] Process conversation failed: {type(e).__name__}: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_assist_error')
        record_metric('ha_assist_error_duration_ms', duration_ms)
        return create_error_response(str(e), 'CONVERSATION_PROCESSING_FAILED')


def handle_assist_pipeline_impl(pipeline_id: str, message: str, **kwargs) -> Dict[str, Any]:
    """
    Handle pipeline-specific conversation operations.
    
    Allows using specific conversation pipelines (if HA has multiple
    configured conversation agents/pipelines).
    
    Args:
        pipeline_id: Pipeline/agent ID to use
        message: User message text
        **kwargs: Additional options
        
    Returns:
        Pipeline conversation result
        
    REF: INT-HA-03
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        _debug_trace(correlation_id, "handle_assist_pipeline START", 
                    pipeline_id=pipeline_id,
                    message_length=len(message))
        
        # Validation
        if not isinstance(pipeline_id, str) or not pipeline_id.strip():
            return create_error_response('Pipeline ID cannot be empty', 'INVALID_PIPELINE_ID')
        
        if not isinstance(message, str) or not message.strip():
            return create_error_response('Message cannot be empty', 'INVALID_MESSAGE')
        
        # Build request with pipeline specification
        request_data = {
            'text': message.strip(),
            'pipeline_id': pipeline_id.strip()
        }
        
        _debug_trace(correlation_id, "Calling HA conversation API with pipeline")
        
        # Call HA Conversation API with pipeline ID
        api_result = ha_interconnect.devices_call_ha_api(
            '/api/conversation/process',
            method='POST',
            data=request_data
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if duration_ms > HA_SLOW_CONVERSATION_THRESHOLD_MS:
            log_warning(f"[{correlation_id}] Slow pipeline conversation: {duration_ms:.2f}ms")
            increment_counter('ha_assist_pipeline_slow')
        
        record_metric('ha_assist_pipeline_duration_ms', duration_ms)
        
        if api_result.get('success'):
            response_data = api_result.get('data', {})
            
            # Extract conversation response
            conversation_response = response_data.get('response', {})
            speech = conversation_response.get('speech', {})
            plain_text = speech.get('plain', {}).get('speech', '')
            
            result = {
                'text': plain_text,
                'pipeline_id': pipeline_id,
                'conversation_id': response_data.get('conversation_id'),
                'response_type': conversation_response.get('response_type', 'unknown'),
                'duration_ms': duration_ms
            }
            
            _debug_trace(correlation_id, "handle_assist_pipeline SUCCESS", 
                        response_type=result['response_type'])
            
            increment_counter('ha_assist_pipeline_success')
            increment_counter(f'ha_assist_pipeline_{pipeline_id}_success')
            
            return create_success_response('Pipeline conversation processed', result)
        
        _debug_trace(correlation_id, "handle_assist_pipeline FAILED")
        increment_counter('ha_assist_pipeline_failure')
        return api_result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(f"[{correlation_id}] Handle pipeline failed: {type(e).__name__}: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_assist_error')
        record_metric('ha_assist_pipeline_error_duration_ms', duration_ms)
        return create_error_response(str(e), 'PIPELINE_OPERATION_FAILED')


__all__ = [
    'send_assist_message_impl',
    'get_assist_response_impl',
    'process_assist_conversation_impl',
    'handle_assist_pipeline_impl'
]

# EOF
