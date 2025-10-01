"""
Lambda Function Handler - Main Entry Point
Version: 2025.09.30.04
Daily Revision: 001

Revolutionary Gateway Architecture with Enhanced HA Features
UPDATED: Added automation, script, input helper, notification, area, and timer intents

Licensed under the Apache License, Version 2.0
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
    - Alexa Custom Skill requests (intents) - ENHANCED
    - Health checks and analytics
    """
    
    try:
        log_info("Lambda invocation started", context={"request_id": context.request_id})
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
    else:
        return 'unknown'


def process_request(event: Dict[str, Any], context: Any, request_type: str) -> Dict[str, Any]:
    """Process the request based on type."""
    if request_type == 'health_check':
        return handle_health_check(event)
    elif request_type == 'analytics':
        return handle_analytics_request(event)
    elif request_type == 'alexa_smart_home':
        return handle_alexa_smart_home(event, context)
    elif request_type == 'alexa_custom_skill':
        return handle_alexa_custom_skill(event, context)
    elif request_type == 'data':
        return handle_data_request(event)
    else:
        log_debug(f"Unknown request type: {request_type}")
        return format_response(200, {"message": "Request processed", "type": request_type})


def handle_health_check(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle health check request."""
    gateway_stats = get_gateway_stats()
    
    return format_response(200, {
        "status": "healthy",
        "gateway": "SUGA + LIGS",
        "loaded_modules": gateway_stats.get('loaded_modules', []),
        "lazy_loading": "active"
    })


def handle_analytics_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle analytics request."""
    usage_summary = get_usage_summary()
    
    return format_response(200, {
        "analytics": usage_summary,
        "gateway_stats": get_gateway_stats()
    })


def handle_alexa_smart_home(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home skill request."""
    try:
        from homeassistant_extension import process_alexa_ha_request, is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            log_error("Home Assistant extension is disabled")
            return _create_alexa_error_response("Home Assistant integration is not enabled")
        
        log_info("Processing Alexa Smart Home request")
        increment_counter("alexa_smart_home_requests")
        
        result = process_alexa_ha_request(event)
        
        record_metric("alexa_smart_home_success", 1.0)
        return result
        
    except Exception as e:
        log_error(f"Alexa Smart Home processing failed: {str(e)}")
        record_metric("alexa_smart_home_error", 1.0)
        return _create_alexa_error_response(str(e))


def handle_alexa_custom_skill(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Custom Skill request."""
    try:
        request = event.get('request', {})
        request_type = request.get('type', '')
        
        log_info(f"Processing Alexa Custom Skill request: {request_type}")
        increment_counter("alexa_custom_skill_requests")
        
        if request_type == 'LaunchRequest':
            return _handle_launch_request(event)
        elif request_type == 'IntentRequest':
            return _handle_intent_request(event)
        elif request_type == 'SessionEndedRequest':
            return _handle_session_ended(event)
        else:
            log_warning(f"Unknown custom skill request type: {request_type}")
            return _create_custom_skill_response("I didn't understand that request.")
            
    except Exception as e:
        log_error(f"Alexa Custom Skill processing failed: {str(e)}")
        record_metric("alexa_custom_skill_error", 1.0)
        return _create_custom_skill_response("Sorry, I encountered an error.")


def _handle_launch_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle skill launch request."""
    return _create_custom_skill_response(
        "Welcome to Home Assistant. You can control devices, trigger automations, run scripts, "
        "make announcements, or manage timers. What would you like to do?",
        should_end_session=False
    )


def _handle_intent_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle intent request."""
    try:
        from homeassistant_extension import is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            return _create_custom_skill_response(
                "Home Assistant integration is not enabled.",
                should_end_session=True
            )
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        intent_name = intent.get('name', '')
        
        if intent_name == 'TalkToHomeAssistant':
            return _handle_conversation_intent(event)
        
        elif intent_name == 'TriggerAutomation':
            return _handle_trigger_automation_intent(event)
        
        elif intent_name == 'RunScript':
            return _handle_run_script_intent(event)
        
        elif intent_name == 'SetInputHelper':
            return _handle_set_input_helper_intent(event)
        
        elif intent_name == 'MakeAnnouncement':
            return _handle_make_announcement_intent(event)
        
        elif intent_name == 'ControlArea':
            return _handle_control_area_intent(event)
        
        elif intent_name == 'ManageTimer':
            return _handle_manage_timer_intent(event)
        
        elif intent_name == 'AMAZON.HelpIntent':
            return _create_custom_skill_response(
                "You can say things like: trigger good morning routine, run bedtime script, "
                "set house mode to away, announce dinner is ready, turn off everything in the kitchen, "
                "or start a 10 minute timer. What would you like to do?",
                should_end_session=False
            )
            
        elif intent_name in ['AMAZON.CancelIntent', 'AMAZON.StopIntent']:
            return _create_custom_skill_response(
                "Goodbye!",
                should_end_session=True
            )
            
        else:
            log_warning(f"Unknown intent: {intent_name}")
            return _create_custom_skill_response(
                "I'm not sure how to help with that.",
                should_end_session=False
            )
            
    except Exception as e:
        log_error(f"Intent processing failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I encountered an error processing your request.",
            should_end_session=True
        )


def _handle_conversation_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle TalkToHomeAssistant intent."""
    try:
        from homeassistant_extension import is_ha_extension_enabled, _get_ha_config_gateway
        from home_assistant_conversation import process_alexa_conversation
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        query_slot = slots.get('query', {})
        user_text = query_slot.get('value', '')
        
        if not user_text:
            return _create_custom_skill_response(
                "I didn't hear what you wanted to say. Please try again.",
                should_end_session=False
            )
        
        ha_config = _get_ha_config_gateway()
        session_attributes = event.get('session', {}).get('attributes', {})
        
        log_info(f"Processing conversation: {user_text}")
        record_metric("ha_conversation_request", 1.0)
        
        result = process_alexa_conversation(
            user_text=user_text,
            ha_config=ha_config,
            session_attributes=session_attributes
        )
        
        return result
        
    except Exception as e:
        log_error(f"Conversation intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't process your conversation request.",
            should_end_session=True
        )


def _handle_trigger_automation_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle TriggerAutomation intent."""
    try:
        from homeassistant_extension import trigger_ha_automation
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        automation_name = slots.get('AutomationName', {}).get('value', '')
        
        if not automation_name:
            return _create_custom_skill_response(
                "I didn't catch the automation name. Please try again.",
                should_end_session=False
            )
        
        log_info(f"Triggering automation: {automation_name}")
        record_metric("ha_automation_trigger_request", 1.0)
        
        result = trigger_ha_automation(automation_name)
        
        if result.get("success", False):
            return _create_custom_skill_response(
                f"Automation {automation_name} triggered successfully.",
                should_end_session=True
            )
        else:
            return _create_custom_skill_response(
                f"I couldn't trigger the automation {automation_name}.",
                should_end_session=True
            )
            
    except Exception as e:
        log_error(f"Trigger automation intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't trigger the automation.",
            should_end_session=True
        )


def _handle_run_script_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle RunScript intent."""
    try:
        from homeassistant_extension import execute_ha_script
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        script_name = slots.get('ScriptName', {}).get('value', '')
        
        if not script_name:
            return _create_custom_skill_response(
                "I didn't catch the script name. Please try again.",
                should_end_session=False
            )
        
        log_info(f"Executing script: {script_name}")
        record_metric("ha_script_execution_request", 1.0)
        
        result = execute_ha_script(script_name)
        
        if result.get("success", False):
            return _create_custom_skill_response(
                f"Script {script_name} executed successfully.",
                should_end_session=True
            )
        else:
            return _create_custom_skill_response(
                f"I couldn't execute the script {script_name}.",
                should_end_session=True
            )
            
    except Exception as e:
        log_error(f"Run script intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't execute the script.",
            should_end_session=True
        )


def _handle_set_input_helper_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle SetInputHelper intent."""
    try:
        from homeassistant_extension import set_ha_input_helper
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        helper_name = slots.get('HelperName', {}).get('value', '')
        helper_value = slots.get('HelperValue', {}).get('value', '')
        
        if not helper_name or not helper_value:
            return _create_custom_skill_response(
                "I need both the helper name and value. Please try again.",
                should_end_session=False
            )
        
        log_info(f"Setting input helper: {helper_name} = {helper_value}")
        record_metric("ha_input_helper_set_request", 1.0)
        
        result = set_ha_input_helper(helper_name, helper_value)
        
        if result.get("success", False):
            return _create_custom_skill_response(
                f"Set {helper_name} to {helper_value}.",
                should_end_session=True
            )
        else:
            return _create_custom_skill_response(
                f"I couldn't set {helper_name}.",
                should_end_session=True
            )
            
    except Exception as e:
        log_error(f"Set input helper intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't set the input helper.",
            should_end_session=True
        )


def _handle_make_announcement_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MakeAnnouncement intent."""
    try:
        from homeassistant_extension import send_ha_announcement
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        message = slots.get('Message', {}).get('value', '')
        
        if not message:
            return _create_custom_skill_response(
                "I didn't catch the message. Please try again.",
                should_end_session=False
            )
        
        log_info(f"Making announcement: {message[:50]}...")
        record_metric("ha_announcement_request", 1.0)
        
        result = send_ha_announcement(message)
        
        if result.get("success", False):
            return _create_custom_skill_response(
                "Announcement sent.",
                should_end_session=True
            )
        else:
            return _create_custom_skill_response(
                "I couldn't send the announcement.",
                should_end_session=True
            )
            
    except Exception as e:
        log_error(f"Make announcement intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't make the announcement.",
            should_end_session=True
        )


def _handle_control_area_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ControlArea intent."""
    try:
        from homeassistant_extension import control_ha_area
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        area_name = slots.get('AreaName', {}).get('value', '')
        action = slots.get('Action', {}).get('value', 'turn_off')
        
        if not area_name:
            return _create_custom_skill_response(
                "I didn't catch the area name. Please try again.",
                should_end_session=False
            )
        
        log_info(f"Controlling area: {area_name} - {action}")
        record_metric("ha_area_control_request", 1.0)
        
        result = control_ha_area(area_name, action)
        
        if result.get("success", False):
            data = result.get("data", {})
            successful = data.get("successful", 0)
            return _create_custom_skill_response(
                f"Controlled {successful} devices in {area_name}.",
                should_end_session=True
            )
        else:
            return _create_custom_skill_response(
                f"I couldn't control devices in {area_name}.",
                should_end_session=True
            )
            
    except Exception as e:
        log_error(f"Control area intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't control the area.",
            should_end_session=True
        )


def _handle_manage_timer_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ManageTimer intent."""
    try:
        from homeassistant_extension import start_ha_timer, cancel_ha_timer
        
        request = event.get('request', {})
        intent = request.get('intent', {})
        slots = intent.get('slots', {})
        
        timer_action = slots.get('TimerAction', {}).get('value', 'start')
        timer_name = slots.get('TimerName', {}).get('value', 'timer')
        duration = slots.get('Duration', {}).get('value', '')
        
        log_info(f"Managing timer: {timer_action} - {timer_name}")
        record_metric("ha_timer_manage_request", 1.0)
        
        if timer_action in ['start', 'create']:
            if not duration:
                return _create_custom_skill_response(
                    "How long should the timer run?",
                    should_end_session=False
                )
            
            result = start_ha_timer(timer_name, duration)
            
            if result.get("success", False):
                return _create_custom_skill_response(
                    f"Timer {timer_name} started for {duration}.",
                    should_end_session=True
                )
            else:
                return _create_custom_skill_response(
                    f"I couldn't start the timer.",
                    should_end_session=True
                )
        
        elif timer_action in ['cancel', 'stop']:
            result = cancel_ha_timer(timer_name)
            
            if result.get("success", False):
                return _create_custom_skill_response(
                    f"Timer {timer_name} cancelled.",
                    should_end_session=True
                )
            else:
                return _create_custom_skill_response(
                    f"I couldn't cancel the timer.",
                    should_end_session=True
                )
        
        else:
            return _create_custom_skill_response(
                "I can start or cancel timers. What would you like to do?",
                should_end_session=False
            )
            
    except Exception as e:
        log_error(f"Manage timer intent failed: {str(e)}")
        return _create_custom_skill_response(
            "Sorry, I couldn't manage the timer.",
            should_end_session=True
        )


def _handle_session_ended(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle session ended request."""
    log_info("Session ended")
    return {
        "version": "1.0",
        "response": {}
    }


def _create_custom_skill_response(speech_text: str, 
                                  should_end_session: bool = False) -> Dict[str, Any]:
    """Create standard Alexa custom skill response."""
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


def _create_alexa_error_response(error_message: str) -> Dict[str, Any]:
    """Create Alexa Smart Home error response."""
    from gateway import generate_correlation_id
    
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": generate_correlation_id(),
                "payloadVersion": "3"
            },
            "payload": {
                "type": "INTERNAL_ERROR",
                "message": error_message
            }
        }
    }


def handle_data_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle generic data request."""
    log_info("Processing data request")
    return format_response(200, {"message": "Data request processed"})


__all__ = ['lambda_handler']

#EOF
