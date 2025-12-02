"""
ha_interface_validation.py - HA Validation Interface
Version: 2.0.0
Date: 2025-12-02
Description: HA-specific validation patterns only

MODIFIED: Removed all custom validation functions (~100 lines)
MODIFIED: Now uses gateway.validate_*() for generic validation
ADDED: DISPATCH dictionary for CR-1 pattern
ADDED: execute_validation_operation() router function
KEPT: HA-specific pattern validation only

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from gateway import validate_string, validate_dict, validate_list
from home_assistant.ha_config import (
    HA_ENTITY_ID_PATTERN,
    HA_DOMAIN_PATTERN,
    HA_SERVICE_PATTERN
)
import re


def _validate_entity_id(entity_id: str, **kwargs) -> bool:
    """Validate HA entity ID format: domain.entity"""
    return validate_string(
        entity_id,
        pattern=HA_ENTITY_ID_PATTERN,
        max_length=255
    )


def _validate_domain(domain: str, **kwargs) -> bool:
    """Validate HA domain name."""
    return validate_string(
        domain,
        pattern=HA_DOMAIN_PATTERN,
        max_length=50
    )


def _validate_service(service: str, **kwargs) -> bool:
    """Validate HA service name."""
    return validate_string(
        service,
        pattern=HA_SERVICE_PATTERN,
        max_length=50
    )


def _validate_event(event: dict, **kwargs) -> bool:
    """Validate HA event structure."""
    required = ['event_type', 'data']
    return validate_dict(event, required_keys=required)


def _validate_state(state: dict, **kwargs) -> bool:
    """Validate HA state structure."""
    required = ['entity_id', 'state']
    return validate_dict(state, required_keys=required)


# ADDED: DISPATCH dictionary (CR-1 pattern)
DISPATCH = {
    'entity_id': _validate_entity_id,
    'domain': _validate_domain,
    'service': _validate_service,
    'event': _validate_event,
    'state': _validate_state,
}


# ADDED: Execute operation router (CR-1 pattern)
def execute_validation_operation(operation: str, **kwargs) -> bool:
    """
    Execute validation operation via dispatch.
    
    Args:
        operation: Validation type
        **kwargs: Validation parameters
    
    Returns:
        Validation result (bool or raises exception)
    """
    if operation not in DISPATCH:
        raise ValueError(f"Unknown validation operation: {operation}")
    
    handler = DISPATCH[operation]
    return handler(**kwargs)


__all__ = [
    'execute_validation_operation',
    '_validate_entity_id',
    '_validate_domain',
    '_validate_service',
    '_validate_event',
    '_validate_state',
]
