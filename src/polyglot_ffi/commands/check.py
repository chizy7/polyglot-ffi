"""
Check command implementation.

Validate project configuration and dependencies.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

from rich.console import Console
from rich.table import Table

from polyglot_ffi.core.config import load_config, validate_config
from polyglot_ffi.utils.errors import ConfigurationError, ValidationError


console = Console()


def check_dependencies(lang: Optional[str] = None) -> Dict[str, bool]:
    """
    Check if required dependencies are available.

    Args:
        lang: Specific language to check (None for all)

    Returns:
        Dictionary of dependency -> available status
    """
    deps = {}

    # OCaml dependencies
    if lang is None or lang == "ocaml":
        deps["ocaml"] = shutil.which("ocaml") is not None
        deps["dune"] = shutil.which("dune") is not None
        deps["opam"] = shutil.which("opam") is not None

    # Python dependencies
    if lang is None or lang == "python":
        deps["python3"] = shutil.which("python3") is not None
        deps["pip"] = shutil.which("pip") is not None

    # Rust dependencies
    if lang is None or lang == "rust":
        deps["cargo"] = shutil.which("cargo") is not None
        deps["rustc"] = shutil.which("rustc") is not None

    return deps


def check_project(check_deps: bool = False, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate project configuration and dependencies.

    Args:
        check_deps: Whether to check dependencies
        lang: Specific language to check

    Returns:
        Dictionary with check results
    """
    results = {
        "config_valid": False,
        "warnings": [],
        "errors": [],
        "dependencies": {},
    }

    # Look for config file
    config_path = Path.cwd() / "polyglot.toml"

    if not config_path.exists():
        results["errors"].append("No polyglot.toml found in current directory")
        results["warnings"].append("Run 'polyglot-ffi init' to create a project")
        return results

    # Load and validate config
    try:
        config = load_config(config_path)
        results["config_valid"] = True
        results["config"] = config

        # Run additional validation
        warnings = validate_config(config)
        results["warnings"].extend(warnings)

    except ConfigurationError as e:
        results["errors"].append(str(e))
        if e.suggestions:
            results["warnings"].extend(e.suggestions)
        return results

    # Check dependencies if requested
    if check_deps:
        deps = check_dependencies(lang)
        results["dependencies"] = deps

        # Add warnings for missing dependencies
        missing_deps = [dep for dep, available in deps.items() if not available]
        if missing_deps:
            results["warnings"].append(f"Missing dependencies: {', '.join(missing_deps)}")

    return results


def display_check_results(results: Dict[str, Any]) -> None:
    """
    Display check results in a nice format.

    Args:
        results: Results from check_project()
    """
    # Configuration status
    if results["config_valid"]:
        console.print("[green]✓[/green] Configuration is valid")

        config = results.get("config")
        if config:
            console.print(
                f"\n[bold]Project:[/bold] {config.project.name} v{config.project.version}"
            )
            console.print(
                f"[bold]Source:[/bold] {config.source.language} ({len(config.source.files)} file(s))"
            )

            # Targets table
            if config.targets:
                console.print(f"\n[bold]Targets:[/bold]")
                table = Table(show_header=True)
                table.add_column("Language")
                table.add_column("Output Directory")
                table.add_column("Status")

                for target in config.targets:
                    status = "[green]enabled[/green]" if target.enabled else "[dim]disabled[/dim]"
                    table.add_row(target.language, target.output_dir, status)

                console.print(table)

    else:
        console.print("[red]✗[/red] Configuration is invalid")

    # Dependencies
    if results["dependencies"]:
        console.print(f"\n[bold]Dependencies:[/bold]")
        table = Table(show_header=True)
        table.add_column("Tool")
        table.add_column("Status")

        for dep, available in results["dependencies"].items():
            status = "[green]✓ installed[/green]" if available else "[red]✗ missing[/red]"
            table.add_row(dep, status)

        console.print(table)

    # Warnings
    if results["warnings"]:
        console.print(f"\n[bold yellow]Warnings:[/bold yellow]")
        for warning in results["warnings"]:
            console.print(f"  [yellow]⚠[/yellow] {warning}")

    # Errors
    if results["errors"]:
        console.print(f"\n[bold red]Errors:[/bold red]")
        for error in results["errors"]:
            console.print(f"  [red]✗[/red] {error}")

    # Summary
    console.print()
    if results["errors"]:
        console.print("[red]✗ Check failed[/red]")
        return

    if results["warnings"]:
        console.print("[yellow]⚠ Check completed with warnings[/yellow]")
        return

    console.print("[green]✓ All checks passed![/green]")
