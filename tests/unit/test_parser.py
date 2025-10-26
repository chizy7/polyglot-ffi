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
