"""
initialization_core.py
Version: 2025.10.17.11
Description: Lambda initialization with SUGA compliance and idempotency

CHANGELOG:
- 2025.10.17.11: Added idempotency check (Issue #44 fix)
  - initialize() now returns cached result if already initialized
  - Prevents duplicate initialization on repeated calls
  - Added uptime tracking to already_initialized response
  - Improved thread safety around initialization check
- 2025.10.16.01: Fixed thread safety, error handling, parameter validation

CRITICAL FIXES (2025.10.16.01):
- Added thread safety with Lock to protect shared state
- Removed circular indirection (direct _INITIALIZATION calls)
- Improved error handling (proper exceptions instead of silent defaults)
- Fixed parameter validation for all operations
- Added consistent flag name validation
- Improved parameter extraction logic

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
import sys
import time
from typing import Dict, Any, Optional
from threading import Lock
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
    """
    Handles Lambda environment initialization with thread safety and idempotency.
    
    Thread-safe singleton manager for initialization state, configuration,
    and runtime flags. Ensures initialization happens exactly once per container.
    """
    
    def __init__(self):
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._flags: Dict[str, Any] = {}
        self._init_timestamp: Optional[float] = None
        self._init_duration_ms: Optional[float] = None
        self._lock = Lock()
    
    def initialize(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Initialize Lambda environment with thread safety and idempotency (Issue #44).
        
        Idempotency guarantee: Calling initialize() multiple times is safe.
        If already initialized, returns cached result immediately without
        re-initializing. This prevents duplicate work on repeated calls.
        
        Args:
            config: Optional configuration dictionary to store
            **kwargs: Additional configuration items (merged with config dict)
            
        Returns:
            Dictionary with initialization status:
            - First call: {'status': 'initialized', ...}
            - Subsequent calls: {'status': 'already_initialized', ...}
            
        Thread Safety:
            Double-checked locking ensures thread-safe initialization
            even if called concurrently from multiple threads.
        """
        # Fast path: check without lock first (optimization)
        if self._initialized:
            with self._lock:
                # Double-check with lock for thread safety
                if self._initialized:
                    return {
                        'status': 'already_initialized',
                        'cached': True,
                        'timestamp': self._init_timestamp,
                        'init_duration_ms': self._init_duration_ms,
                        'uptime_seconds': time.time() - self._init_timestamp if self._init_timestamp else 0,
                        'config_keys': list(self._config.keys())
                    }
        
        # Slow path: actually initialize
        with self._lock:
            # Triple-check inside lock (another thread might have initialized)
            if self._initialized:
                return {
                    'status': 'already_initialized',
                    'cached': True,
                    'timestamp': self._init_timestamp,
                    'init_duration_ms': self._init_duration_ms,
                    'uptime_seconds': time.time() - self._init_timestamp if self._init_timestamp else 0,
                    'config_keys': list(self._config.keys())
                }
            
            start_time = time.time()
            
            # Merge config and kwargs
            if config is None:
                config = {}
            self._config = {**config, **kwargs}
            
            # Mark as initialized (atomic with config update)
            self._initialized = True
            self._init_timestamp = start_time
            self._init_duration_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'initialized',
                'cached': False,
                'timestamp': self._init_timestamp,
                'duration_ms': self._init_duration_ms,
                'config_keys': list(self._config.keys())
            }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get initialization configuration.
        
        Returns:
            Copy of configuration dictionary (empty if not initialized)
        """
        with self._lock:
            return self._config.copy()
    
    def is_initialized(self) -> bool:
        """
        Check if Lambda environment is initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        with self._lock:
            return self._initialized
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset initialization state with thread safety.
        
        After reset(), initialize() can be called again to re-initialize
        with new configuration.
        
        Returns:
            Dictionary with reset status
        """
        with self._lock:
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
        """
        Get comprehensive initialization status.
        
        Returns:
            Dictionary containing complete initialization state including:
            - initialized: Whether system is initialized
            - config: Current configuration
            - flags: Current flags
            - init_timestamp: When initialized
            - init_duration_ms: How long initialization took
            - uptime_seconds: Time since initialization
            - flag_count: Number of flags set
            - config_keys: List of config keys
        """
        with self._lock:
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
        """
        Set an initialization flag with validation.
        
        Args:
            flag_name: Name of the flag (must be non-empty string)
            value: Value to set (any type including None)
            
        Returns:
            Dictionary with operation result:
            - success: True if set, False if validation failed
            - flag_name: Name of the flag
            - value: New value
            - old_value: Previous value (if any)
            - was_new: True if this flag didn't exist before
        """
        if not flag_name or not isinstance(flag_name, str):
            return {
                'success': False,
                'error': 'Flag name must be a non-empty string',
                'flag_name': flag_name
            }
        
        with self._lock:
            old_value = self._flags.get(flag_name)
            was_new = flag_name not in self._flags
            self._flags[flag_name] = value
            
            return {
                'success': True,
                'flag_name': flag_name,
                'value': value,
                'old_value': old_value,
                'was_new': was_new
            }
    
    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """
        Get an initialization flag value with validation.
        
        Args:
            flag_name: Name of the flag (must be non-empty string)
            default: Default value if flag doesn't exist
            
        Returns:
            Flag value or default
        """
        if not flag_name or not isinstance(flag_name, str):
            return default
        
        with self._lock:
            return self._flags.get(flag_name, default)


# ===== SINGLETON INSTANCE =====

_INITIALIZATION = InitializationCore()


# ===== OPERATION MAP =====

_OPERATION_MAP = {
    InitializationOperation.INITIALIZE: lambda **kwargs: _INITIALIZATION.initialize(**kwargs),
    InitializationOperation.GET_CONFIG: lambda **kwargs: _INITIALIZATION.get_config(),
    InitializationOperation.IS_INITIALIZED: lambda **kwargs: _INITIALIZATION.is_initialized(),
    InitializationOperation.RESET: lambda **kwargs: _INITIALIZATION.reset(),
    InitializationOperation.GET_STATUS: lambda **kwargs: _INITIALIZATION.get_status(),
    InitializationOperation.SET_FLAG: lambda **kwargs: _INITIALIZATION.set_flag(**kwargs),
    InitializationOperation.GET_FLAG: lambda **kwargs: _INITIALIZATION.get_flag(**kwargs),
}


# ===== GENERIC OPERATION EXECUTION =====

def execute_initialization_operation(operation: InitializationOperation, **kwargs):
    """
    Universal initialization operation executor with error handling.
    
    Single function that routes all initialization operations to the InitializationCore instance.
    
    Args:
        operation: InitializationOperation enum value
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from InitializationCore
        
    Raises:
        ValueError: If operation is unknown
        Exception: If operation execution fails
    """
    try:
        if _USE_GENERIC_OPERATIONS:
            operation_func = _OPERATION_MAP.get(operation)
            if operation_func is None:
                raise ValueError(f"Unknown initialization operation: {operation}")
            return operation_func(**kwargs)
        else:
            # Legacy direct dispatch
            if operation == InitializationOperation.INITIALIZE:
                return _INITIALIZATION.initialize(**kwargs)
            elif operation == InitializationOperation.GET_CONFIG:
                return _INITIALIZATION.get_config()
            elif operation == InitializationOperation.IS_INITIALIZED:
                return _INITIALIZATION.is_initialized()
            elif operation == InitializationOperation.RESET:
                return _INITIALIZATION.reset()
            elif operation == InitializationOperation.GET_STATUS:
                return _INITIALIZATION.get_status()
            elif operation == InitializationOperation.SET_FLAG:
                return _INITIALIZATION.set_flag(**kwargs)
            elif operation == InitializationOperation.GET_FLAG:
                return _INITIALIZATION.get_flag(**kwargs)
            else:
                raise ValueError(f"Unknown initialization operation: {operation}")
    except Exception as e:
        # Re-raise with context
        raise Exception(f"Initialization operation '{operation.value}' failed: {e}") from e


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====
# These functions are called by interface_initialization.py router

def _execute_initialize_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute initialization operation.
    
    Args:
        config: Optional configuration dictionary
        **kwargs: Additional configuration items
        
    Returns:
        Initialization result dictionary with idempotency guarantee
    """
    return _INITIALIZATION.initialize(**kwargs)


def _execute_get_config_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute get config operation.
    
    Returns:
        Configuration dictionary
    """
    return _INITIALIZATION.get_config()


def _execute_is_initialized_implementation(**kwargs) -> bool:
    """
    Execute is initialized check.
    
    Returns:
        True if initialized, False otherwise
    """
    return _INITIALIZATION.is_initialized()


def _execute_reset_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute reset operation.
    
    Returns:
        Reset result dictionary
    """
    return _INITIALIZATION.reset()


def _execute_get_status_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute get status operation.
    
    Returns:
        Comprehensive status dictionary
    """
    return _INITIALIZATION.get_status()


def _execute_set_flag_implementation(**kwargs) -> Dict[str, Any]:
    """
    Execute set flag operation.
    
    Args:
        flag_name: Name of the flag (required)
        value: Value to set (required)
        
    Returns:
        Operation result dictionary
        
    Raises:
        ValueError: If required parameters missing
    """
    if 'flag_name' not in kwargs:
        raise ValueError("Parameter 'flag_name' is required for set_flag operation")
    if 'value' not in kwargs:
        raise ValueError("Parameter 'value' is required for set_flag operation")
    
    return _INITIALIZATION.set_flag(
        flag_name=kwargs['flag_name'],
        value=kwargs['value']
    )


def _execute_get_flag_implementation(**kwargs) -> Any:
    """
    Execute get flag operation.
    
    Args:
        flag_name: Name of the flag (required)
        default: Default value if flag doesn't exist (optional)
        
    Returns:
        Flag value or default
        
    Raises:
        ValueError: If flag_name not provided
    """
    if 'flag_name' not in kwargs:
        raise ValueError("Parameter 'flag_name' is required for get_flag operation")
    
    return _INITIALIZATION.get_flag(
        flag_name=kwargs['flag_name'],
        default=kwargs.get('default', None)
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
