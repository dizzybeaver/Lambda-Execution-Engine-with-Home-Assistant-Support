"""
debug_discovery.py - Alexa Discovery Debug Tracer
Version: 2025.10.19.01
Description: Traces every step of Alexa discovery with extensive [DEBUG] output.
             Only shows debug when DEBUG_MODE=true.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import urllib3
from typing import Dict, Any


def _debug(msg: str):
    """Print debug message only if DEBUG_MODE=true."""
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        print(f"[DEBUG] {msg}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Debug trace handler for Alexa discovery."""
    
    _debug("═══════════════════════════════════════════════════")
    _debug("DEBUG_DISCOVERY: Handler started")
    _debug("═══════════════════════════════════════════════════")
    _debug(f"Request ID: {context.aws_request_id}")
    _debug(f"Function: {context.function_name}")
    _debug(f"Memory: {context.memory_limit_in_mb}MB")
    _debug(f"Remaining time: {context.get_remaining_time_in_millis()}ms")
    
    try:
        # Step 1: Parse event
        _debug("\n--- STEP 1: Parse Event ---")
        _debug(f"Event keys: {list(event.keys())}")
        _debug(f"Full event: {json.dumps(event, indent=2)}")
        
        directive = event.get('directive', {})
        _debug(f"Directive present: {bool(directive)}")
        
        if not directive:
            _debug("ERROR: No directive in event!")
            return _error_response("INVALID_DIRECTIVE", "Missing directive")
        
        # Step 2: Extract header
        _debug("\n--- STEP 2: Extract Header ---")
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        message_id = header.get('messageId', 'unknown')
        
        _debug(f"Namespace: {namespace}")
        _debug(f"Name: {name}")
        _debug(f"MessageId: {message_id}")
        _debug(f"PayloadVersion: {header.get('payloadVersion')}")
        
        # Step 3: Extract token
        _debug("\n--- STEP 3: Extract Bearer Token ---")
        scope = directive.get('payload', {}).get('scope')
        _debug(f"Scope present: {bool(scope)}")
        
        if scope:
            _debug(f"Scope type: {scope.get('type')}")
            token = scope.get('token')
            _debug(f"Token present: {bool(token)}")
            _debug(f"Token length: {len(token) if token else 0}")
        else:
            _debug("ERROR: No scope in payload!")
            return _error_response("INVALID_DIRECTIVE", "Missing scope", message_id)
        
        # Step 4: Load HA config
        _debug("\n--- STEP 4: Load HA Configuration ---")
        ha_url = os.getenv('HOME_ASSISTANT_URL')
        ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
        verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() != 'false'
        
        _debug(f"HA URL present: {bool(ha_url)}")
        _debug(f"HA URL: {ha_url}")
        _debug(f"Env token present: {bool(ha_token)}")
        _debug(f"Env token length: {len(ha_token) if ha_token else 0}")
        _debug(f"Verify SSL: {verify_ssl}")
        
        # Use token from event, fallback to env for debug
        final_token = token if token else ha_token
        _debug(f"Final token source: {'event' if token else 'environment'}")
        
        if not ha_url:
            _debug("ERROR: No HOME_ASSISTANT_URL!")
            return _error_response("BRIDGE_UNREACHABLE", "No HA URL configured", message_id)
        
        if not final_token:
            _debug("ERROR: No token available!")
            return _error_response("INVALID_AUTHORIZATION_CREDENTIAL", "No token", message_id)
        
        # Step 5: Build request
        _debug("\n--- STEP 5: Build HTTP Request ---")
        api_url = f"{ha_url}/api/alexa/smart_home"
        _debug(f"Target URL: {api_url}")
        
        cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
        _debug(f"SSL cert_reqs: {cert_reqs}")
        
        # Step 6: Create HTTP client
        _debug("\n--- STEP 6: Create HTTP Client ---")
        try:
            http = urllib3.PoolManager(
                cert_reqs=cert_reqs,
                timeout=urllib3.Timeout(connect=10.0, read=30.0),
                maxsize=5,
                retries=False
            )
            _debug("HTTP client created successfully")
        except Exception as e:
            _debug(f"ERROR creating HTTP client: {type(e).__name__}: {str(e)}")
            return _error_response("INTERNAL_ERROR", f"HTTP client error: {str(e)}", message_id)
        
        # Step 7: Prepare request body
        _debug("\n--- STEP 7: Prepare Request Body ---")
        body = json.dumps(event).encode('utf-8')
        _debug(f"Body length: {len(body)} bytes")
        _debug(f"Body preview: {body[:200]}")
        
        headers = {
            'Authorization': f'Bearer {final_token[:10]}...',
            'Content-Type': 'application/json'
        }
        _debug(f"Headers: {headers}")
        
        # Step 8: Make HTTP request
        _debug("\n--- STEP 8: Make HTTP Request to HA ---")
        _debug("Calling HA...")
        
        try:
            response = http.request(
                'POST',
                api_url,
                headers={
                    'Authorization': f'Bearer {final_token}',
                    'Content-Type': 'application/json'
                },
                body=body
            )
            _debug(f"Response received!")
            _debug(f"Status code: {response.status}")
            _debug(f"Response headers: {dict(response.headers)}")
            
        except urllib3.exceptions.SSLError as e:
            _debug(f"SSL ERROR: {str(e)}")
            _debug(f"Hint: Set HOME_ASSISTANT_VERIFY_SSL=false to disable SSL verification")
            return _error_response("BRIDGE_UNREACHABLE", f"SSL error: {str(e)}", message_id)
        except Exception as e:
            _debug(f"HTTP ERROR: {type(e).__name__}: {str(e)}")
            return _error_response("BRIDGE_UNREACHABLE", f"Connection error: {str(e)}", message_id)
        
        # Step 9: Parse response
        _debug("\n--- STEP 9: Parse HA Response ---")
        
        if response.status >= 400:
            error_body = response.data.decode('utf-8', errors='replace')
            _debug(f"ERROR response from HA: {error_body}")
            
            error_type = 'INVALID_AUTHORIZATION_CREDENTIAL' if response.status in (401, 403) else 'INTERNAL_ERROR'
            return _error_response(error_type, error_body, message_id)
        
        try:
            response_text = response.data.decode('utf-8')
            _debug(f"Response body length: {len(response_text)} bytes")
            
            response_json = json.loads(response_text)
            _debug(f"Response JSON keys: {list(response_json.keys())}")
            
            # Check for endpoints
            if 'event' in response_json:
                payload = response_json.get('event', {}).get('payload', {})
                endpoints = payload.get('endpoints', [])
                _debug(f"Discovery found {len(endpoints)} endpoints")
                
                for i, endpoint in enumerate(endpoints[:5]):  # Show first 5
                    _debug(f"  Endpoint {i+1}: {endpoint.get('friendlyName', 'Unknown')}")
            
            _debug("\n--- SUCCESS: Returning response to Alexa ---")
            return response_json
            
        except json.JSONDecodeError as e:
            _debug(f"JSON PARSE ERROR: {str(e)}")
            _debug(f"Response text: {response_text[:500]}")
            return _error_response("INTERNAL_ERROR", f"Invalid JSON from HA: {str(e)}", message_id)
    
    except Exception as e:
        _debug(f"\n!!! UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        _debug(f"Traceback:\n{traceback.format_exc()}")
        return _error_response("INTERNAL_ERROR", str(e))


def _error_response(error_type: str, message: str, message_id: str = 'error') -> Dict[str, Any]:
    """Create Alexa error response."""
    _debug(f"\n--- Creating Error Response ---")
    _debug(f"Error type: {error_type}")
    _debug(f"Error message: {message}")
    
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
