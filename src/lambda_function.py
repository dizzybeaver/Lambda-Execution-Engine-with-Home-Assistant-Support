"""
lambda_function.py - UPDATED: Main Lambda Function Handler with Gateway Interface Integration
Version: 2025.09.27.01
Description: Main Lambda function handler updated to use gateway interface functions

GATEWAY INTERFACE INTEGRATION:
- ✅ UPDATED: Uses gateway interface functions for all operations
- ✅ OPTIMIZED: Direct gateway function calls for maximum efficiency
- ✅ COMPLIANT: Follows PROJECT_ARCHITECTURE_REFERENCE.md patterns
- ✅ STREAMLINED: Clean imports and function usage

GATEWAY INTERFACE USAGE:
- lambda.py: alexa_lambda_handler, create_alexa_response, lambda_handler_with_gateway, get_lambda_status
- http_client.py: make_request, get_http_status, get_aws_client
- circuit_breaker.py: get_circuit_breaker, circuit_breaker_call, get_circuit_breaker_status, reset_circuit_breaker
- utility.py: validate_string_input, create_success_response, create_error_response, get_current_timestamp
- initialization.py: unified_lambda_initialization, unified_lambda_cleanup, get_initialization_status

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
import logging
from typing import Dict, Any, Optional

# Ultra-optimized gateway imports 
from lambda import alexa_lambda_handler, create_alexa_response, lambda_handler_with_gateway, get_lambda_status
from http_client import make_request, get_http_status, get_aws_client
from circuit_breaker import get_circuit_breaker, circuit_breaker_call, get_circuit_breaker_status, reset_circuit_breaker
from initialization import unified_lambda_initialization, unified_lambda_cleanup, get_initialization_status, get_free_tier_memory_status
from utility import validate_string_input, create_success_response, create_error_response, sanitize_response_data, get_current_timestamp
from logging import log_info, log_error
from metrics import record_metric
from security import validate_request

logger = logging.getLogger(__name__)

# ===== SECTION 1: MAIN LAMBDA HANDLER =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda function handler - Ultra-optimized with gateway interfaces.
    
    Uses gateway interface functions for maximum efficiency and compliance.
    Supports Alexa, HTTP, and generic Lambda events with circuit breaker protection.
    """
    try:
        # Initialize Lambda if needed
        init_result = unified_lambda_initialization()
        if not init_result.get("success", False):
            log_error("Lambda initialization failed", {"error": init_result.get("error")})
            return create_error_response("Initialization failed")
        
        # Generate correlation ID for request tracking
        correlation_id = get_current_timestamp()
        
        # Validate request security
        if not validate_request(event):
            log_error("Request validation failed", {"correlation_id": correlation_id})
            return create_error_response("Request validation failed", "SECURITY_ERROR")
        
        # Determine event type and route to appropriate handler
        if "request" in event and "type" in event.get("request", {}):
            # Alexa event
            log_info("Processing Alexa event", {"correlation_id": correlation_id})
            
            # Use circuit breaker for Alexa handling
            result = circuit_breaker_call(
                "alexa_handler",
                alexa_lambda_handler,
                event=event,
                context=context
            )
            
            record_metric("alexa_requests_processed", 1.0)
            return result if result else create_error_response("Alexa handler failed")
            
        elif "httpMethod" in event or "requestContext" in event:
            # API Gateway/HTTP event
            log_info("Processing HTTP event", {"correlation_id": correlation_id})
            
            # Use circuit breaker for HTTP handling
            result = circuit_breaker_call(
                "http_handler", 
                lambda_handler_with_gateway,
                event=event,
                context=context
            )
            
            record_metric("http_requests_processed", 1.0)
            return result if result else create_error_response("HTTP handler failed")
            
        else:
            # Generic Lambda event
            log_info("Processing generic Lambda event", {"correlation_id": correlation_id})
            
            result = lambda_handler_with_gateway(event, context)
            record_metric("lambda_requests_processed", 1.0)
            return result if result else create_error_response("Lambda handler failed")
            
    except Exception as e:
        log_error("Lambda handler error", {"error": str(e)}, exc_info=True)
        record_metric("lambda_handler_errors", 1.0)
        return create_error_response(f"Internal error: {str(e)}")

# ===== SECTION 2: HEALTH CHECK HANDLER =====

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check handler using gateway interfaces.
    """
    try:
        correlation_id = get_current_timestamp()
        
        # Check Lambda status
        lambda_status = get_lambda_status()
        
        # Check HTTP client status  
        http_status = get_http_status()
        
        # Check circuit breaker status
        cb_status = get_circuit_breaker_status()
        
        # Check initialization status
        init_status = get_initialization_status()
        
        health_result = {
            "healthy": True,
            "lambda": lambda_status,
            "http_client": http_status,
            "circuit_breakers": cb_status,
            "initialization": init_status,
            "correlation_id": correlation_id
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Correlation-ID": correlation_id
            },
            "body": json.dumps(health_result)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "healthy": False,
                "message": f"Health check failed: {str(e)}"
            })
        }

# ===== SECTION 3: WARMUP HANDLER =====

def warmup_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Warmup handler using gateway interfaces.
    """
    try:
        correlation_id = get_current_timestamp()
        
        # Perform warmup operations
        lambda_warmup = get_lambda_status()
        
        # Warm up HTTP client
        http_status = get_http_status()
        
        # Initialize circuit breakers
        cb_status = get_circuit_breaker_status()
        
        warmup_result = {
            "warmed_up": True,
            "lambda": lambda_warmup,
            "http_client": http_status,
            "circuit_breakers": cb_status,
            "correlation_id": correlation_id
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Correlation-ID": correlation_id
            },
            "body": json.dumps(warmup_result)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "warmed_up": False,
                "message": f"Warmup failed: {str(e)}"
            })
        }

# ===== SECTION 4: DEMONSTRATION FUNCTIONS =====

def demo_ultra_optimized_operations():
    """
    Demonstration of gateway interface operations.
    Shows usage of gateway interface functions.
    """
    
    # Example 1: HTTP operation
    http_response = make_request(
        method="GET",
        url="https://httpbin.org/get",
        headers={"User-Agent": "Lambda-Ultra-Optimized/1.0"},
        timeout=10
    )
    
    # Example 2: Circuit breaker operation
    protected_result = circuit_breaker_call(
        name="demo_service",
        func=lambda: {"demo": "success"}
    )
    
    # Example 3: Alexa response creation
    alexa_response = create_alexa_response(
        response_type="simple",
        speech_text="This is an ultra-optimized response!",
        should_end_session=True
    )
    
    return {
        "http_demo": http_response,
        "circuit_breaker_demo": protected_result,
        "alexa_demo": alexa_response,
        "message": "Gateway interface operations completed successfully!"
    }

# ===== SECTION 5: MODULE EXPORTS =====

__all__ = [
    # Main handlers
    'lambda_handler',
    'health_check_handler',
    'warmup_handler',
    
    # Demo function
    'demo_ultra_optimized_operations'
]

# EOF
