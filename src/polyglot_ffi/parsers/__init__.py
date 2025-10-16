"""Parsers package."""

from polyglot_ffi.parsers.ocaml import OCamlParser, parse_mli_file, parse_mli_string

__all__ = ["OCamlParser", "parse_mli_file", "parse_mli_string"]
