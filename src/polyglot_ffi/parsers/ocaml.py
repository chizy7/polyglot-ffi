"""
OCaml .mli parser for extracting function signatures and types.

This parser handles OCaml interface files and converts them to IR.
Phase 1 focuses on primitive types only.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from polyglot_ffi.ir.types import (
    BOOL,
    FLOAT,
    INT,
    STRING,
    UNIT,
    IRFunction,
    IRModule,
    IRParameter,
    IRType,
    TypeKind,
    ir_list,
    ir_option,
    ir_primitive,
)


class ParseError(Exception):
    """Raised when parsing fails."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.line = line
        self.column = column
        if line is not None:
            message = f"Line {line}: {message}"
        super().__init__(message)


class OCamlParser:
    """
    Parse OCaml .mli interface files into IR.

    Phase 1: Supports primitive types (string, int, float, bool, unit)
    Future: Will support options, lists, records, variants
    """

    # Primitive type mappings
    PRIMITIVE_TYPES = {
        "string": STRING,
        "int": INT,
        "float": FLOAT,
        "bool": BOOL,
        "unit": UNIT,
    }

    def __init__(self, content: str, filename: str = "<unknown>"):
        self.content = content
        self.filename = filename
        self.lines = content.split("\n")

    def parse(self) -> IRModule:
        """Parse the content and return an IR module."""
        module_name = Path(self.filename).stem
        functions = self._extract_functions()

        return IRModule(
            name=module_name,
            functions=functions,
            type_definitions=[],  # Phase 1: No custom types
            doc="",
        )

    def _extract_functions(self) -> List[IRFunction]:
        """Extract all function signatures from the file."""
        functions = []
        i = 0

        while i < len(self.lines):
            line = self.lines[i].strip()

            # Look for function declarations starting with 'val'
            if line.startswith("val "):
                func, doc, lines_consumed = self._parse_function(self.lines[i:], i + 1)
                if func:
                    functions.append(func)
                i += lines_consumed
            else:
                i += 1

        return functions

    def _parse_function(
        self, lines: List[str], start_line: int
    ) -> Tuple[Optional[IRFunction], str, int]:
        """
        Parse a single function signature.

        Returns:
            (IRFunction, documentation, lines_consumed)
        """
        # Combine lines until we have the complete signature
        full_sig = ""
        doc = ""
        lines_consumed = 0

        for j, line in enumerate(lines):
            stripped = line.strip()
            full_sig += " " + stripped
            lines_consumed += 1

            # Extract documentation
            doc_match = re.search(r"\(\*\*\s*(.*?)\s*\*\)", stripped)
            if doc_match:
                doc = doc_match.group(1)
                # Remove doc from signature
                full_sig = re.sub(r"\(\*\*.*?\*\)", "", full_sig)

            # Check if signature is complete
            # A signature is complete when it doesn't end with '->' and has no unclosed parens
            if not stripped.endswith("->"):
                # Check for balanced parentheses
                open_count = full_sig.count("(") - full_sig.count(")")
                if open_count == 0:
                    break

        # Parse the complete signature
        try:
            func = self._parse_signature(full_sig.strip(), start_line)
            return func, doc, lines_consumed
        except ParseError as e:
            # Re-raise with line info
            raise ParseError(str(e), start_line)

    def _parse_signature(self, sig: str, line_num: int) -> IRFunction:
        """
        Parse a complete function signature.

        Format: val name : type1 -> type2 -> ... -> return_type
        """
        # Match: val function_name : type_signature
        match = re.match(r"val\s+(\w+)\s*:\s*(.+)", sig)
        if not match:
            raise ParseError(f"Invalid function signature: {sig}", line_num)

        name = match.group(1)
        type_sig = match.group(2).strip()

        # Split by '->' to get parameter types and return type
        parts = [p.strip() for p in type_sig.split("->")]

        if len(parts) < 2:
            raise ParseError(
                f"Function '{name}' must have at least one parameter and return type", line_num
            )

        # All parts except the last are parameters
        param_types = parts[:-1]
        return_type_str = parts[-1]

        # Parse parameter types
        params = []
        for i, param_type_str in enumerate(param_types):
            try:
                param_type = self._parse_type(param_type_str, line_num)
                # Generate parameter name
                param_name = f"arg{i}" if len(params) > 0 else "input"
                params.append(IRParameter(name=param_name, type=param_type))
            except ParseError as e:
                raise ParseError(
                    f"Error parsing parameter {i+1} of function '{name}': {e}", line_num
                )

        # Parse return type
        try:
            return_type = self._parse_type(return_type_str, line_num)
        except ParseError as e:
            raise ParseError(f"Error parsing return type of function '{name}': {e}", line_num)

        return IRFunction(name=name, params=params, return_type=return_type, doc="")

    def _parse_type(self, type_str: str, line_num: int) -> IRType:
        """
        Parse a type string into an IRType.

        Phase 1: Only primitives
        Future phases: options, lists, records, variants
        """
        type_str = type_str.strip()

        # Check for primitive types
        if type_str in self.PRIMITIVE_TYPES:
            return self.PRIMITIVE_TYPES[type_str]

        # Phase 1: Only primitives supported
        raise ParseError(
            f"Unsupported type: '{type_str}'. "
            f"Phase 1 only supports: {', '.join(self.PRIMITIVE_TYPES.keys())}",
            line_num,
        )

    @classmethod
    def parse_file(cls, path: Path) -> IRModule:
        """Parse a .mli file."""
        content = path.read_text()
        parser = cls(content, str(path))
        return parser.parse()

    @classmethod
    def parse_string(cls, content: str, filename: str = "<string>") -> IRModule:
        """Parse a string containing OCaml interface code."""
        parser = cls(content, filename)
        return parser.parse()


def parse_mli_file(path: Path) -> IRModule:
    """Convenience function to parse a .mli file."""
    return OCamlParser.parse_file(path)


def parse_mli_string(content: str) -> IRModule:
    """Convenience function to parse OCaml interface code from a string."""
    return OCamlParser.parse_string(content)
