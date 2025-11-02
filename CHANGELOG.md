# Changelog

All notable changes to Polyglot FFI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [0.5.1] - 2025-11-02

### Added
- **OCaml Library Support:**
  - Support for additional OCaml libraries in build system (e.g., `str`, `unix`, `threads`)
  - `libraries` field in `[source]` config section for specifying OCaml dependencies
  - Automatic linker flags for known OCaml C libraries
  - Enhanced Dune generator with library linking support

- **Improved Error Messages:**
  - Context-specific suggestions for TOML syntax errors
  - Detailed error messages for missing fields and invalid configurations
  - Better error handling in OCaml parser with line numbers
  - Helpful suggestions for common configuration mistakes

- **Test Coverage Improvements:**
  - Added 56 new tests (total: 364 tests, all passing)
  - Achieved 100% coverage for 20 core modules
  - Created new unit test files for better organization:
    - `tests/unit/test_naming.py` - 11 tests for naming utilities
    - `tests/unit/test_config.py` - 15 tests for configuration module
  - Enhanced existing test suites with 30+ additional edge case tests

### Changed
- **Build System:**
  - Removed `ctypes.foreign` from library list (only used via `-package` flag)
  - Cleaner dune configuration with proper library dependencies
  - Eliminates "directory clash" warning for ctypes

- **Type Generation:**
  - Fixed string option handling in ctypes generator (string options now correctly nullable)
  - Added parentheses wrapping for complex ctypes expressions for correct parsing
  - List parameters now automatically add length parameter in function signatures

- **Configuration:**
  - Enhanced TOML error parsing with specific suggestions
  - Better validation error messages with actionable advice
  - Support for OCaml library specification in source config

### Fixed
- **Ctypes Generator:**
  - Fixed string option types (now `string` instead of `ptr string`)
  - Fixed type wrapping with parentheses for proper ctypes parsing
  - Added missing length parameter for list types in function signatures
  - Corrected option type handling for primitives vs pointers

- **Error Handling:**
  - Fixed duplicate line info in parser error messages
  - Improved error message formatting with proper context
  - Better suggestions for configuration errors

- **Test Coverage (Modules at 100%):**
  - parsers/ocaml.py: 90% → 100%
  - core/config.py: 84% → 98%
  - type_system/registry.py: 96% → 100%
  - generators/ctypes_gen.py: 95% → 100%
  - commands/clean.py: 94% → 100%
  - ir/types.py: 90% → 100%

### Technical Details
- **OCaml Library Integration:**
  - Library mapping system for C dependencies (str → `-lcamlstr`, unix → `-lunix`, etc.)
  - Package formatting for ocamlfind `-package` flag
  - Linker flags automatically added to shared library creation
  - Works across macOS (.dylib) and Linux (.so) builds

- **Enhanced Error Messages:**
  - Bracket mismatch suggestions for TOML table syntax
  - Quote-related suggestions for string value errors
  - Missing field suggestions with example configuration
  - Unsupported language suggestions with roadmap reference

- **Code Quality:**
  - 20 modules at 100% test coverage
  - Comprehensive edge case testing
  - Mock-based tests for hard-to-reach error paths
  - Improved test organization and maintainability

### Quality Metrics
- **Before:** 308 tests, 66% coverage
- **After:** 364 tests (+56), 71% coverage (+5%)
- **Achievement:** 20 modules at 100% coverage
- **Test Success Rate:** 100% (364/364 passing)

## [0.5.0] - 2025-10-30

### Added
- **OCaml Runtime Initialization:**
  - Added `ml_init()` function to C stub generator for proper OCaml runtime initialization
  - Automatic initialization call in Python wrapper at module import time
  - Prevents segmentation faults when calling OCaml functions from Python
  - Idempotent design (safe to call multiple times)
  - Uses `caml_startup()` to initialize runtime and execute `Callback.register` calls

### Changed
- **Build System Improvements:**
  - Added `-thread` flag to OCaml compilation commands for proper threading support
  - Added threading library linking: `-lunix -lthreadsnat` (both macOS and Linux)
  - Removed duplicate `-lSystem` flag from macOS linking (already provided by `-lasmrun`)
  - Platform-specific shared library creation rules now include all necessary runtime libraries

- **Python Wrapper Generation:**
  - Platform detection now uses correct library extensions: `.dylib` (macOS), `.so` (Linux), `.dll` (Windows)
  - Runtime initialization happens automatically at module import
  - Improved error messages for library loading failures

### Fixed
- **Critical: Python Integration (Issue #21):**
  - Fixed segmentation fault when calling OCaml functions from Python
  - Shared libraries now properly embed and initialize OCaml runtime
  - All Python integration tests now work correctly across all type tests
  - Complete fix validated with test-fix-check and test-types-float projects

- **Platform Compatibility (Issue #21):**
  - Fixed hardcoded `.so` extension in Python wrapper generator
  - Now correctly detects platform and uses appropriate extension
  - Supports macOS (.dylib), Linux (.so), and Windows (.dll)

- **Build Warnings:**
  - Eliminated "Package `threads': Linking problems may arise" warning
  - Eliminated "ignoring duplicate libraries: '-lSystem'" warning on macOS
  - Reduced build warnings from 3 to 1 (remaining warning is harmless)

### Technical Details
- **OCaml Runtime:**
  - Uses static flag `_ocaml_initialized` to ensure single initialization
  - `caml_startup(argv)` called with NULL argv (command-line args not needed)
  - All `Callback.register` calls execute during runtime initialization
  - Functions accessible via `caml_named_value()` after initialization

- **Shared Library Structure:**
  - Compiles C stubs separately to `.o` file with PIC (-fPIC)
  - Compiles OCaml code with `-output-obj` to create object file with embedded runtime
  - Links both object files with gcc to create final shared library
  - Uses `(mode promote)` to copy library from _build to source tree

- **Threading Support:**
  - Links against `libthreadsnat.a` for native threading support
  - Links against `libunix.a` for Unix system call support
  - Library size increased from ~398K to ~1.2M due to additional runtime support
  - No performance impact observed

### Testing
- All functionality tests pass (test-fix-check, test-types-float)
- No segmentation faults
- Correct results from all generated functions
- Platform detection works on macOS (tested)
- Build warnings reduced from 3 to 1 harmless warning

## [0.4.3] - 2025-01-30

### Fixed
- **Build System (Critical):**
  - Fixed dune-project format error - moved comment after required `(lang dune 3.16)` declaration
  - Removed incorrect manual ocamlmklib rule that conflicted with dune's ctypes extension
  - Fixed include path for local headers - changed from `(include ...)` to `(preamble ...)` directive
  - Fixed C type const correctness - updated string parameters from `char*` to `const char*`

- **Code Generation:**
  - Fixed ctypes function signature type mismatch - added `open F` in functor body
  - Fixed unused open warning in type_description.ml
  - Comprehensive module name sanitization - hyphens now converted to underscores throughout

- **Name Sanitization:**
  - Project names with hyphens (e.g., `my-crypto-lib`) now work correctly
  - Created centralized naming utility for consistent sanitization
  - All generators now use sanitized names for files, libraries, and identifiers
  - Applies to: Dune configs, C stubs, Python wrappers, all generated filenames

### Changed
- C stub generator now uses `const char*` for string types (improved const correctness)
- Dune generator uses preamble directive for local headers instead of include
- All generators import and use centralized `sanitize_module_name()` function

### Documentation
- **Prerequisites:** Added OCaml build dependencies (dune, ctypes, ctypes-foreign) to README, quickstart, and man pages
- **Hyphenated Names:** Documented automatic sanitization and file renaming requirements
- **Troubleshooting:** Added FAQ entries for common build errors:
  - "Library ctypes not found" error and solution
  - "Invalid module name" error with hyphenated projects
  - File renaming guidance when copying sources to generated/
- **Man Pages:** Enhanced polyglot-ffi-generate(1) NOTES section with prerequisites and naming guidance
- **Examples:** Updated all examples to show correct file naming with underscores

### Technical Details
- End-to-end build now works successfully with no errors or warnings
- Generated bindings compile cleanly with dune
- All build artifacts (`.a`, `.cma`, `.cmxa`, `.so`) created correctly
- Full compatibility with OCaml module naming requirements

## [0.4.2] - 2025-01-29

### Fixed
- Verbose flag (-v/--verbose) now works in both positions for better UX
  - Can now use: `polyglot-ffi generate file.mli -v` (standard position after command)
  - Still works: `polyglot-ffi -v generate file.mli` (global position before command)
  - Applies to all commands: init, generate, watch, check, clean

### Documentation
- Updated all man pages to document verbose flag for each command
- Added verbose option to OPTIONS section in all command man pages
- Fixed verbose usage examples in FAQ documentation

## [0.4.1] - 2025-10-28

### Changed
- Updated documentation URL from `https://chizy7.github.io/polyglot-ffi/` to `https://polyglotffi.com/` across all files

### Fixed
- Typo in ROADMAP.md ("Ocotber" → "October")

## [0.4.0] - 2025-10-25

### Added
- **Testing & Quality:**
  - 262 tests (100% passing, 0 failures)
  - 75% code coverage across all modules
  - Test refactoring to use public APIs

- **CI/CD Pipeline:**
  - GitHub Actions workflows (CI, Release, Docs)
  - Automated testing on 3 platforms × 5 Python versions
  - Security scanning (safety, bandit)
  - Code quality checks (black, flake8, mypy)
  - Automated PyPI publishing on release
  - Dependabot for dependency updates

- **Developer Experience:**
  - Shell completions (bash, zsh, fish)
  - Man pages for all commands
  - Performance benchmarks (~15,000 generations/second)
  - Enhanced error messages with suggestions
  - Rich console output with progress indicators

### Changed
- Migrated from Pydantic V1 to V2
- Updated version display in CLI to show "polyglot-ffi" instead of "python -m polyglot_ffi"
- Improved Python identifier sanitization (handles hyphens)

### Fixed
- Config template mismatch between generator and validator
- Bash/fish completion installer improvements
- Better error handling in clean command
- CodeRabbit analysis issues resolved

## [0.3.0] - 2025-10-22

### Added
- **Watch Mode:**
  - Auto-regenerate bindings on file changes
  - Optional auto-build after regeneration
  - Configurable watch paths

- **Project Validation:**
  - `check` command to validate project configuration
  - Dependency checking
  - Language-specific validation

- **Clean Command:**
  - Remove generated files
  - Dry-run mode to preview deletions
  - Clean all option for directories

- **Configuration:**
  - `polyglot.toml` configuration file support
  - Project-level settings
  - Target language configuration

- **Enhanced CLI:**
  - Rich console output with colors
  - Progress indicators for long operations
  - Detailed error messages with suggestions

### Changed
- Improved error handling across all commands
- Better user feedback during operations

## [0.2.0] - 2025-10-19

### Added
- **Complex Types Support:**
  - Option types (`'a option`, `string option`, `int option`)
  - List types (`'a list`, `int list`, `string list`)
  - Tuple types (`'a * 'b`, `int * string * float`)
  - Record types (`type user = { name: string; age: int }`)
  - Variant types (`type result = Ok of string | Error of string`)
  - Type variables (`'a`, `'b` for polymorphic types)
  - Custom type references
  - Nested & combined types (`(int * string) list option`)

- **Type Registry System:**
  - Extensible type mappings
  - Support for OCaml, Python, C, and Rust type mappings
  - Custom type converters
  - Type validation and resolution

- **Testing:**
  - 176 new tests for complex types
  - 65% → 75% coverage increase

### Changed
- Enhanced parser to handle complex type expressions
- Improved code generation for nested types
- Better memory management for complex types in C stubs

## [0.1.0] - 2025-10-15

### Added
- **Core Functionality:**
  - Parse OCaml `.mli` interface files
  - Generate OCaml ctypes bindings
  - Generate memory-safe C stubs
  - Generate Python wrapper modules with type hints
  - Generate Dune build configurations

- **Primitive Types:**
  - `string`, `int`, `float`, `bool`, `unit`
  - Multi-parameter functions
  - Documentation preservation

- **CLI Commands:**
  - `init` - Initialize new project
  - `generate` - Generate FFI bindings
  - `--help` - Comprehensive help system

- **Build System:**
  - Automatic Dune configuration generation
  - OCaml build integration
  - Python packaging support

- **Documentation:**
  - README with quick start
  - Architecture documentation
  - Type mapping guide
  - Contributing guidelines

### Technical Details
- Python 3.8+ support
- OCaml 4.14+ compatibility
- Proper CAMLparam/CAMLreturn macros
- GC-safe memory management
- Type-safe Python wrappers

---

## Release Categories

### Added
New features or capabilities

### Changed
Changes in existing functionality

### Deprecated
Soon-to-be removed features

### Removed
Removed features

### Fixed
Bug fixes

### Security
Security vulnerability fixes

---

## Links

- [PyPI](https://pypi.org/project/polyglot-ffi/)
- [Documentation](https://polyglotffi.com/)
- [GitHub Repository](https://github.com/chizy7/polyglot-ffi)
- [Issue Tracker](https://github.com/chizy7/polyglot-ffi/issues)

---

[Unreleased]: https://github.com/chizy7/polyglot-ffi/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/chizy7/polyglot-ffi/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/chizy7/polyglot-ffi/compare/v0.4.3...v0.5.0
[0.4.3]: https://github.com/chizy7/polyglot-ffi/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/chizy7/polyglot-ffi/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/chizy7/polyglot-ffi/releases/tag/v0.4.1
[0.4.0]: https://github.com/chizy7/polyglot-ffi/releases/tag/v0.4.0
