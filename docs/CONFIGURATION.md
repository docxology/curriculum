# Configuration Guide

Complete reference for all configuration files in the educational course Generator.

## Quick Reference Card

| File | Purpose | Key Sections | When to Edit |
|------|---------|--------------|--------------|
| **`course_config.yaml`** | Course structure | `course.name`, `defaults`, `additional_constraints` | Defining course outline parameters |
| **`llm_config.yaml`** | LLM behavior | `llm.parameters`, `prompts`, `outline_generation` | Adjusting content generation quality |
| **`output_config.yaml`** | Output control | `directories`, `file_naming`, `formats` | Customizing output structure |

**Read time**: 20-30 minutes | **Audience**: Course designers, content customizers

## Overview

The system uses YAML configuration files located in the `config/` directory:

- `course_config.yaml` - Course structure and content specifications (dynamic, LLM-driven)
- `llm_config.yaml` - LLM settings and prompt templates (controls content quality)
- `output_config.yaml` - Output formatting and paths (controls output organization)

## course_config.yaml

Defines the complete course structure with modules, topics, and requirements.

### Structure

```yaml
course:
  name: string                    # Course title
  description: string             # Course description
  level: string                   # Difficulty level
  estimated_duration_weeks: int   # Expected course duration
  additional_constraints: string  # Optional: Additional requirements or constraints
  
  defaults:                       # Configurable defaults
    num_modules: int              # Number of modules to generate
    total_sessions: int           # Total sessions across all modules
    sessions_per_module: null     # Auto-calculated if null
```

### Example

```yaml
course:
  name: "Introductory Biology"
  description: "Comprehensive educational course covering molecular to ecological perspectives"
  level: "Undergraduate Introductory"
  estimated_duration_weeks: 16
  additional_constraints: "Emphasize hands-on lab experiences"
  
  defaults:
    num_modules: 5
    total_sessions: 15
    sessions_per_module: null  # Auto-calculated
```

**Important**: Modules are now **dynamically generated** by the LLM based on these parameters. They are NOT statically defined in this file. The LLM generates a structured JSON outline that is saved to `output/outlines/course_outline_TIMESTAMP.json`.

### Guidelines

- **num_modules**: Number of modules LLM should generate (e.g., 3, 5, 13, 20)
- **total_sessions**: Total class sessions across all modules
- **sessions_per_module**: Leave as `null` to auto-calculate from total_sessions / num_modules
- **additional_constraints**: Optional field for special requirements or topic guidance
  - Examples: "Emphasize hands-on lab experiences", "Include clinical applications", "Focus on molecular biology and genetics"
  - LLM generates all topics based on course description and constraints
  - Use this field to guide topic selection if needed
- **Flexibility**: All defaults can be overridden in interactive mode during outline generation

## llm_config.yaml

Configuration for Ollama LLM integration and prompt templates.

### Structure

```yaml
llm:
  provider: string      # LLM provider (currently "ollama")
  model: string         # Model name (e.g., "gemma3:4b")
  api_url: string       # API endpoint URL
  timeout: int          # Request timeout in seconds
  parameters:           # Generation parameters
    temperature: float  # Randomness (0.0-2.0)
    top_p: float       # Nucleus sampling
    top_k: int         # Top-k sampling
    num_predict: int   # Max tokens to generate
    repeat_penalty: float

outline_generation:     # Outline generation configuration
  items_per_field:      # Min-max bounds for outline fields
    subtopics:
      min: int          # Minimum subtopics per session
      max: int          # Maximum subtopics per session
    learning_objectives:
      min: int          # Minimum objectives per session
      max: int          # Maximum objectives per session
    key_concepts:
      min: int          # Minimum concepts per session
      max: int          # Maximum concepts per session

content_generation:    # Content validation requirements
  lecture:             # Lecture content requirements
    min_examples: int  # Minimum examples required
    max_examples: int  # Maximum examples allowed
    min_sections: int  # Minimum major sections (## headings)
    max_sections: int  # Maximum major sections
    min_word_count: int # Minimum word count
    max_word_count: int # Maximum word count
  study_notes:         # Study notes requirements
    min_key_concepts: int # Minimum key concepts
    max_key_concepts: int # Maximum key concepts
    max_word_count: int   # Maximum word count
  application:         # Application materials requirements
    min_applications: int        # Minimum applications
    max_applications: int        # Maximum applications
    min_words_per_application: int # Minimum words per application
    max_words_per_application: int # Maximum words per application
    max_total_words: int         # Maximum total words
  extension:           # Extension materials requirements
    min_topics: int              # Minimum topics
    max_topics: int              # Maximum topics
    min_words_per_topic: int     # Minimum words per topic
    max_words_per_topic: int     # Maximum words per topic
    max_total_words: int         # Maximum total words
  visualization:       # Visualization requirements
    min_diagram_elements: int    # Minimum diagram elements (nodes + connections)
  integration:         # Integration materials requirements
    min_connections: int         # Minimum cross-module connections
    max_total_words: int        # Maximum total words
  investigation:       # Investigation materials requirements
    min_questions: int         # Minimum research questions
    max_total_words: int        # Maximum total words
  open_questions:      # Open questions requirements
    min_questions: int         # Minimum open questions
    max_total_words: int        # Maximum total words

prompts:
  outline:              # Prompt for outline generation
    system: string      # System prompt
    template: string    # Template with {variables}
  
  lecture:              # Prompt for lecture content
    system: string
    template: string
    
  diagram:              # Prompt for diagram generation
    system: string
    template: string
    
  questions:            # Prompt for question generation
    system: string
    template: string

retry:
  max_attempts: int     # Maximum retry attempts
  backoff_factor: int   # Exponential backoff multiplier
  initial_delay: int    # Initial delay in seconds
```

### Example

```yaml
llm:
  provider: "ollama"
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  timeout: 120
  parameters:
    temperature: 0.7
    top_p: 0.9
    num_predict: 64000   # 64K max output tokens (128K context window)

outline_generation:
  items_per_field:
    subtopics:
      min: 3
      max: 7
    learning_objectives:
      min: 3
      max: 7
    key_concepts:
      min: 3
      max: 7

content_generation:
  lecture:
    min_examples: 5
    max_examples: 15
    min_sections: 4
    max_sections: 8
    min_word_count: 1000
    max_word_count: 1500
  study_notes:
    min_key_concepts: 3
    max_key_concepts: 10
    max_word_count: 1200
  application:
    min_applications: 3
    max_applications: 5
    min_words_per_application: 150
    max_words_per_application: 200
    max_total_words: 1000
  extension:
    min_topics: 3
    max_topics: 4
    min_words_per_topic: 100
    max_words_per_topic: 150
    max_total_words: 600
  visualization:
    min_diagram_elements: 3
  integration:
    min_connections: 3
    max_total_words: 1000
  investigation:
    min_questions: 3
    max_total_words: 1000
  open_questions:
    min_questions: 3
    max_total_words: 1000

prompts:
  lecture:
    system: "You are an expert {subject} educator."
    template: |
      Write a lecture on {module_name}.
      Cover these topics: {subtopics}
      Learning objectives: {objectives}
      Target length: {content_length} words.
```

### Prompt Variables

Available variables for template substitution:

**Outline Template**:
- `{course_name}` - Course title
- `{course_level}` - Course level
- `{course_description}` - Course description
- `{course_duration}` - Estimated duration in weeks
- `{total_sessions}` - Total number of class sessions
- `{num_modules}` - Number of modules to generate
- `{avg_sessions_per_module}` - Average sessions per module
- `{additional_constraints}` - Optional constraints or requirements (can include topic guidance)
- `{min_subtopics}` - Minimum subtopics per session (from outline_generation config)
- `{max_subtopics}` - Maximum subtopics per session (from outline_generation config)
- `{min_objectives}` - Minimum learning objectives per session (from outline_generation config)
- `{max_objectives}` - Maximum learning objectives per session (from outline_generation config)
- `{min_concepts}` - Minimum key concepts per session (from outline_generation config)
- `{max_concepts}` - Maximum key concepts per session (from outline_generation config)

**Lecture Template**:
- `{module_name}` - Module title
- `{subtopics}` - Formatted subtopics list
- `{objectives}` - Formatted learning objectives
- `{key_concepts}` - Key concepts to emphasize
- `{content_length}` - Target word count
- `{outline_context}` - Course outline context
- `{session_number}` - Current session number
- `{total_sessions}` - Total sessions in course
- `{session_title}` - Title of current session
- `{min_examples}` - Minimum examples required (from content_generation config)
- `{max_examples}` - Maximum examples allowed (from content_generation config)
- `{min_sections}` - Minimum sections required (from content_generation config)
- `{max_sections}` - Maximum sections allowed (from content_generation config)
- `{min_word_count}` - Minimum word count (from content_generation config)
- `{max_word_count}` - Maximum word count (from content_generation config)

**Diagram Template**:
- `{topic}` - Diagram topic
- `{context}` - Additional context

**Study Notes Template**:
- `{module_name}` - Module title
- `{subtopics}` - Formatted subtopics list
- `{objectives}` - Formatted learning objectives
- `{key_concepts}` - Key concepts to highlight
- `{lecture_summary}` - Summary of lecture content
- `{min_key_concepts}` - Minimum key concepts required (from content_generation config)
- `{max_key_concepts}` - Maximum key concepts allowed (from content_generation config)
- `{max_word_count}` - Maximum word count (from content_generation config)

**Questions Template**:
- `{module_name}` - Module title
- `{num_questions}` - Total questions
- `{subtopics}` - Subtopics list
- `{objectives}` - Learning objectives
- `{lecture_summary}` - Summary of lecture content
- `{lab_summary}` - Summary of lab exercise
- `{mc_count}` - Number of multiple choice
- `{sa_count}` - Number of short answer
- `{essay_count}` - Number of essay questions

### LLM Parameters Guide

- **temperature** (0.0-2.0): Higher = more creative, lower = more focused
  - Recommended: 0.7 for balanced output
  - Use 0.3-0.5 for factual content
  - Use 0.8-1.0 for creative diagrams

- **top_p** (0.0-1.0): Nucleus sampling threshold
  - Recommended: 0.9
  - Lower for more focused vocabulary

- **top_k**: Number of top tokens to consider
  - Recommended: 40
  - Higher for more variety

- **num_predict**: Maximum tokens in response (with 128K context window)
  - Adjust based on content type
  - Lectures: 50000+ (can generate longer, more detailed content)
  - Questions: 20000
  - Diagrams: 5000
  - Secondary materials: 30000+

### Outline Generation Configuration

The `outline_generation` section controls the number of items generated for each field in course outlines.

**Configuration**:
```yaml
outline_generation:
  items_per_field:
    subtopics:
      min: 3    # Minimum subtopics per session
      max: 7    # Maximum subtopics per session
    learning_objectives:
      min: 3    # Minimum objectives per session
      max: 7    # Maximum objectives per session
    key_concepts:
      min: 3    # Minimum concepts per session
      max: 7    # Maximum concepts per session
```

**Usage Guidelines**:
- **Default bounds (3-7)**: Provides comprehensive coverage without overwhelming detail
- **Narrow bounds (2-4)**: More focused outlines for introductory courses
- **Wide bounds (5-10)**: Detailed outlines for advanced or specialized courses

### Content Generation Requirements

The `content_generation` section defines validation criteria for all generated content types. These requirements are used to automatically validate content quality and generate [COMPLIANT] or [NEEDS REVIEW] status indicators.

**Configuration Structure**:
```yaml
content_generation:
  lecture:
    min_examples: 5
    max_examples: 15
    min_sections: 4
    max_sections: 8
    min_word_count: 1000
    max_word_count: 1500
  study_notes:
    min_key_concepts: 3
    max_key_concepts: 10
    max_word_count: 1200
  application:
    min_applications: 3
    max_applications: 5
    min_words_per_application: 150
    max_words_per_application: 200
    max_total_words: 1000
  extension:
    min_topics: 3
    max_topics: 4
    min_words_per_topic: 100
    max_words_per_topic: 150
    max_total_words: 600
  visualization:
    min_diagram_elements: 3
  integration:
    min_connections: 3
    max_total_words: 1000
  investigation:
    min_questions: 3
    max_total_words: 1000
  open_questions:
    min_questions: 3
    max_total_words: 1000
```

**Primary Materials Requirements**:

- **lecture**: Word count (1000-1500), examples (5-15), sections (4-8)
- **study_notes**: Key concepts (3-10), max words (1200)

**Secondary Materials Requirements**:

- **application**: Applications (3-5), words per application (150-200), max total (1000)
- **extension**: Topics (3-4), words per topic (100-150), max total (600)
- **visualization**: Minimum diagram elements (3 nodes + connections)
- **integration**: Minimum connections (3), max total words (1000)
- **investigation**: Minimum questions (3), max total words (1000)
- **open_questions**: Minimum questions (3), max total words (1000)

**Adjusting Requirements**:

1. **For Shorter Content**: Reduce `max_word_count` and `max_*` values
2. **For Longer Content**: Increase `max_word_count` and `max_*` values
3. **For More Structure**: Increase `min_sections`, `min_applications`, etc.
4. **For Less Structure**: Decrease minimum requirements

**Impact of Changes**:

- **Stricter requirements** (higher minimums, lower maximums): More content will show [NEEDS REVIEW], but quality standards are higher
- **Looser requirements** (lower minimums, higher maximums): More content will show [COMPLIANT], but may allow lower quality
- **Default values**: Balanced for typical educational content

**Validation Behavior**:

- Content is automatically validated after generation
- Warnings are generated for any requirement violations
- [COMPLIANT] status: All requirements met
- [NEEDS REVIEW] status: One or more requirements not met (content may still be usable)
- **Custom bounds**: Adjust based on course complexity and session duration

**Example Configurations**:

```yaml
# Introductory course - focused content
outline_generation:
  items_per_field:
    subtopics: {min: 2, max: 4}
    learning_objectives: {min: 2, max: 4}
    key_concepts: {min: 2, max: 4}

# Standard course - balanced coverage
outline_generation:
  items_per_field:
    subtopics: {min: 3, max: 7}
    learning_objectives: {min: 3, max: 7}
    key_concepts: {min: 3, max: 7}

# Advanced course - comprehensive detail
outline_generation:
  items_per_field:
    subtopics: {min: 5, max: 10}
    learning_objectives: {min: 5, max: 10}
    key_concepts: {min: 5, max: 10}
```

**How It Works**:
- The OutlineGenerator reads these bounds from `llm_config.yaml`
- Values are injected into the outline prompt template as variables
- The LLM is instructed to generate between min-max items for each field
- Each session in the outline will have the specified number of items

## output_config.yaml

Defines output paths, file naming, and formatting rules.

### Structure

```yaml
output:
  base_directory: string     # Root output directory
  
  directories:               # Subdirectory structure
    outlines: string
    lectures: string
    diagrams: string
    questions: string
    modules: string
  
  file_naming:               # Naming conventions
    outline: string          # Template for outline files
    lecture: string          # Template for lecture files
    diagram: string          # Template for diagram files
    questions: string        # Template for question files
    module_combined: string  # Template for combined files
  
  formats:                   # Output formatting
    lectures:
      include_toc: bool
      include_objectives: bool
      include_summary: bool
      heading_level_start: int
    
    diagrams:
      format: string         # "mermaid"
      standalone: bool
      include_description: bool
    
    questions:
      group_by_type: bool
      include_answer_key: bool
      separate_answers: bool
      randomize_options: bool
  
  module_compilation:        # Module bundling
    enabled: bool
    include_components: [string]
    order: [string]
    add_page_breaks: bool
  
  logging:                   # Logging configuration
    level: string            # DEBUG, INFO, WARNING, ERROR
    format: string
    file: string
    console: bool
    verbose_llm: bool        # Set to true for DEBUG-level LLM logs (detailed request/response info)
    show_progress: bool      # Set to true for stream progress updates at INFO level (default: DEBUG)
  
  progress:                  # Progress tracking
    save_checkpoints: bool
    checkpoint_file: string
    resume_on_failure: bool
```

### Example

```yaml
output:
  base_directory: "output"
  
  directories:
    outlines: "outlines"
    modules: "modules"      # Session-based structure: modules/module_XX/session_YY/
    logs: "logs"
    website: "website"
  
  file_naming:
    outline: "course_outline_{timestamp}.md"
    lecture: "module_{module_id:02d}_{module_name_slug}.md"
    diagram: "diagram_{module_id:02d}_{diagram_num}_{topic_slug}.mmd"
    questions: "questions_{module_id:02d}_{module_name_slug}.md"
    module_combined: "module_{module_id:02d}_complete.md"
  
  logging:
    level: "INFO"
    console: true
    verbose_llm: false  # Set to true for detailed LLM request/response logs
    show_progress: false  # Set to true for stream progress at INFO level
```

### Course-Specific Output Directories

When using course templates (from `config/courses/`), generated content is automatically organized into course-specific subdirectories:

**Default Structure** (no course template):
- `output/outlines/`
- `output/modules/`
- `output/logs/`
- `output/website/`

**Course-Specific Structure** (with course template, e.g., `chemistry.yaml`):
- `output/chemistry/outlines/`
- `output/chemistry/modules/`
- `output/chemistry/logs/`
- `output/chemistry/website/`

The course template name is stored in the outline JSON metadata (`course_metadata.course_template`) and automatically used by all generation scripts. You can override this behavior using the `--output-dir` flag in scripts.

### File Naming Variables

- `{module_id}` - Module ID number
- `{module_id:02d}` - Module ID zero-padded to 2 digits
- `{module_name_slug}` - Slugified module name
- `{topic_slug}` - Slugified topic name
- `{diagram_num}` - Diagram number
- `{timestamp}` - Timestamp (YYYYMMDD_HHMMSS)

## Runtime Output Discovery

The system automatically searches multiple locations for generated content, providing flexibility in workspace organization.

### Outline File Discovery

When scripts need course outlines (stages 04 and 05), they search multiple locations:

**Search Order**:
1. Config-specified directory: `{base_directory}/outlines/`
2. Project root: `output/outlines/`
3. Scripts directory: `scripts/output/outlines/`

**Selection Logic**:
- Searches all locations in parallel
- Finds all matching `course_outline_*` files (.json or .md depending on script)
- Selects most recent by file modification time
- Logs the selected file path for transparency

**Script-Specific Behavior**:
- **Script 04 (Primary Materials)**: Searches for `.json` files
- **Script 05 (Secondary Materials)**: Searches for `.md` files

### Override Discovery

Use explicit paths to bypass automatic discovery:

```bash
# Script 04 - Specify JSON outline
uv run python3 scripts/04_generate_primary.py --outline path/to/outline.json

# Script 05 - Specify markdown outline
uv run python3 scripts/05_generate_secondary.py --outline path/to/outline.md
```

### Why Multiple Locations?

- **Workspace Flexibility**: Run scripts from any directory
- **Development/Production**: Separate outputs for testing vs final
- **User Control**: Config specifies preference, but all locations work

### Example Discovery Log

```
2024-12-08 14:17:13 - INFO - Using most recent outline from output/outlines/
2024-12-08 14:17:13 - INFO - Loading most recent outline JSON from: /Users/user/biology/scripts/output/outlines/course_outline_20241208_141121.json
```

## Environment Variables

While not currently used, the system could support:

```bash
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=gemma3:4b
OUTPUT_DIR=/custom/output/path
LOG_LEVEL=DEBUG
```

## Validation

The system validates configurations on startup:

1. **Required Fields**: All required fields must be present
2. **Type Checking**: Values must match expected types
3. **File Existence**: Config files must exist
4. **YAML Syntax**: Valid YAML syntax required

Run validation explicitly:

```python
from src.config.loader import ConfigLoader

config = ConfigLoader("config")
config.validate_all_configs()  # Raises ConfigurationError if invalid
```

## Best Practices

1. **Version Control**: Commit config files to track changes
2. **Comments**: Add YAML comments to document decisions
3. **Backups**: Keep backup configs before major changes
4. **Testing**: Test with small configs before full runs
5. **Validation**: Always validate after editing

## Troubleshooting

**"Config file not found"**
- Check config directory path
- Ensure all three YAML files exist

**"Missing required field"**
- Check validation error message for specific field
- Compare against structure above

**"Invalid YAML"**
- Check for syntax errors (indentation, colons, quotes)
- Use online YAML validator

**"LLM connection error"**
- Verify Ollama is running: `curl http://localhost:11434/api/version`
- Check `api_url` in `llm_config.yaml`
- Verify model is downloaded: `ollama list`

## Advanced Configuration

### Custom Prompt Templates

Create specialized prompts for different content styles:

```yaml
prompts:
  lecture_detailed:
    system: "You are a detailed {subject} educator."
    template: "Comprehensive lecture with examples..."
  
  lecture_concise:
    system: "You are a concise {subject} educator."
    template: "Brief overview covering..."
```

### Module-Specific Settings

While not directly supported, you can:
1. Create multiple config files for different module sets
2. Run pipeline with different configs
3. Combine outputs

### Output Customization

Modify output format through `output_config.yaml`:
- Change directory structure
- Customize file naming patterns
- Adjust content formatting
- Configure logging verbosity

---

## Related Documentation

### Essential Context
- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - How `course_config.yaml` drives JSON outline generation
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - How configurations are used in each pipeline stage
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Configuration layer in system architecture

### Practical Application
- **[FORMATS.md](FORMATS.md)** - How LLM prompts produce each content format
- **[API.md](API.md)** - `ConfigLoader` API for programmatic access
- **[TESTING_COVERAGE.md](TESTING_COVERAGE.md)** - Configuration validation tests

### Specific Topics
| Topic | Reference |
|-------|-----------|
| **Course structure** | This document → `course_config.yaml` |
| **JSON outline generation** | [JSON_OUTLINE.md](JSON_OUTLINE.md) → Configuration Source |
| **LLM prompts** | This document → `llm_config.yaml` → prompts |
| **Outline item counts** | This document → `outline_generation.items_per_field` |
| **Output paths** | This document → `output_config.yaml` |
| **Multi-location discovery** | This document → Runtime Output Discovery |
| **API usage** | [API.md](API.md) → ConfigLoader |
| **Validation** | This document → Validation section |

