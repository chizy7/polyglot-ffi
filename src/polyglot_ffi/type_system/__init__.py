"""
Type system module for mapping types between languages.

This module provides a registry for type mappings and extensible
type conversion rules.
"""

from polyglot_ffi.type_system.registry import TypeRegistry, get_default_registry
from polyglot_ffi.type_system.builtin import register_builtin_types

__all__ = ["TypeRegistry", "get_default_registry", "register_builtin_types"]
