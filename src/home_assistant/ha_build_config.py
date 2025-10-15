"""
home_assistant/ha_build_config.py - Feature Configuration
Version: 2025.10.14.01
Description: Feature flags and build configuration for HA extension.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from enum import Enum
from typing import Dict, List, Set, Any

# ===== FEATURE ENUMERATION =====

class HAFeature(Enum):
    """HA feature flags."""
    CORE = "core"
    ALEXA = "alexa"
    AUTOMATIONS = "automations"
    SCRIPTS = "scripts"
    INPUT_HELPERS = "input_helpers"
    NOTIFICATIONS = "notifications"
    CONVERSATION = "conversation"
    MANAGERS = "managers"
    WEBSOCKET = "websocket"

# ===== FEATURE MODULES =====

FEATURE_MODULES = {
    HAFeature.CORE: ['ha_core', 'ha_config'],
    HAFeature.ALEXA: ['ha_alexa'],
    HAFeature.AUTOMATIONS: ['ha_features'],
    HAFeature.SCRIPTS: ['ha_features'],
    HAFeature.INPUT_HELPERS: ['ha_features'],
    HAFeature.NOTIFICATIONS: ['ha_features'],
    HAFeature.CONVERSATION: ['ha_features'],
    HAFeature.MANAGERS: ['ha_managers'],
    HAFeature.WEBSOCKET: ['ha_websocket'],
}

# ===== FEATURE DEPENDENCIES =====

FEATURE_DEPENDENCIES = {
    HAFeature.CORE: set(),
    HAFeature.ALEXA: {HAFeature.CORE, HAFeature.MANAGERS},
    HAFeature.AUTOMATIONS: {HAFeature.CORE},
    HAFeature.SCRIPTS: {HAFeature.CORE},
    HAFeature.INPUT_HELPERS: {HAFeature.CORE},
    HAFeature.NOTIFICATIONS: {HAFeature.CORE},
    HAFeature.CONVERSATION: {HAFeature.CORE},
    HAFeature.MANAGERS: {HAFeature.CORE},
    HAFeature.WEBSOCKET: {HAFeature.CORE},
}

# ===== COMMON PRESETS =====

COMMON_PRESETS = {
    'minimal': {HAFeature.CORE},
    'basic': {HAFeature.CORE, HAFeature.ALEXA, HAFeature.MANAGERS},
    'standard': {
        HAFeature.CORE, HAFeature.ALEXA, HAFeature.AUTOMATIONS,
        HAFeature.SCRIPTS, HAFeature.MANAGERS
    },
    'full': {
        HAFeature.CORE, HAFeature.ALEXA, HAFeature.AUTOMATIONS,
        HAFeature.SCRIPTS, HAFeature.INPUT_HELPERS, HAFeature.NOTIFICATIONS,
        HAFeature.CONVERSATION, HAFeature.MANAGERS
    },
    'development': {
        HAFeature.CORE, HAFeature.ALEXA, HAFeature.AUTOMATIONS,
        HAFeature.SCRIPTS, HAFeature.INPUT_HELPERS, HAFeature.NOTIFICATIONS,
        HAFeature.CONVERSATION, HAFeature.MANAGERS, HAFeature.WEBSOCKET
    },
}

# ===== FEATURE PARSING =====

def parse_feature_list(feature_string: str) -> Set[HAFeature]:
    """Parse feature string from environment."""
    if not feature_string:
        return COMMON_PRESETS['standard']
    
    feature_string = feature_string.lower().strip()
    
    # Check for preset
    if feature_string in COMMON_PRESETS:
        return COMMON_PRESETS[feature_string]
    
    # Parse individual features
    features = set()
    for feature_name in feature_string.split(','):
        feature_name = feature_name.strip()
        try:
            feature = HAFeature(feature_name)
            features.add(feature)
        except ValueError:
            continue
    
    return features if features else COMMON_PRESETS['standard']


def get_required_modules(features: Set[HAFeature]) -> Set[str]:
    """Get required modules for feature set."""
    modules = set()
    
    for feature in features:
        feature_modules = FEATURE_MODULES.get(feature, [])
        modules.update(feature_modules)
    
    return modules


def get_enabled_features() -> Set[HAFeature]:
    """Get enabled features from environment."""
    feature_string = os.getenv('HA_FEATURES', 'standard')
    return parse_feature_list(feature_string)


def is_feature_enabled(feature: HAFeature) -> bool:
    """Check if feature is enabled."""
    enabled = get_enabled_features()
    return feature in enabled


# ===== FEATURE VALIDATION =====

def validate_feature_dependencies(features: Set[HAFeature]) -> Dict[str, Any]:
    """Validate feature dependencies."""
    missing_deps = {}
    
    for feature in features:
        required_deps = FEATURE_DEPENDENCIES.get(feature, set())
        missing = required_deps - features
        
        if missing:
            missing_deps[feature.value] = [dep.value for dep in missing]
    
    if missing_deps:
        return {
            'valid': False,
            'missing_dependencies': missing_deps
        }
    
    return {'valid': True}


def get_feature_info() -> Dict[str, Any]:
    """Get current feature configuration info."""
    enabled = get_enabled_features()
    modules = get_required_modules(enabled)
    validation = validate_feature_dependencies(enabled)
    
    return {
        'enabled_features': [f.value for f in enabled],
        'required_modules': sorted(list(modules)),
        'validation': validation,
        'preset': os.getenv('HA_FEATURES', 'standard')
    }


# EOF
