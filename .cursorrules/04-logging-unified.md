# Logging Standards - No print() Statements

## Hard Constraint

**MUST use `logging` module for ALL operational output. NO `print()` statements EVER.**

## Core Principle

All operational output uses the logging module. This enables:
- Log levels (DEBUG, INFO, WARNING, ERROR)
- File output (console + file simultaneously)
- Filtering by level/module
- Consistent format across all output

## Basic Setup

### Module-Level Logging

```python
# ✅ CORRECT: Module-level logger
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("Processing data...")
    logger.debug(f"Variable value: {value}")
    logger.error("Something went wrong")

# ❌ WRONG: Using print()
def my_function():
    print("Processing data...")  # Violates rule
    print(f"Variable value: {value}")  # Violates rule
```

### Script-Level Logging

```python
# ✅ CORRECT: Setup logging for scripts
from src.utils.logging_setup import setup_logging
import logging

# Setup with file output
log_file = setup_logging(
    script_name="my_script",
    log_level="INFO",
    console_output=True,
    file_output=True
)

logger = logging.getLogger(__name__)
logger.info(f"Log file: {log_file}")
```

## Logging Levels

### DEBUG - Detailed Diagnostic Info

```python
logger.debug(f"Processing module: {module_id}")
logger.debug(f"Template requires {len(required_vars)} variables")
logger.debug(f"[{request_id}] Stream progress: 5.2s elapsed, 42 chunks")
```

**Use for**: Variable values, detailed execution flow, LLM request/response details

### INFO - General Informational Messages

```python
logger.info("Starting outline generation...")
logger.info(f"Generated lecture: {len(lecture)} characters")
logger.info(f"[{request_id}] LLM Request: lecture | model=gemma3:4b")
logger.info("✓ Lecture generated: [COMPLIANT]")
```

**Use for**: Major steps, progress updates, successful operations, validation status

### WARNING - Recoverable Issues

```python
logger.warning("Ollama connection failed, retrying...")
logger.warning(f"Word count (899) below minimum 1000")
logger.warning("Skipping module 5 due to missing data")
```

**Use for**: Recoverable issues, skipped items, retry attempts, validation warnings

### ERROR - Failures

```python
logger.error("Failed to generate lecture for module 1")
logger.error(f"Configuration error: {e}")
logger.error("Ollama service not responding after 3 retries")
```

**Use for**: Failures that affect functionality, exceptions, critical issues

## Structured Logging

### Request ID Tracing

```python
# ✅ CORRECT: Include request ID for tracing
request_id = generate_request_id()
logger.info(f"[{request_id}] LLM Request: model=gemma3:4b, timeout=120s")
logger.debug(f"[{request_id}] Stream progress: 5.2s elapsed, 42 chunks")
logger.info(f"[{request_id}] Generation complete: 2847 chars in 12.5s")
```

### Operation Context

```python
# ✅ CORRECT: Include operation context
logger.info(f"Generating lecture for module {module_id}, session {session_num}")
logger.debug(f"Module: {module_name}, Session: {session_title}")
```

## Log File Output

All scripts write logs to timestamped files:
- Location: `output/logs/` or `scripts/output/logs/`
- Format: `{script_name}_{YYYYMMDD}_{HHMMSS}.log`
- Example: `04_generate_primary_20241208_143022.log`

## Anti-Patterns

❌ **Don't use `print()` for operational output**  
❌ **Don't use `print()` for debugging (use `logger.debug()`)**  
❌ **Don't use `print()` for errors (use `logger.error()`)**  
❌ **Don't mix `print()` and logging**  
❌ **Don't use `print()` in tests (use `logger` or assertions)**

## Examples

### Good Logging

```python
import logging

logger = logging.getLogger(__name__)

def generate_content(module_info):
    logger.info(f"Generating content for module: {module_info['name']}")
    
    try:
        content = llm_client.generate(prompt)
        logger.info(f"Generated {len(content)} characters")
        logger.debug(f"Content preview: {content[:100]}...")
        return content
    except LLMError as e:
        logger.error(f"LLM generation failed: {e}")
        raise
```

### Bad Logging (Violates Rule)

```python
def generate_content(module_info):
    print(f"Generating content for module: {module_info['name']}")  # ❌
    
    try:
        content = llm_client.generate(prompt)
        print(f"Generated {len(content)} characters")  # ❌
        return content
    except LLMError as e:
        print(f"Error: {e}")  # ❌
        raise
```

## See Also

- **[../docs/LOGGING.md](../docs/LOGGING.md)** - Complete logging guide
- **[../src/utils/logging_setup.py](../src/utils/logging_setup.py)** - Logging setup utilities
- **[00-overview.md](00-overview.md)** - Core principles
