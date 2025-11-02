"""
Naming utilities for sanitizing identifiers across different systems.
"""


def sanitize_for_dune(name: str) -> str:
    """
    Sanitize a name to be valid for Dune build system.

    Dune library names must only contain: A-Z, a-z, 0-9, _

    Args:
        name: Original name (may contain hyphens, etc.)

    Returns:
        Sanitized name with hyphens replaced by underscores

    Example:
        >>> sanitize_for_dune("my-crypto-lib")
        'my_crypto_lib'
    """
    return name.replace("-", "_")


def sanitize_for_python(name: str) -> str:
    """
    Sanitize a name to be valid for Python identifiers.

    Python identifiers must start with letter or underscore,
    and contain only letters, digits, and underscores.

    Args:
        name: Original name (may contain hyphens, etc.)

    Returns:
        Sanitized name valid for Python

    Example:
        >>> sanitize_for_python("my-crypto-lib")
        'my_crypto_lib'
    """
    return name.replace("-", "_")


def sanitize_for_c(name: str) -> str:
    """
    Sanitize a name to be valid for C identifiers.

    C identifiers must start with letter or underscore,
    and contain only letters, digits, and underscores.

    Args:
        name: Original name (may contain hyphens, etc.)

    Returns:
        Sanitized name valid for C

    Example:
        >>> sanitize_for_c("my-crypto-lib")
        'my_crypto_lib'
    """
    return name.replace("-", "_")


def sanitize_module_name(name: str) -> str:
    """
    Sanitize a module name for use across all systems.

    This is the main function to use for module names that need to work
    in Dune, Python, C, and OCaml.

    OCaml module names must:
    - Start with a letter (not a digit or underscore)
    - Contain only letters, digits, and underscores

    Args:
        name: Original module name

    Returns:
        Sanitized module name safe for all systems

    Raises:
        ValueError: If the name cannot be sanitized to a valid module name

    Example:
        >>> sanitize_module_name("my-crypto-lib")
        'my_crypto_lib'
        >>> sanitize_module_name("123invalid")
        ValueError: Module name '123invalid' is invalid...
    """
    # Replace hyphens with underscores
    sanitized = name.replace("-", "_")

    # Check if it starts with a digit
    if sanitized and sanitized[0].isdigit():
        raise ValueError(
            f"Module name '{name}' is invalid: OCaml module names cannot start with a digit.\n"
            f"  Suggestions:\n"
            f"  • Rename the file to start with a letter (e.g., 'module_{name}')\n"
            f"  • Use a descriptive prefix (e.g., 'lib_{name}' or 'test_{name}')"
        )

    # Check if it starts with an underscore (also invalid in OCaml modules)
    if sanitized and sanitized[0] == "_":
        raise ValueError(
            f"Module name '{name}' is invalid: OCaml module names cannot start with an underscore.\n"
            f"  Suggestions:\n"
            f"  • Rename the file to start with a letter (e.g., 'module{name}')\n"
            f"  • Remove leading underscores"
        )

    # Check if it's empty or contains only invalid characters
    if not sanitized or not sanitized.replace("_", "").isalnum():
        raise ValueError(
            f"Module name '{name}' is invalid: must contain at least one letter or digit.\n"
            f"  Suggestions:\n"
            f"  • Use a descriptive name with letters (e.g., 'mymodule')"
        )

    return sanitized
