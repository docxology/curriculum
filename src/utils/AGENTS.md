# Utility Functions Module

Helper functions for file I/O, text processing, and system operations.

## Module Purpose

Provides commonly-used utility functions for file operations, text manipulation, formatting, and system checks. Used throughout the codebase for cross-platform file handling, text sanitization, and environment validation.

## File Operations

```python
from src.utils.helpers import (
    ensure_directory, save_markdown, load_markdown
)
```

### ensure_directory

```python
def ensure_directory(path: Union[str, Path]) -> Path
```

Create directory if it doesn't exist (including parents).

**Usage**:
```python
from pathlib import Path
from src.utils.helpers import ensure_directory

# Create output directory (session-based structure)
output_dir = ensure_directory("output/modules/module_01_cell_biology/session_01")
# Creates output/, output/modules/, output/modules/module_01_cell_biology/, and session_01/ if they don't exist

# Works with Path objects
session_dir = Path("output/modules/module_01_cell_biology/session_01")
ensure_directory(session_dir)

# Returns Path object
path = ensure_directory("output/new_folder")
print(path.resolve())  # Absolute path
```

### save_markdown

```python
def save_markdown(filepath: Union[str, Path], content: str) -> None
```

Save markdown content to file (creates parent directories).

**Usage**:
```python
from src.utils.helpers import save_markdown

content = "# My Lecture\n\nContent here..."

# Save to file (session-based structure)
save_markdown("output/modules/module_01_cell_biology/session_01/lecture.md", content)

# Parent directory created automatically if needed
save_markdown("output/new/nested/file.md", content)
```

### load_markdown

```python
def load_markdown(filepath: Union[str, Path]) -> str
```

Load markdown content from file.

**Usage**:
```python
from src.utils.helpers import load_markdown

# Load file (session-based structure)
content = load_markdown("output/modules/module_01_cell_biology/session_01/lecture.md")
print(len(content))

# Raises FileNotFoundError if file doesn't exist
try:
    content = load_markdown("missing.md")
except FileNotFoundError:
    print("File not found")
```

## Text Processing

```python
from src.utils.helpers import (
    slugify, sanitize_filename, truncate_text, count_words
)
```

### slugify

```python
def slugify(text: str) -> str
```

Convert text to URL-friendly slug (lowercase, underscores, no special chars).

**Usage**:
```python
from src.utils.helpers import slugify

# Basic slugification
slug = slugify("Cell Biology")
# Returns: "cell_biology"

slug = slugify("DNA & RNA: Structure")
# Returns: "dna_rna_structure"

slug = slugify("  Multiple   Spaces  ")
# Returns: "multiple_spaces"

# Use for filenames
module_name = "Introduction to Biology"
filename = f"module_01_{slugify(module_name)}.md"
# Returns: "module_01_introduction_to_biology.md"
```

### sanitize_filename

```python
def sanitize_filename(filename: str) -> str
```

Remove invalid filename characters.

**Usage**:
```python
from src.utils.helpers import sanitize_filename

# Remove invalid chars
safe = sanitize_filename("file<name>:test.txt")
# Returns: "file_name_test.txt"

# Replace spaces
safe = sanitize_filename("my file name.md")
# Returns: "my_file_name.md"

# Handle multiple underscores
safe = sanitize_filename("file___name.md")
# Returns: "file_name.md"
```

### truncate_text

```python
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str
```

Truncate text to maximum length with suffix.

**Usage**:
```python
from src.utils.helpers import truncate_text

text = "This is a very long piece of text"

# Truncate with default suffix
short = truncate_text(text, 20)
# Returns: "This is a very lo..."

# Custom suffix
short = truncate_text(text, 20, suffix=" [more]")
# Returns: "This is a [more]"

# No truncation if under limit
short = truncate_text("Short", 100)
# Returns: "Short"
```

### count_words

```python
def count_words(text: str) -> int
```

Count words in text.

**Usage**:
```python
from src.utils.helpers import count_words

text = "This is a test sentence."
count = count_words(text)
# Returns: 5

# Handles multiple spaces
count = count_words("Word1   Word2    Word3")
# Returns: 3
```

## Formatting

```python
from src.utils.helpers import (
    format_timestamp, format_module_filename
)
```

### format_timestamp

```python
def format_timestamp(dt: datetime = None) -> str
```

Format datetime as timestamp string (YYYYMMDD_HHMMSS).

**Usage**:
```python
from datetime import datetime
from src.utils.helpers import format_timestamp

# Current timestamp
ts = format_timestamp()
# Returns: "20241208_143022"

# Specific datetime
dt = datetime(2024, 12, 8, 14, 30, 22)
ts = format_timestamp(dt)
# Returns: "20241208_143022"

# Use in filenames
filename = f"outline_{format_timestamp()}.md"
# Returns: "outline_20241208_143022.md"
```

### format_module_filename

```python
def format_module_filename(
    module_id: int, 
    module_name: str, 
    suffix: str = ""
) -> str
```

Format standardized module filename.

**Usage**:
```python
from src.utils.helpers import format_module_filename

# Basic module filename
filename = format_module_filename(1, "Cell Biology")
# Returns: "module_01_cell_biology.md"

# With suffix
filename = format_module_filename(1, "Cell Biology", "_lecture")
# Returns: "module_01_cell_biology_lecture.md"

filename = format_module_filename(12, "Genetics & Evolution", "_lab1")
# Returns: "module_12_genetics_evolution_lab1.md"
```

## System Utilities

```python
from src.utils.helpers import (
    run_cmd_capture, ollama_is_running, 
    ensure_model_available, ensure_uv_available
)
```

### ollama_is_running

```python
def ollama_is_running(api_url: str = "http://localhost:11434/api/version") -> bool
```

Check if Ollama service is reachable.

**Usage**:
```python
from src.utils.helpers import ollama_is_running

# Check default endpoint
if ollama_is_running():
    print("Ollama is running")
else:
    print("Start Ollama with: ollama serve")

# Custom endpoint
if ollama_is_running("http://localhost:8080/api/version"):
    print("Custom Ollama running")
```

### ensure_model_available

```python
def ensure_model_available(model_name: str) -> bool
```

Check if specific Ollama model is available.

**Usage**:
```python
from src.utils.helpers import ensure_model_available

# Check model availability
if ensure_model_available("gemma3:4b"):
    print("Model available")
else:
    print("Pull model with: ollama pull gemma3:4b")

# Check multiple models
models = ["gemma3:4b", "llama3", "mistral"]
available = [m for m in models if ensure_model_available(m)]
print(f"Available models: {available}")
```

### ensure_uv_available

```python
def ensure_uv_available() -> bool
```

Check if uv package manager is installed.

**Usage**:
```python
from src.utils.helpers import ensure_uv_available

if not ensure_uv_available():
    print("Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
    exit(1)

print("uv is available")
```

### run_cmd_capture

```python
def run_cmd_capture(
    cmd: Sequence[str], 
    cwd: Optional[Path] = None
) -> subprocess.CompletedProcess
```

Run command and capture output.

**Usage**:
```python
from src.utils.helpers import run_cmd_capture

# Run command
result = run_cmd_capture(["ollama", "list"])

if result.returncode == 0:
    print("Output:", result.stdout)
else:
    print("Error:", result.stderr)

# With working directory
result = run_cmd_capture(["ls", "-la"], cwd=Path("/tmp"))

# Check git status
result = run_cmd_capture(["git", "status", "--short"])
if "M " in result.stdout:
    print("Modified files detected")
```

## Common Patterns

### Safe File Writing

```python
from src.utils.helpers import ensure_directory, save_markdown

def safe_save(content, filepath):
    """Save content with directory creation."""
    ensure_directory(Path(filepath).parent)
    save_markdown(filepath, content)

safe_save("# Content", "output/nested/deep/file.md")
```

### Generate Unique Filename

```python
from src.utils.helpers import format_module_filename, format_timestamp

def unique_filename(module_id, module_name, content_type):
    """Generate unique timestamped filename."""
    ts = format_timestamp()
    base = format_module_filename(module_id, module_name, f"_{content_type}")
    return base.replace(".md", f"_{ts}.md")

filename = unique_filename(1, "Cell Biology", "lecture")
# Returns: "module_01_cell_biology_lecture_20241208_143022.md"
```

### Validate Environment

```python
from src.utils.helpers import (
    ensure_uv_available, ollama_is_running, ensure_model_available
)

def validate_environment(model="gemma3:4b"):
    """Validate complete environment."""
    checks = []
    
    if not ensure_uv_available():
        checks.append("uv not installed")
    
    if not ollama_is_running():
        checks.append("Ollama not running")
    elif not ensure_model_available(model):
        checks.append(f"Model {model} not available")
    
    if checks:
        print("Environment issues:")
        for issue in checks:
            print(f"  - {issue}")
        return False
    
    print("Environment ready")
    return True

validate_environment()
```

## Testing

Tests in `tests/test_utils.py`:
- File operations (ensure_directory, save_markdown, load_markdown)
- Text processing (slugify, sanitize_filename, count_words)
- Formatting (format_timestamp, format_module_filename)
- System utilities (ollama_is_running, ensure_model_available)

Run tests:
```bash
uv run pytest tests/test_utils.py -v
```

## Complete Function Signature Reference

### File Operations

```python
def ensure_directory(path: Union[str, Path]) -> Path
def save_markdown(filepath: Union[str, Path], content: str) -> None
def load_markdown(filepath: Union[str, Path]) -> str
```

### Text Processing

```python
def slugify(text: str) -> str
def sanitize_filename(filename: str) -> str
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str
def count_words(text: str) -> int
```

### Formatting

```python
def format_timestamp(dt: Optional[datetime] = None) -> str
def format_module_filename(
    module_id: int, 
    module_name: str, 
    suffix: str = ""
) -> str
```

### System Utilities

```python
def ollama_is_running(api_url: str = "http://localhost:11434/api/version") -> bool
def ensure_model_available(model_name: str) -> bool
def ensure_uv_available() -> bool
def run_cmd_capture(
    cmd: Sequence[str], 
    cwd: Optional[Path] = None
) -> subprocess.CompletedProcess
```

## Error Collection and Reporting

### ErrorCollector

Centralized error and warning collection system for tracking validation issues during content generation.

```python
from src.utils.error_collector import ErrorCollector

# Initialize collector
collector = ErrorCollector()

# Add errors/warnings
collector.add_error(
    type="validation",
    message="Missing question marks",
    severity="CRITICAL",
    context="Module 1 Session 2",
    content_type="questions",
    module_id=1,
    session_num=2
)

collector.add_warning(
    type="validation",
    message="Word count below minimum",
    context="Module 1 Session 1",
    content_type="lecture"
)

# Query issues
critical_issues = collector.get_critical_issues()
warnings = collector.get_warnings()
all_issues = collector.get_all_issues()

# Filter by criteria
questions_issues = collector.get_by_content_type("questions")
validation_issues = collector.get_by_type("validation")
module1_issues = collector.get_by_context("Module 1 Session 1")

# Get summary statistics
summary = collector.get_summary()
# Returns: {
#     'total_errors': 1,
#     'total_warnings': 1,
#     'total_info': 0,
#     'total_issues': 2,
#     'by_content_type': {'questions': 1, 'lecture': 1},
#     'by_error_type': {'validation': 2},
#     'by_severity': {'CRITICAL': 1, 'WARNING': 1, 'INFO': 0}
# }

# Export to dictionary
data = collector.to_dict()

# Clear all issues
collector.clear()
```

**Key Methods**:
- `add_error()` - Add error with full context
- `add_warning()` - Convenience method for warnings
- `get_critical_issues()` - Get all CRITICAL errors
- `get_warnings()` - Get all WARNING-level issues
- `get_all_issues()` - Get all issues sorted by severity
- `get_by_content_type()` - Filter by content type
- `get_by_type()` - Filter by error type
- `get_by_context()` - Filter by context string
- `get_summary()` - Get summary statistics
- `to_dict()` - Export to dictionary format
- `clear()` - Clear all collected issues

### Summary Generator

Utilities for generating formatted summaries of validation issues and generation statistics.

```python
from src.utils.summary_generator import (
    generate_stage_summary,
    generate_validation_summary,
    generate_generation_summary,
    categorize_errors_by_type,
    format_error_list
)

# Generate stage-level summary
generate_stage_summary(
    collector,
    "Primary Materials Generation",
    logger,
    total_items=10,
    successful_items=8,
    failed_items=2
)

# Generate validation summary
generate_validation_summary(collector, logger)

# Generate overall generation summary
results = {'sessions_generated': 10, 'modules_processed': 5}
generate_generation_summary(results, collector, logger)

# Categorize errors by type
errors = collector.get_all_issues()
categorized = categorize_errors_by_type(errors)
# Returns: {'validation': [ErrorEntry, ...], 'generation': [ErrorEntry, ...]}

# Format error list for display
formatted = format_error_list(errors, max_items=10, show_context=True)
# Returns: List of formatted error strings
```

**Key Functions**:
- `generate_stage_summary()` - Stage-level summary with compliance breakdown
- `generate_validation_summary()` - Summary of all validation issues
- `generate_generation_summary()` - Overall generation statistics
- `categorize_errors_by_type()` - Group errors by error type
- `format_error_list()` - Format errors for display

### Enhanced Logging with Text Labels

Accessibility-focused logging functions that include text labels alongside emojis.

```python
from src.utils.logging_setup import log_status_with_text, log_error_summary

# Log with text label and emoji
log_status_with_text(
    logger,
    "COMPLIANT",
    "Lecture generated",
    emoji="✓",
    level="INFO"
)
# Output: [COMPLIANT] Lecture generated ✓

log_status_with_text(
    logger,
    "CRITICAL",
    "Missing question marks",
    emoji="🔴",
    level="WARNING"
)
# Output: [CRITICAL] Missing question marks 🔴

# Log error summary
errors = collector.get_critical_issues()
log_error_summary(logger, "Critical Issues", errors, max_items=10)
```

**Key Functions**:
- `log_status_with_text()` - Log with text label + optional emoji
- `log_error_summary()` - Structured error summary display

## Content Analysis Submodule

The `content_analysis` submodule provides comprehensive content quality assessment, validation, and consistency checking utilities.

### Module Structure

```
content_analysis/
├── analyzers.py      # Content analysis functions for all content types
├── counters.py       # Counting functions (words, sections, examples, etc.)
├── consistency.py    # Cross-session consistency validation
├── mermaid.py        # Mermaid diagram validation and cleaning
├── logging.py        # Metrics logging utilities
└── question_fixes.py # Auto-correction for question format issues
```

### Importing Content Analysis Functions

```python
# Import from submodule directly
from src.utils.content_analysis.analyzers import (
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
    validate_prompt_quality,
    calculate_quality_score,
    aggregate_validation_results,
)

from src.utils.content_analysis.counters import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
)

from src.utils.content_analysis.consistency import (
    validate_cross_session_consistency,
    track_concept_progression,
)

from src.utils.content_analysis.mermaid import (
    validate_mermaid_syntax,
)

from src.utils.content_analysis.logging import (
    log_content_metrics,
)

# Or import from package __init__
from src.utils.content_analysis import (
    analyze_lecture,
    analyze_questions,
    count_words,
    validate_mermaid_syntax,
    log_content_metrics,
)
```

### Content Analyzers (`analyzers.py`)

Comprehensive analysis functions for all content types with validation criteria.

#### analyze_lecture

```python
def analyze_lecture(
    lecture_text: str, 
    requirements: Dict[str, int] = None
) -> Dict[str, Any]
```

Analyze lecture content for word count, structure, examples, and compliance.

**Usage**:
```python
from src.utils.content_analysis.analyzers import analyze_lecture

lecture = "# Introduction\n\nContent here..."
metrics = analyze_lecture(lecture)

# With custom requirements
metrics = analyze_lecture(
    lecture,
    requirements={
        'min_word_count': 2000,
        'max_word_count': 4000,
        'min_examples': 5,
        'max_examples': 15,
        'min_sections': 4,
        'max_sections': 8
    }
)

# Check results
print(f"Word count: {metrics['word_count']}")
print(f"Sections: {metrics['sections']}")
print(f"Examples: {metrics['examples']}")
if metrics['warnings']:
    for warning in metrics['warnings']:
        print(f"Warning: {warning}")
```

**Returns**: Dictionary with `word_count`, `char_count`, `sections`, `subsections`, `examples`, `terms`, `cross_refs`, `warnings`, `requirements`

#### analyze_lab

```python
def analyze_lab(lab_text: str) -> Dict[str, Any]
```

Analyze lab content for procedure steps, safety warnings, materials, and tables.

**Usage**:
```python
from src.utils.content_analysis.analyzers import analyze_lab

lab = "# Lab Title\n## Materials\n- Item 1\n## Procedure\n1. Step 1"
metrics = analyze_lab(lab)

print(f"Procedure steps: {metrics['procedure_steps']}")
print(f"Safety warnings: {metrics['safety_warnings']}")
print(f"Materials: {metrics['materials']}")
```

#### analyze_questions

```python
def analyze_questions(questions_text: str) -> Dict[str, Any]
```

Analyze question content for format, completeness, and structure.

**Usage**:
```python
from src.utils.content_analysis.analyzers import analyze_questions

questions = "**Question 1:** What is...?\nA) Option 1\nB) Option 2"
metrics = analyze_questions(questions)

print(f"Total questions: {metrics['total_questions']}")
print(f"MC questions: {metrics['mc_questions']}")
print(f"Question marks: {metrics['question_marks']}")
if metrics['warnings']:
    for warning in metrics['warnings']:
        print(f"Warning: {warning}")
```

**Returns**: Dictionary with `total_questions`, `mc_questions`, `question_marks`, `answers_provided`, `explanations_provided`, `warnings`

#### analyze_study_notes

```python
def analyze_study_notes(notes_text: str, requirements: Dict[str, int] = None) -> Dict[str, Any]
```

Analyze study notes for key concepts, structure, and compliance.

**Usage**:
```python
from src.utils.content_analysis.analyzers import analyze_study_notes

notes = "# Key Concepts\n- Concept 1\n- Concept 2"
metrics = analyze_study_notes(notes)

print(f"Key concepts: {metrics['key_concepts']}")
print(f"Word count: {metrics['word_count']}")
```

#### Secondary Material Analyzers

Functions for analyzing secondary materials (application, extension, visualization, integration, investigation, open_questions):

```python
from src.utils.content_analysis.analyzers import (
    analyze_application,
    analyze_extension,
    analyze_visualization,
    analyze_integration,
    analyze_investigation,
    analyze_open_questions,
)

# All follow similar pattern
metrics = analyze_application(application_text)
metrics = analyze_extension(extension_text)
metrics = analyze_visualization(visualization_text)  # Includes Mermaid validation
metrics = analyze_integration(integration_text)
metrics = analyze_investigation(investigation_text)
metrics = analyze_open_questions(open_questions_text)
```

#### Quality Assessment Functions

```python
from src.utils.content_analysis.analyzers import (
    validate_prompt_quality,
    calculate_quality_score,
    aggregate_validation_results,
)

# Validate prompt quality
quality = validate_prompt_quality(prompt_text)

# Calculate overall quality score
score = calculate_quality_score(metrics_dict)

# Aggregate results from multiple analyses
aggregated = aggregate_validation_results([metrics1, metrics2, metrics3])
```

### Counting Functions (`counters.py`)

Basic counting utilities for text elements.

```python
from src.utils.content_analysis.counters import (
    count_words,
    count_sections,
    count_subsections,
    count_examples,
    count_definitions,
    count_cross_references,
)

text = "# Section 1\n## Subsection\nExample: This is an example."

word_count = count_words(text)           # Count words
sections = count_sections(text)          # Count ## headings
subsections = count_subsections(text)    # Count ### headings
examples = count_examples(text)          # Count concrete examples
definitions = count_definitions(text)    # Count term definitions
cross_refs = count_cross_references(text) # Count cross-references
```

### Consistency Validation (`consistency.py`)

Cross-session consistency checking and concept progression tracking.

```python
from src.utils.content_analysis.consistency import (
    validate_cross_session_consistency,
    track_concept_progression,
)

# Validate consistency across sessions
sessions = [
    {'session_num': 1, 'content': 'Session 1 content...'},
    {'session_num': 2, 'content': 'Session 2 content...'},
]

consistency_results = validate_cross_session_consistency(sessions)
print(f"Inconsistencies: {consistency_results['inconsistencies']}")
print(f"Concept gaps: {consistency_results['concept_gaps']}")

# Track concept progression
progression = track_concept_progression(sessions)
print(f"Concepts introduced: {progression['concepts_introduced']}")
print(f"Concept progression: {progression['progression_map']}")
```

### Mermaid Validation (`mermaid.py`)

Mermaid diagram syntax validation and cleaning.

```python
from src.utils.content_analysis.mermaid import validate_mermaid_syntax

diagram = """
graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""

cleaned_diagram, warnings = validate_mermaid_syntax(diagram)

if warnings:
    for warning in warnings:
        print(f"Warning: {warning}")

# Use cleaned diagram
print(cleaned_diagram)
```

**Features**:
- Removes markdown code fences
- Removes unsupported style commands
- Validates diagram structure
- Checks node and connection counts
- Returns cleaned diagram and warnings

### Metrics Logging (`logging.py`)

Structured logging for content analysis metrics with compliance status.

```python
from src.utils.content_analysis.logging import log_content_metrics
import logging

logger = logging.getLogger(__name__)

# Analyze content
metrics = analyze_lecture(lecture_text)

# Log metrics with compliance status
log_content_metrics("lecture", metrics, logger)

# Output includes:
# [COMPLIANT] or [NEEDS REVIEW] status
# Detailed metrics (word count, sections, examples, etc.)
# Warnings if any
# Helpful tips for significant issues
```

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

### Question Fixes (`question_fixes.py`)

Auto-correction functions for common question format issues.

```python
from src.utils.content_analysis.question_fixes import (
    fix_missing_question_marks,
    fix_mc_options,
    fix_question_format,
)

questions = "**Question 1:** What is DNA\nA) Option 1\nB) Option 2"

# Fix missing question marks
fixed_text, fix_count = fix_missing_question_marks(questions)
print(f"Fixed {fix_count} missing question marks")

# Fix MC options formatting
fixed_text, fix_count = fix_mc_options(fixed_text)
print(f"Fixed {fix_count} MC option issues")

# Comprehensive format fix
fixed_text, fixes = fix_question_format(questions)
print(f"Total fixes: {fixes['total']}")
```

**Auto-Fixes**:
- Adds missing question marks
- Ensures MC questions have 4 options (A, B, C, D)
- Standardizes question format
- Fixes option formatting

### Complete Usage Example

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
    print("Content needs review:")
    for warning in metrics['warnings']:
        print(f"  - {warning}")
else:
    print("Content is compliant")

# Validate diagram
diagram = "graph TD\nA --> B"
cleaned, warnings = validate_mermaid_syntax(diagram)
if warnings:
    print("Diagram warnings:", warnings)
```

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide with examples
- **Content Analysis**: [content_analysis/README.md](content_analysis/README.md) - Complete content analysis documentation
- **Configuration**: [../config/AGENTS.md](../config/AGENTS.md) - Uses helpers for file operations
- **Generators**: [../generate/formats/AGENTS.md](../generate/formats/AGENTS.md) - Use helpers for saving
- **Testing**: [../../tests/README.md](../../tests/README.md) - Test coverage details
- **Test File**: [../../tests/test_utils.py](../../tests/test_utils.py) - Utility function tests


