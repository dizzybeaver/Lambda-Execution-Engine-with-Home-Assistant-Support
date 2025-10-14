"""
initialization/__init__.py - Initialization Package Exports
Version: 2025.10.14.01
Description: Exports for initialization package (Lambda environment initialization)

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
from initialization_core import (
    # Enum
    InitializationOperation,
    
    # Core Class
    InitializationCore,
    
    # Operation Executor
    execute_initialization_operation,
    
    # Gateway Implementation Functions
    _execute_initialize_implementation,
    _execute_get_config_implementation,
    _execute_is_initialized_implementation,
    _execute_reset_implementation,
    _execute_get_status_implementation,
    _execute_set_flag_implementation,
    _execute_get_flag_implementation,
)

__all__ = [
    # Enum
    'InitializationOperation',
    
    # Core Class
    'InitializationCore',
    
    # Operation Executor
    'execute_initialization_operation',
    
    # Gateway Implementation Functions
    '_execute_initialize_implementation',
    '_execute_get_config_implementation',
    '_execute_is_initialized_implementation',
    '_execute_reset_implementation',
    '_execute_get_status_implementation',
    '_execute_set_flag_implementation',
    '_execute_get_flag_implementation',
]

# EOF
