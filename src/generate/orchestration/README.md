# Pipeline Orchestration

Workflow coordination for course generation.

## Files

- `pipeline.py` - `ContentGenerator` class

## Overview

This module provides the main orchestration class that coordinates the entire course generation workflow. It integrates outline generation, content parsing, and all format-specific generators into a unified pipeline.

## ContentGenerator

Main pipeline orchestrator that manages:
- Outline generation (interactive and non-interactive)
- Primary content generation (lectures, labs, notes, diagrams, questions)
- Secondary content generation (application, extension, visualization, etc.)
- Session-based modular content organization
- Error collection and reporting

## Usage

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

# Initialize
loader = ConfigLoader("config")
generator = ContentGenerator(loader)

# Generate outline
outline = generator.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Smith"
)

# Generate all content
results = generator.generate_content_for_all_modules()

# Or generate for specific modules
result = generator.generate_content_for_module(1)
```

## Key Methods

**Outline**:
- `generate_outline(course_name, instructor, duration, interactive)` - Generate course outline

**Primary Content**:
- `generate_content_for_all_modules()` - Generate all primary content
- `generate_content_for_module(module_id)` - Generate for one module
- `generate_content_for_modules(module_ids)` - Generate for subset

**Secondary Content**:
- `generate_secondary_content(module_id, content_type)` - Generate secondary materials

**Sessions**:
- `generate_session_content(module_id, session_number, num_labs)` - Session-based generation

**Utilities**:
- `clear_output_directories(confirm)` - Clear generated content
- `_load_latest_outline_json()` - Load most recent outline
- `_get_output_directories()` - Get output paths

## Integration

Coordinates all generators:
- `OutlineGenerator` - Course outlines
- `LectureGenerator` - Lectures
- `LabGenerator` - Lab exercises
- `StudyNotesGenerator` - Study notes
- `DiagramGenerator` - Mermaid diagrams
- `QuestionGenerator` - Assessment questions

## Error Handling

Implements "safe-to-fail" pattern:
- Collects errors instead of raising
- Continues processing remaining modules
- Reports all errors at completion

## Testing

Tests in `tests/test_pipeline.py`:
```bash
uv run pytest tests/test_pipeline.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - API reference
- **Pipeline Guide**: [../../../docs/PIPELINE_GUIDE.md](../../../docs/PIPELINE_GUIDE.md)
- **Scripts**: [../../../scripts/README.md](../../../scripts/README.md)


