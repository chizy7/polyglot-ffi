# IR Types API

The IR (Intermediate Representation) types provide a language-agnostic representation of functions and types. This abstraction allows parsers and generators to work independently.

## Overview

The IR layer is the heart of Polyglot FFI's extensibility:

- **Parsers** convert source language → IR
- **Generators** convert IR → target language
- Adding new languages only requires implementing one side

## Core Types

### IRType

Represents a type in the intermediate representation.

::: polyglot_ffi.ir.types.IRType
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### TypeKind

Enumeration of all supported type kinds.

::: polyglot_ffi.ir.types.TypeKind
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### IRParameter

Represents a function parameter.

::: polyglot_ffi.ir.types.IRParameter
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### IRFunction

Represents a function signature.

::: polyglot_ffi.ir.types.IRFunction
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

### IRModule

Represents a complete module with functions and types.

::: polyglot_ffi.ir.types.IRModule
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Type Construction

### Primitive Types

Pre-defined primitive type constants:

```python
from polyglot_ffi.ir.types import STRING, INT, FLOAT, BOOL, UNIT

# Use directly
string_type = STRING  # IRType(kind=TypeKind.PRIMITIVE, name="string")
int_type = INT        # IRType(kind=TypeKind.PRIMITIVE, name="int")
```

### Custom Primitive

```python
from polyglot_ffi.ir.types import ir_primitive

custom_type = ir_primitive("bytes")
# IRType(kind=TypeKind.PRIMITIVE, name="bytes")
```

### Option Types

```python
from polyglot_ffi.ir.types import ir_option, STRING

opt_string = ir_option(STRING)
# IRType(kind=TypeKind.OPTION, name="option", params=[STRING])

# Nested options
opt_opt_int = ir_option(ir_option(INT))
```

### List Types

```python
from polyglot_ffi.ir.types import ir_list, STRING

string_list = ir_list(STRING)
# IRType(kind=TypeKind.LIST, name="list", params=[STRING])

# List of options
list_of_opts = ir_list(ir_option(STRING))
```

### Tuple Types

```python
from polyglot_ffi.ir.types import ir_tuple, STRING, INT

pair = ir_tuple(STRING, INT)
# IRType(kind=TypeKind.TUPLE, name="tuple", params=[STRING, INT])

# Triple
triple = ir_tuple(STRING, INT, BOOL)
```

### Record Types

```python
from polyglot_ffi.ir.types import IRType, TypeKind

person_record = IRType(
    kind=TypeKind.RECORD,
    name="person",
    fields={
        "name": STRING,
        "age": INT,
        "email": ir_option(STRING)
    }
)
```

### Variant Types

```python
result_variant = IRType(
    kind=TypeKind.VARIANT,
    name="result",
    fields={
        "Ok": STRING,      # Success case with string payload
        "Error": STRING    # Error case with string payload
    }
)
```

## Function Construction

### Simple Function

```python
from polyglot_ffi.ir.types import IRFunction, IRParameter, STRING

encrypt_func = IRFunction(
    name="encrypt",
    parameters=[
        IRParameter(name="input", type=STRING)
    ],
    return_type=STRING,
    doc="Encrypt a string using AES-256"
)
```

### Multiple Parameters

```python
add_func = IRFunction(
    name="add",
    parameters=[
        IRParameter(name="x", type=INT),
        IRParameter(name="y", type=INT)
    ],
    return_type=INT
)
```

### No Parameters

```python
get_version = IRFunction(
    name="get_version",
    parameters=[],
    return_type=STRING
)
```

### Complex Types

```python
from polyglot_ffi.ir.types import ir_option, ir_list

find_func = IRFunction(
    name="find",
    parameters=[
        IRParameter(name="query", type=STRING)
    ],
    return_type=ir_option(STRING),
    doc="Find a value, returns None if not found"
)

map_func = IRFunction(
    name="map",
    parameters=[
        IRParameter(name="items", type=ir_list(STRING))
    ],
    return_type=ir_list(INT)
)
```

## Module Construction

```python
from polyglot_ffi.ir.types import IRModule, IRFunction, IRTypeDefinition

module = IRModule(
    name="crypto",
    functions=[
        IRFunction(
            name="encrypt",
            parameters=[IRParameter(name="data", type=STRING)],
            return_type=STRING
        ),
        IRFunction(
            name="decrypt",
            parameters=[IRParameter(name="data", type=STRING)],
            return_type=STRING
        )
    ],
    type_definitions=[
        IRTypeDefinition(
            name="cipher",
            definition=IRType(kind=TypeKind.VARIANT, name="cipher", fields={
                "AES": UNIT,
                "DES": UNIT
            })
        )
    ],
    doc="Cryptography functions"
)
```

## Type Checking Methods

IRType provides convenient type checking methods:

```python
from polyglot_ffi.ir.types import STRING, ir_option, ir_list, ir_tuple

# Check if primitive
STRING.is_primitive()  # True
ir_option(STRING).is_primitive()  # False

# Check if container (option, list, tuple)
ir_option(STRING).is_container()  # True
ir_list(INT).is_container()  # True
STRING.is_container()  # False

# Check if composite (record, variant)
person_record.is_composite()  # True
STRING.is_composite()  # False
```

## String Representation

All IR types have human-readable string representations:

```python
str(STRING)  # "string"
str(ir_option(STRING))  # "string option"
str(ir_list(INT))  # "int list"
str(ir_tuple(STRING, INT))  # "(string, int)"

func = IRFunction(
    name="encrypt",
    parameters=[IRParameter(name="data", type=STRING)],
    return_type=STRING
)
str(func)  # "encrypt(data: string) -> string"
```

## Usage in Generators

Generators work with IR types to produce target code:

```python
from polyglot_ffi.ir.types import IRType, TypeKind
from polyglot_ffi.type_system.registry import get_default_registry

def generate_python_type(ir_type: IRType) -> str:
    """Convert IR type to Python type hint."""
    registry = get_default_registry()

    if ir_type.kind == TypeKind.PRIMITIVE:
        return registry.get_mapping(ir_type, "python")

    elif ir_type.kind == TypeKind.OPTION:
        inner = generate_python_type(ir_type.params[0])
        return f"Optional[{inner}]"

    elif ir_type.kind == TypeKind.LIST:
        inner = generate_python_type(ir_type.params[0])
        return f"List[{inner}]"

    # ... handle other types
```

## Complete Example

```python
from polyglot_ffi.ir.types import (
    IRModule, IRFunction, IRParameter, IRTypeDefinition,
    STRING, INT, BOOL, ir_option, ir_list, ir_tuple
)

# Define a complete module
api_module = IRModule(
    name="api",
    functions=[
        # Simple function
        IRFunction(
            name="get_version",
            parameters=[],
            return_type=STRING,
            doc="Get API version"
        ),

        # Function with optional return
        IRFunction(
            name="find_user",
            parameters=[IRParameter(name="id", type=INT)],
            return_type=ir_option(STRING),
            doc="Find user by ID, returns None if not found"
        ),

        # Function with list parameters
        IRFunction(
            name="filter_active",
            parameters=[IRParameter(name="users", type=ir_list(STRING))],
            return_type=ir_list(STRING),
            doc="Filter active users"
        ),

        # Function with tuple
        IRFunction(
            name="split_name",
            parameters=[IRParameter(name="full_name", type=STRING)],
            return_type=ir_tuple(STRING, STRING),
            doc="Split full name into (first, last)"
        )
    ],
    doc="User API module"
)

# Use the module
print(f"Module: {api_module.name}")
print(f"Functions: {len(api_module.functions)}")

for func in api_module.functions:
    print(f"  {func.name}: {func.signature}")
```

## See Also

- [Parser API](parser.md) - Parsing to IR
- [Generators API](generators.md) - Generating from IR
- [Type System](type-system.md) - Type mappings
