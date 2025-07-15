# Documentation

This directory contains the documentation for xamr.

## Building the documentation

To build the documentation, you'll need to install the documentation dependencies:

```bash
pip install -e ".[dev]"
```

Then you can build the documentation:

```bash
cd docs
make html
```

## Documentation structure

- `index.rst` - Main documentation index
- `quick_start.md` - **Quick Start Guide** - comprehensive tutorial for new users
- `api.rst` - API reference
- `examples.rst` - Usage examples
- `installation.rst` - Installation instructions
- `testing.md` - Testing guide for developers

## Contributing to documentation

Documentation is written in reStructuredText format and built with Sphinx.

Please ensure that:
1. All public functions and classes are documented
2. Examples are provided for complex functionality
3. Documentation builds without errors
4. Links and references are correct
