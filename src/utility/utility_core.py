"""
utility_core.py
Version: 2025.10.02.01
Description: Common Utility Functions with Template Optimization

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

import json
from typing import Any, Dict, Optional

# ===== LAMBDA RESPONSE TEMPLATES (Phase 2 Optimization) =====

_LAMBDA_RESPONSE = '{"statusCode":%d,"body":%s,"headers":%s}'
_DEFAULT_HEADERS = '{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"}'
_DEFAULT_HEADERS_DICT = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
}


class UtilityCore:
    """Common utility functions with template optimization."""
    
    def format_response_fast(self, status_code: int, body: Any, 
                           headers: Optional[str] = None) -> Dict:
        """Fast Lambda response formatting using template."""
        try:
            body_json = body if isinstance(body, str) else json.dumps(body)
            headers_json = headers or _DEFAULT_HEADERS
            
            json_str = _LAMBDA_RESPONSE % (status_code, body_json, headers_json)
            return json.loads(json_str)
        except Exception:
            return self.format_response(status_code, body, None)
    
    def format_response(self, status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
        """Format Lambda response (legacy)."""
        response = {
            'statusCode': status_code,
            'body': json.dumps(body) if not isinstance(body, str) else body,
            'headers': headers or _DEFAULT_HEADERS_DICT
        }
        return response
    
    def parse_json(self, data: str) -> Dict:
        """Parse JSON string safely."""
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def deep_merge(self, dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def safe_get(self, dictionary: Dict, key_path: str, default: Any = None) -> Any:
        """Safely get nested dictionary value using dot notation."""
        keys = key_path.split('.')
        value = dictionary
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


_UTILITY = UtilityCore()


def _execute_format_response_implementation(status_code: int, body: Any, 
                                          headers: Optional[Dict] = None, 
                                          use_template: bool = True,
                                          **kwargs) -> Dict:
    """Execute response formatting."""
    if use_template and headers is None:
        return _UTILITY.format_response_fast(status_code, body)
    else:
        return _UTILITY.format_response(status_code, body, headers)


def _execute_parse_json_implementation(data: str, **kwargs) -> Dict:
    """Execute JSON parsing."""
    return _UTILITY.parse_json(data)


def _execute_deep_merge_implementation(dict1: Dict, dict2: Dict, **kwargs) -> Dict:
    """Execute deep merge."""
    return _UTILITY.deep_merge(dict1, dict2)


def _execute_safe_get_implementation(dictionary: Dict, key_path: str, default: Any = None, **kwargs) -> Any:
    """Execute safe get."""
    return _UTILITY.safe_get(dictionary, key_path, default)

#EOF
