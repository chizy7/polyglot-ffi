"""
Unit tests for IR (Intermediate Representation) types.
"""

import pytest

from polyglot_ffi.ir.types import (
    TypeKind,
    IRType,
    IRParameter,
    IRFunction,
    IRModule,
    STRING,
    INT,
    FLOAT,
    BOOL,
    UNIT,
)


class TestTypeKind:
    """Test TypeKind enum."""

    def test_type_kind_values(self):
        """Test that TypeKind has all expected values."""
        assert TypeKind.PRIMITIVE.value == "primitive"
        assert TypeKind.OPTION.value == "option"
        assert TypeKind.LIST.value == "list"
        assert TypeKind.TUPLE.value == "tuple"
        assert TypeKind.RECORD.value == "record"
        assert TypeKind.VARIANT.value == "variant"
        assert TypeKind.FUNCTION.value == "function"
        assert TypeKind.CUSTOM.value == "custom"


class TestIRType:
    """Test IRType dataclass."""

    def test_primitive_type(self):
        """Test creating primitive type."""
        t = IRType(kind=TypeKind.PRIMITIVE, name="string")

        assert t.kind == TypeKind.PRIMITIVE
        assert t.name == "string"
        assert t.params == []
        assert t.fields == {}
        assert t.variants == {}

    def test_option_type(self):
        """Test creating option type."""
        inner = IRType(kind=TypeKind.PRIMITIVE, name="int")
        t = IRType(kind=TypeKind.OPTION, name="option", params=[inner])

        assert t.kind == TypeKind.OPTION
        assert len(t.params) == 1
        assert t.params[0].name == "int"

    def test_list_type(self):
        """Test creating list type."""
        inner = IRType(kind=TypeKind.PRIMITIVE, name="string")
        t = IRType(kind=TypeKind.LIST, name="list", params=[inner])

        assert t.kind == TypeKind.LIST
        assert len(t.params) == 1

    def test_tuple_type(self):
        """Test creating tuple type."""
        t1 = IRType(kind=TypeKind.PRIMITIVE, name="int")
        t2 = IRType(kind=TypeKind.PRIMITIVE, name="string")
        t = IRType(kind=TypeKind.TUPLE, name="tuple", params=[t1, t2])

        assert t.kind == TypeKind.TUPLE
        assert len(t.params) == 2

    def test_record_type(self):
        """Test creating record type."""
        fields = {
            "name": IRType(kind=TypeKind.PRIMITIVE, name="string"),
            "age": IRType(kind=TypeKind.PRIMITIVE, name="int"),
        }
        t = IRType(kind=TypeKind.RECORD, name="person", fields=fields)

        assert t.kind == TypeKind.RECORD
        assert t.name == "person"
        assert len(t.fields) == 2
        assert "name" in t.fields
        assert "age" in t.fields

    def test_variant_type(self):
        """Test creating variant type."""
        variants = {
            "Success": IRType(kind=TypeKind.PRIMITIVE, name="string"),
            "Error": IRType(kind=TypeKind.PRIMITIVE, name="string"),
        }
        t = IRType(kind=TypeKind.VARIANT, name="result", variants=variants)

        assert t.kind == TypeKind.VARIANT
        assert t.name == "result"
        assert len(t.variants) == 2

    def test_str_primitive(self):
        """Test string representation of primitive type."""
        t = IRType(kind=TypeKind.PRIMITIVE, name="string")
        assert str(t) == "string"

    def test_str_option(self):
        """Test string representation of option type."""
        inner = IRType(kind=TypeKind.PRIMITIVE, name="int")
        t = IRType(kind=TypeKind.OPTION, name="option", params=[inner])
        assert "option" in str(t)

    def test_str_list(self):
        """Test string representation of list type."""
        inner = IRType(kind=TypeKind.PRIMITIVE, name="string")
        t = IRType(kind=TypeKind.LIST, name="list", params=[inner])
        assert "list" in str(t)

    def test_str_tuple(self):
        """Test string representation of tuple type."""
        t1 = IRType(kind=TypeKind.PRIMITIVE, name="int")
        t2 = IRType(kind=TypeKind.PRIMITIVE, name="string")
        t = IRType(kind=TypeKind.TUPLE, name="tuple", params=[t1, t2])
        result = str(t)
        assert "int" in result
        assert "string" in result
        assert "*" in result

    def test_str_record(self):
        """Test string representation of record type."""
        fields = {"name": IRType(kind=TypeKind.PRIMITIVE, name="string")}
        t = IRType(kind=TypeKind.RECORD, name="user", fields=fields)
        assert "record user" in str(t)

    def test_str_variant(self):
        """Test string representation of variant type."""
        variants = {"Some": None, "None": None}
        t = IRType(kind=TypeKind.VARIANT, name="option", variants=variants)
        assert "variant option" in str(t)

    def test_is_primitive(self):
        """Test is_primitive method."""
        t = IRType(kind=TypeKind.PRIMITIVE, name="int")
        assert t.is_primitive()

        t2 = IRType(kind=TypeKind.LIST, name="list", params=[t])
        assert not t2.is_primitive()

    def test_is_container(self):
        """Test is_container method."""
        option_t = IRType(kind=TypeKind.OPTION, name="option")
        list_t = IRType(kind=TypeKind.LIST, name="list")
        tuple_t = IRType(kind=TypeKind.TUPLE, name="tuple")
        primitive_t = IRType(kind=TypeKind.PRIMITIVE, name="int")

        assert option_t.is_container()
        assert list_t.is_container()
        assert tuple_t.is_container()
        assert not primitive_t.is_container()

    def test_is_composite(self):
        """Test is_composite method."""
        record_t = IRType(kind=TypeKind.RECORD, name="record")
        variant_t = IRType(kind=TypeKind.VARIANT, name="variant")
        primitive_t = IRType(kind=TypeKind.PRIMITIVE, name="int")

        assert record_t.is_composite()
        assert variant_t.is_composite()
        assert not primitive_t.is_composite()


class TestPrimitiveConstants:
    """Test predefined primitive type constants."""

    def test_string_constant(self):
        """Test STRING constant."""
        assert STRING.kind == TypeKind.PRIMITIVE
        assert STRING.name == "string"

    def test_int_constant(self):
        """Test INT constant."""
        assert INT.kind == TypeKind.PRIMITIVE
        assert INT.name == "int"

    def test_float_constant(self):
        """Test FLOAT constant."""
        assert FLOAT.kind == TypeKind.PRIMITIVE
        assert FLOAT.name == "float"

    def test_bool_constant(self):
        """Test BOOL constant."""
        assert BOOL.kind == TypeKind.PRIMITIVE
        assert BOOL.name == "bool"

    def test_unit_constant(self):
        """Test UNIT constant."""
        assert UNIT.kind == TypeKind.PRIMITIVE
        assert UNIT.name == "unit"


class TestIRParameter:
    """Test IRParameter dataclass."""

    def test_basic_parameter(self):
        """Test creating basic parameter."""
        param_type = IRType(kind=TypeKind.PRIMITIVE, name="string")
        param = IRParameter(name="message", type=param_type)

        assert param.name == "message"
        assert param.type.name == "string"

    def test_parameter_str(self):
        """Test string representation of parameter."""
        param_type = IRType(kind=TypeKind.PRIMITIVE, name="int")
        param = IRParameter(name="count", type=param_type)

        result = str(param)
        assert "count" in result
        assert "int" in result

    def test_parameter_with_complex_type(self):
        """Test parameter with complex type."""
        inner = IRType(kind=TypeKind.PRIMITIVE, name="string")
        list_type = IRType(kind=TypeKind.LIST, name="list", params=[inner])
        param = IRParameter(name="items", type=list_type)

        assert param.name == "items"
        assert param.type.kind == TypeKind.LIST


class TestIRFunction:
    """Test IRFunction dataclass."""

    def test_basic_function(self):
        """Test creating basic function."""
        param = IRParameter(name="x", type=INT)
        func = IRFunction(
            name="increment",
            params=[param],
            return_type=INT,
            doc="Increment a number",
        )

        assert func.name == "increment"
        assert len(func.params) == 1
        assert func.return_type.name == "int"
        assert func.doc == "Increment a number"

    def test_function_no_params(self):
        """Test function with no parameters."""
        func = IRFunction(
            name="get_version",
            params=[],
            return_type=STRING,
        )

        assert func.name == "get_version"
        assert len(func.params) == 0

    def test_function_multiple_params(self):
        """Test function with multiple parameters."""
        params = [
            IRParameter(name="x", type=INT),
            IRParameter(name="y", type=INT),
            IRParameter(name="z", type=INT),
        ]
        func = IRFunction(
            name="add_three",
            params=params,
            return_type=INT,
        )

        assert len(func.params) == 3

    def test_function_str(self):
        """Test string representation of function."""
        param = IRParameter(name="name", type=STRING)
        func = IRFunction(
            name="greet",
            params=[param],
            return_type=STRING,
        )

        result = str(func)
        assert "greet" in result

    def test_function_defaults(self):
        """Test function with default values."""
        func = IRFunction(
            name="test",
            params=[],
            return_type=UNIT,
        )

        assert func.doc == ""
        assert not func.is_async


class TestIRModule:
    """Test IRModule dataclass."""

    def test_basic_module(self):
        """Test creating basic module."""
        func = IRFunction(
            name="hello",
            params=[],
            return_type=STRING,
        )
        module = IRModule(
            name="greetings",
            functions=[func],
            type_definitions=[],
        )

        assert module.name == "greetings"
        assert len(module.functions) == 1
        assert len(module.type_definitions) == 0

    def test_module_multiple_functions(self):
        """Test module with multiple functions."""
        f1 = IRFunction(name="f1", params=[], return_type=INT)
        f2 = IRFunction(name="f2", params=[], return_type=STRING)
        f3 = IRFunction(name="f3", params=[], return_type=BOOL)

        module = IRModule(
            name="multi",
            functions=[f1, f2, f3],
            type_definitions=[],
        )

        assert len(module.functions) == 3

    def test_module_with_type_definitions(self):
        """Test module with type definitions."""
        typedef = IRType(kind=TypeKind.RECORD, name="user")
        module = IRModule(
            name="types",
            functions=[],
            type_definitions=[typedef],
        )

        assert len(module.type_definitions) == 1
        assert module.type_definitions[0].name == "user"

    def test_module_str(self):
        """Test string representation of module."""
        module = IRModule(
            name="example",
            functions=[],
            type_definitions=[],
        )

        result = str(module)
        assert "example" in result

    def test_empty_module(self):
        """Test creating empty module."""
        module = IRModule(
            name="empty",
            functions=[],
            type_definitions=[],
        )

        assert module.name == "empty"
        assert len(module.functions) == 0
        assert len(module.type_definitions) == 0


class TestComplexIRTypes:
    """Test complex IR type combinations."""

    def test_option_of_list(self):
        """Test option<list<string>> type."""
        string_list = IRType(kind=TypeKind.LIST, name="list", params=[STRING])
        option_type = IRType(kind=TypeKind.OPTION, name="option", params=[string_list])

        assert option_type.kind == TypeKind.OPTION
        assert option_type.params[0].kind == TypeKind.LIST
        assert option_type.params[0].params[0].name == "string"

    def test_list_of_tuples(self):
        """Test list<(int, string)> type."""
        tuple_type = IRType(kind=TypeKind.TUPLE, name="tuple", params=[INT, STRING])
        list_type = IRType(kind=TypeKind.LIST, name="list", params=[tuple_type])

        assert list_type.kind == TypeKind.LIST
        assert list_type.params[0].kind == TypeKind.TUPLE
        assert len(list_type.params[0].params) == 2

    def test_record_with_complex_fields(self):
        """Test record with complex field types."""
        fields = {
            "id": INT,
            "name": STRING,
            "tags": IRType(kind=TypeKind.LIST, name="list", params=[STRING]),
            "metadata": IRType(kind=TypeKind.OPTION, name="option", params=[STRING]),
        }
        record = IRType(kind=TypeKind.RECORD, name="entity", fields=fields)

        assert len(record.fields) == 4
        assert record.fields["tags"].kind == TypeKind.LIST
        assert record.fields["metadata"].kind == TypeKind.OPTION

    def test_variant_with_payloads(self):
        """Test variant with different payload types."""
        variants = {
            "Success": STRING,
            "Failure": INT,
            "Pending": None,  # No payload
        }
        variant = IRType(kind=TypeKind.VARIANT, name="status", variants=variants)

        assert len(variant.variants) == 3
        assert variant.variants["Success"].name == "string"
        assert variant.variants["Pending"] is None
