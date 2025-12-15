# Ollama Client Troubleshooting Guide

Comprehensive troubleshooting guide for Ollama client issues, including hanging requests, timeouts, and connection problems.

## Common Issues

### Issue: Request Hangs Indefinitely

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

# Check system resources
# On macOS:
top -l 1 | grep -i ollama
```

**Solutions**:

1. **Restart Ollama Service**:
   ```bash
   pkill ollama
   ollama serve
   ```

2. **Check Model Status**:
   ```bash
   # List available models
   ollama list
   
   # Check if model is loaded
   ollama ps
   
   # Pull model if missing
   ollama pull gemma3:4b
   ```

3. **Increase Timeout**:
   Edit `config/llm_config.yaml`:
   ```yaml
   llm:
     timeout: 300  # Increase from default 180
     operation_timeouts:
       outline: 480  # Increase for complex operations
   ```

4. **Use Health Monitoring**:
   ```python
   from src.llm.health import OllamaHealthMonitor
   
   monitor = OllamaHealthMonitor()
   diagnostics = monitor.get_diagnostics()
   print(diagnostics)
   ```

5. **Check System Resources**:
   - Ensure adequate CPU and memory
   - Close other resource-intensive applications
   - Check disk space

### Issue: Connection Timeout

**Symptoms**:
- Error: "Connection timeout after X seconds"
- Error: "Ollama service unreachable"

**Diagnosis**:
```bash
# Test Ollama connectivity
curl http://localhost:11434/api/version

# Check if port is open
# On macOS:
lsof -i :11434

# Check firewall settings
```

**Solutions**:

1. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

2. **Check API URL**:
   Verify `api_url` in `config/llm_config.yaml`:
   ```yaml
   llm:
     api_url: "http://localhost:11434/api/generate"
   ```

3. **Check Network**:
   - Verify localhost connectivity
   - Check firewall rules
   - Test with curl directly

4. **Check Ollama Version**:
   ```bash
   ollama --version
   # Update if needed
   brew upgrade ollama  # macOS
   ```

### Issue: Read Timeout

**Symptoms**:
- Error: "Read timeout after X seconds"
- Error: "Ollama received request but didn't start generating"

**Diagnosis**:
```bash
# Check model performance
ollama ps

# Test generation speed
time curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma3:4b","prompt":"test","stream":false}'
```

**Solutions**:

1. **Increase Timeout**:
   ```yaml
   llm:
     timeout: 300  # Increase base timeout
     operation_timeouts:
       outline: 480
   ```

2. **Use Faster Model**:
   ```yaml
   llm:
     model: "gemma3:4b"  # Smaller models are faster
   ```

3. **Reduce Generation Length**:
   ```python
   client.generate(
       prompt,
       params={"num_predict": 2000}  # Reduce from default
   )
   ```

4. **Check System Resources**:
   - Monitor CPU usage
   - Check memory availability
   - Ensure GPU acceleration is working

### Issue: Stream Timeout

**Symptoms**:
- Error: "Stream timeout: X seconds elapsed (limit: Y seconds)"
- Error: "Stream may be stuck or model is too slow"
- Stream stops making progress
- Partial response received
- Very long generation times (e.g., 919s elapsed vs 225s limit)

**Understanding Adaptive Timeout Logic**:

The client now uses **adaptive timeout extension**:
- **Base timeout**: From `config/llm_config.yaml` (default: 180s)
- **Initial stream timeout**: `base_timeout * 1.5` (e.g., 180s → 270s)
- **Adaptive extension**: If stream is making progress (chunks arriving or text growing), timeout extends up to `base_timeout * 3.5`
- **Stuck detection**: Streams without progress for 30s are detected early and fail fast

**Diagnosis**:
```bash
# Check stream progress in logs
grep "Stream:" output/logs/*.log | tail -20

# Check for stuck stream detection
grep "Stream appears stalled" output/logs/*.log

# Check for adaptive timeout extensions
grep "extending timeout" output/logs/*.log

# Check if model is still processing
ollama ps

# Check model performance
time curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma3:4b","prompt":"test","stream":false}'
```

**Solutions**:

1. **Increase Base Timeout** (Most Effective):
   ```yaml
   llm:
     timeout: 300  # Stream timeout: 450s, max adaptive: 1050s
   ```
   This gives the adaptive system more room to extend when streams are slow but making progress.

2. **Use Operation-Specific Timeouts**:
   ```yaml
   llm:
     timeout: 180  # Base
     operation_timeouts:
       lab: 300      # Longer for slow operations
       visualization: 300
       extension: 240
   ```

3. **Monitor Stream Progress**:
   Look for these log patterns:
   ```
   INFO: [request_id] Stream: 10.0s | Chunks: 42 (4.2/s) | Text: 1234 chars | Speed: 123.4 chars/s
   INFO: Stream making progress - extending timeout by 90.0s
   WARNING: Stream appears stalled: no chunks for 30.1s
   ```
   - **Good**: Speed >50 chars/s, chunks arriving regularly
   - **Slow but OK**: Speed 10-50 chars/s, adaptive extension applied
   - **Problem**: Speed <10 chars/s or "stalled" message

4. **Check for Stuck Streams**:
   If you see "Stream appears stalled", the stream stopped making progress:
   ```bash
   # Restart Ollama
   pkill ollama
   ollama serve
   
   # Verify service
   curl http://localhost:11434/api/version
   ```

5. **Model Performance Issues**:
   If timeouts are frequent even with long timeouts:
   - **Use faster model**: Smaller models (4B) are faster than larger ones (8B+)
   - **Check system resources**: CPU, memory, GPU availability
   - **Reduce prompt length**: Shorter prompts generate faster
   - **Check Ollama logs**: `ollama logs` for model-specific issues

6. **Automatic Retry**:
   The client automatically retries transient failures:
   - Connection errors: Retried with exponential backoff
   - Timeouts: Retried if stream was making progress
   - Check logs for retry attempts

**Example Scenarios**:

**Scenario 1**: Stream timeout after 919s (limit: 225s)
- **What happened**: Adaptive extension applied (stream was slow but making progress)
- **Solution**: Increase base timeout to 300s+ to give more room for slow streams

**Scenario 2**: "Stream appears stalled: no chunks for 30.1s"
- **What happened**: Stream stopped receiving data (likely stuck)
- **Solution**: Restart Ollama, check model status, verify network

**Scenario 3**: Frequent timeouts even with long timeouts
- **What happened**: Model is too slow for the operation
- **Solution**: Use faster model, optimize prompts, check system resources

### Issue: Model Not Found

**Symptoms**:
- Error: "404 Not Found"
- Error: "Model 'model_name' not found"

**Solutions**:

1. **Pull Model**:
   ```bash
   ollama pull gemma3:4b
   ```

2. **List Available Models**:
   ```bash
   ollama list
   ```

3. **Verify Model Name**:
   Check `config/llm_config.yaml`:
   ```yaml
   llm:
     model: "gemma3:4b"  # Must match pulled model name
   ```

### Issue: GPU Not Available

**Symptoms**:
- Slow generation
- High CPU usage
- Warning: "Ollama is not using GPU acceleration"

**Solutions**:

1. **Check GPU Status**:
   ```bash
   ollama ps
   # Should show "100% GPU" or similar
   ```

2. **Verify GPU Support**:
   ```bash
   # On macOS with Metal:
   system_profiler SPDisplaysDataType
   ```

3. **Restart Ollama**:
   ```bash
   pkill ollama
   ollama serve
   ```

## Diagnostic Tools

### Health Monitor

```python
from src.llm.health import OllamaHealthMonitor

monitor = OllamaHealthMonitor()

# Check service status
status = monitor.check_service_status()
print(f"Available: {status['available']}")
print(f"Version: {status.get('version')}")

# Check model status
model_status = monitor.check_model_status("gemma3:4b")
print(f"Loaded: {model_status['loaded']}")
print(f"Available: {model_status['available']}")

# Get comprehensive diagnostics
diagnostics = monitor.get_diagnostics()
print(diagnostics)

# Get troubleshooting suggestions
suggestions = monitor.get_troubleshooting_suggestions(
    diagnostics, error_type="timeout"
)
for suggestion in suggestions:
    print(f"  - {suggestion}")
```

### Request Handler

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

# Execute with monitoring
response = handler.execute_with_monitoring(
    request_func=make_request,
    timeout=30,
    request_id="test-123",
    model="gemma3:4b"
)
```

## Log Analysis

### Filter by Request ID

```bash
# Find request ID from error message
# Error: [a1b2c3d4] Request timeout...

# Filter logs by request ID
grep "\[a1b2c3d4\]" output/logs/*.log

# Find all errors for a request
grep "\[a1b2c3d4\].*ERROR" output/logs/*.log

# Find timeout-related messages
grep "\[a1b2c3d4\].*timeout" output/logs/*.log
```

### Common Log Patterns

**Successful Request** (compact format):
```
INFO: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=3257c
INFO: [lec:56e7ab] ✅ HTTP 200 in 1.93s
INFO: [lec:56e7ab] 📡 Stream active (200)
INFO: [lec:56e7ab] 📊 2.0s: 414c @206c/s (68ch, ~104t @52t/s)
INFO: [lec:56e7ab] ✓ Done 20.03s: 3202c (~800w @176c/s)
```

**Timeout Request**:
```
INFO: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=3257c
INFO: [lec:56e7ab] Pre-flight check passed
ERROR: [lec:56e7ab] ⏱️ Read timeout 240.0s (limit: 240s)
```

**Connection Error**:
```
INFO: [lec:56e7ab] 🚀 lec | m=gemma3:4b | p=3257c
ERROR: [lec:56e7ab] Pre-flight check failed: Ollama service unreachable
```

## Performance Optimization

### Reduce Generation Time

1. **Use Smaller Models**:
   ```yaml
   llm:
     model: "gemma3:4b"  # 4B parameters - faster
   # vs
   # model: "llama3:8b"  # 8B parameters - slower
   ```

2. **Reduce Output Length**:
   ```python
   params = {"num_predict": 1000}  # Limit output tokens
   ```

3. **Optimize Prompts**:
   - Shorter prompts = faster generation
   - Clear, specific instructions
   - Avoid redundant context

### Increase Throughput

1. **Use GPU Acceleration**:
   - Ensure GPU is available
   - Check `ollama ps` shows GPU usage

2. **Optimize System**:
   - Close unnecessary applications
   - Ensure adequate RAM
   - Use SSD storage

3. **Batch Processing**:
   - Process requests sequentially (not parallel)
   - Use appropriate timeouts per operation

## Getting Help

If issues persist:

1. **Collect Diagnostics**:
   ```python
   from src.llm.health import OllamaHealthMonitor
   monitor = OllamaHealthMonitor()
   diagnostics = monitor.get_diagnostics()
   print(diagnostics)
   ```

2. **Check Logs**:
   ```bash
   # Recent errors
   tail -n 100 output/logs/*.log | grep ERROR
   
   # All timeout issues
   grep -i timeout output/logs/*.log
   ```

3. **Verify Environment**:
   ```bash
   # Ollama version
   ollama --version
   
   # Python version
   python3 --version
   
   # System info
   uname -a
   ```

4. **Test Directly**:
   ```bash
   # Test Ollama API directly
   curl -X POST http://localhost:11434/api/generate \
     -d '{"model":"gemma3:4b","prompt":"test","stream":false}'
   ```

## See Also

- [Health Monitoring Guide](HEALTH_MONITORING.md)
- [AGENTS.md](AGENTS.md) - Complete API reference
- [README.md](README.md) - User guide
- [../../docs/TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) - General troubleshooting
