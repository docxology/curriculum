# Content Processors

Parsing and processing utilities for course content.

## Files

- `parser.py` - `OutlineParser` class for markdown outline parsing
- `cleanup.py` - Content cleanup and validation utilities

## Overview

This module provides utilities for parsing and processing generated course content. The primary class `OutlineParser` transforms markdown outlines into structured data for further processing.

## OutlineParser

Parses markdown course outlines to extract:
- **Modules** - Individual course modules from level-2 headings
- **Subtopics** - Bullet-pointed subtopics from each module
- **Learning Objectives** - Educational objectives for each module
- **Metadata** - Course information from outline header
- **Course Title** - Main course title

## Usage

```python
from src.generate.processors.parser import OutlineParser

# Parse outline
parser = OutlineParser(outline_markdown_text)

# Extract modules
modules = parser.parse_modules()

# Extract metadata
metadata = parser.extract_metadata()
title = parser.get_course_title()

# Get complete structure
outline_dict = parser.to_dict()
```

## Key Methods

**parse_modules()**
Extract all modules as list of dicts with title and content.

**extract_subtopics(module_content)**
Extract subtopics from module content.

**extract_objectives(module_content)**
Extract learning objectives from module content.

**extract_metadata()**
Extract course metadata from outline header.

**get_course_title()**
Get main course title.

**get_module_count()**
Get number of modules.

**get_module_by_index(index)**
Get specific module by index.

**to_dict()**
Convert entire parsed outline to dictionary.

## Integration

**Input from**:
- `OutlineGenerator` - Markdown outlines

**Output to**:
- `ContentGenerator` - Module structure
- Content generators - Module information
- Scripts - Structured outline data

## Parsing Pattern

Detects standard markdown structure:
- Level-2 headings (`##`) for modules
- Bold key-value (`**Key**: Value`) for metadata
- Bullet lists (`-` or `*`) for subtopics and objectives
- Section headers (`### Subtopics`, `### Learning Objectives`)

## Testing

Tests in `tests/test_parser.py`:
```bash
uv run pytest tests/test_parser.py -v
```

Tests cover:
- Module extraction
- Subtopic/objective parsing
- Metadata extraction
- Edge cases and malformed input

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - API reference
- **Outline Generator**: [../stages/README.md](../stages/README.md) - Generate outlines
- **Content Generators**: [../formats/README.md](../formats/README.md) - Use parsed data

