# Fish completion for polyglot-ffi
#
# Installation:
#   1. Copy to fish completions directory:
#      cp polyglot-ffi.fish ~/.config/fish/completions/
#   2. Or for system-wide installation:
#      sudo cp polyglot-ffi.fish /usr/share/fish/vendor_completions.d/

function __fish_polyglot_ffi_complete
    set -lx COMP_WORDS (commandline -opc) (commandline -ct)
    set -lx COMP_CWORD (math (count $COMP_WORDS) - 1)
    set -lx _POLYGLOT_FFI_COMPLETE fish_complete
    polyglot-ffi
end

complete -c polyglot-ffi -f -a '(__fish_polyglot_ffi_complete)'

# Command completions
complete -c polyglot-ffi -n '__fish_use_subcommand' -a 'init' -d 'Initialize a new project'
complete -c polyglot-ffi -n '__fish_use_subcommand' -a 'generate' -d 'Generate FFI bindings'
complete -c polyglot-ffi -n '__fish_use_subcommand' -a 'check' -d 'Validate configuration'
complete -c polyglot-ffi -n '__fish_use_subcommand' -a 'clean' -d 'Remove generated files'
complete -c polyglot-ffi -n '__fish_use_subcommand' -a 'watch' -d 'Watch and auto-regenerate'

# Global options
complete -c polyglot-ffi -s v -l verbose -d 'Enable verbose output'
complete -c polyglot-ffi -l version -d 'Show version'
complete -c polyglot-ffi -l help -d 'Show help message'

# Init command options
complete -c polyglot-ffi -n '__fish_seen_subcommand_from init' -l lang -d 'Target language' -a 'python rust go'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from init' -l template -d 'Project template' -a 'library cli'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from init' -l interactive -d 'Interactive setup'

# Generate command options
complete -c polyglot-ffi -n '__fish_seen_subcommand_from generate' -s o -l output -d 'Output directory' -r -F
complete -c polyglot-ffi -n '__fish_seen_subcommand_from generate' -s n -l name -d 'Module name'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from generate' -l dry-run -d 'Show what would be generated'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from generate' -s f -l force -d 'Overwrite existing files'

# Check command options
complete -c polyglot-ffi -n '__fish_seen_subcommand_from check' -l deps -d 'Check dependencies'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from check' -l lang -d 'Specific language' -a 'ocaml python rust'

# Clean command options
complete -c polyglot-ffi -n '__fish_seen_subcommand_from clean' -l all -d 'Remove all generated files'
complete -c polyglot-ffi -n '__fish_seen_subcommand_from clean' -l dry-run -d 'Show what would be removed'

# Watch command options
complete -c polyglot-ffi -n '__fish_seen_subcommand_from watch' -l build -d 'Run build after regeneration'

# File completions for .mli files
complete -c polyglot-ffi -n '__fish_seen_subcommand_from generate' -a '(__fish_complete_suffix .mli)' -d 'OCaml interface file'
