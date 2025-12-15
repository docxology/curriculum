# Content Generation

Modular content generation system for educational course materials.

## Structure

```
generate/
├── orchestration/    # Pipeline coordination
│   └── pipeline.py      # ContentGenerator
├── stages/          # Generation stages
│   └── stage1_outline.py  # OutlineGenerator
├── processors/      # Content processing
│   └── parser.py        # OutlineParser
└── formats/         # Format-specific generators
    ├── __init__.py      # ContentGenerator base
    ├── lectures.py      # LectureGenerator
    ├── labs.py          # LabGenerator
    ├── study_notes.py   # StudyNotesGenerator
    ├── diagrams.py      # DiagramGenerator
    └── questions.py     # QuestionGenerator
```

## Submodules

### orchestration/
Pipeline coordination and workflow management.

**Main class**: `ContentGenerator`

Orchestrates the full generation workflow from outline to all content types.

See [orchestration/README.md](orchestration/README.md)

### stages/
Generation stages for the pipeline.

**Main class**: `OutlineGenerator`

Generates course outlines using LLM with customizable parameters.

See [stages/README.md](stages/README.md)

### processors/
Content processing and parsing.

**Main class**: `OutlineParser`

Parses markdown outlines into structured module data.

See [processors/README.md](processors/README.md)

### formats/
Format-specific content generators.

**Classes**:
- `ContentGenerator` - Base class
- `LectureGenerator` - Lectures
- `LabGenerator` - Lab exercises
- `StudyNotesGenerator` - Study notes
- `DiagramGenerator` - Mermaid diagrams
- `QuestionGenerator` - Questions

See [formats/README.md](formats/README.md)

## Quick Start

### Full Pipeline

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

loader = ConfigLoader("config")
generator = ContentGenerator(loader)

# Generate outline and all content
outline = generator.generate_outline()
results = generator.generate_content_for_all_modules()
```

### Individual Format

```python
from src.generate.formats.lectures import LectureGenerator

lecture_gen = LectureGenerator(loader, llm_client)
module = loader.get_module_by_id(1)
lecture = lecture_gen.generate_lecture(module)
```

## Import Patterns

```python
# Orchestration
from src.generate.orchestration.pipeline import ContentGenerator

# Stages
from src.generate.stages.stage1_outline import OutlineGenerator

# Processors
from src.generate.processors.parser import OutlineParser

# Formats
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator
```

## Content Types

**Primary Materials**:
- Lectures (comprehensive instructional content)
- Labs (laboratory exercises)
- Study Notes (concise summaries)
- Diagrams (Mermaid visualizations)
- Questions (assessments)

**Secondary Materials**:
- Application (real-world applications)
- Extension (advanced topics)
- Visualization (additional diagrams)
- Integration (cross-module connections)
- Investigation (research questions)
- Open Questions (ongoing scientific questions)

## Testing

All submodules have comprehensive tests:

```bash
# All generation tests
uv run pytest tests/test_*generator*.py tests/test_pipeline.py -v

# Specific tests
uv run pytest tests/test_outline_generator.py -v
uv run pytest tests/test_content_generators.py -v
uv run pytest tests/test_pipeline.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - Complete architecture overview
- **Orchestration Details**: [orchestration/README.md](orchestration/README.md)
- **Format Details**: [formats/README.md](formats/README.md)
- **Pipeline Guide**: [../../docs/PIPELINE_GUIDE.md](../../docs/PIPELINE_GUIDE.md)


