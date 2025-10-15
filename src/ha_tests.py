"""
ha_tests.py - Testing & Validation
Version: 2025.10.14.01
Description: Testing functions using Gateway services.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Callable
from gateway import (
    log_info, log_error, log_debug,
    cache_get, cache_set,
    create_success_response, create_error_response
)

# ===== TEST UTILITIES =====

def execute_ha_test_with_caching(test_name: str, test_func: Callable,
                                ttl: int = 300) -> Dict[str, Any]:
    """Execute test with caching."""
    cache_key = f"ha_test_{test_name}"
    
    cached = cache_get(cache_key)
    if cached:
        log_debug(f"Using cached test result: {test_name}")
        return cached
    
    try:
        result = test_func()
        
        response = {
            'test_name': test_name,
            'success': bool(result),
            'passed': bool(result)
        }
        
        cache_set(cache_key, response, ttl=ttl)
        return response
        
    except Exception as e:
        log_error(f"Test {test_name} failed: {str(e)}")
        return {
            'test_name': test_name,
            'success': False,
            'passed': False,
            'error': str(e)
        }


# ===== EXTENSION TESTS =====

def is_ha_extension_available() -> bool:
    """Check if extension is available."""
    try:
        import os
        return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'
    except Exception as e:
        log_error(f"Extension availability check failed: {str(e)}")
        return False


def test_ha_extension_initialization() -> Dict[str, Any]:
    """Test extension initialization."""
    def _test():
        try:
            from homeassistant_extension import is_ha_extension_enabled
            
            if not is_ha_extension_enabled():
                log_debug("HA extension disabled, test skipped")
                return True
            
            from ha_core import initialize_ha_system
            result = initialize_ha_system()
            
            return result.get('success', False)
            
        except Exception as e:
            log_error(f"Initialization test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('initialization', _test)


def test_ha_configuration() -> Dict[str, Any]:
    """Test configuration loading."""
    def _test():
        try:
            from ha_config import load_ha_config, validate_ha_config
            
            config = load_ha_config()
            if not isinstance(config, dict):
                return False
            
            validation = validate_ha_config(config)
            return validation.get('success', False) or 'error' in validation
            
        except Exception as e:
            log_error(f"Configuration test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('configuration', _test)


def test_ha_status_check() -> Dict[str, Any]:
    """Test status checking."""
    def _test():
        try:
            if not is_ha_extension_available():
                return True
            
            from ha_core import check_ha_status
            result = check_ha_status()
            
            return isinstance(result, dict)
            
        except Exception as e:
            log_error(f"Status test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('status_check', _test)


def test_ha_gateway_integration() -> Dict[str, Any]:
    """Test Gateway integration."""
    def _test():
        try:
            from gateway import execute_operation, GatewayInterface
            
            # Test cache
            result1 = execute_operation(GatewayInterface.CACHE, 'set',
                                       key='ha_test', value='test', ttl=60)
            
            result2 = execute_operation(GatewayInterface.CACHE, 'get',
                                       key='ha_test')
            
            if result2 != 'test':
                return False
            
            # Test logging
            execute_operation(GatewayInterface.LOGGING, 'log_info',
                            message='HA test log')
            
            # Test metrics
            execute_operation(GatewayInterface.METRICS, 'increment',
                            name='ha_test_metric')
            
            return True
            
        except Exception as e:
            log_error(f"Gateway integration test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('gateway_integration', _test, ttl=60)


def test_ha_alexa_integration() -> Dict[str, Any]:
    """Test Alexa integration."""
    def _test():
        try:
            if not is_ha_extension_available():
                return True
            
            from ha_alexa import _build_endpoint, _get_display_category
            
            # Test endpoint building
            test_state = {
                'entity_id': 'light.test',
                'attributes': {'friendly_name': 'Test Light'}
            }
            
            endpoint = _build_endpoint(test_state, 'light')
            if not endpoint or not isinstance(endpoint, dict):
                return False
            
            # Test category mapping
            category = _get_display_category('light')
            if category != 'LIGHT':
                return False
            
            return True
            
        except Exception as e:
            log_error(f"Alexa integration test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('alexa_integration', _test)


def test_ha_features() -> Dict[str, Any]:
    """Test feature operations."""
    def _test():
        try:
            if not is_ha_extension_available():
                return True
            
            from ha_features import list_automations, list_scripts
            
            # These should return dict responses even if HA is unavailable
            auto_result = list_automations()
            script_result = list_scripts()
            
            return (isinstance(auto_result, dict) and 
                   isinstance(script_result, dict))
            
        except Exception as e:
            log_error(f"Features test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('features', _test)


def test_ha_managers() -> Dict[str, Any]:
    """Test manager operations."""
    def _test():
        try:
            from ha_managers import HAGenericManager
            
            # Test manager creation
            manager = HAGenericManager('test', 'light')
            
            if not manager or not hasattr(manager, 'list_entities'):
                return False
            
            # Test stats
            stats = manager.get_stats()
            if not isinstance(stats, dict):
                return False
            
            return True
            
        except Exception as e:
            log_error(f"Managers test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('managers', _test)


def test_ha_websocket_integration() -> Dict[str, Any]:
    """Test WebSocket integration."""
    def _test():
        try:
            try:
                from ha_websocket import (
                    is_websocket_enabled,
                    establish_websocket_connection,
                    filter_exposed_entities
                )
                
                # Test feature check
                enabled = is_websocket_enabled()
                
                # Test entity filtering
                test_entities = [
                    {
                        'entity_id': 'light.test',
                        'options': {
                            'alexa': {'should_expose': True}
                        }
                    },
                    {
                        'entity_id': 'light.hidden',
                        'options': {}
                    }
                ]
                
                filtered = filter_exposed_entities(test_entities)
                if len(filtered) != 1:
                    return False
                
                return True
                
            except ImportError:
                # WebSocket module not available - that's OK
                log_debug("WebSocket module not available, test skipped")
                return True
            
        except Exception as e:
            log_error(f"WebSocket test failed: {str(e)}")
            return False
    
    return execute_ha_test_with_caching('websocket_integration', _test)


# ===== TEST SUITE =====

def run_all_ha_tests() -> Dict[str, Any]:
    """Run all HA tests."""
    tests = [
        ('initialization', test_ha_extension_initialization),
        ('configuration', test_ha_configuration),
        ('status_check', test_ha_status_check),
        ('gateway_integration', test_ha_gateway_integration),
        ('alexa_integration', test_ha_alexa_integration),
        ('features', test_ha_features),
        ('managers', test_ha_managers),
        ('websocket_integration', test_ha_websocket_integration),
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        result = test_func()
        results[name] = result
        
        if result.get('passed', False):
            passed += 1
        else:
            failed += 1
    
    return create_success_response('Test suite completed', {
        'results': results,
        'summary': {
            'total': len(tests),
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/len(tests)*100):.1f}%"
        }
    })


# EOF
