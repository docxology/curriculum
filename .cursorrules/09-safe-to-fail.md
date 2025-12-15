# Safe-to-Fail Patterns

## Soft Constraint

**SHOULD implement safe-to-fail patterns: collect errors, continue working, report comprehensively.**

## Core Principle

**FAIL GRACEFULLY, CONTINUE WORKING**

Errors should not crash the system. Report clearly, continue when possible, collect all errors.

## Pattern: Collect Errors

```python
# ✅ CORRECT: Collect errors, continue processing
errors = []
successful = []

for module in modules:
    try:
        result = generate_content(module)
        successful.append(module['id'])
    except ContentGenerationError as e:
        errors.append({
            "module_id": module['id'],
            "module_name": module['name'],
            "error": str(e)
        })
        logger.error(f"Failed module {module['id']}: {e}")

# Report comprehensive results
logger.info(f"Completed: {len(successful)} successful, {len(errors)} failed")
if errors:
    logger.warning("Failed modules:")
    for error in errors:
        logger.warning(f"  - Module {error['module_id']}: {error['error']}")
```

## Pattern: Continue on Partial Failure

```python
# ✅ CORRECT: Continue even if some items fail
def generate_all_sessions(module):
    results = {"lecture": None, "lab": None, "questions": None}
    
    # Generate lecture (continue even if fails)
    try:
        results["lecture"] = generate_lecture(module)
    except ContentGenerationError as e:
        logger.error(f"Lecture generation failed: {e}")
    
    # Generate lab (continue even if lecture failed)
    try:
        results["lab"] = generate_lab(module)
    except ContentGenerationError as e:
        logger.error(f"Lab generation failed: {e}")
    
    # Generate questions (continue even if others failed)
    try:
        results["questions"] = generate_questions(module)
    except ContentGenerationError as e:
        logger.error(f"Questions generation failed: {e}")
    
    return results
```

## Pattern: Retry with Backoff

```python
# ✅ CORRECT: Retry transient errors
from time import sleep

max_retries = 3
for attempt in range(max_retries):
    try:
        response = llm_client.generate(prompt)
        return response
    except LLMError as e:
        if attempt == max_retries - 1:
            raise  # Final attempt failed
        delay = 2 ** attempt
        logger.warning(f"Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
        sleep(delay)
```

## Pattern: Skip Unavailable Dependencies

```python
# ✅ CORRECT: Skip gracefully if dependency unavailable
from src.utils.helpers import check_ollama_available

if check_ollama_available():
    try:
        generate_with_llm()
    except LLMError as e:
        logger.error(f"LLM generation failed: {e}")
else:
    logger.warning("Ollama not available, skipping LLM generation")
    # Continue with other operations
```

## Pattern: Comprehensive Reporting

```python
# ✅ CORRECT: Report all results comprehensively
def generate_all_modules(modules):
    results = {
        "successful": [],
        "failed": [],
        "warnings": []
    }
    
    for module in modules:
        try:
            result = generate_content(module)
            if result.get("warnings"):
                results["warnings"].append({
                    "module": module['id'],
                    "warnings": result["warnings"]
                })
            results["successful"].append(module['id'])
        except ContentGenerationError as e:
            results["failed"].append({
                "module": module['id'],
                "error": str(e)
            })
    
    # Comprehensive summary
    logger.info(f"Generation complete:")
    logger.info(f"  Successful: {len(results['successful'])}")
    logger.info(f"  Failed: {len(results['failed'])}")
    logger.info(f"  Warnings: {len(results['warnings'])}")
    
    return results
```

## Anti-Patterns

❌ **Don't fail fast on first error**  
❌ **Don't stop processing on single failure**  
❌ **Don't hide errors**  
❌ **Don't crash on recoverable errors**

## See Also

- **[06-error-handling.md](06-error-handling.md)** - Error handling patterns
- **[../docs/ERROR_HANDLING.md](../docs/ERROR_HANDLING.md)** - Complete error handling guide
- **[../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md)** - Pipeline error handling
