# Code Standards - Style and Quality

## Mixed Constraints

This file contains both hard constraints (MUST follow) and soft constraints (SHOULD follow).

## Hard Constraints

### Type Hints

**MUST have type hints on all public functions:**

```python
# ✅ CORRECT: Type hints on public function
from typing import Dict, List, Any, Optional
from pathlib import Path

def generate_content(
    module_info: Dict[str, Any],
    session_number: int = 1
) -> str:
    """Generate content for a module."""
    pass

# ❌ WRONG: Missing type hints
def generate_content(module_info, session_number=1):
    """Generate content for a module."""
    pass
```

### Docstrings

**MUST use Google-style docstrings on all public APIs:**

```python
# ✅ CORRECT: Google-style docstring
def generate_content(
    module_info: Dict[str, Any],
    session_number: int = 1
) -> str:
    """Generate content for a module.
    
    Args:
        module_info: Module information dictionary with name, subtopics, etc.
        session_number: Current session number (1-indexed)
    
    Returns:
        Generated content as markdown string
    
    Raises:
        ContentGenerationError: If generation fails
    """
    pass

# ❌ WRONG: Missing docstring
def generate_content(module_info: Dict[str, Any], session_number: int = 1) -> str:
    pass

# ❌ WRONG: Wrong docstring style
def generate_content(module_info: Dict[str, Any], session_number: int = 1) -> str:
    """
    Generate content for a module.
    
    @param module_info: Module information
    @param session_number: Session number
    @return: Generated content
    """
    pass
```

## Soft Constraints

### PEP 8 Style

**SHOULD follow PEP 8 style guide:**

- 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Follow naming conventions:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Code Formatting

```bash
# Format code with black
uv run black src/ tests/

# Check style with flake8
uv run flake8 src/ tests/
```

### Naming Conventions

```python
# ✅ CORRECT: Clear, descriptive names
def generate_lecture_content(module_info: Dict[str, Any]) -> str:
    """Generate lecture content."""
    pass

class LectureGenerator:
    """Generate lecture content."""
    pass

# ❌ WRONG: Unclear names
def gen_lec(mi: Dict[str, Any]) -> str:
    pass
```

## Code Quality

### Error Handling

**SOFT**: Handle errors gracefully (see [06-error-handling.md](06-error-handling.md)):

```python
# ✅ CORRECT: Proper error handling
from src.config.loader import ConfigurationError

try:
    loader = ConfigLoader("config")
    config = loader.load_course_config()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    raise
```

### Function Length

**SOFT**: Keep functions focused and reasonably sized:
- Single responsibility
- Clear purpose
- Easy to test

### Comments

**SOFT**: Use comments to explain "why", not "what":
- Code should be self-documenting
- Comments for complex logic or non-obvious decisions
- Docstrings for public APIs (required)

## Examples

### Good Code

```python
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LectureGenerator:
    """Generate lecture content for course modules."""
    
    def __init__(
        self,
        config_loader: ConfigLoader,
        llm_client: OllamaClient
    ) -> None:
        """Initialize lecture generator.
        
        Args:
            config_loader: Configuration loader instance
            llm_client: LLM client instance
        """
        self.config_loader = config_loader
        self.llm_client = llm_client
    
    def generate_lecture(
        self,
        module_info: Dict[str, Any],
        session_number: int = 1
    ) -> str:
        """Generate lecture content for a module.
        
        Args:
            module_info: Module information dictionary
            session_number: Current session number
        
        Returns:
            Generated lecture content as markdown
        
        Raises:
            ContentGenerationError: If generation fails
        """
        logger.info(f"Generating lecture for module: {module_info['name']}")
        # Implementation...
```

### Bad Code (Violates Multiple Rules)

```python
# ❌ Missing type hints, docstrings, uses print()
class LG:
    def __init__(self, cl, llm):
        self.cl = cl
        self.llm = llm
    
    def gen(self, mi, sn=1):
        print(f"Generating for: {mi['name']}")  # ❌ print() instead of logging
        # Missing error handling
        return self.llm.generate("prompt")
```

## See Also

- **[../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)** - Contribution guidelines
- **[../docs/API.md](../docs/API.md)** - API reference with examples
- **[06-error-handling.md](06-error-handling.md)** - Error handling patterns
