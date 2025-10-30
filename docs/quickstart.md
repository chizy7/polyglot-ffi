# Quickstart Guide

Get started with Polyglot FFI in 5 minutes!

## Installation

### From PyPI

```bash
pip install polyglot-ffi
```

### From Source

```bash
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi
pip install -e ".[dev]"
```

### Verify Installation

```bash
polyglot-ffi --version
# Output: polyglot-ffi, version 0.4.3
```

## Your First Project

### Step 1: Initialize a New Project

```bash
polyglot-ffi init my-crypto-lib
cd my-crypto-lib
```

**Note:** You can use hyphens in project names (like `my-crypto-lib`). Polyglot-ffi automatically converts them to underscores in generated code for compatibility with OCaml, C, and Python naming rules.

This creates:
```
my-crypto-lib/
├── polyglot.toml       # Configuration
├── README.md           # Project documentation
├── Makefile            # Convenience commands
├── .gitignore          # Git ignore rules
└── src/
    ├── my-crypto-lib.mli   # OCaml interface (edit this)
    └── my-crypto-lib.ml    # OCaml implementation (edit this)
```

### Step 2: Define Your API

Edit `src/my-crypto-lib.mli`:

```ocaml
(* my-crypto-lib.mli *)

val encrypt : string -> string
(** Encrypt a string using Caesar cipher *)

val decrypt : string -> string
(** Decrypt a string using Caesar cipher *)

val hash : string -> int
(** Simple hash function *)
```

### Step 3: Generate Bindings

```bash
polyglot-ffi generate src/my-crypto-lib.mli -o generated/ -n my_crypto
```

Output:
```
✓ Bindings generated successfully!

Generated files:
  ✓ generated/type_description.ml
  ✓ generated/function_description.ml
  ✓ generated/my_crypto_stubs.c
  ✓ generated/my_crypto_stubs.h
  ✓ generated/dune
  ✓ generated/dune-project
  ✓ generated/my_crypto_py.py

Generated 3 function(s)
```

### Step 4: Implement Your OCaml Functions

Edit `src/my-crypto-lib.ml`:

```ocaml
(* my-crypto-lib.ml *)

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

(* Register functions for C FFI *)
let () =
  Callback.register "encrypt" encrypt;
  Callback.register "decrypt" decrypt;
  Callback.register "hash" hash
```

### Step 5: Build (Optional - if you have OCaml/Dune)

First, install OCaml build dependencies:

```bash
# Install OCaml dependencies (one-time setup)
opam install dune ctypes ctypes-foreign
```

Then build your bindings:

```bash
# Copy implementation to generated directory
# Note: If your project name has hyphens, rename files to use underscores
cp src/my-crypto-lib.ml generated/my_crypto_lib.ml
cp src/my-crypto-lib.mli generated/my_crypto_lib.mli

cd generated
dune build
```

**Important:** When copying source files with hyphens in their names, rename them to use underscores (e.g., `my-crypto-lib.ml` → `my_crypto_lib.ml`). This ensures compatibility with OCaml's module naming requirements.

### Step 6: Use from Python

```python
# test_crypto.py
from generated.my_crypto_py import encrypt, decrypt, hash

# Test encryption
message = "hello"
encrypted = encrypt(message)
print(f"Original: {message}")
print(f"Encrypted: {encrypted}")  # "khoor"

# Test decryption
decrypted = decrypt(encrypted)
print(f"Decrypted: {decrypted}")  # "hello"

# Test hash
hash_val = hash(message)
print(f"Hash: {hash_val}")
```

## Common Workflows

### Generate with Custom Output

```bash
# Specify output directory and module name
polyglot-ffi generate src/module.mli -o bindings/ -n mymodule

# Dry run (see what would be generated)
polyglot-ffi generate src/module.mli --dry-run

# Force regeneration
polyglot-ffi generate src/module.mli --force
```

### Using the Makefile

The generated `Makefile` provides convenient commands:

```bash
# Generate bindings
make generate

# Build OCaml library
make build

# Clean generated files
make clean

# Run tests
make test
```

## Example: Multiple Function Types

```ocaml
(* example.mli *)

(* String operations *)
val greet : string -> string
(** Greet someone *)

(* Math operations *)
val add : int -> int -> int
(** Add two integers *)

val multiply : float -> float -> float
(** Multiply two floats *)

(* Boolean operations *)
val is_even : int -> bool
(** Check if number is even *)

(* No parameters *)
val get_version : unit -> string
(** Get library version *)
```

Generate and use:

```bash
polyglot-ffi generate example.mli -o gen/ -n example
```

```python
from gen.example_py import greet, add, multiply, is_even, get_version

print(greet("Alice"))      # "Hello, Alice!"
print(add(2, 3))           # 5
print(multiply(2.5, 4.0))  # 10.0
print(is_even(4))          # True
print(get_version())       # "1.0.0"
```

## Supported Types

### Primitive Types

| OCaml Type | C Type  | Python Type | Example |
|------------|---------|-------------|---------|
| `string`   | `char*` | `str`       | `"hello"` |
| `int`      | `int`   | `int`       | `42` |
| `float`    | `double`| `float`     | `3.14` |
| `bool`     | `int`   | `bool`      | `True` |
| `unit`     | `void`  | `None`      | `None` |

### Complex Types

| OCaml Type | Python Type | Example |
|------------|-------------|---------|
| `'a option` | `Optional[T]` | `Optional[int]` |
| `'a list` | `List[T]` | `List[str]` |
| `'a * 'b` | `Tuple[T, U]` | `Tuple[int, str]` |

See [Type Mapping Guide](type-mapping.md) for complete reference.

## Project Structure

After initialization:

```
my-project/
├── polyglot.toml              # Configuration
├── README.md                  # Documentation
├── Makefile                   # Build commands
├── .gitignore                 # Git ignore
│
├── src/                       # Your OCaml source
│   ├── my-project.mli        # Interface (edit this)
│   └── my-project.ml         # Implementation (edit this)
│
└── generated/                 # Generated bindings (don't edit)
    ├── type_description.ml   # OCaml types
    ├── function_description.ml  # OCaml ctypes
    ├── my-project_stubs.c    # C wrappers
    ├── my-project_stubs.h    # C headers
    ├── dune                  # Build config
    ├── dune-project          # Dune metadata
    └── my-project_py.py      # Python wrapper
```

## Configuration File

`polyglot.toml`:

```toml
[project]
name = "my-project"
version = "0.1.0"
source_lang = "ocaml"

[languages.ocaml]
source_dir = "src"
build_system = "dune"

[languages.python]
target_dir = "generated"
min_version = "3.8"

[bindings]
auto_discover = true
interfaces = ["src/my-project.mli"]

[generate]
watch = false
verbose = false
```

## Advanced Features

### Watch Mode (Auto-regenerate)

```bash
# Watch files and auto-regenerate on changes
polyglot-ffi watch src/*.mli

# Watch with auto-build
polyglot-ffi watch src/*.mli --build
```

### Validate Configuration

```bash
# Check project configuration
polyglot-ffi check

# Check with dependencies
polyglot-ffi check --check-deps
```

### Clean Generated Files

```bash
# Preview what will be deleted
polyglot-ffi clean --dry-run

# Actually clean
polyglot-ffi clean
```

## Next Steps

- **Complex types**: Try [options, lists, and tuples](type-mapping.md)
- **Watch mode**: Use `polyglot-ffi watch` for auto-regeneration
- **Configuration**: Customize `polyglot.toml` for your project
- **Multiple modules**: Generate bindings for each `.mli` file
- **CI/CD**: Add `polyglot-ffi generate` to your build pipeline
- **Examples**: Check out `examples/` directory for more patterns

## Troubleshooting

### Command not found

```bash
# Make sure you're in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e ".[dev]"
```

### Import errors in Python

Make sure the shared library is built and in the correct location. The Python wrapper expects `lib{module_name}.so` in the same directory.

### Parse errors

Check your `.mli` syntax:
- Use `val name : type` format
- Currently supports only primitive types
- Multi-line signatures need continuation

## Help and Support

```bash
# Get help
polyglot-ffi --help

# Command-specific help
polyglot-ffi init --help
polyglot-ffi generate --help
polyglot-ffi watch --help
polyglot-ffi check --help
polyglot-ffi clean --help
```

### Resources

- **Documentation**: https://polyglotffi.com/
- **Quick Reference**: [quick_reference.md](quick_reference.md)
- **Type Mapping**: [type-mapping.md](type-mapping.md)
- **Architecture**: [architecture.md](architecture.md)
- **Issues**: https://github.com/chizy7/polyglot-ffi/issues
- **Examples**: See `examples/` directory in repository

### Upgrading

```bash
# Upgrade to latest version
pip install --upgrade polyglot-ffi

# Check version
polyglot-ffi --version
```

See [Installation Guide](installation.md#upgrading) for more options.

---

**Ready to eliminate FFI boilerplate?** Let's build something amazing!

**Version:** 0.4.3 | **Documentation:** https://polyglotffi.com/
