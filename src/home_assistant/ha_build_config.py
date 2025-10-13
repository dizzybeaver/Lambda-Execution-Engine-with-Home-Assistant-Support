"""
ha_build_config.py
Version: 2025.10.13.08
Description: Home Assistant build configuration (Phase 5 - renamed for consistency)
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
from typing import Dict, List, Set, Any
from enum import Enum


class HAFeature(str, Enum):
    """Home Assistant feature modules - now consolidated."""
    ALEXA = "alexa"
    FEATURES = "features"  # Consolidated automation, scripts, input_helpers, notifications, conversation
    MANAGERS = "managers"  # Consolidated devices, areas, timers
    CORE = "core"  # Core utilities
    CONFIG = "config"  # Configuration


# Updated module mapping for consolidated structure
FEATURE_MODULES: Dict[HAFeature, str] = {
    HAFeature.ALEXA: "ha_alexa.py",
    HAFeature.FEATURES: "ha_features.py",
    HAFeature.MANAGERS: "ha_managers.py",
    HAFeature.CORE: "ha_core.py",
    HAFeature.CONFIG: "ha_config.py",
}


FEATURE_DEPENDENCIES: Dict[HAFeature, List[HAFeature]] = {
    HAFeature.ALEXA: [HAFeature.CORE, HAFeature.MANAGERS],
    HAFeature.FEATURES: [HAFeature.CORE],
    HAFeature.MANAGERS: [HAFeature.CORE],
    HAFeature.CORE: [],
    HAFeature.CONFIG: [],
}


COMMON_PRESETS: Dict[str, List[HAFeature]] = {
    "minimal": [
        HAFeature.ALEXA,
        HAFeature.CORE,
        HAFeature.CONFIG,
    ],
    "voice_control": [
        HAFeature.ALEXA,
        HAFeature.CORE,
        HAFeature.CONFIG,
        HAFeature.FEATURES,
    ],
    "full": [
        HAFeature.ALEXA,
        HAFeature.FEATURES,
        HAFeature.MANAGERS,
        HAFeature.CORE,
        HAFeature.CONFIG,
    ],
}


def parse_feature_list(feature_str: str) -> Set[HAFeature]:
    """Parse comma-separated feature list from environment variable."""
    if not feature_str:
        return set(COMMON_PRESETS["full"])
    
    feature_str = feature_str.strip().lower()
    
    if feature_str in COMMON_PRESETS:
        return set(COMMON_PRESETS[feature_str])
    
    features = set()
    for item in feature_str.split(','):
        item = item.strip()
        try:
            features.add(HAFeature(item))
        except ValueError:
            pass
    
    return features if features else set(COMMON_PRESETS["full"])


def get_required_modules(features: Set[HAFeature]) -> Set[str]:
    """Get all required modules for given features including dependencies."""
    required = set()
    to_process = list(features)
    processed = set()
    
    while to_process:
        feature = to_process.pop(0)
        
        if feature in processed:
            continue
        
        processed.add(feature)
        required.add(FEATURE_MODULES[feature])
        
        for dep in FEATURE_DEPENDENCIES.get(feature, []):
            if dep not in processed:
                to_process.append(dep)
    
    return required


def get_enabled_features() -> Set[HAFeature]:
    """Get enabled features from environment."""
    feature_str = os.environ.get('HA_FEATURES', 'full')
    return parse_feature_list(feature_str)


def is_feature_enabled(feature: HAFeature) -> bool:
    """Check if a specific feature is enabled."""
    return feature in get_enabled_features()


__all__ = [
    'HAFeature',
    'FEATURE_MODULES',
    'FEATURE_DEPENDENCIES',
    'COMMON_PRESETS',
    'parse_feature_list',
    'get_required_modules',
    'get_enabled_features',
    'is_feature_enabled',
]

# EOF
