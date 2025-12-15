# LLM Integration Module

Ollama API client for text generation with retry logic, health monitoring, and comprehensive error handling.

## Module Purpose

Provides `OllamaClient` class for interacting with local Ollama LLM instances. Handles request formatting, streaming responses, retries, error management, and health monitoring.

## Module Structure

- `client.py` - Main OllamaClient class
- `health.py` - Health monitoring and diagnostics (NEW)
- `request_handler.py` - Request handling with timeout monitoring (NEW)
- `TROUBLESHOOTING.md` - Comprehensive troubleshooting guide (NEW)
- `HEALTH_MONITORING.md` - Health monitoring documentation (NEW)

## Key Class: OllamaClient

```python
from src.llm.client import OllamaClient, LLMError
```

### Initialization

```python
# From configuration
from src.config.loader import ConfigLoader

loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# With custom retry settings
client = OllamaClient(
    llm_config,
    max_retries=3,
    retry_delay=1.0
)

# Config structure:
# {
#     "model": "gemma3:4b",
#     "api_url": "http://localhost:11434/api/generate",
#     "timeout": 120,
#     "parameters": {
#         "temperature": 0.7,
#         "top_p": 0.9
#     }
# }
```

### Basic Text Generation

```python
# Simple generation
response = client.generate(
    prompt="Explain photosynthesis in 100 words",
    system_prompt="You are a {subject} educator"
)

# With custom parameters
response = client.generate(
    prompt="Describe cell division",
    system_prompt="You are an expert biologist",
    params={
        "temperature": 0.8,
        "num_predict": 500
    }
)
```

### Template-Based Generation

```python
# Format prompt with template
template = "Generate a {content_type} about {topic} covering {aspects}"
variables = {
    "content_type": "lecture",
    "topic": "DNA replication",
    "aspects": "enzymes and process steps"
}

formatted_prompt = client.format_prompt(template, variables)

# Generate with template directly
response = client.generate_with_template(
    template=template,
    variables=variables,
    system_prompt="You are a {subject} educator"
)

# Override timeout for specific operation
response = client.generate_with_template(
    template=template,
    variables=variables,
    system_prompt="You are a {subject} educator",
    timeout_override=300  # 5 minutes for complex generation
)

# Or use operation-specific timeout from config
from src.config.loader import ConfigLoader
loader = ConfigLoader("config")
operation_timeout = loader.get_operation_timeout("outline")  # Get timeout for "outline" operation
response = client.generate_with_template(
    template=template,
    variables=variables,
    timeout_override=operation_timeout
)
```

### Using Configuration Templates

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient

# Load configuration
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# Get prompt template from config
lecture_template = loader.get_prompt_template("lecture")
system_prompt = lecture_template["system"]
template = lecture_template["template"]

# Generate with config template
module = {
    "name": "Cell Biology",
    "subtopics": "- Organelles\n- Membranes",
    "objectives": "- Understand cell structure",
    "content_length": "2500"
}

lecture_content = client.generate_with_template(
    template=template,
    variables={
        "module_name": module["name"],
        "subtopics": module["subtopics"],
        "objectives": module["objectives"],
        "content_length": module["content_length"]
    },
    system_prompt=system_prompt
)
```

## Retry Logic

Automatic retries for transient errors:

```python
client = OllamaClient(
    llm_config,
    max_retries=3,      # Total attempts = max_retries + 1
    retry_delay=1.0     # Exponential backoff: 1s, 2s, 4s
)

# Retries automatically on:
# - requests.ConnectionError (Ollama not reachable)
# - requests.Timeout (generation timeout)
# 
# Does NOT retry on:
# - requests.HTTPError (4xx/5xx errors)
# - Other exceptions
```

## Request Tracing and Logging

Each LLM request is assigned a unique request ID with operation abbreviation that appears in all related log messages. This enables easy tracing of specific requests through logs:

```python
# All log messages include request ID in format [op:uuid] (e.g., [lec:56e7ab])
# Example logs (compact format with emojis):
# INFO: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=3257c
# INFO: [lec:56e7ab] ✅ HTTP 200 in 1.93s
# INFO: [lec:56e7ab] 📡 Stream active (200)
# INFO: [lec:56e7ab] 📊 2.0s: 414c @206c/s (68ch, ~104t @52t/s)
# INFO: [lec:56e7ab] ✓ Done 20.03s: 3202c (~800w @176c/s)

# Filter logs by request ID
import subprocess
subprocess.run(["grep", "\\[lec:56e7ab\\]", "output/logs/*.log"])
```

**Request ID Format**: `[operation_abbrev:6char_uuid]`
- Operation abbreviations: `out` (outline), `lec` (lecture), `lab`, `stu` (study_notes), `dia` (diagram), `qst` (questions), `app` (application), `ext` (extension), `viz` (visualization), `int` (integration), `inv` (investigation), `opq` (open_questions)
- UUID: 6-character hexadecimal (unique enough for session)

## Error Handling

### Complete Error Message Reference

All `LLMError` exceptions include:
- **Request ID**: `[lec:56e7ab]` - Unique identifier with operation abbreviation for tracing
- **Elapsed time**: Time spent before error occurred
- **Diagnostic info**: Chunks, bytes, characters received (for stream errors)
- **Troubleshooting suggestions**: Actionable guidance

#### Error Type 1: Connection Error

```python
LLMError("[lec:56e7ab] Connection error after 0.5s: Connection refused. Check if Ollama is running: curl http://localhost:11434/api/version")
```

**Causes**:
- Ollama service not running
- Wrong API URL
- Network connectivity issues

**Solutions**:
```bash
# Start Ollama
ollama serve

# Verify Ollama is running
curl http://localhost:11434/api/version

# Check API URL in config
# llm_config.yaml: api_url: "http://localhost:11434/api/generate"
```

#### Error Type 2: Request Timeout

```python
LLMError("[a1b2c3d4] Request timeout after 120.3s (limit: 120s): Read timed out. Consider increasing timeout in config or using a faster model.")
```

**Causes**:
- Model too slow for prompt length
- Network latency
- System resource constraints

**Solutions**:
- Increase timeout in `llm_config.yaml`: `timeout: 180`
- Use faster model (e.g., smaller model variant)
- Reduce prompt length
- Check system resources (CPU, memory)

#### Error Type 3: Stream Timeout

```python
LLMError("[a1b2c3d4] Stream timeout: 180.5s elapsed (limit: 180.0s). Received 15 chunks, 2048 bytes, 512 chars before timeout. Stream may be stuck or model is too slow.")
```

**Causes**:
- Stream stopped making progress
- Model generation stalled
- Network interruption during stream

**Solutions**:
- Check stream progress logs (should show increasing chunks/chars)
- Increase timeout (stream timeout = connection timeout * 1.5)
- Retry request (automatic retry handles transient issues)
- Check model status: `ollama ps`

#### Error Type 4: HTTP Error

```python
LLMError("[a1b2c3d4] HTTP error after 2.1s: 404 Not Found. Model 'invalid_model' not found. Pull model with: ollama pull gemma3:4b")
```

**Causes**:
- Model not available
- Invalid API endpoint
- Server error (5xx)

**Solutions**:
```bash
# Pull required model
ollama pull gemma3:4b

# List available models
ollama list

# Verify model name in config matches pulled model
```

#### Error Type 5: Unexpected Error

```python
LLMError("[a1b2c3d4] Unexpected error after 5.2s: JSON decode error: Expecting value: line 1 column 1 (char 0)")
```

**Causes**:
- Invalid JSON response from Ollama
- Malformed response format
- Unexpected API changes

**Solutions**:
- Check Ollama version: `ollama --version`
- Update Ollama: `ollama update`
- Check logs for full error details
- Report issue if persistent

### Error Handling Pattern

```python
from src.llm.client import LLMError
import logging

logger = logging.getLogger(__name__)

try:
    response = client.generate(prompt="Generate content")
except LLMError as e:
    error_msg = str(e)
    
    # Extract request ID for log filtering
    if "[" in error_msg and "]" in error_msg:
        request_id = error_msg[error_msg.find("[")+1:error_msg.find("]")]
        logger.error(f"LLM generation failed: {e}")
        logger.info(f"Request ID: {request_id} - filter logs: grep '[{request_id}]' output/logs/*.log")
    
    # Handle specific error types
    if "Connection error" in error_msg:
        logger.error("Ollama not running. Start with: ollama serve")
    elif "Request timeout" in error_msg:
        logger.warning("Timeout too short. Increase timeout in llm_config.yaml")
    elif "Stream timeout" in error_msg:
        logger.warning("Stream stalled. Check model performance or increase timeout")
    elif "HTTP error" in error_msg:
        logger.error("Check model availability: ollama list")
    else:
        logger.error(f"Unexpected error: {e}")
    
    raise  # Re-raise or handle appropriately
```

## Streaming Response Handling

The client uses streaming responses internally for better responsiveness:

```python
# Internally, the client:
# 1. Sends request with stream=True
# 2. Parses each line as JSON
# 3. Accumulates "response" fields
# 4. Returns complete text when "done" is True
# 5. Logs progress every 5 seconds during long streams
# 6. Tracks stream timeout (timeout * 1.5) separately from connection timeout

# This is transparent to the caller - you just get the final text
response = client.generate(prompt="...")

# Progress is automatically logged:
# INFO: [a1b2c3d4] Stream progress: 5.1s elapsed, 42 chunks, 1234 chars (242.0 chars/s)
# INFO: [a1b2c3d4] Stream progress: 10.2s elapsed, 85 chunks, 2567 chars (251.7 chars/s)
# INFO: [a1b2c3d4] Stream complete: 12.5s, 100 chunks, 3072 bytes, 2847 chars (227.8 chars/s)
```

## Stream Timeout Handling

The client uses **adaptive timeout extension** to handle slow but progressing generations:

### Timeout Types

1. **Connection timeout**: Time to establish HTTP connection (configured via `timeout` parameter)
2. **Stream timeout**: Time to read complete stream response
   - **Initial limit**: `base_timeout * 1.5` (e.g., 180s → 270s)
   - **Adaptive extension**: If stream is making progress, extends up to `base_timeout * 3.5` (e.g., 180s → 630s max)
   - **Stuck detection**: Streams without progress for 30s are detected early and fail fast

### Adaptive Timeout Behavior

```python
# Example: timeout=180s means:
# - Connection timeout: 180s
# - Initial stream timeout: 270s (180 * 1.5)
# - Maximum stream timeout: 630s (180 * 3.5) if making progress

# The system automatically extends timeout if:
# - Chunks are arriving regularly (within 15s)
# - Text is growing (progress detected every 5s)
# - Stream hasn't exceeded maximum extension limit

# Progress monitoring logs every 2s:
# INFO: [lecture-7c3f93fc] Stream: 2.0s | Chunks: 68 (33.9/s) | Text: 414 chars (~104 tokens, 51.6 tok/s) | Speed: 206.3 chars/s
# INFO: [lecture-7c3f93fc] Stream: 4.0s | Chunks: 136 (33.9/s) | Text: 820 chars (~205 tokens, 51.1 tok/s) | Speed: 204.6 chars/s
# INFO: [lecture-7c3f93fc] Stream making progress - extending timeout by 90.0s (new limit: 360.0s, max: 630.0s)
```

### Enhanced Timeout Error Messages

Timeout errors now include comprehensive diagnostic information:

```python
# Enhanced error message format:
LLMError(
    "[lecture-7c3f93fc] Stream timeout: 941.62s elapsed "
    "(limit: 360.00s, base timeout: 240.00s). "
    "Operation: lecture. "
    "Received 1427 chunks, 136439 bytes, 6649 chars (~1662 tokens) before timeout. "
    "Performance: 7.1 chars/s, ~1.8 tok/s. "
    "Very slow generation (7.1 chars/s). "
    "For lecture generation, consider: (1) Increasing timeout to 480s+, "
    "(2) Breaking into smaller sections, (3) Using a faster model. "
    "General solutions: (1) Increase timeout in config/llm_config.yaml, "
    "(2) Use a faster model, (3) Check system resources (CPU/memory/GPU), "
    "(4) See docs/TROUBLESHOOTING.md for detailed guidance."
)
```

**Error Message Components**:
- **Request ID**: `[operation-uuid]` for log filtering
- **Elapsed time**: Actual time spent vs timeout limit
- **Operation context**: Which operation timed out (lecture, outline, etc.)
- **Performance metrics**: Chunks, bytes, chars, tokens, speed (chars/s, tok/s)
- **Operation-specific recommendations**: Tailored advice based on operation type
- **General solutions**: Universal troubleshooting steps

### Operation-Specific Timeout Recommendations

The client provides operation-specific recommendations in timeout errors:

- **Outline generation**: Increase timeout to 600s+, use faster model, reduce prompt complexity
- **Lecture generation**: Increase timeout to 480s+, break into smaller sections, use faster model
- **Lab generation**: Increase timeout to 360s+, simplify procedures, use faster model
- **Secondary materials**: Increase timeout to 300s+, reduce examples/topics, use faster model

### Using Request IDs for Troubleshooting

All timeout errors include request IDs for traceability:

```bash
# Extract request ID from error
# Error: [lecture-7c3f93fc] Stream timeout...
REQUEST_ID="lecture-7c3f93fc"

# Filter logs by request ID
grep "[${REQUEST_ID}]" scripts/output/logs/*.log

# See performance progression
grep "[${REQUEST_ID}]" scripts/output/logs/*.log | grep "Stream:"

# See timeout extension events
grep "[${REQUEST_ID}]" scripts/output/logs/*.log | grep "extending timeout"
```

### Progress Monitoring

The client logs stream progress every 2 seconds (configurable):

```
INFO: [lecture-7c3f93fc] Stream: 2.0s | Chunks: 68 (33.9/s) | Text: 414 chars (~104 tokens, 51.6 tok/s) | Speed: 206.3 chars/s
INFO: [lecture-7c3f93fc] Stream: 4.0s | Chunks: 136 (33.9/s) | Text: 820 chars (~205 tokens, 51.1 tok/s) | Speed: 204.6 chars/s
INFO: [lecture-7c3f93fc] Stream: 6.0s | Chunks: 204 (33.9/s) | Text: 1264 chars (~316 tokens, 52.6 tok/s) | Speed: 210.3 chars/s
```

**Metrics Tracked**:
- **Elapsed time**: Time since stream started
- **Chunk count**: Number of chunks received and rate (chunks/s)
- **Text length**: Characters generated and estimated tokens
- **Token rate**: Estimated tokens per second
- **Character speed**: Characters per second

**Performance Indicators**:
- **Normal**: 50-200 chars/s, 10-50 tok/s
- **Slow but acceptable**: 20-50 chars/s, 5-10 tok/s
- **Very slow (may timeout)**: <10 chars/s, <2 tok/s

### Stuck Stream Detection

The client detects stuck streams early (no progress for 30s):

```
WARNING: [lecture-7c3f93fc] Stream appears stalled: no chunks for 30.5s 
         (received 1427 chunks, 6649 chars). 
         Stream may have completed without 'done' flag or may be stuck.
```

If no text is generated and stream is stalled, it fails fast:
```
ERROR: [lecture-7c3f93fc] Stream stuck: no progress for 30.1s 
       (received 1427 chunks but no text extracted). 
       Stream may be stuck. Consider increasing timeout or checking model status.
```

## Integration with Content Generators

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator

# Setup
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# Create generator
lecture_gen = LectureGenerator(loader, client)

# Generate content
module = loader.get_module_by_id(1)
lecture = lecture_gen.generate_lecture(module)
```

## Common Patterns

### Check Ollama Availability

```python
from src.utils.helpers import ollama_is_running

if not ollama_is_running():
    print("Ollama is not running. Start with: ollama serve")
    exit(1)

client = OllamaClient(llm_config)
```

### Generate with Validation

```python
def generate_with_validation(client, prompt, min_length=100):
    try:
        response = client.generate(prompt)
        
        if len(response) < min_length:
            logger.warning(f"Generated text too short: {len(response)} chars")
            
        return response
        
    except LLMError as e:
        logger.error(f"Generation failed: {e}")
        raise
```

### Batch Generation with Error Collection

```python
def generate_batch(client, prompts):
    results = []
    errors = []
    
    for i, prompt in enumerate(prompts):
        try:
            response = client.generate(prompt)
            results.append({"index": i, "content": response})
        except LLMError as e:
            errors.append({"index": i, "error": str(e)})
            
    return results, errors
```

## Configuration Parameters

**Model Selection**:
- `model`: Model name (e.g., "gemma3:4b", "llama3")
- Verify availability: `ollama list`

**API Settings**:
- `api_url`: Ollama endpoint (default: http://localhost:11434/api/generate)
- `timeout`: Base request timeout in seconds (default: 180)
- `operation_timeouts`: Optional operation-specific timeouts (e.g., `outline: 240`, `lecture: 180`)

**Generation Parameters**:
- `temperature`: Randomness (0.0-1.0, default: 0.7)
- `top_p`: Nucleus sampling (0.0-1.0, default: 0.9)
- `top_k`: Top-k sampling (default: 40)
- `num_predict`: Maximum tokens to generate (Ollama parameter, e.g., 100000 for comprehensive content)
- `num_ctx`: Context window size (e.g., 128000 for 128K context)

## Health Monitoring

The module includes comprehensive health monitoring capabilities:

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

# Check service status
status = monitor.check_service_status()
print(f"Available: {status['available']}, Version: {status.get('version')}")

# Check model status
model_status = monitor.check_model_status("gemma3:4b")
print(f"Loaded: {model_status['loaded']}, Available: {model_status['available']}")

# Get comprehensive diagnostics
diagnostics = monitor.get_diagnostics()

# Get troubleshooting suggestions
suggestions = monitor.get_troubleshooting_suggestions(diagnostics, "timeout")
```

**Features**:
- Service availability checking
- Model status monitoring
- Request health tracking during long operations
- Automatic diagnostics collection
- Troubleshooting suggestions based on error type

See [HEALTH_MONITORING.md](HEALTH_MONITORING.md) for complete guide.

## Request Handler

The request handler provides non-blocking request execution with monitoring:

```python
from src.llm.request_handler import RequestHandler
import requests

handler = RequestHandler()

def make_request():
    return requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "gemma3:4b", "prompt": "test"},
        timeout=(5, 30),
        stream=True
    )

# Execute with automatic health monitoring
response = handler.execute_with_monitoring(
    request_func=make_request,
    timeout=30,
    request_id="req-123",
    model="gemma3:4b"
)
```

**Features**:
- Thread-based timeout monitoring
- Periodic health checks during requests
- Heartbeat logging for long requests
- Request cancellation support
- Better error detection and reporting

The `OllamaClient` automatically uses the request handler for all requests.

## Testing

Tests in `tests/test_llm_client.py`:
- Connection and initialization
- Text generation
- Template formatting
- Error handling
- Retry logic
- **NEW**: Hanging request scenarios
- **NEW**: Comprehensive timeout testing
- **NEW**: Health monitoring functionality
- **NEW**: Request handler with monitoring
- **NEW**: Ollama unavailable scenarios
- **NEW**: Streaming issues

**Requires Ollama + gemma3:4b model**

Run tests:
```bash
uv run pytest tests/test_llm_client.py -v
```

## Performance Characteristics

### Generation Speed

Typical generation speeds (varies by model and hardware):

| Model | Speed | Use Case |
|-------|-------|----------|
| `gemma3:4b` | ~200-300 chars/s | Fast generation, good quality, large context |
| `llama3:8b` | ~150-250 chars/s | Higher quality, slower |
| `mistral:7b` | ~180-280 chars/s | Balanced quality/speed |

**Factors affecting speed**:
- Model size (larger = slower)
- Prompt length (longer = slower)
- System resources (CPU, RAM, GPU)
- Network latency (if remote Ollama)

### Timeout Guidelines

**Base Timeout**: 180 seconds (configured in `config/llm_config.yaml`)

**Operation-Specific Timeouts** (recommended):

| Content Type | Recommended Timeout | Reason |
|--------------|---------------------|--------|
| Outline generation | 240s | Complex JSON output, large structured data |
| Lecture generation | 180s | Standard timeout for comprehensive content |
| Lab generation | 150s | Moderate complexity, structured format |
| Study notes | 120s | Shorter content, concise format |
| Diagram generation | 120s | Mermaid syntax, typically shorter output |
| Question generation | 150s | Multiple questions with explanations |
| Default (other operations) | 180s | Base timeout for unspecified operations |

**Configuration Example**:
```yaml
llm:
  timeout: 180  # Base timeout
  operation_timeouts:
    outline: 240
    lecture: 180
    lab: 150
    study_notes: 120
    diagram: 120
    questions: 150
    default: 180
```

**Timeout Override**: You can also override timeout programmatically:
```python
client.generate(prompt, timeout_override=300)  # 5 minutes for specific request
```

**Stream timeout**: Automatically set to `connection_timeout * 1.5` initially, with adaptive extension up to `connection_timeout * 3.5` when stream is making progress. Early detection of stuck streams (30s without progress).

**Model-Specific Guidelines**:
- Small models (4B): 120-180 seconds base
- Medium models (8B): 180-240 seconds base  
- Large models (13B+): 240-480 seconds base

### Retry Behavior

- **Max retries**: 3 (total 4 attempts)
- **Backoff strategy**: Exponential (1s, 2s, 4s delays)
- **Retries on**: Connection errors, timeouts
- **No retry on**: HTTP errors (4xx/5xx), invalid responses

### Memory Usage

- **Client overhead**: Minimal (~1-2 MB)
- **Streaming buffer**: Accumulates response in memory
- **Large responses**: Can use 10-50 MB for 10K+ character responses

### Performance Optimization Tips

1. **Use appropriate model size**: Smaller models for faster generation
2. **Optimize prompts**: Shorter prompts = faster generation
3. **Batch requests**: Process multiple items sequentially (not parallel)
4. **Monitor timeouts**: Adjust based on actual generation times
5. **Check system resources**: Ensure adequate CPU/RAM for model

### Performance Considerations

- **Streaming**: Responses stream incrementally for better UX and early feedback
- **Caching**: No caching - each generation is fresh (ensures up-to-date content)
- **Timeout**: Default 120s, adjust for longer content or slower models
- **Retries**: 3 attempts with exponential backoff for resilience against transient failures
- **Request tracing**: Request IDs enable performance analysis via log filtering

## Logging

Comprehensive logging at all levels with request ID tracing:
- **DEBUG**: Prompt previews, template details, generation parameters
- **INFO**: Request start, progress updates, successful completions, statistics
- **WARNING**: Retry attempts, recoverable errors, JSON parse warnings
- **ERROR**: Fatal errors, exceptions with full diagnostic information

Example logs with request ID tracing:
```
INFO: Initialized OllamaClient: model=gemma3:4b, url=http://localhost:11434/api/generate
INFO: [a1b2c3d4] LLM Request: model=gemma3:4b, timeout=120s
INFO: [a1b2c3d4] Prompt length: 523 chars, system_prompt: 45 chars
DEBUG: [a1b2c3d4] Prompt preview: Explain photosynthesis in detail...
DEBUG: [a1b2c3d4] Generation parameters: {'temperature': 0.7, 'top_p': 0.9}
INFO: [a1b2c3d4] Attempt 1/4: Sending request to http://localhost:11434/api/generate
INFO: [a1b2c3d4] Response status: 200
INFO: [a1b2c3d4] Starting stream parsing (timeout: 120s)
INFO: [a1b2c3d4] Stream progress: 5.2s elapsed, 42 chunks, 1234 chars (237.3 chars/s)
INFO: [a1b2c3d4] Stream complete: 12.5s, 100 chunks, 3072 bytes, 2847 chars (227.8 chars/s)
INFO: [a1b2c3d4] Generation complete: 2847 chars (~569 words) in 12.5s (227.8 chars/s)
```

Error logs with diagnostic information:
```
WARNING: [a1b2c3d4] Connection error (attempt 1/4, elapsed: 0.5s): Connection refused
INFO: [a1b2c3d4] Retrying in 1.0s...
ERROR: [a1b2c3d4] Connection error after 2.5s: Connection refused. Check if Ollama is running: curl http://localhost:11434/api/version

ERROR: [a1b2c3d4] Request timeout after 120.3s (limit: 120s): Read timed out. Consider increasing timeout in config or using a faster model.

ERROR: [a1b2c3d4] Stream timeout: 180.5s elapsed (limit: 180.0s). Received 15 chunks, 2048 bytes, 512 chars before timeout. Stream may be stuck or model is too slow.
```

## Troubleshooting Quick Reference

### Common Issues and Solutions

**Connection Errors**:
```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
ollama serve
```

**Timeout Errors**:
```yaml
# Increase timeout in config/llm_config.yaml
llm:
  timeout: 300  # Increase base timeout
  operation_timeouts:
    outline: 600  # Operation-specific timeout
    lecture: 480
```

**Very Slow Generation**:
- Check GPU acceleration: `ollama ps`
- Restart Ollama: `pkill ollama && ollama serve`
- Use faster model or check system resources

**Using Request IDs**:
```bash
# Extract request ID from error: [lecture-7c3f93fc]
REQUEST_ID="lecture-7c3f93fc"

# Filter logs by request ID
grep "[${REQUEST_ID}]" scripts/output/logs/*.log

# See performance metrics
grep "[${REQUEST_ID}]" scripts/output/logs/*.log | grep "Stream:"
```

### Timeout Configuration Guidelines

**By Operation Type**:
- Outline: 480-600s (complex JSON)
- Lecture: 360-480s (comprehensive content)
- Lab: 300-360s (detailed procedures)
- Secondary materials: 300s (applications, extensions, etc.)
- Questions: 240-300s (assessment questions)
- Diagrams: 180-240s (Mermaid diagrams)

**By Model Size**:
- Small (4B): 180-300s base
- Medium (8B): 300-480s base
- Large (13B+): 480-900s base

### Performance Expectations

- **Normal**: 50-200 chars/s, 10-50 tok/s
- **Slow but acceptable**: 20-50 chars/s, 5-10 tok/s
- **Very slow (may timeout)**: <10 chars/s, <2 tok/s

For comprehensive troubleshooting, see:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Complete troubleshooting guide with detailed examples
- [HEALTH_MONITORING.md](HEALTH_MONITORING.md) - Health monitoring guide

**Common Issues**:
- **Request hangs**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#issue-request-hangs-indefinitely)
- **Connection timeout**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#issue-connection-timeout)
- **Read timeout**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#issue-read-timeout)
- **Stream timeout**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#issue-stream-timeout)

## See Also

- **For Humans**: [README.md](README.md) - Human-readable guide with examples
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Comprehensive troubleshooting guide
- **Health Monitoring**: [HEALTH_MONITORING.md](HEALTH_MONITORING.md) - Health monitoring guide
- **Configuration**: [../config/AGENTS.md](../config/AGENTS.md)
- **Content Generators**: [../generate/formats/AGENTS.md](../generate/formats/AGENTS.md)
- **API Reference**: [../../docs/API.md](../../docs/API.md)


