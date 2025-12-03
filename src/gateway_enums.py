"""
gateway_enums.py - Gateway Interface Enumeration
Version: 1.0.0
Date: 2025-12-03
Description: Shared enum to prevent circular imports

CREATED: Extracted GatewayInterface from gateway_core.py
PURPOSE: Break circular import between gateway_core and gateway_wrappers

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from enum import Enum


class GatewayInterface(Enum):
    """Gateway interface enumeration."""
    CACHE = "cache"
    LOGGING = "logging"
    SECURITY = "security"
    METRICS = "metrics"
    CONFIG = "config"
    SINGLETON = "singleton"
    INITIALIZATION = "initialization"
    HTTP_CLIENT = "http_client"
    WEBSOCKET = "websocket"
    CIRCUIT_BREAKER = "circuit_breaker"
    UTILITY = "utility"
    DEBUG = "debug"


__all__ = ['GatewayInterface']
