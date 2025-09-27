"""
lambda.py - Lambda/Alexa Response Operations Primary Gateway Interface
Version: 2025.09.27.01
Description: Ultra-pure gateway for Lambda/Alexa operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE
- Function declarations ONLY - no implementation code
- Pure delegation to lambda_core.py
- External access point for Lambda/Alexa operations
- Ultra-optimized for 128MB Lambda constraint

PRIMARY GATEWAY FUNCTIONS:
- alexa_lambda_handler() - Main Alexa skill handler
- create_alexa_response() - Response creation and formatting
- lambda_handler_with_gateway() - Gateway-aware Lambda handler
- get_lambda_status() - Lambda status and health monitoring

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

from typing import Dict, Any, Callable
from enum import Enum

# Ultra-pure core delegation import
from .lambda_core import generic_lambda_operation, LambdaOperation, AlexaResponseType

# ===== SECTION 1: PRIMARY GATEWAY INTERFACE FUNCTIONS =====

def alexa_lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Primary gateway function for Alexa skill Lambda handler.
    Pure delegation to lambda_core implementation.
    """
    return generic_lambda_operation(
        LambdaOperation.ALEXA_HANDLER,
        event=event,
        context=context
    )

def create_alexa_response(response_type: AlexaResponseType, **kwargs) -> Dict[str, Any]:
    """
    Primary gateway function for Alexa response creation.
    Pure delegation to lambda_core implementation.
    """
    return generic_lambda_operation(
        LambdaOperation.CREATE_ALEXA_RESPONSE,
        response_type=response_type,
        **kwargs
    )

def lambda_handler_with_gateway(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Primary gateway function for gateway-aware Lambda handler.
    Pure delegation to lambda_core implementation.
    """
    return generic_lambda_operation(
        LambdaOperation.GATEWAY_HANDLER,
        event=event,
        context=context
    )

def get_lambda_status() -> Dict[str, Any]:
    """
    Primary gateway function for Lambda status monitoring.
    Pure delegation to lambda_core implementation.
    """
    return generic_lambda_operation(LambdaOperation.GET_STATUS)

# ===== SECTION 2: MODULE EXPORTS =====

__all__ = [
    'alexa_lambda_handler',
    'create_alexa_response', 
    'lambda_handler_with_gateway',
    'get_lambda_status'
]

# EOF
