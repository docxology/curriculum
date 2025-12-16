# Course Templates - For AI Agents

## Purpose

This directory contains pre-configured course templates (YAML files) that can be selected interactively or via command-line flags. Templates provide ready-to-use course configurations for different subjects.

## Directory Structure

```
config/courses/
├── biology.yaml
├── chemistry.yaml
├── physics.yaml
├── active_inference.yaml
├── active_inference_ai_short.yaml
├── active_inference_college.yaml
├── free_energy_principle.yaml
├── tree_grafting.yaml
└── ...
```

## Template Format

Each template file follows the same structure as `course_config.yaml`:

```yaml
course:
  name: "Course Name"
  subject: "Subject Area"
  description: "Course description..."
  level: "Undergraduate Introductory"
  estimated_duration_weeks: 16
  defaults:
    num_modules: 5
    total_sessions: 15
    sessions_per_module: null  # Auto-calculated
  additional_constraints: "Optional constraints or topic guidance"
```

## Loading Templates

### Using ConfigLoader

```python
from src.config.loader import ConfigLoader

loader = ConfigLoader("config")

# List available templates
courses = loader.list_available_courses()
# Returns: [
#     {"name": "biology", "filename": "biology.yaml", "course_info": {...}},
#     {"name": "chemistry", "filename": "chemistry.yaml", "course_info": {...}},
#     ...
# ]

# Load specific template
template = loader.load_course_template("biology")
course_info = template["course"]

# Get course info from template
course_info = loader.get_course_info(course_template="biology")
```

### Using in Scripts

Templates can be used in scripts via:
- **Interactive mode**: Scripts show a numbered menu of available templates
- **Command-line**: Use `--course` flag: `--course biology`
- **Programmatic**: Pass `course_template` parameter to config methods

## Template Discovery

The system automatically discovers templates:
1. Scans `config/courses/` directory for `.yaml` files
2. Validates each file structure
3. Extracts course metadata
4. Returns list of available templates

## Error Handling

- **Template not found**: Raises `ConfigurationError` with list of available courses
- **Invalid YAML**: Raises `ConfigurationError` with parsing error details
- **Missing directory**: `list_available_courses()` returns empty list (graceful degradation)

## Output Organization

When using course templates, generated content is automatically organized into course-specific subdirectories:

- `output/{course_name}/outlines/` - Course outlines
- `output/{course_name}/modules/` - Generated modules
- `output/{course_name}/website/` - Generated website
- `output/{course_name}/logs/` - Log files

## Creating New Templates

1. Create new YAML file in `config/courses/`
2. Follow same structure as `course_config.yaml`
3. Use descriptive filename (e.g., `biology.yaml`)
4. Template will be automatically discovered

## See Also

- **[../README.md](../README.md)** - Configuration files overview
- **[../AGENTS.md](../AGENTS.md)** - Configuration management guide
- **[../../src/config/AGENTS.md](../../src/config/AGENTS.md)** - ConfigLoader API
- **[../../docs/CONFIGURATION.md](../../docs/CONFIGURATION.md)** - Complete configuration guide
