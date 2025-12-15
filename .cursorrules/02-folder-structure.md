# Modular Code Organization

## Hard Constraint

**MUST follow the modular folder structure. All imports MUST use the modular structure.**

## Folder Structure

```
src/
├── config/               # Configuration management
│   ├── __init__.py
│   └── loader.py        # ConfigLoader class
├── llm/                 # LLM integration
│   ├── __init__.py
│   └── client.py        # OllamaClient class
├── generate/            # Content generation
│   ├── __init__.py
│   ├── orchestration/   # Pipeline coordination
│   │   ├── __init__.py
│   │   ├── pipeline.py # ContentGenerator
│   │   └── batch.py     # BatchCourseProcessor
│   ├── stages/          # Generation stages
│   │   ├── __init__.py
│   │   └── stage1_outline.py  # OutlineGenerator
│   ├── processors/      # Content processing
│   │   ├── __init__.py
│   │   ├── parser.py    # OutlineParser
│   │   └── cleanup.py   # ContentCleanup
│   └── formats/         # Format generators
│       ├── __init__.py
│       ├── lectures.py   # LectureGenerator
│       ├── labs.py       # LabGenerator
│       ├── study_notes.py # StudyNotesGenerator
│       ├── diagrams.py   # DiagramGenerator
│       └── questions.py # QuestionGenerator
├── utils/               # Utilities
│   ├── __init__.py
│   ├── helpers.py        # File I/O, text processing
│   └── content_analysis/ # Content quality assessment
│       ├── __init__.py
│       ├── analyzers.py
│       ├── counters.py
│       └── ...
└── website/             # Website generation
    ├── __init__.py
    └── generator.py     # WebsiteGenerator
```

## Import Patterns

### Hard Constraint: Modular Imports

**MUST use modular imports from subfolders:**

```python
# ✅ CORRECT: Modular imports
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.orchestration.pipeline import ContentGenerator
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.processors.parser import OutlineParser
from src.generate.formats.lectures import LectureGenerator
from src.utils.helpers import save_markdown, slugify
from src.website.generator import WebsiteGenerator

# ❌ WRONG: Root-level imports (if they exist)
from src import ConfigLoader
from src import OllamaClient
```

### Module Organization Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Clear Dependencies**: Dependencies flow unidirectionally
3. **Consistent Naming**: Module names match their primary class
4. **Documentation**: Each module has AGENTS.md and README.md

## Documentation Structure

**HARD**: Every folder level MUST have:
- `AGENTS.md` - Guide for AI agents
- `README.md` - Guide for humans

### Example Structure

```
src/
├── AGENTS.md            # Package overview
├── README.md           # Package overview
├── config/
│   ├── AGENTS.md       # ConfigLoader API
│   └── README.md       # Configuration usage
├── generate/
│   ├── AGENTS.md       # Generation overview
│   ├── README.md       # Generation overview
│   ├── formats/
│   │   ├── AGENTS.md   # Format generators API
│   │   └── README.md   # Format generators usage
│   └── ...
```

## Adding New Modules

When adding a new module:

1. **Create folder structure** following existing patterns
2. **Add `__init__.py`** files at each level
3. **Create AGENTS.md and README.md** in the new folder
4. **Use modular imports** in all code
5. **Update parent AGENTS.md** to reference new module

## Anti-Patterns

❌ **Don't create flat module structure**  
❌ **Don't use root-level imports**  
❌ **Don't skip `__init__.py` files**  
❌ **Don't skip documentation files**  
❌ **Don't mix concerns in single modules**

## See Also

- **[../docs/MODULE_ORGANIZATION.md](../docs/MODULE_ORGANIZATION.md)** - Detailed module structure
- **[../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System architecture
- **[../src/AGENTS.md](../src/AGENTS.md)** - Package overview
- **[11-documentation-standards.md](11-documentation-standards.md)** - Documentation requirements
