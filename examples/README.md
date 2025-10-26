# Polyglot FFI Examples

Real-world examples demonstrating Polyglot FFI capabilities from beginner to advanced.

## Example Projects

### [1. Simple Math](simple-math/) - **Beginner**

Basic arithmetic functions demonstrating primitive types.

**Demonstrates:**
- Primitive types (int, float)
- Multiple parameters
- Simple function signatures
- Basic project structure

**Best for:** First-time users learning the basics

```ocaml
val add : int -> int -> int
val multiply : float -> float -> float
```

---

### [2. Crypto Library](crypto-lib/) - **Intermediate**

Cryptography functions with option types for error handling.

**Demonstrates:**
- Option types (`'a option`)
- Error handling with None/Some
- Null safety patterns
- Real-world use case

**Best for:** Understanding option types and error handling

```ocaml
val decrypt : string -> string -> string option
val find_key : string -> string option
```

---

### [3. Data Processing](data-processing/) - **Intermediate**

List operations and functional transformations.

**Demonstrates:**
- List types (`'a list`)
- Functional programming (map, filter, fold)
- Complex list operations
- Data pipelines

**Best for:** Working with collections and data transformations

```ocaml
val filter_by_length : int -> string list -> string list
val map_lengths : string list -> int list
val find_max : int list -> int option
```

---

## Quick Start

### Running an Example

```bash
# Navigate to example directory
cd examples/simple-math

# Generate bindings
polyglot-ffi generate src/math.mli --output generated --name math

# Build OCaml library (if Makefile provided)
make build

# Run Python example
python example.py
```

### Using Watch Mode

```bash
# Auto-regenerate on changes
cd examples/crypto-lib
polyglot-ffi watch
```

## Learning Path

### Path 1: Complete Beginner

1. **[simple-math](simple-math/)** - Learn the basics
   - Understand primitive types
   - See how OCaml maps to Python
   - Run your first example

2. **[crypto-lib](crypto-lib/)** - Add complexity
   - Learn option types
   - Handle errors gracefully
   - Use type hints effectively

3. **[data-processing](data-processing/)** - Master lists
   - Work with collections
   - Build data pipelines
   - Apply functional patterns

### Path 2: Specific Feature

**Learning Option Types?**
→ Start with [crypto-lib](crypto-lib/)

**Learning List Types?**
→ Start with [data-processing](data-processing/)

**Just exploring?**
→ Start with [simple-math](simple-math/)

## Example Structure

Each example follows the same structure:

```
example-name/
├── README.md              # Comprehensive guide
├── polyglot.toml          # Project configuration
├── src/
│   ├── module.mli         # OCaml interface
│   └── module.ml          # OCaml implementation (reference)
├── generated/             # Auto-generated bindings
│   ├── type_description.ml
│   ├── function_description.ml
│   ├── stubs.c
│   ├── stubs.h
│   ├── module_py.py
│   └── dune
└── example.py             # Python usage demonstration
```

## Type Coverage

| Type | Example | Complexity |
|------|---------|------------|
| Primitives (`int`, `float`, `string`, `bool`) | [simple-math](simple-math/) | ⭐ Beginner |
| Option types (`'a option`) | [crypto-lib](crypto-lib/) | ⭐⭐ Intermediate |
| List types (`'a list`) | [data-processing](data-processing/) | ⭐⭐ Intermediate |
| Tuples (`'a * 'b`) | Coming soon | ⭐⭐ Intermediate |
| Records | Coming soon | ⭐⭐⭐ Advanced |
| Variants | Coming soon | ⭐⭐⭐ Advanced |

## Common Patterns

### Error Handling with Options

```python
# Pattern from crypto-lib example
result = decrypt(ciphertext, key)
if result is not None:
    process(result)
else:
    handle_error()
```

### Data Pipelines

```python
# Pattern from data-processing example
def process_pipeline(items: List[str]) -> int:
    filtered = filter_by_length(5, items)
    lengths = map_lengths(filtered)
    return sum(lengths)
```

### Default Values

```python
# Pattern from crypto-lib example
key = find_key("production") or "default-key"
```

## Prerequisites

### For All Examples

- Python 3.8+
- Polyglot FFI installed (`pip install polyglot-ffi`)
- OCaml 4.14+ (for building examples)
- Dune 3.0+ (build system)

### Optional

- Make (for using Makefiles)
- Type checker (mypy, pyright) for type checking

## Installation

```bash
# Install Polyglot FFI
pip install polyglot-ffi

# Clone examples
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi/examples

# Try an example
cd simple-math
polyglot-ffi generate src/math.mli
```

## Troubleshooting

### Common Issues

**Issue**: `polyglot-ffi: command not found`
```bash
# Solution: Install polyglot-ffi
pip install polyglot-ffi
```

**Issue**: `No module named 'math_py'`
```bash
# Solution: Add generated/ to Python path or run from project root
export PYTHONPATH=generated:$PYTHONPATH
```

**Issue**: `OSError: libmath.so: cannot open shared object file`
```bash
# Solution: Build the OCaml library first
make build
# Or manually:
dune build
cp _build/default/src/math.so generated/
```

## Contributing Examples

Have a great example? We'd love to include it!

**Good example characteristics:**
- Demonstrates a specific feature clearly
- Includes comprehensive README
- Has working code (tested)
- Follows the standard structure
- Includes real-world use case

**To contribute:**
1. Create your example in a new directory
2. Follow the standard structure
3. Test thoroughly
4. Submit a pull request

## Resources

- [Polyglot FFI Documentation](https://docs.polyglot-ffi.dev)
- [API Reference](../docs/api/)
- [Type Mapping Guide](../docs/type-mapping.md)
- [Configuration Reference](../docs/configuration.md)

## Next Steps

After completing the examples:

1. **Build Your Own Project**
   - Use `polyglot-ffi init my-project`
   - Define your OCaml interface
   - Generate and use bindings

2. **Explore Advanced Features**
   - Custom type mappings
   - Multiple target languages
   - Watch mode for development

3. **Contribute**
   - Report issues
   - Suggest improvements
   - Share your own examples

---

**Happy coding!**

Stop writing FFI boilerplate. Start building amazing things.
