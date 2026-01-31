# Documentation Guide

This guide explains how to build, test, and deploy the Polyglot FFI documentation.

## Overview

Our documentation is built with:
- **MkDocs** - Static site generator
- **Material Theme** - Modern, responsive design
- **mkdocstrings** - Auto-generate API docs from Python docstrings
- **GitHub Pages** - Hosting platform

**Live Documentation:** https://polyglotffi.com/

---

## Quick Start

### Install Dependencies

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Or install all dev dependencies
pip install -e ".[dev]"
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Build Documentation

```bash
# Build documentation
mkdocs build

# Output: site/ directory with HTML files
```

### Serve Locally

```bash
# Start local server with live reload
mkdocs serve

# Open in browser: http://127.0.0.1:8000
```

---

## Documentation Structure

```
docs/
├── index.md                    # Homepage
├── quickstart.md              # Quick start guide
├── installation.md            # Installation instructions
├── configuration.md           # Configuration reference
├── quick_reference.md         # CLI quick reference
├── architecture.md            # Architecture overview
├── type-mapping.md            # Type system guide
├── contributing.md            # Contributing guidelines
├── faq.md                     # Frequently asked questions
├── CHANGELOG.md → ../         # Symlink to root
├── SECURITY.md → ../          # Symlink to root
├── CODE_OF_CONDUCT.md → ../   # Symlink to root
├── LICENSE.md → ../LICENSE    # Symlink to root
└── api/                       # API reference (auto-generated)
    ├── index.md
    ├── parser.md
    ├── generators.md
    ├── type-system.md
    ├── ir-types.md
    └── config.md

mkdocs.yml                     # MkDocs configuration
```

### File Purposes

| File | Purpose |
|------|---------|
| `index.md` | Homepage with project overview |
| `installation.md` | Detailed installation instructions |
| `quickstart.md` | 5-minute getting started guide |
| `configuration.md` | Configuration file reference |
| `architecture.md` | System architecture and design |
| `type-mapping.md` | Type system mappings |
| `contributing.md` | Contribution guidelines |
| `faq.md` | Common questions and answers |
| `api/*.md` | Python API documentation |

---

## Building Documentation

### Standard Build

```bash
# Build documentation
mkdocs build

# Output location
ls site/

# Check for errors
echo $?  # Should be 0
```

### Strict Mode

Build with warnings treated as errors:

```bash
# Fail on any warnings
mkdocs build --strict

# Useful for CI/CD
```

### Clean Build

```bash
# Remove old build
rm -rf site/

# Clean build
mkdocs build --clean
```

---

## Serving Documentation

### Local Development

```bash
# Start development server
mkdocs serve

# Custom port
mkdocs serve -a 127.0.0.1:8080

# Custom address (allow remote access)
mkdocs serve -a 0.0.0.0:8000
```

**Features:**
- Live reload on file changes
- Automatic browser refresh
- Fast rebuild times
- Error messages in terminal

### Testing Changes

1. **Start server:**
   ```bash
   mkdocs serve
   ```

2. **Open browser:**
   ```
   http://127.0.0.1:8000
   ```

3. **Edit docs:**
   ```bash
   vim docs/index.md
   ```

4. **See changes immediately** - browser auto-refreshes!

---

## Configuration

### mkdocs.yml

Main configuration file:

```yaml
site_name: Polyglot FFI Documentation
site_url: https://polyglotffi.com/
repo_url: https://github.com/chizy7/polyglot-ffi

theme:
  name: material
  palette:
    - scheme: default      # Light mode
    - scheme: slate        # Dark mode
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - content.code.copy

plugins:
  - search
  - mkdocstrings

nav:
  - Home: index.md
  - Getting Started: ...
  - API Reference: ...
```

### Theme Customization

Edit `mkdocs.yml` to customize:

```yaml
theme:
  name: material
  palette:
    primary: indigo      # Primary color
    accent: indigo       # Accent color
  font:
    text: Roboto        # Body font
    code: Roboto Mono   # Code font
  logo: assets/logo.png # Custom logo
  favicon: assets/favicon.ico
```

---

## API Documentation

### Auto-Generated API Docs

We use `mkdocstrings` to generate API docs from Python docstrings:

```markdown
<!-- In docs/api/parser.md -->

::: polyglot_ffi.parsers.ocaml.parse_mli_file
    options:
      show_source: true
      show_root_heading: true
```

### Writing Docstrings

**Good docstring example:**

```python
def parse_mli_file(file_path: Path) -> IRModule:
    """
    Parse an OCaml interface file (.mli) into an IR module.

    Args:
        file_path: Path to the .mli file to parse

    Returns:
        IRModule: Parsed module containing functions and types

    Raises:
        FileNotFoundError: If the file doesn't exist
        ParseError: If the file has syntax errors

    Example:
        ```python
        from pathlib import Path
        from polyglot_ffi.parsers import parse_mli_file

        module = parse_mli_file(Path("crypto.mli"))
        print(f"Found {len(module.functions)} functions")
        ```
    """
    ...
```

### Updating API Docs

API docs are **auto-generated** from code:

1. **Update Python docstrings** in source code
2. **Rebuild docs:** `mkdocs build`
3. **API docs update automatically!**

No need to manually edit `docs/api/*.md` files for docstring changes.

---

## Testing Documentation

### Check for Broken Links

```bash
# Build first
mkdocs build

# Install link checker
pip install linkchecker

# Check for broken links
linkchecker site/

# Or specific page
linkchecker site/index.html
```

### Validate Markdown

```bash
# Install markdown linter
npm install -g markdownlint-cli

# Check markdown files
markdownlint docs/**/*.md

# Fix automatically
markdownlint --fix docs/**/*.md
```

### Spell Check

```bash
# Install spell checker
pip install pyspelling

# Create .pyspelling.yml config
# Run spell check
pyspelling
```

### Test Locally Before Push

**Checklist:**

```bash
# 1. Clean build
rm -rf site/
mkdocs build --strict

# 2. Check for errors
echo $?  # Should be 0

# 3. Serve locally
mkdocs serve

# 4. Test in browser
# - Navigation works
# - Search works
# - Code highlighting works
# - Links work

# 5. Check specific pages
# - Homepage
# - Installation
# - API docs
# - FAQ

# 6. Test responsiveness
# - Desktop view
# - Mobile view (browser dev tools)
```

---

## Deployment

### Automatic Deployment (GitHub Actions)

Documentation is **automatically deployed** when you push to `master`:

```yaml
# .github/workflows/docs.yml
- Push to master with doc changes
  ↓
- Cloudflare Pages triggers build
  ↓
- mkdocs build
  ↓
- Published to Cloudflare Pages!
```

**URL:** https://polyglotffi.com/

### Deployment

Documentation is automatically deployed to [Cloudflare Pages](https://pages.cloudflare.com/) when changes are pushed to the `master` branch.

**To test locally before pushing:**

```bash
# Build documentation
mkdocs build

# Preview locally
mkdocs serve
```

**What happens on push:**
1. Cloudflare Pages detects the push to `master`
2. Runs `pip install mkdocs mkdocs-material mkdocstrings[python] && mkdocs build`
3. Deploys the `site/` directory to `polyglotffi.com`

### Deployment with Versioning

For versioned docs (on releases):

```bash
# Install mike (version manager)
pip install mike

# Deploy version 0.4.0 as 'latest'
mike deploy 0.4.0 latest

# Set default version
mike set-default latest

# Deploy and push
mike deploy 0.4.0 latest --push
```

**Result:**
- `/latest/` → points to 0.4.0
- `/0.4.0/` → version 0.4.0
- `/0.3.0/` → version 0.3.0 (previous)

---

## Common Tasks

### Add a New Page

1. **Create markdown file:**
   ```bash
   vim docs/new-page.md
   ```

2. **Add to navigation:**
   ```yaml
   # mkdocs.yml
   nav:
     - Home: index.md
     - New Page: new-page.md  # Add here
   ```

3. **Build and test:**
   ```bash
   mkdocs serve
   ```

### Add Images

1. **Create assets directory:**
   ```bash
   mkdir -p docs/assets/images
   ```

2. **Add image:**
   ```bash
   cp screenshot.png docs/assets/images/
   ```

3. **Reference in markdown:**
   ```markdown
   ![Screenshot](assets/images/screenshot.png)
   ```

### Add Code Examples

````markdown
```python
# Python code
from polyglot_ffi import parse_mli_file

module = parse_mli_file("api.mli")
```

```ocaml
(* OCaml code *)
val greet : string -> string
```
````

### Add Admonitions

```markdown
!!! note
    This is a note

!!! warning
    This is a warning

!!! tip
    This is a helpful tip

!!! danger
    This is dangerous!
```

---

## Troubleshooting

### Build Fails

**Error:** `Module 'polyglot_ffi' not found`

**Solution:**
```bash
# Install package in editable mode
pip install -e .

# Then build
mkdocs build
```

### Links Not Working

**Error:** `WARNING - Doc file contains broken link`

**Solution:**
```bash
# Check the link path
# Relative to current file:
[Link](../other-page.md)

# Or absolute from docs/:
[Link](/installation.md)
```

### Theme Not Loading

**Error:** `Theme 'material' not found`

**Solution:**
```bash
# Install theme
pip install mkdocs-material

# Verify installation
pip show mkdocs-material
```

### Search Not Working

**Error:** Search returns no results

**Solution:**
```bash
# Make sure search plugin is enabled
# in mkdocs.yml:
plugins:
  - search

# Rebuild
mkdocs build --clean
```

### Slow Build Times

**Solution:**
```bash
# Use serve mode (faster rebuilds)
mkdocs serve

# Or disable plugins temporarily
# Comment out in mkdocs.yml:
plugins:
  - search
  # - mkdocstrings  # Disable for speed
```

---

## Best Practices

### Writing Good Documentation

1. **Be Clear and Concise**
   - Short sentences
   - Active voice
   - Simple language

2. **Use Examples**
   - Code snippets
   - Real-world scenarios
   - Before/after comparisons

3. **Structure Well**
   - Use headings (##, ###)
   - Short paragraphs
   - Lists and tables

4. **Test Your Examples**
   - All code should work
   - Copy-pasteable
   - Up-to-date

### Markdown Style

```markdown
# Use ATX-style headings
## Not underlines
---

Use **bold** for emphasis, not *italics* for UI elements

Use `code` for:
- Commands: `polyglot-ffi init`
- File names: `config.toml`
- Code: `def foo():`

Use fenced code blocks:
````python
def example():
    pass
````
```

### Documentation Workflow

1. **Plan:** What needs documenting?
2. **Write:** Create/update markdown files
3. **Review:** Read through as a user
4. **Test:** `mkdocs serve` and check
5. **Build:** `mkdocs build --strict`
6. **Commit:** Git commit with clear message
7. **Push:** Automatic deployment!

---

## Resources

### MkDocs

- **Documentation:** https://www.mkdocs.org/
- **Material Theme:** https://squidfunk.github.io/mkdocs-material/
- **Plugins:** https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins

### Writing

- **Markdown Guide:** https://www.markdownguide.org/
- **Style Guide:** https://google.github.io/styleguide/docguide/style.html
- **API Docs Guide:** https://www.divio.com/blog/documentation/

### Tools

- **Link Checker:** https://linkchecker.github.io/linkchecker/
- **Spell Checker:** https://facelessuser.github.io/pyspelling/
- **Markdown Linter:** https://github.com/DavidAnson/markdownlint

---

## Getting Help

- **MkDocs Issues:** https://github.com/mkdocs/mkdocs/issues
- **Material Theme:** https://github.com/squidfunk/mkdocs-material/discussions
- **Our Issues:** https://github.com/chizy7/polyglot-ffi/issues

---

## Quick Reference

```bash
# Development
mkdocs serve              # Live preview
mkdocs build              # Build site
mkdocs build --strict     # Strict build (fail on warnings)

# Deployment (automatic via Cloudflare Pages on push to master)
git push origin master    # Triggers Cloudflare Pages deploy
mike deploy VERSION       # Deploy versioned docs

# Maintenance
rm -rf site/              # Clean build
mkdocs build --clean      # Clean + build

# Testing
linkchecker site/         # Check for broken links
markdownlint docs/        # Lint markdown files
```

---

**Last Updated:** October 2025
