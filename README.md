# Polyglot FFI

**Automatic FFI bindings generator for polyglot projects**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/chizy7/polyglot-ffi)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/phase-1%20complete-success.svg)](PHASE1_COMPLETE.md)

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
# Output: polyglot-ffi, version 0.1.0
```

---

## Features

### ✅ Phase 1 (Current - v0.1.0)

**Supported Types:**
- ✅ `string`, `int`, `float`, `bool`, `unit`
- ✅ Multi-parameter functions
- ✅ Documentation preservation

**Generated Code:**
- ✅ OCaml ctypes bindings
- ✅ Memory-safe C stubs
- ✅ Python wrappers with type hints
- ✅ Dune build configuration

**CLI Commands:**
- ✅ `polyglot-ffi init` - Initialize projects
- ✅ `polyglot-ffi generate` - Generate bindings
- ✅ `polyglot-ffi check` - Validate config
- ✅ `polyglot-ffi clean` - Clean generated files

### 🚧 Phase 2 (In Progress)

- [ ] Option types (`'a option`)
- [ ] List types (`'a list`)
- [ ] Tuple types (`'a * 'b`)
- [ ] Record types
- [ ] Variant types
- [ ] Custom type mappings

### 📋 Future Phases

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
- **[Configuration](docs/configuration.md)** - Configure projects
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

- 70%+ test coverage
- Rich error messages
- CLI with progress indicators
- Dry run mode
- Force regeneration

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
| Core Architecture | ✅ Complete | 61% |
| OCaml Parser | ✅ Complete | 92% |
| IR System | ✅ Complete | 63% |
| Ctypes Generator | ✅ Complete | 96% |
| C Stub Generator | ✅ Complete | 79% |
| Python Generator | ✅ Complete | 94% |
| Dune Generator | ✅ Complete | 100% |
| CLI | ✅ Complete | 78% |
| Documentation | ✅ Complete | 100% |

**Current Version:** 0.1.0 (Alpha)
**Phase 1:** ✅ Complete - Primitive types working
**Phase 2:** 🚧 In Progress - Complex types
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

# Generate bindings
polyglot-ffi generate src/module.mli

# Custom output & name
polyglot-ffi generate src/module.mli -o bindings/ -n mymodule

# Dry run
polyglot-ffi generate src/module.mli --dry-run

# Force regeneration
polyglot-ffi generate src/module.mli --force

# Check configuration
polyglot-ffi check

# Clean generated files
polyglot-ffi clean

# Get help
polyglot-ffi --help
```

---

## Supported Types (Phase 1)

| OCaml | C | Python | Example |
|-------|---|--------|---------|
| `string` | `char*` | `str` | `"hello"` |
| `int` | `int` | `int` | `42` |
| `float` | `double` | `float` | `3.14` |
| `bool` | `int` | `bool` | `True` |
| `unit` | `void` | `None` | `None` |

---

## Architecture

```
┌─────────────┐
│  .mli file  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  Parse OCaml interface
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     IR      │  Language-agnostic representation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Generators  │  Generate target code
│  - Ctypes   │
│  - C Stubs  │
│  - Python   │
│  - Dune     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Output    │  Ready-to-use bindings
└─────────────┘
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

### v0.2 (Phase 2) - Q1 2025
- Option, list, tuple, record, variant types
- Type registry
- Custom type mappings

### v0.3 (Phase 3) - Q2 2025
- Watch mode
- Better error messages
- Configuration file support

### v1.0 (Production) - Q3 2025
- Stable API
- Rust target support
- Comprehensive documentation
- Battle-tested on real projects

---

**Made with ❤️ for polyglot developers**

Stop writing FFI boilerplate. Start building amazing things.

```bash
pip install polyglot-ffi
```

[Get Started](docs/quickstart.md) • [Documentation](docs/index.md) • [Examples](examples/)
