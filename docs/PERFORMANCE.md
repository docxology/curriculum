# Performance Guide

Complete reference for performance considerations, optimization strategies, and performance monitoring in the educational course Generator.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Bottleneck** | LLM generation (60-80% of time) |
| **Processing** | Sequential (modules processed one at a time) |
| **Caching** | Config and outline cached after first load |
| **Optimization** | Model selection, timeout tuning, batch processing |
| **Monitoring** | Log analysis, timing metrics |

**Read time**: 20-30 minutes | **Audience**: Developers, system operators

## Performance Characteristics

### Time Distribution

**Typical full course generation (20 modules, 40 sessions)**:

- **Configuration loading**: <1% (cached after first load)
- **Outline generation**: 2-5% (30-60 seconds)
- **Primary content generation**: 60-75% (2-3 hours)
  - Lectures: 40-50% (60-120s each)
  - Labs: 20-25% (45-90s each)
  - Study notes: 10-15% (30-60s each)
  - Diagrams: 5-10% (20-40s each)
  - Questions: 10-15% (40-80s each)
- **Secondary content generation**: 15-20% (30-60 minutes)
- **Website generation**: <1% (10-30 seconds)
- **File I/O**: <1% (minimal overhead)

### Per-Content-Type Times

**Approximate generation times** (with gemma3:4b, typical hardware):

| Content Type | Time Range | Average |
|--------------|------------|---------|
| Outline | 30-60s | 45s |
| Lecture | 60-120s | 90s |
| Lab | 45-90s | 70s |
| Study Notes | 30-60s | 45s |
| Diagram | 20-40s | 30s |
| Questions | 40-80s | 60s |
| Application | 30-60s | 45s |
| Extension | 20-40s | 30s |
| Visualization | 20-40s | 30s |
| Integration | 30-60s | 45s |
| Investigation | 30-60s | 45s |
| Open Questions | 30-60s | 45s |

**Full 20-module course**: ~2-4 hours (depends on model, hardware, content length)

## Performance Bottlenecks

### Primary Bottleneck: LLM Generation

**Impact**: 60-80% of total time

**Characteristics**:
- Network latency to Ollama API
- Model inference time (depends on model size)
- Prompt length (longer prompts = slower)
- Response length (longer responses = slower)

**Optimization Strategies**:
1. **Use smaller models**: 4B models faster than 13B+ models
2. **Reduce prompt length**: Shorter prompts = faster generation
3. **Reduce response length**: Lower `num_predict` parameter
4. **Optimize prompts**: More specific prompts = faster generation

### Secondary Bottleneck: Sequential Processing

**Impact**: 10-20% of total time (could be parallelized)

**Characteristics**:
- Modules processed one at a time
- Sessions processed sequentially within modules
- Content types generated sequentially per session

**Optimization Strategies**:
1. **Parallel module processing**: Process multiple modules simultaneously (future enhancement)
2. **Parallel content generation**: Generate multiple content types simultaneously (future enhancement)
3. **Batch processing**: Group similar operations together

### Minor Bottlenecks

**File I/O**: <1% of time
- Minimal impact
- Cached reads after first access

**Configuration Loading**: <1% of time
- Cached after first load
- Minimal impact

## Optimization Strategies

### Model Selection

**Choose appropriate model size**:

| Model Size | Speed | Quality | Use Case |
|------------|-------|---------|----------|
| 4B | Fast | Good | Quick generation, testing |
| 8B | Medium | Better | Balanced speed/quality |
| 13B+ | Slow | Best | High-quality content |

**Recommendation**: Start with 4B for testing, use 8B for production

### Timeout Configuration

**Set appropriate timeouts**:

```yaml
# config/llm_config.yaml
llm:
  timeout: 120  # Adjust based on model and prompt size
```

**Guidelines**:
- Small models (4B): 60-120 seconds
- Medium models (8B): 120-240 seconds
- Large models (13B+): 240-480 seconds

**Too short**: Causes unnecessary retries
**Too long**: Wastes time on hung requests

### Prompt Optimization

**Reduce prompt length**:
- Remove unnecessary context
- Use concise variable names
- Minimize template verbosity

**Improve prompt specificity**:
- More specific prompts = faster generation
- Clear requirements = fewer retries
- Better examples = faster convergence

### Content Length Optimization

**Adjust `num_predict` parameter**:

```yaml
# config/llm_config.yaml
llm:
  parameters:
    num_predict: 32000  # Reduce from 64000 for faster generation (128K context allows up to 64K output)
```

**Trade-offs**:
- Lower `num_predict`: Faster, but may truncate content (with 128K context, can use up to 64K output)
- Higher `num_predict`: Slower, but ensures completeness (recommended: 50000-100000 for comprehensive content)

**Recommendation**: With 128K context, start with 32000, increase to 64000 for comprehensive content

### Caching Strategies

**Configuration Caching**:
- Configs loaded once and cached
- No reloading unless explicitly requested
- Minimal overhead after first load

**Outline Caching**:
- JSON outline parsed once and cached
- Reused across multiple generators
- Avoids redundant parsing

**Future Enhancements**:
- Content caching (cache generated content)
- Template caching (cache formatted prompts)

## Performance Monitoring

### Log Analysis

**Extract timing information**:

```bash
# Find generation times
grep "Generation complete" scripts/output/logs/*.log | \
  grep -oE "[0-9]+\.[0-9]+s" | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count, "s"}'

# Find slow operations
grep "Generation complete" scripts/output/logs/*.log | \
  grep -E "[0-9]{3,}\.[0-9]+s"

# Count operations
grep "Generation complete" scripts/output/logs/*.log | wc -l
```

### Performance Metrics

**Track key metrics**:
- Total generation time
- Per-content-type times
- Success/failure rates
- Retry counts
- Timeout occurrences

**Example metrics collection**:
```python
import time
from src.generate.formats.lectures import LectureGenerator

start_time = time.time()
content = generator.generate_lecture(module_info)
elapsed = time.time() - start_time
print(f"Lecture generation: {elapsed:.2f}s")
```

### Performance Profiling

**Use Python profiler**:

```bash
# Profile script execution
python3 -m cProfile -o profile.stats scripts/04_generate_primary.py

# Analyze profile
python3 -m pstats profile.stats
```

**Identify slow functions**:
- Focus optimization on functions with most time
- Look for unnecessary operations
- Identify I/O bottlenecks

## Performance Testing

### Benchmark Generation

**Create benchmark script**:

```python
"""Benchmark content generation performance."""

import time
from src.config.loader import ConfigLoader
from src.generate.orchestration.pipeline import ContentGenerator

config = ConfigLoader("config")
generator = ContentGenerator(config)

# Benchmark outline generation
start = time.time()
outline_path = generator.stage1_generate_outline()
outline_time = time.time() - start
print(f"Outline generation: {outline_time:.2f}s")

# Benchmark content generation
start = time.time()
results = generator.stage2_generate_content_by_session(module_ids=[1])
content_time = time.time() - start
print(f"Content generation (1 module): {content_time:.2f}s")
```

### Performance Regression Testing

**Track performance over time**:
- Record generation times for standard test cases
- Compare against baseline
- Alert on significant regressions

## Memory Considerations

### Memory Usage

**Typical memory usage**:
- Configuration: <10MB (cached)
- Outline: <5MB (cached)
- Content generation: 100-500MB (depends on model)
- File I/O: <50MB (buffered)

**Peak memory**: During LLM generation (model loaded in memory)

### Memory Optimization

**Strategies**:
1. **Use smaller models**: Lower memory footprint
2. **Process incrementally**: Don't load all content at once
3. **Clear caches**: Free memory when not needed
4. **Monitor memory**: Use `top` or `htop` to monitor usage

## Network Considerations

### Local vs Remote Ollama

**Local Ollama** (default):
- Low latency (<1ms)
- No network overhead
- Recommended for performance

**Remote Ollama**:
- Higher latency (depends on network)
- Network overhead
- May impact performance

**Recommendation**: Use local Ollama for best performance

### Network Optimization

**If using remote Ollama**:
- Use fast network connection
- Minimize network hops
- Consider VPN optimization
- Monitor network latency

## Parallel Processing Opportunities

### Current Implementation

**Sequential processing**:
- Modules processed one at a time
- Sessions processed sequentially
- Content types generated sequentially

**Benefits**:
- Predictable resource usage
- Easier debugging
- Lower memory usage

### Future Enhancements

**Parallel module processing**:
- Process multiple modules simultaneously
- Use thread pool or process pool
- Requires careful resource management

**Parallel content generation**:
- Generate multiple content types simultaneously
- Requires independent generators
- May increase memory usage

**Implementation considerations**:
- Thread safety
- Resource limits
- Error handling
- Progress tracking

## Performance Best Practices

1. **Choose appropriate model**: Balance speed and quality
2. **Set realistic timeouts**: Based on model and prompt size
3. **Optimize prompts**: Shorter, more specific prompts
4. **Monitor performance**: Track generation times
5. **Profile regularly**: Identify bottlenecks
6. **Cache aggressively**: Cache configs and outlines
7. **Process incrementally**: Don't load everything at once
8. **Use local Ollama**: Minimize network latency

## Performance Troubleshooting

### Issue: Generation is very slow

**Diagnosis**:
- Check model size (larger = slower)
- Check system resources (CPU/memory)
- Check Ollama performance
- Review generation times in logs

**Solutions**:
- Use smaller model
- Increase system resources
- Optimize prompts
- Reduce content length

### Issue: Timeouts are too frequent

**Diagnosis**:
- Check timeout setting
- Check model performance
- Review prompt length

**Solutions**:
- Increase timeout
- Use faster model
- Reduce prompt length

### Issue: High memory usage

**Diagnosis**:
- Check model size
- Check concurrent operations
- Review memory usage patterns

**Solutions**:
- Use smaller model
- Process sequentially
- Clear caches when not needed

## Related Documentation

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Performance troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and performance considerations
- **[LOGGING.md](LOGGING.md)** - Performance logging and monitoring

## Summary

Performance optimization focuses on:

1. **LLM generation**: Primary bottleneck (60-80% of time)
2. **Model selection**: Balance speed and quality
3. **Timeout tuning**: Set appropriate timeouts
4. **Prompt optimization**: Shorter, more specific prompts
5. **Caching**: Cache configs and outlines
6. **Monitoring**: Track performance metrics

The system is designed for sequential processing with aggressive caching. Future enhancements could include parallel processing for improved performance.






