# Example 3: Data Processing

Advanced example demonstrating list types, data transformations, and functional programming patterns.

## Overview

This example shows:
- List types (`'a list`)
- Functional transformations (map, filter, fold)
- Complex list operations
- Real-world data processing

## OCaml Interface

**File: `src/data.mli`**

```ocaml
(** Filter list of strings by length *)
val filter_by_length : int -> string list -> string list

(** Map strings to their lengths *)
val map_lengths : string list -> int list

(** Find maximum in integer list. Returns None if empty. *)
val find_max : int list -> int option

(** Sum all integers in a list *)
val sum : int list -> int

(** Count occurrences of a value *)
val count : string -> string list -> int

(** Remove duplicates from list *)
val unique : string list -> string list

(** Sort strings alphabetically *)
val sort_strings : string list -> string list
```

## Python Usage

**File: `example.py`**

```python
from data_py import (
    filter_by_length, map_lengths, find_max, sum,
    count, unique, sort_strings
)

# Example 1: Filter by length
words = ["cat", "elephant", "dog", "butterfly"]
long_words = filter_by_length(5, words)
print(f"Words >= 5 chars: {long_words}")
# Output: ['elephant', 'butterfly']

# Example 2: Map to lengths
lengths = map_lengths(words)
print(f"Lengths: {lengths}")
# Output: [3, 8, 3, 9]

# Example 3: Find maximum
max_length = find_max(lengths)
if max_length:
    print(f"Max length: {max_length}")
# Output: Max length: 9

# Empty list returns None
empty_max = find_max([])
print(f"Max of empty: {empty_max}")  # None

# Example 4: Sum
total = sum(lengths)
print(f"Total: {total}")  # 23

# Example 5: Count occurrences
names = ["Alice", "Bob", "Alice", "Charlie", "Alice"]
alice_count = count("Alice", names)
print(f"Alice appears {alice_count} times")  # 3

# Example 6: Remove duplicates
unique_names = unique(names)
print(f"Unique: {unique_names}")
# Output: ['Alice', 'Bob', 'Charlie']

# Example 7: Sort
sorted_names = sort_strings(names)
print(f"Sorted: {sorted_names}")
# Output: ['Alice', 'Alice', 'Alice', 'Bob', 'Charlie']

# Real-world pipeline
def process_log_file(lines: list[str]) -> dict:
    """Process log lines and return statistics."""
    # Filter non-empty lines
    non_empty = filter_by_length(1, lines)

    # Get line lengths
    lengths = map_lengths(non_empty)

    # Calculate statistics
    return {
        "total_lines": len(non_empty),
        "total_chars": sum(lengths),
        "max_length": find_max(lengths) or 0,
        "unique_lines": len(unique(non_empty))
    }

# Use it
log_lines = [
    "2025-01-22 INFO: Server started",
    "2025-01-22 INFO: Server started",  # duplicate
    "2025-01-22 ERROR: Connection failed",
    "",  # empty line
    "2025-01-22 INFO: Request processed"
]

stats = process_log_file(log_lines)
print(f"Log statistics: {stats}")
```

## Key Learnings

### 1. List Type Mapping

**OCaml**: `string list`
**Python**: `List[str]`
**C**: `char**` (array of strings)

### 2. Memory Management

Lists are automatically managed:
- OCaml handles memory on its side
- Python receives copied data
- No manual memory management needed

### 3. Empty Lists

```python
# Empty lists are valid
result = filter_by_length(10, [])  # Returns []
total = sum([])  # Returns 0
max_val = find_max([])  # Returns None (option type!)
```

### 4. Type Safety

```python
from typing import List, Optional

def process(items: List[str]) -> Optional[int]:
    lengths = map_lengths(items)
    return find_max(lengths)
```

## Running

```bash
polyglot-ffi generate src/data.mli --output generated --name data
make build
python example.py
```

## Next Examples

- **Records**: [web-api](../web-api/) - Structured data
- **Tuples**: [ml-pipeline](../ml-pipeline/) - Multiple return values
