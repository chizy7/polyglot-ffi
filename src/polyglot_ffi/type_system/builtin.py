"""
Built-in type mappings for common programming languages.

This module registers standard type mappings for primitives
across multiple target languages.
"""

from polyglot_ffi.type_system.registry import TypeRegistry


def register_builtin_types(registry: TypeRegistry) -> None:
    """
    Register built-in type mappings in the registry.

    Registers mappings for: string, int, float, bool, unit/void
    Target languages: OCaml, Python, C, Rust
    """

    # String type
    registry.register_primitive(
        "string",
        {
            "ocaml": "string",
            "python": "str",
            "c": "char*",
            "rust": "String",
        },
    )

    # Integer type
    registry.register_primitive(
        "int",
        {
            "ocaml": "int",
            "python": "int",
            "c": "int",
            "rust": "i64",
        },
    )

    # Float type
    registry.register_primitive(
        "float",
        {
            "ocaml": "float",
            "python": "float",
            "c": "double",
            "rust": "f64",
        },
    )

    # Boolean type
    registry.register_primitive(
        "bool",
        {
            "ocaml": "bool",
            "python": "bool",
            "c": "int",  # C uses int for booleans (0/1)
            "rust": "bool",
        },
    )

    # Unit/void type
    registry.register_primitive(
        "unit",
        {
            "ocaml": "unit",
            "python": "None",
            "c": "void",
            "rust": "()",
        },
    )

    # Type variables (for polymorphic/generic types)
    # These are typically preserved as-is or mapped to generic syntax
    for var in ["'a", "'b", "'c", "'d"]:
        registry.register_primitive(
            var,
            {
                "ocaml": var,
                "python": "Any",  # Python doesn't have direct type variables in this context
                "c": "void*",  # C uses void* for generic pointers
                "rust": "T",  # Rust uses generic type parameters
            },
        )
