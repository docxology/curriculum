# Project Philosophy and Quick Reference

## Core Principles

The educational course Generator follows these fundamental principles:

1. **No Mock Methods** - All code uses real implementations. Tests interact with actual services.
2. **Use uv** - All package management and script execution uses `uv` (not pip/venv).
3. **Configuration-Driven** - Course structure, LLM settings, and output formats are in YAML files under `config/`.
4. **TDD Approach** - Write tests before or alongside implementation.
5. **Text-Based** - All content in markdown/YAML for git-friendly version control.
6. **Modular Architecture** - Each component has a single, well-defined responsibility.
7. **Logging-First** - Comprehensive logging throughout (no print() statements).
8. **Safe-to-Fail** - Errors collected, processing continues, comprehensive reporting.

## Quick Reference

### Package Management
- **HARD**: Use `uv` for all package operations
- **HARD**: Never use `pip` or `venv`
- See: [01-uv-environment.md](01-uv-environment.md)

### Code Organization
- **HARD**: Follow modular folder structure (`src/config/`, `src/llm/`, etc.)
- **HARD**: Use modular imports (`from src.config.loader import ConfigLoader`)
- See: [02-folder-structure.md](02-folder-structure.md)

### Testing
- **HARD**: NO MOCKS EVER - Use real implementations only
- **SOFT**: Write tests before or alongside implementation
- **SOFT**: Skip tests if external dependencies unavailable
- See: [03-testing-real-only.md](03-testing-real-only.md)

### Logging
- **HARD**: NO print() statements - Use logging module
- **HARD**: Use `logging.getLogger(__name__)` in all modules
- See: [04-logging-unified.md](04-logging-unified.md)

### Code Standards
- **HARD**: Type hints on all public functions
- **HARD**: Google-style docstrings on all public APIs
- **SOFT**: Follow PEP 8 style guide
- See: [05-code-standards.md](05-code-standards.md)

### Error Handling
- **SOFT**: Collect errors, continue processing
- **SOFT**: Fail gracefully with clear messages
- See: [06-error-handling.md](06-error-handling.md), [09-safe-to-fail.md](09-safe-to-fail.md)

### Configuration
- **HARD**: Configuration-driven (YAML configs in `config/`)
- **HARD**: No hard-coded paths or settings
- See: [07-configuration.md](07-configuration.md)

### Documentation
- **HARD**: AGENTS.md and README.md at every folder level
- **SOFT**: Progressive documentation (quick start → deep dive)
- See: [11-documentation-standards.md](11-documentation-standards.md)

## What NOT to Do

❌ **Don't use mock methods in tests**  
❌ **Don't use pip/virtualenv (use uv)**  
❌ **Don't hard-code paths or settings (use config files)**  
❌ **Don't use print() (use logging)**  
❌ **Don't skip type hints on public functions**  
❌ **Don't skip docstrings on public APIs**  
❌ **Don't create monolithic modules**  
❌ **Don't fail fast on first error (collect and report)**

## What TO Do

✅ **Use real data in tests**  
✅ **Use uv for package management**  
✅ **Use YAML configuration files**  
✅ **Use logging module for all output**  
✅ **Add type hints to all public functions**  
✅ **Add Google-style docstrings to all public APIs**  
✅ **Follow modular folder structure**  
✅ **Collect errors and continue processing**

## Related Rules

- [01-uv-environment.md](01-uv-environment.md) - Environment setup
- [02-folder-structure.md](02-folder-structure.md) - Code organization
- [03-testing-real-only.md](03-testing-real-only.md) - Testing philosophy
- [04-logging-unified.md](04-logging-unified.md) - Logging standards
- [05-code-standards.md](05-code-standards.md) - Code style

## See Also

- **[../AGENTS.md](../AGENTS.md)** - Complete repository overview
- **[../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System design
- **[../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)** - Contribution guidelines
