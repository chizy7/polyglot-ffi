(** Data processing functions *)

(** Filter list of strings by minimum length *)
val filter_by_length : int -> string list -> string list

(** Map strings to their lengths *)
val map_lengths : string list -> int list

(** Find maximum in integer list. Returns None if empty. *)
val find_max : int list -> int option

(** Sum all integers in a list *)
val sum : int list -> int

(** Count occurrences of a value in a list *)
val count : string -> string list -> int

(** Remove duplicates from list *)
val unique : string list -> string list

(** Sort strings alphabetically *)
val sort_strings : string list -> string list
