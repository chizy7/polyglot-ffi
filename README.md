# Polyglot FFI

**Automatic Foreign Function Interface (FFI) bindings generator for multi-language projects**

Stop writing boilerplate. Start building.

---

## Tagline Options

- **"FFI bindings that write themselves"**
- **"Bridge languages without the pain"**
- **"Your polyglot projects, zero boilerplate"**
- **"Multi-language FFI, single command"**

---

## Problem Statement

Building multi-language projects is powerful but painful. You want to:
- Use OCaml's correctness guarantees for core logic
- Use Python's ecosystem for APIs and data science
- Use Rust's performance for hot paths

But you get stuck writing:
- Manual ctypes type descriptions
- C stub code with CAMLparam/CAMLreturn macros
- Foreign function declarations
- Build system configuration (Dune, setuptools, cargo)
- Python/Rust wrapper code with proper encoding

**Polyglot FFI eliminates all this boilerplate.**

---

## What It Does

Parse your OCaml interface files (`.mli`) and automatically generate:

- **OCaml ctypes bindings** - Complete type and function descriptions
- **C stubs** - Proper memory management, type conversions, error handling
- **Python wrappers** - Type hints, docstrings, Pythonic APIs
- **Rust bindings** - Safe FFI with proper ownership semantics (coming soon)
- **Build configuration** - Dune, setuptools, cargo configs with correct versions

---

## Features

### **Zero Boilerplate**
```bash
polyglot-ffi generate encryption.mli
# ✓ type_description.ml
# ✓ function_description.ml  
# ✓ encryption_stubs.c
# ✓ encryption_stubs.h
# ✓ dune & dune-project
# ✓ encryption.py
```

### **Fast Development**
```bash
polyglot-ffi watch
# Auto-regenerate on file changes
# See results instantly
```

### **Type Safe**
- Preserves OCaml type information
- Generates Python type hints
- Catches mismatches at generation time

### **Smart Defaults**
- Works zero-config for common cases
- Extensible via `polyglot.toml` for custom types
- Automatic memory management

### **Production Ready**
- Proper error handling
- Memory leak prevention
- Thread-safe stubs
- Comprehensive testing

---

## Quick Start

### Installation
```bash
pip install polyglot-ffi
```

### Usage
```bash
# Initialize new project
polyglot-ffi init my-crypto-lib

# Generate bindings
polyglot-ffi generate src/crypto.mli

# Watch for changes during development
polyglot-ffi watch

# Build everything
polyglot-ffi build
```

### Example

**Input:** `encryption.mli`
```ocaml
val encrypt : string -> string
(** Encrypt a string using AES-256 *)

val decrypt : string -> string
(** Decrypt a string *)
```

**Output:** Ready-to-use Python module
```python
from encryption import encrypt, decrypt

encrypted = encrypt("secret message")
decrypted = decrypt(encrypted)
```

---

## Why Polyglot FFI?

### Before (Manual)
```ocaml
(* 50+ lines of manual ctypes boilerplate *)
open Ctypes
module Types (F : Ctypes.TYPE) = struct
  (* ... manual type descriptions ... *)
end
module Functions (F : Ctypes.FOREIGN) = struct
  (* ... manual foreign declarations ... *)
end
```

```c
/* 30+ lines of C stubs with tricky memory management */
char* ml_encrypt(char* input) {
    CAMLparam0();
    CAMLlocal2(ml_input, ml_result);
    ml_input = caml_copy_string(input);
    ml_result = caml_callback(*caml_named_value("encrypt"), ml_input);
    char* result = strdup(String_val(ml_result));
    CAMLreturnT(char*, result);
}
```

```python
# 20+ lines of ctypes configuration
import ctypes
_lib = ctypes.CDLL("libencryption.so")
_lib.ml_encrypt.argtypes = [ctypes.c_char_p]
_lib.ml_encrypt.restype = ctypes.c_char_p
# ... manual error handling ...
```

Plus: Dune configuration, build system setup, debugging version mismatches...

### After (Polyglot FFI)
```bash
polyglot-ffi generate encryption.mli
```

**All of the above generated automatically. Zero manual work.**

---

## Use Cases

### Cryptography Libraries
OCaml for correctness-critical crypto, Python for easy integration

### Data Processing Pipelines  
OCaml for business logic, Python for data science ecosystem

### Game Engines
Rust for hot paths, Python for scripting, OCaml for game logic

### Financial Systems
OCaml for trading algorithms, Python for analysis and reporting

### ML Infrastructure
OCaml for type-safe pipelines, Python for model training

---

## Supported Languages

| Source | Target | Status |
|--------|--------|--------|
| OCaml → Python | ✅ Stable |
| OCaml → Rust | 🚧 In Progress |
| OCaml → Go | 📋 Planned |
| Rust → Python | 📋 Planned |
| Python → OCaml | 📋 Planned |

---

## Supported Types

- Primitive types: `string`, `int`, `float`, `bool`, `unit`
- Options: `'a option`
- Lists: `'a list`
- Records: Custom OCaml records
- Variants: Sum types
- Arrays, tuples (in progress)
- Custom types via config (planned)

---

## Project Goals

1. **Eliminate FFI boilerplate** - Developers shouldn't waste time on plumbing
2. **Type safety first** - Catch errors at generation time, not runtime
3. **Production quality** - Memory safe, thread safe, performant
4. **Developer experience** - Fast, intuitive, well-documented
5. **Multi-language** - Support major languages in polyglot ecosystems

---

## Non-Goals

- Not a replacement for language-native solutions (use those when available)
- Not trying to make all languages "the same"
- Not a protocol layer (use gRPC/Apache Arrow for that)
- Not a runtime bridge (everything is compiled, zero runtime overhead)

---

## Architecture

```
┌─────────────────┐
│   .mli Parser   │  Parse OCaml interfaces
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Type Analyzer  │  Analyze types, build IR
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Generators    │  Generate target code
│  - Ctypes       │
│  - C Stubs      │
│  - Python       │
│  - Rust         │
└─────────────────┘
```

All generation happens at build time. Zero runtime overhead.

---

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [Configuration Reference](docs/config.md)
- [Type Mapping Guide](docs/types.md)
- [API Reference](docs/api.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Examples](examples/)

---

## Community

- [Discord Server](https://discord.gg/polyglot-ffi)
- [Twitter](https://twitter.com/polyglot_ffi)
- [Blog](https://blog.polyglot-ffi.dev)
- [Tutorials](https://polyglot-ffi.dev/tutorials)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up development environment
- Code style and testing guidelines
- How to add support for new languages
- How to add support for new types

**Good first issues:** Look for issues tagged with `good-first-issue`

---

## License

MIT License - See [LICENSE](LICENSE) for details

---

## Acknowledgments

Built with inspiration from:
- [PyO3](https://github.com/PyO3/pyo3) - Rust ↔ Python bindings
- [Ctypes](https://github.com/ocamllabs/ocaml-ctypes) - OCaml FFI library
- [SWIG](http://www.swig.org/) - Multi-language wrapper generator
- The entire OCaml, Python, and Rust communities

---

## Status

**Current Version:** 0.1.0 (Alpha)

**Stability:**
- ✅ OCaml → Python: Stable for production use
- 🚧 OCaml → Rust: Beta, breaking changes possible
- 📋 Other language pairs: Planned

**Maintenance:** Actively maintained. Issues typically responded to within 48 hours.

---

## Roadmap

### v0.2 (Next Release)
- [ ] Rust target support
- [ ] Record and variant type support
- [ ] Improved error messages
- [ ] VSCode extension

### v0.3
- [ ] Bidirectional bindings (Python → OCaml)
- [ ] Go target support
- [ ] Custom type registry

### v1.0
- [ ] Stable API
- [ ] Comprehensive test suite
- [ ] Production deployments at 5+ companies

---

## Stats

![GitHub stars](https://img.shields.io/github/stars/yourorg/polyglot-ffi?style=social)
![PyPI downloads](https://img.shields.io/pypi/dm/polyglot-ffi)
![License](https://img.shields.io/badge/license-MIT-blue)
![Build Status](https://img.shields.io/github/workflow/status/yourorg/polyglot-ffi/CI)

---

**Made with ❤️ for polyglot developers**

Stop writing FFI boilerplate. Start building amazing things.

```bash
pip install polyglot-ffi
```

[Get Started](https://polyglot-ffi.dev/quickstart) • [Documentation](https://polyglot-ffi.dev/docs) • [Examples](examples/)
