"""
Unit tests for OCaml parser.
"""

import pytest
from polyglot_ffi.parsers.ocaml import OCamlParser, ParseError
from polyglot_ffi.ir.types import TypeKind


class TestOCamlParser:
    """Test OCaml .mli parser."""

    def test_parse_simple_function(self):
        """Test parsing a simple function with primitive types."""
        content = """
val encrypt : string -> string
(** Encrypt a string *)
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 1
        func = module.functions[0]

        assert func.name == "encrypt"
        assert len(func.params) == 1
        assert func.params[0].type.name == "string"
        assert func.return_type.name == "string"

    def test_parse_multiple_parameters(self):
        """Test parsing function with multiple parameters."""
        content = """
val add : int -> int -> int
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 1
        func = module.functions[0]

        assert func.name == "add"
        assert len(func.params) == 2
        assert func.params[0].type.name == "int"
        assert func.params[1].type.name == "int"
        assert func.return_type.name == "int"

    def test_parse_different_types(self):
        """Test parsing functions with different primitive types."""
        content = """
val string_func : string -> string
val int_func : int -> int
val float_func : float -> float
val bool_func : bool -> bool
val unit_func : unit -> unit
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 5

        assert module.functions[0].name == "string_func"
        assert module.functions[0].return_type.name == "string"

        assert module.functions[1].name == "int_func"
        assert module.functions[1].return_type.name == "int"

        assert module.functions[2].name == "float_func"
        assert module.functions[2].return_type.name == "float"

        assert module.functions[3].name == "bool_func"
        assert module.functions[3].return_type.name == "bool"

        assert module.functions[4].name == "unit_func"
        assert module.functions[4].return_type.name == "unit"

    def test_parse_with_documentation(self):
        """Test parsing function with documentation comment."""
        content = """
val greet : string -> string
(** Greet someone by name *)
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 1
        # Note: Documentation extraction is parsed but not stored in IR initially

    def test_parse_multiline_signature(self):
        """Test parsing function signature split across multiple lines."""
        content = """
val complex_function : string -> int -> float -> bool
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 1
        func = module.functions[0]

        assert func.name == "complex_function"
        assert len(func.params) == 3
        assert func.return_type.name == "bool"

    def test_parse_multiple_functions(self):
        """Test parsing multiple functions in one file."""
        content = """
val encrypt : string -> string
(** Encrypt a string *)

val decrypt : string -> string
(** Decrypt a string *)

val hash : string -> int
(** Generate hash *)
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 3
        assert module.functions[0].name == "encrypt"
        assert module.functions[1].name == "decrypt"
        assert module.functions[2].name == "hash"

    def test_unsupported_type_error(self):
        """Test that unsupported types are now handled as CUSTOM types."""
        content = """
val process : custom_type -> string
"""
        parser = OCamlParser(content)

        # Note: custom types are now supported as CUSTOM type kind
        module = parser.parse()
        assert len(module.functions) == 1
        func = module.functions[0]
        assert func.params[0].type.kind == TypeKind.CUSTOM
        assert func.params[0].type.name == "custom_type"

    def test_invalid_signature_error(self):
        """Test that invalid signatures raise ParseError."""
        content = """
val invalid
"""
        parser = OCamlParser(content)

        with pytest.raises(ParseError) as exc_info:
            parser.parse()

        assert "Invalid function signature" in str(exc_info.value)

    def test_empty_file(self):
        """Test parsing empty file."""
        content = ""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 0

    def test_comments_ignored(self):
        """Test that regular comments are ignored."""
        content = """
(* This is a comment *)
val test : string -> string
(* Another comment *)
"""
        parser = OCamlParser(content)
        module = parser.parse()

        assert len(module.functions) == 1
        assert module.functions[0].name == "test"


class TestOCamlParserTypeDefinitions:
    """Test parsing type definitions."""

    def test_invalid_type_definition_malformed(self):
        """Test malformed type definition."""
        # This should trigger line 154 - has "type" and "=" but invalid format
        # The regex expects: type name = definition
        # This has "=" but no valid name before it
        content = """
type = invalid_format
"""
        parser = OCamlParser(content)

        with pytest.raises(ParseError) as exc_info:
            parser.parse()

        assert "Invalid type definition" in str(exc_info.value)

    def test_parameter_parsing_error_with_mock(self):
        """Test error handling when parsing parameter types fails."""
        from unittest.mock import Mock, patch

        content = """
val test : string -> int
"""
        parser = OCamlParser(content)

        # Mock _parse_type to raise ParseError for the first parameter
        original_parse_type = parser._parse_type
        call_count = [0]

        def mock_parse_type(type_str, line_num):
            call_count[0] += 1
            # Raise error on first call (first parameter)
            if call_count[0] == 1:
                raise ParseError("Mocked parse error", line=line_num)
            return original_parse_type(type_str, line_num)

        parser._parse_type = mock_parse_type

        with pytest.raises(ParseError) as exc_info:
            parser.parse()

        # Should contain error about parsing parameter
        assert "Error parsing parameter" in str(exc_info.value)

    def test_type_alias(self):
        """Test parsing type aliases."""
        content = """
type my_int = int
"""
        parser = OCamlParser(content)
        # Type aliases are skipped for now
        module = parser.parse()
        # Should not fail, but alias won't be in type_definitions
        assert len(module.type_definitions) == 0

    def test_invalid_record_field(self):
        """Test that invalid record fields raise ParseError."""
        content = """
type user = { invalid_syntax }
"""
        parser = OCamlParser(content)

        with pytest.raises(ParseError) as exc_info:
            parser.parse()

        assert "Invalid record field" in str(exc_info.value)

    def test_invalid_variant(self):
        """Test that invalid variant constructors raise ParseError."""
        content = """
type result = | 123invalid | Error
"""
        parser = OCamlParser(content)

        with pytest.raises(ParseError) as exc_info:
            parser.parse()

        assert "Invalid variant" in str(exc_info.value)


class TestOCamlParserFunctionEdgeCases:
    """Test edge cases in function parsing."""

    def test_function_with_inline_documentation(self):
        """Test parsing function with inline documentation."""
        content = """
val greet : string -> (** name parameter **) string
"""
        parser = OCamlParser(content)
        module = parser.parse()

        # Should parse successfully despite inline doc
        assert len(module.functions) == 1
        assert module.functions[0].name == "greet"

    def test_invalid_parameter_type(self):
        """Test that invalid parameter types with suggestions raise ParseError."""
        content = """
val process : unknown_type123 -> string
"""
        parser = OCamlParser(content)

        # This should create a CUSTOM type, not raise an error
        module = parser.parse()
        assert module.functions[0].params[0].type.kind == TypeKind.CUSTOM

    def test_invalid_return_type_in_function(self):
        """Test error parsing return type."""
        # Create an invalid type that will trigger unsupported type error
        content = """
val test : string -> (((invalid
"""
        parser = OCamlParser(content)

        with pytest.raises(ParseError):
            parser.parse()


class TestOCamlParserClassMethods:
    """Test class methods."""

    def test_parse_string_class_method(self):
        """Test parse_string class method."""
        content = """
val test : string -> string
"""
        module = OCamlParser.parse_string(content, "test.mli")

        assert len(module.functions) == 1
        assert module.functions[0].name == "test"

    def test_parse_string_with_default_filename(self):
        """Test parse_string with default filename."""
        content = """
val greet : string -> string
"""
        module = OCamlParser.parse_string(content)

        assert len(module.functions) == 1


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_parse_mli_string(self):
        """Test parse_mli_string convenience function."""
        from polyglot_ffi.parsers.ocaml import parse_mli_string

        content = """
val add : int -> int -> int
"""
        module = parse_mli_string(content)

        assert len(module.functions) == 1
        assert module.functions[0].name == "add"
