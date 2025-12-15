# Testing - NO MOCKS EVER

## Hard Constraint

**MUST use real implementations in tests. NO MOCK METHODS EVER.**

## Core Principle

All tests interact with actual services, real data, and real implementations. Tests skip gracefully if external dependencies are unavailable.

## Testing Philosophy

### Real Implementations Only

```python
# ✅ CORRECT: Real ConfigLoader
from src.config.loader import ConfigLoader

def test_config_loading():
    loader = ConfigLoader("config")
    config = loader.load_course_config()
    assert config["course"]["name"] == "Introductory Biology"

# ✅ CORRECT: Real OllamaClient (with skip if unavailable)
import pytest
from src.llm.client import OllamaClient

@pytest.mark.skipif(not ollama_available(), reason="Ollama not available")
def test_llm_generation():
    client = OllamaClient(llm_config)
    response = client.generate("Test prompt")
    assert len(response) > 0

# ❌ WRONG: Mocking ConfigLoader
from unittest.mock import Mock

def test_config_loading():
    mock_loader = Mock()
    mock_loader.load_course_config.return_value = {"course": {"name": "Test"}}
    # This violates the NO MOCKS rule

# ❌ WRONG: Mocking LLM client
from unittest.mock import patch

@patch('src.llm.client.OllamaClient')
def test_generation(mock_client):
    # This violates the NO MOCKS rule
    pass
```

### Test Fixtures

Use real test data from fixtures:

```python
# ✅ CORRECT: Real fixture data
import pytest
from pathlib import Path

@pytest.fixture
def sample_outline():
    """Load real outline from fixture."""
    fixture_path = Path("tests/fixtures/sample_outline.json")
    return json.loads(fixture_path.read_text())

def test_parser(sample_outline):
    parser = OutlineParser()
    modules = parser.parse_outline(sample_outline)
    assert len(modules) > 0
```

### Graceful Skipping

Tests should skip if dependencies unavailable:

```python
# ✅ CORRECT: Skip if Ollama unavailable
import pytest
from src.utils.helpers import check_ollama_available

@pytest.mark.skipif(
    not check_ollama_available(),
    reason="Ollama not available"
)
def test_llm_integration():
    # Real LLM test
    pass
```

## Test Organization

### Unit Tests
- Fast tests (<2s total)
- No external dependencies
- Real implementations with fixtures
- Examples: `test_config_loader.py`, `test_parser.py`, `test_utils.py`

### Integration Tests
- Slower tests (~150s total)
- Require Ollama + model
- Real LLM interactions
- Skip gracefully if unavailable
- Examples: `test_llm_client.py`, `test_outline_generator.py`, `test_content_generators.py`

## Test Data

### Fixtures Directory

Use real test data from `tests/fixtures/`:
- Sample outlines (JSON)
- Sample content (markdown)
- Sample configurations (YAML)

### Creating Fixtures

```python
# ✅ CORRECT: Save real data as fixture
def create_fixture():
    loader = ConfigLoader("config")
    config = loader.load_course_config()
    
    fixture_path = Path("tests/fixtures/sample_config.json")
    fixture_path.write_text(json.dumps(config, indent=2))
```

## Error Handling in Tests

Tests should handle real errors gracefully:

```python
# ✅ CORRECT: Handle real errors
from src.config.loader import ConfigurationError

def test_invalid_config():
    with pytest.raises(ConfigurationError):
        loader = ConfigLoader("invalid_path")
        loader.validate_all_configs()
```

## Coverage

- **Unit tests**: ~30% coverage (no Ollama)
- **Integration tests**: ~75% coverage (with Ollama)
- Tests skip if dependencies unavailable (don't fail)

## Running Tests

```bash
# Unit tests only (fast, no Ollama required)
uv run pytest tests/test_config_loader.py tests/test_parser.py

# All tests (includes integration, requires Ollama)
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html
```

## Anti-Patterns

❌ **Don't use `unittest.mock`**  
❌ **Don't use `pytest.fixture` with mocks**  
❌ **Don't patch external dependencies**  
❌ **Don't create fake implementations for testing**  
❌ **Don't fail tests if external dependencies unavailable (skip instead)**

## Rationale

- **Real behavior**: Tests verify actual system behavior
- **Integration confidence**: Tests catch real integration issues
- **Documentation**: Tests serve as usage examples
- **Maintenance**: Real tests are easier to maintain

## See Also

- **[../docs/TESTING_COVERAGE.md](../docs/TESTING_COVERAGE.md)** - Test suite overview
- **[../tests/AGENTS.md](../tests/AGENTS.md)** - Test organization
- **[../tests/README.md](../tests/README.md)** - Test documentation
