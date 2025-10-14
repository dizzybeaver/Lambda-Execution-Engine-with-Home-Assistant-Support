"""
home_assistant/__init__.py - Home Assistant Package Exports
Version: 2025.10.14.01
Description: Exports for home_assistant package (Alexa, features, managers, core).

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

# Alexa Integration
from ha_alexa import AlexaSmartHomeManager

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
)

# Configuration Loading
from ha_config import (
    load_ha_config,
    validate_ha_config,
    get_ha_preset,
    load_ha_connection_config,
    load_ha_preset_config,
)

# Core Operations
from ha_core import (
    batch_get_states,
    call_ha_service,
    is_ha_available,
    get_ha_config,
    filter_exposed_entities,
    ha_operation_wrapper,
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES,
)

# Feature Operations
from ha_features import (
    # Automation
    list_automations,
    trigger_automation,
    # Scripts
    list_scripts,
    run_script,
    # Input Helpers
    list_input_helpers,
    set_input_helper,
    # Notifications
    send_notification,
    # Conversation
    process_conversation,
)

# Generic Managers
from ha_managers import HAGenericManager

# Testing
from ha_tests import (
    is_ha_extension_available,
)

__all__ = [
    # Alexa
    'AlexaSmartHomeManager',
    
    # Build Configuration
    'HAFeature',
    'FEATURE_MODULES',
    'FEATURE_DEPENDENCIES',
    'COMMON_PRESETS',
    'parse_feature_list',
    'get_required_modules',
    'get_enabled_features',
    'is_feature_enabled',
    
    # Configuration
    'load_ha_config',
    'validate_ha_config',
    'get_ha_preset',
    'load_ha_connection_config',
    'load_ha_preset_config',
    
    # Core Operations
    'batch_get_states',
    'call_ha_service',
    'is_ha_available',
    'get_ha_config',
    'filter_exposed_entities',
    'ha_operation_wrapper',
    'fuzzy_match_name',
    'HA_CACHE_TTL_ENTITIES',
    
    # Feature Operations - Automation
    'list_automations',
    'trigger_automation',
    
    # Feature Operations - Scripts
    'list_scripts',
    'run_script',
    
    # Feature Operations - Input Helpers
    'list_input_helpers',
    'set_input_helper',
    
    # Feature Operations - Notifications
    'send_notification',
    
    # Feature Operations - Conversation
    'process_conversation',
    
    # Managers
    'HAGenericManager',
    
    # Testing
    'is_ha_extension_available',
]

# EOF
