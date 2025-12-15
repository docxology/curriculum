# Technical Documentation - For AI Agents

## Purpose

This directory contains comprehensive technical documentation for the educational course Generator. All documentation follows evergreen principles - permanent knowledge only, no temporary progress reports.

## Documentation Files

### Core Architecture

**[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and implementation
- Design principles (modular, configuration-driven, no mocks, pipeline-based)
- Component layers (Configuration, LLM, Generation, Processing, Orchestration, Utility)
- Data flow diagrams (YAML → JSON outline → Content)
- Module dependencies and interactions
- Error handling and logging strategies
- Extension points for customization
- Performance and security considerations

**When to read**: Understanding system internals, extending functionality, debugging

### Pipeline and Workflows

**[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - 6-stage pipeline execution
- **Stage 01**: Environment Setup (`01_setup_environment.py`)
- **Stage 02**: Validation & Tests (`02_run_tests.py`)
- **Stage 03**: Generate Outline (`03_generate_outline.py`)
- **Stage 04**: Generate Primary Materials (`04_generate_primary.py`)
- **Stage 05**: Generate Secondary Materials (`05_generate_secondary.py`)
- **Stage 06**: Generate Website (`06_website.py`)
- Full pipeline orchestration (`run_pipeline.py`)
- Workflow examples and best practices
- Error handling, monitoring, troubleshooting

**When to read**: Running the pipeline, understanding workflow, troubleshooting

### Data Structures

**[JSON_OUTLINE.md](JSON_OUTLINE.md)** - JSON outline format and lifecycle
- JSON schema and field definitions
- Generation process (Stage 03, interactive vs non-interactive)
- Consumption process (Stages 04-05, session-based content)
- Multi-location discovery mechanism
- Validation rules and normalization
- Migration from static modules
- Best practices and troubleshooting

**When to read**: Understanding course structure, debugging outline issues

### Configuration

**[CONFIGURATION.md](CONFIGURATION.md)** - Complete YAML configuration reference
- `course_config.yaml` - Course structure, defaults, topic areas
- `llm_config.yaml` - LLM settings, prompts, outline generation bounds
- `output_config.yaml` - Output paths, naming, formatting, logging
- Environment variables and validation
- LLM parameter tuning guide
- Best practices and troubleshooting

**When to read**: Configuring courses, adjusting LLM behavior, customizing output

### Content Formats

**[FORMATS.md](FORMATS.md)** - Content format specifications
- **Primary Materials** (Stage 04): Lectures, Labs, Study Notes, Diagrams, Questions
- **Secondary Materials** (Stage 05): Application, Extension, Visualization, Integration, Investigation, Open Questions
- Format structure and examples
- LLM prompt templates
- Customization options (high school vs university, lab-heavy, self-study)
- Output directory structure (session-based)
- Integration with Obsidian, Markdown editors, LMS

**When to read**: Understanding output formats, customizing content types

### API Reference

**[API.md](API.md)** - Complete public API documentation
- Configuration Layer: `ConfigLoader`
- LLM Integration Layer: `OllamaClient`
- Generation Layer: `ContentGenerator`, `OutlineGenerator`
- Processing Layer: `OutlineParser`, `ContentCleanup`
- Format Generators: `LectureGenerator`, `LabGenerator`, `StudyNotesGenerator`, `DiagramGenerator`, `QuestionGenerator`
- Utility Layer: File I/O, text processing, system checks
- Type hints, examples, error handling
- Custom workflow examples

**When to read**: Building custom workflows, integrating with other systems

### Testing

**[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Test suite overview
- Test statistics (~540 tests across 25 files, NO MOCKS)
- Unit vs integration tests (fast tests <2s, slow tests ~150s)
- Coverage metrics (~30% without Ollama, ~75% with integration tests)
- Test organization by functionality and speed
- Running tests (unit-only, full suite, coverage reports)
- Coverage improvement roadmap
- CI/CD integration guidelines

**When to read**: Running tests, improving coverage, setting up CI/CD

### Technical Deep Dives

**[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns and exception hierarchy
- Exception hierarchy and usage
- Error handling patterns by layer
- Error recovery strategies
- Error message guidelines
- Common error scenarios and solutions

**When to read**: Understanding error handling, debugging failures, implementing error recovery

**[LOGGING.md](LOGGING.md)** - Logging patterns and debugging
- Logging levels and usage
- Structured logging patterns
- Request ID tracing
- Operation context logging
- Log analysis and debugging

**When to read**: Debugging issues, analyzing logs, understanding system behavior

**LLM-Specific Documentation**:
- **[../src/llm/TROUBLESHOOTING.md](../src/llm/TROUBLESHOOTING.md)** - Comprehensive LLM troubleshooting guide (connection issues, timeouts, model problems)
- **[../src/llm/HEALTH_MONITORING.md](../src/llm/HEALTH_MONITORING.md)** - Health monitoring and diagnostics for Ollama service
- **LLM Module**: [../src/llm/AGENTS.md](../src/llm/AGENTS.md) - Complete LLM integration documentation including health monitoring and request handling

**[VALIDATION.md](VALIDATION.md)** - Content validation rules and criteria
- Validation criteria for all content types
- Configuration and customization
- Validation troubleshooting
- Custom validation rules

**When to read**: Understanding validation, troubleshooting validation issues, customizing criteria

**[EXTENSION.md](EXTENSION.md)** - Extension guide for adding new features
- Adding new content types and generators
- Adding new configuration options
- Adding new pipeline stages
- Custom workflows and integration patterns

**When to read**: Extending the system, adding new features, creating custom workflows

**[DATA_FLOW.md](DATA_FLOW.md)** - Data flow and transformations
- Data structure evolution (YAML → JSON → Content)
- Detailed transformations at each stage
- Data validation points
- Data flow troubleshooting

**When to read**: Understanding data transformations, debugging data flow issues

**[MODULE_ORGANIZATION.md](MODULE_ORGANIZATION.md)** - Module structure and organization
- Module structure and dependencies
- Import patterns and standards
- Module interface contracts
- Adding new modules workflow

**When to read**: Understanding module structure, adding new modules, organizing code

**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide
- Common issues by category
- Issue diagnosis workflow
- Solution patterns
- Recovery procedures

**When to read**: Troubleshooting issues, diagnosing problems, recovering from failures

**[PERFORMANCE.md](PERFORMANCE.md)** - Performance considerations and optimization
- Performance characteristics by stage
- Optimization strategies
- Performance monitoring
- Performance testing

**When to read**: Optimizing performance, monitoring system performance, performance testing

**[SECURITY.md](SECURITY.md)** - Security considerations and best practices
- Security model overview
- Input validation and sanitization
- File path security
- Security best practices

**When to read**: Understanding security model, implementing security best practices

**[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and production use
- Production environment setup
- Configuration for production
- Monitoring and logging
- Backup and recovery

**When to read**: Deploying to production, production configuration, monitoring

**[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and workflow
- Development setup
- Code standards and testing requirements
- Contribution workflow
- Documentation requirements

**When to read**: Contributing to the project, understanding development standards


## Quick Task Reference

| I want to... | Read this |
|--------------|-----------|
| **Understand system design** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Run the pipeline** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) |
| **Understand JSON outlines** | [JSON_OUTLINE.md](JSON_OUTLINE.md) |
| **Configure course content** | [CONFIGURATION.md](CONFIGURATION.md) |
| **Customize output formats** | [FORMATS.md](FORMATS.md) |
| **Use the public API** | [API.md](API.md) |
| **Review test coverage** | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) |
| **Review codebase quality** | [ARCHITECTURE.md](ARCHITECTURE.md), [TESTING_COVERAGE.md](TESTING_COVERAGE.md) |
| **Understand data flow** | [ARCHITECTURE.md](ARCHITECTURE.md) → Data Flow section |
| **Troubleshoot generation** | [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) → Troubleshooting |
| **Troubleshoot LLM issues** | [../src/llm/TROUBLESHOOTING.md](../src/llm/TROUBLESHOOTING.md) |
| **Monitor LLM health** | [../src/llm/HEALTH_MONITORING.md](../src/llm/HEALTH_MONITORING.md) |
| **Extend functionality** | [ARCHITECTURE.md](ARCHITECTURE.md) → Extension Points |
| **Build custom workflow** | [API.md](API.md) → Custom Workflow Examples |

## Documentation Principles

All documentation in this directory follows these principles:

### Evergreen Documentation
✅ **Permanent knowledge only** - No temporary progress reports  
✅ **No "TODO" sections** - Use issue tracker instead  
✅ **No dated content** - Avoid "As of Dec 2024" unless critical  
✅ **Architecture over implementation** - Explain why, not just how  
✅ **Examples that last** - Use realistic, timeless examples  

### Quality Standards
✅ **Complete** - Comprehensive coverage of each topic  
✅ **Accurate** - Reflects actual implementation  
✅ **Navigable** - Clear signposting and cross-references  
✅ **Actionable** - Includes examples and commands  
✅ **Progressive** - From quick start to deep technical detail  
✅ **Modular** - Each file has a focused purpose  

### Maintenance Guidelines
✅ **Update with code changes** - Keep docs synchronized  
✅ **Verify cross-references** - Ensure links work  
✅ **Remove obsolete content** - Delete outdated information  
✅ **Consolidate duplicates** - Single source of truth  
✅ **Link, don't duplicate** - Reference other docs  

## Documentation Update Workflow

When making code changes:

1. **Identify affected docs** - Check which files need updates
2. **Update content** - Modify relevant sections
3. **Verify cross-references** - Ensure links still work
4. **Check examples** - Test code examples still run
5. **Update navigation** - Adjust README.md if needed

## Common Documentation Tasks

### Adding a New Feature

Update these docs:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Add to component description
- [API.md](API.md) - Document new public APIs
- [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) - If it's a new stage/script
- [FORMATS.md](FORMATS.md) - If it's a new content type
- [README.md](README.md) - Update quick reference

### Changing Configuration

Update these docs:
- [CONFIGURATION.md](CONFIGURATION.md) - Update YAML reference
- [../config/README.md](../config/README.md) - Update examples
- [../config/AGENTS.md](../config/AGENTS.md) - Update agent guidance

### Modifying Pipeline

Update these docs:
- [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) - Update stage descriptions
- [../scripts/README.md](../scripts/README.md) - Update script reference
- [../scripts/AGENTS.md](../scripts/AGENTS.md) - Update agent guidance

### Adding Tests

Update these docs:
- [TESTING_COVERAGE.md](TESTING_COVERAGE.md) - Update test counts
- [../tests/README.md](../tests/README.md) - Update test descriptions
- [../tests/AGENTS.md](../tests/AGENTS.md) - Update test organization

## Cross-Reference Matrix

Where topics are covered across multiple documents:

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
| **Code Quality** | [ARCHITECTURE.md](ARCHITECTURE.md) | [TESTING_COVERAGE.md](TESTING_COVERAGE.md) |

## Documentation Quality Checks

Before considering documentation complete:

- [ ] All code examples tested and working
- [ ] All cross-references verified
- [ ] No broken links
- [ ] No temporary/dated content (unless necessary)
- [ ] No TODO sections
- [ ] Consistent formatting
- [ ] Proper heading hierarchy
- [ ] Table of contents if >500 lines
- [ ] Examples for all features
- [ ] Troubleshooting section included

## What NOT to Include

❌ **Temporary progress reports** - Use git log instead  
❌ **Implementation TODOs** - Use issue tracker  
❌ **Dated status updates** - Keep evergreen  
❌ **Personal notes** - Keep professional  
❌ **Redundant content** - Link to single source  
❌ **Mock examples** - All examples use real implementations  


## When to Read Each Document

### Start Here
- **New to project**: [ARCHITECTURE.md](ARCHITECTURE.md) → [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) → [CONFIGURATION.md](CONFIGURATION.md)
- **Want to run pipeline**: [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)
- **Want to understand formats**: [FORMATS.md](FORMATS.md)

### Development Tasks
- **Extending functionality**: [ARCHITECTURE.md](ARCHITECTURE.md) → [API.md](API.md)
- **Adding new content type**: [FORMATS.md](FORMATS.md) → [API.md](API.md)
- **Modifying pipeline**: [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Changing configuration**: [CONFIGURATION.md](CONFIGURATION.md)
- **Understanding JSON outlines**: [JSON_OUTLINE.md](JSON_OUTLINE.md)

### Troubleshooting
- **Pipeline issues**: [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) → Troubleshooting section
- **Configuration errors**: [CONFIGURATION.md](CONFIGURATION.md) → Validation section
- **Outline problems**: [JSON_OUTLINE.md](JSON_OUTLINE.md) → Troubleshooting section
- **Test failures**: [TESTING_COVERAGE.md](TESTING_COVERAGE.md) → Running tests section

### Code Review
- **Understanding codebase**: [ARCHITECTURE.md](ARCHITECTURE.md), [TESTING_COVERAGE.md](TESTING_COVERAGE.md)
- **API usage**: [API.md](API.md)
- **Test coverage**: [TESTING_COVERAGE.md](TESTING_COVERAGE.md)

## Documentation Update Workflow

When making code changes:

1. **Identify affected docs** - Check which files need updates
2. **Update content** - Modify relevant sections
3. **Verify cross-references** - Ensure links still work
4. **Check examples** - Test code examples still run
5. **Update navigation** - Adjust this AGENTS.md if needed

### Update Checklist

- [ ] All code examples tested and working
- [ ] All cross-references verified
- [ ] No broken links
- [ ] No temporary/dated content (unless necessary)
- [ ] No TODO sections
- [ ] Consistent formatting
- [ ] Proper heading hierarchy
- [ ] Examples for all features
- [ ] Troubleshooting section included (if applicable)

## See Also

- **Main README**: [../README.md](../README.md) - Quick start and navigation hub
- **Setup Guide**: [../SETUP.md](../SETUP.md) - Installation and prerequisites
- **Development Rules**: [../.cursorrules/README.md](../.cursorrules/README.md) - All 12 modular rule files
- **Agent Guide**: [../AGENTS.md](../AGENTS.md) - High-level overview for AI agents
- **Config Docs**: [../config/AGENTS.md](../config/AGENTS.md) - Configuration guide
- **Script Docs**: [../scripts/AGENTS.md](../scripts/AGENTS.md) - Script usage
- **Test Docs**: [../tests/AGENTS.md](../tests/AGENTS.md) - Testing guide

