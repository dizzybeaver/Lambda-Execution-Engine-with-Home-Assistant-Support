"""
config/config_core.py
Version: 2025-12-09_1
Purpose: Core configuration management with singleton pattern
License: Apache 2.0
"""

import time
from typing import Dict, Any
from collections import deque

from config.config_state import ConfigurationState
from config.config_validator import ConfigurationValidator

_config_core = None

class ConfigurationCore:
    """Configuration system core with rate limiting."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._state = ConfigurationState()
        self._validator = ConfigurationValidator()
        self._cache_prefix = "config_"
        self._initialized = False
        self._use_parameter_store = False
        self._parameter_prefix = "/lambda-execution-engine"
        
        # Rate limiting (1000 ops/sec)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if operation should be rate limited."""
        import gateway
        
        current_time_ms = int(time.time() * 1000)
        
        # Remove old entries
        while self._rate_limiter and \
              (current_time_ms - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            gateway.debug_log("CONFIG", "CONFIG", "Rate limit exceeded", 
                            count=self._rate_limited_count)
            return True
        
        self._rate_limiter.append(current_time_ms)
        return False
    
    def reset(self) -> bool:
        """Reset configuration state."""
        import gateway
        
        try:
            with gateway.debug_timing("CONFIG", "CONFIG", "reset"):
                self._config.clear()
                self._state = ConfigurationState()
                self._initialized = False
                self._rate_limiter.clear()
                self._rate_limited_count = 0
                
                gateway.debug_log("CONFIG", "CONFIG", "Configuration reset")
                return True
                
        except Exception as e:
            gateway.log_error(f"Config reset failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics."""
        return {
            'initialized': self._initialized,
            'parameter_count': len(self._config),
            'use_parameter_store': self._use_parameter_store,
            'rate_limited_count': self._rate_limited_count,
            'rate_limiter_size': len(self._rate_limiter)
        }


def get_config_manager() -> ConfigurationCore:
    """
    Get configuration manager singleton.
    
    Uses SINGLETON pattern for lifecycle management.
    Attempts gateway registration, falls back to module-level singleton.
    """
    global _config_core
    
    try:
        import gateway
        manager = gateway.singleton_get('config_manager')
        if manager is None:
            if _config_core is None:
                _config_core = ConfigurationCore()
            gateway.singleton_register('config_manager', _config_core)
            manager = _config_core
        return manager
    except (ImportError, Exception):
        if _config_core is None:
            _config_core = ConfigurationCore()
        return _config_core


__all__ = [
    'ConfigurationCore',
    'get_config_manager'
]
