"""
lambda_ha_connection.py - Home Assistant Connection Diagnostic Handler
Version: 2025.10.18.08
Description: Drop-in Lambda handler for diagnosing HA connection issues.
             Uses ONLY SUGA-ISP Gateway services to trace every step.
             Enhanced with config_param_store module testing.
             
Usage: Deploy as Lambda handler to test HA connectivity.
       Every step shows [DEBUG] output even if successful.

CHANGELOG:
- 2025.10.18.08: ENHANCED SSM diagnostics with config_param_store testing
  - Added direct config_param_store module testing in step 2
  - Tests both direct SSM access and via gateway
  - Compares results to ensure consistency
  - Enhanced error logging with type information
  - Helps diagnose boto3 object wrapper issues
- 2025.10.18.02: FIXED Issue #30 - SSM parameter path fix
  - Changed from full paths '/lambda-execution-engine/homeassistant/*' to relative paths
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
    2. Config loading (SSM with enhanced debugging)
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
    
    # ===== STEP 2: Config Loading from SSM (Enhanced) =====
    print("\n[DEBUG] ===== STEP 2: Config Loading (SSM Parameter Store - Enhanced) =====")
    step2_result = test_config_loading_enhanced()
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


def test_config_loading_enhanced() -> Dict[str, Any]:
    """
    Test configuration loading from SSM Parameter Store with enhanced debugging.
    
    Tests multiple access methods:
    1. Direct config_param_store module access
    2. Via gateway CONFIG interface
    3. Compares results for consistency
    """
    try:
        from gateway import execute_operation, GatewayInterface, log_debug
        
        use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
        print(f"[DEBUG] USE_PARAMETER_STORE: {use_ssm}")
        
        if use_ssm:
            print("[DEBUG] Testing SSM Parameter Store access with enhanced diagnostics...")
            
            # Strategy 1: Direct config_param_store module test
            print("\n[DEBUG] --- Strategy 1: Direct config_param_store Module ---")
            try:
                from config import config_param_store
                print("[DEBUG] ✓ config_param_store module imported")
                
                # Test URL loading directly
                print("[DEBUG] Testing: config_param_store.get_parameter('homeassistant/url')")
                direct_url = config_param_store.get_parameter('homeassistant/url')
                print(f"[DEBUG] Direct module returned:")
                print(f"[DEBUG]   Type: {type(direct_url)}")
                print(f"[DEBUG]   Value: {direct_url}")
                print(f"[DEBUG]   Length: {len(str(direct_url)) if direct_url else 0}")
                
                # Test token loading directly
                print("[DEBUG] Testing: config_param_store.get_parameter('homeassistant/token')")
                direct_token = config_param_store.get_parameter('homeassistant/token')
                print(f"[DEBUG] Direct module returned:")
                print(f"[DEBUG]   Type: {type(direct_token)}")
                print(f"[DEBUG]   Value: {direct_token[:20] if direct_token else 'None'}...")
                print(f"[DEBUG]   Length: {len(str(direct_token)) if direct_token else 0}")
                
            except Exception as e:
                print(f"[DEBUG] ✗ Direct module access failed: {e}")
                print(f"[DEBUG]   Error type: {type(e).__name__}")
                direct_url = None
                direct_token = None
            
            # Strategy 2: Via Gateway CONFIG interface
            print("\n[DEBUG] --- Strategy 2: Via Gateway CONFIG Interface ---")
            print("[DEBUG] Loading homeassistant/url via gateway...")
            ha_url = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='homeassistant/url'
            )
            print(f"[DEBUG] Gateway returned:")
            print(f"[DEBUG]   Type: {type(ha_url)}")
            print(f"[DEBUG]   Value: {ha_url}")
            
            print("[DEBUG] Loading homeassistant/token via gateway...")
            ha_token = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='homeassistant/token'
            )
            print(f"[DEBUG] Gateway returned:")
            print(f"[DEBUG]   Type: {type(ha_token)}")
            print(f"[DEBUG]   Value: {ha_token[:20] if ha_token else 'None'}...")
            
            # Strategy 3: Compare results
            print("\n[DEBUG] --- Strategy 3: Result Comparison ---")
            if direct_url is not None:
                if direct_url == ha_url:
                    print("[DEBUG] ✓ Direct and gateway URL values match")
                else:
                    print("[DEBUG] ✗ Direct and gateway URL values DIFFER!")
                    print(f"[DEBUG]   Direct:  {direct_url}")
                    print(f"[DEBUG]   Gateway: {ha_url}")
            
            # Validate results
            if ha_url and ha_token:
                print(f"\n[DEBUG] ✓ Loaded HA URL from SSM: {ha_url}")
                print(f"[DEBUG] ✓ Loaded HA token from SSM: {ha_token[:10]}...")
                print("[DEBUG] SUCCESS: Config loading functional")
                
                return {
                    "success": True,
                    "message": "Configuration loaded successfully from SSM",
                    "details": {
                        "using_ssm": True,
                        "ha_url_loaded": ha_url is not None,
                        "ha_token_loaded": ha_token is not None,
                        "ha_url": ha_url,
                        "ha_url_type": str(type(ha_url)),
                        "direct_module_test": direct_url is not None,
                        "results_match": direct_url == ha_url if direct_url else None
                    }
                }
            else:
                print("[DEBUG] ✗ Failed to load one or more parameters")
                print("[DEBUG] Falling back to environment variables...")
                
                ha_url = os.getenv('HOME_ASSISTANT_URL')
                ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
                
                return {
                    "success": True if ha_url and ha_token else False,
                    "message": "SSM failed, using environment variables" if ha_url else "Configuration not available",
                    "details": {
                        "using_ssm": False,
                        "ha_url": ha_url,
                        "ha_token_present": ha_token is not None
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
        print(f"[DEBUG] Error type: {type(e).__name__}")
        import traceback
        print(f"[DEBUG] Traceback:")
        traceback.print_exc()
        
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
        state = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            'get_state'
        )
        
        print(f"[DEBUG] HTTP client state: {json.dumps(state, indent=2)}")
        
        # Check state fields
        if 'exists' in state:
            print(f"[DEBUG] ✓ Total requests: {state.get('total_requests', 0)}")
            print(f"[DEBUG] ✓ Successful: {state.get('successful_requests', 0)}")
            print(f"[DEBUG] ✓ Failed: {state.get('failed_requests', 0)}")
        
        print("[DEBUG] SUCCESS: HTTP client operational")
        return {
            "success": True,
            "message": "HTTP client operational",
            "data": state
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: HTTP client state error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_circuit_breaker_state() -> Dict[str, Any]:
    """Test circuit breaker state."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        breaker_name = 'home_assistant'
        print(f"[DEBUG] Getting circuit breaker state for '{breaker_name}'...")
        
        state = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'get',
            name=breaker_name
        )
        
        print(f"[DEBUG] Circuit breaker state: {json.dumps(state, indent=2)}")
        
        print(f"[DEBUG] ✓ State: {state.get('state')}")
        print(f"[DEBUG] ✓ Failures: {state.get('failures')}")
        print(f"[DEBUG] ✓ Threshold: {state.get('threshold')}")
        
        is_blocking = state.get('state') == 'open'
        if is_blocking:
            print("[DEBUG] ✗ Circuit breaker is OPEN (blocking requests)")
        else:
            print("[DEBUG] ✓ Circuit breaker is CLOSED (allowing requests)")
        
        print("[DEBUG] SUCCESS: Circuit breaker operational")
        return {
            "success": True,
            "message": "Circuit breaker operational",
            "data": state,
            "is_blocking": is_blocking
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
        
        ha_enabled = is_ha_extension_enabled()
        print(f"[DEBUG] HA Extension enabled: {ha_enabled}")
        
        if not ha_enabled:
            print("[DEBUG] FAILURE: HA extension not enabled")
            return {
                "success": False,
                "error": "HOME_ASSISTANT_ENABLED not set to true"
            }
        
        print("[DEBUG] Loading HA configuration...")
        from ha_config import load_ha_config
        
        config = load_ha_config()
        
        # Mask token for security
        safe_config = config.copy()
        if 'access_token' in safe_config:
            token = safe_config['access_token']
            safe_config['access_token'] = token[:10] + '...' if token else None
        
        print(f"[DEBUG] HA Config: {json.dumps(safe_config, indent=2)}")
        
        print(f"[DEBUG] ✓ HA enabled: {config.get('enabled')}")
        print(f"[DEBUG] ✓ Base URL: {config.get('base_url')}")
        print(f"[DEBUG] ✓ Token: {config.get('access_token', '')[:10]}...")
        print(f"[DEBUG] ✓ Timeout: {config.get('timeout')} seconds")
        print(f"[DEBUG] ✓ Assistant name: {config.get('assistant_name')}")
        
        print("[DEBUG] SUCCESS: HA configuration valid")
        return {
            "success": True,
            "message": "HA configuration valid",
            "data": safe_config
        }
        
    except Exception as e:
        print(f"[DEBUG] FAILURE: HA configuration error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_network_connectivity(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test raw network connectivity to HA."""
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
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"[DEBUG] Headers: \n{json.dumps({'Authorization': 'Bearer ' + token[:10] + '...', 'Content-Type': 'application/json'}, indent=4)}")
        
        print("[DEBUG] Making authenticated HTTP GET request to /api/...")
        result = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            'get',
            url=f"{base_url}/api/",
            headers=headers,
            timeout=10
        )
        
        print(f"[DEBUG] HTTP Response: {json.dumps(result, indent=2)}")
        
        if result.get('success') and result.get('status_code') == 200:
            print(f"[DEBUG] ✓ Status code: {result.get('status_code')}")
            print(f"[DEBUG] ✓ Authentication successful")
            print(f"[DEBUG] ✓ Response: {result.get('data')}")
            print("[DEBUG] SUCCESS: Authentication confirmed")
            return {
                "success": True,
                "message": "Authentication successful",
                "data": result
            }
        else:
            print(f"[DEBUG] FAILURE: Authentication failed")
            print(f"[DEBUG] Status: {result.get('status_code')}")
            print(f"[DEBUG] Error: {result.get('error')}")
            return {
                "success": False,
                "error": f"HTTP {result.get('status_code')}: {result.get('error')}",
                "data": result
            }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: Authentication test error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def test_api_endpoint(config: Dict[str, Any]) -> Dict[str, Any]:
    """Test calling HA API through full stack."""
    try:
        print("[DEBUG] Testing full API call through HA core...")
        from ha_core import call_ha_api
        
        print("[DEBUG] Calling call_ha_api('/api/')...")
        result = call_ha_api('/api/', ha_config=config)
        
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
            print(f"[DEBUG] FAILURE: API call failed")
            print(f"[DEBUG] Error: {result.get('error')}")
            return {
                "success": False,
                "error": result.get('error'),
                "data": result
            }
            
    except Exception as e:
        print(f"[DEBUG] FAILURE: API endpoint test error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def generate_summary(steps: Dict[str, Any]) -> Dict[str, Any]:
    """Generate test summary."""
    total = len(steps)
    passed = sum(1 for step in steps.values() if step.get('success', False))
    failed = total - passed
    
    failed_steps = [
        name for name, result in steps.items() 
        if not result.get('success', False)
    ]
    
    return {
        "total_steps": total,
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0,
        "failed_steps": failed_steps,
        "success_rate": f"{(passed/total*100):.1f}%"
    }


def print_summary(summary: Dict[str, Any]):
    """Print test summary."""
    print(f"[DEBUG] Total steps: {summary['total_steps']}")
    print(f"[DEBUG] Passed: {summary['passed']}")
    print(f"[DEBUG] Failed: {summary['failed']}")
    print(f"[DEBUG] Success rate: {summary['success_rate']}")
    
    if summary['all_passed']:
        print("[DEBUG] ✓✓✓ ALL TESTS PASSED ✓✓✓")
    else:
        print("[DEBUG] ✗✗✗ TESTS FAILED ✗✗✗")
        print(f"[DEBUG] Failed steps: {', '.join(summary['failed_steps'])}")


def format_diagnostic_response(results: Dict[str, Any], status_code: int) -> Dict[str, Any]:
    """Format diagnostic response."""
    return {
        "statusCode": status_code,
        "body": json.dumps(results, indent=2),
        "headers": {
            "Content-Type": "application/json"
        }
    }


# EOF
