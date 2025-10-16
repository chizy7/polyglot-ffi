# Configuration

## polyglot.toml Format

```toml
[project]
name = "my-project"
version = "0.1.0"
source_lang = "ocaml"

[languages.ocaml]
source_dir = "src"
build_system = "dune"

[languages.python]
target_dir = "generated"
min_version = "3.8"

[bindings]
auto_discover = true
interfaces = ["src/my-project.mli"]

[generate]
watch = false
verbose = false
```

## Configuration Reference

### [project]

- `name` - Project name (string, required)
- `version` - Project version (string, default: "0.1.0")
- `source_lang` - Source language (string, default: "ocaml")

### [languages.ocaml]

- `source_dir` - OCaml source directory (string, default: "src")
- `build_system` - Build system to use (string, default: "dune")

### [languages.python]

- `target_dir` - Python output directory (string, default: "generated")
- `min_version` - Minimum Python version (string, default: "3.8")

### [bindings]

- `auto_discover` - Auto-discover `.mli` files (boolean, default: true)
- `interfaces` - List of interface files (array of strings)

### [generate]

- `watch` - Enable watch mode (boolean, default: false) - Coming in Phase 3
- `verbose` - Verbose output (boolean, default: false)

## CLI Options

Override configuration with command-line flags:

```bash
# Output directory
polyglot-ffi generate src/module.mli -o custom-output/

# Module name
polyglot-ffi generate src/module.mli -n custom_name

# Target languages
polyglot-ffi generate src/module.mli --target python --target rust

# Dry run
polyglot-ffi generate src/module.mli --dry-run

# Force regeneration
polyglot-ffi generate src/module.mli --force
```

## Environment Variables

Not yet supported - Coming in Phase 3.
