"""
gateway_wrappers_debug.py - DEBUG Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for DEBUG interface operations

CHANGELOG:
- 2025.10.22.02: Added WEBSOCKET and CIRCUIT_BREAKER interface debug operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


# ===== GENERAL DEBUG OPERATIONS =====

def check_component_health(component: str) -> Dict[str, Any]:
    """Check component health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_component_health', component=component)


def check_gateway_health() -> Dict[str, Any]:
    """Check gateway health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_gateway_health')


def diagnose_system_health() -> Dict[str, Any]:
    """Diagnose system health."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_system_health')


def run_debug_tests() -> Dict[str, Any]:
    """Run debug tests."""
    return execute_operation(GatewayInterface.DEBUG, 'run_debug_tests')


def validate_system_architecture() -> Dict[str, Any]:
    """Validate system architecture."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_system_architecture')


# ===== CONFIG DEBUG OPERATIONS (2025.10.22.02) =====

def check_config_health() -> Dict[str, Any]:
    """
    Check CONFIG interface health.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness
    - No threading locks (AP-08 compliance)
    - Reset operation availability
    - Parameter operations working
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_config_health')


def diagnose_config_performance() -> Dict[str, Any]:
    """
    Diagnose CONFIG interface performance.
    
    Analyzes:
    - Rate limiting effectiveness
    - Parameter operation performance
    - SSM vs environment variable usage
    - Configuration reload patterns
    - Cache hit rates
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_config_performance')


def validate_config_configuration() -> Dict[str, Any]:
    """
    Validate CONFIG interface configuration.
    
    Checks:
    - SINGLETON registration
    - No threading locks (AP-08 compliance)
    - Rate limiting configuration
    - Parameter Store setup
    - Reset operation availability
    - Configuration initialization
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_config_configuration')


def benchmark_config_operations() -> Dict[str, Any]:
    """
    Benchmark CONFIG interface operations.
    
    Measures:
    - Parameter get/set operations
    - Configuration validation
    - Reset operation
    - Rate limiting overhead
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_config_operations')


# ===== HTTP_CLIENT DEBUG OPERATIONS (2025.10.22.02) =====

def check_http_client_health() -> Dict[str, Any]:
    """
    Check HTTP_CLIENT interface health and compliance.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness
    - No threading locks (AP-08)
    - Reset operation availability
    - Connection pool status
    - Request statistics
    
    Returns:
        Dict with health status and detailed checks
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_http_client_health')


def diagnose_http_client_performance() -> Dict[str, Any]:
    """
    Diagnose HTTP_CLIENT interface performance characteristics.
    
    Analyzes:
    - Request patterns and statistics
    - Connection pool utilization
    - Retry behavior effectiveness
    - Rate limiting impact
    - Error rates and types
    
    Returns:
        Dict with performance diagnostics
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_http_client_performance')


def validate_http_client_configuration() -> Dict[str, Any]:
    """
    Validate HTTP_CLIENT interface configuration and compliance.
    
    Validates:
    - SINGLETON registration compliance
    - Threading lock compliance (CRITICAL)
    - Rate limiting configuration (500 ops/sec)
    - Connection pool settings
    - Retry configuration
    - Reset operation availability
    
    Returns:
        Dict with validation results and compliance status
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_http_client_configuration')


def benchmark_http_client_operations() -> Dict[str, Any]:
    """
    Benchmark HTTP_CLIENT interface operations.
    
    Benchmarks:
    - GET request setup (100 ops)
    - POST request setup (100 ops)
    - Manager retrieval (50 ops)
    - get_stats (200 ops)
    - reset (10 ops)
    
    Total: 460 operations
    
    NOTE: Tests infrastructure only, not actual network performance.
    
    Returns:
        Dict with benchmark results for each operation
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_http_client_operations')


# ===== WEBSOCKET DEBUG OPERATIONS (2025.10.22.02) =====

def check_websocket_health() -> Dict[str, Any]:
    """
    Check WEBSOCKET interface health and compliance.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness (300 ops/sec)
    - No threading locks (AP-08)
    - Reset operation availability
    - Core operations availability
    - Statistics tracking
    
    Returns:
        Dict with health status and detailed checks
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_websocket_health')


def diagnose_websocket_performance() -> Dict[str, Any]:
    """
    Diagnose WEBSOCKET interface performance characteristics.
    
    Analyzes:
    - Connection patterns and statistics
    - Message send/receive ratios
    - Error rates and types
    - Rate limiting impact
    - Performance recommendations
    
    Returns:
        Dict with performance diagnostics
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_websocket_performance')


def validate_websocket_configuration() -> Dict[str, Any]:
    """
    Validate WEBSOCKET interface configuration and compliance.
    
    Validates:
    - SINGLETON registration compliance
    - Threading lock compliance (CRITICAL)
    - Rate limiting configuration (300 ops/sec)
    - Reset operation availability
    - Core operations availability
    - Interface router availability
    
    Returns:
        Dict with validation results and compliance status
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_websocket_configuration')


def benchmark_websocket_operations() -> Dict[str, Any]:
    """
    Benchmark WEBSOCKET interface operations.
    
    Benchmarks:
    - Manager retrieval (50 ops)
    - get_stats (200 ops)
    - reset (10 ops)
    - Rate limit checking (50 ops)
    
    Total: 310 operations
    
    NOTE: Tests infrastructure only, not actual network performance.
          WebSocket operations depend on external network conditions.
    
    Returns:
        Dict with benchmark results for each operation
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_websocket_operations')


# ===== CIRCUIT_BREAKER DEBUG OPERATIONS (2025.10.22.02) =====

def check_circuit_breaker_health() -> Dict[str, Any]:
    """
    Check CIRCUIT_BREAKER interface health and compliance.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness (1000 ops/sec)
    - No threading locks (AP-08, DEC-04) - CRITICAL
    - Reset operation availability
    - Core operations availability
    - Statistics tracking
    - Circuit breaker functionality
    
    Returns:
        Dict with health status and detailed checks
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_circuit_breaker_health')


def diagnose_circuit_breaker_performance() -> Dict[str, Any]:
    """
    Diagnose CIRCUIT_BREAKER interface performance characteristics.
    
    Analyzes:
    - Operation statistics across all breakers
    - Circuit breaker states and patterns
    - Success/failure/rejection rates
    - Rate limiting impact
    - Performance recommendations
    
    Returns:
        Dict with performance diagnostics
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_circuit_breaker_performance')


def validate_circuit_breaker_configuration() -> Dict[str, Any]:
    """
    Validate CIRCUIT_BREAKER interface configuration and compliance.
    
    Validates:
    - SINGLETON registration compliance
    - Threading lock compliance (CRITICAL)
    - Rate limiting configuration (1000 ops/sec)
    - Reset operation availability
    - Core operations availability
    - Manager and breaker class structure
    
    Returns:
        Dict with validation results and compliance status
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_circuit_breaker_configuration')


def benchmark_circuit_breaker_operations() -> Dict[str, Any]:
    """
    Benchmark CIRCUIT_BREAKER interface operations.
    
    Benchmarks:
    - Manager retrieval (50 ops)
    - Circuit breaker creation (100 ops)
    - get_all_states (100 ops)
    - get_stats (200 ops)
    - reset (10 ops)
    - Rate limit checking (50 ops)
    
    Total: 510 operations
    
    NOTE: Tests infrastructure only, not actual protected function calls.
          Overhead depends on protected function complexity.
    
    Returns:
        Dict with benchmark results for each operation
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_circuit_breaker_operations')


__all__ = [
    # General debug operations
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
    
    # CONFIG debug operations
    'check_config_health',
    'diagnose_config_performance',
    'validate_config_configuration',
    'benchmark_config_operations',
    
    # HTTP_CLIENT debug operations
    'check_http_client_health',
    'diagnose_http_client_performance',
    'validate_http_client_configuration',
    'benchmark_http_client_operations',
    
    # WEBSOCKET debug operations
    'check_websocket_health',
    'diagnose_websocket_performance',
    'validate_websocket_configuration',
    'benchmark_websocket_operations',
    
    # CIRCUIT_BREAKER debug operations
    'check_circuit_breaker_health',
    'diagnose_circuit_breaker_performance',
    'validate_circuit_breaker_configuration',
    'benchmark_circuit_breaker_operations',
]
