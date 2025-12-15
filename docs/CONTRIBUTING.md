# Contributing Guide

Complete guide for contributing to the educational course Generator, including development setup, code standards, testing requirements, and contribution workflow.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Development Setup** | Python 3.10+, uv, Ollama |
| **Code Standards** | PEP 8, type hints, docstrings |
| **Testing** | pytest, no mocks, real implementations |
| **Documentation** | Google-style docstrings, update docs |
| **Workflow** | Fork, branch, test, document, submit PR |

**Read time**: 25-35 minutes | **Audience**: Contributors, developers

## Development Setup

### Prerequisites

**Required**:
- **Python**: 3.10 or higher
- **uv**: Package manager
- **Ollama**: LLM runtime (for integration tests)
- **git**: Version control

**Optional**:
- **IDE**: VS Code, PyCharm, or similar
- **Linters**: black, flake8, mypy (included in dev dependencies)

### Initial Setup

1. **Fork and clone repository**:
   ```bash
   git clone <your-fork-url>
   cd biology
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Install Ollama** (for integration tests):
   ```bash
   # Follow instructions at ollama.ai
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull gemma3:4b
   ```

4. **Validate setup**:
   ```bash
   uv run python3 scripts/01_setup_environment.py
   uv run pytest
   ```

## Code Standards

### Python Style

**Follow PEP 8**:
- 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Follow naming conventions

**Format code**:
```bash
# Format with black
uv run black src/ tests/

# Check with flake8
uv run flake8 src/ tests/
```

### Type Hints

**All public functions must have type hints**:

```python
# ✅ GOOD
def generate_content(module_info: Dict[str, Any]) -> str:
    """Generate content."""
    pass

# ❌ BAD
def generate_content(module_info):
    """Generate content."""
    pass
```

### Docstrings

**Use Google-style docstrings**:

```python
def generate_content(
    module_info: Dict[str, Any],
    session_number: int = 1
) -> str:
    """Generate content for a module.
    
    Args:
        module_info: Module information dictionary
        session_number: Current session number
        
    Returns:
        Generated content as markdown string
        
    Raises:
        LLMError: If generation fails
    """
    pass
```

### Import Organization

**Organize imports**:
```python
# Standard library
import logging
from pathlib import Path
from typing import Dict, Any

# Third-party
import yaml
import requests

# Local (modular imports)
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
```

## Testing Requirements

### Testing Philosophy

**No mocks, real implementations only**:
- Use real data and real services
- Skip tests if dependencies unavailable
- Test actual behavior, not mocked behavior

### Test Organization

**Test file structure**:
- One test file per module: `test_<module_name>.py`
- Test class per class: `TestConfigLoader`
- Test method per method: `test_load_course_config`

**Example test**:
```python
"""Tests for ConfigLoader."""

import pytest
from src.config.loader import ConfigLoader, ConfigurationError


def test_load_course_config(config_loader):
    """Test loading course configuration."""
    config = config_loader.load_course_config()
    assert 'course' in config
    assert 'name' in config['course']


def test_invalid_config_rejected():
    """Test invalid config is rejected."""
    with pytest.raises(ConfigurationError):
        ConfigLoader("invalid_path").validate_all_configs()
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_config_loader.py

# With coverage
uv run pytest --cov=src --cov-report=html

# Only unit tests (no Ollama required)
uv run pytest -m "not integration"

# Only integration tests (requires Ollama)
uv run pytest -m "integration"
```

### Test Coverage

**Aim for high coverage**:
- Test all public methods
- Test error cases
- Test edge cases
- Test integration points

**Check coverage**:
```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Documentation Requirements

### Code Documentation

**All public APIs must be documented**:
- Module docstrings
- Class docstrings
- Method docstrings
- Type hints

### Documentation Updates

**Update documentation when**:
- Adding new features
- Changing APIs
- Fixing bugs (if behavior changes)
- Adding new modules

**Documentation files to update**:
- `docs/API.md` - Public API changes
- `docs/ARCHITECTURE.md` - Architectural changes
- `docs/FORMATS.md` - Content format changes
- `docs/CONFIGURATION.md` - Configuration changes
- Module `README.md` or `AGENTS.md` - Module-specific docs

## Contribution Workflow

### Step 1: Fork and Clone

```bash
# Fork repository on GitHub
# Clone your fork
git clone <your-fork-url>
cd biology
```

### Step 2: Create Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/your-bug-description
```

### Step 3: Make Changes

1. **Write code**: Follow code standards
2. **Write tests**: Add tests for new functionality
3. **Update documentation**: Update relevant docs
4. **Run tests**: Ensure all tests pass
5. **Format code**: Run black and flake8

### Step 4: Test Changes

```bash
# Run all tests
uv run pytest

# Validate configuration
uv run python3 scripts/01_setup_environment.py

# Test your changes specifically
uv run pytest tests/test_your_module.py
```

### Step 5: Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of changes

- Detail 1
- Detail 2
- Fixes #issue-number"
```

**Commit message guidelines**:
- Use imperative mood: "Add feature" not "Added feature"
- First line: Short summary (50 chars)
- Body: Detailed description
- Reference issues: "Fixes #123"

### Step 6: Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

**Pull request guidelines**:
- Clear title and description
- Reference related issues
- List changes made
- Include test results
- Request review

## Code Review Process

### Review Criteria

**Code will be reviewed for**:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Backward compatibility

### Responding to Feedback

1. **Address comments**: Make requested changes
2. **Ask questions**: Clarify if unclear
3. **Update PR**: Push changes to same branch
4. **Mark resolved**: Mark comments as resolved

## Adding New Features

### Feature Checklist

- [ ] Code follows style guidelines
- [ ] Type hints on all public methods
- [ ] Docstrings for all public APIs
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Integration tested (if applicable)

### Feature Documentation

**Document new features in**:
- Code docstrings
- `docs/API.md` (if public API)
- `docs/ARCHITECTURE.md` (if architectural)
- Module `README.md` or `AGENTS.md`

## Fixing Bugs

### Bug Report Checklist

**Before submitting bug fix**:
- [ ] Reproduce the bug
- [ ] Identify root cause
- [ ] Write test that fails before fix
- [ ] Implement fix
- [ ] Verify test passes
- [ ] Update documentation if needed

### Bug Fix PR

**Include in PR**:
- Description of bug
- Steps to reproduce
- Root cause analysis
- Fix explanation
- Test demonstrating fix

## Adding Tests

### Test Requirements

**All new code must have tests**:
- Unit tests for functions
- Integration tests for LLM interaction
- Edge case tests
- Error case tests

### Test Patterns

**Use existing test patterns**:
- Follow structure of existing tests
- Use fixtures from `conftest.py`
- Skip integration tests if Ollama unavailable
- Use real implementations, no mocks

## Documentation Contributions

### Documentation Standards

**Follow existing documentation style**:
- Markdown format
- Clear structure
- Code examples
- Cross-references

### Documentation Locations

**Where to document**:
- **API changes**: `docs/API.md`
- **Architecture changes**: `docs/ARCHITECTURE.md`
- **Configuration changes**: `docs/CONFIGURATION.md`
- **Format changes**: `docs/FORMATS.md`
- **Module-specific**: Module `README.md` or `AGENTS.md`

## Release Process

### Version Numbering

**Follow semantic versioning**:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Release notes prepared

## Getting Help

### Questions

**Ask questions via**:
- GitHub Issues (for bugs and features)
- GitHub Discussions (for questions)
- Code review comments (for PR feedback)

### Resources

**Helpful resources**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - Public API reference
- [EXTENSION.md](EXTENSION.md) - Extension guide
- [MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md) - Module structure
- [.cursorrules/](../.cursorrules/) - Development rules

## Code of Conduct

### Expectations

**All contributors should**:
- Be respectful and inclusive
- Provide constructive feedback
- Follow code standards
- Test thoroughly
- Document changes

### Reporting Issues

**Report violations via**:
- GitHub Issues
- Direct contact with maintainers

## Related Documentation

- **[EXTENSION.md](EXTENSION.md)** - Guide for extending the system
- **[MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md)** - Module structure and organization
- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Testing guidelines
- **[.cursorrules/](../.cursorrules/)** - Development rules and standards

## Summary

Contributing involves:

1. **Setup**: Fork, clone, install dependencies
2. **Development**: Follow code standards, write tests, document
3. **Testing**: Run tests, validate changes
4. **Submission**: Commit, push, create PR
5. **Review**: Address feedback, iterate

All contributions are welcome! Follow the guidelines above to ensure smooth integration of your changes.






