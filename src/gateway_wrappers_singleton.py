"""
gateway_wrappers_singleton.py - SINGLETON Interface Wrappers
Version: 2025.10.22.03
Description: Convenience wrappers for SINGLETON interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


# ===== SINGLETON OPERATIONS =====

def singleton_get(key: str) -> Any:
    """Get singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'get', key=key)


def singleton_has(key: str) -> bool:
    """Check if singleton exists."""
    return execute_operation(GatewayInterface.SINGLETON, 'has', key=key)


def singleton_delete(key: str) -> bool:
    """Delete singleton instance."""
    return execute_operation(GatewayInterface.SINGLETON, 'delete', key=key)


def singleton_clear() -> None:
    """Clear all singletons."""
    execute_operation(GatewayInterface.SINGLETON, 'clear')


def singleton_stats() -> Dict[str, Any]:
    """Get singleton statistics."""
    return execute_operation(GatewayInterface.SINGLETON, 'stats')


def singleton_get_stats() -> Dict[str, Any]:
    """Get singleton statistics (alias for singleton_stats)."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_stats')


def singleton_reset() -> bool:
    """Reset SINGLETON manager state (lifecycle management)."""
    return execute_operation(GatewayInterface.SINGLETON, 'reset')


# ===== MEMORY MONITORING OPERATIONS =====

def get_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_memory_stats')


def get_comprehensive_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics including GC info."""
    return execute_operation(GatewayInterface.SINGLETON, 'get_comprehensive_memory_stats')


def check_lambda_memory_compliance() -> Dict[str, Any]:
    """Check if memory usage is within Lambda 128MB limit."""
    return execute_operation(GatewayInterface.SINGLETON, 'check_lambda_memory_compliance')


def force_memory_cleanup() -> Dict[str, Any]:
    """Force aggressive memory cleanup."""
    return execute_operation(GatewayInterface.SINGLETON, 'force_memory_cleanup')


def optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage with multi-strategy approach."""
    return execute_operation(GatewayInterface.SINGLETON, 'optimize_memory')


def force_comprehensive_memory_cleanup() -> Dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies."""
    return execute_operation(GatewayInterface.SINGLETON, 'force_comprehensive_memory_cleanup')


def emergency_memory_preserve() -> Dict[str, Any]:
    """Emergency memory preservation for critical situations."""
    return execute_operation(GatewayInterface.SINGLETON, 'emergency_memory_preserve')


__all__ = [
    # Singleton operations
    'singleton_get',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'singleton_get_stats',
    'singleton_reset',
    
    # Memory monitoring operations
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
]
