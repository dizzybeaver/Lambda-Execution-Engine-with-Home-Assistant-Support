"""
http_client_state.py - HTTP Client State Management
Version: 2025.09.24.01
Description: HTTP client state management using singleton.py gateway interface

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Client lifecycle management via singleton.py
- Connection pool state via singleton.py
- Configuration state via config.py
- Metrics state via metrics.py

PRIMARY FILE: http_client.py (interface)
SECONDARY FILE: http_client_state.py (state management)

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

from typing import Dict, Any, Optional, Union
import logging

# Gateway imports
from . import singleton
from . import config
from . import metrics

logger = logging.getLogger(__name__)

# ===== CLIENT STATE MANAGEMENT FUNCTIONS =====

def get_client_state(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get HTTP client state via singleton.py."""
    
    try:
        singleton_key = f'http_client_{client_type}'
        
        # Use singleton.py for state retrieval
        client = singleton.get_singleton(singleton_key)
        
        if not client:
            return {
                'exists': False,
                'client_type': client_type,
                'state': 'not_initialized'
            }
        
        # Extract client state information
        state_info = {
            'exists': True,
            'client_type': client_type,
            'state': 'initialized',
            'instance_id': id(client)
        }
        
        # Add urllib3-specific state if available
        if hasattr(client, 'pools'):
            state_info['pool_count'] = len(client.pools)
            state_info['pool_info'] = _get_pool_state(client)
        
        return state_info
        
    except Exception as e:
        logger.error(f"Failed to get client state: {e}")
        return {
            'exists': False,
            'error': str(e)
        }

def reset_client_state(client_type: str = None) -> Dict[str, Any]:
    """Reset HTTP client state via singleton.py."""
    
    try:
        if client_type:
            singleton_key = f'http_client_{client_type}'
            
            # Use singleton.py for state reset
            result = singleton.manage_singletons('reset', singleton_key)
            
            metrics.increment_counter(f'http_client_state.{client_type}.reset')
            
            return {
                'success': True,
                'client_type': client_type,
                'action': 'reset',
                'result': result
            }
        else:
            # Reset all HTTP clients
            result = singleton.manage_singletons('reset_all', 'http_client')
            
            metrics.increment_counter('http_client_state.all.reset')
            
            return {
                'success': True,
                'client_type': 'all',
                'action': 'reset_all',
                'result': result
            }
        
    except Exception as e:
        logger.error(f"Failed to reset client state: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_all_client_states() -> Dict[str, Any]:
    """Get state of all HTTP clients via singleton.py."""
    
    try:
        # Use singleton.py to get system status
        singleton_status = singleton.get_system_status()
        
        client_states = {}
        
        # Filter for HTTP client singletons
        for key, info in singleton_status.items():
            if key.startswith('http_client_'):
                client_type = key.replace('http_client_', '')
                client_states[client_type] = {
                    'state': 'initialized' if info else 'not_initialized',
                    'singleton_info': info
                }
        
        return {
            'client_count': len(client_states),
            'clients': client_states
        }
        
    except Exception as e:
        logger.error(f"Failed to get all client states: {e}")
        return {
            'client_count': 0,
            'clients': {},
            'error': str(e)
        }

def optimize_client_state(client_type: str = None) -> Dict[str, Any]:
    """Optimize HTTP client state for memory efficiency."""
    
    try:
        results = {}
        
        if client_type:
            result = _optimize_single_client(client_type)
            results[client_type] = result
        else:
            # Optimize all clients
            all_states = get_all_client_states()
            for client_name in all_states.get('clients', {}):
                result = _optimize_single_client(client_name)
                results[client_name] = result
        
        return {
            'success': True,
            'optimized_clients': results
        }
        
    except Exception as e:
        logger.error(f"Client optimization failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== CONNECTION POOL STATE FUNCTIONS =====

def get_pool_statistics(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Get connection pool statistics."""
    
    try:
        singleton_key = f'http_client_{client_type}'
        client = singleton.get_singleton(singleton_key)
        
        if not client or not hasattr(client, 'pools'):
            return {
                'pool_count': 0,
                'pools': {}
            }
        
        pool_stats = {}
        for pool_key, pool in client.pools.items():
            pool_stats[pool_key] = _get_individual_pool_stats(pool)
        
        return {
            'pool_count': len(pool_stats),
            'pools': pool_stats,
            'total_connections': sum(p.get('num_connections', 0) for p in pool_stats.values())
        }
        
    except Exception as e:
        logger.error(f"Failed to get pool statistics: {e}")
        return {
            'pool_count': 0,
            'pools': {},
            'error': str(e)
        }

def cleanup_idle_connections(client_type: str = 'urllib3') -> Dict[str, Any]:
    """Clean up idle connections in pools."""
    
    try:
        singleton_key = f'http_client_{client_type}'
        client = singleton.get_singleton(singleton_key)
        
        if not client or not hasattr(client, 'pools'):
            return {
                'success': False,
                'error': 'Client or pools not available'
            }
        
        cleaned_count = 0
        
        for pool_key, pool in list(client.pools.items()):
            if hasattr(pool, 'num_connections') and pool.num_connections == 0:
                # Remove idle pools
                del client.pools[pool_key]
                cleaned_count += 1
        
        metrics.increment_counter(f'http_client_state.{client_type}.cleanup')
        
        return {
            'success': True,
            'cleaned_pools': cleaned_count,
            'remaining_pools': len(client.pools)
        }
        
    except Exception as e:
        logger.error(f"Connection cleanup failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== CONFIGURATION STATE FUNCTIONS =====

def get_client_configuration(client_type: str) -> Dict[str, Any]:
    """Get client configuration via config.py."""
    
    try:
        config_key = f'http_client_{client_type}'
        
        # Use config.py for configuration retrieval
        client_config = config.get_parameter(config_key, {})
        
        # Add default configuration
        default_config = {
            'timeout': config.get_parameter('http_timeout', 30),
            'retries': config.get_parameter('http_retries', 3),
            'pool_size': config.get_parameter('http_pool_size', 10)
        }
        
        return {
            'client_type': client_type,
            'configuration': {**default_config, **client_config}
        }
        
    except Exception as e:
        logger.error(f"Failed to get client configuration: {e}")
        return {
            'client_type': client_type,
            'configuration': {},
            'error': str(e)
        }

def update_client_configuration(client_type: str, 
                              new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update client configuration via config.py."""
    
    try:
        config_key = f'http_client_{client_type}'
        
        # Use config.py for configuration update
        success = config.set_parameter(config_key, new_config)
        
        if success:
            # Reset client to pick up new configuration
            reset_result = reset_client_state(client_type)
            
            metrics.increment_counter(f'http_client_state.{client_type}.config_updated')
            
            return {
                'success': True,
                'client_type': client_type,
                'configuration_updated': True,
                'client_reset': reset_result.get('success', False)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to update configuration'
            }
        
    except Exception as e:
        logger.error(f"Configuration update failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# ===== HELPER FUNCTIONS =====

def _get_pool_state(client) -> Dict[str, Any]:
    """Get detailed pool state information."""
    
    try:
        pool_info = {}
        
        for pool_key, pool in client.pools.items():
            pool_info[pool_key] = _get_individual_pool_stats(pool)
        
        return pool_info
        
    except Exception as e:
        logger.error(f"Failed to get pool state: {e}")
        return {}

def _get_individual_pool_stats(pool) -> Dict[str, Any]:
    """Get statistics for individual pool."""
    
    try:
        stats = {}
        
        # Common pool attributes
        if hasattr(pool, 'num_connections'):
            stats['num_connections'] = pool.num_connections
        
        if hasattr(pool, 'pool'):
            stats['pool_size'] = len(pool.pool._queue)
        
        if hasattr(pool, 'timeout'):
            stats['timeout'] = str(pool.timeout)
        
        return stats
        
    except Exception as e:
        return {'error': str(e)}

def _optimize_single_client(client_type: str) -> Dict[str, Any]:
    """Optimize single client state."""
    
    try:
        # Clean up idle connections
        cleanup_result = cleanup_idle_connections(client_type)
        
        # Get current state
        current_state = get_client_state(client_type)
        
        return {
            'client_type': client_type,
            'cleanup_performed': cleanup_result.get('success', False),
            'current_state': current_state
        }
        
    except Exception as e:
        return {
            'client_type': client_type,
            'error': str(e)
        }

# EOF
