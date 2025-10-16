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
@click.version_option(version="0.1.0")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    Polyglot FFI - Automatic FFI bindings generator for polyglot projects.

    Bridge language pairs with zero boilerplate. Generate type-safe,
    memory-safe bindings automatically.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--lang", multiple=True, help="Target languages (e.g., python, rust)")
@click.option("--template", default="library", help="Project template")
@click.option("--interactive", is_flag=True, help="Interactive project setup")
@click.argument("project_name", required=False)
@click.pass_context
def init(
    ctx: click.Context, project_name: Optional[str], lang: tuple, template: str, interactive: bool
) -> None:
    """
    Initialize a new polyglot FFI project.

    Example:
        polyglot-ffi init my-crypto-lib --lang python --lang rust
    """
    from polyglot_ffi.commands.init import init_project

    verbose = ctx.obj.get("verbose", False)

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
@click.pass_context
def generate(
    ctx: click.Context,
    source_file: Optional[str],
    output: Optional[str],
    name: Optional[str],
    target: tuple,
    dry_run: bool,
    force: bool,
) -> None:
    """
    Generate FFI bindings from source files.

    Examples:
        polyglot-ffi generate encryption.mli
        polyglot-ffi generate src/crypto.mli -o bindings/ -n crypto
        polyglot-ffi generate --target python --target rust
    """
    from polyglot_ffi.commands.generate import generate_bindings

    verbose = ctx.obj.get("verbose", False)

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
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating bindings...", total=None)

            result = generate_bindings(
                source_file=source_file,
                output_dir=output,
                module_name=name,
                target_langs=list(target) if target else None,
                dry_run=dry_run,
                force=force,
                verbose=verbose,
            )

            progress.update(task, completed=True)

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
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--build", is_flag=True, help="Build after regeneration")
@click.pass_context
def watch(ctx: click.Context, paths: tuple, build: bool) -> None:
    """
    Watch source files and auto-regenerate bindings on changes.

    Example:
        polyglot-ffi watch
        polyglot-ffi watch src/*.mli --build
    """
    verbose = ctx.obj.get("verbose", False)

    console.print("[yellow]Watch mode not yet implemented[/yellow]")
    console.print("This will be available in Phase 3")
    sys.exit(1)


@cli.command()
@click.option("--check-deps", is_flag=True, help="Check dependencies")
@click.option("--lang", help="Check specific language support")
@click.pass_context
def check(ctx: click.Context, check_deps: bool, lang: Optional[str]) -> None:
    """
    Validate project configuration and dependencies.

    Example:
        polyglot-ffi check
        polyglot-ffi check --lang rust
    """
    verbose = ctx.obj.get("verbose", False)

    console.print("[yellow]Check command not yet implemented[/yellow]")
    console.print("This will be available in Phase 3")
    sys.exit(1)


@cli.command()
@click.option("--all", is_flag=True, help="Clean all generated files")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted")
@click.pass_context
def clean(ctx: click.Context, all: bool, dry_run: bool) -> None:
    """
    Clean generated files.

    Example:
        polyglot-ffi clean
        polyglot-ffi clean --all --dry-run
    """
    verbose = ctx.obj.get("verbose", False)

    console.print("[yellow]Clean command not yet implemented[/yellow]")
    console.print("This will be available in Phase 3")
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
