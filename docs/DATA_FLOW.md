# Data Flow Guide

Complete reference for data flow, transformations, and data structure evolution throughout the educational course Generator pipeline.

## Quick Reference Card

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| **Stage 01** | YAML configs | Validation | Validated configs |
| **Stage 03** | YAML configs | LLM generation | JSON outline + Markdown |
| **Stage 04** | JSON outline | LLM generation | Session content (markdown) |
| **Stage 05** | JSON outline + Primary materials | LLM synthesis | Secondary materials (markdown) |
| **Stage 06** | JSON outline + All content | HTML conversion | Single HTML website |

**Read time**: 25-35 minutes | **Audience**: Developers, system architects, contributors

## Overview

The educational course Generator transforms data through multiple stages:

1. **Configuration** (YAML) → **Structured Outline** (JSON)
2. **Structured Outline** (JSON) → **Content Materials** (Markdown)
3. **Content Materials** (Markdown) → **Website** (HTML)

Each stage transforms data structures and adds new information while preserving the original structure.

## Data Structure Evolution

### Stage 0: Initial Configuration (YAML)

**Input**: YAML configuration files

**Structure**:
```yaml
# course_config.yaml
course:
  name: "Introductory Biology"
  description: "Comprehensive educational course..."
  level: "Undergraduate Introductory"
  estimated_duration_weeks: 16
  defaults:
    num_modules: 5
    total_sessions: 15
  additional_constraints: "Emphasize hands-on lab experiences"

# llm_config.yaml
llm:
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  timeout: 120
  parameters:
    temperature: 0.7
    top_p: 0.9
    num_predict: 64000   # 64K max output tokens (128K context window)

prompts:
  outline:
    system: "You are an expert biology curriculum designer..."
    template: "Generate a course outline with {num_modules} modules..."

# output_config.yaml
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
    modules: "modules"
```

**Characteristics**:
- Human-readable configuration
- Hierarchical structure
- Type-safe (validated on load)
- Cached after first load

### Stage 1: Configuration Loading

**Transformation**: YAML → Python dictionaries

**Process**:
1. `ConfigLoader` reads YAML files
2. Validates structure and types
3. Caches in memory
4. Provides typed accessor methods

**Data Structure**:
```python
{
    'course': {
        'name': 'Introductory Biology',
        'description': '...',
        'level': 'Undergraduate Introductory',
        'estimated_duration_weeks': 16,
        'defaults': {
            'num_modules': 5,
            'total_sessions': 15
        }
    },
    'llm': {
        'model': 'gemma3:4b',
        'api_url': '...',
        'parameters': {...}
    },
    'prompts': {
        'outline': {
            'system': '...',
            'template': '...'
        }
    }
}
```

**Access Methods**:
```python
config_loader.get_course_info()
config_loader.get_llm_parameters()
config_loader.get_prompt_template("outline")
```

### Stage 2: Outline Generation (Stage 03)

**Transformation**: YAML config → JSON outline

**Process**:
1. Extract course metadata from `course_config.yaml`
2. Extract outline generation bounds from `llm_config.yaml`
3. Format prompt template with variables
4. LLM generates structured JSON outline
5. Validate and normalize JSON structure
6. Save as both `.json` and `.md` files

**Input Data**:
```python
{
    'course_name': 'Introductory Biology',
    'course_level': 'Undergraduate Introductory',
    'num_modules': 5,
    'total_sessions': 15,
    'min_subtopics': 3,
    'max_subtopics': 7,
    # ... more variables
}
```

**Output Data Structure** (JSON):
```json
{
  "course_metadata": {
    "name": "Introductory Biology",
    "description": "Comprehensive educational course...",
    "level": "Undergraduate Introductory",
    "duration_weeks": 16,
    "total_sessions": 15,
    "total_modules": 5,
    "generated": "2024-12-09T12:00:00Z"
  },
  "modules": [
    {
      "module_id": 1,
      "module_name": "Molecular and Cellular Foundations",
      "sessions": [
        {
          "session_number": 1,
          "session_title": "Chemical Basis of Life",
          "subtopics": [
            "Chemical basis of life",
            "Water properties and biological molecules",
            "Macromolecule structure and function"
          ],
          "learning_objectives": [
            "Explain the chemical basis of biological processes",
            "Describe the properties of water relevant to life",
            "Compare and contrast the four major macromolecule classes"
          ],
          "key_concepts": [
            "Biochemistry fundamentals",
            "Organic chemistry in biology",
            "Molecular interactions"
          ],
          "rationale": "This session provides the foundation for understanding biological processes at the molecular level"
        }
      ]
    }
  ]
}
```

**Key Transformations**:
- **Metadata extraction**: Course info from YAML → JSON metadata
- **Structure generation**: LLM creates module/session structure
- **Normalization**: Sequential IDs, validation, type checking
- **Dual format**: Both JSON (machine-readable) and Markdown (human-readable)

### Stage 3: Primary Materials Generation (Stage 04)

**Transformation**: JSON outline → Session-based content files

**Process**:
1. Load JSON outline
2. For each module → each session:
   - Extract session data (subtopics, objectives, concepts)
   - Generate lecture (with session context)
   - Generate lab (with lecture context)
   - Generate study notes (with lecture + lab context)
   - Generate diagrams (with session context)
   - Generate questions (with lecture + lab context)
3. Apply content cleanup
4. Save to session directories

**Input Data** (from JSON outline):
```python
{
    'module_id': 1,
    'module_name': 'Molecular and Cellular Foundations',
    'sessions': [
        {
            'session': 1,
            'subtopics': ['Chemical basis of life', ...],
            'learning_objectives': ['Explain...', ...],
            'key_concepts': ['Biochemistry fundamentals', ...]
        }
    ]
}
```

**Output Data Structure** (Files):
```
output/modules/module_01_molecular_and_cellular_foundations/
  session_01/
    lecture.md          # Markdown lecture content
    lab.md              # Markdown lab exercise
    study_notes.md      # Markdown study notes
    diagram_1.mmd       # Mermaid diagram
    diagram_2.mmd       # Mermaid diagram
    questions.md        # Markdown questions
```

**Content Transformations**:
- **Session data** → **Lecture content** (2000-4000 words)
- **Session data + Lecture** → **Lab content** (1000-2000 words)
- **Session data + Lecture + Lab** → **Study notes** (500-1000 words)
- **Session data** → **Diagrams** (Mermaid code)
- **Session data + Lecture + Lab** → **Questions** (20-30 items)

**Context Flow**:
```
Session Data
    ↓
Lecture (uses session data)
    ↓
Lab (uses session data + lecture)
    ↓
Study Notes (uses session data + lecture + lab)
    ↓
Questions (uses session data + lecture + lab)
```

### Stage 4: Secondary Materials Generation (Stage 05)

**Transformation**: JSON outline + Primary materials → Secondary materials

**Process**:
1. Load JSON outline
2. For each module → each session:
   - Read all primary materials from session folder
   - Synthesize session-level context (using all session materials)
   - Generate application (real-world uses)
   - Generate extension (advanced topics)
   - Generate visualization (additional diagrams)
   - Generate integration (cross-module connections)
   - Generate investigation (research questions)
   - Generate open questions (scientific debates)
3. Apply content cleanup
4. Save directly to session directories (flat structure: `session_XX/[type].md`)

**Input Data**:
- JSON outline (module/session structure)
- Primary materials files (lecture.md, lab.md, study_notes.md, etc.)

**Output Data Structure** (Files):
```
output/modules/module_01_molecular_and_cellular_foundations/
  session_01/
    lecture.md              # From Stage 04
    lab.md                  # From Stage 04
    study_notes.md          # From Stage 04
    diagram_1.mmd           # From Stage 04
    questions.md            # From Stage 04
    application.md          # From Stage 05
    extension.md            # From Stage 05
    visualization.mmd       # From Stage 05
    integration.md          # From Stage 05
    investigation.md        # From Stage 05
    open_questions.md       # From Stage 05
```

**Content Transformations**:
- **Primary materials + Session context** → **Application** (real-world uses)
- **Primary materials + Session context** → **Extension** (advanced topics)
- **Primary materials + Session context** → **Visualization** (concept maps)
- **Primary materials + Module context** → **Integration** (cross-module connections)
- **Primary materials + Session context** → **Investigation** (research questions)
- **Primary materials + Session context** → **Open Questions** (scientific debates)

### Stage 5: Website Generation (Stage 06)

**Transformation**: JSON outline + All content → Single HTML website

**Process**:
1. Load JSON outline
2. Discover all content files (lectures, labs, diagrams, etc.)
3. Convert markdown to HTML
4. Generate navigation structure
5. Embed CSS and JavaScript
6. Create single HTML file

**Input Data**:
- JSON outline (course structure)
- All markdown content files
- All Mermaid diagram files

**Output Data Structure** (File):
```
output/website/
  index.html  # Single HTML file containing entire website
```

**Content Transformations**:
- **Markdown** → **HTML** (with proper formatting)
- **Mermaid diagrams** → **HTML** (with Mermaid.js rendering)
- **File structure** → **Navigation structure** (modules → sessions → content types)
- **Multiple files** → **Single HTML file** (self-contained)

## Detailed Data Flow by Stage

### Stage 01: Environment Setup

**Data Flow**:
```
YAML Configs (course_config.yaml, llm_config.yaml, output_config.yaml)
    ↓
ConfigLoader.load_*_config()
    ↓
Validation (validate_all_configs())
    ↓
Validated Configs (cached in memory)
```

**No data transformation** - Only validation and caching

### Stage 02: Validation & Tests

**Data Flow**:
```
Validated Configs
    ↓
ConfigLoader.validate_all_configs()
    ↓
Validation Results (pass/fail)
    ↓
Optional: Test Execution
    ↓
Test Results (pass/fail/skip counts)
```

**No data transformation** - Only validation and testing

### Stage 03: Outline Generation

**Data Flow**:
```
YAML Configs
    ↓
ConfigLoader.get_course_info()
ConfigLoader.get_outline_bounds()
ConfigLoader.get_prompt_template("outline")
    ↓
Template Variables
{
    'course_name': '...',
    'num_modules': 5,
    'total_sessions': 15,
    'min_subtopics': 3,
    'max_subtopics': 7,
    ...
}
    ↓
LLM.generate_with_template()
    ↓
Raw LLM Response (markdown with JSON code block)
    ↓
JSON Extraction (extract JSON from markdown)
    ↓
JSON Validation (validate structure, required fields)
    ↓
JSON Normalization (sequential IDs, type checking)
    ↓
JSON Outline (validated, normalized)
    ↓
Save to file (course_outline_TIMESTAMP.json + .md)
```

**Key Transformations**:
1. **YAML → Template Variables**: Extract config values
2. **Template Variables → LLM Prompt**: Format template with variables
3. **LLM Prompt → Raw Response**: LLM generates markdown with JSON
4. **Raw Response → JSON**: Extract JSON from markdown code block
5. **JSON → Validated JSON**: Validate structure and fields
6. **Validated JSON → Normalized JSON**: Sequential IDs, type checking

### Stage 04: Primary Materials Generation

**Data Flow** (per session):
```
JSON Outline
    ↓
ConfigLoader.load_outline_from_json()
    ↓
Module/Session Structure
{
    'module_id': 1,
    'module_name': '...',
    'sessions': [
        {
            'session': 1,
            'subtopics': [...],
            'learning_objectives': [...],
            'key_concepts': [...]
        }
    ]
}
    ↓
For each session:
    Session Data
        ↓
    LectureGenerator.generate_lecture()
        ↓
    Lecture Content (markdown)
        ↓
    LabGenerator.generate_lab() [uses lecture context]
        ↓
    Lab Content (markdown)
        ↓
    StudyNotesGenerator.generate_study_notes() [uses lecture + lab]
        ↓
    Study Notes Content (markdown)
        ↓
    DiagramGenerator.generate_diagram() [per diagram]
        ↓
    Diagram Content (Mermaid code)
        ↓
    QuestionGenerator.generate_questions() [uses lecture + lab]
        ↓
    Questions Content (markdown)
        ↓
    Content Cleanup (remove artifacts, standardize placeholders)
        ↓
    Save to session directory
```

**Key Transformations**:
1. **JSON Session Data → Lecture**: Session subtopics/objectives → comprehensive lecture
2. **Lecture → Lab**: Lecture content provides context for lab exercises
3. **Lecture + Lab → Study Notes**: Synthesize into concise notes
4. **Session Data → Diagrams**: Visual representations of concepts
5. **Lecture + Lab → Questions**: Assessment questions based on content
6. **Raw Content → Cleaned Content**: Remove conversational artifacts, standardize placeholders

### Stage 05: Secondary Materials Generation

**Data Flow** (per session):
```
JSON Outline + Primary Materials Files
    ↓
Load session primary materials
{
    'lecture': '...',
    'lab': '...',
    'study_notes': '...',
    'diagrams': [...],
    'questions': '...'
}
    ↓
For each secondary type:
    Primary Materials + Session Context
        ↓
    SecondaryGenerator.generate_*()
        ↓
    Secondary Materials (markdown)
        ↓
    Content Cleanup
        ↓
    Save to session directory
```

**Key Transformations**:
1. **Primary Materials → Application**: Real-world uses and case studies
2. **Primary Materials → Extension**: Advanced topics beyond core
3. **Primary Materials → Visualization**: Additional concept maps
4. **Primary Materials + Module Context → Integration**: Cross-module connections
5. **Primary Materials → Investigation**: Research questions
6. **Primary Materials → Open Questions**: Scientific debates

### Stage 06: Website Generation

**Data Flow**:
```
JSON Outline
    ↓
WebsiteGenerator.load_outline()
    ↓
Course Structure
{
    'modules': [
        {
            'module_id': 1,
            'module_name': '...',
            'sessions': [...]
        }
    ]
}
    ↓
Content Discovery
    ↓
All Content Files
{
    'lectures': [...],
    'labs': [...],
    'study_notes': [...],
    'diagrams': [...],
    'questions': [...],
    'secondary': [...]
}
    ↓
Markdown → HTML Conversion
    ↓
Navigation Structure Generation
    ↓
HTML Assembly (with embedded CSS/JS)
    ↓
Single HTML File (index.html)
```

**Key Transformations**:
1. **JSON Outline → Navigation Structure**: Module/session hierarchy
2. **Markdown → HTML**: Convert all markdown content
3. **Mermaid → HTML**: Embed Mermaid.js for diagram rendering
4. **Multiple Files → Single File**: Combine all content into one HTML file

## Data Validation Points

### Configuration Validation

**Location**: `ConfigLoader.validate_all_configs()`

**Validates**:
- File existence
- YAML syntax
- Required fields
- Type correctness
- Value ranges

**Errors**: Raise `ConfigurationError` with clear messages

### Outline Validation

**Location**: `OutlineGenerator.validate_outline()`

**Validates**:
- JSON structure
- Required fields (course_metadata, modules)
- Module structure (module_id, module_name, sessions)
- Session structure (session, subtopics, objectives, key_concepts)
- Sequential IDs
- Field counts (within bounds)

**Errors**: Raise `ValueError` with validation details

### Content Validation

**Location**: `src.utils.content_analysis.analyzers`

**Validates**:
- Word counts (within ranges)
- Element counts (examples, sections, concepts)
- Format compliance (question format, key concept format)
- Structure completeness (answers, explanations)

**Warnings**: Logged as [NEEDS REVIEW] status

## Data Caching Strategies

### Configuration Caching

**Location**: `ConfigLoader`

**Strategy**:
- Load configs once on first access
- Cache in instance variables (`_course_config`, `_llm_config`, `_output_config`)
- No reloading unless explicitly requested

**Benefits**:
- Faster subsequent access
- Consistent data throughout execution
- Reduced file I/O

### Outline Caching

**Location**: `ConfigLoader.load_outline_from_json()`

**Strategy**:
- Load JSON once per ConfigLoader instance
- Cache parsed structure
- Reuse across multiple generators

**Benefits**:
- Avoid redundant JSON parsing
- Consistent module structure
- Faster content generation

## Data Dependencies

### Dependency Graph

```
YAML Configs
    ↓
ConfigLoader (validates, caches)
    ↓
    ├─→ OutlineGenerator (Stage 03)
    │       ↓
    │   JSON Outline
    │       ↓
    │   └─→ ContentGenerator (Stage 04)
    │           ↓
    │       Primary Materials
    │           ↓
    │       └─→ Secondary Generators (Stage 05)
    │               ↓
    │           Secondary Materials
    │               ↓
    │           └─→ WebsiteGenerator (Stage 06)
    │                   ↓
    │               HTML Website
    │
    └─→ LLM Client (all stages)
            ↓
        Ollama API
```

### Dependency Rules

1. **Stage 03** depends on: YAML configs
2. **Stage 04** depends on: JSON outline (from Stage 03)
3. **Stage 05** depends on: JSON outline + Primary materials (from Stage 04)
4. **Stage 06** depends on: JSON outline + All content (from Stages 04-05)

## Data Flow Troubleshooting

### Issue: Outline Not Found

**Problem**: Stage 04/05 can't find JSON outline

**Data Flow Check**:
1. Verify Stage 03 completed successfully
2. Check outline file exists: `output/outlines/course_outline_*.json`
3. Verify multi-location search paths
4. Check file permissions

**Solution**: Run Stage 03 first, or specify outline path explicitly

### Issue: Missing Primary Materials

**Problem**: Stage 05 can't find primary materials

**Data Flow Check**:
1. Verify Stage 04 completed successfully
2. Check session directories exist: `output/modules/module_XX/session_YY/`
3. Verify expected files present (lecture.md, lab.md, etc.)
4. Check file permissions

**Solution**: Run Stage 04 first, or regenerate missing content

### Issue: Invalid JSON Structure

**Problem**: JSON outline has invalid structure

**Data Flow Check**:
1. Check JSON syntax (valid JSON)
2. Verify required fields present
3. Check field types (integers, strings, arrays)
4. Review validation logs

**Solution**: Regenerate outline (Stage 03), or manually fix JSON

### Issue: Content Not Generated

**Problem**: Expected content files missing

**Data Flow Check**:
1. Check generation logs for errors
2. Verify LLM connectivity
3. Check output directory permissions
4. Review error collection in pipeline

**Solution**: Check logs, verify LLM availability, check permissions

## Performance Considerations

### Data Loading Performance

- **Config loading**: Cached after first load (fast)
- **Outline loading**: JSON parsing (moderate, cached)
- **Content loading**: File I/O (moderate, per file)

### Data Transformation Performance

- **YAML → JSON**: LLM generation (slow, ~30-60s)
- **JSON → Content**: LLM generation (slow, ~60-120s per content type)
- **Markdown → HTML**: Fast (text processing)

### Optimization Strategies

1. **Caching**: Config and outline cached to avoid reloading
2. **Batch Processing**: Process multiple sessions together
3. **Parallel Processing**: Could parallelize module processing (future enhancement)

## Related Documentation

- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - JSON outline format and structure
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and data flow overview
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Pipeline execution and data flow
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration file structure
- **[FORMATS.md](FORMATS.md)** - Content format specifications

## Summary

Data flows through the system in a structured, predictable manner:

1. **Configuration** (YAML) provides initial parameters
2. **Outline Generation** (Stage 03) creates structured JSON outline
3. **Primary Generation** (Stage 04) creates session-based content
4. **Secondary Generation** (Stage 05) generates session-level secondary materials
5. **Website Generation** (Stage 06) combines everything into single HTML

Each stage:
- Transforms data structures
- Adds new information
- Preserves original structure
- Validates data integrity
- Caches for performance

The data flow is designed to be:
- **Traceable**: Each transformation is logged
- **Validated**: Multiple validation points ensure data integrity
- **Cached**: Config and outline cached for performance
- **Flexible**: Supports custom workflows and extensions






