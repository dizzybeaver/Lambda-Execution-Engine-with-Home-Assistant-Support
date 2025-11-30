# ha_interconnect.py
"""
ha_interconnect.py - Home Assistant Gateway (HA-SUGA) - Main Entry Point
Version: 4.0.0 - MODULAR STRUCTURE
Date: 2025-11-05
Purpose: Central gateway importing from specialized wrappers

ARCHITECTURE CHANGE v4.0.0:
- Split 691-line file into 5 modular files (SIMAv4 compliance)
- All files ≤400 lines for visibility in project knowledge
- Follows gateway/gateway_wrappers pattern
- Clean separation by interface (Alexa, Devices, Assist)
- Shared validation helpers in separate module

Structure:
ha_interconnect.py (main, 80 lines)
  ├─→ ha_interconnect_validation.py (8 helpers, 160 lines)
  ├─→ ha_interconnect_alexa.py (7 functions, 150 lines)
  ├─→ ha_interconnect_devices.py (14 functions, 300 lines)
  └─→ ha_interconnect_assist.py (4 functions, 100 lines)

Total: 790 lines across 5 files (vs 691 in 1 file)
Benefits: Better organization, all files visible, easier maintenance

Pattern:
This is the ONLY entry point for Home Assistant operations.
All HA internal calls route through this gateway.
External calls to LEE route through LEE's gateway.py.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# Import validation helpers
from .ha_interconnect_validation import (
    _validate_entity_id,
    _validate_domain,
    _validate_event,
    _validate_threshold,
    _validate_endpoint,
    _validate_http_method,
    _validate_message,
)

# Import Alexa gateway functions
from .ha_interconnect_alexa import (
    alexa_process_directive,
    alexa_handle_discovery,
    alexa_handle_control,
    alexa_handle_power_control,
    alexa_handle_brightness_control,
    alexa_handle_thermostat_control,
    alexa_handle_accept_grant,
)

# Import Devices gateway functions
from .ha_interconnect_devices import (
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
from .ha_interconnect_assist import (
    assist_send_message,
    assist_get_response,
    assist_process_conversation,
    assist_handle_pipeline,
)


# ====================
# EXPORTS
# ====================

__all__ = [
    # Validation helpers (internal use, not typically called externally)
    '_validate_entity_id',
    '_validate_domain',
    '_validate_event',
    '_validate_threshold',
    '_validate_endpoint',
    '_validate_http_method',
    '_validate_message',
    
    # Alexa interface (7 functions)
    'alexa_process_directive',
    'alexa_handle_discovery',
    'alexa_handle_control',
    'alexa_handle_power_control',
    'alexa_handle_brightness_control',
    'alexa_handle_thermostat_control',
    'alexa_handle_accept_grant',
    
    # Devices interface (14 functions)
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
    
    # Assist interface (4 functions)
    'assist_send_message',
    'assist_get_response',
    'assist_process_conversation',
    'assist_handle_pipeline',
]

# MODULAR GATEWAY v4.0.0:
# - Central entry point imports from specialized wrappers
# - No circular imports (clean dependency tree)
# - All wrappers ≤400 lines (SIMAv4 compliant)
# - Follows gateway/gateway_wrappers pattern from LEE
# - Easy to extend (add functions to appropriate wrapper)
# - Easy to maintain (changes localized to specific files)
# - Security hardening via input validation (CRIT-03 compliant)

# BACKWARD COMPATIBILITY:
# All existing imports still work:
#   from ha_interconnect import alexa_process_directive
#   from ha_interconnect import devices_get_states
#   from ha_interconnect import assist_send_message
# No breaking changes for consumers.

# EOF
