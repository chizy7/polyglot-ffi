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


def generate_bindings(
    source_file: Optional[str],
    output_dir: Optional[str],
    module_name: Optional[str],
    target_langs: Optional[List[str]],
    dry_run: bool,
    force: bool,
    verbose: bool,
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

    Returns:
        Dictionary with generation results
    """
    # Validate inputs
    if not source_file:
        raise ValueError("source_file is required")

    source_path = Path(source_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    # Determine module name
    if not module_name:
        module_name = source_path.stem

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
    if not dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Generate OCaml ctypes bindings
    if verbose:
        print("Generating OCaml ctypes bindings...")

    ctypes_gen = CtypesGenerator()
    type_desc = ctypes_gen.generate_type_description(ir_module)
    func_desc = ctypes_gen.generate_function_description(ir_module)

    if not dry_run:
        (output_path / "type_description.ml").write_text(type_desc)
        (output_path / "function_description.ml").write_text(func_desc)

    generated_files.extend(
        [str(output_path / "type_description.ml"), str(output_path / "function_description.ml")]
    )

    # Generate C stubs
    if verbose:
        print("Generating C stubs...")

    c_stub_gen = CStubGenerator()
    c_stubs = c_stub_gen.generate_stubs(ir_module, module_name)
    c_header = c_stub_gen.generate_header(ir_module, module_name)

    if not dry_run:
        (output_path / f"{module_name}_stubs.c").write_text(c_stubs)
        (output_path / f"{module_name}_stubs.h").write_text(c_header)

    generated_files.extend(
        [str(output_path / f"{module_name}_stubs.c"), str(output_path / f"{module_name}_stubs.h")]
    )

    # Generate Dune configuration
    if verbose:
        print("Generating Dune configuration...")

    dune_gen = DuneGenerator()
    dune_config = dune_gen.generate_dune(module_name)
    dune_project = dune_gen.generate_dune_project(module_name)

    if not dry_run:
        (output_path / "dune").write_text(dune_config)
        (output_path / "dune-project").write_text(dune_project)

    generated_files.extend([str(output_path / "dune"), str(output_path / "dune-project")])

    # Generate Python wrapper if requested
    if "python" in target_langs:
        if verbose:
            print("Generating Python wrapper...")

        python_gen = PythonGenerator()
        python_wrapper = python_gen.generate(ir_module, module_name)

        if not dry_run:
            (output_path / f"{module_name}_py.py").write_text(python_wrapper)

        generated_files.append(str(output_path / f"{module_name}_py.py"))

    return {
        "success": True,
        "module_name": module_name,
        "functions": [f.name for f in ir_module.functions],
        "files": generated_files,
        "output_dir": str(output_path),
    }
