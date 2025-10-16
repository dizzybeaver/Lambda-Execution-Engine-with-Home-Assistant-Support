"""
lambda_function.py
Version: 2025.10.15.03
Description: Main Entry Point with Emergency Failsafe - Fixed timeout issues
Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import json
import os
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler with Emergency Failsafe.
    
    FAILSAFE MODE:
      If LEE_FAILSAFE_ENABLED=true, routes ALL requests to lambda_failsafe.py
      bypassing the entire LEE and extension system.
      
    NORMAL MODE:
      Uses Revolutionary Gateway Architecture and extensions.
    """
    
    # ========================================================================
    # FAILSAFE CHECK - MUST BE FIRST - NO SUGA DEPENDENCIES
    # ========================================================================
    if os.getenv('LEE_FAILSAFE_ENABLED', 'false').lower() == 'true':
        try:
            # Import failsafe handler (standalone, no SUGA dependencies)
            import lambda_failsafe
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError as e:
            # Failsafe file not found - log error and continue with LEE
            print(f"ERROR: Failsafe enabled but lambda_failsafe.py not found: {e}")
            print("Falling back to normal LEE operation")
        except Exception as e:
            # Failsafe crashed - return error
            print(f"CRITICAL: Failsafe handler crashed: {e}")
            return {
                'event': {
                    'header': {
                        'namespace': 'Alexa',
                        'name': 'ErrorResponse',
                        'messageId': 'failsafe-crash',
                        'payloadVersion': '3'
                    },
                    'payload': {
                        'type': 'INTERNAL_ERROR',
                        'message': f'Failsafe handler error: {str(e)}'
                    }
                }
            }
    
    # ========================================================================
    # NORMAL LEE OPERATION
    # âœ… Lazy imports - only load what we need when we need it
    # ========================================================================
    from gateway import (
        log_info, log_error, log_debug, log_warning,
        validate_request, validate_token,
        increment_counter,
        format_response,
        get_gateway_stats
    )
    
    try:
        log_info("Lambda invocation started", context={"request_id": context.aws_request_id})
        increment_counter("lambda_invocations")
        request_type = _determine_request_type(event)
        log_debug(f"Processing request type: {request_type}")

        # Skip validation for Alexa directives
        if 'directive' not in event and not validate_request(event):
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
    elif 'httpMethod' in event:
        return 'api_gateway'
    elif 'test_type' in event:
        return 'diagnostic'
    elif 'health_check' in event:
        return 'health_check'
    else:
        return 'unknown'


def process_request(event: Dict[str, Any], context: Any, request_type: str) -> Dict[str, Any]:
    """Route request to appropriate handler."""
    if request_type == 'alexa_smart_home':
        return _handle_alexa_smart_home(event, context)
    elif request_type == 'alexa_custom_skill':
        return _handle_alexa_custom_skill(event, context)
    elif request_type == 'api_gateway':
        return _handle_api_gateway_request(event, context)
    elif request_type == 'diagnostic':
        return _handle_diagnostic_request(event, context)
    elif request_type == 'health_check':
        return _handle_health_check(event, context)
    else:
        from gateway import log_warning, format_response
        log_warning(f"Unknown request type: {request_type}")
        return format_response(400, {"error": "Unknown request type"})


def _handle_alexa_smart_home(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home skill directives."""
    # âœ… Lazy imports - only load HA extension when handling Alexa requests
    from gateway import log_info, log_error, log_debug, increment_counter
    from homeassistant_extension import process_alexa_ha_request, is_ha_extension_enabled
    
    try:
        directive = event.get('directive', {})
        namespace = directive.get('header', {}).get('namespace', 'Unknown')
        name = directive.get('header', {}).get('name', 'Unknown')
        
        log_info(f"Processing Alexa directive: {namespace}.{name}")
        log_debug(f"Full directive: {json.dumps(directive)}")
        increment_counter("alexa_smart_home_requests")
        
        if not is_ha_extension_enabled():
            log_error("Home Assistant extension not enabled")
            return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE',
                                               'Home Assistant integration is not available')
        
        result = process_alexa_ha_request(event)
        increment_counter("alexa_smart_home_success")
        return result
        
    except Exception as e:
        log_error(f"Alexa Smart Home request failed: {str(e)}")
        increment_counter("alexa_smart_home_failed")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def _handle_alexa_custom_skill(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Custom Skill requests."""
    # âœ… Lazy imports
    from gateway import log_info, log_error, increment_counter
    from homeassistant_extension import is_ha_extension_enabled
    
    try:
        request_type = event.get('request', {}).get('type', 'Unknown')
        log_info(f"Processing Alexa custom skill request: {request_type}")
        increment_counter("alexa_custom_requests")
        
        if not is_ha_extension_enabled():
            return _create_alexa_response("Home Assistant integration is not available.")
        
        if request_type == 'LaunchRequest':
            return _handle_launch_request(event, context)
        elif request_type == 'SessionEndedRequest':
            return _handle_session_ended_request(event, context)
        elif request_type == 'IntentRequest':
            intent_name = event.get('request', {}).get('intent', {}).get('name', '')
            return _handle_intent_request(event, context, intent_name)
        else:
            log_error(f"Unknown custom skill request type: {request_type}")
            return _create_alexa_response("I don't understand that request.")
            
    except Exception as e:
        log_error(f"Custom skill request failed: {str(e)}")
        increment_counter("alexa_custom_intents_failed")
        return _create_alexa_response("Sorry, something went wrong.")


def _handle_launch_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa skill launch."""
    from gateway import log_info
    from homeassistant_extension import get_ha_assistant_name, is_ha_extension_enabled
    
    log_info("Alexa skill launched")
    
    if not is_ha_extension_enabled():
        return _create_alexa_response("Home Assistant integration is not available.")
    
    assistant_name = get_ha_assistant_name()
    return _create_alexa_response(
        f"Hello, I'm {assistant_name}. What can I help you with?",
        should_end_session=False
    )


def _handle_session_ended_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle session end."""
    from gateway import log_info
    log_info("Alexa session ended")
    return _create_alexa_response("Goodbye.", should_end_session=True)


def _handle_intent_request(event: Dict[str, Any], context: Any, intent_name: str) -> Dict[str, Any]:
    """Route intent to appropriate handler."""
    intent_handlers = {
        'AMAZON.HelpIntent': _handle_help_intent,
        'AMAZON.CancelIntent': _handle_cancel_intent,
        'AMAZON.StopIntent': _handle_stop_intent,
        'TriggerAutomationIntent': _handle_trigger_automation_intent,
        'ConversationIntent': _handle_conversation_intent,
        'RunScriptIntent': _handle_run_script_intent,
        'SetInputHelperIntent': _handle_set_input_helper_intent,
        'MakeAnnouncementIntent': _handle_make_announcement_intent,
        'ListAutomationsIntent': _handle_list_automations_intent,
        'ListScriptsIntent': _handle_list_scripts_intent,
        'HomeAssistantStatusIntent': _handle_status_intent
    }
    
    handler = intent_handlers.get(intent_name)
    if handler:
        return handler(event, context)
    else:
        from gateway import log_warning
        log_warning(f"Unknown intent: {intent_name}")
        return _create_alexa_response("I don't know how to do that yet.")


def _handle_help_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle help intent."""
    from homeassistant_extension import get_ha_assistant_name
    assistant_name = get_ha_assistant_name()
    return _create_alexa_response(
        f"I'm {assistant_name}. You can ask me to trigger automations, run scripts, "
        "have conversations, or control your Home Assistant devices.",
        should_end_session=False
    )


def _handle_cancel_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle cancel intent."""
    return _create_alexa_response("Okay, cancelled.")


def _handle_stop_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle stop intent."""
    return _create_alexa_response("Goodbye.")


def _handle_status_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle status check intent."""
    from gateway import log_info
    from homeassistant_extension import get_ha_status
    
    log_info("Status check requested via Alexa")
    status = get_ha_status()
    
    if status.get('success'):
        return _create_alexa_response("Home Assistant is connected and running.")
    else:
        error = status.get('error', 'Unknown error')
        return _create_alexa_response(f"Home Assistant is not available. {error}")


def _handle_trigger_automation_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle trigger automation intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import trigger_automation
    
    try:
        slots = event.get('request', {}).get('intent', {}).get('slots', {})
        automation_name = slots.get('AutomationName', {}).get('value', '')
        
        if not automation_name:
            return _create_alexa_response("I didn't catch the automation name. Please try again.")
        
        log_info(f"Triggering automation: {automation_name}")
        result = trigger_automation(automation_name)
        
        if result.get('success'):
            return _create_alexa_response(f"I've triggered the {automation_name} automation.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't trigger that automation. {error}")
            
    except Exception as e:
        log_error(f"Trigger automation failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't trigger that automation.")


def _handle_conversation_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle conversation intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import process_conversation
    
    try:
        slots = event.get('request', {}).get('intent', {}).get('slots', {})
        message = slots.get('Message', {}).get('value', '')
        
        if not message:
            return _create_alexa_response("I didn't hear what you said. Please try again.")
        
        log_info(f"Processing conversation: {message}")
        result = process_conversation(message)
        
        if result.get('success'):
            response_text = result.get('data', {}).get('response', {}).get('speech', {}).get('plain', {}).get('speech', 'Done.')
            return _create_alexa_response(response_text)
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't process that. {error}")
            
    except Exception as e:
        log_error(f"Conversation failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't understand that.")


def _handle_run_script_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle run script intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import run_script
    
    try:
        slots = event.get('request', {}).get('intent', {}).get('slots', {})
        script_name = slots.get('ScriptName', {}).get('value', '')
        
        if not script_name:
            return _create_alexa_response("I didn't catch the script name. Please try again.")
        
        log_info(f"Running script: {script_name}")
        result = run_script(script_name)
        
        if result.get('success'):
            return _create_alexa_response(f"I've run the {script_name} script.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't run that script. {error}")
            
    except Exception as e:
        log_error(f"Run script failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't run that script.")


def _handle_set_input_helper_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle set input helper intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import set_input_helper
    
    try:
        slots = event.get('request', {}).get('intent', {}).get('slots', {})
        helper_name = slots.get('HelperName', {}).get('value', '')
        helper_value = slots.get('HelperValue', {}).get('value', '')
        
        if not helper_name or not helper_value:
            return _create_alexa_response("I need both the helper name and value. Please try again.")
        
        log_info(f"Setting input helper: {helper_name} = {helper_value}")
        result = set_input_helper(helper_name, helper_value)
        
        if result.get('success'):
            return _create_alexa_response(f"I've set {helper_name} to {helper_value}.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't set that helper. {error}")
            
    except Exception as e:
        log_error(f"Set input helper failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't set that helper.")


def _handle_list_automations_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle list automations intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import list_automations
    
    try:
        log_info("Listing automations")
        result = list_automations()
        
        if result.get('success'):
            automations = result.get('data', [])
            count = len(automations)
            if count == 0:
                return _create_alexa_response("You don't have any automations.")
            elif count == 1:
                return _create_alexa_response("You have one automation available.")
            else:
                return _create_alexa_response(f"You have {count} automations available.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't list the automations. {error}")
            
    except Exception as e:
        log_error(f"List automations failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't list the automations.")


def _handle_list_scripts_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle list scripts intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import list_scripts
    
    try:
        log_info("Listing scripts")
        result = list_scripts()
        
        if result.get('success'):
            scripts = result.get('data', [])
            count = len(scripts)
            if count == 0:
                return _create_alexa_response("You don't have any scripts.")
            elif count == 1:
                return _create_alexa_response("You have one script available.")
            else:
                return _create_alexa_response(f"You have {count} scripts available.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't list the scripts. {error}")
            
    except Exception as e:
        log_error(f"List scripts failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't list the scripts.")


def _handle_make_announcement_intent(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle make announcement intent."""
    from gateway import log_info, log_error
    from homeassistant_extension import send_notification
    
    try:
        slots = event.get('request', {}).get('intent', {}).get('slots', {})
        message = slots.get('Message', {}).get('value', '')
        
        if not message:
            return _create_alexa_response("I didn't hear the announcement. Please try again.")
        
        log_info(f"Sending notification: {message}")
        result = send_notification(message)
        
        if result.get('success'):
            return _create_alexa_response("I've sent that announcement.")
        else:
            error = result.get('error', 'Unknown error')
            return _create_alexa_response(f"I couldn't send that announcement. {error}")
            
    except Exception as e:
        log_error(f"Make announcement failed: {str(e)}")
        return _create_alexa_response("Sorry, I couldn't make that announcement.")


def _handle_health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle health check requests."""
    # âœ… Lazy imports - minimal for health checks
    from gateway import log_info, log_error, format_response, get_gateway_stats
    
    try:
        log_info("Health check requested")
        health = {
            "status": "healthy",
            "lambda": {
                "function_name": context.function_name,
                "memory_limit": context.memory_limit_in_mb,
                "remaining_time": context.get_remaining_time_in_millis()
            },
            "gateway": get_gateway_stats()
        }

        # Only check HA if explicitly requested or if extension is enabled
        if event.get('check_ha', False):
            from homeassistant_extension import get_ha_status, is_ha_extension_enabled
            if is_ha_extension_enabled():
                ha_status = get_ha_status()
                health["home_assistant"] = ha_status.get('data', {})
            else:
                health["home_assistant"] = {"enabled": False}

        return format_response(200, health)

    except Exception as e:
        log_error(f"Health check failed: {str(e)}")
        return format_response(500, {"status": "unhealthy", "error": str(e)})


def _handle_analytics_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle analytics requests."""
    from gateway import log_info, log_error, format_response, get_gateway_stats
    
    try:
        gateway_stats = get_gateway_stats()
        analytics = {
            "gateway": gateway_stats,
            "timestamp": context.aws_request_id
        }
        return format_response(200, analytics)

    except Exception as e:
        log_error(f"Analytics request failed: {str(e)}")
        return format_response(500, {"error": str(e)})


def _handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle comprehensive diagnostic requests."""
    # âœ… Lazy imports - only load what's needed for this specific test type
    from gateway import log_info, log_error, format_response, get_gateway_stats
    
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

        # âœ… CRITICAL: Only import HA extension if test actually needs it
        if test_type in ['full', 'homeassistant']:
            try:
                from homeassistant_extension import get_ha_diagnostic_info
                ha_diagnostics = get_ha_diagnostic_info()
                diagnostics["home_assistant"] = ha_diagnostics.get('data', {})
                
                if event.get('show_config'):
                    diagnostics["environment"] = {
                        "HOME_ASSISTANT_URL": os.getenv('HOME_ASSISTANT_URL'),
                        "HOME_ASSISTANT_TOKEN": os.getenv('HOME_ASSISTANT_TOKEN', '')[0:20] + '...',
                        "HOME_ASSISTANT_ENABLED": os.getenv('HOME_ASSISTANT_ENABLED'),
                        "USE_PARAMETER_STORE": os.getenv('USE_PARAMETER_STORE'),
                        "LEE_FAILSAFE_ENABLED": os.getenv('LEE_FAILSAFE_ENABLED', 'false')
                    }
            except Exception as e:
                diagnostics["home_assistant_error"] = str(e)

        # âœ… Configuration test - no HA imports needed
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
    from gateway import log_error, format_response
    
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


def _create_alexa_error_response(event: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    from gateway import generate_correlation_id
    
    header = event.get('directive', {}).get('header', {})
    message_id = header.get('messageId', generate_correlation_id())
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': message_id,
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }

# EOF
