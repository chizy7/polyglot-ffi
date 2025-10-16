# Type Mapping Reference

## Phase 1 - Primitive Types

| OCaml | IR | C | Python | Notes |
|-------|-------|-------------|-----------------|-------|
| `string` | `STRING` | `char*` | `str` | UTF-8 encoded |
| `int` | `INT` | `int` | `int` | 31/63-bit on OCaml |
| `float` | `FLOAT` | `double` | `float` | IEEE 754 |
| `bool` | `BOOL` | `int` | `bool` | 0=false, 1=true |
| `unit` | `UNIT` | `void` | `None` | No value |

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

## Coming in Phase 2

### Option Types

```ocaml
val find : string -> string option
```

Maps to:
- C: Custom struct or NULL pointer
- Python: `Optional[str]`

### List Types

```ocaml
val process : int list -> int list
```

Maps to:
- C: Linked list or array
- Python: `List[int]`

### Tuple Types

```ocaml
val pair : int * string -> float
```

Maps to:
- C: Struct
- Python: `Tuple[int, str]`

### Record Types

```ocaml
type user = { name: string; age: int }
val get_user : unit -> user
```

Maps to:
- C: Struct
- Python: dataclass or dict

### Variant Types

```ocaml
type result = Ok of string | Error of string
val process : unit -> result
```

Maps to:
- C: Tagged union
- Python: Union type or class hierarchy
