# AGENTS.md - For AI Agents

## Repository Overview

Educational course materials generator using Ollama (gemma3:4b) to create educational content.

**Key capabilities**: Generate course outlines, lectures, labs, study notes, diagrams, questions, and secondary materials (application, extension, visualization, integration, investigation, open questions).

## Key Principles

1. **No Mock Methods** - All code uses implementations. Tests interact with actual services.
2. **Use uv** - All package management and script execution uses `uv` (not pip/venv).
3. **Configuration-Driven** - Course structure, LLM settings, and output formats are in YAML files under `config/`.
4. **TDD Approach** - Write tests before or alongside implementation.
5. **Text-Based** - All content in markdown/YAML for git-friendly version control.

## Development Rules

**See `.cursorrules/` directory for comprehensive, modular development rules:**

- **[.cursorrules/README.md](.cursorrules/README.md)** - Guide to all rule files
- **[.cursorrules/00-overview.md](.cursorrules/00-overview.md)** - Project philosophy and quick reference
- **[.cursorrules/01-uv-environment.md](.cursorrules/01-uv-environment.md)** - Environment setup (uv only)
- **[.cursorrules/02-folder-structure.md](.cursorrules/02-folder-structure.md)** - Modular code organization
- **[.cursorrules/03-testing-real-only.md](.cursorrules/03-testing-real-only.md)** - Testing (NO MOCKS EVER)
- **[.cursorrules/04-logging-unified.md](.cursorrules/04-logging-unified.md)** - Logging (no print() statements)
- **[.cursorrules/09-safe-to-fail.md](.cursorrules/09-safe-to-fail.md)** - Error handling (fail gracefully)
- **[.cursorrules/10-agentic-generation.md](.cursorrules/10-agentic-generation.md)** - Hybrid workflow patterns
- **[.cursorrules/11-documentation-standards.md](.cursorrules/11-documentation-standards.md)** - Documentation guidelines

All 12 numbered rule files (00-11) plus README.md provide focused, actionable guidance for specific development areas.

## Architecture

### Module Structure (Modular Organization)

```
src/
├── setup/                 # Setup and initialization
│   └── __init__.py
├── config/               # Configuration management
│   ├── __init__.py
│   └── loader.py         # ConfigLoader class
├── llm/                  # LLM integration
│   ├── __init__.py
│   └── client.py         # OllamaClient class
├── generate/             # Content generation
│   ├── __init__.py
│   ├── orchestration/    # Pipeline coordination
│   │   ├── __init__.py
│   │   ├── pipeline.py   # ContentGenerator
│   │   └── batch.py     # BatchCourseProcessor
│   ├── stages/           # Generation stages
│   │   ├── __init__.py
│   │   └── stage1_outline.py  # OutlineGenerator
│   ├── processors/       # Content processing
│   │   ├── __init__.py
│   │   └── parser.py     # OutlineParser
│   └── formats/          # Format-specific generators
│       ├── __init__.py
│       ├── lectures.py   # LectureGenerator
│       ├── labs.py       # LabGenerator
│       ├── study_notes.py  # StudyNotesGenerator
│       ├── diagrams.py   # DiagramGenerator
│       └── questions.py  # QuestionGenerator
├── utils/                # Utilities
│   ├── __init__.py
│   ├── helpers.py        # File I/O, text processing
│   └── content_analysis/  # Content quality assessment and validation
│       ├── analyzers.py   # Content analysis functions
│       ├── counters.py    # Counting functions
│       ├── consistency.py # Cross-session consistency validation
│       ├── mermaid.py     # Mermaid diagram validation
│       ├── logging.py     # Metrics logging
│       └── question_fixes.py  # Question format auto-correction
└── website/              # Website generation
    ├── __init__.py
    └── generator.py       # WebsiteGenerator
```

**All imports use the modular structure**:
```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.orchestration.pipeline import ContentGenerator
from src.generate.orchestration.batch import BatchCourseProcessor
from src.generate.stages.stage1_outline import OutlineGenerator
from src.generate.processors.parser import OutlineParser
from src.generate.formats.lectures import LectureGenerator
from src.generate.formats.labs import LabGenerator
from src.generate.formats.study_notes import StudyNotesGenerator
from src.generate.formats.diagrams import DiagramGenerator
from src.generate.formats.questions import QuestionGenerator
from src.utils.helpers import save_markdown, slugify
from src.utils.content_analysis import analyze_lecture, validate_mermaid_syntax
from src.website.generator import WebsiteGenerator
```

### Configuration Files

All in `config/` directory:
- **`course_config.yaml`** - Course metadata, structure defaults (num_modules, total_sessions), additional constraints for dynamic module generation
- **`llm_config.yaml`** - Ollama settings, model selection, prompt templates for all content types, language settings
- **`output_config.yaml`** - Output paths, file naming conventions, formatting preferences

### Scripts

All in `scripts/` directory (7 scripts):
- **`01_setup_environment.py`** - Stage 01: Environment setup/validation
- **`02_run_tests.py`** - Stage 02: Validation + optional tests
- **`03_generate_outline.py`** - Stage 03: Generate course outline (interactive by default)
- **`04_generate_primary.py`** - Stage 04: Primary materials (lectures, labs, notes, diagrams, questions)
- **`05_generate_secondary.py`** - Stage 05: Secondary materials (application, extension, visualization, integration, investigation, open_questions)
- **`06_website.py`** - Stage 06: Website generation (single HTML file for browsing all materials)
- **`run_pipeline.py`** - Orchestrates stages 01→06 sequentially (skips supported)

See **[docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md)** for detailed script documentation.

### Testing

- **Location**: `tests/` directory
- **Run with**: `uv run pytest`
- **Test files**: 25 test files with ~540 total tests
- **Test types**:
  - Unit tests (no external dependencies)
  - Integration tests (require Ollama + model)
- **Auto-management**: `conftest.py` automatically starts Ollama if installed
- **Graceful skipping**: Integration tests skip if Ollama unavailable

**Test files**:
- `test_batch_processor.py` - Batch course processing (requires Ollama)
- `test_cleanup.py` - Content cleanup and validation
- `test_config_loader.py` - Configuration loading and validation
- `test_content_analysis.py` - Content analysis utilities
- `test_content_generators.py` - Content generators (requires Ollama)
- `test_error_collector.py` - Error collection utilities
- `test_helpers_extended.py` - Additional helper functions
- `test_json_outline_integration.py` - JSON outline integration tests
- `test_llm_client.py` - Ollama API integration (requires Ollama)
- `test_logging_setup.py` - Logging setup and configuration
- `test_new_generators.py` - Study notes and lab generators (requires Ollama)
- `test_outline_generator.py` - Outline generation (requires Ollama)
- `test_outline_generator_noninteractive.py` - Non-interactive outline tests
- `test_parser.py` - Outline parsing
- `test_parser_edge_cases.py` - Parser edge case handling
- `test_pipeline.py` - Full pipeline (requires Ollama)
- `test_pipeline_extended.py` - Extended pipeline tests
- `test_summary_generator.py` - Summary generation utilities
- `test_utils.py` - Utility functions
- `test_website_content_loader.py` - Website content loading
- `test_website_generator.py` - Website generation
- `test_website_scripts.py` - Website script utilities
- `test_website_scripts_interaction.py` - Website script interactions
- `test_website_styles.py` - Website styling
- `test_website_templates.py` - Website templates

## System Status

✅ **Implemented and tested**:
- Configuration management (YAML-based, validated)
- **JSON Outline Integration** (dynamic module generation, multi-location search, automatic discovery)
- LLM client (Ollama integration with retry logic)
- Content generation (Session-based primary + Session-level secondary materials)
- **Content Validation** (automatic quality checks with [COMPLIANT]/[NEEDS REVIEW] status)
- Six-stage pipeline (setup → validation → outline → primary → secondary → website)
- Comprehensive test suite (~540 tests across 25 test files, no mocks)
- Modular documentation (architecture, configuration, pipeline, formats, API reference, testing coverage)
- Development rules (12 numbered rule files + README in .cursorrules/)

### Recent Updates (Dec 2024)
- **Dynamic Module Generation**: Modules now generated by LLM from course metadata, saved as JSON
- **JSON Outline Loading**: ConfigLoader loads modules from `course_outline_*.json` files
- **Session-Based Structure**: Primary materials generated per session (not per module)
- **Automatic Outline Discovery**: Scripts search multiple locations for most recent outline
- **Error Handling**: Clear messages when outlines not found with actionable guidance
- **Content Validation System**: Automatic quality checks with [COMPLIANT]/[NEEDS REVIEW] status indicators
- **Improved Question Parsing**: Supports multiple question formats (Question N:, ## Question N, numbered lists)
- **Logging Improvements**: Reduced verbosity (~40-50% fewer INFO messages), operation context in request IDs, stream progress at DEBUG level, new helper functions (log_operation_context, log_llm_request_summary)

## Common Tasks

### Running Scripts

```bash
# Stage 01: Setup environment
uv run python3 scripts/01_setup_environment.py

# Stage 02: Validation and testing (tests run by default)
uv run python3 scripts/02_run_tests.py

# Stage 03: Generate outline (creates JSON + Markdown)
uv run python3 scripts/03_generate_outline.py
# Output: output/outlines/course_outline_TIMESTAMP.json + .md

# Stage 04: Generate primary materials (finds latest outline automatically, processes all modules)
uv run python3 scripts/04_generate_primary.py

# Stage 04: Generate for specific modules only
uv run python3 scripts/04_generate_primary.py --modules 1 2 3

# Stage 04: Use specific outline file
uv run python3 scripts/04_generate_primary.py --outline path/to/outline.json

# Stage 05: Generate secondary materials (finds latest outline, processes all modules by default)
uv run python3 scripts/05_generate_secondary.py

# Stage 05: Specific types only
uv run python3 scripts/05_generate_secondary.py --types application visualization

# Stage 05: Dry-run mode (preview without LLM calls)
uv run python3 scripts/05_generate_secondary.py --modules 1 --dry-run

# Stage 06: Generate website (auto-finds latest outline, creates single HTML file)
uv run python3 scripts/06_website.py

# Stage 06: Open in browser after generation
uv run python3 scripts/06_website.py --open-browser

# Run full pipeline (all 6 stages)
uv run python3 scripts/run_pipeline.py

# Pipeline options
uv run python3 scripts/run_pipeline.py --skip-outline
uv run python3 scripts/run_pipeline.py --modules 1 2 3
uv run python3 scripts/run_pipeline.py --log-level DEBUG
```

### JSON Outline Workflow

```bash
# 1. Generate outline with LLM (creates JSON structure)
uv run python3 scripts/03_generate_outline.py
# Creates: output/{course_name}/outlines/course_outline_TIMESTAMP.json (or output/outlines/ if course_name not available)
# Contains: course_metadata + modules array with sessions

# 2. Verify outline structure
cat output/{course_name}/outlines/course_outline_*.json | jq '.modules[0]'  # Or output/outlines/ if course_name not available

# 3. Generate content (automatically finds latest outline)
uv run python3 scripts/04_generate_primary.py --modules 1

# 4. Output structure (session-based, course-specific)
# output/{course_name}/modules/module_01_name/
#   session_01/
#     lecture.md, lab.md, study_notes.md, diagram_1.mmd, diagram_2.mmd, questions.md
#     application.md  # From stage 05 (session-level)
#     extension.md
#     visualization.mmd
#     integration.md
#     investigation.md
#     open_questions.md
#   session_02/
#     ...
# Note: {course_name} is derived from outline metadata or default course config
```

### Running Tests

```bash
# All tests (auto-starts Ollama if needed)
uv run pytest

# Specific test file
uv run pytest tests/test_config_loader.py -v

# With coverage
uv run pytest --cov=src --cov-report=html

# Only unit tests (no Ollama required)
uv run pytest tests/test_config_loader.py tests/test_parser.py tests/test_utils.py

# Only integration tests (requires Ollama)
uv run pytest tests/test_llm_client.py tests/test_outline_generator.py tests/test_content_generators.py tests/test_pipeline.py
```

### Adding a New Module

1. Create module in appropriate `src/` subfolder
2. Create tests in `tests/test_<module>.py`
3. Import and integrate in pipeline
4. Update documentation (AGENTS.md, relevant docs/ files)
5. Run tests to verify

### Modifying Configuration

1. Edit YAML in `config/` directory
2. Validate: `uv run python3 -c "from src.config.loader import ConfigLoader; ConfigLoader('config').validate_all_configs()"`
3. Test with small module first
4. Run full pipeline

## Code Standards

- **Type hints** on all functions
- **Docstrings** (Google style) for all public functions/classes
- **Logging** via `logging` module (never `print()`) - ✅ Verified: All modules compliant
- **Error handling** with custom exceptions (ConfigurationError, LLMError, ContentGenerationError)
- **File operations** using `pathlib.Path`
- **PEP 8** compliance (use `black` for formatting)
- **Modular imports** - All imports use `from src.module import` pattern - ✅ Verified: No circular dependencies

## What NOT to Do

❌ Don't use mock methods in tests  
❌ Don't use pip/virtualenv (use uv)  
❌ Don't hard-code paths or settings (use config files)  
❌ Don't use print() (use logging)  

## Quick Reference

### Common Tasks Quick Reference

| Task | Command/Code | Documentation |
|------|-------------|--------------|
| **Setup environment** | `uv run python3 scripts/01_setup_environment.py` | [scripts/AGENTS.md](scripts/AGENTS.md) |
| **Run tests** | `uv run pytest` | [tests/AGENTS.md](tests/AGENTS.md) |
| **Generate outline** | `uv run python3 scripts/03_generate_outline.py --no-interactive` | [scripts/AGENTS.md](scripts/AGENTS.md#03_generate_outlinepy) |
| **Generate primary content** | `uv run python3 scripts/04_generate_primary.py --modules 1` | [scripts/AGENTS.md](scripts/AGENTS.md#04_generate_primarypy) |
| **Generate secondary content** | `uv run python3 scripts/05_generate_secondary.py --types application` | [scripts/AGENTS.md](scripts/AGENTS.md#05_generate_secondarypy) |
| **Generate website** | `uv run python3 scripts/06_website.py --open-browser` | [scripts/AGENTS.md](scripts/AGENTS.md#06_websitepy) |
| **Full pipeline** | `uv run python3 scripts/run_pipeline.py --no-interactive` | [docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) |
| **Load configuration** | `from src.config.loader import ConfigLoader; loader = ConfigLoader("config")` | [src/config/AGENTS.md](src/config/AGENTS.md) |
| **Use LLM client** | `from src.llm.client import OllamaClient; client = OllamaClient(llm_config)` | [src/llm/AGENTS.md](src/llm/AGENTS.md) |
| **Generate content** | `from src.generate.orchestration.pipeline import ContentGenerator` | [src/generate/orchestration/AGENTS.md](src/generate/orchestration/AGENTS.md) |

### File Location Reference

| Path | Purpose | Key Files |
|------|---------|-----------|
| **`config/`** | YAML configuration files | `course_config.yaml`, `llm_config.yaml`, `output_config.yaml` |
| **`src/config/`** | Configuration loading module | `loader.py` (ConfigLoader class) |
| **`src/llm/`** | LLM integration module | `client.py` (OllamaClient class) |
| **`src/generate/orchestration/`** | Pipeline coordination | `pipeline.py` (ContentGenerator class) |
| **`src/generate/stages/`** | Generation stages | `stage1_outline.py` (OutlineGenerator class) |
| **`src/generate/processors/`** | Content processing | `parser.py` (OutlineParser class), `cleanup.py` |
| **`src/generate/formats/`** | Format generators | `lectures.py`, `labs.py`, `study_notes.py`, `diagrams.py`, `questions.py` |
| **`src/utils/`** | Utility functions | `helpers.py` (file I/O, text processing) |
| **`src/website/`** | Website generation | `generator.py` (WebsiteGenerator class) |
| **`scripts/`** | Executable pipeline scripts | `01_setup_environment.py` through `06_website.py`, `run_pipeline.py` |
| **`tests/`** | Test suite | 25 test files, `conftest.py` (auto-start Ollama) |
| **`docs/`** | Technical documentation | `ARCHITECTURE.md`, `PIPELINE_GUIDE.md`, `CONFIGURATION.md`, etc. |
| **`output/outlines/`** | Generated outlines | `course_outline_TIMESTAMP.json`, `course_outline_TIMESTAMP.md` |
| **`output/{course_name}/modules/`** | Generated content | `module_XX_name/session_YY/` (primary + secondary, both session-level, course-specific) |
| **`output/{course_name}/website/`** | Generated website | `index.html` (single self-contained file, course-specific if course_name available) |
| **`output/website/`** | Generated website (fallback) | `index.html` (when course_name not available) |
| **`.cursorrules/`** | Development rules | 12 numbered rule files (00-11) + README |

### Module Dependency Chain

```
ConfigLoader (src/config/loader.py)
    ↓
OllamaClient (src/llm/client.py)
    ↓
OutlineGenerator (src/generate/stages/stage1_outline.py)
    ↓
OutlineParser (src/generate/processors/parser.py)
    ↓
ContentGenerator (src/generate/orchestration/pipeline.py)
    ↓
Format Generators (src/generate/formats/*.py)
    ├── LectureGenerator
    ├── LabGenerator
    ├── StudyNotesGenerator
    ├── DiagramGenerator
    └── QuestionGenerator
    ↓
WebsiteGenerator (src/website/generator.py)
```

### Project Layout

```
biology/
├── src/                  # Source code (modular structure)
│   ├── config/           # Configuration management
│   ├── llm/              # LLM integration
│   ├── generate/         # Content generation
│   │   ├── orchestration/  # Pipeline coordination
│   │   ├── stages/         # Generation stages
│   │   ├── processors/     # Content processing
│   │   └── formats/         # Format generators
│   ├── utils/            # Utility functions
│   ├── website/          # Website generation
│   └── setup/            # Package initialization
├── config/               # YAML configurations
│   ├── course_config.yaml
│   ├── llm_config.yaml
│   └── output_config.yaml
├── tests/                # Test suite (~540 tests across 25 files, no mocks)
│   ├── conftest.py       # Auto-start Ollama
│   └── test_*.py         # Test files
├── scripts/              # Executable scripts (7 scripts: 6 stages + pipeline)
│   ├── 01_setup_environment.py
│   ├── 02_run_tests.py
│   ├── 03_generate_outline.py
│   ├── 04_generate_primary.py
│   ├── 05_generate_secondary.py
│   ├── 06_website.py
│   └── run_pipeline.py
├── docs/                 # Comprehensive documentation (18+ technical docs)
│   ├── ARCHITECTURE.md
│   ├── PIPELINE_GUIDE.md
│   ├── CONFIGURATION.md
│   ├── FORMATS.md
│   ├── API.md
│   └── TESTING_COVERAGE.md
├── .cursorrules/         # Development rules (12 numbered rule files + README)
├── output/               # Generated content (gitignored)
│   ├── outlines/         # Course outlines (JSON + Markdown)
│   ├── modules/          # Generated content (session-based)
│   └── website/          # Generated website (single HTML)
├── pyproject.toml        # Project metadata and dependencies
├── README.md             # Navigation hub for humans
└── AGENTS.md             # This file - for AI agents
```

### Dependencies

**Core**: pyyaml, requests  
**Dev**: pytest, pytest-cov, black, flake8, mypy

**Install**: `uv pip install -e ".[dev]"`

### Key Documentation

#### Technical Documentation (docs/)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, modules, data flow, extension points
- **[docs/PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md)** - Complete 6-stage pipeline documentation, workflows, troubleshooting
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Complete YAML configuration reference, validation rules
- **[docs/FORMATS.md](docs/FORMATS.md)** - All content format specifications (primary + secondary materials)
- **[docs/API.md](docs/API.md)** - Complete public API reference with type hints and examples
- **[docs/JSON_OUTLINE.md](docs/JSON_OUTLINE.md)** - JSON outline format, lifecycle, discovery mechanism
- **[docs/TESTING_COVERAGE.md](docs/TESTING_COVERAGE.md)** - Test suite coverage, organization, running patterns
- **[docs/AGENTS.md](docs/AGENTS.md)** - Documentation directory guide for AI agents

#### Module Documentation (src/*/AGENTS.md)
- **[src/AGENTS.md](src/AGENTS.md)** - Package overview, module organization, import patterns
- **[src/config/AGENTS.md](src/config/AGENTS.md)** - ConfigLoader API, JSON outline discovery, validation
- **[src/llm/AGENTS.md](src/llm/AGENTS.md)** - OllamaClient API, request tracing, error handling, streaming, health monitoring
  - **[src/llm/TROUBLESHOOTING.md](src/llm/TROUBLESHOOTING.md)** - Comprehensive LLM troubleshooting guide
  - **[src/llm/HEALTH_MONITORING.md](src/llm/HEALTH_MONITORING.md)** - Health monitoring and diagnostics
- **[src/generate/AGENTS.md](src/generate/AGENTS.md)** - Content generation overview, submodule coordination
- **[src/generate/orchestration/AGENTS.md](src/generate/orchestration/AGENTS.md)** - ContentGenerator pipeline API
- **[src/generate/stages/AGENTS.md](src/generate/stages/AGENTS.md)** - OutlineGenerator API, interactive/non-interactive modes
- **[src/generate/processors/AGENTS.md](src/generate/processors/AGENTS.md)** - OutlineParser API, parsing patterns, edge cases
- **[src/generate/formats/AGENTS.md](src/generate/formats/AGENTS.md)** - Format generator APIs (lectures, labs, notes, diagrams, questions)
- **[src/utils/AGENTS.md](src/utils/AGENTS.md)** - Utility functions API, file I/O, text processing, system checks, content analysis
- **[src/website/AGENTS.md](src/website/AGENTS.md)** - WebsiteGenerator API, content discovery, HTML generation
- **[src/setup/AGENTS.md](src/setup/AGENTS.md)** - Package initialization (minimal, reserved for future)

#### Scripts & Configuration
- **[scripts/AGENTS.md](scripts/AGENTS.md)** - Complete script documentation, CLI options, exit codes, hands-off patterns
- **[config/AGENTS.md](config/AGENTS.md)** - Configuration files guide, YAML structure, validation, troubleshooting
- **[tests/AGENTS.md](tests/AGENTS.md)** - Test suite organization, running patterns, coverage, no-mocks philosophy

#### Setup & Development
- **[SETUP.md](SETUP.md)** - Installation, prerequisites, troubleshooting
- **[.cursorrules/README.md](.cursorrules/README.md)** - Guide to all 13 development rule files
- **[.cursorrules/00-overview.md](.cursorrules/00-overview.md)** - Project philosophy and quick reference
- **[.cursorrules/03-testing-real-only.md](.cursorrules/03-testing-real-only.md)** - NO MOCKS EVER philosophy
- **[.cursorrules/10-agentic-generation.md](.cursorrules/10-agentic-generation.md)** - Hybrid workflow patterns

## Integration Patterns

### Configuration → LLM → Generation Flow

```python
# 1. Load configuration
from src.config.loader import ConfigLoader
loader = ConfigLoader("config")
loader.validate_all_configs()

# 2. Initialize LLM client
from src.llm.client import OllamaClient
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# 3. Generate outline
from src.generate.stages.stage1_outline import OutlineGenerator
outline_gen = OutlineGenerator(loader, client)
outline = outline_gen.generate_outline(course_name="Biology", interactive=False)

# 4. Parse outline (if needed)
from src.generate.processors.parser import OutlineParser
parser = OutlineParser(outline)
modules = parser.parse_modules()

# 5. Generate content
from src.generate.formats.lectures import LectureGenerator
lecture_gen = LectureGenerator(loader, client)
for module in modules:
    lecture = lecture_gen.generate_lecture(module)
```

### Pipeline Orchestration Pattern

```python
# Use ContentGenerator for full workflow
from src.generate.orchestration.pipeline import ContentGenerator
generator = ContentGenerator(loader)

# Generate outline
outline = generator.generate_outline(course_name="Biology", interactive=False)

# Generate all primary content
results = generator.generate_content_for_all_modules()

# Generate secondary materials
for module_id in [1, 2, 3]:
    content = generator.generate_secondary_content(module_id, "application")
```

### Session-Based Generation Pattern

```python
# Generate session-based content (primary materials per session)
for module_id in range(1, 6):
    for session_num in range(1, 4):  # 3 sessions per module
        result = generator.generate_session_content(
            module_id=module_id,
            session_number=session_num,
            num_labs=2
        )
        # Saves to: output/{course_name}/modules/module_XX_name/session_YY/
```

### Error Handling Pattern

```python
# Safe-to-fail: collect errors, continue processing
from src.generate.orchestration.pipeline import ContentGenerator

generator = ContentGenerator(loader)
results, errors = generator.generate_content_for_all_modules()

if errors:
    logger.warning(f"Generation completed with {len(errors)} errors")
    for error in errors:
        logger.error(f"Module {error['module_id']}: {error['error']}")
```

## Notes for AI Agents

### Before Making Changes
- **Always check `.cursorrules/`** for development standards before making changes
- **Scan existing code** to understand current implementation patterns
- **Read relevant AGENTS.md files** in the module you're modifying
- **Check test files** to understand expected behavior

### Code Standards
- **Use real data in tests** - fixtures with actual test data, no mocks (see [.cursorrules/03-testing-real-only.md](.cursorrules/03-testing-real-only.md))
- **Log extensively** - Use `logging.getLogger(__name__)` in all modules (see [.cursorrules/04-logging-unified.md](.cursorrules/04-logging-unified.md))
- **Handle errors gracefully** - Collect errors, continue processing, report comprehensively (see [.cursorrules/09-safe-to-fail.md](.cursorrules/09-safe-to-fail.md))
- **Use modular imports** - Import from `src.*` submodules (e.g., `from src.config.loader import ConfigLoader`)
- **Type hints required** - All public functions must have type annotations
- **Docstrings required** - Google-style docstrings for all public APIs

### Testing
- **Test with real Ollama** - Integration tests use actual LLM, skip if unavailable
- **No mocks ever** - All tests use implementations (see [tests/AGENTS.md](tests/AGENTS.md))
- **Run tests before committing** - `uv run pytest` should pass
- **Add tests for new features** - Create `tests/test_<module>.py` if needed

### Documentation
- **Update AGENTS.md** when making architectural changes
- **Update README.md** in the module directory if it exists
- **Update docs/** files if changing public APIs or workflows
- **Keep signposts current** - Ensure cross-references are accurate

### File Locations
- **Source code**: `src/` directory (modular structure)
- **Configuration**: `config/` directory (YAML files)
- **Scripts**: `scripts/` directory (executable Python scripts)
- **Tests**: `tests/` directory (test files matching source structure)
- **Documentation**: `docs/` directory (technical documentation)
- **Output**: `output/` directory (gitignored, generated content)
  - Course-specific: `output/{course_name}/` when using course templates
  - Default: `output/` when using default config

## Workflow Modes

The system supports three workflow modes:

1. **Programmatic** (Full automation): `uv run python3 scripts/run_pipeline.py`
2. **Agentic** (AI + human review): Generate → Review → Edit → Commit
3. **Manual** (Human-controlled): Edit YAML and markdown files directly

See **[.cursorrules/10-agentic-generation.md](.cursorrules/10-agentic-generation.md)** for hybrid workflow patterns.

## Content Formats

All text-based, human-editable, git-friendly:

- **Markdown** (.md) - All content (lectures, labs, study notes, questions)
- **Mermaid** (.mmd) - Diagrams (text-based visual syntax)
- **YAML** (.yaml) - All configuration

See **[docs/FORMATS.md](docs/FORMATS.md)** for complete format documentation.
