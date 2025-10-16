"""
http_client_state.py - HTTP Client State Management
Version: 2025.10.16.02
Description: State management, configuration, and statistics for HTTP client.
             Internal module - accessed via http_client.py interface.

CHANGELOG:
- 2025.10.16.02: Added missing functions configure_http_retry and get_connection_statistics
                 Improved error handling and state management

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

from typing import Dict, Any, Optional


def get_client_state(client_type: str = 'urllib3', **kwargs) -> Dict[str, Any]:
    """Get HTTP client state via singleton."""
    from gateway import execute_operation, GatewayInterface, log_error
    
    try:
        # Try to get the specific client type first
        singleton_key = f'http_client_{client_type}'
        
        # Check if singleton exists first
        exists = execute_operation(
            GatewayInterface.SINGLETON,
            'has',
            name=singleton_key
        )
        
        if exists:
            client = execute_operation(
                GatewayInterface.SINGLETON,
                'get',
                name=singleton_key,
                factory_func=None
            )
            
            if client:
                state_info = {
                    'exists': True,
                    'client_type': client_type,
                    'state': 'initialized',
                    'instance_id': id(client)
                }
                
                if hasattr(client, 'get_stats'):
                    state_info['stats'] = client.get_stats()
                
                return state_info
        
        # Fallback to default http_client_core
        exists = execute_operation(
            GatewayInterface.SINGLETON,
            'has',
            name='http_client_core'
        )
        
        if exists:
            client = execute_operation(
                GatewayInterface.SINGLETON,
                'get',
                name='http_client_core',
                factory_func=None
            )
            
            if client:
                state_info = {
                    'exists': True,
                    'client_type': 'http_client_core',
                    'state': 'initialized',
                    'instance_id': id(client)
                }
                
                if hasattr(client, 'get_stats'):
                    state_info['stats'] = client.get_stats()
                
                return state_info
        
        # No client exists
        return {
            'exists': False,
            'client_type': client_type,
            'state': 'not_initialized',
            'error': None
        }
        
    except Exception as e:
        log_error(f"Failed to get client state: {e}", error=e)
        return {
            'exists': False,
            'client_type': client_type,
            'state': 'error',
            'error': str(e)
        }


def reset_client_state(client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Reset HTTP client state via singleton delete."""
    from gateway import execute_operation, GatewayInterface, log_info, log_error
    
    try:
        if client_type:
            # Reset specific client type
            singleton_key = f'http_client_{client_type}'
            deleted = execute_operation(
                GatewayInterface.SINGLETON,
                'delete',
                name=singleton_key
            )
            
            if deleted:
                log_info(f"Reset HTTP client state: {client_type}")
                return {
                    'success': True,
                    'client_type': client_type,
                    'message': 'Client state reset'
                }
            else:
                return {
                    'success': False,
                    'client_type': client_type,
                    'message': 'Client not found or already reset'
                }
        else:
            # Reset all HTTP clients
            count = 0
            for key in ['http_client_core', 'http_client_urllib3']:
                deleted = execute_operation(
                    GatewayInterface.SINGLETON,
                    'delete',
                    name=key
                )
                if deleted:
                    count += 1
            
            log_info(f"Reset {count} HTTP client(s)")
            return {
                'success': True,
                'count': count,
                'message': f'Reset {count} client(s)'
            }
            
    except Exception as e:
        log_error(f"Failed to reset client state: {e}", error=e)
        return {
            'success': False,
            'error': str(e)
        }


def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100, 
                        backoff_multiplier: float = 2.0, **kwargs) -> Dict[str, Any]:
    """
    Configure HTTP retry behavior.
    
    Args:
        max_attempts: Maximum retry attempts (1-10)
        backoff_base_ms: Base backoff time in milliseconds (50-1000)
        backoff_multiplier: Backoff multiplier (1.0-5.0)
        
    Returns:
        Dict with success status and configuration
    """
    from gateway import log_info, log_error, create_success_response, create_error_response
    
    try:
        # Validate parameters
        if not (1 <= max_attempts <= 10):
            return create_error_response(
                'max_attempts must be between 1 and 10',
                'VALIDATION_ERROR'
            )
        
        if not (50 <= backoff_base_ms <= 1000):
            return create_error_response(
                'backoff_base_ms must be between 50 and 1000',
                'VALIDATION_ERROR'
            )
        
        if not (1.0 <= backoff_multiplier <= 5.0):
            return create_error_response(
                'backoff_multiplier must be between 1.0 and 5.0',
                'VALIDATION_ERROR'
            )
        
        # Get current client
        from http_client_core import get_http_client
        client = get_http_client()
        
        # Update retry configuration
        client._retry_config['max_attempts'] = max_attempts
        client._retry_config['backoff_base_ms'] = backoff_base_ms
        client._retry_config['backoff_multiplier'] = backoff_multiplier
        
        log_info(f"Configured HTTP retry: max_attempts={max_attempts}, "
                f"backoff_base_ms={backoff_base_ms}, backoff_multiplier={backoff_multiplier}")
        
        return create_success_response('HTTP retry configured', {
            'max_attempts': max_attempts,
            'backoff_base_ms': backoff_base_ms,
            'backoff_multiplier': backoff_multiplier
        })
        
    except Exception as e:
        log_error(f"Failed to configure HTTP retry: {e}", error=e)
        return create_error_response(f'Configuration failed: {str(e)}', 'CONFIGURATION_ERROR')


def get_connection_statistics(**kwargs) -> Dict[str, Any]:
    """
    Get HTTP client connection statistics.
    
    Returns:
        Dict with client statistics including requests, successes, failures, retries
    """
    from gateway import log_info, create_success_response, create_error_response
    
    try:
        # Get current client
        from http_client_core import get_http_client
        client = get_http_client()
        
        # Get statistics
        stats = client.get_stats()
        
        # Calculate additional metrics
        total_requests = stats.get('requests', 0)
        successful = stats.get('successful', 0)
        failed = stats.get('failed', 0)
        retries = stats.get('retries', 0)
        
        success_rate = (successful / total_requests * 100) if total_requests > 0 else 0.0
        failure_rate = (failed / total_requests * 100) if total_requests > 0 else 0.0
        
        statistics = {
            'requests': total_requests,
            'successful': successful,
            'failed': failed,
            'retries': retries,
            'success_rate': round(success_rate, 2),
            'failure_rate': round(failure_rate, 2),
            'retry_config': client._retry_config.copy()
        }
        
        return create_success_response('Statistics retrieved', statistics)
        
    except Exception as e:
        from gateway import log_error
        log_error(f"Failed to get connection statistics: {e}", error=e)
        return create_error_response(f'Failed to get statistics: {str(e)}', 'STATISTICS_ERROR')


__all__ = [
    'get_client_state',
    'reset_client_state',
    'configure_http_retry',
    'get_connection_statistics',
]

# EOF
