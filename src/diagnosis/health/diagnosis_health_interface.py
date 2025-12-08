"""
diagnosis/health/diagnosis_health_interface.py
Version: 2025-12-08_1
Purpose: Interface-specific health checks (INITIALIZATION, UTILITY, SINGLETON)
License: Apache 2.0
"""

import time
from typing import Dict, Any


def check_initialization_health(**kwargs) -> Dict[str, Any]:
    """Check INITIALIZATION interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import initialization_core
        from gateway import singleton_get
        
        health = {
            'interface': 'INITIALIZATION',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        manager = singleton_get('initialization_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'INITIALIZATION manager must be registered (LESS-18)'
        }
        
        if hasattr(initialization_core, 'InitializationCore'):
            core_instance = initialization_core.InitializationCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {
                'status': 'fail',
                'value': False,
                'requirement': 'InitializationCore class not found'
            }
        
        source_file = initialization_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'from threading import Lock' in source_code or 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        has_reset = hasattr(initialization_core.InitializationCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(initialization_core, 'InitializationCore') else False
        
        all_checks_pass = all(check['status'] == 'pass' for check in health['checks'].values())
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {'interface': 'INITIALIZATION', 'status': 'error', 'error': str(e), 'timestamp': time.time()}


def check_utility_health(**kwargs) -> Dict[str, Any]:
    """Check UTILITY interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import utility_core
        from gateway import singleton_get
        
        health = {
            'interface': 'UTILITY',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        manager = singleton_get('utility_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'UTILITY manager must be registered (LESS-18)'
        }
        
        if hasattr(utility_core, 'SharedUtilityCore'):
            core_instance = utility_core.SharedUtilityCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {'status': 'fail', 'value': False, 'requirement': 'SharedUtilityCore class not found'}
        
        source_file = utility_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        has_reset = hasattr(utility_core.SharedUtilityCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(utility_core, 'SharedUtilityCore') else False
        
        all_checks_pass = all(check['status'] == 'pass' for check in health['checks'].values())
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {'interface': 'UTILITY', 'status': 'error', 'error': str(e), 'timestamp': time.time()}


def check_singleton_health(**kwargs) -> Dict[str, Any]:
    """Check SINGLETON interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import singleton_core
        from gateway import singleton_get
        
        health = {
            'interface': 'SINGLETON',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        manager = singleton_get('singleton_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'SINGLETON manager must be registered (LESS-18)'
        }
        
        if hasattr(singleton_core, 'SingletonCore'):
            core_instance = singleton_core.SingletonCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {'status': 'fail', 'value': False, 'requirement': 'SingletonCore class not found'}
        
        source_file = singleton_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'from threading import Lock' in source_code or 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        has_reset = hasattr(singleton_core.SingletonCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(singleton_core, 'SingletonCore') else False
        
        all_checks_pass = all(check['status'] == 'pass' for check in health['checks'].values())
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {'interface': 'SINGLETON', 'status': 'error', 'error': str(e), 'timestamp': time.time()}


__all__ = [
    'check_initialization_health',
    'check_utility_health',
    'check_singleton_health'
]
