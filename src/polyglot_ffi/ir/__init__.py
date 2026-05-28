"""Intermediate representation package."""

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
)

__all__ = [
    "IRModule",
    "IRFunction",
    "IRType",
    "IRParameter",
    "IRTypeDefinition",
    "TypeKind",
    "STRING",
    "INT",
    "FLOAT",
    "BOOL",
    "UNIT",
]
