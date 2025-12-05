# ha_build_config.py
"""
ha_build_config.py - Feature Configuration
Version: 3.0.0
Description: Feature flags and build configuration with debug tracing

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from enum import Enum
from typing import Dict, List, Set, Any

# ===== MODULE-LEVEL DEBUG MODE =====
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _debug_trace(correlation_id: str, step: str, **details):
    """
    Debug trace helper for HA build config operations.
    
    Args:
        correlation_id: Correlation ID for request tracing
        step: Step description
        **details: Additional details to log
    """
    if _DEBUG_MODE_ENABLED:
        from gateway import log_info
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [BUILD-CONFIG-TRACE] {step}" + (f" ({detail_str})" if detail_str else ""))


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
    from gateway import generate_correlation_id
    
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "parse_feature_list START", feature_string=feature_string)
    
    if not feature_string:
        _debug_trace(correlation_id, "parse_feature_list COMPLETE (default standard)")
        return COMMON_PRESETS['standard']
    
    feature_string = feature_string.lower().strip()
    
    # Check for preset
    if feature_string in COMMON_PRESETS:
        preset_features = COMMON_PRESETS[feature_string]
        _debug_trace(correlation_id, "parse_feature_list COMPLETE (preset)", 
                    preset=feature_string, count=len(preset_features))
        return preset_features
    
    # Parse individual features
    features = set()
    for feature_name in feature_string.split(','):
        feature_name = feature_name.strip()
        try:
            feature = HAFeature(feature_name)
            features.add(feature)
        except ValueError:
            _debug_trace(correlation_id, "Invalid feature ignored", feature=feature_name)
            continue
    
    result = features if features else COMMON_PRESETS['standard']
    _debug_trace(correlation_id, "parse_feature_list COMPLETE", count=len(result))
    
    return result


def get_required_modules(features: Set[HAFeature]) -> Set[str]:
    """Get required modules for feature set."""
    modules = set()
    
    for feature in features:
        feature_modules = FEATURE_MODULES.get(feature, [])
        modules.update(feature_modules)
    
    return modules


def get_enabled_features() -> Set[HAFeature]:
    """Get enabled features from environment."""
    from gateway import generate_correlation_id, increment_counter
    
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "get_enabled_features START")
    
    feature_string = os.getenv('HA_FEATURES', 'standard')
    features = parse_feature_list(feature_string)
    
    _debug_trace(correlation_id, "get_enabled_features COMPLETE", 
                count=len(features), source=feature_string)
    increment_counter('ha_build_config_features_loaded')
    
    return features


def is_feature_enabled(feature: HAFeature) -> bool:
    """Check if feature is enabled."""
    enabled = get_enabled_features()
    return feature in enabled


# ===== FEATURE VALIDATION =====

def validate_feature_dependencies(features: Set[HAFeature]) -> Dict[str, Any]:
    """Validate feature dependencies."""
    from gateway import generate_correlation_id, record_metric, increment_counter
    
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "validate_feature_dependencies START", feature_count=len(features))
    
    missing_deps = {}
    
    for feature in features:
        required_deps = FEATURE_DEPENDENCIES.get(feature, set())
        missing = required_deps - features
        
        if missing:
            missing_deps[feature.value] = [dep.value for dep in missing]
            _debug_trace(correlation_id, "Missing dependencies", 
                        feature=feature.value, missing=[d.value for d in missing])
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    if missing_deps:
        _debug_trace(correlation_id, "validate_feature_dependencies COMPLETE (INVALID)",
                    duration_ms=duration_ms, missing_count=len(missing_deps))
        increment_counter('ha_build_config_validation_failure')
        record_metric('ha_build_config_validation_duration_ms', duration_ms)
        return {
            'valid': False,
            'missing_dependencies': missing_deps
        }
    
    _debug_trace(correlation_id, "validate_feature_dependencies COMPLETE (VALID)",
                duration_ms=duration_ms)
    increment_counter('ha_build_config_validation_success')
    record_metric('ha_build_config_validation_duration_ms', duration_ms)
    
    return {'valid': True}


def get_feature_info() -> Dict[str, Any]:
    """Get current feature configuration info."""
    from gateway import generate_correlation_id
    
    correlation_id = generate_correlation_id()
    _debug_trace(correlation_id, "get_feature_info START")
    
    enabled = get_enabled_features()
    modules = get_required_modules(enabled)
    validation = validate_feature_dependencies(enabled)
    
    info = {
        'enabled_features': [f.value for f in enabled],
        'required_modules': sorted(list(modules)),
        'validation': validation,
        'preset': os.getenv('HA_FEATURES', 'standard')
    }
    
    _debug_trace(correlation_id, "get_feature_info COMPLETE", 
                features=len(enabled), modules=len(modules), valid=validation.get('valid'))
    
    return info

# EOF
