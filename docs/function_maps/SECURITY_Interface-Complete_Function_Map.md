# SECURITY Interface - Complete Function Map
**Interface:** GatewayInterface.SECURITY  
**Category:** Security & Validation  
**Core File:** security_core.py

---

## Call Hierarchy Map

```
gateway.execute_operation(GatewayInterface.SECURITY, operation)
    ├─→ gateway.validate_request(request_data)    [Gateway Function]
    ├─→ gateway.validate_token(token)             [Gateway Function]
    ├─→ gateway.encrypt_data(data)                [Gateway Function]
    └─→ gateway.decrypt_data(encrypted_data)      [Gateway Function]
            ↓
    [Routes to security_core Gateway Implementations]
            ↓
    ├─→ _execute_validate_request_implementation(request)
    ├─→ _execute_validate_token_implementation(token)
    ├─→ _execute_encrypt_data_implementation(data, key)
    └─→ _execute_decrypt_data_implementation(data, key)
            ↓
    [Delegates to Singleton Security Manager]
            ↓
    _MANAGER.execute_security_operation(SecurityOperation, ...)
            ↓
    SecurityCore methods
            ↓
    ├─→ SecurityCore.validate_request()
    ├─→ SecurityCore.validate_token()
    ├─→ SecurityCore.encrypt()
    ├─→ SecurityCore.decrypt()
    ├─→ SecurityCore.validate_string()
    ├─→ SecurityCore.sanitize_input()
    └─→ SecurityCore.get_stats()
```

---

## File: gateway.py
**Functions:** 4 gateway convenience wrappers

### validate_request(request_data: Dict[str, Any]) -> bool
- **Category:** Gateway Function - Security Validation
- **Map:** `User → gateway.validate_request() → execute_operation(SECURITY, 'validate_request') → _execute_validate_request_implementation() → _MANAGER.validate_request()`
- **Description:** Validate incoming request structure and content

### validate_token(token: str) -> bool
- **Category:** Gateway Function - Security Validation
- **Map:** `User → gateway.validate_token() → execute_operation(SECURITY, 'validate_token') → _execute_validate_token_implementation() → _MANAGER.validate_token()`
- **Description:** Validate authentication token format and integrity

### encrypt_data(data: str) -> str
- **Category:** Gateway Function - Data Protection
- **Map:** `User → gateway.encrypt_data() → execute_operation(SECURITY, 'encrypt') → _execute_encrypt_data_implementation() → _MANAGER.encrypt()`
- **Description:** Encrypt sensitive data

### decrypt_data(encrypted_data: str) -> str
- **Category:** Gateway Function - Data Protection
- **Map:** `User → gateway.decrypt_data() → execute_operation(SECURITY, 'decrypt') → _execute_decrypt_data_implementation() → _MANAGER.decrypt()`
- **Description:** Decrypt encrypted data

---

## File: security_core.py

### Gateway Implementation Functions (4)

#### _execute_validate_request_implementation(request: Dict[str, Any]) -> bool
- **Category:** Gateway Implementation - Security Validation
- **Map:** `execute_operation() → _execute_validate_request_implementation() → _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_REQUEST)`
- **Description:** Gateway implementation for request validation
- **Private:** Yes

#### _execute_validate_token_implementation(token: str) -> bool
- **Category:** Gateway Implementation - Security Validation
- **Map:** `execute_operation() → _execute_validate_token_implementation() → _MANAGER.execute_security_operation(SecurityOperation.VALIDATE_TOKEN)`
- **Description:** Gateway implementation for token validation
- **Private:** Yes

#### _execute_encrypt_data_implementation(data: str, key: str) -> str
- **Category:** Gateway Implementation - Data Protection
- **Map:** `execute_operation() → _execute_encrypt_data_implementation() → _MANAGER.execute_security_operation(SecurityOperation.ENCRYPT)`
- **Description:** Gateway implementation for encryption
- **Private:** Yes

#### _execute_decrypt_data_implementation(data: str, key: str) -> str
- **Category:** Gateway Implementation - Data Protection
- **Map:** `execute_operation() → _execute_decrypt_data_implementation() → _MANAGER.execute_security_operation(SecurityOperation.DECRYPT)`
- **Description:** Gateway implementation for decryption
- **Private:** Yes

---

### Public Interface Functions (2)

#### validate_string_input(value: str, min_length: int, max_length: int) -> bool
- **Category:** Public Function - Input Validation
- **Map:** `Direct call → _MANAGER.validate_string()`
- **Description:** Validate string input against length constraints
- **Public:** Yes

#### get_security_stats() -> Dict[str, Any]
- **Category:** Public Function - Observability
- **Map:** `Direct call → _MANAGER.get_stats()`
- **Description:** Get security validation statistics
- **Public:** Yes

---

### Core Class: SecurityCore

#### Constructor: __init__()
- **Category:** Initialization - Security
- **Description:** Initialize security manager with validation patterns and statistics
- **Initializes:**
  - `self._validation_patterns` - Dict of ValidationPattern regex
  - `self._stats` - Security operation statistics

#### execute_security_operation(operation: SecurityOperation, *args, **kwargs)
- **Category:** Generic Operation Dispatch - Security
- **Map:** `execute_security_operation() → getattr(operation.value) → validate_*/encrypt/decrypt()`
- **Description:** Universal security operation dispatcher
- **Sub-functions:**
  - Dynamically routes to appropriate security method
  - Exception handling with fallback responses

#### validate_request(request: Dict[str, Any]) -> bool
- **Category:** Core Operation - Request Validation
- **Map:** `validate_request() → validate structure → sanitize → update _stats`
- **Description:** Validate request has required fields and valid structure
- **Validation Steps:**
  1. Check if dict type
  2. Validate required fields exist
  3. Check field types
  4. Sanitize values
- **Sub-functions:**
  - `self.sanitize_input()` - Clean dangerous content
  - Updates `self._stats['validations']`
  - Updates `self._stats['successful_validations']` or `self._stats['failed_validations']`

#### validate_token(token: str) -> bool
- **Category:** Core Operation - Token Validation
- **Map:** `validate_token() → check format → validate pattern → update _stats`
- **Description:** Validate token format and structure
- **Validation Steps:**
  1. Check string type and non-empty
  2. Check length constraints (min/max)
  3. Regex pattern matching
  4. Character set validation
- **Sub-functions:**
  - Pattern matching using `self._validation_patterns[ValidationPattern.TOKEN]`
  - Updates `self._stats['validations']`
  - Updates success/fail counters

#### encrypt(data: str, key: str) -> str
- **Category:** Core Operation - Encryption
- **Map:** `encrypt() → [encryption logic] → update _stats`
- **Description:** Encrypt data using provided key
- **Sub-functions:**
  - Basic encryption implementation (placeholder)
  - Updates `self._stats['encryptions']`
- **Note:** Production implementation would use proper crypto library

#### decrypt(data: str, key: str) -> str
- **Category:** Core Operation - Decryption
- **Map:** `decrypt() → [decryption logic] → update _stats`
- **Description:** Decrypt encrypted data
- **Sub-functions:**
  - Basic decryption implementation (placeholder)
  - Updates `self._stats['encryptions']` (shared counter)

#### validate_string(value: str, min_length: int, max_length: int) -> bool
- **Category:** Validation - Input Validation
- **Map:** `validate_string() → check type → check length → sanitize`
- **Description:** Validate string meets length requirements
- **Validation Steps:**
  1. Check string type
  2. Check length >= min_length
  3. Check length <= max_length
  4. Optional: Check for dangerous patterns
- **Returns:** bool

#### sanitize_input(data: Any) -> Any
- **Category:** Data Protection - XSS Prevention
- **Map:** `sanitize_input() → [recursive sanitization] → return cleaned`
- **Description:** Recursively sanitize data to prevent XSS and injection
- **Sanitization Rules:**
  - String: Replace `<` with `&lt;`, `>` with `&gt;`
  - String: Replace `"` with `&quot;`, `'` with `&#x27;`
  - Dict: Recursively sanitize all values
  - List: Recursively sanitize all items
  - Other types: Return as-is
- **Sub-functions:**
  - Recursive calls for nested structures

#### get_stats() -> Dict[str, Any]
- **Category:** Observability - Statistics
- **Map:** `get_stats() → calculate rates → return dict`
- **Description:** Get comprehensive security statistics
- **Calculations:**
  - `validation_success_rate = (successful / total) * 100`
- **Returns:** Dict with validation counts, rates, encryption counts

---

## Enums

### SecurityOperation
- **VALIDATE_REQUEST** = "validate_request"
- **VALIDATE_TOKEN** = "validate_token"
- **ENCRYPT** = "encrypt"
- **DECRYPT** = "decrypt"

### ValidationPattern
Pre-compiled regex patterns for validation:
- **TOKEN** - Token format pattern
- **EMAIL** - Email validation pattern
- **URL** - URL validation pattern
- **ALPHANUMERIC** - Alphanumeric only pattern

---

## Module Variables

### _MANAGER
- **Type:** SecurityCore
- **Category:** Singleton Instance
- **Description:** Global security manager
- **Initialization:** `_MANAGER = SecurityCore()`

---

## Function Categories Summary

### Security Validation (Primary)
- Request structure validation
- Token format validation
- String validation with constraints

### Data Protection
- Encryption/Decryption operations
- Input sanitization
- XSS prevention

### Input Validation
- String length validation
- Pattern matching
- Type checking

### Observability
- Validation statistics
- Success/failure tracking
- Operation counting

---

## Usage Examples

### Request Validation
```python
from gateway import validate_request

request = {
    'action': 'turn_on',
    'entity_id': 'light.living_room'
}

if validate_request(request):
    # Process request
    pass
```

### Token Validation
```python
from gateway import validate_token

token = "Bearer abc123def456"
if validate_token(token):
    # Allow access
    pass
```

### Data Sanitization
```python
from security_core import _MANAGER

dirty_data = {
    'user_input': '<script>alert("xss")</script>',
    'nested': {'value': '<b>test</b>'}
}

clean_data = _MANAGER.sanitize_input(dirty_data)
# Result: {
#   'user_input': '&lt;script&gt;alert("xss")&lt;/script&gt;',
#   'nested': {'value': '&lt;b&gt;test&lt;/b&gt;'}
# }
```

---

**End of SECURITY Interface Function Map**
