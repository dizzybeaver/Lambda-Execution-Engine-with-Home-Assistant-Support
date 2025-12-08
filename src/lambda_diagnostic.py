"""
lambda_diagnostic.py
Version: 2025-12-08_1
Purpose: Diagnostic mode handler (wrapper for DIAGNOSIS interface)
License: Apache 2.0
"""

from typing import Dict, Any
import gateway


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Diagnostic mode handler - tests module imports sequentially."""
    
    # Define critical modules to test in order
    modules = [
        'gateway_core',
        'gateway_wrappers_cache',
        'gateway_wrappers_logging',
        'gateway_wrappers_security',
        'gateway_wrappers_metrics',
        'gateway_wrappers_config',
        'gateway_wrappers_singleton',
        'gateway_wrappers_initialization',
        'gateway_wrappers_http_client',
        'gateway_wrappers_websocket',
        'gateway_wrappers_circuit_breaker',
        'gateway_wrappers_utility',
        'gateway_wrappers_debug',
        'gateway_wrappers_diagnosis',
        'gateway_wrappers_test',
        'gateway',
        'interface_cache',
        'interface_logging',
        'interface_security',
        'interface_metrics',
        'interface_config',
        'interface_singleton',
        'interface_initialization',
        'interface_http_client',
        'interface_websocket',
        'interface_circuit_breaker',
        'interface_utility',
        'interface_debug',
        'interface_diagnosis',
        'interface_test',
        'cache_core',
        'logging_core',
        'security_core',
    ]
    
    # Use DIAGNOSIS interface via gateway
    return gateway.test_import_sequence(modules)

# EOF
