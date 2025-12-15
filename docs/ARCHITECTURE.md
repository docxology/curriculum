# Architecture Documentation

## System Overview

The educational course Generator is a modular, configuration-driven system that uses a local Ollama LLM to generate comprehensive educational course materials.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Architecture Style** | Modular, layered, configuration-driven |
| **Pipeline Stages** | 6 stages (01: Setup, 02: Tests, 03: Outline, 04: Primary, 05: Secondary, 06: Website) |
| **Core Layers** | Configuration, LLM, Generation, Processing, Orchestration, Utility |
| **Data Flow** | YAML configs → JSON outline → Session-based content → Module synthesis |
| **Key Innovation** | Dynamic JSON outline structure, not static module definitions |
| **Testing Philosophy** | Real implementations only, no mocks (~540 tests across 25 files) |
| **Extension Points** | New content types, custom workflows, additional config |

**Read time**: 15-30 minutes | **Audience**: Developers, contributors, system architects

## Design Principles

1. **Modular Architecture**: Each component has a single, well-defined responsibility
2. **Configuration-Driven**: Behavior controlled through YAML configuration files
3. **No Mock Methods**: All tests use real implementations and data
4. **Pipeline-Based**: 6-stage workflow (setup → validation → outline → primary → secondary → website)
5. **Logging-First**: Comprehensive logging throughout for debugging and monitoring

### Terminology Note

The system uses a **6-stage pipeline** (Stages 01-06):
- **Stage 01**: Environment Setup
- **Stage 02**: Validation & Tests
- **Stage 03**: Generate Outline (JSON + Markdown)
- **Stage 04**: Generate Primary Materials (lectures, labs, diagrams, questions, study notes)
- **Stage 05**: Generate Secondary Materials (application, extension, visualization, etc.)
- **Stage 06**: Generate Website (single HTML file for browsing all materials)

## System Components

### Configuration Layer

**`src/config/loader.py`**
- Loads and validates YAML configuration files
- Provides typed access to configuration values
- Caches loaded configs for performance
- Validates required fields and structure

**Configuration Files**:
- `course_config.yaml`: Course structure with 20 comprehensive biology modules
- `llm_config.yaml`: Ollama settings and prompt templates
- `output_config.yaml`: Output paths and formatting rules

### LLM Integration Layer

**`src/llm/client.py`**
- Communicates with Ollama API via HTTP
- Handles streaming responses
- Implements retry logic with exponential backoff
- Supports template-based prompt formatting
- Error handling for connection, timeout, and HTTP errors

**Key Features**:
- Non-blocking streaming responses
- Configurable generation parameters (temperature, top_p, etc.)
- Template variable substitution
- System prompt support

### Generation Layer

**`src/generate/stages/stage1_outline.py`**
- Generates structured course outlines
- Uses configured course structure and LLM
- Adds metadata headers (level, duration, timestamp)
- Validates outline before saving

**`src/generate/formats/`**
Contains specialized generators for each content format:

1. **LectureGenerator** (`lectures.py`)
   - Creates detailed lecture content
   - Includes learning objectives
   - Respects target content length
   - Formats as markdown

2. **LabGenerator** (`labs.py`)
   - Generates laboratory exercises
   - Includes materials, safety, procedures
   - Formats with data collection tables
   - Multiple labs per module supported

3. **StudyNotesGenerator** (`study_notes.py`)
   - Creates concise review summaries
   - Key concepts and terms
   - Memory aids and mnemonics
   - Common exam questions

4. **DiagramGenerator** (`diagrams.py`)
   - Generates Mermaid diagram code
   - Context-aware diagram creation
   - Cleans LLM output (removes code fences)
   - Saves as `.mmd` files

5. **QuestionGenerator** (`questions.py`)
   - Creates comprehension questions
   - Distributes across question types (50% MC, 30% SA, 20% Essay)
   - Includes answer keys
   - Formats with metadata header

### Processing Layer

**`src/generate/processors/parser.py`**
- Parses generated markdown outlines
- Extracts modules, subtopics, and objectives
- Handles metadata extraction
- Provides structured data for content generation

**Capabilities**:
- Module extraction via heading detection
- Bullet point parsing for subtopics/objectives
- Metadata extraction from header
- Flexible format handling

**`src/generate/processors/cleanup.py`**
- Post-generation content quality control
- Removes conversational artifacts from LLM output
- Standardizes placeholders (names, dates)
- Validates content for common quality issues

**Cleanup Features**:
- **Conversational Artifact Removal**: Strips phrases like "Okay, here's...", "Would you like...", "Let me know...", "Feel free to..."
- **Placeholder Standardization**: Replaces specific names ("Dr. Smith" → "[INSTRUCTOR]"), dates ("Oct 26, 2023" → "[DATE]")
- **Word Count Statement Removal**: Removes LLM-generated word count statements from content
- **Content Validation**: Checks for missing answer keys, formatting issues, etc.
- **Batch Processing**: Validates multiple materials at once with detailed reporting
- **Automatic Integration**: Applied automatically during Stage 04 content generation

**Cleanup Process**:
1. **Conversational Patterns**: Removes informal phrases that LLMs sometimes include
2. **Instructor Names**: Standardizes all instructor references to `[INSTRUCTOR]`
3. **Dates**: Replaces specific dates with `[DATE]` placeholder
4. **Word Counts**: Removes LLM-generated word count statements
5. **Validation**: Checks content structure and completeness

**Usage**: Cleanup is automatically applied during Stage 04 generation. No manual intervention required.

### Orchestration Layer

**`src/generate/orchestration/pipeline.py`**
- Coordinates full workflow
- Manages two-stage execution
- Progress tracking and logging
- Error handling and recovery
- Multi-location output discovery

**Output Discovery**:
- Multi-location search for generated files
- Finds most recent by modification time
- Config-driven with intelligent defaults
- Supports flexible workspace organization
- Searches: config directory, project root, scripts directory

**Pipeline Stages**:

**Stage 03 (Outline Generation)**:
- Loads course configuration
- Generates comprehensive outline using LLM
- Saves to configured output directory (both .md and .json)
- Returns path to outline file
- Script: `03_generate_outline.py`

**Stage 04 (Primary Materials)**:
- Loads most recent outline JSON automatically
- Processes each module (or selected modules)
- **Context-Aware Generation**: Passes lecture content to lab/questions generators
- Generates lectures, labs, study notes, diagrams, and questions
- **Automatic Cleanup**: Removes conversational artifacts and standardizes placeholders
- Saves all content with consistent naming
- **Optional Validation**: Post-generation quality checking
- Collects results and status
- Script: `04_generate_primary.py`

**Stage 05 (Secondary Materials)**:
- Loads outline JSON and reads primary materials
- Generates session-level secondary materials (per session, not per module)
- Generates application, extension, visualization, integration, investigation, open questions
- Saves directly to session folders (flat structure)
- Script: `05_generate_secondary.py`

**Stage 06 (Website Generation)**:
- Loads JSON outline and discovers all generated content
- Converts markdown to HTML
- Generates single self-contained HTML website
- Provides navigation for browsing all course materials
- Script: `06_website.py`

### Website Layer

**`src/website/generator.py`**
- Generates single HTML website from course materials
- Converts markdown content to HTML
- Embeds CSS and JavaScript for standalone operation
- Provides module/session navigation

**`src/website/content_loader.py`**
- Discovers and loads all generated content files
- Reads markdown files from session directories
- Organizes content by module and session

**`src/website/templates.py`**
- HTML templates for website structure
- Module navigation templates
- Content display templates

**`src/website/styles.py`**
- CSS styling for website
- Responsive design support
- Print-friendly styles

**`src/website/scripts.py`**
- JavaScript for interactive features
- Search functionality
- Content filtering

### Utility Layer

**`src/utils/helpers.py`** (Expanded Dec 2025)
- File I/O operations (save/load markdown)
- Text processing (slugify, sanitize filenames)
- Directory management
- Timestamp formatting
- **System checks**: Ollama availability, model checks, uv availability
- **Command execution**: Subprocess wrapper for system commands

## Data Flow

Data flows through the system in a structured, predictable manner: Configuration (YAML) → Structured Outline (JSON) → Content Materials (Markdown) → Website (HTML).

**Key transformations**:
- YAML configs → Python dictionaries (validated and cached)
- Template variables → LLM prompts → Generated content
- JSON outline → Session-based content files
- All content → Single HTML website

**See [DATA_FLOW.md](DATA_FLOW.md)** for detailed data flow documentation, transformations at each stage, and data structure evolution.

## Module Dependencies

The system uses a modular architecture with clear, unidirectional dependencies. Each module has a single responsibility and follows consistent organization principles.

**Dependency flow**:
```
utils/ (no dependencies)
  └─> config/
        └─> llm/
              ├─> generate/stages/
              │     └─> generate/processors/
              └─> generate/formats/
                      └─> generate/orchestration/
                            └─> website/
```

**See [MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md)** for complete module structure, dependencies, organization principles, and adding new modules.

## File Organization

```
biology/
├── src/          # Core modules (modular structure)
│   ├── __init__.py
│   ├── config/             # Configuration management
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── llm/                # LLM integration
│   │   ├── __init__.py
│   │   └── client.py
│   ├── generate/           # Content generation
│   │   ├── __init__.py
│   │   ├── orchestration/  # Pipeline coordination
│   │   │   ├── __init__.py
│   │   │   └── pipeline.py
│   │   ├── stages/         # Generation stages
│   │   │   ├── __init__.py
│   │   │   └── stage1_outline.py
│   │   ├── processors/     # Content processing
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   └── formats/        # Format generators
│   │       ├── __init__.py
│   │       ├── lectures.py
│   │       ├── labs.py
│   │       ├── study_notes.py
│   │       ├── diagrams.py
│   │       └── questions.py
│   ├── setup/              # Initialization
│   │   └── __init__.py
│   └── utils/              # Utilities
│       ├── __init__.py
│       └── helpers.py
│
├── config/                  # Configuration files
│   ├── course_config.yaml   # Course structure
│   ├── llm_config.yaml      # LLM settings
│   └── output_config.yaml   # Output configuration
│
├── tests/                   # Test suite (~540 tests across 25 files)
│   ├── test_batch_processor.py
│   ├── test_cleanup.py
│   ├── test_config_loader.py
│   ├── test_content_generators.py
│   ├── test_error_collector.py
│   ├── test_summary_generator.py
│   ├── test_helpers_extended.py
│   ├── test_json_outline_integration.py
│   ├── test_llm_client.py
│   ├── test_new_generators.py
│   ├── test_outline_generator.py
│   ├── test_outline_generator_noninteractive.py
│   ├── test_parser.py
│   ├── test_parser_edge_cases.py
│   ├── test_pipeline.py
│   ├── test_pipeline_extended.py
│   └── test_utils.py
│
├── scripts/                 # Executable scripts
│   ├── 01_setup_environment.py  # Environment validation
│   ├── 02_run_tests.py          # Configuration and tests
│   ├── 03_generate_outline.py   # Stage 03: Outline
│   ├── 04_generate_primary.py   # Stage 04: Primary materials
│   ├── 05_generate_secondary.py # Stage 05: Secondary materials
│   └── run_pipeline.py          # Full pipeline orchestration
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # This file
│   ├── CONFIGURATION.md     # Config guide
│   ├── PIPELINE_GUIDE.md    # Pipeline documentation
│   ├── FORMATS.md           # Content formats
│   └── README.md            # Documentation hub
│
├── .cursorrules/            # Development rules (12 rule files + README)
│
└── output/                  # Generated content
    ├── outlines/
    ├── lectures/
    ├── labs/
    ├── study_notes/
    ├── diagrams/
    └── questions/
```

## Error Handling Strategy

The system implements comprehensive error handling with safe-to-fail principles. Errors are collected rather than stopping execution, allowing partial success and comprehensive error reporting.

**Key principles**:
- Configuration errors: Fail fast with clear messages
- LLM errors: Retry with exponential backoff
- Pipeline errors: Continue processing, collect all errors
- Partial success: Return what was generated successfully

**See [ERROR_HANDLING.md](ERROR_HANDLING.md)** for complete error handling patterns, exception hierarchy, and recovery strategies.

## Logging Strategy

The system uses structured logging with multiple levels and comprehensive context. All operational output uses the logging module (no print statements).

**Logging levels**:
- **DEBUG**: Detailed execution flow, variable values
- **INFO**: Major steps, progress updates, success messages
- **WARNING**: Recoverable issues, skipped items
- **ERROR**: Failures that affect module generation

**See [LOGGING.md](LOGGING.md)** for complete logging patterns, levels, structured logging, and debugging guides.

## Extension Points

The system is designed for extensibility. New content types, generators, configuration options, and custom workflows can be added following established patterns.

**Extension capabilities**:
- Add new content types and generators
- Add new configuration options
- Add new pipeline stages
- Create custom workflows

**See [EXTENSION.md](EXTENSION.md)** for comprehensive extension guide with step-by-step instructions and examples.

## Performance Considerations

The system is optimized for sequential processing with aggressive caching. LLM generation is the primary bottleneck (60-80% of time).

**Performance characteristics**:
- Config files loaded once and cached
- LLM responses streamed for responsiveness
- Modules processed sequentially (could be parallelized)
- File I/O buffered, directories created only when needed

**See [PERFORMANCE.md](PERFORMANCE.md)** for complete performance considerations, optimization strategies, and monitoring.

## Security Considerations

The system is designed for local execution with comprehensive input validation and output sanitization.

**Security model**:
- Local LLM only (no external API calls)
- No credential storage required
- File paths validated and sanitized
- Output directory configurable (avoid system directories)

**See [SECURITY.md](SECURITY.md)** for complete security considerations, best practices, and security model.

## Testing Strategy

- **Unit Tests**: Individual module functionality (no external dependencies)
- **Integration Tests**: LLM interaction (requires Ollama running)
- **No Mocks**: Real implementations only, tests skip if dependencies unavailable
- **Coverage**: ~30% without Ollama, ~75% with integration tests
- **Test Files**: 15 comprehensive test modules with 297 total tests

## Future Enhancements

Potential areas for expansion:

1. **Parallel Module Processing**: Generate multiple modules concurrently
2. **Progress Persistence**: Save checkpoints, resume interrupted runs
3. **Multiple LLM Support**: Abstract LLM client for different providers
4. **Interactive Mode**: CLI prompts for module selection
5. **Export Formats**: PDF, HTML, EPUB generation from markdown
6. **Assessment Tools**: Automated grading rubrics, flashcards
7. **Version Control**: Track iterations of generated content

---

## Related Documentation

### Essential Reading
- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - Understand the JSON outline data structure (central to the system)
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration system details (YAML files and validation)
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - How the 6-stage pipeline orchestrates these components

### Detailed References
- **[API.md](API.md)** - Public API for all modules described here
- **[FORMATS.md](FORMATS.md)** - Output formats from the format generators
- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - How components are tested

### Development
- **[../.cursorrules/00-overview.md](../.cursorrules/00-overview.md)** - Development philosophy
- **[../.cursorrules/02-folder-structure.md](../.cursorrules/02-folder-structure.md)** - Modular organization rationale
- **[../AGENTS.md](../AGENTS.md)** - Quick reference for AI agents

### Quick Navigation
| I want to... | See |
|--------------|-----|
| Understand data flow | This document → Data Flow section |
| See module code | [API.md](API.md) → Module imports |
| Extend system | This document → Extension Points |
| Configure system | [CONFIGURATION.md](CONFIGURATION.md) |
| Run the system | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) |

