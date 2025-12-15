# Utility Functions

Helper functions for common operations.

## Files

- `helpers.py` - Utility functions for file I/O, text processing, and system checks
- `logging_setup.py` - Centralized logging configuration for scripts and modules
- `content_analysis/` - Content quality assessment and validation submodule

## Overview

This module provides commonly-used utility functions that support the entire codebase. Functions are organized into categories: file operations, text processing, formatting, and system utilities.

## Function Categories

### File Operations
- `ensure_directory(path)` - Create directory with parents
- `save_markdown(filepath, content)` - Save markdown file
- `load_markdown(filepath)` - Load markdown file

### Text Processing
- `slugify(text)` - Convert to URL-friendly slug
- `sanitize_filename(filename)` - Remove invalid filename chars
- `truncate_text(text, max_length, suffix)` - Truncate with suffix
- `count_words(text)` - Count words in text

### Formatting
- `format_timestamp(dt)` - Format datetime as YYYYMMDD_HHMMSS
- `format_module_filename(module_id, name, suffix)` - Standard module filename

### Logging Configuration
- `setup_logging(script_name, log_dir, log_level)` - Configure logging with console and file handlers
- `print_section_header(title, level)` - Print formatted section headers
- Visual separators for consistent script output

### System Utilities
- `ollama_is_running(api_url)` - Check Ollama service
- `ensure_model_available(model_name)` - Check Ollama model
- `ensure_uv_available()` - Check uv package manager
- `run_cmd_capture(cmd, cwd)` - Run command and capture output

### Content Analysis (`content_analysis/`)
Comprehensive content quality assessment and validation utilities.

**Submodules**:
- `analyzers.py` - Content analysis functions for all content types (lectures, labs, questions, study notes, secondary materials)
- `counters.py` - Counting functions (words, sections, examples, definitions, cross-references)
- `consistency.py` - Cross-session consistency validation and concept progression tracking
- `mermaid.py` - Mermaid diagram syntax validation and cleaning
- `logging.py` - Structured metrics logging with compliance status ([COMPLIANT]/[NEEDS REVIEW])
- `question_fixes.py` - Auto-correction for question format issues

**Key Functions**:
```python
from src.utils.content_analysis import (
    analyze_lecture, analyze_lab, analyze_questions,
    analyze_study_notes, analyze_application, analyze_extension,
    validate_mermaid_syntax, log_content_metrics,
    validate_cross_session_consistency, track_concept_progression,
)

# Analyze content
metrics = analyze_lecture(lecture_text, requirements={...})

# Log with compliance status
log_content_metrics("lecture", metrics, logger)

# Validate diagrams
cleaned, warnings = validate_mermaid_syntax(diagram_text)

# Check consistency
consistency = validate_cross_session_consistency(sessions)
```

See [content_analysis/README.md](content_analysis/README.md) for complete documentation.

## Usage

```python
from src.utils.helpers import (
    ensure_directory, save_markdown,
    slugify, format_module_filename,
    ollama_is_running
)

# File operations
# Session-based structure
session_dir = ensure_directory("output/modules/module_01_cell_biology/session_01")
save_markdown("output/modules/module_01_cell_biology/session_01/lecture.md", content)

# Text processing
slug = slugify("Cell Biology")  # Returns: "cell_biology"

# Formatting
filename = format_module_filename(1, "Cell Biology", "_lecture")
# Returns: "module_01_cell_biology_lecture.md"

# System checks
if ollama_is_running():
    print("Ollama ready")
```

## Integration

Used by:
- All content generators - File saving
- Configuration loader - File operations
- Pipeline orchestrator - Directory management
- Scripts - Environment validation

## Quick Reference

| Function | Purpose | Returns |
|----------|---------|---------|
| `ensure_directory` | Create directory | Path |
| `save_markdown` | Save markdown file | None |
| `load_markdown` | Load markdown file | str |
| `slugify` | Text to slug | str |
| `sanitize_filename` | Clean filename | str |
| `format_timestamp` | Timestamp string | str |
| `format_module_filename` | Module filename | str |
| `ollama_is_running` | Check Ollama | bool |
| `ensure_model_available` | Check model | bool |
| `run_cmd_capture` | Run command | CompletedProcess |

## Testing

Tests in `tests/test_utils.py`:
```bash
uv run pytest tests/test_utils.py -v
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - Complete API reference with examples
- **Content Analysis**: [content_analysis/README.md](content_analysis/README.md) - Content quality assessment documentation
- **Generators**: [../generate/formats/README.md](../generate/formats/README.md) - Main users
- **Scripts**: [../../scripts/README.md](../../scripts/README.md) - CLI usage


