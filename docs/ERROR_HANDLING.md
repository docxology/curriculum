# Error Handling Guide

Complete reference for error handling patterns, exception hierarchy, and recovery strategies in the educational course Generator.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Philosophy** | Safe-to-fail: collect errors, continue working, report comprehensively |
| **Exception Hierarchy** | BiologyCourseError → ConfigurationError, LLMError, ContentGenerationError, ValidationError |
| **Error Collection** | Pipeline collects all errors, doesn't stop on first failure |
| **Retry Strategy** | Exponential backoff for transient errors (LLM), fail-fast for permanent errors (config) |
| **Error Logging** | All errors logged with context, request IDs, and actionable messages |

**Read time**: 20-30 minutes | **Audience**: Developers, contributors, system operators

## Core Principle

### FAIL GRACEFULLY, CONTINUE WORKING

Errors should not crash the system. Report clearly, continue when possible, collect all errors.

**Traditional approach**: First error stops everything  
**Safe-to-fail approach**: Collect all errors, complete what's possible, report comprehensively

## Exception Hierarchy

### Base Exception

```python
class BiologyCourseError(Exception):
    """Base exception for all course generator errors."""
    pass
```

### Specific Exceptions

```python
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

### Import Paths

```python
from src.config.loader import ConfigurationError
from src.llm.client import LLMError
```

### Usage Examples

```python
# Configuration errors
if not self.config_dir.exists():
    raise ConfigurationError(
        f"Config directory not found: {self.config_dir}"
    )

# LLM errors
if not ollama_available():
    raise LLMError("Ollama service not running on port 11434")

# Content generation errors
if len(lecture) < 500:
    raise ContentGenerationError(f"Lecture too short: {len(lecture)} chars")

# Validation errors
if not modules:
    raise ValidationError("No modules found in outline")
```

## Error Handling Patterns by Layer

### Configuration Layer

**Strategy**: Fail fast with clear messages

**Pattern**:
```python
# Validate early, fail fast
if not self.config_dir.exists():
    raise ConfigurationError(
        f"Config directory not found: {self.config_dir}. "
        f"Expected location: {Path.cwd() / 'config'}"
    )

# Validate structure
if 'course' not in config:
    raise ConfigurationError(
        "Missing 'course' section in course_config.yaml"
    )

# Validate types
if not isinstance(num_modules, int) or num_modules < 1:
    raise ConfigurationError(
        f"'course.defaults.num_modules' must be a positive integer. "
        f"Got: {num_modules} (type: {type(num_modules).__name__})"
    )
```

**Characteristics**:
- No retries (permanent errors)
- Clear, actionable error messages
- Include expected vs actual values
- Suggest fixes

### LLM Integration Layer

**Strategy**: Retry with exponential backoff, distinguish transient vs permanent errors

**Pattern**:
```python
def generate(self, prompt: str, system_prompt: str = None) -> str:
    """Generate with retry logic."""
    for attempt in range(self.max_retries + 1):
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            return self._parse_streaming_response(response)
            
        except requests.ConnectionError as e:
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Connection error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
                continue
            raise LLMError(f"Connection error after {self.max_retries + 1} attempts: {e}") from e
            
        except requests.Timeout as e:
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Timeout (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
                continue
            raise LLMError(f"Timeout after {self.max_retries + 1} attempts: {e}") from e
            
        except requests.HTTPError as e:
            # Don't retry HTTP errors (4xx, 5xx)
            raise LLMError(f"HTTP error {e.response.status_code}: {e}") from e
```

**Characteristics**:
- Retry transient errors (ConnectionError, Timeout)
- Don't retry permanent errors (HTTPError, ConfigurationError)
- Exponential backoff (1s, 2s, 4s, ...)
- Request ID tracking for debugging
- Detailed logging at each attempt

### Generation Layer

**Strategy**: Collect errors, continue processing, report comprehensively

**Pattern**:
```python
def stage2_generate_content_by_session(
    self,
    module_ids: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """Generate content for sessions, collecting all errors."""
    results = []
    errors = []
    
    for module in modules:
        for session in module['sessions']:
            session_result = {
                'module_id': module['module_id'],
                'session_num': session['session'],
                'status': 'pending'
            }
            
            try:
                # Generate all content types
                lecture = self.lecture_generator.generate_lecture(...)
                lab = self.lab_generator.generate_lab(...)
                # ... more generation ...
                
                session_result['status'] = 'success'
                logger.info(f"  ✓ Session {session['session']} completed")
                
            except Exception as e:
                logger.error(f"  ✗ Error processing session {session['session']}: {e}")
                session_result['status'] = 'error'
                session_result['error'] = str(e)
                errors.append({
                    'module': module['module_name'],
                    'session': session['session'],
                    'error': str(e),
                    'type': type(e).__name__
                })
                # Continue to next session
            
            results.append(session_result)
    
    # Report summary
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = len(results) - successful
    
    logger.info("=" * 80)
    logger.info(f"Stage 2 complete. Processed {len(results)} sessions")
    logger.info(f"  Successful: {successful}, Failed: {failed}")
    if errors:
        logger.error("Errors encountered:")
        for err in errors:
            logger.error(f"  - {err['module']} Session {err['session']}: {err['error']}")
    logger.info("=" * 80)
    
    return results
```

**Characteristics**:
- Collect all errors, don't stop on first failure
- Continue processing remaining items
- Report comprehensive summary at end
- Include context (module, session, error type)
- Return partial results

### Processing Layer

**Strategy**: Validate early, provide clear validation errors

**Pattern**:
```python
def parse_outline(outline_text: str) -> List[Dict[str, Any]]:
    """Parse outline with validation."""
    if not outline_text or not outline_text.strip():
        raise ValidationError("Outline text is empty")
    
    # Validate structure
    if "course_metadata" not in outline_data:
        raise ValidationError(
            "Missing 'course_metadata' in outline JSON. "
            "Expected structure: {'course_metadata': {...}, 'modules': [...]}"
        )
    
    # Validate required fields
    required_fields = ['name', 'level', 'duration_weeks', 'total_sessions', 'total_modules']
    metadata = outline_data['course_metadata']
    missing = [f for f in required_fields if f not in metadata]
    if missing:
        raise ValidationError(
            f"Missing required fields in course_metadata: {', '.join(missing)}"
        )
    
    # Process if valid
    return extract_modules(outline_data)
```

**Characteristics**:
- Validate before expensive operations
- Clear validation error messages
- Include expected structure/format
- Fail fast on invalid input

## Error Handling Patterns

### Pattern 1: Collect Errors, Don't Stop

```python
# GOOD ✅ - Collect all errors
def generate_all_modules(modules):
    """Generate content for all modules, collecting errors."""
    results = []
    errors = []
    
    for module in modules:
        try:
            result = generate_module_content(module)
            results.append(result)
            logger.info(f"✓ Module {module['name']} completed")
        except Exception as e:
            error_info = {
                'module': module['name'],
                'error': str(e),
                'type': type(e).__name__
            }
            errors.append(error_info)
            logger.error(f"✗ Module {module['name']} failed: {e}")
            continue  # Keep going
    
    # Report summary
    logger.info(f"Completed: {len(results)}/{len(modules)}")
    if errors:
        logger.error(f"Failed: {len(errors)} modules")
        for err in errors:
            logger.error(f"  - {err['module']}: {err['error']}")
    
    return results, errors

# BAD ❌ - Stop on first error
def generate_all_modules(modules):
    results = []
    for module in modules:
        result = generate_module_content(module)  # Crashes on first error
        results.append(result)
    return results
```

### Pattern 2: Try-Except with Context

```python
# GOOD ✅ - Specific exceptions, clear messages
try:
    content = llm_client.generate(prompt)
except requests.ConnectionError as e:
    logger.error(f"Cannot connect to Ollama at {api_url}: {e}")
    raise LLMError("Ollama service unavailable") from e
except requests.Timeout as e:
    logger.error(f"Ollama timeout after {timeout}s: {e}")
    raise LLMError("Ollama response timeout") from e
except requests.HTTPError as e:
    logger.error(f"Ollama HTTP error: {e.response.status_code}")
    raise LLMError(f"Ollama API error: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

# BAD ❌ - Generic catch-all
try:
    content = llm_client.generate(prompt)
except Exception as e:
    logger.error("Error")  # No context!
    raise
```

### Pattern 3: Partial Success

```python
# GOOD ✅ - Return what succeeded
def generate_module_content(module):
    """Generate all content types, return partial results."""
    results = {}
    errors = {}
    
    # Try lecture
    try:
        results['lecture'] = generate_lecture(module)
    except Exception as e:
        errors['lecture'] = str(e)
        logger.warning(f"Lecture generation failed: {e}")
    
    # Try lab (even if lecture failed)
    try:
        results['lab'] = generate_lab(module)
    except Exception as e:
        errors['lab'] = str(e)
        logger.warning(f"Lab generation failed: {e}")
    
    # Try questions (even if others failed)
    try:
        results['questions'] = generate_questions(module)
    except Exception as e:
        errors['questions'] = str(e)
        logger.warning(f"Questions generation failed: {e}")
    
    if not results:
        raise ContentGenerationError(f"All content types failed: {errors}")
    
    return results, errors
```

### Pattern 4: Fallback Mechanisms

```python
# GOOD ✅ - Multiple fallback options
def get_content(module, strategies=['ollama', 'template', 'manual']):
    """Try multiple strategies until one works."""
    errors = []
    
    for strategy in strategies:
        try:
            if strategy == 'ollama':
                return generate_with_ollama(module)
            elif strategy == 'template':
                return use_template(module)
            elif strategy == 'manual':
                return request_manual_input(module)
        except Exception as e:
            logger.warning(f"Strategy '{strategy}' failed: {e}")
            errors.append((strategy, str(e)))
            continue
    
    # All strategies failed
    raise ContentGenerationError(f"All strategies failed: {errors}")
```

## Error Recovery Strategies

### Retry Logic with Exponential Backoff

```python
def generate_with_retry(prompt, max_retries=3):
    """Generate with exponential backoff retry."""
    for attempt in range(max_retries + 1):
        try:
            return llm_client.generate(prompt)
        except (ConnectionError, Timeout) as e:
            if attempt < max_retries:
                delay = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
                raise LLMError(f"Failed after {max_retries + 1} retries") from e
```

### Smart Retries (Don't Retry Everything)

```python
# Retry transient errors
RETRIABLE_ERRORS = (ConnectionError, Timeout, requests.HTTPError)

# Don't retry permanent errors
PERMANENT_ERRORS = (ConfigurationError, ValidationError)

try:
    return operation()
except RETRIABLE_ERRORS as e:
    # Retry
    return retry_operation()
except PERMANENT_ERRORS as e:
    # Don't retry, fail fast
    raise
```

### Validation Before Processing

```python
def generate_content(module):
    """Generate content with validation."""
    # Validate BEFORE expensive operations
    errors = validate_module(module)
    if errors:
        raise ValidationError(f"Invalid module: {errors}")
    
    # Now do expensive work
    return expensive_generation(module)

def validate_module(module):
    """Check module configuration."""
    errors = []
    
    if 'name' not in module:
        errors.append("Missing 'name' field")
    
    if 'id' not in module or module['id'] < 1:
        errors.append("Invalid 'id' field")
    
    if not module.get('subtopics'):
        errors.append("No subtopics defined")
    
    return errors
```

## Error Messages

### Clear, Actionable Messages

```python
# GOOD ✅ - Tells user what and how to fix
raise ConfigurationError(
    "Module 'num_lectures' must be positive integer. "
    f"Got: {num_lectures} (type: {type(num_lectures).__name__}). "
    "Fix in config/course_config.yaml"
)

# BAD ❌ - Vague, unhelpful
raise ValueError("Invalid config")
```

### Include Context

```python
# GOOD ✅ - Full context
logger.error(
    f"Failed to generate lecture for module {module['id']}: {module['name']}\n"
    f"  Error: {e}\n"
    f"  Config: {module_config}\n"
    f"  Attempt: {attempt}/{max_attempts}\n"
    f"  Request ID: {request_id}"
)

# BAD ❌ - No context
logger.error("Generation failed")
```

## Timeout Protection

### Set Reasonable Timeouts

```python
# GOOD ✅ - Always set timeout
response = requests.post(
    url,
    json=payload,
    timeout=120  # 2 minutes max
)

# BAD ❌ - No timeout, can hang forever
response = requests.post(url, json=payload)
```

### User-Configurable Timeouts

```yaml
# llm_config.yaml
llm:
  timeout: 120  # seconds
  retry_timeout: 60
```

## Resource Cleanup

### Always Clean Up

```python
# GOOD ✅ - Use context managers
def save_all_content(modules):
    """Save with proper cleanup."""
    with open(logfile, 'w') as f:
        for module in modules:
            try:
                content = generate(module)
                f.write(content)
            except Exception as e:
                logger.error(f"Failed {module['name']}: {e}")
                continue
    # File automatically closed

# Or explicit try-finally
file = None
try:
    file = open(path, 'w')
    file.write(content)
finally:
    if file:
        file.close()
```

## Progress Reporting

### Show Progress Even on Errors

```python
def generate_all_modules(modules):
    """Generate with progress reporting."""
    total = len(modules)
    completed = 0
    failed = 0
    
    for i, module in enumerate(modules, 1):
        logger.info(f"[{i}/{total}] Processing: {module['name']}")
        
        try:
            generate_module(module)
            completed += 1
            logger.info(f"  ✓ Success ({completed} completed, {failed} failed)")
        except Exception as e:
            failed += 1
            logger.error(f"  ✗ Failed: {e} ({completed} completed, {failed} failed)")
            continue
    
    # Final summary
    logger.info("="*80)
    logger.info(f"SUMMARY: {completed} succeeded, {failed} failed out of {total}")
    logger.info("="*80)
```

## Session Failure Patterns

### Pattern: Individual Session Failures

**Scenario**: One or more sessions fail during content generation, but pipeline continues.

**Error Pattern**:
```
✗ Error processing session 2: [lecture-7c3f93fc] Stream timeout: 941.62s elapsed...
Module: Cell Biology (ID: 1)
Session: Cell Structure and Function
Generated materials: lecture
Request ID: lecture-7c3f93fc (filter logs: grep '[lecture-7c3f93fc]' output/logs/*.log)
Error: Stream timeout: 941.62s elapsed (limit: 360.00s)...
```

**Characteristics**:
- Error includes request ID for traceability
- Shows which materials were successfully generated before failure
- Provides module and session context
- Includes recovery suggestions

**Recovery**:
1. **Extract request ID** from error message
2. **Filter logs** to see full request lifecycle:
   ```bash
   grep "[lecture-7c3f93fc]" scripts/output/logs/*.log
   ```
3. **Identify root cause**: Check timeout, connection, or validation errors
4. **Regenerate failed session**:
   ```bash
   uv run python3 scripts/04_generate_primary.py --modules 1
   ```

### Pattern: Multiple Session Failures

**Scenario**: Multiple sessions fail, often with similar error patterns.

**Error Pattern**:
```
EXIT CODE: 1 (FAILURE)
Reason: 6 session(s) failed during generation

Failed sessions:
  - Module 1 Session 2: Stream timeout...
  - Module 1 Session 5: Stream timeout...
  - Module 2 Session 1: Stream timeout...
```

**Common Causes**:
- **Systematic timeout issues**: All failures are timeouts → increase timeout configuration
- **Resource exhaustion**: System overloaded → check CPU/memory, restart Ollama
- **Model performance degradation**: Model slowing down → restart Ollama, check GPU

**Recovery Strategy**:
1. **Identify pattern**: Are all failures the same type (timeout, connection, validation)?
2. **Check system resources**: `top`, `htop`, `ollama ps`
3. **Adjust configuration**: Increase timeouts if all are timeout errors
4. **Restart services**: Restart Ollama if performance degraded
5. **Regenerate in batches**: Process fewer sessions at once

### Pattern: Material Type-Specific Failures

**Scenario**: Specific material types consistently fail (e.g., all secondary materials).

**Error Pattern**:
```
✗ Error for session 4: application generation failed
Module: Genetics (ID: 2)
Session: Meiosis & Basic Inheritance
Request ID: application-a8246b76
Error: Stream timeout: 940.01s elapsed...
```

**Analysis**:
- Check if failures are specific to one material type
- Review operation-specific timeout settings
- Consider if material type has unique requirements

**Recovery**:
1. **Check operation timeout** for failing material type:
   ```yaml
   llm:
     operation_timeouts:
       application: 360  # Increase if timing out
   ```
2. **Regenerate specific material type**:
   ```bash
   uv run python3 scripts/05_generate_secondary.py --types application --modules 2
   ```

## Request ID Tracing

### Understanding Request IDs

Every LLM request is assigned a unique request ID in format `[operation-uuid]`:
- **Format**: `[operation-8char-uuid]`
- **Examples**: `[lecture-7c3f93fc]`, `[outline-a1b2c3d4]`, `[application-be338c3e]`
- **Purpose**: Trace specific request through logs for debugging

### Extracting Request IDs from Errors

**From Error Messages**:
```python
# Error message format
error_msg = "[lecture-7c3f93fc] Stream timeout: 941.62s elapsed..."

# Extract request ID
if "[" in error_msg and "]" in error_msg:
    request_id = error_msg[error_msg.find("[")+1:error_msg.find("]")]
    # request_id = "lecture-7c3f93fc"
```

**From Log Files**:
```bash
# Find request ID in logs
grep "Stream timeout" scripts/output/logs/*.log | grep -oE "\[.*?\]"

# Extract all request IDs from errors
grep "ERROR" scripts/output/logs/*.log | grep -oE "\[[a-z]+-[a-f0-9]{8}\]" | sort | uniq
```

### Tracing Request Lifecycle

**Step 1: Find Request ID**
```bash
# From error message or log entry
REQUEST_ID="lecture-7c3f93fc"
```

**Step 2: Filter Logs by Request ID**
```bash
# Find all entries for this request
grep "[${REQUEST_ID}]" scripts/output/logs/*.log

# See full lifecycle
grep -E "\[${REQUEST_ID}\]" scripts/output/logs/*.log | head -50
```

**Step 3: Analyze Request Timeline**
```bash
# Extract timeline of events
grep "[${REQUEST_ID}]" scripts/output/logs/*.log | \
  awk '{print $1, $2, $NF}' | \
  head -20
```

**Step 4: Check Performance Metrics**
```bash
# See stream progress logs
grep "[${REQUEST_ID}]" scripts/output/logs/*.log | grep "Stream:"

# Example output:
# Stream: 2.0s | Chunks: 68 (33.9/s) | Text: 414 chars (~104 tokens, 51.6 tok/s)
# Stream: 4.0s | Chunks: 136 (33.9/s) | Text: 820 chars (~205 tokens, 51.1 tok/s)
# Stream: 6.0s | Chunks: 204 (33.9/s) | Text: 1264 chars (~316 tokens, 52.6 tok/s)
```

### Common Request ID Patterns

**Timeout Errors**:
```
[operation-uuid] Stream timeout: X.XXs elapsed (limit: Y.YYs)
```
- Check if generation was making progress (chunks increasing)
- Verify timeout limit vs elapsed time
- Review performance metrics (chars/s, tok/s)

**Connection Errors**:
```
[operation-uuid] Connection timeout after X.XXs (limit: Ys)
```
- Check Ollama service status
- Verify network connectivity
- Review connection timeout settings

**HTTP Errors**:
```
[operation-uuid] HTTP error after X.XXs: 404 Not Found
```
- Check model availability
- Verify API endpoint
- Review model name in configuration

## Batch Processing Error Recovery

### Understanding Batch Processing Failures

**Scenario**: Running full pipeline for multiple courses, some stages fail.

**Error Pattern**:
```
Course 3/5: Introductory Chemistry
✗ Course Introductory Chemistry completed with errors: Failed stages: Secondary Materials

EXIT CODE: 1 (FAILURE)
Reason: 6 session(s) failed during generation
```

**Characteristics**:
- Pipeline continues processing remaining courses
- Each course reports success/failure status
- Final summary shows which courses/stages failed
- Request IDs included for all failures

### Recovery Strategies

#### Strategy 1: Identify and Fix Root Cause

**Step 1: Analyze Failure Pattern**
```bash
# Check which courses failed
grep "completed with errors" scripts/output/logs/run_pipeline_*.log

# Check which stages failed
grep "Failed stages" scripts/output/logs/run_pipeline_*.log

# Extract all request IDs from failures
grep "Stream timeout\|Connection error" scripts/output/logs/*.log | \
  grep -oE "\[[a-z]+-[a-f0-9]{8}\]" | sort | uniq
```

**Step 2: Identify Common Pattern**
- **All timeouts**: Increase timeout configuration
- **All connection errors**: Check Ollama service
- **Specific operation**: Adjust operation-specific timeout
- **Specific course**: Course-specific issue (check course config)

**Step 3: Fix Configuration**
```yaml
# config/llm_config.yaml
llm:
  timeout: 300  # Increase base timeout
  operation_timeouts:
    application: 360  # Increase for failing operation
    extension: 360
```

**Step 4: Retry Failed Courses**
```bash
# Retry specific course
uv run python3 scripts/run_pipeline.py
# Select failed course from menu

# Or retry specific stage for all courses
uv run python3 scripts/05_generate_secondary.py --all
```

#### Strategy 2: Process Courses Individually

**Instead of batch processing all courses**:
```bash
# Process one course at a time
uv run python3 scripts/run_pipeline.py
# Select course 1, wait for completion
# Then run again for course 2, etc.
```

**Benefits**:
- Easier to identify course-specific issues
- Can adjust configuration between courses
- Less resource intensive
- Easier to monitor progress

#### Strategy 3: Skip Failed Stages

**If outline generation fails**:
```bash
# Use existing outline, skip outline generation
uv run python3 scripts/run_pipeline.py --skip-outline
```

**If secondary materials fail**:
```bash
# Regenerate just secondary materials
uv run python3 scripts/05_generate_secondary.py --all
```

**If primary materials fail**:
```bash
# Regenerate just primary materials
uv run python3 scripts/04_generate_primary.py --all
```

#### Strategy 4: Selective Regeneration

**Regenerate specific modules**:
```bash
# Regenerate module 1 and 2 only
uv run python3 scripts/04_generate_primary.py --modules 1 2
uv run python3 scripts/05_generate_secondary.py --modules 1 2
```

**Regenerate specific material types**:
```bash
# Regenerate only applications and extensions
uv run python3 scripts/05_generate_secondary.py --types application extension
```

### Batch Processing Best Practices

1. **Start Small**: Test with one course before batch processing
2. **Monitor Progress**: Watch logs during first course to identify issues early
3. **Adjust Timeouts**: If timeouts occur, increase before continuing
4. **Check Resources**: Ensure adequate CPU/memory before starting
5. **Restart Services**: Restart Ollama between courses if needed
6. **Use Request IDs**: Track specific failures using request IDs
7. **Save Progress**: Generated content is saved even if pipeline fails

### Error Recovery Checklist

When batch processing fails:

- [ ] Extract request IDs from error messages
- [ ] Identify failure pattern (timeout, connection, validation)
- [ ] Check system resources (CPU, memory, disk)
- [ ] Review timeout configuration
- [ ] Check Ollama service status
- [ ] Filter logs by request ID to understand failures
- [ ] Adjust configuration based on failure pattern
- [ ] Retry failed courses or stages
- [ ] Verify successful completion before continuing

## Common Error Scenarios

### Configuration Errors

**Scenario**: Missing or invalid configuration file

**Error**:
```
ConfigurationError: Config directory not found: /path/to/config
```

**Solution**:
1. Verify config directory exists
2. Check file permissions
3. Ensure all required YAML files present

**Prevention**: Run `01_setup_environment.py` to validate configuration

### LLM Connection Errors

**Scenario**: Ollama service not running

**Error**:
```
LLMError: Connection error after 4 attempts: Connection refused
```

**Solution**:
1. Start Ollama: `ollama serve`
2. Verify service: `curl http://localhost:11434/api/version`
3. Check model availability: `ollama list`

**Prevention**: Run `01_setup_environment.py` to check Ollama availability

### LLM Timeout Errors

**Scenario**: LLM request takes too long

**Error**:
```
[lecture-7c3f93fc] Stream timeout: 941.62s elapsed (limit: 360.00s, base timeout: 240.00s).
Operation: lecture. Received 1427 chunks, 136439 bytes, 6649 chars (~1662 tokens) before timeout.
Performance: 7.1 chars/s, ~1.8 tok/s. Very slow generation...
```

**Solution**:
1. **Extract request ID**: `lecture-7c3f93fc`
2. **Filter logs** to see full request lifecycle:
   ```bash
   grep "[lecture-7c3f93fc]" scripts/output/logs/*.log
   ```
3. **Increase timeout** in `llm_config.yaml`:
   ```yaml
   llm:
     timeout: 300  # Increase base timeout
     operation_timeouts:
       lecture: 480  # Increase operation-specific timeout
   ```
4. **Check Ollama performance**: `ollama ps`, check GPU usage
5. **Consider using faster model** or checking system resources

**Prevention**: Set appropriate timeout based on model, operation type, and prompt size. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for timeout guidelines.

### Content Generation Errors

**Scenario**: Generated content doesn't meet requirements

**Error**:
```
ContentGenerationError: Lecture too short: 450 chars (minimum 1000)
```

**Solution**:
1. Adjust prompt template in `llm_config.yaml`
2. Increase `num_predict` parameter
3. Regenerate with different parameters

**Prevention**: Configure appropriate validation criteria

### Validation Errors

**Scenario**: Invalid JSON outline structure

**Error**:
```
ValidationError: Missing required fields in course_metadata: total_modules, total_sessions
```

**Solution**:
1. Regenerate outline: `03_generate_outline.py`
2. Validate JSON structure manually
3. Check LLM output format

**Prevention**: Use outline validation in `OutlineGenerator`

## Error Handling in Tests

### Test Failure Scenarios

```python
def test_handles_ollama_unavailable():
    """Verify graceful handling when Ollama down."""
    # Stop Ollama
    stop_ollama()
    
    from src.config.loader import ConfigLoader
    from src.generate.orchestration.pipeline import ContentGenerator
    config_loader = ConfigLoader("config")
    generator = ContentGenerator(config_loader)
    
    # Should not crash, should report error
    with pytest.raises(LLMError, match="Ollama service unavailable"):
        generator.stage1_generate_outline()
    
    # Verify error was logged
    assert "Cannot connect to Ollama" in caplog.text

def test_partial_module_generation():
    """Verify partial results returned on partial failure."""
    module = {...}
    
    # Mock one generator to fail
    with patch('lecture_generator.generate', side_effect=Exception("Mock fail")):
        results, errors = generate_module_content(module)
    
    # Should have some results
    assert 'lab' in results
    assert 'questions' in results
    
    # Should have error for lecture
    assert 'lecture' in errors
```

## Best Practices

1. **Collect errors** - Don't stop on first failure
2. **Clear messages** - Include context and how to fix
3. **Retry transient** - But not permanent errors
4. **Validate early** - Before expensive operations
5. **Clean up always** - Use context managers
6. **Report progress** - Even when failing
7. **Test failures** - Error paths need tests too
8. **Use specific exceptions** - Don't use generic Exception
9. **Include context** - Module, session, request ID, etc.
10. **Actionable messages** - Tell user how to fix

## Related Documentation

- **[LOGGING.md](LOGGING.md)** - Error logging patterns and best practices
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common errors and solutions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and error handling strategy
- **[API.md](API.md)** - Exception hierarchy and usage
- **[.cursorrules/09-safe-to-fail.md](../.cursorrules/09-safe-to-fail.md)** - Safe-to-fail principles

## Summary

**Philosophy**: Systems fail. Design for it. Fail gracefully, report clearly, continue when possible.

The educational course Generator implements comprehensive error handling that:
- Collects errors instead of stopping
- Provides clear, actionable error messages
- Retries transient errors with exponential backoff
- Validates early to prevent expensive failures
- Reports progress even during failures
- Returns partial results when possible

All error handling follows the "safe-to-fail" principle: the system continues working even when individual components fail, collecting and reporting all errors comprehensively.






