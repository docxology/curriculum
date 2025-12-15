# Ollama Health Monitoring

Guide to using health monitoring features for Ollama client requests.

## Overview

The health monitoring system provides:
- Service availability checking
- Model status monitoring
- Request health tracking
- Comprehensive diagnostics
- Troubleshooting suggestions

## Quick Start

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

# Check if Ollama is running
status = monitor.check_service_status()
if status["available"]:
    print(f"Ollama is running (version: {status['version']})")
else:
    print(f"Ollama is not available: {status['error']}")
```

## Service Status Checking

### Basic Status Check

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()
status = monitor.check_service_status()

print(f"Available: {status['available']}")
print(f"Response time: {status['response_time']:.3f}s")
print(f"Version: {status.get('version', 'unknown')}")
```

### Status Check with Timeout

```python
# Custom timeout for health check
status = monitor.check_service_status(timeout=10)
```

**Response Structure**:
```python
{
    "available": True,           # bool - Service is reachable
    "response_time": 0.003,      # float - Response time in seconds
    "version": "0.13.2",         # str - Ollama version
    "error": None                 # Optional[str] - Error message if unavailable
}
```

## Model Status Checking

### Check if Model is Loaded

```python
monitor = OllamaHealthMonitor()
model_status = monitor.check_model_status("gemma3:4b")

print(f"Loaded: {model_status['loaded']}")
print(f"Available: {model_status['available']}")
print(f"Processor: {model_status.get('processor')}")
```

**Response Structure**:
```python
{
    "loaded": True,               # bool - Model is currently loaded in memory
    "available": True,            # bool - Model exists (may not be loaded)
    "processor": "100% GPU",      # Optional[str] - Processor info
    "size": None                  # Optional[str] - Model size if loaded
}
```

### Monitor Model During Request

```python
import time

monitor = OllamaHealthMonitor()
start_time = time.time()

# During long request, check model status
health_status = monitor.monitor_request_health(
    request_id="req-123",
    model="gemma3:4b",
    start_time=start_time,
    timeout=240,
    check_interval=10
)

if health_status:
    print(f"Issue detected: {health_status['issue']}")
    print(f"Details: {health_status['details']}")
```

## Comprehensive Diagnostics

### Get Full Diagnostics

```python
monitor = OllamaHealthMonitor()
diagnostics = monitor.get_diagnostics()

print("Service Status:", diagnostics["service_status"])
print("GPU Info:", diagnostics["gpu_info"])
print("Available Models:", diagnostics["models_available"])
```

**Response Structure**:
```python
{
    "service_status": {
        "available": True,
        "response_time": 0.003,
        "version": "0.13.2",
        "error": None
    },
    "gpu_info": {
        "using_gpu": True,
        "processor_info": "100% GPU",
        "models_loaded": ["gemma3:4b"],
        "details": [
            {"model": "gemma3:4b", "processor": "100% GPU"}
        ]
    },
    "models_available": ["gemma3:4b", "llama3:8b"],
    "timestamp": 1234567890.123
}
```

## Troubleshooting Suggestions

### Get Suggestions for Specific Error Types

```python
monitor = OllamaHealthMonitor()
diagnostics = monitor.get_diagnostics()

# Get suggestions for timeout errors
suggestions = monitor.get_troubleshooting_suggestions(
    diagnostics,
    error_type="timeout"
)

for suggestion in suggestions:
    print(f"  - {suggestion}")
```

**Error Types**:
- `"timeout"` - Request timeout issues
- `"connection"` - Connection problems
- `None` - General suggestions

**Example Output**:
```
  - Request timed out. Consider:
  - Increasing timeout in config/llm_config.yaml
  - Using a faster/smaller model
  - Reducing num_predict parameter
  - Checking system resources (CPU/memory)
```

## Integration with Request Handler

The request handler automatically uses health monitoring:

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

# Health monitoring happens automatically
response = handler.execute_with_monitoring(
    request_func=make_request,
    timeout=30,
    request_id="req-123",
    model="gemma3:4b"
)
```

## Health Check Intervals

### During Long Requests

Health checks are performed automatically during long requests:

```python
# Health checks every 10 seconds by default
handler = RequestHandler(health_check_interval=10)

# Custom interval
handler = RequestHandler(health_check_interval=5)  # Check every 5 seconds
```

### Manual Health Monitoring

```python
import time

monitor = OllamaHealthMonitor()
start_time = time.time()
timeout = 240

while True:
    elapsed = time.time() - start_time
    if elapsed > timeout:
        break
    
    # Check health
    health_status = monitor.monitor_request_health(
        request_id="req-123",
        model="gemma3:4b",
        start_time=start_time,
        timeout=timeout,
        check_interval=10
    )
    
    if health_status:
        issue = health_status["issue"]
        if issue == "service_unavailable":
            print("Critical: Service became unavailable!")
            break
        elif issue == "model_not_loaded":
            print("Warning: Model not loaded")
        elif issue == "slow_response":
            print("Warning: Service is slow")
    
    time.sleep(10)
```

## Health Status Issues

### Service Unavailable

**Issue**: `"service_unavailable"`

**Detection**: Ollama service becomes unreachable during request

**Response**:
```python
{
    "issue": "service_unavailable",
    "elapsed": 45.2,
    "details": {
        "available": False,
        "error": "Connection refused"
    }
}
```

### Model Not Loaded

**Issue**: `"model_not_loaded"`

**Detection**: Model should be loaded but isn't after significant time

**Response**:
```python
{
    "issue": "model_not_loaded",
    "elapsed": 120.5,
    "details": {
        "loaded": False,
        "available": True,
        "processor": None
    }
}
```

### Slow Response

**Issue**: `"slow_response"`

**Detection**: Ollama responds but very slowly

**Response**:
```python
{
    "issue": "slow_response",
    "elapsed": 60.3,
    "details": {
        "available": True,
        "response_time": 3.5,  # > 2.0 seconds
        "version": "0.13.2"
    }
}
```

## Best Practices

### Pre-Request Health Check

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

# Check before making request
status = monitor.check_service_status()
if not status["available"]:
    raise RuntimeError("Ollama service is not available")

# Check model
model_status = monitor.check_model_status("gemma3:4b")
if not model_status["available"]:
    raise RuntimeError("Model is not available")
```

### Periodic Health Monitoring

```python
import time
import threading

def monitor_health_periodically(monitor, model, interval=30):
    """Monitor health in background thread."""
    while True:
        diagnostics = monitor.get_diagnostics()
        if not diagnostics["service_status"]["available"]:
            print("Warning: Ollama service unavailable")
        time.sleep(interval)

# Start monitoring thread
monitor = OllamaHealthMonitor()
thread = threading.Thread(
    target=monitor_health_periodically,
    args=(monitor, "gemma3:4b"),
    daemon=True
)
thread.start()
```

### Error Recovery

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

try:
    # Make request
    result = client.generate(prompt)
except LLMError as e:
    # Get diagnostics
    diagnostics = monitor.get_diagnostics()
    
    # Get suggestions
    suggestions = monitor.get_troubleshooting_suggestions(
        diagnostics,
        error_type="timeout"
    )
    
    # Log suggestions
    for suggestion in suggestions:
        logger.info(f"  - {suggestion}")
    
    raise
```

## API Reference

### OllamaHealthMonitor

**Methods**:
- `check_service_status(timeout=5) -> Dict[str, Any]`
- `check_model_status(model: str) -> Dict[str, Any]`
- `get_diagnostics() -> Dict[str, Any]`
- `monitor_request_health(request_id, model, start_time, timeout, check_interval) -> Optional[Dict]`
- `get_troubleshooting_suggestions(diagnostics, error_type=None) -> List[str]`

## See Also

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Comprehensive troubleshooting guide
- [AGENTS.md](AGENTS.md) - Complete API reference
- [README.md](README.md) - User guide
