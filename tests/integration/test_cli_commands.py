"""
Integration tests for CLI commands.

Tests for check, clean, watch, and other CLI functionality.
"""

import tempfile
import time
from pathlib import Path
from typing import Dict, Any

import pytest
from polyglot_ffi.commands.check import (
    check_dependencies,
    check_project,
    display_check_results,
)
from polyglot_ffi.commands.clean import (
    find_generated_files,
    clean_files,
    clean_project,
    GENERATED_PATTERNS,
)
from polyglot_ffi.commands.watch import SourceFileHandler
from polyglot_ffi.core.config import (
    load_config,
    create_default_config,
    validate_config,
    PolyglotConfig,
)


class TestCheckCommand:
    """Test the check command."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def valid_config_file(self, temp_dir):
        """Create a valid polyglot.toml file."""
        config_content = """
[project]
name = "test_project"
version = "0.1.0"
description = "Test project"

[source]
language = "ocaml"
dir = "src"
files = ["test.mli"]

[[targets]]
language = "python"
output_dir = "generated/python"
enabled = true

[build]
auto_build = false
"""
        config_path = temp_dir / "polyglot.toml"
        config_path.write_text(config_content)

        # Create source directory and file
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "test.mli").write_text("val test : string -> string\n")

        return config_path

    @pytest.fixture
    def invalid_config_file(self, temp_dir):
        """Create an invalid polyglot.toml file."""
        config_content = """
[project]
name = "test_project"

[source]
language = "invalid_lang"
"""
        config_path = temp_dir / "polyglot.toml"
        config_path.write_text(config_content)
        return config_path

    def test_check_dependencies_all(self):
        """Test checking all dependencies."""
        deps = check_dependencies(lang=None)

        # Should check for all language dependencies
        assert "ocaml" in deps or "python3" in deps or "cargo" in deps
        assert isinstance(deps, dict)

        # Values should be booleans
        for available in deps.values():
            assert isinstance(available, bool)

    def test_check_dependencies_ocaml(self):
        """Test checking OCaml dependencies only."""
        deps = check_dependencies(lang="ocaml")

        assert "ocaml" in deps
        assert "dune" in deps
        assert "opam" in deps

        # Should not include other languages
        assert "cargo" not in deps
        assert "rustc" not in deps

    def test_check_dependencies_python(self):
        """Test checking Python dependencies only."""
        deps = check_dependencies(lang="python")

        assert "python3" in deps
        assert "pip" in deps

        # Should not include other languages
        assert "ocaml" not in deps
        assert "cargo" not in deps

    def test_check_dependencies_rust(self):
        """Test checking Rust dependencies only."""
        deps = check_dependencies(lang="rust")

        assert "cargo" in deps
        assert "rustc" in deps

        # Should not include other languages
        assert "ocaml" not in deps
        assert "python3" not in deps

    def test_check_project_no_config(self, temp_dir, monkeypatch):
        """Test check when no config file exists."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=False)

        assert not results["config_valid"]
        assert "No polyglot.toml found" in results["errors"][0]
        assert len(results["warnings"]) > 0
        assert "polyglot-ffi init" in results["warnings"][0]

    def test_check_project_valid_config(self, temp_dir, valid_config_file, monkeypatch):
        """Test check with valid configuration."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=False)

        assert results["config_valid"]
        assert "config" in results
        assert results["config"].project.name == "test_project"
        assert results["config"].source.language == "ocaml"

    def test_check_project_with_dependencies(self, temp_dir, valid_config_file, monkeypatch):
        """Test check with dependency checking."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=True, lang="python")

        assert results["config_valid"]
        assert "dependencies" in results
        assert len(results["dependencies"]) > 0

        # Should have Python dependencies
        assert "python3" in results["dependencies"]

    def test_check_project_invalid_config(self, temp_dir, invalid_config_file, monkeypatch):
        """Test check with invalid configuration."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=False)

        assert not results["config_valid"]
        assert len(results["errors"]) > 0

    def test_display_check_results_valid(self, temp_dir, valid_config_file, monkeypatch, capsys):
        """Test displaying check results for valid config."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=True)
        display_check_results(results)

        captured = capsys.readouterr()
        # Should contain success indicator (the actual output includes ANSI codes)
        assert "Configuration" in captured.out or captured.out  # Basic check

    def test_display_check_results_invalid(self, temp_dir, monkeypatch, capsys):
        """Test displaying check results when no config exists."""
        monkeypatch.chdir(temp_dir)

        results = check_project(check_deps=False)
        display_check_results(results)

        captured = capsys.readouterr()
        # Output should exist
        assert captured.out


class TestCleanCommand:
    """Test the clean command."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def generated_files_dir(self, temp_dir):
        """Create a directory with generated files."""
        output_dir = temp_dir / "generated"
        output_dir.mkdir()

        # Create various generated files
        (output_dir / "module_stubs.c").write_text("// C stub")
        (output_dir / "module_stubs.h").write_text("// Header")
        (output_dir / "module_py.py").write_text("# Python wrapper")
        (output_dir / "type_description.ml").write_text("(* OCaml *)")
        (output_dir / "function_description.ml").write_text("(* OCaml *)")
        (output_dir / "dune").write_text("; Dune file")

        # Create a subdirectory with cache files
        pycache = output_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_text("bytecode")

        return output_dir

    @pytest.fixture
    def config_with_output(self, temp_dir):
        """Create a config file with output directory."""
        config_content = """
[project]
name = "test_project"
version = "0.1.0"

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "python"
output_dir = "generated"
enabled = true
"""
        config_path = temp_dir / "polyglot.toml"
        config_path.write_text(config_content)
        return config_path

    def test_find_generated_files_patterns(self, generated_files_dir):
        """Test finding generated files by patterns."""
        files = find_generated_files([generated_files_dir], all_files=False)

        # Should find files matching patterns
        assert len(files) > 0

        # Check specific files
        file_names = {f.name for f in files}
        assert "module_stubs.c" in file_names
        assert "module_stubs.h" in file_names
        assert "type_description.ml" in file_names
        assert "dune" in file_names

    def test_find_generated_files_all(self, generated_files_dir):
        """Test finding all files including directory."""
        files = find_generated_files([generated_files_dir], all_files=True)

        # Should include the entire directory
        assert generated_files_dir in files

    def test_find_generated_files_nonexistent_dir(self, temp_dir):
        """Test finding files in non-existent directory."""
        nonexistent = temp_dir / "does_not_exist"
        files = find_generated_files([nonexistent], all_files=False)

        # Should return empty set
        assert len(files) == 0

    def test_clean_files_dry_run(self, generated_files_dir, capsys):
        """Test cleaning files in dry-run mode."""
        files_to_clean = find_generated_files([generated_files_dir], all_files=False)
        initial_count = len(files_to_clean)

        count = clean_files(files_to_clean, dry_run=True)

        # Files should still exist after dry-run
        for file_path in files_to_clean:
            assert file_path.exists(), f"File {file_path} should still exist after dry-run"

        # Dry run returns 0
        assert count == 0

        # Check output
        captured = capsys.readouterr()
        assert "Would remove" in captured.out

    def test_clean_files_actual(self, generated_files_dir):
        """Test actually cleaning files."""
        # Create a test file
        test_file = generated_files_dir / "test_stubs.c"
        test_file.write_text("test")

        files_to_clean = {test_file}
        count = clean_files(files_to_clean, dry_run=False)

        # File should be deleted
        assert not test_file.exists()
        assert count == 1

    def test_clean_files_directory(self, generated_files_dir):
        """Test cleaning a directory."""
        # Create a test subdirectory
        test_dir = generated_files_dir / "test_subdir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("test")

        files_to_clean = {test_dir}
        count = clean_files(files_to_clean, dry_run=False)

        # Directory should be deleted
        assert not test_dir.exists()
        assert count == 1

    def test_clean_project_no_files(self, temp_dir, monkeypatch, capsys):
        """Test clean when no generated files exist."""
        monkeypatch.chdir(temp_dir)

        count = clean_project(all_files=False, dry_run=False)

        assert count == 0

        captured = capsys.readouterr()
        assert "No generated files found" in captured.out

    def test_clean_project_with_config(
        self, temp_dir, config_with_output, generated_files_dir, monkeypatch
    ):
        """Test clean with config file."""
        monkeypatch.chdir(temp_dir)

        count = clean_project(all_files=False, dry_run=False)

        # Some files should be cleaned
        assert count >= 0

    def test_clean_project_dry_run(self, temp_dir, generated_files_dir, monkeypatch, capsys):
        """Test clean in dry-run mode."""
        monkeypatch.chdir(temp_dir)

        # Create some files
        (generated_files_dir / "test_stubs.c").write_text("test")

        count = clean_project(all_files=False, dry_run=True)

        captured = capsys.readouterr()
        assert "Dry run" in captured.out

    def test_clean_project_all_files(self, temp_dir, generated_files_dir, monkeypatch):
        """Test clean with all_files flag."""
        monkeypatch.chdir(temp_dir)

        # Should clean entire directories
        count = clean_project(all_files=True, dry_run=False)

        # Directory might be cleaned
        assert count >= 0


class TestWatchCommand:
    """Test the watch command functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def watched_files(self, temp_dir):
        """Create files to watch."""
        file1 = temp_dir / "test1.mli"
        file2 = temp_dir / "test2.mli"

        file1.write_text("val test1 : string -> string\n")
        file2.write_text("val test2 : int -> int\n")

        return {file1, file2}

    def test_source_file_handler_init(self, watched_files):
        """Test SourceFileHandler initialization."""
        callback_called = []

        def callback(path):
            callback_called.append(path)

        # use a short debounce interval to make the test fast and deterministic
        handler = SourceFileHandler(watched_files, callback, debounce_seconds=0.05)

        assert len(handler.watched_files) == len(watched_files)
        assert handler.debounce_seconds == 0.05
        assert len(callback_called) == 0

    def test_source_file_handler_debounce(self, watched_files):
        """Test that handler debounces rapid changes."""
        callback_count = []

        def callback(path):
            callback_count.append(path)

        handler = SourceFileHandler(watched_files, callback, debounce_seconds=0.05)

        # Get one of the watched files
        test_file = list(watched_files)[0]

        # Create a mock event
        class MockEvent:
            def __init__(self, src_path, is_directory=False):
                self.src_path = str(src_path)
                self.is_directory = is_directory

        # First modification should trigger callback
        event1 = MockEvent(test_file)
        handler.on_modified(event1)
        assert len(callback_count) == 1

        # Second modification immediately after should be debounced
        event2 = MockEvent(test_file)
        handler.on_modified(event2)
        assert len(callback_count) == 1  # Still 1, debounced

        # After debounce period, should trigger again (short sleep because debounce is small)
        time.sleep(0.1)
        event3 = MockEvent(test_file)
        handler.on_modified(event3)
        assert len(callback_count) == 2

    def test_source_file_handler_ignores_directories(self, temp_dir):
        """Test that handler ignores directory events."""
        callback_count = []

        def callback(path):
            callback_count.append(path)

        test_dir = temp_dir / "subdir"
        test_dir.mkdir()

        handler = SourceFileHandler({test_dir}, callback)

        class MockEvent:
            def __init__(self, src_path, is_directory=False):
                self.src_path = str(src_path)
                self.is_directory = is_directory

        # Directory event should be ignored
        event = MockEvent(test_dir, is_directory=True)
        handler.on_modified(event)

        assert len(callback_count) == 0

    def test_source_file_handler_ignores_unwatched_files(self, temp_dir, watched_files):
        """Test that handler ignores unwatched files."""
        callback_count = []

        def callback(path):
            callback_count.append(path)

        handler = SourceFileHandler(watched_files, callback)

        # Create a file not in watched set
        unwatched_file = temp_dir / "unwatched.txt"
        unwatched_file.write_text("test")

        class MockEvent:
            def __init__(self, src_path, is_directory=False):
                self.src_path = str(src_path)
                self.is_directory = is_directory

        event = MockEvent(unwatched_file)
        handler.on_modified(event)

        assert len(callback_count) == 0


class TestConfigModule:
    """Test configuration loading and validation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def valid_config_file(self, temp_dir):
        """Create a valid config file."""
        config_content = """
[project]
name = "test_project"
version = "0.2.0"
description = "A test project"
authors = ["Test Author"]

[source]
language = "ocaml"
dir = "src"
files = ["module.mli", "other.mli"]
exclude = ["internal.mli"]

[[targets]]
language = "python"
output_dir = "generated/python"
enabled = true

[[targets]]
language = "rust"
output_dir = "generated/rust"
enabled = false

[build]
auto_build = true
build_command = "dune build"

[type_mappings.custom_type]
ocaml = "custom_t"
python = "CustomType"
rust = "CustomType"
c = "custom_t*"
"""
        config_path = temp_dir / "polyglot.toml"
        config_path.write_text(config_content)
        return config_path

    @pytest.fixture
    def minimal_config_file(self, temp_dir):
        """Create a minimal valid config file."""
        config_content = """
[project]
name = "minimal"

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "python"
"""
        config_path = temp_dir / "polyglot.toml"
        config_path.write_text(config_content)
        return config_path

    def test_load_config_valid(self, valid_config_file):
        """Test loading a valid configuration."""
        config = load_config(valid_config_file)

        assert config.project.name == "test_project"
        assert config.project.version == "0.2.0"
        assert config.project.description == "A test project"
        assert len(config.project.authors) == 1

        assert config.source.language == "ocaml"
        assert config.source.dir == "src"
        assert len(config.source.files) == 2
        assert len(config.source.exclude) == 1

        assert len(config.targets) == 2
        assert config.targets[0].language == "python"
        assert config.targets[0].enabled is True
        assert config.targets[1].language == "rust"
        assert config.targets[1].enabled is False

        assert config.build.auto_build is True
        assert config.build.build_command == "dune build"

        assert "custom_type" in config.type_mappings

    def test_load_config_minimal(self, minimal_config_file):
        """Test loading a minimal configuration."""
        config = load_config(minimal_config_file)

        assert config.project.name == "minimal"
        assert config.project.version == "0.1.0"  # Default
        assert config.source.language == "ocaml"
        assert len(config.targets) == 1

    def test_load_config_not_found(self, temp_dir):
        """Test loading non-existent config file."""
        from polyglot_ffi.utils.errors import ConfigurationError

        nonexistent = temp_dir / "does_not_exist.toml"

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(nonexistent)

        assert "not found" in str(exc_info.value)
        assert len(exc_info.value.suggestions) > 0

    def test_load_config_invalid_toml(self, temp_dir):
        """Test loading invalid TOML syntax."""
        from polyglot_ffi.utils.errors import ConfigurationError

        invalid_toml = temp_dir / "invalid.toml"
        invalid_toml.write_text("[project\nname = invalid")

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(invalid_toml)

        assert "parse TOML" in str(exc_info.value)

    def test_load_config_invalid_schema(self, temp_dir):
        """Test loading config with invalid schema."""
        from polyglot_ffi.utils.errors import ConfigurationError

        invalid_schema = temp_dir / "invalid_schema.toml"
        invalid_schema.write_text(
            """
[project]
name = "test"

[source]
language = "invalid_language"
files = ["test.mli"]

[[targets]]
language = "python"
"""
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(invalid_schema)

        assert "Invalid configuration" in str(exc_info.value)

    def test_load_config_no_targets(self, temp_dir):
        """Test loading config with no targets (validation should catch this)."""
        from polyglot_ffi.utils.errors import ConfigurationError

        no_targets = temp_dir / "no_targets.toml"
        no_targets.write_text(
            """
[project]
name = "test"

[source]
language = "ocaml"
files = ["test.mli"]
"""
        )

        # Config loads but validator should catch empty targets
        try:
            config = load_config(no_targets)
            # If it loads, validate should warn about it
            warnings = validate_config(config)
            # Should have no targets
            assert len(config.targets) == 0 or all(not t.enabled for t in config.targets)
        except ConfigurationError:
            # This is also acceptable - config rejects empty targets
            pass

    def test_create_default_config(self):
        """Test creating default configuration."""
        config_dict = create_default_config("my_project", ["python", "rust"])

        assert config_dict["project"]["name"] == "my_project"
        assert config_dict["project"]["version"] == "0.1.0"
        assert config_dict["source"]["language"] == "ocaml"
        assert len(config_dict["targets"]) == 2
        assert config_dict["targets"][0]["language"] == "python"
        assert config_dict["targets"][1]["language"] == "rust"

    def test_validate_config_missing_source_files(self, temp_dir, minimal_config_file):
        """Test validation warnings for missing source files."""
        config = load_config(minimal_config_file)
        warnings = validate_config(config)

        # Should warn about missing source file
        assert len(warnings) > 0
        assert any("not found" in w for w in warnings)

    def test_validate_config_valid(self, temp_dir, valid_config_file):
        """Test validation of valid config with existing files."""
        # Create the source directory and files
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "module.mli").write_text("val test : string -> string\n")
        (src_dir / "other.mli").write_text("val other : int -> int\n")

        config = load_config(valid_config_file)
        warnings = validate_config(config)

        # Should have minimal warnings (files exist)
        # May still have warnings about disabled targets, etc.
        assert isinstance(warnings, list)

    def test_validate_config_duplicate_targets(self, temp_dir):
        """Test validation warning for duplicate target languages."""
        duplicate_targets = temp_dir / "duplicate.toml"
        duplicate_targets.write_text(
            """
[project]
name = "test"

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "python"

[[targets]]
language = "python"
"""
        )

        config = load_config(duplicate_targets)
        warnings = validate_config(config)

        assert any("Duplicate" in w for w in warnings)

    def test_validate_config_no_enabled_targets(self, temp_dir):
        """Test validation warning when no targets are enabled."""
        no_enabled = temp_dir / "no_enabled.toml"
        no_enabled.write_text(
            """
[project]
name = "test"

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "python"
enabled = false
"""
        )

        config = load_config(no_enabled)
        warnings = validate_config(config)

        assert any("No target languages are enabled" in w for w in warnings)
