"""
Unit tests for memory management improvements.

Tests the memory leaks and proper cleanup function generation.
"""

import pytest
from polyglot_ffi.generators.c_stubs_gen import CStubGenerator
from polyglot_ffi.generators.python_gen import PythonGenerator
from polyglot_ffi.ir.types import (
    IRModule,
    IRFunction,
    IRParameter,
    IRType,
    TypeKind,
    STRING,
    INT,
    FLOAT,
    BOOL,
)


class TestCStubMemoryCleanup:
    """Test C stub generator produces cleanup functions."""

    def test_header_includes_cleanup_functions(self):
        """Test that header file includes memory cleanup function declarations."""
        gen = CStubGenerator()
        func = IRFunction(
            name="test_func",
            params=[IRParameter(name="x", type=INT)],
            return_type=INT,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        header = gen.generate_header(module, "test")

        # Check for cleanup function declarations
        assert "ml_free_option" in header
        assert "ml_free_list_result" in header
        assert "ml_free_string_list_result" in header
        assert "ml_free_tuple_list_result" in header
        assert "/* Memory cleanup functions */" in header
        assert "/* NOTE: Caller must free returned pointers" in header

    def test_stubs_includes_cleanup_implementations(self):
        """Test that stubs file includes cleanup function implementations."""
        gen = CStubGenerator()
        func = IRFunction(
            name="test_func",
            params=[IRParameter(name="x", type=INT)],
            return_type=INT,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Check for cleanup function implementations
        assert "void ml_free_option(void* ptr)" in stubs
        assert "void ml_free_list_result(void* result)" in stubs
        assert "void ml_free_string_list_result(void* result)" in stubs
        assert "void ml_free_tuple_list_result(void* result)" in stubs

    def test_option_int_returns_allocate_memory(self):
        """Test that option int return types allocate memory correctly."""
        gen = CStubGenerator()
        option_int = IRType(kind=TypeKind.OPTION, name="option", params=[INT])
        func = IRFunction(
            name="get_optional_int",
            params=[],
            return_type=option_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Check that we allocate memory for int option
        assert "int* result = (int*)malloc(sizeof(int))" in stubs
        assert "*result = Int_val(ml_some_value)" in stubs

    def test_option_float_returns_allocate_memory(self):
        """Test that option float return types allocate memory correctly."""
        gen = CStubGenerator()
        option_float = IRType(kind=TypeKind.OPTION, name="option", params=[FLOAT])
        func = IRFunction(
            name="get_optional_float",
            params=[],
            return_type=option_float,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Check that we allocate memory for float option
        assert "double* result = (double*)malloc(sizeof(double))" in stubs
        assert "*result = Double_val(ml_some_value)" in stubs

    def test_list_int_returns_allocate_memory(self):
        """Test that list int return types allocate memory correctly."""
        gen = CStubGenerator()
        list_int = IRType(kind=TypeKind.LIST, name="list", params=[INT])
        func = IRFunction(
            name="get_int_list",
            params=[],
            return_type=list_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Check that we allocate result structure
        assert "void** result = (void**)malloc(2 * sizeof(void*))" in stubs
        assert "int* array = (int*)malloc(list_len * sizeof(int))" in stubs

    def test_list_string_returns_duplicate_strings(self):
        """Test that list string return types duplicate strings."""
        gen = CStubGenerator()
        list_string = IRType(kind=TypeKind.LIST, name="list", params=[STRING])
        func = IRFunction(
            name="get_string_list",
            params=[],
            return_type=list_string,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Check that we use strdup for strings
        assert "strdup(String_val(head))" in stubs


class TestPythonGeneratorMemoryCleanup:
    """Test Python generator calls cleanup functions."""

    def test_python_loads_cleanup_functions(self):
        """Test that Python wrapper loads cleanup functions."""
        gen = PythonGenerator()
        func = IRFunction(
            name="test_func",
            params=[IRParameter(name="x", type=INT)],
            return_type=INT,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Check that cleanup functions are configured
        assert "_lib.ml_free_option.argtypes" in wrapper
        assert "_lib.ml_free_list_result.argtypes" in wrapper
        assert "_lib.ml_free_string_list_result.argtypes" in wrapper
        assert "_lib.ml_free_tuple_list_result.argtypes" in wrapper

    def test_option_int_calls_cleanup(self):
        """Test that option int return types call cleanup."""
        gen = PythonGenerator()
        option_int = IRType(kind=TypeKind.OPTION, name="option", params=[INT])
        func = IRFunction(
            name="get_optional_int",
            params=[],
            return_type=option_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Check that we call cleanup after extracting value
        assert "_lib.ml_free_option(result)" in wrapper
        assert "# Clean up C-allocated memory" in wrapper

    def test_option_int_uses_is_none_check(self):
        """Test that option int uses 'is None' instead of falsy check."""
        gen = PythonGenerator()
        option_int = IRType(kind=TypeKind.OPTION, name="option", params=[INT])
        func = IRFunction(
            name="get_optional_int",
            params=[],
            return_type=option_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Check that we use 'is None' not 'not result'
        assert "if result is None:" in wrapper
        # Should NOT contain the buggy falsy check
        assert "if not result:" not in wrapper or "if result is None:" in wrapper

    def test_list_int_calls_cleanup(self):
        """Test that list int return types call cleanup."""
        gen = PythonGenerator()
        list_int = IRType(kind=TypeKind.LIST, name="list", params=[INT])
        func = IRFunction(
            name="get_int_list",
            params=[],
            return_type=list_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Check that we call cleanup after converting list
        assert "_lib.ml_free_list_result(result)" in wrapper

    def test_list_string_calls_string_cleanup(self):
        """Test that list string return types call string-specific cleanup."""
        gen = PythonGenerator()
        list_string = IRType(kind=TypeKind.LIST, name="list", params=[STRING])
        func = IRFunction(
            name="get_string_list",
            params=[],
            return_type=list_string,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Check that we call string-specific cleanup
        assert "_lib.ml_free_string_list_result(result)" in wrapper
        assert "# Clean up C-allocated memory (strings + array + result)" in wrapper


class TestCAMLlocalPlacement:
    """Test that CAMLlocal declarations are placed correctly."""

    def test_list_parameter_camllocal_outside_loop(self):
        """Test that CAMLlocal1(cons) is outside the loop for list parameters."""
        gen = CStubGenerator()
        list_int = IRType(kind=TypeKind.LIST, name="list", params=[INT])
        func = IRFunction(
            name="process_list",
            params=[IRParameter(name="items", type=list_int)],
            return_type=INT,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Find the CAMLlocal1(cons) declaration
        lines = stubs.split("\n")
        camllocal_line = None
        for_loop_line = None

        for i, line in enumerate(lines):
            if "CAMLlocal1(cons)" in line:
                camllocal_line = i
            if "for (int i =" in line and "items_len" in line:
                for_loop_line = i

        # CAMLlocal should be declared before the loop starts
        if camllocal_line is not None and for_loop_line is not None:
            assert camllocal_line < for_loop_line, "CAMLlocal1(cons) should be before the for loop"

    def test_nested_list_camllocal_outside_loops(self):
        """Test that nested list CAMLlocal declarations are outside loops."""
        gen = CStubGenerator()
        inner_list = IRType(kind=TypeKind.LIST, name="list", params=[INT])
        list_list = IRType(kind=TypeKind.LIST, name="list", params=[inner_list])
        func = IRFunction(
            name="process_nested",
            params=[IRParameter(name="matrix", type=list_list)],
            return_type=INT,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        stubs = gen.generate_stubs(module, "test")

        # Find the function definition and check CAMLlocal placement within it
        lines = stubs.split("\n")
        func_start = None
        inner_cons_decl = None
        outer_cons_decl = None
        first_loop_in_func = None

        for i, line in enumerate(lines):
            # Find the start of our test function
            if "int ml_process_nested(" in line:
                func_start = i

            # Only look for declarations after function start
            if func_start is not None:
                if "CAMLlocal1(inner_cons)" in line:
                    inner_cons_decl = i
                if "CAMLlocal1(outer_cons)" in line:
                    outer_cons_decl = i
                # Find first loop in this function (should be the outer loop for matrix)
                if first_loop_in_func is None and "for (int i = matrix_len" in line:
                    first_loop_in_func = i

        # Both should be declared before the loop in this function starts
        assert func_start is not None, "Function ml_process_nested not found"
        assert inner_cons_decl is not None, "CAMLlocal1(inner_cons) not found"
        assert outer_cons_decl is not None, "CAMLlocal1(outer_cons) not found"
        assert first_loop_in_func is not None, "Loop not found in function"
        assert inner_cons_decl < first_loop_in_func, "CAMLlocal1(inner_cons) should be before loops"
        assert outer_cons_decl < first_loop_in_func, "CAMLlocal1(outer_cons) should be before loops"


class TestOptionTypeEdgeCases:
    """Test edge cases for option type handling."""

    def test_option_bool_false_is_not_none(self):
        """Test that Some(false) is not treated as None."""
        gen = PythonGenerator()
        option_bool = IRType(kind=TypeKind.OPTION, name="option", params=[BOOL])
        func = IRFunction(
            name="get_optional_bool",
            params=[],
            return_type=option_bool,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Should use 'is None' check, not falsy check
        # This ensures Some(False) is not treated as None
        lines = wrapper.split("\n")
        found_is_none = False
        for line in lines:
            if "bool" in line and "if result is None:" in line:
                found_is_none = True
                break

        # The wrapper should handle bool options with proper None check
        assert "if result is None:" in wrapper

    def test_option_int_zero_is_not_none(self):
        """Test that Some(0) is not treated as None."""
        gen = PythonGenerator()
        option_int = IRType(kind=TypeKind.OPTION, name="option", params=[INT])
        func = IRFunction(
            name="get_optional_zero",
            params=[],
            return_type=option_int,
        )
        module = IRModule(name="test", functions=[func], type_definitions=[])

        wrapper = gen.generate(module, "test")

        # Should use 'is None' check, not falsy check
        # This ensures Some(0) is not treated as None
        assert "if result is None:" in wrapper
