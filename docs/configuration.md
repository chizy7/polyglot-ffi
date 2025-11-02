# Configuration Guide

Complete reference for configuring Polyglot FFI projects.

## Overview

Polyglot FFI uses `polyglot.toml` for project configuration. This file is created automatically by `polyglot-ffi init` and can be customized for your needs.

**Location:** Project root directory

## Quick Example

```toml
[project]
name = "my-crypto-lib"
version = "0.1.0"
description = "FFI bindings for crypto library"
authors = ["Your Name <you@example.com>"]

[bindings]
source_dir = "src"
output_dir = "generated"
source_files = ["src/crypto.mli", "src/hash.mli"]
auto_discover = false

[targets.python]
enabled = true
output_dir = "generated/python"
module_prefix = "crypto"
```

## Configuration Reference

### [project]

Project metadata and general settings.

**Required:**
- `name` (string) - Project name
  ```toml
  name = "my-project"
  ```

**Optional:**
- `version` (string) - Project version (default: `"0.1.0"`)
- `description` (string) - Project description
- `authors` (array) - List of authors
  ```toml
  version = "1.0.0"
  description = "My awesome FFI bindings"
  authors = ["Alice <alice@example.com>", "Bob <bob@example.com>"]
  ```

### [source]

Source language configuration.

**Required:**
- `language` (string) - Source language (currently only `"ocaml"` is supported)

**Optional:**
- `dir` (string) - Source directory (default: `"src"`)
- `files` (array) - List of `.mli` files to process
- `libraries` (array) - Additional OCaml libraries to link (default: `[]`)
  - Supported libraries: `str`, `unix`, `threads`, and others
  - Automatically adds required C library flags (e.g., `-lcamlstr` for `str`)
  - Example: `["str", "unix"]`
- `exclude` (array) - Files to exclude from processing

**Example:**
```toml
[source]
language = "ocaml"
dir = "src"
files = ["api.mli", "utils.mli"]
libraries = ["str", "unix"]  # Link OCaml str and unix libraries
```

### [bindings]

Bindings generation configuration.

**Optional:**
- `source_dir` (string) - Source directory (default: `"src"`)
- `output_dir` (string) - Output directory (default: `"generated"`)
- `source_files` (array) - List of `.mli` files to process
- `auto_discover` (boolean) - Auto-discover `.mli` files (default: `true`)

**Example:**
```toml
[bindings]
source_dir = "src"
output_dir = "generated"
source_files = ["src/api.mli", "src/utils.mli"]
auto_discover = false  # Only process listed files
```

### [targets.python]

Python-specific configuration.

**Optional:**
- `enabled` (boolean) - Enable Python target (default: `true`)
- `output_dir` (string) - Python output directory
- `module_prefix` (string) - Prefix for generated modules
- `min_version` (string) - Minimum Python version (default: `"3.8"`)

**Example:**
```toml
[targets.python]
enabled = true
output_dir = "generated/python"
module_prefix = "mylib"
min_version = "3.9"
```

### [targets.rust]

Rust-specific configuration (future support).

**Optional:**
- `enabled` (boolean) - Enable Rust target (default: `false`)
- `output_dir` (string) - Rust output directory
- `crate_name` (string) - Rust crate name

**Example:**
```toml
[targets.rust]
enabled = true
output_dir = "generated/rust"
crate_name = "mylib_ffi"
```

### [types]

Custom type mappings.

Define custom type mappings for your project:

```toml
[types.binary_data]
ocaml = "bytes"
python = "bytes"
rust = "Vec<u8>"
c = "uint8_t*"

[types.timestamp]
ocaml = "float"
python = "datetime.datetime"
rust = "SystemTime"
c = "double"
```

### [build]

Build system configuration.

**Optional:**
- `system` (string) - Build system (`"dune"`, `"make"`, etc.)
- `auto_build` (boolean) - Auto-build after generation (default: `false`)

**Example:**
```toml
[build]
system = "dune"
auto_build = true
```

## Complete Example

A full-featured configuration file:

```toml
# Project metadata
[project]
name = "crypto-bindings"
version = "0.1.0"
description = "FFI bindings for cryptographic library"
authors = ["Jane Developer <jane@example.com>"]

# Source configuration
[source]
language = "ocaml"
dir = "src"
files = ["crypto.mli", "hash.mli"]
libraries = ["str", "unix"]  # Link OCaml str and unix libraries

# Bindings configuration
[bindings]
source_dir = "src"
output_dir = "generated"
source_files = ["src/crypto.mli", "src/hash.mli"]
auto_discover = false

# Python target
[targets.python]
enabled = true
output_dir = "generated/python"
module_prefix = "crypto"
min_version = "3.8"

# Rust target (future)
[targets.rust]
enabled = false
output_dir = "generated/rust"
crate_name = "crypto_ffi"

# Custom type mappings
[types.binary_data]
ocaml = "bytes"
python = "bytes"
rust = "Vec<u8>"
c = "uint8_t*"

# Build configuration
[build]
system = "dune"
auto_build = false
```

## CLI Override

Command-line options override configuration file settings:

```bash
# Override output directory
polyglot-ffi generate src/module.mli -o custom-output/

# Override module name
polyglot-ffi generate src/module.mli -n custom_name

# Dry run (preview only)
polyglot-ffi generate src/module.mli --dry-run

# Force regeneration
polyglot-ffi generate src/module.mli --force

# Verbose output
polyglot-ffi generate src/module.mli -v
```

## Configuration Patterns

### Single Module Project

```toml
[project]
name = "simple-lib"

[source]
language = "ocaml"
files = ["api.mli"]

[targets.python]
enabled = true
```

### Using OCaml Standard Libraries

If your OCaml code uses standard libraries like `Str`, `Unix`, or `Thread`, you need to specify them:

```toml
[project]
name = "text-processor"

[source]
language = "ocaml"
files = ["text_utils.mli"]
libraries = ["str"]  # For Str module (regex, string operations)

[targets.python]
enabled = true
```

**Common OCaml Libraries:**
- `str` - Regular expressions and advanced string operations
- `unix` - Unix system calls (files, processes, networking)
- `threads` - Multi-threading support

**Why specify libraries?**
When you use OCaml standard libraries, the generated bindings need to link against both the OCaml library and its corresponding C library. Polyglot FFI automatically handles this by:
1. Adding the library to the Dune configuration
2. Including the correct C linker flags (e.g., `-lcamlstr` for `str`)
3. Ensuring the shared library links properly

### Multi-Module Project

```toml
[project]
name = "complex-lib"

[bindings]
source_dir = "src"
auto_discover = true  # Find all .mli files

[targets.python]
enabled = true
module_prefix = "complex"
```

### Development vs Production

**Development (`polyglot.dev.toml`):**
```toml
[bindings]
auto_discover = true

[build]
auto_build = true  # Rebuild on changes
```

**Production (`polyglot.toml`):**
```toml
[bindings]
source_files = ["src/api.mli"]  # Explicit list
auto_discover = false

[build]
auto_build = false
```

Use with: `polyglot-ffi generate --config polyglot.dev.toml`

## Environment Variables

Override configuration with environment variables:

```bash
# Override output directory
export POLYGLOT_FFI_OUTPUT_DIR="custom-output"
polyglot-ffi generate src/module.mli

# Override module name
export POLYGLOT_FFI_MODULE_NAME="custom_name"
polyglot-ffi generate src/module.mli
```

## Validation

Check your configuration:

```bash
# Validate configuration file
polyglot-ffi check

# Validate with dependency check
polyglot-ffi check --check-deps

# Show current configuration
polyglot-ffi check --show-config
```

## Default Configuration

If no `polyglot.toml` exists, these defaults are used:

```toml
[project]
name = "polyglot-project"
version = "0.1.0"

[bindings]
source_dir = "src"
output_dir = "generated"
auto_discover = true

[targets.python]
enabled = true
min_version = "3.8"
```

## Troubleshooting

### Configuration Not Found

```bash
# Create default configuration
polyglot-ffi init

# Or specify config location
polyglot-ffi generate --config path/to/polyglot.toml
```

### Invalid Configuration

```bash
# Check for errors
polyglot-ffi check

# Common issues:
# - Missing required fields (name)
# - Invalid TOML syntax
# - Wrong type for field values
```

### Module Name Conflicts

If generated module names conflict with Python builtins:

```toml
[targets.python]
module_prefix = "my"  # Generates my_crypto instead of crypto
```

## See Also

- [Quickstart Guide](quickstart.md) - Get started quickly
- [Type Mapping](type-mapping.md) - Custom type mappings
- [CLI Reference](quick_reference.md) - Command-line options
- [API Configuration](api/config.md) - Configuration API

---

**Need help?** See [Installation Guide](installation.md#troubleshooting) or [open an issue](https://github.com/chizy7/polyglot-ffi/issues).
