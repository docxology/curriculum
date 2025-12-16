# Documentation

Technical documentation for the educational course Generator.

## Core Documentation

### Essential Reading

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, module interactions, data flow, extension points
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - 6-stage pipeline, scripts reference, workflows, error handling
- **[CONFIGURATION.md](CONFIGURATION.md)** - Complete YAML configuration reference
- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - 🆕 JSON outline format, generation, and consumption

### Content & Output

- **[FORMATS.md](FORMATS.md)** - Content formats and validation
- **[API.md](API.md)** - Public API reference

### Testing & Quality

- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Test suite overview

### Technical Deep Dives

- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns
- **[LOGGING.md](LOGGING.md)** - Logging patterns
- **[VALIDATION.md](VALIDATION.md)** - Content validation rules
- **[../src/llm/TROUBLESHOOTING.md](../src/llm/TROUBLESHOOTING.md)** - LLM troubleshooting guide
- **[../src/llm/HEALTH_MONITORING.md](../src/llm/HEALTH_MONITORING.md)** - LLM health monitoring
- **[EXTENSION.md](EXTENSION.md)** - Extension guide
- **[DATA_FLOW.md](DATA_FLOW.md)** - Data flow
- **[MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md)** - Module structure
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting guide
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance considerations
- **[SECURITY.md](SECURITY.md)** - Security considerations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Quick Navigation

| I want to... | Read this | Priority |
|--------------|-----------|----------|
| **Get started quickly** | [../README.md](../README.md) | ⭐⭐⭐ |
| **Understand system design** | [ARCHITECTURE.md](ARCHITECTURE.md) | ⭐⭐⭐ |
| **Run the pipeline** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) | ⭐⭐⭐ |
| **Understand JSON outlines** | [JSON_OUTLINE.md](JSON_OUTLINE.md) | ⭐⭐⭐ |
| Configure course content | [CONFIGURATION.md](CONFIGURATION.md) | ⭐⭐ |
| Customize output formats | [FORMATS.md](FORMATS.md) | ⭐⭐ |
| Use the public API | [API.md](API.md) | ⭐⭐ |
| Troubleshoot issues | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | ⭐⭐ |
| Extend the system | [EXTENSION.md](EXTENSION.md) | ⭐⭐ |
| Understand error handling | [ERROR_HANDLING.md](ERROR_HANDLING.md) | ⭐ |
| Debug with logs | [LOGGING.md](LOGGING.md) | ⭐ |
| Understand validation | [VALIDATION.md](VALIDATION.md) | ⭐ |
| Understand data flow | [DATA_FLOW.md](DATA_FLOW.md) | ⭐ |
| Understand module structure | [MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md) | ⭐ |
| Optimize performance | [PERFORMANCE.md](PERFORMANCE.md) | ⭐ |
| Understand security | [SECURITY.md](SECURITY.md) | ⭐ |
| Deploy to production | [DEPLOYMENT.md](DEPLOYMENT.md) | ⭐ |
| Contribute to project | [CONTRIBUTING.md](CONTRIBUTING.md) | ⭐ |
| Review test coverage | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) | ⭐ |
| Set up development environment | [../SETUP.md](../SETUP.md) | ⭐⭐⭐ |
| Learn development rules | [../.cursorrules/README.md](../.cursorrules/README.md) | ⭐⭐ |

**Priority**: ⭐⭐⭐ Essential | ⭐⭐ Important | ⭐ Reference

## Documentation Structure

### [ARCHITECTURE.md](ARCHITECTURE.md)
**System design and implementation details** - 📐 Technical deep-dive
- Design principles (modular, configuration-driven, no mocks, pipeline-based)
- Component layers (Configuration, LLM, Generation, Processing, Orchestration, Utility)
- Data flow diagrams (YAML → JSON outline → Content)
- Module dependencies and interactions
- Error handling and logging strategies
- Extension points for customization
- Performance and security considerations

**Read when**: Understanding how the system works internally, extending functionality, debugging

### [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)
**6-stage pipeline execution and workflows** - 🔄 Operational guide
- **Stage 01**: Environment Setup (`01_setup_environment.py`)
- **Stage 02**: Validation & Tests (`02_run_tests.py`)
- **Stage 03**: Generate Outline (`03_generate_outline.py`)
- **Stage 04**: Generate Primary Materials (`04_generate_primary.py`)
- **Stage 05**: Generate Secondary Materials (`05_generate_secondary.py`)
- Full pipeline orchestration (`run_pipeline.py`)
- Workflow examples and best practices
- Error handling, monitoring, troubleshooting

**Read when**: Running the pipeline, understanding the workflow, troubleshooting generation issues

### [JSON_OUTLINE.md](JSON_OUTLINE.md)
**JSON outline format and lifecycle** - 📋 Core data structure
- JSON schema and field definitions
- Generation process (Stage 03, interactive vs non-interactive)
- Consumption process (Stages 04-05, session-based content)
- Multi-location discovery mechanism
- Validation rules and normalization
- Migration from static modules
- Best practices and troubleshooting

**Read when**: Understanding course structure, debugging outline issues, migrating from old format

### [CONFIGURATION.md](CONFIGURATION.md)
**Complete YAML configuration reference** - ⚙️ Configuration guide
- `course_config.yaml` - Course structure, defaults, topic areas
- `llm_config.yaml` - LLM settings, prompts, outline generation bounds
- `output_config.yaml` - Output paths, naming, formatting, logging
- Environment variables and validation
- LLM parameter tuning guide
- Best practices and troubleshooting

**Read when**: Configuring a new course, adjusting LLM behavior, customizing output

### [FORMATS.md](FORMATS.md)
**Content format specifications** - 📝 Output reference
- **Primary Materials** (Stage 04): Lectures, Labs, Study Notes, Diagrams, Questions
- **Secondary Materials** (Stage 05): Application, Extension, Visualization, Integration, Investigation, Open Questions
- Format structure and examples
- **Validation and Quality Checks**: [COMPLIANT]/[NEEDS REVIEW] status, validation criteria, troubleshooting
- LLM prompt templates
- Customization options (high school vs university, lab-heavy, self-study)
- Output directory structure (session-based)
- Integration with Obsidian, Markdown editors, LMS

**Read when**: Understanding output formats, customizing content types, understanding validation warnings, integrating with other tools

### [API.md](API.md)
**Complete public API reference** - 💻 Developer guide
- Configuration Layer: `ConfigLoader`
- LLM Integration Layer: `OllamaClient`
- Generation Layer: `ContentGenerator`, `OutlineGenerator`
- Processing Layer: `OutlineParser`, `ContentCleanup`
- Format Generators: `LectureGenerator`, `LabGenerator`, `StudyNotesGenerator`, `DiagramGenerator`, `QuestionGenerator`
- Content Analysis: `analyze_lecture()`, `analyze_questions()`, `analyze_study_notes()`, `log_content_metrics()`
- Utility Layer: File I/O, text processing, system checks
- Type hints, examples, error handling
- Custom workflow examples

**Read when**: Building custom workflows, integrating with other systems, extending functionality, using validation APIs

### [TESTING_COVERAGE.md](TESTING_COVERAGE.md)
**Test suite overview and coverage** - 🧪 Quality assurance
- Test statistics (~540 tests across 25 files)
- Unit vs integration tests (fast tests <2s, slow tests ~150s)
- Coverage metrics (~30% without Ollama, ~75% with integration tests)
- Test organization by functionality and speed
- Running tests (unit-only, full suite, coverage reports)
- Coverage improvement roadmap
- CI/CD integration guidelines

**Read when**: Running tests, improving test coverage, setting up CI/CD

## Learning Paths

### Quick Start (30 minutes)
For users who want to generate content:

1. **[../README.md](../README.md)** - Overview and quick start
2. **[../SETUP.md](../SETUP.md)** - Installation (5 min)
3. **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Stage 03-05 basics (15 min)
4. **[CONFIGURATION.md](CONFIGURATION.md)** - Adjust settings (10 min)
5. Run: `uv run python3 scripts/run_pipeline.py`

### Comprehensive Understanding (2 hours)
For users who want deep understanding:

1. **[../README.md](../README.md)** - Project overview (10 min)
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design (30 min)
3. **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - Core data structure (20 min)
4. **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration reference (20 min)
5. **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Full pipeline (30 min)
6. **[FORMATS.md](FORMATS.md)** - Output formats (20 min)
7. **[API.md](API.md)** - Public API (10 min)

### Developer/Contributor (4 hours)
For developers extending the project:

1. **[../AGENTS.md](../AGENTS.md)** - Developer overview (15 min)
2. **[../.cursorrules/README.md](../.cursorrules/README.md)** - Development rules (20 min)
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System internals (45 min)
4. **[API.md](API.md)** - Complete API reference (60 min)
5. **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Test suite (30 min)
6. **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - Data format (30 min)
7. **[CONFIGURATION.md](CONFIGURATION.md)** - Config system (30 min)
8. Read source code with understanding

## For AI Agents

AI agents should reference **[AGENTS.md](AGENTS.md)** for:
- Repository overview and key principles
- Development rules (links to all 13 `.cursorrules/` files)
- Architecture summary and module structure
- Common tasks and workflows
- Code standards and testing philosophy
- Quick reference and "what NOT to do"

## Additional Resources

- **Setup Guide**: [../SETUP.md](../SETUP.md) - Installation
- **Main README**: [../README.md](../README.md) - Quick start
- **Development Rules**: [../.cursorrules/README.md](../.cursorrules/README.md) - Development rules
- **Scripts Documentation**: [../scripts/README.md](../scripts/README.md) - Script usage details

## Common Scenarios

| Scenario | Documentation to Read | Estimated Time |
|----------|----------------------|----------------|
| **First-time setup** | [../SETUP.md](../SETUP.md) → [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) (Stages 01-02) | 15 min |
| **Generate a course** | [CONFIGURATION.md](CONFIGURATION.md) → [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) (Stages 03-05) | 3-5 hrs |
| **Customize content format** | [FORMATS.md](FORMATS.md) → [CONFIGURATION.md](CONFIGURATION.md) (prompts section) | 20 min |
| **Adjust LLM behavior** | [CONFIGURATION.md](CONFIGURATION.md) (llm_config.yaml) | 10 min |
| **Understanding JSON outlines** | [JSON_OUTLINE.md](JSON_OUTLINE.md) | 20 min |
| **Troubleshooting outline errors** | [JSON_OUTLINE.md](JSON_OUTLINE.md) (Troubleshooting) | 5 min |
| **Troubleshooting generation errors** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) (Troubleshooting) | 10 min |
| **Understanding validation warnings** | [FORMATS.md](FORMATS.md) (Validation and Quality Checks) | 5 min |
| **Understanding log output** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) (Understanding Log Output) | 10 min |
| **Build custom workflow** | [API.md](API.md) (Custom Workflow Examples) | 30 min |
| **Extend with new format** | [ARCHITECTURE.md](ARCHITECTURE.md) (Extension Points) → [API.md](API.md) | 45 min |
| **Run tests** | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) | 2-150s |
| **Improve test coverage** | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) (Coverage Improvement) | 60 min |
| **Understanding module structure** | [ARCHITECTURE.md](ARCHITECTURE.md) (Module Dependencies) | 15 min |
| **Migrate from old config** | [JSON_OUTLINE.md](JSON_OUTLINE.md) (Migration from Static Modules) | 10 min |
| **Configure for high school** | [FORMATS.md](FORMATS.md) (Customization Examples) | 10 min |
| **Configure for university** | [FORMATS.md](FORMATS.md) (Customization Examples) | 10 min |
| **Integrate with Obsidian** | [FORMATS.md](FORMATS.md) (Integration with Other Tools) | 5 min |

## Cross-Reference Matrix


| Topic | Primary Doc | Also See |
|-------|-------------|----------|
| **JSON Outline Format** | [JSON_OUTLINE.md](JSON_OUTLINE.md) | [CONFIGURATION.md](CONFIGURATION.md), [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) |
| **Pipeline Stages** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) | [ARCHITECTURE.md](ARCHITECTURE.md), [JSON_OUTLINE.md](JSON_OUTLINE.md) |
| **Configuration Files** | [CONFIGURATION.md](CONFIGURATION.md) | [JSON_OUTLINE.md](JSON_OUTLINE.md), [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) |
| **Content Formats** | [FORMATS.md](FORMATS.md) | [CONFIGURATION.md](CONFIGURATION.md), [API.md](API.md) |
| **LLM Integration** | [ARCHITECTURE.md](ARCHITECTURE.md) | [CONFIGURATION.md](CONFIGURATION.md), [API.md](API.md) |
| **Generator APIs** | [API.md](API.md) | [FORMATS.md](FORMATS.md), [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Testing** | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md), [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Module Structure** | [ARCHITECTURE.md](ARCHITECTURE.md) | [API.md](API.md), [JSON_OUTLINE.md](JSON_OUTLINE.md) |
| **Troubleshooting** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) | [JSON_OUTLINE.md](JSON_OUTLINE.md), [CONFIGURATION.md](CONFIGURATION.md) |

## Documentation Philosophy

Documentation follows these principles:
- **Modular** - Each file has a focused purpose
- **Complete** - Coverage of each topic
- **Accurate** - Reflects actual implementation
- **Navigable** - Clear signposting and cross-references
- **Actionable** - Includes examples and commands
- **Progressive** - From quick start to deep technical detail
