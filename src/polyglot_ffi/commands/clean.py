"""
Clean command implementation.

Remove generated files.
"""

from pathlib import Path
from typing import List, Set
import shutil

from rich.console import Console

from polyglot_ffi.core.config import load_config
from polyglot_ffi.utils.errors import ConfigurationError


console = Console()


# Common generated file patterns
GENERATED_PATTERNS = [
    "*_stubs.c",
    "*_stubs.h",
    "*_py.py",
    "type_description.ml",
    "function_description.ml",
    "dune",
    "dune-project",
    "*.so",
    "*.dylib",
    "*.dll",
    "__pycache__",
    "*.pyc",
    ".dune",
]


def find_generated_files(output_dirs: List[Path], all_files: bool = False) -> Set[Path]:
    """
    Find all generated files in output directories.

    Args:
        output_dirs: List of output directories to search
        all_files: If True, include all files; otherwise only match patterns

    Returns:
        Set of file paths to clean
    """
    files_to_clean: Set[Path] = set()

    for output_dir in output_dirs:
        if not output_dir.exists():
            continue

        if all_files:
            # Include entire directory
            files_to_clean.add(output_dir)
        else:
            # Match specific patterns
            for pattern in GENERATED_PATTERNS:
                files_to_clean.update(output_dir.glob(pattern))
                # Also check recursively for some patterns
                if pattern in ["__pycache__", "*.pyc"]:
                    files_to_clean.update(output_dir.rglob(pattern))

    return files_to_clean


def clean_files(files: Set[Path], dry_run: bool = False) -> int:
    """
    Clean (delete) specified files.

    Args:
        files: Set of file paths to delete
        dry_run: If True, don't actually delete

    Returns:
        Number of files cleaned
    """
    count = 0

    for file_path in sorted(files):
        if not file_path.exists():
            continue

        if dry_run:
            if file_path.is_dir():
                console.print(f"  [dim]Would remove directory:[/dim] {file_path}")
            else:
                console.print(f"  [dim]Would remove file:[/dim] {file_path}")
        else:
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    console.print(f"  [red]✗[/red] Removed directory: {file_path}")
                else:
                    file_path.unlink()
                    console.print(f"  [red]✗[/red] Removed file: {file_path}")
                count += 1
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Failed to remove {file_path}: {e}")

    return count


def clean_project(all_files: bool = False, dry_run: bool = False) -> int:
    """
    Clean generated files from the project.

    Args:
        all_files: If True, remove all generated directories
        dry_run: If True, don't actually delete files

    Returns:
        Number of files cleaned
    """
    # Try to load config to find output directories
    config_path = Path.cwd() / "polyglot.toml"
    output_dirs: List[Path] = []

    if config_path.exists():
        try:
            config = load_config(config_path)
            # Get output directories from config
            for target in config.targets:
                output_dir = Path(target.output_dir)
                if not output_dir.is_absolute():
                    output_dir = Path.cwd() / output_dir
                output_dirs.append(output_dir)

        except ConfigurationError:
            # If config fails to load, fall back to default
            pass

    # Also include default "generated" directory
    default_output = Path.cwd() / "generated"
    if default_output not in output_dirs:
        output_dirs.append(default_output)

    # Find files to clean
    files = find_generated_files(output_dirs, all_files=all_files)

    if not files:
        console.print("[dim]No generated files found[/dim]")
        return 0

    # Display what will be cleaned
    if dry_run:
        console.print(f"[yellow]Dry run - would clean {len(files)} item(s):[/yellow]\n")
    else:
        console.print(f"[yellow]Cleaning {len(files)} item(s)...[/yellow]\n")

    # Clean files
    count = clean_files(files, dry_run=dry_run)

    # Summary
    console.print()
    if dry_run:
        console.print(f"[dim]Dry run complete - {len(files)} item(s) would be removed[/dim]")
    else:
        console.print(f"[green]✓[/green] Cleaned {count} item(s)")

    return count
