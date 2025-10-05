"""
variables_utils.py - Ultra-Optimized Configuration System Utility Functions
Version: 2025.10.04.03
Description: Complete utility functions for configuration estimation and validation

DEPLOYMENT FIX: Removed relative imports for Lambda compatibility

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

import time
from typing import Dict, Any, List, Optional, Union
from variables import (
    ConfigurationTier, InterfaceType,
    CACHE_INTERFACE_CONFIG, LOGGING_INTERFACE_CONFIG, 
    METRICS_INTERFACE_CONFIG, SECURITY_INTERFACE_CONFIG,
    CIRCUIT_BREAKER_INTERFACE_CONFIG, SINGLETON_INTERFACE_CONFIG,
    CONFIGURATION_PRESETS
)

# ===== RESOURCE ESTIMATION FUNCTIONS =====

def estimate_cache_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for cache configuration tier."""
    config = CACHE_INTERFACE_CONFIG.get(tier, CACHE_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["cache_pools"]["total_cache_allocation_mb"]

def estimate_logging_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for logging configuration tier."""
    base_memory = {
        ConfigurationTier.MINIMUM: 0.5,
        ConfigurationTier.STANDARD: 2.0,
        ConfigurationTier.MAXIMUM: 6.0
    }
    return base_memory.get(tier, 0.5)

def estimate_metrics_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for metrics configuration tier."""
    base_memory = {
        ConfigurationTier.MINIMUM: 1.0,
        ConfigurationTier.STANDARD: 3.0,
        ConfigurationTier.MAXIMUM: 8.0
    }
    return base_memory.get(tier, 1.0)

def estimate_security_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for security configuration tier."""
    config = SECURITY_INTERFACE_CONFIG.get(tier, SECURITY_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["resource_allocation"]["total_security_memory_mb"]

def estimate_total_memory_usage(preset_name: str) -> float:
    """Estimate total memory usage for a configuration preset."""
    if preset_name not in CONFIGURATION_PRESETS:
        return 0.0
    
    preset = CONFIGURATION_PRESETS[preset_name]
    base_tier = preset["base_tier"]
    overrides = preset.get("overrides", {})
    
    total_memory = 0.0
    
    for interface_type in InterfaceType:
        tier = overrides.get(interface_type, base_tier)
        
        if interface_type == InterfaceType.CACHE:
            total_memory += estimate_cache_memory_usage(tier)
        elif interface_type == InterfaceType.LOGGING:
            total_memory += estimate_logging_memory_usage(tier)
        elif interface_type == InterfaceType.METRICS:
            total_memory += estimate_metrics_memory_usage(tier)
        elif interface_type == InterfaceType.SECURITY:
            total_memory += estimate_security_memory_usage(tier)
    
    return total_memory

def validate_preset_constraints(preset_name: str) -> Dict[str, Any]:
    """Validate that a preset meets AWS Lambda constraints."""
    if preset_name not in CONFIGURATION_PRESETS:
        return {
            "valid": False,
            "error": f"Unknown preset: {preset_name}"
        }
    
    preset = CONFIGURATION_PRESETS[preset_name]
    memory_estimate = preset.get("memory_estimate", 0)
    metric_estimate = preset.get("metric_estimate", 0)
    
    violations = []
    
    if memory_estimate > 128:
        violations.append(f"Memory estimate ({memory_estimate}MB) exceeds 128MB limit")
    
    if metric_estimate > 10:
        violations.append(f"Metric estimate ({metric_estimate}) exceeds 10 metric limit")
    
    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "memory_estimate_mb": memory_estimate,
        "metric_estimate": metric_estimate
    }

def get_preset_info(preset_name: str) -> Dict[str, Any]:
    """Get complete information about a configuration preset."""
    if preset_name not in CONFIGURATION_PRESETS:
        return {
            "exists": False,
            "error": f"Unknown preset: {preset_name}"
        }
    
    preset = CONFIGURATION_PRESETS[preset_name]
    validation = validate_preset_constraints(preset_name)
    
    return {
        "exists": True,
        "name": preset_name,
        "description": preset.get("description", ""),
        "base_tier": preset["base_tier"].value,
        "overrides": {k.value: v.value for k, v in preset.get("overrides", {}).items()},
        "memory_estimate_mb": preset.get("memory_estimate", 0),
        "metric_estimate": preset.get("metric_estimate", 0),
        "validation": validation
    }

def list_all_presets() -> List[Dict[str, Any]]:
    """List all available configuration presets with their info."""
    return [get_preset_info(name) for name in CONFIGURATION_PRESETS.keys()]

def recommend_preset(requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Recommend a preset based on requirements."""
    target_memory = requirements.get("max_memory_mb", 64)
    target_metrics = requirements.get("max_metrics", 5)
    features_needed = requirements.get("features", [])
    
    candidates = []
    
    for preset_name in CONFIGURATION_PRESETS.keys():
        preset = CONFIGURATION_PRESETS[preset_name]
        memory_est = preset.get("memory_estimate", 0)
        metric_est = preset.get("metric_estimate", 0)
        
        if memory_est <= target_memory and metric_est <= target_metrics:
            candidates.append({
                "name": preset_name,
                "memory_estimate": memory_est,
                "metric_estimate": metric_est,
                "score": memory_est + (metric_est * 5)
            })
    
    if not candidates:
        return {
            "success": False,
            "error": "No preset meets the specified requirements"
        }
    
    candidates.sort(key=lambda x: x["score"], reverse=True)
    recommended = candidates[0]
    
    return {
        "success": True,
        "recommended_preset": recommended["name"],
        "memory_estimate_mb": recommended["memory_estimate"],
        "metric_estimate": recommended["metric_estimate"],
        "alternatives": [c["name"] for c in candidates[1:3]]
    }

__all__ = [
    'estimate_cache_memory_usage',
    'estimate_logging_memory_usage',
    'estimate_metrics_memory_usage',
    'estimate_security_memory_usage',
    'estimate_total_memory_usage',
    'validate_preset_constraints',
    'get_preset_info',
    'list_all_presets',
    'recommend_preset'
]

# EOF
