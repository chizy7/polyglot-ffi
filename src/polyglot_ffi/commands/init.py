"""
Init command implementation.
"""

from pathlib import Path
from typing import Dict, List, Any


def init_project(
    name: str, target_langs: List[str], template: str, verbose: bool
) -> Dict[str, Any]:
    """
    Initialize a new polyglot-ffi project.

    Args:
        name: Project name
        target_langs: List of target languages
        template: Project template to use
        verbose: Enable verbose output

    Returns:
        Dictionary with initialization results
    """
    project_path = Path(name)

    if project_path.exists():
        raise ValueError(f"Directory '{name}' already exists")

    # Create project structure
    project_path.mkdir(parents=True)
    (project_path / "src").mkdir()

    # Create polyglot.toml
    config_content = generate_config(name, target_langs)
    (project_path / "polyglot.toml").write_text(config_content)

    # Create example .mli file
    example_mli = f"""(* {name}.mli - Example OCaml interface *)

val greet : string -> string
(** Greet someone by name *)

val add : int -> int -> int
(** Add two integers *)
"""
    (project_path / "src" / f"{name}.mli").write_text(example_mli)

    # Create example .ml implementation
    example_ml = f"""(* {name}.ml - Example implementation *)

let greet name = 
  "Hello, " ^ name ^ "!"

let add x y = 
  x + y

(* Register functions for C callbacks *)
let () =
  Callback.register "greet" greet;
  Callback.register "add" add
"""
    (project_path / "src" / f"{name}.ml").write_text(example_ml)

    # Create README
    readme_content = generate_readme(name, target_langs)
    (project_path / "README.md").write_text(readme_content)

    # Create Makefile
    makefile_content = generate_makefile(name)
    (project_path / "Makefile").write_text(makefile_content)

    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.egg-info/
dist/
build/

# OCaml
*.cmo
*.cmi
*.cma
*.cmx
*.cmxa
*.o
*.a
_build/
*.native
*.byte

# C
*.so
*.a
*.o
*.dylib

# Generated
generated/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
"""
    (project_path / ".gitignore").write_text(gitignore_content)

    return {
        "success": True,
        "project_path": str(project_path),
        "files_created": [
            "polyglot.toml",
            "README.md",
            "Makefile",
            ".gitignore",
            f"src/{name}.mli",
            f"src/{name}.ml",
        ],
    }


def generate_config(name: str, target_langs: List[str]) -> str:
    """Generate polyglot.toml configuration file."""
    langs_str = ", ".join(f'"{lang}"' for lang in target_langs)

    return f"""# Polyglot FFI Configuration

[project]
name = "{name}"
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
interfaces = [
    "src/{name}.mli"
]

[generate]
watch = false
verbose = false
"""


def generate_readme(name: str, target_langs: List[str]) -> str:
    """Generate README.md file."""
    return f"""# {name}

Auto-generated FFI bindings project using Polyglot FFI.

## Quick Start

```bash
# Generate bindings
polyglot-ffi generate

# Or use the Makefile
make generate

# Build OCaml library
make build

# Test from Python
make test
```

## Project Structure

```
{name}/
├── polyglot.toml         # Polyglot FFI configuration
├── src/
│   ├── {name}.mli        # OCaml interface (edit this)
│   └── {name}.ml         # OCaml implementation (edit this)
└── generated/            # Generated bindings (don't edit)
    ├── type_description.ml
    ├── function_description.ml
    ├── {name}_stubs.c
    ├── {name}_stubs.h
    ├── dune
    ├── dune-project
    └── {name}_py.py      # Python wrapper
```

## Development Workflow

1. Edit `src/{name}.mli` to define your API
2. Run `polyglot-ffi generate` to generate bindings
3. Implement functions in `src/{name}.ml`
4. Build with `make build`
5. Use from Python:

```python
from {name}_py import greet, add

print(greet("World"))  # Hello, World!
print(add(2, 3))       # 5
```

## Generated Files

Don't edit files in `generated/` - they are auto-generated.
Run `polyglot-ffi generate` to regenerate after changing `.mli` files.

## Learn More

- [Polyglot FFI Documentation](https://github.com/yourorg/polyglot-ffi)
- [OCaml Ctypes](https://github.com/ocamllabs/ocaml-ctypes)
"""


def generate_makefile(name: str) -> str:
    """Generate Makefile for the project."""
    return f"""# Makefile for {name}

.PHONY: generate build clean test

# Generate bindings from .mli files
generate:
	@echo "Generating bindings..."
	polyglot-ffi generate src/{name}.mli -o generated -n {name}
	@echo "✓ Bindings generated"

# Build OCaml library
build: generate
	@echo "Building OCaml library..."
	cd generated && dune build
	@echo "✓ Build complete"

# Clean generated files
clean:
	@echo "Cleaning..."
	rm -rf generated/
	@echo "✓ Clean complete"

# Test from Python
test: build
	@echo "Testing Python bindings..."
	cd generated && python3 -c "from {name}_py import greet, add; print(greet('Test')); print(add(2, 3))"
	@echo "✓ Tests passed"

# Help
help:
	@echo "Available targets:"
	@echo "  make generate  - Generate FFI bindings"
	@echo "  make build     - Build OCaml library"
	@echo "  make clean     - Clean generated files"
	@echo "  make test      - Test Python bindings"
"""
