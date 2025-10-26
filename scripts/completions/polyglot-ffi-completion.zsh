#compdef polyglot-ffi
# Zsh completion for polyglot-ffi
#
# Installation:
#   1. Place this file in your $fpath (e.g., /usr/local/share/zsh/site-functions/)
#   2. Or source it in your .zshrc:
#      source /path/to/polyglot-ffi-completion.zsh
#   3. Reload completions: compinit

_polyglot_ffi() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[polyglot-ffi] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _POLYGLOT_FFI_COMPLETE=zsh_complete polyglot-ffi)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _polyglot_ffi polyglot-ffi
