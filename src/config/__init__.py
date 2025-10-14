"""
config/__init__.py
Version: 2025.10.14.01
Description: Configuration subsystem package initialization

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

# Import gateway implementation functions (used by gateway.py)
from config_core import (
    _initialize_implementation,
    _get_parameter_implementation,
    _set_parameter_implementation,
    _get_category_implementation,
    _reload_implementation,
    _switch_preset_implementation,
    _get_state_implementation,
    _load_environment_implementation,
    _load_file_implementation,
    _validate_all_implementation
)

# Import main classes for extension use
from config_core import ConfigurationCore, _config_core
from config_state import ConfigurationState, ConfigurationVersion
from config_validator import ConfigurationValidator
from config_loader import (
    load_from_environment,
    load_from_file,
    apply_user_overrides,
    merge_configs
)

# Import tier/variable utilities
from variables import ConfigurationTier
from variables_utils import (
    get_full_system_configuration,
    get_preset_configuration
)

__all__ = [
    # Gateway implementation functions
    '_initialize_implementation',
    '_get_parameter_implementation',
    '_set_parameter_implementation',
    '_get_category_implementation',
    '_reload_implementation',
    '_switch_preset_implementation',
    '_get_state_implementation',
    '_load_environment_implementation',
    '_load_file_implementation',
    '_validate_all_implementation',
    
    # Core classes
    'ConfigurationCore',
    '_config_core',
    'ConfigurationState',
    'ConfigurationVersion',
    'ConfigurationValidator',
    
    # Loader functions
    'load_from_environment',
    'load_from_file',
    'apply_user_overrides',
    'merge_configs',
    
    # Variables
    'ConfigurationTier',
    'get_full_system_configuration',
    'get_preset_configuration',
]

# EOF
