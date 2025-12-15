# Content Processors Module

Parsing and processing utilities for generated course content.

## Module Purpose

Provides `OutlineParser` class for parsing markdown course outlines into structured data. Extracts modules, subtopics, learning objectives, and metadata from LLM-generated text.

## Key Class: OutlineParser

```python
from src.generate.processors.parser import OutlineParser
```

### Initialization

```python
# Initialize with outline text
outline_text = """
# Introductory Biology - Course Outline

**Course Name**: Introductory Biology
**Instructor**: Dr. Smith

## Module 1: Cell Biology

### Subtopics
- Cell structure
- Organelles

### Learning Objectives
- Understand cell structure
- Identify organelles
"""

parser = OutlineParser(outline_text)
```

### Parse Modules

```python
# Extract all modules from outline
modules = parser.parse_modules()

# Returns list of dicts:
# [
#     {
#         "title": "Module 1: Cell Biology",
#         "content": "### Subtopics\n- Cell structure\n..."
#     },
#     ...
# ]

# Get module count
count = parser.get_module_count()

# Get specific module by index
module = parser.get_module_by_index(0)  # First module
```

### Extract Metadata

```python
# Extract course metadata from header
metadata = parser.extract_metadata()

# Returns:
# {
#     "course name": "Introductory Biology",
#     "instructor": "Dr. Smith",
#     "duration": "16 weeks",
#     "level": "Undergraduate"
# }

# Get course title
title = parser.get_course_title()
# Returns: "Introductory Biology"
```

### Extract Subtopics

```python
# Get module content
module = parser.get_module_by_index(0)
content = module["content"]

# Extract subtopics from module
subtopics = parser.extract_subtopics(content)

# Returns:
# ["Cell structure", "Organelles", "Cell membrane"]
```

### Extract Learning Objectives

```python
# Extract learning objectives from module
objectives = parser.extract_objectives(content)

# Returns:
# [
#     "Understand cell structure",
#     "Identify organelles",
#     "Explain membrane function"
# ]
```

### Complete Parsing

```python
# Parse entire outline to structured dict
outline_dict = parser.to_dict()

# Returns complete structure:
# {
#     "title": "Introductory Biology",
#     "metadata": {
#         "course name": "...",
#         "instructor": "...",
#         "duration": "..."
#     },
#     "modules": [
#         {
#             "title": "Module 1: Cell Biology",
#             "content": "...",
#             "subtopics": ["Cell structure", "Organelles"],
#             "objectives": ["Understand cell structure", ...]
#         },
#         ...
#     ]
# }
```

## Complete Workflow

```python
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.processors.parser import OutlineParser

# Generate outline
outline_gen = OutlineGenerator(loader, llm_client)
outline_md = outline_gen.generate_outline(
    course_name="Biology 101",
    instructor="Dr. Smith"
)

# Parse outline
parser = OutlineParser(outline_md)
modules = parser.parse_modules()

# Process each module
for module in modules:
    title = module["title"]
    content = module["content"]
    
    subtopics = parser.extract_subtopics(content)
    objectives = parser.extract_objectives(content)
    
    print(f"{title}")
    print(f"  Subtopics: {len(subtopics)}")
    print(f"  Objectives: {len(objectives)}")
```

## Integration with Content Generation

```python
from src.generate.processors.parser import OutlineParser
from src.generate.formats.lectures import LectureGenerator

# Parse outline
parser = OutlineParser(outline_text)
parsed = parser.to_dict()

# Generate content for each module
lecture_gen = LectureGenerator(loader, llm_client)

for module in parsed["modules"]:
    module_info = {
        "name": module["title"],
        "subtopics": module["subtopics"],
        "learning_objectives": module["objectives"]
    }
    
    lecture = lecture_gen.generate_lecture(module_info)
```

## Parsing Patterns

### Module Detection

Modules are detected by level-2 headings:

```markdown
## Module 1: Cell Biology
## Module 2: Genetics
```

Pattern: `^##\s+(.+)$`

### Subtopics Detection

Subtopics are bullet points in subtopics section:

```markdown
### Subtopics
- Cell structure
- Organelles
- Membranes
```

Detected when line starts with `-` or `*` in subtopics section.

### Objectives Detection

Objectives are bullet points in objectives section:

```markdown
### Learning Objectives
- Understand cell structure
- Identify organelles
```

Detected when line starts with `-` or `*` in objectives/learning section.

### Metadata Detection

Metadata uses bold key-value pattern:

```markdown
**Course Name**: Introductory Biology
**Instructor**: Dr. Smith
```

Pattern: `\*\*(.+?)\*\*:\s*(.+?)$`

## Error Handling

```python
try:
    parser = OutlineParser(outline_text)
    modules = parser.parse_modules()
    
    if not modules:
        logger.warning("No modules found in outline")
    
    for i, module in enumerate(modules):
        subtopics = parser.extract_subtopics(module["content"])
        if not subtopics:
            logger.warning(f"No subtopics found in module {i+1}")
            
except IndexError as e:
    logger.error(f"Module index out of range: {e}")
except Exception as e:
    logger.error(f"Parsing error: {e}")
```

## Caching

Parser caches parsed results to avoid re-processing:

```python
parser = OutlineParser(outline_text)

# First call parses and caches
modules1 = parser.parse_modules()

# Second call returns cached result
modules2 = parser.parse_modules()

# Same for metadata
metadata1 = parser.extract_metadata()
metadata2 = parser.extract_metadata()  # Cached
```

## Testing

Tests in `tests/test_parser.py`:
- Module parsing
- Subtopic extraction
- Objective extraction
- Metadata extraction
- Edge cases (empty sections, malformed markdown)

Run tests:
```bash
uv run pytest tests/test_parser.py -v
```

## Common Patterns

### Parse and Validate

```python
def parse_and_validate(outline_text):
    parser = OutlineParser(outline_text)
    parsed = parser.to_dict()
    
    # Validate structure
    if not parsed["modules"]:
        raise ValueError("No modules found")
    
    for module in parsed["modules"]:
        if not module["subtopics"]:
            logger.warning(f"Module {module['title']} has no subtopics")
        if not module["objectives"]:
            logger.warning(f"Module {module['title']} has no objectives")
    
    return parsed
```

### Extract Module Summary

```python
def get_module_summary(parser, module_index):
    module = parser.get_module_by_index(module_index)
    content = module["content"]
    
    return {
        "title": module["title"],
        "num_subtopics": len(parser.extract_subtopics(content)),
        "num_objectives": len(parser.extract_objectives(content))
    }
```

## Parsing Pattern Reference

### Regex Patterns Used

#### Module Detection
```python
# Pattern: Level-2 headings (##)
pattern = r'^##\s+(.+)$'
# Matches: "## Module 1: Cell Biology"
```

#### Subtopic Detection
```python
# Pattern: Bullet points in subtopics section
pattern = r'^[-*]\s+(.+)$'
# Matches: "- Cell structure", "* Organelles"
# Context: Must be within "### Subtopics" section
```

#### Objective Detection
```python
# Pattern: Bullet points in objectives section
pattern = r'^[-*]\s+(.+)$'
# Matches: "- Understand cell structure"
# Context: Must be within "### Learning Objectives" or "### Objectives" section
```

#### Metadata Detection
```python
# Pattern: Bold key-value pairs
pattern = r'\*\*(.+?)\*\*:\s*(.+?)$'
# Matches: "**Course Name**: Introductory Biology"
# Extracts: key="Course Name", value="Introductory Biology"
```

### Edge Case Handling

**Empty sections**: Returns empty list `[]` instead of raising error

**Malformed markdown**: Attempts to parse what it can, logs warnings for unparseable sections

**Unicode handling**: Supports Unicode characters in module names, subtopics, objectives

**Multiple formats**: Handles variations in heading levels, bullet styles, spacing

**Missing metadata**: Returns partial metadata dict with available fields

## Content Cleanup Utilities

The `cleanup.py` module provides post-generation content cleanup functions:

```python
from src.generate.processors.cleanup import (
    clean_conversational_artifacts,
    standardize_placeholders,
    remove_word_count_statements,
    remove_duplicate_headings,
    validate_content,
    full_cleanup_pipeline,
    batch_validate_materials
)

# Clean conversational artifacts from LLM output
cleaned = clean_conversational_artifacts(content)
# Removes: "Okay, here's...", "I understand the requirements...", 
#          "I have carefully adhered...", "the output following...", etc.

# Standardize placeholders (instructor names, dates)
standardized = standardize_placeholders(content)
# Replaces: "Dr. Smith" → "[INSTRUCTOR]", "January 15, 2024" → "[DATE]"

# Remove word count statements
no_counts = remove_word_count_statements(content)
# Removes: "Word Count: 198 words", "Total: 1021 words", etc.

# Remove duplicate markdown headings
no_duplicates = remove_duplicate_headings(content)
# Removes duplicate headings at same level, keeps first occurrence

# Validate content quality
validation_result = validate_content(content, content_type="lecture")

# Full cleanup pipeline (content-type aware)
cleaned_content, validation = full_cleanup_pipeline(content, content_type="lecture")
# For "visualization" or "diagram" content_type, applies Mermaid-specific cleanup
# For markdown content, applies duplicate heading removal

# Batch validate multiple materials
materials = {"lecture": lecture_text, "lab": lab_text}
results = batch_validate_materials(materials)
```

**Cleanup Features**:

- **Conversational Artifact Removal**: Removes informal phrases, meta-commentary, and prompts
- **Placeholder Standardization**: Replaces specific names/dates with generic placeholders
- **Word Count Removal**: Strips LLM-generated word count statements
- **Duplicate Heading Removal**: Removes duplicate markdown headings (markdown content only)
- **Mermaid Diagram Cleanup**: For visualization/diagram content, removes code fences, linkStyle commands, style commands, and explanatory text
- **Content-Type Aware**: `full_cleanup_pipeline()` applies appropriate cleanup based on content type

These utilities are used internally by content generators to ensure professional output quality.

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide with examples
- **Outline Generator**: [../stages/AGENTS.md](../stages/AGENTS.md) - Generate outlines
- **Content Generators**: [../formats/AGENTS.md](../formats/AGENTS.md) - Use parsed data
- **Pipeline**: [../orchestration/AGENTS.md](../orchestration/AGENTS.md) - Complete workflow
- **Test Files**: [../../../tests/test_parser.py](../../../tests/test_parser.py), [../../../tests/test_parser_edge_cases.py](../../../tests/test_parser_edge_cases.py), [../../../tests/test_cleanup.py](../../../tests/test_cleanup.py) - Parser and cleanup tests


