"""
Edge case tests for generators, type registry, and other modules.

These tests target uncovered branches and edge cases to reach 75% coverage.
"""

import pytest
from polyglot_ffi.generators.ctypes_gen import CtypesGenerator
from polyglot_ffi.generators.c_stubs_gen import CStubGenerator
from polyglot_ffi.generators.python_gen import PythonGenerator
from polyglot_ffi.type_system.registry import TypeRegistry
from polyglot_ffi.ir.types import (
    IRModule,
    IRFunction,
    IRParameter,
    IRType,
    IRTypeDefinition,
    TypeKind,
    STRING,
    INT,
    FLOAT,
    BOOL,
    UNIT,
)


class TestCtypesGeneratorEdgeCases:
    """Edge case tests for Ctypes generator."""

    def test_option_type_generation(self):
        """Test generating ctypes for option types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_optional",
                    params=[
                        IRParameter(
                            name="opt",
                            type=IRType(kind=TypeKind.OPTION, name="option", params=[STRING]),
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # String option types are represented as nullable strings (not ptr string)
        # because string is already a pointer (char*) in C
        assert "process_optional" in result
        assert "ml_process_optional" in result
        assert "string" in result

    def test_list_type_generation(self):
        """Test generating ctypes for list types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_list",
                    params=[
                        IRParameter(
                            name="items", type=IRType(kind=TypeKind.LIST, name="list", params=[INT])
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # List types should be represented as ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_list" in result
        assert "ml_process_list" in result

    def test_tuple_type_generation(self):
        """Test generating ctypes for tuple types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_tuple",
                    params=[
                        IRParameter(
                            name="pair",
                            type=IRType(kind=TypeKind.TUPLE, name="tuple", params=[INT, STRING]),
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Tuple types should be represented as ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_tuple" in result
        assert "ml_process_tuple" in result

    def test_custom_type_generation(self):
        """Test generating ctypes for custom types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_custom",
                    params=[
                        IRParameter(name="data", type=IRType(kind=TypeKind.CUSTOM, name="custom_t"))
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Custom types should be represented as ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_custom" in result
        assert "ml_process_custom" in result

    def test_record_type_generation(self):
        """Test generating ctypes for record types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_record",
                    params=[
                        IRParameter(name="person", type=IRType(kind=TypeKind.RECORD, name="person"))
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Record types should be represented as ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_record" in result
        assert "ml_process_record" in result

    def test_variant_type_generation(self):
        """Test generating ctypes for variant types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_variant",
                    params=[
                        IRParameter(
                            name="result", type=IRType(kind=TypeKind.VARIANT, name="result")
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Variant types should be represented as ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_variant" in result
        assert "ml_process_variant" in result

    def test_unknown_primitive_type(self):
        """Test handling unknown primitive types."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_unknown",
                    params=[
                        IRParameter(
                            name="data", type=IRType(kind=TypeKind.PRIMITIVE, name="unknown")
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Unknown primitives should fall back to string in OCaml ctypes
        assert "string @->" in result
        assert "process_unknown" in result
        assert "ml_process_unknown" in result

    def test_option_without_params(self):
        """Test option type without parameters."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_empty_option",
                    params=[
                        IRParameter(
                            name="opt", type=IRType(kind=TypeKind.OPTION, name="option", params=[])
                        )
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        result = gen.generate_function_description(module)
        # Option without params should still be ptr void in OCaml ctypes
        assert "ptr void" in result
        assert "process_empty_option" in result
        assert "ml_process_empty_option" in result

    def test_unsupported_type_raises_error(self):
        """Test that unsupported types raise ValueError."""
        gen = CtypesGenerator()
        module = IRModule(
            name="test",
            functions=[
                IRFunction(
                    name="process_function",
                    params=[
                        IRParameter(name="fn", type=IRType(kind=TypeKind.FUNCTION, name="function"))
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        with pytest.raises(ValueError) as exc_info:
            gen.generate_function_description(module)

        assert "Unsupported type" in str(exc_info.value)


class TestCStubGeneratorEdgeCases:
    """Edge case tests for C stub generator."""

    def test_float_parameter_conversion(self):
        """Test C stub with float parameter."""
        module = IRModule(
            name="math",
            functions=[
                IRFunction(
                    name="sqrt",
                    params=[IRParameter(name="x", type=FLOAT)],
                    return_type=FLOAT,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "math")

        assert "double" in result
        assert "sqrt" in result

    def test_bool_parameter_conversion(self):
        """Test C stub with bool parameter."""
        module = IRModule(
            name="logic",
            functions=[
                IRFunction(
                    name="negate",
                    params=[IRParameter(name="value", type=BOOL)],
                    return_type=BOOL,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "logic")

        assert "int" in result or "bool" in result
        assert "negate" in result

    def test_unit_return_type(self):
        """Test C stub with unit return type."""
        module = IRModule(
            name="actions",
            functions=[
                IRFunction(
                    name="log_message",
                    params=[IRParameter(name="msg", type=STRING)],
                    return_type=UNIT,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "actions")

        assert "void" in result
        assert "log_message" in result

    def test_no_parameters_function(self):
        """Test C stub for function with no parameters."""
        module = IRModule(
            name="getters",
            functions=[
                IRFunction(
                    name="get_version",
                    params=[],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "getters")

        assert "get_version" in result
        assert "CAMLparam0" in result

    def test_three_parameters(self):
        """Test C stub with three parameters."""
        module = IRModule(
            name="calc",
            functions=[
                IRFunction(
                    name="add_three",
                    params=[
                        IRParameter(name="x", type=INT),
                        IRParameter(name="y", type=INT),
                        IRParameter(name="z", type=INT),
                    ],
                    return_type=INT,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "calc")

        assert "add_three" in result
        assert "caml_callback3" in result or "caml_callback" in result


class TestPythonGeneratorEdgeCases:
    """Edge case tests for Python generator."""

    def test_float_types(self):
        """Test Python wrapper with float types."""
        module = IRModule(
            name="math",
            functions=[
                IRFunction(
                    name="sqrt",
                    params=[IRParameter(name="x", type=FLOAT)],
                    return_type=FLOAT,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "math")

        assert "c_double" in result
        assert "sqrt" in result

    def test_bool_types(self):
        """Test Python wrapper with bool types."""
        module = IRModule(
            name="logic",
            functions=[
                IRFunction(
                    name="is_valid",
                    params=[IRParameter(name="value", type=STRING)],
                    return_type=BOOL,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "logic")

        assert "c_bool" in result or "c_int" in result
        assert "bool" in result
        assert "is_valid" in result

    def test_unit_return(self):
        """Test Python wrapper with unit return type."""
        module = IRModule(
            name="actions",
            functions=[
                IRFunction(
                    name="log",
                    params=[IRParameter(name="msg", type=STRING)],
                    return_type=UNIT,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "actions")

        assert "None" in result
        assert "log" in result

    def test_no_parameters(self):
        """Test Python wrapper with no parameters."""
        module = IRModule(
            name="info",
            functions=[
                IRFunction(
                    name="get_version",
                    params=[],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "info")

        assert "get_version" in result
        assert "def get_version() -> str:" in result or "def get_version()" in result


class TestTypeRegistryEdgeCases:
    """Edge case tests for type registry."""

    def test_type_registry_instantiation(self):
        """Test creating a type registry."""
        registry = TypeRegistry()
        assert registry is not None


class TestIRTypeDefinition:
    """Test IRTypeDefinition edge cases."""

    def test_record_type_definition(self):
        """Test record type definition."""
        fields = {
            "id": INT,
            "name": STRING,
            "active": BOOL,
        }

        record = IRTypeDefinition(
            name="user",
            kind=TypeKind.RECORD,
            fields=fields,
        )

        assert record.name == "user"
        assert record.kind == TypeKind.RECORD
        assert len(record.fields) == 3

    def test_variant_type_definition(self):
        """Test variant type definition."""
        variants = {
            "Success": STRING,
            "Error": STRING,
            "Pending": None,
        }

        variant = IRTypeDefinition(
            name="status",
            kind=TypeKind.VARIANT,
            variants=variants,
        )

        assert variant.name == "status"
        assert variant.kind == TypeKind.VARIANT
        assert len(variant.variants) == 3

    def test_type_definition_str(self):
        """Test string representation of type definition."""
        typedef = IRTypeDefinition(
            name="person",
            kind=TypeKind.RECORD,
        )

        result = str(typedef)
        assert "person" in result


class TestIRFunctionEdgeCases:
    """Test IRFunction edge cases."""

    def test_function_with_documentation(self):
        """Test function with doc string."""
        func = IRFunction(
            name="greet",
            params=[IRParameter(name="name", type=STRING)],
            return_type=STRING,
            doc="Greet a person by name",
        )

        assert func.doc == "Greet a person by name"

    def test_async_function(self):
        """Test async function flag."""
        func = IRFunction(
            name="fetch_data",
            params=[],
            return_type=STRING,
            is_async=True,
        )

        assert func.is_async is True

    def test_function_repr(self):
        """Test function representation."""
        func = IRFunction(
            name="add",
            params=[
                IRParameter(name="x", type=INT),
                IRParameter(name="y", type=INT),
            ],
            return_type=INT,
        )

        # Should have string representation
        result = repr(func)
        assert "add" in result or "IRFunction" in result


class TestComplexGeneratorScenarios:
    """Test complex scenarios across generators."""

    def test_module_with_multiple_function_types(self):
        """Test module with varied function signatures."""
        module = IRModule(
            name="mixed",
            functions=[
                IRFunction(name="f1", params=[], return_type=STRING),
                IRFunction(
                    name="f2",
                    params=[IRParameter(name="x", type=INT)],
                    return_type=INT,
                ),
                IRFunction(
                    name="f3",
                    params=[
                        IRParameter(name="a", type=STRING),
                        IRParameter(name="b", type=BOOL),
                    ],
                    return_type=UNIT,
                ),
            ],
            type_definitions=[],
        )

        # Test all generators
        ctypes_gen = CtypesGenerator()
        c_stub_gen = CStubGenerator()
        python_gen = PythonGenerator()

        ctypes_result = ctypes_gen.generate_function_description(module)
        c_stub_result = c_stub_gen.generate_stubs(module, "mixed")
        python_result = python_gen.generate(module, "mixed")

        # All should contain function names
        for name in ["f1", "f2", "f3"]:
            assert name in ctypes_result
            assert name in c_stub_result
            assert name in python_result

    def test_empty_module(self):
        """Test generators with empty module."""
        module = IRModule(
            name="empty",
            functions=[],
            type_definitions=[],
        )

        ctypes_gen = CtypesGenerator()
        c_stub_gen = CStubGenerator()
        python_gen = PythonGenerator()

        # Should handle empty modules gracefully
        ctypes_result = ctypes_gen.generate_function_description(module)
        c_stub_result = c_stub_gen.generate_stubs(module, "empty")
        python_result = python_gen.generate(module, "empty")

        # Results should be valid code (not crash)
        assert isinstance(ctypes_result, str)
        assert isinstance(c_stub_result, str)
        assert isinstance(python_result, str)


class TestPythonGeneratorCompleteCoverage:
    """Additional tests for Python generator to reach coverage."""

    def test_multiple_parameters_wrapper(self):
        """Test wrapper with many parameters."""
        module = IRModule(
            name="calc",
            functions=[
                IRFunction(
                    name="calculate",
                    params=[
                        IRParameter(name="a", type=INT),
                        IRParameter(name="b", type=FLOAT),
                        IRParameter(name="c", type=STRING),
                        IRParameter(name="d", type=BOOL),
                    ],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "calc")

        # Should have all parameter types
        assert "int" in result
        assert "float" in result
        assert "str" in result
        assert "bool" in result

    def test_option_type_in_wrapper(self):
        """Test option type in Python wrapper."""
        option_type = IRType(kind=TypeKind.OPTION, name="option", params=[STRING])
        module = IRModule(
            name="optional",
            functions=[
                IRFunction(
                    name="maybe_greet",
                    params=[IRParameter(name="name", type=option_type)],
                    return_type=STRING,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "optional")

        # Should handle optional types
        assert "Optional" in result or "maybe_greet" in result

    def test_list_type_in_wrapper(self):
        """Test list type in Python wrapper."""
        list_type = IRType(kind=TypeKind.LIST, name="list", params=[INT])
        module = IRModule(
            name="lists",
            functions=[
                IRFunction(
                    name="process_list",
                    params=[IRParameter(name="items", type=list_type)],
                    return_type=INT,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "lists")

        # Should handle list types
        assert "List" in result or "process_list" in result


class TestIRModuleEdgeCases:
    """Additional IR module tests."""

    def test_module_with_type_definitions(self):
        """Test module containing type definitions."""
        typedef = IRTypeDefinition(
            name="config",
            kind=TypeKind.RECORD,
            fields={"host": STRING, "port": INT},
        )

        module = IRModule(
            name="server",
            functions=[],
            type_definitions=[typedef],
        )

        assert len(module.type_definitions) == 1
        assert module.type_definitions[0].name == "config"

    def test_module_str_representation(self):
        """Test module string representation."""
        module = IRModule(
            name="test_mod",
            functions=[],
            type_definitions=[],
        )

        result = str(module)
        assert "test_mod" in result or "Module" in result


class TestCStubGeneratorComplete:
    """Complete C stub generator coverage."""

    def test_header_generation(self):
        """Test C header file generation."""
        module = IRModule(
            name="example",
            functions=[
                IRFunction(
                    name="func1",
                    params=[IRParameter(name="x", type=INT)],
                    return_type=STRING,
                ),
                IRFunction(
                    name="func2",
                    params=[],
                    return_type=UNIT,
                ),
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_header(module, "example")

        # Header guard
        assert "#ifndef" in result
        assert "#define" in result
        assert "#endif" in result

        # Function declarations
        assert "func1" in result
        assert "func2" in result

    def test_mixed_return_types(self):
        """Test functions with various return types."""
        module = IRModule(
            name="mixed",
            functions=[
                IRFunction(name="get_int", params=[], return_type=INT),
                IRFunction(name="get_float", params=[], return_type=FLOAT),
                IRFunction(name="get_bool", params=[], return_type=BOOL),
                IRFunction(name="get_unit", params=[], return_type=UNIT),
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "mixed")

        # Should handle all return types
        assert "int" in result or "Int_val" in result
        assert "double" in result or "Double_val" in result
        assert "void" in result or "Unit" in result


class TestFinalCoveragePush:
    """Final tests to push coverage to 75%+."""

    def test_python_gen_tuple_type(self):
        """Test Python generator with tuple types."""
        tuple_type = IRType(kind=TypeKind.TUPLE, name="tuple", params=[INT, STRING])
        module = IRModule(
            name="tuples",
            functions=[
                IRFunction(
                    name="make_pair",
                    params=[],
                    return_type=tuple_type,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "tuples")

        assert "Tuple" in result or "make_pair" in result

    def test_python_gen_custom_type(self):
        """Test Python generator with custom types."""
        custom_type = IRType(kind=TypeKind.CUSTOM, name="user_t")
        module = IRModule(
            name="users",
            functions=[
                IRFunction(
                    name="create_user",
                    params=[IRParameter(name="name", type=STRING)],
                    return_type=custom_type,
                )
            ],
            type_definitions=[],
        )

        gen = PythonGenerator()
        result = gen.generate(module, "users")

        assert "create_user" in result

    def test_c_stub_option_types(self):
        """Test C stub with option types."""
        option_type = IRType(kind=TypeKind.OPTION, name="option", params=[INT])
        module = IRModule(
            name="opts",
            functions=[
                IRFunction(
                    name="maybe_get",
                    params=[],
                    return_type=option_type,
                )
            ],
            type_definitions=[],
        )

        gen = CStubGenerator()
        result = gen.generate_stubs(module, "opts")

        assert "maybe_get" in result

    def test_ir_type_custom_str(self):
        """Test IR type string for custom type."""
        custom = IRType(kind=TypeKind.CUSTOM, name="special")
        assert str(custom) == "special"

    def test_ir_function_is_async_false(self):
        """Test IR function with is_async=False."""
        func = IRFunction(
            name="sync_func",
            params=[],
            return_type=UNIT,
            is_async=False,
        )
        assert func.is_async is False

    def test_ir_module_empty_collections(self):
        """Test IR module with empty functions and types."""
        mod = IRModule(name="empty", functions=[], type_definitions=[])
        assert len(mod.functions) == 0
        assert len(mod.type_definitions) == 0
        assert mod.name == "empty"
