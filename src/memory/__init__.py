"""
memory/__init__.py - Memory Package Exports
Version: 2025.10.14.01
Description: Exports for memory package (Cache, Singleton)

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

# Cache Core
from cache_core import (
    CacheCore,
    _CACHE_MANAGER,
)

# Singleton Core
from singleton_core import (
    SingletonOperation,
    SingletonCore,
    execute_singleton_operation,
    # Gateway-aligned implementations
    _execute_get_implementation,
    _execute_set_implementation,
    _execute_has_implementation,
    _execute_delete_implementation,
    _execute_clear_implementation,
    _execute_get_stats_implementation,
    # Legacy implementations
    _execute_reset_implementation,
    _execute_reset_all_implementation,
    _execute_exists_implementation,
)

# Singleton Convenience Functions
from singleton_convenience import (
    get_named_singleton,
    set_named_singleton,
    has_singleton,
    delete_singleton,
    clear_all_singletons,
    get_singleton_stats,
    get_http_client,
    get_cache_manager,
    get_config_manager,
    get_metrics_manager,
    get_logging_manager,
    get_circuit_breaker,
    reset_singleton,
    reset_all_singletons,
    singleton_exists,
)

# Singleton Memory Management
from singleton_memory import (
    get_singleton_memory_breakdown,
    optimize_singleton_memory,
    emergency_memory_preserve,
)

__all__ = [
    # Cache Core
    'CacheCore',
    '_CACHE_MANAGER',
    
    # Singleton Core - Enum
    'SingletonOperation',
    
    # Singleton Core - Class
    'SingletonCore',
    
    # Singleton Core - Executor
    'execute_singleton_operation',
    
    # Singleton Core - Gateway Implementations
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_has_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_get_stats_implementation',
    
    # Singleton Core - Legacy Implementations
    '_execute_reset_implementation',
    '_execute_reset_all_implementation',
    '_execute_exists_implementation',
    
    # Singleton Convenience Functions
    'get_named_singleton',
    'set_named_singleton',
    'has_singleton',
    'delete_singleton',
    'clear_all_singletons',
    'get_singleton_stats',
    'get_http_client',
    'get_cache_manager',
    'get_config_manager',
    'get_metrics_manager',
    'get_logging_manager',
    'get_circuit_breaker',
    'reset_singleton',
    'reset_all_singletons',
    'singleton_exists',
    
    # Singleton Memory Management
    'get_singleton_memory_breakdown',
    'optimize_singleton_memory',
    'emergency_memory_preserve',
]

# EOF
