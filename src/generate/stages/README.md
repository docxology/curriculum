# Generation Stages

Course outline generation stage.

## Files

- `stage1_outline.py` - `OutlineGenerator` class for LLM-based outline generation

## Overview

This module provides the first stage of the course generation pipeline: creating comprehensive, structured course outlines. The `OutlineGenerator` creates both JSON-structured data and markdown-formatted documents.

## OutlineGenerator

Generates course outlines with:
- **Interactive mode** - User prompts and confirmations
- **Non-interactive mode** - Automated generation from config
- **JSON output** - Structured data for parsing
- **Markdown output** - Human-readable documents
- **Dual saving** - Both formats saved with timestamps

## Usage

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.stages.stage1_outline import OutlineGenerator

# Setup
loader = ConfigLoader("config")
llm_client = OllamaClient(loader.get_llm_parameters())
outline_gen = OutlineGenerator(loader, llm_client)

# Generate (interactive)
outline = outline_gen.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Smith",
    interactive=True
)

# Save
paths = outline_gen.save_outline(outline, "output/outlines")
```

## Key Methods

**generate_outline(course_name, instructor, duration, interactive)**
Generate complete outline in markdown format.

**generate_json_outline(course_name, instructor, duration, num_modules)**
Generate structured JSON outline.

**save_outline(outline_text, output_dir, json_data)**
Save outline in both markdown and JSON formats.

**_format_modules_list(modules)**
Format module list for prompt template.

**_extract_json_from_response(response)**
Parse JSON from LLM response (handles markdown wrapping).

## Output Formats

### Markdown
Human-readable outline with course metadata, modules, subtopics, and learning objectives.

Saved to: `output/outlines/course_outline_YYYYMMDD_HHMMSS.md`

### JSON
Structured data for programmatic processing and parsing.

Saved to: `output/outlines/course_outline_YYYYMMDD_HHMMSS.json`

## Interactive vs Non-Interactive

**Interactive** (`interactive=True`):
- Shows outline preview
- Prompts for user approval
- Allows regeneration
- Better for manual workflows

**Non-Interactive** (`interactive=False`):
- Uses config defaults
- No user prompts
- Automated execution
- Better for pipelines

## Integration

Used by:
- `ContentGenerator` - Main pipeline orchestrator
- `scripts/03_generate_outline.py` - CLI script
- `scripts/run_pipeline.py` - Full pipeline execution

Outputs consumed by:
- `OutlineParser` - Parses markdown to structured data
- Content generators - Use parsed modules for generation

## Testing

Tests in `tests/test_outline_generator.py` (requires Ollama):
```bash
uv run pytest tests/test_outline_generator.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - Complete API reference
- **Parser**: [../processors/README.md](../processors/README.md) - Parse outlines
- **Pipeline**: [../orchestration/README.md](../orchestration/README.md) - Full workflow
- **Scripts**: [../../../scripts/README.md](../../../scripts/README.md) - CLI usage


