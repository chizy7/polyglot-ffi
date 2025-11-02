"""
Configuration file parsing and validation.

Support for polyglot.toml configuration files.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Handle tomli/tomllib (Python < 3.11 needs tomli)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

from pydantic import BaseModel, Field, field_validator, ConfigDict
from polyglot_ffi.utils.errors import ConfigurationError


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    name: str = Field(..., description="Project name")
    version: str = Field(default="0.1.0", description="Project version")
    description: Optional[str] = Field(None, description="Project description")
    authors: List[str] = Field(default_factory=list, description="Project authors")


class SourceConfig(BaseModel):
    """Source language configuration."""

    language: str = Field(..., description="Source language (e.g., 'ocaml')")
    files: List[str] = Field(default_factory=list, description="Source files to process")
    dir: Optional[str] = Field(None, description="Source directory")
    exclude: List[str] = Field(default_factory=list, description="Files to exclude")
    libraries: List[str] = Field(
        default_factory=list, description="OCaml libraries to link (e.g., ['str', 'unix'])"
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate source language."""
        supported = ["ocaml"]
        if v.lower() not in supported:
            raise ValueError(f"Unsupported source language: {v}. Supported: {', '.join(supported)}")
        return v.lower()


class TargetConfig(BaseModel):
    """Target language configuration."""

    language: str = Field(..., description="Target language (e.g., 'python', 'rust')")
    output_dir: str = Field(default="generated", description="Output directory")
    enabled: bool = Field(default=True, description="Enable this target")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate target language."""
        supported = ["python", "rust", "c"]
        if v.lower() not in supported:
            raise ValueError(f"Unsupported target language: {v}. Supported: {', '.join(supported)}")
        return v.lower()


class BuildConfig(BaseModel):
    """Build system configuration."""

    auto_build: bool = Field(default=False, description="Auto-build after generation")
    build_command: Optional[str] = Field(None, description="Custom build command")


class TypeMappingConfig(BaseModel):
    """Custom type mapping configuration."""

    ocaml: Optional[str] = None
    python: Optional[str] = None
    rust: Optional[str] = None
    c: Optional[str] = None


class PolyglotConfig(BaseModel):
    """Complete polyglot.toml configuration."""

    project: ProjectConfig
    source: SourceConfig
    targets: List[TargetConfig] = Field(default_factory=list)
    build: BuildConfig = Field(default_factory=BuildConfig)
    type_mappings: Dict[str, TypeMappingConfig] = Field(
        default_factory=dict, description="Custom type mappings"
    )

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v: List[TargetConfig]) -> List[TargetConfig]:
        """Ensure at least one target is configured."""
        if not v:
            raise ValueError("At least one target language must be configured")
        return v

    model_config = ConfigDict(extra="allow")  # Allow extra fields for future expansion


def load_config(config_path: Path) -> PolyglotConfig:
    """
    Load and validate configuration from polyglot.toml.

    Args:
        config_path: Path to polyglot.toml file

    Returns:
        Validated PolyglotConfig object

    Raises:
        ConfigurationError: If configuration is invalid
    """
    if tomllib is None:
        raise ConfigurationError(
            message="TOML library not available",
            config_path=config_path,
            suggestions=[
                "Install tomli: pip install tomli",
                "Upgrade to Python 3.11+ which includes tomllib",
            ],
        )

    if not config_path.exists():
        raise ConfigurationError(
            message=f"Configuration file not found: {config_path}",
            config_path=config_path,
            suggestions=[
                "Run 'polyglot-ffi init' to create a project",
                "Create polyglot.toml manually in the project root",
            ],
        )

    try:
        with open(config_path, "rb") as f:
            raw_config = tomllib.load(f)
    except Exception as e:
        error_msg = str(e)

        # Build context-specific suggestions
        suggestions = []
        if "Expected ']'" in error_msg:
            suggestions.append("Table names must be enclosed in square brackets")
            suggestions.append("Check that all opening brackets have matching closing brackets")
            suggestions.append("Example: \\[project] or \\[\\[targets]]")
        elif "Expected '\"'" in error_msg or "quote" in error_msg.lower():
            suggestions.append('String values must be quoted: name = "value"')
            suggestions.append("Use single quotes for literal strings: path = 'C:\\Windows'")
        elif "Expected '='" in error_msg:
            suggestions.append("Key-value pairs must use '=': key = \"value\"")
        else:
            suggestions.append("Check TOML syntax at https://toml.io/en/")
            suggestions.append("Ensure proper quoting of strings")
            suggestions.append("Verify array and table syntax")

        raise ConfigurationError(
            message=f"TOML syntax error: {e}",
            config_path=config_path,
            suggestions=suggestions,
        )

    try:
        config = PolyglotConfig(**raw_config)
        return config
    except Exception as e:
        # Parse pydantic error to extract field info
        error_msg = str(e)

        # Build helpful suggestions based on the error
        suggestions = []

        # Check if it's a missing field error
        if "Field required" in error_msg or "missing" in error_msg.lower():
            suggestions.append("Add the required section to your polyglot.toml")
            suggestions.append(
                "Required sections: 'project' (with name field), 'source' (with language), 'targets' (array)"
            )
            suggestions.append("Example: See the template created by 'polyglot-ffi init'")
        # Check if it's an unsupported language error
        elif "Unsupported target language" in error_msg:
            suggestions.append("Currently supported target languages: python, rust, c")
            suggestions.append("Note: Only Python is fully implemented at this time")
            suggestions.append("Check the roadmap at: https://github.com/chizy7/polyglot-ffi")
        elif "Unsupported source language" in error_msg:
            suggestions.append("Currently supported source language: ocaml")
            suggestions.append("Other source languages may be added in future releases")
        else:
            suggestions.append("Verify field names and types in polyglot.toml")
            suggestions.append("Check for typos in section names")
            suggestions.append("See docs/configuration.md for examples")

        raise ConfigurationError(
            message=f"Invalid configuration: {e}",
            config_path=config_path,
            suggestions=suggestions,
        )


def create_default_config(project_name: str, target_langs: List[str]) -> Dict[str, Any]:
    """
    Create a default polyglot.toml configuration.

    Args:
        project_name: Name of the project
        target_langs: List of target languages

    Returns:
        Dictionary representing the default configuration
    """
    return {
        "project": {
            "name": project_name,
            "version": "0.1.0",
            "description": f"FFI bindings for {project_name}",
        },
        "source": {
            "language": "ocaml",
            "dir": "src",
            "files": [f"{project_name}.mli"],
        },
        "targets": [
            {"language": lang, "output_dir": f"generated/{lang}", "enabled": True}
            for lang in target_langs
        ],
        "build": {
            "auto_build": False,
        },
    }


def validate_config(config: PolyglotConfig) -> List[str]:
    """
    Validate configuration and return list of warnings.

    Args:
        config: Configuration to validate

    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings = []

    # Check if source files exist
    if config.source.dir:
        source_dir = Path(config.source.dir)
        if not source_dir.exists():
            warnings.append(f"Source directory does not exist: {source_dir}")

    for source_file in config.source.files:
        file_path = Path(config.source.dir or ".") / source_file
        if not file_path.exists():
            warnings.append(f"Source file not found: {file_path}")

    # Check for duplicate target languages
    target_langs = [t.language for t in config.targets if t.enabled]
    if len(target_langs) != len(set(target_langs)):
        warnings.append("Duplicate target languages found")

    # Warn if no targets are enabled
    if not any(t.enabled for t in config.targets):
        warnings.append("No target languages are enabled")

    return warnings
