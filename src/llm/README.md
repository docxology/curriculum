# LLM Integration

Ollama API client for text generation.

## Files

- `client.py` - `OllamaClient` class for Ollama API integration

## Overview

This module provides a lightweight client for interacting with local Ollama LLM instances. It handles HTTP communication, streaming responses, automatic retries, and error management.

## Key Features

- **Streaming responses** for better responsiveness
- **Automatic retries** with exponential backoff
- **Template formatting** with variable substitution
- **Error handling** with custom exceptions
- **Comprehensive logging** at all levels
- **Request ID tracing** for debugging and monitoring
- **Stream timeout tracking** (separate from connection timeout)
- **Progress logging** during long generations
- **Health monitoring** - Automatic health checks and diagnostics
- **Request handler** - Non-blocking requests with timeout monitoring
- **Troubleshooting tools** - Comprehensive diagnostics and suggestions

## Usage

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient, LLMError

# Initialize from configuration
loader = ConfigLoader("config")
llm_config = loader.get_llm_parameters()
client = OllamaClient(llm_config)

# Generate text
try:
    response = client.generate(
        prompt="Explain photosynthesis",
        system_prompt="You are a {subject} educator"
    )
    print(response)
except LLMError as e:
    print(f"Error: {e}")

# Use templates
template = "Write about {topic} covering {aspects}"
response = client.generate_with_template(
    template=template,
    variables={"topic": "cells", "aspects": "structure and function"}
)
```

## OllamaClient Class

### Constructor
```python
OllamaClient(config, max_retries=3, retry_delay=1.0)
```

**Parameters**:
- `config` - LLM configuration dict with model, api_url, timeout, parameters
- `max_retries` - Maximum retry attempts (default: 3)
- `retry_delay` - Initial retry delay in seconds (default: 1.0)

### Methods

**generate(prompt, system_prompt=None, params=None)**
Generate text from prompt.

**format_prompt(template, variables)**
Format template with variable substitution.

**generate_with_template(template, variables, system_prompt=None, params=None)**
Generate text using formatted template.

## Request Tracing

Each LLM request is assigned a unique 8-character request ID that appears in all related log messages. This makes it easy to trace a specific request through the logs:

```
INFO: [a1b2c3d4] LLM Request: model=gemma3:4b, timeout=120s
INFO: [a1b2c3d4] Prompt length: 523 chars, system_prompt: 45 chars
INFO: [a1b2c3d4] Stream progress: 5.2s elapsed, 42 chunks, 1234 chars (237.3 chars/s)
INFO: [a1b2c3d4] Generation complete: 2847 chars (~569 words) in 12.5s (227.8 chars/s)
```

Use the request ID to filter logs and trace specific requests when debugging issues.

## Error Handling

Custom `LLMError` exception raised for:
- Connection errors (Ollama not reachable)
- Timeout errors (generation too slow)
- HTTP errors (API errors)
- Response parsing errors
- Template formatting errors

All error messages include:
- **Request ID** for tracing: `[a1b2c3d4]`
- **Elapsed time** when error occurred
- **Diagnostic information** (chunks received, bytes, characters)
- **Troubleshooting suggestions** (check Ollama status, increase timeout, etc.)

Example error messages:
```
[a1b2c3d4] Connection error after 0.5s: Connection refused. Check if Ollama is running: curl http://localhost:11434/api/version

[a1b2c3d4] Request timeout after 120.3s (limit: 120s): Read timed out. Consider increasing timeout in config or using a faster model.

[a1b2c3d4] Stream timeout: 180.5s elapsed (limit: 180.0s). Received 15 chunks, 2048 bytes, 512 chars before timeout. Stream may be stuck or model is too slow.
```

## Retry Behavior

Automatic retry with exponential backoff:
- **Retry on**: ConnectionError, Timeout
- **Don't retry**: HTTPError, other exceptions
- **Backoff**: 1s, 2s, 4s (exponential)

Each retry attempt is logged with the request ID:
```
WARNING: [a1b2c3d4] Connection error (attempt 1/4, elapsed: 0.5s): Connection refused
INFO: [a1b2c3d4] Retrying in 1.0s...
```

## Stream Timeout Handling

The client tracks two types of timeouts:

1. **Connection timeout**: Time to establish HTTP connection (configured via `timeout` parameter)
2. **Stream timeout**: Time to read complete stream response (automatically set to `timeout * 1.5`)

If a stream takes longer than `timeout * 1.5` seconds, it will timeout with detailed diagnostic information:
- Chunks received before timeout
- Bytes received
- Characters generated
- Elapsed time

Progress is logged every 5 seconds during long streams to help identify stuck or slow generations.

## Configuration

Expected config structure:
```python
{
    "model": "gemma3:4b",
    "api_url": "http://localhost:11434/api/generate",
    "timeout": 120,
    "parameters": {
        "temperature": 0.7,
        "top_p": 0.9
    }
}
```

## Integration

Used by all content generators:
- `LectureGenerator`
- `LabGenerator`
- `StudyNotesGenerator`
- `DiagramGenerator`
- `QuestionGenerator`

## Testing

Tests in `tests/test_llm_client.py` (requires Ollama + gemma3:4b):
```bash
uv run pytest tests/test_llm_client.py -v
```

## Health Monitoring

The module includes comprehensive health monitoring:

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

# Check service status
status = monitor.check_service_status()
if status["available"]:
    print(f"Ollama is running (version: {status['version']})")

# Get diagnostics
diagnostics = monitor.get_diagnostics()
print(f"GPU usage: {diagnostics['gpu_info']['processor_info']}")
print(f"Models loaded: {diagnostics['gpu_info']['models_loaded']}")

# Get troubleshooting suggestions
suggestions = monitor.get_troubleshooting_suggestions(diagnostics, "timeout")
```

See [HEALTH_MONITORING.md](HEALTH_MONITORING.md) for complete guide.

## Troubleshooting

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

**Quick fixes**:

**"Connection error"**:
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# Start Ollama
ollama serve
```

**"Request timeout"**:
- Increase timeout in `llm_config.yaml`
- Use faster model
- Reduce content length
- Check system resources

**"Request hangs"**:
- Check Ollama service: `curl http://localhost:11434/api/version`
- Check model status: `ollama ps`
- Restart Ollama: `pkill ollama && ollama serve`
- Use health monitoring to diagnose

**"Stream timeout"**:
- Stream timeout is `timeout * 1.5` (e.g., 180s for 120s timeout)
- Check progress logs to see if stream is making progress
- If stream is stuck, check Ollama service status
- Consider using a faster model or reducing `num_predict` parameter

**Using request IDs for debugging**:
```bash
# Filter logs by request ID
grep "\[a1b2c3d4\]" output/logs/*.log

# Find all error messages for a specific request
grep "\[a1b2c3d4\].*ERROR" output/logs/*.log
```

## See Also

- **For AI Agents**: [AGENTS.md](AGENTS.md) - Complete API reference
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Comprehensive troubleshooting guide
- **Health Monitoring**: [HEALTH_MONITORING.md](HEALTH_MONITORING.md) - Health monitoring guide
- **Configuration**: [../../config/README.md](../../config/README.md)
- **Ollama Setup**: [../../SETUP.md](../../SETUP.md)


