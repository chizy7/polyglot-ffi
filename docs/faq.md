# Frequently Asked Questions (FAQ)

## General

### What is Polyglot FFI?

Polyglot FFI is an automatic Foreign Function Interface (FFI) bindings generator that bridges programming languages. It reads OCaml interface files (`.mli`) and generates complete, type-safe, memory-safe bindings for other languages like Python.

### Why use Polyglot FFI?

- **Zero boilerplate:** One command generates 100+ lines of FFI code
- **Type safe:** Preserves type information across languages
- **Memory safe:** Proper GC handling and no memory leaks
- **Time-saving:** Focus on logic, not FFI plumbing

### What languages are supported?

**Currently:**
- OCaml → Python (fully supported)

**Coming soon:**
- OCaml → Rust
- OCaml → Go

### Is it production-ready?

Yes! Version 0.4.3 is production-ready with:
- 262 comprehensive tests (0 failures)
- 88% code coverage
- Full CI/CD pipeline
- Battle-tested on real projects

## Installation & Setup

### How do I install Polyglot FFI?

```bash
pip install polyglot-ffi
```

See [Installation Guide](installation.md) for detailed instructions.

### What are the system requirements?

- **Python 3.8+** (required for Polyglot FFI)
- **OCaml 4.14+** (required to build generated bindings)
- **Dune 3.0+** (build system for OCaml)

### Do I need to know OCaml?

Basic knowledge helps, but you don't need to be an expert. You mainly need to:
1. Write OCaml interface files (`.mli`)
2. Implement the functions in OCaml (`.ml`)
3. Use the generated Python bindings

## Usage

### How do I generate bindings?

```bash
# From an interface file
polyglot-ffi generate my_module.mli

# From a project with polyglot.toml
polyglot-ffi generate
```

### Can I customize the generated code?

Yes, through `polyglot.toml`:

```toml
[source]
language = "ocaml"
interface_file = "src/mylib.mli"

[[targets]]
language = "python"
output_dir = "bindings/python"
module_name = "mylib"
```

### How do I use the generated bindings?

```python
# Import generated module
from generated.mylib_py import my_function

# Use it like normal Python
result = my_function("hello", 42)
```

## Type System

### What OCaml types are supported?

**Primitives:**
- `int`, `float`, `string`, `bool`, `unit`

**Complex types:**
- `'a option` → `Optional[T]`
- `'a list` → `List[T]`
- `'a * 'b` → `Tuple[T1, T2]`
- Records → Python dataclasses
- Variants → Python classes

See [Type Mapping Guide](type-mapping.md) for complete list.

### How are option types handled?

OCaml `option` maps to Python `Optional`:

```ocaml
(* OCaml *)
val find_user : string -> user option
```

```python
# Python
def find_user(name: str) -> Optional[User]:
    ...

user = find_user("john")
if user is not None:
    print(user.name)
```

### How are lists handled?

OCaml lists map to Python lists:

```ocaml
(* OCaml *)
val get_all_users : unit -> user list
```

```python
# Python
def get_all_users() -> List[User]:
    ...

users = get_all_users()
for user in users:
    print(user.name)
```

### Can I use custom types?

Yes! Define types in your `.mli` file:

```ocaml
type user = {
  name: string;
  age: int;
}

val create_user : string -> int -> user
```

The generator creates corresponding Python classes automatically.

## Error Handling

### How are OCaml exceptions handled?

Currently, exceptions cause the C stub to return an error value. We recommend using result types:

```ocaml
type ('a, 'b) result = Ok of 'a | Error of 'b

val process : string -> (user, string) result
```

### What if generation fails?

Check the error message - they include suggestions:

```bash
Error: Unsupported type 'custom_type' in function 'foo'

Suggestion: Define 'custom_type' in the same .mli file
```

### How do I debug generated code?

```bash
# Generate with verbose output
polyglot-ffi generate mylib.mli -v

# Check generated files
ls -la generated/

# Review the generated code
cat generated/stubs.c
cat generated/mylib_py.py
```

## Performance

### How fast is code generation?

Very fast! Benchmark results:
- ~15,000 generations per second
- < 0.3ms for 100 functions
- Parser: < 0.01ms for simple functions

### Does it add runtime overhead?

Minimal overhead:
- Direct C FFI calls (no interpretation)
- Native OCaml performance preserved
- Python wrapper overhead is negligible

### Can I use it for large projects?

Yes! The tool is designed to scale:
- Handles modules with 100+ functions
- Efficient memory management
- Incremental regeneration with watch mode

## Development & Contributing

### How can I contribute?

See [Contributing Guide](contributing.md) for:
- Setting up development environment
- Running tests
- Submitting pull requests
- Code style guidelines

### How do I report bugs?

[Open an issue](https://github.com/chizy7/polyglot-ffi/issues) with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### How do I request features?

[Open an issue](https://github.com/chizy7/polyglot-ffi/issues) with:
- Use case description
- Proposed solution (if you have one)
- Why it would be useful

## Troubleshooting

### "Command not found" error

```bash
# Check if installed
pip show polyglot-ffi

# Try using module directly
python -m polyglot_ffi --version

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### "Module not found" when importing

```bash
# Make sure you built the OCaml library
cd your-project
dune build

# Check the generated .so file exists
ls _build/default/src/*.so
```

### OCaml build fails

```bash
# Make sure OCaml environment is set up
eval $(opam env)

# Install required packages
opam install dune ctypes ctypes-foreign

# Verify OCaml version
ocaml --version  # Should be 4.14+
```

### Types not matching

Make sure type definitions are in the same `.mli` file:

```ocaml
(* Define types first *)
type user = { name: string; age: int }

(* Then use them *)
val create_user : string -> int -> user
```

### Generated code doesn't compile

1. Check the error message
2. Verify your `.mli` syntax is correct
3. Make sure all types are defined
4. Try regenerating with `--force` flag

### Project names with hyphens causing errors

**Issue:** Dune build fails with "invalid module name" or "invalid library name"

**Solution:**
Project names with hyphens (e.g., `my-crypto-lib`) are automatically sanitized in generated code. However, when copying source files to the `generated/` directory for building, you must rename them to use underscores:

```bash
# Don't do this
cp src/my-crypto-lib.ml generated/

# Do this instead
cp src/my-crypto-lib.ml generated/my_crypto_lib.ml
cp src/my-crypto-lib.mli generated/my_crypto_lib.mli
```

This is required because OCaml module names cannot contain hyphens.

### "Library ctypes not found" error

**Issue:** `Error: Library "ctypes" not found` when running `dune build`

**Solution:**
Install the required OCaml dependencies:

```bash
opam install dune ctypes ctypes-foreign
```

These are prerequisites for building the generated bindings, but not for the polyglot-ffi tool itself.

## Best Practices

### Project structure

```
my-project/
├── src/
│   ├── mylib.mli      # Interface (input to polyglot-ffi)
│   └── mylib.ml       # Implementation
├── generated/          # Generated bindings (don't edit!)
├── polyglot.toml      # Configuration
└── dune-project       # OCaml build config
```

### Development workflow

1. Write OCaml interface (`.mli`)
2. Generate bindings: `polyglot-ffi generate`
3. Implement OCaml code (`.ml`)
4. Build: `dune build`
5. Use from Python: `import generated.mylib_py`

### Watch mode for development

```bash
# Auto-regenerate on file changes
polyglot-ffi watch
```

### Testing

Test both sides of the FFI boundary:
- Write OCaml tests with `dune runtest`
- Write Python tests with `pytest`

## Comparison with Alternatives

### vs. Manual FFI code

| Feature | Manual | Polyglot FFI |
|---------|--------|--------------|
| Lines of code | 100+ | 1 command |
| Type safety | Manual | Automatic |
| Memory safety | Error-prone | Guaranteed |
| Maintenance | High | Low |
| Documentation | Manual | Preserved |

### vs. SWIG

| Feature | SWIG | Polyglot FFI |
|---------|------|--------------|
| Language support | Many | OCaml-focused |
| Setup complexity | High | Simple |
| Type preservation | Partial | Full |
| OCaml support | Limited | First-class |

### vs. Pyo3 (Rust)

| Feature | Pyo3 | Polyglot FFI |
|---------|------|--------------|
| Source language | Rust | OCaml |
| Maturity | High | Growing |
| Proc macros | Yes | N/A (different approach) |
| Type system | Strong | Strong |

## Future Plans

### Upcoming features (v1.0)

- Publish to PyPI
- Rust target support
- Go target support
- Bidirectional bindings
- Plugin system

### Long-term roadmap

- IDE/LSP integration
- More language targets (Java, JavaScript)
- Advanced type features (GADTs, functors)
- REPL integration
- Performance optimization

## Getting Help

### Resources

- **Documentation:** https://polyglotffi.com/
- **GitHub:** https://github.com/chizy7/polyglot-ffi
- **Issues:** https://github.com/chizy7/polyglot-ffi/issues
- **Discussions:** https://github.com/chizy7/polyglot-ffi/discussions

### Community

- Report bugs via GitHub Issues
- Ask questions via GitHub Discussions
- Contribute via Pull Requests

---

**Didn't find your answer?** [Ask a question](https://github.com/chizy7/polyglot-ffi/issues/new)
