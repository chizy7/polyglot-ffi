#!/usr/bin/env bash
# Install shell completions for polyglot-ffi
#
# Usage: ./install-completions.sh [bash|zsh|fish|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETIONS_DIR="$SCRIPT_DIR/completions"

COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

print_success() {
    echo -e "${COLOR_GREEN}✓${COLOR_RESET} $1"
}

print_info() {
    echo -e "${COLOR_BLUE}ℹ${COLOR_RESET} $1"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠${COLOR_RESET} $1"
}

print_error() {
    echo -e "${COLOR_RED}✗${COLOR_RESET} $1"
}

install_bash() {
    print_info "Installing Bash completion..."

    local bash_completion_dir=""

    # Detect bash completion directory
    if [[ -d "/etc/bash_completion.d" ]]; then
        bash_completion_dir="/etc/bash_completion.d"
    elif [[ -d "/usr/local/etc/bash_completion.d" ]]; then
        bash_completion_dir="/usr/local/etc/bash_completion.d"
    else
        print_warning "Bash completion directory not found"
        print_info "You can source the completion script manually:"
        echo "    source $COMPLETIONS_DIR/polyglot-ffi-completion.bash"
        return 1
    fi

    # Install completion
    if [[ -w "$bash_completion_dir" ]]; then
        cp "$COMPLETIONS_DIR/polyglot-ffi-completion.bash" "$bash_completion_dir/"
        print_success "Bash completion installed to $bash_completion_dir"
    else
        sudo cp "$COMPLETIONS_DIR/polyglot-ffi-completion.bash" "$bash_completion_dir/"
        print_success "Bash completion installed to $bash_completion_dir (required sudo)"
    fi

    print_info "Reload your shell or run: source ~/.bashrc"
}

install_zsh() {
    print_info "Installing Zsh completion..."

    local zsh_completion_dir=""

    # Detect zsh completion directory
    if [[ -d "/usr/local/share/zsh/site-functions" ]]; then
        zsh_completion_dir="/usr/local/share/zsh/site-functions"
    elif [[ -d "/usr/share/zsh/site-functions" ]]; then
        zsh_completion_dir="/usr/share/zsh/site-functions"
    else
        # Use user's local directory
        zsh_completion_dir="$HOME/.zsh/completions"
        mkdir -p "$zsh_completion_dir"

        # Add to fpath if not already there
        if ! grep -qF "$zsh_completion_dir" "$HOME/.zshrc" 2>/dev/null; then
            echo "" >> "$HOME/.zshrc"
            echo "# Polyglot FFI completions" >> "$HOME/.zshrc"
            echo "fpath=(\"$zsh_completion_dir\" \$fpath)" >> "$HOME/.zshrc"
            echo "autoload -Uz compinit && compinit" >> "$HOME/.zshrc"
            print_info "Added completion directory to ~/.zshrc"
        fi
    fi

    # Install completion
    if [[ -w "$zsh_completion_dir" ]]; then
        cp "$COMPLETIONS_DIR/polyglot-ffi-completion.zsh" "$zsh_completion_dir/_polyglot-ffi"
        print_success "Zsh completion installed to $zsh_completion_dir"
    else
        sudo cp "$COMPLETIONS_DIR/polyglot-ffi-completion.zsh" "$zsh_completion_dir/_polyglot-ffi"
        print_success "Zsh completion installed to $zsh_completion_dir (required sudo)"
    fi

    print_info "Reload completions: rm -f ~/.zcompdump && exec zsh"
}

install_fish() {
    print_info "Installing Fish completion..."

    local fish_completion_dir=""

    # Detect fish completion directory
    fish_completion_dir="$HOME/.config/fish/completions"
    if [[ ! -d "$fish_completion_dir" ]]; then
        mkdir -p "$fish_completion_dir"
        print_info "Created Fish completions directory: $fish_completion_dir"
    fi

    # Install completion
    if [[ -w "$fish_completion_dir" ]]; then
        cp "$COMPLETIONS_DIR/polyglot-ffi.fish" "$fish_completion_dir/"
        print_success "Fish completion installed to $fish_completion_dir"
    else
        sudo cp "$COMPLETIONS_DIR/polyglot-ffi.fish" "$fish_completion_dir/"
        print_success "Fish completion installed to $fish_completion_dir (required sudo)"
    fi
    print_info "Completions are loaded automatically in Fish!"
}

show_usage() {
    cat << EOF
Install shell completions for polyglot-ffi

Usage:
    $0 [SHELL]

Shells:
    bash    Install Bash completion
    zsh     Install Zsh completion
    fish    Install Fish completion
    all     Install for all detected shells

Examples:
    $0 bash           # Install Bash completion only
    $0 all            # Install for all shells

If no shell is specified, installs for the current shell.
EOF
}

main() {
    local shell_type="${1:-auto}"

    echo "Polyglot FFI Shell Completion Installer"
    echo "========================================"
    echo ""

    case "$shell_type" in
        bash)
            install_bash
            ;;
        zsh)
            install_zsh
            ;;
        fish)
            install_fish
            ;;
        all)
            install_bash || true
            echo ""
            install_zsh || true
            echo ""
            install_fish || true
            ;;
        auto)
            # Detect current shell
            if [[ -n "$BASH_VERSION" ]]; then
                install_bash
            elif [[ -n "$ZSH_VERSION" ]]; then
                install_zsh
            elif [[ -n "$FISH_VERSION" ]]; then
                install_fish
            else
                print_error "Could not detect shell. Please specify: bash, zsh, or fish"
                show_usage
                exit 1
            fi
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown shell: $shell_type"
            show_usage
            exit 1
            ;;
    esac

    echo ""
    print_success "Installation complete!"
}

main "$@"
