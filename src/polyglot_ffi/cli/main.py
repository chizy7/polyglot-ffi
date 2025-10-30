"""
Command-line interface for Polyglot FFI.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
@click.version_option(version="0.4.2", prog_name="polyglot-ffi")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    Polyglot FFI - Automatic FFI bindings generator for polyglot projects.

    Bridge language pairs with zero boilerplate. Generate type-safe,
    memory-safe bindings automatically.
    """
    ctx.ensure_object(dict)
    # Store global verbose for backward compatibility
    ctx.obj["global_verbose"] = verbose


@cli.command()
@click.option("--lang", multiple=True, help="Target languages (e.g., python, rust)")
@click.option("--template", default="library", help="Project template")
@click.option("--interactive", is_flag=True, help="Interactive project setup")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.argument("project_name", required=False)
@click.pass_context
def init(
    ctx: click.Context,
    project_name: Optional[str],
    lang: tuple,
    template: str,
    interactive: bool,
    verbose: bool,
) -> None:
    """
    Initialize a new polyglot FFI project.

    Example:
        polyglot-ffi init my-crypto-lib --lang python --lang rust
    """
    from polyglot_ffi.commands.init import init_project

    # Use local verbose flag OR global verbose flag (support both positions)
    verbose = verbose or ctx.obj.get("global_verbose", False)

    if interactive:
        console.print("[bold blue]Interactive Project Setup[/bold blue]")
        project_name = click.prompt("Project name", default="my-lib")

        target_langs = []
        while True:
            lang_choice = click.prompt(
                "Target language (python/rust/go, or 'done')", default="python"
            )
            if lang_choice.lower() == "done":
                break
            if lang_choice in ("python", "rust", "go"):
                target_langs.append(lang_choice)
            else:
                console.print(f"[red]Unknown language: {lang_choice}[/red]")

        lang = tuple(target_langs) if target_langs else ("python",)

    if not project_name:
        console.print("[red]Error: project_name is required[/red]")
        console.print("Usage: polyglot-ffi init <project_name>")
        sys.exit(1)

    if not lang:
        lang = ("python",)  # Default to Python

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing project...", total=None)

            result = init_project(
                name=project_name, target_langs=list(lang), template=template, verbose=verbose
            )

            progress.update(task, completed=True)

        console.print(f"[green]✓[/green] Project '{project_name}' created!")
        console.print(f"\nNext steps:")
        console.print(f"  cd {project_name}")
        console.print(f"  polyglot-ffi generate")

    except Exception as e:
        # Check if it's a polyglot-ffi error with rich formatting
        from polyglot_ffi.utils.errors import PolyglotFFIError

        if isinstance(e, PolyglotFFIError):
            console.print(e.format_rich())
        else:
            console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("source_file", type=click.Path(exists=True), required=False)
@click.option("-o", "--output", type=click.Path(), help="Output directory")
@click.option("-n", "--name", help="Module name")
@click.option("--target", multiple=True, help="Target languages")
@click.option("--dry-run", is_flag=True, help="Show what would be generated")
@click.option("--force", is_flag=True, help="Force regeneration")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def generate(
    ctx: click.Context,
    source_file: Optional[str],
    output: Optional[str],
    name: Optional[str],
    target: tuple,
    dry_run: bool,
    force: bool,
    verbose: bool,
) -> None:
    """
    Generate FFI bindings from source files.

    Examples:
        polyglot-ffi generate encryption.mli
        polyglot-ffi generate src/crypto.mli -o bindings/ -n crypto
        polyglot-ffi generate --target python --target rust
    """
    from polyglot_ffi.commands.generate import generate_bindings

    # Use local verbose flag OR global verbose flag (support both positions)
    verbose = verbose or ctx.obj.get("global_verbose", False)

    # If no source file provided, look for config
    if not source_file:
        config_path = Path.cwd() / "polyglot.toml"
        if not config_path.exists():
            console.print("[red]Error:[/red] No source file provided and no polyglot.toml found")
            console.print("\nUsage: polyglot-ffi generate <source_file>")
            console.print("   or: polyglot-ffi generate (with polyglot.toml in current directory)")
            sys.exit(1)

        console.print(f"Using config: {config_path}")

    try:
        from rich.progress import BarColumn, TaskProgressColumn, TimeRemainingColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            # Create main task
            main_task = progress.add_task("[cyan]Generating bindings...", total=5)

            # Parse
            progress.update(main_task, description="[cyan]Parsing source file...")
            progress.advance(main_task)

            # Generate (the actual generation happens here)
            result = generate_bindings(
                source_file=source_file,
                output_dir=output,
                module_name=name,
                target_langs=list(target) if target else None,
                dry_run=dry_run,
                force=force,
                verbose=verbose,
            )

            # Update progress for each stage
            progress.update(main_task, description="[cyan]Generated ctypes bindings")
            progress.advance(main_task)

            progress.update(main_task, description="[cyan]Generated C stubs")
            progress.advance(main_task)

            progress.update(main_task, description="[cyan]Generated Python wrappers")
            progress.advance(main_task)

            progress.update(main_task, description="[green]Complete!", completed=5)

        if dry_run:
            console.print("\n[yellow]Dry run - no files written[/yellow]")
            console.print("\nWould generate:")
            for file_path in result.get("files", []):
                console.print(f"  [dim]→[/dim] {file_path}")
        else:
            console.print("\n[green]✓[/green] Bindings generated successfully!")
            console.print("\nGenerated files:")
            for file_path in result.get("files", []):
                console.print(f"  [green]✓[/green] {file_path}")

            console.print(f"\n[dim]Generated {len(result.get('functions', []))} function(s)[/dim]")

    except Exception as e:
        # Check if it's a polyglot-ffi error with rich formatting
        from polyglot_ffi.utils.errors import PolyglotFFIError

        if isinstance(e, PolyglotFFIError):
            console.print(e.format_rich())
        else:
            console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--build", is_flag=True, help="Build after regeneration")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def watch(ctx: click.Context, paths: tuple, build: bool, verbose: bool) -> None:
    """
    Watch source files and auto-regenerate bindings on changes.

    Example:
        polyglot-ffi watch
        polyglot-ffi watch src/*.mli
        polyglot-ffi watch --build
    """
    from polyglot_ffi.commands.watch import watch_files
    from pathlib import Path

    # Use local verbose flag OR global verbose flag (support both positions)
    verbose = verbose or ctx.obj.get("global_verbose", False)

    try:
        watch_files(
            paths=[Path(p) for p in paths],
            build=build,
            verbose=verbose,
        )
    except Exception as e:
        from polyglot_ffi.utils.errors import PolyglotFFIError

        if isinstance(e, PolyglotFFIError):
            console.print(e.format_rich())
        else:
            console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--check-deps", is_flag=True, help="Check dependencies")
@click.option("--lang", help="Check specific language support")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def check(ctx: click.Context, check_deps: bool, lang: Optional[str], verbose: bool) -> None:
    """
    Validate project configuration and dependencies.

    Example:
        polyglot-ffi check
        polyglot-ffi check --check-deps
        polyglot-ffi check --lang rust
    """
    from polyglot_ffi.commands.check import check_project, display_check_results

    # Use local verbose flag OR global verbose flag (support both positions)
    verbose = verbose or ctx.obj.get("global_verbose", False)

    try:
        results = check_project(check_deps=check_deps, lang=lang)
        display_check_results(results)

        # Exit with error code if there are errors
        if results["errors"]:
            sys.exit(1)

    except Exception as e:
        from polyglot_ffi.utils.errors import PolyglotFFIError

        if isinstance(e, PolyglotFFIError):
            console.print(e.format_rich())
        else:
            console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--all", is_flag=True, help="Clean all generated files")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def clean(ctx: click.Context, all: bool, dry_run: bool, verbose: bool) -> None:
    """
    Clean generated files.

    Example:
        polyglot-ffi clean
        polyglot-ffi clean --dry-run
        polyglot-ffi clean --all
    """
    from polyglot_ffi.commands.clean import clean_project

    # Use local verbose flag OR global verbose flag (support both positions)
    verbose = verbose or ctx.obj.get("global_verbose", False)

    try:
        clean_project(all_files=all, dry_run=dry_run)
    except Exception as e:
        from polyglot_ffi.utils.errors import PolyglotFFIError

        if isinstance(e, PolyglotFFIError):
            console.print(e.format_rich())
        else:
            console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
