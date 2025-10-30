# Polyglot FFI

**Automatic FFI bindings generator for polyglot projects**

[![PyPI version](https://img.shields.io/pypi/v/polyglot-ffi.svg)](https://pypi.org/project/polyglot-ffi/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![Build](https://github.com/chizy7/polyglot-ffi/actions/workflows/ci.yml/badge.svg)](https://github.com/chizy7/polyglot-ffi/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/chizy7/polyglot-ffi/branch/master/graph/badge.svg)](https://codecov.io/gh/chizy7/polyglot-ffi)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://polyglotffi.com/)

Stop writing FFI boilerplate. Start building amazing things.

**[Full Documentation](https://polyglotffi.com/)** | [Quickstart](https://polyglotffi.com/quickstart/) | [API Reference](https://polyglotffi.com/api/) | [Type Mapping](https://polyglotffi.com/type-mapping/)

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

## Why Polyglot FFI?

**Zero Boilerplate** - One command generates OCaml ctypes declarations, C wrappers, Python modules, build configs, type conversions, and error handling.

**Type Safe** - Preserves type information with Python type hints, OCaml type constraints, C type declarations, and compile-time checking.

**Memory Safe** - Proper memory management with CAMLparam/CAMLreturn macros, no memory leaks, and GC-safe conversions.

## Quick Start

Initialize a new project:

```bash
polyglot-ffi init my-crypto-lib
cd my-crypto-lib
```

**Note on project names:** You can use hyphens in project names (like `my-crypto-lib`). The tool automatically converts them to underscores for generated code to ensure compatibility with OCaml, C, and Python naming requirements.

Write your OCaml interface:

```ocaml
(* src/my-crypto-lib.mli *)
val greet : string -> string
val add : int -> int -> int
```

Generate bindings:

```bash
polyglot-ffi generate src/my-crypto-lib.mli
```

Implement your OCaml functions:

```ocaml
(* src/my-crypto-lib.ml *)
let greet name = "Hello, " ^ name ^ "!"
let add x y = x + y

let () =
  Callback.register "greet" greet;
  Callback.register "add" add
```

Use from Python:

```python
from generated.my_crypto_lib_py import greet, add

print(greet("World"))  # Hello, World!
print(add(2, 3))       # 5
```

**Complex types supported**: Records, variants (Result, Option), lists, tuples, and more. See the [Type Mapping docs](docs/type-mapping.md) for details.

## Installation

```bash
pip install polyglot-ffi
```

Verify installation:
```bash
polyglot-ffi --version
```

To upgrade:
```bash
pip install --upgrade polyglot-ffi
```

See the [full installation guide](docs/installation.md) for virtual environments, shell completion, and troubleshooting.

### Prerequisites for Building Generated Bindings

If you want to **build and use** the generated OCaml bindings (not just generate them), you'll need:

```bash
# Install OCaml and required libraries
opam install dune ctypes ctypes-foreign
```

**Note:** polyglot-ffi itself is a Python tool and doesn't require OCaml. OCaml dependencies are only needed if you want to compile the generated bindings.

## Features

- **Automatic Code Generation** - One command generates OCaml ctypes, C wrappers, Python modules, and build configs
- **Rich Type Support** - Primitives, records, variants (Result, Option), lists, tuples, and nested types
- **Type Safety** - Full Python type hints and OCaml type preservation
- **Memory Safety** - Proper GC integration, no memory leaks
- **Watch Mode** - Auto-regenerate bindings on file changes
- **Project Validation** - Built-in dependency and configuration checking
- **Zero Runtime Overhead** - All generation happens at build time

### Roadmap

- [ ] Rust target support
- [ ] Go target support
- [ ] Bidirectional bindings (call Python from OCaml)
- [ ] Plugin system for custom type mappings

## Use Cases

- **Cryptography** - OCaml for correctness, Python for integration
- **Data Processing** - OCaml for logic, Python for data science
- **Financial Systems** - OCaml for algorithms, Python for reporting
- **ML Infrastructure** - OCaml for pipelines, Python for training

## CLI Reference

```bash
polyglot-ffi init my-project              # Initialize new project
polyglot-ffi generate src/module.mli      # Generate bindings
polyglot-ffi watch                        # Auto-regenerate on changes
polyglot-ffi check                        # Validate configuration
polyglot-ffi clean                        # Remove generated files
polyglot-ffi --help                       # Get help
```

Run any command with `--help` for full options. See the [CLI documentation](https://polyglotffi.com/) for detailed usage.

## Documentation

- **[Quickstart Guide](docs/quickstart.md)** - Get started in 5 minutes
- **[Type Mapping](docs/type-mapping.md)** - Complete type system reference
- **[Architecture](docs/architecture.md)** - How it works under the hood
- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Contributing](docs/contributing.md)** - Join development

## Contributing & Community

We welcome contributions! See [CONTRIBUTING.md](docs/contributing.md) for development setup, testing requirements, and PR process. Look for `good-first-issue` labels to get started.

**Get in touch:**
- **GitHub**: [chizy7/polyglot-ffi](https://github.com/chizy7/polyglot-ffi)
- **Issues**: [Report bugs or request features](https://github.com/chizy7/polyglot-ffi/issues)
- **Email**: [chizy@chizyhub.com](mailto:chizy@chizyhub.com)
- **Twitter**: [@Chizyization](https://x.com/Chizyization)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with inspiration from [PyO3](https://github.com/PyO3/pyo3), [OCaml-Ctypes](https://github.com/ocamllabs/ocaml-ctypes), and [SWIG](http://www.swig.org/).