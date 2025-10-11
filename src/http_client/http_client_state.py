"""
http_client_state.py
Version: 2025.09.30.02
Description: HTTP Client State Management

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
import logging

from gateway import (
    get_singleton, register_singleton,
    create_success_response, create_error_response,
    log_info, log_error,
    get_parameter, set_parameter,
    record_metric,
    execute_operation, GatewayInterface
)

logger = logging.getLogger(__name__)

def get_client_state(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get HTTP client state via gateway singleton."""
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
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
        
        if hasattr(client, 'pools'):
            state_info['pool_count'] = len(client.pools)
            state_info['pool_info'] = _get_pool_state(client)
        
        return state_info
    
    except Exception as e:
        log_error(f"Failed to get client state: {e}")
        return {'exists': False, 'error': str(e)}

def reset_client_state(client_type: str = None) -> Dict[str, Any]:
    """Reset HTTP client state via gateway singleton."""
    try:
        if client_type:
            singleton_key = f'http_client_{client_type}'
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset',
                singleton_name=singleton_key
            )
            record_metric(f'http_client_state.{client_type}.reset', 1.0)
        else:
            result = execute_operation(
                GatewayInterface.SINGLETON,
                'reset_all'
            )
            record_metric('http_client_state.reset_all', 1.0)
        
        return create_success_response("Client state reset", result)
    
    except Exception as e:
        log_error(f"Failed to reset client state: {e}")
        return create_error_response(str(e))

def initialize_client(client_type: str, configuration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize HTTP client with configuration."""
    try:
        singleton_key = f'http_client_{client_type}'
        existing_client = get_singleton(singleton_key)
        
        if existing_client:
            log_info(f"Client {client_type} already initialized")
            return create_success_response("Client already exists", {
                'client_type': client_type,
                'reused': True
            })
        
        if client_type == 'urllib3':
            import urllib3
            
            config = configuration or {}
            timeout = config.get('timeout', get_parameter('http_timeout', 30))
            retries = config.get('retries', get_parameter('http_retries', 3))
            
            client = urllib3.PoolManager(
                timeout=urllib3.Timeout(connect=10, read=timeout),
                retries=urllib3.Retry(total=retries)
            )
        else:
            return create_error_response(f"Unsupported client type: {client_type}")
        
        register_singleton(singleton_key, client)
        record_metric(f'http_client_state.{client_type}.initialized', 1.0)
        
        return create_success_response("Client initialized", {
            'client_type': client_type,
            'configuration': configuration
        })
    
    except Exception as e:
        log_error(f"Failed to initialize client: {e}")
        return create_error_response(str(e))

def cleanup_connections(client_type: str = 'urllib3', max_age_seconds: int = 300) -> Dict[str, Any]:
    """Cleanup old HTTP connections."""
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
            return create_success_response("No client to cleanup", {
                'client_type': client_type,
                'cleaned_pools': 0
            })
        
        cleaned_count = 0
        if hasattr(client, 'pools'):
            initial_count = len(client.pools)
            client.clear()
            cleaned_count = initial_count
            record_metric(f'http_client_state.{client_type}.cleanup', cleaned_count)
        
        return create_success_response("Connections cleaned", {
            'cleaned_pools': cleaned_count,
            'remaining_pools': len(client.pools) if hasattr(client, 'pools') else 0
        })
    
    except Exception as e:
        log_error(f"Connection cleanup failed: {e}")
        return create_error_response(str(e))

def get_client_configuration(client_type: str) -> Dict[str, Any]:
    """Get client configuration via gateway config."""
    try:
        config_key = f'http_client_{client_type}'
        client_config = get_parameter(config_key, {})
        
        default_config = {
            'timeout': get_parameter('http_timeout', 30),
            'retries': get_parameter('http_retries', 3),
            'pool_size': get_parameter('http_pool_size', 10)
        }
        
        return {
            'client_type': client_type,
            'configuration': {**default_config, **client_config}
        }
    
    except Exception as e:
        log_error(f"Failed to get client configuration: {e}")
        return {
            'client_type': client_type,
            'configuration': {},
            'error': str(e)
        }

def update_client_configuration(client_type: str, new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration via gateway config."""
    try:
        config_key = f'http_client_{client_type}'
        success = set_parameter(config_key, new_config)
        
        if success:
            reset_result = reset_client_state(client_type)
            record_metric(f'http_client_state.{client_type}.config_updated', 1.0)
            
            return create_success_response("Configuration updated", {
                'client_type': client_type,
                'configuration_updated': True,
                'client_reset': reset_result.get('success', False)
            })
        else:
            return create_error_response('Failed to update configuration')
    
    except Exception as e:
        log_error(f"Configuration update failed: {e}")
        return create_error_response(str(e))

def get_connection_statistics(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get connection statistics for client."""
    try:
        singleton_key = f'http_client_{client_type}'
        client = get_singleton(singleton_key)
        
        if not client:
            return {
                'client_type': client_type,
                'statistics': {},
                'available': False
            }
        
        stats = {
            'client_type': client_type,
            'available': True
        }
        
        if hasattr(client, 'pools'):
            stats['total_pools'] = len(client.pools)
            stats['pool_details'] = _get_pool_statistics(client)
        
        return stats
    
    except Exception as e:
        log_error(f"Failed to get connection statistics: {e}")
        return {
            'client_type': client_type,
            'statistics': {},
            'error': str(e)
        }

def _get_pool_state(client) -> Dict[str, Any]:
    """Get detailed pool state information."""
    try:
        pool_info = {
            'total_pools': len(client.pools),
            'pools': []
        }
        
        for key, pool in client.pools.items():
            pool_info['pools'].append({
                'host': key[0] if isinstance(key, tuple) else str(key),
                'num_connections': pool.num_connections if hasattr(pool, 'num_connections') else 0
            })
        
        return pool_info
    except Exception:
        return {'total_pools': 0, 'pools': []}

def _get_pool_statistics(client) -> List[Dict[str, Any]]:
    """Get detailed statistics for each pool."""
    stats = []
    try:
        for key, pool in client.pools.items():
            pool_stat = {
                'host': key[0] if isinstance(key, tuple) else str(key),
                'connections': pool.num_connections if hasattr(pool, 'num_connections') else 0
            }
            stats.append(pool_stat)
    except Exception:
        pass
    return stats
