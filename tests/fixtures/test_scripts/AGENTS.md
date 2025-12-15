# Test Script Fixtures - For AI Agents

## Purpose

This directory contains fixture copies of pipeline scripts used for testing. These scripts are used to verify script execution, argument parsing, and integration with the test framework.

## Directory Contents

```
tests/fixtures/test_scripts/
├── 01_setup_environment.py
├── 02_run_tests.py
├── 03_generate_outline.py
├── 04_generate_primary.py
├── 05_generate_secondary.py
└── 06_website.py
```

## Usage in Tests

These fixture scripts are used in tests to:
- Verify script execution patterns
- Test argument parsing
- Validate script integration
- Test error handling in scripts

## Relationship to Source Scripts

These are copies or references to scripts in `scripts/`. They may be:
- Exact copies for testing
- Modified versions for test scenarios
- Minimal versions for specific test cases

## Test Patterns

```python
# Example: Testing script execution
from pathlib import Path
import subprocess

def test_script_execution():
    script_path = Path("tests/fixtures/test_scripts/03_generate_outline.py")
    result = subprocess.run(
        ["uv", "run", "python3", str(script_path)],
        capture_output=True
    )
    assert result.returncode == 0
```

## See Also

- **[../../README.md](../../README.md)** - Test suite overview
- **[../../AGENTS.md](../../AGENTS.md)** - Test organization guide
- **[../../../scripts/README.md](../../../scripts/README.md)** - Script documentation
