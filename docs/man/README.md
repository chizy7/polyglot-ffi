# Polyglot FFI Man Pages

This directory contains manual pages for the polyglot-ffi tool.

## Available Man Pages

### Section 1: User Commands

- **polyglot-ffi(1)** - Main command overview
- **polyglot-ffi-init(1)** - Initialize new projects
- **polyglot-ffi-generate(1)** - Generate FFI bindings
- **polyglot-ffi-check(1)** - Validate configuration and dependencies
- **polyglot-ffi-clean(1)** - Remove generated files
- **polyglot-ffi-watch(1)** - Watch mode for auto-regeneration

### Section 5: File Formats

- **polyglot-ffi-config(5)** - Configuration file format (polyglot.toml)

## Installation

### System-wide Installation

To install man pages system-wide (requires sudo):

```bash
# Copy man pages to system location
sudo cp docs/man/*.1 /usr/local/share/man/man1/
sudo cp docs/man/*.5 /usr/local/share/man/man5/

# Update man database
sudo mandb  # Linux
sudo /usr/libexec/makewhatis /usr/local/share/man  # macOS
```

### User Installation

To install for current user only:

```bash
# Create user man directory
mkdir -p ~/.local/share/man/man1
mkdir -p ~/.local/share/man/man5

# Copy man pages
cp docs/man/*.1 ~/.local/share/man/man1/
cp docs/man/*.5 ~/.local/share/man/man5/

# Add to MANPATH (add to ~/.bashrc or ~/.zshrc)
export MANPATH="$HOME/.local/share/man:$MANPATH"
```

### Development/Local Use

View man pages directly without installation:

```bash
# View a specific man page
man docs/man/polyglot-ffi.1

# Or use less
less docs/man/polyglot-ffi.1
```

## Usage

After installation, access man pages with:

```bash
# Main overview
man polyglot-ffi

# Specific commands
man polyglot-ffi-init
man polyglot-ffi-generate
man polyglot-ffi-check
man polyglot-ffi-clean
man polyglot-ffi-watch

# Configuration format
man polyglot-ffi-config
man 5 polyglot-ffi-config  # Explicit section 5
```

## Viewing Man Pages

### Plain Text
```bash
man polyglot-ffi | col -b > polyglot-ffi.txt
```

### HTML
```bash
man -H polyglot-ffi  # Opens in browser (if configured)

# Or use groff
groff -mandoc -Thtml docs/man/polyglot-ffi.1 > polyglot-ffi.html
```

### PDF
```bash
groff -mandoc -Tpdf docs/man/polyglot-ffi.1 > polyglot-ffi.pdf
```

## Format

Man pages are written in **troff/groff** format using the **man** macro package.

### Common Formatting

- `.TH` - Title header
- `.SH` - Section header
- `.TP` - Tagged paragraph
- `.B` - Bold text
- `.I` - Italic text
- `.EX/.EE` - Example blocks

## Contributing

When adding or modifying man pages:

1. Follow existing structure and formatting
2. Use consistent terminology
3. Include practical examples
4. Test rendering: `man ./docs/man/yourpage.1`
5. Validate with: `groff -man -z docs/man/yourpage.1`

## Resources

- [Man Page Guide](https://www.kernel.org/doc/man-pages/)
- [Groff Manual](https://www.gnu.org/software/groff/manual/)
- [Man Page Best Practices](https://www.man7.org/linux/man-pages/man7/man-pages.7.html)

## License

Man pages are part of the Polyglot FFI project and are licensed under the MIT License.
