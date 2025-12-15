# Deployment Guide

Complete guide for deploying and using the educational course Generator in production environments.

## Quick Reference Card

| Aspect | Details |
|--------|---------|
| **Deployment Type** | Local execution, no server required |
| **Requirements** | Python 3.10+, uv, Ollama, sufficient disk space |
| **Configuration** | YAML files in `config/` directory |
| **Output** | Generated content in `output/` directory |
| **Monitoring** | Log files in `output/logs/` directory |

**Read time**: 20-30 minutes | **Audience**: System administrators, operators

## Overview

The educational course Generator is designed for local execution. This guide covers:
- Production environment setup
- Configuration for production
- Monitoring and logging
- Backup and recovery
- Scaling considerations
- CI/CD integration

## Production Environment Setup

### System Requirements

**Minimum Requirements**:
- **CPU**: 4 cores (8+ recommended)
- **Memory**: 8GB RAM (16GB+ recommended)
- **Disk**: 10GB free space (50GB+ for large courses)
- **Network**: Local only (Ollama runs locally)

**Recommended Requirements**:
- **CPU**: 8+ cores
- **Memory**: 32GB+ RAM
- **Disk**: 100GB+ free space (SSD recommended)
- **Network**: Local network for Ollama (if remote)

### Software Requirements

**Required Software**:
- **Python**: 3.10 or higher
- **uv**: Package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Ollama**: LLM runtime (install via `ollama.ai`)

**Optional Software**:
- **jq**: JSON processing (for log analysis)
- **git**: Version control (for content tracking)

### Installation Steps

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd biology
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Install Ollama**:
   ```bash
   # Follow instructions at ollama.ai
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

4. **Download LLM model**:
   ```bash
   ollama pull gemma3:4b
   ```

5. **Validate installation**:
   ```bash
   uv run python3 scripts/01_setup_environment.py
   ```

## Production Configuration

### Configuration Files

**Required configuration files** in `config/`:

1. **`course_config.yaml`**: Course structure and metadata
2. **`llm_config.yaml`**: LLM settings and prompts
3. **`output_config.yaml`**: Output paths and logging

### Production Configuration Best Practices

**Course Configuration**:
```yaml
# config/course_config.yaml
course:
  name: "Production Course Name"
  description: "Comprehensive course description"
  level: "Undergraduate"
  estimated_duration_weeks: 16
  defaults:
    num_modules: 20
    total_sessions: 40
  additional_constraints: "Production-specific requirements"
```

**LLM Configuration**:
```yaml
# config/llm_config.yaml
llm:
  model: "gemma3:4b"  # Use stable model for production
  api_url: "http://localhost:11434/api/generate"
  timeout: 240  # Higher timeout for production
  parameters:
    temperature: 0.7
    top_p: 0.9
    num_predict: 64000   # 64K max output tokens (128K context window)
```

**Output Configuration**:
```yaml
# config/output_config.yaml
output:
  base_directory: "output"
  logging:
    level: "INFO"  # INFO for production, DEBUG for troubleshooting
    console: true
    file: true
```

### Environment Variables

**Optional environment variables**:

```bash
# Log level override
export LOG_LEVEL=INFO

# Config directory override
export CONFIG_DIR=/path/to/config

# Output directory override
export OUTPUT_DIR=/path/to/output
```

## Monitoring and Logging

### Log File Management

**Log file location**: `output/logs/`

**Log file naming**: `{script_name}_{timestamp}.log`

**Log retention**:
- Keep logs for recent runs (7-30 days)
- Archive older logs
- Delete very old logs (>90 days)

**Log rotation** (manual):
```bash
# Archive old logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz output/logs/*.log

# Clear old logs
find output/logs -name "*.log" -mtime +30 -delete
```

### Monitoring Generation Progress

**Watch logs in real-time**:
```bash
# Follow latest log
tail -f output/logs/04_generate_primary_*.log

# Watch for errors
tail -f output/logs/04_generate_primary_*.log | grep -E "ERROR|Failed"
```

**Check generation status**:
```bash
# Count completed sessions
grep "Session.*completed" output/logs/04_generate_primary_*.log | wc -l

# Count failed sessions
grep "Error processing session" output/logs/04_generate_primary_*.log | wc -l
```

### Performance Monitoring

**Track generation times**:
```bash
# Extract generation times
grep "Generation complete" output/logs/*.log | \
  grep -oE "[0-9]+\.[0-9]+s" | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count, "s"}'
```

**Monitor system resources**:
```bash
# CPU and memory usage
top -p $(pgrep -f "python.*scripts/04_generate_primary")

# Disk usage
df -h output/
```

## Backup and Recovery

### Backup Strategy

**Backup outline files**:
```bash
# Backup JSON outlines
cp output/outlines/course_outline_*.json backups/outlines/

# Backup with timestamp
cp output/outlines/course_outline_*.json \
   backups/outlines/course_outline_$(date +%Y%m%d_%H%M%S).json
```

**Backup generated content**:
```bash
# Backup all generated content
tar -czf backups/content_$(date +%Y%m%d).tar.gz output/modules/

# Incremental backup (only new/modified)
rsync -av output/modules/ backups/modules/
```

**Backup configuration**:
```bash
# Backup configuration files
cp -r config/ backups/config_$(date +%Y%m%d)/
```

### Recovery Procedures

**Recover from outline corruption**:
```bash
# Restore from backup
cp backups/outlines/course_outline_YYYYMMDD_HHMMSS.json \
   output/outlines/course_outline_restored.json

# Regenerate content with restored outline
uv run python3 scripts/04_generate_primary.py \
  --outline output/outlines/course_outline_restored.json
```

**Recover from content loss**:
```bash
# Restore from backup
tar -xzf backups/content_YYYYMMDD.tar.gz -C output/

# Verify restored content
ls -la output/modules/
```

**Recover from configuration loss**:
```bash
# Restore configuration
cp -r backups/config_YYYYMMDD/* config/

# Validate configuration
uv run python3 scripts/01_setup_environment.py
```

## Scaling Considerations

### Horizontal Scaling

**Current limitation**: Sequential processing

**Future enhancement**: Parallel processing
- Process multiple modules simultaneously
- Requires careful resource management
- May increase memory usage

### Vertical Scaling

**Increase system resources**:
- **CPU**: More cores for parallel processing (future)
- **Memory**: More RAM for larger models
- **Disk**: More space for larger courses
- **Network**: Faster local network (if remote Ollama)

### Model Selection

**Choose model based on resources**:
- **4B models**: Lower resource usage, faster
- **8B models**: Balanced resources and quality
- **13B+ models**: Higher resource usage, best quality

## CI/CD Integration

### Continuous Integration

**Example CI configuration** (GitHub Actions):

```yaml
name: Test and Validate

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv pip install -e ".[dev]"
      - name: Run tests
        run: uv run pytest
      - name: Validate configuration
        run: uv run python3 scripts/01_setup_environment.py
```

### Continuous Deployment

**Deployment workflow**:
1. **Test**: Run test suite
2. **Validate**: Validate configuration
3. **Deploy**: Copy files to production
4. **Verify**: Run validation checks

**Example deployment script**:
```bash
#!/bin/bash
# Deploy to production

# Run tests
uv run pytest || exit 1

# Validate configuration
uv run python3 scripts/01_setup_environment.py || exit 1

# Deploy (example)
rsync -av --exclude='.git' . /path/to/production/

# Verify deployment
cd /path/to/production
uv run python3 scripts/01_setup_environment.py
```

## Production Troubleshooting

### Common Production Issues

**Issue: Generation fails intermittently**

**Diagnosis**:
- Check Ollama stability
- Review system resources
- Check log files

**Solutions**:
- Restart Ollama service
- Increase system resources
- Review error logs

**Issue: Disk space running low**

**Diagnosis**:
```bash
df -h output/
```

**Solutions**:
- Clean old generated content
- Archive old logs
- Increase disk space

**Issue: Memory exhaustion**

**Diagnosis**:
```bash
free -h
top
```

**Solutions**:
- Use smaller model
- Process fewer modules at once
- Increase system memory

## Production Best Practices

1. **Regular backups**: Backup outlines and content regularly
2. **Monitor logs**: Review logs for errors and warnings
3. **Validate configuration**: Validate before each run
4. **Test changes**: Test configuration changes before production
5. **Document changes**: Document configuration and process changes
6. **Monitor resources**: Track CPU, memory, and disk usage
7. **Review output**: Review generated content for quality
8. **Update regularly**: Keep dependencies and models updated

## Related Documentation

- **[SETUP.md](../SETUP.md)** - Initial setup and installation
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration reference
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting guide
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance optimization
- **[SECURITY.md](SECURITY.md)** - Security considerations

## Summary

Production deployment involves:

1. **Environment setup**: Install dependencies, configure system
2. **Configuration**: Set up production configuration files
3. **Monitoring**: Set up logging and monitoring
4. **Backup**: Implement backup strategy
5. **Recovery**: Plan recovery procedures
6. **Scaling**: Consider scaling needs
7. **CI/CD**: Integrate with CI/CD pipeline

The system is designed for local execution with minimal deployment complexity. Follow best practices for configuration, monitoring, and backup to ensure reliable production operation.






