"""
initialization_core.py
Version: 2025.10.22.01
Description: Lambda initialization with SINGLETON pattern, rate limiting, NO threading locks

CHANGELOG:
- 2025.10.22.01: Phase 1 + 3 optimizations (Session 6)
  - REMOVED threading locks (CRITICAL FIX - was violating AP-08, DEC-04)
  - ADDED SINGLETON pattern with get_initialization_manager()
  - ADDED rate limiting (1000 ops/sec)
  - ENHANCED reset() operation for lifecycle management
  - ADDED get_stats() operation
  - REPLACED Lock with rate limiting (DoS protection)
  - Compliance: AP-08, DEC-04, LESS-17, LESS-18, LESS-21
- 2025.10.17.11: Added idempotency check (Issue #44 fix)
- 2025.10.16.01: Fixed thread safety, error handling, parameter validation

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from collections import deque
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
    GET_STATS = "get_stats"
    SET_FLAG = "set_flag"
    GET_FLAG = "get_flag"

# ===== INITIALIZATION CORE CLASS =====

class InitializationCore:
    """
    Handles Lambda environment initialization with idempotency.
    
    CRITICAL: NO threading locks - Lambda is single-threaded (DEC-04, AP-08)
    Uses rate limiting for DoS protection instead of locks (LESS-21)
    """
    
    def __init__(self):
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._flags: Dict[str, Any] = {}
        self._init_timestamp: Optional[float] = None
        self._init_duration_ms: Optional[float] = None
        
        # Rate limiting (1000 ops/sec for infrastructure - LESS-21)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check rate limit (1000 ops/sec).
        
        Returns:
            True if within rate limit, False if rate limited
        """
        now = time.time() * 1000
        
        # Remove timestamps outside window
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if at limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        
        # Add timestamp
        self._rate_limiter.append(now)
        return True
    
    def initialize(self, config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Initialize Lambda environment with idempotency (Issue #44).
        
        Idempotency guarantee: Calling initialize() multiple times is safe.
        If already initialized, returns cached result immediately without
        re-initializing. This prevents duplicate work on repeated calls.
        
        Args:
            config: Optional configuration dictionary to store
            **kwargs: Additional configuration items (merged with config dict)
            
        Returns:
            Dictionary with initialization status
        """
        if not self._check_rate_limit():
            return {'status': 'rate_limited', 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        # Check if already initialized (fast path)
        if self._initialized:
            return {
                'status': 'already_initialized',
                'cached': True,
                'timestamp': self._init_timestamp,
                'init_duration_ms': self._init_duration_ms,
                'uptime_seconds': time.time() - self._init_timestamp if self._init_timestamp else 0,
                'config_keys': list(self._config.keys())
            }
        
        # Initialize
        start_time = time.time()
        
        # Merge config and kwargs
        if config is None:
            config = {}
        self._config = {**config, **kwargs}
        
        # Mark as initialized
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
            Copy of configuration dictionary (empty if not initialized or rate limited)
        """
        if not self._check_rate_limit():
            return {}
        return self._config.copy()
    
    def is_initialized(self) -> bool:
        """
        Check if Lambda environment is initialized.
        
        Returns:
            True if initialized, False otherwise or rate limited
        """
        if not self._check_rate_limit():
            return False
        return self._initialized
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset initialization state (lifecycle management).
        
        After reset(), initialize() can be called again to re-initialize
        with new configuration.
        
        Returns:
            Dictionary with reset status
        """
        if not self._check_rate_limit():
            return {'status': 'rate_limited', 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        was_initialized = self._initialized
        
        self._initialized = False
        self._config.clear()
        self._flags.clear()
        self._init_timestamp = None
        self._init_duration_ms = None
        
        # Reset rate limiter
        self._rate_limiter.clear()
        self._rate_limited_count = 0
        
        return {
            'status': 'reset',
            'was_initialized': was_initialized,
            'timestamp': time.time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive initialization status.
        
        Returns:
            Dictionary containing complete initialization state
        """
        if not self._check_rate_limit():
            return {'error': 'Rate limit exceeded'}
        
        return {
            'initialized': self._initialized,
            'config': self._config.copy() if self._initialized else {},
            'flags': self._flags.copy(),
            'init_timestamp': self._init_timestamp,
            'init_duration_ms': self._init_duration_ms,
            'uptime_seconds': (time.time() - self._init_timestamp) if self._init_timestamp else None,
            'flag_count': len(self._flags),
            'config_keys': list(self._config.keys()) if self._initialized else [],
            'rate_limited_count': self._rate_limited_count,
            'use_generic_operations': _USE_GENERIC_OPERATIONS
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get initialization statistics (alias for get_status).
        
        Returns:
            Dictionary containing initialization statistics
        """
        return self.get_status()
    
    def set_flag(self, flag_name: str, value: Any) -> Dict[str, Any]:
        """
        Set an initialization flag with validation.
        
        Args:
            flag_name: Name of the flag (must be non-empty string)
            value: Value to set (any type including None)
            
        Returns:
            Dictionary with operation result
        """
        if not self._check_rate_limit():
            return {'success': False, 'error': 'Rate limit exceeded (1000 ops/sec)'}
        
        if not flag_name or not isinstance(flag_name, str):
            return {
                'success': False,
                'error': 'Flag name must be a non-empty string',
                'flag_name': flag_name
            }
        
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
        if not self._check_rate_limit():
            return default
        
        if not flag_name or not isinstance(flag_name, str):
            return default
        
        return self._flags.get(flag_name, default)


# Global initialization manager instance
_manager_core = None


def get_initialization_manager() -> InitializationCore:
    """
    Get the initialization manager instance (SINGLETON pattern - LESS-18).
    
    Returns:
        InitializationCore instance
    """
    global _manager_core
    
    try:
        # Try to use gateway's SINGLETON system if available
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('initialization_manager')
        if manager is None:
            # Create and register
            if _manager_core is None:
                _manager_core = InitializationCore()
            singleton_register('initialization_manager', _manager_core)
            manager = _manager_core
        
        return manager
    except (ImportError, Exception):
        # Fallback: use module-level singleton
        if _manager_core is None:
            _manager_core = InitializationCore()
        return _manager_core


# ===== OPERATION MAP =====

_OPERATION_MAP = {
    InitializationOperation.INITIALIZE: lambda **kwargs: get_initialization_manager().initialize(**kwargs),
    InitializationOperation.GET_CONFIG: lambda **kwargs: get_initialization_manager().get_config(),
    InitializationOperation.IS_INITIALIZED: lambda **kwargs: get_initialization_manager().is_initialized(),
    InitializationOperation.RESET: lambda **kwargs: get_initialization_manager().reset(),
    InitializationOperation.GET_STATUS: lambda **kwargs: get_initialization_manager().get_status(),
    InitializationOperation.GET_STATS: lambda **kwargs: get_initialization_manager().get_stats(),
    InitializationOperation.SET_FLAG: lambda **kwargs: get_initialization_manager().set_flag(**kwargs),
    InitializationOperation.GET_FLAG: lambda **kwargs: get_initialization_manager().get_flag(**kwargs),
}


# ===== GENERIC OPERATION EXECUTION =====

def execute_initialization_operation(operation: InitializationOperation, **kwargs):
    """
    Universal initialization operation executor with error handling.
    
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
            manager = get_initialization_manager()
            if operation == InitializationOperation.INITIALIZE:
                return manager.initialize(**kwargs)
            elif operation == InitializationOperation.GET_CONFIG:
                return manager.get_config()
            elif operation == InitializationOperation.IS_INITIALIZED:
                return manager.is_initialized()
            elif operation == InitializationOperation.RESET:
                return manager.reset()
            elif operation == InitializationOperation.GET_STATUS:
                return manager.get_status()
            elif operation == InitializationOperation.GET_STATS:
                return manager.get_stats()
            elif operation == InitializationOperation.SET_FLAG:
                return manager.set_flag(**kwargs)
            elif operation == InitializationOperation.GET_FLAG:
                return manager.get_flag(**kwargs)
            else:
                raise ValueError(f"Unknown initialization operation: {operation}")
    except Exception as e:
        raise Exception(f"Initialization operation '{operation.value}' failed: {e}") from e


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_initialize_implementation(**kwargs) -> Dict[str, Any]:
    """Execute initialization operation."""
    return get_initialization_manager().initialize(**kwargs)


def _execute_get_config_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get config operation."""
    return get_initialization_manager().get_config()


def _execute_is_initialized_implementation(**kwargs) -> bool:
    """Execute is initialized check."""
    return get_initialization_manager().is_initialized()


def _execute_reset_implementation(**kwargs) -> Dict[str, Any]:
    """Execute reset operation."""
    return get_initialization_manager().reset()


def _execute_get_status_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get status operation."""
    return get_initialization_manager().get_status()


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return get_initialization_manager().get_stats()


def _execute_set_flag_implementation(**kwargs) -> Dict[str, Any]:
    """Execute set flag operation."""
    if 'flag_name' not in kwargs:
        raise ValueError("Parameter 'flag_name' is required for set_flag operation")
    if 'value' not in kwargs:
        raise ValueError("Parameter 'value' is required for set_flag operation")
    
    return get_initialization_manager().set_flag(
        flag_name=kwargs['flag_name'],
        value=kwargs['value']
    )


def _execute_get_flag_implementation(**kwargs) -> Any:
    """Execute get flag operation."""
    if 'flag_name' not in kwargs:
        raise ValueError("Parameter 'flag_name' is required for get_flag operation")
    
    return get_initialization_manager().get_flag(
        flag_name=kwargs['flag_name'],
        default=kwargs.get('default', None)
    )


# ===== EXPORTS =====

__all__ = [
    'InitializationOperation',
    'InitializationCore',
    'execute_initialization_operation',
    'get_initialization_manager',
    '_execute_initialize_implementation',
    '_execute_get_config_implementation',
    '_execute_is_initialized_implementation',
    '_execute_reset_implementation',
    '_execute_get_status_implementation',
    '_execute_get_stats_implementation',
    '_execute_set_flag_implementation',
    '_execute_get_flag_implementation',
]

# EOF
