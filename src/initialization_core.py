"""
initialization_core.py
Version: 2025.10.14.01
Description: Lambda initialization with SUGA compliance, flag management, and comprehensive status tracking

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
import time
from typing import Dict, Any, Optional
from enum import Enum


_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== INITIALIZATION OPERATION ENUM =====

class InitializationOperation(Enum):
    """Enumeration of all initialization operations."""
    INITIALIZE = "initialize"
    GET_CONFIG = "get_config"
    IS_INITIALIZED = "is_initialized"
    RESET = "reset"
    GET_STATUS = "get_status"
    SET_FLAG = "set_flag"
    GET_FLAG = "get_flag"


# ===== INITIALIZATION CORE CLASS =====

class InitializationCore:
    """Handles Lambda environment initialization with flag management and status tracking."""
    
    def __init__(self):
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._flags: Dict[str, Any] = {}
        self._init_timestamp: Optional[float] = None
        self._init_duration_ms: Optional[float] = None
    
    def initialize(self, **kwargs) -> Dict[str, Any]:
        """Initialize Lambda environment."""
        if self._initialized:
            return {
                'status': 'already_initialized',
                'config': self._config,
                'timestamp': self._init_timestamp
            }
        
        start_time = time.time()
        
        self._config = {
            'aws_region': os.environ.get('AWS_REGION', 'us-east-1'),
            'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'unknown'),
            'memory_limit': os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE', '128'),
            'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
            'environment': os.environ.get('ENVIRONMENT', 'production'),
            'use_generic_operations': _USE_GENERIC_OPERATIONS,
            'python_version': os.environ.get('AWS_EXECUTION_ENV', 'unknown')
        }
        
        # Apply any custom config from kwargs
        if kwargs:
            self._config.update({k: v for k, v in kwargs.items() if k not in self._config})
        
        self._initialized = True
        self._init_timestamp = time.time()
        self._init_duration_ms = (self._init_timestamp - start_time) * 1000
        
        return {
            'status': 'initialized',
            'config': self._config,
            'timestamp': self._init_timestamp,
            'duration_ms': self._init_duration_ms
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get initialization config."""
        return self._config.copy()
    
    def is_initialized(self) -> bool:
        """Check if initialized."""
        return self._initialized
    
    def reset(self) -> Dict[str, Any]:
        """Reset initialization state."""
        was_initialized = self._initialized
        
        self._initialized = False
        self._config.clear()
        self._flags.clear()
        self._init_timestamp = None
        self._init_duration_ms = None
        
        return {
            'status': 'reset',
            'was_initialized': was_initialized,
            'timestamp': time.time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive initialization status."""
        return {
            'initialized': self._initialized,
            'config': self._config.copy() if self._initialized else {},
            'flags': self._flags.copy(),
            'init_timestamp': self._init_timestamp,
            'init_duration_ms': self._init_duration_ms,
            'uptime_seconds': (time.time() - self._init_timestamp) if self._init_timestamp else None,
            'flag_count': len(self._flags),
            'config_keys': list(self._config.keys()) if self._initialized else [],
            'use_generic_operations': _USE_GENERIC_OPERATIONS
        }
    
    def set_flag(self, flag_name: str, value: Any) -> Dict[str, Any]:
        """Set an initialization flag."""
        if not flag_name:
            return {
                'success': False,
                'error': 'Flag name cannot be empty',
                'flag_name': flag_name
            }
        
        old_value = self._flags.get(flag_name)
        self._flags[flag_name] = value
        
        return {
            'success': True,
            'flag_name': flag_name,
            'value': value,
            'old_value': old_value,
            'was_new': old_value is None
        }
    
    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """Get an initialization flag value."""
        return self._flags.get(flag_name, default)


# ===== SINGLETON INSTANCE =====

_INITIALIZATION = InitializationCore()


# ===== GENERIC OPERATION EXECUTION =====

def execute_initialization_operation(operation: InitializationOperation, *args, **kwargs):
    """
    Universal initialization operation executor.
    
    Single function that routes all initialization operations to the InitializationCore instance.
    """
    if not _USE_GENERIC_OPERATIONS:
        return _execute_legacy_operation(operation, *args, **kwargs)
    
    try:
        method_name = operation.value
        method = getattr(_INITIALIZATION, method_name, None)
        
        if method is None:
            default_returns = {
                InitializationOperation.INITIALIZE: {},
                InitializationOperation.GET_CONFIG: {},
                InitializationOperation.GET_STATUS: {},
                InitializationOperation.IS_INITIALIZED: False,
                InitializationOperation.RESET: {},
                InitializationOperation.GET_FLAG: kwargs.get('default'),
                InitializationOperation.SET_FLAG: {'success': False, 'error': 'Method not found'}
            }
            return default_returns.get(operation, None)
        
        return method(*args, **kwargs)
    except Exception as e:
        default_returns = {
            InitializationOperation.INITIALIZE: {},
            InitializationOperation.GET_CONFIG: {},
            InitializationOperation.GET_STATUS: {'error': str(e)},
            InitializationOperation.IS_INITIALIZED: False,
            InitializationOperation.RESET: {},
            InitializationOperation.GET_FLAG: kwargs.get('default'),
            InitializationOperation.SET_FLAG: {'success': False, 'error': str(e)}
        }
        return default_returns.get(operation, None)


def _execute_legacy_operation(operation: InitializationOperation, *args, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    try:
        method = getattr(_INITIALIZATION, operation.value)
        return method(*args, **kwargs)
    except Exception as e:
        default_returns = {
            InitializationOperation.INITIALIZE: {},
            InitializationOperation.GET_CONFIG: {},
            InitializationOperation.GET_STATUS: {'error': str(e)},
            InitializationOperation.IS_INITIALIZED: False,
            InitializationOperation.RESET: {},
            InitializationOperation.GET_FLAG: kwargs.get('default'),
            InitializationOperation.SET_FLAG: {'success': False, 'error': str(e)}
        }
        return default_returns.get(operation, None)


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_initialize_implementation(**kwargs) -> Dict[str, Any]:
    """Execute initialization."""
    return execute_initialization_operation(InitializationOperation.INITIALIZE, **kwargs)


def _execute_get_config_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get config."""
    return execute_initialization_operation(InitializationOperation.GET_CONFIG, **kwargs)


def _execute_is_initialized_implementation(**kwargs) -> bool:
    """Execute is initialized check."""
    return execute_initialization_operation(InitializationOperation.IS_INITIALIZED, **kwargs)


def _execute_reset_implementation(**kwargs) -> Dict[str, Any]:
    """Execute reset."""
    return execute_initialization_operation(InitializationOperation.RESET, **kwargs)


def _execute_get_status_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get status - comprehensive initialization state."""
    return execute_initialization_operation(InitializationOperation.GET_STATUS, **kwargs)


def _execute_set_flag_implementation(flag_name: str = None, value: Any = None, **kwargs) -> Dict[str, Any]:
    """Execute set flag - set initialization flag."""
    if flag_name is None:
        flag_name = kwargs.get('flag_name', '')
    if value is None:
        value = kwargs.get('value')
    
    return execute_initialization_operation(
        InitializationOperation.SET_FLAG,
        flag_name=flag_name,
        value=value
    )


def _execute_get_flag_implementation(flag_name: str = None, default: Any = None, **kwargs) -> Any:
    """Execute get flag - retrieve initialization flag value."""
    if flag_name is None:
        flag_name = kwargs.get('flag_name', '')
    if default is None:
        default = kwargs.get('default')
    
    return execute_initialization_operation(
        InitializationOperation.GET_FLAG,
        flag_name=flag_name,
        default=default
    )


# ===== EXPORTS =====

__all__ = [
    # Enums
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
