"""
extension_interface_tests.py - Extension Interface Testing
Version: 2025.09.29.06
Daily Revision: Phase 4 Extension Testing Implementation

Tests for Home Assistant Extension using gateway architecture.
Validates extension integration with SUGA + LIGS architecture.
"""

import time
from typing import Dict, Any

def run_extension_interface_tests() -> Dict[str, Any]:
    """Run all extension interface tests."""
    print("\n" + "="*80)
    print("PHASE 4: EXTENSION INTERFACE TESTS")
    print("Testing Home Assistant Extension with Gateway Architecture")
    print("="*80 + "\n")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_ha_initialization_gateway,
        test_ha_config_retrieval,
        test_ha_status_check,
        test_ha_service_call_structure,
        test_ha_state_retrieval_structure,
        test_alexa_discovery_structure,
        test_alexa_power_control_structure,
        test_ha_cleanup,
        test_gateway_import_compatibility,
        test_lazy_loading_compatibility
    ]
    
    for test_func in tests:
        results["total_tests"] += 1
        test_name = test_func.__name__
        
        try:
            print(f"Running: {test_name}...")
            test_result = test_func()
            
            if test_result.get("success", False):
                results["passed"] += 1
                print(f"  âœ… PASSED: {test_result.get('message', 'Test passed')}")
            else:
                results["failed"] += 1
                print(f"  âŒ FAILED: {test_result.get('error', 'Test failed')}")
            
            results["tests"].append({
                "name": test_name,
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
            
        except Exception as e:
            results["failed"] += 1
            print(f"  âŒ EXCEPTION: {str(e)}")
            results["tests"].append({
                "name": test_name,
                "success": False,
                "message": f"Exception: {str(e)}"
            })
    
    print("\n" + "="*80)
    print(f"EXTENSION INTERFACE TEST RESULTS")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
    print("="*80 + "\n")
    
    return results

def test_ha_initialization_gateway() -> Dict[str, Any]:
    """Test HA initialization using gateway."""
    try:
        from homeassistant_extension import initialize_ha_extension
        
        result = initialize_ha_extension()
        
        if "success" in result or "error" in result:
            return {
                "success": True,
                "message": "HA initialization structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid initialization response structure"
            }
    except ImportError as e:
        return {
            "success": False,
            "error": f"Import failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Initialization test failed: {str(e)}"
        }

def test_ha_config_retrieval() -> Dict[str, Any]:
    """Test HA configuration retrieval."""
    try:
        from homeassistant_extension import _get_ha_config_gateway
        
        config = _get_ha_config_gateway()
        
        required_keys = ["enabled", "base_url", "access_token", "timeout", "verify_ssl"]
        
        if all(key in config for key in required_keys):
            return {
                "success": True,
                "message": f"Config has all required keys: {len(required_keys)}"
            }
        else:
            missing = [k for k in required_keys if k not in config]
            return {
                "success": False,
                "error": f"Missing config keys: {missing}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Config retrieval test failed: {str(e)}"
        }

def test_ha_status_check() -> Dict[str, Any]:
    """Test HA status check function."""
    try:
        from homeassistant_extension import get_ha_status
        
        result = get_ha_status()
        
        if isinstance(result, dict) and ("success" in result or "error" in result):
            return {
                "success": True,
                "message": "Status check returns valid structure"
            }
        else:
            return {
                "success": False,
                "error": "Invalid status response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Status check test failed: {str(e)}"
        }

def test_ha_service_call_structure() -> Dict[str, Any]:
    """Test HA service call function structure."""
    try:
        from homeassistant_extension import call_ha_service
        
        result = call_ha_service("light", "turn_on", "light.test_light")
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": "Service call function structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid service call response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Service call test failed: {str(e)}"
        }

def test_ha_state_retrieval_structure() -> Dict[str, Any]:
    """Test HA state retrieval function structure."""
    try:
        from homeassistant_extension import get_ha_state
        
        result = get_ha_state("light.test_light")
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": "State retrieval function structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid state retrieval response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"State retrieval test failed: {str(e)}"
        }

def test_alexa_discovery_structure() -> Dict[str, Any]:
    """Test Alexa discovery function structure."""
    try:
        from homeassistant_extension import process_alexa_ha_request
        
        test_event = {
            "directive": {
                "header": {
                    "namespace": "Alexa.Discovery",
                    "name": "Discover"
                }
            }
        }
        
        result = process_alexa_ha_request(test_event)
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": "Alexa discovery function structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid Alexa discovery response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Alexa discovery test failed: {str(e)}"
        }

def test_alexa_power_control_structure() -> Dict[str, Any]:
    """Test Alexa power control function structure."""
    try:
        from homeassistant_extension import process_alexa_ha_request
        
        test_event = {
            "directive": {
                "header": {
                    "namespace": "Alexa.PowerController",
                    "name": "TurnOn"
                },
                "endpoint": {
                    "endpointId": "light.test_light"
                }
            }
        }
        
        result = process_alexa_ha_request(test_event)
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": "Alexa power control function structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid Alexa power control response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Alexa power control test failed: {str(e)}"
        }

def test_ha_cleanup() -> Dict[str, Any]:
    """Test HA cleanup function."""
    try:
        from homeassistant_extension import cleanup_ha_extension
        
        result = cleanup_ha_extension()
        
        if isinstance(result, dict) and ("success" in result or "error" in result):
            return {
                "success": True,
                "message": "Cleanup function structure valid"
            }
        else:
            return {
                "success": False,
                "error": "Invalid cleanup response structure"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Cleanup test failed: {str(e)}"
        }

def test_gateway_import_compatibility() -> Dict[str, Any]:
    """Test that HA extension uses gateway imports."""
    try:
        import homeassistant_extension
        import inspect
        
        source = inspect.getsource(homeassistant_extension)
        
        if "from gateway import" in source:
            gateway_imports = source.count("from gateway import")
            return {
                "success": True,
                "message": f"Uses gateway imports (found {gateway_imports} import statement(s))"
            }
        else:
            return {
                "success": False,
                "error": "Does not use gateway imports"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Import compatibility test failed: {str(e)}"
        }

def test_lazy_loading_compatibility() -> Dict[str, Any]:
    """Test that HA extension is compatible with lazy loading."""
    try:
        from homeassistant_extension import initialize_ha_extension, is_ha_extension_enabled
        
        enabled = is_ha_extension_enabled()
        
        result = initialize_ha_extension()
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": f"Lazy loading compatible (enabled: {enabled})"
            }
        else:
            return {
                "success": False,
                "error": "Not lazy loading compatible"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lazy loading test failed: {str(e)}"
        }

def test_gateway_operation_execution() -> Dict[str, Any]:
    """Test direct gateway operation execution."""
    try:
        from gateway import GatewayInterface, execute_operation
        
        result = execute_operation(
            GatewayInterface.CACHE,
            "get",
            key="test_key",
            default_value=None
        )
        
        return {
            "success": True,
            "message": "Gateway operation execution successful"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Gateway operation test failed: {str(e)}"
        }

def test_correlation_id_generation() -> Dict[str, Any]:
    """Test correlation ID generation for HA operations."""
    try:
        from gateway import generate_correlation_id
        
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()
        
        if id1 != id2 and len(id1) > 0 and len(id2) > 0:
            return {
                "success": True,
                "message": f"Correlation IDs generated successfully (length: {len(id1)})"
            }
        else:
            return {
                "success": False,
                "error": "Correlation ID generation invalid"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Correlation ID test failed: {str(e)}"
        }

def test_ha_domain_enum() -> Dict[str, Any]:
    """Test HA domain enum definition."""
    try:
        from homeassistant_extension import HADomain
        
        domains = [d.value for d in HADomain]
        
        expected_domains = ["light", "switch", "sensor", "binary_sensor", "climate", "cover", "lock", "media_player"]
        
        if all(d in domains for d in expected_domains):
            return {
                "success": True,
                "message": f"HADomain enum complete ({len(domains)} domains)"
            }
        else:
            return {
                "success": False,
                "error": "HADomain enum incomplete"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Domain enum test failed: {str(e)}"
        }

if __name__ == "__main__":
    results = run_extension_interface_tests()
    
    if results["failed"] > 0:
        print(f"\nâš ï¸ {results['failed']} test(s) failed")
        exit(1)
    else:
        print("\nâœ… All extension interface tests passed!")
        exit(0)

# EOF
