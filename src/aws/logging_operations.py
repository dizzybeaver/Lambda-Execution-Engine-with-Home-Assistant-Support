"""
aws/logging_operations.py - Logging operation dispatcher
Version: 2025.10.14.01
Description: Generic operation execution and dispatcher timing integration

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
import time
import logging

from logging_types import LogOperation
from logging_manager import _MANAGER

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


# ===== GENERIC OPERATION EXECUTION =====

def execute_logging_operation(operation: LogOperation, *args, **kwargs):
    """Universal logging operation executor with dispatcher performance monitoring."""
    start_time = time.time()
    
    if not _USE_GENERIC_OPERATIONS:
        result = _execute_legacy_operation(operation, *args, **kwargs)
    else:
        result = _execute_generic_operation(operation, *args, **kwargs)
    
    duration_ms = (time.time() - start_time) * 1000
    _record_dispatcher_metric(operation, duration_ms)
    
    return result


def _execute_generic_operation(operation: LogOperation, *args, **kwargs):
    """Execute logging operation using generic dispatcher."""
    try:
        method_name = operation.value
        method = getattr(_MANAGER, method_name, None)
        
        if method is None:
            return None
        
        return method(*args, **kwargs)
    except Exception as e:
        logger.error(f"Operation {operation.value} failed: {str(e)}")
        return None


def _execute_legacy_operation(operation: LogOperation, *args, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    try:
        method = getattr(_MANAGER, operation.value)
        return method(*args, **kwargs)
    except Exception as e:
        logger.error(f"Legacy operation {operation.value} failed: {str(e)}")
        return None


def _record_dispatcher_metric(operation: LogOperation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation (Phase 4 Task #7)."""
    try:
        from gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.METRICS,
            'record_dispatcher_timing',
            interface_name='LoggingCore',
            operation_name=operation.value,
            duration_ms=duration_ms
        )
    except Exception:
        pass


# ===== EXPORTS =====

__all__ = [
    'execute_logging_operation',
]

# EOF
