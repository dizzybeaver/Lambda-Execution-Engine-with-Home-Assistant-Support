"""
gateway_updates.py - Gateway Operations Registry Updates
Version: 2025.10.14.01
Description: Required changes to gateway.py _OPERATION_REGISTRY

INSTRUCTIONS:
Update gateway.py _OPERATION_REGISTRY with these changes:

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0
"""

# ===== CHANGES TO gateway.py _OPERATION_REGISTRY =====

# REPLACE THESE LINES:
# OLD:
#     (GatewayInterface.HTTP_CLIENT, 'request'): ('http_client_core', 'http_request_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'get'): ('http_client_core', 'http_get_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'post'): ('http_client_core', 'http_post_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'put'): ('http_client_core', 'http_put_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'delete'): ('http_client_core', 'http_delete_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'get_state'): ('http_client_core', 'get_state_implementation'),
#     (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('http_client_core', 'reset_state_implementation'),

# NEW:
_OPERATION_REGISTRY_HTTP_CLIENT = {
    (GatewayInterface.HTTP_CLIENT, 'request'): ('http_client', 'http_request'),
    (GatewayInterface.HTTP_CLIENT, 'get'): ('http_client', 'http_get'),
    (GatewayInterface.HTTP_CLIENT, 'post'): ('http_client', 'http_post'),
    (GatewayInterface.HTTP_CLIENT, 'put'): ('http_client', 'http_put'),
    (GatewayInterface.HTTP_CLIENT, 'delete'): ('http_client', 'http_delete'),
    (GatewayInterface.HTTP_CLIENT, 'get_state'): ('http_client', 'get_state'),
    (GatewayInterface.HTTP_CLIENT, 'reset_state'): ('http_client', 'reset_state'),
}

# REPLACE THESE LINES:
# OLD:
#     (GatewayInterface.WEBSOCKET, 'connect'): ('websocket_core', 'websocket_connect_implementation'),
#     (GatewayInterface.WEBSOCKET, 'send'): ('websocket_core', 'websocket_send_implementation'),
#     (GatewayInterface.WEBSOCKET, 'receive'): ('websocket_core', 'websocket_receive_implementation'),
#     (GatewayInterface.WEBSOCKET, 'close'): ('websocket_core', 'websocket_close_implementation'),
#     (GatewayInterface.WEBSOCKET, 'request'): ('websocket_core', 'websocket_request_implementation'),

# NEW:
_OPERATION_REGISTRY_WEBSOCKET = {
    (GatewayInterface.WEBSOCKET, 'connect'): ('websocket', 'websocket_connect'),
    (GatewayInterface.WEBSOCKET, 'send'): ('websocket', 'websocket_send'),
    (GatewayInterface.WEBSOCKET, 'receive'): ('websocket', 'websocket_receive'),
    (GatewayInterface.WEBSOCKET, 'close'): ('websocket', 'websocket_close'),
    (GatewayInterface.WEBSOCKET, 'request'): ('websocket', 'websocket_request'),
}

# ===== SUMMARY OF CHANGES =====
"""
HTTP_CLIENT operations now call http_client.py interface (was http_client_core.py)
WEBSOCKET operations now call websocket.py interface (was websocket_core.py)

This provides stable interface layer - internal refactoring won't affect gateway.
"""

# EOF
