# Module Organization Guide

Complete reference for module structure, dependencies, organization principles, and adding new modules in the educational course Generator.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Structure** | Modular, layered, single responsibility |
| **Dependencies** | Unidirectional (downward flow) |
| **Import Pattern** | `from src.module.submodule import Class` |
| **Module Types** | Configuration, LLM, Generation, Processing, Orchestration, Utility, Website |
| **Organization** | Functional grouping by purpose |

**Read time**: 20-30 minutes | **Audience**: Developers, contributors

## Overview

The educational course Generator uses a modular architecture with clear separation of concerns. Each module has a single, well-defined responsibility and follows consistent organization principles.

## Module Structure

### Complete Module Hierarchy

```
src/
├── setup/                 # Setup and initialization
│   └── __init__.py
├── config/                # Configuration management
│   ├── __init__.py
│   └── loader.py          # ConfigLoader class
├── llm/                   # LLM integration
│   ├── __init__.py
│   └── client.py          # OllamaClient class
├── generate/              # Content generation
│   ├── __init__.py
│   ├── orchestration/     # Pipeline coordination
│   │   ├── __init__.py
│   │   └── pipeline.py    # ContentGenerator
│   ├── stages/            # Generation stages
│   │   ├── __init__.py
│   │   └── stage1_outline.py  # OutlineGenerator
│   ├── processors/        # Content processing
│   │   ├── __init__.py
│   │   ├── parser.py      # OutlineParser
│   │   └── cleanup.py     # ContentCleanup
│   └── formats/           # Format-specific generators
│       ├── __init__.py    # ContentGenerator base class
│       ├── lectures.py    # LectureGenerator
│       ├── labs.py        # LabGenerator
│       ├── study_notes.py # StudyNotesGenerator
│       ├── diagrams.py    # DiagramGenerator
│       └── questions.py   # QuestionGenerator
├── website/               # Website generation
│   ├── __init__.py
│   ├── generator.py       # WebsiteGenerator
│   ├── content_loader.py  # ContentLoader
│   ├── templates.py       # HTML templates
│   ├── styles.py          # CSS styles
│   └── scripts.py         # JavaScript
└── utils/                 # Utilities
    ├── __init__.py
    ├── helpers.py         # File I/O, text processing
    ├── logging_setup.py   # Logging configuration
    └── content_analysis/  # Content analysis
        ├── __init__.py
        ├── analyzers.py   # Analysis functions
        ├── counters.py    # Counting utilities
        ├── logging.py     # Validation logging
        └── mermaid.py     # Mermaid validation
```

## Module Dependencies

### Dependency Graph

```
utils/helpers.py (no dependencies)
    └─> config/loader.py
            └─> llm/client.py
                    ├─> generate/stages/stage1_outline.py
                    │       └─> generate/processors/parser.py
                    └─> generate/formats/*.py (lectures, labs, diagrams, etc.)
                                └─> generate/orchestration/pipeline.py
                                        └─> website/ (generator, content_loader, templates)
```

### Dependency Rules

1. **Unidirectional Flow**: Dependencies flow downward only
2. **No Circular Dependencies**: Modules don't import from modules that depend on them
3. **Utility Layer**: `utils/` has no dependencies (pure functions)
4. **Configuration Layer**: `config/` depends only on `utils/`
5. **LLM Layer**: `llm/` depends on `config/` and `utils/`
6. **Generation Layer**: `generate/` depends on `llm/`, `config/`, and `utils/`
7. **Website Layer**: `website/` depends on `config/` and `utils/`

### Dependency Examples

**Valid Dependencies**:
```python
# ✅ CORRECT - Downward dependency
from src.utils.helpers import ensure_directory
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator
```

**Invalid Dependencies**:
```python
# ❌ WRONG - Circular dependency
# In generate/formats/lectures.py:
from src.generate.orchestration.pipeline import ContentGenerator  # Circular!

# ❌ WRONG - Upward dependency
# In config/loader.py:
from src.generate.formats.lectures import LectureGenerator  # Upward!
```

## Module Organization Principles

### Principle 1: Single Responsibility

Each module has ONE clear purpose:

- **`config/`**: Configuration loading and validation only
- **`llm/`**: LLM API communication only
- **`generate/orchestration/`**: Pipeline coordination only
- **`generate/formats/`**: Content generation only
- **`generate/processors/`**: Content processing only
- **`utils/`**: Utility functions only
- **`website/`**: Website generation only

### Principle 2: Functional Grouping

Related functionality grouped together:

- **`generate/stages/`**: All generation stages (outline generation, etc.)
- **`generate/formats/`**: All format generators (lectures, labs, diagrams, etc.)
- **`generate/processors/`**: All content processors (parser, cleanup, etc.)
- **`utils/content_analysis/`**: All content analysis functions

### Principle 3: Thin Orchestration

Pipeline coordination is minimal - just coordinates other modules:

- **`generate/orchestration/pipeline.py`**: Calls generators, collects results
- Heavy lifting done in specialized generators
- Orchestration layer doesn't contain business logic

### Principle 4: Clear Interfaces

Each module has a clear public interface:

- **Public classes**: Documented with docstrings
- **Public methods**: Type hints and docstrings
- **Private methods**: Prefixed with `_`

## Import Patterns and Standards

### Modular Imports

Always use modular imports from submodules:

```python
# ✅ CORRECT - Modular imports
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.orchestration.pipeline import ContentGenerator
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.processors.parser import OutlineParser
from src.generate.formats.lectures import LectureGenerator
from src.utils.helpers import save_markdown, slugify
from src.website.generator import WebsiteGenerator
```

### Import Rules

1. **Always use `src.` prefix**: `from src.module.submodule import Class`
2. **Import from subfolders**: Never import from root level
3. **Group imports**: Standard library, third-party, local
4. **Avoid wildcard imports**: `from module import *` (not allowed)
5. **Use specific imports**: Import only what you need

### Import Organization

```python
# Standard library
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Third-party
import yaml
import requests

# Local (modular imports)
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator
```

## Module Interface Contracts

### ConfigLoader Interface

**Module**: `src.config.loader`

**Public Methods**:
- `load_course_config() -> Dict[str, Any]`
- `load_llm_config() -> Dict[str, Any]`
- `load_output_config() -> Dict[str, Any]`
- `get_course_info() -> Dict[str, Any]`
- `get_llm_parameters() -> Dict[str, Any]`
- `get_prompt_template(name: str) -> Dict[str, str]`
- `validate_all_configs() -> None`

**Dependencies**: `utils.helpers`

### OllamaClient Interface

**Module**: `src.llm.client`

**Public Methods**:
- `generate(prompt: str, ...) -> str`
- `generate_with_template(template: str, variables: Dict, ...) -> str`

**Dependencies**: `config.loader`, `utils.helpers`

### ContentGenerator Interface

**Module**: `src.generate.orchestration.pipeline`

**Public Methods**:
- `stage1_generate_outline(...) -> Path`
- `stage2_generate_content_by_session(module_ids: Optional[List[int]]) -> List[Dict]`

**Dependencies**: All generators, `config.loader`, `llm.client`

### Format Generator Interface

**Module**: `src.generate.formats.*`

**Base Class**: `ContentGenerator`

**Required Methods**:
- `generate_<content_type>(module_info: Dict, ...) -> str`
- `save_<content_type>(content: str, module_info: Dict, output_dir: Path, ...) -> Path`

**Dependencies**: `config.loader`, `llm.client`, `utils.*`

## Adding New Modules

### Decision Tree

**Question**: Where should this new module go?

1. **Is it configuration-related?** → `src/config/`
2. **Is it LLM communication?** → `src/llm/`
3. **Is it a content generator?** → `src/generate/formats/`
4. **Is it content processing?** → `src/generate/processors/`
5. **Is it a generation stage?** → `src/generate/stages/`
6. **Is it pipeline coordination?** → `src/generate/orchestration/`
7. **Is it a utility function?** → `src/utils/`
8. **Is it website-related?** → `src/website/`
9. **Is it initialization?** → `src/setup/`

### Step-by-Step: Adding a New Module

#### Step 1: Create Module File

```bash
# Example: Adding a new utility module
touch src/utils/new_utility.py
```

#### Step 2: Implement Module

```python
"""New utility module.

This module provides utility functions for...
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def new_utility_function(param: str) -> str:
    """Do something useful.
    
    Args:
        param: Parameter description
        
    Returns:
        Result description
    """
    logger.debug(f"Processing: {param}")
    # Implementation
    return result
```

#### Step 3: Add to `__init__.py`

```python
# src/utils/__init__.py
from src.utils.new_utility import new_utility_function

__all__ = [
    # ... existing exports ...
    'new_utility_function',
]
```

#### Step 4: Create Tests

```python
# tests/test_new_utility.py
"""Tests for new utility module."""

import pytest
from src.utils.new_utility import new_utility_function


def test_new_utility_function():
    """Test new utility function."""
    result = new_utility_function("test")
    assert isinstance(result, str)
    assert len(result) > 0
```

#### Step 5: Update Documentation

- Update `docs/API.md` if public API
- Update `docs/ARCHITECTURE.md` if architectural change
- Update module `AGENTS.md` if module-specific docs exist

### Example: Adding a New Content Generator

See [EXTENSION.md](EXTENSION.md) for complete guide on adding new content generators.

### Example: Adding a New Utility Module

```python
# src/utils/new_utility.py
"""New utility functions."""

from pathlib import Path
from typing import List


def find_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
    """Find files matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "*.md")
        
    Returns:
        List of matching file paths
    """
    return list(directory.glob(pattern))
```

## Module Testing Organization

### Test File Structure

Tests mirror source structure:

```
tests/
├── test_config_loader.py          # Tests for config/loader.py
├── test_llm_client.py             # Tests for llm/client.py
├── test_pipeline.py                # Tests for generate/orchestration/pipeline.py
├── test_outline_generator.py       # Tests for generate/stages/stage1_outline.py
├── test_parser.py                  # Tests for generate/processors/parser.py
├── test_lecture_generator.py       # Tests for generate/formats/lectures.py
├── test_utils.py                  # Tests for utils/helpers.py
└── test_website_generator.py      # Tests for website/generator.py
```

### Test Organization Principles

1. **One test file per module**: `test_<module_name>.py`
2. **Test class per class**: `TestConfigLoader`, `TestOllamaClient`
3. **Test method per method**: `test_load_course_config`, `test_generate`
4. **Use fixtures**: Share test data via pytest fixtures
5. **No mocks**: Use real implementations (see [TESTING_COVERAGE.md](TESTING_COVERAGE.md))

## Module Documentation Requirements

### Code Documentation

Each module should have:

1. **Module docstring**: Describe purpose
2. **Class docstrings**: Google-style for all public classes
3. **Method docstrings**: Google-style with Args, Returns, Raises
4. **Type hints**: All parameters and return types

### Module-Level Documentation

Each module directory should have (if needed):

1. **`README.md`**: Module overview and usage
2. **`AGENTS.md`**: Detailed API reference for AI agents

### Documentation Standards

- **Google-style docstrings**: Consistent format
- **Type hints**: All public methods
- **Examples**: Include usage examples
- **Cross-references**: Link to related modules

## File Naming Conventions

### Source Files

- **Modules**: `snake_case.py` (e.g., `stage1_outline.py`, `content_loader.py`)
- **Classes**: `PascalCase` (e.g., `ConfigLoader`, `OllamaClient`)
- **Functions**: `snake_case` (e.g., `generate_content`, `save_markdown`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)

### Test Files

- **Test files**: `test_<module_name>.py` (e.g., `test_config_loader.py`)
- **Test classes**: `Test<ClassName>` (e.g., `TestConfigLoader`)
- **Test methods**: `test_<method_name>` (e.g., `test_load_course_config`)

### Documentation Files

- **Module docs**: `README.md`, `AGENTS.md` (in module directory)
- **Technical docs**: `docs/*.md` (in docs directory)

## Module Dependencies Best Practices

### Minimize Dependencies

- **Only import what you need**: Don't import entire modules if you only need one function
- **Avoid deep dependencies**: Keep dependency chains short
- **Use dependency injection**: Pass dependencies as parameters

### Dependency Injection Example

```python
# ✅ GOOD - Dependency injection
class LectureGenerator:
    def __init__(self, config_loader: ConfigLoader, llm_client: OllamaClient):
        self.config_loader = config_loader
        self.llm_client = llm_client

# ❌ BAD - Creates dependencies internally
class LectureGenerator:
    def __init__(self):
        self.config_loader = ConfigLoader("config")  # Hard dependency
        self.llm_client = OllamaClient(...)  # Hard dependency
```

## Common Module Patterns

### Pattern 1: Configuration Module

```python
"""Configuration management module."""

import logging
from pathlib import Path
from typing import Dict, Any
import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate configuration files."""
    
    def __init__(self, config_dir: str | Path):
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load and cache configuration file."""
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.config_dir / filename
        with open(filepath) as f:
            config = yaml.safe_load(f)
        
        self._cache[filename] = config
        return config
```

### Pattern 2: Generator Module

```python
"""Content generator module."""

import logging
from typing import Dict, Any
from pathlib import Path

from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Base class for content generators."""
    
    def __init__(self, config_loader: ConfigLoader, llm_client: OllamaClient):
        self.config_loader = config_loader
        self.llm_client = llm_client
    
    def generate(self, module_info: Dict[str, Any]) -> str:
        """Generate content."""
        raise NotImplementedError
    
    def save(self, content: str, output_dir: Path) -> Path:
        """Save content to file."""
        raise NotImplementedError
```

### Pattern 3: Utility Module

```python
"""Utility functions module."""

from pathlib import Path
from typing import List


def find_files(directory: Path, pattern: str) -> List[Path]:
    """Find files matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        
    Returns:
        List of matching file paths
    """
    return list(directory.glob(pattern))
```

## Module Integration

### Integrating into Pipeline

When adding a new module to the pipeline:

1. **Import in pipeline**: Add import to `src/generate/orchestration/pipeline.py`
2. **Initialize in `__init__`**: Create instance in `ContentGenerator.__init__`
3. **Use in methods**: Call methods in appropriate pipeline stages
4. **Update tests**: Add tests for integration

### Integration Example

```python
# In src/generate/orchestration/pipeline.py

# 1. Import
from src.generate.formats.custom_content import CustomContentGenerator

# 2. Initialize
def __init__(self, config_loader: ConfigLoader):
    # ... existing initialization ...
    self.custom_content_generator = CustomContentGenerator(
        config_loader, self.llm_client
    )

# 3. Use in pipeline
def stage2_generate_content_by_session(self, ...):
    # ... existing code ...
    custom_content = self.custom_content_generator.generate_custom_content(...)
    # ... save content ...
```

## Module Maintenance

### When to Refactor

Refactor modules when:
- Module has multiple responsibilities (split)
- Dependencies become circular (restructure)
- Module becomes too large (split into submodules)
- Interface becomes unclear (clarify)

### Refactoring Guidelines

1. **Maintain backward compatibility**: Don't break existing APIs
2. **Update tests**: Ensure tests still pass
3. **Update documentation**: Keep docs synchronized
4. **Update imports**: Fix all import statements

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and module overview
- **[EXTENSION.md](EXTENSION.md)** - Guide for extending the system
- **[API.md](API.md)** - Public API for all modules
- **[.cursorrules/02-folder-structure.md](../.cursorrules/02-folder-structure.md)** - Folder structure standards

## Summary

The educational course Generator uses a modular architecture that:
- **Separates concerns**: Each module has single responsibility
- **Maintains clear dependencies**: Unidirectional, no circular dependencies
- **Follows consistent patterns**: Similar modules organized similarly
- **Supports extensibility**: Easy to add new modules following patterns
- **Enforces standards**: Import patterns, naming conventions, documentation

All modules follow these principles:
- **Single responsibility**: One clear purpose per module
- **Clear interfaces**: Well-defined public APIs
- **Proper dependencies**: Unidirectional, minimal dependencies
- **Comprehensive documentation**: Docstrings, type hints, examples
- **Thorough testing**: Tests mirror source structure






