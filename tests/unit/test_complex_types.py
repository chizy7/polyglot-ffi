"""
Tests for parsing complex types: options, lists, tuples, records, and variants.
"""

import pytest
from polyglot_ffi.parsers.ocaml import OCamlParser, ParseError
from polyglot_ffi.ir.types import TypeKind, IRTypeDefinition


class TestOptionTypes:
    """Test parsing of option types."""

    def test_string_option(self):
        """Test parsing string option type."""
        code = "val find : string -> string option"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        assert len(module.functions) == 1
        func = module.functions[0]
        assert func.name == "find"
        assert func.return_type.kind == TypeKind.OPTION
        assert func.return_type.params[0].name == "string"

    def test_int_option(self):
        """Test parsing int option type."""
        code = "val parse : string -> int option"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.OPTION
        assert func.return_type.params[0].name == "int"

    def test_nested_option(self):
        """Test parsing nested option types."""
        code = "val deep : string -> string option option"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.OPTION
        inner = func.return_type.params[0]
        assert inner.kind == TypeKind.OPTION
        assert inner.params[0].name == "string"


class TestListTypes:
    """Test parsing of list types."""

    def test_string_list(self):
        """Test parsing string list type."""
        code = "val get_all : unit -> string list"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.LIST
        assert func.return_type.params[0].name == "string"

    def test_int_list(self):
        """Test parsing int list type."""
        code = "val numbers : int -> int list"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.LIST
        assert func.return_type.params[0].name == "int"

    def test_list_parameter(self):
        """Test parsing function with list parameter."""
        code = "val process : int list -> int"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert len(func.params) == 1
        param = func.params[0]
        assert param.type.kind == TypeKind.LIST
        assert param.type.params[0].name == "int"

    def test_list_of_options(self):
        """Test parsing list of options."""
        code = "val maybes : unit -> int option list"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.LIST
        inner = func.return_type.params[0]
        assert inner.kind == TypeKind.OPTION
        assert inner.params[0].name == "int"


class TestTupleTypes:
    """Test parsing of tuple types."""

    def test_pair(self):
        """Test parsing a pair (2-tuple)."""
        code = "val pair : string -> int * string"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.TUPLE
        assert len(func.return_type.params) == 2
        assert func.return_type.params[0].name == "int"
        assert func.return_type.params[1].name == "string"

    def test_triple(self):
        """Test parsing a triple (3-tuple)."""
        code = "val triple : unit -> int * string * float"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.TUPLE
        assert len(func.return_type.params) == 3
        assert func.return_type.params[0].name == "int"
        assert func.return_type.params[1].name == "string"
        assert func.return_type.params[2].name == "float"

    def test_tuple_parameter(self):
        """Test parsing function with tuple parameter."""
        code = "val process : int * string -> bool"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        param = func.params[0]
        assert param.type.kind == TypeKind.TUPLE
        assert len(param.type.params) == 2

    def test_parenthesized_tuple(self):
        """Test parsing tuple with parentheses."""
        code = "val coords : unit -> (float * float)"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.TUPLE
        assert len(func.return_type.params) == 2


class TestRecordTypes:
    """Test parsing of record types."""

    def test_simple_record(self):
        """Test parsing a simple record type."""
        code = """
type user = { name: string; age: int }
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        assert len(module.type_definitions) == 1
        typedef = module.type_definitions[0]
        assert typedef.name == "user"
        assert typedef.kind == TypeKind.RECORD
        assert "name" in typedef.fields
        assert "age" in typedef.fields
        assert typedef.fields["name"].name == "string"
        assert typedef.fields["age"].name == "int"

    def test_multi_field_record(self):
        """Test parsing record with multiple fields."""
        code = """
type person = { name: string; age: int; email: string; active: bool }
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert len(typedef.fields) == 4
        assert typedef.fields["active"].name == "bool"

    def test_record_with_complex_types(self):
        """Test parsing record with complex field types."""
        code = """
type profile = { name: string; tags: string list }
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert typedef.fields["name"].name == "string"
        assert typedef.fields["tags"].kind == TypeKind.LIST
        assert typedef.fields["tags"].params[0].name == "string"

    def test_function_with_record_param(self):
        """Test parsing function with record parameter."""
        code = """
type user = { name: string; age: int }
val create_user : user -> bool
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        assert len(module.type_definitions) == 1
        assert len(module.functions) == 1
        func = module.functions[0]
        assert func.params[0].type.name == "user"
        assert func.params[0].type.kind == TypeKind.CUSTOM


class TestVariantTypes:
    """Test parsing of variant types."""

    def test_simple_variant(self):
        """Test parsing simple variant without payloads."""
        code = """
type status = Success | Failure | Pending
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        assert len(module.type_definitions) == 1
        typedef = module.type_definitions[0]
        assert typedef.name == "status"
        assert typedef.kind == TypeKind.VARIANT
        assert "Success" in typedef.variants
        assert "Failure" in typedef.variants
        assert "Pending" in typedef.variants
        assert typedef.variants["Success"] is None  # No payload

    def test_variant_with_payloads(self):
        """Test parsing variant with payload types."""
        code = """
type result = Ok of string | Error of string
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert typedef.kind == TypeKind.VARIANT
        assert typedef.variants["Ok"].name == "string"
        assert typedef.variants["Error"].name == "string"

    def test_variant_mixed_payloads(self):
        """Test parsing variant with mixed constructors."""
        code = """
type response = Success | Partial of int | Full of string
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert typedef.variants["Success"] is None
        assert typedef.variants["Partial"].name == "int"
        assert typedef.variants["Full"].name == "string"

    def test_variant_with_complex_payload(self):
        """Test parsing variant with complex payload types."""
        code = """
type data = Empty | Items of string list | Pair of int * string
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert typedef.variants["Empty"] is None

        items_payload = typedef.variants["Items"]
        assert items_payload.kind == TypeKind.LIST
        assert items_payload.params[0].name == "string"

        pair_payload = typedef.variants["Pair"]
        assert pair_payload.kind == TypeKind.TUPLE
        assert len(pair_payload.params) == 2

    def test_function_with_variant_return(self):
        """Test parsing function returning variant."""
        code = """
type result = Ok of string | Error of string
val process : string -> result
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.name == "result"
        assert func.return_type.kind == TypeKind.CUSTOM


class TestComplexCombinations:
    """Test complex combinations of types."""

    def test_option_list(self):
        """Test option of list."""
        code = "val maybe_list : unit -> string list option"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.OPTION
        inner = func.return_type.params[0]
        assert inner.kind == TypeKind.LIST
        assert inner.params[0].name == "string"

    def test_list_of_tuples(self):
        """Test list of tuples."""
        code = "val pairs : unit -> (int * string) list"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.LIST
        inner = func.return_type.params[0]
        assert inner.kind == TypeKind.TUPLE
        assert len(inner.params) == 2

    def test_multiple_type_definitions(self):
        """Test multiple type definitions in one file."""
        code = """
type user = { name: string; age: int }
type status = Active | Inactive
val get_user : user -> status
"""
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        assert len(module.type_definitions) == 2
        assert len(module.functions) == 1

        user_type = module.get_type("user")
        assert user_type.kind == TypeKind.RECORD

        status_type = module.get_type("status")
        assert status_type.kind == TypeKind.VARIANT


class TestTypeVariables:
    """Test generic/polymorphic type variables."""

    def test_type_variable_single(self):
        """Test single type variable."""
        code = "val identity : 'a -> 'a"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.params[0].type.name == "'a"
        assert func.return_type.name == "'a"

    def test_type_variable_option(self):
        """Test type variable in option."""
        code = "val optional : 'a -> 'a option"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.OPTION
        assert func.return_type.params[0].name == "'a"

    def test_type_variable_list(self):
        """Test type variable in list."""
        code = "val singleton : 'a -> 'a list"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        func = module.functions[0]
        assert func.return_type.kind == TypeKind.LIST
        assert func.return_type.params[0].name == "'a"


class TestErrorCases:
    """Test error handling for invalid type syntax."""

    def test_invalid_option_syntax(self):
        """Test error on invalid option syntax."""
        code = "val bad : option string"  # Wrong order
        parser = OCamlParser(code, "test.mli")

        with pytest.raises(ParseError):
            parser.parse()

    def test_empty_record(self):
        """Test error on empty record."""
        code = "type empty = {}"
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert len(typedef.fields) == 0  # Should handle empty records

    def test_invalid_variant_syntax(self):
        """Test parsing with slightly malformed variant (should be tolerant)."""
        code = "type result = Ok of string"  # Single constructor
        parser = OCamlParser(code, "test.mli")
        module = parser.parse()

        typedef = module.type_definitions[0]
        assert typedef.kind == TypeKind.VARIANT
        assert "Ok" in typedef.variants
