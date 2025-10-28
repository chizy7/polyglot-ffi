"""
Polyglot FFI - Automatic FFI bindings generator for polyglot projects.
"""

__version__ = "0.4.1"
__author__ = "Chizaram Chibueze"
__license__ = "MIT"

from polyglot_ffi.parsers.ocaml import parse_mli_file, parse_mli_string
from polyglot_ffi.ir.types import IRModule, IRFunction, IRType

__all__ = [
    "__version__",
    "parse_mli_file",
    "parse_mli_string",
    "IRModule",
    "IRFunction",
    "IRType",
]
