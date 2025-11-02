"""
Tests for naming utilities.
"""

import pytest
from polyglot_ffi.utils.naming import (
    sanitize_for_dune,
    sanitize_for_python,
    sanitize_for_c,
    sanitize_module_name,
)


class TestSanitizeForDune:
    """Test Dune name sanitization."""

    def test_sanitize_hyphen_to_underscore(self):
        """Test that hyphens are replaced with underscores."""
        assert sanitize_for_dune("my-crypto-lib") == "my_crypto_lib"

    def test_sanitize_already_valid(self):
        """Test that valid names are unchanged."""
        assert sanitize_for_dune("my_crypto_lib") == "my_crypto_lib"

    def test_sanitize_multiple_hyphens(self):
        """Test multiple hyphens."""
        assert sanitize_for_dune("my-test-crypto-lib") == "my_test_crypto_lib"


class TestSanitizeForPython:
    """Test Python name sanitization."""

    def test_sanitize_hyphen_to_underscore(self):
        """Test that hyphens are replaced with underscores."""
        assert sanitize_for_python("my-module") == "my_module"

    def test_sanitize_already_valid(self):
        """Test that valid names are unchanged."""
        assert sanitize_for_python("my_module") == "my_module"


class TestSanitizeForC:
    """Test C name sanitization."""

    def test_sanitize_hyphen_to_underscore(self):
        """Test that hyphens are replaced with underscores."""
        assert sanitize_for_c("my-function") == "my_function"

    def test_sanitize_already_valid(self):
        """Test that valid names are unchanged."""
        assert sanitize_for_c("my_function") == "my_function"


class TestSanitizeModuleName:
    """Test module name sanitization with validation."""

    def test_sanitize_valid_name(self):
        """Test sanitizing a valid module name."""
        assert sanitize_module_name("my_module") == "my_module"

    def test_sanitize_name_with_hyphens(self):
        """Test sanitizing name with hyphens."""
        assert sanitize_module_name("my-module") == "my_module"

    def test_starts_with_digit_raises_error(self):
        """Test that names starting with digits raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            sanitize_module_name("123invalid")

        assert "cannot start with a digit" in str(exc_info.value)
        assert "module_123invalid" in str(exc_info.value)

    def test_starts_with_underscore_raises_error(self):
        """Test that names starting with underscore raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            sanitize_module_name("_invalid")

        assert "cannot start with an underscore" in str(exc_info.value)
        assert "Remove leading underscores" in str(exc_info.value)

    def test_empty_name_raises_error(self):
        """Test that empty names raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            sanitize_module_name("")

        assert "must contain at least one letter or digit" in str(exc_info.value)

    def test_only_special_chars_raises_error(self):
        """Test that names with only special characters raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            sanitize_module_name("---")

        # "---" becomes "___" which starts with underscore
        assert "cannot start with an underscore" in str(exc_info.value)

    def test_valid_after_sanitization(self):
        """Test name that becomes valid after sanitization."""
        assert sanitize_module_name("my-valid-123") == "my_valid_123"

    def test_mixed_case_preserved(self):
        """Test that mixed case is preserved."""
        # Note: OCaml modules are typically capitalized, but we preserve input
        assert sanitize_module_name("MyModule") == "MyModule"
