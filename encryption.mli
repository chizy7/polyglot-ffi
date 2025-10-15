(* encryption.mli - Example OCaml interface file *)

val encrypt : string -> string
(** Encrypt a string using our custom algorithm *)

val decrypt : string -> string
(** Decrypt a string using our custom algorithm *)

val hash : string -> string
(** Generate a hash of the input string *)

val validate : string -> string -> bool
(** Validate that an encrypted string matches the original *)