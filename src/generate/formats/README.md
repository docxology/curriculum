# Format Generators

Specialized generators for each content format.

## Files

- `__init__.py` - `ContentGenerator` base class
- `lectures.py` - `LectureGenerator`
- `labs.py` - `LabGenerator`
- `study_notes.py` - `StudyNotesGenerator`
- `diagrams.py` - `DiagramGenerator`
- `questions.py` - `QuestionGenerator`

## Overview

This module provides specialized generators for each content format. All generators inherit from `ContentGenerator` base class and use LLM with format-specific prompt templates.

## Generators

### ContentGenerator (Base)
Base class providing:
- Configuration access via `config_loader`
- LLM access via `llm_client`
- Common initialization pattern

### LectureGenerator
Generates lecture content (2000-4000 words).

**Methods**:
- `generate_lecture(module_info)` - Generate lecture
- `save_lecture(lecture, module_info, output_dir)` - Save to file

### LabGenerator
Generates laboratory exercises with procedures and safety notes.

**Methods**:
- `generate_lab(module_info, lab_number, lecture_context)` - Single lab
- `generate_labs(module_info, num_labs, lecture_context)` - Multiple labs
- `save_lab(lab, module_info, lab_number, output_dir)` - Save to file

### StudyNotesGenerator
Generates concise review summaries.

**Methods**:
- `generate_study_notes(module_info, lecture_context, lab_context)` - Generate notes
- `save_study_notes(notes, module_info, output_dir)` - Save to file

### DiagramGenerator
Generates Mermaid diagrams for visual concepts.

**Methods**:
- `generate_diagram(topic, context)` - Single diagram
- `generate_diagrams(module_info, num_diagrams)` - Multiple diagrams
- `save_diagram(diagram, topic, module_id, num, output_dir)` - Save to file

### QuestionGenerator
Generates comprehension questions (MC/SA/Essay).

**Methods**:
- `generate_questions(module_info, lecture_context, lab_context)` - Generate questions
- `save_questions(questions, module_info, output_dir)` - Save to file

## Usage

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator

# Setup
loader = ConfigLoader("config")
llm_client = OllamaClient(loader.get_llm_parameters())

# Create generator
lecture_gen = LectureGenerator(loader, llm_client)

# Generate content
module = loader.get_module_by_id(1)
lecture = lecture_gen.generate_lecture(module)

# Save
# Session-based structure
session_dir = Path("output/modules/module_01_cell_biology/session_01")
session_dir.mkdir(parents=True, exist_ok=True)
path = lecture_gen.save_lecture(lecture, module, session_dir)
```

## Integration

**Uses**:
- `ConfigLoader` - Get prompt templates
- `OllamaClient` - Generate text
- `utils.helpers` - File operations

**Used by**:
- `ContentGenerator` - Pipeline orchestration
- Scripts - CLI generation

## Format Specifications

Each generator produces specific format defined in [../../../docs/FORMATS.md](../../../docs/FORMATS.md):

- **Lectures**: 2000-4000 words, pedagogically structured
- **Labs**: Detailed procedures, safety notes, expected results
- **Study Notes**: Concise, well-organized, key concepts
- **Diagrams**: Mermaid syntax, clear labels
- **Questions**: Mix of MC/SA/Essay, varying difficulty

## Testing

Tests in `tests/test_content_generators.py` and `tests/test_new_generators.py`:
```bash
uv run pytest tests/test_content_generators.py tests/test_new_generators.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - API reference
- **Format Details**: [../../../docs/FORMATS.md](../../../docs/FORMATS.md)
- **Pipeline**: [../orchestration/README.md](../orchestration/README.md)


