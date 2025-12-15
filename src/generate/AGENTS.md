# Content Generation Module

Course content generation with modular architecture for different content types.

## Module Purpose

Coordinates all content generation activities through specialized submodules: orchestration (pipeline management), stages (outline generation), processors (parsing), and formats (lectures, labs, diagrams, questions, study notes).

## Architecture

```
generate/
├── orchestration/    # Pipeline coordination (ContentGenerator)
├── stages/          # Generation stages (OutlineGenerator)
├── processors/      # Content processing (OutlineParser)
└── formats/         # Format generators (Lecture, Lab, StudyNotes, Diagram, Question)
```

## Submodules

### orchestration/
Pipeline coordination and workflow management.

**Key class**: `ContentGenerator`

Orchestrates the complete generation workflow:
1. Generate course outline
2. Parse outline into modules
3. Generate content for each module (all formats)

See [orchestration/AGENTS.md](orchestration/AGENTS.md)

### stages/
Generation stages for different pipeline phases.

**Key class**: `OutlineGenerator`

Generates course outlines using LLM with interactive or non-interactive modes.

See [stages/AGENTS.md](stages/AGENTS.md)

### processors/
Content processing and parsing utilities.

**Key class**: `OutlineParser`

Parses markdown outlines into structured data (modules, subtopics, objectives).

See [processors/AGENTS.md](processors/AGENTS.md)

### formats/
Format-specific content generators.

**Key classes**:
- `ContentGenerator` - Base class for all generators
- `LectureGenerator` - Comprehensive lectures (2000-4000 words)
- `LabGenerator` - Laboratory exercises with procedures
- `StudyNotesGenerator` - Concise review summaries
- `DiagramGenerator` - Mermaid visualizations
- `QuestionGenerator` - Multiple choice, short answer, essay questions

See [formats/AGENTS.md](formats/AGENTS.md)

## Usage Patterns

### Full Pipeline Execution

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

# Initialize
loader = ConfigLoader("config")
generator = ContentGenerator(loader)

# Run full pipeline
outline = generator.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Smith"
)

results = generator.generate_content_for_all_modules()
```

### Stage-by-Stage Execution

```python
# Stage 1: Generate outline
from src.generate.stages.stage1_outline import OutlineGenerator

outline_gen = OutlineGenerator(loader, llm_client)
outline = outline_gen.generate_outline(
    course_name="Biology 101",
    instructor="Dr. Jones"
)
outline_gen.save_outline(outline, "output/outlines")

# Stage 2: Parse outline
from src.generate.processors.parser import OutlineParser

parser = OutlineParser(outline)
modules = parser.parse_modules()

# Stage 3: Generate content
from src.generate.formats.lectures import LectureGenerator

lecture_gen = LectureGenerator(loader, llm_client)
for module_info in modules:
    for session in module_info.get('sessions', []):
        session_dir = Path(f"output/modules/module_{module_info['module_id']:02d}_{module_info['module_name'].lower().replace(' ', '_')}/session_{session['session_number']:02d}")
        session_dir.mkdir(parents=True, exist_ok=True)
        lecture = lecture_gen.generate_lecture(
            module_info,
            session_number=session['session_number'],
            session_title=session['session_title']
        )
        lecture_gen.save_lecture(lecture, module_info, session_dir)
```

### Single Format Generation

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.diagrams import DiagramGenerator

# Setup
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# Generate diagrams
diagram_gen = DiagramGenerator(loader, client)
module = loader.get_module_by_id(1)

# Generate for first session
session = module.get('sessions', [{}])[0]
session_dir = Path(f"output/modules/module_{module['module_id']:02d}_{module['module_name'].lower().replace(' ', '_')}/session_{session.get('session_number', 1):02d}")
session_dir.mkdir(parents=True, exist_ok=True)
diagrams = diagram_gen.generate_diagrams(module, num_diagrams=3)
for i, diagram in enumerate(diagrams, 1):
    diagram_gen.save_diagram(diagram, module.get('subtopics', ['Overview'])[i-1] if i <= len(module.get('subtopics', [])) else "Overview", module['module_id'], i, session_dir)
```

## Common Tasks

### Generate All Primary Content for Module

```python
from src.generate.orchestration.pipeline import ContentGenerator

generator = ContentGenerator(loader)

# Generate for specific module
module_id = 1
results = generator.generate_content_for_module(module_id)

# Results contain:
# - lecture: Markdown text
# - labs: List of lab exercises
# - study_notes: Markdown summary
# - diagrams: List of Mermaid diagrams
# - questions: Markdown with MC/SA/Essay
```

### Generate Secondary Content

```python
from src.generate.orchestration.pipeline import ContentGenerator

generator = ContentGenerator(loader)

# Generate secondary materials
module_id = 1
secondary_types = ["application", "extension", "visualization"]

for content_type in secondary_types:
    content = generator.generate_secondary_content(module_id, content_type)
    # Save to output/module_XX/{content_type}/
```

### Custom Content Generation

```python
from src.generate.formats import ContentGenerator
from src.llm.client import OllamaClient

class CustomGenerator(ContentGenerator):
    """Custom content generator."""
    
    def generate_custom(self, module_info):
        prompt_template = loader.get_prompt_template("custom")
        
        variables = {
            "module_name": module_info["name"],
            "topic": module_info["subtopics"][0]
        }
        
        content = self.llm_client.generate_with_template(
            template=prompt_template["template"],
            variables=variables,
            system_prompt=prompt_template["system"]
        )
        
        return content

# Use custom generator
custom_gen = CustomGenerator(loader, client)
content = custom_gen.generate_custom(module)
```

## Error Handling

All generators follow the "safe-to-fail" pattern:

```python
from src.generate.orchestration.pipeline import ContentGenerator

generator = ContentGenerator(loader)

# Collect errors, continue processing
results, errors = generator.generate_content_for_all_modules()

if errors:
    logger.warning(f"Generation completed with {len(errors)} errors")
    for error in errors:
        logger.error(f"Module {error['module_id']}: {error['error']}")
else:
    logger.info("All content generated successfully")
```

## Integration Points

### Configuration Integration
All generators use `ConfigLoader` for:
- Module information
- Prompt templates
- Output paths
- Generation parameters

### LLM Integration
All generators use `OllamaClient` for:
- Text generation
- Template formatting
- Retry logic
- Error handling

### File I/O Integration
All generators use helpers from `utils.helpers` for:
- Directory management (`ensure_directory`)
- File naming (`slugify`, `format_module_filename`)
- Markdown saving (`save_markdown`)

## Testing

Comprehensive tests for all submodules:

```bash
# Test outline generation
uv run pytest tests/test_outline_generator.py -v

# Test content generators
uv run pytest tests/test_content_generators.py -v
uv run pytest tests/test_new_generators.py -v

# Test full pipeline
uv run pytest tests/test_pipeline.py -v

# Test parser
uv run pytest tests/test_parser.py -v
```

## Content Quality

All generated content follows standards defined in [../../docs/FORMATS.md](../../docs/FORMATS.md):

- **Lectures**: 2000-4000 words, comprehensive, pedagogically structured
- **Labs**: Detailed procedures, safety notes, expected results
- **Study Notes**: Concise, well-organized, key concepts highlighted
- **Diagrams**: Clear Mermaid syntax, informative labels
- **Questions**: Mix of MC/SA/Essay, varying difficulty levels

## Submodule Interaction Patterns

### Data Flow

```
OutlineGenerator (stages/)
    ↓ (generates JSON + Markdown outline)
OutlineParser (processors/)
    ↓ (parses into structured modules)
ContentGenerator (orchestration/)
    ↓ (coordinates generation)
Format Generators (formats/)
    ├── LectureGenerator
    ├── LabGenerator
    ├── StudyNotesGenerator
    ├── DiagramGenerator
    └── QuestionGenerator
    ↓ (generates content)
Output Files (output/modules/)
```

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: Outline Generation (stages/stage1_outline.py) │
│  - Generate JSON outline with LLM                       │
│  - Generate Markdown outline                           │
│  - Save to output/outlines/                            │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 2: Outline Parsing (processors/parser.py)        │
│  - Parse Markdown outline                               │
│  - Extract modules, subtopics, objectives              │
│  - Return structured data                              │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 3: Content Generation (orchestration/pipeline.py)│
│  - Load modules from JSON outline                       │
│  - For each session:                                    │
│    ├── Generate lecture (formats/lectures.py)          │
│    ├── Generate labs (formats/labs.py)                 │
│    ├── Generate study notes (formats/study_notes.py)   │
│    ├── Generate diagrams (formats/diagrams.py)          │
│    └── Generate questions (formats/questions.py)        │
│  - Save to output/modules/module_XX/session_YY/        │
└─────────────────────────────────────────────────────────┘
```

### Output Structure Reference

```
output/
├── outlines/
│   ├── course_outline_TIMESTAMP.json  # JSON structure
│   └── course_outline_TIMESTAMP.md    # Markdown format
└── modules/
    └── module_01_molecular_foundations/
        ├── session_01/                # Primary materials (per session)
        │   ├── lecture.md
        │   ├── lab.md
        │   ├── study_notes.md
        │   ├── diagram_1.mmd
        │   ├── diagram_2.mmd
        │   └── questions.md
        ├── session_02/
        │   └── ...
        # Secondary materials (session-level, saved directly in session folders):
        # session_01/application.md
        # session_01/extension.md
        # session_01/visualization.mmd
        # session_01/integration.md
        # session_01/investigation.md
        # session_01/open_questions.md
```

## See Also

- **For Humans**: [README.md](README.md) - Human-readable overview with usage examples
- **Orchestration**: [orchestration/AGENTS.md](orchestration/AGENTS.md) - Pipeline coordination, session-based generation
- **Stages**: [stages/AGENTS.md](stages/AGENTS.md) - Outline generation, interactive/non-interactive modes
- **Processors**: [processors/AGENTS.md](processors/AGENTS.md) - Outline parsing, content cleanup, edge cases
- **Formats**: [formats/AGENTS.md](formats/AGENTS.md) - Format generators (lectures, labs, notes, diagrams, questions)
- **Pipeline Guide**: [../../docs/PIPELINE_GUIDE.md](../../docs/PIPELINE_GUIDE.md) - Complete pipeline documentation
- **Format Specifications**: [../../docs/FORMATS.md](../../docs/FORMATS.md) - Content format details
- **JSON Outline**: [../../docs/JSON_OUTLINE.md](../../docs/JSON_OUTLINE.md) - Outline format and lifecycle


