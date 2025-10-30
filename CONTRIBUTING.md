# Contributing to Polyglot FFI

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/chizy7/polyglot-ffi
cd polyglot-ffi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
polyglot-ffi --version
pytest tests/ -v
```

## Development Workflow

1. **Create a branch** for your feature/fix
2. **Write tests** first (TDD recommended)
3. **Implement** your changes
4. **Run tests** to ensure they pass
5. **Format code** with black
6. **Lint code** with ruff
7. **Submit PR** with description

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_parser.py -v

# With coverage
pytest tests/ --cov=polyglot_ffi --cov-report=html

# View coverage
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
polyglot-ffi/
├── src/polyglot_ffi/   # Main package
│   ├── parsers/        # Language parsers
│   ├── ir/             # Intermediate representation
│   ├── generators/     # Code generators
│   ├── commands/       # CLI commands
│   ├── cli/            # CLI interface
│   └── utils/          # Utilities
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
└── examples/           # Example projects
```

## Adding Features

### Adding a New Type

1. Update `src/polyglot_ffi/ir/types.py`
2. Update parser in `src/polyglot_ffi/parsers/ocaml.py`
3. Update generators to handle new type
4. Add tests
5. Update documentation

### Adding a New Generator

1. Create `src/polyglot_ffi/generators/rust_gen.py`
2. Implement `generate()` method
3. Register in `__init__.py`
4. Add tests in `tests/unit/test_generators.py`
5. Update documentation

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Keep functions small and focused
- Prefer composition over inheritance

## Testing Guidelines

- **Unit tests**: Test individual components
- **Integration tests**: Test end-to-end workflows
- **Aim for 70%+ coverage**
- Use fixtures for complex test data
- Mock external dependencies

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Create PR with clear description
6. Address review feedback

## Reporting Issues

- Use GitHub Issues
- Provide minimal reproducible example
- Include version information
- Describe expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
