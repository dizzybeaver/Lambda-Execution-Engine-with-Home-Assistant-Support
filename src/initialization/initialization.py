"""
initialization.py - Lambda Initialization Primary Gateway Interface
Version: 2025.09.27.01
Description: Ultra-pure gateway for Lambda initialization operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE
- Function declarations ONLY - no implementation code
- Pure delegation to initialization_core.py
- External access point for initialization operations
- Ultra-optimized for 128MB Lambda constraint

PRIMARY GATEWAY FUNCTIONS:
- unified_lambda_initialization() - Lambda startup coordination
- unified_lambda_cleanup() - Lambda cleanup operations
- get_initialization_status() - Initialization status monitoring
- get_free_tier_memory_status() - Memory status monitoring

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

from typing import Dict, Any
from .initialization_core import generic_initialization_operation, InitializationOperation

# ===== SECTION 1: PRIMARY GATEWAY INTERFACE FUNCTIONS =====

def unified_lambda_initialization() -> Dict[str, Any]:
    """
    Primary gateway function for Lambda startup coordination.
    Pure delegation to initialization_core implementation.
    """
    return generic_initialization_operation(InitializationOperation.LAMBDA_INIT)

def unified_lambda_cleanup() -> Dict[str, Any]:
    """
    Primary gateway function for Lambda cleanup operations.
    Pure delegation to initialization_core implementation.
    """
    return generic_initialization_operation(InitializationOperation.LAMBDA_CLEANUP)

def get_initialization_status() -> Dict[str, Any]:
    """
    Primary gateway function for initialization status monitoring.
    Pure delegation to initialization_core implementation.
    """
    return generic_initialization_operation(InitializationOperation.GET_STATUS)

def get_free_tier_memory_status() -> Dict[str, Any]:
    """
    Primary gateway function for memory status monitoring.
    Pure delegation to initialization_core implementation.
    """
    return generic_initialization_operation(InitializationOperation.MEMORY_STATUS)

# ===== SECTION 2: MODULE EXPORTS =====

__all__ = [
    'unified_lambda_initialization',
    'unified_lambda_cleanup',
    'get_initialization_status',
    'get_free_tier_memory_status'
]

# EOF
