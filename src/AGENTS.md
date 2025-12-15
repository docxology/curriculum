# educational course Package - For AI Agents

Python package for AI-powered educational course materials generation.

## Package Purpose

This is the main Python package containing all source code for the educational course Generator. It provides a modular architecture with clear separation of concerns across configuration, LLM integration, content generation, and utilities.

## Module Organization

The package is organized into focused submodules:

```
src/
├── config/          # Configuration management (ConfigLoader)
├── llm/             # LLM integration (OllamaClient)
├── generate/        # Content generation (all generators)
│   ├── orchestration/  # Pipeline coordination (ContentGenerator)
│   ├── stages/         # Generation stages (OutlineGenerator)
│   ├── processors/     # Content processing (OutlineParser, cleanup)
│   └── formats/        # Format generators (Lecture, Lab, StudyNotes, Diagram, Question)
├── setup/           # Package initialization (currently minimal)
├── utils/           # Utility functions (file I/O, text processing, system checks)
└── website/         # Website generation (WebsiteGenerator)
```

## Key Classes

### Configuration
- **`ConfigLoader`** (`config/loader.py`) - YAML configuration loading and validation

### LLM Integration
- **`OllamaClient`** (`llm/client.py`) - Ollama API client with retry logic

### Pipeline Orchestration
- **`ContentGenerator`** (`generate/orchestration/pipeline.py`) - Main pipeline coordinator

### Generation Stages
- **`OutlineGenerator`** (`generate/stages/stage1_outline.py`) - Course outline generation

### Content Processing
- **`OutlineParser`** (`generate/processors/parser.py`) - Outline parsing
- **Content cleanup utilities** (`generate/processors/cleanup.py`) - Markdown cleanup and validation

### Format Generators
- **`ContentGenerator`** (`generate/formats/__init__.py`) - Base class
- **`LectureGenerator`** (`generate/formats/lectures.py`) - Comprehensive lectures
- **`LabGenerator`** (`generate/formats/labs.py`) - Laboratory exercises
- **`StudyNotesGenerator`** (`generate/formats/study_notes.py`) - Concise summaries
- **`DiagramGenerator`** (`generate/formats/diagrams.py`) - Mermaid visualizations
- **`QuestionGenerator`** (`generate/formats/questions.py`) - Assessment questions

### Website Generation
- **`WebsiteGenerator`** (`website/generator.py`) - Single HTML website generation

### Utilities
- **Helper functions** (`utils/helpers.py`) - File I/O, text processing, system validation

## Complete Import Reference

### Configuration Module
```python
from src.config.loader import ConfigLoader, ConfigurationError
```

**Key class**: `ConfigLoader`  
**Location**: `src/config/loader.py`  
**Documentation**: [config/AGENTS.md](config/AGENTS.md)

### LLM Integration Module
```python
from src.llm.client import OllamaClient, LLMError
```

**Key class**: `OllamaClient`  
**Location**: `src/llm/client.py`  
**Documentation**: [llm/AGENTS.md](llm/AGENTS.md)

### Pipeline Orchestration Module
```python
from src.generate.orchestration.pipeline import ContentGenerator
```

**Key class**: `ContentGenerator`  
**Location**: `src/generate/orchestration/pipeline.py`  
**Documentation**: [generate/orchestration/AGENTS.md](generate/orchestration/AGENTS.md)

### Generation Stages Module
```python
from src.generate.stages.stage1_outline import OutlineGenerator
```

**Key class**: `OutlineGenerator`  
**Location**: `src/generate/stages/stage1_outline.py`  
**Documentation**: [generate/stages/AGENTS.md](generate/stages/AGENTS.md)

### Content Processing Module
```python
from src.generate.processors.parser import OutlineParser
from src.generate.processors.cleanup import ContentCleanup
```

**Key classes**: `OutlineParser`, `ContentCleanup`  
**Location**: `src/generate/processors/parser.py`, `src/generate/processors/cleanup.py`  
**Documentation**: [generate/processors/AGENTS.md](generate/processors/AGENTS.md)

### Format Generators Module
```python
from src.generate.formats import ContentGenerator as BaseGenerator
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator
```

**Key classes**: `LectureGenerator`, `LabGenerator`, `StudyNotesGenerator`, `DiagramGenerator`, `QuestionGenerator`  
**Location**: `src/generate/formats/*.py`  
**Documentation**: [generate/formats/AGENTS.md](generate/formats/AGENTS.md)

### Website Generation Module
```python
from src.website.generator import WebsiteGenerator
```

**Key class**: `WebsiteGenerator`  
**Location**: `src/website/generator.py`  
**Documentation**: [website/AGENTS.md](website/AGENTS.md)

### Utilities Module
```python
from src.utils.helpers import (
    ensure_directory, save_markdown, load_markdown,
    slugify, sanitize_filename, truncate_text, count_words,
    format_timestamp, format_module_filename,
    ollama_is_running, ensure_model_available, ensure_uv_available,
    run_cmd_capture
)
```

**Key functions**: File I/O, text processing, system utilities  
**Location**: `src/utils/helpers.py`  
**Documentation**: [utils/AGENTS.md](utils/AGENTS.md)

### Logging Setup
```python
from src.utils.logging_setup import setup_logging
```

**Location**: `src/utils/logging_setup.py`  
**Documentation**: See [.cursorrules/04-logging-unified.md](../.cursorrules/04-logging-unified.md)

## Usage Example

```python
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

# Initialize configuration
loader = ConfigLoader("config")
loader.validate_all_configs()

# Create pipeline
generator = ContentGenerator(loader)

# Generate outline
outline = generator.generate_outline(
    course_name="Introductory Biology",
    instructor="Dr. Smith"
)

# Generate all content
results = generator.generate_content_for_all_modules()
```

## Module Dependency Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Layer                       │
│  ConfigLoader (config/loader.py)                             │
│  - Loads YAML configs (course, llm, output)                 │
│  - Discovers JSON outlines                                   │
│  - Validates configuration                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM Layer                               │
│  OllamaClient (llm/client.py)                                │
│  - HTTP client for Ollama API                                │
│  - Retry logic, streaming, request tracing                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Generation Layer                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  OutlineGenerator (stages/stage1_outline.py)         │   │
│  │  - Generates JSON + Markdown outlines                │   │
│  └───────────────────┬───────────────────────────────────┘   │
│                      │                                         │
│                      ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  OutlineParser (processors/parser.py)                │   │
│  │  - Parses markdown outlines                          │   │
│  └───────────────────┬───────────────────────────────────┘   │
│                      │                                         │
│                      ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ContentGenerator (orchestration/pipeline.py)        │   │
│  │  - Orchestrates full pipeline                        │   │
│  └───────────────────┬─────────────────────────────────┘   │
│                      │                                         │
│        ┌─────────────┼─────────────┬─────────────┐           │
│        ▼             ▼             ▼             ▼           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │Lecture  │  │   Lab   │  │  Study  │  │Diagram  │         │
│  │Generator│  │Generator│  │  Notes  │  │Generator│         │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │
│                                                               │
│  ┌─────────┐                                                  │
│  │Question │                                                  │
│  │Generator│                                                  │
│  └─────────┘                                                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Website Layer                              │
│  WebsiteGenerator (website/generator.py)                     │
│  - Generates single HTML website                             │
│  - Uses content from all modules                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Utility Layer                             │
│  helpers.py (utils/helpers.py)                               │
│  - File I/O, text processing, system checks                  │
│  - Used by all modules                                       │
└─────────────────────────────────────────────────────────────┘
```

## File Location Map

| Module | Key Files | Purpose |
|--------|-----------|---------|
| **config/** | `loader.py` | ConfigLoader class, YAML loading, JSON outline discovery |
| **llm/** | `client.py` | OllamaClient class, HTTP client, retry logic, streaming |
| **generate/orchestration/** | `pipeline.py` | ContentGenerator class, full pipeline coordination |
| **generate/stages/** | `stage1_outline.py` | OutlineGenerator class, outline generation |
| **generate/processors/** | `parser.py`, `cleanup.py` | OutlineParser class, content cleanup utilities |
| **generate/formats/** | `lectures.py`, `labs.py`, `study_notes.py`, `diagrams.py`, `questions.py` | Format-specific generators |
| **website/** | `generator.py`, `content_loader.py`, `templates.py`, `styles.py`, `scripts.py` | Website generation components |
| **utils/** | `helpers.py`, `logging_setup.py` | Utility functions, logging setup |
| **setup/** | `__init__.py` | Package initialization (minimal) |

## Integration Patterns

### Pattern 1: Configuration → LLM → Generation

```python
# 1. Load and validate configuration
from src.config.loader import ConfigLoader
loader = ConfigLoader("config")
loader.validate_all_configs()

# 2. Initialize LLM client with config
from src.llm.client import OllamaClient
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# 3. Create generators with config and client
from src.generate.formats.lectures import LectureGenerator
lecture_gen = LectureGenerator(loader, client)

# 4. Generate content
module = loader.get_module_by_id(1)
lecture = lecture_gen.generate_lecture(module)
```

### Pattern 2: Pipeline Orchestration

```python
# Use ContentGenerator for complete workflow
from src.generate.orchestration.pipeline import ContentGenerator
generator = ContentGenerator(loader)

# Generates outline, parses it, generates all content
outline = generator.generate_outline(course_name="Biology", interactive=False)
results = generator.generate_content_for_all_modules()
```

### Pattern 3: Session-Based Generation

```python
# Generate content per session (not per module)
for module_id in range(1, 6):
    for session_num in range(1, 4):
        result = generator.generate_session_content(
            module_id=module_id,
            session_number=session_num,
            num_labs=2
        )
```

### Pattern 4: Direct Format Generation

```python
# Use format generators directly
from src.generate.formats.diagrams import DiagramGenerator
diagram_gen = DiagramGenerator(loader, client)
diagrams = diagram_gen.generate_diagrams(module, num_diagrams=3)
```

### Pattern 5: Error Collection Pattern

```python
# Safe-to-fail: collect errors, continue processing
results, errors = generator.generate_content_for_all_modules()
if errors:
    for error in errors:
        logger.error(f"Module {error['module_id']}: {error['error']}")
```

## Module Documentation

Each submodule has detailed documentation:

- **[config/AGENTS.md](config/AGENTS.md)** - Configuration management, JSON outline discovery, validation
- **[llm/AGENTS.md](llm/AGENTS.md)** - LLM integration, request tracing, error handling, streaming
- **[generate/AGENTS.md](generate/AGENTS.md)** - Content generation overview, submodule coordination
- **[generate/orchestration/AGENTS.md](generate/orchestration/AGENTS.md)** - Pipeline coordination, session-based generation
- **[generate/stages/AGENTS.md](generate/stages/AGENTS.md)** - Outline generation, interactive/non-interactive modes
- **[generate/processors/AGENTS.md](generate/processors/AGENTS.md)** - Outline parsing, content cleanup, edge cases
- **[generate/formats/AGENTS.md](generate/formats/AGENTS.md)** - Format generators (lectures, labs, notes, diagrams, questions)
- **[setup/AGENTS.md](setup/AGENTS.md)** - Package initialization (minimal, reserved for future)
- **[utils/AGENTS.md](utils/AGENTS.md)** - Utility functions, file I/O, text processing, system checks
- **[website/AGENTS.md](website/AGENTS.md)** - Website generation, content discovery, HTML generation

## Development Principles

1. **Modular Design** - Clear separation of concerns
2. **Implementations** - No mocks in tests
3. **Type Hints** - All public functions have type annotations
4. **Comprehensive Logging** - Logging at all levels
5. **Error Handling** - Custom exceptions with clear messages
6. **Configuration-Driven** - All behavior controlled by YAML files

## Testing

Comprehensive test suite with ~540 tests across 25 test files:

```bash
# Run all tests
uv run pytest

# Run specific module tests
uv run pytest tests/test_config_loader.py -v
```

See **[../tests/README.md](../tests/README.md)** for complete testing documentation.

## Installation

This package is installed in development mode:

```bash
uv pip install -e ".[dev]"
```

## Code Standards

- **PEP 8** compliance via `black` formatting
- **Type checking** via `mypy`
- **Google-style docstrings** for all public APIs
- **Logging** via `logging` module (never `print()`)
- **Path handling** via `pathlib.Path`

## See Also

- **For Humans**: [README.md](README.md) - Human-readable package overview
- **Root Documentation**: [../AGENTS.md](../AGENTS.md) - Complete repository overview
- **API Reference**: [../docs/API.md](../docs/API.md) - Full public API documentation
- **Architecture**: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- **Development Rules**: [../.cursorrules/README.md](../.cursorrules/README.md) - All development standards


