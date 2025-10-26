"""
Watch command implementation.

Watch source files and auto-regenerate bindings on changes.
"""

import time
from pathlib import Path
from typing import List, Set, Optional
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from rich.console import Console
from rich.live import Live
from rich.table import Table

from polyglot_ffi.core.config import load_config
from polyglot_ffi.commands.generate import generate_bindings
from polyglot_ffi.utils.errors import ConfigurationError


console = Console()


class SourceFileHandler(FileSystemEventHandler):
    """Handler for source file changes.

    Accepts an optional debounce_seconds to control the debounce interval (default 0.5s)
    and an optional time_provider callable (defaults to time.time) to make testing
    deterministic without relying on wall-clock sleeps.
    """

    def __init__(
        self,
        watched_files: Set[Path],
        on_change_callback,
        debounce_seconds: float = 0.5,
        time_provider=None,
    ):
        super().__init__()
        self.watched_files = {f.resolve() for f in watched_files}
        self.on_change_callback = on_change_callback
        self.last_modified = {}
        self.debounce_seconds = debounce_seconds
        # time_provider is a callable that returns current time in seconds.
        # Default to time.time for production; tests can inject a fake provider.
        self._time_provider = time_provider or time.time

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path).resolve()

        # Check if this is a file we're watching
        if file_path not in self.watched_files:
            return

        # Debounce: ignore if modified very recently
        current_time = self._time_provider()
        last_time = self.last_modified.get(file_path, 0)

        if current_time - last_time < self.debounce_seconds:
            return

        self.last_modified[file_path] = current_time

        # Trigger callback
        self.on_change_callback(file_path)


def watch_files(
    paths: List[Path],
    build: bool = False,
    verbose: bool = False,
) -> None:
    """
    Watch source files and regenerate bindings on changes.

    Args:
        paths: List of paths to watch (files or directories)
        build: Whether to run build after regeneration
        verbose: Enable verbose output
    """
    # Load configuration to find source files
    config_path = Path.cwd() / "polyglot.toml"
    watched_files: Set[Path] = set()

    if config_path.exists():
        try:
            config = load_config(config_path)

            # Add source files from config
            source_dir = Path(config.source.dir or ".")
            for source_file in config.source.files:
                file_path = source_dir / source_file
                if file_path.exists():
                    watched_files.add(file_path.resolve())

            # Also watch the config file itself
            watched_files.add(config_path.resolve())

        except ConfigurationError as e:
            console.print(f"[red]Error loading config:[/red] {e}")
            return

    # Add explicitly provided paths
    if paths:
        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                watched_files.add(path_obj.resolve())
            elif path_obj.is_dir():
                # Watch all .mli files in directory
                watched_files.update(path_obj.glob("*.mli"))

    if not watched_files:
        console.print("[yellow]No files to watch[/yellow]")
        console.print("Either:")
        console.print("  1. Create a polyglot.toml configuration")
        console.print("  2. Provide paths: polyglot-ffi watch src/*.mli")
        return

    # Statistics
    stats = {
        "regenerations": 0,
        "successes": 0,
        "failures": 0,
        "last_change": None,
        "last_file": None,
    }

    def on_file_change(file_path: Path) -> None:
        """Callback when a file changes."""
        stats["last_change"] = time.strftime("%H:%M:%S")
        stats["last_file"] = str(file_path.name)

        console.print(f"\n[yellow]Change detected:[/yellow] {file_path.name}")
        console.print(f"[dim]Regenerating bindings...[/dim]")

        try:
            # Regenerate bindings
            result = generate_bindings(
                source_file=str(file_path) if file_path.suffix == ".mli" else None,
                output_dir=None,
                module_name=None,
                target_langs=None,
                dry_run=False,
                force=True,
                verbose=verbose,
            )

            stats["regenerations"] += 1
            stats["successes"] += 1

            console.print(f"[green]✓[/green] Regenerated {len(result['files'])} file(s)")

            # Run build if requested
            if build and result["success"]:
                console.print("[dim]Running build...[/dim]")
                try:
                    subprocess.run(["dune", "build"], check=True, capture_output=not verbose)
                    console.print("[green]✓[/green] Build successful")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]✗[/red] Build failed: {e}")
                except FileNotFoundError:
                    console.print("[yellow]⚠[/yellow] dune not found, skipping build")

        except Exception as e:
            stats["regenerations"] += 1
            stats["failures"] += 1
            console.print(f"[red]✗[/red] Generation failed: {e}")

    # Create file system observer
    event_handler = SourceFileHandler(watched_files, on_file_change)
    observer = Observer()

    # Watch directories containing the files
    watched_dirs: Set[Path] = {f.parent for f in watched_files}
    for directory in watched_dirs:
        observer.schedule(event_handler, str(directory), recursive=False)

    # Start watching
    observer.start()

    # Display initial status
    console.print(f"\n[bold green]Watch mode started[/bold green]")
    console.print(f"Watching {len(watched_files)} file(s):\n")
    for file in sorted(watched_files):
        console.print(f"  [cyan]→[/cyan] {file}")

    console.print(f"\n[dim]Press Ctrl+C to stop[/dim]\n")

    # Keep running and display live stats
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[yellow]Stopping watch mode...[/yellow]")

    observer.join()

    # Display final statistics
    console.print("\n[bold]Watch Statistics:[/bold]")
    console.print(f"  Total regenerations: {stats['regenerations']}")
    console.print(f"  [green]Successes:[/green] {stats['successes']}")
    console.print(f"  [red]Failures:[/red] {stats['failures']}")
    console.print("\n[green]✓[/green] Watch mode stopped")
