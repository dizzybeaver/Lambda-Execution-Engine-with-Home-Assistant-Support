"""
lambda_ha_connection.py - Home Assistant Connection Diagnostic Handler
Version: 2025.10.18.02
Description: Drop-in Lambda handler for diagnosing HA connection issues.
             Uses ONLY SUGA-ISP Gateway services to trace every step.
             
Usage: Deploy as Lambda handler to test HA connectivity.
       Every step shows [DEBUG] output even if successful.

CHANGELOG:
- 2025.10.18.02: FIXED Issue #30 - SSM parameter path fix
  - Changed from full paths '/lambda-execution-engine/homeassistant/*' to relative paths 'homeassistant/*'
  - Config system adds prefix automatically, full path caused double prefix
  - Fixes: 'object' object is not subscriptable error in step 2

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for HA connection diagnostics.
    
    Tests each layer:
    1. Gateway initialization
    2. Config loading (SSM)
    3. HTTP client state
    4. Circuit breaker state
    5. HA configuration
    6. Network connectivity
    7. Authentication
    8. API endpoint access
    
    Returns detailed diagnostic report with [DEBUG] logs for each step.
    """
    print("[DEBUG] ===== Lambda Handler Started =====")
    print(f"[DEBUG] Function: {context.function_name}")
    print(f"[DEBUG] Memory: {context.memory_limit_in_mb} MB")
    print(f"[DEBUG] Remaining time: {context.get_remaining_time_in_millis()} ms")
    print(f"[DEBUG] Event type: {event.get('test_type', 'unknown')}")
    
    # Initialize results dictionary
    results = {
        "test_name": "Home Assistant Connection Diagnostic",
        "timestamp": None,
        "steps": {}
    }
    
    # ===== STEP 1: Gateway Initialization =====
    print("\n[DEBUG] ===== STEP 1: Gateway Initialization =====")
    step1_result = test_gateway_initialization()
    results["steps"]["1_gateway_init"] = step1_result
    
    if not step1_result["success"]:
        print("[DEBUG] FAILURE: Gateway initialization failed, cannot continue")
        return format_diagnostic_response(results, 500)
    
    # Now we can import Gateway functions
    from gateway import (
        log_info, log_error, log_debug,
        generate_uuid, get_timestamp,
        execute_operation, GatewayInterface,
        create_success_response, create_error_response
    )
    
    results["timestamp"] = get_timestamp()
    
    # ===== STEP 2: Config Loading from SSM =====
    print("\n[DEBUG] ===== STEP 2: Config Loading (SSM Parameter Store) =====")
    step2_result = test_config_loading()
    results["steps"]["2_config_loading"] = step2_result
    
    # ===== STEP 3: HTTP Client State =====
    print("\n[DEBUG] ===== STEP 3: HTTP Client State =====")
    step3_result = test_http_client_state()
    results["steps"]["3_http_client"] = step3_result
    
    # ===== STEP 4: Circuit Breaker State =====
    print("\n[DEBUG] ===== STEP 4: Circuit Breaker State =====")
    step4_result = test_circuit_breaker_state()
    results["steps"]["4_circuit_breaker"] = step4_result
    
    # ===== STEP 5: HA Configuration =====
    print("\n[DEBUG] ===== STEP 5: Home Assistant Configuration =====")
    step5_result = test_ha_configuration()
    results["steps"]["5_ha_config"] = step5_result
    
    if not step5_result["success"]:
        print("[DEBUG] FAILURE: HA configuration failed, cannot test connection")
        return format_diagnostic_response(results, 500)
    
    # ===== STEP 6: Network Connectivity Test =====
    print("\n[DEBUG] ===== STEP 6: Network Connectivity Test =====")
    step6_result = test_network_connectivity(step5_result["data"])
    results["steps"]["6_network_test"] = step6_result
    
    # ===== STEP 7: Authentication Test =====
    print("\n[DEBUG] ===== STEP 7: Authentication Test =====")
    step7_result = test_authentication(step5_result["data"])
    results["steps"]["7_authentication"] = step7_result
    
    # ===== STEP 8: API Endpoint Test =====
    print("\n[DEBUG] ===== STEP 8: API Endpoint Test =====")
    step8_result = test_api_endpoint(step5_result["data"])
    results["steps"]["8_api_endpoint"] = step8_result
    
    # ===== FINAL SUMMARY =====
    print("\n[DEBUG] ===== DIAGNOSTIC SUMMARY =====")
    results["summary"] = generate_summary(results["steps"])
    print_summary(results["summary"])
    
    status_code = 200 if results["summary"]["all_passed"] else 500
    return format_diagnostic_response(results, status_code)


def test_gateway_initialization() -> Dict[str, Any]:
    """Test Gateway initialization and basic functionality."""
    try:
        print("[DEBUG] Attempting to import Gateway...")
        from gateway import execute_operation, GatewayInterface
        print("[DEBUG] ✓ Gateway imported successfully")
        
        print("[DEBUG] Testing Gateway utility functions...")
        uuid = execute_operation(GatewayInterface.UTILITY, 'generate_uuid')
        print(f"[DEBUG] ✓ Generated UUID: {uuid}")
        
        timestamp = execute_operation(GatewayInterface.UTILITY, 'get_timestamp')
        print(f"[DEBUG] ✓ Generated timestamp: {timestamp}")
        
        print("[DEBUG] Testing Gateway logging...")
        execute_operation(GatewayInterface.LOGGING, 'log_info', 
                         message="Gateway diagnostic test started")
        print("[DEBUG] ✓ Logging functional")
        
        print("[DEBUG] SUCCESS: Gateway fully operational")
        return {
            "success": True,
            "message": "Gateway initialized and functional",
            "details": {
                "uuid": uuid,
                "timestamp": timestamp
            }
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: Gateway initialization error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_config_loading() -> Dict[str, Any]:
    """Test configuration loading from SSM Parameter Store."""
    try:
        from gateway import execute_operation, GatewayInterface, log_debug
        
        use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
        print(f"[DEBUG] USE_PARAMETER_STORE: {use_ssm}")
        
        if use_ssm:
            print("[DEBUG] Testing SSM Parameter Store access...")
            
            # FIXED: Use relative paths - config system adds prefix automatically
            # Test loading HA URL from SSM
            print("[DEBUG] Loading homeassistant/url...")
            ha_url = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='homeassistant/url'  # FIXED: Removed prefix
            )
            
            if ha_url:
                print(f"[DEBUG] ✓ Loaded HA URL from SSM: {ha_url}")
            else:
                print("[DEBUG] ⚠ HA URL not found in SSM, checking environment...")
                ha_url = os.getenv('HOME_ASSISTANT_URL')
                print(f"[DEBUG] Environment HA URL: {ha_url}")
            
            # FIXED: Use relative path for token too
            # Test loading HA token from SSM  
            print("[DEBUG] Loading homeassistant/token...")
            ha_token = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='homeassistant/token'  # FIXED: Removed prefix
            )
            
            if ha_token:
                print(f"[DEBUG] ✓ Loaded HA token from SSM: {ha_token[:10]}...")
            else:
                print("[DEBUG] ⚠ HA token not found in SSM, checking environment...")
                ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
                if ha_token:
                    print(f"[DEBUG] Environment HA token: {ha_token[:10]}...")
            
            print("[DEBUG] SUCCESS: Config loading functional")
            return {
                "success": True,
                "message": "Configuration loaded successfully",
                "details": {
                    "using_ssm": True,
                    "ha_url_loaded": ha_url is not None,
                    "ha_token_loaded": ha_token is not None,
                    "ha_url": ha_url if ha_url else "Not loaded"
                }
            }
        else:
            print("[DEBUG] SSM not enabled, using environment variables only")
            ha_url = os.getenv('HOME_ASSISTANT_URL')
            ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
            
            print(f"[DEBUG] Environment HA URL: {ha_url}")
            print(f"[DEBUG] Environment HA token: {'Present' if ha_token else 'Missing'}")
            
            return {
                "success": True,
                "message": "Using environment variables (SSM disabled)",
                "details": {
                    "using_ssm": False,
                    "ha_url": ha_url,
                    "ha_token_present": ha_token is not None
                }
            }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: Config loading error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_http_client_state() -> Dict[str, Any]:
    """Test HTTP client state and readiness."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        print("[DEBUG] Getting HTTP client state...")
        state = execute_operation(GatewayInterface.HTTP_CLIENT, 'get_state')
        
        print(f"[DEBUG] HTTP client state: {json.dumps(state, indent=2)}")
        print(f"[DEBUG] ✓ Total requests: {state.get('requests', 0)}")
        print(f"[DEBUG] ✓ Successful: {state.get('successful', 0)}")
        print(f"[DEBUG] ✓ Failed: {state.get('failed', 0)}")
        
        print("[DEBUG] SUCCESS: HTTP client operational")
        return {
            "success": True,
            "message": "HTTP client operational",
            "data": state
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: HTTP client error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_circuit_breaker_state() -> Dict[str, Any]:
    """Test circuit breaker state."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        print("[DEBUG] Getting circuit breaker state for 'home_assistant'...")
        state = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'get',
            name='home_assistant'
        )
        
        print(f"[DEBUG] Circuit breaker state: {json.dumps(state, indent=2)}")
        print(f"[DEBUG] ✓ State: {state.get('state', 'unknown')}")
        print(f"[DEBUG] ✓ Failures: {state.get('failures', 0)}")
        print(f"[DEBUG] ✓ Threshold: {state.get('threshold', 0)}")
        
        is_open = state.get('state') == 'open'
        if is_open:
            print("[DEBUG] ⚠ WARNING: Circuit breaker is OPEN (blocking requests)")
        else:
            print("[DEBUG] ✓ Circuit breaker is CLOSED (allowing requests)")
        
        print("[DEBUG] SUCCESS: Circuit breaker operational")
        return {
            "success": True,
            "message": "Circuit breaker operational",
            "data": state,
            "is_blocking": is_open
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: Circuit breaker error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_ha_configuration() -> Dict[str, Any]:
    """Test Home Assistant configuration loading."""
    try:
        print("[DEBUG] Importing HA facade...")
        from homeassistant_extension import is_ha_extension_enabled
        
        enabled = is_ha_extension_enabled()
        print(f"[DEBUG] HA Extension enabled: {enabled}")
        
        if not enabled:
            print("[DEBUG] FAILURE: HA extension is disabled")
            return {
                "success": False,
                "error": "Home Assistant extension is disabled",
                "details": {"enabled": False}
            }
        
        print("[DEBUG] Loading HA configuration...")
        from ha_core import get_ha_config
        config = get_ha_config()
        
        print(f"[DEBUG] HA Config: {json.dumps({
            'enabled': config.get('enabled'),
            'base_url': config.get('base_url'),
            'has_token': config.get('access_token') is not None,
            'timeout': config.get('timeout'),
            'assistant_name': config.get('assistant_name')
        }, indent=2)}")
        
        if not config.get('enabled'):
            print("[DEBUG] FAILURE: HA is disabled in configuration")
            return {
                "success": False,
                "error": "Home Assistant disabled in configuration",
                "data": config
            }
        
        if not config.get('base_url'):
            print("[DEBUG] FAILURE: HA base URL not configured")
            return {
                "success": False,
                "error": "Home Assistant base URL not configured",
                "data": config
            }
        
        if not config.get('access_token'):
            print("[DEBUG] FAILURE: HA access token not configured")
            return {
                "success": False,
                "error": "Home Assistant access token not configured",
                "data": config
            }
        
        print("[DEBUG] ✓ HA enabled: True")
        print(f"[DEBUG] ✓ Base URL: {config.get('base_url')}")
        print(f"[DEBUG] ✓ Token: {config.get('access_token')[:10]}...")
        print(f"[DEBUG] ✓ Timeout: {config.get('timeout')} seconds")
        print(f"[DEBUG] ✓ Assistant name: {config.get('assistant_name')}")
        
        print("[DEBUG] SUCCESS: HA configuration valid")
        return {
            "success": True,
            "message": "HA configuration valid",
            "data": config
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: HA configuration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_network_connectivity(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test basic network connectivity to HA instance."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        base_url = config.get('base_url')
        print(f"[DEBUG] Testing network connectivity to: {base_url}")
        
        print("[DEBUG] Making HTTP GET request to /api/ (no auth)...")
        result = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            'get',
            url=f"{base_url}/api/",
            timeout=10
        )
        
        print(f"[DEBUG] HTTP Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"[DEBUG] ✓ Network reachable")
            print(f"[DEBUG] ✓ Status code: {result.get('status_code')}")
            print(f"[DEBUG] ✓ Response data: {result.get('data')}")
            print("[DEBUG] SUCCESS: Network connectivity confirmed")
            return {
                "success": True,
                "message": "Network connectivity successful",
                "data": result
            }
        else:
            print(f"[DEBUG] ⚠ Network request failed")
            print(f"[DEBUG] Error: {result.get('error')}")
            print(f"[DEBUG] Error type: {result.get('error_type')}")
            
            # Still return success if we got an error because network is reachable
            # (401 means network works, just auth failed)
            if result.get('status_code') in [401, 403]:
                print("[DEBUG] ⚠ Auth error (expected at this step)")
                print("[DEBUG] SUCCESS: Network reachable (auth will be tested next)")
                return {
                    "success": True,
                    "message": "Network reachable (auth error expected)",
                    "data": result
                }
            
            print("[DEBUG] FAILURE: Network unreachable")
            return {
                "success": False,
                "error": result.get('error'),
                "data": result
            }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: Network test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_authentication(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test authentication with HA API."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        base_url = config.get('base_url')
        token = config.get('access_token')
        
        print(f"[DEBUG] Testing authentication to: {base_url}/api/")
        print(f"[DEBUG] Using token: {token[:10]}...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"[DEBUG] Headers: {json.dumps({'Authorization': f'Bearer {token[:10]}...', 'Content-Type': 'application/json'})}")
        print("[DEBUG] Making authenticated HTTP GET request to /api/...")
        
        result = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            'get',
            url=f"{base_url}/api/",
            headers=headers,
            timeout=10
        )
        
        print(f"[DEBUG] HTTP Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            status_code = result.get('status_code')
            print(f"[DEBUG] ✓ Status code: {status_code}")
            
            if 200 <= status_code < 300:
                print(f"[DEBUG] ✓ Authentication successful")
                print(f"[DEBUG] ✓ Response: {result.get('data')}")
                print("[DEBUG] SUCCESS: Authentication confirmed")
                return {
                    "success": True,
                    "message": "Authentication successful",
                    "data": result
                }
            else:
                print(f"[DEBUG] ⚠ Unexpected status code: {status_code}")
                print("[DEBUG] FAILURE: Authentication may have failed")
                return {
                    "success": False,
                    "error": f"Unexpected status code: {status_code}",
                    "data": result
                }
        else:
            status_code = result.get('status_code')
            error = result.get('error')
            
            print(f"[DEBUG] Request failed")
            print(f"[DEBUG] Status code: {status_code}")
            print(f"[DEBUG] Error: {error}")
            
            if status_code == 401:
                print("[DEBUG] FAILURE: Authentication failed - invalid token (401)")
                return {
                    "success": False,
                    "error": "Authentication failed - invalid token (401)",
                    "data": result
                }
            elif status_code == 403:
                print("[DEBUG] FAILURE: Authentication failed - forbidden (403)")
                return {
                    "success": False,
                    "error": "Authentication failed - forbidden (403)",
                    "data": result
                }
            else:
                print(f"[DEBUG] FAILURE: Request failed with status {status_code}")
                return {
                    "success": False,
                    "error": error,
                    "data": result
                }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: Authentication test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_api_endpoint(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test full API endpoint through HA core."""
    try:
        print("[DEBUG] Testing full API call through HA core...")
        from ha_core import call_ha_api
        
        print("[DEBUG] Calling call_ha_api('/api/')...")
        result = call_ha_api('/api/')
        
        print(f"[DEBUG] Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"[DEBUG] ✓ API call successful")
            print(f"[DEBUG] ✓ Response: {result.get('data')}")
            print("[DEBUG] SUCCESS: API endpoint accessible")
            return {
                "success": True,
                "message": "API endpoint accessible",
                "data": result
            }
        else:
            print(f"[DEBUG] ⚠ API call failed")
            print(f"[DEBUG] Error: {result.get('error')}")
            print(f"[DEBUG] Error code: {result.get('error_code')}")
            print("[DEBUG] FAILURE: API endpoint test failed")
            return {
                "success": False,
                "error": result.get('error'),
                "data": result
            }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: API endpoint test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def generate_summary(steps: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary of all test results."""
    total = len(steps)
    passed = sum(1 for step in steps.values() if step.get('success'))
    failed = total - passed
    
    failed_steps = [
        name for name, result in steps.items() 
        if not result.get('success')
    ]
    
    return {
        "total_steps": total,
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0,
        "failed_steps": failed_steps,
        "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
    }


def print_summary(summary: Dict[str, Any]):
    """Print diagnostic summary to logs."""
    print(f"[DEBUG] Total steps: {summary['total_steps']}")
    print(f"[DEBUG] Passed: {summary['passed']}")
    print(f"[DEBUG] Failed: {summary['failed']}")
    print(f"[DEBUG] Success rate: {summary['success_rate']}")
    
    if summary['all_passed']:
        print("[DEBUG] ✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print(f"[DEBUG] ✗✗✗ TESTS FAILED ✗✗✗")
        print(f"[DEBUG] Failed steps: {', '.join(summary['failed_steps'])}")


def format_diagnostic_response(results: Dict[str, Any], status_code: int) -> Dict[str, Any]:
    """Format final diagnostic response."""
    return {
        "statusCode": status_code,
        "body": json.dumps(results, indent=2),
        "headers": {
            "Content-Type": "application/json"
        }
    }


# EOF
