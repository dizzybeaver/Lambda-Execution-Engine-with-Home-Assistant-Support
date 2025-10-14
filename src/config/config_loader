"""
config_loader.py
Version: 2025.10.14.01
Description: Configuration loading operations for Lambda Execution Engine

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
import json
from typing import Dict, Any
from variables import ConfigurationTier


# ===== LOADING FUNCTIONS =====

def load_from_environment(active_tier: ConfigurationTier, use_parameter_store: bool, parameter_prefix: str) -> Dict[str, Any]:
    """Load configuration from environment variables with tier support."""
    config = {
        "system": {
            "aws_region": os.environ.get('AWS_REGION', 'us-east-1'),
            "debug_mode": os.environ.get('DEBUG_MODE', 'false').lower() == 'true',
            "configuration_tier": os.environ.get('CONFIGURATION_TIER', 'standard'),
            "use_parameter_store": use_parameter_store,
            "parameter_prefix": parameter_prefix
        }
    }
    
    # Load tier configuration
    try:
        tier_name = config["system"]["configuration_tier"]
        tier = ConfigurationTier(tier_name)
        
        # Load tier-specific settings from variables.py
        from variables_utils import get_full_system_configuration
        tier_config = get_full_system_configuration(tier, {})
        
        # Merge tier config into base config (excluding metadata)
        for category, settings in tier_config.items():
            if category != '_metadata' and isinstance(settings, dict):
                if category not in config:
                    config[category] = {}
                config[category].update(settings)
        
    except Exception as e:
        from gateway import log_warning
        log_warning(f"Failed to load tier config: {e}")
    
    return config


def load_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        from gateway import log_error
        log_error(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        from gateway import log_error
        log_error(f"Invalid JSON in config file: {e}")
        return {}
    except Exception as e:
        from gateway import log_error
        log_error(f"Failed to load config file: {e}")
        return {}


def apply_user_overrides(base_config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply user custom configuration overrides."""
    try:
        from user_config import USER_CUSTOM_CONFIG
        
        if USER_CUSTOM_CONFIG:
            from gateway import log_info
            merged = merge_configs(base_config, USER_CUSTOM_CONFIG)
            log_info(f"Applied user config overrides: {len(USER_CUSTOM_CONFIG)} categories")
            return merged
            
    except ImportError:
        pass
    except Exception as e:
        from gateway import log_error
        log_error(f"Error applying user overrides: {e}")
    
    return base_config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge configuration dictionaries."""
    merged = base.copy()
    
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


# ===== EXPORTS =====

__all__ = [
    'load_from_environment',
    'load_from_file',
    'apply_user_overrides',
    'merge_configs'
]

# EOF
