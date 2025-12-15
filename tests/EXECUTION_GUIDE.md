# Test Execution Guide

Quick reference for running and managing the test suite.

## Quick Commands

```bash
# Run all tests
uv run pytest

# Run only unit tests (fast, no Ollama needed)
uv run pytest -m unit

# Run only integration tests (requires Ollama)
uv run pytest -m integration

# Run tests excluding slow ones
uv run pytest -m "not slow"

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_logging_setup.py -v

# Run specific test
uv run pytest tests/test_logging_setup.py::TestSetupLogging::test_setup_logging_defaults -v
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Fast tests that don't require Ollama:
- `test_config_loader.py`
- `test_parser.py`
- `test_parser_edge_cases.py`
- `test_utils.py`
- `test_cleanup.py`
- `test_helpers_extended.py`
- `test_content_analysis.py`
- `test_logging_setup.py`

**Run with**: `uv run pytest -m unit`

**Expected time**: ~5-10 seconds

### Integration Tests (`@pytest.mark.integration`)

Tests that require Ollama and LLM model:
- `test_llm_client.py`
- `test_outline_generator.py`
- `test_content_generators.py`
- `test_new_generators.py`
- `test_pipeline.py`
- `test_json_outline_integration.py`

**Run with**: `uv run pytest -m integration`

**Expected time**: ~4-5 minutes

**Prerequisites**: 
- Ollama installed and running
- `gemma3:4b` model available (`ollama pull gemma3:4b`)

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer than 10 seconds:
- Full pipeline tests
- Multi-module generation tests
- Large content generation tests

**Run with**: `uv run pytest -m slow`

**Skip with**: `uv run pytest -m "not slow"`

## Test Execution Strategies

### Development Workflow

1. **Quick feedback** (during development):
   ```bash
   uv run pytest -m unit -v
   ```

2. **Before commit** (full unit tests):
   ```bash
   uv run pytest -m unit --cov=src --cov-report=term-missing
   ```

3. **Pre-release** (full suite):
   ```bash
   uv run pytest --cov=src --cov-report=html
   ```

### Debugging Failed Tests

```bash
# Show full traceback
uv run pytest tests/test_logging_setup.py -v --tb=long

# Stop at first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Run with pdb debugger on failure
uv run pytest --pdb
```

## Coverage Reports

### Terminal Report
```bash
uv run pytest --cov=src --cov-report=term-missing
```

### HTML Report
```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Coverage Targets

- **Overall**: 75%+ (with integration tests)
- **Unit tests only**: 50%+
- **Critical modules**: 80%+ (config, parser, cleanup)

## Troubleshooting

### "Ollama not found"

Integration tests will skip automatically. To run them:
1. Install Ollama: https://ollama.ai/
2. Start Ollama: `ollama serve`
3. Pull model: `ollama pull gemma3:4b`

### "Model not available"

```bash
# Check available models
ollama list

# Pull required model
ollama pull gemma3:4b

# Verify model works
ollama run gemma3:4b "test"
```

### Tests timing out

Some integration tests may timeout if Ollama is slow:
- Increase timeout in `config/llm_config.yaml`
- Run tests individually to isolate slow ones
- Use `-m "not slow"` to skip slow tests

### Coverage not updating

```bash
# Clear coverage cache
rm -rf .coverage htmlcov .pytest_cache

# Run tests with fresh coverage
uv run pytest --cov=src --cov-report=html
```

## Performance Optimization

### Parallel Execution

Install pytest-xdist:
```bash
uv pip install pytest-xdist
```

Run tests in parallel:
```bash
uv run pytest -n auto  # Auto-detect CPU count
uv run pytest -n 4    # Use 4 workers
```

**Note**: Integration tests with Ollama may not benefit much from parallelization due to API rate limits.

### Test Selection

Run only changed tests:
```bash
# Run tests for specific module
uv run pytest tests/test_logging_setup.py

# Run tests matching pattern
uv run pytest -k "test_setup_logging"
```

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before committing major changes
3. **Check coverage** regularly to identify gaps
4. **Fix failing tests immediately** - don't let them accumulate
5. **Add tests** for new functionality before implementing
6. **Use markers** to categorize new tests appropriately

## Test Markers Reference

- `@pytest.mark.unit` - Unit tests (no Ollama)
- `@pytest.mark.integration` - Integration tests (requires Ollama)
- `@pytest.mark.slow` - Slow tests (>10s)

**Usage**:
```python
@pytest.mark.unit
def test_something():
    """Unit test that doesn't need Ollama."""
    pass

@pytest.mark.integration
def test_with_ollama(skip_if_no_ollama):
    """Integration test requiring Ollama."""
    pass
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Fast feedback (unit tests only)
uv run pytest -m unit --cov=src --cov-report=xml

# Full suite (if Ollama available)
uv run pytest --cov=src --cov-report=xml --junitxml=test-results.xml
```

## Additional Resources

- **Test Philosophy**: See `.cursorrules/03-testing-real-only.md`
- **Test Coverage Report**: See `docs/TESTING_COVERAGE.md`
- **Test Organization**: See `tests/README.md`
- **For AI Agents**: See `tests/AGENTS.md`






