# Contributing to Newport 8742 Picomotor Controller

Thank you for your interest in contributing! This document provides guidelines
for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Controller model/firmware if relevant

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case and benefits
3. Discuss implementation approach if you have ideas

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following the coding standards below
4. Test your changes
5. Commit with clear messages: `git commit -m "Add: description"`
6. Push and create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/newport-8742-picomotor.git
cd newport-8742-picomotor

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e ".[dev]"
```

## Coding Standards

### Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting: `black src/`
- Maximum line length: 100 characters

### Type Hints

- Add type hints to all public functions
- Use `typing` module for complex types

```python
def move_to_target(self, motor_id: int, target: int) -> None:
    """Move motor to absolute position."""
    ...
```

### Docstrings

- Use Google-style docstrings
- Document all public classes and methods

```python
def get_position(self, motor_id: int) -> int:
    """Get current position of a motor.
    
    Args:
        motor_id: Motor channel (1-4)
        
    Returns:
        Current position in encoder steps
        
    Raises:
        ValueError: If motor_id not in range 1-4
    """
```

### SPDX Headers

Add license header to all Python files:

```python
# SPDX-License-Identifier: MIT
"""Module description."""
```

## Commit Messages

Use conventional commit format:

- `Add:` New feature
- `Fix:` Bug fix
- `Docs:` Documentation only
- `Refactor:` Code change that doesn't add features or fix bugs
- `Test:` Adding or updating tests
- `Chore:` Maintenance tasks

## Testing

Before submitting:

1. Test with actual hardware if possible
2. Run the GUI to verify functionality
3. Check that `--list` discovery works

```bash
# Run discovery test
python -m picomotor.gui --list

# Run GUI (requires hardware)
python -m picomotor.gui
```

## Questions?

Open an issue with the "question" label.

---

Thank you for contributing! 🎉
