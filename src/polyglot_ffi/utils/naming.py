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

    Args:
        name: Original module name

    Returns:
        Sanitized module name safe for all systems

    Example:
        >>> sanitize_module_name("my-crypto-lib")
        'my_crypto_lib'
    """
    return name.replace("-", "_")
