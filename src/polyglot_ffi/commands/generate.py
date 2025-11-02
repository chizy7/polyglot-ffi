"""
Generate command implementation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from polyglot_ffi.generators.ctypes_gen import CtypesGenerator
from polyglot_ffi.generators.c_stubs_gen import CStubGenerator
from polyglot_ffi.generators.python_gen import PythonGenerator
from polyglot_ffi.generators.dune_gen import DuneGenerator
from polyglot_ffi.parsers.ocaml import parse_mli_file, ParseError
from polyglot_ffi.utils.naming import sanitize_module_name


def _write_file_with_error_handling(file_path: Path, content: str) -> None:
    """Write content to file with better error handling for permissions."""
    try:
        file_path.write_text(content)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied: Cannot write to '{file_path.parent}'.\n"
            f"  Suggestions:\n"
            f"  • Check directory permissions: chmod 755 {file_path.parent}\n"
            f"  • Ensure you have write access to the directory\n"
            f"  • Try running with appropriate permissions"
        ) from e
    except OSError as e:
        # Handle other OS errors (disk full, etc.)
        raise OSError(
            f"Cannot write to '{file_path}': {e}\n"
            f"  Suggestions:\n"
            f"  • Check if the disk has enough space\n"
            f"  • Verify the path is correct\n"
            f"  • Ensure the parent directory exists"
        ) from e


def generate_bindings(
    source_file: Optional[str],
    output_dir: Optional[str],
    module_name: Optional[str],
    target_langs: Optional[List[str]],
    dry_run: bool,
    force: bool,
    verbose: bool,
    ocaml_libraries: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate FFI bindings from a source file.

    Args:
        source_file: Path to source .mli file
        output_dir: Output directory for generated files
        module_name: Module name (derived from filename if not provided)
        target_langs: Target languages (defaults to ['python'])
        dry_run: If True, don't write files
        force: If True, regenerate even if files exist
        verbose: Enable verbose output
        ocaml_libraries: Additional OCaml libraries to link (e.g., ['str', 'unix'])

    Returns:
        Dictionary with generation results
    """
    # Validate inputs
    if not source_file:
        raise ValueError("source_file is required")

    source_path = Path(source_file)
    if not source_path.exists():
        # Provide helpful error message with suggestions
        abs_path = source_path.resolve()
        parent_dir = source_path.parent

        suggestions = []
        suggestions.append(f"Check if the path is correct: {abs_path}")

        if not parent_dir.exists():
            suggestions.append(f"Create the directory: mkdir -p {parent_dir}")

        suggestions.append("Verify the 'dir' and 'files' settings in polyglot.toml")
        suggestions.append("Use an absolute path or ensure working directory is correct")

        error_msg = f"Source file not found: {source_file}\n"
        error_msg += "  Suggestions:\n"
        for suggestion in suggestions:
            error_msg += f"  • {suggestion}\n"

        raise FileNotFoundError(error_msg.rstrip())

    # Determine module name
    if not module_name:
        module_name = source_path.stem

    # Sanitize module name for use in filenames and identifiers
    # Keep original for display, use sanitized for files/identifiers
    safe_module_name = sanitize_module_name(module_name)

    # Determine output directory
    if not output_dir:
        output_dir = "generated"
    output_path = Path(output_dir)

    # Default target languages
    if not target_langs:
        target_langs = ["python"]

    # Parse the source file
    if verbose:
        print(f"Parsing {source_file}...")

    try:
        ir_module = parse_mli_file(source_path)
    except ParseError as e:
        raise ValueError(f"Parse error: {e}")

    if verbose:
        print(f"✓ Found {len(ir_module.functions)} function(s)")
        for func in ir_module.functions:
            print(
                f"  - {func.name}: {' -> '.join(str(p.type) for p in func.params)} -> {func.return_type}"
            )

    # Create output directory
    output_exists = output_path.exists()
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    # Warn if output directory already exists and has files
    if output_exists and not force and verbose:
        existing_files = list(output_path.glob("*"))
        if existing_files:
            print(
                f"Warning: Output directory '{output_path}' already exists with {len(existing_files)} file(s)."
            )
            print(f"  Existing files may be overwritten. Use --force to suppress this warning.")

    generated_files = []

    # Generate OCaml ctypes bindings
    if verbose:
        print("Generating OCaml ctypes bindings...")

    ctypes_gen = CtypesGenerator()
    type_desc = ctypes_gen.generate_type_description(ir_module)
    func_desc = ctypes_gen.generate_function_description(ir_module)

    if not dry_run:
        _write_file_with_error_handling(output_path / "type_description.ml", type_desc)
        _write_file_with_error_handling(output_path / "function_description.ml", func_desc)

    generated_files.extend(
        [str(output_path / "type_description.ml"), str(output_path / "function_description.ml")]
    )

    # Generate C stubs
    if verbose:
        print("Generating C stubs...")

    c_stub_gen = CStubGenerator()
    c_stubs = c_stub_gen.generate_stubs(ir_module, safe_module_name)
    c_header = c_stub_gen.generate_header(ir_module, safe_module_name)

    if not dry_run:
        _write_file_with_error_handling(output_path / f"{safe_module_name}_stubs.c", c_stubs)
        _write_file_with_error_handling(output_path / f"{safe_module_name}_stubs.h", c_header)

    generated_files.extend(
        [
            str(output_path / f"{safe_module_name}_stubs.c"),
            str(output_path / f"{safe_module_name}_stubs.h"),
        ]
    )

    # Generate Dune configuration
    if verbose:
        print("Generating Dune configuration...")

    dune_gen = DuneGenerator()
    dune_config = dune_gen.generate_dune(safe_module_name, ocaml_libraries)
    dune_project = dune_gen.generate_dune_project(safe_module_name)

    if not dry_run:
        _write_file_with_error_handling(output_path / "dune", dune_config)
        _write_file_with_error_handling(output_path / "dune-project", dune_project)

    generated_files.extend([str(output_path / "dune"), str(output_path / "dune-project")])

    # Generate Python wrapper if requested
    if "python" in target_langs:
        if verbose:
            print("Generating Python wrapper...")

        python_gen = PythonGenerator()
        python_wrapper = python_gen.generate(ir_module, safe_module_name)

        if not dry_run:
            _write_file_with_error_handling(
                output_path / f"{safe_module_name}_py.py", python_wrapper
            )

        generated_files.append(str(output_path / f"{safe_module_name}_py.py"))

    return {
        "success": True,
        "module_name": module_name,
        "functions": [f.name for f in ir_module.functions],
        "files": generated_files,
        "output_dir": str(output_path),
    }
