# Shell Completions for Polyglot FFI

Tab completion support for polyglot-ffi commands in Bash, Zsh, and Fish shells.

## Installation

### Bash

1. **Using the completion script:**
   ```bash
   # Add to ~/.bashrc or ~/.bash_profile
   source /path/to/polyglot-ffi/scripts/completions/polyglot-ffi-completion.bash
   ```

2. **System-wide installation:**
   ```bash
   sudo cp scripts/completions/polyglot-ffi-completion.bash /etc/bash_completion.d/
   ```

3. **Reload your shell:**
   ```bash
   source ~/.bashrc
   ```

### Zsh

1. **Using the completion script:**
   ```zsh
   # Add to ~/.zshrc
   fpath=(/path/to/polyglot-ffi/scripts/completions $fpath)
   autoload -Uz compinit && compinit
   ```

2. **System-wide installation:**
   ```zsh
   sudo cp scripts/completions/polyglot-ffi-completion.zsh /usr/local/share/zsh/site-functions/_polyglot-ffi
   ```

3. **Reload completions:**
   ```zsh
   rm -f ~/.zcompdump && compinit
   ```

### Fish

1. **User installation:**
   ```fish
   cp scripts/completions/polyglot-ffi.fish ~/.config/fish/completions/
   ```

2. **System-wide installation:**
   ```fish
   sudo cp scripts/completions/polyglot-ffi.fish /usr/share/fish/vendor_completions.d/
   ```

3. **Completions are loaded automatically in Fish!**

## Features

The completion scripts provide:

- **Command completion**: Auto-complete polyglot-ffi subcommands (init, generate, check, clean, watch)
- **Option completion**: Tab-complete command options (--lang, --output, --dry-run, etc.)
- **File completion**: Smart completion for .mli files when using generate command
- **Language completion**: Auto-complete target languages (python, rust, go)
- **Help text**: Show descriptions for commands and options (Fish and Zsh)

## Usage Examples

```bash
# Type and press TAB to see all commands
polyglot-ffi <TAB>

# Auto-complete init command with options
polyglot-ffi init --l<TAB>  # Completes to --lang

# Complete language names
polyglot-ffi init mylib --lang <TAB>  # Shows: python rust go

# File completion for generate command
polyglot-ffi generate src/<TAB>  # Shows .mli files in src/

# Check completion with options
polyglot-ffi check --<TAB>  # Shows available flags
```

## Troubleshooting

### Bash

- **Completions not working?**
  - Ensure bash-completion is installed: `apt-get install bash-completion` (Debian/Ubuntu) or `brew install bash-completion@2` (macOS)
  - Check if the completion script is sourced: `type _polyglot_ffi_completion`

### Zsh

- **Completions not loading?**
  - Verify fpath includes the completion directory: `echo $fpath`
  - Rebuild completion cache: `rm ~/.zcompdump* && compinit`
  - Check if completion function exists: `which _polyglot-ffi`

### Fish

- **Completions not appearing?**
  - Fish loads completions automatically from `~/.config/fish/completions/`
  - Verify the file is in the right location: `ls ~/.config/fish/completions/polyglot-ffi.fish`
  - Reload completions: `fish_update_completions`

## Development

To generate completions directly from Click (for advanced users):

```bash
# Bash
_POLYGLOT_FFI_COMPLETE=bash_source polyglot-ffi > polyglot-ffi-completion.bash

# Zsh
_POLYGLOT_FFI_COMPLETE=zsh_source polyglot-ffi > polyglot-ffi-completion.zsh

# Fish
_POLYGLOT_FFI_COMPLETE=fish_source polyglot-ffi > polyglot-ffi.fish
```

## Contributing

If you add new commands or options to polyglot-ffi, please update the completion scripts accordingly, especially the Fish completion which includes manual command definitions.
