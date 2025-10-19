"""
Integration tests for end-to-end generation.
"""

import tempfile
from pathlib import Path

import pytest
from polyglot_ffi.commands.generate import generate_bindings


class TestEndToEnd:
    """Test complete generation workflow."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def simple_mli_file(self, temp_dir):
        """Create a simple .mli file for testing."""
        mli_content = """
val encrypt : string -> string
(** Encrypt a string *)

val decrypt : string -> string
(** Decrypt a string *)

val hash : string -> int
(** Generate hash of a string *)
"""
        mli_path = temp_dir / "crypto.mli"
        mli_path.write_text(mli_content)
        return mli_path

    def test_generate_from_mli(self, simple_mli_file, temp_dir):
        """Test generating bindings from .mli file."""
        output_dir = temp_dir / "generated"

        result = generate_bindings(
            source_file=str(simple_mli_file),
            output_dir=str(output_dir),
            module_name="crypto",
            target_langs=["python"],
            dry_run=False,
            force=True,
            verbose=False,
        )

        assert result["success"]
        assert result["module_name"] == "crypto"
        assert len(result["functions"]) == 3
        assert "encrypt" in result["functions"]
        assert "decrypt" in result["functions"]
        assert "hash" in result["functions"]

        # Check that files were created
        assert (output_dir / "type_description.ml").exists()
        assert (output_dir / "function_description.ml").exists()
        assert (output_dir / "crypto_stubs.c").exists()
        assert (output_dir / "crypto_stubs.h").exists()
        assert (output_dir / "dune").exists()
        assert (output_dir / "dune-project").exists()
        assert (output_dir / "crypto_py.py").exists()

    def test_generated_ctypes_valid(self, simple_mli_file, temp_dir):
        """Test that generated ctypes code is valid OCaml."""
        output_dir = temp_dir / "generated"

        generate_bindings(
            source_file=str(simple_mli_file),
            output_dir=str(output_dir),
            module_name="crypto",
            target_langs=["python"],
            dry_run=False,
            force=True,
            verbose=False,
        )

        # Check function_description.ml content
        func_desc = (output_dir / "function_description.ml").read_text()

        assert "open Ctypes" in func_desc
        assert "module Functions" in func_desc
        assert "let encrypt" in func_desc
        assert "let decrypt" in func_desc
        assert "let hash" in func_desc
        assert 'F.foreign "ml_encrypt"' in func_desc

    def test_generated_c_stubs_valid(self, simple_mli_file, temp_dir):
        """Test that generated C stubs are valid."""
        output_dir = temp_dir / "generated"

        generate_bindings(
            source_file=str(simple_mli_file),
            output_dir=str(output_dir),
            module_name="crypto",
            target_langs=["python"],
            dry_run=False,
            force=True,
            verbose=False,
        )

        # Check C stubs content
        c_stubs = (output_dir / "crypto_stubs.c").read_text()

        assert "#include <caml/mlvalues.h>" in c_stubs
        assert "char* ml_encrypt(char* input)" in c_stubs
        assert "char* ml_decrypt(char* input)" in c_stubs
        assert "int ml_hash(char* input)" in c_stubs
        assert "CAMLparam0()" in c_stubs
        assert "caml_callback" in c_stubs

    def test_generated_python_valid(self, simple_mli_file, temp_dir):
        """Test that generated Python wrapper is valid."""
        output_dir = temp_dir / "generated"

        generate_bindings(
            source_file=str(simple_mli_file),
            output_dir=str(output_dir),
            module_name="crypto",
            target_langs=["python"],
            dry_run=False,
            force=True,
            verbose=False,
        )

        # Check Python wrapper content
        py_wrapper = (output_dir / "crypto_py.py").read_text()

        assert "import ctypes" in py_wrapper
        assert "class CryptoError(Exception):" in py_wrapper
        assert "def encrypt(input: str) -> str:" in py_wrapper
        assert "def decrypt(input: str) -> str:" in py_wrapper
        assert "def hash(input: str) -> int:" in py_wrapper

        # Try to compile the Python code
        compile(py_wrapper, "crypto_py.py", "exec")

    def test_dry_run_mode(self, simple_mli_file, temp_dir):
        """Test that dry run doesn't create files."""
        output_dir = temp_dir / "generated"

        result = generate_bindings(
            source_file=str(simple_mli_file),
            output_dir=str(output_dir),
            module_name="crypto",
            target_langs=["python"],
            dry_run=True,
            force=True,
            verbose=False,
        )

        assert result["success"]
        assert len(result["files"]) > 0

        # Files should not exist in dry run
        assert not (output_dir / "type_description.ml").exists()
        assert not (output_dir / "crypto_py.py").exists()
