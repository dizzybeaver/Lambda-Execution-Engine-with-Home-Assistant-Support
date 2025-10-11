"""
http_client_transformers.py
Version: 2025.10.02.01
Description: Response transformation and validation utilities

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

from typing import Dict, Any, List, Callable, Optional, Union
import json


class ResponseValidator:
    """Validates response structure and content."""
    
    @staticmethod
    def validate_structure(data: Any, schema: Dict[str, Any]) -> bool:
        """Validate response data against schema."""
        if not isinstance(data, dict):
            return False
        
        for field, field_type in schema.get('required_fields', {}).items():
            if field not in data:
                return False
            
            if not isinstance(data[field], field_type):
                return False
        
        return True
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], fields: List[str]) -> bool:
        """Check if all required fields are present."""
        return all(field in data for field in fields)
    
    @staticmethod
    def validate_data_types(data: Dict[str, Any], type_map: Dict[str, type]) -> bool:
        """Validate data types match expected types."""
        for field, expected_type in type_map.items():
            if field in data and not isinstance(data[field], expected_type):
                return False
        return True
    
    @staticmethod
    def validate_value_ranges(data: Dict[str, Any], ranges: Dict[str, tuple]) -> bool:
        """Validate numeric values are within specified ranges."""
        for field, (min_val, max_val) in ranges.items():
            if field in data:
                value = data[field]
                if not (min_val <= value <= max_val):
                    return False
        return True


class ResponseTransformer:
    """Transforms response data using various strategies."""
    
    @staticmethod
    def flatten(data: Dict[str, Any], separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary structure."""
        def _flatten_recursive(obj, parent_key=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{separator}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(_flatten_recursive(v, new_key).items())
                    elif isinstance(v, list):
                        for i, item in enumerate(v):
                            items.extend(_flatten_recursive(item, f"{new_key}[{i}]").items())
                    else:
                        items.append((new_key, v))
            return dict(items)
        
        return _flatten_recursive(data)
    
    @staticmethod
    def extract(data: Dict[str, Any], paths: List[str]) -> Dict[str, Any]:
        """Extract specific fields from nested structure."""
        result = {}
        
        for path in paths:
            parts = path.split('.')
            current = data
            
            try:
                for part in parts:
                    if '[' in part:
                        field, index = part.split('[')
                        index = int(index.rstrip(']'))
                        current = current[field][index]
                    else:
                        current = current[part]
                
                result[path] = current
            except (KeyError, IndexError, TypeError):
                result[path] = None
        
        return result
    
    @staticmethod
    def map_fields(data: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
        """Rename fields according to mapping."""
        result = {}
        
        for old_name, new_name in field_map.items():
            if old_name in data:
                result[new_name] = data[old_name]
        
        for key, value in data.items():
            if key not in field_map:
                result[key] = value
        
        return result
    
    @staticmethod
    def filter_fields(data: Dict[str, Any], include: Optional[List[str]] = None,
                     exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Filter fields by inclusion or exclusion list."""
        if include:
            return {k: v for k, v in data.items() if k in include}
        
        if exclude:
            return {k: v for k, v in data.items() if k not in exclude}
        
        return data
    
    @staticmethod
    def transform_values(data: Dict[str, Any], 
                        transformers: Dict[str, Callable]) -> Dict[str, Any]:
        """Apply transformation functions to specific fields."""
        result = data.copy()
        
        for field, transformer in transformers.items():
            if field in result:
                try:
                    result[field] = transformer(result[field])
                except Exception:
                    pass
        
        return result
    
    @staticmethod
    def normalize(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data according to schema."""
        result = {}
        
        for field, config in schema.items():
            if field in data:
                value = data[field]
                
                if 'type' in config:
                    try:
                        value = config['type'](value)
                    except:
                        value = config.get('default')
                
                if 'min' in config and value < config['min']:
                    value = config['min']
                
                if 'max' in config and value > config['max']:
                    value = config['max']
                
                result[field] = value
        
        return result


class TransformationPipeline:
    """Chains multiple transformations with caching support."""
    
    def __init__(self):
        self._transformations: List[tuple] = []
        self._cache_results = True
    
    def add_validation(self, validator: Callable, error_handler: Optional[Callable] = None):
        """Add validation step to pipeline."""
        self._transformations.append(('validate', validator, error_handler))
        return self
    
    def add_transformation(self, transformer: Callable, cache_key: Optional[str] = None):
        """Add transformation step to pipeline."""
        self._transformations.append(('transform', transformer, cache_key))
        return self
    
    def execute(self, data: Any, cache_pipeline: bool = True) -> Dict[str, Any]:
        """Execute transformation pipeline."""
        result = data
        pipeline_cache_key = self._generate_pipeline_cache_key()
        
        if cache_pipeline and pipeline_cache_key:
            from gateway import cache_get
            cached = cache_get(pipeline_cache_key)
            if cached:
                return cached
        
        for step_type, operation, metadata in self._transformations:
            try:
                if step_type == 'validate':
                    validator = operation
                    error_handler = metadata
                    
                    if not validator(result):
                        if error_handler:
                            result = error_handler(result)
                        else:
                            return {
                                'success': False,
                                'error': 'Validation failed',
                                'data': result
                            }
                
                elif step_type == 'transform':
                    transformer = operation
                    cache_key = metadata
                    
                    if cache_key:
                        from gateway import cache_get, cache_set
                        cached_transform = cache_get(cache_key)
                        if cached_transform:
                            result = cached_transform
                            continue
                    
                    result = transformer(result)
                    
                    if cache_key:
                        from gateway import cache_set
                        cache_set(cache_key, result, ttl=300)
            
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Pipeline step failed: {str(e)}',
                    'data': result
                }
        
        if cache_pipeline and pipeline_cache_key:
            from gateway import cache_set
            cache_set(pipeline_cache_key, result, ttl=300)
        
        return {
            'success': True,
            'data': result
        }
    
    def _generate_pipeline_cache_key(self) -> Optional[str]:
        """Generate cache key for entire pipeline."""
        if not self._cache_results:
            return None
        
        step_keys = []
        for step_type, operation, metadata in self._transformations:
            if hasattr(operation, '__name__'):
                step_keys.append(operation.__name__)
        
        if step_keys:
            return f"transform_pipeline_{'_'.join(step_keys)}"
        
        return None


def create_common_transformers() -> Dict[str, Callable]:
    """Create dictionary of common transformation functions."""
    transformer = ResponseTransformer()
    
    return {
        'flatten': transformer.flatten,
        'extract': transformer.extract,
        'map': transformer.map_fields,
        'filter': transformer.filter_fields,
        'transform_values': transformer.transform_values,
        'normalize': transformer.normalize
    }


def create_validator() -> ResponseValidator:
    """Create response validator instance."""
    return ResponseValidator()


def create_transformer() -> ResponseTransformer:
    """Create response transformer instance."""
    return ResponseTransformer()


def create_pipeline() -> TransformationPipeline:
    """Create transformation pipeline instance."""
    return TransformationPipeline()


# EOF
