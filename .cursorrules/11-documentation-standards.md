# Documentation Standards

## Hard Constraint

**MUST have AGENTS.md and README.md at every folder level.**

## Documentation Requirements

### Folder-Level Documentation

**HARD**: Every folder MUST have:
- `AGENTS.md` - Guide for AI agents (API reference, usage patterns)
- `README.md` - Guide for humans (overview, quick start)

### Documentation Structure

```
src/
├── AGENTS.md            # Package overview for AI
├── README.md           # Package overview for humans
├── config/
│   ├── AGENTS.md       # ConfigLoader API
│   └── README.md       # Configuration usage
├── generate/
│   ├── AGENTS.md       # Generation overview
│   ├── README.md       # Generation overview
│   ├── formats/
│   │   ├── AGENTS.md   # Format generators API
│   │   └── README.md   # Format generators usage
│   └── ...
```

## Documentation Content

### AGENTS.md Structure

**For AI agents** - Focus on:
- API reference with type hints
- Usage patterns and examples
- Integration points
- Error handling
- Common tasks

```markdown
# Module Name - For AI Agents

## Module Purpose
Brief description of module purpose.

## Key Class/Function
```python
from src.module.name import ClassName

class ClassName:
    def method(self, param: Type) -> ReturnType:
        """Method description."""
        pass
```

## Usage Examples
```python
# Example usage
```

## Error Handling
How errors are handled in this module.

## See Also
Links to related documentation.
```

### README.md Structure

**For humans** - Focus on:
- Overview and purpose
- Quick start examples
- Common tasks
- Integration with other modules

```markdown
# Module Name

Brief description of module purpose.

## Overview
What this module does.

## Usage
```python
# Quick start example
```

## Common Tasks
How to accomplish common tasks.

## See Also
Links to related documentation.
```

## Progressive Documentation

**SOFT**: Documentation should be progressive (quick start → deep dive):

1. **Quick Reference** - Top of file, essential info
2. **Overview** - What and why
3. **Usage** - How to use
4. **Details** - Deep technical information
5. **Examples** - Real-world examples
6. **See Also** - Cross-references

## Documentation Principles

### Evergreen Documentation

**SOFT**: Keep documentation evergreen:
- ✅ Permanent knowledge only
- ✅ No temporary progress reports
- ✅ No "TODO" sections (use issue tracker)
- ✅ No dated content (unless critical)

### Quality Standards

**SOFT**: Follow quality standards:
- ✅ Complete - Comprehensive coverage
- ✅ Accurate - Reflects actual implementation
- ✅ Navigable - Clear signposting
- ✅ Actionable - Includes examples
- ✅ Progressive - Quick start → deep dive

## Code Documentation

### Docstrings

**HARD**: All public APIs MUST have Google-style docstrings (see [05-code-standards.md](05-code-standards.md))

### Comments

**SOFT**: Use comments to explain "why", not "what":
- Code should be self-documenting
- Comments for complex logic
- Comments for non-obvious decisions

## Cross-References

**SOFT**: Maintain accurate cross-references:
- Link to related documentation
- Update links when files move
- Verify links work

## See Also

- **[02-folder-structure.md](02-folder-structure.md)** - Folder structure requirements
- **[05-code-standards.md](05-code-standards.md)** - Docstring requirements
- **[../docs/README.md](../docs/README.md)** - Documentation hub
- **[../docs/AGENTS.md](../docs/AGENTS.md)** - Documentation guide for AI agents
