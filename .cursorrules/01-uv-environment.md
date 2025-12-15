# Environment Setup - uv Only

## Hard Constraint

**MUST use `uv` for all package management and script execution. Never use `pip` or `venv`.**

## Requirements

### Package Management
- **HARD**: Use `uv` for installing dependencies
- **HARD**: Use `uv pip install` instead of `pip install`
- **HARD**: Use `uv run` for executing scripts
- **HARD**: Never create or use virtual environments manually

### Installation Commands

```bash
# ✅ CORRECT: Install dependencies with uv
uv pip install -e ".[dev]"

# ✅ CORRECT: Run scripts with uv
uv run python3 scripts/03_generate_outline.py

# ✅ CORRECT: Run tests with uv
uv run pytest

# ❌ WRONG: Using pip
pip install -e ".[dev]"

# ❌ WRONG: Using venv
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# ❌ WRONG: Direct python execution (when uv should be used)
python3 scripts/03_generate_outline.py
```

### Script Execution

All scripts in `scripts/` should be executed with `uv run`:

```bash
# Environment setup
uv run python3 scripts/01_setup_environment.py

# Run tests
uv run python3 scripts/02_run_tests.py

# Generate outline
uv run python3 scripts/03_generate_outline.py

# Generate content
uv run python3 scripts/04_generate_primary.py

# Full pipeline
uv run python3 scripts/run_pipeline.py
```

### Testing

```bash
# ✅ CORRECT: Run tests with uv
uv run pytest

# ✅ CORRECT: Run specific test file
uv run pytest tests/test_config_loader.py -v

# ✅ CORRECT: Run with coverage
uv run pytest --cov=src --cov-report=html

# ❌ WRONG: Direct pytest execution
pytest
```

## Rationale

- **Consistency**: Single package manager across all operations
- **Speed**: `uv` is significantly faster than `pip`
- **Simplicity**: No need to manage virtual environments
- **Reliability**: Consistent dependency resolution

## Integration

The system assumes `uv` is available:
- Scripts use `uv run` for execution
- Documentation assumes `uv` commands
- CI/CD should use `uv` for setup

## Error Handling

If `uv` is not available:
- Scripts should check for `uv` and provide clear error messages
- Installation instructions should mention `uv` requirement
- Error messages should guide users to install `uv`

## See Also

- **[../SETUP.md](../SETUP.md)** - Installation instructions
- **[../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)** - Development setup
- **[00-overview.md](00-overview.md)** - Core principles
