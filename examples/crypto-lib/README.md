# Example 2: Crypto Library

An intermediate example demonstrating option types, error handling, and real-world cryptography patterns.

## Overview

This example shows:
- Option types (`string option`)
- Error handling with None/Some
- Real-world use case (encryption)
- Key management

## Key Concepts

### Option Types in OCaml

```ocaml
val find_key : string -> string option
(* Returns Some(key) if found, None if not found *)
```

### Mapping to Python

```python
def find_key(name: str) -> Optional[str]:
    # Returns key or None
```

## Project Structure

```
crypto-lib/
├── README.md
├── polyglot.toml
├── src/
│   ├── crypto.mli         # Interface with option types
│   └── crypto.ml          # Implementation
├── generated/
└── example.py             # Demonstrates option handling
```

## OCaml Interface

**File: `src/crypto.mli`**

```ocaml
(** Encrypt data with a key *)
val encrypt : string -> string -> string

(** Decrypt data with a key. Returns None if decryption fails. *)
val decrypt : string -> string -> string option

(** Find a stored key by name. Returns None if not found. *)
val find_key : string -> string option

(** Verify data signature. Returns None if invalid. *)
val verify_signature : string -> string -> bool option

(** Hash data to a fixed-length string *)
val hash : string -> string
```

## Configuration

**File: `polyglot.toml`**

```toml
[project]
name = "crypto"
version = "0.1.0"
description = "Cryptography library with option types"

[bindings]
source_files = ["src/crypto.mli"]
output_dir = "generated"

[targets.python]
enabled = true
```

## Python Usage

**File: `example.py`**

```python
#!/usr/bin/env python3
"""Example demonstrating option type handling."""

import sys
sys.path.insert(0, 'generated')

from crypto_py import encrypt, decrypt, find_key, verify_signature, hash
from typing import Optional

# Example 1: Basic encryption (always succeeds)
plaintext = "Hello, World!"
key = "my-secret-key"

ciphertext = encrypt(plaintext, key)
print(f"Encrypted: {ciphertext}")

# Example 2: Decryption with option type
# decrypt returns Optional[str] - could be None
decrypted = decrypt(ciphertext, key)

if decrypted is not None:
    print(f"Decrypted: {decrypted}")
    assert decrypted == plaintext
else:
    print("Decryption failed!")

# Example 3: Wrong key returns None
wrong_decrypted = decrypt(ciphertext, "wrong-key")
if wrong_decrypted is None:
    print("Decryption with wrong key returned None (expected)")

# Example 4: Find key (may not exist)
def load_key(name: str) -> str:
    """Load a key, using default if not found."""
    key = find_key(name)
    if key is not None:
        return key
    else:
        print(f"Key '{name}' not found, using default")
        return "default-key"

production_key = load_key("production")
dev_key = load_key("development")

# Example 5: Signature verification
data = "important message"
signature = "abc123"

is_valid = verify_signature(data, signature)

if is_valid is None:
    print("Signature format invalid")
elif is_valid:
    print("Signature valid!")
else:
    print("Signature invalid!")

# Example 6: Hashing (always returns a value)
hash_value = hash(plaintext)
print(f"Hash: {hash_value}")

# Idiomatic Python patterns with options
def safe_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt with fallback to original if it fails."""
    result = decrypt(ciphertext, key)
    return result if result is not None else ciphertext

# Using walrus operator (Python 3.8+)
if (key := find_key("api-key")) is not None:
    print(f"Found API key: {key[:10]}...")
else:
    print("API key not configured")
```

## Generated Code

### Type Description

```ocaml
(* generated/type_description.ml *)
open Ctypes

let string = Ctypes.string
let string_opt = Ctypes.(ptr string)  (* option represented as pointer *)
let bool_opt = Ctypes.(ptr bool)
```

### Function Description

```ocaml
(* generated/function_description.ml *)
open Ctypes

let encrypt = foreign "ml_encrypt"
  (string @-> string @-> returning string)

let decrypt = foreign "ml_decrypt"
  (string @-> string @-> returning string_opt)

let find_key = foreign "ml_find_key"
  (string @-> returning string_opt)

let verify_signature = foreign "ml_verify_signature"
  (string @-> string @-> returning bool_opt)

let hash = foreign "ml_hash"
  (string @-> returning string)
```

### Python Wrapper

```python
# generated/crypto_py.py
import ctypes
from pathlib import Path
from typing import Optional

_lib = ctypes.CDLL(str(Path(__file__).parent / "crypto.so"))

# encrypt: always returns a value
_lib.ml_encrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_lib.ml_encrypt.restype = ctypes.c_char_p

def encrypt(data: str, key: str) -> str:
    """Encrypt data with a key."""
    result = _lib.ml_encrypt(data.encode('utf-8'), key.encode('utf-8'))
    return result.decode('utf-8')

# decrypt: returns Optional[str]
_lib.ml_decrypt.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_lib.ml_decrypt.restype = ctypes.c_char_p

def decrypt(ciphertext: str, key: str) -> Optional[str]:
    """Decrypt data. Returns None if decryption fails."""
    result = _lib.ml_decrypt(ciphertext.encode('utf-8'), key.encode('utf-8'))
    if result is None:
        return None
    return result.decode('utf-8')

# find_key: returns Optional[str]
_lib.ml_find_key.argtypes = [ctypes.c_char_p]
_lib.ml_find_key.restype = ctypes.c_char_p

def find_key(name: str) -> Optional[str]:
    """Find a stored key. Returns None if not found."""
    result = _lib.ml_find_key(name.encode('utf-8'))
    if result is None:
        return None
    return result.decode('utf-8')

# verify_signature: returns Optional[bool]
_lib.ml_verify_signature.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
_lib.ml_verify_signature.restype = ctypes.POINTER(ctypes.c_bool)

def verify_signature(data: str, signature: str) -> Optional[bool]:
    """Verify signature. Returns None if format invalid, True/False otherwise."""
    result = _lib.ml_verify_signature(data.encode('utf-8'), signature.encode('utf-8'))
    if not result:
        return None
    return bool(result[0])

# hash: always returns a value
_lib.ml_hash.argtypes = [ctypes.c_char_p]
_lib.ml_hash.restype = ctypes.c_char_p

def hash(data: str) -> str:
    """Hash data to a fixed-length string."""
    result = _lib.ml_hash(data.encode('utf-8'))
    return result.decode('utf-8')
```

## Key Learnings

### 1. Option Type Semantics

**OCaml**:
```ocaml
type 'a option = None | Some of 'a

val decrypt : string -> string -> string option
(* Can return None or Some(decrypted_string) *)
```

**Python**:
```python
def decrypt(ciphertext: str, key: str) -> Optional[str]:
    # Returns None or str
```

### 2. Null Safety

Option types make null handling explicit:

```python
# Must check for None
result = decrypt(data, key)
if result is not None:
    print(f"Success: {result}")
else:
    print("Failed")

# Type checker catches missing None check
print(result.upper())  # Error if not checked!
```

### 3. Error Handling Patterns

**Pattern 1: Default Values**
```python
key = find_key("production") or "default-key"
```

**Pattern 2: Early Return**
```python
def process_encrypted(ciphertext: str, key: str) -> bool:
    decrypted = decrypt(ciphertext, key)
    if decrypted is None:
        return False
    # Use decrypted safely
    return len(decrypted) > 0
```

**Pattern 3: Walrus Operator**
```python
if (key := find_key("api")) is not None:
    use_key(key)
```

### 4. Type Hints Integration

Generated Python code includes proper type hints:

```python
from typing import Optional

def find_key(name: str) -> Optional[str]:
    """IDE autocomplete knows this can be None"""
```

## Running the Example

```bash
# Generate bindings
polyglot-ffi generate src/crypto.mli --output generated --name crypto

# Build OCaml library
make build

# Run Python example
python example.py
```

## Common Patterns

### Safe Unwrapping

```python
def unwrap_or(option: Optional[str], default: str) -> str:
    """Unwrap option or return default."""
    return option if option is not None else default

key = unwrap_or(find_key("api"), "default-api-key")
```

### Chaining Options

```python
def chain_decrypt(ciphertext: str) -> Optional[str]:
    """Try multiple keys until one works."""
    for key_name in ["production", "staging", "development"]:
        if (key := find_key(key_name)) is not None:
            if (result := decrypt(ciphertext, key)) is not None:
                return result
    return None
```

### Map Over Option

```python
from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')

def map_option(option: Optional[T], f: Callable[[T], U]) -> Optional[U]:
    """Apply function to option value if present."""
    return f(option) if option is not None else None

# Use it
key_length = map_option(find_key("api"), len)
# Returns Optional[int]: length of key if found, None otherwise
```

## Next Steps

- **Lists**: See [data-processing](../data-processing/) example
- **Records**: See [web-api](../web-api/) example
- **Tuples**: See [ml-pipeline](../ml-pipeline/) example

## Troubleshooting

**Issue**: Type checker complains about None
```python
# Bad: result might be None
result = decrypt(data, key)
print(result.upper())  # Error!

# Good: Check for None first
if result is not None:
    print(result.upper())
```

**Issue**: Option always returns None
- Check OCaml implementation returns Some properly
- Verify C stub NULL pointer handling
- Ensure key/data encoding is correct
