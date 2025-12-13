# utility_validation_advanced.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_validation_advanced.py  
**Module:** Utility advanced validation

---

## Overview

Decorators and factory validators for complex validation scenarios. Builds on core validation to provide higher-level validation patterns.

**File:** `utility/utility_validation_advanced.py`  
**Lines:** ~120  
**Pattern:** Validation factories and decorators

---

## Re-Exported Functions

### safe_validate()

**Purpose:** Run validator and return structured result (re-exported from core)  
**Returns:** dict (validation result)

**Parameters:**
- `validator_func` (Callable): Validator function
- `*args`: Validator arguments
- `**kwargs`: Validator keyword arguments

**Usage:**
```python
from utility_validation_advanced import safe_validate, validate_required

result = safe_validate(validate_required, name, 'name')
if not result['valid']:
    return {'error': result['error']}
```

---

### validate_all()

**Purpose:** Run multiple validators and aggregate results (re-exported from core)  
**Returns:** dict (aggregated results)

**Parameters:**
- `validators` (list[Callable]): List of validators

**Usage:**
```python
from utility_validation_advanced import validate_all

result = validate_all([
    lambda: validate_required(name, 'name'),
    lambda: validate_type(age, int, 'age')
])
```

---

## Factory Validators

### create_cache_key_validator()

**Purpose:** Create validator for cache keys  
**Returns:** Callable (validator function)

**Parameters:**
- `min_length` (int, default=1): Minimum key length
- `max_length` (int, default=255): Maximum key length

**Usage:**
```python
from utility_validation_advanced import create_cache_key_validator

validate_cache_key = create_cache_key_validator(min_length=1, max_length=255)

# Use validator
validate_cache_key('user_123')  # OK
validate_cache_key('')  # Raises ValidationError
validate_cache_key('a' * 300)  # Raises ValidationError
```

**Validations:**
- Required (not None)
- Type (str)
- Length (min_length to max_length)

---

### create_ttl_validator()

**Purpose:** Create validator for TTL values  
**Returns:** Callable (validator function)

**Parameters:**
- `min_ttl` (int, default=0): Minimum TTL
- `max_ttl` (int, default=86400): Maximum TTL (24 hours)

**Usage:**
```python
from utility_validation_advanced import create_ttl_validator

validate_ttl = create_ttl_validator(min_ttl=0, max_ttl=86400)

# Use validator
validate_ttl(300)  # OK
validate_ttl(-1)  # Raises RangeValidationError
validate_ttl(100000)  # Raises RangeValidationError
validate_ttl(None)  # OK (None is allowed)
```

**Validations:**
- Type (int) if not None
- Range (min_ttl to max_ttl) if not None

---

### create_metric_validator()

**Purpose:** Create validator for metric recording  
**Returns:** Callable (validator function)

**Usage:**
```python
from utility_validation_advanced import create_metric_validator

validate_metric = create_metric_validator()

# Use validator
validate_metric('cache_hits', 100)  # OK
validate_metric('cache_hits', 'not-a-number')  # Raises TypeValidationError
validate_metric('', 100)  # Raises ValidationError (name too short)
validate_metric('a' * 300, 100)  # Raises ValidationError (name too long)
```

**Validations:**
- name: Required, str, 1-255 characters
- value: Required, int or float

---

## Decorators

### validate_params()

**Purpose:** Decorator to validate function parameters  
**Returns:** Decorator function

**Parameters:**
- `**validators`: Keyword arguments mapping parameter names to validators

**Usage:**
```python
from utility_validation_advanced import validate_params
from utility_validation_core import validate_required, validate_range

@validate_params(
    name=lambda x: validate_required(x, 'name'),
    age=lambda x: validate_range(x, 0, 150, 'age')
)
def create_user(name, age):
    return {'name': name, 'age': age}

# Valid call
user = create_user('Alice', 30)

# Invalid call (missing name)
user = create_user(None, 30)  # Raises RequiredFieldError

# Invalid call (age out of range)
user = create_user('Alice', 200)  # Raises RangeValidationError
```

**Features:**
- Validates parameters before function execution
- Uses function signature to bind arguments
- Applies defaults before validation
- Raises original ValidationError on failure

---

### validate_return_type()

**Purpose:** Decorator to validate function return type  
**Returns:** Decorator function

**Parameters:**
- `expected_type` (type): Expected return type

**Usage:**
```python
from utility_validation_advanced import validate_return_type

@validate_return_type(dict)
def get_config():
    return {"key": "value"}

# Valid return
config = get_config()  # OK

@validate_return_type(dict)
def broken_config():
    return "not a dict"

# Invalid return
config = broken_config()  # Raises TypeValidationError
```

**Features:**
- Validates return value after function execution
- Raises TypeValidationError if type mismatch
- Includes expected and actual types in error

---

## Usage Patterns

### Factory Pattern
```python
from utility_validation_advanced import create_cache_key_validator, create_ttl_validator

# Create validators
validate_key = create_cache_key_validator(min_length=1, max_length=100)
validate_ttl = create_ttl_validator(min_ttl=60, max_ttl=3600)

# Use in function
def cache_set(key, value, ttl=300):
    validate_key(key)
    validate_ttl(ttl)
    # Set cache...
```

### Parameter Validation Decorator
```python
from utility_validation_advanced import validate_params
from utility_validation_core import validate_required, validate_type, validate_string_length

@validate_params(
    user_id=lambda x: validate_required(x, 'user_id'),
    name=lambda x: validate_string_length(x, 1, 100, 'name'),
    age=lambda x: validate_type(x, int, 'age')
)
def update_user(user_id, name, age):
    # Function implementation
    pass
```

### Return Type Validation
```python
from utility_validation_advanced import validate_return_type

@validate_return_type(dict)
def get_user_data(user_id):
    # Must return dict
    return {'user_id': user_id, 'name': 'Alice'}

@validate_return_type(list)
def get_users():
    # Must return list
    return [{'id': '1'}, {'id': '2'}]
```

### Combined Validation
```python
from utility_validation_advanced import validate_params, validate_return_type
from utility_validation_core import validate_required, validate_range

@validate_params(
    name=lambda x: validate_required(x, 'name'),
    age=lambda x: validate_range(x, 0, 150, 'age')
)
@validate_return_type(dict)
def create_user(name, age):
    return {'name': name, 'age': age}
```

---

## Advanced Examples

### Custom Factory Validator
```python
from utility_validation_core import validate_required, validate_type, validate_string_length

def create_email_validator():
    """Create validator for email addresses."""
    def validator(email: str) -> None:
        validate_required(email, 'email')
        validate_type(email, str, 'email')
        validate_string_length(email, 5, 255, 'email')
        
        if '@' not in email:
            raise ValidationError('email', 'Must contain @', email)
        
        parts = email.split('@')
        if len(parts) != 2:
            raise ValidationError('email', 'Invalid email format', email)
        
        if not parts[0] or not parts[1]:
            raise ValidationError('email', 'Invalid email format', email)
    
    return validator

# Use custom validator
validate_email = create_email_validator()
validate_email('alice@example.com')  # OK
validate_email('invalid')  # Raises ValidationError
```

### Chained Decorators
```python
from utility_validation_advanced import validate_params, validate_return_type
from utility_validation_core import validate_required, validate_range

@validate_return_type(dict)
@validate_params(
    amount=lambda x: validate_range(x, 0.01, 10000, 'amount'),
    currency=lambda x: validate_required(x, 'currency')
)
def create_payment(amount, currency):
    return {
        'amount': amount,
        'currency': currency,
        'status': 'pending'
    }
```

---

## Related Files

- **Core:** `utility/utility_validation_core.py` (core validators)
- **Operations:** `utility/utility_validation.py` (high-level operations)
- **Implementation:** `utility/utility_core.py`

---

**END OF DOCUMENTATION**
