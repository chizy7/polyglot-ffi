# Quick Reference Card

## Installation

```bash
cd /Users/chizy/Desktop/polyglot-ffi
pip install -e ".[dev]"
```

## Common Commands

### Generate Bindings

```bash
# From project root
polyglot-ffi generate src/file.mli -o output/

# With custom name
polyglot-ffi generate src/file.mli -n mylib
```

### Watch Mode (Auto-regenerate)

```bash
# Watch single file
polyglot-ffi watch src/crypto.mli

# Watch multiple files
polyglot-ffi watch src/*.mli

# Watch with auto-build
polyglot-ffi watch --build
```

### Validate Project

```bash
# Check configuration
polyglot-ffi check

# Check dependencies
polyglot-ffi check --deps
```

### Clean Generated Files

```bash
# Dry run (preview)
polyglot-ffi clean --dry-run

# Actually clean
polyglot-ffi clean
```

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src/polyglot_ffi --cov-report=html
```

## Type Mappings

| OCaml | Python | C |
|-------|--------|---|
| `string` | `str` | `char*` |
| `int` | `int` | `int` |
| `float` | `float` | `double` |
| `bool` | `bool` | `int` |
| `unit` | `None` | `void` |
| `'a option` | `Optional[T]` | `void*` |
| `'a list` | `List[T]` | `void*` |
| `'a * 'b` | `Tuple[T, U]` | `void*` |

## Example Workflow

```bash
# 1. Create interface
cat > crypto.mli << 'EOF'
val encrypt : string -> string
val decrypt : string -> string
EOF

# 2. Generate bindings
polyglot-ffi generate crypto.mli -o generated/

# 3. View generated files
ls -la generated/

# 4. Clean up
polyglot-ffi clean
```

## Getting Help

```bash
# Main help
polyglot-ffi --help

# Command-specific help
polyglot-ffi generate --help
polyglot-ffi watch --help
polyglot-ffi check --help
polyglot-ffi clean --help
```

## Documentation Links

- [Architecture](architecture.md)
- [Type Mapping](type-mapping.md)

---

**Version:** 0.3.0 
