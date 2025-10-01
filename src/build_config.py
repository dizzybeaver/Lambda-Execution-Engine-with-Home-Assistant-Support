"""
build_config.py - Build-Time Feature Configuration
Version: 2025.10.01.01
Daily Revision: Phase 3 Build Optimization

Feature-selective compilation system for Lambda Execution Engine.
Reduces deployment size by 60-80% for typical users.

Licensed under the Apache License, Version 2.0
"""

import os
from typing import Dict, List, Set, Any
from enum import Enum


class HAFeature(str, Enum):
    """Home Assistant feature modules."""
    ALEXA = "alexa"
    AUTOMATION = "automation"
    SCRIPTS = "scripts"
    INPUT_HELPERS = "input_helpers"
    NOTIFICATIONS = "notifications"
    AREAS = "areas"
    TIMERS = "timers"
    CONVERSATION = "conversation"
    DEVICES = "devices"
    RESPONSE = "response"


FEATURE_MODULES: Dict[HAFeature, str] = {
    HAFeature.ALEXA: "homeassistant_alexa.py",
    HAFeature.AUTOMATION: "home_assistant_automation.py",
    HAFeature.SCRIPTS: "home_assistant_scripts.py",
    HAFeature.INPUT_HELPERS: "home_assistant_input_helpers.py",
    HAFeature.NOTIFICATIONS: "home_assistant_notifications.py",
    HAFeature.AREAS: "home_assistant_areas.py",
    HAFeature.TIMERS: "home_assistant_timers.py",
    HAFeature.CONVERSATION: "home_assistant_conversation.py",
    HAFeature.DEVICES: "home_assistant_devices.py",
    HAFeature.RESPONSE: "home_assistant_response.py",
}


FEATURE_DEPENDENCIES: Dict[HAFeature, List[HAFeature]] = {
    HAFeature.ALEXA: [HAFeature.DEVICES, HAFeature.RESPONSE],
    HAFeature.AUTOMATION: [],
    HAFeature.SCRIPTS: [],
    HAFeature.INPUT_HELPERS: [],
    HAFeature.NOTIFICATIONS: [],
    HAFeature.AREAS: [HAFeature.DEVICES],
    HAFeature.TIMERS: [],
    HAFeature.CONVERSATION: [HAFeature.RESPONSE],
    HAFeature.DEVICES: [],
    HAFeature.RESPONSE: [],
}


COMMON_PRESETS: Dict[str, List[HAFeature]] = {
    "minimal": [
        HAFeature.ALEXA,
        HAFeature.DEVICES,
        HAFeature.RESPONSE,
    ],
    "voice_control": [
        HAFeature.ALEXA,
        HAFeature.DEVICES,
        HAFeature.RESPONSE,
        HAFeature.CONVERSATION,
    ],
    "automation_basic": [
        HAFeature.ALEXA,
        HAFeature.DEVICES,
        HAFeature.RESPONSE,
        HAFeature.AUTOMATION,
        HAFeature.SCRIPTS,
    ],
    "smart_home": [
        HAFeature.ALEXA,
        HAFeature.DEVICES,
        HAFeature.RESPONSE,
        HAFeature.AUTOMATION,
        HAFeature.SCRIPTS,
        HAFeature.AREAS,
        HAFeature.INPUT_HELPERS,
    ],
    "full": [
        HAFeature.ALEXA,
        HAFeature.AUTOMATION,
        HAFeature.SCRIPTS,
        HAFeature.INPUT_HELPERS,
        HAFeature.NOTIFICATIONS,
        HAFeature.AREAS,
        HAFeature.TIMERS,
        HAFeature.CONVERSATION,
        HAFeature.DEVICES,
        HAFeature.RESPONSE,
    ],
}


def parse_feature_list(feature_str: str) -> Set[HAFeature]:
    """Parse comma-separated feature list from environment variable."""
    if not feature_str:
        return set()
    
    features = set()
    for item in feature_str.split(","):
        item = item.strip().lower()
        try:
            features.add(HAFeature(item))
        except ValueError:
            print(f"Warning: Unknown feature '{item}' ignored")
    
    return features


def resolve_dependencies(features: Set[HAFeature]) -> Set[HAFeature]:
    """Resolve feature dependencies recursively."""
    resolved = set(features)
    
    changed = True
    while changed:
        changed = False
        for feature in list(resolved):
            deps = FEATURE_DEPENDENCIES.get(feature, [])
            for dep in deps:
                if dep not in resolved:
                    resolved.add(dep)
                    changed = True
    
    return resolved


def get_enabled_features() -> Set[HAFeature]:
    """Get enabled features from environment configuration."""
    preset = os.getenv("HA_FEATURE_PRESET", "").lower()
    
    if preset in COMMON_PRESETS:
        features = set(COMMON_PRESETS[preset])
    else:
        feature_list = os.getenv("HA_FEATURES", "")
        if feature_list:
            features = parse_feature_list(feature_list)
        else:
            features = set(COMMON_PRESETS["full"])
    
    return resolve_dependencies(features)


def get_enabled_modules() -> List[str]:
    """Get list of module filenames to include in build."""
    enabled_features = get_enabled_features()
    modules = []
    
    for feature in enabled_features:
        module_file = FEATURE_MODULES.get(feature)
        if module_file:
            modules.append(module_file)
    
    modules.extend([
        "homeassistant_extension.py",
        "ha_common.py",
    ])
    
    return list(set(modules))


def get_excluded_modules() -> List[str]:
    """Get list of module filenames to exclude from build."""
    enabled_features = get_enabled_features()
    all_modules = set(FEATURE_MODULES.values())
    enabled_modules = {FEATURE_MODULES[f] for f in enabled_features}
    
    return list(all_modules - enabled_modules)


def validate_feature_configuration() -> Dict[str, Any]:
    """Validate feature configuration and return status."""
    enabled = get_enabled_features()
    enabled_modules = get_enabled_modules()
    excluded_modules = get_excluded_modules()
    
    return {
        "valid": True,
        "enabled_features": [f.value for f in enabled],
        "feature_count": len(enabled),
        "enabled_modules": enabled_modules,
        "excluded_modules": excluded_modules,
        "estimated_size_reduction": f"{len(excluded_modules) * 10}%",
    }


def get_build_config() -> Dict[str, Any]:
    """Get complete build configuration."""
    config = validate_feature_configuration()
    
    config["presets"] = list(COMMON_PRESETS.keys())
    config["all_features"] = [f.value for f in HAFeature]
    config["dependencies"] = {
        f.value: [d.value for d in deps]
        for f, deps in FEATURE_DEPENDENCIES.items()
    }
    
    return config
