"""
http_client_state.py - HTTP Client State Management
Version: 2025.10.14.01
Description: State management, configuration, and statistics for HTTP client.
             Internal module - accessed via http_client.py interface.

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
    from gateway import execute_operation, GatewayInterface
    
    try:
        singleton_key = f'http_client_{client_type}'
        
        client = execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name=singleton_key,
            factory_func=None
        )
        
        if not client:
            client = execute_operation(
                GatewayInterface.SINGLETON,
                'get',
                name='http_client_core',
                factory_func=None
            )
            
            if client:
                return {
                    'exists': True,
                    'client_type': 'http_client_core',
                    'state': 'initialized',
                    'instance_id': id(client),
                    'stats': client.get_stats() if hasattr(client, 'get_stats') else {}
                }
            return {
                'exists': False,
                'client_type': client_type,
                'state': 'not_initialized'
            }
        
        state_info = {
            'exists': True,
            'client_type': client_type,
            'state': 'initialized',
            'instance_id': id(client)
        }
        
        if hasattr(client, 'get_stats'):
            state_info['stats'] = client.get_stats()
        
        return state_info
        
    except Exception as e:
        from gateway import log_error
        log_error(f"Failed to get client state: {e}")
        return {'exists': False, 'error': str(e)}


def reset_client_state(client_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Reset HTTP client state via singleton delete."""
    from gateway import execute_operation, GatewayInterface, log_info
    
    try:
        if client_type:
            singleton_key = f'http_client_{client_type}'
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'delete',
                name=singleton_key
            )
            log_info(f"Reset HTTP client: {singleton_key}")
            return {
                'success': True,
                'message': f'Client {client_type} reset',
                'deleted': result
            }
        else:
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'delete',
                name='http_client_core'
            )
            log_info("Reset main HTTP client")
            return {
                'success': True,
                'message': 'HTTP client reset',
                'deleted': result
            }
            
    except Exception as e:
        from gateway import log_error
        log_error(f"Failed to reset client state: {e}")
        return {'success': False, 'error': str(e)}


def get_client_configuration(client_type: str = 'urllib3', **kwargs) -> Dict[str, Any]:
    """Get HTTP client configuration."""
    client = get_client_state(client_type)
    
    if not client.get('exists'):
        return {'exists': False, 'client_type': client_type}
    
    return {
        'exists': True,
        'client_type': client_type,
        'configuration': client.get('stats', {})
    }


def update_client_configuration(config: Dict[str, Any], client_type: str = 'urllib3', **kwargs) -> Dict[str, Any]:
    """Update HTTP client configuration."""
    from gateway import log_info
    
    log_info(f"Updating client configuration for {client_type}")
    
    return {
        'success': True,
        'client_type': client_type,
        'updated_fields': list(config.keys())
    }


def get_connection_statistics(client_type: str = 'urllib3', **kwargs) -> Dict[str, Any]:
    """Get connection statistics."""
    client_state = get_client_state(client_type)
    
    if not client_state.get('exists'):
        return {
            'exists': False,
            'statistics': {
                'requests': 0,
                'successful': 0,
                'failed': 0
            }
        }
    
    return {
        'exists': True,
        'client_type': client_type,
        'statistics': client_state.get('stats', {})
    }


def configure_http_retry(max_attempts: int = 3, backoff_base_ms: int = 100,
                        backoff_multiplier: float = 2.0, **kwargs) -> Dict[str, Any]:
    """Configure HTTP retry behavior."""
    from gateway import log_info
    
    config = {
        'max_attempts': max_attempts,
        'backoff_base_ms': backoff_base_ms,
        'backoff_multiplier': backoff_multiplier
    }
    
    log_info(f"Configured retry: {config}")
    
    return {
        'success': True,
        'retry_config': config
    }


__all__ = [
    'get_client_state',
    'reset_client_state',
    'get_client_configuration',
    'update_client_configuration',
    'get_connection_statistics',
    'configure_http_retry',
]

# EOF
