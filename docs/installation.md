# Installation

This guide covers installing Polyglot FFI and its dependencies.

## Quick Install

### From PyPI (Recommended)

```bash
pip install polyglot-ffi
```

### From Source

```bash
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi
pip install -e ".[dev]"
```

## Requirements

### Python

- **Python 3.8 or higher**
- pip (Python package manager)

Check your Python version:

```bash
python --version
# or
python3 --version
```

### OCaml (For Building Examples)

If you want to build and run the generated bindings:

- **OCaml 4.14 or higher**
- **Dune 3.0 or higher** (build system)
- **ocaml-ctypes** library

#### Install OCaml on macOS

```bash
# Using Homebrew
brew install opam
opam init
opam switch create 4.14.1
eval $(opam env)

# Install dependencies
opam install dune ctypes ctypes-foreign
```

#### Install OCaml on Linux

```bash
# Ubuntu/Debian
sudo apt-get install opam
opam init
opam switch create 4.14.1
eval $(opam env)

# Install dependencies
opam install dune ctypes ctypes-foreign
```

#### Install OCaml on Windows

```bash
# Using WSL2 (recommended)
# Follow Linux instructions above

# Or using OCaml for Windows
# Download from: https://ocaml.org/docs/install.html
```

## Installation Methods

### Method 1: User Install (Recommended)

Install for current user only:

```bash
pip install --user polyglot-ffi
```

The command will be available at:
- Linux/macOS: `~/.local/bin/polyglot-ffi`
- Windows: `%APPDATA%\Python\Scripts\polyglot-ffi.exe`

Make sure this directory is in your PATH.

### Method 2: Virtual Environment

Create isolated environment:

```bash
# Create virtual environment
python -m venv polyglot-env

# Activate it
source polyglot-env/bin/activate  # Linux/macOS
# or
polyglot-env\Scripts\activate     # Windows

# Install
pip install polyglot-ffi
```

### Method 3: System-Wide Install

Requires sudo/admin privileges:

```bash
sudo pip install polyglot-ffi  # Linux/macOS
# or
pip install polyglot-ffi       # Windows (run as Administrator)
```

### Method 4: Development Install

For contributing or testing:

```bash
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi
pip install -e ".[dev]"
```

This installs in "editable" mode with development dependencies.

## Verify Installation

### Check Version

```bash
polyglot-ffi --version
# Output: polyglot-ffi, version 0.5.1
```

### Check Help

```bash
polyglot-ffi --help
```

### Run Quick Test

```bash
# Initialize a test project
polyglot-ffi init test-project
cd test-project

# Generate bindings
polyglot-ffi generate
```

## Shell Completion (Optional)

Install shell completion for better CLI experience:

### Bash

```bash
# Install completion script
_POLYGLOT_FFI_COMPLETE=bash_source polyglot-ffi > ~/.polyglot-ffi-complete.bash

# Add to ~/.bashrc
echo 'source ~/.polyglot-ffi-complete.bash' >> ~/.bashrc
source ~/.bashrc
```

### Zsh

```bash
# Install completion script
_POLYGLOT_FFI_COMPLETE=zsh_source polyglot-ffi > ~/.polyglot-ffi-complete.zsh

# Add to ~/.zshrc
echo 'source ~/.polyglot-ffi-complete.zsh' >> ~/.zshrc
source ~/.zshrc
```

### Fish

```bash
# Install completion script
_POLYGLOT_FFI_COMPLETE=fish_source polyglot-ffi > ~/.config/fish/completions/polyglot-ffi.fish
```

## Upgrading

### Upgrade to Latest Version

To upgrade to the latest version from PyPI:

```bash
pip install --upgrade polyglot-ffi
```

### Upgrade to Specific Version

To upgrade to a specific version:

```bash
pip install --upgrade polyglot-ffi==0.5.1
```

### Check Current Version

Before upgrading, check what version you have:

```bash
polyglot-ffi --version
```

### Check Available Versions

To see all available versions on PyPI:

```bash
pip index versions polyglot-ffi
```

### Upgrade from Source

If you installed from source (development mode):

```bash
cd polyglot-ffi
git pull origin master
pip install -e ".[dev]"
```

### Force Reinstall

If you encounter issues during upgrade:

```bash
pip install --upgrade --force-reinstall polyglot-ffi
```

### Upgrade in Virtual Environment

If you're using a virtual environment:

```bash
# Activate your environment first
source env/bin/activate  # Linux/macOS
# or
env\Scripts\activate     # Windows

# Then upgrade
pip install --upgrade polyglot-ffi
```

### What's New

After upgrading, check what changed:

- **View Changelog**: https://github.com/chizy7/polyglot-ffi/blob/master/CHANGELOG.md
- **Release Notes**: https://github.com/chizy7/polyglot-ffi/releases

### Breaking Changes

When upgrading between major versions (e.g., v0.x to v1.x), review the changelog for breaking changes and migration guides.

## Uninstallation

```bash
pip uninstall polyglot-ffi
```

## Troubleshooting

### Command Not Found

**Issue:** `polyglot-ffi: command not found`

**Solution:**
```bash
# Check if installed
pip show polyglot-ffi

# Find installation location
python -m polyglot_ffi --version

# Add to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"  # Linux/macOS
```

### Import Error

**Issue:** `ModuleNotFoundError: No module named 'polyglot_ffi'`

**Solution:**
```bash
# Reinstall
pip uninstall polyglot-ffi
pip install polyglot-ffi

# Or install in current Python environment
python -m pip install polyglot-ffi
```

### Permission Denied

**Issue:** Permission errors during installation

**Solution:**
```bash
# Use --user flag
pip install --user polyglot-ffi

# Or use virtual environment
python -m venv env
source env/bin/activate
pip install polyglot-ffi
```

### OCaml Not Found

**Issue:** OCaml commands not available after installation

**Solution:**
```bash
# Run opam environment setup
eval $(opam env)

# Add to shell rc file permanently
echo 'eval $(opam env)' >> ~/.bashrc  # or ~/.zshrc
```

### Version Mismatch

**Issue:** Old version showing after upgrade

**Solution:**
```bash
# Clear pip cache
pip cache purge

# Force reinstall
pip install --force-reinstall polyglot-ffi

# Or uninstall first
pip uninstall polyglot-ffi
pip install polyglot-ffi
```

## Platform-Specific Notes

### macOS

- Use Homebrew for OCaml: `brew install opam`
- May need Command Line Tools: `xcode-select --install`

### Linux

- Ubuntu/Debian: `apt-get install opam`
- Fedora/RHEL: `dnf install opam`
- Arch: `pacman -S opam`

### Windows

- Use WSL2 for best experience
- Or install OCaml for Windows from official site
- PowerShell may require execution policy: `Set-ExecutionPolicy RemoteSigned`

## Next Steps

After installation:

1. [Quick Start Guide](quickstart.md) - Get started in 5 minutes
2. [Configuration](configuration.md) - Set up your project
3. [CLI Commands](quick_reference.md) - Learn available commands

## Getting Help

- **Documentation:** https://polyglotffi.com/
- **Issues:** https://github.com/chizy7/polyglot-ffi/issues
- **Discussions:** https://github.com/chizy7/polyglot-ffi/discussions
