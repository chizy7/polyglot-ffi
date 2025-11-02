"""
OCaml .mli parser for extracting function signatures and types.

This parser handles OCaml interface files and converts them to IR.
Primitive types,
Complex types (options, lists, tuples, records, variants),
Enhanced error messages with suggestions
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
    IRTypeDefinition,
    TypeKind,
    ir_list,
    ir_option,
    ir_primitive,
)
from polyglot_ffi.utils.errors import (
    ParseError,
    suggest_type_fix,
    suggest_syntax_fix,
)


class OCamlParser:
    """
    Parse OCaml .mli interface files into IR.

    Supports:
    - Primitive types (string, int, float, bool, unit)
    - Complex types (option, list, tuple, record, variant)
    - Type variables ('a, 'b, etc.)
    """

    # Primitive type mappings
    PRIMITIVE_TYPES = {
        "string": STRING,
        "int": INT,
        "float": FLOAT,
        "bool": BOOL,
        "unit": UNIT,
    }

    # Pre-compiled regex patterns for performance
    OPTION_PATTERN = re.compile(r"(.+?)\s+option$")
    LIST_PATTERN = re.compile(r"(.+?)\s+list$")
    TYPE_VAR_PATTERN = re.compile(r"^'[a-z]$")
    CUSTOM_TYPE_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")

    def __init__(self, content: str, filename: str = "<unknown>"):
        self.content = content
        self.filename = filename
        self.lines = content.split("\n")

    def parse(self) -> IRModule:
        """Parse the content and return an IR module."""
        module_name = Path(self.filename).stem
        functions = self._extract_functions()
        type_definitions = self._extract_type_definitions()

        return IRModule(
            name=module_name,
            functions=functions,
            type_definitions=type_definitions,
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

    def _extract_type_definitions(self) -> List[IRTypeDefinition]:
        """Extract all type definitions (records and variants) from the file."""
        type_defs = []
        i = 0

        while i < len(self.lines):
            line = self.lines[i].strip()

            # Look for type definitions starting with 'type'
            if line.startswith("type ") and "=" in line:
                typedef, lines_consumed = self._parse_type_definition(self.lines[i:], i + 1)
                if typedef:
                    type_defs.append(typedef)
                i += lines_consumed
            else:
                i += 1

        return type_defs

    def _parse_type_definition(
        self, lines: List[str], start_line: int
    ) -> Tuple[Optional[IRTypeDefinition], int]:
        """
        Parse a type definition (record or variant).

        Examples:
            type user = { name: string; age: int }
            type result = Ok of string | Error of string
            type status = Success | Failure | Pending
        """
        # Combine lines until we have the complete definition
        full_def = ""
        lines_consumed = 0

        for j, line in enumerate(lines):
            stripped = line.strip()
            full_def += " " + stripped
            lines_consumed += 1

            # Check if definition is complete
            # A simple heuristic: ends with a closing brace or doesn't have '|' at end
            if stripped.endswith("}") or ("|" not in stripped and j > 0):
                break
            # Also stop if next line doesn't continue the definition
            if j + 1 < len(lines):
                next_line = lines[j + 1].strip()
                if next_line and not next_line.startswith("|") and "{" not in full_def:
                    break

        full_def = full_def.strip()

        try:
            # Match: type name = definition
            match = re.match(r"type\s+(\w+)\s*=\s*(.+)", full_def)
            if not match:
                raise ParseError(f"Invalid type definition: {full_def}", start_line)

            type_name = match.group(1)
            type_body = match.group(2).strip()

            # Determine if it's a record or variant
            if type_body.startswith("{") and type_body.endswith("}"):
                # Record type
                return self._parse_record_type(type_name, type_body, start_line), lines_consumed
            elif "|" in type_body or (type_body[0].isupper() and " of " in type_body):
                # Variant type
                return self._parse_variant_type(type_name, type_body, start_line), lines_consumed
            else:
                # Type alias - treat as custom named type
                aliased_type = self._parse_type(type_body, start_line)
                # For now, we'll skip pure type aliases as they don't need special handling
                return None, lines_consumed

        except ParseError as e:
            raise ParseError(f"Error parsing type definition: {e}", start_line)

    def _parse_record_type(self, type_name: str, type_body: str, line_num: int) -> IRTypeDefinition:
        """
        Parse a record type definition.

        Example: { name: string; age: int; email: string }
        """
        # Remove braces
        inner = type_body[1:-1].strip()

        # Split by semicolon
        field_strs = [f.strip() for f in inner.split(";") if f.strip()]

        fields = {}
        for field_str in field_strs:
            # Match: field_name : type
            match = re.match(r"(\w+)\s*:\s*(.+)", field_str)
            if not match:
                raise ParseError(
                    f"Invalid record field: '{field_str}' in type '{type_name}'", line_num
                )

            field_name = match.group(1)
            field_type_str = match.group(2).strip()
            field_type = self._parse_type(field_type_str, line_num)
            fields[field_name] = field_type

        return IRTypeDefinition(name=type_name, kind=TypeKind.RECORD, fields=fields, doc="")

    def _parse_variant_type(
        self, type_name: str, type_body: str, line_num: int
    ) -> IRTypeDefinition:
        """
        Parse a variant (sum) type definition.

        Examples:
            Ok of string | Error of string
            Success | Failure | Pending
        """
        # Split by pipe
        variant_strs = [v.strip() for v in type_body.split("|")]

        variants = {}
        for variant_str in variant_strs:
            # Match: Constructor or Constructor of type
            match = re.match(r"(\w+)(?:\s+of\s+(.+))?", variant_str)
            if not match:
                raise ParseError(
                    f"Invalid variant: '{variant_str}' in type '{type_name}'", line_num
                )

            constructor = match.group(1)
            type_str = match.group(2)

            if type_str:
                variant_type = self._parse_type(type_str.strip(), line_num)
                variants[constructor] = variant_type
            else:
                # Constructor without payload
                variants[constructor] = None

        return IRTypeDefinition(name=type_name, kind=TypeKind.VARIANT, variants=variants, doc="")

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
            # Re-raise with line info (avoid duplicating if already has line info)
            if e.context.line:
                raise  # Already has line info, just re-raise
            raise ParseError(e.message, line=start_line)

    def _parse_signature(self, sig: str, line_num: int) -> IRFunction:
        """
        Parse a complete function signature.

        Format: val name : type1 -> type2 -> ... -> return_type
        """
        # Match: val function_name : type_signature
        match = re.match(r"val\s+(\w+)\s*:\s*(.+)", sig)
        if not match:
            raise ParseError(
                f"Invalid function signature: {sig}",
                line=line_num,
                suggestions=[
                    "Function signatures must be in format: val name : type -> type -> ...",
                    "Check for missing '->' between parameter types",
                ],
            )

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

        Supports:
        - Primitives: string, int, float, bool, unit
        - Options: 'a option, int option, string option, etc.
        - Lists: 'a list, int list, string list, etc.
        - Tuples: 'a * 'b, int * string, etc.
        - Records and Variants: (complex type definitions)
        """
        type_str = type_str.strip()

        # Check for primitive types
        if type_str in self.PRIMITIVE_TYPES:
            return self.PRIMITIVE_TYPES[type_str]

        # Check for option types: "X option"
        option_match = self.OPTION_PATTERN.match(type_str)
        if option_match:
            inner_type_str = option_match.group(1).strip()
            inner_type = self._parse_type(inner_type_str, line_num)
            return ir_option(inner_type)

        # Check for list types: "X list"
        list_match = self.LIST_PATTERN.match(type_str)
        if list_match:
            inner_type_str = list_match.group(1).strip()
            inner_type = self._parse_type(inner_type_str, line_num)
            return ir_list(inner_type)

        # Check for tuple types: "X * Y" or "X * Y * Z"
        if " * " in type_str:
            # Handle parentheses around tuples
            if type_str.startswith("(") and type_str.endswith(")"):
                type_str = type_str[1:-1].strip()

            # Split by * and parse each component
            parts = [p.strip() for p in type_str.split("*")]
            tuple_types = [self._parse_type(part, line_num) for part in parts]

            from polyglot_ffi.ir.types import ir_tuple

            return ir_tuple(*tuple_types)

        # Check for type variables: 'a, 'b, etc.
        if self.TYPE_VAR_PATTERN.match(type_str):
            # Type variables represent generic/polymorphic types
            # For now, treat them as a special primitive
            return ir_primitive(type_str)

        # Check for custom named types (records, variants, or type aliases)
        # These are identifiers that don't match primitives
        if self.CUSTOM_TYPE_PATTERN.match(type_str):
            # This is a custom type reference
            # We'll create it as a CUSTOM type kind
            return IRType(kind=TypeKind.CUSTOM, name=type_str)

        # If we reach here, it's an unsupported type
        suggestions = suggest_type_fix(type_str)
        raise ParseError(
            message=f"Unsupported type: '{type_str}'",
            file_path=Path(self.filename) if self.filename != "<unknown>" else None,
            line=line_num,
            suggestions=suggestions,
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
