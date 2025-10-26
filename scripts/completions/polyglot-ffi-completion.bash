#!/usr/bin/env bash
# Bash completion for polyglot-ffi
#
# Installation:
#   1. Source this file in your .bashrc or .bash_profile:
#      source /path/to/polyglot-ffi-completion.bash
#
#   2. Or copy to bash completion directory:
#      sudo cp polyglot-ffi-completion.bash /etc/bash_completion.d/

_polyglot_ffi_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _POLYGLOT_FFI_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_polyglot_ffi_completion_setup() {
    complete -o nosort -F _polyglot_ffi_completion polyglot-ffi
}

_polyglot_ffi_completion_setup
