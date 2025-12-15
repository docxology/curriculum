# Development Rules - Guide

This directory contains comprehensive, modular development rules for the educational course Generator. All rules are organized by topic with clear distinction between hard constraints (MUST follow) and soft constraints (SHOULD follow).

## Rule Files Overview

| File | Topic | Constraint Type | Purpose |
|------|-------|----------------|---------|
| **[00-overview.md](00-overview.md)** | Project Philosophy | Mixed | Quick reference, core principles |
| **[01-uv-environment.md](01-uv-environment.md)** | Environment Setup | HARD | uv-only package management |
| **[02-folder-structure.md](02-folder-structure.md)** | Code Organization | HARD | Modular structure requirements |
| **[03-testing-real-only.md](03-testing-real-only.md)** | Testing Philosophy | HARD | NO MOCKS EVER |
| **[04-logging-unified.md](04-logging-unified.md)** | Logging Standards | HARD | No print() statements |
| **[05-code-standards.md](05-code-standards.md)** | Code Style | MIXED | Type hints, docstrings, PEP 8 |
| **[06-error-handling.md](06-error-handling.md)** | Error Patterns | SOFT | Graceful failure patterns |
| **[07-configuration.md](07-configuration.md)** | Config-Driven | HARD | YAML configuration requirements |
| **[08-content-generation.md](08-content-generation.md)** | Generation Patterns | SOFT | Content generation best practices |
| **[09-safe-to-fail.md](09-safe-to-fail.md)** | Failure Handling | SOFT | Collect errors, continue working |
| **[10-agentic-generation.md](10-agentic-generation.md)** | Workflow Patterns | SOFT | Hybrid AI/human workflows |
| **[11-documentation-standards.md](11-documentation-standards.md)** | Documentation | HARD | Docs at every level |

## Constraint Types

### Hard Constraints (MUST Follow)
These are non-negotiable requirements. Code that violates hard constraints will be rejected.

**Examples**:
- Use `uv` for package management (no pip/venv)
- No mock methods in tests (real implementations only)
- No `print()` statements (use logging)
- Type hints on all public functions
- Google-style docstrings on all public APIs

### Soft Constraints (SHOULD Follow)
These are best practices and recommendations. Code that violates soft constraints may be acceptable but should be justified.

**Examples**:
- TDD approach (write tests before/alongside)
- Comprehensive error handling
- Extensive logging
- Progressive documentation

## Quick Reference

### Before Writing Code
1. Read **[00-overview.md](00-overview.md)** for project philosophy
2. Check **[02-folder-structure.md](02-folder-structure.md)** for module organization
3. Review **[05-code-standards.md](05-code-standards.md)** for style requirements

### Before Writing Tests
1. Read **[03-testing-real-only.md](03-testing-real-only.md)** - NO MOCKS EVER
2. Use real implementations and fixtures
3. Skip tests if external dependencies unavailable

### Before Adding Logging
1. Read **[04-logging-unified.md](04-logging-unified.md)** - No print() statements
2. Use `logging.getLogger(__name__)`
3. Follow logging level guidelines

### Before Handling Errors
1. Read **[06-error-handling.md](06-error-handling.md)** for patterns
2. Read **[09-safe-to-fail.md](09-safe-to-fail.md)** for graceful failures
3. Collect errors, continue working, report comprehensively

### Before Adding Configuration
1. Read **[07-configuration.md](07-configuration.md)** - Config-driven approach
2. Add to YAML files in `config/`
3. Update ConfigLoader validation

### Before Writing Documentation
1. Read **[11-documentation-standards.md](11-documentation-standards.md)**
2. Ensure AGENTS.md and README.md at every folder level
3. Follow progressive documentation (quick start → deep dive)

## Integration with Documentation

These rules complement the comprehensive documentation in `docs/`:

- **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System design context
- **[docs/CONFIGURATION.md](../docs/CONFIGURATION.md)** - Configuration details
- **[docs/API.md](../docs/API.md)** - API reference
- **[docs/TESTING_COVERAGE.md](../docs/TESTING_COVERAGE.md)** - Testing philosophy
- **[docs/ERROR_HANDLING.md](../docs/ERROR_HANDLING.md)** - Error handling patterns
- **[docs/LOGGING.md](../docs/LOGGING.md)** - Logging patterns
- **[docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)** - Contribution guidelines

## For AI Agents

AI agents should:
1. **Always check `.cursorrules/`** before making changes
2. **Read relevant rule files** for the area being modified
3. **Follow hard constraints strictly** - these are non-negotiable
4. **Consider soft constraints** - apply when appropriate
5. **Reference documentation** in `docs/` for detailed context

## Rule File Format

Each rule file follows this structure:

1. **Overview** - What this rule covers
2. **Hard Constraints** - MUST follow requirements
3. **Soft Constraints** - SHOULD follow recommendations
4. **Examples** - Good and bad patterns
5. **Cross-References** - Links to related documentation
6. **Anti-Patterns** - What NOT to do

## Maintenance

Rules are living documents. When updating:
- Keep hard constraints stable (major changes require discussion)
- Soft constraints can evolve with project needs
- Update cross-references when documentation changes
- Ensure consistency across all rule files

## See Also

- **[../AGENTS.md](../AGENTS.md)** - High-level overview for AI agents
- **[../README.md](../README.md)** - Project quick start
- **[../docs/README.md](../docs/README.md)** - Documentation hub
