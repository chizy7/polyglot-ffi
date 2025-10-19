"""
Enhanced error types with rich context and suggestions.

Developer Experience - Better error messages.
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """Context information for an error."""

    file_path: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None


class PolyglotFFIError(Exception):
    """Base exception for all polyglot-ffi errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.message = message
        self.context = context or ErrorContext()
        self.suggestions = suggestions or []
        super().__init__(message)

    def format_rich(self) -> str:
        """Format error message with rich markup for console display."""
        lines = []

        # Error title
        lines.append(f"[bold red]Error:[/bold red] {self.message}")

        # Location information
        if self.context.file_path:
            location = f"  [dim]in[/dim] {self.context.file_path}"
            if self.context.line:
                location += f"[dim]:[/dim]{self.context.line}"
                if self.context.column:
                    location += f"[dim]:[/dim]{self.context.column}"
            lines.append(location)

        # Code snippet
        if self.context.code_snippet:
            lines.append("")
            lines.append("[dim]Code:[/dim]")
            # Highlight the problematic line
            snippet_lines = self.context.code_snippet.split("\n")
            for i, line in enumerate(snippet_lines, 1):
                if self.context.line and i == self.context.line:
                    lines.append(f"  [yellow]→[/yellow] {line}")
                    if self.context.column:
                        # Add a caret pointer
                        pointer = " " * (self.context.column + 3) + "[red]^[/red]"
                        lines.append(pointer)
                else:
                    lines.append(f"    {line}")

        # Suggestions
        if self.suggestions:
            lines.append("")
            lines.append("[bold cyan]Suggestions:[/bold cyan]")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        return "\n".join(lines)

    def __str__(self) -> str:
        """Plain text representation."""
        parts = [self.message]
        if self.context.file_path:
            location = str(self.context.file_path)
            if self.context.line:
                location += f":{self.context.line}"
                if self.context.column:
                    location += f":{self.context.column}"
            parts.append(f"  in {location}")
        if self.suggestions:
            parts.append("Suggestions:")
            for suggestion in self.suggestions:
                parts.append(f"  • {suggestion}")
        return "\n".join(parts)


class ParseError(PolyglotFFIError):
    """Error during parsing of source files."""

    def __init__(
        self,
        message: str,
        file_path: Optional[Path] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        code_snippet: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        context = ErrorContext(
            file_path=file_path,
            line=line,
            column=column,
            code_snippet=code_snippet,
        )
        super().__init__(message, context, suggestions)


class TypeError_(PolyglotFFIError):
    """Error related to type handling."""

    pass


class GenerationError(PolyglotFFIError):
    """Error during code generation."""

    pass


class ConfigurationError(PolyglotFFIError):
    """Error in configuration file."""

    def __init__(
        self,
        message: str,
        config_path: Optional[Path] = None,
        suggestions: Optional[List[str]] = None,
    ):
        context = ErrorContext(file_path=config_path)
        super().__init__(message, context, suggestions)


class ValidationError(PolyglotFFIError):
    """Error during validation."""

    pass


# Error suggestion helpers

def suggest_type_fix(invalid_type: str) -> List[str]:
    """Suggest fixes for invalid type names."""
    suggestions = []

    # Common misspellings
    type_corrections = {
        "str": "string",
        "String": "string",
        "integer": "int",
        "Integer": "int",
        "Int": "int",
        "boolean": "bool",
        "Boolean": "bool",
        "Bool": "bool",
        "double": "float",
        "Float": "float",
        "void": "unit",
        "None": "unit",
        "null": "unit",
    }

    if invalid_type in type_corrections:
        correct = type_corrections[invalid_type]
        suggestions.append(f"Did you mean '[cyan]{correct}[/cyan]'?")

    # Check for option vs optional
    if "optional" in invalid_type.lower():
        suggestions.append("Use '[cyan]option[/cyan]' instead of 'optional' (e.g., 'string option')")

    # Check for array/list confusion
    if "array" in invalid_type.lower():
        suggestions.append("OCaml uses '[cyan]list[/cyan]' instead of 'array' (e.g., 'int list')")

    if not suggestions:
        suggestions.append("Supported types: string, int, float, bool, unit")
        suggestions.append("Complex types: 'a option, 'a list, tuples (int * string)")
        suggestions.append("Custom types: define with 'type name = ...'")

    return suggestions


def suggest_syntax_fix(syntax_error: str) -> List[str]:
    """Suggest fixes for syntax errors."""
    suggestions = []

    if "signature" in syntax_error.lower():
        suggestions.append("Function signature format: [cyan]val name : type1 -> type2 -> return_type[/cyan]")
        suggestions.append("Example: [dim]val encrypt : string -> string[/dim]")

    if "record" in syntax_error.lower():
        suggestions.append("Record format: [cyan]type name = { field1: type1; field2: type2 }[/cyan]")
        suggestions.append("Don't forget semicolons between fields!")

    if "variant" in syntax_error.lower():
        suggestions.append("Variant format: [cyan]type name = Constructor1 | Constructor2 of type[/cyan]")
        suggestions.append("Example: [dim]type result = Ok of string | Error of string[/dim]")

    return suggestions
