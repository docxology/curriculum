# Configuration-Driven Approach

## Hard Constraint

**MUST use YAML configuration files. No hard-coded paths or settings.**

## Configuration Files

All configuration is in YAML files under `config/`:

- `course_config.yaml` - Course structure and metadata
- `llm_config.yaml` - LLM settings and prompt templates
- `output_config.yaml` - Output paths and formatting

## Configuration Loading

**MUST use ConfigLoader for all configuration access:**

```python
# ✅ CORRECT: Use ConfigLoader
from src.config.loader import ConfigLoader

loader = ConfigLoader("config")
loader.validate_all_configs()

course_info = loader.get_course_info()
llm_params = loader.get_llm_parameters()
output_paths = loader.get_output_paths()

# ❌ WRONG: Hard-coded configuration
course_name = "Introductory Biology"  # Should be in config
llm_model = "gemma3:4b"  # Should be in config
output_dir = "output"  # Should be in config
```

## No Hard-Coded Values

### Paths

```python
# ✅ CORRECT: Get paths from config
output_paths = loader.get_output_paths()
output_dir = Path(output_paths["base_directory"])

# ❌ WRONG: Hard-coded paths
output_dir = Path("output")
config_dir = Path("config")
```

### Settings

```python
# ✅ CORRECT: Get settings from config
llm_config = loader.get_llm_parameters()
model = llm_config["model"]
temperature = llm_config["parameters"]["temperature"]

# ❌ WRONG: Hard-coded settings
model = "gemma3:4b"
temperature = 0.7
```

### Prompt Templates

```python
# ✅ CORRECT: Get prompts from config
prompt_config = loader.get_prompt_template("lecture")
system_prompt = prompt_config["system"]
template = prompt_config["template"]

# ❌ WRONG: Hard-coded prompts
system_prompt = "You are an expert educator."
template = "Write a lecture on {topic}."
```

## Configuration Validation

**MUST validate configurations before use:**

```python
# ✅ CORRECT: Validate configs
loader = ConfigLoader("config")
loader.validate_all_configs()  # Raises ConfigurationError if invalid

# ❌ WRONG: Use config without validation
loader = ConfigLoader("config")
config = loader.load_course_config()  # May be invalid
```

## Dynamic Configuration

### JSON Outlines

Modules are loaded from dynamically-generated JSON outlines:

```python
# ✅ CORRECT: Load from JSON outline
modules = loader.get_modules_from_outline()  # Searches for latest

# ❌ WRONG: Hard-coded module structure
modules = [
    {"id": 1, "name": "Cell Biology"},
    {"id": 2, "name": "Genetics"},
]
```

### Course Templates

Course templates allow multiple configurations:

```python
# ✅ CORRECT: Use course template
course_info = loader.get_course_info(course_template="biology")

# ❌ WRONG: Hard-coded course info
course_info = {"name": "Biology", "level": "Introductory"}
```

## Configuration Structure

### Course Config

```yaml
course:
  name: "Introductory Biology"
  description: "Comprehensive course..."
  level: "Undergraduate Introductory"
  defaults:
    num_modules: 5
    total_sessions: 15
```

### LLM Config

```yaml
llm:
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  parameters:
    temperature: 0.7
    top_p: 0.9
```

### Output Config

```yaml
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
    modules: "modules"
```

## Anti-Patterns

❌ **Don't hard-code paths**  
❌ **Don't hard-code settings**  
❌ **Don't hard-code prompts**  
❌ **Don't skip validation**  
❌ **Don't use environment variables for config (use YAML)**

## See Also

- **[../docs/CONFIGURATION.md](../docs/CONFIGURATION.md)** - Complete configuration guide
- **[../src/config/AGENTS.md](../src/config/AGENTS.md)** - ConfigLoader API
- **[../config/README.md](../config/README.md)** - Configuration files guide
