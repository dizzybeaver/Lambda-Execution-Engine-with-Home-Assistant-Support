"""
utility_response.py - Response Formatting (Internal)
Version: 2025.10.16.04
Description: Response formatting methods for success/error responses and Lambda responses

SUGA-ISP: Internal module - only accessed via interface_utility.py

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import time
import os
from typing import Dict, Any, Optional
import logging as stdlib_logging

from utility_types import (
    SUCCESS_TEMPLATE,
    SUCCESS_WITH_CORRELATION,
    ERROR_TEMPLATE,
    ERROR_WITH_CODE,
    ERROR_WITH_CORRELATION,
    LAMBDA_RESPONSE,
    DEFAULT_HEADERS_JSON,
    DEFAULT_HEADERS_DICT,
    EMPTY_DATA,
    DEFAULT_USE_TEMPLATES
)

logger = stdlib_logging.getLogger(__name__)

# Runtime configuration
_USE_TEMPLATES = os.environ.get('USE_JSON_TEMPLATES', 'true').lower() == 'true'


# ===== RESPONSE FORMATTING =====

class ResponseFormatter:
    """Response formatting utilities for Lambda and API responses."""
    
    @staticmethod
    def format_response_fast(status_code: int, body: Any, 
                           headers: Optional[str] = None) -> Dict:
        """Fast Lambda response formatting using template."""
        try:
            body_json = body if isinstance(body, str) else json.dumps(body)
            headers_json = headers or DEFAULT_HEADERS_JSON
            
            json_str = LAMBDA_RESPONSE % (status_code, body_json, headers_json)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Fast response formatting error: {str(e)}")
            return ResponseFormatter.format_response(status_code, body, None)
    
    @staticmethod
    def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
        """Format Lambda response (standard path)."""
        if _USE_TEMPLATES and (headers is None or headers == DEFAULT_HEADERS_DICT):
            return ResponseFormatter.format_response_fast(status_code, body)
        
        try:
            return {
                "statusCode": status_code,
                "body": json.dumps(body) if not isinstance(body, str) else body,
                "headers": headers or DEFAULT_HEADERS_DICT
            }
        except Exception as e:
            logger.error(f"Response formatting error: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Response formatting failed"}),
                "headers": DEFAULT_HEADERS_DICT
            }
    
    @staticmethod
    def create_success_response(message: str, data: Any = None, 
                               correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create success response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                data_json = json.dumps(data) if data is not None else EMPTY_DATA
                
                if correlation_id:
                    json_str = SUCCESS_WITH_CORRELATION % (message, timestamp, data_json, correlation_id)
                else:
                    json_str = SUCCESS_TEMPLATE % (message, timestamp, data_json)
                
                return json.loads(json_str)
            
            response = {
                "success": True,
                "message": message,
                "timestamp": int(time.time())
            }
            
            if data is not None:
                response["data"] = data
            
            if correlation_id:
                response["correlation_id"] = correlation_id
            
            return response
            
        except Exception as e:
            logger.error(f"Success response creation error: {str(e)}")
            return {
                "success": True,
                "message": message,
                "timestamp": int(time.time())
            }
    
    @staticmethod
    def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                             details: Any = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create error response with template optimization."""
        try:
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                details_json = json.dumps(details) if details is not None else EMPTY_DATA
                
                if correlation_id:
                    json_str = ERROR_WITH_CORRELATION % (message, error_code, timestamp, details_json, correlation_id)
                else:
                    json_str = ERROR_WITH_CODE % (message, error_code, timestamp, details_json)
                
                return json.loads(json_str)
            
            response = {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": int(time.time())
            }
            
            if details is not None:
                response["details"] = details
            
            if correlation_id:
                response["correlation_id"] = correlation_id
            
            return response
            
        except Exception as e:
            logger.error(f"Error response creation error: {str(e)}")
            return {
                "success": False,
                "error": message,
                "error_code": error_code,
                "timestamp": int(time.time())
            }


# ===== SINGLETON INSTANCE =====

_RESPONSE_FORMATTER = ResponseFormatter()


# ===== PUBLIC FUNCTIONS =====

def format_response_fast(status_code: int, body: Any, 
                        headers: Optional[str] = None) -> Dict:
    """Fast Lambda response formatting using template."""
    return _RESPONSE_FORMATTER.format_response_fast(status_code, body, headers)


def format_response(status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
    """Format Lambda response."""
    return _RESPONSE_FORMATTER.format_response(status_code, body, headers)


def create_success_response(message: str, data: Any = None, 
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create success response."""
    return _RESPONSE_FORMATTER.create_success_response(message, data, correlation_id)


def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR",
                         details: Any = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create error response."""
    return _RESPONSE_FORMATTER.create_error_response(message, error_code, details, correlation_id)


# ===== MODULE EXPORTS =====

__all__ = [
    'ResponseFormatter',
    'format_response_fast',
    'format_response',
    'create_success_response',
    'create_error_response',
]

# EOF
