# Test Fixtures - For AI Agents

## Purpose

This directory contains test fixtures - sample data files used in tests. Fixtures provide real test data without requiring external dependencies.

## Directory Structure

```
tests/fixtures/
├── test_scripts/          # Script fixtures for testing
│   ├── 01_setup_environment.py
│   ├── 02_run_tests.py
│   └── ...
└── [other fixture files]  # Sample data files
```

## Fixture Usage

### In Tests

```python
# ✅ CORRECT: Load real fixture data
from pathlib import Path
import json

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

### Fixture Types

- **JSON files**: Sample outlines, configurations
- **Markdown files**: Sample content
- **YAML files**: Sample configurations
- **Script files**: Test script fixtures (in `test_scripts/`)

## Creating Fixtures

### From Real Data

```python
# ✅ CORRECT: Save real data as fixture
def create_fixture():
    loader = ConfigLoader("config")
    config = loader.load_course_config()
    
    fixture_path = Path("tests/fixtures/sample_config.json")
    fixture_path.write_text(json.dumps(config, indent=2))
```

### Manual Creation

Create fixture files manually with realistic test data that represents actual system data structures.

## Testing Philosophy

Fixtures follow the "NO MOCKS EVER" principle:
- Use real data structures
- Represent actual system formats
- Enable tests to verify real behavior

## See Also

- **[../AGENTS.md](../AGENTS.md)** - Test suite organization
- **[../README.md](../README.md)** - Test documentation
- **[test_scripts/AGENTS.md](test_scripts/AGENTS.md)** - Test script fixtures
- **[../../.cursorrules/03-testing-real-only.md](../../.cursorrules/03-testing-real-only.md)** - Testing philosophy
