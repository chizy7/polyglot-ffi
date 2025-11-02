"""
Unit tests for init command.
"""

import tempfile
from pathlib import Path
import pytest

from polyglot_ffi.commands.init import (
    init_project,
    generate_config,
    generate_readme,
    generate_makefile,
)


class TestInitProject:
    """Test project initialization."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_init_basic_project(self, temp_dir, monkeypatch):
        """Test initializing a basic project."""
        monkeypatch.chdir(temp_dir)

        result = init_project(
            name="my_project",
            target_langs=["python"],
            template="basic",
            verbose=False,
        )

        assert result["success"]
        assert "my_project" in result["project_path"]

        # Check that project directory was created
        project_path = temp_dir / "my_project"
        assert project_path.exists()
        assert project_path.is_dir()

    def test_init_creates_structure(self, temp_dir, monkeypatch):
        """Test that init creates correct directory structure."""
        monkeypatch.chdir(temp_dir)

        init_project(
            name="test_project",
            target_langs=["python"],
            template="basic",
            verbose=False,
        )

        project_path = temp_dir / "test_project"

        # Check directories
        assert (project_path / "src").exists()
        assert (project_path / "src").is_dir()

        # Check files
        assert (project_path / "polyglot.toml").exists()
        assert (project_path / "README.md").exists()
        assert (project_path / "Makefile").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "src" / "test_project.mli").exists()
        assert (project_path / "src" / "test_project.ml").exists()

    def test_init_creates_valid_mli(self, temp_dir, monkeypatch):
        """Test that generated .mli file is valid."""
        monkeypatch.chdir(temp_dir)

        init_project(
            name="example",
            target_langs=["python"],
            template="basic",
            verbose=False,
        )

        mli_path = temp_dir / "example" / "src" / "example.mli"
        content = mli_path.read_text()

        # Should contain example functions
        assert "val greet" in content
        assert "string -> string" in content
        assert "val add" in content
        assert "int -> int -> int" in content
        assert "(** " in content  # Documentation comments

    def test_init_creates_valid_ml(self, temp_dir, monkeypatch):
        """Test that generated .ml file is valid."""
        monkeypatch.chdir(temp_dir)

        init_project(
            name="example",
            target_langs=["python"],
            template="basic",
            verbose=False,
        )

        ml_path = temp_dir / "example" / "src" / "example.ml"
        content = ml_path.read_text()

        # Should contain implementations
        assert "let greet" in content
        assert "let add" in content
        assert "Callback.register" in content

    def test_init_existing_directory_fails(self, temp_dir, monkeypatch):
        """Test that init fails if directory already exists."""
        monkeypatch.chdir(temp_dir)

        # Create the directory first
        (temp_dir / "existing").mkdir()

        with pytest.raises(ValueError) as exc_info:
            init_project(
                name="existing",
                target_langs=["python"],
                template="basic",
                verbose=False,
            )

        assert "already exists" in str(exc_info.value)

    def test_init_returns_files_list(self, temp_dir, monkeypatch):
        """Test that init returns list of created files."""
        monkeypatch.chdir(temp_dir)

        result = init_project(
            name="filetest",
            target_langs=["python"],
            template="basic",
            verbose=False,
        )

        assert "files_created" in result
        files = result["files_created"]

        assert "polyglot.toml" in files
        assert "README.md" in files
        assert "Makefile" in files
        assert ".gitignore" in files
        assert "src/filetest.mli" in files
        assert "src/filetest.ml" in files

    def test_init_with_multiple_targets(self, temp_dir, monkeypatch):
        """Test init with multiple target languages."""
        monkeypatch.chdir(temp_dir)

        result = init_project(
            name="multi",
            target_langs=["python", "rust"],
            template="basic",
            verbose=False,
        )

        assert result["success"]

        # Config should be generated with multiple targets
        config_path = temp_dir / "multi" / "polyglot.toml"
        assert config_path.exists()


class TestGenerateConfig:
    """Test configuration generation."""

    def test_generate_config_basic(self):
        """Test generating basic configuration."""
        config = generate_config("my_project", "my_project", ["python"])

        assert "my_project" in config
        assert "[project]" in config
        assert 'name = "my_project"' in config
        assert "[source]" in config
        assert "[[targets]]" in config

    def test_generate_config_with_multiple_langs(self):
        """Test generating config with multiple target languages."""
        config = generate_config("multi_proj", "multi_proj", ["python", "rust"])

        assert "multi_proj" in config
        # Config should include project name and structure
        assert "[project]" in config

    def test_generate_config_has_bindings_section(self):
        """Test that config includes source and target sections."""
        config = generate_config("test", "test", ["python"])

        assert "[source]" in config
        assert "[[targets]]" in config
        assert 'language = "python"' in config

    def test_generate_config_includes_source_file(self):
        """Test that config references the source .mli file."""
        config = generate_config("mylib", "mylib", ["python"])

        assert "mylib.mli" in config


class TestGenerateReadme:
    """Test README generation."""

    def test_generate_readme_basic(self):
        """Test generating basic README."""
        readme = generate_readme("my_project", ["python"])

        assert "# my_project" in readme
        assert "Polyglot FFI" in readme

    def test_generate_readme_has_quickstart(self):
        """Test that README includes quickstart section."""
        readme = generate_readme("test_proj", ["python"])

        assert "Quick Start" in readme
        assert "polyglot-ffi generate" in readme
        assert "make" in readme

    def test_generate_readme_has_structure(self):
        """Test that README shows project structure."""
        readme = generate_readme("example", ["python"])

        assert "Project Structure" in readme
        assert "polyglot.toml" in readme
        assert "example.mli" in readme
        assert "generated/" in readme

    def test_generate_readme_has_workflow(self):
        """Test that README includes development workflow."""
        readme = generate_readme("workflow_test", ["python"])

        assert "Development Workflow" in readme
        assert "Edit" in readme or "edit" in readme

    def test_generate_readme_includes_examples(self):
        """Test that README includes usage examples."""
        readme = generate_readme("lib_example", ["python"])

        assert "python" in readme.lower() or "Python" in readme
        assert "greet" in readme
        assert "add" in readme

    def test_generate_readme_warns_about_generated(self):
        """Test that README warns not to edit generated files."""
        readme = generate_readme("test", ["python"])

        assert "generated" in readme.lower()
        assert "auto-generated" in readme.lower()


class TestGenerateMakefile:
    """Test Makefile generation."""

    def test_generate_makefile_basic(self):
        """Test generating basic Makefile."""
        makefile = generate_makefile("my_project")

        assert "Makefile for my_project" in makefile
        assert ".PHONY" in makefile

    def test_generate_makefile_has_targets(self):
        """Test that Makefile has all required targets."""
        makefile = generate_makefile("test_proj")

        assert "generate:" in makefile
        assert "build:" in makefile
        assert "clean:" in makefile
        assert "test:" in makefile

    def test_generate_makefile_generate_target(self):
        """Test that generate target calls polyglot-ffi."""
        makefile = generate_makefile("example")

        assert "polyglot-ffi generate" in makefile
        assert "example.mli" in makefile

    def test_generate_makefile_build_target(self):
        """Test that build target uses dune."""
        makefile = generate_makefile("buildtest")

        assert "dune build" in makefile

    def test_generate_makefile_clean_target(self):
        """Test that clean target removes generated files."""
        makefile = generate_makefile("cleantest")

        assert "rm -rf generated" in makefile or "rm -rf generated/" in makefile

    def test_generate_makefile_test_target(self):
        """Test that test target runs Python tests."""
        makefile = generate_makefile("pytest")

        assert "python" in makefile.lower()
        # Should test the generated Python bindings
        assert "greet" in makefile
        assert "add" in makefile

    def test_generate_makefile_has_help(self):
        """Test that Makefile includes help target."""
        makefile = generate_makefile("help_test")

        # Should have help target
        assert "help:" in makefile or "Available targets" in makefile
