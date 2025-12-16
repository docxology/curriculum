# Extension Guide

Complete guide for extending the educational course Generator with new features, content types, generators, and custom workflows.

## Quick Reference Card

| Extension Type | Location | Key Steps |
|----------------|----------|-----------|
| **New Content Type** | `src/generate/formats/` | Create generator class, add prompt template, integrate into pipeline |
| **New Generator** | `src/generate/formats/` | Inherit from ContentGenerator, implement generate/save methods |
| **New Configuration** | `config/*.yaml` | Add fields, update ConfigLoader, add validation |
| **New Pipeline Stage** | `src/generate/stages/` | Create stage class, add to pipeline orchestration |
| **Custom Workflow** | Custom script | Import components, create custom orchestration |

**Read time**: 30-40 minutes | **Audience**: Developers, contributors

## Overview

The educational course Generator is designed for extensibility. This guide covers:
- Adding content types and generators
- Adding configuration options
- Adding pipeline stages
- Creating custom workflows
- Integration patterns
- Testing requirements
- Documentation requirements

## Adding New Content Types

### Step 1: Create Generator Class

Create a new file in `src/generate/formats/`:

**File**: `src/generate/formats/custom_content.py`

```python
"""Custom content generator."""

import logging
from pathlib import Path
from typing import Dict, Any

from src.generate.formats import ContentGenerator
from src.utils.helpers import ensure_directory

logger = logging.getLogger(__name__)


class CustomContentGenerator(ContentGenerator):
    """Generate custom content for modules."""
    
    def generate_custom_content(
        self,
        module_info: Dict[str, Any],
        session_number: int = 1,
        total_sessions: int = 1,
        session_title: str = ""
    ) -> str:
        """Generate custom content for a module.
        
        Args:
            module_info: Module information dictionary
            session_number: Current session number
            total_sessions: Total number of sessions
            session_title: Title of this specific session
            
        Returns:
            Generated content as markdown
        """
        module_name = module_info['name']
        logger.info(f"Generating custom content for: {module_name}")
        
        # Get prompt template
        prompt_config = self.config_loader.get_prompt_template("custom_content")
        system_prompt = prompt_config['system']
        template = prompt_config['template']
        
        # Prepare variables
        variables = {
            "module_name": module_name,
            "subtopics": "\n".join(f"- {s}" for s in module_info.get('subtopics', [])),
            "objectives": "\n".join(f"- {o}" for o in module_info.get('learning_objectives', [])),
            "session_number": str(session_number),
            "total_sessions": str(total_sessions),
            "session_title": session_title or module_name,
        }
        
        # Generate content
        content = self.llm_client.generate_with_template(
            template,
            variables,
            system_prompt=system_prompt,
            operation="custom_content"
        )
        
        # Add header
        header = f"""# {module_name} - Custom Content

---
"""
        return header + content
    
    def save_custom_content(
        self,
        content: str,
        module_info: Dict[str, Any],
        output_dir: Path,
        session_number: int = 1
    ) -> Path:
        """Save custom content to file.
        
        Args:
            content: Content to save
            module_info: Module information
            output_dir: Output directory
            session_number: Session number
            
        Returns:
            Path to saved file
        """
        ensure_directory(output_dir)
        
        module_id = module_info['module_id']
        module_name_slug = module_info.get('module_name_slug', module_info['name'].lower().replace(' ', '_'))
        filename = f"custom_content_{module_id:02d}_{module_name_slug}_session_{session_number:02d}.md"
        filepath = output_dir / filename
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Saved custom content to: {filepath}")
        
        return filepath
```

### Step 2: Add Prompt Template

Add prompt template to `config/llm_config.yaml`:

```yaml
prompts:
  custom_content:
    system: "You are an expert {subject} educator creating custom content."
    template: |
      Create custom content for: {module_name}
      
      Topics to cover:
      {subtopics}
      
      Learning objectives:
      {objectives}
      
      Session: {session_number}/{total_sessions}
      Session title: {session_title}
      
      Generate comprehensive custom content following the format...
```

### Step 3: Integrate into Pipeline

Update `src/generate/orchestration/pipeline.py`:

**Add import**:
```python
from src.generate.formats.custom_content import CustomContentGenerator
```

**Initialize in `__init__`**:
```python
def __init__(self, config_loader: ConfigLoader):
    # ... existing initialization ...
    self.custom_content_generator = CustomContentGenerator(config_loader, self.llm_client)
```

**Add to generation method**:
```python
def stage2_generate_content_by_session(self, module_ids: Optional[List[int]] = None):
    # ... existing code ...
    for module in modules:
        for session in module['sessions']:
            # ... existing generation ...
            
            # Generate custom content
            logger.info("  → Generating custom content...")
            custom_content = self.custom_content_generator.generate_custom_content(
                module_info=module,
                session_number=session['session'],
                total_sessions=total_sessions,
                session_title=session.get('title', '')
            )
            custom_content, _ = full_cleanup_pipeline(custom_content, "custom_content")
            custom_content_path = session_dir / "custom_content.md"
            custom_content_path.write_text(custom_content, encoding='utf-8')
            session_result['custom_content_path'] = custom_content_path
```

### Step 4: Add Validation (Optional)

If your content type needs validation, add analysis function:

**File**: `src/utils/content_analysis/analyzers.py`

```python
def analyze_custom_content(content: str, requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """Analyze custom content."""
    if requirements is None:
        requirements = {}
    
    metrics = {
        'word_count': count_words(content),
        'char_count': len(content),
        # ... custom metrics ...
    }
    
    warnings = []
    # Add validation logic
    if metrics['word_count'] < requirements.get('min_word_count', 500):
        warnings.append(f"Word count below minimum")
    
    metrics['warnings'] = warnings
    metrics['requirements'] = requirements
    return metrics
```

**Add requirements to `config/llm_config.yaml`**:
```yaml
content_generation:
  custom_content:
    min_word_count: 500
    max_word_count: 1000
```

**Update ConfigLoader** in `src/config/loader.py`:
```python
def get_content_requirements(self) -> Dict[str, Dict[str, int]]:
    # ... existing code ...
    return {
        # ... existing content types ...
        'custom_content': content_config.get('custom_content', {
            'min_word_count': 500,
            'max_word_count': 1000
        })
    }
```

### Step 5: Add Tests

Create test file `tests/test_custom_content_generator.py`:

```python
"""Tests for CustomContentGenerator."""

import pytest
from pathlib import Path
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.custom_content import CustomContentGenerator


@pytest.fixture
def custom_content_generator(config_loader, llm_client):
    """Create CustomContentGenerator instance."""
    return CustomContentGenerator(config_loader, llm_client)


def test_generate_custom_content(custom_content_generator, module_info, skip_if_no_ollama):
    """Test custom content generation."""
    content = custom_content_generator.generate_custom_content(
        module_info=module_info,
        session_number=1,
        total_sessions=3
    )
    
    assert isinstance(content, str)
    assert len(content) > 0
    assert module_info['name'] in content


def test_save_custom_content(custom_content_generator, module_info, tmp_path, skip_if_no_ollama):
    """Test saving custom content."""
    content = custom_content_generator.generate_custom_content(module_info)
    filepath = custom_content_generator.save_custom_content(
        content, module_info, tmp_path
    )
    
    assert filepath.exists()
    assert filepath.read_text() == content
```

### Step 6: Update Documentation

Update `docs/FORMATS.md` with new format documentation:

```markdown
## Format X: Custom Content

**Purpose**: [Description]

**Generator**: `src.generate.formats.custom_content.CustomContentGenerator`

**Output File**: `output/modules/module_XX/session_YY/custom_content.md`

**Format Structure**:
[Document format structure]

**LLM Prompt Template**:
[Document prompt template]
```

## Adding New Generators

### Generator Base Class

All generators inherit from `ContentGenerator` base class:

**File**: `src/generate/formats/__init__.py`

```python
class ContentGenerator:
    """Base class for all content generators."""
    
    def __init__(self, config_loader: ConfigLoader, llm_client: OllamaClient):
        self.config_loader = config_loader
        self.llm_client = llm_client
```

### Generator Interface

All generators should implement:

1. **Generation method**: `generate_<content_type>(module_info, ...) -> str`
2. **Save method**: `save_<content_type>(content, module_info, output_dir, ...) -> Path`
3. **Logging**: Use `logging.getLogger(__name__)`
4. **Error handling**: Raise appropriate exceptions
5. **Type hints**: All methods should have type hints
6. **Docstrings**: Google-style docstrings

### Example: Complete Generator

See existing generators for complete examples:
- `src/generate/formats/lectures.py` - LectureGenerator
- `src/generate/formats/labs.py` - LabGenerator
- `src/generate/formats/study_notes.py` - StudyNotesGenerator

## Adding New Configuration Options

### Step 1: Add to YAML File

Add fields to appropriate YAML file:

**Example**: Add to `config/llm_config.yaml`:

```yaml
llm:
  # ... existing fields ...
  custom_setting: "default_value"
  custom_options:
    option1: true
    option2: 100
```

### Step 2: Update ConfigLoader

Add accessor method in `src/config/loader.py`:

```python
def get_custom_setting(self) -> str:
    """Get custom setting value.
    
    Returns:
        Custom setting value
    """
    llm_config = self.load_llm_config()
    return llm_config.get('llm', {}).get('custom_setting', 'default_value')

def get_custom_options(self) -> Dict[str, Any]:
    """Get custom options.
    
    Returns:
        Dictionary of custom options
    """
    llm_config = self.load_llm_config()
    return llm_config.get('llm', {}).get('custom_options', {})
```

### Step 3: Add Validation

Add validation in `validate_llm_config()`:

```python
def validate_llm_config(self) -> None:
    """Validate LLM configuration."""
    # ... existing validation ...
    
    # Validate custom setting
    custom_setting = llm_config.get('llm', {}).get('custom_setting')
    if custom_setting and not isinstance(custom_setting, str):
        raise ConfigurationError(
            "'llm.custom_setting' must be a string"
        )
```

### Step 4: Document Configuration

Update `docs/CONFIGURATION.md`:

```markdown
### Custom Settings

**`llm.custom_setting`**: Description of setting
- Type: string
- Default: "default_value"
- Purpose: [Explain purpose]

**`llm.custom_options`**: Description of options
- Type: dictionary
- Default: {}
- Options:
  - `option1`: boolean - [Description]
  - `option2`: integer - [Description]
```

## Adding New Pipeline Stages

### Step 1: Create Stage Class

Create new file in `src/generate/stages/`:

**File**: `src/generate/stages/stage_custom.py`

```python
"""Custom pipeline stage."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient

logger = logging.getLogger(__name__)


class CustomStageGenerator:
    """Generate custom stage content."""
    
    def __init__(self, config_loader: ConfigLoader, llm_client: OllamaClient):
        self.config_loader = config_loader
        self.llm_client = llm_client
    
    def generate(self, outline_path: Optional[Path] = None) -> Path:
        """Generate custom stage content.
        
        Args:
            outline_path: Optional path to outline file
            
        Returns:
            Path to generated content
        """
        logger.info("Starting custom stage generation...")
        
        # Load outline
        if outline_path is None:
            outline_path = self.config_loader._find_latest_outline_json()
        
        if not outline_path or not outline_path.exists():
            raise ValueError("No outline found. Run Stage 03 first.")
        
        # Load modules
        modules = self.config_loader.load_outline_from_json(outline_path)
        
        # Process modules
        for module in modules:
            self._process_module(module)
        
        logger.info("Custom stage generation complete")
        return Path("output/custom_stage/")
    
    def _process_module(self, module: Dict[str, Any]) -> None:
        """Process a single module."""
        logger.info(f"Processing module: {module['module_name']}")
        # ... custom processing logic ...
```

### Step 2: Integrate into Pipeline

Update `src/generate/orchestration/pipeline.py`:

**Add import**:
```python
from src.generate.stages.stage_custom import CustomStageGenerator
```

**Add method**:
```python
def stage_custom(self, outline_path: Optional[Path] = None) -> Path:
    """Execute custom stage.
    
    Args:
        outline_path: Optional path to outline file
        
    Returns:
        Path to generated content
    """
    custom_stage = CustomStageGenerator(self.config_loader, self.llm_client)
    return custom_stage.generate(outline_path)
```

### Step 3: Add Script

Create script `scripts/07_custom_stage.py`:

```python
"""Stage 07: Custom Stage Generation."""

from pathlib import Path
import sys
import logging

# Add project root to path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.utils.logging_setup import setup_logging
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

# Setup logging
log_file = setup_logging(
    script_name="07_custom_stage",
    log_level="INFO",
    console_output=True,
    file_output=True
)

logger = logging.getLogger(__name__)

def main():
    """Run custom stage generation."""
    logger.info("Starting custom stage generation...")
    
    config_loader = ConfigLoader("config")
    generator = ContentGenerator(config_loader)
    
    result_path = generator.stage_custom()
    logger.info(f"Custom stage complete. Output: {result_path}")

if __name__ == "__main__":
    main()
```

### Step 4: Update Pipeline Script

Update `scripts/run_pipeline.py` to include new stage:

```python
# Add stage execution
if not args.skip_custom:
    logger.info("STAGE 07: Custom Stage")
    generator.stage_custom()
```

## Custom Workflows

### Pattern 1: Selective Content Generation

Generate only specific content types:

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.diagrams import DiagramGenerator

config = ConfigLoader("config")
llm = OllamaClient(config.get_llm_parameters())

# Initialize only needed generators
lecture_gen = LectureGenerator(config, llm)
diagram_gen = DiagramGenerator(config, llm)

# Load modules
modules = config.load_outline_from_json("output/outlines/course_outline.json")

# Generate only lectures and diagrams
for module in modules:
    for session in module['sessions']:
        lecture = lecture_gen.generate_lecture(module, session_number=session['session'])
        diagram = diagram_gen.generate_diagram(
            topic=session['subtopics'][0],
            context=lecture[:500]
        )
        # Save manually...
```

### Pattern 2: Custom Processing Pipeline

Create custom processing logic:

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

config = ConfigLoader("config")
generator = ContentGenerator(config)

# Generate outline
outline_path = generator.stage1_generate_outline()

# Custom processing
modules = config.load_outline_from_json(outline_path)
for module in modules:
    # Custom logic here
    process_module_custom(module)
```

### Pattern 3: Integration with External Systems

Integrate with external tools:

```python
from src.config.loader import ConfigLoader
from src.generate.formats.lectures import LectureGenerator

config = ConfigLoader("config")
generator = LectureGenerator(config, llm_client)

# Generate content
lecture = generator.generate_lecture(module)

# Process with external tool
processed = external_tool.process(lecture)

# Save
generator.save_lecture(processed, module, output_dir)
```

## Integration Patterns

### Pattern 1: Reuse Existing Generators

```python
# Use existing generators without pipeline
from src.generate.formats.lectures import LectureGenerator

generator = LectureGenerator(config_loader, llm_client)
content = generator.generate_lecture(module_info)
```

### Pattern 2: Extend Base Generator

```python
from src.generate.formats import ContentGenerator

class ExtendedGenerator(ContentGenerator):
    """Extended generator with additional features."""
    
    def generate_with_custom_logic(self, module_info):
        # Custom logic
        base_content = super().generate_lecture(module_info)
        # Additional processing
        return enhanced_content
```

### Pattern 3: Composition

```python
class CompositeGenerator:
    """Compose multiple generators."""
    
    def __init__(self, config_loader, llm_client):
        self.lecture_gen = LectureGenerator(config_loader, llm_client)
        self.lab_gen = LabGenerator(config_loader, llm_client)
    
    def generate_all(self, module_info):
        return {
            'lecture': self.lecture_gen.generate_lecture(module_info),
            'lab': self.lab_gen.generate_lab(module_info)
        }
```

## Extension Testing Requirements

### Unit Tests

Test generator functionality:

```python
def test_generator_initialization():
    """Test generator can be initialized."""
    generator = CustomGenerator(config_loader, llm_client)
    assert generator is not None

def test_generation_method():
    """Test generation method."""
    content = generator.generate_custom_content(module_info)
    assert isinstance(content, str)
    assert len(content) > 0
```

### Integration Tests

Test with real LLM:

```python
@pytest.mark.skipif(not ollama_available(), reason="Ollama not available")
def test_generation_with_llm():
    """Test generation with real LLM."""
    content = generator.generate_custom_content(module_info)
    assert len(content) > 100
    assert module_info['name'] in content
```

### Test Organization

- **Location**: `tests/test_<generator_name>.py`
- **Fixtures**: Use existing fixtures from `conftest.py`
- **Coverage**: Test all public methods
- **Edge cases**: Test error handling, empty inputs, etc.

## Extension Documentation Requirements

### Code Documentation

1. **Module docstring**: Describe purpose
2. **Class docstring**: Describe class purpose and usage
3. **Method docstrings**: Google-style with Args, Returns, Raises
4. **Type hints**: All parameters and return types

### User Documentation

1. **Update FORMATS.md**: Document new content format
2. **Update API.md**: Document new generator API
3. **Update CONFIGURATION.md**: Document new configuration options
4. **Update PIPELINE_GUIDE.md**: Document new pipeline stage (if applicable)

### Example Documentation

```python
"""Custom content generator.

This module provides CustomContentGenerator for generating
custom educational content.
"""

class CustomContentGenerator(ContentGenerator):
    """Generate custom content for modules.
    
    This generator creates custom educational content based on
    module information and session context.
    
    Example:
        >>> generator = CustomContentGenerator(config_loader, llm_client)
        >>> content = generator.generate_custom_content(module_info)
        >>> path = generator.save_custom_content(content, module_info, output_dir)
    """
```

## Best Practices

1. **Follow existing patterns**: Study existing generators before creating new ones
2. **Inherit from base class**: Use `ContentGenerator` base class
3. **Use configuration**: Load settings from config files, not hardcode
4. **Add validation**: Validate inputs and outputs
5. **Log appropriately**: Use appropriate log levels
6. **Handle errors**: Raise specific exceptions with clear messages
7. **Write tests**: Test all functionality, including error cases
8. **Update documentation**: Keep docs synchronized with code
9. **Type hints**: Use type hints for all public methods
10. **Docstrings**: Write comprehensive docstrings

## Common Extension Scenarios

### Scenario 1: New Content Format

**Goal**: Add a new content type (e.g., "flashcards")

**Steps**:
1. Create `FlashcardGenerator` in `src/generate/formats/flashcards.py`
2. Add prompt template to `llm_config.yaml`
3. Integrate into pipeline
4. Add validation (optional)
5. Add tests
6. Update documentation

### Scenario 2: New Configuration Option

**Goal**: Add configurable setting (e.g., "content_style")

**Steps**:
1. Add field to appropriate YAML file
2. Add accessor method to `ConfigLoader`
3. Add validation
4. Use in generators
5. Document in `CONFIGURATION.md`

### Scenario 3: New Pipeline Stage

**Goal**: Add new processing stage (e.g., "content review")

**Steps**:
1. Create stage class in `src/generate/stages/`
2. Integrate into `ContentGenerator`
3. Create script in `scripts/`
4. Update `run_pipeline.py`
5. Document in `PIPELINE_GUIDE.md`

### Scenario 4: Custom Workflow

**Goal**: Create specialized workflow (e.g., "generate only for module 1")

**Steps**:
1. Create custom script
2. Import needed components
3. Implement custom logic
4. Document usage

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and extension points
- **[API.md](API.md)** - Generator APIs and interfaces
- **[MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md)** - Module structure and dependencies
- **[FORMATS.md](FORMATS.md)** - Content format specifications
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration system

## Summary

The educational course Generator is designed for extensibility. You can:
- Add new content types by creating generator classes
- Add new configuration options by updating YAML and ConfigLoader
- Add new pipeline stages by creating stage classes
- Create custom workflows by composing existing components

All extensions should:
- Follow existing patterns and conventions
- Include comprehensive tests
- Update documentation
- Use proper error handling and logging
- Include type hints and docstrings

The modular architecture makes it easy to extend functionality while maintaining code quality and consistency.






