# Logging Guide

Complete reference for logging patterns, levels, structured logging, and debugging in the educational course Generator.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Golden Rule** | NO print() statements. EVER. Use logging module for ALL output |
| **Logging Levels** | DEBUG (detailed), INFO (progress), WARNING (recoverable), ERROR (failures) |
| **Centralized Setup** | Use `setup_logging()` from `src.utils.logging_setup` |
| **Request Tracing** | All LLM requests have unique request IDs for traceability |
| **Operation Context** | Module/session context included in all log messages |
| **Log Files** | Timestamped files in `output/logs/` directory |

**Read time**: 20-30 minutes | **Audience**: Developers, contributors, system operators

## Core Principle

### NO print() STATEMENTS. EVER.

Use `logging` module for ALL operational output.

**Why logging over print()?**
- **Levels**: DEBUG, INFO, WARNING, ERROR (can filter)
- **File output**: Console + file simultaneously
- **Filtering**: Can filter by level/module
- **Structured**: Consistent format across all output

## Basic Setup

### Module-Level Logging

```python
import logging

logger = logging.getLogger(__name__)
```

### Script-Level Logging

```python
from src.utils.logging_setup import setup_logging

# Setup with file output (logs to output/logs/)
log_file = setup_logging(
    script_name="script_name",
    log_level="INFO", 
    console_output=True,
    file_output=True
)

logger = logging.getLogger(__name__)
logger.info(f"Log file: {log_file}")
```

## Logging Levels

### DEBUG - Detailed Diagnostic Info

Use for:
- Variable values
- Detailed execution flow
- LLM request/response details
- Stream progress updates
- Operation context

```python
logger.debug(f"Processing module: {module_id}")
logger.debug(f"Template requires {len(required_vars)} variables")
logger.debug(f"[{request_id}] 📊 Stream progress: 5.2s elapsed, 42 chunks")
```

**When to use**: Development, debugging, detailed diagnostics

### INFO - General Informational Messages

Use for:
- Major steps and milestones
- Progress updates
- Successful operations
- LLM request summaries
- Validation status

```python
logger.info("Starting outline generation...")
logger.info(f"Generated lecture: {len(lecture)} characters")
logger.info(f"[{request_id}] 🚀 lec | m=gemma3:4b | p=5000c")
logger.info("✓ Lecture generated: [COMPLIANT]")
```

**When to use**: Normal operation, progress tracking, status updates

### WARNING - Something Unexpected But Recoverable

Use for:
- Recoverable issues
- Skipped items
- Retry attempts
- Validation warnings
- Missing optional data

```python
logger.warning("Ollama not available - skipping integration tests")
logger.warning(f"Retrying ({attempt}/{max_attempts})...")
logger.warning("⚠️ Word count (899) below minimum 1000")
```

**When to use**: Issues that don't stop execution but should be noted

### ERROR - Serious Problems

Use for:
- Failures that affect functionality
- Exceptions (with `exc_info=True`)
- Critical validation failures
- Connection errors

```python
logger.error(f"Failed to generate content for module: {name}")
logger.error("LLM returned empty response", exc_info=True)
logger.error(f"✗ Error processing session {session_num}: {e}")
```

**When to use**: Failures that prevent normal operation

## Centralized Logging Setup

### Standard Script Setup

All scripts should use the centralized logging setup:

```python
from pathlib import Path
import sys
from src.utils.logging_setup import setup_logging

# Setup logging before any other imports that use logging
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.utils.logging_setup import setup_logging
import logging

# Setup logging
log_file = setup_logging(
    script_name="03_generate_outline",
    log_level="INFO",
    console_output=True,
    file_output=True
)

logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")
```

### Configuration-Based Setup

```python
from src.config.loader import ConfigLoader
from src.utils.logging_setup import setup_logging, get_logging_config

config_loader = ConfigLoader("config")
logging_config = get_logging_config(config_loader)

log_file = setup_logging(
    script_name="script_name",
    log_level=logging_config['level'],
    console_output=logging_config['console'],
    file_output=True
)
```

## Visual Formatting

### Section Headers

```python
from src.utils.logging_setup import (
    log_section_header,
    log_section_clean,
    SEPARATOR_LINE
)

# Major section (double line)
log_section_header(logger, "STAGE 1: Outline Generation", major=True)
# Output:
# ════════════════════════════════════════════════════════════════════════════
# STAGE 1: Outline Generation
# ════════════════════════════════════════════════════════════════════════════

# Clean section with emoji
log_section_clean(logger, "Configuration Validation", emoji="📋")
# Output:
# 
# 📋 Configuration Validation
# ────────────────────────────────────────────────────────────
```

### Information Boxes

```python
from src.utils.logging_setup import log_info_box, log_status_item

# Structured information box
log_info_box(
    logger,
    "Configuration",
    {
        "Config directory": "/path/to/config",
        "Project root": "/path/to/project",
        "Python executable": sys.executable
    },
    emoji="ℹ️"
)
# Output:
# 
# ℹ️ Configuration
# ────────────────────────────────────────────────────────────
#   • Config directory: /path/to/config
#   • Project root: /path/to/project
#   • Python executable: /usr/bin/python3
# ────────────────────────────────────────────────────────────

# Single status item
log_status_item(logger, "Ollama status", "Running", status="success")
# Output:
#   ✅ Ollama status: Running
```

### Parameter Logging

```python
from src.utils.logging_setup import log_parameters

params = {
    "course_name": "Introductory Biology",
    "num_modules": 5,
    "total_sessions": 15
}
log_parameters(logger, params, "Generation Parameters")
# Output:
# Generation Parameters (3 provided):
#   ✓ course_name  : "Introductory Biology"
#   ✓ num_modules  : 5
#   ✓ total_sessions : 15
```

### Validation Results

```python
from src.utils.logging_setup import log_validation_results

required = {'course_name', 'num_modules', 'total_sessions'}
provided = {'course_name', 'num_modules', 'total_sessions', 'extra_var'}
missing = set()
extra = {'extra_var'}

log_validation_results(logger, required, provided, missing, extra)
# Output:
# Template Validation:
#   ✓ All 3 required variables provided
#   ✓ No missing variables
#   ⚠️  Extra 1 variables provided (will be ignored):
#       - extra_var
```

## Request ID Tracing

### LLM Request Tracing

All LLM requests are assigned unique request IDs for traceability:

```python
# Request ID includes operation abbreviation (format: [op:uuid])
from src.llm.client import OPERATION_ABBREVIATIONS
import uuid

operation = "lecture"
abbrev = OPERATION_ABBREVIATIONS.get(operation, operation[:3])
request_id = f"{abbrev}:{uuid.uuid4().hex[:6]}"
# Example: "lec:56e7ab"

# Log request summary (compact format with emoji)
logger.info(f"[{request_id}] 🚀 {abbrev} | m={model} | p={prompt_len}c")

# All related log messages include request ID
logger.info(f"[{request_id}] 📊 5.2s: 1234c @237c/s (42ch, ~309t @46t/s)")
logger.info(f"[{request_id}] ✓ Done 12.5s: 2847c (~569w @228c/s)")
```

### Tracing Through Logs

Search for request ID to trace a single operation:

```bash
# Find all logs for a specific request (escape brackets for grep)
grep "\\[lec:56e7ab\\]" output/logs/*.log

# Find all LLM requests (search for emoji or operation abbreviations)
grep "🚀" output/logs/*.log
grep "\\[lec:" output/logs/*.log  # All lecture requests
```

## Operation Context

### Module/Session Context

Include operation context in log messages for better traceability:

```python
from src.utils.logging_setup import log_operation_context

# Log operation context
log_operation_context(logger, module="Cell Biology", session="1")
# Output: DEBUG: Operation context: Cell Biology (Session 1)

# Use in content generation
logger.info(f"Generating lecture for {module} (Session {session})...")
logger.info(f"✓ Lecture generated for {module} (Session {session})")
```

### LLM Request Summary

```python
from src.utils.logging_setup import log_llm_request_summary

log_llm_request_summary(
    logger, 
    request_id="lecture-abc123",
    operation="lecture",
    model="gemma3:4b",
    prompt_len=5000,
    level="INFO"
)
# Output: INFO: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=5000c
```

## Log File Organization

### File Location

- **Directory**: `output/logs/`
- **Format**: `{script_name}_{YYYYMMDD}_{HHMMSS}.log`
- **Example**: `04_generate_primary_20241209_091827.log`

### File Contents

Log files contain:
- Same output as console
- Timestamped entries
- All log levels (based on configured level)
- Complete request traces

### Log Retention

- **Automatic**: Not rotated automatically
- **Manual**: Clean up old logs as needed
- **Recommendation**: Keep logs for recent runs, archive or delete older logs

## Log Analysis and Debugging

### Finding Errors

```bash
# Find all errors
grep "ERROR" output/logs/*.log

# Find errors for specific module
grep "ERROR.*Module.*Cell Biology" output/logs/*.log

# Find validation warnings
grep "NEEDS REVIEW" output/logs/*.log
```

### Tracing Operations

```bash
# Find all logs for a specific request ID
grep "lecture-a1b2c3d4" output/logs/*.log

# Find all LLM requests
grep "LLM Request:" output/logs/*.log | head -20

# Find stream progress for long operations
grep "Stream progress" output/logs/*.log
```

### Performance Analysis

```bash
# Find slow operations (look for long durations)
grep "Generation complete.*in.*s" output/logs/*.log | grep -E "[0-9]{2,}\.[0-9]+s"

# Find timeout issues
grep "timeout\|Timeout" output/logs/*.log
```

### Module Processing Analysis

```bash
# Count successful vs failed sessions
grep "Session.*completed\|Error processing session" output/logs/*.log | \
  awk '{if ($0 ~ /completed/) success++; else failed++} END {print "Success:", success, "Failed:", failed}'

# Find modules with errors
grep "Error processing" output/logs/*.log | cut -d: -f2- | sort | uniq
```

## Logging Configuration

### Configuration File

Configure logging in `config/output_config.yaml`:

```yaml
output:
  logging:
    level: "INFO"              # DEBUG, INFO, WARNING, ERROR
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console: true              # Output to console
    file: "output/logs/generation.log"  # Log file path
    verbose_llm: false         # Set to true for DEBUG-level LLM logs
    show_progress: false        # Set to true for stream progress at INFO level
    # Logging interval configuration
    heartbeat_interval: 5      # Heartbeat logs for long requests (seconds, default: 5)
    progress_log_interval: 2  # Stream progress update frequency (seconds, default: 2)
```

### Configurable Logging Intervals

The system provides two types of periodic logging that can be configured:

**Heartbeat Logging** (`heartbeat_interval`):
- Logs "Request in progress" messages during long LLM operations
- Default: 5 seconds (changed from 15s)
- Purpose: Indicate that a request is still active during long-running operations
- Example message: `[lecture-abc123] Request in progress: 15.2s elapsed, 164.8s remaining (timeout: 180s)`
- Adjust if you want more or less frequent status updates during long operations

**Stream Progress Logging** (`progress_log_interval`):
- Logs detailed stream progress during LLM response streaming
- Default: 2 seconds
- Purpose: Show chunk rate, text generation speed, and token estimates
- Example message: `[lecture-abc123] Stream: 10.0s | Chunks: 348 (34.6/s) | Text: 1690 chars (~422 tokens, 42.1 tok/s) | Speed: 168.2 chars/s`
- Adjust to reduce log noise (increase interval) or get more frequent updates (decrease interval)

**Tuning Recommendations**:
- **Quiet logging**: Increase both intervals (e.g., `heartbeat_interval: 10`, `progress_log_interval: 5`)
- **Verbose logging**: Decrease intervals (e.g., `heartbeat_interval: 3`, `progress_log_interval: 1`)
- **Production**: Use defaults (5s heartbeat, 2s progress) for balanced visibility
- **Debugging**: Decrease intervals to see more frequent updates

**Example Configuration**:
```yaml
logging:
  heartbeat_interval: 10      # Less frequent heartbeat (every 10 seconds)
  progress_log_interval: 5     # Less frequent progress updates (every 5 seconds)
```

### Verbosity Control

**Normal Operation** (INFO level):
- Major steps and milestones
- LLM request summaries
- Validation status
- Progress updates

**Debug Mode** (DEBUG level):
- Detailed execution flow
- Variable values
- LLM request/response details
- Stream progress updates
- Operation context

**Enable Debug Logging**:
```bash
# Via script argument
uv run python3 scripts/04_generate_primary.py --log-level DEBUG

# Via environment variable
LOG_LEVEL=DEBUG uv run python3 scripts/04_generate_primary.py
```

## Recent Improvements

### Reduced Verbosity (Dec 2024)

- **Stream progress** updates moved to DEBUG level (was INFO)
- **LLM request details** consolidated into single INFO message
- **Detailed diagnostics** (attempts, response status) at DEBUG level
- **Result**: ~40-50% reduction in INFO-level log messages

### Operation Context (Dec 2024)

- **Request IDs** use compact format with operation abbreviations: `[lec:56e7ab]` instead of `[lecture-abc123]`
- **Content generators** include module/session context in all log messages
- **Better traceability** - easier to follow specific operations through logs
- **Token efficiency** - ~40-50% reduction in log message length

### Visual Improvements

- **Emoji-based logging** functions for cleaner output
- **Structured information boxes** for configuration and status
- **Aligned parameter logging** for readability
- **Clean separators** instead of ASCII art

## Best Practices

1. **NO print()** - Use logging always
2. **Use setup_logging()** - For all scripts (file output)
3. **Get logger** - `logging.getLogger(__name__)`
4. **Right level** - DEBUG/INFO/WARNING/ERROR
5. **Add context** - Module name, operation, request ID, details
6. **Include errors** - Use `exc_info=True` for exceptions
7. **Visual clarity** - Use log_section_header() for major sections
8. **Structured data** - Use log_parameters() for dicts
9. **Operation context** - Use log_operation_context() for traceability
10. **Request tracing** - Include request IDs in all LLM-related logs

## Common Patterns

### Pattern 1: Module Processing

```python
logger.info(f"Processing Module {module_id}/{total}: {module_name}")
try:
    result = process_module(module)
    logger.info(f"✓ Module {module_name} completed")
except Exception as e:
    logger.error(f"✗ Module {module_name} failed: {e}", exc_info=True)
```

### Pattern 2: LLM Request

```python
from src.llm.client import OllamaClient

# Request ID is automatically formatted by OllamaClient
try:
    result = llm_client.generate(prompt, operation="lecture")
    # Logs: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=5000c
    #       [lec:56e7ab] ✓ Done 12.5s: 2847c (~569w @228c/s)
except Exception as e:
    logger.error(f"Generation failed: {e}", exc_info=True)
```

### Pattern 3: Validation Status

```python
metrics = analyze_content(content, requirements)
if metrics.get('warnings'):
    logger.warning(f"⚠️ Content generated: [NEEDS REVIEW]")
    for warning in metrics['warnings']:
        logger.warning(f"  ⚠️  {warning}")
else:
    logger.info(f"✓ Content generated: [COMPLIANT]")
```

### Pattern 4: Progress Reporting

```python
total = len(items)
for i, item in enumerate(items, 1):
    logger.info(f"[{i}/{total}] Processing: {item['name']}")
    try:
        process_item(item)
        logger.info(f"  ✓ Success")
    except Exception as e:
        logger.error(f"  ✗ Failed: {e}")
        continue
```

## Performance Considerations

### Logging Overhead

- **File I/O**: Logging to file has minimal overhead
- **String formatting**: Use lazy formatting for DEBUG messages
- **Log level filtering**: Set appropriate level to reduce overhead

### Lazy Formatting

```python
# GOOD ✅ - Only formats if DEBUG level enabled
logger.debug(f"Processing module: {module_id} with {len(subtopics)} subtopics")

# BETTER ✅ - Use % formatting for complex strings
logger.debug("Processing module: %s with %d subtopics", module_id, len(subtopics))
```

### Log Level Selection

- **Production**: INFO level (reduces overhead)
- **Development**: DEBUG level (full diagnostics)
- **Troubleshooting**: DEBUG level (detailed information)

## Error Collector System

The system includes a centralized error collection and reporting system for tracking validation issues, warnings, and critical errors during content generation.

### ErrorCollector Class

The `ErrorCollector` class provides centralized error/warning collection with categorization:

```python
from src.utils.error_collector import ErrorCollector

# Initialize collector
collector = ErrorCollector()

# Add errors/warnings during generation
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

# Query collected issues
critical_issues = collector.get_critical_issues()
warnings = collector.get_warnings()
summary = collector.get_summary()
```

### Stage Summaries

After each generation stage, a comprehensive summary is automatically generated:

```python
from src.utils.summary_generator import generate_stage_summary

generate_stage_summary(
    collector,
    "Primary Materials Generation",
    logger,
    total_items=10,
    successful_items=8,
    failed_items=2
)
```

This produces formatted output showing:
- Total items processed
- Compliance breakdown ([COMPLIANT] vs [NEEDS REVIEW] vs [CRITICAL])
- Critical issues count and list
- Warnings count
- Recommendations

### Error Categorization

Errors are automatically categorized by:
- **Severity**: CRITICAL, WARNING, INFO
- **Type**: validation, generation, format, content, system
- **Content Type**: lecture, lab, questions, diagrams, etc.
- **Context**: Module/session information

### Integration in Generators

All format generators accept an optional `error_collector` parameter:

```python
lecture = lecture_generator.generate_lecture(
    module_info,
    error_collector=collector
)
```

Validation issues are automatically collected and included in stage summaries.

## Visual Accessibility Improvements

All status indicators now include text labels alongside emojis for maximum accessibility and screen reader compatibility.

### Text Labels with Emojis

All status messages use the pattern: `[STATUS] message (emoji)`:

```python
from src.utils.logging_setup import log_status_with_text

# Always includes text label
log_status_with_text(logger, "COMPLIANT", "Lecture generated", emoji="✓", level="INFO")
# Output: [COMPLIANT] Lecture generated ✓

log_status_with_text(logger, "CRITICAL", "Missing question marks", emoji="🔴", level="WARNING")
# Output: [CRITICAL] Missing question marks 🔴
```

### Status Indicators

All content validation uses standardized status indicators:

- `[COMPLIANT] ✓` - Content meets all requirements
- `[NEEDS REVIEW] ⚠️` - Content has warnings but is usable
- `[CRITICAL] 🔴` - Critical issues requiring immediate attention
- `[OK] ✓` - Validation passed
- `[WARNING] ⚠️` - Warning-level issues
- `[FIXED] ✓` - Issue was automatically fixed

### Enhanced Critical Error Logging

Critical errors are logged with structured format including context, impact, and recommendations:

```
[CRITICAL] Format Issue: Missing question marks 🔴
    Context: Module 1 Session 2
    Impact: Questions may not be properly formatted for parsing
    Recommendation: Ensure all questions end with '?' and use **Question N:** format
```

This provides actionable information for fixing issues.

### Benefits

- **Screen Reader Compatible**: Text labels ensure all status information is accessible
- **Clear Categorization**: Errors are clearly categorized by severity and type
- **Actionable Guidance**: Critical errors include recommendations for fixes
- **Comprehensive Summaries**: Stage summaries provide overview of all issues
- **Traceability**: All errors include context (module, session, content type)

## Related Documentation

- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error logging patterns
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Using logs for debugging
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Logging strategy in system design
- **[.cursorrules/04-logging-unified.md](../.cursorrules/04-logging-unified.md)** - Logging standards

## Implementation Status

### Logging Compliance (Verified Dec 2024)

✅ **All modules use logging.getLogger(__name__)** - Consistent logger initialization across all 50+ Python files  
✅ **No print() statements** - All operational output uses logging module  
✅ **Request IDs included** - All LLM operations include request IDs for traceability  
✅ **Operation context** - All content generation includes module/session context  
✅ **Status indicators** - Consistent use of [COMPLIANT]/[NEEDS REVIEW]/[CRITICAL] status  
✅ **Error messages enhanced** - All errors include actionable guidance and troubleshooting hints  
✅ **Visual formatting** - Consistent emoji usage with text labels for accessibility  
✅ **Helper functions** - All modules use centralized logging utilities from `src.utils.logging_setup`

## Summary

The educational course Generator uses comprehensive, structured logging that:
- Provides clear visibility into system operation
- Enables debugging through request ID tracing
- Includes operation context for traceability
- Supports both console and file output
- Uses appropriate log levels for different scenarios
- Follows consistent formatting patterns

All logging follows the principle: **NO print() statements. EVER.** Use the logging module for all operational output, with centralized setup and helper functions for consistent, readable log messages.






