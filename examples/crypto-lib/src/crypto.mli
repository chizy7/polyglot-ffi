(** Cryptography library interface *)

(** Encrypt data with a key *)
val encrypt : string -> string -> string

(** Decrypt data with a key. Returns None if decryption fails. *)
val decrypt : string -> string -> string option

(** Find a stored key by name. Returns None if not found. *)
val find_key : string -> string option

(** Verify data signature. Returns None if invalid format. *)
val verify_signature : string -> string -> bool option

(** Hash data to a fixed-length string *)
val hash : string -> string
