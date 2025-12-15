# Outline Generation Stage

Course outline generation with interactive and non-interactive modes.

## Module Purpose

Provides `OutlineGenerator` class for creating comprehensive course outlines using LLM. Generates both JSON-structured and markdown-formatted outlines with interactive user prompts or automated configuration-driven generation.

## Key Class: OutlineGenerator

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.stages.stage1_outline import OutlineGenerator
```

### Initialization

```python
# Initialize with configuration
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

outline_gen = OutlineGenerator(loader, client)
```

### Outline Generation

#### Interactive Mode (Default)

```python
# Generate with user prompts
outline_markdown = outline_gen.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Jane Smith",
    duration="16 weeks",
    interactive=True  # Prompts for confirmation
)

# Returns markdown outline
# Also saves JSON version internally
```

#### Non-Interactive Mode

```python
# Generate without prompts (uses config defaults)
outline_markdown = outline_gen.generate_outline(
    course_name="Biology 101",
    instructor="Dr. John Doe",
    interactive=False
)

# Uses defaults from course_config.yaml
```

### JSON Outline Generation

```python
# Generate JSON-structured outline
json_outline = outline_gen.generate_json_outline(
    course_name="Advanced Biology",
    instructor="Dr. Smith",
    duration="16 weeks",
    num_modules=20
)

# Returns dict with structure:
# {
#     "course_name": "...",
#     "instructor": "...",
#     "modules": [
#         {
#             "id": 1,
#             "name": "...",
#             "subtopics": [...],
#             "learning_objectives": [...]
#         },
#         ...
#     ]
# }
```

### Saving Outlines

```python
# Save outline to file
output_dir = "output/outlines"
saved_paths = outline_gen.save_outline(
    outline_markdown,
    output_dir,
    json_data=json_outline  # Optional JSON data
)

# Returns:
# {
#     "markdown": Path("output/outlines/course_outline_20241208_143022.md"),
#     "json": Path("output/outlines/course_outline_20241208_143022.json")
# }
```

## Complete Workflow

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.stages.stage1_outline import OutlineGenerator

# Setup
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)
outline_gen = OutlineGenerator(loader, client)

# Generate outline
outline_md = outline_gen.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Smith",
    duration="16 weeks",
    interactive=True
)

# Save to file
paths = outline_gen.save_outline(outline_md, "output/outlines")
print(f"Saved: {paths['markdown']}")
print(f"JSON: {paths['json']}")
```

## JSON Extraction and Parsing

The generator handles various response formats from LLM:

```python
# Internally used method
json_data = outline_gen._extract_json_from_response(llm_response)

# Handles:
# 1. JSON in markdown code blocks (```json {...} ```)
# 2. JSON in plain code blocks (``` {...} ```)
# 3. Raw JSON in response
# 4. Multiple JSON objects (takes first valid one)
```

## Module Formatting

```python
# Format modules for prompt
modules = loader.get_modules()
formatted = outline_gen._format_modules_list(modules)

# Output:
# 1. Introduction to Biology
#    - Scientific Method
#    - Characteristics of Life
# 2. Chemistry of Life
#    - Atoms and Molecules
#    - Water and pH
```

## Interactive Prompting

When `interactive=True`, the generator:
1. Shows proposed outline structure
2. Prompts for confirmation
3. Allows regeneration if not satisfied
4. Saves only after approval

```python
# Interactive workflow
outline = outline_gen.generate_outline(
    course_name="Biology",
    instructor="Dr. Smith",
    interactive=True
)

# Console output:
# ================================================================================
# PROPOSED COURSE OUTLINE
# ================================================================================
# [outline preview...]
# 
# Accept this outline? (y/n): y
# Generating final outline...
```

## Configuration Integration

Uses prompt templates from `llm_config.yaml`:

```python
# Loads template
prompt_config = loader.get_prompt_template("outline")
system_prompt = prompt_config["system"]
template = prompt_config["template"]

# Template variables:
# - {course_name}
# - {instructor}
# - {duration}
# - {modules_list}
# - {num_modules}
```

## Output Format

### Markdown Outline

```markdown
# Introductory Biology - Course Outline

**Course Name**: Introductory Biology
**Instructor**: Dr. Jane Smith
**Duration**: 16 weeks
**Level**: Undergraduate

## Module 1: Introduction to Biology and Scientific Method

### Subtopics
- Nature of science
- Scientific method
- Experimental design

### Learning Objectives
- Understand the scientific method
- Design controlled experiments
- Analyze experimental data
```

### JSON Outline

```json
{
  "course_name": "Introductory Biology",
  "instructor": "Dr. Jane Smith",
  "duration": "16 weeks",
  "modules": [
    {
      "id": 1,
      "name": "Introduction to Biology",
      "subtopics": ["Nature of science", "Scientific method"],
      "learning_objectives": ["Understand scientific method"]
    }
  ]
}
```

## Error Handling

```python
from src.llm.client import LLMError

try:
    outline = outline_gen.generate_outline(
        course_name="Biology",
        instructor="Dr. Smith"
    )
except LLMError as e:
    logger.error(f"Outline generation failed: {e}")
    # Handle connection errors, timeouts, etc.
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Integration with Pipeline

```python
from src.generate.orchestration.pipeline import ContentGenerator

# Pipeline uses OutlineGenerator internally
generator = ContentGenerator(loader)

# Generates outline through pipeline
outline = generator.generate_outline(
    course_name="Biology 101",
    instructor="Dr. Smith"
)
```

## Testing

Tests in `tests/test_outline_generator.py`:
- Outline generation
- JSON extraction
- Markdown formatting
- File saving
- Interactive mode

**Requires Ollama + gemma3:4b model**

Run tests:
```bash
uv run pytest tests/test_outline_generator.py -v
```

## Performance

Typical timing:
- JSON outline generation: 20-40s
- Markdown formatting: <1s
- Total: 30-60s per outline

Generation is cached - subsequent calls use same outline unless regenerated.

## Interactive vs Non-Interactive Mode

### Interactive Mode (Default)

**Behavior**:
- Prompts user for course metadata (name, level, description)
- Prompts for structure (num_modules, total_sessions)
- Prompts for content bounds (subtopics, objectives, concepts per session)
- Shows proposed outline for approval
- Allows regeneration if not satisfied

**Use case**: Manual course creation, customization

**Example**:
```python
outline = outline_gen.generate_outline(
    course_name="Biology",
    instructor="Dr. Smith",
    interactive=True  # Default
)
# Console prompts appear for customization
```

### Non-Interactive Mode

**Behavior**:
- Uses all defaults from `course_config.yaml`
- No user prompts
- Generates outline immediately
- Critical for automation/CI/CD

**Use case**: Automated generation, hands-off execution

**Example**:
```python
outline = outline_gen.generate_outline(
    course_name="Biology",
    instructor="Dr. Smith",
    interactive=False  # No prompts
)
# Uses config defaults, generates immediately
```

## Prompt Template Variables

The outline generator uses prompt templates from `llm_config.yaml` with these variables:

**Template variables**:
- `{course_name}` - Course name
- `{instructor}` - Instructor name
- `{duration}` - Course duration (e.g., "16 weeks")
- `{num_modules}` - Number of modules to generate
- `{total_sessions}` - Total class sessions
- `{modules_list}` - Formatted list of existing modules (if any)
- `{additional_constraints}` - Additional requirements from config

**Template location**: `llm_config.yaml` → `prompts.outline`

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide with examples
- **Parser**: [../processors/AGENTS.md](../processors/AGENTS.md) - Parse generated outlines
- **Pipeline**: [../orchestration/AGENTS.md](../orchestration/AGENTS.md) - Full workflow
- **Configuration**: [../../config/AGENTS.md](../../config/AGENTS.md) - Prompt templates, JSON outline discovery
- **Scripts**: [../../../scripts/AGENTS.md](../../../scripts/AGENTS.md) - Script 03 usage and CLI options
- **JSON Outline**: [../../../docs/JSON_OUTLINE.md](../../../docs/JSON_OUTLINE.md) - Outline format specification


