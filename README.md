# Polyglot FFI

**Automatic FFI bindings generator for polyglot projects**

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/chizy7/polyglot-ffi)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

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

### From PyPI (when published)

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
# Output: polyglot-ffi, version 0.3.0
```

---

## Features

### v0.1.0

**Primitive Types:**
- `string`, `int`, `float`, `bool`, `unit`
- Multi-parameter functions
- Documentation preservation

### v0.2.0

**Complex Types:**
- Option types (`'a option`, `string option`, `int option`)
- List types (`'a list`, `int list`, `string list`)
- Tuple types (`'a * 'b`, `int * string * float`)
- Record types (`type user = { name: string; age: int }`)
- Variant types (`type result = Ok of string | Error of string`)
- Type variables (`'a`, `'b` for polymorphic types)
- Custom type references
- Nested & combined types (`(int * string) list option`)

**New Features:**
- Type Registry system for extensible type mappings
- Support for OCaml, Python, C, and Rust type mappings
- Custom type converters
- 86 passing tests (61 new tests added)

### v0.3.0

**Developer Experience:**
- Enhanced error messages with suggestions
- Configuration file support (`polyglot.toml`)
- Watch mode for auto-regeneration
- Project validation (`check` command)
- Clean command for removing generated files
- Detailed progress indicators
- Rich console output with colors

**New Commands:**
- `polyglot-ffi watch` - Auto-regenerate on file changes
- `polyglot-ffi check` - Validate project configuration
- `polyglot-ffi clean` - Remove generated files

**Generated Code:**
- OCaml ctypes bindings (with complex types)
- Memory-safe C stubs (GC-safe opaque pointers)
- Python wrappers with full type hints
- Dune build configuration

### Future Features

- [ ] Rust target support
- [ ] Go target support
- [ ] Watch mode
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

### Production Ready

- 86 comprehensive tests (100% passing)
- 65% code coverage across all modules
- Type Registry for extensible mappings
- Rich error messages
- CLI with progress indicators
- Dry run mode & force regeneration
- Backward compatible

---

## Use Cases

- **Cryptography**: OCaml for correctness, Python for integration
- **Data Processing**: OCaml for logic, Python for data science
- **Financial Systems**: OCaml for algorithms, Python for reporting
- **ML Infrastructure**: OCaml for pipelines, Python for training

---

## Project Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Core Architecture | Complete | 65% |
| OCaml Parser | Complete | 91% |
| Type Registry | Complete | 82% |
| IR System | Complete | 69% |
| Ctypes Generator | Complete | 69% |
| C Stub Generator | Complete | 75% |
| Python Generator | Complete | 70% |
| Dune Generator | Complete | 100% |
| CLI | Complete | 78% |
| Documentation | Complete | 100% |
| **Tests** | **86 passing** | **100%** |

**Current Version:** 0.3.0 (Beta)
**Phase 1:** Complete - Primitive types
**Phase 2:** Complete - Complex types
**Phase 3:** Complete - Developer Experience
**Phase 4:** Next - Documentation & Publishing
**Production Ready:** Targeting v1.0

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

## Roadmap

### v0.1 - Complete
- Primitive types (string, int, float, bool, unit)
- Multi-parameter functions
- Basic code generation

### v0.2 - Complete
- Option, list, tuple, record, variant types
- Type registry
- Custom type mappings
- 86 passing tests

### v0.3 - Complete
- Watch mode for auto-regeneration
- Enhanced error messages with suggestions
- Configuration file support (polyglot.toml)
- Check and clean commands
- Rich progress indicators

### v0.4 - In Progress
- [ ] Comprehensive documentation site
- [ ] Video tutorials and examples
- [ ] Integration tests for CLI commands
- [ ] Performance optimizations
- [ ] Shell completion (bash, zsh, fish)

### v1.0 (Production) - Coming Soon
- [ ] Publish to PyPI
- [ ] Stable API guarantee
- [ ] Rust target support
- [ ] CI/CD pipeline
- [ ] Battle-tested on 5+ real projects

---

**Made with ❤️ for polyglot developers**

Stop writing FFI boilerplate. Start building amazing things.

```bash
pip install polyglot-ffi
```
