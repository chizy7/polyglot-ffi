"""
Unit tests for error types and error formatting.
"""

from pathlib import Path
import pytest

from polyglot_ffi.utils.errors import (
    ErrorContext,
    PolyglotFFIError,
    ParseError,
    TypeError_,
    GenerationError,
    ConfigurationError,
    ValidationError,
    suggest_type_fix,
    suggest_syntax_fix,
)


class TestErrorContext:
    """Test ErrorContext dataclass."""

    def test_error_context_default(self):
        """Test ErrorContext with default values."""
        ctx = ErrorContext()

        assert ctx.file_path is None
        assert ctx.line is None
        assert ctx.column is None
        assert ctx.code_snippet is None
        assert ctx.suggestion is None

    def test_error_context_full(self):
        """Test ErrorContext with all fields."""
        ctx = ErrorContext(
            file_path=Path("test.mli"),
            line=10,
            column=5,
            code_snippet="val test : string -> string",
            suggestion="Check the type signature",
        )

        assert ctx.file_path == Path("test.mli")
        assert ctx.line == 10
        assert ctx.column == 5
        assert ctx.code_snippet == "val test : string -> string"
        assert ctx.suggestion == "Check the type signature"


class TestPolyglotFFIError:
    """Test base error class."""

    def test_basic_error(self):
        """Test basic error without context."""
        error = PolyglotFFIError("Something went wrong")

        assert error.message == "Something went wrong"
        assert isinstance(error.context, ErrorContext)
        assert error.suggestions == []
        assert str(error) == "Something went wrong"

    def test_error_with_suggestions(self):
        """Test error with suggestions."""
        error = PolyglotFFIError(
            "Invalid type",
            suggestions=["Use 'string' instead", "Check documentation"],
        )

        assert len(error.suggestions) == 2
        assert "Use 'string' instead" in error.suggestions

    def test_error_with_context(self):
        """Test error with full context."""
        ctx = ErrorContext(
            file_path=Path("test.mli"),
            line=5,
            column=10,
        )
        error = PolyglotFFIError("Parse error", context=ctx)

        assert error.context.file_path == Path("test.mli")
        assert error.context.line == 5
        assert error.context.column == 10

    def test_error_str_with_location(self):
        """Test string representation with location."""
        ctx = ErrorContext(
            file_path=Path("test.mli"),
            line=5,
            column=10,
        )
        error = PolyglotFFIError("Parse error", context=ctx)
        error_str = str(error)

        assert "Parse error" in error_str
        assert "test.mli:5:10" in error_str

    def test_error_str_with_suggestions(self):
        """Test string representation with suggestions."""
        error = PolyglotFFIError(
            "Invalid syntax",
            suggestions=["Check parentheses", "Review documentation"],
        )
        error_str = str(error)

        assert "Invalid syntax" in error_str
        assert "Suggestions:" in error_str
        assert "Check parentheses" in error_str
        assert "Review documentation" in error_str

    def test_error_format_rich_basic(self):
        """Test rich formatting of basic error."""
        error = PolyglotFFIError("Something failed")
        rich_output = error.format_rich()

        assert "Error:" in rich_output
        assert "Something failed" in rich_output

    def test_error_format_rich_with_location(self):
        """Test rich formatting with file location."""
        ctx = ErrorContext(
            file_path=Path("module.mli"),
            line=10,
            column=5,
        )
        error = PolyglotFFIError("Type error", context=ctx)
        rich_output = error.format_rich()

        assert "module.mli" in rich_output
        assert "10" in rich_output

    def test_error_format_rich_with_code_snippet(self):
        """Test rich formatting with code snippet."""
        code = "val encrypt : string -> string\nval decrypt : string -> string"
        ctx = ErrorContext(
            file_path=Path("test.mli"),
            line=1,
            column=15,
            code_snippet=code,
        )
        error = PolyglotFFIError("Invalid type", context=ctx)
        rich_output = error.format_rich()

        assert "Code:" in rich_output
        assert "encrypt" in rich_output

    def test_error_format_rich_with_suggestions(self):
        """Test rich formatting with suggestions."""
        error = PolyglotFFIError(
            "Parse failed",
            suggestions=["Check syntax", "Verify parentheses"],
        )
        rich_output = error.format_rich()

        assert "Suggestions:" in rich_output
        assert "Check syntax" in rich_output
        assert "Verify parentheses" in rich_output


class TestParseError:
    """Test ParseError exception."""

    def test_parse_error_basic(self):
        """Test basic parse error."""
        error = ParseError("Failed to parse function signature")

        assert error.message == "Failed to parse function signature"
        assert isinstance(error, PolyglotFFIError)

    def test_parse_error_with_location(self):
        """Test parse error with file location."""
        error = ParseError(
            "Invalid syntax",
            file_path=Path("crypto.mli"),
            line=15,
            column=20,
        )

        assert error.context.file_path == Path("crypto.mli")
        assert error.context.line == 15
        assert error.context.column == 20

    def test_parse_error_with_code_snippet(self):
        """Test parse error with code snippet."""
        code = "val invalid : string ->"
        error = ParseError(
            "Incomplete signature",
            file_path=Path("test.mli"),
            line=1,
            code_snippet=code,
            suggestions=["Add return type"],
        )

        assert error.context.code_snippet == code
        assert len(error.suggestions) == 1


class TestTypeError:
    """Test TypeError_ exception."""

    def test_type_error_basic(self):
        """Test basic type error."""
        error = TypeError_("Unsupported type: foobar")

        assert error.message == "Unsupported type: foobar"
        assert isinstance(error, PolyglotFFIError)

    def test_type_error_with_suggestions(self):
        """Test type error with suggestions."""
        error = TypeError_(
            "Invalid type name",
            suggestions=["Use 'string' instead of 'str'"],
        )

        assert len(error.suggestions) == 1


class TestGenerationError:
    """Test GenerationError exception."""

    def test_generation_error_basic(self):
        """Test basic generation error."""
        error = GenerationError("Failed to generate C stubs")

        assert error.message == "Failed to generate C stubs"
        assert isinstance(error, PolyglotFFIError)


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_basic(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid TOML syntax")

        assert error.message == "Invalid TOML syntax"
        assert isinstance(error, PolyglotFFIError)

    def test_configuration_error_with_path(self):
        """Test configuration error with config path."""
        error = ConfigurationError(
            "Missing required field",
            config_path=Path("polyglot.toml"),
            suggestions=["Add [project] section"],
        )

        assert error.context.file_path == Path("polyglot.toml")
        assert len(error.suggestions) == 1


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic validation error."""
        error = ValidationError("Source file not found")

        assert error.message == "Source file not found"
        assert isinstance(error, PolyglotFFIError)


class TestSuggestTypeFix:
    """Test type suggestion helper."""

    def test_suggest_type_fix_str(self):
        """Test suggestion for 'str' -> 'string'."""
        suggestions = suggest_type_fix("str")

        assert len(suggestions) > 0
        assert any("string" in s for s in suggestions)

    def test_suggest_type_fix_String(self):
        """Test suggestion for 'String' -> 'string'."""
        suggestions = suggest_type_fix("String")

        assert len(suggestions) > 0
        assert any("string" in s for s in suggestions)

    def test_suggest_type_fix_integer(self):
        """Test suggestion for 'integer' -> 'int'."""
        suggestions = suggest_type_fix("integer")

        assert len(suggestions) > 0
        assert any("int" in s for s in suggestions)

    def test_suggest_type_fix_Int(self):
        """Test suggestion for 'Int' -> 'int'."""
        suggestions = suggest_type_fix("Int")

        assert len(suggestions) > 0

    def test_suggest_type_fix_boolean(self):
        """Test suggestion for 'boolean' -> 'bool'."""
        suggestions = suggest_type_fix("boolean")

        assert len(suggestions) > 0
        assert any("bool" in s for s in suggestions)

    def test_suggest_type_fix_Boolean(self):
        """Test suggestion for 'Boolean' -> 'bool'."""
        suggestions = suggest_type_fix("Boolean")

        assert len(suggestions) > 0

    def test_suggest_type_fix_Bool(self):
        """Test suggestion for 'Bool' -> 'bool'."""
        suggestions = suggest_type_fix("Bool")

        assert len(suggestions) > 0

    def test_suggest_type_fix_double(self):
        """Test suggestion for 'double' -> 'float'."""
        suggestions = suggest_type_fix("double")

        assert len(suggestions) > 0
        assert any("float" in s for s in suggestions)

    def test_suggest_type_fix_Float(self):
        """Test suggestion for 'Float' -> 'float'."""
        suggestions = suggest_type_fix("Float")

        assert len(suggestions) > 0

    def test_suggest_type_fix_void(self):
        """Test suggestion for 'void' -> 'unit'."""
        suggestions = suggest_type_fix("void")

        assert len(suggestions) > 0
        assert any("unit" in s for s in suggestions)

    def test_suggest_type_fix_None(self):
        """Test suggestion for 'None' -> 'unit'."""
        suggestions = suggest_type_fix("None")

        assert len(suggestions) > 0
        assert any("unit" in s for s in suggestions)

    def test_suggest_type_fix_null(self):
        """Test suggestion for 'null' -> 'unit'."""
        suggestions = suggest_type_fix("null")

        assert len(suggestions) > 0

    def test_suggest_type_fix_Optional(self):
        """Test suggestion for 'Optional' -> 'option'."""
        suggestions = suggest_type_fix("Optional")

        assert len(suggestions) > 0
        assert any("option" in s for s in suggestions)

    def test_suggest_type_fix_array(self):
        """Test suggestion for 'array' -> 'list'."""
        suggestions = suggest_type_fix("array")

        assert len(suggestions) > 0
        assert any("list" in s for s in suggestions)

    def test_suggest_type_fix_unknown(self):
        """Test suggestion for unknown type."""
        suggestions = suggest_type_fix("completely_unknown_type")

        # Should provide general suggestions
        assert len(suggestions) > 0
        assert any("Supported types" in s for s in suggestions)


class TestSuggestSyntaxFix:
    """Test syntax suggestion helper."""

    def test_suggest_syntax_fix_signature(self):
        """Test suggestion for signature errors."""
        suggestions = suggest_syntax_fix("invalid signature")

        assert len(suggestions) > 0
        assert any("val" in s for s in suggestions)
        assert any("encrypt" in s for s in suggestions)

    def test_suggest_syntax_fix_record(self):
        """Test suggestion for record syntax errors."""
        suggestions = suggest_syntax_fix("invalid record")

        assert len(suggestions) > 0
        assert any("type" in s for s in suggestions)
        assert any("semicolon" in s.lower() for s in suggestions)

    def test_suggest_syntax_fix_variant(self):
        """Test suggestion for variant syntax errors."""
        suggestions = suggest_syntax_fix("invalid variant")

        assert len(suggestions) > 0
        assert any("type" in s for s in suggestions)
        assert any("|" in s or "Constructor" in s for s in suggestions)

    def test_suggest_syntax_fix_unknown(self):
        """Test suggestion for unknown syntax error."""
        suggestions = suggest_syntax_fix("some random error")

        # Might return empty or general suggestions
        assert isinstance(suggestions, list)
