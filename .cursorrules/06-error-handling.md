# Error Handling Patterns

## Soft Constraint

**SHOULD handle errors gracefully with clear messages and proper exception types.**

## Exception Hierarchy

```python
class BiologyCourseError(Exception):
    """Base exception for all course generator errors."""
    pass

class ConfigurationError(BiologyCourseError):
    """Configuration file errors."""
    pass

class LLMError(BiologyCourseError):
    """LLM service errors."""
    pass

class ContentGenerationError(BiologyCourseError):
    """Content generation errors."""
    pass

class ValidationError(BiologyCourseError):
    """Validation errors."""
    pass
```

## Error Handling Patterns

### Configuration Errors

**Strategy**: Fail fast with clear messages

```python
# ✅ CORRECT: Clear error messages
from src.config.loader import ConfigurationError

if not self.config_dir.exists():
    raise ConfigurationError(
        f"Config directory not found: {self.config_dir}. "
        f"Expected location: {Path.cwd() / 'config'}"
    )

# ✅ CORRECT: Validate early
try:
    config = yaml.safe_load(config_file.read_text())
except yaml.YAMLError as e:
    raise ConfigurationError(f"Invalid YAML in {config_file}: {e}")
```

### LLM Errors

**Strategy**: Retry with exponential backoff

```python
# ✅ CORRECT: Retry logic
from src.llm.client import LLMError

max_retries = 3
for attempt in range(max_retries):
    try:
        response = self._make_request(prompt)
        return response
    except requests.RequestException as e:
        if attempt == max_retries - 1:
            raise LLMError(f"LLM request failed after {max_retries} attempts: {e}")
        delay = 2 ** attempt
        logger.warning(f"Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
        time.sleep(delay)
```

### Content Generation Errors

**Strategy**: Collect errors, continue processing

```python
# ✅ CORRECT: Collect errors
errors = []
for module in modules:
    try:
        generate_content(module)
    except ContentGenerationError as e:
        errors.append({"module": module['id'], "error": str(e)})
        logger.error(f"Failed to generate content for module {module['id']}: {e}")

if errors:
    logger.warning(f"Generation completed with {len(errors)} errors")
    return errors
```

## Error Messages

### Good Error Messages

- **Clear**: Explain what went wrong
- **Actionable**: Tell user how to fix
- **Contextual**: Include relevant information

```python
# ✅ CORRECT: Clear, actionable error
raise ConfigurationError(
    "No course outline JSON found. Generate outline first with: "
    "uv run python3 scripts/03_generate_outline.py"
)

# ✅ CORRECT: Contextual error
raise LLMError(
    f"Ollama connection failed: {e}. "
    f"Ensure Ollama is running: ollama serve"
)
```

### Bad Error Messages

```python
# ❌ WRONG: Vague error
raise Error("Something went wrong")

# ❌ WRONG: No context
raise ConfigurationError("Error")

# ❌ WRONG: Technical jargon without explanation
raise Error(f"HTTP {status_code}")
```

## Logging Errors

**SOFT**: Log errors with appropriate level and context:

```python
# ✅ CORRECT: Log with context
try:
    content = generate_content(module)
except ContentGenerationError as e:
    logger.error(
        f"Failed to generate content for module {module['id']} "
        f"({module['name']}): {e}",
        exc_info=True  # Include stack trace
    )
    raise
```

## See Also

- **[09-safe-to-fail.md](09-safe-to-fail.md)** - Safe-to-fail patterns
- **[../docs/ERROR_HANDLING.md](../docs/ERROR_HANDLING.md)** - Complete error handling guide
- **[04-logging-unified.md](04-logging-unified.md)** - Logging standards
