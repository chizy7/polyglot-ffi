# Quick Reference Card

**Quick command reference for Polyglot FFI**

## Installation

```bash
# From PyPI
pip install polyglot-ffi

# From source (development)
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi
pip install -e ".[dev]"
```

## Common Commands

### Initialize Project

```bash
# Create new project
polyglot-ffi init my-project

# Create with specific languages
polyglot-ffi init my-project --lang python --lang rust

# Interactive mode
polyglot-ffi init --interactive
```

### Generate Bindings

```bash
# Basic generation
polyglot-ffi generate src/file.mli

# With output directory
polyglot-ffi generate src/file.mli -o output/

# With custom module name
polyglot-ffi generate src/file.mli -n mylib

# Preview without writing (dry-run)
polyglot-ffi generate src/file.mli --dry-run

# Force regeneration
polyglot-ffi generate src/file.mli --force
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
# Check configuration and setup
polyglot-ffi check

# Check with dependencies
polyglot-ffi check --check-deps

# Check specific language
polyglot-ffi check --lang python
```

### Clean Generated Files

```bash
# Preview what will be deleted (dry-run)
polyglot-ffi clean --dry-run

# Clean generated files
polyglot-ffi clean

# Clean everything including directories
polyglot-ffi clean --all
```

### Check Version

```bash
# Show version
polyglot-ffi --version

# Show help
polyglot-ffi --help
```

### Run Tests (Development)

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/polyglot_ffi --cov-report=html

# Specific test file
pytest tests/unit/test_generators.py -v
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

## Example Workflows

### Quick Start

```bash
# 1. Initialize project
polyglot-ffi init my-crypto-lib
cd my-crypto-lib

# 2. Create OCaml interface
cat > src/crypto.mli << 'EOF'
val encrypt : string -> string
val decrypt : string -> string
EOF

# 3. Generate bindings
polyglot-ffi generate src/crypto.mli

# 4. View generated files
ls -la generated/
```

### Development Workflow

```bash
# 1. Start watch mode
polyglot-ffi watch src/*.mli --build &

# 2. Edit your .mli files
# (bindings auto-regenerate on save)

# 3. Check configuration
polyglot-ffi check --check-deps

# 4. Clean when needed
polyglot-ffi clean --dry-run  # Preview first
polyglot-ffi clean            # Then clean
```

## Getting Help

```bash
# Main help
polyglot-ffi --help

# Command-specific help
polyglot-ffi init --help
polyglot-ffi generate --help
polyglot-ffi watch --help
polyglot-ffi check --help
polyglot-ffi clean --help
```

## Configuration File

**Location:** `polyglot.toml` (project root)

```toml
[project]
name = "my-project"
version = "0.1.0"

[bindings]
source_files = ["src/api.mli"]
output_dir = "generated"

[targets.python]
enabled = true
```

See [Configuration Guide](configuration.md) for full reference.

## Upgrading

```bash
# Upgrade to latest version
pip install --upgrade polyglot-ffi

# Check current version
polyglot-ffi --version
```

See [Installation Guide](installation.md#upgrading) for more options.

## Documentation Links

- [Quickstart Guide](quickstart.md) - Get started in 5 minutes
- [Installation](installation.md) - Setup and upgrade
- [Configuration](configuration.md) - Project configuration
- [Architecture](architecture.md) - System design
- [Type Mapping](type-mapping.md) - Type reference
- [Contributing](contributing.md) - How to contribute
- [Roadmap](ROADMAP.md) - Future plans

## Troubleshooting

```bash
# Command not found?
python -m polyglot_ffi --version

# Permission issues?
pip install --user polyglot-ffi

# Dependencies missing?
polyglot-ffi check --check-deps
```

See [Installation Guide](installation.md#troubleshooting) for more help.

---

**Version:** 0.4.0
**Documentation:** https://chizy7.github.io/polyglot-ffi/
**Repository:** https://github.com/chizy7/polyglot-ffi 
