"""
ha_alexa_templates.py - Alexa Smart Home API response templates
Version: 1.0.0
Date: 2025-12-02
Description: Pure data structures - no logic

Used with gateway.render_template() for response building.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

ALEXA_ERROR_RESPONSE = {
    'event': {
        'header': {
            'namespace': 'Alexa',
            'name': 'ErrorResponse',
            'messageId': '{message_id}',
            'correlationToken': '{correlation_token}',
            'payloadVersion': '3'
        },
        'payload': {
            'type': '{error_type}',
            'message': '{error_message}'
        }
    }
}

ALEXA_SUCCESS_RESPONSE = {
    'event': {
        'header': {
            'namespace': '{namespace}',
            'name': '{response_name}',
            'messageId': '{message_id}',
            'correlationToken': '{correlation_token}',
            'payloadVersion': '3'
        },
        'endpoint': {
            'endpointId': '{endpoint_id}'
        },
        'payload': {}
    }
}

ALEXA_ACCEPT_GRANT_RESPONSE = {
    'event': {
        'header': {
            'namespace': 'Alexa.Authorization',
            'name': 'AcceptGrant.Response',
            'messageId': '{message_id}',
            'correlationToken': '{correlation_token}',
            'payloadVersion': '3'
        },
        'payload': {}
    }
}

ALEXA_DISCOVERY_RESPONSE = {
    'event': {
        'header': {
            'namespace': 'Alexa.Discovery',
            'name': 'Discover.Response',
            'messageId': '{message_id}',
            'payloadVersion': '3'
        },
        'payload': {
            'endpoints': '{endpoints}'
        }
    }
}

__all__ = [
    'ALEXA_ERROR_RESPONSE',
    'ALEXA_SUCCESS_RESPONSE',
    'ALEXA_ACCEPT_GRANT_RESPONSE',
    'ALEXA_DISCOVERY_RESPONSE',
]
