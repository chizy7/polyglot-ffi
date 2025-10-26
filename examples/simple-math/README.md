# Example 1: Simple Math Library

A basic example demonstrating OCaml → Python bindings for mathematical functions.

## Overview

This example shows:
- Primitive types (int, float)
- Multiple parameters
- Simple function signatures
- Basic project structure

## Project Structure

```
simple-math/
├── README.md
├── polyglot.toml           # Configuration
├── src/
│   ├── math.mli            # OCaml interface
│   └── math.ml             # OCaml implementation
├── generated/              # Auto-generated bindings
└── example.py              # Python usage example
```

## Step 1: Define OCaml Interface

**File: `src/math.mli`**

```ocaml
(** Add two integers *)
val add : int -> int -> int

(** Subtract two integers *)
val subtract : int -> int -> int

(** Multiply two floats *)
val multiply : float -> float -> float

(** Divide two floats *)
val divide : float -> float -> float

(** Calculate power *)
val power : float -> int -> float
```

## Step 2: Implement in OCaml

**File: `src/math.ml`**

```ocaml
let add x y = x + y

let subtract x y = x - y

let multiply x y = x *. y

let divide x y =
  if y = 0.0 then
    failwith "Division by zero"
  else
    x /. y

let power base exp =
  Float.pow base (float_of_int exp)
```

## Step 3: Configure Project

**File: `polyglot.toml`**

```toml
[project]
name = "math"
version = "0.1.0"
description = "Simple math library bindings"

[bindings]
source_files = ["src/math.mli"]
output_dir = "generated"

[targets.python]
enabled = true
```

## Step 4: Generate Bindings

```bash
# Initialize project (if starting fresh)
polyglot-ffi init simple-math --lang python

# Generate bindings
polyglot-ffi generate src/math.mli --output generated --name math

# Or use watch mode during development
polyglot-ffi watch
```

## Step 5: Build OCaml Library

**File: `Makefile`**

```makefile
.PHONY: all build clean

all: build

build:
	dune build
	cp _build/default/src/math.so generated/

clean:
	dune clean
	rm -rf generated/*.so
```

Build the library:

```bash
make build
```

## Step 6: Use from Python

**File: `example.py`**

```python
#!/usr/bin/env python3
"""Example usage of math bindings."""

import sys
sys.path.insert(0, 'generated')

from math_py import add, subtract, multiply, divide, power

# Integer operations
print(f"add(5, 3) = {add(5, 3)}")           # 8
print(f"subtract(10, 4) = {subtract(10, 4)}")  # 6

# Float operations
print(f"multiply(2.5, 4.0) = {multiply(2.5, 4.0)}")  # 10.0
print(f"divide(15.0, 3.0) = {divide(15.0, 3.0)}")    # 5.0

# Power
print(f"power(2.0, 10) = {power(2.0, 10)}")  # 1024.0

# Error handling
try:
    result = divide(10.0, 0.0)
except RuntimeError as e:
    print(f"Error: {e}")  # Division by zero
```

Run the example:

```bash
python example.py
```

## Generated Files

After running `polyglot-ffi generate`, you'll have:

### OCaml Ctypes (`generated/type_description.ml`)

```ocaml
open Ctypes

let int = Ctypes.int
let float = Ctypes.float
```

### OCaml Functions (`generated/function_description.ml`)

```ocaml
open Ctypes

let add = foreign "ml_add" (int @-> int @-> returning int)
let subtract = foreign "ml_subtract" (int @-> int @-> returning int)
let multiply = foreign "ml_multiply" (float @-> float @-> returning float)
let divide = foreign "ml_divide" (float @-> float @-> returning float)
let power = foreign "ml_power" (float @-> int @-> returning float)
```

### C Stubs (`generated/stubs.c`)

```c
#include <caml/mlvalues.h>
#include <caml/memory.h>
#include "stubs.h"

CAMLprim value ml_add(value x, value y) {
    CAMLparam2(x, y);
    int c_x = Int_val(x);
    int c_y = Int_val(y);
    int result = add(c_x, c_y);
    CAMLreturn(Val_int(result));
}

// ... similar for other functions
```

### Python Wrapper (`generated/math_py.py`)

```python
import ctypes
from pathlib import Path

_lib = ctypes.CDLL(str(Path(__file__).parent / "math.so"))

# Configure signatures
_lib.ml_add.argtypes = [ctypes.c_int, ctypes.c_int]
_lib.ml_add.restype = ctypes.c_int

def add(x: int, y: int) -> int:
    """Add two integers."""
    return _lib.ml_add(x, y)

# ... similar for other functions
```

## Key Learnings

### 1. Primitive Types

The example demonstrates all primitive types:
- `int` → Python `int`
- `float` → Python `float`
- Automatic type conversion handled by generated code

### 2. Multiple Parameters

Functions can have multiple parameters:

```ocaml
val add : int -> int -> int
```

Becomes:

```python
def add(x: int, y: int) -> int:
```

### 3. Type Safety

The generated Python code includes type hints:

```python
def power(base: float, exp: int) -> float:
    """Calculate power."""
```

### 4. Error Handling

OCaml exceptions are converted to Python exceptions:

```ocaml
let divide x y =
  if y = 0.0 then failwith "Division by zero"
  else x /. y
```

```python
try:
    result = divide(10.0, 0.0)
except RuntimeError as e:
    print(f"Error: {e}")
```

## Next Steps

After mastering this example:

1. **Add More Functions**: Extend `math.mli` with more operations
2. **Complex Types**: See [crypto-lib](../crypto-lib/) for option types
3. **Lists**: See [data-processing](../data-processing/) for list handling
4. **Records**: See [web-api](../web-api/) for structured data

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'math_py'`
- **Solution**: Ensure `generated/` is in Python path or run from project root

**Issue**: `OSError: math.so: cannot open shared object file`
- **Solution**: Run `make build` to compile the OCaml library

**Issue**: `TypeError: Required argument 'x' (pos 1) not found`
- **Solution**: Check function signature matches generated bindings

## Resources

- [Polyglot FFI Documentation](https://docs.polyglot-ffi.dev)
- [OCaml Manual](https://ocaml.org/manual/)
- [Python ctypes](https://docs.python.org/3/library/ctypes.html)
