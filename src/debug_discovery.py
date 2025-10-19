"""
debug_discovery.py - Alexa Discovery Debug Tracer (SELECTIVE IMPORTS)
Version: 2025.10.19.SELECTIVE
Description: Traces every step of Alexa discovery using preloaded urllib3

CRITICAL CHANGE: Uses preloaded urllib3 from lambda_preload
- NO `import urllib3` in function (was causing 1,700ms delay!)
- Uses PoolManager and Timeout from lambda_preload (already loaded)

Performance: HTTP client creation in ~0ms (urllib3 preloaded!)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
from typing import Dict, Any

# Import preloaded urllib3 classes (already initialized during Lambda INIT!)
from lambda_preload import PoolManager, Timeout


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
            token = os.getenv('HOME_ASSISTANT_TOKEN')
            _debug(f"Using fallback token from env: {bool(token)}")
        
        # Step 4: Get Home Assistant URL
        _debug("\n--- STEP 4: Get Home Assistant Config ---")
        ha_url = os.getenv('HOME_ASSISTANT_URL')
        _debug(f"HA URL: {ha_url}")
        
        if not ha_url:
            _debug("ERROR: No HOME_ASSISTANT_URL configured!")
            return _error_response("INVALID_CONFIGURATION", "HOME_ASSISTANT_URL not set")
        
        # Step 5: Create HTTP client (uses preloaded urllib3!)
        _debug("\n--- STEP 5: Create HTTP Client ---")
        _debug("Using preloaded urllib3 from lambda_preload...")
        
        verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() != 'false'
        cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
        _debug(f"SSL verification: {verify_ssl}")
        _debug(f"Cert requirements: {cert_reqs}")
        
        # Use preloaded classes (NO IMPORT OVERHEAD!)
        http = PoolManager(
            cert_reqs=cert_reqs,
            timeout=Timeout(connect=10.0, read=30.0),
            maxsize=5,
            retries=False
        )
        _debug("HTTP client created successfully")
        
        # Step 6: Make request
        _debug("\n--- STEP 6: Make HTTP Request ---")
        api_endpoint = f"{ha_url}/api/alexa/smart_home"
        _debug(f"API endpoint: {api_endpoint}")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        _debug(f"Headers: Authorization=Bearer *****, Content-Type={headers['Content-Type']}")
        
        body = json.dumps(event).encode('utf-8')
        _debug(f"Body length: {len(body)} bytes")
        
        _debug("Sending POST request...")
        response = http.request(
            'POST',
            api_endpoint,
            headers=headers,
            body=body
        )
        
        _debug(f"Response status: {response.status}")
        _debug(f"Response headers: {dict(response.headers)}")
        
        # Step 7: Parse response
        _debug("\n--- STEP 7: Parse Response ---")
        
        if response.status != 200:
            _debug(f"ERROR: Non-200 status code: {response.status}")
            return _error_response("INTERNAL_ERROR", f"Home Assistant returned {response.status}")
        
        response_data = json.loads(response.data.decode('utf-8'))
        _debug(f"Response parsed successfully")
        _debug(f"Response keys: {list(response_data.keys())}")
        
        # Extract endpoints if discovery
        if 'event' in response_data:
            event_data = response_data['event']
            if 'payload' in event_data and 'endpoints' in event_data['payload']:
                endpoints = event_data['payload']['endpoints']
                _debug(f"Discovered {len(endpoints)} endpoints")
                for i, endpoint in enumerate(endpoints):
                    _debug(f"  Endpoint {i+1}: {endpoint.get('friendlyName', 'Unknown')}")
        
        _debug("\n═══════════════════════════════════════════════════")
        _debug("DEBUG_DISCOVERY: Success!")
        _debug("═══════════════════════════════════════════════════")
        
        return response_data
        
    except Exception as e:
        _debug(f"\n!!! EXCEPTION: {str(e)}")
        _debug(f"Exception type: {type(e).__name__}")
        import traceback
        _debug(f"Traceback:\n{traceback.format_exc()}")
        return _error_response("INTERNAL_ERROR", str(e))


def _error_response(error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': 'error',
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


# EOF
