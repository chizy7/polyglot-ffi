"""
Intermediate Representation (IR) type definitions.

This module defines language-agnostic types that serve as a bridge
between source language parsers and target language generators.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class TypeKind(Enum):
    """Categories of types in the IR."""

    PRIMITIVE = "primitive"
    OPTION = "option"
    LIST = "list"
    TUPLE = "tuple"
    RECORD = "record"
    VARIANT = "variant"
    FUNCTION = "function"
    CUSTOM = "custom"


@dataclass
class IRType:
    """
    Language-agnostic type representation.

    Examples:
        - Primitive: IRType(kind=PRIMITIVE, name="string")
        - Option: IRType(kind=OPTION, name="option", params=[IRType(...)])
        - List: IRType(kind=LIST, name="list", params=[IRType(...)])
        - Record: IRType(kind=RECORD, name="user", fields={"name": IRType(...), ...})
    """

    kind: TypeKind
    name: str
    params: List["IRType"] = field(default_factory=list)
    fields: Dict[str, "IRType"] = field(default_factory=dict)
    variants: Dict[str, Optional["IRType"]] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation for debugging."""
        if self.kind == TypeKind.PRIMITIVE:
            return self.name
        elif self.kind == TypeKind.OPTION:
            return f"{self.params[0]} option"
        elif self.kind == TypeKind.LIST:
            return f"{self.params[0]} list"
        elif self.kind == TypeKind.TUPLE:
            types = " * ".join(str(p) for p in self.params)
            return f"({types})"
        elif self.kind == TypeKind.RECORD:
            return f"record {self.name}"
        elif self.kind == TypeKind.VARIANT:
            return f"variant {self.name}"
        return self.name

    def is_primitive(self) -> bool:
        """Check if this is a primitive type."""
        return self.kind == TypeKind.PRIMITIVE

    def is_container(self) -> bool:
        """Check if this is a container type (option, list, etc.)."""
        return self.kind in (TypeKind.OPTION, TypeKind.LIST, TypeKind.TUPLE)

    def is_composite(self) -> bool:
        """Check if this is a composite type (record, variant)."""
        return self.kind in (TypeKind.RECORD, TypeKind.VARIANT)


@dataclass
class IRParameter:
    """Function parameter representation."""

    name: str
    type: IRType

    def __str__(self) -> str:
        return f"{self.name}: {self.type}"


@dataclass
class IRFunction:
    """
    Language-agnostic function representation.

    Attributes:
        name: Function name
        params: List of parameters
        return_type: Return type
        doc: Documentation string
        is_async: Whether function is async/concurrent
    """

    name: str
    params: List[IRParameter]
    return_type: IRType
    doc: str = ""
    is_async: bool = False

    def __str__(self) -> str:
        params_str = ", ".join(str(p) for p in self.params)
        return f"{self.name}({params_str}) -> {self.return_type}"

    @property
    def arity(self) -> int:
        """Number of parameters."""
        return len(self.params)


@dataclass
class IRTypeDefinition:
    """
    Custom type definition (record or variant).

    Examples:
        Record:
            IRTypeDefinition(
                name="user",
                kind=RECORD,
                fields={"name": IRType(...), "age": IRType(...)}
            )

        Variant:
            IRTypeDefinition(
                name="result",
                kind=VARIANT,
                variants={"Ok": IRType(...), "Error": IRType(...)}
            )
    """

    name: str
    kind: TypeKind
    fields: Dict[str, IRType] = field(default_factory=dict)
    variants: Dict[str, Optional[IRType]] = field(default_factory=dict)
    doc: str = ""

    def __str__(self) -> str:
        if self.kind == TypeKind.RECORD:
            fields_str = ", ".join(f"{k}: {v}" for k, v in self.fields.items())
            return f"type {self.name} = {{ {fields_str} }}"
        elif self.kind == TypeKind.VARIANT:
            variants_str = " | ".join(
                f"{k}" + (f" of {v}" if v else "") for k, v in self.variants.items()
            )
            return f"type {self.name} = {variants_str}"
        return f"type {self.name}"


@dataclass
class IRModule:
    """
    Top-level module representation.

    Contains all functions and type definitions from a source file.
    """

    name: str
    functions: List[IRFunction] = field(default_factory=list)
    type_definitions: List[IRTypeDefinition] = field(default_factory=list)
    doc: str = ""

    def __str__(self) -> str:
        return f"Module {self.name} ({len(self.functions)} functions, {len(self.type_definitions)} types)"

    def get_function(self, name: str) -> Optional[IRFunction]:
        """Get function by name."""
        for func in self.functions:
            if func.name == name:
                return func
        return None

    def get_type(self, name: str) -> Optional[IRTypeDefinition]:
        """Get type definition by name."""
        for typedef in self.type_definitions:
            if typedef.name == name:
                return typedef
        return None


# Helper functions for creating common IR types


def ir_primitive(name: str) -> IRType:
    """Create a primitive type."""
    return IRType(kind=TypeKind.PRIMITIVE, name=name)


def ir_option(inner: IRType) -> IRType:
    """Create an option type."""
    return IRType(kind=TypeKind.OPTION, name="option", params=[inner])


def ir_list(inner: IRType) -> IRType:
    """Create a list type."""
    return IRType(kind=TypeKind.LIST, name="list", params=[inner])


def ir_tuple(*types: IRType) -> IRType:
    """Create a tuple type."""
    return IRType(kind=TypeKind.TUPLE, name="tuple", params=list(types))


# Common primitive types
STRING = ir_primitive("string")
INT = ir_primitive("int")
FLOAT = ir_primitive("float")
BOOL = ir_primitive("bool")
UNIT = ir_primitive("unit")
