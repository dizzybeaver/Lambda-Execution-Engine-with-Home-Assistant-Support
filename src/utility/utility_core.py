"""
Utility Core - Common Utility Functions
Version: 2025.09.29.01
Daily Revision: 001
"""

import json
from typing import Any, Dict, Optional

class UtilityCore:
    """Common utility functions."""
    
    def format_response(self, status_code: int, body: Any, headers: Optional[Dict] = None) -> Dict:
        """Format Lambda response."""
        response = {
            'statusCode': status_code,
            'body': json.dumps(body) if not isinstance(body, str) else body,
            'headers': headers or {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
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

def _execute_format_response_implementation(status_code: int, body: Any, headers: Optional[Dict] = None, **kwargs) -> Dict:
    """Execute response formatting."""
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
