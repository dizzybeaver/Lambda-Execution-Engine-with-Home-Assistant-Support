"""
test/__init__.py - TEST Core Implementations Package
Version: 2025-12-08_1
Purpose: Test implementation modules in /test/ subdirectory
License: Apache 2.0
"""

# Lazy loading - modules imported on demand via ../interface_test.py
# No module-level imports to minimize cold start impact

__version__ = '2025-12-08_1'
__interface__ = 'INT-15'

__all__ = [
    'test_core',
    'test_scenarios',
    'test_performance',
    'test_lambda_modes'
]
