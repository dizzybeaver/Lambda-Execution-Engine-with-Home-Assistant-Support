"""
singleton_convenience.py - Convenience Functions with Circuit Breaker Support
Version: 2025.09.24.13
Description: Convenience wrapper functions with circuit breaker manager access

UPDATES APPLIED:
- ✅ CIRCUIT_BREAKER_MANAGER: Added convenience function for circuit breaker access
- ✅ MEMORY OPTIMIZED: Maintains existing memory optimization patterns
- ✅ GATEWAY INTEGRATION: Uses singleton_core.py for all implementations

ARCHITECTURE: SECONDARY IMPLEMENTATION - INTERNAL ACCESS ONLY
- Uses singleton_core.py for actual singleton management
- Provides convenient wrapper functions for external access
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Import from core implementation
from .singleton_core import get_singleton_registry

def get_cost_protection():
    """Get cost protection singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('cost_protection', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get cost protection: {e}")
        return None

def get_cache_manager():
    """Get cache manager singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('cache_manager', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get cache manager: {e}")
        return None

def get_security_validator():
    """Get security validator singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('security_validator', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get security validator: {e}")
        return None

def get_unified_validator():
    """Get unified validator singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('unified_validator', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get unified validator: {e}")
        return None

def get_config_manager():
    """Get config manager singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('config_manager', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get config manager: {e}")
        return None

def get_memory_manager():
    """Get memory manager singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('memory_manager', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get memory manager: {e}")
        return None

def get_lambda_cache():
    """Get lambda cache singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('lambda_cache', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get lambda cache: {e}")
        return None

def get_response_cache():
    """Get response cache singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('response_cache', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get response cache: {e}")
        return None

def get_circuit_breaker_manager():
    """Get circuit breaker manager singleton - NEW FUNCTION."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('circuit_breaker_manager', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get circuit breaker manager: {e}")
        return None

def get_response_processor():
    """Get response processor singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('response_processor', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get response processor: {e}")
        return None

def get_lambda_optimizer():
    """Get lambda optimizer singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('lambda_optimizer', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get lambda optimizer: {e}")
        return None

def get_response_metrics_manager():
    """Get response metrics manager singleton."""
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance('response_metrics_manager', create_if_missing=True)
    except Exception as e:
        logger.error(f"Failed to get response metrics manager: {e}")
        return None

# EOF
