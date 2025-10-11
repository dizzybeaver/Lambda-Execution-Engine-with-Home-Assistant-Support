"""
singleton_convenience.py
Version: 2025.09.30.01
Description: Singleton access with generic pattern

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

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

from singleton_core import get_singleton_registry


def get_named_singleton(name: str, create_if_missing: bool = True) -> Optional[Any]:
    """
    Universal singleton accessor with consistent error handling.
    
    Args:
        name: Singleton instance name
        create_if_missing: Create instance if it doesn't exist
        
    Returns:
        Singleton instance or None on error
    """
    try:
        registry = get_singleton_registry()
        return registry.get_singleton_instance(name, create_if_missing=create_if_missing)
    except Exception as e:
        logger.error(f"Failed to get singleton '{name}': {e}")
        return None


def get_cost_protection() -> Optional[Any]:
    """Get cost protection singleton."""
    return get_named_singleton('cost_protection')


def get_cache_manager() -> Optional[Any]:
    """Get cache manager singleton."""
    return get_named_singleton('cache_manager')


def get_security_validator() -> Optional[Any]:
    """Get security validator singleton."""
    return get_named_singleton('security_validator')


def get_unified_validator() -> Optional[Any]:
    """Get unified validator singleton."""
    return get_named_singleton('unified_validator')


def get_config_manager() -> Optional[Any]:
    """Get config manager singleton."""
    return get_named_singleton('config_manager')


def get_memory_manager() -> Optional[Any]:
    """Get memory manager singleton."""
    return get_named_singleton('memory_manager')


def get_lambda_cache() -> Optional[Any]:
    """Get lambda cache singleton."""
    return get_named_singleton('lambda_cache')


def get_response_cache() -> Optional[Any]:
    """Get response cache singleton."""
    return get_named_singleton('response_cache')


def get_circuit_breaker_manager() -> Optional[Any]:
    """Get circuit breaker manager singleton."""
    return get_named_singleton('circuit_breaker_manager')


def get_response_processor() -> Optional[Any]:
    """Get response processor singleton."""
    return get_named_singleton('response_processor')


def get_lambda_optimizer() -> Optional[Any]:
    """Get lambda optimizer singleton."""
    return get_named_singleton('lambda_optimizer')


def get_response_metrics_manager() -> Optional[Any]:
    """Get response metrics manager singleton."""
    return get_named_singleton('response_metrics_manager')


__all__ = [
    'get_named_singleton',
    'get_cost_protection',
    'get_cache_manager',
    'get_security_validator',
    'get_unified_validator',
    'get_config_manager',
    'get_memory_manager',
    'get_lambda_cache',
    'get_response_cache',
    'get_circuit_breaker_manager',
    'get_response_processor',
    'get_lambda_optimizer',
    'get_response_metrics_manager',
]

# EOF
