# Polyglot FFI

**Automatic FFI bindings generator for polyglot projects**

[![PyPI version](https://img.shields.io/pypi/v/polyglot-ffi.svg)](https://pypi.org/project/polyglot-ffi/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![Build](https://github.com/chizy7/polyglot-ffi/actions/workflows/ci.yml/badge.svg)](https://github.com/chizy7/polyglot-ffi/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/chizy7/polyglot-ffi/branch/master/graph/badge.svg)](https://codecov.io/gh/chizy7/polyglot-ffi)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://chizy7.github.io/polyglot-ffi/)

Stop writing FFI boilerplate. Start building amazing things.

---

## What is Polyglot FFI?

Polyglot FFI automatically generates complete Foreign Function Interface (FFI) bindings between programming languages. Write your OCaml interface once, and get type-safe, memory-safe bindings for Python (and soon Rust, Go, etc.) instantly.

### The Problem

Building multi-language projects requires writing:
- 50+ lines of OCaml ctypes boilerplate
- 30+ lines of C stubs with tricky memory management
- 20+ lines of Python ctypes configuration
- Plus: Dune configs, debugging, memory leaks...

### The Solution

```bash
polyglot-ffi generate crypto.mli
```

**Done!** All 100+ lines generated automatically.

---

## Quick Example

### Primitive Types

**1. Write OCaml interface:**

```ocaml
(* crypto.mli *)
val encrypt : string -> string
(** Encrypt a string *)

val hash : string -> int
(** Hash to integer *)
```

**2. Generate bindings:**

```bash
polyglot-ffi generate crypto.mli -o generated/ -n crypto
```

**3. Use from Python:**

```python
from generated.crypto_py import encrypt, hash

encrypted = encrypt("secret")
hash_val = hash("data")
```

### Complex Types

**1. Write OCaml interface with complex types:**

```ocaml
(* user.mli *)
type user = {
  name: string;
  age: int;
  email: string option;
}

type result = Ok of user | Error of string

val find_user : string -> user option
val create_user : string -> int -> string -> result
val get_all_users : unit -> user list
val get_name_and_age : user -> string * int
```

**2. Generate bindings:**

```bash
polyglot-ffi generate user.mli
```

**3. Use from Python with full type hints:**

```python
from typing import Optional, List, Tuple
from generated.user_py import find_user, create_user, get_all_users

# Option type → Optional[User]
user = find_user("john")  # Returns Optional[User]

# Variant type → Result
result = create_user("Jane", 25, "jane@example.com")

# List type → List[User]
all_users = get_all_users()  # Returns List[User]

# Tuple type → Tuple[str, int]
name, age = get_name_and_age(user)  # Returns Tuple[str, int]
```

---

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

### Verify

```bash
polyglot-ffi --version
# Output: polyglot_ffi, version 0.4.0
```

### Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade polyglot-ffi
```

To upgrade to a specific version:

```bash
pip install --upgrade polyglot-ffi==0.5.0
```

See the [full installation guide](docs/installation.md) for detailed instructions including:
- Virtual environment setup
- Shell completion
- Troubleshooting
- Platform-specific notes
- **[Complete upgrade guide](docs/installation.md#upgrading)** with all options

---

## Features

- **Automatic Code Generation**: One command generates OCaml ctypes, C wrappers, Python modules, and build configs.
- **Plus Many More Features**: Check docs and roadmap!

### Some Future Features

- [ ] Rust target support
- [ ] Go target support
- [ ] Bidirectional bindings
- [ ] Plugin system

---

## Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Architecture](docs/architecture.md)** - How it works
- **[Type Mapping](docs/type-mapping.md)** - Type system reference
- **[Contributing](docs/contributing.md)** - Join development

---

## Why Polyglot FFI?

### Zero Boilerplate

One command generates everything:
- OCaml ctypes declarations
- C wrapper functions
- Python wrapper module
- Build configuration
- Type conversions
- Error handling

### Type Safe

Preserves type information:
- Python type hints
- OCaml type constraints
- C type declarations
- Compile-time checking

### Memory Safe

Proper memory management:
- CAMLparam/CAMLreturn macros
- No memory leaks
- String ownership handled
- GC-safe conversions

---

## Use Cases

- **Cryptography**: OCaml for correctness, Python for integration
- **Data Processing**: OCaml for logic, Python for data science
- **Financial Systems**: OCaml for algorithms, Python for reporting
- **ML Infrastructure**: OCaml for pipelines, Python for training

---

## Quick Start

### Initialize a New Project

```bash
polyglot-ffi init my-crypto-lib
cd my-crypto-lib
```

### Edit Your Interface

```ocaml
(* src/my-crypto-lib.mli *)
val greet : string -> string
val add : int -> int -> int
```

### Generate Bindings

```bash
polyglot-ffi generate src/my-crypto-lib.mli
```

### Implement OCaml Functions

```ocaml
(* src/my-crypto-lib.ml *)
let greet name = "Hello, " ^ name ^ "!"
let add x y = x + y

let () =
  Callback.register "greet" greet;
  Callback.register "add" add
```

### Use from Python

```python
from generated.my_crypto_lib_py import greet, add

print(greet("World"))  # Hello, World!
print(add(2, 3))       # 5
```

---

## CLI Reference

```bash
# Initialize project
polyglot-ffi init my-project
polyglot-ffi init --interactive              # Interactive setup

# Generate bindings
polyglot-ffi generate src/module.mli
polyglot-ffi generate -o bindings/ -n mymodule
polyglot-ffi generate --dry-run              # Preview only
polyglot-ffi generate --force                # Force regeneration

# Watch mode (NEW in v0.3!)
polyglot-ffi watch                           # Watch files from config
polyglot-ffi watch src/*.mli                 # Watch specific files
polyglot-ffi watch --build                   # Auto-build after changes

# Validate project (NEW in v0.3!)
polyglot-ffi check                           # Check configuration
polyglot-ffi check --check-deps              # Include dependency check
polyglot-ffi check --lang rust               # Check specific language

# Clean generated files (NEW in v0.3!)
polyglot-ffi clean                           # Remove generated files
polyglot-ffi clean --dry-run                 # Preview what would be deleted
polyglot-ffi clean --all                     # Remove all including directories

# Get help
polyglot-ffi --help
```

All generation happens at build time. **Zero runtime overhead.**

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/contributing.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- PR process

**Good first issues:** Look for `good-first-issue` label

---

## Community

- **GitHub**: [chizy7/polyglot-ffi](https://github.com/chizy7/polyglot-ffi)
- **Issues**: [Report bugs](https://github.com/chizy7/polyglot-ffi/issues)
- **Discussions**: Coming soon

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

## Acknowledgments

Built with inspiration from:
- [PyO3](https://github.com/PyO3/pyo3) - Rust ↔ Python bindings
- [Ctypes](https://github.com/ocamllabs/ocaml-ctypes) - OCaml FFI library
- [SWIG](http://www.swig.org/) - Multi-language wrapper generator

---
## Contact Me

For questions, feedback, or collaboration opportunities:

- **Email**: [chizy@chizyhub.com](mailto:chizy@chizyhub.com)
- **X(Twitter)**: [![Twitter Follow](https://img.shields.io/twitter/follow/chizyization?style=social)](https://x.com/Chizyization)

---

Stop writing FFI boilerplate. Start building amazing things.

```bash
pip install polyglot-ffi
```