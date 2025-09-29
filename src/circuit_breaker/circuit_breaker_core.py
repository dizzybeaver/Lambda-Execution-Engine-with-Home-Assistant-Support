"""
circuit_breaker_core.py - Core Circuit Breaker Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Circuit breaker pattern
"""

import time
from typing import Any, Callable, Optional, Dict
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitStats:
    """Circuit breaker statistics."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_failure_time: Optional[float] = None
    state_changed_time: float = 0
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

_CIRCUITS: Dict[str, Dict] = {}
_DEFAULT_THRESHOLD = 5
_DEFAULT_TIMEOUT = 60
_DEFAULT_HALF_OPEN_CALLS = 1

def _get_circuit(name: str) -> Dict:
    """Get or create circuit."""
    if name not in _CIRCUITS:
        _CIRCUITS[name] = {
            "state": CircuitState.CLOSED,
            "stats": CircuitStats(state_changed_time=time.time()),
            "threshold": _DEFAULT_THRESHOLD,
            "timeout": _DEFAULT_TIMEOUT,
            "half_open_calls": _DEFAULT_HALF_OPEN_CALLS
        }
    return _CIRCUITS[name]

def _should_attempt_reset(circuit: Dict) -> bool:
    """Check if circuit should attempt reset."""
    if circuit["state"] != CircuitState.OPEN:
        return False
    
    time_since_open = time.time() - circuit["stats"].state_changed_time
    return time_since_open >= circuit["timeout"]

def _record_success(circuit: Dict) -> None:
    """Record successful call."""
    stats = circuit["stats"]
    stats.total_calls += 1
    stats.successful_calls += 1
    
    if circuit["state"] == CircuitState.HALF_OPEN:
        circuit["state"] = CircuitState.CLOSED
        circuit["stats"].state_changed_time = time.time()

def _record_failure(circuit: Dict) -> None:
    """Record failed call."""
    stats = circuit["stats"]
    stats.total_calls += 1
    stats.failed_calls += 1
    stats.last_failure_time = time.time()
    
    if circuit["state"] == CircuitState.HALF_OPEN:
        circuit["state"] = CircuitState.OPEN
        circuit["stats"].state_changed_time = time.time()
    elif circuit["state"] == CircuitState.CLOSED:
        if stats.failed_calls >= circuit["threshold"]:
            circuit["state"] = CircuitState.OPEN
            circuit["stats"].state_changed_time = time.time()

def circuit_breaker_call(
    operation: Callable,
    fallback: Optional[Callable] = None,
    circuit_name: str = "default",
    **kwargs
) -> Any:
    """Execute operation with circuit breaker."""
    circuit = _get_circuit(circuit_name)
    
    if circuit["state"] == CircuitState.OPEN:
        if _should_attempt_reset(circuit):
            circuit["state"] = CircuitState.HALF_OPEN
            circuit["stats"].state_changed_time = time.time()
        else:
            if fallback:
                return fallback()
            raise Exception(f"Circuit breaker '{circuit_name}' is OPEN")
    
    try:
        result = operation()
        _record_success(circuit)
        return result
    except Exception as e:
        _record_failure(circuit)
        if fallback:
            return fallback()
        raise e

def get_circuit_state(circuit_name: str = "default") -> str:
    """Get circuit state."""
    circuit = _get_circuit(circuit_name)
    return circuit["state"].value

def get_circuit_stats(circuit_name: str = "default") -> Dict[str, Any]:
    """Get circuit statistics."""
    circuit = _get_circuit(circuit_name)
    stats = circuit["stats"]
    
    return {
        "state": circuit["state"].value,
        "total_calls": stats.total_calls,
        "successful_calls": stats.successful_calls,
        "failed_calls": stats.failed_calls,
        "failure_rate": stats.get_failure_rate(),
        "last_failure_time": stats.last_failure_time,
        "threshold": circuit["threshold"],
        "timeout": circuit["timeout"]
    }

def reset_circuit(circuit_name: str = "default") -> None:
    """Reset circuit breaker."""
    if circuit_name in _CIRCUITS:
        circuit = _CIRCUITS[circuit_name]
        circuit["state"] = CircuitState.CLOSED
        circuit["stats"] = CircuitStats(state_changed_time=time.time())

def configure_circuit(
    circuit_name: str,
    threshold: int = _DEFAULT_THRESHOLD,
    timeout: int = _DEFAULT_TIMEOUT,
    half_open_calls: int = _DEFAULT_HALF_OPEN_CALLS
) -> None:
    """Configure circuit breaker parameters."""
    circuit = _get_circuit(circuit_name)
    circuit["threshold"] = threshold
    circuit["timeout"] = timeout
    circuit["half_open_calls"] = half_open_calls

def get_all_circuits() -> Dict[str, Dict[str, Any]]:
    """Get all circuit breaker states."""
    return {
        name: get_circuit_stats(name)
        for name in _CIRCUITS.keys()
    }

def clear_all_circuits() -> int:
    """Clear all circuit breakers."""
    count = len(_CIRCUITS)
    _CIRCUITS.clear()
    return count
