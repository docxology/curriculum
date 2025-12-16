# Test Suite - For AI Agents

## Purpose

This directory contains the comprehensive test suite for the educational course Generator. **ALL TESTS USE IMPLEMENTATIONS - NO MOCKS EVER**.

## Core Philosophy: NO MOCKS

✅ **Ollama** - Integration tests use actual LLM API  
✅ **Files** - Tests use actual file I/O  
✅ **Data** - Tests use actual configuration and content  
✅ **Graceful Skipping** - Tests skip if dependencies unavailable  
✅ **NO unittest.mock** - Removed from entire codebase  

**Rationale**: Mocks hide integration issues. Tests catch problems.

## Test Statistics

**Total**: ~540 tests across 25 test files + 10 fixture files  
**Coverage**: 30% without Ollama, 75% with integration tests  
**Speed**: Fast unit tests ~5s, full suite ~150s  

## Test Files (25 files)

### Unit Tests (No Ollama Required)

1. **test_config_loader.py** (23 tests) - Configuration loading, JSON outline discovery
2. **test_parser.py** (14 tests) - Outline parsing from markdown
3. **test_parser_edge_cases.py** (15 tests) - Malformed markdown, unicode, boundaries
4. **test_utils.py** (15 tests) - Utility functions, file I/O
5. **test_helpers_extended.py** (8 tests) - Additional helper functions
6. **test_cleanup.py** (35 tests) - Content cleanup and validation
7. **test_outline_generator_noninteractive.py** (15 tests) - Non-interactive outline tests
8. **test_content_analysis.py** (10 tests) - Content analysis utilities
9. **test_error_collector.py** (15 tests) - Error collection utilities
10. **test_summary_generator.py** (8 tests) - Summary generation utilities
11. **test_website_generator.py** (10 tests) - WebsiteGenerator class (initialization, generation, error handling)
12. **test_website_content_loader.py** (18 tests) - Content discovery and loading functions
13. **test_website_templates.py** (25 tests) - HTML template generation and markdown conversion
14. **test_website_scripts.py** (13 tests) - JavaScript code generation and functionality
15. **test_website_scripts_interaction.py** (11 tests) - JavaScript event handler interaction behavior
16. **test_website_styles.py** (6 tests) - CSS stylesheet generation
17. **test_logging_setup.py** (38 tests) - Logging configuration and setup

**Total unit tests**: ~221 tests, run in ~5 seconds

### Integration Tests (Require Ollama + gemma3:4b)

18. **test_batch_processor.py** (14 tests) - Batch course processing
19. **test_llm_client.py** (15 tests) - LLM API integration, real network calls
20. **test_outline_generator.py** (12+ tests) - Outline generation with real LLM and edge cases
21. **test_content_generators.py** (10 tests) - Lectures, diagrams, questions generation
22. **test_new_generators.py** (7 tests) - Study notes and labs generation
23. **test_pipeline.py** (11+ tests) - Full pipeline orchestration with expanded tests
24. **test_json_outline_integration.py** (10 tests) - JSON outline integration
25. **test_pipeline_extended.py** (20 tests) - Additional pipeline scenarios

**Total integration tests**: ~89 tests, run in ~150 seconds with Ollama

## Test Organization

### By Functionality

**Configuration & Loading**:
- `test_config_loader.py` - YAML loading, validation, JSON outline discovery
- `test_json_outline_integration.py` - JSON outline integration

**Content Processing**:
- `test_parser.py` - Markdown parsing
- `test_parser_edge_cases.py` - Edge cases
- `test_cleanup.py` - Content cleanup
- `test_content_analysis.py` - Quality analysis

**LLM Integration**:
- `test_llm_client.py` - Ollama API client
- `test_outline_generator.py` - Outline generation
- `test_outline_generator_noninteractive.py` - Non-interactive mode

**Content Generation**:
- `test_content_generators.py` - Primary formats (lectures, diagrams, questions)
- `test_new_generators.py` - Additional formats (study notes, labs)

**Pipeline & Orchestration**:
- `test_pipeline.py` - Full pipeline
- `test_pipeline_extended.py` - Extended scenarios

**Utilities**:
- `test_utils.py` - Core utility functions
- `test_helpers_extended.py` - Additional helpers
- `test_logging_setup.py` - Logging configuration

**Website Generation**:
- `test_website_generator.py` - WebsiteGenerator class
- `test_website_content_loader.py` - Content discovery and loading
- `test_website_templates.py` - HTML template generation
- `test_website_scripts.py` - JavaScript code generation
- `test_website_scripts_interaction.py` - JavaScript event handler interactions
- `test_website_styles.py` - CSS stylesheet generation

### By Speed

**Fast (<2s each)**:
- `test_config_loader.py`
- `test_parser.py`
- `test_parser_edge_cases.py`
- `test_utils.py`
- `test_helpers_extended.py`
- `test_cleanup.py`
- `test_outline_generator_noninteractive.py`
- `test_content_analysis.py`
- `test_logging_setup.py`
- `test_website_generator.py`
- `test_website_content_loader.py`
- `test_website_templates.py`
- `test_website_scripts.py`
- `test_website_scripts_interaction.py`
- `test_website_styles.py`

**Slow (require Ollama, 10-30s each, marked with `@pytest.mark.slow` and `@pytest.mark.integration`)**:
- `test_llm_client.py` (some tests)
- `test_outline_generator.py` (all tests)
- `test_content_generators.py` (all tests)
- `test_new_generators.py` (all tests)
- `test_pipeline.py` (content generation tests)
- `test_pipeline_integration.py` (all tests)
- `test_json_outline_integration.py`
- `test_pipeline_extended.py`

**Note**: Test scope has been optimized (reduced to 1 module, 2 sessions) to improve performance while maintaining coverage.

## Running Tests

### All Tests (Auto-Start Ollama)
```bash
# Auto-starts Ollama if installed, runs all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Fast Unit Tests Only (No Ollama)
```bash
# Run only tests that don't require Ollama (~5s)
uv run pytest tests/test_config_loader.py tests/test_parser.py tests/test_utils.py tests/test_cleanup.py tests/test_helpers_extended.py tests/test_parser_edge_cases.py tests/test_outline_generator_noninteractive.py tests/test_content_analysis.py
```

### Integration Tests Only (Require Ollama)
```bash
# Run only tests that require Ollama (~150s)
uv run pytest tests/test_llm_client.py tests/test_outline_generator.py tests/test_content_generators.py tests/test_new_generators.py tests/test_pipeline.py tests/test_json_outline_integration.py tests/test_pipeline_extended.py
```

### Specific Test File
```bash
uv run pytest tests/test_config_loader.py -v
```

### Specific Test Function
```bash
uv run pytest tests/test_config_loader.py::TestConfigLoader::test_load_course_config -v
```

### With Verbose Output
```bash
uv run pytest -v
```

### Show Print Statements
```bash
uv run pytest -s
```

## Test Fixtures

### Auto-Start Mechanism (conftest.py)

`conftest.py` provides session-level fixtures:

```python
@pytest.fixture(scope="session", autouse=True)
def ensure_ollama_running():
    """Runs once per test session, starts Ollama if needed."""
    # 1. Check if Ollama is running
    # 2. Attempt to start if not running
    # 3. Verify gemma3:4b model available
    # 4. Skip integration tests if setup fails

@pytest.fixture
def skip_if_no_ollama():
    """Add to test signature to skip if Ollama unavailable."""
    # Usage: def test_something(self, skip_if_no_ollama):
```

**How it works**:
1. Before any test runs, checks Ollama status
2. If not running, attempts to start: `ollama serve`
3. Waits up to 10s for service to be ready
4. Verifies gemma3:4b model is available
5. Sets `ollama_available` flag for test skipping

### Test Data Fixtures (tests/fixtures/)

**10 fixture files** with sample data:

1. **sample_course_config.yaml** - Course configuration example
2. **sample_module_info.json** - Module structure (JSON outline format)
3. **sample_outline.json** - Complete JSON outline (2 modules, 6 sessions)
4. **sample_markdown_outline.md** - Markdown outline for parser testing
5. **sample_lecture.md** - Example lecture content
6. **sample_lab.md** - Example lab exercise
7. **sample_study_notes.md** - Example study notes
8. **sample_questions.md** - Example questions with answers
9. **sample_diagram.mmd** - Example Mermaid diagram
10. **README.md** - Fixture documentation

**Usage in tests**:
```python
def test_something():
    # Load fixture
    fixture_path = Path(__file__).parent / "fixtures" / "sample_outline.json"
    with open(fixture_path) as f:
        outline = json.load(f)
```

### Temporary Directories

All tests use pytest's `tmp_path` fixture for temporary files:

```python
def test_file_operation(tmp_path):
    """Test with temporary directory."""
    test_file = tmp_path / "test.md"
    test_file.write_text("content")
    # Cleanup automatic
```

## Test Coverage

### Without Ollama (Unit Tests): ~30% overall
- **config_loader.py**: 95% ✅
- **parser.py**: 80% ✅
- **utils/helpers.py**: 90% ✅
- **processors/cleanup.py**: 85% ✅
- **llm_client.py**: 30% (only init/config without Ollama)

### With Ollama (Full Suite): ~75% overall
- All modules tested with real LLM
- Integration tests add ~45% coverage
- End-to-end workflows validated

## Key Test Principles

### 1. NO MOCKS EVER
```python
# ❌ BAD (using mocks)
from unittest.mock import Mock, patch
with patch('requests.post') as mock_post:
    mock_post.return_value = Mock(status_code=200)

# ✅ GOOD (real implementation)
def test_llm_client(skip_if_no_ollama):
    """Test with real Ollama service."""
    client = OllamaClient(config)
    result = client.generate("Test prompt")
    assert isinstance(result, str)
```

### 2. Graceful Skipping
```python
# Tests skip if dependencies unavailable
def test_requires_ollama(self, skip_if_no_ollama):
    """This test skips if Ollama not available."""
    # Test code using real Ollama
```

### 3. Real Data Only
```python
# Use actual files, configurations, content
def test_config_loading():
    """Load real YAML configuration."""
    loader = ConfigLoader("config")  # Real config directory
    config = loader.load_course_config()  # Real YAML parsing
    assert "course" in config
```

### 4. Isolated Tests
```python
# Each test is independent
def test_something(tmp_path):
    """Uses temporary directory, no shared state."""
    # Creates fresh environment
    # Cleans up automatically
```

### 5. Clear Assertions
```python
# Specific, meaningful checks
assert result.status == "success"
assert len(modules) == 5
assert "Biology" in content
assert output_file.exists()
```

## Common Test Patterns

### Testing LLM Integration
```python
def test_generate_content(self, skip_if_no_ollama):
    """Test content generation with real LLM."""
    client = OllamaClient(llm_config)
    result = client.generate(
        prompt="Generate a biology concept",
        params={"num_predict": 50}
    )
    assert isinstance(result, str)
    assert len(result) > 0
```

### Testing File Operations
```python
def test_save_file(tmp_path):
    """Test file saving with real I/O."""
    output_file = tmp_path / "test.md"
    content = "# Test Content"
    
    output_file.write_text(content)
    
    assert output_file.exists()
    assert output_file.read_text() == content
```

### Testing Configuration
```python
def test_config_validation():
    """Test config validation with real YAML."""
    loader = ConfigLoader("config")
    
    # Should not raise exception
    loader.validate_all_configs()
    
    # Check specific values
    course_info = loader.get_course_info()
    assert "name" in course_info
```

### Testing Error Handling
```python
def test_error_handling():
    """Test error handling with real error conditions."""
    llm_config["api_url"] = "http://localhost:99999/invalid"
    client = OllamaClient(llm_config)
    
    # Should raise LLMError with clear message
    with pytest.raises(LLMError, match="connection|failed"):
        client.generate("Test")
```

## Troubleshooting Tests

### "Ollama not found"
```bash
# Install Ollama
# https://ollama.ai/

# Tests will skip integration tests but run unit tests
```

### "gemma3:4b model not available"
```bash
ollama pull gemma3:4b
```

### "Ollama server failed to start"
```bash
# Check if already running
curl http://localhost:11434/api/version

# Manually start
ollama serve
```

### Tests hang
```bash
# LLM generation can be slow
# Increase timeout in test configs or use faster model
```

### All tests skipped
```bash
# Verify Ollama installation
which ollama
ollama list
```

### Specific test fails
```bash
# Run with verbose output
uv run pytest tests/test_file.py::test_function -vv

# Show print statements
uv run pytest tests/test_file.py::test_function -s
```

## CI/CD Considerations

### Without Ollama (Fast Unit Tests)
```bash
# Run only unit tests in CI
uv run pytest tests/test_config_loader.py tests/test_parser.py tests/test_utils.py tests/test_cleanup.py tests/test_helpers_extended.py tests/test_parser_edge_cases.py tests/test_outline_generator_noninteractive.py tests/test_content_analysis.py
```

### With Ollama (Full Suite)
```yaml
# GitHub Actions example
- name: Install Ollama
  run: curl https://ollama.ai/install.sh | sh

- name: Pull Model
  run: ollama pull gemma3:4b

- name: Run Tests
  run: uv run pytest --cov=src
```

### Using Test Markers (Future Enhancement)
```bash
# Could add pytest markers
pytest -m "not integration"  # Skip integration tests
pytest -m "integration"      # Run only integration tests
```

## Best Practices

✅ **Use implementations** - No mocks, ever  
✅ **Skip gracefully** - Don't fail on missing dependencies  
✅ **Isolate tests** - Each test independent  
✅ **Clear assertions** - Specific, meaningful checks  
✅ **Good coverage** - Mix of happy path and edge cases  
✅ **Fast unit tests** - Run frequently during development  
✅ **Comprehensive integration** - Full end-to-end validation  
✅ **Temporary directories** - Use `tmp_path` for file operations  
✅ **Real data fixtures** - Sample outlines, configs, content  
✅ **Descriptive names** - Clear test purpose from name  
✅ **Good docstrings** - Explain what each test validates  

## What NOT to Do

❌ Don't use mocks (`unittest.mock`)  
❌ Don't use fake/dummy LLM responses  
❌ Don't skip error cases  
❌ Don't test implementation details  
❌ Don't share state between tests  
❌ Don't hard-code paths (use `tmp_path`)  
❌ Don't rely on external state  
❌ Don't test multiple things in one test  

## Test Organization Patterns

### By Functionality

**Configuration & Loading**:
- `test_config_loader.py` - YAML loading, validation, JSON outline discovery
- `test_json_outline_integration.py` - JSON outline integration

**Content Processing**:
- `test_parser.py` - Markdown parsing
- `test_parser_edge_cases.py` - Edge cases, malformed input
- `test_cleanup.py` - Content cleanup and validation
- `test_content_analysis.py` - Quality analysis

**LLM Integration**:
- `test_llm_client.py` - Ollama API client
- `test_outline_generator.py` - Outline generation
- `test_outline_generator_noninteractive.py` - Non-interactive mode

**Content Generation**:
- `test_content_generators.py` - Primary formats (lectures, diagrams, questions)
- `test_new_generators.py` - Additional formats (study notes, labs)

**Pipeline & Orchestration**:
- `test_pipeline.py` - Full pipeline
- `test_pipeline_extended.py` - Extended scenarios

**Website Generation**:
- `test_website_generator.py` - WebsiteGenerator class
- `test_website_content_loader.py` - Content discovery
- `test_website_templates.py` - HTML templates
- `test_website_scripts.py` - JavaScript code
- `test_website_scripts_interaction.py` - JavaScript interactions
- `test_website_styles.py` - CSS styles

**Utilities**:
- `test_utils.py` - Core utility functions
- `test_helpers_extended.py` - Additional helpers
- `test_logging_setup.py` - Logging configuration

### By Speed

**Fast Unit Tests** (<2s each, no Ollama):
- `test_config_loader.py`
- `test_parser.py`
- `test_parser_edge_cases.py`
- `test_utils.py`
- `test_helpers_extended.py`
- `test_cleanup.py`
- `test_outline_generator_noninteractive.py`
- `test_content_analysis.py`
- `test_logging_setup.py`
- All `test_website_*.py` files

**Slow Integration Tests** (10-30s each, require Ollama):
- `test_llm_client.py`
- `test_outline_generator.py`
- `test_content_generators.py`
- `test_new_generators.py`
- `test_pipeline.py`
- `test_json_outline_integration.py`
- `test_pipeline_extended.py`

## Running Test Patterns

### Pattern 1: Fast Development Cycle

```bash
# Run only fast unit tests (~5s)
uv run pytest tests/test_config_loader.py tests/test_parser.py tests/test_utils.py tests/test_cleanup.py
```

### Pattern 2: Full Test Suite

```bash
# Run all tests (auto-starts Ollama if needed, ~150s)
uv run pytest
```

### Pattern 3: Specific Module Tests

```bash
# Test specific module
uv run pytest tests/test_config_loader.py -v

# Test with coverage
uv run pytest tests/test_config_loader.py --cov=src.config --cov-report=html
```

### Pattern 4: Integration Tests Only

```bash
# Run only integration tests (requires Ollama, ~150s)
uv run pytest tests/test_llm_client.py tests/test_outline_generator.py tests/test_content_generators.py tests/test_pipeline.py
```

## Coverage Details

### Without Ollama (Unit Tests Only)

**Overall**: ~30% coverage

**Module Coverage**:
- `config_loader.py`: 95% ✅
- `parser.py`: 80% ✅
- `utils/helpers.py`: 90% ✅
- `processors/cleanup.py`: 85% ✅
- `llm_client.py`: 30% (only init/config without Ollama)

### With Ollama (Full Suite)

**Overall**: ~75% coverage

**Additional Coverage**:
- `llm_client.py`: 85% (with integration tests)
- All format generators: 70-80%
- Pipeline orchestration: 75%
- Outline generation: 80%

**Coverage Gaps**:
- Error edge cases: ~60%
- Complex integration scenarios: ~65%
- Website generation edge cases: ~70%

## Test Fixture Reference

### Auto-Start Mechanism (conftest.py)

```python
@pytest.fixture(scope="session", autouse=True)
def ensure_ollama_running():
    """Auto-starts Ollama if needed, runs once per test session."""
```

### Test Data Fixtures (tests/fixtures/)

| File | Purpose | Used By |
|------|---------|---------|
| `sample_course_config.yaml` | Course configuration example | `test_config_loader.py` |
| `sample_module_info.json` | Module structure (JSON format) | `test_json_outline_integration.py` |
| `sample_outline.json` | Complete JSON outline (2 modules, 6 sessions) | `test_json_outline_integration.py` |
| `sample_markdown_outline.md` | Markdown outline for parser testing | `test_parser.py`, `test_parser_edge_cases.py` |
| `sample_lecture.md` | Example lecture content | `test_content_generators.py` |
| `sample_lab.md` | Example lab exercise | `test_new_generators.py` |
| `sample_study_notes.md` | Example study notes | `test_new_generators.py` |
| `sample_questions.md` | Example questions with answers | `test_content_generators.py` |
| `sample_diagram.mmd` | Example Mermaid diagram | `test_content_generators.py` |

## See Also

- **Test Coverage**: [../docs/TESTING_COVERAGE.md](../docs/TESTING_COVERAGE.md) - Detailed coverage report
- **README**: [README.md](README.md) - Human-readable test guide
- **Development Rules**: [../.cursorrules/03-testing-real-only.md](../.cursorrules/03-testing-real-only.md) - No mocks philosophy
- **Architecture**: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- **Pipeline**: [../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md) - How pipeline uses tests
- **Script Tests**: [../scripts/02_run_tests.py](../scripts/02_run_tests.py) - Test execution script



