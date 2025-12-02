"""
ha_interconnect.py - Home Assistant Gateway (HA-SUGA) - Main Entry Point
Version: 5.0.0
Date: 2025-12-02
Purpose: Central gateway with CR-1 pattern and template support

ADDED: Core registry imports (HAInterface, execute_ha_operation, etc.)
ADDED: Configuration imports (HA_ENABLED, HA_CACHE_ENABLED, etc.)
ADDED: Template imports (ALEXA_ERROR_RESPONSE, etc.)
REMOVED: Validation imports (file deleted, now use gateway.validate_*)
KEPT: All function exports (100% backward compatible)

Structure:
ha_interconnect.py (main, 90 lines) - THIS FILE
  ├→ ha_interconnect_core.py (CR-1 registry)
  ├→ ha_config.py (centralized config)
  ├→ ha_alexa_templates.py (response templates)
  ├→ ha_interconnect_alexa.py (7 functions)
  ├→ ha_interconnect_devices.py (14 functions)
  └→ ha_interconnect_assist.py (4 functions)

Pattern:
This is the ONLY entry point for Home Assistant operations.
All HA internal calls route through this gateway.
External calls to LEE route through LEE's gateway.py.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ADDED: Core registry
from home_assistant.ha_interconnect_core import (
    HAInterface,
    execute_ha_operation,
    get_ha_registry_stats,
    clear_ha_cache,
)

# ADDED: Configuration
from home_assistant.ha_config import (
    HA_ENABLED,
    HA_CACHE_ENABLED,
    HA_METRICS_ENABLED,
    HA_DEBUG_MODE,
    HA_CACHE_TTL_STATE,
    HA_CACHE_TTL_DOMAIN,
    HA_CACHE_TTL_FUZZY,
    HA_CACHE_TTL_CONFIG,
    HA_API_TIMEOUT,
    HA_WEBSOCKET_TIMEOUT,
    HA_CONNECT_TIMEOUT,
)

# ADDED: Templates
from home_assistant.ha_alexa_templates import (
    ALEXA_ERROR_RESPONSE,
    ALEXA_SUCCESS_RESPONSE,
    ALEXA_ACCEPT_GRANT_RESPONSE,
    ALEXA_DISCOVERY_RESPONSE,
)

# Import Alexa gateway functions
from home_assistant.ha_interconnect_alexa import (
    alexa_process_directive,
    alexa_handle_discovery,
    alexa_handle_control,
    alexa_handle_power_control,
    alexa_handle_brightness_control,
    alexa_handle_thermostat_control,
    alexa_handle_accept_grant,
)

# Import Devices gateway functions
from home_assistant.ha_interconnect_devices import (
    devices_get_states,
    devices_get_by_id,
    devices_find_fuzzy,
    devices_update_state,
    devices_call_service,
    devices_list_by_domain,
    devices_check_status,
    devices_call_ha_api,
    devices_get_ha_config,
    devices_warm_cache,
    devices_invalidate_entity_cache,
    devices_invalidate_domain_cache,
    devices_get_performance_report,
    devices_get_diagnostic_info,
)

# Import Assist gateway functions
from home_assistant.ha_interconnect_assist import (
    assist_send_message,
    assist_get_response,
    assist_process_conversation,
    assist_handle_pipeline,
)

# REMOVED: Validation imports (file deleted - use gateway.validate_* instead)


__all__ = [
    # Core registry (NEW)
    'HAInterface',
    'execute_ha_operation',
    'get_ha_registry_stats',
    'clear_ha_cache',
    
    # Configuration (NEW)
    'HA_ENABLED',
    'HA_CACHE_ENABLED',
    'HA_METRICS_ENABLED',
    'HA_DEBUG_MODE',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_DOMAIN',
    'HA_CACHE_TTL_FUZZY',
    'HA_CACHE_TTL_CONFIG',
    'HA_API_TIMEOUT',
    'HA_WEBSOCKET_TIMEOUT',
    'HA_CONNECT_TIMEOUT',
    
    # Templates (NEW)
    'ALEXA_ERROR_RESPONSE',
    'ALEXA_SUCCESS_RESPONSE',
    'ALEXA_ACCEPT_GRANT_RESPONSE',
    'ALEXA_DISCOVERY_RESPONSE',
    
    # Alexa functions (7)
    'alexa_process_directive',
    'alexa_handle_discovery',
    'alexa_handle_control',
    'alexa_handle_power_control',
    'alexa_handle_brightness_control',
    'alexa_handle_thermostat_control',
    'alexa_handle_accept_grant',
    
    # Devices functions (14)
    'devices_get_states',
    'devices_get_by_id',
    'devices_find_fuzzy',
    'devices_update_state',
    'devices_call_service',
    'devices_list_by_domain',
    'devices_check_status',
    'devices_call_ha_api',
    'devices_get_ha_config',
    'devices_warm_cache',
    'devices_invalidate_entity_cache',
    'devices_invalidate_domain_cache',
    'devices_get_performance_report',
    'devices_get_diagnostic_info',
    
    # Assist functions (4)
    'assist_send_message',
    'assist_get_response',
    'assist_process_conversation',
    'assist_handle_pipeline',
]

# EOF
