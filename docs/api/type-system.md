# Type System API

The type system manages mappings between IR types and target language types, ensuring consistent type translation across all generators.

## Overview

The type system provides:

- **Type Registry**: Central repository for type mappings
- **Built-in Types**: Standard primitive type mappings
- **Custom Types**: User-defined type mappings
- **Type Validation**: Ensure types are supported
- **Caching**: O(1) lookup performance

## Type Registry

::: polyglot_ffi.type_system.registry.TypeRegistry
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      members:
        - register_primitive
        - register_converter
        - get_mapping
        - validate

### Getting the Registry

```python
from polyglot_ffi.type_system.registry import get_default_registry

# Get the global registry (lazy-initialized)
registry = get_default_registry()
```

### Basic Usage

```python
from polyglot_ffi.ir.types import STRING, INT, ir_option
from polyglot_ffi.type_system.registry import get_default_registry

registry = get_default_registry()

# Map primitive types
registry.get_mapping(STRING, "python")  # "str"
registry.get_mapping(INT, "python")     # "int"
registry.get_mapping(STRING, "rust")    # "String"
registry.get_mapping(INT, "c")          # "int64_t"

# Map complex types
opt_string = ir_option(STRING)
registry.get_mapping(opt_string, "python")  # "Optional[str]"
registry.get_mapping(opt_string, "rust")    # "Option<String>"
```

## Built-in Type Mappings

The registry comes pre-loaded with standard type mappings:

### String Types

| IR Type | Python | Rust | OCaml | C |
|---------|--------|------|-------|---|
| `string` | `str` | `String` | `string` | `char*` |

### Integer Types

| IR Type | Python | Rust | OCaml | C |
|---------|--------|------|-------|---|
| `int` | `int` | `i64` | `int` | `int64_t` |

### Float Types

| IR Type | Python | Rust | OCaml | C |
|---------|--------|------|-------|---|
| `float` | `float` | `f64` | `float` | `double` |

### Boolean Types

| IR Type | Python | Rust | OCaml | C |
|---------|--------|------|-------|---|
| `bool` | `bool` | `bool` | `bool` | `int` |

### Unit Types

| IR Type | Python | Rust | OCaml | C |
|---------|--------|------|-------|---|
| `unit` | `None` | `()` | `unit` | `void` |

## Complex Type Mappings

### Option Types

```python
from polyglot_ffi.ir.types import STRING, ir_option

opt_string = ir_option(STRING)

registry.get_mapping(opt_string, "python")  # "Optional[str]"
registry.get_mapping(opt_string, "rust")    # "Option<String>"
registry.get_mapping(opt_string, "ocaml")   # "string option"
```

### List Types

```python
from polyglot_ffi.ir.types import INT, ir_list

int_list = ir_list(INT)

registry.get_mapping(int_list, "python")  # "List[int]"
registry.get_mapping(int_list, "rust")    # "Vec<i64>"
registry.get_mapping(int_list, "ocaml")   # "int list"
```

### Tuple Types

```python
from polyglot_ffi.ir.types import STRING, INT, ir_tuple

pair = ir_tuple(STRING, INT)

registry.get_mapping(pair, "python")  # "Tuple[str, int]"
registry.get_mapping(pair, "rust")    # "(String, i64)"
registry.get_mapping(pair, "ocaml")   # "(string * int)"
```

### Nested Types

The type system handles arbitrarily nested types:

```python
from polyglot_ffi.ir.types import STRING, INT, ir_option, ir_list, ir_tuple

# option[list[tuple[str, int]]]
complex = ir_option(ir_list(ir_tuple(STRING, INT)))

registry.get_mapping(complex, "python")
# "Optional[List[Tuple[str, int]]]"

registry.get_mapping(complex, "rust")
# "Option<Vec<(String, i64)>>"
```

## Custom Type Mappings

### Registering Primitive Types

```python
from polyglot_ffi.type_system.registry import TypeRegistry

registry = TypeRegistry()

# Register a custom primitive type
registry.register_primitive("bytes", {
    "ocaml": "bytes",
    "python": "bytes",
    "rust": "Vec<u8>",
    "c": "uint8_t*"
})

# Use it
from polyglot_ffi.ir.types import ir_primitive
bytes_type = ir_primitive("bytes")
registry.get_mapping(bytes_type, "python")  # "bytes"
```

### Registering Type Converters

For complex custom types, register a converter function:

```python
from polyglot_ffi.ir.types import IRType

def convert_timestamp(ir_type: IRType) -> str:
    """Convert timestamp type to Python."""
    return "datetime.datetime"

registry.register_converter("timestamp", "python", convert_timestamp)

# Use it
timestamp = ir_primitive("timestamp")
registry.get_mapping(timestamp, "python")  # "datetime.datetime"
```

### Custom Types in Configuration

Users can define custom types in `polyglot.toml`:

```toml
[types.binary_data]
ocaml = "bytes"
python = "bytes"
rust = "Vec<u8>"
c = "uint8_t*"

[types.timestamp]
ocaml = "float"
python = "datetime.datetime"
rust = "SystemTime"
c = "time_t"
```

## Type Validation

Check if a type mapping exists before using it:

```python
from polyglot_ffi.ir.types import STRING, ir_primitive

registry = get_default_registry()

# Validate known type
is_valid = registry.validate(STRING, "python")  # True

# Validate unknown type
unknown = ir_primitive("unknown_type")
is_valid = registry.validate(unknown, "python")  # False
```

## Error Handling

The registry raises `TypeMappingError` for invalid mappings:

```python
from polyglot_ffi.type_system.registry import TypeMappingError
from polyglot_ffi.ir.types import ir_primitive

try:
    unknown = ir_primitive("unknown_type")
    registry.get_mapping(unknown, "python")
except TypeMappingError as e:
    print(f"Type mapping error: {e}")
    # "Unknown primitive type 'unknown_type'"
```

## Performance

The type registry is optimized for speed:

- **O(1) primitive lookups**: Direct dictionary access
- **Caching**: Computed mappings cached automatically
- **Pre-compilation**: No runtime regex compilation

Typical performance:
- Primitive lookup: ~0.0003ms
- Option lookup: ~0.0007ms (with cache hit)
- Complex nested type: ~0.0019ms (with cache hit)

## Cache Behavior

The registry automatically caches computed type mappings:

```python
# First call: computes and caches
result1 = registry.get_mapping(ir_option(STRING), "python")

# Second call: returns cached result (faster)
result2 = registry.get_mapping(ir_option(STRING), "python")

# Cache is cleared when registry is modified
registry.register_primitive("newtype", {...})
# Cache cleared automatically
```

## Usage in Generators

Generators use the registry to produce consistent type mappings:

```python
from polyglot_ffi.ir.types import IRFunction, IRParameter
from polyglot_ffi.type_system.registry import get_default_registry

def generate_python_signature(func: IRFunction) -> str:
    """Generate Python function signature."""
    registry = get_default_registry()

    # Map parameter types
    params = []
    for param in func.parameters:
        py_type = registry.get_mapping(param.type, "python")
        params.append(f"{param.name}: {py_type}")

    # Map return type
    return_type = registry.get_mapping(func.return_type, "python")

    # Build signature
    params_str = ", ".join(params)
    return f"def {func.name}({params_str}) -> {return_type}:"
```

## Complete Example

```python
from polyglot_ffi.ir.types import (
    STRING, INT, BOOL, ir_option, ir_list, ir_tuple, ir_primitive
)
from polyglot_ffi.type_system.registry import (
    TypeRegistry, get_default_registry
)

# Get default registry with built-in types
registry = get_default_registry()

# Test primitive mappings
print("Primitives:")
for lang in ["python", "rust", "ocaml", "c"]:
    print(f"  {lang}: string -> {registry.get_mapping(STRING, lang)}")

# Test complex types
print("\nComplex types:")
opt_int = ir_option(INT)
print(f"  option[int] -> {registry.get_mapping(opt_int, 'python')}")

list_str = ir_list(STRING)
print(f"  list[str] -> {registry.get_mapping(list_str, 'rust')}")

pair = ir_tuple(STRING, INT)
print(f"  tuple[str,int] -> {registry.get_mapping(pair, 'python')}")

# Test nested types
nested = ir_option(ir_list(ir_tuple(STRING, INT)))
print(f"\nNested type:")
print(f"  Python: {registry.get_mapping(nested, 'python')}")
print(f"  Rust: {registry.get_mapping(nested, 'rust')}")

# Register custom type
registry.register_primitive("uuid", {
    "python": "uuid.UUID",
    "rust": "Uuid",
    "ocaml": "string",
    "c": "char*"
})

uuid_type = ir_primitive("uuid")
print(f"\nCustom type:")
print(f"  uuid -> {registry.get_mapping(uuid_type, 'python')}")

# Validate types
print(f"\nValidation:")
print(f"  STRING valid? {registry.validate(STRING, 'python')}")
print(f"  unknown valid? {registry.validate(ir_primitive('unknown'), 'python')}")
```

## See Also

- [IR Types](ir-types.md) - Type definitions
- [Generators](generators.md) - Using type mappings
- [Configuration](../configuration.md) - Custom type config
