"""
lambda_function.py - AWS Lambda Entry Point
Version: 2025.10.18.10
Description: Main Lambda handler with SUGA-ISP gateway integration

CHANGELOG:
- 2025.10.18.10: Added Alexa.Authorization namespace routing to fix AcceptGrant
- 2025.10.18.01: Added ha_connection_test mode for HA connection diagnostics
- 2025.10.16.10: Added network connectivity test (ha_ping/network_test)
- 2025.10.16.09: Added SKIP_HA_HEALTH_CHECK environment variable option

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
import time
import urllib3
from typing import Dict, Any


# ===== LAMBDA MODE SELECTION =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point with mode selection.
    
    Modes:
    - normal: Full LEE operation (default)
    - failsafe: Direct HA passthrough via lambda_failsafe.py
    - diagnostic: Import testing via lambda_diagnostic.py
    - emergency: Emergency bypass via lambda_emergency.py
    - ha_connection_test: HA connection diagnostic via lambda_ha_connection.py
    """
    
    # Check Lambda mode
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    
    # Bypass modes - skip LEE entirely
    if lambda_mode == 'failsafe':
        try:
            import lambda_failsafe
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'diagnostic':
        try:
            import lambda_diagnostic
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'emergency':
        try:
            import lambda_emergency
            return lambda_emergency.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'ha_connection_test':
        try:
            import lambda_ha_connection
            return lambda_ha_connection.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    # Normal mode - full LEE operation
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    # Lazy import gateway functions
    from gateway import (
        log_info, log_error, log_debug,
        execute_operation, GatewayInterface,
        increment_counter, format_response,
        validate_request, validate_token
    )
    
    try:
        log_info("Lambda invocation started", 
                request_id=context.aws_request_id,
                function_name=context.function_name,
                memory_limit=context.memory_limit_in_mb,
                remaining_time=context.get_remaining_time_in_millis())
        
        increment_counter("lambda_invocations")
        
        # Determine request type
        request_type = determine_request_type(event)
        log_debug(f"Request type: {request_type}")
        
        # Route to appropriate handler
        if request_type == "alexa":
            return handle_alexa_request(event, context)
        elif request_type == "diagnostic":
            return handle_diagnostic_request(event, context)
        else:
            return format_response(400, {
                "error": "Unknown request type",
                "event": event
            })
            
    except Exception as e:
        log_error("Lambda execution failed", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def determine_request_type(event: Dict[str, Any]) -> str:
    """Determine the type of request from the event structure."""
    
    # Alexa Smart Home directive
    if "directive" in event:
        return "alexa"
    
    # Diagnostic/test request
    if "test_type" in event:
        return "diagnostic"
    
    # Default
    return "unknown"


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests."""
    
    # Lazy import gateway and HA extension
    from gateway import (
        log_info, log_error, log_warning, increment_counter,
        validate_request, validate_token
    )
    from homeassistant_extension import (
        handle_alexa_discovery,
        handle_alexa_control,
        handle_alexa_authorization,
        is_ha_extension_enabled,
        get_ha_status
    )
    
    try:
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        
        log_info(f"Alexa request: {namespace}.{name}")
        increment_counter(f"alexa_{namespace.lower()}")
        
        # Check HA availability
        if not is_ha_extension_enabled():
            log_error("Home Assistant extension not enabled")
            return create_alexa_error_response(
                event, 
                "BRIDGE_UNREACHABLE",
                "Home Assistant extension is not enabled"
            )
        
        # Optional: Skip health check if environment variable set
        skip_health_check = os.getenv('SKIP_HA_HEALTH_CHECK', 'false').lower() == 'true'
        
        if not skip_health_check:
            # Check HA connection status
            ha_status = get_ha_status()
            if not ha_status.get('success', False):
                log_warning("Home Assistant health check failed")
        
        # Route based on namespace
        if namespace == "Alexa.Discovery":
            return handle_alexa_discovery(event)
        
        elif namespace == "Alexa.Authorization":
            return handle_alexa_authorization(event)
        
        elif namespace in ["Alexa.PowerController", "Alexa.BrightnessController", 
                          "Alexa.ColorController", "Alexa.ThermostatController"]:
            return handle_alexa_control(event)
        
        else:
            log_error(f"Unknown Alexa namespace: {namespace}")
            return create_alexa_error_response(
                event,
                "INVALID_DIRECTIVE",
                f"Unknown namespace: {namespace}"
            )
            
    except Exception as e:
        log_error(f"Alexa request failed: {str(e)}", error=e)
        increment_counter("alexa_errors")
        return create_alexa_error_response(event, "INTERNAL_ERROR", str(e))


def handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostic/test requests."""
    
    test_type = event.get("test_type", "unknown")
    
    # Special network connectivity test - bypass all LEE systems
    if test_type in ['network_test', 'ha_ping']:
        return handle_network_test(event, context)
    
    # Standard diagnostic with gateway
    from gateway import (
        log_info, log_debug, log_error, increment_counter,
        format_response, execute_operation, GatewayInterface
    )
    
    try:
        log_info(f"Diagnostic request: {test_type}")
        increment_counter(f"diagnostic_{test_type}")
        
        response_data = {
            "timestamp": execute_operation(GatewayInterface.UTILITY, 'generate_uuid'),
            "test_type": test_type,
            "lambda_info": {
                "function_name": context.function_name,
                "function_version": context.function_version,
                "memory_limit": str(context.memory_limit_in_mb),
                "remaining_time": context.get_remaining_time_in_millis()
            }
        }
        
        # Add gateway stats
        if test_type in ["full", "configuration"]:
            response_data["gateway_stats"] = execute_operation(
                GatewayInterface.DEBUG, 
                'get_gateway_stats'
            )
        
        # Add Home Assistant diagnostic info
        if test_type == "full":
            try:
                from homeassistant_extension import get_ha_diagnostic_info
                response_data["home_assistant"] = get_ha_diagnostic_info()
            except Exception as e:
                log_error(f"Diagnostic info failed: {str(e)}")
                response_data["home_assistant"] = {}
        
        # Add environment info (sanitized)
        if test_type in ["full", "configuration"]:
            response_data["environment"] = {
                "HOME_ASSISTANT_URL": os.getenv("HOME_ASSISTANT_URL"),
                "HOME_ASSISTANT_TOKEN": "..." if os.getenv("HOME_ASSISTANT_TOKEN") else None,
                "HOME_ASSISTANT_ENABLED": os.getenv("HOME_ASSISTANT_ENABLED", "false"),
                "USE_PARAMETER_STORE": os.getenv("USE_PARAMETER_STORE", "false"),
                "DEBUG_MODE": os.getenv("DEBUG_MODE", "false"),
                "LAMBDA_MODE": os.getenv("LAMBDA_MODE", "normal")
            }
        
        return format_response(200, response_data)
        
    except Exception as e:
        log_error(f"Diagnostic failed: {str(e)}", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def handle_network_test(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Network connectivity test - bypasses all LEE systems.
    Direct urllib3 testing to HA.
    """
    
    print("[NETWORK TEST] Starting direct connectivity test")
    
    # Get HA config from environment
    ha_url = os.getenv('HOME_ASSISTANT_URL')
    ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
    
    if not ha_url or not ha_token:
        print("[NETWORK TEST] Missing HOME_ASSISTANT_URL or HOME_ASSISTANT_TOKEN")
        return {
            "statusCode": 400,
            "body": {"error": "Missing HA configuration"},
            "headers": {"Content-Type": "application/json"}
        }
    
    print(f"[NETWORK TEST] Testing connection to: {ha_url}")
    
    # Initialize results
    results = {
        "test_name": "Network Connectivity Test",
        "ha_url": ha_url,
        "tests": []
    }
    
    # Create HTTP client
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        timeout=urllib3.Timeout(connect=5.0, read=10.0),
        maxsize=5,
        retries=False
    )
    
    # Test 1: DNS Resolution
    dns_test = {"name": "DNS Resolution", "success": False, "details": {}}
    try:
        print(f"[NETWORK TEST] Testing DNS resolution for {ha_url}")
        import socket
        from urllib.parse import urlparse
        hostname = urlparse(ha_url).hostname
        ip_addr = socket.gethostbyname(hostname)
        dns_test["success"] = True
        dns_test["details"] = {"hostname": hostname, "ip_address": ip_addr}
        results["tests"].append(dns_test)
        print(f"[NETWORK TEST] ✓ DNS resolved: {hostname} -> {ip_addr}")
    except Exception as e:
        dns_test["error"] = str(e)
        dns_test["details"] = {"error_type": type(e).__name__}
        results["tests"].append(dns_test)
        print(f"[NETWORK TEST] ✗ DNS resolution failed: {str(e)}")
        return {"statusCode": 200, "body": results}
    
    # Test 2: HTTP Connection
    http_test = {"name": "HTTP Connection", "success": False, "details": {}}
    try:
        print(f"[NETWORK TEST] Testing HTTP connection")
        test_url = f"{ha_url}/api/"
        start_time = time.time()
        
        response = http.request(
            'GET',
            test_url,
            headers={'Content-Type': 'application/json'}
        )
        
        duration = (time.time() - start_time) * 1000
        
        http_test["success"] = True
        http_test["details"] = {
            "status_code": response.status,
            "duration_ms": duration,
            "can_reach_server": True
        }
        results["tests"].append(http_test)
        print(f"[NETWORK TEST] ✓ HTTP connection successful: {response.status} in {duration:.0f}ms")
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        http_test["error"] = str(e)
        http_test["details"] = {
            "duration_ms": duration,
            "can_reach_server": False,
            "error_type": type(e).__name__
        }
        results["tests"].append(http_test)
        print(f"[NETWORK TEST] ✗ HTTP connection failed: {str(e)}")
        return {"statusCode": 200, "body": results}
    
    # Test 3: Authenticated API call
    auth_test = {"name": "Authenticated API Test", "success": False, "details": {}}
    try:
        print(f"[NETWORK TEST] Testing authenticated API call")
        test_url = f"{ha_url}/api/"
        start_time = time.time()
        
        response = http.request(
            'GET',
            test_url,
            headers={
                'Authorization': f'Bearer {ha_token}',
                'Content-Type': 'application/json'
            }
        )
        
        duration = (time.time() - start_time) * 1000
        
        try:
            body = json.loads(response.data.decode('utf-8'))
        except:
            body = response.data.decode('utf-8')
        
        auth_test["success"] = response.status == 200
        auth_test["details"] = {
            "status_code": response.status,
            "duration_ms": duration,
            "response_body": body,
            "auth_working": response.status == 200
        }
        results["tests"].append(auth_test)
        print(f"[NETWORK TEST] ✓ Auth test: {response.status} in {duration:.0f}ms")
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        auth_test["error"] = str(e)
        auth_test["details"] = {
            "duration_ms": duration,
            "error_type": type(e).__name__
        }
        results["tests"].append(auth_test)
        print(f"[NETWORK TEST] ✗ Auth test failed: {str(e)}")
    
    # Test 4: Alexa Smart Home API endpoint
    alexa_api_test = {"name": "Alexa Smart Home API Test", "success": False, "details": {}}
    try:
        print(f"[NETWORK TEST] Testing Alexa Smart Home API endpoint")
        test_url = f"{ha_url}/api/alexa/smart_home"
        start_time = time.time()
        
        # Minimal discovery directive
        test_event = {
            "directive": {
                "header": {
                    "namespace": "Alexa.Discovery",
                    "name": "Discover",
                    "payloadVersion": "3",
                    "messageId": "network-test-msg"
                },
                "payload": {
                    "scope": {
                        "type": "BearerToken",
                        "token": ha_token
                    }
                }
            }
        }
        
        response = http.request(
            'POST',
            test_url,
            headers={
                'Authorization': f'Bearer {ha_token}',
                'Content-Type': 'application/json'
            },
            body=json.dumps(test_event).encode('utf-8')
        )
        
        duration = (time.time() - start_time) * 1000
        
        try:
            body = json.loads(response.data.decode('utf-8'))
            device_count = len(body.get('event', {}).get('payload', {}).get('endpoints', []))
        except:
            body = response.data.decode('utf-8')[:200]
            device_count = 0
        
        alexa_api_test["success"] = response.status == 200
        alexa_api_test["details"] = {
            "status_code": response.status,
            "duration_ms": duration,
            "devices_found": device_count,
            "response_preview": str(body)[:200]
        }
        results["tests"].append(alexa_api_test)
        print(f"[NETWORK TEST] ✓ Alexa API test: {response.status}, {device_count} devices in {duration:.0f}ms")
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        alexa_api_test["error"] = str(e)
        alexa_api_test["details"] = {
            "duration_ms": duration,
            "error_type": type(e).__name__
        }
        results["tests"].append(alexa_api_test)
        print(f"[NETWORK TEST] ✗ Alexa API test failed: {str(e)}")
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t.get("success"))
    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "all_passed": passed_tests == total_tests
    }
    
    print(f"[NETWORK TEST] Complete: {passed_tests}/{total_tests} tests passed")
    
    return {
        "statusCode": 200,
        "body": results,
        "headers": {
            "Content-Type": "application/json"
        }
    }


def create_alexa_error_response(event: Dict[str, Any], error_type: str, 
                                error_message: str) -> Dict[str, Any]:
    """Create Alexa-formatted error response."""
    
    directive = event.get("directive", {})
    header = directive.get("header", {})
    
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": header.get("messageId"),
                "correlationToken": header.get("correlationToken"),
                "payloadVersion": "3"
            },
            "endpoint": {},
            "payload": {
                "type": error_type,
                "message": error_message
            }
        }
    }

# EOF
