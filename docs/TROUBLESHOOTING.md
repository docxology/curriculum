# Troubleshooting Guide

Complete troubleshooting reference for common issues, diagnosis workflows, and solutions in the educational course Generator.

## Quick Reference Card

| Issue Category | Common Issues | Quick Fix |
|----------------|---------------|-----------|
| **Configuration** | Missing files, invalid YAML, missing fields | Run `01_setup_environment.py` |
| **LLM** | Connection errors, timeouts, model not found | Start Ollama, verify model |
| **Generation** | Outline not found, invalid JSON, content missing | Regenerate, check logs |
| **File I/O** | Permission errors, path issues, missing directories | Check permissions, verify paths |
| **Import Errors** | ModuleNotFoundError, import failures | Check sys.path, verify structure |

**Read time**: 25-35 minutes | **Audience**: All users, especially operators and developers

## Issue Diagnosis Workflow

### Step 1: Identify Issue Category

1. **Configuration**: Issues with YAML files, validation errors
2. **LLM**: Connection errors, timeouts, generation failures
3. **Generation**: Content not generated, invalid structure
4. **File I/O**: Permission errors, missing files, path issues
5. **Import**: Module import errors, path problems

### Step 2: Check Logs

```bash
# Find most recent log file
ls -lt scripts/output/logs/*.log | head -1

# Search for errors
grep "ERROR" scripts/output/logs/*.log

# Search for specific issue
grep "Connection" scripts/output/logs/*.log
grep "not found" scripts/output/logs/*.log
```

### Step 3: Verify Prerequisites

```bash
# Check environment
uv run python3 scripts/01_setup_environment.py

# Check Ollama
curl http://localhost:11434/api/version

# Check configs
uv run python3 scripts/02_run_tests.py
```

### Step 4: Apply Solution

Follow solution patterns below for specific issues.

## Configuration Issues

### Issue: "Config file not found"

**Symptoms**:
```
ConfigurationError: Config directory not found: /path/to/config
```

**Diagnosis**:
```bash
# Check config directory exists
ls -la config/

# Should see:
# - course_config.yaml
# - llm_config.yaml
# - output_config.yaml
```

**Solutions**:
1. Verify config directory exists: `ls -la config/`
2. Check file permissions: `chmod 644 config/*.yaml`
3. Verify working directory: Run scripts from project root
4. Use explicit path: `ConfigLoader("/absolute/path/to/config")`

**Prevention**: Run `01_setup_environment.py` to validate configuration

### Issue: "Missing required field"

**Symptoms**:
```
ConfigurationError: Missing required field: 'model' in llm_config.yaml
```

**Diagnosis**:
```bash
# Check specific field
cat config/llm_config.yaml | grep -A 5 "llm:"

# Validate all configs
uv run python3 -c "from src.config.loader import ConfigLoader; ConfigLoader('config').validate_all_configs()"
```

**Solutions**:
1. Check validation error message for specific field
2. Compare against structure in [CONFIGURATION.md](CONFIGURATION.md)
3. Add missing field to YAML file
4. Re-validate: `ConfigLoader('config').validate_all_configs()`

**Common Missing Fields**:
- `llm.model` - Model name (e.g., "gemma3:4b")
- `course.name` - Course title
- `course.defaults.num_modules` - Number of modules
- `prompts.outline` - Outline prompt template

### Issue: "Invalid YAML"

**Symptoms**:
```
ConfigurationError: Invalid YAML in llm_config.yaml: ...
```

**Diagnosis**:
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/llm_config.yaml'))"

# Use online validator
# https://www.yamllint.com/
```

**Solutions**:
1. Check for syntax errors:
   - Indentation (use spaces, not tabs)
   - Colons after keys
   - Proper quote usage
   - List formatting
2. Use YAML validator: Online tool or `yaml.safe_load()`
3. Check for trailing commas (not allowed in YAML)
4. Verify nested structure matches expected format

**Common YAML Errors**:
- Missing colons: `key value` → `key: value`
- Wrong indentation: Use consistent spaces (2 or 4)
- Tabs instead of spaces: Convert tabs to spaces
- Unquoted special characters: Quote strings with special chars

### Issue: "Type mismatch"

**Symptoms**:
```
ConfigurationError: 'course.defaults.num_modules' must be a positive integer. Got: "5" (type: str)
```

**Diagnosis**:
```bash
# Check field type
cat config/course_config.yaml | grep -A 2 "num_modules"
```

**Solutions**:
1. Remove quotes from numeric values: `num_modules: 5` not `num_modules: "5"`
2. Check boolean values: `true`/`false` (lowercase) not `True`/`False`
3. Verify list formatting: Use `- item` not `item1, item2`
4. Re-validate configuration

## LLM Issues

### Issue: "Ollama connection error"

**Symptoms**:
```
LLMError: Connection error after 4 attempts: Connection refused
```

**Diagnosis**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check Ollama process
ps aux | grep ollama

# Check port availability
lsof -i :11434
```

**Solutions**:
1. **Start Ollama service**:
   ```bash
   ollama serve
   ```

2. **Verify service is running**:
   ```bash
   curl http://localhost:11434/api/version
   # Should return: {"version":"..."}
   ```

3. **Check API URL in config**:
   ```yaml
   # config/llm_config.yaml
   llm:
     api_url: "http://localhost:11434/api/generate"
   ```

4. **Check firewall/network**: Ensure port 11434 is accessible

**Prevention**: Run `01_setup_environment.py` to check Ollama availability

### Issue: "Model not found"

**Symptoms**:
```
LLMError: Model 'gemma3:4b' not found
```

**Diagnosis**:
```bash
# List available models
ollama list

# Check model name in config
cat config/llm_config.yaml | grep "model:"
```

**Solutions**:
1. **Download model**:
   ```bash
   ollama pull gemma3:4b
   ```

2. **Verify model name**: Check `llm_config.yaml` matches downloaded model
   ```bash
   ollama list
   # Use exact model name from list
   ```

3. **Check model availability**:
   ```bash
   ollama show gemma3:4b
   ```

**Common Model Names**:
- `gemma3:4b` - Gemma 3 4B model (default)
- `mistral` - Mistral model

### Issue: "Request hangs indefinitely"

**Symptoms**:
- Request appears to hang with no response
- Log shows "Waiting for HTTP response..." but nothing happens
- Process appears frozen

**Diagnosis**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check Ollama logs
ollama logs

# Check if model is loaded
ollama ps

# Use health monitoring
python3 -c "
from src.llm.health import OllamaHealthMonitor
monitor = OllamaHealthMonitor()
diagnostics = monitor.get_diagnostics()
print(diagnostics)
"
```

**Solutions**:
1. **Restart Ollama Service**:
   ```bash
   pkill ollama
   ollama serve
   ```

2. **Check Model Status**:
   ```bash
   ollama list
   ollama ps
   ollama pull gemma3:4b  # If missing
   ```

3. **Use Health Monitoring**:
   The client now includes automatic health monitoring. Check logs for health check messages.

4. **Increase Timeout**:
   ```yaml
   llm:
     timeout: 300  # Increase from default 180
   ```

See [src/llm/TROUBLESHOOTING.md](../../src/llm/TROUBLESHOOTING.md) for comprehensive guide.

### Issue: "LLM timeout" / "Stream timeout"

**Symptoms**:
```
LLMError: [outline-a1b2c3d4] Stream timeout: 940.01s elapsed (limit: 480.00s, base timeout: 320.00s).
Operation: outline. Received 1373 chunks, 130759 bytes, 5452 chars (~1363 tokens) before timeout.
Performance: 5.8 chars/s, ~1.5 tok/s. Very slow generation...
```

**Understanding Adaptive Timeout Behavior**:

The system uses **adaptive timeout extension** to handle slow but progressing generations:
- **Base timeout**: From `config/llm_config.yaml` (default: 180s)
- **Initial stream timeout**: `base_timeout * 1.5` (e.g., 180s → 270s)
- **Adaptive extension**: If stream is making progress (chunks arriving or text growing), timeout extends up to `base_timeout * 3.5` (e.g., 180s → 630s max)
- **Stuck detection**: Streams without progress for 30s are detected early and fail fast
- **Progress monitoring**: Logs stream progress every 2s with chunk rate, text growth, speed

**Diagnosis**:
```bash
# Check timeout setting
cat config/llm_config.yaml | grep -A 10 "timeout"

# Check operation-specific timeout
cat config/llm_config.yaml | grep -A 10 "operation_timeouts"

# Extract request ID from error and filter logs
# Error message format: [operation-uuid] Stream timeout...
grep "[REQUEST_ID]" scripts/output/logs/*.log

# Check Ollama service status and performance
curl http://localhost:11434/api/version
time curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma3:4b","prompt":"test","stream":false,"num_predict":100}'

# Check system resources
top -l 1 | head -10  # macOS
htop  # Linux

# Use health monitoring for diagnostics
python3 -c "
from src.llm.health import OllamaHealthMonitor
monitor = OllamaHealthMonitor()
diagnostics = monitor.get_diagnostics()
suggestions = monitor.get_troubleshooting_suggestions(diagnostics, 'timeout')
for s in suggestions:
    print(f'  - {s}')
"
```

**Solutions by Error Type**:

1. **Very Slow Generation (<10 chars/s)**:
   - **Symptoms**: Performance metrics show <10 chars/s or <2 tok/s
   - **Causes**: Model too slow, system overloaded, GPU not available
   - **Solutions**:
     ```yaml
     # Increase timeout significantly
     llm:
       timeout: 300  # Increase base timeout
       operation_timeouts:
         outline: 600  # Very long for complex outlines
         lecture: 480  # Long for comprehensive lectures
     ```
   - **Additional steps**:
     - Check GPU acceleration: `ollama ps` (should show GPU usage)
     - Restart Ollama: `pkill ollama && ollama serve`
     - Use faster model: Consider smaller model variant
     - Check system resources: Ensure adequate CPU/memory

2. **Operation-Specific Timeout Recommendations**:
   ```yaml
   llm:
     timeout: 180  # Base timeout
     operation_timeouts:
       outline: 480  # Complex JSON generation (recommended: 480-600s)
       lecture: 360  # Comprehensive content (recommended: 360-480s)
       lab: 300  # Detailed procedures (recommended: 300-360s)
       application: 300  # Real-world examples (recommended: 300s)
       extension: 300  # Advanced topics (recommended: 300s)
       integration: 300  # Cross-module connections (recommended: 300s)
       investigation: 300  # Research questions (recommended: 300s)
       open_questions: 300  # Scientific debates (recommended: 300s)
       questions: 240  # Assessment questions (recommended: 240-300s)
       study_notes: 240  # Concise summaries (recommended: 240s)
       diagrams: 180  # Mermaid diagrams (recommended: 180-240s)
       default: 180
   ```

3. **No Chunks Received (chunk_count == 0)**:
   - **Symptoms**: Error shows "Received 0 chunks"
   - **Causes**: Ollama not responding, network issue, model not loaded
   - **Solutions**:
     - Check Ollama is running: `curl http://localhost:11434/api/version`
     - Verify model is available: `ollama list`
     - Check network connectivity
     - Restart Ollama service

4. **Chunks Received But No Text (text length == 0)**:
   - **Symptoms**: Error shows chunks received but 0 chars extracted
   - **Causes**: Model output format issue, parsing error
   - **Solutions**:
     - Check model compatibility: `ollama show gemma3:4b`
     - Update Ollama: `ollama update`
     - Check logs for parsing errors

5. **Stream Stuck (No Progress for 30s+)**:
   - **Symptoms**: Stream stops making progress, detected early
   - **Causes**: Model hung, network interruption
   - **Solutions**:
     - Retry the operation (automatic retry handles transient issues)
     - Restart Ollama: `pkill ollama && ollama serve`
     - Check for network interruptions

**Timeout Guidelines by Operation**:
- **Outline generation**: 480-600 seconds (complex JSON output, may be slow)
- **Lecture generation**: 360-480 seconds (comprehensive content)
- **Lab generation**: 300-360 seconds (detailed procedures)
- **Secondary materials**: 300 seconds (applications, extensions, etc.)
- **Questions**: 240-300 seconds (assessment questions)
- **Study notes**: 240 seconds (concise summaries)
- **Diagrams**: 180-240 seconds (Mermaid diagrams)

**Timeout Guidelines by Model Size**:
- **Small models (4B)**: 180-300 seconds base
- **Medium models (8B)**: 300-480 seconds base
- **Large models (13B+)**: 480-900 seconds base

**Using Request IDs for Troubleshooting**:

Error messages include request IDs in format `[operation-uuid]`:
```
[lecture-7c3f93fc] Stream timeout: 941.62s elapsed...
```

Filter logs by request ID:
```bash
# Find all log entries for a specific request
grep "[lecture-7c3f93fc]" scripts/output/logs/*.log

# See full request lifecycle
grep -E "\[lecture-7c3f93fc\]" scripts/output/logs/*.log | head -50
```

**Performance Expectations**:
- **Normal generation**: 50-200 chars/s, 10-50 tok/s
- **Slow but acceptable**: 20-50 chars/s, 5-10 tok/s
- **Very slow (may timeout)**: <10 chars/s, <2 tok/s
- **Outline generation**: 30-120 seconds (with optimized parameters)
- **Lecture generation**: 60-180 seconds
- **Secondary materials**: 30-120 seconds per type

**Note**: The system automatically extends timeouts if progress is being made. If you see timeout errors with very slow performance (<10 chars/s), the model or system may be overloaded. Consider increasing timeouts significantly or using a faster model.

### Issue: "Batch Processing Timeout Failures"

**Symptoms**:
- Multiple sessions fail during batch processing (e.g., "6 session(s) failed during generation")
- Timeout errors appear for specific operations (outline, lecture, secondary materials)
- Errors show request IDs but no clear pattern

**Understanding Batch Processing**:
- Batch processing runs full pipeline for multiple courses sequentially
- Each course goes through all 6 stages (setup → validation → outline → primary → secondary → website)
- Timeout failures in one stage don't stop the pipeline but are reported at the end
- Request IDs are included in all error messages for traceability

**Diagnosis**:
```bash
# Check which sessions failed
grep "failed during generation" scripts/output/logs/run_pipeline_*.log

# Find timeout errors with request IDs
grep "Stream timeout" scripts/output/logs/*.log | grep -E "\[.*\]"

# Check for specific operation timeouts
grep -E "Operation: (outline|lecture|application)" scripts/output/logs/*.log | grep timeout

# Analyze timeout patterns
grep "Stream timeout" scripts/output/logs/*.log | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
```

**Solutions**:

1. **Increase Operation-Specific Timeouts**:
   ```yaml
   # config/llm_config.yaml
   llm:
     timeout: 300  # Increase base timeout for batch processing
     operation_timeouts:
       outline: 600  # Very long for complex outlines
       lecture: 480  # Long for comprehensive lectures
       application: 360  # Longer for detailed applications
       extension: 360
       integration: 360
       investigation: 360
       open_questions: 360
   ```

2. **Process Courses Individually**:
   Instead of batch processing all courses, process them one at a time:
   ```bash
   # Process one course at a time
   uv run python3 scripts/run_pipeline.py
   # Select course 1, wait for completion, then run again for course 2
   ```

3. **Skip Failed Stages and Retry**:
   ```bash
   # If outline generation fails, skip it and use existing outline
   uv run python3 scripts/run_pipeline.py --skip-outline
   
   # If secondary materials fail, regenerate just those
   uv run python3 scripts/05_generate_secondary.py --modules 1 2 3
   ```

4. **Monitor System Resources During Batch Processing**:
   - Check CPU/memory usage: `top` or `htop`
   - Monitor Ollama performance: `ollama ps`
   - Restart Ollama between courses if needed

5. **Use Request IDs to Investigate Specific Failures**:
   ```bash
   # Extract request ID from error message
   # Example: [lecture-7c3f93fc] Stream timeout...
   REQUEST_ID="lecture-7c3f93fc"
   
   # Find all log entries for this request
   grep "[${REQUEST_ID}]" scripts/output/logs/*.log
   
   # See performance metrics
   grep "[${REQUEST_ID}]" scripts/output/logs/*.log | grep "Stream:"
   ```

**Best Practices for Batch Processing**:
- **Start with one course**: Test pipeline with one course before batch processing
- **Monitor first course**: Watch logs during first course to identify timeout issues early
- **Adjust timeouts**: If timeouts occur, increase operation-specific timeouts before continuing
- **Use course-specific timeouts**: Different courses may need different timeout settings
- **Check system resources**: Ensure adequate CPU/memory before starting batch processing
- **Restart Ollama periodically**: If processing many courses, restart Ollama between courses

**Recovery from Batch Processing Failures**:
1. **Identify failed courses**: Check final summary in logs
2. **Extract request IDs**: Note request IDs from error messages
3. **Investigate specific failures**: Use request IDs to filter logs and understand failures
4. **Adjust configuration**: Increase timeouts for operations that failed
5. **Retry failed courses**: Re-run pipeline for specific courses or regenerate failed stages

### Issue: "Slow generation performance"

**Symptoms**:
- Outline generation taking 240+ seconds (expected: 30-60s)
- Connection check shows slow response time (>1s)
- Generation rate is very low (<10 chars/s)
- Warnings about Ollama performance in logs

**Diagnosis**:
```bash
# Check Ollama response time
time curl http://localhost:11434/api/version

# Check system resources
top -l 1 | head -10  # macOS
htop  # Linux

# Check Ollama is using resources
ps aux | grep ollama

# Test simple generation
time curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma3:4b","prompt":"test","stream":false,"num_predict":100}'
```

**Solutions**:

1. **Check Ollama Performance**:
   - Verify Ollama is running: `curl http://localhost:11434/api/version`
   - Check response time (should be <1s)
   - Restart Ollama if slow: `pkill ollama && ollama serve`

2. **Check System Resources**:
   - Ensure adequate CPU/memory available
   - Close other resource-intensive applications
   - Check disk space (Ollama needs space for models)

3. **Optimize Generation Parameters** (already applied for outlines):
   - Outline generation uses optimized parameters:
     - `num_ctx: 32000` (reduced from 128K)
     - `num_predict: 4000` (reduced from 64K)
   - These optimizations significantly improve speed

4. **Model Performance**:
   - gemma3:4b should complete outlines in 30-60s
   - If consistently slow, consider:
     - Restarting Ollama service
     - Using a different model
     - Checking for model corruption: `ollama pull gemma3:4b`

5. **Connection Health Check**:
   - System automatically checks Ollama before generation
   - Warnings appear if response time >1s
   - Address slow connection before generation starts

**Performance Expectations**:
- Outline generation: 30-60 seconds (with optimized parameters)
- Connection check: <1 second
- Generation rate: 50-200 chars/s (varies by model and hardware)

**Optimization Applied**:
The system automatically optimizes outline generation:
- Reduced context window (32K vs 128K) for faster inference
- Reduced output tokens (4K vs 64K) for faster generation
- Connection health check before generation
- Performance diagnostics and warnings

### Issue: "LLM returned empty response"

**Symptoms**:
```
LLMError: LLM returned empty response
```

**Diagnosis**:
```bash
# Check logs for request details
grep "LLM Request" scripts/output/logs/*.log | tail -5

# Test Ollama directly
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma3:4b","prompt":"test","stream":false}'
```

**Solutions**:
1. **Check model is working**: Test with simple prompt
2. **Check prompt length**: Very long prompts may cause issues
3. **Check Ollama logs**: Review Ollama service logs
4. **Restart Ollama**: `pkill ollama && ollama serve`

## Generation Issues

### Issue: "Outline not found"

**Symptoms**:
```
ValueError: No JSON outline found. Run stage 1 (outline generation) first.
```

**Diagnosis**:
```bash
# Check outline exists
ls -la output/outlines/course_outline_*.json
ls -la scripts/output/outlines/course_outline_*.json

# Check search paths
grep "Searching for" scripts/output/logs/*.log
```

**Solutions**:
1. **Generate outline first**:
   ```bash
   uv run python3 scripts/03_generate_outline.py
   ```

2. **Use explicit path**:
   ```bash
   uv run python3 scripts/04_generate_primary.py --outline path/to/outline.json
   ```

3. **Check file permissions**: Ensure outline files are readable

**Prevention**: Always run Stage 03 before Stage 04/05

### Issue: "Invalid JSON structure"

**Symptoms**:
```
ValueError: Generated outline JSON failed validation. Check logs for details.
```

**Diagnosis**:
```bash
# Validate JSON syntax
cat output/outlines/course_outline_*.json | jq '.'

# Check for required fields
cat output/outlines/course_outline_*.json | jq '.course_metadata'
cat output/outlines/course_outline_*.json | jq '.modules[0]'
```

**Solutions**:
1. **Validate JSON syntax**: Use `jq` or Python `json.load()`
2. **Check required fields**: Verify `course_metadata` and `modules` present
3. **Regenerate outline**: LLM may have generated invalid JSON
4. **Manually fix JSON**: Edit JSON file if structure is close

**Common JSON Issues**:
- Missing closing braces/brackets
- Trailing commas
- Invalid field types
- Missing required fields

### Issue: "Module count mismatch"

**Symptoms**:
```
Warning: Generated modules (4) don't match requested (5)
```

**Diagnosis**:
```bash
# Check actual vs requested
jq '.course_metadata.total_modules, (.modules | length)' output/outlines/course_outline_*.json

# Check config
cat config/course_config.yaml | grep -A 2 "num_modules"
```

**Solutions**:
1. **Regenerate outline**: LLM may not have followed count exactly
2. **Adjust prompt template**: Make module count requirement more explicit
3. **Accept if close**: If 4 vs 5, may be acceptable
4. **Manually edit JSON**: Add/remove modules if needed

### Issue: "Content not generated"

**Symptoms**:
```
ERROR: Error processing session 1: ...
```

**Diagnosis**:
```bash
# Check logs for specific error
grep "Error processing" scripts/output/logs/*.log

# Check which sessions failed
grep "Failed:" scripts/output/logs/*.log
```

**Solutions**:
1. **Check error message**: Read specific error in logs
2. **Regenerate failed sessions**: Use `--modules` to regenerate specific modules
3. **Check LLM availability**: Verify Ollama is running
4. **Check disk space**: Ensure adequate space for output files

### Issue: "Module generation failed"

**Symptoms**:
```
✗ Error processing module Evolution: Connection timeout
```

**Solutions**:
```bash
# Regenerate just that module
uv run python3 scripts/04_generate_primary.py --modules <failed_id>

# Check logs for specific error
grep "Evolution" scripts/output/logs/*.log

# Adjust configuration if needed
```

## File I/O Issues

### Issue: "Permission denied"

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

**Diagnosis**:
```bash
# Check file permissions
ls -la output/

# Check directory permissions
ls -ld output/
```

**Solutions**:
1. **Fix permissions**:
   ```bash
   chmod -R u+w output/
   ```

2. **Check directory exists**: Ensure output directory exists
3. **Check disk space**: `df -h` to verify space available
4. **Run from correct directory**: Ensure you have write permissions

### Issue: "File not found"

**Symptoms**:
```
FileNotFoundError: File not found: /path/to/file
```

**Diagnosis**:
```bash
# Check if file exists
ls -la /path/to/file

# Check search paths
grep "Searching for" scripts/output/logs/*.log
```

**Solutions**:
1. **Verify file exists**: Check expected location
2. **Check search paths**: System searches multiple locations
3. **Use explicit path**: Specify full path if needed
4. **Regenerate file**: If missing, regenerate content

### Issue: "Directory not found"

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'output/modules'
```

**Solutions**:
1. **Create directory**: System should create automatically, but verify
2. **Check output config**: Verify `output.base_directory` in `output_config.yaml`
3. **Check permissions**: Ensure write permissions on parent directory

## Import Errors

### Issue: "ModuleNotFoundError: No module named 'src'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
```

**Diagnosis**:
```bash
# Check if running from project root
pwd

# Check sys.path in script
head -20 scripts/04_generate_primary.py | grep sys.path
```

**Solutions**:
1. **Run from project root**: `cd /path/to/biology && uv run python3 scripts/...`
2. **Check script has sys.path fix**: All scripts should include:
   ```python
   _script_dir = Path(__file__).resolve().parent
   _project_root = _script_dir.parent
   if str(_project_root) not in sys.path:
       sys.path.insert(0, str(_project_root))
   ```
3. **Verify project structure**: Ensure `src/` directory exists
4. **Use uv run**: `uv run python3 scripts/...` handles paths correctly

**Prevention**: Always use `uv run python3 scripts/...` from project root

### Issue: "Import from wrong location"

**Symptoms**:
```
ImportError: cannot import name 'ConfigLoader' from 'src.config'
```

**Diagnosis**:
```bash
# Check import statement
grep "from src.config" your_script.py

# Verify module structure
ls -la src/config/
```

**Solutions**:
1. **Use modular imports**: `from src.config.loader import ConfigLoader`
2. **Check module structure**: Verify `src/config/loader.py` exists
3. **Verify `__init__.py`**: Ensure `src/config/__init__.py` exists
4. **Check Python path**: Verify project root in `sys.path`

## Validation Issues

### Issue: "Content always shows [NEEDS REVIEW]"

**Symptoms**: All generated content has validation warnings

**Diagnosis**:
```bash
# Check validation criteria
cat config/llm_config.yaml | grep -A 10 "content_generation:"

# Check actual content metrics
grep "Word count" scripts/output/logs/*.log | head -10
```

**Solutions**:
1. **Adjust validation criteria** in `llm_config.yaml`:
   ```yaml
   content_generation:
     lecture:
       min_word_count: 800  # Lower if consistently too strict
       max_word_count: 2000  # Raise if consistently too low
   ```

2. **Review prompt templates**: Guide LLM toward compliant output
3. **Accept if quality good**: Validation is conservative, warnings may be acceptable

### Issue: "Questions not detected"

**Symptoms**: Validation shows 0 questions detected

**Diagnosis**:
```bash
# Check question format in generated content
grep "Question" output/modules/*/session_*/questions.md | head -5

# Check validation logs
grep "No questions detected" scripts/output/logs/*.log
```

**Solutions**:
1. **Verify question format**: Should be `**Question 1:**` (colon inside bold)
2. **Check generated content**: Review actual question format
3. **Regenerate**: LLM may have used different format
4. **Manually fix**: Edit questions.md to match expected format

## Performance Issues

### Issue: "Generation is very slow"

**Symptoms**: Content generation takes much longer than expected

**Diagnosis**:
```bash
# Check generation times in logs
grep "Generation complete" scripts/output/logs/*.log | tail -10

# Check system resources
top
df -h
```

**Solutions**:
1. **Check model size**: Larger models are slower
2. **Check system resources**: CPU/memory may be constrained
3. **Reduce content length**: Lower `num_predict` in LLM config
4. **Use smaller model**: Consider smaller model for faster generation

### Issue: "Out of memory"

**Symptoms**: System runs out of memory during generation

**Solutions**:
1. **Use smaller model**: Switch to smaller LLM model
2. **Reduce batch size**: Process fewer modules at once
3. **Increase system memory**: Add more RAM if possible
4. **Close other applications**: Free up memory

## Debugging Techniques

### Enable Debug Logging

```bash
# Run with DEBUG level
uv run python3 scripts/04_generate_primary.py --log-level DEBUG

# Or set environment variable
LOG_LEVEL=DEBUG uv run python3 scripts/04_generate_primary.py
```

### Analyze Logs

```bash
# Find all errors
grep "ERROR" scripts/output/logs/*.log

# Find validation warnings
grep "NEEDS REVIEW" scripts/output/logs/*.log

# Find slow operations
grep "Generation complete" scripts/output/logs/*.log | grep -E "[0-9]{3,}\.[0-9]+s"

# Count successful vs failed
grep "completed\|Failed" scripts/output/logs/*.log | wc -l
```

### Test Individual Components

```python
# Test configuration loading
from src.config.loader import ConfigLoader
config = ConfigLoader("config")
config.validate_all_configs()

# Test LLM connection
from src.llm.client import OllamaClient
llm = OllamaClient(config.get_llm_parameters())
result = llm.generate("Test prompt", params={"num_predict": 10})

# Test outline loading
modules = config.load_outline_from_json("output/outlines/course_outline.json")
print(f"Loaded {len(modules)} modules")
```

## Recovery Procedures

### Recover from Partial Failure

**Scenario**: Some modules generated, others failed

**Procedure**:
1. **Identify failed modules**: Check logs for errors
2. **Regenerate failed modules only**:
   ```bash
   uv run python3 scripts/04_generate_primary.py --modules <failed_ids>
   ```
3. **Verify all modules complete**: Check output directories
4. **Continue with Stage 05**: Generate secondary materials

### Recover from Corrupted Outline

**Scenario**: JSON outline is corrupted or invalid

**Procedure**:
1. **Backup corrupted outline**: `cp outline.json outline.json.backup`
2. **Regenerate outline**: `uv run python3 scripts/03_generate_outline.py`
3. **Verify new outline**: Check JSON structure
4. **Regenerate content**: Run Stage 04 with new outline

### Recover from LLM Failure

**Scenario**: LLM service unavailable during generation

**Procedure**:
1. **Restart Ollama**: `pkill ollama && ollama serve`
2. **Verify service**: `curl http://localhost:11434/api/version`
3. **Resume generation**: Run Stage 04 again (will skip existing content)
4. **Check partial results**: Review what was generated before failure

## Prevention Strategies

### Configuration Validation

**Always validate before running**:
```bash
uv run python3 scripts/01_setup_environment.py
uv run python3 scripts/02_run_tests.py
```

### Regular Backups

**Backup generated content**:
```bash
# Backup outline
cp output/outlines/course_outline_*.json backups/

# Backup generated content
tar -czf backups/content_$(date +%Y%m%d).tar.gz output/modules/
```

### Incremental Generation

**Generate modules incrementally**:
```bash
# Generate one module at a time
uv run python3 scripts/04_generate_primary.py --modules 1
# Review, then continue
uv run python3 scripts/04_generate_primary.py --modules 2
```

### Monitor Progress

**Watch logs during generation**:
```bash
# Follow log file
tail -f scripts/output/logs/04_generate_primary_*.log

# Or watch for errors
tail -f scripts/output/logs/04_generate_primary_*.log | grep -E "ERROR|Failed"
```

## Related Documentation

- **[ERROR_HANDLING.md](ERROR_HANDLING.md)** - Error handling patterns and exception hierarchy
- **[LOGGING.md](LOGGING.md)** - Logging patterns and log analysis
- **[VALIDATION.md](VALIDATION.md)** - Content validation troubleshooting
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration troubleshooting
- **[JSON_OUTLINE.md](JSON_OUTLINE.md)** - Outline troubleshooting
- **[PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)** - Pipeline-specific troubleshooting

## Summary

Troubleshooting follows a systematic approach:

1. **Identify category**: Configuration, LLM, Generation, File I/O, Import
2. **Check logs**: Review error messages and context
3. **Verify prerequisites**: Environment, Ollama, configs
4. **Apply solution**: Follow specific solution patterns
5. **Prevent recurrence**: Use validation and monitoring

Most issues can be resolved by:
- Validating configuration
- Ensuring Ollama is running
- Checking file permissions
- Reviewing logs for specific errors
- Regenerating content if needed

The system is designed to fail gracefully and provide clear error messages to help diagnose and resolve issues quickly.






