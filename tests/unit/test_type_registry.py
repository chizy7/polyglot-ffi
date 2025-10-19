"""
Tests for the Type Registry system.
"""

import pytest
from polyglot_ffi.type_system.registry import TypeRegistry, TypeMappingError
from polyglot_ffi.type_system.builtin import register_builtin_types
from polyglot_ffi.ir.types import (
    IRType,
    TypeKind,
    ir_primitive,
    ir_option,
    ir_list,
    ir_tuple,
)


class TestTypeRegistry:
    """Test type registry functionality."""

    def test_register_primitive(self):
        """Test registering a primitive type."""
        registry = TypeRegistry()
        registry.register_primitive("string", {
            "python": "str",
            "rust": "String",
            "c": "char*"
        })

        ir_type = ir_primitive("string")
        assert registry.get_mapping(ir_type, "python") == "str"
        assert registry.get_mapping(ir_type, "rust") == "String"
        assert registry.get_mapping(ir_type, "c") == "char*"

    def test_missing_primitive(self):
        """Test error when primitive type not registered."""
        registry = TypeRegistry()

        ir_type = ir_primitive("unknown")
        with pytest.raises(TypeMappingError, match="Unknown primitive"):
            registry.get_mapping(ir_type, "python")

    def test_missing_language(self):
        """Test error when language not supported for type."""
        registry = TypeRegistry()
        registry.register_primitive("string", {"python": "str"})

        ir_type = ir_primitive("string")
        with pytest.raises(TypeMappingError, match="No rust mapping"):
            registry.get_mapping(ir_type, "rust")

    def test_validate_type(self):
        """Test type validation."""
        registry = TypeRegistry()
        registry.register_primitive("string", {"python": "str"})

        ir_type = ir_primitive("string")
        assert registry.validate(ir_type, "python") is True
        assert registry.validate(ir_type, "rust") is False


class TestBuiltinTypes:
    """Test built-in type mappings."""

    def test_string_mappings(self):
        """Test string type mappings."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_primitive("string")
        assert registry.get_mapping(ir_type, "ocaml") == "string"
        assert registry.get_mapping(ir_type, "python") == "str"
        assert registry.get_mapping(ir_type, "c") == "char*"
        assert registry.get_mapping(ir_type, "rust") == "String"

    def test_int_mappings(self):
        """Test int type mappings."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_primitive("int")
        assert registry.get_mapping(ir_type, "ocaml") == "int"
        assert registry.get_mapping(ir_type, "python") == "int"
        assert registry.get_mapping(ir_type, "c") == "int"
        assert registry.get_mapping(ir_type, "rust") == "i64"

    def test_float_mappings(self):
        """Test float type mappings."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_primitive("float")
        assert registry.get_mapping(ir_type, "python") == "float"
        assert registry.get_mapping(ir_type, "c") == "double"
        assert registry.get_mapping(ir_type, "rust") == "f64"

    def test_bool_mappings(self):
        """Test bool type mappings."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_primitive("bool")
        assert registry.get_mapping(ir_type, "python") == "bool"
        assert registry.get_mapping(ir_type, "c") == "int"

    def test_unit_mappings(self):
        """Test unit type mappings."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_primitive("unit")
        assert registry.get_mapping(ir_type, "ocaml") == "unit"
        assert registry.get_mapping(ir_type, "python") == "None"
        assert registry.get_mapping(ir_type, "c") == "void"
        assert registry.get_mapping(ir_type, "rust") == "()"


class TestOptionTypes:
    """Test option type mappings."""

    def test_option_python(self):
        """Test option type in Python."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_primitive("string"))
        result = registry.get_mapping(ir_type, "python")
        assert result == "Optional[str]"

    def test_option_rust(self):
        """Test option type in Rust."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_primitive("int"))
        result = registry.get_mapping(ir_type, "rust")
        assert result == "Option<i64>"

    def test_option_ocaml(self):
        """Test option type in OCaml."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_primitive("string"))
        result = registry.get_mapping(ir_type, "ocaml")
        assert result == "string option"

    def test_option_c(self):
        """Test option type in C (nullable pointer)."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_primitive("int"))
        result = registry.get_mapping(ir_type, "c")
        assert result == "int*"

    def test_nested_option(self):
        """Test nested option types."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_option(ir_primitive("string")))
        result = registry.get_mapping(ir_type, "python")
        assert result == "Optional[Optional[str]]"


class TestListTypes:
    """Test list type mappings."""

    def test_list_python(self):
        """Test list type in Python."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_list(ir_primitive("string"))
        result = registry.get_mapping(ir_type, "python")
        assert result == "List[str]"

    def test_list_rust(self):
        """Test list type in Rust."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_list(ir_primitive("int"))
        result = registry.get_mapping(ir_type, "rust")
        assert result == "Vec<i64>"

    def test_list_ocaml(self):
        """Test list type in OCaml."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_list(ir_primitive("float"))
        result = registry.get_mapping(ir_type, "ocaml")
        assert result == "float list"

    def test_list_of_options(self):
        """Test list of options."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_list(ir_option(ir_primitive("int")))
        result = registry.get_mapping(ir_type, "python")
        assert result == "List[Optional[int]]"


class TestTupleTypes:
    """Test tuple type mappings."""

    def test_tuple_python(self):
        """Test tuple type in Python."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_tuple(ir_primitive("int"), ir_primitive("string"))
        result = registry.get_mapping(ir_type, "python")
        assert result == "Tuple[int, str]"

    def test_tuple_rust(self):
        """Test tuple type in Rust."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_tuple(ir_primitive("int"), ir_primitive("string"))
        result = registry.get_mapping(ir_type, "rust")
        assert result == "(i64, String)"

    def test_tuple_ocaml(self):
        """Test tuple type in OCaml."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_tuple(ir_primitive("int"), ir_primitive("string"))
        result = registry.get_mapping(ir_type, "ocaml")
        assert result == "(int * string)"

    def test_triple(self):
        """Test 3-tuple."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_tuple(
            ir_primitive("int"),
            ir_primitive("string"),
            ir_primitive("float")
        )
        result = registry.get_mapping(ir_type, "python")
        assert result == "Tuple[int, str, float]"


class TestCustomTypes:
    """Test custom type mappings."""

    def test_custom_type_python(self):
        """Test custom type in Python (capitalized)."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.CUSTOM, name="user")
        result = registry.get_mapping(ir_type, "python")
        assert result == "User"

    def test_custom_type_c(self):
        """Test custom type in C (with _t suffix)."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.CUSTOM, name="user")
        result = registry.get_mapping(ir_type, "c")
        assert result == "user_t"

    def test_custom_type_ocaml(self):
        """Test custom type in OCaml (lowercase)."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.CUSTOM, name="user")
        result = registry.get_mapping(ir_type, "ocaml")
        assert result == "user"

    def test_record_type(self):
        """Test record type mapping."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.RECORD, name="user")
        result = registry.get_mapping(ir_type, "python")
        assert result == "User"

    def test_variant_type(self):
        """Test variant type mapping."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.VARIANT, name="status")
        result = registry.get_mapping(ir_type, "python")
        assert result == "Status"


class TestCustomConverters:
    """Test custom converter registration."""

    def test_register_converter(self):
        """Test registering a custom converter function."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        # Register a custom converter for a specific type
        def custom_converter(ir_type: IRType) -> str:
            return f"Custom_{ir_type.name}"

        registry.register_converter("user", "python", custom_converter)

        ir_type = IRType(kind=TypeKind.CUSTOM, name="user")
        result = registry.get_mapping(ir_type, "python")
        assert result == "Custom_user"

    def test_converter_override(self):
        """Test that custom converter overrides default behavior."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = IRType(kind=TypeKind.CUSTOM, name="special")

        # Get default mapping
        default_result = registry.get_mapping(ir_type, "python")
        assert default_result == "Special"

        # Register custom converter
        registry.register_converter("special", "python", lambda _: "VerySpecial")
        custom_result = registry.get_mapping(ir_type, "python")
        assert custom_result == "VerySpecial"


class TestComplexCombinations:
    """Test complex type combinations."""

    def test_option_of_list(self):
        """Test option of list."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_option(ir_list(ir_primitive("string")))
        result = registry.get_mapping(ir_type, "python")
        assert result == "Optional[List[str]]"

    def test_list_of_tuples(self):
        """Test list of tuples."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_list(ir_tuple(ir_primitive("int"), ir_primitive("string")))
        result = registry.get_mapping(ir_type, "python")
        assert result == "List[Tuple[int, str]]"

    def test_tuple_of_options(self):
        """Test tuple of options."""
        registry = TypeRegistry()
        register_builtin_types(registry)

        ir_type = ir_tuple(
            ir_option(ir_primitive("int")),
            ir_option(ir_primitive("string"))
        )
        result = registry.get_mapping(ir_type, "python")
        assert result == "Tuple[Optional[int], Optional[str]]"
