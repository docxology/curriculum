# Configuration Files - For AI Agents

## Purpose

This directory contains YAML configuration files that control all aspects of educational course generation. Scripts automatically discover and load these files from this location.

## Configuration Files

### course_config.yaml
**Course structure and metadata (default template)**

Defines course-level information and dynamic module generation parameters:
- Course name, description, level, duration
- Configurable defaults (`num_modules`, `total_sessions`, `sessions_per_module`)
- Additional constraints for LLM-guided module generation

**Key sections**:
```yaml
course:
  name: "Course name"
  description: "..."
  level: "Undergraduate"
  defaults:
    num_modules: 5          # How many modules to generate
    total_sessions: 15       # Total class sessions
  additional_constraints: ""  # Optional: Additional requirements or constraints
```

**Used by**: Stages 03 (outline generation)

**Note**: This is the default template. You can also use pre-set course templates from `courses/` directory (see Course Templates section below).

### courses/ Directory
**Pre-set course templates**

Contains multiple course configuration templates that can be selected interactively or via `--course` flag.

**Directory structure**:
```
config/
├── course_config.yaml      # Default template
├── courses/                # Pre-set course templates
│   ├── biology.yaml
│   ├── chemistry.yaml
│   └── physics.yaml
├── llm_config.yaml
└── output_config.yaml
```

**Template format**: Each template file follows the same structure as `course_config.yaml`:
```yaml
course:
  name: "Introductory Biology"
  subject: "General Biology"
  description: "Comprehensive introduction covering fundamental concepts..."
  level: "Undergraduate Introductory"
  defaults:
    num_modules: 2
    total_sessions: 4
  additional_constraints: ""
```

**Usage**:
- **Interactive mode**: Scripts show a numbered menu of available templates
- **Command-line**: Use `--course` flag: `--course biology`
- **Default**: If no template selected, uses `course_config.yaml`

**Creating new templates**:
1. Copy an existing template from `courses/` directory
2. Edit course metadata (name, description, level, defaults)
3. Save as `courses/your_course.yaml`
4. Template will appear in selection menu automatically

### llm_config.yaml
**LLM settings and prompt templates**

Configures Ollama integration and all content generation prompts:
- LLM provider settings (model, API URL, timeout)
- Generation parameters (temperature, num_predict, num_ctx)
- Outline generation bounds (`items_per_field`)
- Prompt templates for all content types

**Key sections**:
```yaml
llm:
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  parameters:
    temperature: 0.7
    num_predict: 64000   # 128K context allows up to 64K output tokens

outline_generation:
  items_per_field:
    subtopics: {min: 3, max: 7}
    learning_objectives: {min: 3, max: 7}
    key_concepts: {min: 3, max: 7}

prompts:
  lecture:
    system: "..."
    template: "..."
```

**Used by**: All generation stages (03, 04, 05)

### output_config.yaml
**Output paths and file naming**

Controls where and how generated content is saved:
- Base output directory (course-specific subdirectories created automatically when using course templates)
- Subdirectories for each content type
- File naming patterns
- Logging configuration

**Key sections**:
```yaml
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
    modules: "modules"
    logs: "logs"
  file_naming:
    outline: "course_outline_{timestamp}.md"
  logging:
    level: "INFO"
    file: true
```

**Used by**: All stages

## Configuration Discovery

### How Scripts Find Configurations

All scripts use consistent configuration discovery:

```python
from src.config.loader import ConfigLoader

# Default: looks in ../config relative to script
loader = ConfigLoader("config")

# Or override with command-line argument
# scripts --config-dir /custom/path/to/config
```

**Default search pattern**:
1. Command-line `--config-dir` argument (if provided)
2. `Path(__file__).parent.parent / "config"` (relative to script location)
3. Raises `ConfigurationError` if not found

**All 6 scripts support `--config-dir`**:
- `01_setup_environment.py --config-dir PATH`
- `02_run_tests.py --config-dir PATH`
- `03_generate_outline.py --config-dir PATH`
- `04_generate_primary.py --config-dir PATH`
- `05_generate_secondary.py --config-dir PATH`
- `run_pipeline.py --config-dir PATH`

### Validation

ConfigLoader validates all configurations on load:
- Required fields present
- YAML syntax correct
- Types match expectations
- Cross-references valid

```python
loader = ConfigLoader("config")
loader.validate_all_configs()  # Raises ConfigurationError if invalid
```

## Common Modifications

### Adjust Course Structure

**Option 1: Edit default template**
Edit `course_config.yaml`:
```yaml
course:
  defaults:
    num_modules: 8           # Generate 8 modules instead of 5
    total_sessions: 24       # 24 total class sessions
```

**Option 2: Use pre-set template**
Select from available templates:
```bash
# Interactive selection
uv run python3 scripts/03_generate_outline.py

# Or specify directly
uv run python3 scripts/03_generate_outline.py --course biology
```

**Option 3: Create custom template**
1. Copy `courses/biology.yaml` to `courses/my_course.yaml`
2. Edit the template with your course details
3. Use it: `--course my_course`

### Change LLM Model

Edit `llm_config.yaml`:
```yaml
llm:
  model: "llama3.1:latest"  # Use different model
```

Ensure model is pulled: `ollama pull llama3.1:latest`

### Adjust Content Bounds

Edit `llm_config.yaml`:
```yaml
outline_generation:
  items_per_field:
    subtopics: {min: 5, max: 10}      # More subtopics per session
    learning_objectives: {min: 4, max: 8}
```

### Modify Prompt Templates

Edit `llm_config.yaml`:
```yaml
prompts:
  lecture:
    system: "You are an expert {subject} educator."
    template: |
      Generate lecture content for: {module_name}
      
      Subtopics: {subtopics}
      
      Include:
      - Clear explanations
      - Examples
      - Key takeaways
```

### Change Output Location

Edit `output_config.yaml`:
```yaml
output:
  base_directory: "generated_content"  # Custom output folder
```

Or use command-line override:
```bash
uv run python3 scripts/03_generate_outline.py --output-dir custom_output
```

## Configuration Loading API

### Basic Usage

```python
from src.config.loader import ConfigLoader

# Initialize
loader = ConfigLoader("config")

# Get course metadata
course_info = loader.get_course_info()
# Returns: {"name": "...", "description": "...", "level": "..."}

# Get course defaults
defaults = loader.get_course_defaults()
# Returns: {"num_modules": 5, "total_sessions": 15, ...}

# Get course defaults
defaults = loader.get_course_defaults()
# Returns: {"num_modules": 5, "total_sessions": 15, "sessions_per_module": None}

# Get LLM parameters
llm_params = loader.get_llm_parameters()
# Returns: {"model": "gemma3:4b", "api_url": "...", "parameters": {...}}

# Get prompt template
lecture_prompt = loader.get_prompt_template("lecture")
# Returns: {"system": "...", "template": "..."}

# Get output paths
output_paths = loader.get_output_paths()
# Returns: {"base_directory": "output", "directories": {...}}
```

### Advanced Usage

```python
# Load specific configs
course_config = loader.load_course_config()
llm_config = loader.load_llm_config()
output_config = loader.load_output_config()

# Get module from JSON outline (new dynamic approach)
modules = loader.get_modules_from_outline()
# Searches multiple locations for latest course_outline_*.json

# Get specific module by ID
module = loader.get_module_by_id(1, from_outline=True)
```

## Validation Guidelines

Before running pipeline, validate configurations:

```bash
# Stage 01 validates automatically
uv run python3 scripts/01_setup_environment.py

# Or validate programmatically
uv run python3 -c "from src.config.loader import ConfigLoader; ConfigLoader('config').validate_all_configs(); print('✓ Valid')"
```

**Validation checks**:
- ✓ All YAML files parse correctly
- ✓ Required fields present in all configs
- ✓ Course has name, description, level
- ✓ Defaults have valid num_modules and total_sessions
- ✓ LLM config has model and prompts sections
- ✓ Output config specifies base directory

## Troubleshooting

### "Config directory not found"

Ensure `config/` exists relative to where you're running scripts from, or use `--config-dir`:
```bash
uv run python3 scripts/run_pipeline.py --config-dir /path/to/config
```

### "Config file not found: course_config.yaml"

Check all three files exist:
```bash
ls -la config/
# Should show: course_config.yaml, llm_config.yaml, output_config.yaml
```

### "Invalid YAML in course_config.yaml"

YAML syntax error. Validate with:
```bash
python3 -c "import yaml; yaml.safe_load(open('config/course_config.yaml'))"
```

### "Missing required field: model"

LLM config is incomplete. Ensure all required fields present.

### Configuration not taking effect

- Clear any cached configs: Restart Python interpreter
- Check file permissions: Ensure files are readable
- Verify no typos in field names
- Check YAML indentation (spaces, not tabs)

## Best Practices

✅ **Version control configurations** - Track changes in git  
✅ **Use defaults when possible** - Override only what's needed  
✅ **Validate before running** - Use stage 01 to validate  
✅ **Document custom changes** - Add comments in YAML  
✅ **Keep backups** - Copy before major edits  
✅ **Test with small values** - Try `num_modules: 1` first  
✅ **Use consistent paths** - Stick to `config/` directory  

## Complete YAML Structure Reference

### course_config.yaml Structure

```yaml
course:
  name: "Course Name"                    # Required
  description: "Course description"      # Required
  level: "Introductory"                  # Required (Introductory, Undergraduate, Graduate)
  estimated_duration_weeks: 16           # Optional
  
  defaults:
    num_modules: 20                      # Required: Number of modules to generate
    total_sessions: 40                   # Required: Total class sessions
    sessions_per_module: 2               # Optional: Auto-calculated if not provided
  
  additional_constraints: ""            # Optional: Additional requirements for LLM
```

### llm_config.yaml Structure

```yaml
llm:
  model: "gemma3:4b"                     # Required: Ollama model name
  api_url: "http://localhost:11434/api/generate"  # Required: Ollama API endpoint
  timeout: 120                           # Required: Request timeout in seconds
  
  parameters:
    temperature: 0.7                      # Optional: Randomness (0.0-1.0)
    top_p: 0.9                           # Optional: Nucleus sampling
    top_k: 40                            # Optional: Top-k sampling
    num_predict: 64000                  # Optional: Maximum generation tokens (128K context allows up to 64K output)
    num_ctx: 128000                     # Optional: Context window size (128K for gemma3:4b)

outline_generation:
  items_per_field:
    subtopics: {min: 3, max: 7}         # Required: Bounds for subtopics per session
    learning_objectives: {min: 3, max: 7}  # Required: Bounds for objectives per session
    key_concepts: {min: 3, max: 7}      # Required: Bounds for concepts per session

prompts:
  outline:
    system: "System prompt..."           # Required
    template: "Template with {variables}"  # Required
  lecture:
    system: "System prompt..."
    template: "Template..."
  # ... (lab, study_notes, diagram, questions)
```

### output_config.yaml Structure

```yaml
output:
  base_directory: "output"               # Required: Base output directory
  
  directories:
    outlines: "outlines"                 # Required: Outline output directory
    modules: "modules"                   # Required: Module content directory
    logs: "logs"                        # Required: Log files directory
    website: "website"                  # Required: Website output directory
  
  file_naming:
    outline: "course_outline_{timestamp}.md"  # Optional: Outline filename pattern
  
  logging:
    level: "INFO"                       # Optional: Log level (DEBUG, INFO, WARNING, ERROR)
    file: true                          # Optional: Enable file logging
```

## Validation Rules Reference

### Course Config Validation

- ✓ `course` section must exist
- ✓ `course.name` must be non-empty string
- ✓ `course.description` must be non-empty string
- ✓ `course.level` must be one of: "Introductory", "Undergraduate", "Graduate"
- ✓ `course.defaults.num_modules` must be positive integer
- ✓ `course.defaults.total_sessions` must be positive integer
- ✓ `num_modules <= total_sessions` (logical constraint)

### LLM Config Validation

- ✓ `llm` section must exist
- ✓ `llm.model` must be non-empty string
- ✓ `llm.api_url` must be valid URL
- ✓ `llm.timeout` must be positive integer
- ✓ `prompts` section must exist
- ✓ All required prompt templates must exist (outline, lecture, lab, study_notes, diagram, questions)
- ✓ `outline_generation.items_per_field` must have min/max for subtopics, learning_objectives, key_concepts

### Output Config Validation

- ✓ `output` section must exist
- ✓ `output.base_directory` must be non-empty string
- ✓ All required directories must be specified

## Troubleshooting Guide

### "Config directory not found"

**Error**: `ConfigurationError: Config directory not found: {path}`

**Solutions**:
1. Ensure `config/` directory exists relative to script location
2. Use `--config-dir` to specify custom path: `--config-dir /path/to/config`
3. Check current working directory

### "Config file not found"

**Error**: `ConfigurationError: Config file not found: {filepath}`

**Solutions**:
1. Ensure all three files exist: `course_config.yaml`, `llm_config.yaml`, `output_config.yaml`
2. Check file names (case-sensitive)
3. Verify file permissions (must be readable)

### "Invalid YAML"

**Error**: `ConfigurationError: Invalid YAML in {filename}: {error}`

**Solutions**:
1. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('config/course_config.yaml'))"`
2. Check indentation (use spaces, not tabs)
3. Verify all quotes are properly closed
4. Check for special characters that need escaping

### "Missing required field"

**Error**: `ConfigurationError: Missing required field '{field}' in {context}`

**Solutions**:
1. Add missing field to configuration file
2. Check field name spelling (case-sensitive)
3. Verify field is at correct nesting level
4. See validation rules above for required fields

### "No course outline JSON found"

**Error**: `ConfigurationError: No course outline JSON found...`

**Solutions**:
1. Generate outline: `uv run python3 scripts/03_generate_outline.py --no-interactive`
2. Check outline exists in expected locations:
   - `output/outlines/course_outline_*.json`
   - `scripts/output/outlines/course_outline_*.json`
   - Config-specified directory
3. Verify outline file is valid JSON

## See Also

- **Complete Reference**: [../docs/CONFIGURATION.md](../docs/CONFIGURATION.md) - Full YAML reference
- **ConfigLoader API**: [../src/config/AGENTS.md](../src/config/AGENTS.md) - Configuration loading API
- **README**: [README.md](README.md) - Human-readable guide with examples
- **Scripts**: [../scripts/AGENTS.md](../scripts/AGENTS.md) - How scripts use configs
- **Pipeline Guide**: [../docs/PIPELINE_GUIDE.md](../docs/PIPELINE_GUIDE.md) - End-to-end workflow




