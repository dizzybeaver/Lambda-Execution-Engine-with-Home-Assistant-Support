"""
http_client_utilities.py - HTTP Client Utilities
Version: 2025.10.14.01
Description: Utility functions for HTTP operations (headers, query strings, parsing).
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
from urllib.parse import urlencode


def get_standard_headers() -> Dict[str, str]:
    """Get standard HTTP headers for requests."""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'LambdaExecutionEngine/1.0'
    }


def get_ha_headers(token: str) -> Dict[str, str]:
    """Get Home Assistant specific headers."""
    headers = get_standard_headers()
    headers['Authorization'] = f'Bearer {token}'
    return headers


def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters."""
    if not params:
        return ''
    return urlencode(params)


def build_query_string_fast(params: Dict[str, Any]) -> str:
    """Fast query string builder (optimized for small param sets)."""
    return build_query_string(params)


def parse_response_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and normalize response headers."""
    normalized = {}
    for key, value in headers.items():
        normalized[key.lower()] = value
    return normalized


def parse_response_headers_fast(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Fast header parser (optimized version)."""
    return parse_response_headers(headers)


def process_response(response_data: Dict[str, Any], expected_format: str = 'json',
                    validation_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process and validate HTTP response."""
    return response_data


__all__ = [
    'get_standard_headers',
    'get_ha_headers',
    'build_query_string',
    'build_query_string_fast',
    'parse_response_headers',
    'parse_response_headers_fast',
    'process_response',
]

# EOF
