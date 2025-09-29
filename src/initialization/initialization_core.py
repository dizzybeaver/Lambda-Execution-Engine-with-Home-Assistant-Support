"""
initialization_core.py - Core Initialization Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Lambda initialization optimization
"""

import os
import time
from typing import Any, Dict, Optional

_INITIALIZATION_STATE = {
    "initialized": False,
    "start_time": None,
    "cold_start": True,
    "invocation_count": 0
}

def initialize_lambda() -> Dict[str, Any]:
    """Initialize Lambda environment."""
    if not _INITIALIZATION_STATE["initialized"]:
        _INITIALIZATION_STATE["start_time"] = time.time()
        _INITIALIZATION_STATE["initialized"] = True
        _INITIALIZATION_STATE["cold_start"] = True
    else:
        _INITIALIZATION_STATE["cold_start"] = False
    
    _INITIALIZATION_STATE["invocation_count"] += 1
    
    return {
        "initialized": True,
        "cold_start": _INITIALIZATION_STATE["cold_start"],
        "invocation_count": _INITIALIZATION_STATE["invocation_count"],
        "uptime": time.time() - _INITIALIZATION_STATE["start_time"]
    }

def get_initialization_state() -> Dict[str, Any]:
    """Get initialization state."""
    return _INITIALIZATION_STATE.copy()

def is_cold_start() -> bool:
    """Check if this is a cold start."""
    return _INITIALIZATION_STATE["cold_start"]

def get_invocation_count() -> int:
    """Get invocation count."""
    return _INITIALIZATION_STATE["invocation_count"]

def get_uptime() -> float:
    """Get Lambda uptime in seconds."""
    if _INITIALIZATION_STATE["start_time"]:
        return time.time() - _INITIALIZATION_STATE["start_time"]
    return 0.0

def get_environment_variables() -> Dict[str, str]:
    """Get Lambda environment variables."""
    return dict(os.environ)

def get_environment_variable(key: str, default: Any = None) -> Any:
    """Get specific environment variable."""
    return os.environ.get(key, default)

def reset_initialization() -> None:
    """Reset initialization state."""
    _INITIALIZATION_STATE["initialized"] = False
    _INITIALIZATION_STATE["start_time"] = None
    _INITIALIZATION_STATE["cold_start"] = True
    _INITIALIZATION_STATE["invocation_count"] = 0
