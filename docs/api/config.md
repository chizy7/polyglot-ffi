# Configuration API

The configuration module handles loading, validating, and managing project configuration from `polyglot.toml` files.

## Overview

Configuration provides:

- **TOML parsing**: Load configuration from files
- **Validation**: Ensure configuration is valid
- **Type safety**: Pydantic models for configuration
- **Defaults**: Sensible default values
- **Error reporting**: Clear error messages

## Configuration Models

::: polyglot_ffi.core.config.PolyglotConfig
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

::: polyglot_ffi.core.config.SourceConfig
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

::: polyglot_ffi.core.config.TargetConfig
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Loading Configuration

### From File

```python
from pathlib import Path
from polyglot_ffi.core.config import load_config

# Load from default location (./polyglot.toml)
config = load_config()

# Load from specific path
config = load_config(Path("custom.toml"))

# Access configuration
print(f"Project: {config.name}")
print(f"Targets: {', '.join(t.language for t in config.targets)}")
```

### Creating Configuration

```python
from polyglot_ffi.core.config import (
    ProjectConfig, BindingsConfig, TargetConfig
)

# Create configuration programmatically
config = ProjectConfig(
    name="my-project",
    version="0.1.0",
    description="My FFI bindings",
    bindings=BindingsConfig(
        source_dir="src",
        output_dir="generated",
        source_files=["src/api.mli"]
    ),
    targets=[
        TargetConfig(
            language="python",
            enabled=True,
            output_dir="generated/python"
        )
    ]
)
```

### Saving Configuration

```python
# Convert to dictionary
config_dict = config.dict()

# Save to TOML
import toml
with open("polyglot.toml", "w") as f:
    toml.dump(config_dict, f)
```

## Validation

### Automatic Validation

Configuration is validated automatically on load:

```python
from polyglot_ffi.core.config import load_config
from polyglot_ffi.utils.errors import ConfigurationError

try:
    config = load_config(Path("polyglot.toml"))
except ConfigurationError as e:
    print(f"Invalid configuration: {e.message}")
    if e.suggestions:
        print(f"Suggestions: {', '.join(e.suggestions)}")
```

### Manual Validation

```python
from polyglot_ffi.core.config import validate_config

# Validate loaded configuration
errors = validate_config(config)

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid!")
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Missing name | No project name specified | Add `name = "project-name"` |
| Invalid language | Unsupported target language | Use: python, rust, or go |
| Source file not found | .mli file doesn't exist | Check source_files paths |
| Duplicate targets | Same language listed twice | Remove duplicate |
| No enabled targets | All targets disabled | Enable at least one target |

## Configuration Structure

### Complete Example

```toml
# polyglot.toml

# Project metadata
[project]
name = "crypto-bindings"
version = "0.1.0"
description = "FFI bindings for crypto library"
authors = ["Jane Developer <jane@example.com>"]

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

# Rust target
[targets.rust]
enabled = true
output_dir = "generated/rust"

# Custom type mappings
[types.binary_data]
ocaml = "bytes"
python = "bytes"
rust = "Vec<u8>"
c = "uint8_t*"
```

### Minimal Example

```toml
[project]
name = "simple-project"

[bindings]
source_files = ["src/api.mli"]

[targets.python]
enabled = true
```

## Default Values

The configuration system provides sensible defaults:

```python
# Default bindings config
bindings = BindingsConfig(
    source_dir="src",          # Default source directory
    output_dir="generated",    # Default output directory
    source_files=[],           # No default files
    auto_discover=True         # Auto-discover .mli files
)

# Default target config
target = TargetConfig(
    language="python",
    enabled=True,              # Enabled by default
    output_dir=None,          # Uses bindings.output_dir
    module_prefix=None        # No prefix by default
)
```

## Environment Variables

Override configuration with environment variables:

```python
import os
from polyglot_ffi.core.config import load_config

# Override config file location
os.environ["POLYGLOT_FFI_CONFIG"] = "/path/to/custom.toml"
config = load_config()

# Override output directory
os.environ["POLYGLOT_FFI_OUTPUT"] = "/tmp/bindings"
```

## Accessing Configuration Values

```python
config = load_config()

# Project information
print(f"Name: {config.name}")
print(f"Version: {config.version}")
print(f"Description: {config.description}")

# Bindings settings
print(f"Source dir: {config.bindings.source_dir}")
print(f"Output dir: {config.bindings.output_dir}")
print(f"Source files: {config.bindings.source_files}")

# Targets
for target in config.targets:
    print(f"Target: {target.language}")
    print(f"  Enabled: {target.enabled}")
    print(f"  Output: {target.output_dir}")

# Custom types
if hasattr(config, 'types'):
    for type_name, mappings in config.types.items():
        print(f"Custom type: {type_name}")
        for lang, target_type in mappings.items():
            print(f"  {lang}: {target_type}")
```

## Filtering Targets

```python
# Get only enabled targets
enabled_targets = [t for t in config.targets if t.enabled]

# Get specific language target
python_target = next(
    (t for t in config.targets if t.language == "python"),
    None
)

if python_target:
    print(f"Python output: {python_target.output_dir}")
```

## Creating Default Configuration

```python
from polyglot_ffi.core.config import create_default_config

# Create default config for a new project
config = create_default_config(
    name="my-project",
    target_langs=["python", "rust"]
)

# Save to file
import toml
with open("polyglot.toml", "w") as f:
    toml.dump(config.dict(), f)
```

## Complete Usage Example

```python
from pathlib import Path
from polyglot_ffi.core.config import load_config, validate_config
from polyglot_ffi.utils.errors import ConfigurationError

def setup_project():
    """Load and validate project configuration."""
    try:
        # Load configuration
        config_path = Path("polyglot.toml")
        config = load_config(config_path)

        # Validate
        errors = validate_config(config)
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  ✗ {error}")
            return None

        print(f"✓ Loaded configuration for {config.name}")

        # Check source files exist
        for source_file in config.bindings.source_files:
            if not Path(source_file).exists():
                print(f"✗ Source file not found: {source_file}")
                return None

        # Check enabled targets
        enabled = [t for t in config.targets if t.enabled]
        if not enabled:
            print("✗ No enabled targets")
            return None

        print(f"✓ Found {len(enabled)} enabled target(s):")
        for target in enabled:
            print(f"  - {target.language}")

        return config

    except ConfigurationError as e:
        print(f"✗ Configuration error: {e.message}")
        if e.suggestions:
            print("Suggestions:")
            for suggestion in e.suggestions:
                print(f"  - {suggestion}")
        return None

    except FileNotFoundError:
        print("✗ Configuration file not found: polyglot.toml")
        print("Run 'polyglot-ffi init' to create a new project")
        return None

# Use it
if __name__ == "__main__":
    config = setup_project()
    if config:
        print("\n✓ Configuration valid and ready!")
```

## See Also

- [Configuration Guide](../configuration.md) - Detailed configuration reference
- [Quick Reference](../quick_reference.md) - Quick configuration examples
