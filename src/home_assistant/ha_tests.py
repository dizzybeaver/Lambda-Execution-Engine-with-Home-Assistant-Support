"""
ha_tests.py
Version: 2025.10.11.01
Daily Revision: Home Assistant Extension Test Suite

Copyright 2025 Joseph Hersey

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

import os
import time
from typing import Dict, Any, List, Optional, Callable

from gateway import (
    cache_get, cache_set, cache_delete,
    log_info, log_error, log_debug,
    record_metric, increment_counter,
    create_success_response, create_error_response,
    generate_correlation_id, parse_json_safely
)

def is_ha_extension_available() -> bool:
    """Check if Home Assistant extension is available for testing."""
    try:
        import homeassistant_extension
        return homeassistant_extension.is_ha_extension_enabled()
    except ImportError:
        return False

def execute_ha_test_with_caching(test_name: str, test_func: Callable, ttl: int = 300) -> Dict[str, Any]:
    """Execute HA test using standard caching pattern."""
    if not is_ha_extension_available():
        return {
            'test_name': test_name,
            'status': 'skip',
            'reason': 'Home Assistant extension not available or disabled',
            'timestamp': time.time()
        }
    
    cache_key = f"ha_test_result_{test_name}"
    
    cached_result = cache_get(cache_key)
    if cached_result:
        log_debug(f"Using cached HA test result for {test_name}")
        return cached_result
    
    correlation_id = generate_correlation_id()
    start_time = time.time()
    
    log_info(f"Executing HA test: {test_name}", correlation_id=correlation_id)
    
    try:
        success = test_func()
        duration = time.time() - start_time
        
        result = {
            'test_name': test_name,
            'status': 'pass' if success else 'fail',
            'duration_seconds': duration,
            'correlation_id': correlation_id,
            'timestamp': time.time(),
            'category': 'home_assistant'
        }
        
        record_metric("ha_test_execution", duration * 1000, dimensions={
            "test": test_name,
            "status": "pass" if success else "fail",
            "correlation_id": correlation_id
        })
        
        cache_set(cache_key, result, ttl=ttl)
        
        log_info(f"HA test completed: {test_name}", **result)
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        
        result = {
            'test_name': test_name,
            'status': 'error',
            'error': str(e),
            'duration_seconds': duration,
            'correlation_id': correlation_id,
            'timestamp': time.time(),
            'category': 'home_assistant'
        }
        
        log_error(f"HA test failed: {test_name}", error=e, **result)
        return result

def test_ha_extension_initialization() -> Dict[str, Any]:
    """Test Home Assistant extension initialization."""
    return execute_ha_test_with_caching("ha_extension_initialization", _test_ha_extension_initialization_impl)

def _test_ha_extension_initialization_impl() -> bool:
    """HA extension initialization test implementation."""
    try:
        from homeassistant_extension import initialize_ha_extension, is_ha_extension_enabled
        
        if not is_ha_extension_enabled():
            log_debug("HA extension disabled, skipping initialization test")
            return True
        
        result = initialize_ha_extension()
        
        if not isinstance(result, dict):
            return False
        
        return result.get('success', False) or 'error' not in result
        
    except Exception as e:
        log_error(f"HA initialization test failed: {str(e)}")
        return False

def test_ha_assistant_name_validation() -> Dict[str, Any]:
    """Test assistant name validation functionality."""
    return execute_ha_test_with_caching("ha_assistant_name_validation", _test_ha_assistant_name_validation_impl)

def _test_ha_assistant_name_validation_impl() -> bool:
    """Assistant name validation test implementation."""
    try:
        from homeassistant_extension import validate_assistant_name
        
        valid_names = [
            "Jarvis",
            "Computer", 
            "Smart Home",
            "House Assistant",
            "Home Control"
        ]
        
        for name in valid_names:
            result = validate_assistant_name(name)
            if not result.get('is_valid', False):
                log_error(f"Valid name '{name}' failed validation: {result.get('error')}")
                return False
        
        invalid_names = [
            "",
            "   ",
            "Alexa",
            "Amazon", 
            "Echo",
            "a",
            "a" * 30,
            "123",
            "test@home"
        ]
        
        for name in invalid_names:
            result = validate_assistant_name(name)
            if result.get('is_valid', True):
                log_error(f"Invalid name '{name}' passed validation")
                return False
        
        return True
        
    except Exception as e:
        log_error(f"Assistant name validation test failed: {str(e)}")
        return False

def test_ha_configuration_retrieval() -> Dict[str, Any]:
    """Test Home Assistant configuration retrieval."""
    return execute_ha_test_with_caching("ha_configuration_retrieval", _test_ha_configuration_retrieval_impl)

def _test_ha_configuration_retrieval_impl() -> bool:
    """HA configuration retrieval test implementation."""
    try:
        from homeassistant_extension import _get_ha_config_gateway
        
        config = _get_ha_config_gateway()
        
        if not isinstance(config, dict):
            return False
        
        required_keys = ["enabled", "base_url", "access_token", "timeout", "verify_ssl"]
        
        for key in required_keys:
            if key not in config:
                log_error(f"Missing required config key: {key}")
                return False
        
        if config.get("enabled", False):
            if not config.get("base_url"):
                log_error("HA enabled but no base_url configured")
                return False
            if not config.get("access_token"):
                log_error("HA enabled but no access_token configured")
                return False
        
        return True
        
    except Exception as e:
        log_error(f"HA configuration test failed: {str(e)}")
        return False

def test_ha_assistant_name_retrieval() -> Dict[str, Any]:
    """Test assistant name retrieval from configuration."""
    return execute_ha_test_with_caching("ha_assistant_name_retrieval", _test_ha_assistant_name_retrieval_impl)

def _test_ha_assistant_name_retrieval_impl() -> bool:
    """Assistant name retrieval test implementation."""
    try:
        from homeassistant_extension import get_ha_assistant_name
        
        assistant_name = get_ha_assistant_name()
        
        if not isinstance(assistant_name, str):
            return False
        
        if len(assistant_name) < 2:
            return False
        
        if not assistant_name.strip():
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Assistant name retrieval test failed: {str(e)}")
        return False

def test_ha_status_check() -> Dict[str, Any]:
    """Test Home Assistant status checking."""
    return execute_ha_test_with_caching("ha_status_check", _test_ha_status_check_impl)

def _test_ha_status_check_impl() -> bool:
    """HA status check test implementation."""
    try:
        from homeassistant_extension import get_ha_status
        
        result = get_ha_status()
        
        if not isinstance(result, dict):
            return False
        
        return 'success' in result or 'data' in result or 'error' in result
        
    except Exception as e:
        log_error(f"HA status check test failed: {str(e)}")
        return False

def test_ha_diagnostic_info() -> Dict[str, Any]:
    """Test Home Assistant diagnostic information retrieval."""
    return execute_ha_test_with_caching("ha_diagnostic_info", _test_ha_diagnostic_info_impl)

def _test_ha_diagnostic_info_impl() -> bool:
    """HA diagnostic info test implementation."""
    try:
        from homeassistant_extension import get_ha_diagnostic_info
        
        result = get_ha_diagnostic_info()
        
        if not isinstance(result, dict):
            return False
        
        if not result.get('success', False):
            return 'error' in result
        
        data = result.get('data', {})
        
        expected_fields = [
            'timestamp',
            'ha_enabled', 
            'connection_status',
            'assistant_name',
            'configuration'
        ]
        
        for field in expected_fields:
            if field not in data:
                log_error(f"Missing diagnostic field: {field}")
                return False
        
        return True
        
    except Exception as e:
        log_error(f"HA diagnostic info test failed: {str(e)}")
        return False

def test_ha_cleanup() -> Dict[str, Any]:
    """Test Home Assistant extension cleanup."""
    return execute_ha_test_with_caching("ha_cleanup", _test_ha_cleanup_impl, ttl=60)

def _test_ha_cleanup_impl() -> bool:
    """HA cleanup test implementation."""
    try:
        from homeassistant_extension import cleanup_ha_extension
        
        result = cleanup_ha_extension()
        
        if not isinstance(result, dict):
            return False
        
        return result.get('success', False) or 'error' not in result
        
    except Exception as e:
        log_error(f"HA cleanup test failed: {str(e)}")
        return False

def test_ha_environment_variables() -> Dict[str, Any]:
    """Test Home Assistant environment variable handling."""
    return execute_ha_test_with_caching("ha_environment_variables", _test_ha_environment_variables_impl)

def _test_ha_environment_variables_impl() -> bool:
    """HA environment variables test implementation."""
    try:
        ha_enabled = os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower()
        
        if ha_enabled not in ["true", "false", "1", "0"]:
            log_error(f"Invalid HOME_ASSISTANT_ENABLED value: {ha_enabled}")
            return False
        
        if ha_enabled in ["true", "1"]:
            assistant_name = os.environ.get("HA_ASSISTANT_NAME")
            if assistant_name:
                from homeassistant_extension import validate_assistant_name
                validation = validate_assistant_name(assistant_name)
                if not validation.get('is_valid', False):
                    log_error(f"Invalid HA_ASSISTANT_NAME in environment: {assistant_name}")
                    return False
        
        return True
        
    except Exception as e:
        log_error(f"HA environment variables test failed: {str(e)}")
        return False

def test_ha_cache_operations() -> Dict[str, Any]:
    """Test Home Assistant cache operations."""
    return execute_ha_test_with_caching("ha_cache_operations", _test_ha_cache_operations_impl, ttl=60)

def _test_ha_cache_operations_impl() -> bool:
    """HA cache operations test implementation."""
    try:
        test_keys = [
            "ha_extension_config",
            "ha_manager_data", 
            "ha_assistant_name"
        ]
        
        for key in test_keys:
            cache_set(f"test_{key}", {"test": "data"}, ttl=60)
            
            value = cache_get(f"test_{key}")
            if value is None:
                log_error(f"Cache get failed for key: test_{key}")
                return False
            
            cache_delete(f"test_{key}")
            
            value = cache_get(f"test_{key}")
            if value is not None:
                log_error(f"Cache delete failed for key: test_{key}")
                return False
        
        return True
        
    except Exception as e:
        log_error(f"HA cache operations test failed: {str(e)}")
        return False

def test_ha_response_formatting() -> Dict[str, Any]:
    """Test Home Assistant response formatting consistency."""
    return execute_ha_test_with_caching("ha_response_formatting", _test_ha_response_formatting_impl)

def _test_ha_response_formatting_impl() -> bool:
    """HA response formatting test implementation."""
    try:
        success_response = create_success_response("Test message", {"test": "data"})
        
        if not isinstance(success_response, dict):
            return False
        
        if not success_response.get('success', False):
            return False
        
        error_response = create_error_response("Test error", {"error": "details"})
        
        if not isinstance(error_response, dict):
            return False
        
        if error_response.get('success', True):
            return False
        
        return True
        
    except Exception as e:
        log_error(f"HA response formatting test failed: {str(e)}")
        return False

def run_all_ha_tests() -> Dict[str, Any]:
    """Run all Home Assistant extension tests."""
    if not is_ha_extension_available():
        return {
            'status': 'skip',
            'reason': 'Home Assistant extension not available or disabled',
            'timestamp': time.time()
        }
    
    correlation_id = generate_correlation_id()
    start_time = time.time()
    
    log_info("Starting HA extension test suite", correlation_id=correlation_id)
    
    tests = {
        'initialization': test_ha_extension_initialization,
        'assistant_name_validation': test_ha_assistant_name_validation,
        'configuration_retrieval': test_ha_configuration_retrieval,
        'assistant_name_retrieval': test_ha_assistant_name_retrieval,
        'status_check': test_ha_status_check,
        'diagnostic_info': test_ha_diagnostic_info,
        'cleanup': test_ha_cleanup,
        'environment_variables': test_ha_environment_variables,
        'cache_operations': test_ha_cache_operations,
        'response_formatting': test_ha_response_formatting
    }
    
    results = {}
    passed = 0
    failed = 0
    skipped = 0
    
    for name, test_func in tests.items():
        try:
            result = test_func()
            results[name] = result
            
            status = result.get('status', 'unknown')
            if status == 'pass':
                passed += 1
            elif status == 'skip':
                skipped += 1
            else:
                failed += 1
                
        except Exception as e:
            results[name] = {
                'status': 'error',
                'error': str(e),
                'test_name': name
            }
            failed += 1
    
    duration = time.time() - start_time
    total_tests = len(tests)
    
    summary = {
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': (passed / (total_tests - skipped)) * 100 if (total_tests - skipped) > 0 else 0,
        'duration_seconds': duration,
        'correlation_id': correlation_id,
        'results': results,
        'category': 'home_assistant_extension'
    }
    
    record_metric("ha_test_suite_execution", duration, dimensions={
        "total": total_tests,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "correlation_id": correlation_id
    })
    
    log_info("HA extension test suite completed", **summary)
    
    return summary

def get_ha_test_info() -> Dict[str, Any]:
    """Get information about available HA tests."""
    return {
        'available': is_ha_extension_available(),
        'test_count': 10,
        'tests': [
            'initialization',
            'assistant_name_validation', 
            'configuration_retrieval',
            'assistant_name_retrieval',
            'status_check',
            'diagnostic_info',
            'cleanup',
            'environment_variables',
            'cache_operations',
            'response_formatting'
        ],
        'description': 'Home Assistant extension test suite',
        'category': 'home_assistant_extension'
    }
