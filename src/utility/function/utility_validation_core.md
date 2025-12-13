# utility_validation_core.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_validation_core.py  
**Module:** Utility core validation

---

## Overview

Core validation exceptions and basic validation implementations. Provides foundational validation primitives used by other validation modules.

**File:** `utility/utility_validation_core.py`  
**Lines:** ~240  
**Pattern:** Core validation functions and exceptions

---

## Exceptions

### ValidationError

**Purpose:** Base validation error  
**Type:** Exception

**Attributes:**
- `field` (str): Field name that failed validation
- `message` (str): Error message
- `value` (Any): Value that failed (optional)

**Usage:**
```python
from utility_validation_core import ValidationError

raise ValidationError('email', 'Invalid format', 'not-an-email')
# Raises: "Validation failed for email: Invalid format"
```

---

### RequiredFieldError

**Purpose:** Required field missing error  
**Type:** ValidationError subclass

**Usage:**
```python
from utility_validation_core import RequiredFieldError

raise RequiredFieldError('name', 'Required field is missing or null')
```

---

### TypeValidationError

**Purpose:** Type validation error  
**Type:** ValidationError subclass

**Usage:**
```python
from utility_validation_core import TypeValidationError

raise TypeValidationError('age', 'Expected int, got str', '30')
```

---

### RangeValidationError

**Purpose:** Range validation error  
**Type:** ValidationError subclass

**Usage:**
```python
from utility_validation_core import RangeValidationError

raise RangeValidationError('age', 'Value 150 above maximum 120', 150)
```

---

## Validation Functions

### validate_required()

**Purpose:** Validate field is present and not None  
**Raises:** RequiredFieldError if None

**Parameters:**
- `value` (Any): Value to validate
- `field_name` (str): Field name

**Usage:**
```python
from utility_validation_core import validate_required

validate_required(name, 'name')  # OK if name is not None
validate_required(None, 'name')  # Raises RequiredFieldError
```

---

### validate_type()

**Purpose:** Validate value is of expected type  
**Raises:** TypeValidationError if wrong type

**Parameters:**
- `value` (Any): Value to validate
- `expected_type` (type or tuple[type]): Expected type(s)
- `field_name` (str): Field name

**Usage:**
```python
from utility_validation_core import validate_type

validate_type(30, int, 'age')  # OK
validate_type('30', int, 'age')  # Raises TypeValidationError

# Multiple types
validate_type(3.14, (int, float), 'value')  # OK
```

---

### validate_range()

**Purpose:** Validate value is within range  
**Raises:** RangeValidationError if out of range

**Parameters:**
- `value` (float): Value to validate
- `min_val` (float, optional): Minimum value
- `max_val` (float, optional): Maximum value
- `field_name` (str, default='value'): Field name

**Usage:**
```python
from utility_validation_core import validate_range

validate_range(50, 0, 100, 'percentage')  # OK
validate_range(150, 0, 100, 'percentage')  # Raises RangeValidationError
validate_range(-5, min_val=0, field_name='count')  # Raises RangeValidationError
```

---

### validate_string_length()

**Purpose:** Validate string length  
**Raises:** ValidationError if length invalid

**Parameters:**
- `value` (str): String to validate
- `min_length` (int, optional): Minimum length
- `max_length` (int, optional): Maximum length
- `field_name` (str, default='string'): Field name

**Usage:**
```python
from utility_validation_core import validate_string_length

validate_string_length('test', 1, 10, 'username')  # OK
validate_string_length('', min_length=1, field_name='name')  # Raises ValidationError
validate_string_length('a' * 200, max_length=100, field_name='bio')  # Raises ValidationError
```

---

### validate_one_of()

**Purpose:** Validate value is one of allowed values  
**Raises:** ValidationError if not in allowed values

**Parameters:**
- `value` (Any): Value to validate
- `allowed_values` (list[Any]): Allowed values
- `field_name` (str, default='value'): Field name

**Usage:**
```python
from utility_validation_core import validate_one_of

validate_one_of('active', ['active', 'inactive', 'pending'], 'status')  # OK
validate_one_of('deleted', ['active', 'inactive'], 'status')  # Raises ValidationError
```

---

### validate_required_fields()

**Purpose:** Validate all required fields present in dict  
**Raises:** RequiredFieldError if any field missing

**Parameters:**
- `data` (dict): Dictionary to validate
- `required_fields` (list[str]): Required field names

**Usage:**
```python
from utility_validation_core import validate_required_fields

data = {'name': 'Alice', 'age': 30}
validate_required_fields(data, ['name', 'age'])  # OK
validate_required_fields(data, ['name', 'email'])  # Raises RequiredFieldError for 'email'
```

---

### validate_dict_schema()

**Purpose:** Validate dict against schema  
**Raises:** Various validation errors based on schema violations

**Parameters:**
- `data` (dict): Dictionary to validate
- `schema` (dict): Schema definition

**Schema Definition:**
```python
{
    'field_name': {
        'required': bool,           # Optional, default False
        'type': type,               # Optional, expected type
        'min': float,               # Optional, minimum value (for numbers)
        'max': float,               # Optional, maximum value (for numbers)
        'min_length': int,          # Optional, minimum length (for strings)
        'max_length': int,          # Optional, maximum length (for strings)
        'allowed': list             # Optional, allowed values
    }
}
```

**Usage:**
```python
from utility_validation_core import validate_dict_schema

schema = {
    'name': {'required': True, 'type': str, 'min_length': 1, 'max_length': 100},
    'age': {'required': True, 'type': int, 'min': 0, 'max': 150},
    'status': {'required': False, 'allowed': ['active', 'inactive']},
    'email': {'required': True, 'type': str}
}

data = {
    'name': 'Alice',
    'age': 30,
    'status': 'active',
    'email': 'alice@example.com'
}

validate_dict_schema(data, schema)  # OK

# Missing required field
data = {'name': 'Alice'}
validate_dict_schema(data, schema)  # Raises RequiredFieldError for 'age'

# Invalid type
data = {'name': 'Alice', 'age': '30'}
validate_dict_schema(data, schema)  # Raises TypeValidationError for 'age'

# Out of range
data = {'name': 'Alice', 'age': 200}
validate_dict_schema(data, schema)  # Raises RangeValidationError for 'age'
```

---

### safe_validate()

**Purpose:** Run validator and return structured result (no exception)  
**Returns:** dict (validation result)

**Parameters:**
- `validator_func` (Callable): Validator function to run
- `*args`: Arguments for validator
- `**kwargs`: Keyword arguments for validator

**Usage:**
```python
from utility_validation_core import safe_validate, validate_required

result = safe_validate(validate_required, None, 'name')
# Result: {
#     'valid': False,
#     'error': 'Validation failed for name: Required field is missing or null',
#     'field': 'name',
#     'message': 'Required field is missing or null'
# }

result = safe_validate(validate_required, 'Alice', 'name')
# Result: {'valid': True, 'error': None}
```

---

### validate_all()

**Purpose:** Run multiple validators and aggregate results  
**Returns:** dict (aggregated results)

**Parameters:**
- `validators` (list[Callable]): List of validator functions

**Usage:**
```python
from utility_validation_core import validate_all, validate_required, validate_type

validators = [
    lambda: validate_required(name, 'name'),
    lambda: validate_type(age, int, 'age'),
    lambda: validate_range(age, 0, 150, 'age')
]

result = validate_all(validators)
# Result: {
#     'all_valid': True,
#     'results': [
#         {'valid': True, 'error': None},
#         {'valid': True, 'error': None},
#         {'valid': True, 'error': None}
#     ],
#     'error_count': 0
# }

# With errors
validators = [
    lambda: validate_required(None, 'name'),
    lambda: validate_type('not-an-int', int, 'age')
]

result = validate_all(validators)
# Result: {
#     'all_valid': False,
#     'results': [
#         {'valid': False, 'error': '...', 'field': 'name', 'message': '...'},
#         {'valid': False, 'error': '...', 'field': 'age', 'message': '...'}
#     ],
#     'error_count': 2
# }
```

---

## Enums

### ValidationOperation

**Purpose:** Validation operations for utility interface  
**Type:** Enum

**Members:**
- VALIDATE_REQUIRED
- VALIDATE_TYPE
- VALIDATE_RANGE
- VALIDATE_STRING_LENGTH
- VALIDATE_ONE_OF
- VALIDATE_REQUIRED_FIELDS
- VALIDATE_DICT_SCHEMA
- SAFE_VALIDATE
- VALIDATE_ALL
- CREATE_CACHE_KEY_VALIDATOR
- CREATE_TTL_VALIDATOR
- CREATE_METRIC_VALIDATOR

---

## Usage Patterns

### Basic Validation
```python
from utility_validation_core import validate_required, validate_type, validate_range

# Validate required
validate_required(name, 'name')

# Validate type
validate_type(age, int, 'age')

# Validate range
validate_range(age, 0, 150, 'age')
```

### Safe Validation (No Exceptions)
```python
from utility_validation_core import safe_validate, validate_required

result = safe_validate(validate_required, value, 'field_name')
if not result['valid']:
    return {'error': result['error']}
```

### Batch Validation
```python
from utility_validation_core import validate_all

validators = [
    lambda: validate_required(name, 'name'),
    lambda: validate_type(age, int, 'age'),
    lambda: validate_range(age, 0, 150, 'age')
]

result = validate_all(validators)
if not result['all_valid']:
    errors = [r for r in result['results'] if not r['valid']]
    return {'errors': errors}
```

### Schema Validation
```python
from utility_validation_core import validate_dict_schema

schema = {
    'name': {'required': True, 'type': str, 'min_length': 1},
    'age': {'required': True, 'type': int, 'min': 0, 'max': 150}
}

try:
    validate_dict_schema(data, schema)
except ValidationError as e:
    return {'error': str(e)}
```

---

## Related Files

- **Advanced:** `utility/utility_validation_advanced.py` (decorators and factories)
- **Operations:** `utility/utility_validation.py` (high-level operations)
- **Core:** `utility/utility_core.py`

---

**END OF DOCUMENTATION**
