# ha_test_config.py
"""
ha_test_config.py
Version: 1.0.0
Date: 2025-11-04
Description: HA-SUGA test configuration for generic LEE tests

Provides HA-specific parameters to pass to generic LEE tests.
Keeps HA testing configuration separate from test implementation.

Copyright 2025 Joseph Hersey

Licensed under the Apache License, Version 2.0.
"""

import os
from typing import Dict, List, Any


# ADDED: HA-SUGA test configuration
HA_TEST_CONFIG = {
    # Environment variables for HA tests
    'environment': {
        'HOME_ASSISTANT_ENABLE': 'true',
        'DEBUG_MODE': 'false',  # Production-like testing
        'HA_URL': os.environ.get('HA_URL', 'https://homeassistant.local'),
        'HA_TOKEN_PARAM': os.environ.get('HA_TOKEN_PARAM', '/suga-isp/ha/token'),
    },
    
    # Cores to test for debug patterns
    'debug_pattern_cores': [
        'home_assistant.ha_alexa_core',
        'home_assistant.ha_assist_core',
        'home_assistant.ha_devices_core'
    ],
    
    # Error scenarios specific to HA
    'error_scenarios': [
        {
            'test': 'invalid_alexa_directive',
            'directive': {
                'directive': {
                    'header': {
                        'namespace': 'Invalid.Namespace',
                        'name': 'InvalidDirective'
                    }
                }
            },
            'expected': 'ErrorResponse'
        },
        {
            'test': 'websocket_disconnect',
            'simulate': 'network_failure',
            'expected': 'retry_logic'
        },
        {
            'test': 'ha_timeout',
            'timeout_ms': 1,  # Force timeout
            'expected': 'graceful_degradation'
        },
        {
            'test': 'missing_token',
            'token': None,
            'expected': 'authentication_error'
        }
    ],
    
    # Performance thresholds
    'performance': {
        'cold_start_target_ms': 3000,  # < 3 seconds
        'ha_overhead_max_ms': 500,     # HA should add < 500ms
        'websocket_connect_max_ms': 2000,  # Connect < 2 seconds
        'directive_process_max_ms': 100,   # Process directive < 100ms
        'device_query_max_ms': 200        # Query devices < 200ms
    },
    
    # Integration test scenarios
    'integration_tests': [
        {
            'name': 'alexa_discovery',
            'directive_type': 'Alexa.Discovery',
            'expected_response': 'Discover.Response'
        },
        {
            'name': 'device_control',
            'directive_type': 'Alexa.PowerController',
            'expected_response': 'Response'
        },
        {
            'name': 'device_query',
            'directive_type': 'Alexa.EndpointHealth',
            'expected_response': 'StateReport'
        }
    ],
    
    # Test devices (for HA-specific tests)
    'test_devices': [
        {
            'id': 'switch.test_switch',
            'friendly_name': 'Test Switch',
            'type': 'switch',
            'expected_capabilities': ['PowerController']
        },
        {
            'id': 'light.test_light',
            'friendly_name': 'Test Light',
            'type': 'light',
            'expected_capabilities': ['PowerController', 'BrightnessController']
        }
    ]
}


# ADDED: Helper to apply HA environment
def apply_ha_test_environment() -> Dict[str, str]:
    """
    Apply HA test environment variables.
    
    Returns:
        Dictionary of previous environment values (for cleanup)
    """
    previous_env = {}
    
    for key, value in HA_TEST_CONFIG['environment'].items():
        previous_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    return previous_env


# ADDED: Helper to restore previous environment
def restore_environment(previous_env: Dict[str, str]) -> None:
    """
    Restore previous environment variables.
    
    Args:
        previous_env: Dictionary from apply_ha_test_environment()
    """
    for key, value in previous_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value


# ADDED: Helper to get performance threshold
def get_performance_threshold(metric: str) -> int:
    """
    Get performance threshold for metric.
    
    Args:
        metric: Metric name (e.g., 'cold_start_target_ms')
        
    Returns:
        Threshold value in milliseconds
    """
    return HA_TEST_CONFIG['performance'].get(metric, 0)


# ADDED: Helper to check if HA tests should run
def should_run_ha_tests() -> bool:
    """
    Check if HA tests should run based on environment.
    
    Returns:
        True if HA tests should run, False otherwise
    """
    return os.environ.get('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true'


# ADDED: Helper to get test device by type
def get_test_device(device_type: str) -> Dict[str, Any]:
    """
    Get test device configuration by type.
    
    Args:
        device_type: Type of device ('switch', 'light', etc.)
        
    Returns:
        Device configuration dictionary or None
    """
    for device in HA_TEST_CONFIG['test_devices']:
        if device['type'] == device_type:
            return device
    return None


__all__ = [
    'HA_TEST_CONFIG',
    'apply_ha_test_environment',
    'restore_environment',
    'get_performance_threshold',
    'should_run_ha_tests',
    'get_test_device'
]

# EOF
