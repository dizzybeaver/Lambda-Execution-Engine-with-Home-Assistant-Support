"""
config_validator.py
Version: 2025.10.14.01
Description: Configuration validation logic for Lambda Execution Engine

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

from typing import Dict, Any, Callable, Set


# ===== VALIDATION CLASS =====

class ConfigurationValidator:
    """Validates configuration changes with custom validators."""
    
    def __init__(self):
        self._validators: Dict[str, Callable] = {}
        self._critical_keys: Set[str] = {
            'aws_region', 'lambda_timeout', 'memory_limit',
            'configuration_tier', 'parameter_prefix'
        }
    
    def register_validator(self, key: str, validator: Callable):
        """Register custom validator for configuration key."""
        self._validators[key] = validator
    
    def validate_change(self, key: str, value: Any) -> tuple:
        """Validate configuration change."""
        if key in self._validators:
            return self._validators[key](value)
        return True, None
    
    def is_critical(self, key: str) -> bool:
        """Check if key is critical (requires restart)."""
        return key in self._critical_keys
    
    def validate_all_sections(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all engine configuration sections."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sections_validated": []
        }
        
        # Validate core categories
        core_categories = [
            'cache', 'logging', 'metrics', 'security', 
            'circuit_breaker', 'singleton', 'http_client',
            'lambda_opt', 'cost_protection', 'utility', 'initialization'
        ]
        
        for category in core_categories:
            if category in config:
                validation["sections_validated"].append(category)
                # Add specific validation logic per category if needed
        
        # Check for required system settings
        if 'system' in config:
            if 'aws_region' not in config['system']:
                validation["warnings"].append("aws_region not specified, using default")
        
        return validation


# ===== EXPORTS =====

__all__ = [
    'ConfigurationValidator'
]

# EOF
