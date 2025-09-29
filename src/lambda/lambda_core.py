"""
lambda_core.py - Core Lambda Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Lambda response building
"""

import json
from typing import Any, Dict, Optional

def build_response(
    status_code: int,
    body: Any,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Build Lambda response."""
    response_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
    }
    
    if headers:
        response_headers.update(headers)
    
    if isinstance(body, (dict, list)):
        body_str = json.dumps(body)
    else:
        body_str = str(body)
    
    response = {
        "statusCode": status_code,
        "headers": response_headers,
        "body": body_str
    }
    
    if "isBase64Encoded" in kwargs:
        response["isBase64Encoded"] = kwargs["isBase64Encoded"]
    
    return response

def build_success_response(body: Any, **kwargs) -> Dict[str, Any]:
    """Build success response."""
    return build_response(200, body, **kwargs)

def build_error_response(message: str, status_code: int = 500, **kwargs) -> Dict[str, Any]:
    """Build error response."""
    body = {
        "error": message,
        "statusCode": status_code
    }
    return build_response(status_code, body, **kwargs)

def build_alexa_response(
    speech: str,
    card_title: Optional[str] = None,
    card_content: Optional[str] = None,
    reprompt: Optional[str] = None,
    should_end_session: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Build Alexa response."""
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech
            },
            "shouldEndSession": should_end_session
        }
    }
    
    if card_title and card_content:
        response["response"]["card"] = {
            "type": "Simple",
            "title": card_title,
            "content": card_content
        }
    
    if reprompt:
        response["response"]["reprompt"] = {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt
            }
        }
    
    if "sessionAttributes" in kwargs:
        response["sessionAttributes"] = kwargs["sessionAttributes"]
    
    return response

def parse_lambda_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Lambda event."""
    parsed = {
        "event_type": "unknown",
        "http_method": None,
        "path": None,
        "query_params": {},
        "headers": {},
        "body": None,
        "is_alexa": False,
        "raw_event": event
    }
    
    if "requestContext" in event:
        parsed["event_type"] = "api_gateway"
        parsed["http_method"] = event.get("httpMethod")
        parsed["path"] = event.get("path")
        parsed["query_params"] = event.get("queryStringParameters", {}) or {}
        parsed["headers"] = event.get("headers", {}) or {}
        
        body = event.get("body")
        if body:
            try:
                parsed["body"] = json.loads(body)
            except json.JSONDecodeError:
                parsed["body"] = body
    
    elif "request" in event and "type" in event.get("request", {}):
        parsed["event_type"] = "alexa"
        parsed["is_alexa"] = True
        parsed["alexa_request_type"] = event["request"]["type"]
        parsed["alexa_intent"] = event["request"].get("intent", {}).get("name")
    
    return parsed

def extract_path_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract path parameters from event."""
    return event.get("pathParameters", {}) or {}

def extract_query_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract query parameters from event."""
    return event.get("queryStringParameters", {}) or {}

def extract_headers(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract headers from event."""
    return event.get("headers", {}) or {}

def extract_body(event: Dict[str, Any]) -> Any:
    """Extract body from event."""
    body = event.get("body")
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body
    return None

def is_alexa_event(event: Dict[str, Any]) -> bool:
    """Check if event is from Alexa."""
    return "request" in event and "type" in event.get("request", {})

def get_alexa_intent(event: Dict[str, Any]) -> Optional[str]:
    """Get Alexa intent name."""
    if is_alexa_event(event):
        return event.get("request", {}).get("intent", {}).get("name")
    return None

def get_alexa_slots(event: Dict[str, Any]) -> Dict[str, Any]:
    """Get Alexa slot values."""
    if is_alexa_event(event):
        slots = event.get("request", {}).get("intent", {}).get("slots", {})
        return {
            name: slot.get("value")
            for name, slot in slots.items()
            if "value" in slot
        }
    return {}
