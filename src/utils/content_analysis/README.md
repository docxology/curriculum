# Content Analysis Submodule

Comprehensive content quality assessment, validation, and consistency checking utilities for educational course materials.

## Purpose

This submodule provides tools for:
- **Content Quality Assessment**: Analyze lectures, labs, questions, study notes, and secondary materials
- **Validation**: Check content against requirements and quality criteria
- **Consistency Checking**: Validate cross-session coherence and concept progression
- **Format Validation**: Validate and clean Mermaid diagrams
- **Auto-Correction**: Fix common question format issues
- **Metrics Logging**: Structured logging with compliance status indicators

## Module Structure

```
content_analysis/
├── analyzers.py      # Content analysis functions for all content types
├── counters.py       # Counting functions (words, sections, examples, etc.)
├── consistency.py    # Cross-session consistency validation
├── mermaid.py        # Mermaid diagram validation and cleaning
├── logging.py        # Metrics logging utilities
└── question_fixes.py # Auto-correction for question format issues
```

## Quick Start

```python
from src.utils.content_analysis import (
    analyze_lecture,
    log_content_metrics,
    validate_mermaid_syntax,
)
import logging

logger = logging.getLogger(__name__)

# Analyze lecture content
lecture_text = "# Introduction\n\nContent here..."
metrics = analyze_lecture(
    lecture_text,
    requirements={
        'min_word_count': 2000,
        'max_word_count': 4000,
        'min_examples': 5,
        'min_sections': 4
    }
)

# Log results with compliance status
log_content_metrics("lecture", metrics, logger)

# Check compliance
if metrics['warnings']:
    print("Content needs review")
else:
    print("Content is compliant")
```

## Modules

### analyzers.py

Comprehensive analysis functions for all content types with validation criteria.

#### Primary Material Analyzers

**analyze_lecture(lecture_text, requirements=None)**
- Analyzes word count, structure, examples, definitions, cross-references
- Validates against min/max requirements
- Returns metrics with warnings for non-compliance

**analyze_lab(lab_text)**
- Analyzes procedure steps, safety warnings, materials, tables
- Validates lab structure and completeness

**analyze_questions(questions_text)**
- Analyzes question format, completeness, structure
- Validates question marks, MC options, answers, explanations
- Detects format issues and missing elements

**analyze_study_notes(notes_text, requirements=None)**
- Analyzes key concepts, structure, word count
- Validates against requirements

#### Secondary Material Analyzers

**analyze_application(application_text, requirements=None)**
- Analyzes real-world applications and case studies
- Validates application count and word distribution

**analyze_extension(extension_text, requirements=None)**
- Analyzes advanced topics beyond core curriculum
- Validates topic count and word distribution

**analyze_visualization(visualization_text, requirements=None)**
- Analyzes Mermaid diagrams (includes syntax validation)
- Validates diagram elements, nodes, connections

**analyze_integration(integration_text, requirements=None)**
- Analyzes cross-module connections and synthesis
- Validates connection count and structure

**analyze_investigation(investigation_text, requirements=None)**
- Analyzes research questions and experiments
- Validates question count and structure

**analyze_open_questions(open_questions_text, requirements=None)**
- Analyzes current scientific debates and frontiers
- Validates question count and structure

#### Quality Assessment Functions

**validate_prompt_quality(prompt_text)**
- Validates prompt structure and completeness

**calculate_quality_score(metrics_dict)**
- Calculates overall quality score from metrics

**aggregate_validation_results(results_list)**
- Aggregates results from multiple analyses

### counters.py

Basic counting utilities for text elements.

**Functions**:
- `count_words(text)` - Count words in text
- `count_sections(text)` - Count major sections (## headings)
- `count_subsections(text)` - Count subsections (### headings)
- `count_examples(text)` - Count concrete examples
- `count_definitions(text)` - Count term definitions
- `count_cross_references(text)` - Count cross-references

**Usage**:
```python
from src.utils.content_analysis.counters import (
    count_words, count_sections, count_examples
)

text = "# Section 1\n## Subsection\nExample: This is an example."
word_count = count_words(text)
sections = count_sections(text)
examples = count_examples(text)
```

### consistency.py

Cross-session consistency checking and concept progression tracking.

**validate_cross_session_consistency(sessions)**
- Validates coherence across sessions
- Detects inconsistencies and concept gaps
- Returns analysis with recommendations

**track_concept_progression(sessions)**
- Tracks how concepts progress across sessions
- Maps concept introduction and progression
- Identifies concept gaps and jumps

**Usage**:
```python
from src.utils.content_analysis.consistency import (
    validate_cross_session_consistency,
    track_concept_progression,
)

sessions = [
    {'session_num': 1, 'content': 'Session 1 content...'},
    {'session_num': 2, 'content': 'Session 2 content...'},
]

consistency = validate_cross_session_consistency(sessions)
progression = track_concept_progression(sessions)
```

### mermaid.py

Mermaid diagram syntax validation and cleaning.

**clean_mermaid_diagram(diagram)**
- Comprehensive Mermaid diagram cleanup
- Removes markdown code fences (```mermaid ... ```)
- Removes `linkStyle` commands (not supported in all renderers)
- Removes `style` and `classDef` commands
- Removes explanatory text before and after diagram code
- Extracts only valid Mermaid diagram syntax
- Returns cleaned diagram code

**validate_mermaid_syntax(diagram, min_nodes=3, min_connections=2)**
- Validates Mermaid diagram syntax
- Uses `clean_mermaid_diagram()` for comprehensive cleanup
- Validates diagram structure
- Checks node and connection counts
- Returns cleaned diagram and warnings

**Usage**:
```python
from src.utils.content_analysis.mermaid import (
    clean_mermaid_diagram,
    validate_mermaid_syntax
)

# Comprehensive cleanup (removes code fences, linkStyle, explanatory text)
diagram_with_artifacts = """```mermaid
graph TD
    A --> B
    linkStyle 0 stroke:#f9f
```

**Explanation:** This diagram shows a simple flow.
"""
cleaned = clean_mermaid_diagram(diagram_with_artifacts)
# Result: "graph TD\n    A --> B"

# Validation with cleanup
diagram = """
graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""
cleaned_diagram, warnings = validate_mermaid_syntax(diagram)
if warnings:
    for warning in warnings:
        print(f"Warning: {warning}")
```

**Cleanup Features**:
- **Code Fences**: Automatically removes ```mermaid and ``` markers
- **linkStyle Commands**: Removes linkStyle commands for compatibility
- **Style Commands**: Removes style and classDef commands
- **Explanatory Text**: Removes text before/after diagram that explains the diagram
- **Pure Syntax**: Output contains only valid Mermaid diagram code

### logging.py

Structured logging for content analysis metrics with compliance status.

**log_content_metrics(content_type, metrics, logger_obj=None)**
- Logs content analysis metrics with appropriate formatting
- Includes [COMPLIANT] or [NEEDS REVIEW] status indicators
- Provides detailed metrics (word count, sections, examples, etc.)
- Logs warnings if any
- Includes helpful tips for significant issues

**Supported Content Types**:
- `lecture` - Lecture analysis
- `lab` - Lab analysis
- `questions` - Question analysis
- `study_notes` - Study notes analysis
- `application` - Application analysis
- `extension` - Extension analysis
- `diagram` / `visualization` - Diagram analysis
- `integration` - Integration analysis
- `investigation` - Investigation analysis
- `open_questions` - Open questions analysis

**Usage**:
```python
from src.utils.content_analysis.logging import log_content_metrics
import logging

logger = logging.getLogger(__name__)
metrics = analyze_lecture(lecture_text)
log_content_metrics("lecture", metrics, logger)
```

### question_fixes.py

Auto-correction functions for common question format issues.

**Functions**:
- `fix_missing_question_marks(questions_text)` - Add missing question marks
- `fix_mc_options(questions_text)` - Fix MC question option formatting
- `fix_question_format(questions_text)` - Comprehensive format fix

**Auto-Fixes**:
- Adds missing question marks
- Ensures MC questions have 4 options (A, B, C, D)
- Standardizes question format
- Fixes option formatting

**Usage**:
```python
from src.utils.content_analysis.question_fixes import (
    fix_missing_question_marks,
    fix_mc_options,
    fix_question_format,
)

questions = "**Question 1:** What is DNA\nA) Option 1\nB) Option 2"

# Fix missing question marks
fixed_text, fix_count = fix_missing_question_marks(questions)

# Fix MC options
fixed_text, fix_count = fix_mc_options(fixed_text)

# Comprehensive fix
fixed_text, fixes = fix_question_format(questions)
```

## Compliance Status

All analysis functions return metrics with a `warnings` list. The presence of warnings indicates [NEEDS REVIEW] status, while no warnings indicates [COMPLIANT] status.

**Compliance Indicators**:
- `[COMPLIANT]` ✓ - Content meets all requirements
- `[NEEDS REVIEW]` ⚠️ - Content has warnings that should be reviewed
- `[CRITICAL]` 🔴 - Content has critical issues requiring attention

## Integration

Used by:
- Content generators - Quality validation during generation
- Pipeline orchestrator - Batch validation and reporting
- Scripts - Content quality reporting

## Examples

### Complete Analysis Workflow

```python
from src.utils.content_analysis import (
    analyze_lecture,
    analyze_questions,
    log_content_metrics,
    validate_mermaid_syntax,
)
import logging

logger = logging.getLogger(__name__)

# Analyze lecture
lecture_metrics = analyze_lecture(
    lecture_text,
    requirements={
        'min_word_count': 2000,
        'max_word_count': 4000,
        'min_examples': 5,
        'min_sections': 4
    }
)
log_content_metrics("lecture", lecture_metrics, logger)

# Analyze questions
question_metrics = analyze_questions(questions_text)
log_content_metrics("questions", question_metrics, logger)

# Validate diagram
diagram = "graph TD\nA --> B"
cleaned, warnings = validate_mermaid_syntax(diagram)
if warnings:
    logger.warning(f"Diagram warnings: {warnings}")
```

### Batch Validation

```python
from src.utils.content_analysis import (
    analyze_lecture,
    aggregate_validation_results,
)

results = []
for lecture in lectures:
    metrics = analyze_lecture(lecture)
    results.append(metrics)

aggregated = aggregate_validation_results(results)
print(f"Total warnings: {len(aggregated['all_warnings'])}")
print(f"Compliance rate: {aggregated['compliance_rate']}%")
```

### Consistency Checking

```python
from src.utils.content_analysis.consistency import (
    validate_cross_session_consistency,
    track_concept_progression,
)

sessions = load_sessions_from_module(module_id)
consistency = validate_cross_session_consistency(sessions)
progression = track_concept_progression(sessions)

if consistency['inconsistencies']:
    logger.warning("Cross-session inconsistencies detected")
    for issue in consistency['inconsistencies']:
        logger.warning(f"  - {issue}")
```

## See Also

- **For AI Agents**: [../AGENTS.md](../AGENTS.md) - Complete API reference
- **Utils Module**: [../README.md](../README.md) - Parent module documentation
- **Formats Documentation**: [../../../docs/FORMATS.md](../../../docs/FORMATS.md) - Content format specifications
- **Validation Documentation**: [../../../docs/VALIDATION.md](../../../docs/VALIDATION.md) - Validation criteria details
- **API Reference**: [../../../docs/API.md](../../../docs/API.md) - Public API documentation
