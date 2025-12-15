# educational course Modules

Core Python modules for the educational course generator.

## Package Architecture

```mermaid
graph TB
    A[src Package] --> B[config]
    A --> C[llm]
    A --> D[generate]
    A --> E[setup]
    A --> F[utils]
    
    B --> B1[loader.py<br/>ConfigLoader]
    C --> C1[client.py<br/>OllamaClient]
    
    D --> D1[orchestration]
    D --> D2[stages]
    D --> D3[processors]
    D --> D4[formats]
    
    D1 --> D1A[pipeline.py<br/>ContentGenerator]
    D2 --> D2A[stage1_outline.py<br/>OutlineGenerator]
    D3 --> D3A[parser.py<br/>OutlineParser]
    D3 --> D3B[cleanup.py<br/>Cleanup Utils]
    
    D4 --> D4A[lectures.py<br/>LectureGenerator]
    D4 --> D4B[labs.py<br/>LabGenerator]
    D4 --> D4C[study_notes.py<br/>StudyNotesGenerator]
    D4 --> D4D[diagrams.py<br/>DiagramGenerator]
    D4 --> D4E[questions.py<br/>QuestionGenerator]
    
    F --> F1[helpers.py<br/>File I/O, Text Processing]
    F --> F2[logging_setup.py<br/>Unified Logging]
    F --> F3[content_analysis.py<br/>Quality Analysis]
    
    style A fill:#e1f5ff
    style B fill:#e1ffe1
    style C fill:#ffe1e1
    style D fill:#fff4e1
    style F fill:#f0e1ff
```

## Data Flow Through Layers

```mermaid
flowchart LR
    A[YAML Configs] -->|Load| B[ConfigLoader]
    B -->|Validate| C[Valid Config]
    C -->|Provide| D[ContentGenerator]
    D -->|Generate| E[JSON Outline]
    E -->|Parse| F[OutlineParser]
    F -->|Structure| G[Module/Session Data]
    G -->|Generate| H[Format Generators]
    H -->|Create| I[Markdown/Mermaid Files]
    I -->|Cleanup| J[Final Content]
    
    D -.->|Uses| K[OllamaClient]
    H -.->|Uses| K
    
    style C fill:#e1ffe1
    style E fill:#fff4e1
    style J fill:#e1ffe1
```

## Module Dependencies

```mermaid
graph TD
    Scripts[Scripts] --> Pipeline[orchestration/pipeline]
    Pipeline --> Config[config/loader]
    Pipeline --> LLM[llm/client]
    Pipeline --> Outline[stages/stage1_outline]
    Pipeline --> Formats[formats/*]
    
    Outline --> Config
    Outline --> LLM
    Outline --> Parser[processors/parser]
    
    Formats --> Config
    Formats --> LLM
    Formats --> Cleanup[processors/cleanup]
    
    Config --> Utils[utils/helpers]
    LLM --> Utils
    Cleanup --> Utils
    
    style Config fill:#e1ffe1
    style LLM fill:#ffe1e1
    style Utils fill:#f0e1ff
```

## Modular Structure

All components are organized into logical subpackages:

### Configuration (`config/`)
- `loader.py` - Configuration loading and validation

### LLM Integration (`llm/`)
- `client.py` - Ollama API integration

### Content Generation (`generate/`)

**Orchestration** (`generate/orchestration/`)
- `pipeline.py` - Workflow orchestration (ContentGenerator)

**Stages** (`generate/stages/`)
- `stage1_outline.py` - Course outline generation (OutlineGenerator)

**Processors** (`generate/processors/`)
- `parser.py` - Outline parsing and processing (OutlineParser)
- `cleanup.py` - Content cleanup and validation utilities

**Formats** (`generate/formats/`)
- `__init__.py` - Base ContentGenerator class
- `lectures.py` - LectureGenerator
- `labs.py` - LabGenerator
- `study_notes.py` - StudyNotesGenerator
- `diagrams.py` - DiagramGenerator
- `questions.py` - QuestionGenerator

### Utilities (`utils/`)
- `helpers.py` - File I/O, text processing, formatting utilities

## Usage

Import using modular paths:

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.orchestration.pipeline import ContentGenerator
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.processors.parser import OutlineParser
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator
from src.utils.helpers import ensure_directory, slugify, save_markdown
```

All modules follow best practices with comprehensive logging, error handling, and type hints.
