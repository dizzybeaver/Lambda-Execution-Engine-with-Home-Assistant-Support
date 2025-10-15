"""
home_assistant/__init__.py - Home Assistant Extension Package
Version: 2025.10.14.01
Description: Package initialization for Home Assistant extension internal modules.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# Core Operations
from ha_core import (
    get_ha_config,
    call_ha_api,
    get_states,
    get_entity_state,
    call_service,
    ha_operation_wrapper,
    check_ha_status,
    is_ha_available,
    initialize_ha_system,
    cleanup_ha_system,
    get_diagnostic_info,
    get_ha_entity_registry,
    filter_exposed_entities_wrapper,
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES,
    HA_CACHE_TTL_STATE,
    HA_CACHE_TTL_CONFIG,
    HA_CIRCUIT_BREAKER_NAME,
)

# Configuration
from ha_config import (
    load_ha_config,
    validate_ha_config,
    get_ha_preset,
    load_ha_connection_config,
    load_ha_preset_config,
)

# Build Configuration
from ha_build_config import (
    HAFeature,
    FEATURE_MODULES,
    FEATURE_DEPENDENCIES,
    COMMON_PRESETS,
    parse_feature_list,
    get_required_modules,
    get_enabled_features,
    is_feature_enabled,
    validate_feature_dependencies,
    get_feature_info,
)

# Features
from ha_features import (
    list_automations,
    trigger_automation,
    list_scripts,
    run_script,
    list_input_helpers,
    set_input_helper,
    send_notification,
    process_conversation,
)

# Managers
from ha_managers import (
    HAGenericManager,
    list_entities_by_domain,
    manage_device,
    manage_area,
)

# Alexa Integration
from ha_alexa import (
    process_alexa_directive,
    handle_discovery,
    handle_control,
    handle_power_control,
    handle_brightness_control,
    handle_thermostat_control,
    handle_accept_grant,
)

# WebSocket Operations (optional)
try:
    from ha_websocket import (
        establish_websocket_connection,
        authenticate_websocket,
        websocket_request,
        get_entity_registry_via_websocket,
        filter_exposed_entities,
        is_websocket_enabled,
    )
    _WEBSOCKET_AVAILABLE = True
except ImportError:
    _WEBSOCKET_AVAILABLE = False

# Tests
from ha_tests import (
    is_ha_extension_available,
    execute_ha_test_with_caching,
    test_ha_extension_initialization,
    test_ha_configuration,
    test_ha_status_check,
    test_ha_gateway_integration,
    test_ha_alexa_integration,
    test_ha_features,
    test_ha_managers,
    run_all_ha_tests,
)

__all__ = [
    # Core
    'get_ha_config',
    'call_ha_api',
    'get_states',
    'get_entity_state',
    'call_service',
    'ha_operation_wrapper',
    'check_ha_status',
    'is_ha_available',
    'initialize_ha_system',
    'cleanup_ha_system',
    'get_diagnostic_info',
    'get_ha_entity_registry',
    'filter_exposed_entities_wrapper',
    'fuzzy_match_name',
    'HA_CACHE_TTL_ENTITIES',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_CONFIG',
    'HA_CIRCUIT_BREAKER_NAME',
    
    # Configuration
    'load_ha_config',
    'validate_ha_config',
    'get_ha_preset',
    'load_ha_connection_config',
    'load_ha_preset_config',
    
    # Build Configuration
    'HAFeature',
    'FEATURE_MODULES',
    'FEATURE_DEPENDENCIES',
    'COMMON_PRESETS',
    'parse_feature_list',
    'get_required_modules',
    'get_enabled_features',
    'is_feature_enabled',
    'validate_feature_dependencies',
    'get_feature_info',
    
    # Features
    'list_automations',
    'trigger_automation',
    'list_scripts',
    'run_script',
    'list_input_helpers',
    'set_input_helper',
    'send_notification',
    'process_conversation',
    
    # Managers
    'HAGenericManager',
    'list_entities_by_domain',
    'manage_device',
    'manage_area',
    
    # Alexa
    'process_alexa_directive',
    'handle_discovery',
    'handle_control',
    'handle_power_control',
    'handle_brightness_control',
    'handle_thermostat_control',
    'handle_accept_grant',
    
    # Tests
    'is_ha_extension_available',
    'execute_ha_test_with_caching',
    'test_ha_extension_initialization',
    'test_ha_configuration',
    'test_ha_status_check',
    'test_ha_gateway_integration',
    'test_ha_alexa_integration',
    'test_ha_features',
    'test_ha_managers',
    'run_all_ha_tests',
]

# Add WebSocket exports if available
if _WEBSOCKET_AVAILABLE:
    __all__.extend([
        'establish_websocket_connection',
        'authenticate_websocket',
        'websocket_request',
        'get_entity_registry_via_websocket',
        'filter_exposed_entities',
        'is_websocket_enabled',
    ])

# EOF
