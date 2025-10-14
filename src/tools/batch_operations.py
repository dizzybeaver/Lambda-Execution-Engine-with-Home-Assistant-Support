"""
batch_operations.py
Version: 2025.10.13.01
Description: Unified batch operation processing for optimized multi-operation execution

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

from typing import Any, Dict, List, Optional
from gateway import execute_operation, GatewayInterface


# ===== BATCH EXECUTION =====

def execute_batch(operations: List[Dict[str, Any]], fail_fast: bool = False) -> List[Dict[str, Any]]:
    """
    Execute multiple operations in batch.
    
    Args:
        operations: List of operation dicts with 'interface', 'operation', 'params'
        fail_fast: If True, stop on first error
    
    Returns:
        List of result dicts with 'success', 'result', 'error'
    """
    results = []
    
    for op in operations:
        try:
            interface = op.get('interface')
            operation = op.get('operation')
            params = op.get('params', {})
            
            result = execute_operation(interface, operation, **params)
            
            results.append({
                'success': True,
                'result': result,
                'error': None,
                'operation': operation
            })
        
        except Exception as e:
            results.append({
                'success': False,
                'result': None,
                'error': str(e),
                'operation': operation
            })
            
            if fail_fast:
                break
    
    return results


# ===== BATCH CACHE OPERATIONS =====

def batch_cache_get(keys: List[str]) -> Dict[str, Any]:
    """
    Get multiple cache values in batch.
    
    Args:
        keys: List of cache keys
    
    Returns:
        Dictionary mapping keys to values
    """
    results = {}
    
    for key in keys:
        try:
            value = execute_operation(
                GatewayInterface.CACHE,
                'get',
                key=key
            )
            results[key] = value
        except:
            results[key] = None
    
    return results


def batch_cache_set(items: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Set multiple cache values in batch.
    
    Args:
        items: List of dicts with 'key', 'value', 'ttl'
    
    Returns:
        Dictionary mapping keys to success status
    """
    results = {}
    
    for item in items:
        try:
            key = item['key']
            value = item['value']
            ttl = item.get('ttl')
            
            success = execute_operation(
                GatewayInterface.CACHE,
                'set',
                key=key,
                value=value,
                ttl=ttl
            )
            results[key] = success
        except:
            results[item['key']] = False
    
    return results


def batch_cache_delete(keys: List[str]) -> Dict[str, bool]:
    """
    Delete multiple cache keys in batch.
    
    Args:
        keys: List of cache keys to delete
    
    Returns:
        Dictionary mapping keys to success status
    """
    results = {}
    
    for key in keys:
        try:
            success = execute_operation(
                GatewayInterface.CACHE,
                'delete',
                key=key
            )
            results[key] = success
        except:
            results[key] = False
    
    return results


# ===== BATCH METRICS OPERATIONS =====

def batch_record_metrics(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Record multiple metrics in batch.
    
    Args:
        metrics: List of dicts with 'name', 'value', 'dimensions'
    
    Returns:
        Summary of recorded metrics
    """
    success_count = 0
    failed_count = 0
    
    for metric in metrics:
        try:
            name = metric.get('name')
            value = metric.get('value', 1.0)
            dimensions = metric.get('dimensions')
            
            execute_operation(
                GatewayInterface.METRICS,
                'record_metric',
                name=name,
                value=value,
                dimensions=dimensions
            )
            success_count += 1
        except:
            failed_count += 1
    
    return {
        'total': len(metrics),
        'success': success_count,
        'failed': failed_count,
        'success_rate': round((success_count / len(metrics)) * 100, 2) if metrics else 0
    }


def batch_increment_counters(counters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Increment multiple counters in batch.
    
    Args:
        counters: List of dicts with 'name', 'value'
    
    Returns:
        Summary of counter operations
    """
    results = {}
    
    for counter in counters:
        try:
            name = counter.get('name')
            value = counter.get('value', 1)
            
            new_value = execute_operation(
                GatewayInterface.METRICS,
                'increment_counter',
                name=name,
                value=value
            )
            results[name] = new_value
        except:
            results[counter.get('name')] = None
    
    return results


# ===== BATCH LOGGING OPERATIONS =====

def batch_log_messages(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Log multiple messages in batch.
    
    Args:
        messages: List of dicts with 'level', 'message', 'extra'
    
    Returns:
        Summary of logging operations
    """
    success_count = 0
    level_counts = {'info': 0, 'error': 0, 'warning': 0, 'debug': 0}
    
    for msg in messages:
        try:
            level = msg.get('level', 'info')
            message = msg.get('message')
            extra = msg.get('extra')
            
            operation = f'log_{level}'
            
            execute_operation(
                GatewayInterface.LOGGING,
                operation,
                message=message,
                extra=extra
            )
            
            success_count += 1
            level_counts[level] = level_counts.get(level, 0) + 1
        except:
            pass
    
    return {
        'total': len(messages),
        'success': success_count,
        'by_level': level_counts
    }


# ===== TRANSACTION-LIKE BATCH OPERATIONS =====

def execute_transaction(operations: List[Dict[str, Any]], rollback_on_error: bool = True) -> Dict[str, Any]:
    """
    Execute operations as transaction with optional rollback.
    
    Args:
        operations: List of operations to execute
        rollback_on_error: If True, attempt to rollback on error
    
    Returns:
        Transaction result with success status
    """
    completed_ops = []
    
    try:
        # Execute all operations
        for op in operations:
            interface = op.get('interface')
            operation = op.get('operation')
            params = op.get('params', {})
            
            result = execute_operation(interface, operation, **params)
            
            completed_ops.append({
                'interface': interface,
                'operation': operation,
                'params': params,
                'result': result
            })
        
        return {
            'success': True,
            'completed_operations': len(completed_ops),
            'results': completed_ops
        }
    
    except Exception as e:
        # Rollback if enabled
        if rollback_on_error:
            rollback_results = _attempt_rollback(completed_ops)
        else:
            rollback_results = {'attempted': False}
        
        return {
            'success': False,
            'error': str(e),
            'completed_operations': len(completed_ops),
            'rollback': rollback_results
        }


def _attempt_rollback(completed_ops: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Attempt to rollback completed operations.
    
    Args:
        completed_ops: List of completed operations
    
    Returns:
        Rollback results
    """
    rollback_count = 0
    
    # Reverse order for rollback
    for op in reversed(completed_ops):
        try:
            interface = op['interface']
            operation = op['operation']
            
            # Attempt inverse operation
            if interface == GatewayInterface.CACHE and operation == 'set':
                # Rollback set with delete
                execute_operation(
                    GatewayInterface.CACHE,
                    'delete',
                    key=op['params'].get('key')
                )
                rollback_count += 1
        except:
            pass
    
    return {
        'attempted': True,
        'operations_rolled_back': rollback_count,
        'total_operations': len(completed_ops)
    }


# ===== PARALLEL EXECUTION =====

def execute_parallel(operations: List[Dict[str, Any]], max_workers: int = 5) -> List[Dict[str, Any]]:
    """
    Execute operations in parallel (simulated).
    
    Note: Actual parallelism limited in Lambda environment.
    
    Args:
        operations: List of operations
        max_workers: Maximum parallel workers (ignored in Lambda)
    
    Returns:
        List of results
    """
    # In Lambda, just execute sequentially
    # Real parallelism would require threads/processes
    return execute_batch(operations, fail_fast=False)


# ===== BATCH STATISTICS =====

def analyze_batch_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze batch execution results.
    
    Args:
        results: List of batch results
    
    Returns:
        Analysis summary
    """
    total = len(results)
    success = sum(1 for r in results if r.get('success'))
    failed = total - success
    
    success_rate = (success / total * 100) if total > 0 else 0
    
    # Group by operation
    by_operation = {}
    for result in results:
        op = result.get('operation', 'unknown')
        if op not in by_operation:
            by_operation[op] = {'success': 0, 'failed': 0}
        
        if result.get('success'):
            by_operation[op]['success'] += 1
        else:
            by_operation[op]['failed'] += 1
    
    return {
        'total_operations': total,
        'successful': success,
        'failed': failed,
        'success_rate_percent': round(success_rate, 2),
        'by_operation': by_operation
    }


# ===== BATCH BUILDERS =====

class BatchBuilder:
    """
    Builder for constructing batch operations.
    
    Usage:
        batch = (BatchBuilder()
                 .add_cache_get('key1')
                 .add_cache_set('key2', 'value2')
                 .add_log_info('Processing complete')
                 .build())
    """
    
    def __init__(self):
        self.operations = []
    
    def add_operation(self, interface: GatewayInterface, operation: str, **params):
        """Add generic operation to batch."""
        self.operations.append({
            'interface': interface,
            'operation': operation,
            'params': params
        })
        return self
    
    def add_cache_get(self, key: str):
        """Add cache get operation."""
        return self.add_operation(GatewayInterface.CACHE, 'get', key=key)
    
    def add_cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Add cache set operation."""
        return self.add_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl)
    
    def add_cache_delete(self, key: str):
        """Add cache delete operation."""
        return self.add_operation(GatewayInterface.CACHE, 'delete', key=key)
    
    def add_log_info(self, message: str, **extra):
        """Add log info operation."""
        return self.add_operation(GatewayInterface.LOGGING, 'log_info', message=message, extra=extra)
    
    def add_log_error(self, message: str, error: Optional[Exception] = None, **extra):
        """Add log error operation."""
        return self.add_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, extra=extra)
    
    def add_record_metric(self, name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None):
        """Add record metric operation."""
        return self.add_operation(GatewayInterface.METRICS, 'record_metric', name=name, value=value, dimensions=dimensions)
    
    def build(self) -> List[Dict[str, Any]]:
        """Build and return operations list."""
        return self.operations
    
    def execute(self, fail_fast: bool = False) -> List[Dict[str, Any]]:
        """Build and execute operations."""
        return execute_batch(self.operations, fail_fast=fail_fast)


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'execute_batch',
    'batch_cache_get',
    'batch_cache_set',
    'batch_cache_delete',
    'batch_record_metrics',
    'batch_increment_counters',
    'batch_log_messages',
    'execute_transaction',
    'execute_parallel',
    'analyze_batch_results',
    'BatchBuilder'
]

# EOF
