# Simple Example

This is a minimal example showing how to use Polyglot FFI to generate bindings for basic OCaml functions.

## What This Example Shows

- Defining a simple OCaml interface (`.mli`)
- Implementing OCaml functions (`.ml`)
- Generating FFI bindings automatically
- Using the generated bindings from Python

## Files

```
simple/
├── README.md           # This file
├── crypto.mli          # OCaml interface definition
├── crypto.ml           # OCaml implementation
└── generated/          # Generated bindings (after running polyglot-ffi)
```

## Quick Start

### 1. Define Your OCaml Interface

**crypto.mli:**
```ocaml
val encrypt : string -> string
(** Encrypt a string using Caesar cipher *)

val decrypt : string -> string
(** Decrypt a string using Caesar cipher *)

val hash : string -> int
(** Simple hash function *)
```

### 2. Implement Your Functions

**crypto.ml:**
```ocaml
let encrypt s =
  String.map (fun c ->
    if c >= 'a' && c <= 'z' then
      Char.chr ((Char.code c - Char.code 'a' + 3) mod 26 + Char.code 'a')
    else c
  ) s

let decrypt s =
  String.map (fun c ->
    if c >= 'a' && c <= 'z' then
      Char.chr ((Char.code c - Char.code 'a' - 3 + 26) mod 26 + Char.code 'a')
    else c
  ) s

let hash s =
  String.fold_left (fun acc c -> acc * 31 + Char.code c) 0 s

(* Register functions for FFI *)
let () =
  Callback.register "encrypt" encrypt;
  Callback.register "decrypt" decrypt;
  Callback.register "hash" hash
```

### 3. Generate Bindings

From this directory:

```bash
polyglot-ffi generate crypto.mli -o generated/ -n crypto
```

This creates:
- `generated/type_description.ml` - OCaml type definitions
- `generated/function_description.ml` - OCaml ctypes foreign declarations
- `generated/crypto_stubs.c` - C wrapper functions
- `generated/crypto_stubs.h` - C header file
- `generated/crypto_py.py` - Python wrapper
- `generated/dune` - Dune build configuration
- `generated/dune-project` - Dune project file

### 4. Build (Optional - requires OCaml/Dune)

```bash
# Copy implementation to generated directory
cp crypto.ml crypto.mli generated/

# Build
cd generated
dune build

# This creates a shared library that Python can load
```

### 5. Use from Python

```python
from generated.crypto_py import encrypt, decrypt, hash

# Test encryption
message = "hello"
encrypted = encrypt(message)
print(f"Original: {message}")
print(f"Encrypted: {encrypted}")  # Output: "khoor"

# Test decryption
decrypted = decrypt(encrypted)
print(f"Decrypted: {decrypted}")  # Output: "hello"

# Test hash
hash_value = hash(message)
print(f"Hash: {hash_value}")
```

## What Gets Generated

### OCaml Ctypes (function_description.ml)

```ocaml
open Ctypes

module Functions (F : Ctypes.FOREIGN) = struct
  let encrypt = F.foreign "ml_encrypt" (string @-> returning string)
  let decrypt = F.foreign "ml_decrypt" (string @-> returning string)
  let hash = F.foreign "ml_hash" (string @-> returning int)
end
```

### C Stubs (crypto_stubs.c)

```c
char* ml_encrypt(char* input) {
    CAMLparam0();
    CAMLlocal2(ml_input, ml_result);

    ml_input = caml_copy_string(input);
    ml_result = caml_callback(*caml_named_value("encrypt"), ml_input);

    char* result = strdup(String_val(ml_result));
    CAMLreturnT(char*, result);
}
// ... similar for decrypt and hash
```

### Python Wrapper (crypto_py.py)

```python
import ctypes
from pathlib import Path

_lib = ctypes.CDLL(str(Path(__file__).parent / "libcrypto.so"))

_lib.ml_encrypt.argtypes = [ctypes.c_char_p]
_lib.ml_encrypt.restype = ctypes.c_char_p

def encrypt(input: str) -> str:
    """Call OCaml encrypt function"""
    result = _lib.ml_encrypt(input.encode('utf-8'))
    if result is None:
        raise CryptoError("encrypt returned NULL")
    return result.decode('utf-8')
# ... similar for decrypt and hash
```

## Key Concepts

### Type Safety
- OCaml types → IR → C types → Python types
- Type hints in Python wrapper
- Compile-time type checking in OCaml

### Memory Safety
- Proper CAMLparam/CAMLreturn macros in C
- String ownership handled with strdup
- No memory leaks

### Zero Boilerplate
- Write interface once (`.mli`)
- Generate 100+ lines automatically
- Type-safe, memory-safe, ready to use

## Supported Types (Phase 1)

| OCaml | C | Python |
|-------|---|--------|
| `string` | `char*` | `str` |
| `int` | `int` | `int` |
| `float` | `double` | `float` |
| `bool` | `int` | `bool` |
| `unit` | `void` | `None` |

## Next Steps

- Try adding more functions to `crypto.mli`
- Regenerate with `polyglot-ffi generate crypto.mli -o generated/ -n crypto --force`
- Experiment with different types (int, float, bool)
- See [main documentation](../../docs/index.md) for more

## Troubleshooting

**"Command not found: polyglot-ffi"**
```bash
pip install -e ../..  # Install from repo root
```

**"Module not found: crypto_py"**
- Make sure you built the OCaml library with `dune build`
- The Python wrapper expects `libcrypto.so` in the same directory

**Parse errors**
- Check `.mli` syntax matches `val name : type -> type` format
- Currently only supports primitive types (Phase 1)

## Learn More

- [Quickstart Guide](../../docs/quickstart.md)
- [Type Mapping Reference](../../docs/type-mapping.md)
- [Architecture Overview](../../docs/architecture.md)
