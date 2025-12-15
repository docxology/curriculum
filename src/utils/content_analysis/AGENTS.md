# Content Analysis Module - For AI Agents

## Overview

Comprehensive content quality assessment, validation, and consistency checking utilities for educational course materials.

## Module Structure

```
content_analysis/
├── analyzers.py      # Content analysis functions for all content types
├── counters.py       # Counting functions (words, sections, examples, etc.)
├── consistency.py    # Cross-session consistency validation
├── mermaid.py        # Mermaid diagram validation and cleaning
├── logging.py        # Metrics logging utilities
└── question_fixes.py  # Auto-correction for question format issues
```

## Public API

### Import Pattern

```python
from src.utils.content_analysis import (
    # Counting functions
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
    # Analysis functions
    analyze_lecture,
    analyze_lab,
    analyze_questions,
    analyze_study_notes,
    analyze_application,
    analyze_extension,
    analyze_visualization,
    analyze_integration,
    analyze_investigation,
    analyze_open_questions,
    # Quality and validation
    validate_prompt_quality,
    calculate_quality_score,
    aggregate_validation_results,
    # Consistency validation
    validate_cross_session_consistency,
    track_concept_progression,
    # Mermaid validation
    validate_mermaid_syntax,
    # Logging
    log_content_metrics,
)
```

## Primary Material Analyzers

### analyze_lecture(lecture_text, requirements=None)

Analyzes lecture content for quality and compliance.

**Parameters**:
- `lecture_text` (str): Lecture content in markdown
- `requirements` (dict, optional): Validation requirements with keys:
  - `min_word_count`, `max_word_count`
  - `min_examples`, `max_examples`
  - `min_sections`, `max_sections`

**Returns**: Dictionary with metrics:
- `word_count`, `char_count`, `sections`, `subsections`
- `examples`, `terms`, `cross_refs`
- `warnings`: List of validation warnings

**Example**:
```python
metrics = analyze_lecture(
    lecture_text,
    requirements={
        'min_word_count': 1000,
        'max_word_count': 1500,
        'min_examples': 5,
        'min_sections': 4
    }
)
```

### analyze_lab(lab_text)

Analyzes laboratory exercise content.

**Returns**: Dictionary with metrics:
- `word_count`, `procedure_steps`, `safety_warnings`
- `materials_count`, `tables`, `warnings`

### analyze_questions(questions_text)

Analyzes question content for format and completeness.

**Returns**: Dictionary with metrics:
- `total_questions`, `mc_questions`, `sa_questions`, `essay_questions`
- `question_marks`, `answers`, `explanations`
- `warnings`: Format and completeness issues

### analyze_study_notes(notes_text, requirements=None)

Analyzes study notes content.

**Returns**: Dictionary with metrics:
- `word_count`, `key_concepts`, `sections`
- `warnings`: Validation warnings

## Secondary Material Analyzers

### analyze_application(application_text, requirements=None)

Analyzes real-world applications.

**Returns**: Dictionary with metrics:
- `applications`: Count of application sections
- `word_count`, `avg_words_per_application`
- `warnings`: Validation warnings

### analyze_extension(extension_text, requirements=None)

Analyzes advanced extension topics.

**Returns**: Dictionary with metrics:
- `topics`: Count of extension topics
- `word_count`, `avg_words_per_topic`
- `warnings`: Validation warnings

### analyze_visualization(visualization_text, requirements=None)

Analyzes Mermaid diagrams (includes syntax validation).

**Returns**: Dictionary with metrics:
- `elements`, `nodes`, `connections`
- `warnings`: Syntax and structure issues

### analyze_integration(integration_text, requirements=None)

Analyzes cross-module connections.

**Returns**: Dictionary with metrics:
- `connections`: Count of integration connections
- `word_count`, `warnings`

### analyze_investigation(investigation_text, requirements=None)

Analyzes research questions and experiments.

**Returns**: Dictionary with metrics:
- `questions`: Count of investigation questions
- `word_count`, `warnings`

### analyze_open_questions(open_questions_text, requirements=None)

Analyzes current scientific debates.

**Returns**: Dictionary with metrics:
- `questions`: Count of open questions
- `word_count`, `warnings`

## Quality Assessment Functions

### validate_prompt_quality(prompt_text)

Validates prompt structure and completeness.

**Returns**: Dictionary with:
- `quality_score`: 0-100 score
- `issues`: List of quality issues
- `suggestions`: Improvement suggestions

### calculate_quality_score(metrics_dict, requirements, content_type)

Calculates overall quality score from metrics.

**Returns**: Dictionary with:
- `overall_score`: 0-100 score
- `quality_level`: "excellent", "good", "fair", "poor"
- `breakdown`: Score breakdown by category

### aggregate_validation_results(results_list)

Aggregates results from multiple analyses.

**Returns**: Dictionary with aggregated metrics and warnings.

## Consistency Validation

### validate_cross_session_consistency(sessions_data)

Validates consistency across multiple sessions.

**Returns**: Dictionary with:
- `inconsistencies`: List of inconsistencies found
- `concept_gaps`: Missing concept connections
- `recommendations`: Improvement suggestions

### track_concept_progression(sessions_data)

Tracks concept introduction and progression.

**Returns**: Dictionary with:
- `concepts_introduced`: Concepts per session
- `progression_map`: Concept progression tracking

## Mermaid Validation

### validate_mermaid_syntax(diagram_text)

Validates Mermaid diagram syntax.

**Returns**: Dictionary with:
- `valid`: Boolean indicating validity
- `errors`: List of syntax errors
- `warnings`: Syntax warnings
- `cleaned_diagram`: Cleaned version if issues found

## Logging Utilities

### log_content_metrics(content_type, metrics, logger)

Logs content metrics with compliance status.

**Parameters**:
- `content_type` (str): Type of content ("lecture", "lab", etc.)
- `metrics` (dict): Metrics dictionary from analyzer
- `logger` (logging.Logger): Logger instance

**Output**: Logs metrics with [COMPLIANT] or [NEEDS REVIEW] status.

## Counting Functions

### count_words(text) -> int

Counts words in text.

### count_sections(text) -> int

Counts markdown sections (## headings).

### count_subsections(text) -> int

Counts markdown subsections (### headings).

### count_examples(text) -> int

Counts example phrases ("for example", "for instance", etc.).

### count_definitions(text) -> int

Counts term definitions (phrases like "is defined as", "refers to").

### count_cross_references(text) -> int

Counts cross-references to other modules/sessions.

## Question Format Auto-Correction

### auto_fix_questions(questions_text)

Automatically fixes common question format issues.

**Returns**: Tuple of (fixed_text, fix_summary):
- `fixed_text`: Corrected questions text
- `fix_summary`: Dictionary with fix counts and details

## Usage Patterns

### Pattern 1: Analyze and Log

```python
from src.utils.content_analysis import analyze_lecture, log_content_metrics
import logging

logger = logging.getLogger(__name__)

metrics = analyze_lecture(lecture_text, requirements=reqs)
log_content_metrics("lecture", metrics, logger)

if metrics['warnings']:
    logger.warning("Content needs review")
else:
    logger.info("Content is compliant")
```

### Pattern 2: Quality Score

```python
from src.utils.content_analysis import analyze_lecture, calculate_quality_score

metrics = analyze_lecture(lecture_text, requirements=reqs)
quality = calculate_quality_score(metrics, reqs, "lecture")

logger.info(f"Quality score: {quality['overall_score']}/100 ({quality['quality_level']})")
```

### Pattern 3: Mermaid Validation

```python
from src.utils.content_analysis import validate_mermaid_syntax

result = validate_mermaid_syntax(diagram_text)
if not result['valid']:
    logger.warning(f"Mermaid syntax errors: {result['errors']}")
    diagram_text = result['cleaned_diagram']
```

## Related Documentation

- **[README.md](README.md)** - Complete module documentation
- **[../AGENTS.md](../AGENTS.md)** - Utils module overview
- **[../../docs/VALIDATION.md](../../docs/VALIDATION.md)** - Validation rules and criteria
- **[../../docs/FORMATS.md](../../docs/FORMATS.md)** - Content format specifications



