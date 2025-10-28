# Type Mapping Reference

**Version:** v0.4.1

Complete guide to type mappings across languages in Polyglot FFI.

## Implementation Status

| Type Category | Status | Notes |
|---------------|--------|-------|
| **Primitives** | Fully Supported | `string`, `int`, `float`, `bool`, `unit` |
| **Option Types** | Fully Supported | `'a option` → `Optional[T]`, `Option<T>` |
| **List Types** | Fully Supported | `'a list` → `List[T]`, `Vec<T>` |
| **Tuple Types** | Fully Supported | `'a * 'b` → `Tuple[T1, T2]`, `(T1, T2)` |
| **Record Types** | Partial Support | Parsed, basic generation implemented |
| **Variant Types** | Partial Support | Parsed, basic generation implemented |
| **Type Variables** | Supported | Generic/polymorphic types |

**Legend:**
- Fully Supported - Production ready, tested, documented
- Partial Support - Basic functionality works, advanced features in progress

## Primitive Types 

| OCaml | IR | C | Python | Rust | Notes |
|-------|-------|-------|--------|------|-------|
| `string` | `STRING` | `char*` | `str` | `String` | UTF-8 encoded |
| `int` | `INT` | `int` | `int` | `i64` | 31/63-bit on OCaml |
| `float` | `FLOAT` | `double` | `float` | `f64` | IEEE 754 |
| `bool` | `BOOL` | `int` | `bool` | `bool` | 0=false, 1=true |
| `unit` | `UNIT` | `void` | `None` | `()` | No value |

## Conversion Details

### String

**OCaml → C:**
```c
ml_string = caml_copy_string(c_string);
```

**C → OCaml:**
```c
char* c_string = strdup(String_val(ml_string));
```

**Python:**
```python
# Python → C
c_bytes = py_string.encode('utf-8')

# C → Python
py_string = c_bytes.decode('utf-8')
```

### Integer

**OCaml → C:**
```c
ml_int = Val_int(c_int);
```

**C → OCaml:**
```c
int c_int = Int_val(ml_int);
```

### Float

**OCaml → C:**
```c
ml_float = caml_copy_double(c_double);
```

**C → OCaml:**
```c
double c_double = Double_val(ml_float);
```

### Boolean

**OCaml → C:**
```c
ml_bool = Val_bool(c_bool);
```

**C → OCaml:**
```c
int c_bool = Bool_val(ml_bool);
```

## Complex Types 

### Option Types

**OCaml:**
```ocaml
val find : string -> string option
val parse : string -> int option
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `'a option` | `Some x` or `None` |
| IR | `OPTION` | `IRType(kind=OPTION, params=[...])` |
| C | `void*` | Opaque pointer (GC-safe) |
| Python | `Optional[T]` | `value` or `None` |
| Rust | `Option<T>` | `Some(value)` or `None` |

**Example:**
```python
# Python
user = find_user("john")  # Returns Optional[User]
if user is not None:
    print(user.name)
```

### List Types

**OCaml:**
```ocaml
val get_all : unit -> string list
val filter : (int -> bool) -> int list -> int list
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `'a list` | `[x; y; z]` |
| IR | `LIST` | `IRType(kind=LIST, params=[...])` |
| C | `void*` | Opaque OCaml list pointer |
| Python | `List[T]` | `[x, y, z]` |
| Rust | `Vec<T>` | `vec![x, y, z]` |

**Example:**
```python
# Python
users = get_all_users()  # Returns List[User]
for user in users:
    print(user.name)
```

### Tuple Types

**OCaml:**
```ocaml
val pair : string -> int * string
val triple : unit -> int * string * float
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `'a * 'b` | `(x, y)` |
| IR | `TUPLE` | `IRType(kind=TUPLE, params=[...])` |
| C | `void*` | Opaque tuple pointer |
| Python | `Tuple[T1, T2]` | `(x, y)` |
| Rust | `(T1, T2)` | `(x, y)` |

**Example:**
```python
# Python
name, age = get_name_and_age(user)  # Returns Tuple[str, int]
print(f"{name} is {age} years old")
```

### Record Types

**OCaml:**
```ocaml
type user = {
  name: string;
  age: int;
  email: string option;
}

val create_user : string -> int -> string -> user
val get_name : user -> string
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `type t = { ... }` | Record with fields |
| IR | `RECORD` | `IRTypeDefinition(kind=RECORD, fields={...})` |
| C | `void*` | Opaque record pointer |
| Python | `class User` | Python class |
| Rust | `struct User` | Rust struct |

**Example:**
```python
# Python (type hint generated)
def create_user(name: str, age: int, email: str) -> User:
    pass

user = create_user("John", 25, "john@example.com")
```

### Variant Types

**OCaml:**
```ocaml
type result = Ok of string | Error of string
type status = Active | Inactive | Pending

val process : string -> result
val check : user -> status
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `type t = A \| B of 'a` | Sum type with constructors |
| IR | `VARIANT` | `IRTypeDefinition(kind=VARIANT, variants={...})` |
| C | `void*` | Opaque variant pointer |
| Python | `class Result` | Python class (enum-like) |
| Rust | `enum Result` | Rust enum |

**Example:**
```python
# Python
result = process("input")  # Returns Result
# Handle different variants in application logic
```

### Type Variables (Polymorphic Types)

**OCaml:**
```ocaml
val identity : 'a -> 'a
val map : ('a -> 'b) -> 'a list -> 'b list
```

**Type Mappings:**

| Language | Type | Representation |
|----------|------|----------------|
| OCaml | `'a`, `'b` | Type variables |
| IR | `PRIMITIVE` | `IRType(kind=PRIMITIVE, name="'a")` |
| C | `void*` | Generic pointer |
| Python | `Any` | `typing.Any` |
| Rust | `T`, `U` | Generic type parameters |

### Complex Combinations

**Nested Types:**
```ocaml
val find : string -> user option
val get_optional_lists : unit -> int list option
val process : (int * string) list -> string list option
```

**Python Mappings:**
```python
def find(input: str) -> Optional[User]: ...
def get_optional_lists() -> Optional[List[int]]: ...
def process(pairs: List[Tuple[int, str]]) -> Optional[List[str]]: ...
```

## Complete Type Matrix

### All Supported Types

| OCaml Type | IR Kind | C Type | Python Type | Rust Type |
|------------|---------|--------|-------------|-----------|
| **Primitives** |
| `string` | `PRIMITIVE` | `char*` | `str` | `String` |
| `int` | `PRIMITIVE` | `int` | `int` | `i64` |
| `float` | `PRIMITIVE` | `double` | `float` | `f64` |
| `bool` | `PRIMITIVE` | `int` | `bool` | `bool` |
| `unit` | `PRIMITIVE` | `void` | `None` | `()` |
| **Containers** |
| `'a option` | `OPTION` | `void*` | `Optional[T]` | `Option<T>` |
| `'a list` | `LIST` | `void*` | `List[T]` | `Vec<T>` |
| `'a * 'b` | `TUPLE` | `void*` | `Tuple[T1, T2]` | `(T1, T2)` |
| **Custom** |
| `type t = {...}` | `RECORD` | `void*` | `T` (class) | `struct T` |
| `type t = A \| B` | `VARIANT` | `void*` | `T` (class) | `enum T` |
| `'a` | `PRIMITIVE` | `void*` | `Any` | `T` |
| **Combined** |
| `int list option` | nested | `void*` | `Optional[List[int]]` | `Option<Vec<i64>>` |
| `(int * string) list` | nested | `void*` | `List[Tuple[int, str]]` | `Vec<(i64, String)>` |
