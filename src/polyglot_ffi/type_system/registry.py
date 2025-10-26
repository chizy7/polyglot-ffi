"""
Type Registry for managing type mappings between languages.

The registry allows defining how types in the IR map to types
in different target languages.
"""

from functools import lru_cache
from typing import Dict, Optional, Callable
from polyglot_ffi.ir.types import IRType, TypeKind


class TypeMappingError(Exception):
    """Raised when a type mapping cannot be found or is invalid."""

    pass


class TypeRegistry:
    """
    Registry for type mappings between IR types and target language types.

    Example usage:
        registry = TypeRegistry()
        registry.register_primitive("string", {
            "ocaml": "string",
            "python": "str",
            "c": "char*"
        })

        python_type = registry.get_mapping("string", "python")  # Returns "str"
    """

    def __init__(self):
        self._primitive_mappings: Dict[str, Dict[str, str]] = {}
        self._custom_converters: Dict[str, Dict[str, Callable]] = {}
        # Cache for type mappings (cleared when registry is modified)
        self._mapping_cache: Dict[tuple, str] = {}

    def register_primitive(self, ir_type_name: str, mappings: Dict[str, str]) -> None:
        """
        Register a primitive type mapping.

        Args:
            ir_type_name: Name of the IR type (e.g., "string", "int")
            mappings: Dictionary of language -> type_name mappings
        """
        self._primitive_mappings[ir_type_name] = mappings
        self._mapping_cache.clear()  # Clear cache when registry is modified

    def register_converter(
        self, ir_type_name: str, target_lang: str, converter: Callable[[IRType], str]
    ) -> None:
        """
        Register a custom type converter function.

        Args:
            ir_type_name: Name of the IR type
            target_lang: Target language
            converter: Function that takes IRType and returns type string
        """
        if ir_type_name not in self._custom_converters:
            self._custom_converters[ir_type_name] = {}
        self._custom_converters[ir_type_name][target_lang] = converter
        self._mapping_cache.clear()  # Clear cache when registry is modified

    def _type_to_cache_key(self, ir_type: IRType) -> tuple:
        """Convert IRType to a hashable cache key."""
        params_key = (
            tuple(self._type_to_cache_key(p) for p in ir_type.params) if ir_type.params else ()
        )
        return (ir_type.kind.value, ir_type.name, params_key)

    def get_mapping(self, ir_type: IRType, target_lang: str) -> str:
        """
        Get the type mapping for a target language.

        Args:
            ir_type: The IR type to map
            target_lang: Target language (e.g., "python", "c", "rust")

        Returns:
            Type string in the target language

        Raises:
            TypeMappingError: If no mapping exists
        """
        # Check cache first
        cache_key = (self._type_to_cache_key(ir_type), target_lang)
        if cache_key in self._mapping_cache:
            return self._mapping_cache[cache_key]

        # Compute the mapping
        result = self._compute_mapping(ir_type, target_lang)

        # Store in cache
        self._mapping_cache[cache_key] = result
        return result

    def _compute_mapping(self, ir_type: IRType, target_lang: str) -> str:
        """
        Compute the type mapping for a target language (internal, uncached).

        Args:
            ir_type: The IR type to map
            target_lang: Target language

        Returns:
            Type string in the target language

        Raises:
            TypeMappingError: If no mapping exists
        """
        # Handle primitive types
        if ir_type.kind == TypeKind.PRIMITIVE:
            if ir_type.name in self._primitive_mappings:
                mappings = self._primitive_mappings[ir_type.name]
                if target_lang in mappings:
                    return mappings[target_lang]
                raise TypeMappingError(
                    f"No {target_lang} mapping for primitive type '{ir_type.name}'"
                )
            raise TypeMappingError(f"Unknown primitive type '{ir_type.name}'")

        # Handle option types
        elif ir_type.kind == TypeKind.OPTION:
            if not ir_type.params:
                raise TypeMappingError("Option type must have a parameter")

            inner_type = self.get_mapping(ir_type.params[0], target_lang)

            if target_lang == "python":
                return f"Optional[{inner_type}]"
            elif target_lang == "c":
                # In C, we can use a struct with a flag
                return f"{inner_type}*"  # Nullable pointer
            elif target_lang == "ocaml":
                return f"{inner_type} option"
            elif target_lang == "rust":
                return f"Option<{inner_type}>"
            else:
                raise TypeMappingError(f"No option type support for {target_lang}")

        # Handle list types
        elif ir_type.kind == TypeKind.LIST:
            if not ir_type.params:
                raise TypeMappingError("List type must have a parameter")

            inner_type = self.get_mapping(ir_type.params[0], target_lang)

            if target_lang == "python":
                return f"List[{inner_type}]"
            elif target_lang == "c":
                # In C, lists need special handling with structs
                return f"{inner_type}*"  # Array pointer
            elif target_lang == "ocaml":
                return f"{inner_type} list"
            elif target_lang == "rust":
                return f"Vec<{inner_type}>"
            else:
                raise TypeMappingError(f"No list type support for {target_lang}")

        # Handle tuple types
        elif ir_type.kind == TypeKind.TUPLE:
            if not ir_type.params:
                raise TypeMappingError("Tuple type must have parameters")

            tuple_types = [self.get_mapping(p, target_lang) for p in ir_type.params]

            if target_lang == "python":
                types_str = ", ".join(tuple_types)
                return f"Tuple[{types_str}]"
            elif target_lang == "c":
                # In C, tuples need struct definitions
                return "tuple_t"  # Placeholder - needs actual struct
            elif target_lang == "ocaml":
                types_str = " * ".join(tuple_types)
                return f"({types_str})"
            elif target_lang == "rust":
                types_str = ", ".join(tuple_types)
                return f"({types_str})"
            else:
                raise TypeMappingError(f"No tuple type support for {target_lang}")

        # Handle custom types (records, variants)
        elif ir_type.kind in (TypeKind.CUSTOM, TypeKind.RECORD, TypeKind.VARIANT):
            # For custom types, check if there's a converter registered
            if ir_type.name in self._custom_converters:
                if target_lang in self._custom_converters[ir_type.name]:
                    converter = self._custom_converters[ir_type.name][target_lang]
                    return converter(ir_type)

            # Default: use the type name as-is (with some conventions)
            if target_lang == "python":
                # Python: CamelCase for classes
                return ir_type.name.title()
            elif target_lang == "c":
                # C: lowercase with _t suffix
                return f"{ir_type.name}_t"
            elif target_lang == "ocaml":
                # OCaml: lowercase
                return ir_type.name
            elif target_lang == "rust":
                # Rust: CamelCase
                return ir_type.name.title()
            else:
                return ir_type.name

        else:
            raise TypeMappingError(f"Unsupported type kind: {ir_type.kind}")

    def validate(self, ir_type: IRType, target_lang: str) -> bool:
        """
        Check if a type can be mapped to the target language.

        Args:
            ir_type: The IR type to validate
            target_lang: Target language

        Returns:
            True if mapping exists, False otherwise
        """
        try:
            self.get_mapping(ir_type, target_lang)
            return True
        except TypeMappingError:
            return False


# Global default registry instance
_default_registry: Optional[TypeRegistry] = None


def get_default_registry() -> TypeRegistry:
    """Get the default global type registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = TypeRegistry()
        # Register built-in types
        from polyglot_ffi.type_system.builtin import register_builtin_types

        register_builtin_types(_default_registry)
    return _default_registry
