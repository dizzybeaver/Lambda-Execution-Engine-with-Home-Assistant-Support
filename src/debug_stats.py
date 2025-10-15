"""
debug_stats.py - Debug Statistics Operations
Version: 2025.10.14.01
Description: Statistics and metrics operations for debug subsystem

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

from typing import Dict, Any
import sys


def _get_system_stats(**kwargs) -> Dict[str, Any]:
    """Get comprehensive system statistics."""
    try:
        modules = list(sys.modules.keys())
        project_modules = [m for m in modules if not m.startswith('_') and '.' not in m]
        
        return {
            'success': True,
            'total_modules': len(modules),
            'project_modules': len(project_modules),
            'python_version': sys.version,
            'platform': sys.platform
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _get_optimization_stats(**kwargs) -> Dict[str, Any]:
    """Get optimization statistics with dispatcher stats."""
    from debug.debug_verification import _verify_registry_operations
    
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
    except:
        gateway_stats = {'error': 'gateway stats not available'}
    
    try:
        from import_fixer import get_import_statistics
        import_stats = get_import_statistics('.')
    except:
        import_stats = {'error': 'import_fixer not available'}
    
    verification_results = _verify_registry_operations()
    
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'success': True,
        'gateway_stats': gateway_stats,
        'import_compliance': import_stats,
        'registry_verification': verification_results,
        'dispatcher_stats': dispatcher_stats,
        'optimization_phase': 'Phase 4 Task #7 Complete'
    }


def _get_dispatcher_stats(**kwargs) -> Dict[str, Any]:
    """Get dispatcher performance stats - delegates to METRICS."""
    try:
        from gateway import execute_operation, GatewayInterface
        return execute_operation(GatewayInterface.METRICS, 'get_dispatcher_metrics')
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'note': 'Dispatcher metrics require METRICS interface support'
        }


def _get_operation_metrics(**kwargs) -> Dict[str, Any]:
    """Get operation-level metrics."""
    try:
        from gateway import execute_operation, GatewayInterface
        return execute_operation(GatewayInterface.METRICS, 'get_operation_metrics')
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'note': 'Operation metrics require METRICS interface support'
        }


__all__ = [
    '_get_system_stats',
    '_get_optimization_stats',
    '_get_dispatcher_stats',
    '_get_operation_metrics'
]

# EOF
