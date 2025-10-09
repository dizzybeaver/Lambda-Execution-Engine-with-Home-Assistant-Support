"""
Lambda Function Handler - Main Entry Point
Version: 2025.10.07.04
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug, log_warning,
    validate_request, validate_token,
    cache_get, cache_set,
    record_metric, increment_counter,
    format_response,
    get_gateway_stats,
    initialize_lambda
)
from usage_analytics import record_request_usage, get_usage_summary


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler using Revolutionary Gateway Architecture.
    
    Handles:
    - Alexa Smart Home skill requests (directives)
    - Alexa Custom Skill requests (intents)
    - Health checks and analytics
    - Diagnostic endpoint
    """
    
    try:
        log_info("Lambda invocation started", context={"request_id": context.aws_request_id})
        increment_counter("lambda_invocations")
        
        request_type = _determine_request_type(event)
        log_debug(f"Processing request type: {request_type}")
        
        if not validate_request(event):
            log_error("Request validation failed")
            increment_counter("validation_failures")
            return format_response(400, {"error": "Invalid request"})
        
        if 'token' in event:
            if not validate_token(event['token']):
                log_error("Token validation failed")
                increment_counter("auth_failures")
                return format_response(401, {"error": "Unauthorized"})
        
        result = process_request(event, context, request_type)
        
        log_info("Request processed successfully")
        increment_counter("successful_requests")
        
        gateway_stats = get_gateway_stats()
        record_request_usage(
            loaded_modules=gateway_stats.get('loaded_modules', []),
            request_type=request_type
        )
        
        return result
        
    except Exception as e:
        log_error("Lambda execution failed", error=e)
        increment_counter("lambda_errors")
        return format_response(500, {"error": "Internal server error"})


def _determine_request_type(event: Dict[str, Any]) -> str:
    """Determine the type of request from event structure."""
    if 'directive' in event:
        return 'alexa_smart_home'
    elif 'request' in event and 'type' in event.get('request', {}):
        return 'alexa_custom_skill'
    elif 'requestType' in event:
        return event['requestType']
    elif 'httpMethod' in event:
        return 'api_gateway'
    elif 'test_type' in event:
        return 'diagnostic'
    else:
        return 'unknown'


def process_request(event: Dict[str, Any], context: Any, request_type: str) -> Dict[str, Any]:
    """Process the request based on type."""
    
    if request_type == 'alexa_smart_home':
        return _handle_alexa_smart_home(event, context)
    
    elif request_type == 'alexa_custom_skill':
        return _handle_alexa_custom_skill(event, context)
    
    elif request_type == 'health_check':
        return _handle_health_check(event, context)
    
    elif request_type == 'analytics':
        return _handle_analytics_request(event, context)
    
    elif request_type == 'diagnostic':
        return _handle_diagnostic_request(event, context)
    
    elif request_type == 'api_gateway':
        return _handle_api_gateway_request(event, context)
    
    else:
        log_warning(f"Unknown request type: {request_type}")
        return format_response(400, {"error": f"Unknown request type: {request_type}"})


def _handle_alexa_smart_home(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home skill requests."""
    try:
        from homeassistant_extension import process_alexa_ha_request, is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            log_error("Home Assistant extension disabled")
            return format_response(500, {"error": "Home Assistant integration disabled"})
        
        return process_alexa_ha_request(event)
        
    except Exception as e:
        log_error(f"Alexa Smart Home processing failed: {str(e)}")
        return format_response(500, {"error": "Smart Home request failed"})


def _handle_alexa_custom_skill(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Custom Skill requests with assistant name support."""
    try:
        request = event.get('request', {})
        request_type = request.get('type', '')
        
        log_info(f"Processing Alexa Custom Skill request: {request_type}")
        
        if request_type == 'LaunchRequest':
            return _handle_launch_request(event, context)
        
        elif request_type == 'IntentRequest':
            return _handle_intent_request(event, context)
        
        elif request_type == 'SessionEndedRequest':
            return _handle_session_ended_request(event, context)
        
        else:
            log_warning(f"Unknown Alexa request type: {request_type}")
            return _create_alexa_response("I don't understand that request type.")
    
    except Exception as e:
        log_error(f"Alexa Custom Skill processing failed: {str(e)}")
        return _create_alexa_response("Sorry, there was an error processing your request.")


def _handle_launch_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa LaunchRequest with personalized assistant name."""
    try:
        from homeassistant_extension import get_ha_assistant_name, is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            speech_text = "Home Assistant integration is currently disabled."
        else:
            assistant_name = get_ha_assistant_name()
            speech_text = f"Hello! {assistant_name} is ready to help you control your smart home. What would you like me to do?"
        
        return _create_alexa_response(speech_text, should_end_session=False)
        
    except Exception as e:
        log_error(f"Launch request failed: {str(e)}")
        return _create_alexa_response("Hello! I'm ready to help with your smart home.")


def _handle_intent_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa intent requests."""
    try:
        request = event.get('request', {})
        intent = request.get('intent', {})
        intent_name = intent.get('name', '')
        
        log_info(f"Processing intent: {intent_name}")
        
        if intent_name == 'TalkToHomeAssistant':
            return _handle_conversation_intent(event, context)
        
        elif intent_name == 'TriggerAutomation':
            return _handle_trigger_automation_intent(event, context)
        
        elif intent_name == 'RunScript':
            return _handle_run_script_intent(event, context)
        
        elif intent_name == 'SetInputHelper':
            return _handle_set_input_helper_intent(event, context)
        
        elif intent_name == 'MakeAnnouncement':
            return _handle_make_announcement_intent(event, context)
        
        elif intent_name == 'ControlArea':
            return _handle_control_area_intent(event, context)
        
        elif intent_name == 'ManageTimer':
            return _handle_manage_timer_intent(event, context)
        
        elif intent_name == 'GetDiagnostics':
            return _handle_get_diagnostics_intent(event, context)
        
        elif intent_name in ['AMAZON.HelpIntent']:
            return _handle_help_intent(event, context)
        
        elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
            return _handle_stop_intent(event, context)
        
        else:
            log_warning(f"Unknown intent: {intent_name}")
            return _create_alexa_response(f"I don't know how to handle the {intent_name} intent.")
            
    except Exception as e:
        log_error(f"Intent request failed: {str(e)}")
        return _create_alexa_response("Sorry, there was an error processing your request.")


def _handle_conversation_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle conversation with Home Assistant."""
    try:
        from homeassistant_extension import is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            return _create_alexa_response("Home Assistant integration is not enabled.")
        
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        query_slot = slots.get('query', {})
        user_query = query_slot.get('value', '')
        
        if not user_query:
            return _create_alexa_response("I didn't hear what you wanted me to tell Home Assistant.")
        
        log_info(f"Processing conversation query: {user_query}")
        
        return _create_alexa_response(f"I would process the query '{user_query}' with Home Assistant, but conversation processing is not yet implemented.")
        
    except Exception as e:
        log_error(f"Conversation intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't process your conversation request.")


def _handle_trigger_automation_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle automation triggering."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        automation_slot = slots.get('AutomationName', {})
        automation_name = automation_slot.get('value', '')
        
        if not automation_name:
            return _create_alexa_response("I didn't hear which automation you want me to trigger.")
        
        log_info(f"Triggering automation: {automation_name}")
        
        return _create_alexa_response(f"I would trigger the {automation_name} automation, but automation control is not yet implemented.")
        
    except Exception as e:
        log_error(f"Trigger automation intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't trigger that automation.")


def _handle_run_script_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle script execution."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        script_slot = slots.get('ScriptName', {})
        script_name = script_slot.get('value', '')
        
        if not script_name:
            return _create_alexa_response("I didn't hear which script you want me to run.")
        
        log_info(f"Running script: {script_name}")
        
        return _create_alexa_response(f"I would run the {script_name} script, but script execution is not yet implemented.")
        
    except Exception as e:
        log_error(f"Run script intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't run that script.")


def _handle_set_input_helper_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle input helper modification."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        helper_slot = slots.get('HelperName', {})
        value_slot = slots.get('HelperValue', {})
        
        helper_name = helper_slot.get('value', '')
        helper_value = value_slot.get('value', '')
        
        if not helper_name or not helper_value:
            return _create_alexa_response("I need both a helper name and value to set an input helper.")
        
        log_info(f"Setting input helper {helper_name} to {helper_value}")
        
        return _create_alexa_response(f"I would set {helper_name} to {helper_value}, but input helper control is not yet implemented.")
        
    except Exception as e:
        log_error(f"Set input helper intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't set that input helper.")


def _handle_make_announcement_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle TTS announcements."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        message_slot = slots.get('Message', {})
        message = message_slot.get('value', '')
        
        if not message:
            return _create_alexa_response("I didn't hear what you want me to announce.")
        
        log_info(f"Making announcement: {message}")
        
        return _create_alexa_response(f"I would announce '{message}' throughout your home, but announcement functionality is not yet implemented.")
        
    except Exception as e:
        log_error(f"Make announcement intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't make that announcement.")


def _handle_control_area_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle area-based device control."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        area_slot = slots.get('AreaName', {})
        action_slot = slots.get('Action', {})
        
        area_name = area_slot.get('value', '')
        action = action_slot.get('value', '')
        
        if not area_name or not action:
            return _create_alexa_response("I need both an area name and action to control area devices.")
        
        log_info(f"Controlling area {area_name}: {action}")
        
        return _create_alexa_response(f"I would turn {action} all devices in the {area_name}, but area control is not yet implemented.")
        
    except Exception as e:
        log_error(f"Control area intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't control that area.")


def _handle_manage_timer_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle timer management."""
    try:
        intent = event.get('request', {}).get('intent', {})
        slots = intent.get('slots', {})
        
        log_info("Managing timer")
        
        return _create_alexa_response("Timer management functionality is not yet implemented.")
        
    except Exception as e:
        log_error(f"Manage timer intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't manage that timer.")


def _handle_get_diagnostics_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostics request via Alexa."""
    try:
        from homeassistant_extension import get_ha_diagnostic_info, get_ha_assistant_name
        
        assistant_name = get_ha_assistant_name()
        diagnostic_result = get_ha_diagnostic_info()
        
        if diagnostic_result.get('success', False):
            data = diagnostic_result.get('data', {})
            ha_enabled = data.get('ha_enabled', False)
            connection_status = data.get('connection_status', 'unknown')
            
            if ha_enabled and connection_status == 'connected':
                speech_text = f"{assistant_name} is running normally and connected to Home Assistant."
            elif ha_enabled:
                speech_text = f"{assistant_name} is enabled but having connection issues with Home Assistant."
            else:
                speech_text = f"{assistant_name} is currently disabled."
        else:
            speech_text = f"I'm having trouble getting diagnostic information for {assistant_name}."
        
        return _create_alexa_response(speech_text)
        
    except Exception as e:
        log_error(f"Get diagnostics intent failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't get diagnostic information.")


def _handle_help_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle help request."""
    try:
        from homeassistant_extension import get_ha_assistant_name, is_ha_extension_enabled
        
        if is_ha_extension_enabled():
            assistant_name = get_ha_assistant_name()
            speech_text = f"I'm {assistant_name}, your smart home voice assistant. I can help you control devices, run automations, execute scripts, and manage your home. What would you like me to do?"
        else:
            speech_text = "I'm your smart home assistant, but Home Assistant integration is currently disabled. Please check your configuration."
        
        return _create_alexa_response(speech_text, should_end_session=False)
        
    except Exception as e:
        log_error(f"Help intent failed: {str(e)}")
        return _create_alexa_response("I'm here to help with your smart home. What would you like me to do?")


def _handle_stop_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle stop/cancel request."""
    return _create_alexa_response("Goodbye!", should_end_session=True)


def _handle_session_ended_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle session ended request."""
    log_info("Alexa session ended")
    return {}


def _handle_health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle health check requests."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": context.aws_request_id,
            "version": "2025.10.02.01",
            "gateway_loaded": True
        }
        
        try:
            from homeassistant_extension import get_ha_status, is_ha_extension_enabled
            
            health_status["ha_extension_enabled"] = is_ha_extension_enabled()
            
            if is_ha_extension_enabled():
                ha_status = get_ha_status()
                health_status["ha_connection"] = ha_status.get('success', False)
            
        except Exception as e:
            import traceback
            log_error(f"HA extension error: {traceback.format_exc()}")
            health_status["ha_extension_error"] = str(e)
        
        return format_response(200, health_status)
        
    except Exception as e:
        log_error(f"Health check failed: {str(e)}")
        return format_response(500, {"status": "unhealthy", "error": str(e)})


def _handle_analytics_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle analytics requests."""
    try:
        usage_summary = get_usage_summary()
        gateway_stats = get_gateway_stats()
        
        analytics = {
            "usage": usage_summary,
            "gateway": gateway_stats,
            "timestamp": context.aws_request_id
        }
        
        return format_response(200, analytics)
        
    except Exception as e:
        log_error(f"Analytics request failed: {str(e)}")
        return format_response(500, {"error": str(e)})


def _handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle comprehensive diagnostic requests."""
    try:
        test_type = event.get('test_type', 'full')
        
        diagnostics = {
            "timestamp": context.aws_request_id,
            "test_type": test_type,
            "lambda_info": {
                "function_name": context.function_name,
                "function_version": context.function_version,
                "memory_limit": context.memory_limit_in_mb,
                "remaining_time": context.get_remaining_time_in_millis()
            },
            "gateway_stats": get_gateway_stats()
        }
        
        if test_type in ['full', 'homeassistant']:
            try:
                from homeassistant_extension import get_ha_diagnostic_info
                ha_diagnostics = get_ha_diagnostic_info()
                diagnostics["home_assistant"] = ha_diagnostics.get('data', {})
            except Exception as e:
                diagnostics["home_assistant_error"] = str(e)
        
        if test_type in ['full', 'configuration']:
            try:
                from homeassistant_extension import get_assistant_name_status
                name_status = get_assistant_name_status()
                diagnostics["assistant_name"] = name_status.get('data', {})
            except Exception as e:
                diagnostics["assistant_name_error"] = str(e)
        
        return format_response(200, diagnostics)
        
    except Exception as e:
        log_error(f"Diagnostic request failed: {str(e)}")
        return format_response(500, {"error": str(e)})


def _handle_api_gateway_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle API Gateway requests."""
    try:
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        if path == '/health' and method == 'GET':
            return _handle_health_check(event, context)
        
        elif path == '/diagnostics' and method in ['GET', 'POST']:
            diagnostic_event = {
                'test_type': event.get('queryStringParameters', {}).get('type', 'full') if method == 'GET' else 'full'
            }
            return _handle_diagnostic_request(diagnostic_event, context)
        
        elif path == '/analytics' and method == 'GET':
            return _handle_analytics_request(event, context)
        
        else:
            return format_response(404, {"error": "Not found"})
            
    except Exception as e:
        log_error(f"API Gateway request failed: {str(e)}")
        return format_response(500, {"error": str(e)})


def _create_alexa_response(speech_text: str, should_end_session: bool = True) -> Dict[str, Any]:
    """Create standardized Alexa response."""
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech_text
            },
            "shouldEndSession": should_end_session
        }
    }

# EOF
