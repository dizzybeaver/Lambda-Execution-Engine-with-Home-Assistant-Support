"""
test/__init__.py - TEST Core Implementations Package
Version: 2025-12-08_1
Purpose: Test implementation modules in /src/test/ subdirectory
License: Apache 2.0
"""

# CRITICAL: No relative imports (AP-28) - Lambda fails with dots
# Use absolute imports from sys.path root
import test.test_core
import test.test_scenarios
import test.test_performance
import test.test_lambda_modes

# Make modules accessible via "from test import test_core"
test_core = test.test_core
test_scenarios = test.test_scenarios
test_performance = test.test_performance
test_lambda_modes = test.test_lambda_modes

__version__ = '2025-12-08_1'
__interface__ = 'INT-15'

__all__ = [
    'test_core',
    'test_scenarios',
    'test_performance',
    'test_lambda_modes'
]
