# Setup Guide

Quick start guide for the educational course Generator.

## Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **uv package manager**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Ollama with gemma3:4b**
   ```bash
   # Install Ollama from https://ollama.ai/
   
   # Pull gemma3:4b model
   ollama pull gemma3:4b
   
   # Verify Ollama is running
   curl http://localhost:11434/api/version
   ```

## Installation

```bash
# Clone repository
cd /path/to/biology

# Install dependencies with uv
uv pip install -e ".[dev]"
```

## Quick Test

The test suite automatically attempts to start Ollama if installed.

```bash
# Run all tests (auto-starts Ollama if installed)
uv run pytest

# If Ollama isn't running, integration tests will be skipped
# Unit tests will still run (~30% coverage without Ollama, ~75% with)

# Run specific test module
uv run pytest tests/test_config_loader.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## Usage

### Generate Course Outline (Stage 1)

```bash
uv run python3 scripts/03_generate_outline.py
```

Output: `output/outlines/course_outline_YYYYMMDD_HHMMSS.md`

### Generate Content for All Modules (Stage 2)

```bash
uv run python3 scripts/04_generate_primary.py --all
```

### Generate Content for Specific Modules

```bash
uv run python3 scripts/04_generate_primary.py --modules 1 2 3
```

### Run Full Pipeline

```bash
uv run python3 scripts/run_pipeline.py
```

Options:
- `--skip-outline` - Skip Stage 1
- `--modules ID [ID ...]` - Only process specific modules
- `--log-level DEBUG` - Set logging verbosity

## Configuration

Edit YAML files in `config/`:

### Course Structure (`config/course_config.yaml`)

Define your course modules, topics, and requirements.

Currently configured with 20 comprehensive biology modules.

### LLM Settings (`config/llm_config.yaml`)

Adjust:
- Model name (default: gemma3:4b)
- Generation parameters (temperature, etc.)
- Prompt templates

### Output Settings (`config/output_config.yaml`)

Configure:
- Output directory paths
- File naming conventions
- Formatting preferences

See `docs/CONFIGURATION.md` for complete reference.

## Verification

### Check Installation

```bash
# Python modules importable
uv run python3 -c "from src.generate.orchestration.pipeline import ContentGenerator; print('✓ Installation OK')"
```

### Check Ollama Connection

```bash
# Verify Ollama is accessible
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:4b",
  "prompt": "Say hello",
  "stream": false
}'
```

### Run Sample Generation

```bash
# Generate outline only (quick test)
uv run python3 scripts/03_generate_outline.py

# Check output
ls -l output/outlines/
```

## Project Structure

```
biology/
├── src/                 # Source code (modular structure)
│   ├── config/          # Configuration management
│   │   └── loader.py    # ConfigLoader class
│   ├── llm/             # LLM integration
│   │   └── client.py    # OllamaClient class
│   ├── generate/        # Content generation
│   │   ├── orchestration/  # Pipeline coordination
│   │   │   └── pipeline.py  # ContentGenerator
│   │   ├── stages/         # Generation stages
│   │   │   └── stage1_outline.py  # OutlineGenerator
│   │   ├── processors/     # Content processing
│   │   │   └── parser.py   # OutlineParser
│   │   └── formats/        # Format generators
│   │       ├── lectures.py
│   │       ├── labs.py
│   │       ├── study_notes.py
│   │       ├── diagrams.py
│   │       └── questions.py
│   ├── utils/           # Utilities
│   │   └── helpers.py    # File I/O, text processing
│   └── website/         # Website generation
│       └── generator.py # WebsiteGenerator
├── config/              # YAML configurations
├── tests/               # Test suite (~540 tests across 25 files)
├── scripts/             # Executable scripts
├── docs/                # Documentation
└── output/              # Generated content (gitignored)
```

## Testing

### Run All Tests

```bash
uv run pytest
```

### Test Coverage

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Specific Components

```bash
# Configuration loading
uv run pytest tests/test_config_loader.py -v

# Content parsing
uv run pytest tests/test_parser.py -v

# Utilities
uv run pytest tests/test_utils.py -v
```

### Integration Tests (Require Ollama)

The test framework automatically starts Ollama if it's installed:

```bash
# These tests auto-start Ollama (requires gemma3:4b model)
uv run pytest tests/test_llm_client.py -v
uv run pytest tests/test_outline_generator.py -v
uv run pytest tests/test_content_generators.py -v
uv run pytest tests/test_pipeline.py -v

# Tests gracefully skip if:
# - Ollama not installed
# - gemma3:4b model not pulled
# - Ollama fails to start
```

## Troubleshooting

### "Ollama connection refused"

```bash
# Start Ollama
ollama serve

# In another terminal, verify
curl http://localhost:11434/api/version
```

### "Model not found"

```bash
# Pull gemma3:4b model
ollama pull gemma3:4b

# List available models
ollama list
```

### "Config file not found"

Ensure you're running from the repository root:
```bash
cd /path/to/biology
ls config/*.yaml  # Should show 3 files
```

### "ModuleNotFoundError: No module named 'src'"

**Problem**: Scripts fail with import errors when run directly.

**Solution**: All scripts now include automatic sys.path manipulation to resolve this. If you still encounter this error, ensure you're using the scripts from the repository (not copied elsewhere), or run them via `uv run python3`:

```python
# This code is already in all scripts
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
```

This allows scripts to be run directly from any location without import errors.

### "Permission denied" on scripts

```bash
chmod +x scripts/*.py
```

### Tests failing

```bash
# Most tests don't require Ollama
# Tests requiring Ollama should skip gracefully

# Run without Ollama-dependent tests
uv run pytest -m "not integration"

# Or just run unit tests
uv run pytest tests/test_config_loader.py tests/test_parser.py tests/test_utils.py
```

## Development

### Code Style

```bash
# Format code
uv run black src/ tests/ scripts/

# Lint
uv run flake8 src/

# Type check
uv run mypy src/
```

### Adding New Modules

1. Create module in `src/`
2. Add tests in `tests/test_<module>.py`
3. Update documentation
4. Run tests

### Modifying Configuration

1. Edit YAML in `config/`
2. Validate: `uv run python3 -c "from src.config.loader import ConfigLoader; ConfigLoader('config').validate_all_configs()"`
3. Test with a small module first

## Performance

Typical generation times (with gemma3:4b on M-series Mac):

- Outline: ~30-60 seconds
- Lecture (3000 words): ~2-3 minutes
- Diagram: ~30-45 seconds
- Questions (20): ~1-2 minutes
- Full module: ~5-7 minutes
- Complete course (20 modules): ~2-3 hours

Times vary based on:
- Hardware
- Model used
- Content length
- Temperature settings

## Next Steps

1. Review generated outline
2. Test with 1-2 modules first
3. Adjust prompts if needed
4. Run full course generation
5. Review and refine output

## Resources

- **Documentation**: `docs/` directory
- **Configuration Guide**: `docs/CONFIGURATION.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **For AI Agents**: `AGENTS.md`
- **Main README**: `README.md`

## Support

Check:
1. This setup guide
2. Documentation in `docs/`
3. Test examples in `tests/`
4. `.cursorrules` for development standards

