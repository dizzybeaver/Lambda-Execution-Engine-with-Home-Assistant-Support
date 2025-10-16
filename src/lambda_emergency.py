"""
lambda_function.py - EMERGENCY BYPASS VERSION
Version: 2025.10.15.EMERGENCY
Description: Minimal handler to test if Lambda works without gateway
"""

import json
import os
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Emergency bypass handler - NO gateway imports at all.
    """
    
    # Print directly - bypass all systems
    print(f"[EMERGENCY] Lambda invoked!")
    print(f"[EMERGENCY] Event: {json.dumps(event)}")
    print(f"[EMERGENCY] Request ID: {context.aws_request_id}")
    print(f"[EMERGENCY] Memory limit: {context.memory_limit_in_mb}MB")
    print(f"[EMERGENCY] Remaining time: {context.get_remaining_time_in_millis()}ms")
    
    # Determine request type
    request_type = 'unknown'
    if 'test_type' in event:
        request_type = 'diagnostic'
        test_type = event.get('test_type')
        print(f"[EMERGENCY] Test type: {test_type}")
    elif 'health_check' in event:
        request_type = 'health_check'
    
    print(f"[EMERGENCY] Request type: {request_type}")
    
    # Return immediately - no processing
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "status": "emergency_bypass_active",
            "message": "Lambda is running but gateway disabled",
            "request_type": request_type,
            "request_id": context.aws_request_id,
            "memory_limit_mb": context.memory_limit_in_mb,
            "remaining_time_ms": context.get_remaining_time_in_millis(),
            "event": event
        })
    }
    
    print(f"[EMERGENCY] Response: {json.dumps(response)}")
    print(f"[EMERGENCY] Handler complete!")
    
    return response

# EOF
