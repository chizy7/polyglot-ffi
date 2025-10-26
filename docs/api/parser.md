# Parser API

The parser module is responsible for converting OCaml interface files (.mli) into the intermediate representation (IR).

## Overview

The parser takes OCaml `.mli` files as input and produces language-agnostic IR that can be used by any generator. This abstraction allows adding support for new source languages (Rust, Python, etc.) without changing generators.

## OCaml Parser

::: polyglot_ffi.parsers.ocaml.OCamlParser
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - __init__
        - parse
        - parse_file
        - parse_string

## Convenience Functions

::: polyglot_ffi.parsers.ocaml.parse_mli_file
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

::: polyglot_ffi.parsers.ocaml.parse_mli_string
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Usage Examples

### Parsing from File

```python
from pathlib import Path
from polyglot_ffi.parsers.ocaml import OCamlParser

# Method 1: Using class method
module = OCamlParser.parse_file(Path("crypto.mli"))

# Method 2: Using convenience function
from polyglot_ffi.parsers.ocaml import parse_mli_file
module = parse_mli_file(Path("crypto.mli"))

print(f"Module: {module.name}")
print(f"Functions: {len(module.functions)}")
```

### Parsing from String

```python
from polyglot_ffi.parsers.ocaml import parse_mli_string

mli_code = """
val encrypt : string -> string
val decrypt : string -> string
"""

module = parse_mli_string(mli_code)

for func in module.functions:
    print(f"Function: {func.name}")
    print(f"  Parameters: {[p.name for p in func.parameters]}")
    print(f"  Return type: {func.return_type}")
```

### Custom Parser Instance

```python
from polyglot_ffi.parsers.ocaml import OCamlParser

content = Path("api.mli").read_text()
parser = OCamlParser(content, filename="api.mli")
module = parser.parse()

# Access parsed data
for func in module.functions:
    print(f"{func.name}: {func.signature}")
```

## Supported OCaml Syntax

### Primitive Types

- `string` - String type
- `int` - Integer type
- `float` - Floating point type
- `bool` - Boolean type
- `unit` - Unit/void type

### Complex Types

- **Option types**: `'a option`, `string option`, `int option`
- **List types**: `'a list`, `string list`, `int list`
- **Tuple types**: `'a * 'b`, `string * int`, `int * string * bool`
- **Record types**: Named field records
- **Variant types**: Sum types with constructors
- **Type variables**: `'a`, `'b`, etc. (polymorphic types)
- **Custom types**: User-defined type names

### Function Signatures

```ocaml
(* Simple function *)
val process : string -> string

(* Multiple parameters *)
val add : int -> int -> int

(* No parameters *)
val get_version : unit -> string

(* Complex types *)
val find : string -> string option
val map : ('a -> 'b) -> 'a list -> 'b list

(* With documentation *)
(** Encrypt a string using AES-256 *)
val encrypt : string -> string
```

## Error Handling

The parser raises `ParseError` exceptions with detailed information:

```python
from polyglot_ffi.parsers.ocaml import parse_mli_string
from polyglot_ffi.utils.errors import ParseError

try:
    module = parse_mli_string("val invalid : unknown_type -> string")
except ParseError as e:
    print(f"Parse error: {e.message}")
    print(f"Line: {e.context.line}")
    print(f"File: {e.context.file_path}")
    if e.suggestions:
        print(f"Suggestions: {', '.join(e.suggestions)}")
```

### Common Parse Errors

| Error | Cause | Suggestion |
|-------|-------|------------|
| Unsupported type | Unknown type name | Check type name spelling, use supported types |
| Invalid signature | Malformed function signature | Check syntax: `val name : type -> type` |
| Invalid record | Record syntax error | Use `type t = { field : type }` |
| Invalid variant | Variant syntax error | Use `type t = Constructor \| Other` |

## Performance

The parser is optimized for speed:

- **Regex pre-compilation**: Patterns compiled once at class level
- **Single-pass parsing**: Each line read once
- **Lazy evaluation**: Only parses when needed

Typical performance:
- Small files (< 10 functions): ~0.01ms
- Medium files (10-50 functions): ~0.05ms
- Large files (100+ functions): ~0.3ms

## See Also

- [IR Types](ir-types.md) - Intermediate representation
- [Type System](type-system.md) - Type mappings
- [Generators](generators.md) - Code generation
