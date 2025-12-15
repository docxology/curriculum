# Configuration Management Module

YAML configuration loading and validation for the educational course generator.

## Module Purpose

Provides `ConfigLoader` class for loading, caching, and validating all YAML configuration files (course structure, LLM settings, output paths).

## Key Class: ConfigLoader

```python
from src.config.loader import ConfigLoader, ConfigurationError
from pathlib import Path
from typing import Dict, List, Optional, Any
```

### Class Signature

```python
class ConfigLoader:
    def __init__(self, config_dir: Union[str, Path]) -> None
    """
    Initialize ConfigLoader with configuration directory.
    
    Args:
        config_dir: Path to directory containing YAML config files
        
    Raises:
        ConfigurationError: If config directory doesn't exist
    """
```

### Initialization

```python
# Default config directory
loader = ConfigLoader("config")

# Custom directory
loader = ConfigLoader("/path/to/configs")

# With Path object
loader = ConfigLoader(Path("config"))

# Raises ConfigurationError if directory doesn't exist
```

### Loading Configurations

```python
# Load individual configs (cached after first load)
course_config = loader.load_course_config()
llm_config = loader.load_llm_config()
output_config = loader.load_output_config()

# Get course metadata
course_info = loader.get_course_info()
# Returns: {"name": "...", "description": "...", "level": "..."}

# Get all modules
modules = loader.get_modules()
# Returns: List[Dict] with 20 modules

# Get specific module
module = loader.get_module_by_id(1)
# Returns: Dict with module 1 data or None

# Get LLM parameters
llm_params = loader.get_llm_parameters()
# Returns: {"model": "gemma3:4b", "api_url": "...", "parameters": {...}}

# Get prompt template
lecture_prompt = loader.get_prompt_template("lecture")
# Returns: {"system": "...", "template": "..."}
# Available templates: outline, lecture, lab, study_notes, diagram, questions

# Get output paths
output_paths = loader.get_output_paths()
# Returns: {"base_dir": "...", "lectures_dir": "...", ...}
```

### Complete Method Signature Reference

#### Configuration Loading Methods

```python
def load_course_config(self) -> Dict[str, Any]
    """Load course_config.yaml (cached after first call)."""

def load_llm_config(self) -> Dict[str, Any]
    """Load llm_config.yaml (cached after first call)."""

def load_output_config(self) -> Dict[str, Any]
    """Load output_config.yaml (cached after first call)."""
```

#### Course Information Methods

```python
def get_course_info(self, course_template: Optional[str] = None) -> Dict[str, str]
    """
    Get course metadata: name, description, level.
    
    Args:
        course_template: Optional course template name from config/courses/.
                       If None, uses default course_config.yaml.
    
    Returns:
        {"name": "...", "description": "...", "level": "...", "subject": "..."}
    """

def get_course_defaults(self) -> Dict[str, Any]
    """Get course defaults: num_modules, total_sessions, sessions_per_module."""
    # Returns: {"num_modules": 20, "total_sessions": 40, "sessions_per_module": 2}
```

#### Course Template Methods

```python
def list_available_courses(self) -> List[Dict[str, Any]]
    """
    List available course templates from config/courses/ directory.
    
    Scans config/courses/ for YAML files and returns metadata about each template.
    
    Returns:
        List of dictionaries with:
        - name: Course template name (filename without .yaml)
        - filename: Full filename (e.g., "biology.yaml")
        - course_info: Course metadata dict (name, description, level, subject)
    
    Example:
        >>> courses = loader.list_available_courses()
        >>> # Returns: [
        >>> #     {"name": "biology", "filename": "biology.yaml", "course_info": {...}},
        >>> #     {"name": "chemistry", "filename": "chemistry.yaml", "course_info": {...}},
        >>> #     ...
        >>> # ]
    
    Note:
        Returns empty list if config/courses/ directory doesn't exist.
    """

def load_course_template(self, course_name: str) -> Dict[str, Any]
    """
    Load a specific course template from config/courses/.
    
    Args:
        course_name: Name of the course template (filename without .yaml extension)
                    (e.g., "biology", "chemistry")
    
    Returns:
        Full course configuration dictionary (same structure as load_course_config()):
        {
            "course": {
                "name": "...",
                "description": "...",
                "level": "...",
                "defaults": {...}
            }
        }
    
    Raises:
        ConfigurationError: If course template not found or invalid YAML
    
    Example:
        >>> template = loader.load_course_template("biology")
        >>> course_info = template["course"]
        >>> # Returns: {"name": "Introductory Biology", ...}
    """

def load_course_config(self, course_template: Optional[str] = None) -> Dict[str, Any]
    """
    Load course configuration from template or default.
    
    Args:
        course_template: Optional course template name from config/courses/.
                         If None, loads default course_config.yaml.
    
    Returns:
        Course configuration dictionary with "course" key
    
    Example:
        >>> # Load default
        >>> config = loader.load_course_config()
        
        >>> # Load from template
        >>> config = loader.load_course_config("biology")
    
    Note:
        Default config is cached after first load. Template configs are not cached.
    """

#### Module Loading Methods (JSON Outline)

```python
def get_modules_from_outline(
    self, 
    outline_path: Optional[Path] = None
) -> List[Dict[str, Any]]
    """
    Load all modules from JSON outline.
    
    Args:
        outline_path: Optional specific outline file path.
                     If None, searches multiple locations for most recent.
    
    Returns:
        List of module dictionaries with structure:
        [
            {
                "module_id": 1,
                "module_name": "...",
                "module_description": "...",
                "sessions": [...]
            },
            ...
        ]
    
    Raises:
        ConfigurationError: If no outline found or invalid JSON
    """

def get_module_by_id_from_outline(
    self, 
    module_id: int, 
    outline_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]
    """
    Get specific module by ID from JSON outline.
    
    Args:
        module_id: Module ID (1-indexed)
        outline_path: Optional specific outline file path
    
    Returns:
        Module dictionary or None if not found
    """

def get_modules(self) -> List[Dict[str, Any]]
    """Convenience method: same as get_modules_from_outline()."""

def get_module_by_id(self, module_id: int) -> Optional[Dict[str, Any]]
    """Convenience method: same as get_module_by_id_from_outline(module_id)."""
```

#### LLM Configuration Methods

```python
def get_llm_parameters(self) -> Dict[str, Any]
    """
    Get LLM configuration parameters.
    
    Returns:
        {
            "model": "gemma3:4b",
            "api_url": "http://localhost:11434/api/generate",
            "timeout": 120,
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                ...
            }
        }
    """

def get_prompt_template(self, template_name: str) -> Dict[str, str]
    """
    Get prompt template by name.
    
    Args:
        template_name: Template name (outline, lecture, lab, study_notes, diagram, questions)
    
    Returns:
        {"system": "...", "template": "..."}
    
    Raises:
        ConfigurationError: If template not found
    """
```

#### Output Configuration Methods

```python
def get_output_paths(self) -> Dict[str, str]
    """
    Get output directory paths.
    
    Returns:
        {
            "base_directory": "output",
            "directories": {
                "outlines": "outlines",
                "modules": "modules",
                "logs": "logs",
                ...
            }
        }
    """
```

#### Validation Methods

```python
def validate_course_config(self) -> None
    """Validate course_config.yaml structure."""
    # Raises ConfigurationError if invalid

def validate_all_configs(self) -> None
    """Validate all configuration files."""
    # Raises ConfigurationError if any invalid
```

### Loading Modules from JSON Outlines

Modules are loaded from dynamically-generated JSON outlines instead of static YAML configuration.

```python
from src.config.loader import ConfigLoader
from pathlib import Path

loader = ConfigLoader("config")

# Load all modules from latest outline (searches multiple locations)
modules = loader.get_modules_from_outline()
# Returns: [{"module_id": 1, "module_name": "...", "sessions": [...]}, ...]

# Load from specific outline file
modules = loader.get_modules_from_outline(
    Path("output/outlines/course_outline_20241208.json")
)

# Get specific module by ID
module = loader.get_module_by_id_from_outline(1)
# Returns: {"module_id": 1, "module_name": "...", "sessions": [...]}

# Get module from specific outline
module = loader.get_module_by_id_from_outline(
    1, 
    Path("output/outlines/course_outline_20241208.json")
)

# Convenience methods (same as above)
modules = loader.get_modules()  # Same as get_modules_from_outline()
module = loader.get_module_by_id(1)  # Same as get_module_by_id_from_outline()
```

**JSON Outline Discovery Algorithm**:

ConfigLoader searches multiple locations for JSON outlines (returns most recent by modification time):

1. **Explicit path** (if provided): Use the specified `outline_path`
2. **Config-specified directory**: `{base_directory}/outlines/` from `output_config.yaml`
3. **Project root**: `output/outlines/` (relative to project root)
4. **Scripts directory**: `scripts/output/outlines/` (common when run from scripts/)

**Search order**:
```python
# Internal search logic (pseudo-code)
def _find_latest_outline(self) -> Optional[Path]:
    search_paths = [
        Path(self.output_config["base_directory"]) / "outlines",
        Path("output") / "outlines",
        Path("scripts") / "output" / "outlines"
    ]
    
    all_outlines = []
    for search_path in search_paths:
        if search_path.exists():
            all_outlines.extend(search_path.glob("course_outline_*.json"))
    
    if not all_outlines:
        return None
    
    # Return most recent by modification time
    return max(all_outlines, key=lambda p: p.stat().st_mtime)
```

**Error handling**:
- If no outline found: Raises `ConfigurationError` with message: "No course outline JSON found. Generate outline first with: uv run python3 scripts/03_generate_outline.py"
- If invalid JSON: Raises `ConfigurationError` with YAML parsing error details
- If outline missing required fields: Raises `ConfigurationError` with specific missing field

**Module Structure from JSON**:
```python
{
    "module_id": 1,
    "module_name": "Cell Biology",
    "module_description": "Introduction to cells",
    "sessions": [
        {
            "session_number": 1,
            "session_title": "Cell Structure",
            "subtopics": ["Prokaryotes", "Eukaryotes"],
            "learning_objectives": ["Understand cell types"],
            "key_concepts": ["Cell membrane", "Organelles"],
            "rationale": "Foundation for biology"
        }
    ]
```

### Using Course Templates

Course templates allow you to use pre-configured course settings from `config/courses/` directory.

```python
from src.config.loader import ConfigLoader

loader = ConfigLoader("config")

# List available course templates
courses = loader.list_available_courses()
# Returns: [
#     {"name": "biology", "filename": "biology.yaml", "course_info": {...}},
#     {"name": "chemistry", "filename": "chemistry.yaml", "course_info": {...}},
#     ...
# ]

# Load a specific course template
template = loader.load_course_template("biology")
course_info = template["course"]
# Returns: {"name": "Introductory Biology", "description": "...", ...}

# Get course info from template
course_info = loader.get_course_info(course_template="biology")
# Returns: {"name": "Introductory Biology", ...}

# Load full config from template
config = loader.load_course_config(course_template="biology")
# Returns: {"course": {...}} (same structure as default)
```

**Template Directory Structure**:
```
config/
├── course_config.yaml      # Default template
├── courses/                # Pre-set templates
│   ├── biology.yaml
│   ├── chemistry.yaml
│   └── physics.yaml
```

**Template File Format**:
Each template in `config/courses/` follows the same structure as `course_config.yaml`:
```yaml
course:
  name: "Introductory Biology"
  subject: "General Biology"
  description: "Comprehensive introduction..."
  level: "Undergraduate Introductory"
  defaults:
    num_modules: 2
    total_sessions: 4
  additional_constraints: ""
```

**Usage in Scripts**:
- **Interactive mode**: Scripts show a numbered menu of available templates
- **Command-line**: Use `--course` flag: `--course biology`
- **Programmatic**: Pass `course_template` parameter to `get_course_info()` or `load_course_config()`

**Error Handling**:
- If template not found: Raises `ConfigurationError` with list of available courses
- If invalid YAML: Raises `ConfigurationError` with parsing error details
- If `config/courses/` doesn't exist: `list_available_courses()` returns empty list (graceful degradation)
}
```

### Validation

```python
# Validate course config
loader.validate_course_config()

# Validate all configs
loader.validate_all_configs()

# Both raise ConfigurationError if validation fails
```

## Exception Handling

```python
from src.config.loader import ConfigurationError

try:
    loader = ConfigLoader("config")
    loader.validate_all_configs()
    module = loader.get_module_by_id(1)
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    # Handle missing files, invalid YAML, missing fields
```

## Configuration Files

### course_config.yaml

Required structure (dynamic module generation):
```yaml
course:
  name: "Course Name"
  description: "Description"
  level: "Introductory"
  estimated_duration_weeks: 16
  
  defaults:
    num_modules: 20           # Number of modules to generate
    total_sessions: 40        # Total class sessions
    sessions_per_module: 2    # Average sessions per module (optional, auto-calculated)
  
  additional_constraints: ""   # Optional: Additional requirements or topic guidance
```

**Note**: Modules are no longer statically defined in YAML. They are generated dynamically by the LLM based on course metadata and additional constraints, then saved as JSON outlines. The LLM generates all topics based on the course description and constraints.

### llm_config.yaml

Required structure:
```yaml
llm:
  model: "gemma3:4b"
  api_url: "http://localhost:11434/api/generate"
  timeout: 120
  parameters:
    temperature: 0.7
    
prompts:
  outline:
    system: "System prompt"
    template: "Template with {variables}"
```

### output_config.yaml

Required structure:
```yaml
output:
  base_directory: "output"
  directories:
    outlines: "outlines"
    modules: "modules"  # Session-based structure: modules/module_XX/session_YY/
    logs: "logs"
    website: "website"
```

## Integration with Pipeline

```python
from src.config.loader import ConfigLoader
from src.llm.client import OllamaClient
from src.generate.formats.lectures import LectureGenerator

# Initialize configuration
loader = ConfigLoader("config")
loader.validate_all_configs()

# Create LLM client with config
llm_config = loader.get_llm_parameters()
llm_client = OllamaClient(llm_config)

# Create content generators
lecture_gen = LectureGenerator(loader, llm_client)

# Generate content for module
module = loader.get_module_by_id(1)
lecture = lecture_gen.generate_lecture(module)
```

## Validation Rules

**Course Config**:
- Must have `course` and `modules` sections
- Course must have `name`, `description`, `level`
- Must have at least one module
- Each module must have: `id`, `name`, `subtopics`, `learning_objectives`, `content_length`, `num_diagrams`, `num_questions`

**LLM Config**:
- Must have `llm` section
- Must have `prompts` section
- Model name required in `llm.model`

**Output Config**:
- Must have `output` section

## Common Tasks

### Load and Iterate Modules

```python
loader = ConfigLoader("config")
modules = loader.get_modules()

for module in modules:
    print(f"Module {module['id']}: {module['name']}")
    print(f"  Subtopics: {len(module['subtopics'])}")
    print(f"  Objectives: {len(module['learning_objectives'])}")
```

### Get Custom Prompt Template

```python
loader = ConfigLoader("config")

try:
    template = loader.get_prompt_template("custom_template")
    system_prompt = template["system"]
    prompt_text = template["template"]
except ConfigurationError as e:
    print(f"Template not found: {e}")
```

### Validate Before Processing

```python
from src.config.loader import ConfigLoader, ConfigurationError

def setup_pipeline(config_dir: str):
    try:
        loader = ConfigLoader(config_dir)
        loader.validate_all_configs()
        logger.info("Configuration validated successfully")
        return loader
    except ConfigurationError as e:
        logger.error(f"Invalid configuration: {e}")
        raise
```

## Error Handling Strategy

The module uses `ConfigurationError` exceptions with clear, actionable messages:

### Error Types and Messages

#### Configuration Directory Errors

```python
# Error: Config directory not found
ConfigurationError("Config directory not found: {path}")

# Example:
# ConfigurationError("Config directory not found: /invalid/path")
```

**Solution**: Ensure config directory exists or use correct path.

#### Configuration File Errors

```python
# Error: Missing config file
ConfigurationError("Config file not found: {filepath}")

# Example:
# ConfigurationError("Config file not found: config/course_config.yaml")
```

**Solution**: Ensure all three config files exist: `course_config.yaml`, `llm_config.yaml`, `output_config.yaml`.

#### YAML Parsing Errors

```python
# Error: Invalid YAML syntax
ConfigurationError("Invalid YAML in {filename}: {error}")

# Example:
# ConfigurationError("Invalid YAML in course_config.yaml: while scanning for the next token found character '\\t' that cannot start any token")
```

**Solution**: Fix YAML syntax errors (check indentation, use spaces not tabs, validate with YAML parser).

#### Missing Field Errors

```python
# Error: Missing required field
ConfigurationError("Missing required field '{field}' in {context}")

# Examples:
# ConfigurationError("Missing required field 'name' in course")
# ConfigurationError("Missing required field 'model' in llm")
# ConfigurationError("Missing required field 'base_directory' in output")
```

**Solution**: Add missing required fields to configuration file. See validation rules section.

#### Missing Template Errors

```python
# Error: Prompt template not found
ConfigurationError("Prompt template '{name}' not found in configuration")

# Example:
# ConfigurationError("Prompt template 'lecture' not found in configuration")
```

**Solution**: Ensure template exists in `llm_config.yaml` under `prompts` section.

#### JSON Outline Errors

```python
# Error: No outline found
ConfigurationError("No course outline JSON found. Generate outline first with: uv run python3 scripts/03_generate_outline.py")

# Error: Invalid JSON in outline
ConfigurationError("Invalid JSON in outline file {path}: {error}")

# Error: Missing required field in outline
ConfigurationError("Missing required field '{field}' in course outline")
```

**Solution**: 
- Generate outline: `uv run python3 scripts/03_generate_outline.py --no-interactive`
- Fix JSON syntax errors
- Ensure outline has required structure (see JSON_OUTLINE.md)

### Error Handling Pattern

```python
from src.config.loader import ConfigLoader, ConfigurationError
import logging

logger = logging.getLogger(__name__)

try:
    loader = ConfigLoader("config")
    loader.validate_all_configs()
    modules = loader.get_modules()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    
    # Handle specific error types
    if "directory not found" in str(e):
        logger.error("Check config directory path")
    elif "file not found" in str(e):
        logger.error("Ensure all config files exist")
    elif "Invalid YAML" in str(e):
        logger.error("Fix YAML syntax errors")
    elif "Missing required field" in str(e):
        logger.error("Add missing fields to config")
    elif "No course outline JSON found" in str(e):
        logger.error("Generate outline first: uv run python3 scripts/03_generate_outline.py")
    
    raise  # Re-raise or handle appropriately
```

All errors are logged with appropriate severity levels (ERROR for fatal, WARNING for recoverable).

## Testing

Tests in `tests/test_config_loader.py`:
- Load each configuration file
- Validate required fields
- Handle missing files gracefully
- Cache loaded configurations
- Retrieve specific modules and templates

Run tests:
```bash
uv run pytest tests/test_config_loader.py -v
```

## Internal Implementation

- **Caching**: Configurations loaded once and cached in `_course_config`, `_llm_config`, `_output_config`
- **YAML Parsing**: Uses `yaml.safe_load()` for security
- **Path Handling**: Uses `pathlib.Path` for cross-platform compatibility
- **Logging**: Comprehensive logging at DEBUG and INFO levels

## See Also

- **Configuration Guide**: [../../docs/CONFIGURATION.md](../../docs/CONFIGURATION.md)
- **Config Files**: [../../config/README.md](../../config/README.md)
- **API Reference**: [../../docs/API.md](../../docs/API.md)

