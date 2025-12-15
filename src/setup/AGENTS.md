# Setup Module

Package initialization and setup utilities.

## Module Purpose

Provides package-level initialization for the src package. Currently minimal, containing only `__init__.py` for Python package structure. Reserved for future setup and initialization utilities.

## Current Status

This module is intentionally minimal. The `__init__.py` file makes `src/setup/` a Python package but does not export any public APIs.

## Usage

Not used directly. The module exists for package structure and future extension.

```python
# No direct imports needed from setup module
# All setup is handled by individual component modules
```

## Package Structure

The src package is organized with clear separation:

```
src/
├── setup/           # This module (initialization utilities)
├── config/          # Configuration management
├── llm/             # LLM integration
├── generate/        # Content generation
│   ├── orchestration/
│   ├── stages/
│   ├── processors/
│   └── formats/
└── utils/           # Utility functions
```

## Initialization Pattern

The src package uses distributed initialization:

```python
# Each module initializes independently
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.orchestration.pipeline import ContentGenerator

# No central setup module required
loader = ConfigLoader("config")
client = OllamaClient(loader.get_llm_parameters())
generator = ContentGenerator(loader)
```

## Future Extensions

This module is reserved for future setup utilities:

- Environment validation scripts
- Package-level configuration
- Installation helpers
- First-run initialization
- Dependency checking utilities
- Setup wizards or interactive configuration

## Integration

Currently not integrated with other modules. All setup is handled at the application level through:
- `scripts/01_setup_environment.py` - Environment validation
- `scripts/02_run_tests.py` - Testing and validation
- Individual module initialization

## Testing

No tests currently needed for this module as it contains only package structure.

When setup utilities are added:
```bash
uv run pytest tests/test_setup.py -v
```

## Development Notes

When adding setup utilities to this module:

1. **Keep it minimal** - Only package-level concerns
2. **Follow patterns** - Use same structure as other modules
3. **Document thoroughly** - Update this AGENTS.md with new APIs
4. **Test comprehensively** - Add to test suite
5. **Log appropriately** - Use logging module

Example future utility:

```python
# Future: src/setup/initializer.py

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def initialize_environment(
    config_dir: str = "config",
    output_dir: str = "output",
    validate: bool = True
) -> bool:
    """Initialize educational course environment.
    
    Args:
        config_dir: Configuration directory
        output_dir: Output directory
        validate: Run validation checks
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing educational course environment")
    
    # Create directories
    # Validate configuration
    # Check dependencies
    # etc.
    
    return True
```

## Future Extension Patterns

When adding setup utilities to this module:

### Pattern 1: Environment Validation

```python
# Future: src/setup/initializer.py
def validate_environment(
    config_dir: str = "config",
    check_ollama: bool = True,
    check_models: bool = True
) -> Dict[str, bool]:
    """Validate complete environment."""
    results = {}
    results["config"] = Path(config_dir).exists()
    if check_ollama:
        results["ollama"] = ollama_is_running()
    if check_models:
        results["model"] = ensure_model_available("gemma3:4b")
    return results
```

### Pattern 2: First-Run Initialization

```python
def initialize_first_run(
    config_dir: str = "config",
    output_dir: str = "output"
) -> None:
    """Initialize directories and default configs on first run."""
    ensure_directory(config_dir)
    ensure_directory(output_dir)
    # Create default configs if missing
    # Validate environment
    # Set up logging
```

### Pattern 3: Integration with Scripts

```python
# Integration point with scripts/01_setup_environment.py
from src.setup.initializer import validate_environment

# Script can use setup module utilities
results = validate_environment()
if not all(results.values()):
    logger.error("Environment validation failed")
```

## Integration Points

- **Scripts**: `scripts/01_setup_environment.py` - Environment validation script
- **Configuration**: `src/config/loader.py` - ConfigLoader initialization
- **Pipeline**: `src/generate/orchestration/pipeline.py` - ContentGenerator initialization
- **Utils**: `src/utils/helpers.py` - System check utilities

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide
- **Environment Setup**: [../../scripts/AGENTS.md](../../scripts/AGENTS.md) - Script 01 documentation
- **Configuration**: [../config/AGENTS.md](../config/AGENTS.md) - Config initialization
- **Pipeline**: [../generate/orchestration/AGENTS.md](../generate/orchestration/AGENTS.md) - Generator initialization
- **Setup Guide**: [../../SETUP.md](../../SETUP.md) - Installation and setup documentation


