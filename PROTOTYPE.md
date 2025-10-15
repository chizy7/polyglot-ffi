# Polyglot FFI Generator - Prototype

Automatic OCaml ↔ Python FFI binding generator. Say goodbye to manual ctypes boilerplate!

## Quick Start

```bash
# Generate bindings from your .mli file
python polyglot-ffi-gen.py encryption.mli -o bindings -n encryption

# Output:
# Found 4 function(s):
#   - encrypt: string -> string
#   - decrypt: string -> string
#   - hash: string -> string
#   - validate: string -> string -> bool
# 
# Generating bindings in bindings/...
#   ✓ type_description.ml
#   ✓ function_description.ml
#   ✓ encryption_stubs.c
#   ✓ encryption_stubs.h
#   ✓ dune
#   ✓ dune-project
#   ✓ encryption_py.py
```

## What Gets Generated

### 1. OCaml Ctypes Files
- `type_description.ml` - Type definitions (auto-generated boilerplate)
- `function_description.ml` - Foreign function declarations with correct ctypes syntax

### 2. C Stubs
- `encryption_stubs.c` - C wrapper functions with proper:
  - `CAMLparam`/`CAMLreturn` macros
  - Memory management
  - Type conversions between C and OCaml
- `encryption_stubs.h` - C header declarations

### 3. Build Configuration
- `dune` - Complete dune file with ctypes stanza (correct version!)
- `dune-project` - Project configuration with all dependencies

### 4. Python Wrapper
- `encryption_py.py` - Pythonic API with:
  - Type hints
  - Docstrings
  - Error handling
  - Automatic encoding/decoding

## Usage Example

### Step 1: Write Your OCaml Interface

```ocaml
(* encryption.mli *)
val encrypt : string -> string
(** Encrypt a string using our custom algorithm *)

val decrypt : string -> string
(** Decrypt a string using our custom algorithm *)
```

### Step 2: Generate Bindings

```bash
python polyglot-ffi-gen.py encryption.mli
```

### Step 3: Implement OCaml Functions

```ocaml
(* encryption.ml *)
let encrypt s = 
  (* Your encryption logic *)
  String.map (fun c -> Char.chr ((Char.code c + 1) mod 256)) s

let decrypt s = 
  (* Your decryption logic *)
  String.map (fun c -> Char.chr ((Char.code c - 1) mod 256)) s

(* Register functions for C callbacks *)
let () =
  Callback.register "encrypt" encrypt;
  Callback.register "decrypt" decrypt
```

### Step 4: Build

```bash
cd generated
dune build
```

### Step 5: Use from Python

```python
from encryption_py import encrypt, decrypt

message = "Hello, World!"
encrypted = encrypt(message)
decrypted = decrypt(encrypted)

print(f"Original: {message}")
print(f"Encrypted: {encrypted}")
print(f"Decrypted: {decrypted}")
```

## Supported Types

Currently supports:
- `string` → `char*` → `str`
- `int` → `int` → `int`
- `float` → `double` → `float`
- `bool` → `int` → `bool`
- `unit` → `void` → `None`

## Command Line Options

```bash
python polyglot-ffi-gen.py [options] <mli_file>

Options:
  -o, --output-dir DIR    Output directory (default: generated)
  -n, --name NAME         Module name (default: derived from filename)
  -h, --help              Show this help message
```

## What Problems Does This Solve?

### Before (Manual Approach):
```ocaml
(* You had to write this manually: *)
open Ctypes

module Types (F : Ctypes.TYPE) = struct
  (* Type descriptions... *)
end

module Functions (F : Ctypes.FOREIGN) = struct
  let encrypt = 
    F.foreign "ml_encrypt"
      (string @-> returning string)
  (* More boilerplate... *)
end
```

```c
/* And this C code: */
char* ml_encrypt(char* input) {
    CAMLparam0();
    CAMLlocal2(ml_input, ml_result);
    ml_input = caml_copy_string(input);
    ml_result = caml_callback(*caml_named_value("encrypt"), ml_input);
    char* result = strdup(String_val(ml_result));
    CAMLreturnT(char*, result);
}
/* More boilerplate... */
```

```python
# And configure Python ctypes:
import ctypes
_lib = ctypes.CDLL("libencryption.so")
_lib.ml_encrypt.argtypes = [ctypes.c_char_p]
_lib.ml_encrypt.restype = ctypes.c_char_p
# More boilerplate...
```

### After (With Polyglot FFI):
```bash
python polyglot-ffi-gen.py encryption.mli
# Done! All boilerplate generated.
```

## Pain Points Eliminated

No more Dune version mismatches  
No manual ctypes type descriptions  
No C stub boilerplate  
No confusion about `Callback.register` vs `foreign`  
No manual Python ctypes configuration  
Proper memory management automatically  
Type-safe bindings with hints  

## Limitations (Prototype)

This is a **prototype** demonstrating the concept. Current limitations:
- Only handles simple function signatures
- No support for records, variants, or custom types (yet)
- No support for optional arguments
- No support for lists/arrays
- Single direction: OCaml → Python (not Python → OCaml callbacks)

## Next Steps (After prototype):

For the production version, we'll add:
- Complex type support (records, variants, lists)
- Bidirectional bindings
- Better error messages
- Configuration file for custom type mappings
- Multiple language backends (not just Python)
- CLI with more options
- Proper testing suite
