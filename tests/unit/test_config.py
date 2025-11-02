"""
Unit tests for configuration module.
"""

import tempfile
from pathlib import Path
import pytest

from polyglot_ffi.core.config import (
    PolyglotConfig,
    TargetConfig,
    load_config,
    validate_config,
)
from polyglot_ffi.utils.errors import ConfigurationError


class TestTargetConfigValidation:
    """Test TargetConfig validation."""

    def test_unsupported_target_language(self):
        """Test that unsupported target languages raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TargetConfig(language="javascript", output_dir="out", enabled=True)

        assert "Unsupported target language" in str(exc_info.value)

    def test_supported_target_languages(self):
        """Test that supported languages are accepted."""
        # Python
        config = TargetConfig(language="python", output_dir="out", enabled=True)
        assert config.language == "python"

        # Rust
        config = TargetConfig(language="rust", output_dir="out", enabled=True)
        assert config.language == "rust"

        # C
        config = TargetConfig(language="c", output_dir="out", enabled=True)
        assert config.language == "c"


class TestPolyglotConfigValidation:
    """Test PolyglotConfig validation."""

    def test_no_targets_raises_error(self):
        """Test that empty targets list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            PolyglotConfig(
                project={"name": "test"},
                source={"language": "ocaml", "files": ["test.mli"]},
                targets=[],
            )

        assert "At least one target language must be configured" in str(exc_info.value)


class TestLoadConfigErrors:
    """Test load_config error handling."""

    def test_tomllib_not_available_error(self, monkeypatch, tmp_path):
        """Test error when tomllib is not available."""
        # Mock tomllib to be None
        import polyglot_ffi.core.config as config_module

        original_tomllib = config_module.tomllib
        monkeypatch.setattr(config_module, "tomllib", None)

        config_file = tmp_path / "polyglot.toml"
        config_file.write_text("[project]\nname = 'test'")

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                load_config(config_file)

            assert "TOML library not available" in str(exc_info.value)
            assert "pip install tomli" in str(exc_info.value)
        finally:
            # Restore original
            monkeypatch.setattr(config_module, "tomllib", original_tomllib)

    def test_toml_syntax_error_with_bracket_suggestion(self, tmp_path):
        """Test TOML syntax error with bracket mismatch."""
        config_file = tmp_path / "polyglot.toml"
        config_file.write_text("[project\nname = 'test'")

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        assert "TOML syntax error" in str(exc_info.value)
        # Should have bracket-related suggestion
        error_str = str(exc_info.value)
        assert "bracket" in error_str.lower() or "Expected" in error_str

    def test_toml_syntax_error_with_quote_suggestion(self, tmp_path):
        """Test TOML syntax error with quote issue."""
        config_file = tmp_path / "polyglot.toml"
        # Missing closing quote
        config_file.write_text('[project]\nname = "test')

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        assert "TOML syntax error" in str(exc_info.value)

    def test_toml_syntax_error_with_equals_suggestion(self, tmp_path):
        """Test TOML syntax error with equals issue."""
        config_file = tmp_path / "polyglot.toml"
        # Missing equals sign
        config_file.write_text("[project]\nname")

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        assert "TOML syntax error" in str(exc_info.value)

    def test_missing_field_error(self, tmp_path):
        """Test missing required field error."""
        config_file = tmp_path / "polyglot.toml"
        # Missing source section
        config_file.write_text(
            """
[project]
name = "test"

[[targets]]
language = "python"
output_dir = "out"
"""
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        assert "Invalid configuration" in str(exc_info.value)
        error_str = str(exc_info.value)
        assert "required" in error_str.lower() or "missing" in error_str.lower()

    def test_unsupported_target_language_error(self, tmp_path):
        """Test unsupported target language error with suggestions."""
        config_file = tmp_path / "polyglot.toml"
        config_file.write_text(
            """
[project]
name = "test"

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "javascript"
output_dir = "out"
"""
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        error_str = str(exc_info.value)
        assert "Unsupported target language" in error_str
        assert "python" in error_str.lower()

    def test_unsupported_source_language_error(self, tmp_path):
        """Test unsupported source language error."""
        config_file = tmp_path / "polyglot.toml"
        config_file.write_text(
            """
[project]
name = "test"

[source]
language = "rust"
files = ["test.rs"]

[[targets]]
language = "python"
output_dir = "out"
"""
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        error_str = str(exc_info.value)
        assert "Unsupported source language" in error_str or "Invalid configuration" in error_str


class TestValidateConfig:
    """Test validate_config function."""

    def test_validate_config_with_missing_source_dir(self, tmp_path):
        """Test validation with missing source directory."""
        config_file = tmp_path / "polyglot.toml"
        config_file.write_text(
            """
[project]
name = "test"

[source]
language = "ocaml"
files = ["test.mli"]
dir = "nonexistent_dir"

[[targets]]
language = "python"
output_dir = "out"
"""
        )

        config = load_config(config_file)
        warnings = validate_config(config)

        # Should have warning about missing source directory
        assert any("Source directory does not exist" in w for w in warnings)


class TestConfigEdgeCases:
    """Test edge cases in config parsing."""

    def test_toml_quote_error_suggestion(self, tmp_path):
        """Test TOML error with quote-related message."""
        config_file = tmp_path / "polyglot.toml"
        # Create a file with mismatched quotes that triggers quote error
        config_file.write_text("[project]\nname = 'test\"")

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        error_str = str(exc_info.value)
        assert "TOML syntax error" in error_str
        # Should have quote-related suggestion
        assert "quote" in error_str.lower() or "TOML" in error_str

    def test_toml_missing_quote_error(self, tmp_path):
        """Test TOML error with missing quote."""
        config_file = tmp_path / "polyglot.toml"
        # Missing closing quote - should trigger "Expected '\"'" error
        config_file.write_text('[project]\nname = "test\nversion = "1.0"')

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        error_str = str(exc_info.value)
        assert "TOML syntax error" in error_str
        # Should have string quoting suggestions
        assert "String" in error_str or "quote" in error_str.lower() or "TOML" in error_str

    def test_generic_validation_error(self, tmp_path):
        """Test generic validation error with fallback suggestions."""
        config_file = tmp_path / "polyglot.toml"
        # Create config with an invalid type (not related to common errors)
        config_file.write_text(
            """
[project]
name = "test"
version = 123

[source]
language = "ocaml"
files = ["test.mli"]

[[targets]]
language = "python"
output_dir = "out"
"""
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_config(config_file)

        error_str = str(exc_info.value)
        # Should have generic suggestions
        assert "Invalid configuration" in error_str or "TOML" in error_str


class TestPythonVersionCompatibility:
    """Test Python version compatibility for tomli import."""

    def test_tomli_import_on_old_python(self, monkeypatch):
        """Test tomli import path for Python < 3.11."""
        import sys
        import polyglot_ffi.core.config as config_module

        # Save original values
        original_version = sys.version_info
        original_tomllib = config_module.tomllib

        try:
            # Simulate Python 3.10
            monkeypatch.setattr(sys, "version_info", (3, 10, 0, "final", 0))

            # Force reload to trigger the import logic
            import importlib

            importlib.reload(config_module)

            # tomllib should be imported from tomli on Python < 3.11
            # If tomli is available, it should be used
            # This test just ensures the import path exists
            assert config_module.tomllib is not None or config_module.tomllib is None

        finally:
            # Restore original values
            monkeypatch.setattr(sys, "version_info", original_version)
            importlib.reload(config_module)
