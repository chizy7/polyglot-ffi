"""
Unit tests for code generators.
"""

import pytest
from polyglot_ffi.generators.ctypes_gen import CtypesGenerator
from polyglot_ffi.generators.c_stubs_gen import CStubGenerator
from polyglot_ffi.generators.python_gen import PythonGenerator
from polyglot_ffi.generators.dune_gen import DuneGenerator
from polyglot_ffi.ir.types import (
    IRModule,
    IRFunction,
    IRParameter,
    STRING,
    INT,
    FLOAT,
)


@pytest.fixture
def simple_module():
    """Create a simple IR module for testing."""
    func = IRFunction(
        name="greet",
        params=[IRParameter(name="name", type=STRING)],
        return_type=STRING,
        doc="Greet someone",
    )

    return IRModule(name="example", functions=[func], type_definitions=[])


@pytest.fixture
def multi_param_module():
    """Create an IR module with multi-parameter function."""
    func = IRFunction(
        name="add",
        params=[IRParameter(name="x", type=INT), IRParameter(name="y", type=INT)],
        return_type=INT,
    )

    return IRModule(name="math", functions=[func], type_definitions=[])


class TestCtypesGenerator:
    """Test OCaml ctypes generator."""

    def test_generate_type_description(self, simple_module):
        """Test generating type_description.ml."""
        gen = CtypesGenerator()
        result = gen.generate_type_description(simple_module)

        assert "open Ctypes" in result
        assert "module Types" in result

    def test_generate_function_description(self, simple_module):
        """Test generating function_description.ml."""
        gen = CtypesGenerator()
        result = gen.generate_function_description(simple_module)

        assert "open Ctypes" in result
        assert "module Functions" in result
        assert "let greet =" in result
        assert 'F.foreign "ml_greet"' in result
        assert "string @-> returning string" in result

    def test_multi_parameter_function(self, multi_param_module):
        """Test generating function with multiple parameters."""
        gen = CtypesGenerator()
        result = gen.generate_function_description(multi_param_module)

        assert "let add =" in result
        assert "int @-> int @-> returning int" in result


class TestCStubGenerator:
    """Test C stub generator."""

    def test_generate_stubs(self, simple_module):
        """Test generating C stubs."""
        gen = CStubGenerator()
        result = gen.generate_stubs(simple_module, "example")

        assert "#include <caml/mlvalues.h>" in result
        assert "#include <caml/callback.h>" in result
        assert "char* ml_greet(char* name)" in result
        assert "CAMLparam0()" in result
        assert "caml_copy_string" in result
        assert "caml_callback" in result
        assert "String_val" in result

    def test_generate_header(self, simple_module):
        """Test generating C header."""
        gen = CStubGenerator()
        result = gen.generate_header(simple_module, "example")

        assert "#ifndef EXAMPLE_STUBS_H" in result
        assert "#define EXAMPLE_STUBS_H" in result
        assert "char* ml_greet(char* name);" in result

    def test_multi_parameter_stubs(self, multi_param_module):
        """Test generating stubs for multi-parameter function."""
        gen = CStubGenerator()
        result = gen.generate_stubs(multi_param_module, "math")

        assert "int ml_add(int x, int y)" in result
        assert "Val_int(x)" in result
        assert "Val_int(y)" in result
        assert "caml_callback2" in result


class TestPythonGenerator:
    """Test Python wrapper generator."""

    def test_generate_wrapper(self, simple_module):
        """Test generating Python wrapper."""
        gen = PythonGenerator()
        result = gen.generate(simple_module, "example")

        assert "import ctypes" in result
        assert "class ExampleError(Exception):" in result
        assert "_lib.ml_greet.argtypes" in result
        assert "_lib.ml_greet.restype" in result
        assert "def greet(name: str) -> str:" in result
        assert "encode('utf-8')" in result
        assert "decode('utf-8')" in result

    def test_multi_parameter_wrapper(self, multi_param_module):
        """Test generating wrapper for multi-parameter function."""
        gen = PythonGenerator()
        result = gen.generate(multi_param_module, "math")

        assert "def add(x: int, y: int) -> int:" in result
        assert "ctypes.c_int" in result


class TestDuneGenerator:
    """Test Dune configuration generator."""

    def test_generate_dune(self):
        """Test generating dune file."""
        gen = DuneGenerator()
        result = gen.generate_dune("example")

        assert "(library" in result
        assert "(name example_bindings)" in result
        assert "(libraries ctypes ctypes.foreign)" in result
        assert "(ctypes" in result
        assert "example_stubs.c" in result
        assert "example_stubs.h" in result

    def test_generate_dune_project(self):
        """Test generating dune-project file."""
        gen = DuneGenerator()
        result = gen.generate_dune_project("example")

        assert "(lang dune 3.16)" in result
        assert "(using ctypes 0.3)" in result
        assert "(name example_bindings)" in result
        assert "(ocaml (>= 4.14))" in result
